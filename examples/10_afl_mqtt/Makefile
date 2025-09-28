CC ?= clang
CFLAGS ?= -O2 -g -fno-omit-frame-pointer -Wall -Wextra -Wno-unused-parameter

# Allow building with AFL++ by overriding CC=afl-clang-fast or afl-clang-lto

ROOT := ../../..
IDF_ROOT := $(abspath $(ROOT))

MOCK_INC := mocks/include
HOST_TEST_MOCKS := $(IDF_ROOT)/components/mqtt/esp-mqtt/host_test/mocks/include

INCLUDES := \
  -I$(MOCK_INC) \
  -I$(HOST_TEST_MOCKS) \
  -I$(IDF_ROOT)/components/mqtt/esp-mqtt/include \
  -I$(IDF_ROOT)/components/mqtt/esp-mqtt/lib/include \
  -I$(IDF_ROOT)/components/http_parser

SRCS := \
  $(IDF_ROOT)/components/mqtt/esp-mqtt/mqtt_client.c \
  $(IDF_ROOT)/components/mqtt/esp-mqtt/mqtt5_client.c \
  $(IDF_ROOT)/components/mqtt/esp-mqtt/lib/mqtt_msg.c \
  $(IDF_ROOT)/components/mqtt/esp-mqtt/lib/mqtt5_msg.c \
  $(IDF_ROOT)/components/mqtt/esp-mqtt/lib/mqtt_outbox.c \
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

.PHONY: all clean

all: $(OUT)

OVERRIDES := $(MOCK_INC)/platform_overrides.h $(MOCK_INC)/net/if.h

$(OUT): $(SRCS) $(OVERRIDES)
	$(CC) $(CFLAGS) $(INCLUDES) $(DEFS) -include $(MOCK_INC)/platform_overrides.h -include $(MOCK_INC)/net/if.h $(SRCS) -o $@ $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(OUT)
