/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_transport API and fuzz transport handle
#pragma once
#include <stdint.h>
#include <stddef.h>
#include "esp_err.h"

typedef struct esp_transport* esp_transport_handle_t;
typedef struct esp_transport_list* esp_transport_list_handle_t;

typedef int (*transport_connect_func)(esp_transport_handle_t t, const char* host, int port, int timeout_ms);
typedef int (*transport_read_func)(esp_transport_handle_t t, char* buf, int len, int timeout_ms);
typedef int (*transport_write_func)(esp_transport_handle_t t, const char* buf, int len, int timeout_ms);
typedef int (*transport_poll_read_func)(esp_transport_handle_t t, int timeout_ms);
typedef int (*transport_close_func)(esp_transport_handle_t t);
typedef int (*transport_destroy_func)(esp_transport_handle_t t);

struct esp_transport {
    transport_connect_func _connect;
    transport_read_func _read;
    transport_write_func _write;
    transport_poll_read_func _poll_read;
    transport_close_func _close;
    transport_destroy_func _destroy;
    int last_errno;
    void* data;
};

// Errors expected by mqtt_client.c
#define ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT  1
#define ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN 2

static inline int esp_transport_connect(esp_transport_handle_t t, const char* host, int port, int timeout_ms)
{
    return t->_connect ? t->_connect(t, host, port, timeout_ms) : -1;
}
static inline int esp_transport_read(esp_transport_handle_t t, char* buf, int len, int timeout_ms)
{
    return t->_read ? t->_read(t, buf, len, timeout_ms) : -1;
}
static inline int esp_transport_write(esp_transport_handle_t t, const char* buf, int len, int timeout_ms)
{
    return t->_write ? t->_write(t, buf, len, timeout_ms) : -1;
}
static inline int esp_transport_poll_read(esp_transport_handle_t t, int timeout_ms)
{
    return t->_poll_read ? t->_poll_read(t, timeout_ms) : -1;
}
static inline int esp_transport_close(esp_transport_handle_t t)
{
    return t->_close ? t->_close(t) : 0;
}
static inline int esp_transport_destroy(esp_transport_handle_t t)
{
    if (!t) {
        return 0;
    } int r = t->_destroy ? t->_destroy(t) : 0;
    return r;
}

static inline int esp_transport_get_errno(esp_transport_handle_t t)
{
    return t ? t->last_errno : 0;
}

static inline void* esp_transport_get_error_handle(esp_transport_handle_t t)
{
    (void)t;
    return NULL;
}

typedef struct {
    int keep_alive_enable;
    int keep_alive_idle;
    int keep_alive_interval;
    int keep_alive_count;
} esp_transport_keep_alive_t;

static inline void esp_transport_tcp_set_keep_alive(esp_transport_handle_t t, const esp_transport_keep_alive_t* cfg)
{
    (void)t;
    (void)cfg;
}
static inline int esp_transport_get_default_port(esp_transport_handle_t t)
{
    (void)t;
    return 0;
}

// Minimal list API stubs (unused in our direct-transport mode)
static inline esp_transport_list_handle_t esp_transport_list_init(void)
{
    return (esp_transport_list_handle_t)1;
}
static inline void esp_transport_list_destroy(esp_transport_list_handle_t l)
{
    (void)l;
}
static inline void esp_transport_list_add(esp_transport_list_handle_t l, esp_transport_handle_t t, const char* scheme)
{
    (void)l;
    (void)t;
    (void)scheme;
}
static inline esp_transport_handle_t esp_transport_list_get_transport(esp_transport_list_handle_t l, const char* scheme)
{
    (void)l;
    (void)scheme;
    return NULL;
}
