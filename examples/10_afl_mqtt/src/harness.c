/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include "mqtt_client.h"
#include "esp_transport.h"
#include "MockAFL.h"
#include <unistd.h>
#include "platform_esp32_idf.h"

// Factory from esp_transport_fuzz.c
esp_transport_handle_t esp_transport_fuzz_init(const unsigned char* data, size_t size, int autopilot, int mode, int frag);

static void event_handler(void* handler_args, void* base)
{
    (void)handler_args;
    (void)base;
}

static int g_autopilot = 0;      // 0=off,1=on
static int g_mode = 0;           // 0=handshake,1=connected,2=subscribe,3=qos,4=mqtt5,5=dynamic
static int g_frag = 0;           // 0=off, >0 = max bytes per read

static void parse_args(int argc, char** argv)
{
    for (int i = 1; i < argc; ++i) {
        const char* a = argv[i];
        if (strcmp(a, "--autopilot") == 0) {
            g_autopilot = 1;
        } else if (strncmp(a, "--mode=", 7) == 0) {
            const char* m = a + 7;
            if (strcmp(m, "connected") == 0) {
                g_mode = 1;
            } else if (strcmp(m, "subscribe") == 0) {
                g_mode = 2;
            } else if (strcmp(m, "qos") == 0) {
                g_mode = 3;
            } else if (strcmp(m, "mqtt5") == 0) {
                g_mode = 4;
            } else if (strcmp(m, "dynamic") == 0) {
                g_mode = 5;
            } else {
                g_mode = 0;
            }
        } else if (strncmp(a, "--frag=", 8) == 0) {
            g_frag = atoi(a + 8);
            if (g_frag < 0) {
                g_frag = 0;
            }
        }
    }
}

static void run_once(const unsigned char* data, size_t size)
{
    // Prepare custom transport wrapping the current input
    esp_transport_handle_t t = esp_transport_fuzz_init(data, size, g_autopilot, g_mode, g_frag);
    if (!t) {
        return;
    }

    esp_mqtt_client_config_t cfg = {0};
    // Use direct transport mode; do not set URI/scheme
    cfg.broker.address.transport = MQTT_TRANSPORT_UNKNOWN;
    cfg.network.transport = t; // Note: this relies on matching struct layout; we only need mqtt_client.c to store pointer
    cfg.network.timeout_ms = 0; // non-blocking in single-thread mode
    cfg.session.keepalive = 60; // large keepalive
    cfg.session.disable_keepalive = true; // disable keepalive to reduce timer traffic
    if (g_mode == 4) {
        cfg.session.protocol_ver = MQTT_PROTOCOL_V_5;
    }
    cfg.task.stack_size = 8192;

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&cfg);
    if (!client) {
        esp_transport_destroy(t);
        return;
    }
    esp_mqtt_client_register_event(client, MQTT_EVENT_ANY, (void*)event_handler, NULL);

    // Single-thread stepping loop: bounded iterations
    for (int i = 0; i < 2048; ++i) {
        (void)esp_mqtt_client_fuzz_step(client, 0);
    }

    // Destroy (client owns and destroys transport)
    esp_mqtt_client_destroy(client);
}

int main(int argc, char** argv)
{
    parse_args(argc, argv);
    __AFL_INIT();
    // unsigned char *buf = NULL;
    size_t len = 0;

    // // Standalone mode: read from stdin once if not under AFL
    // if (!isatty(0)) {
    //     buf = (unsigned char*)malloc(1<<16);
    //     if (!buf) return 0;
    //     len = fread(buf, 1, (1<<16), stdin);
    //     run_once(buf, len);
    //     free(buf);
    //     return 0;
    // }

    // Fallback loop (no AFL): run a single empty iteration
    uint8_t buf[1460];
    while (__AFL_LOOP(10000)) {
        memset(buf, 0, 1460);
        size_t len = read(0, buf, 1460);
        run_once(buf, len);
        // Without AFL, just feed empty input
        // run_once((const unsigned char*)"\x20\x02\x00\x00", 4); // minimal CONNACK
    }
    return 0;
}
