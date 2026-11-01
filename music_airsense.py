#!/usr/bin/env python3
import cv2, mediapipe as mp, math, time, os, sys, glob, json, shutil, subprocess

HUD_MODE = "--hud" in sys.argv
CONFIG_PATH = os.path.expanduser("~/Vault/airsense_config.json")
MUSIC_DIRS = [os.path.expanduser("~/Vault/Music"), os.path.expanduser("~/Music")]
MANIFOLD_MODES = ["gargantua", "supernova", "attractor", "fibonacci", "tesseract", "pendulum", "geodesic", "fabric"]
MANIFOLD_PALS = ["interstellar", "aether", "cosmos", "monolith"]
manifold_idx = -1
pal_idx = 0
track_idx = -1

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"hold_duration_seconds": 0.65, "cooldown_seconds": 1.4, "gestures": {}}

def notify(title, msg):
    subprocess.Popen(["notify-send", "-u", "normal", "-t", "2200", title, msg],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def play_next_track():
    global track_idx
    exts = (".opus", ".mp3", ".m4a", ".wav", ".flac", ".ogg")
    files = []
    for base in MUSIC_DIRS:
        if os.path.isdir(base):
            for root, _, fnames in os.walk(base):
                for f in fnames:
                    if f.lower().endswith(exts):
                        files.append(os.path.join(root, f))
    files.sort()
    if not files:
        notify("✦ Air-Sense", "No audio tracks found in ~/Vault/Music")
        return
    track_idx = (track_idx + 1) % len(files)
    subprocess.run(["pkill", "-f", "mpv.*--no-video"], stderr=subprocess.DEVNULL)
    subprocess.Popen(["mpv", "--no-video", "--really-quiet", "--loop-file=inf", files[track_idx]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    notify("✦ Air-Sense ▶ Next Track", os.path.splitext(os.path.basename(files[track_idx]))[0])

def launch_smart_hud():
    """Universal cascading launcher so V-Sign works on both your laptop and any GitHub user's PC."""
    if os.path.exists("/usr/local/bin/mission-control"):
        subprocess.Popen(["/usr/local/bin/mission-control", "--hotkey"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify("✦ Air-Sense", "Launching Mission Control HUD")
        return
    term = next((t for t in ["kitty", "ptyxis", "gnome-terminal", "x-terminal-emulator"] if shutil.which(t)), None)
    if os.path.exists("/usr/local/bin/vault") and term:
        cmd = f"{term} -- /usr/local/bin/vault" if term != "kitty" else "kitty /usr/local/bin/vault"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify("✦ Air-Sense", "Launching The Vault Sanctuary")
    elif os.path.exists("/usr/local/bin/hud-veer") and term:
        cmd = f"{term} -- /usr/local/bin/hud-veer" if term != "kitty" else "kitty /usr/local/bin/hud-veer"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify("✦ Air-Sense", "Launching Veer Neural HUD")
    elif term:
        subprocess.Popen(term, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify("✦ Air-Sense", f"Launching {term}")

def trigger_lockdown():
    """Triggers Protocol Zero if installed; otherwise falls back to native Linux session lock."""
    if os.path.exists("/usr/local/bin/protocol-zero"):
        subprocess.Popen(["/usr/local/bin/protocol-zero"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    else:
        subprocess.Popen(["loginctl", "lock-session"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def trigger_action(gesture_key, cfg):
    global manifold_idx, pal_idx
    g_cfg = cfg.get("gestures", {}).get(gesture_key, {})
    action = g_cfg.get("action", "")
    label = g_cfg.get("label", gesture_key.upper())

    if not action:
        return label

    if action == "INTERNAL:NEXT_TRACK":
        play_next_track()
    elif action == "INTERNAL:SMART_HUD":
        launch_smart_hud()
    elif action == "INTERNAL:LOCKDOWN":
        trigger_lockdown()
    elif action == "INTERNAL:EXPAND_SPACE":
        if os.path.exists("/usr/local/bin/manifoldctl"):
            manifold_idx = (manifold_idx + 1) % len(MANIFOLD_MODES)
            mode = MANIFOLD_MODES[manifold_idx]
            subprocess.Popen(["/usr/local/bin/manifoldctl", mode],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if manifold_idx % 2 == 0:
                pal_idx = (pal_idx + 1) % len(MANIFOLD_PALS)
                subprocess.Popen(["/usr/local/bin/manifoldctl", MANIFOLD_PALS[pal_idx]],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            notify("✦ Air-Sense Spatial Stretch", f"Dynamic Theme: {mode.upper()} ({MANIFOLD_PALS[pal_idx].upper()})")
        else:
            notify("✦ Air-Sense Spatial Stretch", label)
    elif action == "INTERNAL:COMPRESS_SPACE":
        if os.path.exists("/usr/local/bin/manifoldctl"):
            subprocess.Popen(["/usr/local/bin/manifoldctl", "off"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            notify("✦ Air-Sense Singularity", "Collapsed into Minimalist Zen Sanctum")
        else:
            notify("✦ Air-Sense Singularity", label)
    else:
        subprocess.Popen(action, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify(f"✦ Air-Sense // {label}", f"Executed: {action}")
    return label

def get_finger_states(lm):
    """Angle-independent distance check from wrist (lm[0]) so gestures work at any hand tilt."""
    wrist = lm[0]
    def d(idx):
        return math.hypot(lm[idx].x - wrist.x, lm[idx].y - wrist.y)
    idx_up  = d(8)  > d(6)  * 1.14
    mid_up  = d(12) > d(10) * 1.14
    ring_up = d(16) > d(14) * 1.14
    pink_up = d(20) > d(18) * 1.14
    return [idx_up, mid_up, ring_up, pink_up]

def main():
    cfg = load_config()
    hold_target = float(cfg.get("hold_duration_seconds", 0.65))
    cooldown = float(cfg.get("cooldown_seconds", 1.4))

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        notify("❌ Air-Sense Error", "Could not access webcam /dev/video0")
        sys.exit(1)

    last_trigger_t = 0.0
    status_banner = "AIR-SENSE // 2F: HUD | 3F: NEXT SONG | 4F: STOP | FIST: LOCK"
    banner_until = 0.0

    current_pose = None
    pose_start_t = 0.0
    prev_two_hand_ratio = None
    vol_smooth = 50.0
    last_vol_int = -1

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        now = time.time()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.cvtColor_BGR2RGB if hasattr(cv2, 'cvtColor_BGR2RGB') else cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if HUD_MODE:
            frame = cv2.convertScaleAbs(frame, alpha=0.65, beta=0)

        landmarks_list = res.multi_hand_landmarks or []
        hold_progress = 0.0

        # ======================================================================
        # 1. TWO-HAND SPATIAL STRETCH / COMPRESS
        # ======================================================================
        if len(landmarks_list) == 2:
            current_pose = None
            h1, h2 = landmarks_list[0].landmark, landmarks_list[1].landmark
            c1x, c1y = int(h1[9].x * w), int(h1[9].y * h)
            c2x, c2y = int(h2[9].x * w), int(h2[9].y * h)
            mx, my = (c1x + c2x) // 2, (c1y + c2y) // 2

            dist_px = math.hypot(c2x - c1x, c2y - c1y)
            norm_span = dist_px / max(1.0, float(w))

            if prev_two_hand_ratio is None:
                prev_two_hand_ratio = norm_span
            else:
                delta_span = norm_span - prev_two_hand_ratio
                prev_two_hand_ratio = prev_two_hand_ratio * 0.68 + norm_span * 0.32

                if (now - last_trigger_t) > cooldown:
                    if norm_span > 0.52 and delta_span > 0.028:
                        status_banner = trigger_action("two_hand_expand", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0
                    elif norm_span < 0.22 and delta_span < -0.025:
                        status_banner = trigger_action("two_hand_compress", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0

            if HUD_MODE:
                radius = int(max(18, min(220, dist_px * 0.42)))
                cv2.line(frame, (c1x, c1y), (c2x, c2y), (255, 240, 0), 2)
                cv2.circle(frame, (mx, my), radius, (255, 0, 255), 2)
                for p_i in range(24):
                    ang = (p_i / 24.0) * math.tau + now * 2.5
                    r_orb = radius * (0.45 + 0.55 * math.sin(now * 3.0 + p_i))
                    px = int(mx + math.cos(ang) * r_orb)
                    py = int(my + math.sin(ang) * r_orb)
                    cv2.circle(frame, (px, py), 3, (255, 240, 0), -1)

        # ======================================================================
        # 2. SINGLE-HAND STATIC FINGER-COUNT HOLDS (NO SWIPING REQUIRED)
        # ======================================================================
        elif len(landmarks_list) == 1:
            prev_two_hand_ratio = None
            lm = landmarks_list[0].landmark
            idx_up, mid_up, ring_up, pink_up = get_finger_states(lm)
            palm_size = math.hypot(lm[9].x - lm[0].x, lm[9].y - lm[0].y) + 1e-6

            detected_pose = None
            req_hold = hold_target

            # A. 1 Finger Up (Index Only) -> Live Thumb+Index Pinch Volume Dial
            if idx_up and not mid_up and not ring_up and not pink_up:
                current_pose = None
                pinch = math.hypot(lm[8].x - lm[4].x, lm[8].y - lm[4].y) / palm_size
                raw_vol = max(0.0, min(100.0, (pinch - 0.20) / 1.15 * 100.0))
                vol_smooth = vol_smooth * 0.70 + raw_vol * 0.30
                v_int = int(vol_smooth)
                if abs(v_int - last_vol_int) >= 2:
                    subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{v_int}%"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    last_vol_int = v_int
                status_banner = f"1-FINGER PINCH VOLUME: {v_int}%"
                banner_until = now + 0.4
                if HUD_MODE:
                    x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                    x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # B. 2 Fingers Up (Index + Middle V-Sign) -> Launch HUD / Vault
            elif idx_up and mid_up and not ring_up and not pink_up:
                detected_pose = "peace_hold"

            # C. 3 Fingers Up (Index + Middle + Ring) -> Play / Next Track
            elif idx_up and mid_up and ring_up and not pink_up:
                detected_pose = "three_fingers"

            # D. 4 Fingers Up (Index + Middle + Ring + Pinky) -> Stop / Silence Audio
            elif idx_up and mid_up and ring_up and pink_up:
                detected_pose = "four_fingers"

            # E. Closed Fist (0 Fingers Extended) -> Protocol Zero Lockdown
            elif not idx_up and not mid_up and not ring_up and not pink_up:
                detected_pose = "fist_hold"
                req_hold = 0.90

            if detected_pose:
                if current_pose != detected_pose:
                    current_pose = detected_pose
                    pose_start_t = now
                else:
                    elapsed = now - pose_start_t
                    hold_progress = min(1.0, elapsed / req_hold)
                    if elapsed >= req_hold and (now - last_trigger_t) > cooldown:
                        status_banner = trigger_action(detected_pose, cfg)
                        last_trigger_t = now
                        banner_until = now + 2.2
                        pose_start_t = now + 1.0
            else:
                current_pose = None
        else:
            prev_two_hand_ratio = None
            current_pose = None

        if HUD_MODE:
            for hand_lms in landmarks_list:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_lms, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 240, 0), thickness=2, circle_radius=3),
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 255), thickness=2)
                )
            if hold_progress > 0.05 and len(landmarks_list) == 1:
                cx_p = int(landmarks_list[0].landmark[9].x * w)
                cy_p = int(landmarks_list[0].landmark[9].y * h)
                cv2.ellipse(frame, (cx_p, cy_p), (48, 48), -90, 0, int(hold_progress * 360), (0, 255, 180), 4)

            msg = status_banner if now < banner_until else "2F: HUD | 3F: NEXT TRACK | 4F: STOP AUDIO | FIST: LOCK | 2-HAND: THEME"
            cv2.rectangle(frame, (0, 0), (w, 42), (10, 10, 16), -1)
            cv2.putText(frame, msg, (14, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 240, 0), 2)
            cv2.imshow("Air-Sense Spatial Telepathy HUD (Press Q to close)", frame)
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), 27):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
