#!/bin/bash
echo "🗑️ Uninstalling Air-Sense Spatial Telepathy Engine..."
pkill -f "music_airsense.py" 2>/dev/null || true
sudo rm -f /usr/local/bin/air-sense
rm -f "$HOME/.veer/music_airsense.py"
rm -rf "$HOME/.air-sense"
echo "✅ Air-Sense completely uninstalled."
