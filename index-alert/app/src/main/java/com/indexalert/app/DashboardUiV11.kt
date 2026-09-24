package com.indexalert.app

import android.content.Context
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import java.util.Locale

val dashboardRules: List<Rule> = buildList {
    rules.forEach { rule ->
        if (rule.id == "kospi100") {
            add(
                rule.copy(
                    name = "KOSPI",
                    cashSymbol = "^KS11",
                    proxySymbol = null,
                    description = "코스피 종합지수 · 네이버 증권 · 표시 전용 (알림 없음)",
                    timezone = "Asia/Seoul"
                )
            )
        } else {
            add(rule)
        }
    }
    if (none { it.id == "usdkrw" }) {
        add(
            Rule(
                id = "usdkrw",
                name = "USD/KRW 달러 환율",
                cashSymbol = "KRW=X",
                proxySymbol = null,
                levels = emptyList(),
                description = "원/달러 환율 · 네이버 증권(하나은행 고시) · 표시 전용",
                timezone = "Asia/Seoul"
            )
        )
    }
}

@Composable
fun HomeV11(
    ctx: Context,
    snapshots: List<IndexSnapshot>,
    loading: Boolean,
    statusText: String,
    onRefresh: () -> Unit,
    laggards: List<LaggardItem> = emptyList(),
    laggardStatus: String = ""
) {
    val prefs = ctx.getSharedPreferences("state", Context.MODE_PRIVATE)
    var refreshHistory by remember { mutableIntStateOf(0) }
    var alertSettingsExpanded by remember { mutableStateOf(false) }

    Column(Modifier.fillMaxSize().padding(18.dp).verticalScroll(rememberScrollState())) {
        Text("시장 하락 알리미", style = MaterialTheme.typography.headlineMedium)
        Text("SPY · QQQ · SCHD · KOSPI · USD/KRW / 시장 현황", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(14.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRefresh, enabled = !loading, modifier = Modifier.weight(1f)) {
                Text(if (loading) "새로고침 중" else "새로고침")
            }
            OutlinedButton(
                onClick = {
                    IndexWorker.notify(ctx, "테스트 알림", "시장 하락 알리미가 정상 작동합니다.")
                    HistoryStore.add(ctx, "테스트 알림 발송")
                    refreshHistory++
                },
                modifier = Modifier.weight(1f)
            ) { Text("테스트 알림") }
        }
        Text(statusText, Modifier.padding(top = 8.dp), style = MaterialTheme.typography.bodySmall)

        Spacer(Modifier.height(10.dp))
        if (snapshots.isEmpty() && loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        snapshots.forEach { IndexCardV11(it) }

        Spacer(Modifier.height(18.dp))
        Text("개별종목 ATH 하락 TOP 10", style = MaterialTheme.typography.titleLarge)
        Text("각 그룹별 ATH 대비 하락률이 큰 순 · 중복 편입은 그대로 표시", style = MaterialTheme.typography.bodySmall)
        val groups = listOf(
            "sp500" to "S&P500 하락 TOP 10",
            "nasdaq100" to "NASDAQ100 하락 TOP 10",
            "schd" to "SCHD 보유종목 하락 TOP 10"
        )
        var anyGroup = false
        groups.forEach { (key, title) ->
            val group = laggards.filter { it.universe == key }.sortedBy { it.rank }
            if (group.isNotEmpty()) {
                anyGroup = true
                Spacer(Modifier.height(12.dp))
                Text(title, style = MaterialTheme.typography.titleMedium)
                group.forEach { LaggardCard(it) }
            }
        }
        if (!anyGroup) {
            Text(laggardStatus.ifBlank { "TOP10 순위 계산 중" }, Modifier.padding(top = 8.dp))
        } else if (laggardStatus.isNotBlank()) {
            Text(laggardStatus, Modifier.padding(top = 6.dp), style = MaterialTheme.typography.bodySmall)
        }

        Spacer(Modifier.height(18.dp))
        OutlinedButton(
            onClick = { alertSettingsExpanded = !alertSettingsExpanded },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(if (alertSettingsExpanded) "알림 단계 설정 ▲ 접기" else "알림 단계 설정 ▼ 펼치기")
        }
        if (alertSettingsExpanded) {
            Text(
                "SPY · QQQ · SCHD만 알림을 사용합니다. KOSPI와 USD/KRW는 표시 전용입니다.",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 6.dp)
            )
            rules.filter { it.levels.isNotEmpty() }.forEach { rule ->
                Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                    Column(Modifier.padding(14.dp)) {
                        Text(rule.name, style = MaterialTheme.typography.titleMedium)
                        rule.levels.forEach { lv ->
                            key("${rule.id}_${lv.first}") {
                                var enabled by remember { mutableStateOf(prefs.getBoolean("enabled_${rule.id}_${lv.first}", true)) }
                                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text("-${lv.first}%  ·  추가매수 자금 ${lv.second}%")
                                    Switch(
                                        checked = enabled,
                                        onCheckedChange = {
                                            enabled = it
                                            prefs.edit().putBoolean("enabled_${rule.id}_${lv.first}", it).apply()
                                            PushBridge.scheduleSync(ctx)
                                        }
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(18.dp))
        Text("최근 알림", style = MaterialTheme.typography.titleLarge)
        val history = remember(refreshHistory, statusText) { HistoryStore.list(ctx) }
        if (history.isEmpty()) Text("아직 기록된 알림이 없습니다.", style = MaterialTheme.typography.bodySmall)
        else history.take(8).forEach { Text("• $it", Modifier.padding(vertical = 2.dp)) }

        Spacer(Modifier.height(18.dp))
        Text(
            "SPY · QQQ · SCHD는 ETF 자체 가격으로 단계별 알림을 감시합니다. " +
                "KOSPI 현재값과 전일 등락은 네이버 증권을 우선 사용하고, USD/KRW는 네이버 증권의 하나은행 고시 환율을 표시합니다. " +
                "KOSPI와 환율은 알림을 보내지 않습니다.",
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun IndexCardV11(s: IndexSnapshot) {
    Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
        Column(Modifier.padding(16.dp)) {
            Text(s.rule.name, style = MaterialTheme.typography.titleLarge)
            Text(s.rule.description, style = MaterialTheme.typography.bodySmall)
            if (s.error != null) {
                Spacer(Modifier.height(6.dp))
                Text("데이터 확인 실패: ${s.error}")
                return@Column
            }

            Spacer(Modifier.height(8.dp))
            val change = if (s.dayChange != null && s.dayChangePercent != null) {
                "  ${signedV11(s.dayChange)} (${signedPctV11(s.dayChangePercent)})"
            } else ""
            val currentLabel = if (s.rule.id == "usdkrw") "현재 환율" else "현재값"
            Text("$currentLabel  ${fmtV11(s.current)}$change", style = MaterialTheme.typography.titleMedium)

            if (s.rule.id != "usdkrw" && s.ath != null && s.ath > 0.0) {
                val age = s.athDays?.let { if (it == 0) " · 오늘 최고가" else " · 최고가 후 ${it}일" } ?: ""
                val date = s.athDate?.let { " ($it)" } ?: ""
                Text("ATH      ${fmtV11(s.ath)}$age$date")
                Text("ATH 대비 ${s.drawdown?.let { String.format(Locale.US, "%.2f%%", it) } ?: "-"}")
            }

            if (s.alertsEnabled) {
                Text("현재 단계 ${s.stageText}")
                Text("다음 알림 ${s.nextText}")
            }

            val source = when (s.rule.id) {
                "kospi100" -> s.sourceText.replace("KOSPI 100", "KOSPI")
                "usdkrw" -> if (s.sourceText.contains("ETF 자체")) "USD/KRW · Yahoo 로컬 보조 조회" else s.sourceText
                else -> s.sourceText
            }
            Text("기준       $source", style = MaterialTheme.typography.bodySmall)
        }
    }
}

private fun fmtV11(v: Double?): String = v?.let { String.format(Locale.US, "%,.2f", it) } ?: "-"
private fun signedV11(v: Double): String = String.format(Locale.US, "%+,.2f", v)
private fun signedPctV11(v: Double): String = String.format(Locale.US, "%+.2f%%", v)
