"""Gate 5 -- deterministic capture / contact-sheet assembly.

A review sheet that is not reproducible is not evidence. If two people build a
sheet from the same captures and get two different files, nobody can say
whether a difference they are looking at came from the art or from the tool.
So the contract here is narrow and testable:

    the same set of input PNGs, in any listing order, on the same machine,
    produces a BYTE-IDENTICAL sheet and a byte-identical manifest.

How that is achieved, and what each choice buys:

  * **Input order is derived, never taken.** Cells are laid out in sorted
    POSIX-path order, so a directory walk's order cannot reach the output.
  * **The PNG is encoded here, not by the imaging library.** Pillow decodes
    and resizes; the final file is written by `_encode_png` below -- IHDR,
    one IDAT, IEND, no ancillary chunks at all. Nothing carries a timestamp,
    a source filename, a gamma guess, or a library version string, which are
    the four usual reasons two "identical" PNGs differ.
  * **The manifest records pixels, not just bytes.** `rgba_sha256` is the hash
    of the uncompressed canvas, so two machines with different zlib builds can
    still prove they composed the same image even if the compressed bytes
    differ. The compressed-byte claim is a same-machine claim and is labelled
    as one.

`tools/art_contact_sheet.py` is a different tool for a different job and is
not touched by this lane: it emits an interactive HTML shortlist page for
choosing art. This one emits a flat PNG grid for CHECKING art, and is the
thing a future capture run would feed.

No live captures are taken here. The assembler takes a directory of PNGs; how
those PNGs got there (a capture harness, an export, a hand-made fixture) is
not this module's business.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

from .findings import Report

GATE = "contact-sheet"

DEFAULT_CELL = 128
DEFAULT_COLUMNS = 4
DEFAULT_PADDING = 8
#: Opaque so a sheet reads the same in every viewer; RGBA so a cell that does
#: not fill its box shows the sheet background rather than an undefined one.
DEFAULT_BACKGROUND = (24, 24, 28, 255)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class Cell:
    index: int
    name: str            # path relative to the input root, POSIX
    source_sha256: str
    width: int           # source pixel size, before fitting
    height: int


@dataclass
class Sheet:
    columns: int
    rows: int
    cell: int
    padding: int
    width: int
    height: int
    cells: list[Cell]
    png: bytes
    rgba_sha256: str

    @property
    def png_sha256(self) -> str:
        return hashlib.sha256(self.png).hexdigest()

    def manifest_text(self) -> str:
        """Deterministic sidecar. Text, sorted, no timestamps, LF endings."""
        lines = [
            "contact_sheet=v1",
            f"columns={self.columns}",
            f"rows={self.rows}",
            f"cell={self.cell}",
            f"padding={self.padding}",
            f"size={self.width}x{self.height}",
            f"rgba_sha256={self.rgba_sha256}",
            f"png_sha256={self.png_sha256}",
        ]
        for cell in self.cells:
            lines.append(
                f"cell={cell.index} {cell.source_sha256} "
                f"{cell.width}x{cell.height} {cell.name}"
            )
        return "\n".join(lines) + "\n"


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + tag
        + payload
        + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
    )


def _encode_png(width: int, height: int, rgba: bytes) -> bytes:
    """8-bit RGBA PNG, filter type 0 on every scanline, no ancillary chunks."""
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgba[y * stride:(y + 1) * stride]
    # level 9 and the default strategy, pinned: zlib's defaults have changed
    # between versions before, and the point of this module is that they
    # cannot change the answer without somebody editing this line.
    compressed = zlib.compress(bytes(raw), 9)
    return (
        PNG_MAGIC
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _chunk(b"IDAT", compressed)
        + _chunk(b"IEND", b"")
    )


def iter_pngs(directory: Path) -> list[Path]:
    """Every *.png under `directory`, sorted by POSIX relative path."""
    return sorted(
        (p for p in directory.rglob("*.png") if p.is_file()),
        key=lambda p: p.relative_to(directory).as_posix(),
    )


def build(
    sources: list[Path],
    input_root: Path,
    columns: int = DEFAULT_COLUMNS,
    cell: int = DEFAULT_CELL,
    padding: int = DEFAULT_PADDING,
    background: tuple[int, int, int, int] = DEFAULT_BACKGROUND,
) -> Sheet:
    """Compose the sheet. `sources` need not be sorted; this sorts them."""
    try:
        from PIL import Image
    except ImportError as exc:                            # pragma: no cover
        raise SystemExit(
            f"contact-sheet assembly needs Pillow to decode and scale PNGs ({exc})."
        ) from None

    ordered = sorted(sources, key=lambda p: p.relative_to(input_root).as_posix())
    columns = max(1, columns)
    rows = max(1, (len(ordered) + columns - 1) // columns) if ordered else 0
    width = padding + columns * (cell + padding)
    height = padding + rows * (cell + padding)

    canvas = Image.new("RGBA", (max(width, 1), max(height, 1)), background)
    cells: list[Cell] = []
    for index, path in enumerate(ordered):
        data = path.read_bytes()
        with Image.open(path) as opened:
            source_size = opened.size
            image = opened.convert("RGBA")
        # LANCZOS by name, not by Image.Resampling default: the default has
        # moved between Pillow majors, and a resampler change silently moves
        # every pixel in the sheet.
        fitted = image.copy()
        fitted.thumbnail((cell, cell), Image.LANCZOS)
        column, row = index % columns, index // columns
        x = padding + column * (cell + padding) + (cell - fitted.width) // 2
        y = padding + row * (cell + padding) + (cell - fitted.height) // 2
        canvas.alpha_composite(fitted, (x, y))
        cells.append(
            Cell(
                index=index,
                name=path.relative_to(input_root).as_posix(),
                source_sha256=hashlib.sha256(data).hexdigest(),
                width=source_size[0],
                height=source_size[1],
            )
        )

    rgba = canvas.tobytes()
    return Sheet(
        columns=columns,
        rows=rows,
        cell=cell,
        padding=padding,
        width=canvas.width,
        height=canvas.height,
        cells=cells,
        png=_encode_png(canvas.width, canvas.height, rgba),
        rgba_sha256=hashlib.sha256(rgba).hexdigest(),
    )


def write(sheet: Sheet, out_png: Path) -> Path:
    """Write the sheet and its manifest. Returns the manifest path."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_png.write_bytes(sheet.png)
    manifest = out_png.with_suffix(out_png.suffix + ".manifest.txt")
    # newline="\n" explicitly: on Windows the default translation would make
    # the manifest differ from a POSIX run for no reason anyone could see.
    manifest.write_text(sheet.manifest_text(), encoding="utf-8", newline="\n")
    return manifest


def run(
    input_dir: Path,
    out_png: Path,
    root: Path,
    columns: int = DEFAULT_COLUMNS,
    cell: int = DEFAULT_CELL,
    padding: int = DEFAULT_PADDING,
) -> Report:
    report = Report(GATE)
    try:
        where = input_dir.relative_to(root).as_posix()
    except ValueError:
        where = input_dir.as_posix()

    if not input_dir.is_dir():
        report.error("SH-NO-INPUT", where, "capture directory does not exist.")
        return report

    sources = iter_pngs(input_dir)
    report.checked["captures"] = len(sources)
    if not sources:
        report.error(
            "SH-EMPTY", where,
            "no PNGs found. A contact sheet of nothing renders as a blank "
            "grid, which reads as 'reviewed'.",
        )
        return report

    usable: list[Path] = []
    for path in sources:
        # Builtin-`open` form: see the note in contract.py::sha256_of.
        with open(path, "rb") as handle:
            magic = handle.read(8)
        if magic != PNG_MAGIC:
            report.error(
                "SH-NOT-PNG", path.relative_to(input_dir).as_posix(),
                "file has a .png name and is not a PNG. build_pck.ps1 already "
                "carries a re-encode block for WebP served as .png "
                "(tools/build_pck.ps1:754-768); this one is excluded from the "
                "sheet rather than silently decoded.",
            )
            continue
        usable.append(path)
    if not usable:
        report.error("SH-NO-USABLE", where,
                     "every candidate was rejected; nothing to assemble.")
        return report

    sheet = build(usable, input_dir, columns=columns, cell=cell, padding=padding)
    manifest = write(sheet, out_png)
    report.checked["cells"] = len(sheet.cells)
    report.note(
        "SH-BUILT", str(out_png),
        f"{sheet.columns}x{sheet.rows} grid, {sheet.width}x{sheet.height}px, "
        f"png_sha256={sheet.png_sha256}, manifest at {manifest.name}",
    )
    return report
