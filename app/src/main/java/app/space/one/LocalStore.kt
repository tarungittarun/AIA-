package app.space.one

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

internal data class SavedCalculation(val expression: String, val result: String, val at: Long)
internal data class SavedNote(val id: Long, val title: String, val body: String, val updatedAt: Long)

/** Private, app-scoped persistence. No account, network access, or shared-storage access. */
internal class LocalStore(context: Context) {
    private val prefs = context.getSharedPreferences("myspace-local-v1", Context.MODE_PRIVATE)

    fun calculations(): List<SavedCalculation> = readArray("calc-history").let { rows ->
        (0 until rows.length()).mapNotNull { i -> runCatching {
            rows.getJSONObject(i).let { SavedCalculation(it.getString("expression"), it.getString("result"), it.getLong("at")) }
        }.getOrNull() }
    }

    fun clearCalculations() { prefs.edit().putString("calc-history", "[]").apply() }

    fun addCalculation(row: SavedCalculation) {
        val old = calculations().toMutableList()
        old.add(0, row)
        val json = JSONArray()
        old.take(100).forEach { json.put(JSONObject().put("expression", it.expression).put("result", it.result).put("at", it.at)) }
        prefs.edit().putString("calc-history", json.toString()).apply()
    }

    fun notes(): List<SavedNote> = readArray("notes").let { rows ->
        (0 until rows.length()).mapNotNull { i -> runCatching {
            rows.getJSONObject(i).let { SavedNote(it.getLong("id"), it.getString("title"), it.getString("body"), it.getLong("updatedAt")) }
        }.getOrNull() }.sortedByDescending { it.updatedAt }
    }

    fun saveNote(note: SavedNote) {
        val rows = notes().filterNot { it.id == note.id }
        val json = JSONArray()
        (rows + note).forEach { json.put(JSONObject().put("id", it.id).put("title", it.title).put("body", it.body).put("updatedAt", it.updatedAt)) }
        prefs.edit().putString("notes", json.toString()).apply()
    }

    fun deleteNote(id: Long) = saveNotes(notes().filterNot { it.id == id })
    private fun saveNotes(notes: List<SavedNote>) {
        val json = JSONArray()
        notes.forEach { json.put(JSONObject().put("id", it.id).put("title", it.title).put("body", it.body).put("updatedAt", it.updatedAt)) }
        prefs.edit().putString("notes", json.toString()).apply()
    }
    private fun readArray(key: String) = runCatching { JSONArray(prefs.getString(key, "[]")) }.getOrElse { JSONArray() }
}
