# 09 -- AFLNet with lwip/dhcp server module

## Install AFLNet

## Build the fuzzer program

```
CC=afl-gcc make
```

## Run

```
afl-fuzz -d -i in -o ./out-dhcp -m none -N udp://127.0.0.1/50037 -P DHCP -D 10000 -q 3 -s 3 -E -K -R ./lwip_fuzz
```
