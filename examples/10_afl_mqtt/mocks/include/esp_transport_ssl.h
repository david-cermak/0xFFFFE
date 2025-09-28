/*
 * SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#pragma once
#include "esp_transport.h"
static inline esp_transport_handle_t esp_transport_ssl_init(void)
{
    return NULL;
}
static inline void esp_transport_ssl_enable_global_ca_store(esp_transport_handle_t t)
{
    (void)t;
}
static inline void esp_transport_ssl_crt_bundle_attach(esp_transport_handle_t t, esp_err_t (*fn)(void *conf))
{
    (void)t;
    (void)fn;
}
static inline void esp_transport_ssl_set_cert_data_der(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_client_cert_data_der(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_client_key_data_der(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_cert_data(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_client_cert_data(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_client_key_data(esp_transport_handle_t t, const char* d, int l)
{
    (void)t;
    (void)d;
    (void)l;
}
static inline void esp_transport_ssl_set_psk_key_hint(esp_transport_handle_t t, const void* p)
{
    (void)t;
    (void)p;
}
static inline void esp_transport_ssl_set_alpn_protocol(esp_transport_handle_t t, const char** protos)
{
    (void)t;
    (void)protos;
}
static inline void esp_transport_ssl_skip_common_name_check(esp_transport_handle_t t)
{
    (void)t;
}
static inline void esp_transport_ssl_set_common_name(esp_transport_handle_t t, const char* n)
{
    (void)t;
    (void)n;
}
static inline void esp_transport_ssl_use_secure_element(esp_transport_handle_t t)
{
    (void)t;
}
static inline void esp_transport_ssl_set_ds_data(esp_transport_handle_t t, void* ds)
{
    (void)t;
    (void)ds;
}
static inline void esp_transport_ssl_set_client_key_ecdsa_peripheral(esp_transport_handle_t t, uint8_t blk)
{
    (void)t;
    (void)blk;
}
static inline void esp_transport_ssl_set_client_key_password(esp_transport_handle_t t, const char* p, int len)
{
    (void)t;
    (void)p;
    (void)len;
}
