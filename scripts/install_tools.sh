#!/bin/bash
# install_tools.sh - Fetches pinned binaries for Airlock local development.
# Version: Syft v1.0.1

set -e

# 1. Define Version and Target
SYFT_VERSION="1.0.1"
BIN_DIR="./bin"
mkdir -p $BIN_DIR

echo "--- Installing Airlock Dev Tools ---"

# 2. Detect OS
OS_TYPE=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS_TYPE" in
  linux*)   PLATFORM="linux" ;;
  darwin*)  PLATFORM="darwin" ;;
  msys*|cygwin*|mingw*) PLATFORM="windows" ;;
  *)        echo "Unsupported OS: $OS_TYPE"; exit 1 ;;
esac

# 3. Detect Architecture
ARCH_TYPE=$(uname -m)
case "$ARCH_TYPE" in
  x86_64)  ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)       echo "Unsupported Architecture: $ARCH_TYPE"; exit 1 ;;
esac

echo "Detected: $PLATFORM ($ARCH)"

# 4. Download Syft
SYFT_BINARY="syft_${SYFT_VERSION}_${PLATFORM}_${ARCH}"
if [ "$PLATFORM" == "windows" ]; then
    SYFT_URL="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_windows_amd64.zip"
    echo "Downloading $SYFT_URL..."
    curl -sLo "$BIN_DIR/syft.zip" "$SYFT_URL"
    unzip -o "$BIN_DIR/syft.zip" -d "$BIN_DIR"
    rm "$BIN_DIR/syft.zip"
else
    SYFT_URL="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_${PLATFORM}_${ARCH}.tar.gz"
    echo "Downloading $SYFT_URL..."
    curl -sLo "$BIN_DIR/syft.tar.gz" "$SYFT_URL"
    tar -xzf "$BIN_DIR/syft.tar.gz" -C "$BIN_DIR" syft
    rm "$BIN_DIR/syft.tar.gz"
    chmod +x "$BIN_DIR/syft"
fi

echo "--- Success: Syft v$SYFT_VERSION installed to $BIN_DIR/syft ---"