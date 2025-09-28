# esp-mqtt AFL++ Fuzz Harness (single-thread)

This is a minimal, host-built fuzz harness for the MQTT client in
`components/mqtt/esp-mqtt/`, designed to run with AFL++ (or standalone) using a
custom in-memory transport. It runs fully single-threaded, without FreeRTOS
tasks or timers, and consumes input bytes as if they were TCP payloads coming
from an MQTT broker.

## Build

- Default host build (clang or gcc):
  - `make -C tools/fuzz/mqtt_client`

- AFL++ build (recommended):
  - `CC=afl-clang-fast make -C tools/fuzz/mqtt_client`
  - Optional flags for sanitizer/cmplog (per your AFL build):
    - `AFL_USE_ASAN=1 CC=afl-clang-fast make -C tools/fuzz/mqtt_client`
    - `AFL_LLVM_CMPLOG=1 CC=afl-clang-fast make -C tools/fuzz/mqtt_client`

The target binary is `tools/fuzz/mqtt_client/mqtt_client_fuzz`.

## How It Works (quick overview)

- The harness configures an MQTT client to use a custom transport that serves
  bytes from the fuzz input (stdin) as “server → client” TCP reads.
- It runs the client in single-threaded “step” mode; no tasks/locks. One run
  processes a small bounded number of steps and exits.
- A deterministic counter backs `platform_tick_get_ms()` to avoid time-based
  blocking.

## CLI Flags (modes and autopilot)

You can control behavior using flags (append flags after the binary):

- `--autopilot`
  - Enables minimal server responses to keep flows alive.
  - Only active when a corresponding `--mode` needs it. Otherwise the transport
    returns exactly what you feed via stdin.

- `--mode=handshake|connected|subscribe|qos|mqtt5|dynamic`
  - `handshake` (default): no automatic replies. You must feed the broker’s
    responses (e.g., CONNACK) within the input.
  - `connected`: autopilot may reply to CONNECT with a valid CONNACK, and to
    PINGREQ with PINGRESP. This keeps the client in connected state even with
    empty/short inputs.
  - `subscribe`: autopilot replies SUBACK to SUBSCRIBE (echoing the packet ID).
  - `qos`: autopilot replies PUBCOMP to PUBREL (QoS 2 half of the handshake).
  - `mqtt5`: forces MQTT v5.0 protocol on the client; autopilot replies with
    MQTT5‑shaped frames (e.g., CONNACK with properties length, SUBACK with
    properties length and reason codes). Combine with `--autopilot`.
  - `dynamic`: the first byte of the fuzz input selects the mode, remaining
    bytes are treated as inbound packets. Selector mapping (lower nibble):
    0x00=handshake, 0x01=connected, 0x02=subscribe, 0x03=qos, 0x04=mqtt5.
    Example: `printf '\x04\x20\x03\x00\x00\x00' | ./mqtt_client_fuzz --mode=dynamic --autopilot`
    sends an MQTT 5 CONNACK under v5 mode.

- `--frag=N`
  - Enables deterministic TCP fragmentation; the transport’s `read()` returns
    at most `N` bytes per call (N > 0).

Examples:

- Feed a valid CONNACK directly (handshake fuzzing):
  - `printf '\x20\x02\x00\x00' | ./mqtt_client_fuzz --mode=handshake`

- Exercise connected state with no input (autopilot provides CONNACK):
  - `./mqtt_client_fuzz --mode=connected --autopilot`

- MQTT 5.0 connected mode (autopilot provides MQTT5 CONNACK/SUBACK):
  - `./mqtt_client_fuzz --mode=mqtt5 --autopilot`

- Dynamic mode with v5 PUBLISH seeds:
  - `./mqtt_client_fuzz --mode=dynamic --autopilot` (use `seeds/v5_*` generated with 0x04 prefix)

- Subscribe flow with SUBACK autopilot and 2‑byte fragmentation:
  - `./mqtt_client_fuzz --mode=subscribe --autopilot --frag=2`

## Protocol bytes (quick reference)

- CONNACK: `20 02 00 00`
- PINGREQ: `C0 00` → PINGRESP: `D0 00`
- SUBSCRIBE (0x80) … → SUBACK (0x90)
- PUBREL (0x62) … → PUBCOMP (0x70)

Note: The harness does not generate server→client PUBLISH frames; your input
should include them if you want to fuzz that parsing path.

## Running with AFL++

1) Build the target with AFL++ instrumentation:

```
CC=afl-clang-fast make -C tools/fuzz/mqtt_client
```

2) Create a seed corpus (a couple of minimal samples):

```
mkdir -p tools/fuzz/mqtt_client/seeds
# Minimal CONNACK for handshake mode
printf '\x20\x02\x00\x00' > tools/fuzz/mqtt_client/seeds/connack
# Empty file as a seed (useful with --mode=connected --autopilot)
: > tools/fuzz/mqtt_client/seeds/empty
```

3) Run AFL++ (choose a mode to match your seed strategy):

- Handshake mode (input provides broker responses):

```
cd tools/fuzz/mqtt_client
AFL_SKIP_CPUFREQ=1 afl-fuzz -i seeds -o findings -- \
  ./mqtt_client_fuzz --mode=handshake
```

- Connected mode with autopilot (keeps client alive even for empty inputs):

```
cd tools/fuzz/mqtt_client
AFL_SKIP_CPUFREQ=1 afl-fuzz -i seeds -o findings -- \
  ./mqtt_client_fuzz --mode=connected --autopilot
```

- Fragmentation stress (e.g., 2 bytes max per read) in handshake mode:

```
cd tools/fuzz/mqtt_client
AFL_SKIP_CPUFREQ=1 afl-fuzz -i seeds -o findings -- \
  ./mqtt_client_fuzz --mode=handshake --frag=2
```

Tips:
- You can run separate AFL campaigns for each mode.
- Consider a CMPLOG secondary (
  `AFL_LLVM_CMPLOG=1 CC=afl-clang-fast make ...` and `-c` companion run) to
  help with varint comparisons (Remaining Length, packet IDs).
- Sanitizers (`AFL_USE_ASAN=1`) can help catch memory errors early.

## Target behavior and outputs

- The harness logs a single debug line on successful connect in single-thread
  builds:

```
[DBG] MQTT client connected (CONNACK accepted)
```

- If you see this line when feeding garbage in `--mode=handshake`, that’s a bug
  (the transport no longer primes CONNACK). In `--mode=connected --autopilot`,
  this is expected even with empty input.

## Scope and limitations

- Single-thread step mode only; no FreeRTOS tasks/locks/timers.
- No external networking or files; transport is in-memory.
- Autopilot is intentionally minimal and deterministic.
- For deeper coverage, add more seeds: SUBACK shapes, PUBLISH QoS 0/1/2, coalesced
  packets, malformed Remaining Length, split varints, UTF-8 edge cases, etc.

## File layout

- `src/harness.c` — main entry; parses flags; runs client in single-thread steps.
- `src/esp_transport_fuzz.c` — custom transport with optional autopilot and fragmentation.
- `mocks/include/` — small host mocks of IDF/FreeRTOS APIs.
- `Makefile` — host/AFL build.

## Troubleshooting

- No connection in handshake mode: your input likely doesn’t contain a valid
  CONNACK. Try the CONNACK seed (`20 02 00 00`).
- Too many retries/log spam: reduce steps (see harness loop) or enable
  `--autopilot` in `--mode=connected`.
- Crashes or sanitizer hits: save repro inputs and file an issue with the input
  and mode flags you used.
