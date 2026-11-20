#!/bin/sh
# Copy the freshly built ROM and its manifest next to the page (web/rom/, not in git).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cp "$HERE/../game/pokefirered.gba" "$HERE/rom/pokefirered.gba"
cp "$HERE/../game/rom-manifest.json" "$HERE/rom/rom-manifest.json"
echo "web/rom/ updated"
