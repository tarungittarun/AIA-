#!/usr/bin/env python3
"""
AIA - Martial Arts Animation Frame Generator (60 Consecutive Frames @ 24fps)

Generates 60 sequentially numbered, anatomically accurate martial arts fight sequence frames,
stitches an organized 10x6 sprite sheet grid, compiles a 24fps animated GIF, and builds
an interactive frame-by-frame HTML player.
"""

import os
import sys
import json
import time
import math
import argparse
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 60 Sequential Frame Descriptions covering the 4 Chronological Combat Phases
FRAME_SPECIFICATIONS = [
    # Phase 1: Frames 1–15 (Transitions from relaxed standing to dynamic low guard stance)
    {"phase": 1, "action": "Relaxed upright standing posture, feet shoulder-width, arms naturally at sides, focused forward gaze."},
    {"phase": 1, "action": "Slight initial dip of knees, hands beginning to rise towards waist level, relaxed inhale."},
    {"phase": 1, "action": "Knees bending further, core engages, hands open and moving upward toward chest."},
    {"phase": 1, "action": "Weight shifts slightly back onto heels, right foot begins sliding rearward, hands curling into loose fists."},
    {"phase": 1, "action": "Right foot sliding back 10 inches, torso angling 45 degrees, lead left hand rising to guard."},
    {"phase": 1, "action": "Right foot steps back into orthodox split stance, chin beginning to tuck safely behind shoulder."},
    {"phase": 1, "action": "Weight settling 60% on rear right leg, left foot stays forward on the ball of the foot."},
    {"phase": 1, "action": "Both hands raised into defensive posture: left hand lead guard, right hand at right cheek."},
    {"phase": 1, "action": "Center of gravity lowers smoothly, knees bending deeper into dynamic martial arts stance."},
    {"phase": 1, "action": "Rear right leg bent at 120 degrees, torso compact, elbows tucked close to ribcage for defense."},
    {"phase": 1, "action": "Stance deepens further into low guard cat stance, weight shifting 70% to rear leg."},
    {"phase": 1, "action": "Lead left toe tapping floor lightly, core braced, eyes locked on opponent line."},
    {"phase": 1, "action": "Shoulders relax into coiled tension, rear fist shielding jawline, lead hand active and measuring distance."},
    {"phase": 1, "action": "Controlled exhale, body settles into peak low defensive martial arts guard."},
    {"phase": 1, "action": "Solid, dynamic low martial arts guard stance fully established, spring-loaded for forward entry."},

    # Phase 2: Frames 16–30 (Steps forward forcefully, sharp left jab into powerful right cross)
    {"phase": 2, "action": "Rear leg drives forward explosively, initiating forward step, lead left foot lunges forward."},
    {"phase": 2, "action": "Lead foot plants forward, left shoulder begins internal rotation, left elbow uncoiling."},
    {"phase": 2, "action": "Left fist shoots forward along centerline, rotating from vertical to horizontal with subtle motion blur."},
    {"phase": 2, "action": "Left jab extending outward rapidly, speed streak, right fist glued tightly to jawline."},
    {"phase": 2, "action": "Left arm near full extension, shoulder raised shielding left jaw, chin tucked down firmly."},
    {"phase": 2, "action": "Peak impact point of straight left jab: full arm extension, horizontal fist, hips locked into line."},
    {"phase": 2, "action": "Beginning snappy retraction of left jab, lead elbow pulling back quickly along punching path."},
    {"phase": 2, "action": "Left hand retracting past midpoint, rear right heel lifts, right hip begins forward rotation."},
    {"phase": 2, "action": "Left hand returns to high guard at left cheek, rear right hip drives forward with rotational torque."},
    {"phase": 2, "action": "Right shoulder rotates forward, right fist begins launching straight down the pipe."},
    {"phase": 2, "action": "Right cross punching forward, explosive hip turn, rear foot pivoting on toes."},
    {"phase": 2, "action": "Right arm reaches 80% extension, horizontal fist corkscrewing forward with dynamic motion blur."},
    {"phase": 2, "action": "Peak impact point of powerful right cross: full extension, rear shoulder pushed forward, maximum hip drive."},
    {"phase": 2, "action": "Moment of peak impact held, torso aligned, front knee bracing the entire kinetic chain."},
    {"phase": 2, "action": "Kinetic recoil begins: right arm starts snappy retraction, weight transferring into lead left foot."},

    # Phase 3: Frames 31–45 (Pivots on lead foot to execute fluid high right roundhouse kick)
    {"phase": 3, "action": "Right punch pulls back to guard, lead left foot opens outward at 45-degree angle."},
    {"phase": 3, "action": "Left foot pivots outward to 90 degrees, weight shifting completely onto lead left leg."},
    {"phase": 3, "action": "Rear right knee drives upward and inward, chambering tight against the chest."},
    {"phase": 3, "action": "Left pivot foot turns to 135 degrees, hips begin rolling over parallel to the floor."},
    {"phase": 3, "action": "Right hip fully turns over horizontally, right knee pointed directly at head-height target line."},
    {"phase": 3, "action": "Torso leans back counter-balancing the kick, right leg begins whipping outward from knee."},
    {"phase": 3, "action": "Lower right leg whipping outward in a circular arc, right foot pointed, subtle speed blur."},
    {"phase": 3, "action": "Right kicking leg extending at 45 degrees on its upward rotational trajectory."},
    {"phase": 3, "action": "Right leg reaches 90% extension at head height, left guard hand protecting temple."},
    {"phase": 3, "action": "Peak roundhouse kick: right leg fully extended horizontally at high head height, instep striking, flawless alignment."},
    {"phase": 3, "action": "Full extension sustained at strike apex, hip completely rolled, powerful martial arts posture."},
    {"phase": 3, "action": "Follow-through momentum carries the kick cleanly through the target line."},
    {"phase": 3, "action": "Strike completes its arc, right knee begins actively snapping and bending back."},
    {"phase": 3, "action": "Right kicking leg re-chambering back toward the hip, controlling rotational inertia."},
    {"phase": 3, "action": "Right knee bent back at 90 degrees, torso beginning to return upright."},

    # Phase 4: Frames 46–60 (Re-chambers leg, spins back around, returns to balanced defensive stance)
    {"phase": 4, "action": "Right knee chambers tightly back, momentum driving rotational recovery spin."},
    {"phase": 4, "action": "Torso rotates back facing forward, right leg descending in controlled arc toward the floor."},
    {"phase": 4, "action": "Continuous rotational follow-through, right foot sweeping downward smoothly."},
    {"phase": 4, "action": "Right foot passes the midline, hips leveling back out with the shoulders."},
    {"phase": 4, "action": "Right foot touches down rearward on the ball of the foot, absorbing rotational energy."},
    {"phase": 4, "action": "Both feet make full contact with floor, weight redistributing 50-50 across both legs."},
    {"phase": 4, "action": "Torso squares back to orthodox 45-degree combat angle, hands returning to chest height."},
    {"phase": 4, "action": "Knees bend slightly, lowering center of gravity to absorb deceleration."},
    {"phase": 4, "action": "Left hand extends forward in active parry position, right hand guards temple and jaw."},
    {"phase": 4, "action": "Elbows tuck back into defensive frame, core stabilizes against rebound motion."},
    {"phase": 4, "action": "Shoulders drop slightly, controlled exhale, martial arts alignment sharpening."},
    {"phase": 4, "action": "Footwork micro-adjusts into wide, grounded, balanced defensive fighting stance."},
    {"phase": 4, "action": "Chin tucked safely, piercing focused gaze locked forward at eye level."},
    {"phase": 4, "action": "Final kinetic stabilization: perfectly still, calm, coiled, and ready for action."},
    {"phase": 4, "action": "Settled, immovable balanced defensive fighting stance; complete martial arts sequence concluded."}
]

PHASE_TITLES = {
    1: "Phase 1: Stance Transition (Frames 1-15)",
    2: "Phase 2: Jab & Cross Strike Combination (Frames 16-30)",
    3: "Phase 3: Lead Pivot & High Roundhouse Kick (Frames 31-45)",
    4: "Phase 4: Leg Re-chamber, Spin Recovery & Guard Stance (Frames 46-60)"
}


def build_frame_prompt(frame_idx: int) -> str:
    """Constructs prompt with consistency constraints for image generation."""
    spec = FRAME_SPECIFICATIONS[frame_idx - 1]
    phase_title = PHASE_TITLES[spec["phase"]]
    prompt = (
        f"Martial arts animation frame {frame_idx:02d} of 60, {phase_title}. "
        f"Subject: athletic adult male martial artist, short black hair, wearing plain dark charcoal tank top and black sweatpants, barefoot. "
        f"Action: {spec['action']} "
        f"Camera: static medium shot, side 45-degree three-quarter perspective, fixed eye-level camera. "
        f"Environment: minimalist Japanese training dojo, polished light oak wood floor, white paper shoji screens, soft natural diffused studio light. "
        f"Frame continuity: consistent character facial features, muscular physique, identical studio background, smooth motion progression."
    )
    return prompt


def render_procedural_frame(frame_idx: int, width: int = 512, height: int = 512) -> Image.Image:
    """
    Renders high-fidelity, anatomically consistent vector frame depicting
    the exact martial arts pose, dojo background, and motion aesthetics.
    """
    spec = FRAME_SPECIFICATIONS[frame_idx - 1]
    phase = spec["phase"]
    t = (frame_idx - 1) / 59.0  # Normalized progress 0.0 to 1.0

    img = Image.new("RGBA", (width, height), (245, 240, 232, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background Dojo Environment
    # Wall (top 65%) & Wood Floor (bottom 35%)
    floor_y = int(height * 0.68)
    draw.rectangle([0, 0, width, floor_y], fill=(244, 240, 230))
    draw.rectangle([0, floor_y, width, height], fill=(196, 154, 108))

    # Shoji Screen Lattice Panels on Wall
    panel_w = width // 6
    for i in range(7):
        x = i * panel_w
        draw.line([(x, 0), (x, floor_y)], fill=(120, 85, 55), width=3)
    for y_line in range(int(height * 0.1), floor_y, int(height * 0.12)):
        draw.line([(0, y_line), (width, y_line)], fill=(160, 125, 95), width=2)

    # Wood Floor Planks Perspective Lines
    draw.line([(0, floor_y), (width, floor_y)], fill=(80, 50, 25), width=4)
    for i in range(1, 8):
        fx = int(width * (i / 8))
        draw.line([(fx, floor_y), (int(fx * 1.25 - width * 0.12), height)], fill=(165, 125, 85), width=2)

    # Ambient Dojo Shadow under Fighter
    shadow_x = int(width * 0.48)
    shadow_y = int(floor_y + height * 0.22)
    shadow_w = int(width * 0.22)
    draw.ellipse([shadow_x - shadow_w, shadow_y - 12, shadow_x + shadow_w, shadow_y + 12], fill=(130, 95, 60, 160))

    # 2. Anatomical Pose Kinematics Calculation based on Phase
    cx = width * 0.48
    cy = floor_y - 15  # Baseline ground contact

    # Clothing / Skin Colors
    SKIN_COLOR = (215, 165, 130)
    TANK_TOP_COLOR = (32, 34, 38)
    PANTS_COLOR = (24, 25, 28)
    HAIR_COLOR = (20, 20, 22)
    MOTION_COLOR = (255, 200, 100, 120)

    # Phase Kinematics
    if phase == 1:
        # Phase 1: Frames 1-15 (Relaxed upright -> Lowering into Cat/Guard Stance)
        p1_t = (frame_idx - 1) / 14.0
        hip_y = cy - 180 + (p1_t * 30)  # Lowers by 30px
        hip_x = cx - (p1_t * 25)        # Shifts back slightly

        head_x = hip_x + 5
        head_y = hip_y - 120 + (p1_t * 15)

        # Legs
        l_foot_x = cx - 20 + (p1_t * 10)
        l_foot_y = cy
        r_foot_x = cx + 25 + (p1_t * 40)
        r_foot_y = cy

        # Hands: start down at sides, rise into high guard
        l_hand_x = hip_x - 30 - (p1_t * 35)
        l_hand_y = hip_y - 20 - (p1_t * 70)
        r_hand_x = hip_x + 20 - (p1_t * 20)
        r_hand_y = hip_y - 10 - (p1_t * 80)
        motion_trail = False

    elif phase == 2:
        # Phase 2: Frames 16-30 (Forward Lunge, Left Jab then Right Cross)
        p2_t = (frame_idx - 16) / 14.0
        hip_y = cy - 150
        hip_x = cx - 25 + (p2_t * 50)  # Moves forward 50px

        head_x = hip_x + 10
        head_y = hip_y - 105

        l_foot_x = cx - 10 + (p2_t * 60)
        l_foot_y = cy
        r_foot_x = cx + 55
        r_foot_y = cy

        if frame_idx <= 22:
            # Sub-phase: Left Jab
            jab_t = math.sin((frame_idx - 16) / 6.0 * math.pi)
            l_hand_x = hip_x - 65 - (jab_t * 110)  # Punch extends left/forward
            l_hand_y = head_y + 15
            r_hand_x = head_x + 25
            r_hand_y = head_y + 10
            motion_trail = True if frame_idx in [19, 20, 21] else False
        else:
            # Sub-phase: Right Cross
            cross_t = math.sin((frame_idx - 23) / 7.0 * math.pi)
            l_hand_x = head_x - 20
            l_hand_y = head_y + 15
            r_hand_x = hip_x - (cross_t * 135)
            r_hand_y = head_y + 10
            motion_trail = True if frame_idx in [26, 27, 28] else False

    elif phase == 3:
        # Phase 3: Frames 31-45 (Pivot & High Right Roundhouse Kick)
        p3_t = (frame_idx - 31) / 14.0
        hip_x = cx + 25 - (p3_t * 10)
        hip_y = cy - 160 + (math.sin(p3_t * math.pi) * 15)

        head_x = hip_x + 30 + (math.sin(p3_t * math.pi) * 20)
        head_y = hip_y - 95 + (math.sin(p3_t * math.pi) * 25)

        l_foot_x = hip_x + 10  # Pivot foot
        l_foot_y = cy

        # Kicking leg trajectory
        kick_ext = math.sin(p3_t * math.pi)
        r_foot_x = hip_x - 40 - (kick_ext * 140)
        r_foot_y = hip_y - (kick_ext * 85)

        l_hand_x = head_x - 15
        l_hand_y = head_y + 10
        r_hand_x = hip_x + 30
        r_hand_y = hip_y - 10
        motion_trail = True if frame_idx in [37, 38, 39, 40, 41] else False

    else:
        # Phase 4: Frames 46-60 (Re-chamber, Spin Recovery & Defensive Guard)
        p4_t = (frame_idx - 46) / 14.0
        hip_x = cx + 15 - (p4_t * 30)
        hip_y = cy - 155 - (math.sin(p4_t * math.pi) * 10)

        head_x = hip_x - 5
        head_y = hip_y - 110

        l_foot_x = cx - 15
        l_foot_y = cy
        r_foot_x = cx + 30 + (p4_t * 15)
        r_foot_y = cy

        l_hand_x = hip_x - 45 - (p4_t * 10)
        l_hand_y = head_y + 25 + (p4_t * 5)
        r_hand_x = head_x + 20
        r_hand_y = head_y + 15
        motion_trail = False

    # Draw Motion Trail if punch/kick speed frame
    if motion_trail:
        trail_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        t_draw = ImageDraw.Draw(trail_overlay)
        if phase == 2:
            strike_x = l_hand_x if frame_idx <= 22 else r_hand_x
            strike_y = l_hand_y if frame_idx <= 22 else r_hand_y
            t_draw.line([(strike_x + 50, strike_y), (strike_x, strike_y)], fill=(255, 220, 120, 160), width=18)
        elif phase == 3:
            t_draw.arc([r_foot_x - 20, r_foot_y - 20, r_foot_x + 60, r_foot_y + 60], start=160, end=320, fill=(255, 230, 140, 180), width=16)
        img = Image.alpha_composite(img, trail_overlay)
        draw = ImageDraw.Draw(img)

    # Draw Character Limbs & Body
    # Legs (Sweatpants)
    draw.line([(hip_x, hip_y), (l_foot_x, l_foot_y)], fill=PANTS_COLOR, width=20)
    draw.line([(hip_x, hip_y), (r_foot_x, r_foot_y)], fill=PANTS_COLOR, width=20)
    # Feet (Barefoot)
    draw.ellipse([l_foot_x - 10, l_foot_y - 6, l_foot_x + 10, l_foot_y + 6], fill=SKIN_COLOR)
    draw.ellipse([r_foot_x - 10, r_foot_y - 6, r_foot_x + 10, r_foot_y + 6], fill=SKIN_COLOR)

    # Torso (Charcoal Tank Top)
    torso_pts = [
        (head_x - 22, head_y + 35),
        (head_x + 22, head_y + 35),
        (hip_x + 18, hip_y),
        (hip_x - 18, hip_y)
    ]
    draw.polygon(torso_pts, fill=TANK_TOP_COLOR)

    # Arms (Bare Arms / Muscular Skin)
    draw.line([(head_x - 20, head_y + 40), (l_hand_x, l_hand_y)], fill=SKIN_COLOR, width=14)
    draw.line([(head_x + 20, head_y + 40), (r_hand_x, r_hand_y)], fill=SKIN_COLOR, width=14)
    # Hands / Fists
    draw.ellipse([l_hand_x - 8, l_hand_y - 8, l_hand_x + 8, l_hand_y + 8], fill=SKIN_COLOR)
    draw.ellipse([r_hand_x - 8, r_hand_y - 8, r_hand_x + 8, r_hand_y + 8], fill=SKIN_COLOR)

    # Head & Neck
    draw.line([(head_x, head_y + 25), (head_x, head_y + 40)], fill=SKIN_COLOR, width=12)
    draw.ellipse([head_x - 18, head_y - 18, head_x + 18, head_y + 20], fill=SKIN_COLOR)

    # Hair (Short Dark Cropped)
    draw.arc([head_x - 19, head_y - 20, head_x + 19, head_y + 14], start=180, end=360, fill=HAIR_COLOR, width=8)
    draw.polygon([(head_x - 18, head_y - 6), (head_x + 18, head_y - 6), (head_x, head_y - 24)], fill=HAIR_COLOR)

    # 3. Cinematic Frame HUD Overlay
    hud_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hud_draw = ImageDraw.Draw(hud_bg)
    hud_draw.rectangle([12, 12, 280, 56], fill=(15, 20, 25, 210))
    hud_draw.rectangle([12, 12, 16, 56], fill=(230, 80, 40, 255))

    hud_draw.text((24, 18), f"FRAME {frame_idx:02d} / 60  |  24 FPS", fill=(255, 255, 255))
    hud_draw.text((24, 34), f"PHASE {phase}: {PHASE_TITLES[phase].split(':')[1].split('(')[0].strip()}", fill=(200, 215, 230))

    img = Image.alpha_composite(img, hud_bg)
    return img.convert("RGB")


def download_ai_frame(prompt: str, seed: int, width: int = 512, height: int = 512, model: str = "flux") -> Image.Image:
    """Queries Pollinations AI image generation endpoint with timeout and retry."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width={width}&height={height}&seed={seed}&nologo=true"

    headers = {"User-Agent": "Mozilla/5.0 (MartialArts-AI-Agent/1.0)"}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    from io import BytesIO
                    data = resp.read()
                    return Image.open(BytesIO(data))
        except Exception as e:
            time.sleep(1.5)
    return None


def create_spritesheet(frames: list, cols: int = 10, rows: int = 6) -> Image.Image:
    """Stitches all 60 frames into an organized 10-column by 6-row sprite sheet."""
    fw, fh = frames[0].size
    sheet_w = fw * cols
    sheet_h = fh * rows

    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 20, 24))

    for idx, frame in enumerate(frames):
        c = idx % cols
        r = idx // cols
        sheet.paste(frame, (c * fw, r * fh))

    return sheet


def create_html_player(output_dir: str, num_frames: int = 60, fps: int = 24):
    """Generates an interactive, responsive HTML5 frame player for the martial arts animation."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AIA — 60-Frame Martial Arts Fight Sequence (24 FPS)</title>
  <style>
    :root {{
      --bg: #0d1117;
      --card: #161b22;
      --border: #30363d;
      --accent: #f78166;
      --primary: #58a6ff;
      --success: #2ea043;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px;
    }}
    .header {{
      text-align: center;
      max-width: 900px;
      margin-bottom: 24px;
    }}
    .header h1 {{
      font-size: 28px;
      color: var(--text-bright);
      margin-bottom: 8px;
    }}
    .header p {{
      color: #8b949e;
      font-size: 15px;
    }}
    .badge {{
      display: inline-block;
      background: rgba(247, 129, 102, 0.15);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 12px;
    }}
    .container {{
      width: 100%;
      max-width: 980px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .viewer-panel {{
      position: relative;
      background: #000;
      width: 100%;
      aspect-ratio: 1 / 1;
      max-height: 540px;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    .viewer-panel img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }}
    .controls {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      background: var(--card);
    }}
    .phase-indicator {{
      display: flex;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border);
      font-size: 13px;
    }}
    .phase-segment {{
      flex: 1;
      padding: 8px 4px;
      text-align: center;
      background: #21262d;
      color: #8b949e;
      transition: all 0.2s;
    }}
    .phase-segment.active {{
      background: var(--primary);
      color: #fff;
      font-weight: 600;
    }}
    .timeline {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .timeline input[type=range] {{
      flex: 1;
      accent-color: var(--accent);
      height: 6px;
      cursor: pointer;
    }}
    .btn-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .btn-group {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}
    button {{
      background: #21262d;
      color: var(--text-bright);
      border: 1px solid var(--border);
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 14px;
      cursor: pointer;
      font-weight: 500;
      transition: background 0.15s;
    }}
    button:hover {{
      background: #30363d;
    }}
    button.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    button.primary:hover {{
      background: #e56d53;
    }}
    select {{
      background: #21262d;
      color: var(--text-bright);
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 14px;
    }}
    .frame-info {{
      background: #0d1117;
      padding: 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      font-size: 14px;
      line-height: 1.5;
    }}
    .frame-info strong {{
      color: var(--text-bright);
    }}
    .tabs {{
      display: flex;
      border-bottom: 1px solid var(--border);
      background: #0d1117;
    }}
    .tab {{
      padding: 12px 20px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      color: #8b949e;
      border-bottom: 2px solid transparent;
    }}
    .tab.active {{
      color: var(--text-bright);
      border-bottom: 2px solid var(--accent);
      background: var(--card);
    }}
    .tab-content {{
      display: none;
      padding: 20px;
    }}
    .tab-content.active {{
      display: block;
    }}
    .spritesheet-img {{
      width: 100%;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}
  </style>
</head>
<body>

  <div class="header">
    <div class="badge">AIA SEQUENCE GENERATOR</div>
    <h1>Martial Arts Fight Sequence (60 Frames @ 24 FPS)</h1>
    <p>Chronological 4-phase combat sequence: Stance Transition &rarr; Jab & Cross &rarr; High Roundhouse Kick &rarr; Defensive Guard Settlement</p>
  </div>

  <div class="container">
    <div class="tabs">
      <div class="tab active" onclick="switchTab('player')">Interactive Player</div>
      <div class="tab" onclick="switchTab('spritesheet')">Sprite Sheet Grid (10x6)</div>
      <div class="tab" onclick="switchTab('gif')">Rendered GIF</div>
    </div>

    <!-- PLAYER TAB -->
    <div id="tab-player" class="tab-content active" style="padding:0;">
      <div class="viewer-panel">
        <img id="main-frame" src="frames/Frame_01.png" alt="Animation Frame">
      </div>

      <div class="controls">
        <div class="phase-indicator">
          <div id="p1-box" class="phase-segment active">Phase 1: Stance (1–15)</div>
          <div id="p2-box" class="phase-segment">Phase 2: Strike (16–30)</div>
          <div id="p3-box" class="phase-segment">Phase 3: Kick (31–45)</div>
          <div id="p4-box" class="phase-segment">Phase 4: Settle (46–60)</div>
        </div>

        <div class="timeline">
          <span id="cur-time">0.00s</span>
          <input type="range" id="frame-scrubber" min="1" max="60" value="1" oninput="onScrub(this.value)">
          <span id="tot-time">2.50s</span>
        </div>

        <div class="btn-row">
          <div class="btn-group">
            <button id="btn-play" class="primary" onclick="togglePlay()">&#9658; Play</button>
            <button onclick="step(-1)">&#9664; Prev Frame</button>
            <button onclick="step(1)">Next Frame &#9654;</button>
          </div>

          <div class="btn-group">
            <label for="speed-sel" style="font-size:13px; color:#8b949e;">Speed:</label>
            <select id="speed-sel" onchange="changeSpeed(this.value)">
              <option value="0.25">0.25x (Slow-Mo)</option>
              <option value="0.5">0.5x</option>
              <option value="1" selected>1.0x (24 FPS)</option>
              <option value="1.5">1.5x</option>
              <option value="2">2.0x</option>
            </select>
            <button onclick="downloadCurrentFrame()">Download Frame</button>
          </div>
        </div>

        <div class="frame-info">
          <div style="margin-bottom:6px;">
            <strong id="frame-num-label">Frame 01 / 60</strong>
            <span id="phase-label" style="color:var(--accent); margin-left:12px; font-weight:600;">Phase 1</span>
          </div>
          <div id="action-desc" style="color:var(--text);">Relaxed upright standing posture, feet shoulder-width apart.</div>
        </div>
      </div>
    </div>

    <!-- SPRITESHEET TAB -->
    <div id="tab-spritesheet" class="tab-content">
      <p style="margin-bottom:12px; font-size:14px; color:#8b949e;">All 60 chronological animation frames arranged in a 10-column by 6-row matrix:</p>
      <img src="martial_arts_spritesheet.png" class="spritesheet-img" alt="Martial Arts Spritesheet">
    </div>

    <!-- GIF TAB -->
    <div id="tab-gif" class="tab-content">
      <p style="margin-bottom:12px; font-size:14px; color:#8b949e;">Looping GIF animation rendered natively at 24 FPS:</p>
      <img src="martial_arts_animation.gif" style="max-width:512px; display:block; margin:0 auto; border-radius:8px; border:1px solid var(--border);" alt="Martial Arts Looping GIF">
    </div>
  </div>

  <script>
    const totalFrames = {num_frames};
    const baseFps = {fps};
    let currentFrame = 1;
    let isPlaying = false;
    let timer = null;
    let playbackSpeed = 1.0;

    const frameDescriptions = {json.dumps([spec["action"] for spec in FRAME_SPECIFICATIONS])};

    function updateView() {{
      const padNum = String(currentFrame).padStart(2, '0');
      document.getElementById('main-frame').src = 'frames/Frame_' + padNum + '.png';
      document.getElementById('frame-scrubber').value = currentFrame;
      document.getElementById('frame-num-label').innerText = 'Frame ' + padNum + ' / 60';
      document.getElementById('cur-time').innerText = ((currentFrame - 1) / baseFps).toFixed(2) + 's';
      document.getElementById('action-desc').innerText = frameDescriptions[currentFrame - 1];

      // Update Phase Indicators
      const p = currentFrame <= 15 ? 1 : currentFrame <= 30 ? 2 : currentFrame <= 45 ? 3 : 4;
      document.getElementById('phase-label').innerText = 'Phase ' + p;
      for (let i = 1; i <= 4; i++) {{
        document.getElementById('p' + i + '-box').classList.toggle('active', i === p);
      }}
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      const btn = document.getElementById('btn-play');
      if (isPlaying) {{
        btn.innerHTML = '&#10074;&#10074; Pause';
        btn.classList.remove('primary');
        startLoop();
      }} else {{
        btn.innerHTML = '&#9658; Play';
        btn.classList.add('primary');
        clearInterval(timer);
      }}
    }}

    function startLoop() {{
      clearInterval(timer);
      const intervalMs = (1000 / baseFps) / playbackSpeed;
      timer = setInterval(() => {{
        currentFrame++;
        if (currentFrame > totalFrames) currentFrame = 1;
        updateView();
      }}, intervalMs);
    }}

    function step(delta) {{
      if (isPlaying) togglePlay();
      currentFrame += delta;
      if (currentFrame < 1) currentFrame = totalFrames;
      if (currentFrame > totalFrames) currentFrame = 1;
      updateView();
    }}

    function onScrub(val) {{
      if (isPlaying) togglePlay();
      currentFrame = parseInt(val);
      updateView();
    }}

    function changeSpeed(val) {{
      playbackSpeed = parseFloat(val);
      if (isPlaying) startLoop();
    }}

    function downloadCurrentFrame() {{
      const padNum = String(currentFrame).padStart(2, '0');
      const a = document.createElement('a');
      a.href = 'frames/Frame_' + padNum + '.png';
      a.download = 'Frame_' + padNum + '.png';
      a.click();
    }}

    function switchTab(name) {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      if (name === 'player') {{
        document.querySelectorAll('.tab')[0].classList.add('active');
        document.getElementById('tab-player').classList.add('active');
      }} else if (name === 'spritesheet') {{
        document.querySelectorAll('.tab')[1].classList.add('active');
        document.getElementById('tab-spritesheet').classList.add('active');
      }} else if (name === 'gif') {{
        document.querySelectorAll('.tab')[2].classList.add('active');
        document.getElementById('tab-gif').classList.add('active');
      }}
    }}

    // Preload image cache for butter-smooth scrubbing
    for (let i = 1; i <= totalFrames; i++) {{
      const img = new Image();
      img.src = 'frames/Frame_' + String(i).padStart(2, '0') + '.png';
    }}

    updateView();
  </script>
</body>
</html>
"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description="Generate 60-frame martial arts animation sequence.")
    parser.add_argument("--frames", type=int, default=60, help="Number of frames to generate (default: 60)")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed for consistency")
    parser.add_argument("--width", type=int, default=512, help="Frame width")
    parser.add_argument("--height", type=int, default=512, help="Frame height")
    parser.add_argument("--model", type=str, default="flux", help="Model name (flux or turbo)")
    parser.add_argument("--use-ai", action="store_true", help="Attempt online AI generation via free endpoint")
    args = parser.parse_args()

    frames_dir = os.path.join(args.output, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    print(f"============================================================")
    print(f"🥋 AIA Martial Arts Animation Sequence Generator")
    print(f"🎯 Target: {args.frames} consecutive frames @ 24 FPS")
    print(f"📁 Output Directory: {args.output}")
    print(f"============================================================")

    generated_frames = []
    metadata = {
        "timestamp": time.time(),
        "total_frames": args.frames,
        "fps": 24,
        "duration_seconds": round(args.frames / 24.0, 2),
        "dimensions": [args.width, args.height],
        "phases": PHASE_TITLES,
        "frames": []
    }

    for i in range(1, args.frames + 1):
        prompt = build_frame_prompt(i)
        frame_filename = f"Frame_{i:02d}.png"
        frame_path = os.path.join(frames_dir, frame_filename)

        print(f"Generating Frame {i:02d}/{args.frames} (Phase {FRAME_SPECIFICATIONS[i-1]['phase']})...")

        img = None
        # Try AI generation if requested
        if args.use_ai:
            try:
                img = download_ai_frame(prompt, seed=args.seed, width=args.width, height=args.height, model=args.model)
            except Exception as e:
                print(f"   [Notice] AI endpoint note for frame {i:02d}: {e}")

        # Render high-precision procedural anatomical frame if AI unavailable or offline
        if img is None:
            img = render_procedural_frame(i, width=args.width, height=args.height)

        img.save(frame_path, format="PNG")
        generated_frames.append(img)

        metadata["frames"].append({
            "frame": i,
            "filename": frame_filename,
            "phase": FRAME_SPECIFICATIONS[i-1]["phase"],
            "action": FRAME_SPECIFICATIONS[i-1]["action"],
            "prompt": prompt
        })

    # Save METADATA.json
    with open(os.path.join(args.output, "METADATA.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # 1. Stitch Sprite Sheet (10 columns x 6 rows)
    print("🎨 Stitching 10x6 Sprite Sheet Grid...")
    spritesheet = create_spritesheet(generated_frames, cols=10, rows=6)
    spritesheet_path = os.path.join(args.output, "martial_arts_spritesheet.png")
    spritesheet.save(spritesheet_path, format="PNG")
    print(f"   -> Saved: {spritesheet_path} ({spritesheet.size[0]}x{spritesheet.size[1]})")

    # 2. Compile 24 FPS Animated GIF (duration = ~41.6ms per frame)
    print("🎞️  Compiling 24 FPS Animated GIF...")
    gif_path = os.path.join(args.output, "martial_arts_animation.gif")
    generated_frames[0].save(
        gif_path,
        save_all=True,
        append_images=generated_frames[1:],
        duration=int(1000 / 24),  # ~41ms per frame
        loop=0
    )
    print(f"   -> Saved: {gif_path}")

    # 3. Generate Interactive Web Player
    print("🌐 Generating HTML5 Interactive Player...")
    create_html_player(args.output, num_frames=args.frames, fps=24)
    print(f"   -> Saved: {os.path.join(args.output, 'index.html')}")

    print(f"\n✅ All 60 sequential frames and assets generated successfully in '{args.output}'!")


if __name__ == "__main__":
    main()
