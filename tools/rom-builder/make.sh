#!/bin/sh
# Run `make` for game/ inside the toolchain container.
#   tools/rom-builder/make.sh            -> make (builds game/pokefirered.gba)
#   tools/rom-builder/make.sh compare    -> make compare (checks byte-identical)
#   tools/rom-builder/make.sh --image    -> (re)build the toolchain image only
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
IMAGE=rematch-rom-builder

if [ "$1" = "--image" ] || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build -t "$IMAGE" "$HERE"
  [ "$1" = "--image" ] && exit 0
fi

exec docker run --rm -v "$REPO/game:/work" "$IMAGE" make "$@"
