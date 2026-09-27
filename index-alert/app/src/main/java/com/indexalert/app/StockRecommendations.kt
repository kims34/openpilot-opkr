package com.indexalert.app

import androidx.compose.runtime.Composable

/**
 * Individual-stock recommendation UI intentionally disabled.
 *
 * IndexAlert now limits individual-stock information to neutral constituent
 * mover statistics shown inside the ETF cards. It does not rank or recommend
 * individual stocks by predicted next-session performance.
 */
@Composable
fun StockRecommendationSection(refreshKey: String = "") {
    // Deliberately no UI and no backend request.
}
