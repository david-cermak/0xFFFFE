# Fuzzing hello world

Simple getting start example with Black box mutation fuzzer "radamsa"

## Example output

```
(myenv) ~/repos/0xFFFFE/sessions/00_radamsa_hello (main)$ ./fuzz.sh
Building the project...
-- Configuring done (0.0s)
-- Generating done (0.0s)
-- Build files have been written to: /home/david/repos/0xFFFFE/projects/hello_world/build
[100%] Built target hello
Running the fuzzer...
Starting radamsa fuzzing...
Target: /home/david/repos/0xFFFFE/projects/hello_world/build/hello
Runs: 1000
Timeout: 5s per run
Sample file: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/input_vectors/sample_inputs.txt
Crashes will be saved to: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/crashes/
Timeouts will be saved to: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/timeouts/
Other errors will be saved to: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/errors/
Log file: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/fuzzing.log
==========================================
....................................................................................................
Progress: 100/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 0
....................................................................................................
Progress: 200/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 0
....................................................................................E...............
Progress: 300/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 1
...........................................................................E........................
Progress: 400/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 2
....................E...............................................................................
Progress: 500/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 3
.....................................E..............................................................
Progress: 600/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 4
....................................................................................................
Progress: 700/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 4
..........................................................................E.........................
Progress: 800/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 5
....................................................................................................
Progress: 900/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 5
................................................................................E...................
Progress: 1000/1000 runs - Crashes: 0 - Timeouts: 0 - Errors: 6

==========================================
Fuzzing completed!
Total runs: 1000
Crashes found: 0
Timeouts: 0
Other errors: 6
Success rate: 99.40%
Error files saved in: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/errors/

Check the log file for details: /home/david/repos/0xFFFFE/sessions/00_radamsa_hello/fuzzing_outputs/fuzzing.log
```

## Recreating errors:

```
(myenv) ~/repos/0xFFFFE/sessions/00_radamsa_hello (main)$ cat fuzzing_outputs/errors/error_1750104642_387.txt
He&#000;!xcalc%#x%n;xcalc\nNaN+inf%dldo󠁐 World%d
Test ��1󠀹32 !A#$%
(myenv) ~/repos/0xFFFFE/sessions/00_radamsa_hello (main)$ cat fuzzing_outputs/errors/error_1750104642_387.txt | ../../projects/hello_world/build/hello
AddressSanitizer:DEADLYSIGNAL
=================================================================
==624270==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000000 (pc 0x7fe8b31d709c bp 0x7ffc4bc5da60 sp 0x7ffc4bc5d4f0 T0)
==624270==The signal is caused by a WRITE memory access.
==624270==Hint: address points to the zero page.
    #0 0x7fe8b31d709b in __vfprintf_internal /build/glibc-B3wQXB/glibc-2.31/stdio-common/vfprintf-internal.c:1687
    #1 0x7fe8b33eddc6 in __interceptor_vprintf ../../../../src/libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:1600
    #2 0x7fe8b33edee6 in __interceptor_printf ../../../../src/libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:1658
    #3 0x55adc863d453 in main /home/david/repos/0xFFFFE/projects/hello_world/hello.c:16
    #4 0x7fe8b3182082 in __libc_start_main ../csu/libc-start.c:308
    #5 0x55adc863d20d in _start (/home/david/repos/0xFFFFE/projects/hello_world/build/hello+0x120d)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /build/glibc-B3wQXB/glibc-2.31/stdio-common/vfprintf-internal.c:1687 in __vfprintf_internal
==624270==ABORTING
```

## Takeaways

* `radamsa` is a very simple tool to start with
* use sanitizers to help find more bugs
* use the helper scripts in [tools/radamsa](../../tools/radamsa/run_fuzzer.sh) to
  - feed the `radamsa` generated inputs to your fuzz targets
  - configure various "seed" inputs
  - save inputs that caused errors or timeouts
