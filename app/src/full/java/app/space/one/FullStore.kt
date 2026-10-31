package app.space.one

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

internal data class SavedNote(val id: Long, val title: String, val body: String, val updatedAt: Long)
internal data class SavedEvent(val id: Long, val title: String, val whenText: String)

/** Full-app-only local records. This source set is excluded from MyCalc builds. */
internal class FullStore(context: Context) {
    private val prefs = context.getSharedPreferences("myspace-local-v1", Context.MODE_PRIVATE)
    fun notes(): List<SavedNote> = array("notes").let { rows ->
        (0 until rows.length()).mapNotNull { i -> runCatching {
            rows.getJSONObject(i).let { SavedNote(it.getLong("id"), it.getString("title"), it.getString("body"), it.getLong("updatedAt")) }
        }.getOrNull() }.sortedByDescending { it.updatedAt }
    }
    fun saveNote(note: SavedNote) {
        val json = JSONArray()
        (notes().filterNot { it.id == note.id } + note).forEach { json.put(JSONObject().put("id", it.id).put("title", it.title).put("body", it.body).put("updatedAt", it.updatedAt)) }
        prefs.edit().putString("notes", json.toString()).apply()
    }
    fun deleteNote(id: Long) {
        val json = JSONArray()
        notes().filterNot { it.id == id }.forEach { json.put(JSONObject().put("id", it.id).put("title", it.title).put("body", it.body).put("updatedAt", it.updatedAt)) }
        prefs.edit().putString("notes", json.toString()).apply()
    }
    fun events(): List<SavedEvent> = array("events").let { rows ->
        (0 until rows.length()).mapNotNull { i -> runCatching {
            rows.getJSONObject(i).let { SavedEvent(it.getLong("id"), it.getString("title"), it.getString("whenText")) }
        }.getOrNull() }.sortedBy { it.whenText }
    }
    fun saveEvent(event: SavedEvent) {
        val json = JSONArray()
        (events().filterNot { it.id == event.id } + event).sortedBy { it.whenText }.forEach {
            json.put(JSONObject().put("id", it.id).put("title", it.title).put("whenText", it.whenText))
        }
        prefs.edit().putString("events", json.toString()).apply()
    }
    fun deleteEvent(id: Long) {
        val json = JSONArray()
        events().filterNot { it.id == id }.forEach { json.put(JSONObject().put("id", it.id).put("title", it.title).put("whenText", it.whenText)) }
        prefs.edit().putString("events", json.toString()).apply()
    }
    private fun array(key: String) = runCatching { JSONArray(prefs.getString(key, "[]")) }.getOrElse { JSONArray() }
}
