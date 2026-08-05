"""Minimal Godot .pck (format 3) reader -- the S5 parser, as a module.

The pack's file table lives at the END of the file; its offset is a u64 at
header byte 0x20, and every entry offset is relative to file_base = 112.
Read-only: nothing here writes to a pack or to a game directory.

Used by the Track M spine probe (docs/animation-downfall-investigation-*.md)
to answer "what actually landed in the pack" without trusting the exporter's
own report.
"""
from __future__ import annotations

import struct
import sys
from typing import BinaryIO, NamedTuple

FILE_BASE = 112


class Entry(NamedTuple):
    path: str
    offset: int
    size: int
    flags: int


def parse(path: str) -> tuple[BinaryIO, tuple[int, int, int, int], list[Entry]]:
    f = open(path, "rb")
    magic = f.read(4)
    if magic != b"GDPC":
        raise ValueError(f"{path}: not a Godot pack (magic {magic!r})")
    header = struct.unpack("<4I", f.read(16))
    f.seek(0x20)
    (dir_off,) = struct.unpack("<Q", f.read(8))
    f.seek(dir_off)
    (count,) = struct.unpack("<I", f.read(4))
    entries: list[Entry] = []
    for _ in range(count):
        (slen,) = struct.unpack("<I", f.read(4))
        p = f.read(slen).rstrip(b"\0").decode("utf-8", "replace")
        off, size = struct.unpack("<QQ", f.read(16))
        f.read(16)  # md5
        (flags,) = struct.unpack("<I", f.read(4))
        entries.append(Entry(p, off, size, flags))
    return f, header, entries


def read(f: BinaryIO, entry: Entry) -> bytes:
    f.seek(FILE_BASE + entry.offset)
    return f.read(entry.size)


def find(entries: list[Entry], needle: str) -> list[Entry]:
    return [e for e in entries if needle in e.path]


if __name__ == "__main__":
    pck = sys.argv[1]
    needle = sys.argv[2] if len(sys.argv) > 2 else ""
    _f, hdr, ents = parse(pck)
    print(f"format={hdr[0]} godot={hdr[1]}.{hdr[2]}.{hdr[3]} entries={len(ents)}")
    for e in sorted(find(ents, needle)):
        print(f"{e.size:10d}  {e.path}")
