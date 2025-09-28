/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_heap_caps.h mock
#pragma once
#include <stdlib.h>

// Use standard malloc/free
#define heap_caps_malloc(size, caps) malloc(size)
#define heap_caps_calloc(nmemb, size, caps) calloc(nmemb, size)
