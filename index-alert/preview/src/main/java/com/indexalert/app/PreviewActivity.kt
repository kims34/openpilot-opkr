package com.indexalert.app

import android.app.Activity
import android.os.Bundle
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import java.util.concurrent.Executors

/** Separate, GET-only UI verification. No production registration or app data access. */
class PreviewActivity : Activity() {
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var status: TextView
    private lateinit var refresh: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (20 * resources.displayMetrics.density).toInt()
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        layout.addView(TextView(this).apply {
            text = "IndexAlert 4.8 검증"
            textSize = 24f
        })
        layout.addView(TextView(this).apply {
            text = "기존 앱과 별도로 실행됩니다. 알림과 자동매매 기능은 제공하지 않습니다."
            textSize = 16f
        })
        status = TextView(this).apply { textSize = 20f }
        layout.addView(status)
        refresh = Button(this).apply {
            text = "상태 새로고침"
            setOnClickListener { checkReadiness() }
        }
        layout.addView(refresh)
        setContentView(layout, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        checkReadiness()
    }

    private fun checkReadiness() {
        if (!refresh.isEnabled) return
        refresh.isEnabled = false
        status.text = AutomationAvailability.CHECKING.description
        executor.execute {
            val result = runCatching { AutomationReadiness.fetchAvailability() }
                .getOrDefault(AutomationAvailability.UNKNOWN)
            runOnUiThread {
                if (!isFinishing && !isDestroyed) {
                    status.text = result.description
                    refresh.isEnabled = true
                }
            }
        }
    }

    override fun onDestroy() {
        executor.shutdownNow()
        super.onDestroy()
    }
}
