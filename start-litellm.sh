#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$SCRIPT_DIR/venv-litellm/bin/activate"

litellm -c "$SCRIPT_DIR/config.yaml" --detailed_debug
