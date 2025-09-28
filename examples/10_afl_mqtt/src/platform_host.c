/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Host implementation of platform_* and macros
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <string.h>
#include "esp_log.h"

// Provide the macros expected by esp-mqtt via platform_esp32_idf.h without including IDF
char *platform_create_id_string(void)
{
    char *id = (char*)calloc(1, 32);
    if (!id) {
        return NULL;
    }
    snprintf(id, 31, "host_mqtt_%08x", (unsigned)rand());
    return id;
}

int platform_random(int max)
{
    return (max > 0) ? (rand() % max) : 0;
}

uint64_t platform_tick_get_ms(void)
{
    static uint64_t ticks = 0;
    return ++ticks; // deterministic monotonic counter
}
