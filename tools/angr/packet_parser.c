#include <stdint.h>

uint32_t s_header = 1;

void _exit(int code) {
    while (1);  // trap
}

void _abort(void) {
    while (1);  // trap
}

// Simple protocol: [SOF][LEN-L][LEN-H][CHECKSUM]
//
#define SOF_CHAR 0x40
#define XOR_CHAR 0xFC
#define MAX_PAYLOAD 0xFFF

int process_packet(int16_t len)
{
	if (len > MAX_PAYLOAD) {
		// Should never happen
		_abort();
	}
}


void main(int argc, char** argv)
{
	if ((s_header & SOF_CHAR) == 0x40) {
		uint8_t len0 = (s_header & 0xFF00) >> 8;
		uint8_t len1 = (s_header & 0xFF0000) >> 16;
		uint8_t checksum = (s_header & 0xFF000000) >> 24;
		uint8_t checksum_calculated = XOR_CHAR ^ len0 ^ len1;
		uint16_t len = len0 + len1<<8;
		if (checksum == checksum_calculated) {
			process_packet(len);
		}

	}
}
