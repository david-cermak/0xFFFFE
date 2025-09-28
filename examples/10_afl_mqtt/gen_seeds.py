#!/usr/bin/env python3
"""
MQTT seed generator for esp-mqtt fuzz harness.

Generates valid MQTT v3.1.1 packets that the client receives from a broker
(server→client), with emphasis on PUBLISH variants and other common inbound
packets. Outputs individual binary files under tools/fuzz/mqtt_client/seeds/.

No external dependencies. If paho-mqtt is installed, it is not used here.

Usage:
  python3 tools/fuzz/mqtt_client/gen_seeds.py [--out tools/fuzz/mqtt_client/seeds]

Notes:
- Packets target realistic, well-formed cases to guide AFL++ towards deeper paths.
- Sizes are kept modest to avoid huge files while still crossing varint edges.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable, Tuple


# ----- MQTT helpers (v3.1.1) -----

def enc_remaining_length(n: int) -> bytes:
    if n < 0:
        raise ValueError("remaining length must be >= 0")
    out = bytearray()
    while True:
        byte = n % 128
        n //= 128
        if n > 0:
            byte |= 0x80
        out.append(byte)
        if n == 0:
            break
    return bytes(out)


def enc_utf8(s: str) -> bytes:
    b = s.encode("utf-8")
    if len(b) > 0xFFFF:
        raise ValueError("string too long")
    return len(b).to_bytes(2, "big") + b


def fh(ctrl: int, remaining_len: int) -> bytes:
    return bytes([ctrl]) + enc_remaining_length(remaining_len)


def pkt_connack(session_present: bool = False, rc: int = 0) -> bytes:
    # rc (return code): 0=accepted, others are refusal codes in 3.1.1
    flags = 0x01 if session_present else 0x00
    vh = bytes([flags, rc])
    return fh(0x20, len(vh)) + vh


def pkt_pingresp() -> bytes:
    return b"\xD0\x00"


def pkt_puback(pkt_id: int) -> bytes:
    vh = pkt_id.to_bytes(2, "big")
    return fh(0x40, len(vh)) + vh


def pkt_pubrec(pkt_id: int) -> bytes:
    vh = pkt_id.to_bytes(2, "big")
    return fh(0x50, len(vh)) + vh


def pkt_pubrel(pkt_id: int) -> bytes:
    # In MQTT 3.1.1 the flags must be 0x02, so ctrl is 0x62
    vh = pkt_id.to_bytes(2, "big")
    return fh(0x62, len(vh)) + vh


def pkt_pubcomp(pkt_id: int) -> bytes:
    vh = pkt_id.to_bytes(2, "big")
    return fh(0x70, len(vh)) + vh


def pkt_suback(pkt_id: int, grants: Iterable[int]) -> bytes:
    grants_b = bytes(grants)
    vh = pkt_id.to_bytes(2, "big") + grants_b
    return fh(0x90, len(vh)) + vh


def pkt_publish(
    topic: str,
    payload: bytes,
    qos: int = 0,
    dup: bool = False,
    retain: bool = False,
    pkt_id: int | None = None,
) -> bytes:
    if qos not in (0, 1, 2):
        raise ValueError("qos must be 0,1,2")
    # Control header with flags
    ctrl = 0x30
    if dup:
        ctrl |= 0x08
    if qos == 1:
        ctrl |= 0x02
    elif qos == 2:
        ctrl |= 0x04
    if retain:
        ctrl |= 0x01

    # Variable header: topic, [packet id]
    vh = enc_utf8(topic)
    if qos > 0:
        if pkt_id is None:
            raise ValueError("pkt_id required for qos>0")
        vh += pkt_id.to_bytes(2, "big")

    remaining = len(vh) + len(payload)
    return fh(ctrl, remaining) + vh + payload


# ----- MQTT v5 helpers -----

def pkt5_connack(session_present: bool = False, reason_code: int = 0, properties: bytes = b"") -> bytes:
    flags = 0x01 if session_present else 0x00
    props_len = enc_remaining_length(len(properties))
    vh = bytes([flags, reason_code]) + props_len + properties
    return fh(0x20, len(vh)) + vh


def pkt5_suback(pkt_id: int, reason_codes: Iterable[int], properties: bytes = b"") -> bytes:
    props_len = enc_remaining_length(len(properties))
    payload = bytes(reason_codes)
    vh = pkt_id.to_bytes(2, "big") + props_len + properties
    return fh(0x90, len(vh) + len(payload)) + vh + payload


def pkt5_puback_like(ctrl: int, pkt_id: int, include_reason: bool = False) -> bytes:
    # ctrl: 0x40 PUBACK, 0x50 PUBREC, 0x62 PUBREL, 0x70 PUBCOMP
    if include_reason:
        # Reason Code 0x00 (Success), Properties length 0x00
        vh = pkt_id.to_bytes(2, "big") + b"\x00\x00"
    else:
        # Minimal form with only Packet Identifier (allowed when success/no props)
        vh = pkt_id.to_bytes(2, "big")
    return fh(ctrl, len(vh)) + vh


def pkt5_publish(
    topic: str,
    payload: bytes,
    qos: int = 0,
    dup: bool = False,
    retain: bool = False,
    pkt_id: int | None = None,
    properties: bytes = b"",
) -> bytes:
    if qos not in (0, 1, 2):
        raise ValueError("qos must be 0,1,2")
    ctrl = 0x30
    if dup:
        ctrl |= 0x08
    if qos == 1:
        ctrl |= 0x02
    elif qos == 2:
        ctrl |= 0x04
    if retain:
        ctrl |= 0x01

    vh = enc_utf8(topic)
    if qos > 0:
        if pkt_id is None:
            raise ValueError("pkt_id required for qos>0")
        vh += pkt_id.to_bytes(2, "big")
    vh += enc_remaining_length(len(properties)) + properties
    remaining = len(vh) + len(payload)
    return fh(ctrl, remaining) + vh + payload


# ----- Corpus generation -----

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_seed(base: str, name: str, data: bytes) -> None:
    p = os.path.join(base, name)
    with open(p, "wb") as f:
        f.write(data)


def write_dynamic_seed(base: str, mode_selector: int, name: str, data: bytes) -> None:
    if not (0 <= mode_selector <= 0x0F):
        raise ValueError("mode selector out of range")
    prefixed = bytes([mode_selector & 0x0F]) + data
    write_seed(base, f"dyn_{name}", prefixed)


def gen_connack(out: str) -> None:
    write_seed(out, "connack_ok.bin", pkt_connack(False, 0))
    write_seed(out, "connack_session_present.bin", pkt_connack(True, 0))
    # Dynamic-prefixed v3.1.1 (selector 0x00 = handshake)
    write_dynamic_seed(out, 0x00, "connack_ok.bin", pkt_connack(False, 0))
    write_dynamic_seed(out, 0x00, "connack_session_present.bin", pkt_connack(True, 0))
    # Refusal codes (still well-formed frames)
    for rc, label in [
        (1, "unacceptable_protocol"),
        (2, "identifier_rejected"),
        (3, "server_unavailable"),
        (4, "bad_username_password"),
        (5, "not_authorized"),
    ]:
        name = f"connack_refused_{label}.bin"
        pkt = pkt_connack(False, rc)
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x00, name, pkt)

    # MQTT v5 minimal CONNACK and a couple refusal reasons
    write_seed(out, "v5_connack_ok.bin", pkt5_connack(False, 0x00))
    write_seed(out, "v5_connack_session_present.bin", pkt5_connack(True, 0x00))
    write_dynamic_seed(out, 0x04, "v5_connack_ok.bin", pkt5_connack(False, 0x00))
    write_dynamic_seed(out, 0x04, "v5_connack_session_present.bin", pkt5_connack(True, 0x00))
    for rc, label in [
        (0x81, "malformed_packet"),
        (0x8C, "unsupported_protocol"),
        (0x87, "not_authorized"),
    ]:
        name = f"v5_connack_refused_{label}.bin"
        pkt = pkt5_connack(False, rc)
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x04, name, pkt)


def gen_publish(out: str) -> None:
    topic = "sensors/temperature"
    small_payloads: Tuple[bytes, ...] = (
        b"",
        b"x",
        b"hello",
        b"json:{\"t\":25.3}",
    )
    # QoS 0 variants
    for i, pl in enumerate(small_payloads):
        name = f"publish_qos0_small_{i}.bin"
        pkt = pkt_publish(topic, pl, qos=0, dup=False, retain=False)
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x01, name, pkt)  # connected
    # QoS 0 with retain and dup flags
    name = "publish_qos0_retain.bin"; pkt = pkt_publish(topic, b"retain", qos=0, dup=False, retain=True)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_qos0_dup.bin"; pkt = pkt_publish(topic, b"dup", qos=0, dup=True, retain=False)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # QoS 1 variants
    name = "publish_qos1_basic.bin"; pkt = pkt_publish(topic, b"ack-me", qos=1, dup=False, retain=False, pkt_id=1)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_qos1_dup.bin"; pkt = pkt_publish(topic, b"dup1", qos=1, dup=True, retain=False, pkt_id=0x1234)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_qos1_retain.bin"; pkt = pkt_publish(topic, b"keep", qos=1, dup=False, retain=True, pkt_id=2)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # QoS 2 variants
    name = "publish_qos2_basic.bin"; pkt = pkt_publish(topic, b"two-phase", qos=2, dup=False, retain=False, pkt_id=10)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_qos2_dup.bin"; pkt = pkt_publish(topic, b"dup2", qos=2, dup=True, retain=False, pkt_id=0xBEEF)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_qos2_retain.bin"; pkt = pkt_publish(topic, b"store", qos=2, dup=False, retain=True, pkt_id=11)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # Boundary tests around Remaining Length varint (keep files modest)
    # Use short topic to keep payload sizes manageable.
    short_topic = "t"
    # For QoS0: RL = 2+len(topic) + payload_len
    vh_len_q0 = 2 + len(short_topic)
    # Choose total RL near 127 and 128 boundaries.
    for rl in (127, 128, 129):
        payload_len = max(0, rl - vh_len_q0)
        pl = bytes([0xAA]) * payload_len
        name = f"publish_qos0_rl{rl}.bin"; pkt = pkt_publish(short_topic, pl, qos=0)
        write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # For QoS1: RL = 2+len(topic) + 2(pkt id) + payload
    vh_len_q1 = 2 + len(short_topic) + 2
    for rl in (127, 128, 129):
        payload_len = max(0, rl - vh_len_q1)
        pl = bytes([0x55]) * payload_len
        name = f"publish_qos1_rl{rl}.bin"; pkt = pkt_publish(short_topic, pl, qos=1, pkt_id=0x2222)
        write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # UTF-8 topic with multi-byte characters
    utf_topic = "s/温度/°C"
    name = "publish_utf8_topic_qos0.bin"; pkt = pkt_publish(utf_topic, b"bytes", qos=0)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "publish_utf8_topic_qos1.bin"; pkt = pkt_publish(utf_topic, b"ack", qos=1, pkt_id=3)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # MQTT v5 PUBLISH with empty properties
    name = "v5_publish_qos0.bin"; pkt = pkt5_publish("v5/t", b"p0")
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x04, name, pkt)
    name = "v5_publish_qos1.bin"; pkt = pkt5_publish("v5/t", b"p1", qos=1, pkt_id=1)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x04, name, pkt)
    name = "v5_publish_qos2.bin"; pkt = pkt5_publish("v5/t", b"p2", qos=2, pkt_id=2)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x04, name, pkt)

    # MQTT v5 varint boundary for remaining length with minimal properties
    short_topic = "v"
    vh_len_q0 = 2 + len(short_topic) + 1  # +1 for properties length=0
    for rl in (127, 128, 129):
        payload_len = max(0, rl - vh_len_q0)
        pl = bytes([0xCC]) * payload_len
        name = f"v5_publish_qos0_rl{rl}.bin"; pkt = pkt5_publish(short_topic, pl, qos=0)
        write_seed(out, name, pkt); write_dynamic_seed(out, 0x04, name, pkt)


def gen_qos_acks(out: str) -> None:
    # Acks that a broker could send back
    for name, pkt in [
        ("puback_1.bin", pkt_puback(1)),
        ("pubrec_1.bin", pkt_pubrec(1)),
        ("pubrel_1.bin", pkt_pubrel(1)),
        ("pubcomp_1.bin", pkt_pubcomp(1)),
    ]:
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x01, name, pkt)
    # Higher IDs
    name = "puback_beef.bin"; pkt = pkt_puback(0xBEEF)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)
    name = "pubcomp_cafe.bin"; pkt = pkt_pubcomp(0xCAFE)
    write_seed(out, name, pkt); write_dynamic_seed(out, 0x01, name, pkt)

    # MQTT v5 ack forms: minimal and with reason+props
    for name, pkt in [
        ("v5_puback_min.bin", pkt5_puback_like(0x40, 1, include_reason=False)),
        ("v5_puback_full.bin", pkt5_puback_like(0x40, 1, include_reason=True)),
        ("v5_pubrec_min.bin", pkt5_puback_like(0x50, 2, include_reason=False)),
        ("v5_pubrec_full.bin", pkt5_puback_like(0x50, 2, include_reason=True)),
        ("v5_pubrel_min.bin", pkt5_puback_like(0x62, 3, include_reason=False)),
        ("v5_pubcomp_min.bin", pkt5_puback_like(0x70, 4, include_reason=False)),
    ]:
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x04, name, pkt)


def gen_subacks(out: str) -> None:
    for name, pkt in [
        ("suback_single_q0.bin", pkt_suback(1, [0])),
        ("suback_single_q1.bin", pkt_suback(2, [1])),
        ("suback_single_q2.bin", pkt_suback(3, [2])),
        ("suback_single_fail.bin", pkt_suback(4, [0x80])),
        ("suback_multi_mixed.bin", pkt_suback(5, [0, 1, 2, 0x80])),
    ]:
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x02, name, pkt)

    # MQTT v5 SUBACKs with properties length 0
    for name, pkt in [
        ("v5_suback_q0.bin", pkt5_suback(11, [0x00])),
        ("v5_suback_q1.bin", pkt5_suback(12, [0x01])),
        ("v5_suback_q2.bin", pkt5_suback(13, [0x02])),
        ("v5_suback_fail.bin", pkt5_suback(14, [0x80])),
    ]:
        write_seed(out, name, pkt)
        write_dynamic_seed(out, 0x04, name, pkt)


def gen_misc(out: str) -> None:
    write_seed(out, "pingresp.bin", pkt_pingresp())
    # Coalesced frames in one TCP read: CONNACK + PUBLISH + PINGRESP
    seq = pkt_connack(False, 0) + pkt_publish("coalesced/topic", b"data", qos=0) + pkt_pingresp()
    write_seed(out, "coalesced_connack_publish_pingresp.bin", seq)
    write_dynamic_seed(out, 0x01, "coalesced_connack_publish_pingresp.bin", seq)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default=os.path.join("tools", "fuzz", "mqtt_client", "seeds"),
        help="output directory for seed corpus",
    )
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out)
    ensure_dir(out_dir)

    gen_connack(out_dir)
    gen_publish(out_dir)
    gen_qos_acks(out_dir)
    gen_subacks(out_dir)
    gen_misc(out_dir)

    print(f"Generated seeds in: {out_dir}")


if __name__ == "__main__":
    main()
