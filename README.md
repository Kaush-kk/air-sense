# ✦ Air-Sense — Dual-Hand Spatial Telepathy & Gesture Daemon for Linux

Control your Linux desktop and audio workflow touchlessly at 30 FPS using Google MediaPipe 3D hand-landmark tracking (`max_num_hands=2`). Works standalone or as the official spatial companion module for **[Veer AI](https://github.com/Kaush-kk/veer-jarvis-linux)**.

## Spatial Gestures (100% Customizable)
* **Two-Hand Spatial Stretch (`two_hand_expand`):** Hold both hands up and stretch them apart to expand the live neon tensor field and shift your desktop manifold (`manifoldctl`) or trigger any custom command.
* **Two-Hand Singularity Compress (`two_hand_compress`):** Bring both open palms together to collapse the particle field into a singularity (`gargantua` mode or custom command).
* **Open-Palm Swipe Right / Left:** Skip to the next track in `~/Vault/Music` or silence playback.
* **Thumb + Index Pinch Dial:** Smoothly dial PipeWire master system volume between 0% and 100%.
* **Peace Sign Hold (1.0s):** Launches Mission Control HUD (or any custom script).

## Customize Any Gesture Without Touching Python
* List all gestures and actions: `air-sense list`
* Rebind any gesture interactively: `air-sense set`
* Edit the raw JSON config: `air-sense edit` (`~/Vault/airsense_config.json`)

## One-Command Install

    git clone https://github.com/Kaush-kk/air-sense.git
    cd air-sense && ./install.sh
