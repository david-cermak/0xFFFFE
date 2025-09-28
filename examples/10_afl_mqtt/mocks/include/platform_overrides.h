/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Force-included overrides to avoid depending on IDF platform headers
#pragma once
#include <stdint.h>
#include "esp_err.h"
#include "esp_log.h"

// Define memory check macros
#ifndef ESP_MEM_CHECK
#define ESP_MEM_CHECK(TAG, a, action) if (!(a)) { \
        ESP_LOGE(TAG,"%s(%d): %s",  __FUNCTION__, __LINE__, "Memory exhausted"); \
        action; \
    }
#endif

#ifndef ESP_OK_CHECK
#define ESP_OK_CHECK(TAG, a, action) if ((a) != ESP_OK) { \
        ESP_LOGE(TAG,"%s(%d): %s", __FUNCTION__, __LINE__, "Failed"); \
        action; \
    }
#endif

// Prototypes expected by esp-mqtt
char *platform_create_id_string(void);
int platform_random(int max);
uint64_t platform_tick_get_ms(void);
