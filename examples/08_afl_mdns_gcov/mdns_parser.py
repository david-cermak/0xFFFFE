code_under_test="""
void mdns_parse_packet(mdns_rx_packet_t *packet)
{
    static mdns_name_t n;
    mdns_header_t header;
    const uint8_t *data = _mdns_get_packet_data(packet);
    size_t len = _mdns_get_packet_len(packet);
    const uint8_t *content = data + MDNS_HEAD_LEN;
    bool do_not_reply = false;
    mdns_search_once_t *search_result = NULL;
    mdns_browse_t *browse_result = NULL;
    char *browse_result_instance = NULL;
    char *browse_result_service = NULL;
    char *browse_result_proto = NULL;
    mdns_browse_sync_t *out_sync_browse = NULL;

    DBG_RX_PACKET(packet, data, len);

#ifndef CONFIG_MDNS_SKIP_SUPPRESSING_OWN_QUERIES
    // Check if the packet wasn't sent by us
#ifdef CONFIG_LWIP_IPV4
    if (packet->ip_protocol == MDNS_IP_PROTOCOL_V4) {
        esp_netif_ip_info_t if_ip_info;
        if (esp_netif_get_ip_info(_mdns_get_esp_netif(packet->tcpip_if), &if_ip_info) == ESP_OK &&
                memcmp(&if_ip_info.ip.addr, &packet->src.u_addr.ip4.addr, sizeof(esp_ip4_addr_t)) == 0) {
            return;
        }
    }
#endif /* CONFIG_LWIP_IPV4 */
#ifdef CONFIG_LWIP_IPV6
    if (packet->ip_protocol == MDNS_IP_PROTOCOL_V6) {
        struct esp_ip6_addr if_ip6;
        if (esp_netif_get_ip6_linklocal(_mdns_get_esp_netif(packet->tcpip_if), &if_ip6) == ESP_OK &&
                memcmp(&if_ip6, &packet->src.u_addr.ip6, sizeof(esp_ip6_addr_t)) == 0) {
            return;
        }
    }
#endif /* CONFIG_LWIP_IPV6 */
#endif // CONFIG_MDNS_SKIP_SUPPRESSING_OWN_QUERIES

    // Check for the minimum size of mdns packet
    if (len <=  MDNS_HEAD_ADDITIONAL_OFFSET) {
        return;
    }

    mdns_parsed_packet_t *parsed_packet = (mdns_parsed_packet_t *)mdns_mem_malloc(sizeof(mdns_parsed_packet_t));
    if (!parsed_packet) {
        HOOK_MALLOC_FAILED;
        return;
    }
    memset(parsed_packet, 0, sizeof(mdns_parsed_packet_t));

    mdns_name_t *name = &n;
    memset(name, 0, sizeof(mdns_name_t));

    header.id = mdns_utils_read_u16(data, MDNS_HEAD_ID_OFFSET);
    header.flags = mdns_utils_read_u16(data, MDNS_HEAD_FLAGS_OFFSET);
    header.questions = mdns_utils_read_u16(data, MDNS_HEAD_QUESTIONS_OFFSET);
    header.answers = mdns_utils_read_u16(data, MDNS_HEAD_ANSWERS_OFFSET);
    header.servers = mdns_utils_read_u16(data, MDNS_HEAD_SERVERS_OFFSET);
    header.additional = mdns_utils_read_u16(data, MDNS_HEAD_ADDITIONAL_OFFSET);

    if (header.flags == MDNS_FLAGS_QR_AUTHORITATIVE && packet->src_port != MDNS_SERVICE_PORT) {
        mdns_mem_free(parsed_packet);
        return;
    }

    //if we have not set the hostname, we can not answer questions
    if (header.questions && !header.answers && mdns_utils_str_null_or_empty(mdns_utils_get_global_hostname())) {
        mdns_mem_free(parsed_packet);
        return;
    }

    parsed_packet->tcpip_if = packet->tcpip_if;
    parsed_packet->ip_protocol = packet->ip_protocol;
    parsed_packet->multicast = packet->multicast;
    parsed_packet->authoritative = (header.flags == MDNS_FLAGS_QR_AUTHORITATIVE);
    parsed_packet->distributed = header.flags == MDNS_FLAGS_DISTRIBUTED;
    parsed_packet->id = header.id;
    esp_netif_ip_addr_copy(&parsed_packet->src, &packet->src);
    parsed_packet->src_port = packet->src_port;
    parsed_packet->records = NULL;

    if (header.questions) {
        uint8_t qs = header.questions;

        while (qs--) {
            content = _mdns_parse_fqdn(data, content, name, len);
            if (!content) {
                header.answers = 0;
                header.additional = 0;
                header.servers = 0;
                goto clear_rx_packet;//error
            }

            if (content + MDNS_CLASS_OFFSET + 1 >= data + len) {
                goto clear_rx_packet; // malformed packet, won't read behind it
            }
            uint16_t type = mdns_utils_read_u16(content, MDNS_TYPE_OFFSET);
            uint16_t mdns_class = mdns_utils_read_u16(content, MDNS_CLASS_OFFSET);
            bool unicast = !!(mdns_class & 0x8000);
            mdns_class &= 0x7FFF;
            content = content + 4;

            if (mdns_class != 0x0001 || name->invalid) {//bad class or invalid name for this question entry
                continue;
            }

            if (_mdns_name_is_discovery(name, type)) {
                //service discovery
                parsed_packet->discovery = true;
                mdns_srv_item_t *a = mdns_utils_get_services();
                while (a) {
                    mdns_parsed_question_t *question = (mdns_parsed_question_t *)mdns_mem_calloc(1, sizeof(mdns_parsed_question_t));
                    if (!question) {
                        HOOK_MALLOC_FAILED;
                        goto clear_rx_packet;
                    }
                    question->next = parsed_packet->questions;
                    parsed_packet->questions = question;

                    question->unicast = unicast;
                    question->type = MDNS_TYPE_SDPTR;
                    question->host = NULL;
                    question->service = mdns_mem_strdup(a->service->service);
                    question->proto = mdns_mem_strdup(a->service->proto);
                    question->domain = mdns_mem_strdup(MDNS_UTILS_DEFAULT_DOMAIN);
                    if (!question->service || !question->proto || !question->domain) {
                        goto clear_rx_packet;
                    }
                    a = a->next;
                }
                continue;
            }
            if (!_mdns_name_is_ours(name)) {
                continue;
            }

            if (type == MDNS_TYPE_ANY && !mdns_utils_str_null_or_empty(name->host)) {
                parsed_packet->probe = true;
            }

            mdns_parsed_question_t *question = (mdns_parsed_question_t *)mdns_mem_calloc(1, sizeof(mdns_parsed_question_t));
            if (!question) {
                HOOK_MALLOC_FAILED;
                goto clear_rx_packet;
            }
            question->next = parsed_packet->questions;
            parsed_packet->questions = question;

            question->unicast = unicast;
            question->type = type;
            question->sub = name->sub;
            if (_mdns_strdup_check(&(question->host), name->host)
                    || _mdns_strdup_check(&(question->service), name->service)
                    || _mdns_strdup_check(&(question->proto), name->proto)
                    || _mdns_strdup_check(&(question->domain), name->domain)) {
                goto clear_rx_packet;
            }
        }
    }

    if (header.questions && !parsed_packet->questions && !parsed_packet->discovery && !header.answers) {
        goto clear_rx_packet;
    } else if (header.answers || header.servers || header.additional) {
        uint16_t recordIndex = 0;

        while (content < (data + len)) {

            content = _mdns_parse_fqdn(data, content, name, len);
            if (!content) {
                goto clear_rx_packet;//error
            }

            if (content + MDNS_LEN_OFFSET + 1 >= data + len) {
                goto clear_rx_packet; // malformed packet, won't read behind it
            }
            uint16_t type = mdns_utils_read_u16(content, MDNS_TYPE_OFFSET);
            uint16_t mdns_class = mdns_utils_read_u16(content, MDNS_CLASS_OFFSET);
            uint32_t ttl = mdns_utils_read_u32(content, MDNS_TTL_OFFSET);
            uint16_t data_len = mdns_utils_read_u16(content, MDNS_LEN_OFFSET);
            const uint8_t *data_ptr = content + MDNS_DATA_OFFSET;
            mdns_class &= 0x7FFF;

            content = data_ptr + data_len;
            if (content > (data + len) || data_len == 0) {
                goto clear_rx_packet;
            }

            bool discovery = false;
            bool ours = false;
            mdns_srv_item_t *service = NULL;
            mdns_parsed_record_type_t record_type = MDNS_ANSWER;

            if (recordIndex >= (header.answers + header.servers)) {
                record_type = MDNS_EXTRA;
            } else if (recordIndex >= (header.answers)) {
                record_type = MDNS_NS;
            }
            recordIndex++;

            if (type == MDNS_TYPE_NSEC || type == MDNS_TYPE_OPT) {
                //skip NSEC and OPT
                continue;
            }

            if (parsed_packet->discovery && _mdns_name_is_discovery(name, type)) {
                discovery = true;
            } else if (!name->sub && _mdns_name_is_ours(name)) {
                ours = true;
                if (name->service[0] && name->proto[0]) {
                    service = _mdns_get_service_item(name->service, name->proto, NULL);
                }
            } else {
                if ((header.flags & MDNS_FLAGS_QUERY_REPSONSE) == 0 || record_type == MDNS_NS) {
                    //skip this record
                    continue;
                }
                search_result = mdns_priv_query_find(name, type, packet->tcpip_if, packet->ip_protocol);
                browse_result = _mdns_browse_find(name, type, packet->tcpip_if, packet->ip_protocol);
                if (browse_result) {
                    if (!out_sync_browse) {
                        // will be freed in function `_mdns_browse_sync`
                        out_sync_browse = (mdns_browse_sync_t *)mdns_mem_malloc(sizeof(mdns_browse_sync_t));
                        if (!out_sync_browse) {
                            HOOK_MALLOC_FAILED;
                            goto clear_rx_packet;
                        }
                        out_sync_browse->browse = browse_result;
                        out_sync_browse->sync_result = NULL;
                    }
                    if (!browse_result_service) {
                        browse_result_service = (char *)mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                        if (!browse_result_service) {
                            HOOK_MALLOC_FAILED;
                            goto clear_rx_packet;
                        }
                    }
                    memcpy(browse_result_service, browse_result->service, MDNS_NAME_BUF_LEN);
                    if (!browse_result_proto) {
                        browse_result_proto = (char *)mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                        if (!browse_result_proto) {
                            HOOK_MALLOC_FAILED;
                            goto clear_rx_packet;
                        }
                    }
                    memcpy(browse_result_proto, browse_result->proto, MDNS_NAME_BUF_LEN);
                    if (type == MDNS_TYPE_SRV || type == MDNS_TYPE_TXT) {
                        if (!browse_result_instance) {
                            browse_result_instance = (char *)mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                            if (!browse_result_instance) {
                                HOOK_MALLOC_FAILED;
                                goto clear_rx_packet;
                            }
                        }
                        memcpy(browse_result_instance, name->host, MDNS_NAME_BUF_LEN);
                    }
                }
            }

            if (type == MDNS_TYPE_PTR) {
                if (!_mdns_parse_fqdn(data, data_ptr, name, len)) {
                    continue;//error
                }
                if (search_result) {
                    mdns_priv_query_result_add_ptr(search_result, name->host, name->service, name->proto,
                                                   packet->tcpip_if, packet->ip_protocol, ttl);
                } else if ((discovery || ours) && !name->sub && _mdns_name_is_ours(name)) {
                    if (name->host[0]) {
                        service = _mdns_get_service_item_instance(name->host, name->service, name->proto, NULL);
                    } else {
                        service = _mdns_get_service_item(name->service, name->proto, NULL);
                    }
                    if (discovery && service) {
                        _mdns_remove_parsed_question(parsed_packet, MDNS_TYPE_SDPTR, service);
                    } else if (service && parsed_packet->questions && !parsed_packet->probe) {
                        _mdns_remove_parsed_question(parsed_packet, type, service);
                    } else if (service) {
                        //check if TTL is more than half of the full TTL value (4500)
                        if (ttl > (MDNS_ANSWER_PTR_TTL / 2)) {
                            _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, service);
                        }
                    }
                    if (service) {
                        mdns_parsed_record_t *record = mdns_mem_malloc(sizeof(mdns_parsed_record_t));
                        if (!record) {
                            HOOK_MALLOC_FAILED;
                            goto clear_rx_packet;
                        }
                        record->next = parsed_packet->records;
                        parsed_packet->records = record;
                        record->type = MDNS_TYPE_PTR;
                        record->record_type = MDNS_ANSWER;
                        record->ttl = ttl;
                        record->host = NULL;
                        record->service = NULL;
                        record->proto = NULL;
                        if (name->host[0]) {
                            record->host = mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                            if (!record->host) {
                                HOOK_MALLOC_FAILED;
                                goto clear_rx_packet;
                            }
                            memcpy(record->host, name->host, MDNS_NAME_BUF_LEN);
                        }
                        if (name->service[0]) {
                            record->service = mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                            if (!record->service) {
                                HOOK_MALLOC_FAILED;
                                goto clear_rx_packet;
                            }
                            memcpy(record->service, name->service, MDNS_NAME_BUF_LEN);
                        }
                        if (name->proto[0]) {
                            record->proto = mdns_mem_malloc(MDNS_NAME_BUF_LEN);
                            if (!record->proto) {
                                HOOK_MALLOC_FAILED;
                                goto clear_rx_packet;
                            }
                            memcpy(record->proto, name->proto, MDNS_NAME_BUF_LEN);
                        }
                    }
                }
            } else if (type == MDNS_TYPE_SRV) {
                mdns_result_t *result = NULL;
                if (search_result && search_result->type == MDNS_TYPE_PTR) {
                    result = search_result->result;
                    while (result) {
                        if (_mdns_get_esp_netif(packet->tcpip_if) == result->esp_netif
                                && packet->ip_protocol == result->ip_protocol
                                && result->instance_name && !strcmp(name->host, result->instance_name)) {
                            break;
                        }
                        result = result->next;
                    }
                    if (!result) {
                        result = mdns_priv_query_result_add_ptr(search_result, name->host, name->service, name->proto,
                                                                packet->tcpip_if, packet->ip_protocol, ttl);
                        if (!result) {
                            continue;//error
                        }
                    }
                }
                bool is_selfhosted = _mdns_name_is_selfhosted(name);
                if (!_mdns_parse_fqdn(data, data_ptr + MDNS_SRV_FQDN_OFFSET, name, len)) {
                    continue;//error
                }
                if (data_ptr + MDNS_SRV_PORT_OFFSET + 1 >= data + len) {
                    goto clear_rx_packet; // malformed packet, won't read behind it
                }
                uint16_t priority = mdns_utils_read_u16(data_ptr, MDNS_SRV_PRIORITY_OFFSET);
                uint16_t weight = mdns_utils_read_u16(data_ptr, MDNS_SRV_WEIGHT_OFFSET);
                uint16_t port = mdns_utils_read_u16(data_ptr, MDNS_SRV_PORT_OFFSET);

                if (browse_result) {
                    mdns_browse_result_add_srv(browse_result, name->host, browse_result_instance, browse_result_service,
                                               browse_result_proto, port, packet->tcpip_if, packet->ip_protocol, ttl,
                                               out_sync_browse);
                }
                if (search_result) {
                    if (search_result->type == MDNS_TYPE_PTR) {
                        if (!result->hostname) { // assign host/port for this entry only if not previously set
                            result->port = port;
                            result->hostname = mdns_mem_strdup(name->host);
                        }
                    } else {
                        mdns_priv_query_result_add_srv(search_result, name->host, port, packet->tcpip_if,
                                                       packet->ip_protocol, ttl);
                    }
                } else if (ours) {
                    if (parsed_packet->questions && !parsed_packet->probe) {
                        _mdns_remove_parsed_question(parsed_packet, type, service);
                        continue;
                    } else if (parsed_packet->distributed) {
                        _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, service);
                        continue;
                    }
                    if (!is_selfhosted) {
                        continue;
                    }
                    //detect collision (-1=won, 0=none, 1=lost)
                    int col = 0;
                    if (mdns_class > 1) {
                        col = 1;
                    } else if (!mdns_class) {
                        col = -1;
                    } else if (service) { // only detect srv collision if service existed
                        col = _mdns_check_srv_collision(service->service, priority, weight, port, name->host, name->domain);
                    }
                    if (service && col && (parsed_packet->probe || parsed_packet->authoritative)) {
                        if (col > 0 || !port) {
                            do_not_reply = true;
                            if (mdns_priv_pcb_is_probing(packet)) {
                                mdns_priv_pcb_set_probe_failed(packet);
                                if (!mdns_utils_str_null_or_empty(service->service->instance)) {
                                    char *new_instance = _mdns_mangle_name((char *)service->service->instance);
                                    if (new_instance) {
                                        mdns_mem_free((char *)service->service->instance);
                                        service->service->instance = new_instance;
                                    }
                                    _mdns_probe_all_pcbs(&service, 1, false, false);
                                } else if (!mdns_utils_str_null_or_empty(mdns_utils_get_instance())) {
                                    char *new_instance = _mdns_mangle_name((char *)mdns_utils_get_instance());
                                    if (new_instance) {
                                        mdns_utils_set_instance(new_instance);
                                    }
                                    _mdns_restart_all_pcbs_no_instance();
                                } else {
                                    char *new_host = _mdns_mangle_name((char *)mdns_utils_get_global_hostname());
                                    if (new_host) {
                                        _mdns_remap_self_service_hostname(mdns_utils_get_global_hostname(), new_host);
                                        mdns_utils_set_global_hostname(new_host);
                                    }
                                    _mdns_restart_all_pcbs();
                                }
                            } else if (service) {
                                _mdns_pcb_send_bye(packet->tcpip_if, packet->ip_protocol, &service, 1, false);
                                _mdns_init_pcb_probe(packet->tcpip_if, packet->ip_protocol, &service, 1, false);
                            }
                        }
                    } else if (ttl > 60 && !col && !parsed_packet->authoritative && !parsed_packet->probe && !parsed_packet->questions) {
                        _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, service);
                    }
                }
            } else if (type == MDNS_TYPE_TXT) {
                mdns_txt_item_t *txt = NULL;
                uint8_t *txt_value_len = NULL;
                size_t txt_count = 0;

                mdns_result_t *result = NULL;
                if (browse_result) {
                    _mdns_result_txt_create(data_ptr, data_len, &txt, &txt_value_len, &txt_count);
                    mdns_browse_result_add_txt(browse_result, browse_result_instance, browse_result_service,
                                               browse_result_proto,
                                               txt, txt_value_len, txt_count, packet->tcpip_if, packet->ip_protocol,
                                               ttl, out_sync_browse);
                }
                if (search_result) {
                    if (search_result->type == MDNS_TYPE_PTR) {
                        result = search_result->result;
                        while (result) {
                            if (_mdns_get_esp_netif(packet->tcpip_if) == result->esp_netif
                                    && packet->ip_protocol == result->ip_protocol
                                    && result->instance_name && !strcmp(name->host, result->instance_name)) {
                                break;
                            }
                            result = result->next;
                        }
                        if (!result) {
                            result = mdns_priv_query_result_add_ptr(search_result, name->host, name->service,
                                                                    name->proto,
                                                                    packet->tcpip_if, packet->ip_protocol, ttl);
                            if (!result) {
                                continue;//error
                            }
                        }
                        if (!result->txt) {
                            _mdns_result_txt_create(data_ptr, data_len, &txt, &txt_value_len, &txt_count);
                            if (txt_count) {
                                result->txt = txt;
                                result->txt_count = txt_count;
                                result->txt_value_len = txt_value_len;
                            }
                        }
                    } else {
                        _mdns_result_txt_create(data_ptr, data_len, &txt, &txt_value_len, &txt_count);
                        if (txt_count) {
                            mdns_priv_query_result_add_txt(search_result, txt, txt_value_len, txt_count,
                                                           packet->tcpip_if, packet->ip_protocol, ttl);
                        }
                    }
                } else if (ours) {
                    if (parsed_packet->questions && !parsed_packet->probe && service) {
                        _mdns_remove_parsed_question(parsed_packet, type, service);
                        continue;
                    }
                    if (!_mdns_name_is_selfhosted(name)) {
                        continue;
                    }
                    //detect collision (-1=won, 0=none, 1=lost)
                    int col = 0;
                    if (mdns_class > 1) {
                        col = 1;
                    } else if (!mdns_class) {
                        col = -1;
                    } else if (service) { // only detect txt collision if service existed
                        col = _mdns_check_txt_collision(service->service, data_ptr, data_len);
                    }
                    if (col && !mdns_priv_pcb_is_probing(packet) && service) {
                        do_not_reply = true;
                        _mdns_init_pcb_probe(packet->tcpip_if, packet->ip_protocol, &service, 1, true);
                    } else if (ttl > (MDNS_ANSWER_TXT_TTL / 2) && !col && !parsed_packet->authoritative && !parsed_packet->probe && !parsed_packet->questions && !mdns_priv_pcb_is_probing(
                                   packet)) {
                        _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, service);
                    }
                }

            }
#ifdef CONFIG_LWIP_IPV6
            else if (type == MDNS_TYPE_AAAA) {//ipv6
                esp_ip_addr_t ip6;
                ip6.type = ESP_IPADDR_TYPE_V6;
                memcpy(ip6.u_addr.ip6.addr, data_ptr, MDNS_ANSWER_AAAA_SIZE);
                if (browse_result) {
                    mdns_browse_result_add_ip(browse_result, name->host, &ip6, packet->tcpip_if, packet->ip_protocol,
                                              ttl, out_sync_browse);
                }
                if (search_result) {
                    //check for more applicable searches (PTR & A/AAAA at the same time)
                    while (search_result) {
                        mdns_priv_query_result_add_ip(search_result, name->host, &ip6, packet->tcpip_if,
                                                      packet->ip_protocol, ttl);
                        search_result = mdns_priv_query_find_from(search_result->next, name, type, packet->tcpip_if,
                                                                  packet->ip_protocol);
                    }
                } else if (ours) {
                    if (parsed_packet->questions && !parsed_packet->probe) {
                        _mdns_remove_parsed_question(parsed_packet, type, NULL);
                        continue;
                    }
                    if (!_mdns_name_is_selfhosted(name)) {
                        continue;
                    }
                    //detect collision (-1=won, 0=none, 1=lost)
                    int col = 0;
                    if (mdns_class > 1) {
                        col = 1;
                    } else if (!mdns_class) {
                        col = -1;
                    } else {
                        col = _mdns_check_aaaa_collision(&(ip6.u_addr.ip6), packet->tcpip_if);
                    }
                    if (col == 2) {
                        goto clear_rx_packet;
                    } else if (col == 1) {
                        do_not_reply = true;
                        if (mdns_priv_pcb_is_probing(packet)) {
                            if (col && (parsed_packet->probe || parsed_packet->authoritative)) {
                                mdns_priv_pcb_set_probe_failed(packet);
                                char *new_host = _mdns_mangle_name((char *)mdns_utils_get_global_hostname());
                                if (new_host) {
                                    _mdns_remap_self_service_hostname(mdns_utils_get_global_hostname(), new_host);
                                    mdns_utils_set_global_hostname(new_host);
                                }
                                _mdns_restart_all_pcbs();
                            }
                        } else {
                            _mdns_init_pcb_probe(packet->tcpip_if, packet->ip_protocol, NULL, 0, true);
                        }
                    } else if (ttl > 60 && !col && !parsed_packet->authoritative && !parsed_packet->probe && !parsed_packet->questions && !mdns_priv_pcb_is_probing(
                                   packet)) {
                        _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, NULL);
                    }
                }

            }
#endif /* CONFIG_LWIP_IPV6 */
#ifdef CONFIG_LWIP_IPV4
            else if (type == MDNS_TYPE_A) {
                esp_ip_addr_t ip;
                ip.type = ESP_IPADDR_TYPE_V4;
                memcpy(&(ip.u_addr.ip4.addr), data_ptr, 4);
                if (browse_result) {
                    mdns_browse_result_add_ip(browse_result, name->host, &ip, packet->tcpip_if, packet->ip_protocol,
                                              ttl, out_sync_browse);
                }
                if (search_result) {
                    //check for more applicable searches (PTR & A/AAAA at the same time)
                    while (search_result) {
                        mdns_priv_query_result_add_ip(search_result, name->host, &ip, packet->tcpip_if,
                                                      packet->ip_protocol, ttl);
                        search_result = mdns_priv_query_find_from(search_result->next, name, type, packet->tcpip_if,
                                                                  packet->ip_protocol);
                    }
                } else if (ours) {
                    if (parsed_packet->questions && !parsed_packet->probe) {
                        _mdns_remove_parsed_question(parsed_packet, type, NULL);
                        continue;
                    }
                    if (!_mdns_name_is_selfhosted(name)) {
                        continue;
                    }
                    //detect collision (-1=won, 0=none, 1=lost)
                    int col = 0;
                    if (mdns_class > 1) {
                        col = 1;
                    } else if (!mdns_class) {
                        col = -1;
                    } else {
                        col = _mdns_check_a_collision(&(ip.u_addr.ip4), packet->tcpip_if);
                    }
                    if (col == 2) {
                        goto clear_rx_packet;
                    } else if (col == 1) {
                        do_not_reply = true;
                        if (mdns_priv_pcb_is_probing(packet)) {
                            if (col && (parsed_packet->probe || parsed_packet->authoritative)) {
                                mdns_priv_pcb_set_probe_failed(packet);
                                char *new_host = _mdns_mangle_name((char *)mdns_utils_get_global_hostname());
                                if (new_host) {
                                    _mdns_remap_self_service_hostname(mdns_utils_get_global_hostname(), new_host);
                                    mdns_utils_set_global_hostname(new_host);
                                }
                                _mdns_restart_all_pcbs();
                            }
                        } else {
                            _mdns_init_pcb_probe(packet->tcpip_if, packet->ip_protocol, NULL, 0, true);
                        }
                    } else if (ttl > 60 && !col && !parsed_packet->authoritative && !parsed_packet->probe && !parsed_packet->questions && !mdns_priv_pcb_is_probing(
                                   packet)) {
                        _mdns_remove_scheduled_answer(packet->tcpip_if, packet->ip_protocol, type, NULL);
                    }
                }

            }
#endif /* CONFIG_LWIP_IPV4 */
        }
        //end while
        if (parsed_packet->authoritative) {
            mdns_priv_query_done();
        }
    }

    if (!do_not_reply && mdns_priv_pcb_is_after_probing(packet) && (parsed_packet->questions || parsed_packet->discovery)) {
        _mdns_create_answer_from_parsed_packet(parsed_packet);
    }
    if (out_sync_browse) {
        DBG_BROWSE_RESULTS_WITH_MSG(out_sync_browse->browse->result,
                                    "Browse %s%s total result:", out_sync_browse->browse->service, out_sync_browse->browse->proto);
        if (out_sync_browse->sync_result) {
            DBG_BROWSE_RESULTS_WITH_MSG(out_sync_browse->sync_result->result,
                                        "Changed result:");
            _mdns_sync_browse_action(ACTION_BROWSE_SYNC, out_sync_browse);
        } else {
            mdns_mem_free(out_sync_browse);
        }
        out_sync_browse = NULL;
    }

clear_rx_packet:
    while (parsed_packet->questions) {
        mdns_parsed_question_t *question = parsed_packet->questions;
        parsed_packet->questions = parsed_packet->questions->next;
        if (question->host) {
            mdns_mem_free(question->host);
        }
        if (question->service) {
            mdns_mem_free(question->service);
        }
        if (question->proto) {
            mdns_mem_free(question->proto);
        }
        if (question->domain) {
            mdns_mem_free(question->domain);
        }
        mdns_mem_free(question);
    }
    while (parsed_packet->records) {
        mdns_parsed_record_t *record = parsed_packet->records;
        parsed_packet->records = parsed_packet->records->next;
        if (record->host) {
            mdns_mem_free(record->host);
        }
        if (record->service) {
            mdns_mem_free(record->service);
        }
        if (record->proto) {
            mdns_mem_free(record->proto);
        }
        record->next = NULL;
        mdns_mem_free(record);
    }
    mdns_mem_free(parsed_packet);
    mdns_mem_free(browse_result_instance);
    mdns_mem_free(browse_result_service);
    mdns_mem_free(browse_result_proto);
    mdns_mem_free(out_sync_browse);
}
"""

dns_generate = """
from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, A, PTR, TXT
import struct

def create_mdns_packet(queries, answers, additional, output_file="mdns_packet.bin"):
    dns_header = DNSHeader(id=0, qr=1, aa=1, ra=0)
    dns_record = DNSRecord(dns_header)
    for qname, qtype in queries:
        dns_record.add_question(DNSQuestion(qname, qtype))
    for name, qtype, value, ttl in answers:
        if qtype == "A":
            rr = RR(name, rdata=A(value), ttl=ttl)
        elif qtype == "PTR":
            rr = RR(name, rdata=PTR(value), ttl=ttl)
        elif qtype == "TXT":
            rr = RR(name, rdata=TXT(value), ttl=ttl)
        else:
            print(f"Unsupported type: {qtype}")
            continue
        dns_record.add_answer(rr)
    for name, qtype, value, ttl in additional:
        if qtype == "A":
            rr = RR(name, rdata=A(value), ttl=ttl)
        elif qtype == "TXT":
            rr = RR(name, rdata=TXT(value), ttl=ttl)
        else:
            print(f"Unsupported type: {qtype}")
            continue
        dns_record.add_ar(rr)
    mdns_payload = dns_record.pack()

    with open(output_file, "wb") as f:
        f.write(mdns_payload)

    print(f"mDNS packet saved as {output_file}")

queries = [
    ("_http._tcp.local.", 12),  # PTR query for service discovery
]
answers = [
    ("_http._tcp.local.", "PTR", "MyDevice._http._tcp.local.", 120),
    ("MyDevice._http._tcp.local.", "A", "192.168.1.42", 120),
]
additional = [
    ("MyDevice._http._tcp.local.", "TXT", "info=Sample mDNS TXT Record", 120),
]


create_mdns_packet(queries, answers, additional, "case1.bin")
# Add more test cases here
"""

test_code = """"" \
//
// Test starts here
//
int main(int argc, char **argv)
{
    int i;
    const char *mdns_hostname = "minifritz";
    const char *mdns_instance = "Hristo's Time Capsule";
    mdns_txt_item_t arduTxtData[4] = {
        {"board", "esp32"},
        {"tcp_check", "no"},
        {"ssh_upload", "no"},
        {"auth_upload", "no"}
    };

    const uint8_t mac[6] = {0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x32};

    uint8_t buf[1460];
    char winstance[21 + strlen(mdns_hostname)];

    sprintf(winstance, "%s [%02x:%02x:%02x:%02x:%02x:%02x]", mdns_hostname, mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    // Init depencency injected methods
    mdns_test_init_di();
    mdns_querier_test_init_di();

    if (mdns_init()) {
        abort();
    }

    if (mdns_test_hostname_set(mdns_hostname)) {
        abort();
    }

    if (mdns_test_add_delegated_host(mdns_hostname) || mdns_test_add_delegated_host("megafritz")) {
        abort();
    }

#ifndef MDNS_NO_SERVICES

    if (mdns_test_sub_service_add("_server", "_fritz", "_tcp", 22)) {
        abort();
    }

    if (mdns_test_service_add("_telnet", "_tcp", 22)) {
        abort();
    }

    if (mdns_test_service_add("_workstation", "_tcp", 9)) {
        abort();
    }
    if (mdns_test_service_instance_name_set("_workstation", "_tcp", winstance)) {
        abort();
    }

    if (mdns_test_service_add("_arduino", "_tcp", 3232)) {
        abort();
    }

    if (mdns_test_service_txt_set("_arduino", "_tcp", 4, arduTxtData)) {
        abort();
    }

    if (mdns_test_service_add("_http", "_tcp", 80)) {
        abort();
    }

    if (mdns_test_service_instance_name_set("_http", "_tcp", "ESP WebServer")) {
        abort();
    }

    if (
        mdns_test_service_add("_afpovertcp", "_tcp", 548)
        || mdns_test_service_add("_rfb", "_tcp", 885)
        || mdns_test_service_add("_smb", "_tcp", 885)
        || mdns_test_service_add("_adisk", "_tcp", 885)
        || mdns_test_service_add("_airport", "_tcp", 885)
        || mdns_test_service_add("_printer", "_tcp", 885)
        || mdns_test_service_add("_airplay", "_tcp", 885)
        || mdns_test_service_add("_raop", "_tcp", 885)
        || mdns_test_service_add("_uscan", "_tcp", 885)
        || mdns_test_service_add("_uscans", "_tcp", 885)
        || mdns_test_service_add("_ippusb", "_tcp", 885)
        || mdns_test_service_add("_scanner", "_tcp", 885)
        || mdns_test_service_add("_ipp", "_tcp", 885)
        || mdns_test_service_add("_ipps", "_tcp", 885)
        || mdns_test_service_add("_pdl-datastream", "_tcp", 885)
        || mdns_test_service_add("_ptp", "_tcp", 885)
        || mdns_test_service_add("_sleep-proxy", "_udp", 885)) {
        abort();
    }
#endif
    mdns_result_t *results = NULL;
    FILE *file;
    size_t nread;

#ifdef INSTR_IS_OFF
    size_t len = 1460;
    memset(buf, 0, 1460);

    if (argc != 2) {
        printf("Non-instrumentation mode: please supply a file name created by AFL to reproduce crash\n");
        return 1;
    } else {
        //
        // Note: parameter1 is a file (mangled packet) which caused the crash
        file = fopen(argv[1], "r");
        assert(file >= 0);
        len = fread(buf, 1, 1460, file);
        fclose(file);
    }

    for (i = 0; i < 1; i++) {
#else
    while (__AFL_LOOP(1000)) {
        memset(buf, 0, 1460);
        size_t len = read(0, buf, 1460);
#endif
        mypbuf.payload = malloc(len);
        memcpy(mypbuf.payload, buf, len);
        mypbuf.len = len;
        g_packet.pb = &mypbuf;
        mdns_test_query("minifritz", "_fritz", "_tcp", MDNS_TYPE_ANY);
        mdns_test_query(NULL, "_fritz", "_tcp", MDNS_TYPE_PTR);
        mdns_test_query(NULL, "_afpovertcp", "_tcp", MDNS_TYPE_PTR);
        mdns_parse_packet(&g_packet);
        free(mypbuf.payload);
    }
#ifndef MDNS_NO_SERVICES
    mdns_service_remove_all();
#endif
    ForceTaskDelete();
    mdns_free();
    return 0;
}
"""
