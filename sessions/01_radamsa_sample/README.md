# Radamsa Fuzzing Session: sample + radamsa

This session demonstrates fuzzing the `iot_parser` sample project using the Radamsa fuzzer. The setup is modular: project-specific build logic and tool-specific fuzzing logic are separated for clarity and reusability.

## Structure
- `input_vectors/` — Input vectors for fuzzing (edit or add your own)
- `fuzzing_outputs/` — All fuzzing results (crashes, timeouts, errors, logs)
- `fuzz.sh` — Script to build the sample project and run the fuzzer

## Usage

1. **Edit input vectors (optional):**
   - Edit `input_vectors/sample_inputs.txt` to provide your own test cases.

2. **Run the fuzzing session:**
   ```bash
   ./fuzz.sh
   ```
   This will:
   - Build the sample project (`iot_parser`)
   - Run Radamsa-based fuzzing
   - Store all outputs in `fuzzing_outputs/`

3. **Review results:**
   - Crashes: `fuzzing_outputs/crashes/`
   - Timeouts: `fuzzing_outputs/timeouts/`
   - Errors: `fuzzing_outputs/errors/`
   - Log: `fuzzing_outputs/fuzzing.log`

## Customization
- To use a different project or fuzzer, adjust the build step or the fuzzer invocation in `fuzz.sh`.
- To use a different set of input vectors, edit or replace `input_vectors/sample_inputs.txt`.

---

This session is part of a modular fuzzing framework: project logic and tool logic are kept separate for maximum flexibility.

## Example output
```
(myenv) ~/repos/0xFFFFE/sessions/01_radamsa_sample (main)$ cat fuzzing_outputs/errors/error_1750105700_844.txt | ../../projects/sample/build/iot_parser
IoT Network Message Parser
Supported formats:
  MQTT: mqtt/topic/path {"key":"value"}
  HTTP: GET /path {"key":"value"}
  HTTP: POST /path {"key":"value"}
=================================================================
==639416==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7fffacacd1c0 at pc 0x7f813969e16d bp 0x7fffacacd000 sp 0x7fffacacc7a8
WRITE of size 302 at 0x7fffacacd1c0 thread T0
    #0 0x7f813969e16c in __interceptor_strcpy ../../../../src/libsanitizer/asan/asan_interceptors.cc:431
    #1 0x55855b883841 in parse_mqtt_topic /home/david/repos/0xFFFFE/projects/sample/iot_parser.c:37
    #2 0x55855b885094 in main /home/david/repos/0xFFFFE/projects/sample/iot_parser.c:166
    #3 0x7f8138ac7082 in __libc_start_main ../csu/libc-start.c:308
    #4 0x55855b88350d in _start (/home/david/repos/0xFFFFE/projects/sample/build/iot_parser+0x450d)

Address 0x7fffacacd1c0 is located in stack of thread T0 at offset 368 in frame
    #0 0x55855b884d6c in main /home/david/repos/0xFFFFE/projects/sample/iot_parser.c:150

  This frame has 3 object(s):
    [48, 368) 'mqtt_msg' (line 165)
    [432, 760) 'http_msg' (line 169) <== Memory access at offset 368 partially underflows this variable
    [832, 1344) 'input' (line 151)
HINT: this may be a false positive if your program uses some custom stack unwind mechanism, swapcontext or vfork
      (longjmp and C++ exceptions *are* supported)
SUMMARY: AddressSanitizer: stack-buffer-overflow ../../../../src/libsanitizer/asan/asan_interceptors.cc:431 in __interceptor_strcpy
Shadow bytes around the buggy address:
  0x1000759519e0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x1000759519f0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100075951a00: 00 00 00 00 00 00 00 00 00 00 f1 f1 f1 f1 f1 f1
  0x100075951a10: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100075951a20: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
=>0x100075951a30: 00 00 00 00 00 00 00 00[f2]f2 f2 f2 f2 f2 f2 f2
  0x100075951a40: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100075951a50: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100075951a60: 00 00 00 00 00 00 00 00 00 f2 f2 f2 f2 f2 f2 f2
  0x100075951a70: f2 f2 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100075951a80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
  Shadow gap:              cc
==639416==ABORTING
```
