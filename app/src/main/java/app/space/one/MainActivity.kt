package app.space.one

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.math.BigDecimal
import java.math.BigInteger
import java.math.MathContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { Surface(Modifier.fillMaxSize()) {
            if (BuildConfig.IS_STANDALONE) CalculatorScreen() else HubScreen()
        } } }
    }
}

private val modules = listOf("Calculator", "Notes", "Scanner", "Calendar", "Files", "Music", "Recorder", "Diagnostics")

@Composable
private fun HubScreen() {
    var selected by remember { mutableStateOf(false) }
    if (selected) {
        Column(Modifier.fillMaxSize().padding(20.dp)) {
            Button(onClick = { selected = false }) { Text("← Home") }
            CalculatorScreen()
        }
        return
    }
    Column(Modifier.fillMaxSize().padding(24.dp)) {
        Text("MySpace One", fontSize = 30.sp, fontWeight = FontWeight.Bold)
        Text("Your private, on-device workspace", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(20.dp))
        LazyVerticalGrid(columns = GridCells.Fixed(2), verticalArrangement = Arrangement.spacedBy(12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            items(modules) { module ->
                Card(onClick = { if (module == "Calculator") selected = true }, modifier = Modifier.height(112.dp)) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.Center) {
                        Text(module, fontWeight = FontWeight.SemiBold, fontSize = 18.sp)
                        Text(if (module == "Calculator") "Ready to use" else "Coming in the next build", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Text("Private by design · works offline", fontSize = 13.sp)
    }
}

@Composable
private fun CalculatorScreen() {
    var expression by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf("") }
    val keys = listOf("AC", "⌫", "%", "÷", "7", "8", "9", "×", "4", "5", "6", "−", "1", "2", "3", "+", "±", "0", ".", "=")
    Column(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.Bottom) {
        Text(expression.ifEmpty { "0" }, modifier = Modifier.fillMaxWidth(), fontSize = 32.sp)
        Text(answer, modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp), fontSize = 24.sp, color = MaterialTheme.colorScheme.primary)
        keys.chunked(4).forEach { row ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                row.forEach { key ->
                    Button(onClick = {
                        when (key) {
                            "AC" -> { expression = ""; answer = "" }
                            "⌫" -> { expression = expression.dropLast(1); answer = "" }
                            "=" -> answer = runCatching { evaluate(expression) }.getOrElse { "Error" }
                            "±" -> expression = if (expression.startsWith("-")) expression.drop(1) else "-$expression"
                            else -> { expression += key; answer = "" }
                        }
                    }, modifier = Modifier.weight(1f).padding(vertical = 3.dp)) { Text(key, fontSize = 17.sp) }
                }
            }
        }
    }
}

/** Small deterministic decimal evaluator; parser is intentionally isolated for future spec expansion. */
internal fun evaluate(source: String): String {
    val text = source.replace('×', '*').replace('÷', '/')
    require(text.isNotBlank())
    val parser = DecimalParser(text)
    val result = parser.expression()
    require(parser.atEnd())
    return result.decimal().stripTrailingZeros().toPlainString()
}

private data class ExactNumber private constructor(val numerator: BigInteger, val denominator: BigInteger) {
    fun plus(other: ExactNumber) = of(numerator * other.denominator + other.numerator * denominator, denominator * other.denominator)
    fun minus(other: ExactNumber) = of(numerator * other.denominator - other.numerator * denominator, denominator * other.denominator)
    fun times(other: ExactNumber) = of(numerator * other.numerator, denominator * other.denominator)
    fun dividedBy(other: ExactNumber): ExactNumber { require(other.numerator != BigInteger.ZERO); return of(numerator * other.denominator, denominator * other.numerator) }
    fun negate() = of(numerator.negate(), denominator)
    fun decimal() = BigDecimal(numerator).divide(BigDecimal(denominator), MathContext.DECIMAL128)
    companion object {
        fun of(n: BigInteger, d: BigInteger): ExactNumber {
            require(d != BigInteger.ZERO)
            val sign = if (d.signum() < 0) BigInteger.valueOf(-1) else BigInteger.ONE
            val nn = n * sign; val dd = d * sign
            val gcd = nn.gcd(dd)
            return ExactNumber(nn / gcd, dd / gcd)
        }
        fun parse(s: String): ExactNumber {
            val decimal = s.toBigDecimal().stripTrailingZeros()
            val scale = decimal.scale().coerceAtLeast(0)
            return of(decimal.movePointRight(scale).toBigIntegerExact(), BigInteger.TEN.pow(scale))
        }
    }
}

private class DecimalParser(private val input: String) {
    private var i = 0
    fun atEnd() = i == input.length
    fun expression(): ExactNumber {
        var value = term()
        while (i < input.length && (input[i] == '+' || input[i] == '-')) {
            val op = input[i++]
            val rhs = term()
            value = if (op == '+') value.plus(rhs) else value.minus(rhs)
        }
        return value
    }
    private fun term(): ExactNumber {
        var value = factor()
        while (i < input.length && (input[i] == '*' || input[i] == '/')) {
            val op = input[i++]
            val rhs = factor()
            value = if (op == '*') value.times(rhs) else value.dividedBy(rhs)
        }
        return value
    }
    private fun factor(): ExactNumber {
        if (i < input.length && (input[i] == '+' || input[i] == '-')) {
            val negative = input[i++] == '-'
            val v = factor()
            return if (negative) v.negate() else v
        }
        if (i < input.length && input[i] == '(') {
            i++
            val value = expression()
            require(i < input.length && input[i++] == ')')
            return value
        }
        val start = i
        while (i < input.length && (input[i].isDigit() || input[i] == '.')) i++
        require(i > start)
        return ExactNumber.parse(input.substring(start, i))
    }
}
