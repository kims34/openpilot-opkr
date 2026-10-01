package com.indexalert.app

import android.app.NotificationManager
import android.content.Context
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.google.android.gms.tasks.Tasks
import androidx.work.*
import java.util.concurrent.TimeUnit
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import org.json.JSONObject
import org.json.JSONArray

object PushBridge {
    private enum class ReceiptResult { SUCCESS, RETRY, DROP }
    private enum class SelfTestResult { SUCCESS, RETRY, DROP }

    fun configured(): Boolean = BuildConfig.INDEXALERT_BACKEND_URL.isNotBlank() &&
        BuildConfig.FIREBASE_APP_ID.isNotBlank() && BuildConfig.FIREBASE_API_KEY.isNotBlank() &&
        BuildConfig.FIREBASE_PROJECT_ID.isNotBlank() && BuildConfig.FIREBASE_SENDER_ID.isNotBlank()

    fun notificationsEnabled(ctx: Context): Boolean =
        (ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).areNotificationsEnabled()

    private fun sha256(value: String): String = MessageDigest.getInstance("SHA-256")
        .digest(value.toByteArray(Charsets.UTF_8))
        .joinToString("") { "%02x".format(it) }

    private fun clientBuild(): String = "${BuildConfig.VERSION_NAME}-${BuildConfig.VERSION_CODE}"

    fun tryInit(ctx: Context): Boolean {
        if (!configured()) return false
        if (FirebaseApp.getApps(ctx).isEmpty()) {
            FirebaseApp.initializeApp(ctx, FirebaseOptions.Builder()
                .setApplicationId(BuildConfig.FIREBASE_APP_ID)
                .setApiKey(BuildConfig.FIREBASE_API_KEY)
                .setProjectId(BuildConfig.FIREBASE_PROJECT_ID)
                .setGcmSenderId(BuildConfig.FIREBASE_SENDER_ID).build())
        }
        scheduleSync(ctx)
        return true
    }

    fun scheduleSync(ctx: Context) {
        val request = OneTimeWorkRequestBuilder<RegistrationWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS).build()
        WorkManager.getInstance(ctx).enqueueUniqueWork("push-registration", ExistingWorkPolicy.REPLACE, request)
    }

    private fun scheduleSelfTest(ctx: Context) {
        val build = clientBuild()
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        if (prefs.getBoolean("push_self_test_done_$build", false)) return
        val request = OneTimeWorkRequestBuilder<PushSelfTestWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS).build()
        WorkManager.getInstance(ctx).enqueueUniqueWork(
            "push-self-test-$build",
            ExistingWorkPolicy.KEEP,
            request,
        )
    }

    fun scheduleReceipt(ctx: Context, eventId: String) {
        if (!configured() || eventId.isBlank()) return
        val request = OneTimeWorkRequestBuilder<PushReceiptWorker>()
            .setInputData(workDataOf("event_id" to eventId))
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS).build()
        WorkManager.getInstance(ctx).enqueueUniqueWork(
            "push-receipt-${sha256(eventId).take(24)}",
            ExistingWorkPolicy.KEEP,
            request,
        )
    }

    @Synchronized
    fun sync(ctx: Context): Boolean = runCatching {
        check(configured())
        // Do not tell the server this device is ready until Android can actually
        // show notifications. The permission callback schedules another sync.
        check(notificationsEnabled(ctx))
        val token = Tasks.await(FirebaseMessaging.getInstance().token, 15, TimeUnit.SECONDS)
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val enabled = JSONObject()
        rules.forEach { r -> enabled.put(r.id, JSONArray(r.levels.filter {
            prefs.getBoolean("enabled_${r.id}_${it.first}", true)
        }.map { it.first })) }
        val c = URL(BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/') + "/register")
            .openConnection() as HttpURLConnection
        val ready = try {
            c.requestMethod = "POST"
            c.connectTimeout = 10000
            c.readTimeout = 10000
            c.doOutput = true
            c.setRequestProperty("Content-Type", "application/json")
            val body = JSONObject().put("token", token).put("platform", "android")
                .put("protocol", 2).put("enabled_levels", enabled).toString()
            c.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            val reply = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
            reply.optBoolean("ok") && reply.optBoolean("registered") &&
                reply.optBoolean("firebase") && reply.optInt("protocol") >= 2
        } finally { c.disconnect() }
        if (ready) {
            // Store only a one-way hash for delivery acknowledgements. The raw
            // FCM token remains confined to Firebase registration/self-test calls.
            prefs.edit().putString("push_token_hash", sha256(token)).apply()
            scheduleSelfTest(ctx)
        }
        ready
    }.getOrDefault(false)

    private fun requestSelfTest(ctx: Context): SelfTestResult {
        if (!configured() || !notificationsEnabled(ctx)) return SelfTestResult.DROP
        return try {
            val token = Tasks.await(FirebaseMessaging.getInstance().token, 15, TimeUnit.SECONDS)
            val c = URL(BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/') + "/push-self-test")
                .openConnection() as HttpURLConnection
            try {
                c.requestMethod = "POST"
                c.connectTimeout = 10000
                c.readTimeout = 10000
                c.doOutput = true
                c.setRequestProperty("Content-Type", "application/json")
                val body = JSONObject()
                    .put("token", token)
                    .put("platform", "android")
                    .put("protocol", 2)
                    .put("client_build", clientBuild())
                    .toString()
                c.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                val code = c.responseCode
                when {
                    code in 200..299 -> {
                        val text = c.inputStream.bufferedReader().use { it.readText() }
                        val reply = runCatching { JSONObject(text) }.getOrNull()
                        when {
                            reply?.optBoolean("ok") != true -> SelfTestResult.RETRY
                            // FCM provider send success is not handset receipt.
                            // Mark this build complete only after the server sees
                            // the privacy-safe /push-ack for the original event.
                            reply.optBoolean("receipt_confirmed", false) -> SelfTestResult.SUCCESS
                            else -> SelfTestResult.RETRY
                        }
                    }
                    code == 404 || code == 408 || code == 425 || code == 429 || code >= 500 -> SelfTestResult.RETRY
                    else -> SelfTestResult.DROP
                }
            } finally { c.disconnect() }
        } catch (_: Exception) {
            SelfTestResult.RETRY
        }
    }

    fun runSelfTest(ctx: Context, attempt: Int): ListenableWorker.Result {
        val build = clientBuild()
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        if (prefs.getBoolean("push_self_test_done_$build", false)) {
            return ListenableWorker.Result.success()
        }
        return when (requestSelfTest(ctx)) {
            SelfTestResult.SUCCESS -> {
                prefs.edit().putBoolean("push_self_test_done_$build", true).apply()
                ListenableWorker.Result.success()
            }
            SelfTestResult.DROP -> ListenableWorker.Result.success()
            SelfTestResult.RETRY -> if (attempt >= 4) {
                // Do not mark the build done when the receipt is still unconfirmed.
                // A future registration/settings/token sync can schedule another
                // confirmation attempt for the same already-sent event.
                ListenableWorker.Result.success()
            } else {
                ListenableWorker.Result.retry()
            }
        }
    }

    private fun ackDelivery(ctx: Context, eventId: String): ReceiptResult {
        if (!configured()) return ReceiptResult.DROP
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val tokenHash = prefs.getString("push_token_hash", "").orEmpty()
        if (tokenHash.length != 64) {
            scheduleSync(ctx)
            return ReceiptResult.RETRY
        }
        return try {
            val c = URL(BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/') + "/push-ack")
                .openConnection() as HttpURLConnection
            try {
                c.requestMethod = "POST"
                c.connectTimeout = 10000
                c.readTimeout = 10000
                c.doOutput = true
                c.setRequestProperty("Content-Type", "application/json")
                val body = JSONObject()
                    .put("event_id", eventId)
                    .put("token_hash", tokenHash)
                    .put("notifications_enabled", notificationsEnabled(ctx))
                    .put("protocol", 2)
                    .toString()
                c.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                val code = c.responseCode
                when {
                    code in 200..299 -> {
                        val text = c.inputStream.bufferedReader().use { it.readText() }
                        val reply = runCatching { JSONObject(text) }.getOrNull()
                        if (reply?.optBoolean("ok") == true && reply.optBoolean("acknowledged")) {
                            ReceiptResult.SUCCESS
                        } else {
                            ReceiptResult.RETRY
                        }
                    }
                    code == 404 -> {
                        // Registration may be racing a Firebase token refresh. Re-sync
                        // once before giving up on an old/unknown event.
                        scheduleSync(ctx)
                        ReceiptResult.RETRY
                    }
                    code == 408 || code == 425 || code == 429 || code >= 500 -> ReceiptResult.RETRY
                    else -> ReceiptResult.DROP
                }
            } finally { c.disconnect() }
        } catch (_: Exception) {
            ReceiptResult.RETRY
        }
    }

    fun runReceipt(
        ctx: Context,
        eventId: String,
        attempt: Int,
    ): ListenableWorker.Result = when (ackDelivery(ctx, eventId)) {
        ReceiptResult.SUCCESS, ReceiptResult.DROP -> ListenableWorker.Result.success()
        ReceiptResult.RETRY -> if (attempt >= 4) {
            ListenableWorker.Result.success()
        } else {
            ListenableWorker.Result.retry()
        }
    }
}

class RegistrationWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        // Permission denial is not a transient network error. Avoid an endless
        // background retry loop; granting permission schedules a fresh sync.
        if (!PushBridge.notificationsEnabled(applicationContext)) return Result.success()
        val ready = PushBridge.sync(applicationContext)
        if (ready) {
            // Once server push registration is confirmed, the phone should stay idle.
            // Token refreshes and setting changes schedule their own one-shot syncs.
            WorkManager.getInstance(applicationContext).cancelUniqueWork("index-watch")
            return Result.success()
        }
        return Result.retry()
    }
}

class PushSelfTestWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result = PushBridge.runSelfTest(applicationContext, runAttemptCount)
}

class PushReceiptWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        val eventId = inputData.getString("event_id").orEmpty()
        if (eventId.isBlank()) return Result.success()
        return PushBridge.runReceipt(applicationContext, eventId, runAttemptCount)
    }
}

class AlertFirebaseService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        PushBridge.scheduleSync(applicationContext)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        val ctx = applicationContext
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val id = message.data["index_id"] ?: return
        val threshold = message.data["threshold"]?.toIntOrNull() ?: return
        val eventId = message.data["event_id"] ?: message.messageId ?: return

        // Receipt means the data message reached this FirebaseMessagingService.
        // Send it even if a local threshold preference suppresses presentation.
        PushBridge.scheduleReceipt(ctx, eventId)

        if (!prefs.getBoolean("enabled_${id}_${threshold}", true)) return
        val title = message.data["title"] ?: message.notification?.title ?: "지수 하락 알림"
        val body = message.data["body"] ?: message.notification?.body ?: return
        synchronized(HistoryStore) {
            val seen = prefs.getString("received_events", "")!!.split('\n').filter { it.isNotBlank() }
            val cycle = message.data["cycle"] ?: ""
            val deliveredKey = "delivered_${id}_${cycle}_${threshold}"
            if (eventId in seen || prefs.getBoolean(deliveredKey, false)) return
            createChannel(ctx)
            // Persist receipt even when the OS suppresses presentation later.
            HistoryStore.add(ctx, "$title / $body")
            val edit = prefs.edit().putString("received_events", (listOf(eventId) + seen).take(200).joinToString("\n"))
            val thresholds = runCatching { JSONArray(message.data["thresholds"] ?: "[$threshold]") }.getOrDefault(JSONArray().put(threshold))
            for (i in 0 until thresholds.length()) edit.putBoolean("delivered_${id}_${cycle}_${thresholds.getInt(i)}", true)
            edit.commit()
            IndexWorker.notify(ctx, title, body)
        }
    }
}
