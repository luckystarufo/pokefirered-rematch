#!/bin/sh
# Puts the current page + ROM online (or previews what would change).
#   tools/deploy.sh          deploy (asks before creating/changing security-related resources)
#   tools/deploy.sh diff     show what would change, deploy nothing
#   tools/deploy.sh synth    just build the CloudFormation template locally
# Uses the ROM in game/ (build it first with tools/rom-builder/make.sh) and the page in web/.
set -eu
cd "$(dirname "$0")/.."

[ -f .local/deploy.json ] || { echo "Missing .local/deploy.json (email + secrets)"; exit 1; }
[ -f game/pokefirered.gba ] || { echo "No ROM: run tools/rom-builder/make.sh first"; exit 1; }
[ -f web/emulator/loader.js ] && [ -f web/fonts/press-start-2p.woff2 ] || tools/fetch-web-vendor.sh >/dev/null

# The ROM is mostly empty padding: gzip it once here (CloudFront doesn't compress .gba files), and the
# browser unpacks it transparently (Content-Encoding: gzip).
rm -rf .local/rom-upload && mkdir -p .local/rom-upload
gzip -9 -n -c game/pokefirered.gba > .local/rom-upload/pokefirered.gba
gzip -9 -n -c game/rom-manifest.json > .local/rom-upload/rom-manifest.json

tools/cdk.sh --npm run --silent typecheck

case "${1:-deploy}" in
  deploy) shift 2>/dev/null || true; tools/cdk.sh deploy Rematch --outputs-file /work/.local/outputs.json "$@" ;;
  *)      tools/cdk.sh "$@" ;;
esac
