/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
// Optional AFL-compatible macros if building without AFL headers
#pragma once
#ifndef __AFL_LOOP
static inline int __afl_loop_stub(int x) {
    (void)x;
    static int _done = 0;
    if (_done) return 0;
    _done = 1;
    return 1;
}
#define __AFL_LOOP(x) __afl_loop_stub((x))
#endif
#ifndef __AFL_INIT
#define __AFL_INIT() do {} while(0)
#endif
