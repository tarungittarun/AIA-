package app.space.one

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

internal data class SavedCalculation(val expression: String, val result: String, val at: Long)

/** Calculator-only app-private persistence shared by the full and MyCalc variants. */
internal class LocalStore(context: Context) {
    private val prefs = context.getSharedPreferences("myspace-local-v1", Context.MODE_PRIVATE)

    fun calculations(): List<SavedCalculation> = readArray("calc-history").let { rows ->
        (0 until rows.length()).mapNotNull { i -> runCatching {
            rows.getJSONObject(i).let { SavedCalculation(it.getString("expression"), it.getString("result"), it.getLong("at")) }
        }.getOrNull() }
    }
    fun clearCalculations() { prefs.edit().putString("calc-history", "[]").apply() }
    fun memoryValue(): String = prefs.getString("calc-memory", "") ?: ""
    fun setMemoryValue(value: String) { prefs.edit().putString("calc-memory", value).apply() }
    fun angleInDegrees(): Boolean = prefs.getBoolean("calc-degrees", true)
    fun setAngleInDegrees(value: Boolean) { prefs.edit().putBoolean("calc-degrees", value).apply() }
    fun addCalculation(row: SavedCalculation) {
        val old = calculations().toMutableList()
        old.add(0, row.copy(expression = row.expression.replace('×', '*').replace('÷', '/').replace('−', '-')))
        val json = JSONArray()
        old.take(100).forEach { json.put(JSONObject().put("expression", it.expression).put("result", it.result).put("at", it.at)) }
        prefs.edit().putString("calc-history", json.toString()).apply()
    }
    private fun readArray(key: String) = runCatching { JSONArray(prefs.getString(key, "[]")) }.getOrElse { JSONArray() }
}
