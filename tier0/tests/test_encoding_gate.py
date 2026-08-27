"""The text-encoding gate as a red test ([USER] ratified 2026-07-27).

Every text read/write must declare `encoding=`. The rule and its reasoning
live in tools/lint_text_encoding.py; the short version is that an omitted
encoding resolves to the LOCALE codepage, so the defect appears on Windows
(cp1252) and is invisible on Linux CI (UTF-8). The gate has to be structural
for exactly that reason -- a behavioural check passes on the machine running
it and says nothing about the machine that breaks.

Found the hard way: `loader.py` carried five bare `read_text()` calls, which
decoded `Salon Debut`'s accented `e` to mojibake in memory. The card gallery
rendered it, and re-running the C# codegen on Windows would have shipped it
into the mod's Localization strings. Nothing reached a commit, and no test
could have caught it -- there was no gate, and CI runs the platform that
works.

The content path (tier0/content/, tier05/ pool loaders, both CSV writers) was
fixed at ratification, and the remaining debt -- tools and tests reading
.cs/.tsv/.ps1/.yaml fixtures -- was paid off in full on 2026-08-08. DEBT is
now empty and the tests below hold it there.
"""
from tools import lint_text_encoding as lint

# Spelled out so the probe sources below can be written as concatenated
# lines without an escape sequence inside a comment-bearing expression.
NL = chr(10)

# Undeclared text read/write calls per file. Counts, not line numbers, so
# ordinary edits above an offence do not churn this list -- but a NEW offence
# in an already-listed file still trips the gate, because it pushes the count
# above the recorded one.
#
# An entry here is DEBT. Work it off by adding `encoding="utf-8"` and lowering
# the number; the staleness test below forces that edit, so this list can only
# shrink.
#
# It is empty, and that is the end state, not a starting one. Two clean-ups
# got it here. RECOUNTED 2026-07-29: twenty entries were never offences at all
# -- the `open` arm keyed on the attribute NAME, so every `Image.open(...)`, a
# binary decoder with no `encoding=` parameter to declare, counted as an
# undeclared text read; exempting them dropped four files off the list
# entirely. That miscount was not cosmetic, because the gate compares a
# per-file COUNT: `tools/art_lint.py: 2` was a live allowance for two REAL
# bare `open()` calls to hide behind. PAID 2026-08-08: the surviving 58 calls
# across 14 files all took `encoding="utf-8"`, so the list empties rather than
# zeroing out -- a zero entry is an allowance for the next offence in the
# file, which is why `test_debt_list_is_not_stale` forces deletion instead.
DEBT: dict[str, int] = {}


def test_no_new_undeclared_encodings():
    live = {rel: len(hits) for rel, hits in lint.scan().items()}
    new = []
    for rel, count in sorted(live.items()):
        allowed = DEBT.get(rel, 0)
        if count > allowed:
            detail = ", ".join(f"line {ln} {what}"
                               for ln, what in lint.scan()[rel])
            new.append(f"{rel}: {count} undeclared (allowed {allowed}) "
                       f"-- {detail}")
    assert not new, (
        "text read/write without encoding= (gate RATIFIED 2026-07-27; "
        "an omitted encoding is cp1252 on Windows and UTF-8 on CI, so this "
        "cannot be caught by running the code): " + "; ".join(new))


def test_debt_list_is_not_stale():
    """A file that has been fixed must leave the list, or its entry rots into
    cover for the next real offence in that same file."""
    live = {rel: len(hits) for rel, hits in lint.scan().items()}
    stale = {rel: (recorded, live.get(rel, 0))
             for rel, recorded in DEBT.items()
             if live.get(rel, 0) < recorded}
    assert not stale, (
        "these improved -- lower the DEBT count (recorded, actual): "
        f"{stale}")


def test_the_content_path_carries_no_debt():
    """The loaders are the reason the gate exists: a mojibake card name there
    reaches the sheet, the sim, the gallery and the generated C# at once. They
    are never allowed onto the debt list, however small the entry looks."""
    protected = ("tier0/content/", "tier0/engine/", "tier05/")
    listed = [rel for rel in DEBT if rel.startswith(protected)]
    assert not listed, f"the content path may not carry encoding debt: {listed}"

    live = [rel for rel in lint.scan() if rel.startswith(protected)]
    assert not live, f"undeclared encoding on the content path: {live}"


def test_image_open_is_not_a_text_read(tmp_path):
    """Tooling-hardening sprint 2026-07-29, red demonstration.

    `Image.open` has no `encoding=` parameter and decodes bytes, so flagging it
    produced debt that could only be "paid" by deleting the image pipeline --
    and because the gate compares a per-file COUNT, each phantom entry was a
    live allowance for a REAL bare `open()` to hide behind in that same file.

    The exemption is deliberately narrow and the second half proves it:
    `io.open`, `codecs.open` and `gzip.open` all take `encoding=` and stay in
    scope, so this is not "attribute-form open is exempt".
    """
    probe = tmp_path / "probe.py"
    probe.write_text(
        "from PIL import Image\n"
        "import io, codecs\n"
        "def f(p):\n"
        "    a = Image.open(p).size\n"          # exempt: binary decoder
        "    b = io.open(p).read()\n"           # NOT exempt
        "    c = codecs.open(p).read()\n"       # NOT exempt
        "    d = open(p).read()\n"              # NOT exempt
        "    e = open(p, encoding='utf-8')\n"   # declared
        "    g = open(p, 'rb').read()\n"        # binary mode
        "    return a, b, c, d, e, g\n",
        encoding="utf-8")
    lines = [ln for ln, _ in lint.offences(probe)]
    assert lines == [5, 6, 7], lint.offences(probe)


def test_binary_mode_is_seen_in_both_call_shapes(tmp_path):
    """Fixed 2026-08-27. The mode's position depends on the call shape:
    `open(p, "rb")` and `io.open(p, "rb")` put it at positional index 1, but
    `some_path.open("rb")` puts it at index 0 -- the path is the receiver, not
    an argument. `_is_binary_open` indexed at 1 unconditionally, so every
    bound-method binary read was counted as an undeclared TEXT read: an
    unpayable finding (binary I/O has no encoding), which callers were
    working around by rewriting to the builtin form.

    The mode is now found by SHAPE rather than position, and the second half
    of this probe is what keeps that from over-exempting: a filename literal
    at index 0 is not a mode, even when it contains a 'b'.
    """
    probe = tmp_path / "probe.py"
    probe.write_text(
        "from pathlib import Path" + NL
        + "import io" + NL
        + "def f(p):" + NL
        + "    a = open(p, 'rb').read()" + NL       # exempt: builtin form
        + "    b = io.open(p, 'rb').read()" + NL    # exempt: io form
        + "    c = p.open('rb').read()" + NL        # exempt: bound method
        + "    d = p.open(mode='rb').read()" + NL   # exempt: keyword
        + "    e = p.open('r').read()" + NL         # NOT exempt: text mode
        + "    g = p.open().read()" + NL             # NOT exempt: no mode
        + "    h = open('blob.bin').read()" + NL    # NOT exempt: a FILENAME
        + "    return a, b, c, d, e, g, h" + NL,
        encoding="utf-8")
    lines = [ln for ln, _ in lint.offences(probe)]
    assert lines == [8, 9, 10], lint.offences(probe)


def test_the_exemption_did_not_swallow_the_real_offences_in_those_files():
    """The four files that LEFT the debt list must genuinely have nothing left,
    not merely have gone quiet -- otherwise the recount hid a live defect."""
    live = lint.scan()
    for rel in ("tools/art_lint.py", "tools/gen_furina_stills.py",
                "tools/gen_kokomi_stills.py",
                "tools/archive/autocrop_card_art.py",
                "tools/lint_unique_names.py"):
        assert rel not in live, (live.get(rel), rel)
