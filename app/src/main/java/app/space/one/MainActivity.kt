package app.space.one

import android.content.Intent
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.content.pm.PackageManager
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.util.Locale

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(Modifier.fillMaxSize()) {
                    val store = remember { LocalStore(applicationContext) }
                    var route by remember { mutableStateOf(if (BuildConfig.IS_STANDALONE) "Calculator" else "Home") }
                    when (route) {
                        "Home" -> HubScreen(open = { route = it })
                        "Calculator" -> CalculatorScreen(store, back = { route = if (BuildConfig.IS_STANDALONE) "Calculator" else "Home" }, standalone = BuildConfig.IS_STANDALONE)
                        "Notes" -> NotesScreen(store, back = { route = "Home" })
                        else -> ModuleScreen(route, store, back = { route = "Home" })
                    }
                }
            }
        }
    }
}

private val modules = listOf("Calculator", "Notes", "Scanner", "Calendar", "Files", "Music", "Recorder", "Diagnostics")

@Composable
private fun HubScreen(open: (String) -> Unit) {
    Column(Modifier.fillMaxSize().padding(horizontal = 22.dp, vertical = 28.dp)) {
        Text("MySpace One", fontSize = 31.sp, fontWeight = FontWeight.Bold)
        Text("A private workspace that stays on this device", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(24.dp))
        LazyVerticalGrid(columns = GridCells.Fixed(2), verticalArrangement = Arrangement.spacedBy(12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            items(modules) { module ->
                Card(onClick = { open(module) }, modifier = Modifier.height(116.dp), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer)) {
                    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.Center) {
                        Text(module, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                        Text(when (module) { "Calculator" -> "Exact, offline calculations"; "Notes" -> "Write and keep notes here"; else -> "Open workspace" }, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 13.sp)
                    }
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Text("No sign-in · No ads · No network", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun AppTopBar(title: String, back: () -> Unit, trailing: @Composable (() -> Unit)? = null) {
    Row(Modifier.fillMaxWidth().padding(bottom = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
        TextButton(onClick = back) { Text("‹ Home") }
        Text(title, fontWeight = FontWeight.SemiBold, fontSize = 19.sp)
        if (trailing != null) trailing() else Spacer(Modifier.size(72.dp))
    }
}

@Composable
private fun CalculatorScreen(store: LocalStore, back: () -> Unit, standalone: Boolean) {
    var field by remember { mutableStateOf(TextFieldValue("")) }
    var answer by remember { mutableStateOf("") }
    var error by remember { mutableStateOf("") }
    var showHistory by remember { mutableStateOf(false) }
    var degrees by remember { mutableStateOf(true) }
    val history = remember { mutableStateListOf<SavedCalculation>().apply { addAll(store.calculations()) } }
    fun update(value: TextFieldValue) {
        if (value.text.length <= 512) {
            field = value
            answer = CalculatorEngine.liveAnswer(value.text, degrees)
            error = ""
        }
    }
    fun insert(token: String) {
        val start = field.selection.min.coerceIn(0, field.text.length)
        val end = field.selection.max.coerceIn(start, field.text.length)
        val text = field.text.replaceRange(start, end, token)
        update(TextFieldValue(text, TextRange(start + token.length)))
    }
    fun calculate() {
        val expression = field.text
        val result = runCatching { CalculatorEngine.evaluate(expression, degrees) }.getOrElse {
            error = it.message ?: "Check the expression"
            answer = ""
            return
        }
        answer = result
        error = ""
        val row = SavedCalculation(expression, result, System.currentTimeMillis())
        store.addCalculation(row)
        history.add(0, row)
        field = TextFieldValue(result, TextRange(result.length))
    }

    Column(Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 8.dp), verticalArrangement = Arrangement.Bottom) {
        if (!standalone) AppTopBar("Calculator", back)
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = { showHistory = true }) { Text("History (${history.size})") }
            TextButton(onClick = { degrees = !degrees }) { Text(if (degrees) "DEG" else "RAD") }
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
        Text(if (error.isNotEmpty()) error else answer, modifier = Modifier.fillMaxWidth().padding(bottom = 14.dp), fontSize = 24.sp, color = if (error.isNotEmpty()) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary)
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
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf("sin(", "cos(", "tan(", "ln(", "log(", "π").forEach { fn ->
                TextButton(onClick = { insert(fn) }, modifier = Modifier.weight(1f)) { Text(fn, fontSize = 12.sp) }
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
                        Text(item.result, fontSize = 20.sp)
                        Divider()
                    }
                }
            }
        }, confirmButton = { TextButton(onClick = { showHistory = false }) { Text("Close") } }, dismissButton = {
            TextButton(onClick = { store.clearCalculations(); history.clear() }) { Text("Clear") }
        })
    }
}

@Composable
private fun NotesScreen(store: LocalStore, back: () -> Unit) {
    val notes = remember { mutableStateListOf<SavedNote>().apply { addAll(store.notes()) } }
    var current by remember { mutableStateOf<SavedNote?>(null) }
    var title by remember { mutableStateOf("") }
    var body by remember { mutableStateOf("") }
    var editing by remember { mutableStateOf(false) }
    fun start(note: SavedNote?) {
        current = note; title = note?.title.orEmpty(); body = note?.body.orEmpty(); editing = true
    }
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        AppTopBar(if (editing) "Edit note" else "Notes", if (editing) { { editing = false } } else back,
            trailing = { TextButton(onClick = { start(null) }) { Text("+ New") } })
        if (editing) {
            OutlinedTextField(value = title, onValueChange = { title = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Title") }, singleLine = true)
            Spacer(Modifier.height(10.dp))
            OutlinedTextField(value = body, onValueChange = { body = it }, modifier = Modifier.fillMaxWidth().weight(1f), label = { Text("Note") })
            Button(onClick = {
                val saved = SavedNote(current?.id ?: System.currentTimeMillis(), title.trim(), body, System.currentTimeMillis())
                store.saveNote(saved)
                notes.removeAll { it.id == saved.id }; notes.add(0, saved); editing = false
            }, modifier = Modifier.fillMaxWidth(), enabled = title.isNotBlank() || body.isNotBlank()) { Text("Save on this device") }
        } else if (notes.isEmpty()) {
            Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Your notes stay private", fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
                Text("Create a note to get started.")
                Spacer(Modifier.height(12.dp)); Button(onClick = { start(null) }) { Text("Create note") }
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                items(notes, key = { it.id }) { note ->
                    Card(Modifier.fillMaxWidth().clickable { start(note) }) {
                        Column(Modifier.padding(16.dp)) {
                            Text(note.title.ifBlank { "Untitled" }, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                            Text(note.body.take(240), maxLines = 3, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            TextButton(onClick = { store.deleteNote(note.id); notes.remove(note) }) { Text("Move to trash") }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ModuleScreen(module: String, store: LocalStore, back: () -> Unit) {
    val context = LocalContext.current
    var pickedUri by remember { mutableStateOf<Uri?>(null) }
    var message by remember { mutableStateOf("") }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        pickedUri = uri
        if (uri != null) runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
    }
    when (module) {
        "Calendar" -> CalendarScreen(store, back)
        "Music" -> MusicScreen(context, back)
        "Recorder" -> RecorderScreen(context, back)
        else -> Column(Modifier.fillMaxSize().padding(20.dp)) {
            AppTopBar(module, back)
            when (module) {
                "Files" -> {
                    Text("Browse files using Android's document picker. The app sees only items you select.")
                    Spacer(Modifier.height(16.dp)); Button(onClick = { picker.launch(arrayOf("*/*")) }) { Text("Browse files") }
                    pickedUri?.let { Text("Selected: ${it.lastPathSegment ?: it}", modifier = Modifier.padding(top = 12.dp)) }
                }
                "Scanner" -> {
                    Text("Import a page image or PDF from this device.")
                    Spacer(Modifier.height(16.dp)); Button(onClick = { picker.launch(arrayOf("image/*", "application/pdf")) }) { Text("Import document") }
                    pickedUri?.let { Text("Imported source: ${it.lastPathSegment ?: it}") }
                }
                "Diagnostics" -> {
                    Text("MySpace One diagnostics", fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
                    Text("Version ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                    Text("Build time: ${BuildConfig.BUILD_TIME}")
                    Text("Source revision: ${BuildConfig.PROVENANCE_SHA}")
                    Text("Network permission: absent")
                }
                else -> Text("Settings", fontSize = 22.sp)
            }
        }
    }
}

@Composable
private fun CalendarScreen(store: LocalStore, back: () -> Unit) {
    val events = remember { mutableStateListOf<SavedEvent>().apply { addAll(store.events()) } }
    var title by remember { mutableStateOf("") }
    var date by remember { mutableStateOf(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"))) }
    var error by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().padding(18.dp)) {
        AppTopBar("Calendar", back)
        Text("Local events", fontSize = 23.sp, fontWeight = FontWeight.SemiBold)
        OutlinedTextField(title, { title = it }, modifier = Modifier.fillMaxWidth().padding(top = 12.dp), label = { Text("Event title") }, singleLine = true)
        OutlinedTextField(date, { date = it }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp), label = { Text("Date and time · yyyy-MM-dd HH:mm") }, singleLine = true)
        if (error.isNotEmpty()) Text(error, color = MaterialTheme.colorScheme.error)
        Button(onClick = {
            val valid = runCatching { LocalDateTime.parse(date, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")) }.isSuccess
            if (!valid || title.isBlank()) error = "Enter a title and a valid local date/time."
            else {
                val event = SavedEvent(System.currentTimeMillis(), title.trim(), date)
                store.saveEvent(event); events.add(event); events.sortBy { it.whenText }; title = ""; error = "Saved on this device."
            }
        }, modifier = Modifier.padding(top = 8.dp), enabled = title.isNotBlank()) { Text("Save event") }
        Text("Events are stored locally. Reminder scheduling is not enabled yet.", modifier = Modifier.padding(vertical = 12.dp), color = MaterialTheme.colorScheme.onSurfaceVariant)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(events, key = { it.id }) { event ->
                Card(Modifier.fillMaxWidth()) { Row(Modifier.fillMaxWidth().padding(14.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) { Text(event.title, fontWeight = FontWeight.SemiBold); Text(event.whenText, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                    TextButton(onClick = { store.deleteEvent(event.id); events.remove(event) }) { Text("Delete") }
                } }
            }
        }
    }
}

@Composable
private fun MusicScreen(context: android.content.Context, back: () -> Unit) {
    var audioUri by remember { mutableStateOf<Uri?>(null) }
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var playing by remember { mutableStateOf(false) }
    var ready by remember { mutableStateOf(false) }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        audioUri = uri; ready = false; playing = false
        player?.release(); player = null
        if (uri != null) {
            runCatching {
                MediaPlayer().also { mp ->
                    player = mp
                    mp.setDataSource(context, uri)
                    mp.setOnPreparedListener { ready = true }
                    mp.setOnCompletionListener { playing = false; it.seekTo(0) }
                    mp.prepareAsync()
                }
            }.onFailure { ready = false }
        }
    }
    androidx.compose.runtime.DisposableEffect(Unit) { onDispose { player?.release(); player = null } }
    Column(Modifier.fillMaxSize().padding(20.dp)) {
        AppTopBar("Music", back)
        Text("Play audio stored on your device", fontSize = 21.sp, fontWeight = FontWeight.SemiBold)
        Button(onClick = { picker.launch(arrayOf("audio/*")) }, modifier = Modifier.padding(top = 16.dp)) { Text("Choose audio") }
        audioUri?.let { uri ->
            Text(uri.lastPathSegment ?: "Selected audio", modifier = Modifier.padding(top = 12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                Button(enabled = ready, onClick = { player?.let { if (playing) { it.pause(); playing = false } else { it.start(); playing = true } } }) { Text(if (playing) "Pause" else "Play") }
                OutlinedButton(enabled = player != null, onClick = { player?.seekTo(0); player?.pause(); playing = false }) { Text("Stop") }
            }
            if (!ready) Text("Preparing selected audio…")
        }
    }
}

@Composable
private fun RecorderScreen(context: android.content.Context, back: () -> Unit) {
    var recorder by remember { mutableStateOf<MediaRecorder?>(null) }
    var recordingFile by remember { mutableStateOf<File?>(null) }
    var recording by remember { mutableStateOf(false) }
    var playback by remember { mutableStateOf<MediaPlayer?>(null) }
    var playing by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf("") }
    fun startRecording() {
        runCatching {
            val output = File(context.filesDir, "recording-${System.currentTimeMillis()}.m4a")
            val r = MediaRecorder()
            r.setAudioSource(MediaRecorder.AudioSource.MIC)
            r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            r.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            r.setOutputFile(output.absolutePath)
            r.prepare(); r.start()
            recorder = r; recordingFile = output; recording = true; error = ""
        }.onFailure { error = it.message ?: "Could not start recording" }
    }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) startRecording() else error = "Microphone permission was denied."
    }
    androidx.compose.runtime.DisposableEffect(Unit) { onDispose { runCatching { recorder?.stop() }; recorder?.release(); playback?.release() } }
    Column(Modifier.fillMaxSize().padding(20.dp)) {
        AppTopBar("Recorder", back)
        Text("Voice recorder", fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
        Text("Recordings are saved in app-private storage on this device.", modifier = Modifier.padding(top = 8.dp))
        Button(onClick = {
            if (recording) {
                runCatching { recorder?.stop() }.onFailure { error = "Recording was too short to save." }
                recorder?.release(); recorder = null; recording = false
            } else if (context.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) startRecording()
            else permission.launch(android.Manifest.permission.RECORD_AUDIO)
        }, modifier = Modifier.padding(top = 18.dp)) { Text(if (recording) "Stop recording" else "Start recording") }
        if (recordingFile != null && !recording) {
            Text("Saved: ${recordingFile?.name}", modifier = Modifier.padding(top = 12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = {
                    runCatching {
                        playback?.release()
                        MediaPlayer().also { mp -> playback = mp; mp.setDataSource(recordingFile!!.absolutePath); mp.setOnCompletionListener { playing = false }; mp.prepare(); mp.start(); playing = true }
                    }.onFailure { error = it.message ?: "Could not play recording" }
                }) { Text(if (playing) "Playing" else "Play recording") }
                OutlinedButton(onClick = { recordingFile?.delete(); recordingFile = null; playback?.release(); playback = null; playing = false }) { Text("Delete") }
            }
        }
        if (error.isNotEmpty()) Text(error, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
    }
}
