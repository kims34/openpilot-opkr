package com.indexalert.app

import android.content.Context
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

object PushBridge {
    fun configured(): Boolean = BuildConfig.INDEXALERT_BACKEND_URL.isNotBlank() &&
        BuildConfig.FIREBASE_APP_ID.isNotBlank() && BuildConfig.FIREBASE_API_KEY.isNotBlank() &&
        BuildConfig.FIREBASE_PROJECT_ID.isNotBlank() && BuildConfig.FIREBASE_SENDER_ID.isNotBlank()

    fun tryInit(ctx: Context): Boolean {
        if (!configured()) return false
        if (FirebaseApp.getApps(ctx).isEmpty()) {
            val options = FirebaseOptions.Builder()
                .setApplicationId(BuildConfig.FIREBASE_APP_ID)
                .setApiKey(BuildConfig.FIREBASE_API_KEY)
                .setProjectId(BuildConfig.FIREBASE_PROJECT_ID)
                .setGcmSenderId(BuildConfig.FIREBASE_SENDER_ID)
                .build()
            FirebaseApp.initializeApp(ctx, options)
        }
        FirebaseMessaging.getInstance().token.addOnSuccessListener { registerToken(it) }
        return true
    }

    fun registerToken(token: String) {
        if (!configured() || token.isBlank()) return
        Thread {
            runCatching {
                val base = BuildConfig.INDEXALERT_BACKEND_URL.trimEnd('/')
                val c = URL("$base/register").openConnection() as HttpURLConnection
                c.requestMethod = "POST"
                c.connectTimeout = 10000
                c.readTimeout = 10000
                c.doOutput = true
                c.setRequestProperty("Content-Type", "application/json")
                val body = JSONObject().put("token", token).put("platform", "android").toString()
                c.outputStream.use { it.write(body.toByteArray()) }
                c.inputStream.use { it.readBytes() }
                c.disconnect()
            }
        }.start()
    }
}

class AlertFirebaseService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        PushBridge.registerToken(token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        val title = message.notification?.title ?: message.data["title"] ?: "지수 하락 알림"
        val body = message.notification?.body ?: message.data["body"] ?: return
        IndexWorker.notify(applicationContext, title, body)
        HistoryStore.add(applicationContext, "$title / $body")
    }
}
