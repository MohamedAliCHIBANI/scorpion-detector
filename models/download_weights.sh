#!/usr/bin/env bash
# Download YOLO model weights from the GitHub Release.
# Usage: bash models/download_weights.sh
set -euo pipefail

REPO="MohamedAliCHIBANI/scorpion-detector"
FILENAME="best.pt"
DEST="$(dirname "$0")/${FILENAME}"

if [ -f "$DEST" ]; then
    echo "Model weights already present at $DEST — skipping download."
    exit 0
fi

echo "Downloading ${FILENAME} from latest GitHub Release…"
RELEASE_URL="https://github.com/${REPO}/releases/latest/download/${FILENAME}"

if command -v curl &> /dev/null; then
    curl -L --fail --progress-bar -o "$DEST" "$RELEASE_URL"
elif command -v wget &> /dev/null; then
    wget --show-progress -O "$DEST" "$RELEASE_URL"
else
    echo "Error: neither curl nor wget is available." >&2
    exit 1
fi

echo "Saved to $DEST"
