
# Install dependencies as described in projects/mdns

# Start AFL++ in a container

podman run -it -v $(pwd):/mnt aflplusplus bash

# Install the deps in the container

apt install libbsd-dev

# Start fuzzing

make fuzz
