/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_tls.h mock
#pragma once
#include "esp_err.h"

struct esp_tls_last_error {
    int placeholder;
};

static inline esp_err_t esp_tls_get_and_clear_last_error(void* tls, int *esp_tls_last_esp_err, int *esp_tls_stack_err)
{
    (void)tls;
    if (esp_tls_last_esp_err) {
        *esp_tls_last_esp_err = ESP_OK;
    } if (esp_tls_stack_err) {
        *esp_tls_stack_err = 0;
    } return ESP_OK;
}

struct psk_key_hint {
    int dummy;
};
