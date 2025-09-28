/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#pragma once
#include "esp_transport.h"
static inline esp_transport_handle_t esp_transport_ws_init(esp_transport_handle_t base)
{
    (void)base;
    return NULL;
}
static inline void esp_transport_ws_set_path(esp_transport_handle_t t, const char* path)
{
    (void)t;
    (void)path;
}
static inline void esp_transport_ws_set_subprotocol(esp_transport_handle_t t, const char* sub)
{
    (void)t;
    (void)sub;
}
