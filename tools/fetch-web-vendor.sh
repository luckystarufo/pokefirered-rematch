#!/bin/sh
# Downloads the third-party files the page serves itself (so the night never depends on someone else's CDN):
#  - EmulatorJS 4.2.3 (GPL-3.0; https://github.com/EmulatorJS/EmulatorJS), only the files a GBA game needs,
#    with the mGBA core (MPL-2.0);
#  - the "Press Start 2P" font (SIL Open Font License; https://fonts.google.com/specimen/Press+Start+2P).
# Output: web/emulator/ and web/fonts/ (both git-ignored). Run again after changing EJS_VERSION.
set -eu
cd "$(dirname "$0")/.."

EJS_VERSION=4.2.3
EJS="https://cdn.emulatorjs.org/$EJS_VERSION/data"
FILES="loader.js emulator.min.js emulator.min.css compression/extract7z.js
       cores/reports/mgba.json cores/mgba-wasm.data cores/mgba-legacy-wasm.data"

rm -rf web/emulator.tmp && mkdir -p web/emulator.tmp
for f in $FILES; do
  mkdir -p "web/emulator.tmp/$(dirname "$f")"
  curl -fsSL "$EJS/$f" -o "web/emulator.tmp/$f"
done
echo "EmulatorJS $EJS_VERSION from $EJS" > web/emulator.tmp/VERSION
rm -rf web/emulator && mv web/emulator.tmp web/emulator

# The font: ask Google Fonts' CSS API for the woff2 file, then serve it ourselves.
mkdir -p web/fonts
# (the last @font-face in the CSS is the basic Latin subset, which covers everything the page shows, é included)
FONT_URL=$(curl -fsSL -A "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36" \
  "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" | grep -o 'https://fonts.gstatic.com/[^)]*\.woff2' | tail -1)
curl -fsSL "$FONT_URL" -o web/fonts/press-start-2p.woff2

(cd web && find emulator fonts -type f | sort | xargs shasum -a 256)
