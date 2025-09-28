/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal FreeRTOS task API using pthreads
#pragma once
#include <pthread.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"

typedef pthread_t* TaskHandle_t;

typedef void (*TaskFunction_t)(void*);

static inline BaseType_t xTaskCreate(TaskFunction_t fn, const char* name, uint32_t stack, void* arg, UBaseType_t prio, TaskHandle_t* out)
{
    (void)name; (void)stack; (void)prio;
    pthread_t* t = (pthread_t*)malloc(sizeof(pthread_t));
    if (!t) {
        return pdFALSE;
    }
    if (pthread_create(t, NULL, (void * (*)(void *))fn, arg) != 0) {
        free(t);
        return pdFALSE;
    }
    if (out) {
        *out = t;
    } else {
        /* detach if no handle requested */ pthread_detach(*t);
    }
    return pdTRUE;
}

static inline BaseType_t xTaskCreatePinnedToCore(TaskFunction_t fn, const char* name, uint32_t stack, void* arg, UBaseType_t prio, TaskHandle_t* out, UBaseType_t core)
{
    (void)core;
    return xTaskCreate(fn, name, stack, arg, prio, out);
}

static inline TaskHandle_t xTaskGetCurrentTaskHandle(void)
{
    // Return an opaque handle; not used for equality checks except self-compare
    pthread_t self = pthread_self();
    TaskHandle_t h = (TaskHandle_t)malloc(sizeof(pthread_t));
    if (h) {
        *h = self;
    } return h;
}

static inline void vTaskDelete(TaskHandle_t h)
{
    if (h == NULL) {
        pthread_exit(NULL);
    } else {
        pthread_t t = *h;
        pthread_cancel(t);
        pthread_join(t, NULL);
        free(h);
    }
}

static inline void vTaskDelay(TickType_t ticks)
{
    (void)ticks;
}
