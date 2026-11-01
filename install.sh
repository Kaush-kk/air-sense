#!/bin/bash
set -e
echo "✦ Installing Air-Sense (1-Hand & 2-Hand Spatial Telepathy Engine)..."

if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3.12 libnotify mpv
elif command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3-venv python3-pip libnotify-bin mpv
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm python libnotify mpv
fi

# Share ~/.veer/venv if Veer is installed, otherwise build ~/.air-sense/venv
TARGET_DIR="$HOME/.veer"
[ ! -d "$TARGET_DIR" ] && TARGET_DIR="$HOME/.air-sense"
mkdir -p "$TARGET_DIR" "$HOME/Vault"

PY_BIN=$(command -v python3.12 || command -v python3)
if [ ! -d "$TARGET_DIR/venv" ]; then
    "$PY_BIN" -m venv "$TARGET_DIR/venv"
fi

"$TARGET_DIR/venv/bin/python" -m pip install --upgrade pip
"$TARGET_DIR/venv/bin/python" -m pip install "mediapipe>=0.10.14,<0.10.22" opencv-python

cp music_airsense.py "$TARGET_DIR/music_airsense.py"
chmod +x "$TARGET_DIR/music_airsense.py"
[ ! -f "$HOME/Vault/airsense_config.json" ] && cp airsense_config.json "$HOME/Vault/airsense_config.json"

sudo cp air-sense /usr/local/bin/air-sense
sudo chmod +x /usr/local/bin/air-sense

echo "✅ Air-Sense installed! Run 'air-sense hud' to test 2-hand spatial stretching or 'air-sense set' to customize gestures."
