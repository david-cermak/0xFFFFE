#!/bin/bash
set -e  # Exit on error

# Setup directories
INPUT_VECTORS_DIR="input_vectors"
INPUT_VECTORS="$INPUT_VECTORS_DIR/sample_inputs.txt"
OUTPUT_DIR="fuzzing_outputs"
mkdir -p "$INPUT_VECTORS_DIR" "$OUTPUT_DIR"

# Create sample input file if it doesn't exist
if [ ! -f "$INPUT_VECTORS" ]; then
    echo "Creating sample input file..."
    cat > "$INPUT_VECTORS" << 'EOF'
mqtt/home/temperature {"device_id":"sensor01","temperature":23.5,"status":"active"}
mqtt/device/led {"action":"toggle","brightness":80,"color":"red"}
mqtt/sensors/humidity {"device_id":"esp32_01","humidity":65,"location":"kitchen"}
GET /api/sensors {"action":"read","sensor":"temperature"}
POST /device/control {"action":"set","value":"on","device":"fan"}
GET /status {"device_id":"thermostat","action":"get_state"}
POST /api/data {"temperature":22.5,"humidity":60,"timestamp":1234567890}
mqtt/alarm/motion {"sensor":"pir_01","status":"detected","room":"living_room"}
EOF
fi

# Build the sample project
echo "Building the sample project..."
cd ../../projects/sample
mkdir -p build
cd build
cmake -DENABLE_ASAN=ON -DENABLE_UBSAN=ON ..
make
BINARY_PATH=$(pwd)/iot_parser
cd ../..

# Run the fuzzer with the sample target
echo "Running the fuzzer..."
cd ../tools/radamsa
./run_fuzzer.sh -n 1000 -t 5 -b "$BINARY_PATH" -s "../../sessions/01_radamsa_sample/$INPUT_VECTORS" \
    --crashes-dir "../../sessions/01_radamsa_sample/$OUTPUT_DIR/crashes" \
    --timeouts-dir "../../sessions/01_radamsa_sample/$OUTPUT_DIR/timeouts" \
    --errors-dir "../../sessions/01_radamsa_sample/$OUTPUT_DIR/errors" \
    --log-file "../../sessions/01_radamsa_sample/$OUTPUT_DIR/fuzzing.log"
