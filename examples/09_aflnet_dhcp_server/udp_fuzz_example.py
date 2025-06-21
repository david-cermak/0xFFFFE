#!/usr/bin/env python3
"""
UDP Fuzz Data Sender Example

This script demonstrates how to send fuzz data to the lwIP fuzz test client
via UDP. It can be used to test the UDP input functionality.

Usage:
    python3 udp_fuzz_example.py [server_ip] [port] [data_file]

Example:
    python3 udp_fuzz_example.py 127.0.0.1 8888 test_data.bin
"""

import socket
import sys
import time

def send_fuzz_data(server_ip, port, data):
    """Send fuzz data to the UDP server"""
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set socket timeout
        sock.settimeout(5.0)

        # Send data
        print(f"Sending {len(data)} bytes to {server_ip}:{port}")
        sock.sendto(data, (server_ip, port))

        print("Data sent successfully")
        sock.close()

    except socket.error as e:
        print(f"Socket error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

def main():
    # Default values
    server_ip = "127.0.0.1"
    port = 50037

    # Parse command line arguments
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    # Generate or read test data
    if len(sys.argv) > 3:
        # Read from file
        try:
            with open(sys.argv[3], 'rb') as f:
                data = f.read()
            print(f"Read {len(data)} bytes from {sys.argv[3]}")
        except FileNotFoundError:
            print(f"Error: File {sys.argv[3]} not found")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    else:
        # Generate sample fuzz data (Ethernet frame with IP packet)
        print("Generating sample fuzz data...")

        # Sample Ethernet frame with IP packet
        data = bytes([
            # Ethernet header (14 bytes)
            0x00, 0x23, 0xC1, 0xDE, 0xD0, 0x0D,  # Destination MAC
            0x28, 0x00, 0x00, 0x22, 0x2B, 0x38,  # Source MAC
            0x08, 0x00,                          # EtherType (IPv4)

            # IP header (20 bytes)
            0x45, 0x00, 0x00, 0x28,              # Version, IHL, ToS, Total Length
            0x00, 0x01, 0x00, 0x00,              # ID, Flags, Fragment Offset
            0x40, 0x01, 0x00, 0x00,              # TTL, Protocol (ICMP), Checksum
            0xAC, 0x1E, 0x73, 0x25,              # Source IP (172.30.115.37)
            0xAC, 0x1E, 0x73, 0x54,              # Destination IP (172.30.115.84)

            # ICMP echo request (8 bytes)
            0x08, 0x00, 0x00, 0x00,              # Type, Code, Checksum
            0x00, 0x01, 0x00, 0x01,              # Identifier, Sequence Number
        ])

        print(f"Generated {len(data)} bytes of sample data")

    # Send the data
    if send_fuzz_data(server_ip, port, data):
        print("Fuzz data sent successfully!")
        return 0
    else:
        print("Failed to send fuzz data")
        return 1

if __name__ == "__main__":
    sys.exit(main())
