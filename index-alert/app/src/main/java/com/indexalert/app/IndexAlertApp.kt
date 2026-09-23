package com.indexalert.app

import android.app.Application
import android.content.Context

class IndexAlertApp : Application() {
    override fun onCreate() {
        super.onCreate()
        migrateEtfBasis(this)
    }
}

private fun migrateEtfBasis(ctx: Context) {
    val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
    if (prefs.getBoolean("etf_basis_v1", false)) return

    val ids = listOf("sp500", "ndx", "djdiv")
    val edit = prefs.edit()
    ids.forEach { id ->
        edit.remove("ath_cash_$id")
        edit.remove("ath_day_$id")
    }

    // Clear only old delivery bookkeeping. Keep the user's enabled/disabled
    // threshold choices and notification history intact.
    prefs.all.keys
        .filter { key -> ids.any { id -> key.startsWith("delivered_${id}_") } }
        .forEach { edit.remove(it) }

    edit.putBoolean("etf_basis_v1", true).apply()
}
