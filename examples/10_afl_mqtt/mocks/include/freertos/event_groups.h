/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Minimal Event Groups using pthread condvars
#pragma once
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

typedef struct {
    pthread_mutex_t mtx;
    pthread_cond_t cv;
    uint32_t bits;
} *EventGroupHandle_t;

static inline EventGroupHandle_t xEventGroupCreate(void)
{
    EventGroupHandle_t g = (EventGroupHandle_t)malloc(sizeof(*g));
    if (!g) {
        return NULL;
    }
    pthread_mutex_init(&g->mtx, NULL);
    pthread_cond_init(&g->cv, NULL);
    g->bits = 0;
    return g;
}

static inline void vEventGroupDelete(EventGroupHandle_t g)
{
    if (!g) {
        return;
    }
    pthread_mutex_destroy(&g->mtx);
    pthread_cond_destroy(&g->cv);
    free(g);
}

static inline uint32_t xEventGroupGetBits(EventGroupHandle_t g)
{
    pthread_mutex_lock(&g->mtx);
    uint32_t b = g->bits;
    pthread_mutex_unlock(&g->mtx);
    return b;
}

static inline uint32_t xEventGroupSetBits(EventGroupHandle_t g, uint32_t bits)
{
    pthread_mutex_lock(&g->mtx);
    g->bits |= bits;
    pthread_cond_broadcast(&g->cv);
    uint32_t b = g->bits;
    pthread_mutex_unlock(&g->mtx);
    return b;
}

static inline uint32_t xEventGroupClearBits(EventGroupHandle_t g, uint32_t bits)
{
    pthread_mutex_lock(&g->mtx);
    g->bits &= ~bits;
    uint32_t b = g->bits;
    pthread_mutex_unlock(&g->mtx);
    return b;
}

static inline uint32_t xEventGroupWaitBits(EventGroupHandle_t g, uint32_t bits_to_wait_for, int clear_on_exit, int wait_for_all_bits, TickType_t ticks)
{
    (void)ticks;
    pthread_mutex_lock(&g->mtx);
    while (wait_for_all_bits ? ((g->bits & bits_to_wait_for) != bits_to_wait_for) : ((g->bits & bits_to_wait_for) == 0)) {
        pthread_cond_wait(&g->cv, &g->mtx);
    }
    uint32_t out = g->bits;
    if (clear_on_exit) {
        g->bits &= ~bits_to_wait_for;
    }
    pthread_mutex_unlock(&g->mtx);
    return out;
}
