set -e  # Exit on any error

# Configuration
PROTO_VERSION=6664b881f4bc3a84350c6434b91de314ce21a1f0 # mdns/refactor
PROTO_REPO="https://github.com/david-cermak/esp-protocols.git"

DEPS_DIR="deps"
PROTO_DIR="$DEPS_DIR/esp-protocols"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create deps directory if it doesn't exist
mkdir -p "$DEPS_DIR"

# Clone ESP-IDF if it doesn't exist
if [ ! -d "$PROTO_DIR" ]; then
    echo -e "${YELLOW}Cloning esp-protocols...${NC}"
    git clone --depth 1 "$PROTO_REPO" "$PROTO_DIR"
    cd "$PROTO_DIR"
    git fetch --depth 1 origin "$PROTO_VERSION"
    git checkout "$PROTO_VERSION"
    cd - > /dev/null
fi

echo -e "${GREEN}esp-protocols setup completed successfully!${NC}"
