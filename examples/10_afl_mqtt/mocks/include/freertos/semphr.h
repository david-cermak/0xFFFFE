/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal semaphore (recursive mutex) using pthreads
#pragma once
#include <pthread.h>
#include "freertos/FreeRTOS.h"

typedef pthread_mutex_t* SemaphoreHandle_t;

static inline SemaphoreHandle_t xSemaphoreCreateRecursiveMutex(void)
{
    pthread_mutexattr_t attr; pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_t* m = (pthread_mutex_t*)malloc(sizeof(pthread_mutex_t));
    if (!m) {
        return NULL;
    }
    pthread_mutex_init(m, &attr);
    pthread_mutexattr_destroy(&attr);
    return m;
}

static inline BaseType_t xSemaphoreTakeRecursive(SemaphoreHandle_t m, TickType_t ticks)
{
    (void)ticks;
    return pthread_mutex_lock(m) == 0 ? pdTRUE : pdFALSE;
}

static inline BaseType_t xSemaphoreGiveRecursive(SemaphoreHandle_t m)
{
    return pthread_mutex_unlock(m) == 0 ? pdTRUE : pdFALSE;
}

static inline void vSemaphoreDelete(SemaphoreHandle_t m)
{
    if (m) {
        pthread_mutex_destroy(m);
        free(m);
    }
}
