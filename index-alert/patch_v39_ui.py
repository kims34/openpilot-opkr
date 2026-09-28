from pathlib import Path

root = Path(__file__).resolve().parent

# Dashboard: preserve an already-applied collapse UI; only add it if missing.
ui = root / "app/src/main/java/com/indexalert/app/DashboardUiV11.kt"
text = ui.read_text()
if "var probabilityExpanded by remember(s.rule.id)" not in text:
    text = text.replace(
        'private fun IndexCardV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String, refreshKey: String) {\n    val alertTriggered =',
        'private fun IndexCardV19(s: IndexSnapshot, movers: List<LaggardItem>, moverStatus: String, refreshKey: String) {\n    var probabilityExpanded by remember(s.rule.id) { mutableStateOf(false) }\n    val alertTriggered ='
    )
if 'Text(if (probabilityExpanded) "확률 분석 ▲ 접기" else "확률 분석 ▼ 펼치기")' not in text:
    old = '''            NextDayProbabilitySection(s.rule.id, refreshKey)\n            ExtendedSessionProbabilitySection(s.rule.id, refreshKey)\n            AfterOpenProbabilitySection(s.rule.id, refreshKey)\n            if (s.rule.id == "kospi100") {\n                KospiOneMonthProbabilitySection(refreshKey)\n            }\n            MonthlyChartSection(s.rule.id)'''
    new = '''            if (s.rule.id in setOf("sp500", "ndx", "djdiv", "kospi100")) {\n                Spacer(Modifier.height(10.dp))\n                OutlinedButton(\n                    onClick = { probabilityExpanded = !probabilityExpanded },\n                    modifier = Modifier.fillMaxWidth()\n                ) {\n                    Text(if (probabilityExpanded) "확률 분석 ▲ 접기" else "확률 분석 ▼ 펼치기")\n                }\n                if (probabilityExpanded) {\n                    if (s.rule.id in setOf("sp500", "ndx", "djdiv")) {\n                        NextDayProbabilitySection(s.rule.id, refreshKey)\n                        ExtendedSessionProbabilitySection(s.rule.id, refreshKey)\n                        AfterOpenProbabilitySection(s.rule.id, refreshKey)\n                    } else if (s.rule.id == "kospi100") {\n                        ExtendedSessionProbabilitySection(s.rule.id, refreshKey)\n                        KospiOneMonthProbabilitySection(refreshKey)\n                    }\n                }\n            }\n            MonthlyChartSection(s.rule.id)'''
    if old not in text:
        raise SystemExit("Dashboard probability block not found and collapse UI missing")
    text = text.replace(old, new)
ui.write_text(text)

# All probability panels use a white surface with black content so every numeric
# probability remains black even when the phone is in dark mode.
replacements = {
    "NextDayProbability.kt": [
        (
            'colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)',
            'colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)'
        ),
        (
            'Card(Modifier.weight(1f)) {',
            'Card(Modifier.weight(1f), colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)) {'
        ),
        ('color = androidx.compose.ui.graphics.Color(0xFFD32F2F)', 'color = androidx.compose.ui.graphics.Color.Black'),
        ('color = androidx.compose.ui.graphics.Color(0xFF1565C0)', 'color = androidx.compose.ui.graphics.Color.Black'),
    ],
    "ExtendedSessionProbability.kt": [
        (
            'colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)',
            'colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)'
        ),
    ],
    "AfterOpenProbability.kt": [
        (
            'colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)',
            'colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)'
        ),
    ],
    "FirstHourProbability.kt": [
        (
            'colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)',
            'colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)'
        ),
    ],
    "KospiOneMonth.kt": [
        (
            'colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)',
            'colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.White, contentColor = androidx.compose.ui.graphics.Color.Black)'
        ),
    ],
}
for name, reps in replacements.items():
    path = root / "app/src/main/java/com/indexalert/app" / name
    text = path.read_text()
    for old, new in reps:
        text = text.replace(old, new)
    path.write_text(text)

# Version bump for the installable build.
gradle = root / "app/build.gradle.kts"
text = gradle.read_text()
text = text.replace('versionCode = 38', 'versionCode = 39')
text = text.replace('versionName = "3.8"', 'versionName = "3.9"')
gradle.write_text(text)

print("v3.9 probability collapse + black probability content patch applied")
