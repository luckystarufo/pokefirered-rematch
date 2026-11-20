#!/bin/sh
# Runs the AWS CDK CLI (or npm, with --npm) inside Docker, against infra/.
#   tools/cdk.sh synth            tools/cdk.sh diff            tools/cdk.sh deploy
#   tools/cdk.sh --npm install    (installs infra/node_modules)
# Your AWS credentials (~/.aws) are mounted read-only; the repo is mounted at /work.
set -eu
cd "$(dirname "$0")/.."
IMAGE=rematch-cdk
docker image inspect $IMAGE >/dev/null 2>&1 || docker build -q -t $IMAGE tools/cdk >/dev/null

ENTRY=cdk
if [ "${1:-}" = "--npm" ]; then ENTRY=npm; shift; fi

exec docker run --rm -i \
  -v "$PWD:/work" \
  -v "$HOME/.aws:/root/.aws:ro" \
  -e AWS_PROFILE -e AWS_REGION -e AWS_DEFAULT_REGION \
  -e CDK_DISABLE_VERSION_CHECK=1 -e CDK_DISABLE_CLI_TELEMETRY=1 \
  --entrypoint $ENTRY $IMAGE "$@"
