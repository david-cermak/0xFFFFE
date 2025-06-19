# Fuzzing IoT Parser using boofuzz

* Install boofuzz
* Run `python iot_parser_fuzz.py`

## Example output
```
[2025-06-17 19:05:16,420]   Test Step: Fuzzing Node 'mqtt-message'
[2025-06-17 19:05:16,420]     Info: Sending 266 bytes...
[2025-06-17 19:05:16,449]     Info: Process exit code: 1
[2025-06-17 19:05:16,449]     Transmitted 266 bytes: 6d 71 74 74 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 25 73 20 7b 22 64 65 76 69 63 65 5f 69 64 22 3a 22 73 65 6e 73 6f 72 30 31 22 2c 22 74 65 6d 70 65 72 61 74 75 72 65 22 3a 32 33 2e 35 2c 22 73 74 61 74 75 73 22 3a 22 61 63 74 69 76 65 22 7d b'mqtt%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s {"device_id":"sensor01","temperature":23.5,"status":"active"}'
[2025-06-17 19:05:16,450]   Test Step: Contact target monitors
[2025-06-17 19:05:16,450]     Info: post_send() called - checking for crashes
[2025-06-17 19:05:16,450]     Error!!!! post_send(): got exit code 1
[2025-06-17 19:05:16,450]     Error!!!! CRASH DETECTED: Process exited with code 1
[2025-06-17 19:05:16,450]       Check Failed: <__main__.ProcessTargetMonitor object at 0x7fb3e1c82cd0> detected crash on test case #19:
[2025-06-17 19:05:16,450]   Test Step: Cleaning up connections from callbacks
[2025-06-17 19:05:16,450]     Info: Closing target connection...
[2025-06-17 19:05:16,450]     Info: Connection closed.
[2025-06-17 19:05:16,450]   Test Step: Failure summary
[2025-06-17 19:05:16,450]     Info: <__main__.ProcessTargetMonitor object at 0x7fb3e1c82cd0> detected crash on test case #19:
[2025-06-17 19:05:16,450]   Test Step: Restarting target
[2025-06-17 19:05:16,450]     Info: Restarting target process using ProcessTargetMonitor
[2025-06-17 19:05:16,450]     Info: restart_target() called - target restarted
[2025-06-17 19:05:16,450]     Info: Giving the process 3 seconds to settle in
```
