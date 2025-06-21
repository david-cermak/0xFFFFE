# Examples

This folder contains information about separate fuzzing sessions.
It's a set of concrete examples of
* using tools (from `tools` dir)
* on project (from `projects` directory)
* with methods (from `methods` directory).

This is also the best way to get started and experiment with real life fuzz targets.

## 00 -- Hello world demo on radamsa


| Tool | Project | Method |
|------|---------|--------|
| radamsa | hello | host  |


## 01 -- Sample IoT-parser on radamsa

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|--------|--------|
| radamsa | parser | host  | very simple |     |

## 02 -- LWIP's DHCP module on AFL++

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|--------|--------|
| AFLplusplus | lwip | host | Very powerful | Needs host compilation |

## 03 -- Sample IoT-parser on boofuzz

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|------------|-------|
| boofuzz | parser | host  | Understand protocols |   |
|         |        |       | Monitor status       |   |

## 04 -- ESP32 mDNS app on target on boofuzz

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|------------|-------|
| boofuzz | mdns | target | Protocol aware | Very slow on target |
|         |      |        | Target specific issues |             |

## 05 -- Sample IoT-parser on Fuzztest

| Tool | Project | Method |   Highlights | Notes |
|------|---------|--------|--------------|-------|
| fuzztest | parser | host | + unit tests |  needs clang |
|          |        |      | + property based tests |    |


## 06 -- Firmware binary on angr

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|------------|-------|
| angr | protocol | firmware-binary  | works with binary | limited |
|      |         |                   | analytic solution | no support for riscV32 |

## 07 -- Fuzzing LWIP in CI with AFL++

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|--------|--------|
| AFLplusplus | lwip | host | CI job | complicated/stateful |

## 08 -- mDNS with AFL++ and LLM to generate seed inputs

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|--------|--------|
| AFLplusplus | mdns | host | LLM test generation |  |


## 09 -- DHCP server with stateful AFLNet

| Tool | Project | Method | Highlights | Notes |
|------|---------|--------|--------|--------|
| AFLNet | DHCP | host | Protocol/state aware |  |
