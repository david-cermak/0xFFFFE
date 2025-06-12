#!/bin/bash

# setup_deps.sh - Script to pull ESP-protocols dependencies for mDNS
#

set -e  # Exit on any error

# Configuration
ESP_PROTOCOLS_VERSION=mdns-v1.8.2
ESP_PROTOCOLS_REPO="https://github.com/espressif/esp-protocols.git"
DEPS_DIR="deps"
ESP_PROTOCOLS_DIR="$DEPS_DIR/esp-protocols"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up ESP-protocols dependencies for mDNS...${NC}"
echo -e "${GREEN}Repository: ${YELLOW}$ESP_PROTOCOLS_REPO${NC}"
echo -e "${GREEN}Version: ${YELLOW}$ESP_PROTOCOLS_VERSION${NC}"

# Create deps directory if it doesn't exist
if [ ! -d "$DEPS_DIR" ]; then
    echo -e "${YELLOW}Creating deps directory...${NC}"
    mkdir -p "$DEPS_DIR"
fi

# Clone ESP-protocols repository if not already present
if [ ! -d "$ESP_PROTOCOLS_DIR" ]; then
    echo -e "${YELLOW}Cloning ESP-protocols repository...${NC}"
    git clone "$ESP_PROTOCOLS_REPO" "$ESP_PROTOCOLS_DIR"
    cd "$ESP_PROTOCOLS_DIR"
    if [ "$ESP_PROTOCOLS_VERSION" != "master" ]; then
        echo -e "${YELLOW}Checking out version: $ESP_PROTOCOLS_VERSION${NC}"
        git checkout "$ESP_PROTOCOLS_VERSION"
    fi
    cd - > /dev/null
else
    echo -e "${YELLOW}ESP-protocols repository already exists...${NC}"
fi

# Check if mDNS component exists
if [ ! -d "$ESP_PROTOCOLS_DIR/components/mdns" ]; then
    echo -e "${RED}Error: mDNS component not found in ESP-protocols repository${NC}"
    exit 1
fi

# Go to the fuzzer directory
cd deps/esp-protocols/components/mdns/tests/test_afl_fuzz_host
# Test build without instrumentation
make INSTR=off
make clean

podman run --rm -it -v $(pwd):/app -w /app --privileged --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --name fuzzer fuzzer:latest
