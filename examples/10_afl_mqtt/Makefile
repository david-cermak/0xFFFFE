CC ?= clang
CFLAGS ?= -O2 -g -fno-omit-frame-pointer -Wall -Wextra -Wno-unused-parameter

# Allow building with AFL++ by overriding CC=afl-clang-fast or afl-clang-lto

ifndef IDF_PATH
$(error IDF_PATH is not set. Please export IDF_PATH=/path/to/esp-idf)
endif

IDF_ROOT := $(abspath $(IDF_PATH))

DUT_DIR ?= DUT
MQTT_DIR := $(DUT_DIR)/esp-mqtt
MQTT_ZIP_URL := https://github.com/david-cermak/esp-mqtt/archive/refs/heads/test/fuzz.zip

MOCK_INC := mocks/include
HOST_TEST_MOCKS := $(MQTT_DIR)/host_test/mocks/include

INCLUDES := \
  -I$(MOCK_INC) \
  -I$(HOST_TEST_MOCKS) \
  -I$(MQTT_DIR)/include \
  -I$(MQTT_DIR)/lib/include \
  -I$(IDF_ROOT)/components/http_parser

SRCS := \
  $(MQTT_DIR)/mqtt_client.c \
  $(MQTT_DIR)/mqtt5_client.c \
  $(MQTT_DIR)/lib/mqtt_msg.c \
  $(MQTT_DIR)/lib/mqtt5_msg.c \
  $(MQTT_DIR)/lib/mqtt_outbox.c \
  $(IDF_ROOT)/components/http_parser/http_parser.c \
  src/platform_host.c \
  src/esp_transport_fuzz.c \
  src/harness.c

# Minimal feature toggles for a small host build
DEFS := \
  -DMQTT_PROTOCOL_311 \
  -DCONFIG_MQTT_PROTOCOL_5=1 \
  -DMQTT_TASK_CORE=0 \
  -DMQTT_TASK_STACK=8192 \
  -DMQTT_TASK_PRIORITY=5 \
  -DMQTT_POLL_READ_TIMEOUT_MS=5 \
  -DMQTT_ENABLE_SSL=0 \
  -DMQTT_SUPPORTED_FEATURE_EVENT_LOOP \
  -DIDF_VER=\"host\" \
  -DMQTT_SINGLE_THREAD \
  -DMQTT_DISABLE_API_LOCKS=1

LDFLAGS ?=
LDLIBS ?= -lpthread

OUT := mqtt_client_fuzz

.DEFAULT_GOAL := all

.PHONY: all clean deps

.DELETE_ON_ERROR:

deps: $(MQTT_DIR)/.stamp

all: deps $(OUT)

$(MQTT_DIR)/.stamp:
	@set -e; \
	if [ ! -d "$(MQTT_DIR)" ]; then \
		echo "Fetching esp-mqtt fuzz library into $(MQTT_DIR) ..."; \
		mkdir -p "$(DUT_DIR)"; \
		tmp="$$(mktemp)"; \
		curl -L --fail -o "$$tmp" "$(MQTT_ZIP_URL)"; \
		rm -rf "$(DUT_DIR)/esp-mqtt-test-fuzz" "$(MQTT_DIR)"; \
		unzip -q "$$tmp" -d "$(DUT_DIR)"; \
		rm -f "$$tmp"; \
		mv "$(DUT_DIR)/esp-mqtt-test-fuzz" "$(MQTT_DIR)"; \
	fi; \
	touch "$@"

OVERRIDES := $(MOCK_INC)/platform_overrides.h $(MOCK_INC)/net/if.h

$(OUT): $(SRCS) $(OVERRIDES)
	$(CC) $(CFLAGS) $(INCLUDES) $(DEFS) -include $(MOCK_INC)/platform_overrides.h -include $(MOCK_INC)/net/if.h $(SRCS) -o $@ $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(OUT)
