package app.space.one

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import java.io.File

/** Local AAC recorder that remains active if the Activity is backgrounded or recreated. */
class RecorderService : Service() {
    private var recorder: MediaRecorder? = null
    private var output: File? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startRecording(intent.getStringExtra(EXTRA_PATH))
            ACTION_PAUSE -> pauseRecording()
            ACTION_RESUME -> resumeRecording()
            ACTION_STOP -> stopRecording()
            ACTION_MARK -> if (Companion.active && !Companion.paused && Companion.markers.size < 200) {
                Companion.markers += System.currentTimeMillis() - Companion.startedAt - Companion.totalPausedMs
            }
        }
        return START_NOT_STICKY
    }

    private fun startRecording(path: String?) {
        if (recorder != null) return
        createChannel()
        output = path?.let(::File) ?: File(File(filesDir, "Recordings"), "REC-${System.currentTimeMillis()}.m4a")
        output?.parentFile?.mkdirs()
        startForeground(NOTIFICATION_ID, notification(paused = false))
        try {
            @Suppress("DEPRECATION")
            val instance = if (Build.VERSION.SDK_INT >= 31) MediaRecorder(this) else MediaRecorder()
            instance.setAudioSource(MediaRecorder.AudioSource.MIC)
            instance.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            instance.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            instance.setAudioChannels(1)
            instance.setAudioSamplingRate(48_000)
            instance.setAudioEncodingBitRate(96_000)
            instance.setOutputFile(output!!.absolutePath)
            instance.prepare()
            instance.start()
            recorder = instance
            Companion.startedAt = System.currentTimeMillis()
            Companion.totalPausedMs = 0L
            Companion.pauseStartedAt = 0L
            Companion.markers.clear()
            Companion.active = true
            Companion.paused = false
            refreshNotification(false)
        } catch (failure: Exception) {
            runCatching { recorder?.release() }
            recorder = null
            Companion.active = false
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }

    private fun pauseRecording() {
        if (!Companion.active || Companion.paused) return
        runCatching {
            recorder?.pause()
            Companion.paused = true
            Companion.pauseStartedAt = System.currentTimeMillis()
            refreshNotification(true)
        }
    }

    private fun resumeRecording() {
        if (!Companion.active || !Companion.paused) return
        runCatching {
            recorder?.resume()
            Companion.totalPausedMs += System.currentTimeMillis() - Companion.pauseStartedAt
            Companion.paused = false
            refreshNotification(false)
        }
    }

    private fun stopRecording() {
        if (recorder == null) { stopSelf(); return }
        runCatching { recorder?.stop() }
        recorder?.release()
        recorder = null
        Companion.active = false
        Companion.paused = false
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun notification(paused: Boolean): Notification {
        val stop = actionIntent(ACTION_STOP, 1)
        val toggleAction = if (paused) ACTION_RESUME else ACTION_PAUSE
        val toggle = actionIntent(toggleAction, 2)
        val builder = if (Build.VERSION.SDK_INT >= 26) Notification.Builder(this, CHANNEL_ID) else Notification.Builder(this)
        builder.setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(if (paused) "Recording paused" else "Recording — MySpace One")
            .setContentText(if (paused) "Audio is saved on this device" else "Tap to return · audio stays on this device")
            .setOngoing(true)
            .addAction(Notification.Action.Builder(android.R.drawable.ic_media_pause, if (paused) "Resume" else "Pause", toggle).build())
            .addAction(Notification.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "Stop", stop).build())
        return builder.build()
    }

    private fun actionIntent(action: String, requestCode: Int): PendingIntent {
        val intent = Intent(this, RecorderService::class.java).setAction(action)
        return PendingIntent.getService(this, requestCode, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
    }

    private fun refreshNotification(paused: Boolean) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification(paused))
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            getSystemService(NotificationManager::class.java).createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "Recording", NotificationManager.IMPORTANCE_LOW).apply { description = "Active voice recording controls" }
            )
        }
    }

    override fun onDestroy() {
        if (recorder != null) {
            runCatching { recorder?.stop() }
            recorder?.release()
            recorder = null
        }
        Companion.active = false
        Companion.paused = false
        super.onDestroy()
    }

    companion object {
        const val ACTION_START = "app.space.one.recorder.START"
        const val ACTION_PAUSE = "app.space.one.recorder.PAUSE"
        const val ACTION_RESUME = "app.space.one.recorder.RESUME"
        const val ACTION_STOP = "app.space.one.recorder.STOP"
        const val ACTION_MARK = "app.space.one.recorder.MARK"
        const val EXTRA_PATH = "output-path"
        const val CHANNEL_ID = "recording"
        const val NOTIFICATION_ID = 4201
        @Volatile var active: Boolean = false
        @Volatile var paused: Boolean = false
        @Volatile var startedAt: Long = 0L
        @Volatile var pauseStartedAt: Long = 0L
        @Volatile var totalPausedMs: Long = 0L
        val markers = mutableListOf<Long>()
    }
}
