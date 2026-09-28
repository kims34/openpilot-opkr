from pathlib import Path

root = Path(__file__).resolve().parent
ui = root / "app/src/main/java/com/indexalert/app/DashboardUiV11.kt"
text = ui.read_text()
text = text.replace(
    'private fun IndexCardV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String, refreshKey: String) {\n    val alertTriggered =',
    'private fun IndexCardV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String, refreshKey: String) {\n    var probabilityExpanded by remember(s.rule.id) { mutableStateOf(false) }\n    val alertTriggered ='
)
old = '''            NextDayProbabilitySection(s.rule.id, refreshKey)\n            ExtendedSessionProbabilitySection(s.rule.id, refreshKey)\n            AfterOpenProbabilitySection(s.rule.id, refreshKey)\n            if (s.rule.id == "kospi100") {\n                KospiOneMonthProbabilitySection(refreshKey)\n            }\n            MonthlyChartSection(s.rule.id)'''
new = '''            if (s.rule.id in setOf("sp500", "ndx", "djdiv", "kospi100")) {\n                Spacer(Modifier.height(10.dp))\n                OutlinedButton(\n                    onClick = { probabilityExpanded = !probabilityExpanded },\n                    modifier = Modifier.fillMaxWidth()\n                ) {\n                    Text(if (probabilityExpanded) "확률 분석 ▲ 접기" else "확률 분석 ▼ 펼치기")\n                }\n                if (probabilityExpanded) {\n                    NextDayProbabilitySection(s.rule.id, refreshKey)\n                    ExtendedSessionProbabilitySection(s.rule.id, refreshKey)\n                    AfterOpenProbabilitySection(s.rule.id, refreshKey)\n                    if (s.rule.id == "kospi100") {\n                        KospiOneMonthProbabilitySection(refreshKey)\n                    }\n                }\n            }\n            MonthlyChartSection(s.rule.id)'''
if old not in text:
    raise SystemExit("Dashboard probability block not found")
ui.write_text(text.replace(old, new))

nextday = root / "app/src/main/java/com/indexalert/app/NextDayProbability.kt"
text = nextday.read_text()
text = text.replace(
    'Text("다음 거래일 종가 상승 추정  ${pct(e.probability)}",\n                style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)',
    'Text("다음 거래일 종가 상승 추정  ${pct(e.probability)}",\n                style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold,\n                color = androidx.compose.ui.graphics.Color.Black)'
)
text = text.replace('color = androidx.compose.ui.graphics.Color(0xFFD32F2F)', 'color = androidx.compose.ui.graphics.Color.Black')
text = text.replace('color = androidx.compose.ui.graphics.Color(0xFF1565C0)', 'color = androidx.compose.ui.graphics.Color.Black')
text = text.replace(
    'fontWeight = FontWeight.Bold\n            )\n        }\n    }\n    Text("서로 겹치지 않는 6개 구간',
    'fontWeight = FontWeight.Bold,\n                color = androidx.compose.ui.graphics.Color.Black\n            )\n        }\n    }\n    Text("서로 겹치지 않는 6개 구간'
)
nextday.write_text(text)

ext = root / "app/src/main/java/com/indexalert/app/ExtendedSessionProbability.kt"
text = ext.read_text()
text = text.replace(
    'style = MaterialTheme.typography.bodyMedium,\n                    fontWeight = FontWeight.SemiBold\n                )',
    'style = MaterialTheme.typography.bodyMedium,\n                    fontWeight = FontWeight.SemiBold,\n                    color = androidx.compose.ui.graphics.Color.Black\n                )',
    1
)
text = text.replace(
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold\n            )',
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold,\n                color = androidx.compose.ui.graphics.Color.Black\n            )',
    1
)
text = text.replace(
    'style = MaterialTheme.typography.bodySmall\n                )\n            }\n            e.extendedMovePercent',
    'style = MaterialTheme.typography.bodySmall,\n                    color = androidx.compose.ui.graphics.Color.Black\n                )\n            }\n            e.extendedMovePercent',
    1
)
ext.write_text(text)

after = root / "app/src/main/java/com/indexalert/app/AfterOpenProbability.kt"
text = after.read_text()
text = text.replace(
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold\n            )',
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold,\n                color = androidx.compose.ui.graphics.Color.Black\n            )',
    1
)
text = text.replace(
    'style = MaterialTheme.typography.bodySmall\n                )\n            }\n            e.openingGapPercent',
    'style = MaterialTheme.typography.bodySmall,\n                    color = androidx.compose.ui.graphics.Color.Black\n                )\n            }\n            e.openingGapPercent',
    1
)
after.write_text(text)

first = root / "app/src/main/java/com/indexalert/app/FirstHourProbability.kt"
text = first.read_text()
text = text.replace(
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold\n            )',
    'style = MaterialTheme.typography.titleMedium,\n                fontWeight = FontWeight.Bold,\n                color = androidx.compose.ui.graphics.Color.Black\n            )',
    1
)
text = text.replace(
    'style = MaterialTheme.typography.bodySmall\n                )\n            }\n            e.firstHourReturnPercent',
    'style = MaterialTheme.typography.bodySmall,\n                    color = androidx.compose.ui.graphics.Color.Black\n                )\n            }\n            e.firstHourReturnPercent',
    1
)
first.write_text(text)

gradle = root / "app/build.gradle.kts"
text = gradle.read_text().replace('versionCode = 38', 'versionCode = 39').replace('versionName = "3.8"', 'versionName = "3.9"')
gradle.write_text(text)

print("v3.9 probability collapse + black probability numbers patch applied")
