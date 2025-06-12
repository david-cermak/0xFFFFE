# mDNS Project with Make Build System

This project demonstrates how to use the mDNS component from [ESP-protocols](https://github.com/espressif/esp-protocols) with a Make-based build system.

## Overview

The ESP-protocols repository contains a collection of protocol components for ESP-IDF, including mDNS (Multicast DNS). This project sets up a Make-based build system to work with these components.

## Project Structure

```
mdns/
├── setup_deps.sh          # Script to clone ESP-protocols and setup dependencies
├── Makefile               # Make-based build system
├── src/                   # Source code directory
│   └── main.c            # Main application file
├── deps/                  # Dependencies directory (created by setup script)
├── mdns_component/        # Symbolic link to mDNS component
├── common_components/     # Symbolic link to common components
└── include/               # Include directory with headers
```

## Quick Start

1. **Setup Dependencies**
   ```bash
   chmod +x setup_deps.sh
   ./setup_deps.sh
   ```

   Or specify a specific version/tag:
   ```bash
   ESP_PROTOCOLS_VERSION=v1.0.0 ./setup_deps.sh
   ESP_PROTOCOLS_VERSION=eppp-v0.3.1 ./setup_deps.sh
   ```

   This will:
   - Clone the ESP-protocols repository
   - Checkout the specified version (defaults to master)
   - Create symbolic links to mDNS component
   - Set up include directories

2. **Build the Project**
   ```bash
   make
   ```

3. **Run the Application**
   ```bash
   make run
   ```

## Available Make Targets

- `make` or `make all` - Build the project
- `make setup` - Setup dependencies if not present
- `make deps` - Force setup dependencies
- `make clean` - Clean build artifacts
- `make distclean` - Clean everything including dependencies
- `make run` - Run the compiled program
- `make debug` - Debug the program with GDB
- `make help` - Show help message

## Important Notes

### ESP-IDF Compatibility

The mDNS component from ESP-protocols is specifically designed for ESP-IDF (Espressif IoT Development Framework) and targets ESP32 microcontrollers. It has dependencies on:

- ESP-IDF system components
- FreeRTOS
- ESP32-specific networking stack
- ESP32 hardware abstraction layer

### Linux Adaptation

To use mDNS functionality on Linux, you have several options:

1. **Avahi** - The most common mDNS implementation for Linux
   ```bash
   sudo apt-get install libavahi-client-dev
   ```

2. **Apple Bonjour SDK** - Cross-platform mDNS implementation

3. **Custom adaptation** - Modify the ESP-protocols mDNS component for Linux

### Example Usage with Avahi

For a Linux-compatible mDNS implementation, consider using Avahi:

```c
#include <avahi-client/client.h>
#include <avahi-client/publish.h>
#include <avahi-common/simple-watch.h>
```

## Dependencies

- **Build Tools**: gcc, make, git
- **Runtime**: pthread library
- **Optional**: gdb (for debugging)

## ESP-protocols Repository

The setup script clones from: https://github.com/espressif/esp-protocols

This repository contains:
- mDNS component
- WebSocket client
- MQTT C++ wrapper
- ASIO port
- And many other networking protocol components

## Configuration

### Makefile Configuration

You can modify the Makefile to:
- Change compiler flags (`CFLAGS`)
- Add additional libraries (`LIBS`)
- Modify include paths (`INCLUDES`)
- Change project name (`PROJECT_NAME`)

### Version Management

The setup script supports pinning to specific versions of the ESP-protocols repository:

```bash
# Use latest master (default)
./setup_deps.sh

# Use a specific release tag
ESP_PROTOCOLS_VERSION=eppp-v0.3.1 ./setup_deps.sh

# Use a specific commit hash
ESP_PROTOCOLS_VERSION=abc123def ./setup_deps.sh

# Use a specific branch
ESP_PROTOCOLS_VERSION=release/v5.0 ./setup_deps.sh
```

**Available versions** can be found at: https://github.com/espressif/esp-protocols/releases

## Troubleshooting

1. **Permission Issues**
   ```bash
   chmod +x setup_deps.sh
   ```

2. **Missing Dependencies**
   ```bash
   make deps  # Force re-setup
   ```

3. **Build Errors**
   ```bash
   make clean && make
   ```

4. **Full Reset**
   ```bash
   make distclean && make deps && make
   ```

## Contributing

This is a demonstration project. For the actual ESP-protocols components, please contribute to the upstream repository at https://github.com/espressif/esp-protocols.

## License

This project follows the same license as the ESP-protocols repository. Please refer to the LICENSE file in the ESP-protocols repository for details.
