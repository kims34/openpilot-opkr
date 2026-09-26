package com.indexalert.app

import androidx.compose.runtime.Composable

/**
 * Market/news explanation blocks were intentionally removed from the UI.
 * Keep this no-op composable so older dashboard code can call it safely
 * without rendering any text or performing network requests.
 */
@Composable
fun MarketBriefingSection(indexId: String) {
    // Intentionally empty.
}
