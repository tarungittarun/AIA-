import java.time.Instant

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "app.space.one"
    compileSdk = 36

    defaultConfig {
        applicationId = "app.space.one"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        resourceConfigurations += listOf("en", "en-rIN")
        buildConfigField("String", "PROVENANCE_SHA", "\"${providers.environmentVariable("GITHUB_SHA").orElse("local").get()}\"")
        buildConfigField("String", "BUILD_TIME", "\"${Instant.now()}\"")
    }

    flavorDimensions += "dist"
    productFlavors {
        create("full") {
            dimension = "dist"
            applicationId = "app.space.one"
            resValue("string", "app_name", "MySpace One")
            buildConfigField("boolean", "IS_STANDALONE", "false")
        }
        create("mycalc") {
            dimension = "dist"
            applicationId = "app.space.calc"
            resValue("string", "app_name", "MyCalc")
            buildConfigField("boolean", "IS_STANDALONE", "true")
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    debugImplementation(libs.androidx.compose.ui.tooling)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
    testImplementation(libs.junit)
}
