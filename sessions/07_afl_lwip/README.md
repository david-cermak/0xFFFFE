# Fuzzing LWIP upstream with AFL++

This fuzzing session is part of the [CI](../../.github/workflows/fuzz_lwip.yml)

## Steps to run fuzzer

* Install docker/podman
* Pull latest aflplusplus
* Launch the container with lwip shared folder
* build with afl-cc-fast
* run `afl-fuzz -i input -o out -- ./lwip_fuzz`
