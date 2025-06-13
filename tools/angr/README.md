# angr

* Analyzes firmware binary
* Supports many platforms, but not xtensa32, nor riscV-32 (only riscv64)
* Tested with arm-gcc

## Installation

```
$ pip install angr
$ apt install gcc-arm-none-eabi  # Or any other platform
```

## The demo program

This is a simple packet parser that:
- Validates a 4-byte packet header format: [SOF][LEN-L][LEN-H][CHECKSUM]
- Checks for magic byte (0x40), length, and checksum
- Has a deliberate vulnerability that can be found using symbolic execution
- Serves as a demo for using angr to find crash conditions in firmware

## Build

```
arm-none-eabi-gcc packet_parser.c
```

This program parse packet header, checks magic byte, len and checksum,
but could crash under certain conditions.

## Symbolic resolve

```
python solution.py
```

Finds the solution (symbolically evaluates when `_abort()` is called) and prints the input packet.
```
$ python solution.py
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | The program is accessing register with an unspecified value. This could indicate unwanted behavior.
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | angr will cope with this by generating an unconstrained symbolic variable and continuing. You can resolve this by:
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | 1) setting a value to the initial state
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | 2) adding the state option ZERO_FILL_UNCONSTRAINED_{MEMORY,REGISTERS}, to make unknown regions hold null
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | 3) adding the state option SYMBOL_FILL_UNCONSTRAINED_{MEMORY,REGISTERS}, to suppress these messages.
WARNING  | 2025-06-13 21:41:58,223 | angr.storage.memory_mixins.default_filler_mixin | Filling register r5 with 4 unconstrained bytes referenced from 0x84d0 (memset+0x40 in a.out (0x84d0))
WARNING  | 2025-06-13 21:41:58,273 | angr.storage.memory_mixins.default_filler_mixin | Filling register r6 with 4 unconstrained bytes referenced from 0x85ac (__register_exitproc+0x4 in a.out (0x85ac))
WARNING  | 2025-06-13 21:41:58,303 | angr.storage.memory_mixins.default_filler_mixin | Filling register r9 with 4 unconstrained bytes referenced from 0x8004 (_init+0x4 in a.out (0x8004))
WARNING  | 2025-06-13 21:41:58,303 | angr.storage.memory_mixins.default_filler_mixin | Filling register r8 with 4 unconstrained bytes referenced from 0x8004 (_init+0x4 in a.out (0x8004))
Solution: b'@\x00\x11\xed'
```
