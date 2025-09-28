/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_log.h mock
#pragma once
#include <stdio.h>
#include <inttypes.h>

#ifndef LOG_LOCAL_LEVEL
#define LOG_LOCAL_LEVEL 0
#endif

#define ESP_LOGE(tag, fmt, ...) do { fprintf(stderr, "[E] %s: " fmt "\n", tag, ##__VA_ARGS__); } while(0)
#define ESP_LOGW(tag, fmt, ...) do { fprintf(stderr, "[W] %s: " fmt "\n", tag, ##__VA_ARGS__); } while(0)
#define ESP_LOGI(tag, fmt, ...) do { (void)tag; (void)fmt; } while(0)
#define ESP_LOGD(tag, fmt, ...) do { (void)tag; (void)fmt; } while(0)
#define ESP_LOGV(tag, fmt, ...) do { (void)tag; (void)fmt; } while(0)
