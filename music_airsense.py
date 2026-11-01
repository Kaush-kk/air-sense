#!/usr/bin/env python3
import cv2, mediapipe as mp, math, time, os, sys, glob, json, random, subprocess

HUD_MODE = "--hud" in sys.argv
CONFIG_PATH = os.path.expanduser("~/Vault/airsense_config.json")
MUSIC_DIR = os.path.expanduser("~/Vault/Music")
MANIFOLD_MODES = ["gargantua", "supernova", "attractor", "fibonacci", "tesseract", "pendulum", "geodesic", "fabric"]
manifold_idx = 0
track_idx = -1

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"cooldown_seconds": 1.5, "gestures": {}}

def notify(title, msg):
    subprocess.Popen(["notify-send", "-u", "normal", "-t", "2200", title, msg],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def play_next_track():
    global track_idx
    exts = ("*.opus", "*.mp3", "*.m4a", "*.wav", "*.flac")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(MUSIC_DIR, ext)))
    files.sort()
    if not files:
        notify("✦ Air-Sense", "No audio tracks found in ~/Vault/Music")
        return
    track_idx = (track_idx + 1) % len(files)
    subprocess.run(["pkill", "-f", "mpv.*--no-video"], stderr=subprocess.DEVNULL)
    subprocess.Popen(["mpv", "--no-video", "--really-quiet", "--loop-file=inf", files[track_idx]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    notify("✦ Air-Sense ▶ Next Track", os.path.splitext(os.path.basename(files[track_idx]))[0])

def trigger_action(gesture_key, cfg):
    global manifold_idx
    g_cfg = cfg.get("gestures", {}).get(gesture_key, {})
    action = g_cfg.get("action", "")
    label = g_cfg.get("label", gesture_key.upper())

    if not action:
        return label

    if action == "INTERNAL:NEXT_TRACK":
        play_next_track()
    elif action == "INTERNAL:EXPAND_SPACE":
        if os.path.exists("/usr/local/bin/manifoldctl"):
            manifold_idx = (manifold_idx + 1) % len(MANIFOLD_MODES)
            mode = MANIFOLD_MODES[manifold_idx]
            subprocess.Popen(["/usr/local/bin/manifoldctl", mode],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            notify("✦ Air-Sense Spatial Stretch", f"Expanded space-time fabric to: {mode.upper()}")
        else:
            notify("✦ Air-Sense Spatial Stretch", label)
    elif action == "INTERNAL:COMPRESS_SPACE":
        if os.path.exists("/usr/local/bin/manifoldctl"):
            subprocess.Popen(["/usr/local/bin/manifoldctl", "gargantua"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            notify("✦ Air-Sense Singularity", "Compressed space into Gargantua Black Hole")
        else:
            notify("✦ Air-Sense Singularity", label)
    else:
        subprocess.Popen(action, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        notify(f"✦ Air-Sense // {label}", f"Executed: {action}")
    return label

def count_extended_fingers(lm):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    ext = [lm[t].y < lm[p].y for t, p in zip(tips, pips)]
    return ext  # [index, middle, ring, pinky]

def main():
    cfg = load_config()
    cooldown = float(cfg.get("cooldown_seconds", 1.5))

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.68,
        min_tracking_confidence=0.65
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        notify("❌ Air-Sense Error", "Could not access webcam /dev/video0")
        sys.exit(1)

    prev_x = None
    last_trigger_t = 0.0
    status_Banner = "AIR-SENSE SPATIAL MATRIX ARMED"
    banner_until = 0.0
    peace_start = None
    prev_two_hand_ratio = None
    vol_smooth = 50.0

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        now = time.time()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if HUD_MODE:
            # Darken camera feed slightly for high-contrast Cyberpunk HUD overlay
            frame = cv2.convertScaleAbs(frame, alpha=0.65, beta=0)

        landmarks_list = res.multi_hand_landmarks or []

        # ======================================================================
        # 1. TWO-HAND SPATIAL TENSOR ("EXTEND & STRETCH SPACE")
        # ======================================================================
        if len(landmarks_list) == 2:
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
                prev_two_hand_ratio = prev_two_hand_ratio * 0.7 + norm_span * 0.3

                if (now - last_trigger_t) > cooldown:
                    # Stretch Hands Wide Apart -> Expand Space
                    if norm_span > 0.56 and delta_span > 0.035:
                        status_Banner = trigger_action("two_hand_expand", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0
                    # Bring Hands Together -> Compress into Singularity
                    elif norm_span < 0.20 and delta_span < -0.030:
                        status_Banner = trigger_action("two_hand_compress", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0

            if HUD_MODE:
                # Render live expanding/compressing Cosmic Particle Field between both palms
                radius = int(max(18, min(220, dist_px * 0.42)))
                cv2.line(frame, (c1x, c1y), (c2x, c2y), (255, 240, 0), 2)
                cv2.circle(frame, (mx, my), radius, (255, 0, 255), 2)
                cv2.circle(frame, (mx, my), max(6, radius // 3), (255, 255, 0), -1)
                for p_i in range(28):
                    ang = (p_i / 28.0) * math.tau + now * 2.5
                    r_orb = radius * (0.45 + 0.55 * math.sin(now * 3.0 + p_i))
                    px = int(mx + math.cos(ang) * r_orb)
                    py = int(my + math.sin(ang) * r_orb)
                    cv2.circle(frame, (px, py), 3, (255, 240, 0), -1)
                cv2.putText(frame, f"TENSOR SPAN: {int(norm_span*100)}%", (mx - 75, my - radius - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 240, 0), 2)

        # ======================================================================
        # 2. SINGLE-HAND SPATIAL GESTURES
        # ======================================================================
        elif len(landmarks_list) == 1:
            prev_two_hand_ratio = None
            lm = landmarks_list[0].landmark
            ext = count_extended_fingers(lm)
            palm_size = math.hypot(lm[9].x - lm[0].x, lm[9].y - lm[0].y) + 1e-6

            # A. Thumb + Index Pinch Dial (Index Up, Middle/Ring/Pinky Curled)
            if ext[0] and not ext[1] and not ext[2] and not ext[3]:
                pinch = math.hypot(lm[8].x - lm[4].x, lm[8].y - lm[4].y) / palm_size
                raw_vol = max(0.0, min(100.0, (pinch - 0.22) / 1.15 * 100.0))
                vol_smooth = vol_smooth * 0.72 + raw_vol * 0.28
                subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{int(vol_smooth)}%"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                status_Banner = f"VOLUME DIAL: {int(vol_smooth)}%"
                banner_until = now + 0.5
                if HUD_MODE:
                    x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                    x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # B. Peace Sign Hold (Index + Middle Up, Ring/Pinky Curled)
            elif ext[0] and ext[1] and not ext[2] and not ext[3]:
                if peace_start is None:
                    peace_start = now
                elif (now - peace_start) > 1.0 and (now - last_trigger_t) > cooldown:
                    status_Banner = trigger_action("peace_hold", cfg)
                    last_trigger_t = now
                    banner_until = now + 2.0
                    peace_start = None
            else:
                peace_start = None

            # C. Open Palm Wave Right / Left (All 4 Fingers Extended)
            if all(ext):
                cx = lm[9].x
                if prev_x is not None and (now - last_trigger_t) > cooldown:
                    dx = cx - prev_x
                    if dx > 0.14:
                        status_Banner = trigger_action("swipe_right", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0
                    elif dx < -0.14:
                        status_Banner = trigger_action("swipe_left", cfg)
                        last_trigger_t = now
                        banner_until = now + 2.0
                prev_x = cx
            else:
                prev_x = None
        else:
            prev_two_hand_ratio = None
            prev_x = None
            peace_start = None

        if HUD_MODE:
            for hand_lms in landmarks_list:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_lms, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 240, 0), thickness=2, circle_radius=3),
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 255), thickness=2)
                )
            msg = status_Banner if now < banner_until else "AIR-SENSE // 1-HAND: SWIPE/PINCH | 2-HAND: STRETCH/COMPRESS SPACE"
            cv2.rectangle(frame, (0, 0), (w, 42), (10, 10, 16), -1)
            cv2.putText(frame, msg, (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 240, 0), 2)
            cv2.imshow("Air-Sense Spatial Telepathy HUD (Press Q to close)", frame)
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), 27):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
