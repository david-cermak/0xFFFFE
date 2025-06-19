set -e  # Exit on any error

# Configuration
ESP_IDF_VERSION=ebebda9604b5ec22c56c53619a332410c211410a
ESP_IDF_REPO="https://github.com/espressif/esp-idf.git"
DEPS_DIR="deps"
ESP_IDF_DIR="$DEPS_DIR/idf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create deps directory if it doesn't exist
mkdir -p "$DEPS_DIR"

# Clone ESP-IDF if it doesn't exist
if [ ! -d "$ESP_IDF_DIR" ]; then
    echo -e "${YELLOW}Cloning ESP-IDF...${NC}"
    git clone --depth 1 "$ESP_IDF_REPO" "$ESP_IDF_DIR"
    cd "$ESP_IDF_DIR"
    git fetch --depth 1 origin "$ESP_IDF_VERSION"
    git checkout "$ESP_IDF_VERSION"
    cd - > /dev/null
fi

# Apply the lwip globals patch
echo -e "${YELLOW}Applying lwip globals patch...${NC}"
cd "$ESP_IDF_DIR"
git apply "$(dirname "$0")/multiple-defs-of-lwip-globals.patch"
cd - > /dev/null

# Initialize and update submodules
echo -e "${YELLOW}Initializing ESP-IDF submodules...${NC}"
cd "$ESP_IDF_DIR"
git submodule update --init --recursive --depth 1
cd - > /dev/null

echo -e "${GREEN}ESP-IDF setup completed successfully!${NC}"
