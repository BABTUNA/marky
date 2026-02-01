#!/bin/bash
# Capture agent_architecture_diagram.html as PNG.
# Requires Chromium/Chrome (Google Chrome or Chromium).

HTML="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/agent_architecture_diagram.html"
OUT="$(dirname "$HTML")/agent_architecture_diagram_new.png"

if command -v google-chrome &>/dev/null; then
  BROWSER="google-chrome"
elif command -v chromium &>/dev/null; then
  BROWSER="chromium"
elif command -v chromium-browser &>/dev/null; then
  BROWSER="chromium-browser"
else
  echo "Open docs/agent_architecture_diagram.html in your browser and export/screenshot as PNG."
  echo "Save as docs/agent_architecture_diagram.png"
  exit 1
fi

"$BROWSER" --headless --disable-gpu --screenshot="$OUT" --window-size=800,1200 "file://$HTML" 2>/dev/null
if [ -f "$OUT" ]; then
  echo "Saved to $OUT"
  echo "Replace docs/agent_architecture_diagram.png with this file if desired."
else
  echo "Capture failed. Open docs/agent_architecture_diagram.html in browser and screenshot."
fi
