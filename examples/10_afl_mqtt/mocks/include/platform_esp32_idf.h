/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal platform header to satisfy esp-mqtt expectations on host
#pragma once
#include <stdint.h>
#include <stdlib.h>
#include "esp_log.h"
#include <net/if.h>

char *platform_create_id_string(void);
int platform_random(int max);
uint64_t platform_tick_get_ms(void);

#define ESP_MEM_CHECK(TAG, a, action) if (!(a)) { \
        ESP_LOGE(TAG,"%s(%d): %s",  __FUNCTION__, __LINE__, "Memory exhausted"); \
        action; \
    }

#define ESP_OK_CHECK(TAG, a, action) if ((a) != ESP_OK) { \
        ESP_LOGE(TAG,"%s(%d): %s", __FUNCTION__, __LINE__, "Failed"); \
        action; \
    }
