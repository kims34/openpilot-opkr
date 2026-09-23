package com.indexalert.app

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
import org.json.JSONObject
import org.json.JSONArray

object PushBridge {
    fun configured(): Boolean = BuildConfig.INDEXALERT_BACKEND_URL.isNotBlank() &&
        BuildConfig.FIREBASE_APP_ID.isNotBlank() && BuildConfig.FIREBASE_API_KEY.isNotBlank() &&
        BuildConfig.FIREBASE_PROJECT_ID.isNotBlank() && BuildConfig.FIREBASE_SENDER_ID.isNotBlank()

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

    @Synchronized
    fun sync(ctx: Context): Boolean = runCatching {
        check(configured())
        val token = Tasks.await(FirebaseMessaging.getInstance().token, 15, TimeUnit.SECONDS)
        val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
        val enabled = JSONObject()
        rules.forEach { r -> enabled.put(r.id, JSONArray(r.levels.filter {
            prefs.getBoolean("enabled_${r.id}_${it.first}", true)
        }.map { it.first })) }
        val c = URL(BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/') + "/register")
            .openConnection() as HttpURLConnection
        try {
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
    }.getOrDefault(false)
}

class RegistrationWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result = if (PushBridge.sync(applicationContext)) Result.success() else Result.retry()
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
        if (!prefs.getBoolean("enabled_${id}_${threshold}", true)) return
        val eventId = message.data["event_id"] ?: message.messageId ?: return
        val title = message.data["title"] ?: message.notification?.title ?: "지수 하락 알림"
        val body = message.data["body"] ?: message.notification?.body ?: return
        synchronized(HistoryStore) {
            val seen = prefs.getString("received_events", "")!!.split('\n').filter { it.isNotBlank() }
            val cycle = message.data["cycle"] ?: ""
            val deliveredKey = "delivered_${id}_${cycle}_${threshold}"
            if (eventId in seen || prefs.getBoolean(deliveredKey, false)) return
            createChannel(ctx)
            // Persist receipt even when system notification permission is disabled.
            HistoryStore.add(ctx, "$title / $body")
            val edit = prefs.edit().putString("received_events", (listOf(eventId) + seen).take(200).joinToString("\n"))
            val thresholds = runCatching { JSONArray(message.data["thresholds"] ?: "[$threshold]") }.getOrDefault(JSONArray().put(threshold))
            for (i in 0 until thresholds.length()) edit.putBoolean("delivered_${id}_${cycle}_${thresholds.getInt(i)}", true)
            edit.commit()
            IndexWorker.notify(ctx, title, body)
        }
    }
}
