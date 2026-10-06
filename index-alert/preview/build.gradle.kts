plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.indexalert.app"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.indexalert.preview"
        minSdk = 26
        targetSdk = 35
        versionCode = 48
        versionName = "4.8-preview"
        buildConfigField("String", "INDEXALERT_BACKEND_URL", "\"https://indexalert-runtime-production.up.railway.app\"")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
}
