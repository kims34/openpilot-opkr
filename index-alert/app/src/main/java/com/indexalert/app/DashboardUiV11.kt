package com.indexalert.app

import android.content.Context
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.util.Locale

private val RiseRed = Color(0xFFD32F2F)
private val FallBlue = Color(0xFF1565C0)
private val MetricBlue = Color(0xFF1565C0)

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
        } else add(rule)
    }
    if (none { it.id == "usdkrw" }) {
        add(
            Rule(
                id = "usdkrw",
                name = "USD/KRW 달러 환율",
                cashSymbol = "KRW=X",
                proxySymbol = null,
                levels = emptyList(),
                description = "원/달러 환율 · 실시간 우선 · 표시 전용",
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
        snapshots.forEach { snapshot ->
            val universe = when (snapshot.rule.id) {
                "sp500" -> "sp500"
                "ndx" -> "nasdaq100"
                "djdiv" -> "schd"
                else -> null
            }
            val movers = if (universe == null) emptyList() else laggards.filter { it.universe == universe }.sortedBy { it.rank }.take(3)
            IndexCardV19(snapshot, movers, laggardStatus)
        }

        Spacer(Modifier.height(18.dp))
        OutlinedButton(
            onClick = { alertSettingsExpanded = !alertSettingsExpanded },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(if (alertSettingsExpanded) "알림 단계 설정 ▲ 접기" else "알림 단계 설정 ▼ 펼치기")
        }
        if (alertSettingsExpanded) {
            Text("SPY · QQQ · SCHD만 알림을 사용합니다. KOSPI와 USD/KRW는 표시 전용입니다.", style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 6.dp))
            rules.filter { it.levels.isNotEmpty() }.forEach { rule ->
                Card(Modifier.fillMaxWidth().padding(vertical = 6.dp), border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
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
            "SPY · QQQ · SCHD는 ETF 자체 가격으로 알림을 감시하고, KOSPI와 USD/KRW는 표시 전용입니다.",
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun IndexCardV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String) {
    val alertTriggered = s.alertsEnabled && s.stageText.startsWith("🔔")
    val cardColor = if (alertTriggered) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.surface
    val cardBorder = if (alertTriggered) BorderStroke(2.dp, MaterialTheme.colorScheme.error) else BorderStroke(1.5.dp, MaterialTheme.colorScheme.outline)

    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 7.dp),
        colors = CardDefaults.cardColors(containerColor = cardColor),
        border = cardBorder,
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(
                s.rule.name,
                style = MaterialTheme.typography.titleLarge,
                color = if (alertTriggered) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Bold
            )
            Text(s.rule.description, style = MaterialTheme.typography.bodySmall)
            if (s.error != null) {
                Spacer(Modifier.height(6.dp))
                Text("데이터 확인 실패: ${s.error}")
                return@Column
            }

            Spacer(Modifier.height(8.dp))
            val change = if (s.dayChange != null && s.dayChangePercent != null) "  ${signedV19(s.dayChange)} (${signedPctV19(s.dayChangePercent)})" else ""
            val currentLabel = if (s.rule.id == "usdkrw") "현재 환율" else "현재값"
            Text(
                "$currentLabel  ${fmtV19(s.current)}$change",
                style = MaterialTheme.typography.titleMedium,
                color = movementColorV19(s.dayChangePercent),
                fontWeight = FontWeight.SemiBold
            )

            if (s.rule.id != "usdkrw" && s.ath != null && s.ath > 0.0) {
                val age = s.athDays?.let { if (it == 0) " · 오늘 최고가" else " · 최고가 후 ${it}일" } ?: ""
                val date = s.athDate?.let { " ($it)" } ?: ""
                Text("ATH      ${fmtV19(s.ath)}$age$date")
                Text(
                    "ATH 대비 등락률 ${s.drawdown?.let { String.format(Locale.US, "%+.2f%%", it) } ?: "-"}",
                    color = if (alertTriggered) MaterialTheme.colorScheme.error else MetricBlue,
                    fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.titleSmall
                )
            }

            if (s.alertsEnabled) {
                Spacer(Modifier.height(8.dp))
                if (alertTriggered) {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = MaterialTheme.colorScheme.error,
                        contentColor = MaterialTheme.colorScheme.onError,
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(Modifier.padding(horizontal = 12.dp, vertical = 10.dp)) {
                            Text("🔔 실제 알림 발송됨", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelLarge)
                            Text(
                                s.stageText.removePrefix("🔔 알림 발생 · "),
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleMedium,
                                modifier = Modifier.padding(top = 2.dp)
                            )
                        }
                    }
                    Text("다음 알림 ${s.nextText}", fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 5.dp))
                } else {
                    Text("현재 단계 ${s.stageText}")
                    Text("다음 알림 ${s.nextText}")
                }
            }

            val source = when (s.rule.id) {
                "kospi100" -> s.sourceText.replace("KOSPI 100", "KOSPI")
                "usdkrw" -> if (s.sourceText.contains("ETF 자체")) "USD/KRW · Yahoo 로컬 보조 조회" else s.sourceText
                else -> s.sourceText
            }
            Text("기준       $source", style = MaterialTheme.typography.bodySmall)

            NextDayProbabilitySection(s.rule.id)
            MonthlyChartSection(s.rule.id)

            if (s.rule.id in setOf("sp500", "ndx", "djdiv")) {
                DirectionalMoverSectionV19(s, movers, moverStatus)
            }
        }
    }
}

@Composable
private fun DirectionalMoverSectionV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String) {
    Spacer(Modifier.height(10.dp))
    val isDown = (s.dayChangePercent ?: 0.0) < 0.0
    val title = if (isDown) "구성종목 당일 하락률 상위 3개" else "구성종목 당일 상승률 상위 3개"
    Text(title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
    Spacer(Modifier.height(4.dp))

    if (movers.isEmpty()) {
        Text(moverStatus.ifBlank { "구성종목 등락 계산 중" }, style = MaterialTheme.typography.bodySmall)
        return
    }

    movers.forEach { item ->
        Column(Modifier.fillMaxWidth().padding(vertical = 3.dp)) {
            Text("${item.rank}. ${item.symbol} · ${item.name}", style = MaterialTheme.typography.bodyMedium)
            Text(
                "현재 ${fmtV19(item.current)}  ${signedV19(item.dayChange)} (${signedPctV19(item.dayChangePercent)})",
                color = movementColorV19(item.dayChangePercent),
                fontWeight = FontWeight.SemiBold,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
private fun movementColorV19(percent: Double?): Color = when {
    percent == null || percent == 0.0 -> MaterialTheme.colorScheme.onSurface
    percent > 0.0 -> RiseRed
    else -> FallBlue
}

private fun fmtV19(v: Double?): String = v?.let { String.format(Locale.US, "%,.2f", it) } ?: "-"
private fun signedV19(v: Double): String = String.format(Locale.US, "%+,.2f", v)
private fun signedPctV19(v: Double): String = String.format(Locale.US, "%+.2f%%", v)
