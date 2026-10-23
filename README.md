# ⚡ AIA — AI Media & Video Generation Automation Engine

A high-performance repository containing automated AI generation engines and GitHub Actions cloud runner workflows for both **frame-by-frame animation** and **cinematic 1080p 60FPS video production**.

---

## 🎬 1. MonsterVerse: Godzilla x Kong 1080p 60FPS Video Pipeline

An automated video generation engine that renders a photorealistic, high-frame-rate MonsterVerse action sequence in **Full HD 1080p (1920×1080, 16:9) at 60 Frames Per Second**.

### Fed Prompt Specifications
* **Subject & Clash:** The titanic alpha-predator King Kong (*Godzilla x Kong: The New Empire* look, coarse silver-black fur coat, weathered chest scars, and industrial yellow **B.E.A.S.T. Glove** exoskeleton) battling Godzilla (*charcoal-grey reptilian hide, jagged maple-leaf dorsal plates*) in a smoke-filled, rain-soaked Times Square, New York City.
* **Camera Movement & Style:** Aggressive low-angle tracking shot from street level, violent handheld camera shake upon every massive B.E.A.S.T. Glove impact, dynamic close-ups of Kong’s fierce expression cut with wide anamorphic 2.39:1 letterboxed destruction shots.
* **Lighting & Atmosphere:** Cinematic low-key twilight lighting, cracked neon billboards reflecting in wet asphalt puddles, volumetric smoke, and blue atomic energy sparks slashing across skyscrapers.
* **Technical Output:** 1080p Full HD (1920×1080), 60.00 FPS, H.264 MP4 encoding, 16:9 aspect ratio.

### Deliverables:
* **Rendered Video File:** `output_video/godzilla_vs_kong_cinematic_1080p_60fps.mp4` (Full 1080p @ 60 FPS)
* **Cinematic Storyboard Contact Sheet:** `output_video/godzilla_vs_kong_storyboard.png` (5-shot 1080p matrix)
* **Interactive Video Theater:** `output_video/index.html` (Custom web theater with scene seek buttons, shot breakdowns, and prompt inspector)
* **Metadata & Kinematics:** `output_video/METADATA.json`

### Trigger the Video Workflow:
* **Workflow File:** `.github/workflows/generate-monsterverse-video.yml`
* **Trigger via GitHub Web UI:** Go to **Actions** &rarr; select **MonsterVerse Video Generation Pipeline (1080p 60FPS)** &rarr; click **Run workflow**.

---

## 🥋 2. Martial Arts 60-Frame Sequence Generator (24 FPS)

Generates **60 distinct, consecutive martial arts animation frames** following a strict 4-phase chronological combat progression:
1. **Frames 01–15:** Dynamic low guard stance transition.
2. **Frames 16–30:** Forward lunge, straight left jab into powerful right cross.
3. **Frames 31–45:** Lead foot pivot into high right-legged roundhouse kick at head height.
4. **Frames 46–60:** Leg re-chamber, spin recovery, and balanced settlement into defensive fighting stance.

### Deliverables:
* **60 Individual Frames:** `output/frames/Frame_01.png` to `output/frames/Frame_60.png`
* **Organized 10×6 Sprite Sheet:** `output/martial_arts_spritesheet.png`
* **24 FPS Animated GIF:** `output/martial_arts_animation.gif`
* **Interactive Frame Player:** `output/index.html` (timeline scrubber, slow-mo 0.25x/0.5x, frame stepping)

### Trigger the Animation Workflow:
* **Workflow File:** `.github/workflows/generate-martial-arts.yml`
* **Trigger via GitHub Web UI:** Go to **Actions** &rarr; select **Martial Arts Animation Frame Generator** &rarr; click **Run workflow**.

---

## 💻 Local Quickstart

```bash
# Install dependencies
pip install pillow requests imageio imageio-ffmpeg numpy

# Generate MonsterVerse 1080p 60fps video & storyboard
python3 scripts/generate_video.py --duration 10 --fps 60 --width 1920 --height 1080 --output output_video

# Launch local preview theater
python3 -m http.server 3000 --bind 0.0.0.0 -d output_video
```
Open `http://localhost:3000` to watch the 1080p 60FPS video in the interactive theater!
