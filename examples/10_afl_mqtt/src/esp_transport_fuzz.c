/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "esp_transport.h"

typedef enum {
    FUZZ_MODE_HANDSHAKE = 0,
    FUZZ_MODE_CONNECTED,
    FUZZ_MODE_SUBSCRIBE,
    FUZZ_MODE_QOS,
    FUZZ_MODE_MQTT5,
    FUZZ_MODE_DYNAMIC,
} fuzz_mode_t;

typedef struct {
    const unsigned char* in;
    size_t in_len;
    size_t in_off;
    unsigned char* rx;
    size_t rx_len;
    size_t rx_off;
    int connected;
    int autopilot;
    fuzz_mode_t mode;
    int frag; // max bytes per read (<=0 means unlimited)
} fuzz_state_t;

static void push_rx(fuzz_state_t* s, const unsigned char* data, size_t len)
{
    if (len == 0) {
        return;
    }
    size_t avail = s->rx_len - s->rx_off;
    if (s->rx_off > 0 && avail == 0) {
        // reset to start when fully consumed
        s->rx_len = 0; s->rx_off = 0;
    }
    unsigned char* nrx = (unsigned char*)realloc(s->rx, s->rx_len + len);
    if (!nrx) {
        return;
    }
    s->rx = nrx;
    memcpy(s->rx + s->rx_len, data, len);
    s->rx_len += len;
}

static int fuzz_connect(esp_transport_handle_t t, const char* host, int port, int timeout_ms)
{
    (void)host;
    (void)port;
    (void)timeout_ms;
    ((fuzz_state_t*)t->data)->connected = 1;
    return 0;
}

static int fuzz_read(esp_transport_handle_t t, char* buf, int len, int timeout_ms)
{
    (void)timeout_ms;
    fuzz_state_t* s = (fuzz_state_t*)t->data;
    if (!s->connected) {
        t->last_errno = ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT;
        errno = EAGAIN;
        return -1;
    }
    // Serve injected RX first
    size_t rx_avail = (s->rx_len > s->rx_off) ? (s->rx_len - s->rx_off) : 0;
    if (rx_avail > 0) {
        size_t cap = (s->frag > 0 && s->frag < len) ? (size_t)s->frag : (size_t)len;
        int n = (int)(cap < rx_avail ? cap : rx_avail);
        memcpy(buf, s->rx + s->rx_off, n);
        s->rx_off += n;
        if (s->rx_off == s->rx_len) {
            // fully consumed; reset indices (buffer kept for reuse)
            s->rx_off = s->rx_len = 0;
        }
        return n;
    }
    if (s->in_off >= s->in_len) {
        t->last_errno = ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT;
        errno = EAGAIN;
        return -1;
    }
    size_t rem = s->in_len - s->in_off;
    size_t cap = (s->frag > 0 && s->frag < len) ? (size_t)s->frag : (size_t)len;
    int n = (int)(cap < rem ? cap : rem);
    memcpy(buf, s->in + s->in_off, n);
    s->in_off += n;
    return n;
}

static int parse_varint_remaining(const unsigned char* p, int in_len, int* out_len)
{
    int mul = 1; int value = 0; int i = 0;
    while (i < in_len) {
        unsigned char b = p[i++];
        value += (b & 0x7F) * mul;
        if ((b & 0x80) == 0) {
            break;
        }
        mul *= 128;
        if (mul > (128 * 128 * 128)) {
            break;
        }
    }
    if (out_len) {
        *out_len = i;
    }
    return value;
}

static int fuzz_write(esp_transport_handle_t t, const char* buf, int len, int timeout_ms)
{
    (void)timeout_ms;
    fuzz_state_t* s = (fuzz_state_t*)t->data;
    if (!s->autopilot || len <= 0) {
        return len;
    }

    unsigned char type = ((unsigned char)buf[0]) & 0xF0;
    // CONNECT -> CONNACK (connected or mqtt5 modes)
    if (type == 0x10 && (s->mode == FUZZ_MODE_CONNECTED || s->mode == FUZZ_MODE_MQTT5)) {
        if (s->mode == FUZZ_MODE_MQTT5) {
            // MQTT v5 minimal CONNACK: flags(0), reason code(0), properties len(0)
            static const unsigned char connack5[] = { 0x20, 0x03, 0x00, 0x00, 0x00 };
            push_rx(s, connack5, sizeof(connack5));
        } else {
            static const unsigned char connack[] = { 0x20, 0x02, 0x00, 0x00 };
            push_rx(s, connack, sizeof(connack));
        }
    }
    // PINGREQ -> PINGRESP
    else if (type == 0xC0) {
        static const unsigned char pingresp[] = { 0xD0, 0x00 };
        push_rx(s, pingresp, sizeof(pingresp));
    }
    // SUBSCRIBE -> SUBACK (subscribe/connected/mqtt5)
    else if (type == 0x80 && (s->mode == FUZZ_MODE_SUBSCRIBE || s->mode == FUZZ_MODE_CONNECTED || s->mode == FUZZ_MODE_MQTT5)) {
        // Parse remaining length to find packet id
        int rem_len_bytes = 0;
        (void)parse_varint_remaining((const unsigned char*)buf + 1, len - 1, &rem_len_bytes);
        int fh_len = 1 + rem_len_bytes;
        if (len >= fh_len + 2) {
            unsigned char id_hi = (unsigned char)buf[fh_len + 0];
            unsigned char id_lo = (unsigned char)buf[fh_len + 1];
            if (s->mode == FUZZ_MODE_MQTT5) {
                // MQTT v5 SUBACK: PacketId(2), PropertiesLen(0), ReasonCode(0x00)
                unsigned char suback5[6] = { 0x90, 0x04, id_hi, id_lo, 0x00, 0x00 };
                push_rx(s, suback5, sizeof(suback5));
            } else {
                unsigned char suback[5] = { 0x90, 0x03, id_hi, id_lo, 0x00 };
                push_rx(s, suback, sizeof(suback));
            }
        }
    }
    // PUBREL -> PUBCOMP (qos mode or connected)
    else if (type == 0x60 && (s->mode == FUZZ_MODE_QOS || s->mode == FUZZ_MODE_CONNECTED)) {
        // Note: PUBREL control byte is 0x62 (0x60 with flags)
        int rem_len_bytes = 0;
        (void)parse_varint_remaining((const unsigned char*)buf + 1, len - 1, &rem_len_bytes);
        int fh_len = 1 + rem_len_bytes;
        if (len >= fh_len + 2) {
            unsigned char id_hi = (unsigned char)buf[fh_len + 0];
            unsigned char id_lo = (unsigned char)buf[fh_len + 1];
            unsigned char pubcomp[4] = { 0x70, 0x02, id_hi, id_lo };
            push_rx(s, pubcomp, sizeof(pubcomp));
        }
    }
    return len;
}

static int fuzz_poll_read(esp_transport_handle_t t, int timeout_ms)
{
    (void)timeout_ms;
    fuzz_state_t* s = (fuzz_state_t*)t->data;
    return (s->in_off < s->in_len) ? 1 : -1;
}

static int fuzz_close(esp_transport_handle_t t)
{
    fuzz_state_t* s = (fuzz_state_t*)t->data;
    s->connected = 0;
    return 0;
}

static int fuzz_destroy(esp_transport_handle_t t)
{
    if (t) {
        fuzz_state_t* s = (fuzz_state_t*)t->data;
        if (s) {
            free(s->rx);
            free(s);
        }
        free(t);
    }
    return 0;
}

// Factory to create a fuzz transport around provided input buffer
esp_transport_handle_t esp_transport_fuzz_init(const unsigned char* data, size_t size, int autopilot, int mode, int frag)
{
    esp_transport_handle_t t = (esp_transport_handle_t)calloc(1, sizeof(*t));
    if (!t) {
        return NULL;
    }
    fuzz_state_t* s = (fuzz_state_t*)calloc(1, sizeof(*s));
    if (!s) {
        free(t);
        return NULL;
    }
    s->in = data; s->in_len = size; s->in_off = 0; s->connected = 0;
    s->autopilot = autopilot;
    s->mode = (mode == 1 ? FUZZ_MODE_CONNECTED
                : mode == 2 ? FUZZ_MODE_SUBSCRIBE
                : mode == 3 ? FUZZ_MODE_QOS
                : mode == 4 ? FUZZ_MODE_MQTT5
                : mode == 5 ? FUZZ_MODE_DYNAMIC
                : FUZZ_MODE_HANDSHAKE);
    s->frag = frag;

    // Dynamic mode: first input byte selects the actual fuzz mode; the rest are packet bytes
    if (s->mode == FUZZ_MODE_DYNAMIC && s->in_len > 0) {
        unsigned char sel = s->in[0] & 0x0F;
        switch (sel) {
            case 0x00: s->mode = FUZZ_MODE_HANDSHAKE; break;
            case 0x01: s->mode = FUZZ_MODE_CONNECTED; break;
            case 0x02: s->mode = FUZZ_MODE_SUBSCRIBE; break;
            case 0x03: s->mode = FUZZ_MODE_QOS; break;
            case 0x04: s->mode = FUZZ_MODE_MQTT5; break;
            default:   s->mode = FUZZ_MODE_HANDSHAKE; break;
        }
        // Skip selector byte so reads deliver only packet data
        s->in_off = 1;
    }
    t->_connect = fuzz_connect;
    t->_read = fuzz_read;
    t->_write = fuzz_write;
    t->_poll_read = fuzz_poll_read;
    t->_close = fuzz_close;
    t->_destroy = fuzz_destroy;
    t->data = s;
    return t;
}
