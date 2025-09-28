/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_err.h mock for host fuzzing
#pragma once
#include <stdint.h>

typedef int32_t esp_err_t;

#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_NOT_SUPPORTED 0x105
#define ESP_ERR_TIMEOUT 0x107
