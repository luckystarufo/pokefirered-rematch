#!/bin/sh
# Runs inside the container with game/ mounted at /work.
# The Makefile expects agbcc at tools/agbcc/ inside the repo (gitignored),
# so copy the image's prebuilt copy there if it's missing.
set -e
if [ ! -x /work/tools/agbcc/bin/agbcc ]; then
  echo "[rom-builder] installing agbcc into game/tools/agbcc"
  mkdir -p /work/tools
  cp -R /opt/agbcc-dist/tools/agbcc /work/tools/agbcc
fi

# Same idea for the Poryscript binary (its two config JSONs are tracked in git).
# Always re-copied, so bumping PORYSCRIPT_TAG in the image takes effect.
mkdir -p /work/tools/poryscript
cp /opt/poryscript/poryscript /work/tools/poryscript/poryscript

# Default to a parallel build using every CPU the container has.
if [ "$1" = "make" ]; then
  shift
  exec make -j"$(nproc)" "$@"
fi
exec "$@"
