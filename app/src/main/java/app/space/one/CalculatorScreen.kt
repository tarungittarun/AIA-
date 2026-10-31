package app.space.one

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.Button
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.math.BigDecimal
import java.text.NumberFormat
import java.util.Locale

@Composable
internal fun MySpaceTheme(content: @Composable () -> Unit) {
    val dark = isSystemInDarkTheme()
    val scheme = if (Build.VERSION.SDK_INT >= 31) {
        if (dark) dynamicDarkColorScheme(LocalContext.current) else dynamicLightColorScheme(LocalContext.current)
    } else if (dark) darkColorScheme() else lightColorScheme()
    MaterialTheme(colorScheme = scheme, content = content)
}

private fun formatDisplay(value: String): String {
    if (value.isBlank()) return value
    if (value.contains('E', ignoreCase = true)) return value
    return runCatching {
        NumberFormat.getNumberInstance(Locale.getDefault()).apply { isGroupingUsed = true; maximumFractionDigits = 10; minimumFractionDigits = 0 }.format(BigDecimal(value))
    }.getOrDefault(value)
}


@Composable
internal fun AppTopBar(title: String, back: () -> Unit, trailing: @Composable (() -> Unit)? = null) {
    Row(Modifier.fillMaxWidth().padding(bottom = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
        TextButton(onClick = back) { Text("‹ Home") }
        Text(title, fontWeight = FontWeight.SemiBold, fontSize = 19.sp)
        if (trailing != null) trailing() else Spacer(Modifier.size(72.dp))
    }
}


@Composable
internal fun CalculatorScreen(store: LocalStore, back: () -> Unit, standalone: Boolean) {
    val clipboard = LocalClipboardManager.current
    var field by remember { mutableStateOf(TextFieldValue("")) }
    var answer by remember { mutableStateOf("") }
    var error by remember { mutableStateOf("") }
    var showHistory by remember { mutableStateOf(false) }
    var degrees by remember { mutableStateOf(store.angleInDegrees()) }
    var memory by remember { mutableStateOf(store.memoryValue()) }
    var inverse by remember { mutableStateOf(false) }
    var showScientific by remember { mutableStateOf(false) }
    var lastResult by remember { mutableStateOf("") }
    var repeatOperator by remember { mutableStateOf("") }
    var repeatOperand by remember { mutableStateOf("") }
    val history = remember { mutableStateListOf<SavedCalculation>().apply { addAll(store.calculations()) } }
    fun update(value: TextFieldValue) {
        if (value.text.length <= 512) {
            field = value
            lastResult = ""
            repeatOperator = ""
            repeatOperand = ""
            answer = CalculatorEngine.liveAnswer(value.text, degrees)
            error = ""
        }
    }
    fun insert(token: String) {
        val start = field.selection.min.coerceIn(0, field.text.length)
        val end = field.selection.max.coerceIn(start, field.text.length)
        val operators = setOf("+", "−", "×", "÷", "^")
        if (start == end && start > 0 && token in operators && field.text.substring(start - 1, start) in operators) {
            val previous = field.text[start - 1]
            if (!(token == "−" && previous in charArrayOf('×', '÷', '^'))) {
                val text = field.text.replaceRange(start - 1, start, token)
                update(TextFieldValue(text, TextRange(start)))
                return
            }
        }
        val text = field.text.replaceRange(start, end, token)
        update(TextFieldValue(text, TextRange(start + token.length)))
    }
    fun calculate() {
        val expression = field.text
        val pending = Regex("([+−×÷])$").find(expression)?.groupValues?.get(1).orEmpty()
        val unaryMinusPending = pending == "−" && expression.dropLast(1).lastOrNull() in listOf('×', '÷', '^', '(')
        val repeated = expression == lastResult && repeatOperator.isNotEmpty()
        val evaluationInput = when {
            repeated -> "$expression$repeatOperator$repeatOperand"
            pending.isNotEmpty() && !unaryMinusPending -> {
                repeatOperator = pending
                repeatOperand = Regex("(?:\\d+(?:\\.\\d*)?|\\.\\d+|\\))+$").find(expression.dropLast(1))?.value ?: "1"
                expression
            }
            else -> expression
        }
        val result = runCatching { CalculatorEngine.evaluate(evaluationInput, degrees) }.getOrElse {
            error = it.message ?: "Check the expression"
            answer = ""
            val failed = SavedCalculation(expression, "Error: $error", System.currentTimeMillis())
            store.addCalculation(failed); history.add(0, failed)
            return
        }
        answer = result
        error = ""
        lastResult = result
        if (!repeated && pending.isEmpty()) {
            val op = Regex("[+−×÷](?!.*[+−×÷])").find(expression)?.value.orEmpty()
            if (op.isNotEmpty()) {
                repeatOperator = op
                repeatOperand = expression.substringAfterLast(op).ifBlank { "1" }
            }
        }
        val row = SavedCalculation(expression, result, System.currentTimeMillis())
        store.addCalculation(row)
        history.add(0, row)
        field = TextFieldValue(result, TextRange(result.length))
    }

    Column(Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 8.dp), verticalArrangement = Arrangement.Bottom) {
        if (!standalone) AppTopBar("Calculator", back)
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = { showHistory = true }) { Text("History (${history.size})") }
            TextButton(onClick = { showScientific = !showScientific }) { Text(if (showScientific) "Basic" else "Sci") }
            TextButton(onClick = { degrees = !degrees; store.setAngleInDegrees(degrees); answer = CalculatorEngine.liveAnswer(field.text, degrees) }) { Text(if (degrees) "DEG" else "RAD") }
        }
        BasicTextField(
            value = field,
            onValueChange = { update(it) },
            modifier = Modifier.fillMaxWidth().padding(top = 10.dp, bottom = 8.dp),
            textStyle = MaterialTheme.typography.headlineMedium.copy(color = MaterialTheme.colorScheme.onSurface),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Ascii),
            readOnly = true,
            decorationBox = { inner ->
                if (field.text.isEmpty()) Text("0", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                inner()
            }
        )
        Text(if (error.isNotEmpty()) error else formatDisplay(answer), modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), fontSize = 24.sp, color = if (error.isNotEmpty()) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary)
        Row(Modifier.fillMaxWidth().padding(bottom = 8.dp), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(if (memory.isBlank()) "M —" else "M ${memory.take(14)}", modifier = Modifier.weight(1f), color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 13.sp)
            TextButton(onClick = { if (answer.isNotBlank()) {
                memory = runCatching { CalculatorEngine.evaluate("${if (memory.isBlank()) "0" else memory}+$answer", degrees) }.getOrDefault(answer)
                store.setMemoryValue(memory)
            } }) { Text("M+") }
            TextButton(onClick = { if (memory.isNotBlank()) insert(memory) }) { Text("MR") }
            TextButton(onClick = { memory = ""; store.setMemoryValue("") }) { Text("MC") }
        }
        if (field.selection.start != field.selection.end) {
            val selected = field.text.substring(field.selection.min, field.selection.max)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                TextButton(onClick = { clipboard.setText(AnnotatedString(selected)) }) { Text("Copy") }
                TextButton(onClick = { update(TextFieldValue(field.text.removeRange(field.selection.min, field.selection.max), TextRange(field.selection.min))) }) { Text("Cut") }
                TextButton(onClick = { if (selected.isNotBlank()) {
                    val selectedValue = runCatching { CalculatorEngine.evaluate(selected, degrees) }.getOrNull()
                    if (selectedValue != null) { memory = runCatching { CalculatorEngine.evaluate("${if (memory.isBlank()) "0" else memory}+$selectedValue", degrees) }.getOrDefault(selectedValue); store.setMemoryValue(memory) }
                } }) { Text("MAdd") }
                TextButton(onClick = { if (memory.isNotBlank()) insert(memory) }) { Text("MUse") }
                TextButton(onClick = { clipboard.getText()?.text?.let { insert(it) } }) { Text("Paste") }
            }
        }
        val rows = listOf(listOf("AC", "⌫", "(", ")"), listOf("7", "8", "9", "÷"), listOf("4", "5", "6", "×"), listOf("1", "2", "3", "−"), listOf("%", "0", ".", "+"))
        rows.forEach { row ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                row.forEach { key ->
                    OutlinedButton(onClick = {
                        when (key) {
                            "AC" -> { update(TextFieldValue("")); error = "" }
                            "⌫" -> {
                                val start = field.selection.min; val end = field.selection.max
                                if (start != end) update(TextFieldValue(field.text.removeRange(start, end), TextRange(start)))
                                else if (start > 0) update(TextFieldValue(field.text.removeRange(start - 1, start), TextRange(start - 1)))
                            }
                            "(" -> insert(if (field.text.lastOrNull()?.let { it.isDigit() || it == ')' } == true) "×(" else "(")
                            ")" -> insert(")")
                            else -> insert(key)
                        }
                    }, modifier = Modifier.weight(1f).height(54.dp), shape = RoundedCornerShape(15.dp)) { Text(key, fontSize = 19.sp) }
                }
            }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
            OutlinedButton(onClick = { insert("^2") }, modifier = Modifier.weight(1f).height(54.dp)) { Text("x²") }
            OutlinedButton(onClick = { insert("^") }, modifier = Modifier.weight(1f).height(54.dp)) { Text("xʸ") }
            OutlinedButton(onClick = { insert("√(") }, modifier = Modifier.weight(1f).height(54.dp)) { Text("√") }
            Button(onClick = { calculate() }, modifier = Modifier.weight(1f).height(54.dp), shape = RoundedCornerShape(15.dp)) { Text("=", fontSize = 22.sp) }
        }
        if (showScientific) Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(2.dp)) {
            listOf("INV", "sin", "cos", "tan", "ln", "log", "π", "!").forEach { key ->
                TextButton(onClick = {
                    when (key) {
                        "INV" -> inverse = !inverse
                        "!" -> insert("!")
                        "π" -> insert("π")
                        else -> { insert((if (inverse) "a$key" else key) + "("); inverse = false }
                    }
                }, modifier = Modifier.weight(1f)) { Text(if (key == "INV" && inverse) "INV✓" else key, fontSize = 11.sp) }
            }
        }
    }
    if (showHistory) {
        AlertDialog(onDismissRequest = { showHistory = false }, title = { Text("Calculation history") }, text = {
            if (history.isEmpty()) Text("Solved calculations appear here.") else LazyColumn(Modifier.height(360.dp)) {
                items(history) { item ->
                    Column(Modifier.fillMaxWidth().clickable {
                        field = TextFieldValue(item.expression, TextRange(item.expression.length)); answer = item.result; error = ""; showHistory = false
                    }.padding(vertical = 10.dp)) {
                        Text(item.expression, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(formatDisplay(item.result), fontSize = 20.sp)
                        Divider()
                    }
                }
            }
        }, confirmButton = { TextButton(onClick = { showHistory = false }) { Text("Close") } }, dismissButton = {
            TextButton(onClick = { store.clearCalculations(); history.clear() }) { Text("Clear") }
        })
    }
}

