# UDP Fuzz Input for lwIP

This document describes the UDP input functionality added to the lwIP fuzz testing framework.

## Overview

The `lwip_fuzztest` function has been modified to accept fuzz data from a UDP socket instead of stdin. This allows for remote fuzz testing and integration with external fuzz testing tools.

## Configuration

### Default Settings

The UDP client is configured with the following default values (defined in `fuzz_common.h`):

```c
#ifndef FUZZ_UDP_SERVER_ADDR
#define FUZZ_UDP_SERVER_ADDR "127.0.0.1"
#endif

#ifndef FUZZ_UDP_SERVER_PORT
#define FUZZ_UDP_SERVER_PORT 8888
#endif
```

### Compile-time Configuration

You can override these defaults by defining the macros before including the header:

```c
#define FUZZ_UDP_SERVER_ADDR "192.168.1.100"
#define FUZZ_UDP_SERVER_PORT 9999
#include "fuzz_common.h"
```

## Usage

### Command Line Options

The `lwip_fuzztest` function now supports the following command line options:

1. **File input** (original behavior):
   ```bash
   ./fuzz_test input_file.bin
   ```

2. **UDP input with default settings**:
   ```bash
   ./fuzz_test --udp
   ```

3. **UDP input with custom server address**:
   ```bash
   ./fuzz_test --udp 192.168.1.100
   ```

4. **UDP input with custom server address and port**:
   ```bash
   ./fuzz_test --udp 192.168.1.100 9999
   ```

### UDP Client Behavior

The UDP client:

1. Creates a UDP socket
2. Sets a 5-second timeout for receiving data
3. Connects to the specified UDP server
4. Waits for data to be sent from the server
5. Processes the received data as fuzz input
6. Closes the connection

## Example Usage

### Using the Python Test Script

A Python script (`udp_fuzz_example.py`) is provided to test the UDP functionality:

```bash
# Send sample fuzz data to default server (127.0.0.1:8888)
python3 udp_fuzz_example.py

# Send sample fuzz data to custom server
python3 udp_fuzz_example.py 192.168.1.100 9999

# Send data from a file
python3 udp_fuzz_example.py 127.0.0.1 8888 test_data.bin
```

### Integration with Fuzz Testing Tools

The UDP input can be integrated with various fuzz testing frameworks:

1. **AFL++**: Use `afl-fuzz` with a custom network input
2. **Honggfuzz**: Configure network fuzzing
3. **Custom tools**: Send fuzz data via UDP to the test client

## Implementation Details

### Key Functions

- `read_data_from_udp()`: Reads fuzz data from a UDP socket
- Modified `lwip_fuzztest()`: Supports UDP input via command line options

### Error Handling

The UDP client includes comprehensive error handling:

- Socket creation failures
- Invalid server addresses
- Connection failures
- Timeout handling (5-second timeout)
- Data reception errors

### Timeout Behavior

If no data is received within 5 seconds, the client will:

1. Print a timeout message
2. Return 0 bytes received
3. Continue with the fuzz test (which will likely process empty data)

## Security Considerations

- The UDP client only receives data and does not send any responses
- No authentication is performed - any UDP server can send data
- Consider firewall rules to restrict access if needed
- The 5-second timeout prevents indefinite blocking

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure the UDP server is running and accessible
2. **Timeout**: Check if the server is sending data within 5 seconds
3. **Invalid address**: Verify the server IP address is correct
4. **Permission denied**: Check firewall settings and port availability

### Debug Output

The UDP client provides detailed debug output:

```
UDP client connected to 127.0.0.1:8888, waiting for fuzz data...
Received 1024 bytes from UDP server
```

## Future Enhancements

Potential improvements to consider:

1. **Multiple packet support**: Receive multiple UDP packets
2. **Continuous mode**: Keep connection open for multiple fuzz iterations
3. **Authentication**: Add basic authentication mechanisms
4. **Compression**: Support compressed fuzz data
5. **Statistics**: Add packet statistics and timing information
