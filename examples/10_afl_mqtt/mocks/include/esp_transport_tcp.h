/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#pragma once
#include "esp_transport.h"
static inline esp_transport_handle_t esp_transport_tcp_init(void)
{
    return NULL;
}
static inline void esp_transport_set_default_port(esp_transport_handle_t t, int port)
{
    (void)t;
    (void)port;
}
static inline void esp_transport_tcp_set_interface_name(esp_transport_handle_t t, void* if_name)
{
    (void)t;
    (void)if_name;
}
