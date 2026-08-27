"""A read-only reader for the `.pck` files the bake-off exports.

Package cost is one of the four things this lane is asked to measure, and
"bytes on disk" is only half of it -- the other half is what is actually inside
the pack, which is the number the mod's own derived contract cares about
(`tools/build_pck.ps1:789-823`). Nothing else in the repo can read a pack, so
this exists.

Format, as observed in the packs MegaDot 4.5.1 writes (pack format version 3;
the bytes below were read out of an export produced by
`tools/animation_bakeoff/export_bakeoff.ps1`, not taken from documentation):

    0   char[4]  "GDPC"
    4   u32      pack format version (3)
    8   u32      engine version major
    12  u32      engine version minor
    16  u32      engine version patch
    20  u32      pack flags (bit 1 = file offsets are relative to file_base)
    24  u64      file_base
    32  u64      directory offset
    40  ...      reserved, zero-filled, up to file_base
    <directory offset>
        u32      file count
        per file:
          u32    path length
          char[] path, NUL-padded, WITHOUT the `res://` prefix
          u64    offset
          u64    size
          u8[16] md5
          u32    flags

A pack that does not start with `GDPC` or does not carry format 3 raises,
rather than being silently reported as empty -- an empty resource list is the
exact reading that would make a broken export look cheap.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"GDPC"
SUPPORTED_FORMAT = 3
HEADER_DIR_OFFSET = 32


@dataclass(frozen=True)
class PckEntry:
    path: str
    offset: int
    size: int
    md5: str
    flags: int


@dataclass(frozen=True)
class Pck:
    engine_version: tuple[int, int, int]
    format_version: int
    flags: int
    file_base: int
    total_bytes: int
    entries: tuple[PckEntry, ...]

    @property
    def resource_paths(self) -> tuple[str, ...]:
        return tuple(e.path for e in self.entries)

    @property
    def payload_bytes(self) -> int:
        return sum(e.size for e in self.entries)


def read(path: Path) -> Pck:
    blob = path.read_bytes()
    if blob[:4] != MAGIC:
        raise ValueError(f"{path}: not a Godot pack (magic {blob[:4]!r})")
    fmt, major, minor, patch, flags = struct.unpack_from("<IIIII", blob, 4)
    if fmt != SUPPORTED_FORMAT:
        raise ValueError(f"{path}: pack format {fmt}, this reader only knows {SUPPORTED_FORMAT}")
    (file_base,) = struct.unpack_from("<Q", blob, 24)
    (dir_offset,) = struct.unpack_from("<Q", blob, HEADER_DIR_OFFSET)

    off = dir_offset
    (count,) = struct.unpack_from("<I", blob, off)
    off += 4
    entries: list[PckEntry] = []
    for _ in range(count):
        (path_len,) = struct.unpack_from("<I", blob, off)
        off += 4
        raw = blob[off : off + path_len]
        off += path_len
        entry_offset, size = struct.unpack_from("<QQ", blob, off)
        off += 16
        md5 = blob[off : off + 16].hex()
        off += 16
        (entry_flags,) = struct.unpack_from("<I", blob, off)
        off += 4
        entries.append(
            PckEntry(raw.rstrip(b"\0").decode("utf-8"), entry_offset, size, md5, entry_flags)
        )

    return Pck(
        engine_version=(major, minor, patch),
        format_version=fmt,
        flags=flags,
        file_base=file_base,
        total_bytes=len(blob),
        entries=tuple(entries),
    )
