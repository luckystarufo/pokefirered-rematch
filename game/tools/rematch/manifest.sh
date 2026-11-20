#!/bin/sh
# Rematch (step 1.7): write rom-manifest.json describing where the web page
# finds the personalization block (ROM) and the ending marker (RAM).
# Addresses come from the linked ELF's symbol table, so they can't drift.
#
# usage: manifest.sh <objdump> <elf> <rom>   (prints JSON to stdout)
set -eu
OBJDUMP="$1"; ELF="$2"; ROM="$3"

sym() { # <name> -> "address size" (hex, no 0x)
    "$OBJDUMP" -t "$ELF" | awk -v n="$1" '$NF == n { print $1, $(NF-1); found=1 } END { if (!found) exit 1 }'
}
BLOCK=$(sym gRematchBlock) || { echo "manifest: gRematchBlock not found" >&2; exit 1; }
MARK=$(sym gRematchEndMarker) || { echo "manifest: gRematchEndMarker not found" >&2; exit 1; }
set -- $BLOCK; BLOCK_ADDR=$((0x$1)); BLOCK_SIZE=$((0x$2))
set -- $MARK;  MARK_ADDR=$((0x$1));  MARK_SIZE=$((0x$2))

ROM_SIZE=$(wc -c < "$ROM" | tr -d ' ')
ROM_SHA1=$(sha1sum "$ROM" | cut -d' ' -f1)
VERSION=$(awk '/#define REMATCH_BLOCK_VERSION/ { print $3 }' include/rematch.h)

cat <<JSON
{
  "manifestVersion": 1,
  "rom": { "file": "$(basename "$ROM")", "size": $ROM_SIZE, "sha1": "$ROM_SHA1" },
  "block": {
    "symbol": "gRematchBlock",
    "address": "$(printf '0x%08X' $BLOCK_ADDR)",
    "romOffset": $((BLOCK_ADDR - 0x08000000)),
    "size": $BLOCK_SIZE,
    "magic": "RMCH",
    "version": $VERSION
  },
  "endMarker": {
    "symbol": "gRematchEndMarker",
    "address": "$(printf '0x%08X' $MARK_ADDR)",
    "size": $MARK_SIZE,
    "values": { "none": 0, "endingStarted": $((0x524D0001)), "theEnd": $((0x524D0002)) }
  }
}
JSON
