package app.space.one

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier

/** Calculator-only application entry point. Full-app screens do not compile into this flavor. */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MySpaceTheme {
                Surface(Modifier.fillMaxSize()) {
                    val store = remember { LocalStore(applicationContext) }
                    CalculatorScreen(store, back = {}, standalone = true)
                }
            }
        }
    }
}
