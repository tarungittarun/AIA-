# 🥋 AIA — 60-Frame Sequential Martial Arts Animation Generator (24 FPS)

Automated frame-by-frame animation generator and GitHub Actions runner workflow that produces **60 distinct, consecutive martial arts animation frames**. When played sequentially at 24 frames per second, these images form a continuous, fluid, and anatomically accurate combat scene.

---

## 📋 Core Prompt & Action Specifications

* **Character:** A single adult male with an athletic build, short dark cropped hair, wearing simple training attire (plain dark charcoal tank top and black sweatpants, barefoot) for visual continuity.
* **Camera & Environment:** Fixed Static Medium Shot at a 45-degree three-quarter profile perspective. The background is an identical, minimalist Japanese training dojo featuring polished light-oak wooden tatami planks, paper shoji screens, and soft studio ambient lighting.
* **Speed & Motion:** 24 Frames Per Second (2.50s total duration). Subtle speed blur trails on fast punches and roundhouse kick extensions.

### Strict Chronological 4-Phase Combat Progression

| Phase | Frames | Combat Action Progression |
| :---: | :---: | :--- |
| **1** | **Frames 01–15** | **Dynamic Stance Transition:** Begins from a relaxed upright standing posture, shifts weight rearward 70%, lowers center of gravity into a balanced, spring-loaded defensive martial arts cat/guard stance with high protective hands. |
| **2** | **Frames 16–30** | **Forward Strike Combination:** Drives forward forcefully, launching an explosive, straight left jab with horizontal fist alignment, followed immediately by rotational hip torque into a powerful right cross punch. |
| **3** | **Frames 31–45** | **Lead Pivot & High Roundhouse Kick:** Recoils cross punch, pivots lead left foot 90°–135° outward, rolls hips parallel to the floor, chambers the right knee, and whips a high right-legged roundhouse kick at head height with full extension. |
| **4** | **Frames 46–60** | **Leg Re-Chamber, Spin Recovery & Settlement:** Re-chambers the kicking leg tightly at the knee, executes rotational follow-through, lands rear foot on the ball of the foot, absorbs deceleration, and settles into an immovable, balanced defensive fighting stance. |

---

## 📦 Output Deliverables

The generator produces:
1. **60 Sequential Frames:** `output/frames/Frame_01.png` through `output/frames/Frame_60.png`
2. **Organized 10×6 Sprite Sheet Grid:** `output/martial_arts_spritesheet.png` (5120 × 3072 px)
3. **24 FPS Animated GIF:** `output/martial_arts_animation.gif` (duration = 41.6ms per frame, seamless infinite loop)
4. **Interactive HTML5 Player:** `output/index.html` (timeline scrubber, 24 FPS player, slow-mo 0.25x / 0.5x, frame stepping, sprite sheet inspector)
5. **Frame-by-Frame Kinematics Metadata:** `output/METADATA.json`

---

## ⚡ GitHub Actions Workflow

The repository includes an automated workflow at `.github/workflows/generate-martial-arts.yml`.

### How to Trigger the Workflow:

#### Option A: Via GitHub Web Interface
1. Go to your repository on GitHub.
2. Click the **Actions** tab.
3. Select **Martial Arts Animation Frame Generator** from the left sidebar.
4. Click **Run workflow**, choose options (e.g., model `flux`, frames `60`, seed `42`), and click the green **Run workflow** button.

#### Option B: Via GitHub CLI (`gh`)
```bash
gh workflow run generate-martial-arts.yml --ref arena/e54b5305-aia -f frames=60 -f model=flux -f seed=42
```

The workflow:
- Sets up Python on an `ubuntu-latest` runner.
- Executes the generator script (`scripts/generate_frames.py`).
- Saves all 60 frames, the sprite sheet, the GIF, and the interactive web player.
- Uploads the complete asset bundle as a downloadable GitHub Actions artifact (`martial-arts-60-frames-24fps`).
- Automatically commits and pushes the output assets back to the branch.

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+
- `pip install pillow requests`

### Run Generator Locally
```bash
# Generate complete 60-frame sequence and sprite sheet
python3 scripts/generate_frames.py --frames 60 --output output

# Open the interactive player in your browser
python3 -m http.server 8080 -d output
```
Then navigate to `http://localhost:8080` in your web browser.
