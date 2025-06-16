#!/bin/bash
set -e  # Exit on error

# Setup directories
INPUT_VECTORS=$(pwd)/input_vectors/sample_inputs.txt
OUTPUT_DIR=$(pwd)/fuzzing_outputs
mkdir -p "$OUTPUT_DIR"

# Build the project
echo "Building the project..."
cd ../../projects/hello_world
mkdir -p build
cd build
cmake ..
make
BINARY_PATH=$(pwd)/hello
cd ../..

# Run the fuzzer with the hello world target
echo "Running the fuzzer..."
cd ../tools/radamsa
./run_fuzzer.sh -n 1000 -t 5 -b "$BINARY_PATH" -s "$INPUT_VECTORS" \
    --crashes-dir "$OUTPUT_DIR/crashes" \
    --timeouts-dir "$OUTPUT_DIR/timeouts" \
    --errors-dir "$OUTPUT_DIR/errors" \
    --log-file "$OUTPUT_DIR/fuzzing.log"
