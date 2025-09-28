/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal esp_event.h mock
#pragma once
#include "esp_err.h"
#include <stdint.h>
#include <stddef.h>

typedef void* esp_event_loop_handle_t;
typedef void (*esp_event_handler_t)(void*, void*);
typedef const char* esp_event_base_t;

typedef struct {
    size_t queue_size;
    const char *task_name;
    uint32_t task_prio;
    uint32_t task_stack_size;
    void *task_core_id;
} esp_event_loop_args_t;

#define ESP_EVENT_DECLARE_BASE(x) extern esp_event_base_t x
#define ESP_EVENT_DEFINE_BASE(x) esp_event_base_t x = #x

static inline esp_err_t esp_event_loop_create(const esp_event_loop_args_t* args, esp_event_loop_handle_t* out)
{
    (void)args;
    if (out) {
        *out = (void*)0x1;
    } return ESP_OK;
}
static inline esp_err_t esp_event_loop_delete(esp_event_loop_handle_t h)
{
    (void)h;
    return ESP_OK;
}
static inline esp_err_t esp_event_post_to(esp_event_loop_handle_t loop, esp_event_base_t event_base, int32_t event_id, const void* event_data, size_t event_data_size, uint32_t ticks)
{
    (void)loop;
    (void)event_base;
    (void)event_id;
    (void)event_data;
    (void)event_data_size;
    (void)ticks;
    return ESP_OK;
}
static inline esp_err_t esp_event_loop_run(esp_event_loop_handle_t loop, int32_t timeout_ticks)
{
    (void)loop;
    (void)timeout_ticks;
    return ESP_OK;
}
static inline esp_err_t esp_event_handler_register_with(esp_event_loop_handle_t loop, esp_event_base_t event_base, int32_t event_id, esp_event_handler_t handler, void* arg)
{
    (void)loop;
    (void)event_base;
    (void)event_id;
    (void)handler;
    (void)arg;
    return ESP_OK;
}
static inline esp_err_t esp_event_handler_unregister_with(esp_event_loop_handle_t loop, esp_event_base_t event_base, int32_t event_id, esp_event_handler_t handler)
{
    (void)loop;
    (void)event_base;
    (void)event_id;
    (void)handler;
    return ESP_OK;
}
