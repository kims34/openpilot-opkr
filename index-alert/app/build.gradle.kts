fun envString(name: String): String = (System.getenv(name) ?: "").replace("\\", "\\\\").replace("\"", "\\\"")

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "com.indexalert.app"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.indexalert.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 4
        versionName = "0.4"
        val backendUrl = envString("INDEXALERT_BACKEND_URL").ifBlank { "https://indexalert-runtime-production.up.railway.app" }
        buildConfigField("String", "INDEXALERT_BACKEND_URL", "\"$backendUrl\"")
        buildConfigField("String", "FIREBASE_APP_ID", "\"${envString("FIREBASE_APP_ID")}\"")
        buildConfigField("String", "FIREBASE_API_KEY", "\"${envString("FIREBASE_API_KEY")}\"")
        buildConfigField("String", "FIREBASE_PROJECT_ID", "\"${envString("FIREBASE_PROJECT_ID")}\"")
        buildConfigField("String", "FIREBASE_SENDER_ID", "\"${envString("FIREBASE_SENDER_ID")}\"")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true; buildConfig = true }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}
dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.activity:activity-compose:1.10.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")
    implementation("androidx.work:work-runtime-ktx:2.10.0")
    implementation("androidx.core:core-ktx:1.15.0")
    implementation(platform("com.google.firebase:firebase-bom:34.3.0"))
    implementation("com.google.firebase:firebase-messaging")
}
