# ✦ Air-Sense — 1-Hand & 2-Hand Spatial Telepathy Engine for Linux

Control your Linux desktop, dynamic wallpapers, and audio workflow touchlessly using Google MediaPipe 3D hand-landmark tracking (`max_num_hands=2`). Works standalone or as the official spatial companion to **[Veer AI](https://github.com/Kaush-kk/veer-jarvis-linux)**.

---

## 1. One-Command Installation

    git clone https://github.com/Kaush-kk/air-sense.git
    cd air-sense && ./install.sh

---

## 2. Complete Gesture & Customization Guide

### Launching Air-Sense
* **`air-sense hud`** — Opens the live Cyberpunk camera HUD window showing skeletal tracking, hold-progress rings, and the 2-hand particle tensor field (press **`Q`** to close).
* **`air-sense start`** — Runs Air-Sense invisibly in the background.
* **`air-sense stop`** — Stops Air-Sense and turns off your webcam.

### Default Static Finger-Hold & Dual-Hand Gestures
* **1 Finger Up (Thumb + Index Pinch):** Live volume dial (`0%` to `100%`) based on pinch distance.
* **2 Fingers Held (V-Sign for 0.65s):** Launches your HUD / Vault / Terminal (`INTERNAL:SMART_HUD`).
* **3 Fingers Held (Index + Middle + Ring for 0.65s):** Plays / skips to the next track in `~/Vault/Music`.
* **4 Fingers Held (Open Hand for 0.65s):** Immediately silences background audio.
* **Closed Fist Held (0.9s):** Triggers **Protocol Zero** lockdown (or native Linux session lock).
* **Two Hands Spread Apart (`two_hand_expand`):** Awakens and cycles your **Protocol Manifold** dynamic space-time wallpaper themes and color palettes.
* **Two Hands Brought Together (`two_hand_compress`):** Collapses the desktop fabric into the Minimalist Zen Sanctum.

### Customizing Any Gesture Action
* **Interactive Gesture Builder:** Run `air-sense set` to bind any gesture to any custom Linux command.
* **View Current Gesture Table:** Run `air-sense list`.
* **Edit Raw Config:** Run `air-sense edit` (`~/Vault/airsense_config.json`).

---

## 3. One-Command Complete Removal (Uninstall & Delete Cloned Repo)

To completely uninstall Air-Sense, stop the camera daemon, and delete the cloned GitHub folder:

    ~/air-sense/uninstall.sh && rm -rf ~/air-sense
