# Fuzzing mDNS example on target using boofuzz

* Install boofuzz
* Create mDNS project from example:
```
idf.py create-project-from-example "espressif/mdns:query_advertise"
```
* Set connection method (Wi-Fi/Ethernet)
* Build and flash and wait for acquiring an IP

## Start fuzzing

```
python mdns.py --address [ESP32-address]
```

## Example output:

ESP32:
```
TX[0][0]: To: 224.0.0.251:5353, Packet[11550]: AUTHORITATIVE
    A: _services._dns-sd._udp.local. PTR IN 4500[13] ._http._tcp.local.
    A: ESP32-WebServer1._http._tcp.local. SRV IN FLUSH 120[19] 0 0 80 esp32-mdns.local.
    A: ESP32-WebServer1._http._tcp.local. TXT IN FLUSH 4500[21] u=admin; path=/foobar
    A: esp32-mdns.local. A IN FLUSH 120[4] 192.168.0.37
    A: _services._dns-sd._udp.local. PTR IN 4500[2] ._http._tcp.local.
    A: _http._tcp.local. PTR IN 4500[18] ESP32-WebServer._http._tcp.local.
    A: _server._http._tcp.local. PTR IN 4500[2] ESP32-WebServer._http._tcp.local.
    A: ESP32-WebServer._http._tcp.local. SRV IN FLUSH 120[8] 0 0 80 esp32-mdns.local.
    A: ESP32-WebServer._http._tcp.local. TXT IN FLUSH 4500[30] p=password; u=user; board=esp32

RX[0][0]: From: 192.168.0.32:56351, To: 192.168.0.37, Packet[35940]:
    Q: *U* AAAAAAAAAA.... PTR IN
    S: AAAAAAAAAA.... PTR IN FLUSH 120[0] ....
ERROR: content length overflow

RX[0][0]: From: 192.168.0.32:34547, To: 192.168.0.37, Packet[48080]:
    Q: *U* AAAAAAAAAA.... PTR IN
    S: AAAAAAAAAA.... PTR IN FLUSH 120[0] ....
ERROR: content length overflow

RX[0][0]: From: 192.168.0.32:49588, To: 192.168.0.37, Packet[60060]:
    Q: *U* AAAAAAAAAA.... PTR IN
    S: AAAAAAAAAA.... PTR IN FLUSH 120[0] ....
ERROR: content length overflow

RX[0][0]: From: 192.168.0.32:48353, To: 192.168.0.37, Packet[72150]:
    Q: *U* AAAAAAAAAA.... PTR IN
    S: AAAAAAAAAA.... PTR IN FLUSH 120[0] ....
ERROR: content length overflow

RX[0][0]: From: 192.168.0.32:49130, To: 192.168.0.37, Packet[84130]:
    Q: *U* AAAAAAAAAA.... PTR IN
    S: AAAAAAAAAA.... PTR IN FLUSH 120[0] ....
ERROR: content length overflow
```

---
Fuzzer:
```
[2025-06-17 19:17:41,756] Test Case: 32: query:[query.TransactionID:31]
[2025-06-17 19:17:41,756]     Info: Type: Word
[2025-06-17 19:17:41,756]     Info: Opening target connection (192.168.0.37:5353)...
[2025-06-17 19:17:41,757]     Info: Connection opened.
[2025-06-17 19:17:41,757]   Test Step: Monitor <class '__main__.IOT_TargetMonitor'>.pre_send()
[2025-06-17 19:17:41,757]   Test Step: Monitor CallbackMonitor#140345032411264[pre=[],post=[],restart=[],post_start_target=[]].pre_send()
[2025-06-17 19:17:41,757]   Test Step: Callback function 'insert_questions'
[2025-06-17 19:17:41,757]   Test Step: Fuzzing Node 'query'
[2025-06-17 19:17:41,759]     Info: Sending 52 bytes...
[2025-06-17 19:17:41,760]     Transmitted 52 bytes: f7 0f 00 00 00 01 00 00 00 01 00 00 0a 41 41 41 41 41 41 41 41 41 41 00 00 0c 80 01 0a 41 41 41 41 41 41 41 41 41 41 00 00 0c 80 01 00 00 00 78 00 00 00 00 b'\xf7\x0f\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\nAAAAAAAAAA\x00\x00\x0c\x80\x01\nAAAAAAAAAA\x00\x00\x0c\x80\x01\x00\x00\x00x\x00\x00\x00\x00'
[2025-06-17 19:17:41,760]   Test Step: Contact target monitors
[2025-06-17 19:17:41,760]   Test Step: Cleaning up connections from callbacks
[2025-06-17 19:17:41,760]       Check OK: No crash detected.
[2025-06-17 19:17:41,760]     Info: Closing target connection...
[2025-06-17 19:17:41,760]     Info: Connection closed.
[2025-06-17 19:17:41,760]   Test Step: Sleep between tests.
[2025-06-17 19:17:41,760]     Info: sleeping for 12.000000 seconds
[2025-06-17 19:17:53,814] Test Case: 33: query:[query.TransactionID:32]
[2025-06-17 19:17:53,815]     Info: Type: Word
[2025-06-17 19:17:53,815]     Info: Opening target connection (192.168.0.37:5353)...
[2025-06-17 19:17:53,815]     Info: Connection opened.
[2025-06-17 19:17:53,815]   Test Step: Monitor <class '__main__.IOT_TargetMonitor'>.pre_send()
[2025-06-17 19:17:53,815]   Test Step: Monitor CallbackMonitor#140345032411264[pre=[],post=[],restart=[],post_start_target=[]].pre_send()
[2025-06-17 19:17:53,815]   Test Step: Callback function 'insert_questions'
[2025-06-17 19:17:53,815]   Test Step: Fuzzing Node 'query'
[2025-06-17 19:17:53,817]     Info: Sending 52 bytes...
[2025-06-17 19:17:53,817]     Transmitted 52 bytes: f8 0f 00 00 00 01 00 00 00 01 00 00 0a 41 41 41 41 41 41 41 41 41 41 00 00 0c 80 01 0a 41 41 41 41 41 41 41 41 41 41 00 00 0c 80 01 00 00 00 78 00 00 00 00 b'\xf8\x0f\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\nAAAAAAAAAA\x00\x00\x0c\x80\x01\nAAAAAAAAAA\x00\x00\x0c\x80\x01\x00\x00\x00x\x00\x00\x00\x00'
[2025-06-17 19:17:53,817]   Test Step: Contact target monitors
[2025-06-17 19:17:53,817]   Test Step: Cleaning up connections from callbacks
[2025-06-17 19:17:53,817]       Check OK: No crash detected.
[2025-06-17 19:17:53,817]     Info: Closing target connection...
[2025-06-17 19:17:53,817]     Info: Connection closed.
[2025-06-17 19:17:53,817]   Test Step: Sleep between tests.
[2025-06-17 19:17:53,818]     Info: sleeping for 12.000000 seconds
```
