#!/usr/bin/env python3
"""Every piece of player-facing text the mod ships, grouped per character.

    python tools/player_text_census.py --out player_text.json
    python tools/player_text_census.py --out x.json --summary   # print counts

WHAT IT READS. The text that SHIPS, not the prose about it: the generated card
classes' `Localization` blocks (with their `CanonicalVars` and `OnUpgrade`
deltas, so "{Damage:diff()}" prints "8 [11]"), every other `Localization`
block in `klee-mod/KleeCode` (relics, potions, powers, characters, modal
options), every `new Dictionary<string, string> { ["key"] = ... }` the mod
merges into a loc table (prompts, tooltips, the Teyvat frame's events,
Ancients and enemy names), the story tables (`Story/*Story.cs`, read as
data), the Spiral Abyss texts (one variant per act), the packaged
`card_keywords.json`, and the Architect's finale lines in
`tools/build_pck.ps1`.

HOW. The C# is read by a small lexer, an expression parser and an evaluator
that knows constants, expression-bodied members, records and switch
expressions. It is not a compiler: an expression it cannot evaluate is
printed as `{?expr}` inside the text and counted under `gaps`, and every
string literal in the tree that looks like player text but that no extractor
consumed is listed under `gaps.unextracted_literals` -- so what this tool
cannot see is itself on the page.

Each item carries `source` as `path:line` (repo-relative) so a reviewer can
find it. Markup ([gold], [blue], [i], [sine] ...) is stripped to plain text;
keyword names stay as words.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import itertools
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CS_ROOT = REPO / "klee-mod" / "KleeCode"
SHEET = REPO / "docs" / "prototype-surface.yaml"
KEYWORD_JSON = (REPO / "klee-mod" / "pck-src" / "klee" / "localization" / "eng"
                / "card_keywords.json")
BUILD_PCK = REPO / "tools" / "build_pck.ps1"
GENERATED_CARDS = CS_ROOT / "Cards" / "Prototype" / "Generated"

CHARACTERS = ("Klee", "Kokomi", "Furina", "Varka", "Yae", "Shared")
CHAR_IDS = {"klee": "Klee", "kokomi": "Kokomi", "furina": "Furina",
            "varka": "Varka", "yae": "Yae"}
#: Card id prefix -> owner. Companion rows are the shared roster.
PREFIX_OWNER = {"proto_ko_": "Klee", "proto_kk_": "Kokomi",
                "proto_fs_": "Furina", "proto_vk_": "Varka",
                "proto_ym_": "Yae", "proto_mc_": "Shared",
                "proto_mf_": "Shared", "proto_mi_": "Shared"}
#: Base-game architect keys -> owner.
ARCHITECT_CHAR = {"KLEEMOD-KLEE": "Klee", "KLEEMOD-KOKOMI": "Kokomi",
                  "KLEEMOD-FURINA": "Furina", "KLEEMOD-VARKA": "Varka",
                  "KLEEMOD-YAE": "Yae"}


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


# ---------------------------------------------------------------------------
# LEXER
# ---------------------------------------------------------------------------

@dataclass
class Tok:
    kind: str            # id num str istr char op eof
    val: Any
    line: int
    pos: int             # char offset in the file
    end: int = 0


_OPS = sorted("""=> == != <= >= && || ?? ?. ++ -- += -= *= /= %= &= |= ^= ??= :: ..
            { } ( ) [ ] ; , . : ? + - * / % ! ~ & | ^ < > = @ #""".split(),
              key=len, reverse=True)
_ID = re.compile(r"@?[A-Za-z_][A-Za-z0-9_]*")
_NUM = re.compile(r"0[xX][0-9a-fA-F_]+[uUlL]*|\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?[mMfFdDuUlL]*"
                  r"|\.\d+[mMfFdD]?")
_ESC = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "\\": "\\", '"': '"',
        "'": "'", "a": "\a", "b": "\b", "f": "\f", "v": "\v"}


class LexError(Exception):
    pass


def _read_escape(src: str, i: int) -> tuple[str, int]:
    """src[i] is the backslash. Returns (char, next index)."""
    c = src[i + 1]
    if c in _ESC:
        return _ESC[c], i + 2
    if c == "u":
        return chr(int(src[i + 2:i + 6], 16)), i + 6
    if c == "x":
        m = re.match(r"[0-9a-fA-F]{1,4}", src[i + 2:])
        return chr(int(m.group(0), 16)), i + 2 + len(m.group(0))
    return c, i + 2


def lex(src: str, line0: int = 1, pos0: int = 0) -> list[Tok]:
    toks: list[Tok] = []
    i, n, line = 0, len(src), line0
    at_line_start = True
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
            at_line_start = True
            continue
        if c in " \t\r\f\v﻿":
            i += 1
            continue
        if c == "#" and at_line_start:            # preprocessor line
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        at_line_start = False
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            line += src.count("\n", i, j)
            i = j
            continue
        start, sline = i, line
        # strings
        interp = verbatim = False
        k = i
        while k < n and src[k] in "$@" and k - i < 2:
            if src[k] == "$":
                interp = True
            else:
                verbatim = True
            k += 1
        if k < n and src[k] == '"' and (interp or verbatim or k == i):
            j = k + 1
            if interp:
                parts: list[Any] = []
                buf: list[str] = []
                while True:
                    if j >= n:
                        raise LexError(f"unterminated string at line {sline}")
                    ch = src[j]
                    if ch == '"':
                        if verbatim and src.startswith('""', j):
                            buf.append('"'); j += 2; continue
                        j += 1
                        break
                    if ch == "\\" and not verbatim:
                        e, j = _read_escape(src, j); buf.append(e); continue
                    if ch == "{":
                        if src.startswith("{{", j):
                            buf.append("{"); j += 2; continue
                        # a hole: find its end at depth 0
                        depth, q = 0, j + 1
                        fmt_at = -1
                        while q < n:
                            cq = src[q]
                            if cq in "([{":
                                depth += 1
                            elif cq in ")]":
                                depth -= 1
                            elif cq == "}":
                                if depth == 0:
                                    break
                                depth -= 1
                            elif cq == '"':
                                # nested string literal inside a hole
                                q += 1
                                while q < n and src[q] != '"':
                                    q += 2 if src[q] == "\\" else 1
                            elif cq == ":" and depth == 0 and fmt_at < 0 \
                                    and not src.startswith("::", q):
                                fmt_at = q
                            elif cq == "?" and depth == 0:
                                pass
                            if cq == "\n":
                                line += 1
                            q += 1
                        if buf:
                            parts.append("".join(buf)); buf = []
                        expr_end = fmt_at if fmt_at >= 0 else q
                        expr_src = src[j + 1:expr_end]
                        fmt = src[fmt_at + 1:q] if fmt_at >= 0 else ""
                        parts.append(("hole", lex(expr_src, sline, pos0 + j + 1),
                                      fmt, expr_src))
                        j = q + 1
                        continue
                    if ch == "}" and src.startswith("}}", j):
                        buf.append("}"); j += 2; continue
                    if ch == "\n":
                        line += 1
                    buf.append(ch); j += 1
                if buf:
                    parts.append("".join(buf))
                toks.append(Tok("istr", parts, sline, pos0 + start, pos0 + j))
            else:
                buf = []
                while True:
                    if j >= n:
                        raise LexError(f"unterminated string at line {sline}")
                    ch = src[j]
                    if ch == '"':
                        if verbatim and src.startswith('""', j):
                            buf.append('"'); j += 2; continue
                        j += 1
                        break
                    if ch == "\\" and not verbatim:
                        e, j = _read_escape(src, j); buf.append(e); continue
                    if ch == "\n":
                        line += 1
                    buf.append(ch); j += 1
                toks.append(Tok("str", "".join(buf), sline, pos0 + start, pos0 + j))
            i = j
            continue
        if c == "'":
            j = i + 1
            if src[j] == "\\":
                ch, j = _read_escape(src, j)
            else:
                ch, j = src[j], j + 1
            if j < n and src[j] == "'":
                toks.append(Tok("char", ch, sline, pos0 + i, pos0 + j + 1))
                i = j + 1
                continue
        m = _ID.match(src, i)
        if m:
            toks.append(Tok("id", m.group(0).lstrip("@"), sline, pos0 + i, pos0 + m.end()))
            i = m.end()
            continue
        m = _NUM.match(src, i)
        if m and (c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit())):
            toks.append(Tok("num", m.group(0), sline, pos0 + i, pos0 + m.end()))
            i = m.end()
            continue
        for op in _OPS:
            if src.startswith(op, i):
                toks.append(Tok("op", op, sline, pos0 + i, pos0 + i + len(op)))
                i += len(op)
                break
        else:
            i += 1          # unknown char: skip
    toks.append(Tok("eof", None, line, pos0 + n, pos0 + n))
    # `global::X` is X
    out = []
    k = 0
    while k < len(toks):
        if toks[k].kind == "id" and toks[k].val == "global" and k + 1 < len(toks)                 and toks[k + 1].kind == "op" and toks[k + 1].val == "::":
            k += 2
            continue
        out.append(toks[k])
        k += 1
    return out


# ---------------------------------------------------------------------------
# PARSER (expressions only; the structure scan is separate)
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass


@dataclass
class N:
    """An expression node. `t` is the node type; `a` its fields."""
    t: str
    a: tuple
    line: int = 0
    pos: int = 0
    end: int = 0


_BINARY = [
    ("??",), ("||",), ("&&",), ("|",), ("^",), ("&",), ("==", "!="),
    ("<", ">", "<=", ">=", "is", "as"), ("+", "-"), ("*", "/", "%"),
]
_ASSIGN = {"=", "+=", "-=", "*=", "/=", "%=", "??=", "&=", "|=", "^="}
_TYPE_KEYWORDS = {"int", "decimal", "string", "bool", "float", "double", "long",
                  "object", "void", "var", "uint", "short", "byte", "char"}


class Parser:
    def __init__(self, toks: list[Tok], i: int = 0):
        self.toks, self.i = toks, i

    # -- helpers
    def peek(self, k: int = 0) -> Tok:
        j = min(self.i + k, len(self.toks) - 1)
        return self.toks[j]

    def at(self, val: str, k: int = 0) -> bool:
        t = self.peek(k)
        return t.kind in ("op", "id") and t.val == val

    def take(self) -> Tok:
        t = self.toks[self.i]
        self.i = min(self.i + 1, len(self.toks) - 1)
        return t

    def expect(self, val: str) -> Tok:
        t = self.take()
        if t.val != val:
            raise ParseError(f"expected {val!r} got {t.val!r} at line {t.line}")
        return t

    def skip_balanced(self) -> int:
        """At an opener; skip to after its closer. Returns the closer index."""
        pairs = {"(": ")", "[": "]", "{": "}", "<": ">"}
        open_ = self.take().val
        close = pairs[open_]
        depth = 1
        while True:
            t = self.take()
            if t.kind == "eof":
                raise ParseError("unbalanced")
            if t.kind == "op":
                if t.val == open_:
                    depth += 1
                elif t.val == close:
                    depth -= 1
                    if depth == 0:
                        return self.i - 1

    def try_type_args(self) -> list[str] | None:
        """At '<': try to read generic type args; restore on failure."""
        save = self.i
        if not self.at("<"):
            return None
        depth, j = 0, self.i
        parts: list[str] = []
        while True:
            t = self.toks[j]
            if t.kind == "eof":
                break
            if t.kind == "op" and t.val == "<":
                depth += 1
            elif t.kind == "op" and t.val == ">":
                depth -= 1
                if depth == 0:
                    nxt = self.toks[j + 1]
                    if nxt.kind == "op" and nxt.val in ("(", ".", ")", ",", ">", ";",
                                                         "{", "?", "[", "=>", "]") \
                            or nxt.kind == "id":
                        self.i = j + 1
                        return [p for p in "".join(parts).split(",") if p]
                    break
            elif t.kind == "id" or (t.kind == "op" and t.val in (".", ",", "?", "[", "]",
                                                                 "(", ")")):
                if depth == 1:
                    parts.append(str(t.val))
            else:
                break
            j += 1
        self.i = save
        return None

    def parse_type(self) -> str:
        """A type name: dotted ids, generic args, ?, [], tuple types."""
        out = []
        if self.at("("):
            s = self.i
            self.skip_balanced()
            out.append("tuple")
        else:
            t = self.take()
            if t.kind != "id":
                raise ParseError(f"type expected at line {t.line}")
            out.append(t.val)
            while True:
                if self.at("."):
                    self.take()
                    out.append(self.take().val)
                elif self.at("<"):
                    ta = self.try_type_args()
                    if ta is None:
                        break
                    out[-1] += "<" + ",".join(ta) + ">"
                else:
                    break
        while self.at("?"):
            self.take()
        while self.at("[") and self.at("]", 1):
            self.take(); self.take()
            out[-1] += "[]"
        return ".".join(out)

    # -- expressions
    def parse_expr(self) -> N:
        lhs = self.parse_ternary()
        if self.peek().kind == "op" and self.peek().val in _ASSIGN:
            op = self.take().val
            rhs = self.parse_expr()
            return N("assign", (op, lhs, rhs), lhs.line, lhs.pos, rhs.end)
        return lhs

    def parse_ternary(self) -> N:
        cond = self.parse_binary(0)
        if self.at("?"):
            self.take()
            a = self.parse_expr()
            self.expect(":")
            b = self.parse_expr()
            return N("ternary", (cond, a, b), cond.line, cond.pos, b.end)
        return cond

    def parse_binary(self, level: int) -> N:
        if level >= len(_BINARY):
            return self.parse_unary()
        lhs = self.parse_binary(level + 1)
        while True:
            t = self.peek()
            if t.kind in ("op", "id") and t.val in _BINARY[level]:
                if t.val in ("<", ">") and level == 7:
                    pass
                op = self.take().val
                if op in ("is", "as"):
                    # pattern / type: consume a type and an optional designation
                    neg = False
                    rhs = None
                    while True:
                        if self.at("not"):
                            self.take(); neg = True
                        if self.peek().kind in ("str", "num", "char") or self.at("null")                                 or self.at("-"):
                            r1 = self.parse_unary()
                        elif self.at("{") or self.at("("):
                            self.skip_balanced()
                            if self.peek().kind == "id" and not self.peek().val in (
                                    "and", "or", "when", "is", "as"):
                                self.take()
                            r1 = N("type", ("pattern",), t.line, t.pos, t.end)
                        elif self.at("<") or self.at(">") or self.at("<=") or self.at(">="):
                            self.take()
                            r1 = self.parse_unary()
                        else:
                            tn = self.parse_type()
                            if self.at("{"):
                                self.skip_balanced()
                            if self.peek().kind == "id" and not self.peek().val in (
                                    "and", "or", "when", "is", "as"):
                                self.take()
                            r1 = N("type", (tn,), t.line, t.pos, t.end)
                        rhs = r1 if rhs is None else N("bin", ("or", rhs, r1), t.line, t.pos, r1.end)
                        if self.at("or") or self.at("and"):
                            self.take()
                            continue
                        break
                    lhs = N("is", (op, lhs, rhs, neg), lhs.line, lhs.pos, rhs.end)
                    continue
                rhs = self.parse_binary(level + 1)
                lhs = N("bin", (op, lhs, rhs), lhs.line, lhs.pos, rhs.end)
            else:
                return lhs

    def parse_unary(self) -> N:
        t = self.peek()
        if t.kind == "op" and t.val in ("!", "-", "+", "~", "++", "--", "&", "*"):
            self.take()
            e = self.parse_unary()
            return N("unary", (t.val, e), t.line, t.pos, e.end)
        if t.kind == "id" and t.val in ("await", "ref", "out", "in", "params") \
                and self.peek(1).kind in ("id", "op", "str", "istr", "num"):
            if not (t.val == "in" and self.peek(1).kind == "op"):
                self.take()
                if self.at("var"):
                    self.take()
                return self.parse_unary()
        if t.kind == "id" and t.val == "throw":
            self.take()
            e = self.parse_expr()
            return N("throw", (e,), t.line, t.pos, e.end)
        # cast: (Type) expr
        if t.kind == "op" and t.val == "(":
            save = self.i
            try:
                self.take()
                tn = self.parse_type()
                if self.at(")"):
                    nxt = self.peek(1)
                    if (nxt.kind in ("id", "num", "str", "istr", "char")
                            and nxt.val not in ("is", "as", "switch", "and", "or",
                                                "with", "when")) \
                            or (nxt.kind == "op" and nxt.val in ("(", "!")) \
                            and (tn in _TYPE_KEYWORDS or tn[:1].isupper()):
                        self.take()
                        e = self.parse_unary()
                        return N("cast", (tn, e), t.line, t.pos, e.end)
            except ParseError:
                pass
            self.i = save
        return self.parse_postfix(self.parse_primary())

    def parse_args(self, close: str) -> list[tuple[str | None, N]]:
        args: list[tuple[str | None, N]] = []
        while not self.at(close):
            name = None
            if self.peek().kind == "id" and self.at(":", 1) and not self.at("::", 1):
                name = self.take().val
                self.take()
            args.append((name, self.parse_expr()))
            if self.at(","):
                self.take()
            elif not self.at(close):
                raise ParseError(f"bad arg list at line {self.peek().line}: {self.peek().val!r}")
        self.take()
        return args

    def parse_postfix(self, e: N) -> N:
        while True:
            t = self.peek()
            if t.kind == "op" and t.val in (".", "?."):
                self.take()
                name = self.take()
                e = N("member", (e, name.val), e.line, e.pos, name.end)
                if self.at("<"):
                    ta = self.try_type_args()
                    if ta is not None:
                        e = N("generic", (e, ta), e.line, e.pos, self.peek(-1).end)
            elif t.kind == "op" and t.val == "(":
                self.take()
                args = self.parse_args(")")
                e = N("call", (e, args), e.line, e.pos, self.peek(-1).end)
            elif t.kind == "op" and t.val == "[":
                self.take()
                args = self.parse_args("]")
                e = N("index", (e, args), e.line, e.pos, self.peek(-1).end)
            elif t.kind == "op" and t.val == "!" and not self.at("=", 1):
                nxt = self.peek(1)
                if nxt.kind == "op" and nxt.val in (".", ")", ",", ";", "?.", "[", "}"):
                    self.take()
                else:
                    return e
            elif t.kind == "op" and t.val in ("++", "--"):
                self.take()
            elif t.kind == "id" and t.val == "switch" and self.at("{", 1):
                self.take()
                self.take()
                arms = []
                while not self.at("}"):
                    ps = self.i
                    depth = 0
                    while True:
                        tt = self.peek()
                        if tt.kind == "eof":
                            raise ParseError("switch")
                        if tt.kind == "op" and tt.val in "([{":
                            depth += 1
                        elif tt.kind == "op" and tt.val in ")]}":
                            depth -= 1
                        elif tt.kind == "op" and tt.val == "=>" and depth == 0:
                            break
                        self.take()
                    pat = [x for x in self.toks[ps:self.i]]
                    self.take()
                    body = self.parse_expr()
                    arms.append((pat, body))
                    if self.at(","):
                        self.take()
                self.take()
                e = N("switch", (e, arms), e.line, e.pos, self.peek(-1).end)
            elif t.kind == "id" and t.val == "with" and self.at("{", 1):
                self.take()
                init = self.parse_init()
                e = N("with", (e, init), e.line, e.pos, self.peek(-1).end)
            else:
                return e

    def parse_init(self) -> list:
        """At '{': an initializer list. Elements: ('kv', key, val),
        ('set', name, val), ('item', expr)."""
        self.expect("{")
        out = []
        while not self.at("}"):
            if self.at("["):
                self.take()
                keys = self.parse_args("]")
                self.expect("=")
                val = self.parse_expr()
                key = keys[0][1] if len(keys) == 1 else N("tuple", (tuple(k for _, k in keys),))
                out.append(("kv", key, val))
            elif self.at("{"):
                s = self.peek()
                items = self.parse_init()
                out.append(("item", N("list", (items,), s.line, s.pos, self.peek(-1).end)))
            else:
                e = self.parse_expr()
                if e.t == "assign" and e.a[0] == "=" and e.a[1].t == "id":
                    out.append(("set", e.a[1].a[0], e.a[2]))
                else:
                    out.append(("item", e))
            if self.at(","):
                self.take()
            elif not self.at("}"):
                raise ParseError(f"bad initializer at line {self.peek().line}: {self.peek().val!r}")
        self.take()
        return out

    def parse_lambda_body(self, t: Tok, params: list[str]) -> N:
        if self.at("{"):
            s = self.i
            self.skip_balanced()
            return N("lambda", (params, None), t.line, t.pos, self.peek(-1).end)
        body = self.parse_expr()
        return N("lambda", (params, body), t.line, t.pos, body.end)

    def parse_primary(self) -> N:
        t = self.peek()
        if t.kind == "str":
            self.take()
            return N("str", (t.val,), t.line, t.pos, t.end)
        if t.kind == "istr":
            self.take()
            parts = []
            for p in t.val:
                if isinstance(p, str):
                    parts.append(p)
                else:
                    _, toks, fmt, srctext = p
                    try:
                        sub = Parser(toks)
                        e = sub.parse_expr()
                    except (ParseError, IndexError):
                        e = N("raw", (srctext,), t.line, t.pos, t.end)
                    parts.append((e, fmt, srctext))
            return N("istr", (parts,), t.line, t.pos, t.end)
        if t.kind == "num":
            self.take()
            s = t.val.replace("_", "").rstrip("mMfFdDuUlL")
            if s.lower().startswith("0x"):
                v: Any = int(s, 16)
            elif any(ch in s for ch in ".eE"):
                v = float(s)
            else:
                v = int(s)
            return N("num", (v,), t.line, t.pos, t.end)
        if t.kind == "char":
            self.take()
            return N("str", (t.val,), t.line, t.pos, t.end)
        if t.kind == "op" and t.val == "(":
            # lambda (a, b) => ... ?
            save = self.i
            try:
                self.skip_balanced()
                if self.at("=>"):
                    inner = self.toks[save + 1:self.i - 1]
                    params = [x.val for x in inner if x.kind == "id"]
                    self.take()
                    return self.parse_lambda_body(t, params)
            except ParseError:
                pass
            self.i = save
            self.take()
            if self.peek().kind == "id" and self.at(":", 1):
                self.take(); self.take()
            first = self.parse_expr()
            if self.at(","):
                items = [first]
                while self.at(","):
                    self.take()
                    if self.peek().kind == "id" and self.at(":", 1):
                        self.take(); self.take()
                    items.append(self.parse_expr())
                self.expect(")")
                return N("tuple", (tuple(items),), t.line, t.pos, self.peek(-1).end)
            self.expect(")")
            return first
        if t.kind == "op" and t.val == "[":          # collection expression
            self.take()
            items = self.parse_args("]")
            return N("list", ([("item", e) for _, e in items],), t.line, t.pos,
                     self.peek(-1).end)
        if t.kind == "op" and t.val == "{":
            items = self.parse_init()
            return N("list", (items,), t.line, t.pos, self.peek(-1).end)
        if t.kind == "id":
            v = t.val
            if v in ("static", "async") and (self.peek(1).kind == "id" or self.at("(", 1)):
                self.take()
                return self.parse_primary()
            if v == "new":
                return self.parse_new()
            if v in ("typeof", "nameof", "default", "sizeof", "checked", "unchecked") \
                    and self.at("(", 1):
                self.take()
                s = self.i
                self.skip_balanced()
                inner = self.toks[s + 1:self.i - 1]
                text = "".join(str(x.val) for x in inner)
                if v in ("checked", "unchecked"):
                    sub = Parser(inner + [Tok("eof", None, t.line, t.pos)])
                    return sub.parse_expr()
                return N(v, (text,), t.line, t.pos, self.peek(-1).end)
            if v in ("true", "false"):
                self.take()
                return N("lit", (v == "true",), t.line, t.pos, t.end)
            if v == "null" or v == "default":
                self.take()
                return N("lit", (None,), t.line, t.pos, t.end)
            if self.at("=>", 1):                      # x => ...
                self.take(); self.take()
                return self.parse_lambda_body(t, [v])
            self.take()
            e = N("id", (v,), t.line, t.pos, t.end)
            if self.at("<"):
                ta = self.try_type_args()
                if ta is not None:
                    e = N("generic", (e, ta), t.line, t.pos, self.peek(-1).end)
            return e
        raise ParseError(f"unexpected {t.val!r} at line {t.line}")

    def parse_new(self) -> N:
        t = self.take()
        tn = None
        if self.at("["):                                   # new[] { ... }
            self.skip_balanced()
            tn = "[]"
        elif not self.at("(") and not self.at("{"):
            tn = self.parse_type()
            if self.at("[") and not self.at("]", 1):      # new T[n]
                self.skip_balanced()
                tn += "[]"
        args: list = []
        init = None
        if self.at("("):
            self.take()
            args = self.parse_args(")")
        if self.at("{"):
            init = self.parse_init()
        return N("new", (tn, args, init), t.line, t.pos, self.peek(-1).end)


def parse_expr_at(toks: list[Tok], i: int) -> tuple[N, int]:
    p = Parser(toks, i)
    e = p.parse_expr()
    return e, p.i


# ---------------------------------------------------------------------------
# STRUCTURE SCAN: classes, members
# ---------------------------------------------------------------------------

@dataclass
class Member:
    name: str
    kind: str                    # field prop method
    expr: N | None               # expression body / initializer
    params: list[str]
    line: int
    file: "CsFile"
    cls: "ClassInfo"
    body_span: tuple[int, int] | None = None     # char offsets of a block body
    modifiers: tuple = ()
    type: str = ""


@dataclass
class ClassInfo:
    name: str
    kind: str
    bases: list[str]
    file: "CsFile"
    line: int
    outer: "ClassInfo | None"
    members: dict[str, list[Member]] = field(default_factory=dict)
    record_params: list[tuple[str, N | None]] = field(default_factory=list)
    enum_members: list[str] = field(default_factory=list)
    namespace: str = ""
    span: tuple[int, int] = (0, 0)

    def full(self) -> str:
        return (self.outer.full() + "." if self.outer else "") + self.name


@dataclass
class CsFile:
    path: Path
    src: str
    toks: list[Tok]
    classes: list[ClassInfo] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def line_of(self, pos: int) -> int:
        return self.src.count("\n", 0, pos) + 1


_MODIFIERS = {"public", "private", "protected", "internal", "static", "readonly",
              "const", "override", "virtual", "abstract", "sealed", "new", "async",
              "extern", "unsafe", "volatile", "partial", "required", "file"}


def scan_file(path: Path) -> CsFile:
    src = path.read_text(encoding="utf-8-sig", errors="replace")
    f = CsFile(path, src, lex(src))
    toks = f.toks
    i = 0
    stack: list[tuple[str, ClassInfo | None]] = []   # ('class', ci) | ('block', None)
    namespace = ""

    def cur_class() -> ClassInfo | None:
        if stack and stack[-1][0] == "class":
            return stack[-1][1]
        return None

    while toks[i].kind != "eof":
        t = toks[i]
        if t.kind == "id" and t.val == "namespace":
            j = i + 1
            parts = []
            while toks[j].kind == "id" or (toks[j].kind == "op" and toks[j].val == "."):
                parts.append(toks[j].val); j += 1
            namespace = "".join(parts)
            if toks[j].kind == "op" and toks[j].val == ";":
                i = j + 1
                continue
            if toks[j].kind == "op" and toks[j].val == "{":
                stack.append(("ns", None))
                i = j + 1
                continue
            i = j
            continue
        if t.kind == "id" and t.val in ("class", "struct", "record", "interface", "enum") \
                and toks[i + 1].kind == "id" and (cur_class() is not None
                                                 or not stack or stack[-1][0] == "ns"):
            kind = t.val
            j = i + 1
            if kind == "record" and toks[j].val in ("struct", "class"):
                j += 1
            name = toks[j].val
            j += 1
            ci = ClassInfo(name, kind, [], f, t.line, cur_class(), namespace=namespace)
            # generic params
            if toks[j].kind == "op" and toks[j].val == "<":
                p = Parser(toks, j)
                p.skip_balanced()
                j = p.i
            if toks[j].kind == "op" and toks[j].val == "(":   # record primary ctor
                p = Parser(toks, j + 1)
                try:
                    while not p.at(")"):
                        # attributes
                        while p.at("["):
                            p.skip_balanced()
                        tn = p.parse_type()
                        pname = p.take().val
                        dflt = None
                        if p.at("="):
                            p.take()
                            dflt = p.parse_expr()
                        ci.record_params.append((pname, dflt))
                        if p.at(","):
                            p.take()
                    j = p.i + 1
                except ParseError as exc:
                    f.errors.append(f"{rel(path)}:{t.line}: record params: {exc}")
                    p2 = Parser(toks, j)
                    p2.skip_balanced()
                    j = p2.i
            if toks[j].kind == "op" and toks[j].val == ":":
                j += 1
                p = Parser(toks, j)
                while True:
                    try:
                        ci.bases.append(p.parse_type().split("<")[0].split(".")[-1])
                    except ParseError:
                        break
                    if p.at("("):
                        p.skip_balanced()
                    if p.at(","):
                        p.take()
                        continue
                    break
                j = p.i
            while not (toks[j].kind == "op" and toks[j].val in ("{", ";")) \
                    and toks[j].kind != "eof":
                j += 1
            f.classes.append(ci)
            if toks[j].val == "{":
                if kind == "enum":
                    p = Parser(toks, j)
                    k = p.skip_balanced()
                    inner = toks[j + 1:k]
                    expect_name = True
                    depth = 0
                    for tt in inner:
                        if tt.kind == "op" and tt.val in "([{":
                            depth += 1
                        elif tt.kind == "op" and tt.val in ")]}":
                            depth -= 1
                        elif tt.kind == "op" and tt.val == "," and depth == 0:
                            expect_name = True
                        elif tt.kind == "op" and tt.val == "[":
                            pass
                        elif tt.kind == "id" and expect_name and depth == 0:
                            ci.enum_members.append(tt.val)
                            expect_name = False
                    i = k + 1
                    continue
                ci.span = (toks[j].pos, len(src))
                stack.append(("class", ci))
                i = j + 1
            else:
                i = j + 1
            continue
        if t.kind == "op" and t.val == "}":
            if stack:
                kind_, ci_ = stack.pop()
                if kind_ == "class" and ci_ is not None:
                    ci_.span = (ci_.span[0], t.end)
            i += 1
            continue
        if t.kind == "op" and t.val == "{":
            # a block at class level we did not recognize: skip balanced
            p = Parser(toks, i)
            try:
                i = p.skip_balanced() + 1
            except ParseError:
                i += 1
            continue
        ci = cur_class()
        if ci is not None and t.kind == "op" and t.val == "[":
            # attribute
            p = Parser(toks, i)
            try:
                i = p.skip_balanced() + 1
            except ParseError:
                i += 1
            continue
        if ci is not None and t.kind == "id":
            i = scan_member(f, ci, i)
            continue
        i += 1
    return f


def scan_member(f: CsFile, ci: ClassInfo, i: int) -> int:
    """At the first token of a class member. Records it; returns the index
    after it."""
    toks = f.toks
    start = i
    mods = []
    while toks[i].kind == "id" and toks[i].val in _MODIFIERS:
        mods.append(toks[i].val)
        i += 1
    t = toks[i]
    if t.kind == "id" and t.val in ("class", "struct", "record", "interface", "enum"):
        return i                          # nested type: let the outer loop handle it
    if t.kind == "id" and t.val in ("using", "delegate", "event"):
        while not (toks[i].kind == "op" and toks[i].val == ";") and toks[i].kind != "eof":
            i += 1
        return i + 1
    p = Parser(toks, i)
    # constructor / operator / destructor
    try:
        if toks[i].kind == "id" and toks[i].val == ci.name and toks[i + 1].val == "(":
            p.i = i + 1
            p.skip_balanced()
            if p.at(":"):
                p.take()
                p.take()
                p.skip_balanced()
            if p.at("{"):
                p.skip_balanced()
            elif p.at("=>"):
                p.take()
                p.parse_expr()
                p.expect(";")
            elif p.at(";"):
                p.take()
            return p.i
        if toks[i].kind == "op" and toks[i].val == "~":
            p.i = i + 2
            p.skip_balanced()
            p.skip_balanced()
            return p.i
        mtype = p.parse_type()
        if p.at("operator") or (p.peek().kind == "id" and p.peek().val in ("implicit", "explicit")):
            while not p.at("(") and p.peek().kind != "eof":
                p.take()
            p.skip_balanced()
            if p.at("=>"):
                p.take(); p.parse_expr(); p.expect(";")
            else:
                p.skip_balanced()
            return p.i
        name_t = p.take()
        if name_t.kind != "id":
            raise ParseError(f"member name expected got {name_t.val!r}")
        name = name_t.val
        # explicit interface: IFoo.Bar
        while p.at("."):
            p.take()
            name = p.take().val
        if name == "this" and p.at("["):          # indexer
            p.skip_balanced()
        if p.at("<"):
            p.try_type_args() or p.skip_balanced()
        if p.at("("):                             # method
            s = p.i
            p.skip_balanced()
            ptoks = toks[s + 1:p.i - 1]
            params = _param_names(ptoks)
            while p.peek().kind == "id" and p.peek().val == "where":
                while not (p.at("{") or p.at("=>") or p.at(";")):
                    p.take()
            if p.at("=>"):
                p.take()
                e = p.parse_expr()
                p.expect(";")
                _add(ci, Member(name, "method", e, params, name_t.line, f, ci, modifiers=tuple(mods), type=mtype))
            elif p.at("{"):
                b0 = p.peek().pos
                p.skip_balanced()
                _add(ci, Member(name, "method", None, params, name_t.line, f, ci,
                                (b0, p.peek(-1).end), tuple(mods)))
            else:
                p.expect(";")
            return p.i
        if p.at("=>"):                            # expression-bodied property
            p.take()
            e = p.parse_expr()
            p.expect(";")
            _add(ci, Member(name, "prop", e, [], name_t.line, f, ci, modifiers=tuple(mods), type=mtype))
            return p.i
        if p.at("{"):                             # property with accessors
            b0 = p.peek().pos
            s = p.i
            p.skip_balanced()
            inner = toks[s + 1:p.i - 1]
            getter = None
            # `get => expr;` inside
            for k, tt in enumerate(inner):
                if tt.kind == "id" and tt.val == "get" and k + 1 < len(inner) \
                        and inner[k + 1].val == "=>":
                    sub = Parser(inner + [Tok("eof", None, 0, 0)], k + 2)
                    try:
                        getter = sub.parse_expr()
                    except ParseError:
                        pass
                    break
            init = None
            if p.at("="):
                p.take()
                init = p.parse_expr()
                p.expect(";")
            _add(ci, Member(name, "prop", init or getter, [], name_t.line, f, ci,
                            (b0, p.peek(-1).end), tuple(mods), mtype))
            return p.i
        # field(s)
        while True:
            init = None
            if p.at("="):
                p.take()
                init = p.parse_expr()
            _add(ci, Member(name, "field", init, [], name_t.line, f, ci, modifiers=tuple(mods), type=mtype))
            if p.at(","):
                p.take()
                nt = p.take()
                name = nt.val
                continue
            break
        p.expect(";")
        return p.i
    except (ParseError, IndexError) as exc:
        f.errors.append(f"{rel(f.path)}:{toks[start].line}: member: {exc}")
        # resync: skip to the next ';' or balanced block at this depth
        j = start
        depth = 0
        while toks[j].kind != "eof":
            tt = toks[j]
            if tt.kind == "op" and tt.val in "({[":
                depth += 1
            elif tt.kind == "op" and tt.val in ")}]":
                if depth == 0:
                    return j
                depth -= 1
                if depth == 0 and tt.val == "}":
                    nxt = toks[j + 1]
                    if not (nxt.kind == "op" and nxt.val in (";", ",", ")", "=")):
                        return j + 1
            elif tt.kind == "op" and tt.val == ";" and depth == 0:
                return j + 1
            j += 1
        return j


def _param_names(ptoks: list[Tok]) -> list[str]:
    names, depth, last_id = [], 0, None
    seen_eq = False
    for tt in ptoks + [Tok("op", ",", 0, 0)]:
        if tt.kind == "op" and tt.val in "(<[":
            depth += 1
        elif tt.kind == "op" and tt.val in ")>]":
            depth -= 1
        elif tt.kind == "op" and tt.val == "=" and depth == 0:
            seen_eq = True
        elif tt.kind == "op" and tt.val == "," and depth == 0:
            if last_id:
                names.append(last_id)
            last_id, seen_eq = None, False
        elif tt.kind == "id" and depth == 0 and not seen_eq:
            last_id = tt.val
    return names


def _add(ci: ClassInfo, m: Member) -> None:
    ci.members.setdefault(m.name, []).append(m)


# ---------------------------------------------------------------------------
# EVALUATOR
# ---------------------------------------------------------------------------

class U:
    """An unresolved value; carries the source text."""
    def __init__(self, text: str):
        self.text = " ".join(text.split())

    def __str__(self) -> str:
        return "{?" + self.text + "}"


@dataclass
class ClassRef:
    ci: ClassInfo


@dataclass
class EnumVal:
    enum: str
    name: str


@dataclass
class Obj:
    type: str
    args: list            # positional values (evaluated lazily as nodes)
    named: dict
    fields: dict          # initializer sets (nodes)
    env: dict
    node: N
    file: CsFile
    cls_ctx: ClassInfo | None


@dataclass
class TypeRef:
    name: str
    targs: list


class Index:
    def __init__(self, files: list[CsFile]):
        self.files = files
        self.by_name: dict[str, list[ClassInfo]] = {}
        for f in files:
            for ci in f.classes:
                self.by_name.setdefault(ci.name, []).append(ci)
        self.depth = 0
        self.unresolved: list[str] = []
        #: (file path, char pos) of every string literal an extractor read
        self.consumed: set[tuple[Path, int]] = set()
        #: the concrete class whose members are being read (virtual dispatch)
        self.dyn: ClassInfo | None = None

    # -- lookup
    def classes(self, name: str) -> list[ClassInfo]:
        return self.by_name.get(name, [])

    def base_chain(self, ci: ClassInfo, seen=None) -> list[ClassInfo]:
        seen = seen or set()
        out = [ci]
        for b in ci.bases:
            for bc in self.classes(b):
                if id(bc) not in seen:
                    seen.add(id(bc))
                    out.extend(self.base_chain(bc, seen))
        return out

    def base_names(self, ci: ClassInfo) -> set[str]:
        names: set[str] = set()
        for c in self.base_chain(ci):
            names.add(c.name)
            names.update(c.bases)
        return names

    def find_member(self, ci: ClassInfo, name: str) -> Member | None:
        for c in self.base_chain(ci):
            ms = c.members.get(name)
            if ms:
                return ms[0]
        return None

    def lookup_bare(self, name: str, ctx: ClassInfo | None) -> Any:
        dyn = self.dyn
        if dyn is not None and ctx is not None and dyn is not ctx                 and any(c is ctx for c in self.base_chain(dyn)):
            m = self.find_member(dyn, name)
            if m is not None:
                return m
        c = ctx
        while c is not None:
            m = self.find_member(c, name)
            if m is not None:
                return m
            for nested in self.classes(name):
                if nested.outer is c:
                    return ClassRef(nested)
            c = c.outer
        cands = self.classes(name)
        if cands:
            # prefer same file
            if ctx is not None:
                for cc in cands:
                    if cc.file is ctx.file:
                        return ClassRef(cc)
            return ClassRef(cands[0])
        return None

    # -- eval
    def ev(self, n: N | None, env: dict | None = None, ctx: ClassInfo | None = None,
           this: Obj | None = None) -> Any:
        if n is None:
            return None
        env = env or {}
        self.depth += 1
        try:
            if self.depth > 60:
                return U("<recursion>")
            return self._ev(n, env, ctx, this)
        except RecursionError:
            return U("<recursion>")
        finally:
            self.depth -= 1

    def src_of(self, n: N, ctx: ClassInfo | None) -> str:
        if ctx is not None and n.end > n.pos:
            return ctx.file.src[n.pos:n.end]
        return n.t

    def _member_value(self, m: Member, this: Obj | None = None) -> Any:
        if m.expr is None:
            return U(m.name)
        v = self.ev(m.expr, {}, m.cls, this)
        if isinstance(v, Obj) and v.type == "?":
            v.type = m.type.split("<")[0].split(".")[-1].rstrip("?")
        return v

    def _resolve_ref(self, v: Any, ctx) -> Any:
        if isinstance(v, Member):
            if v.kind == "method":
                return ("method", v)
            return self._member_value(v)
        return v

    def _ev(self, n: N, env: dict, ctx, this) -> Any:
        t = n.t
        if t in ("str", "istr") and ctx is not None:
            self.consumed.add((ctx.file.path, n.pos))
        if t == "str":
            return n.a[0]
        if t == "num":
            return n.a[0]
        if t == "lit":
            return n.a[0]
        if t == "raw":
            return U(n.a[0])
        if t == "istr":
            out = []
            for p in n.a[0]:
                if isinstance(p, str):
                    out.append(p)
                else:
                    e, fmt, srctext = p
                    v = self.ev(e, env, ctx, this)
                    out.append(fmt_value(v, fmt) if not isinstance(v, U) else str(U(srctext)))
            return "".join(out)
        if t == "id":
            name = n.a[0]
            if name in env:
                return env[name]
            if this is not None:
                v = self.obj_member(this, name)
                if v is not None:
                    return v
            if name == "this":
                return this if this is not None else U("this")
            if name in ("string", "int", "decimal", "Math", "Array", "String"):
                return TypeRef(name, [])
            v = self.lookup_bare(name, ctx)
            if v is None:
                return U(name)
            return self._resolve_ref(v, ctx)
        if t == "member":
            obj_n, name = n.a
            obj = self.ev(obj_n, env, ctx, this)
            return self.member_of(obj, name, n, ctx)
        if t == "generic":
            base = self.ev(n.a[0], env, ctx, this)
            if isinstance(base, tuple) and base and base[0] == "method":
                return ("gmethod", base[1], n.a[1])
            if isinstance(base, U):
                return ("gcall", base.text, n.a[1])
            if isinstance(base, ClassRef):
                return ClassRef(base.ci)
            return ("gcall", self.src_of(n.a[0], ctx), n.a[1])
        if t == "call":
            return self.call(n, env, ctx, this)
        if t == "index":
            obj = self.ev(n.a[0], env, ctx, this)
            args = [self.ev(a, env, ctx, this) for _, a in n.a[1]]
            if isinstance(obj, (list, tuple)) and args and isinstance(args[0], int):
                try:
                    return obj[args[0]]
                except IndexError:
                    return U(self.src_of(n, ctx))
            if isinstance(obj, dict) and args and not isinstance(args[0], U):
                k = args[0]
                if k in obj:
                    return obj[k]
            return U(self.src_of(n, ctx))
        if t == "bin":
            op, l, r = n.a
            lv = self.ev(l, env, ctx, this)
            rv = self.ev(r, env, ctx, this)
            return binop(op, lv, rv, self.src_of(n, ctx))
        if t == "unary":
            op, e = n.a
            v = self.ev(e, env, ctx, this)
            if op == "-" and isinstance(v, (int, float)) and not isinstance(v, bool):
                return -v
            if op == "!" and isinstance(v, bool):
                return not v
            if op == "+":
                return v
            return U(self.src_of(n, ctx))
        if t == "cast":
            tn, e = n.a
            v = self.ev(e, env, ctx, this)
            if tn == "int" and isinstance(v, (int, float)):
                return int(v)
            if tn in ("decimal", "double", "float") and isinstance(v, (int, float)):
                return v
            return v
        if t == "ternary":
            c = self.ev(n.a[0], env, ctx, this)
            if isinstance(c, bool):
                return self.ev(n.a[1] if c else n.a[2], env, ctx, this)
            return U(self.src_of(n, ctx))
        if t == "tuple":
            return tuple(self.ev(x, env, ctx, this) for x in n.a[0])
        if t == "list":
            return self.ev_init_list(n.a[0], env, ctx, this)
        if t == "new":
            tn, args, init = n.a
            if tn and (tn.startswith("Dictionary") or tn.startswith("SortedDictionary")):
                d = {}
                for el in init or []:
                    if el[0] == "kv":
                        d[_hashable(self.ev(el[1], env, ctx, this))] = self.ev(el[2], env, ctx, this)
                    elif el[0] == "item" and el[1].t == "list":
                        kv = self.ev(el[1], env, ctx, this)
                        if len(kv) == 2:
                            d[_hashable(kv[0])] = kv[1]
                # copy-constructor of another dictionary
                for _, a in args:
                    v = self.ev(a, env, ctx, this)
                    if isinstance(v, dict):
                        d = {**v, **d}
                return d
            if tn is None and (args or any(el[0] == "set" for el in (init or []))):
                tn = "?"
            if tn is None or tn == "[]" or tn.endswith("[]") or tn.startswith(("List", "HashSet", "IEnumerable")):
                if init is None:
                    return []
                return self.ev_init_list(init, env, ctx, this)
            short = tn.split("<")[0].split(".")[-1]
            return Obj(short, [a for nm, a in args if nm is None],
                       {nm: a for nm, a in args if nm is not None},
                       {el[1]: el[2] for el in (init or []) if el[0] == "set"},
                       env, n, ctx.file if ctx else None, ctx)
        if t == "switch":
            subj = self.ev(n.a[0], env, ctx, this)
            for pat, body in n.a[1]:
                if pattern_matches(pat, subj):
                    return self.ev(body, env, ctx, this)
            return U(self.src_of(n, ctx))
        if t == "typeof":
            return TypeRef(n.a[0].split("<")[0].split(".")[-1], [])
        if t == "nameof":
            return n.a[0].split(".")[-1]
        if t in ("lambda",):
            return ("lambda", n, env, ctx, this)
        if t == "throw":
            return U("throw")
        if t == "assign":
            if n.a[0] == "??=":
                return self.ev(n.a[2], env, ctx, this)
            return U(self.src_of(n, ctx))
        return U(self.src_of(n, ctx))

    def ev_init_list(self, items, env, ctx, this) -> list:
        out = []
        for el in items:
            if el[0] == "item":
                out.append(self.ev(el[1], env, ctx, this))
            elif el[0] == "kv":
                out.append((self.ev(el[1], env, ctx, this), self.ev(el[2], env, ctx, this)))
            else:
                out.append((el[1], self.ev(el[2], env, ctx, this)))
        return out

    def obj_member(self, o: Obj, name: str) -> Any:
        if name in o.fields:
            return self.ev(o.fields[name], o.env, o.cls_ctx)
        if name in o.named:
            return self.ev(o.named[name], o.env, o.cls_ctx)
        for ci in self.classes(o.type):
            for k, (pname, dflt) in enumerate(ci.record_params):
                if pname == name:
                    if k < len(o.args):
                        return self.ev(o.args[k], o.env, o.cls_ctx)
                    return self.ev(dflt, {}, ci) if dflt is not None else None
            m = self.find_member(ci, name)
            if m is not None and m.kind != "method":
                if m.expr is None:
                    return None
                return self.ev(m.expr, {}, ci, o)
        return None

    def member_of(self, obj: Any, name: str, n: N, ctx) -> Any:
        if isinstance(obj, ClassRef):
            m = self.find_member(obj.ci, name)
            if m is not None:
                return ("method", m) if m.kind == "method" else self._member_value(m)
            if name in obj.ci.enum_members:
                return EnumVal(obj.ci.name, name)
            for nested in self.classes(name):
                if nested.outer is obj.ci:
                    return ClassRef(nested)
            # enum declared in a class with the same name elsewhere
            for ci in self.classes(obj.ci.name):
                if name in ci.enum_members:
                    return EnumVal(ci.name, name)
                m = self.find_member(ci, name)
                if m is not None:
                    return ("method", m) if m.kind == "method" else self._member_value(m)
            return U(self.src_of(n, ctx))
        if isinstance(obj, U):
            # namespace prefix: Powers.SlyGrant -> SlyGrant
            cands = self.classes(name)
            if cands:
                return ClassRef(cands[0])
            return U(obj.text + "." + name)
        if isinstance(obj, Obj):
            v = self.obj_member(obj, name)
            return v if v is not None else U(self.src_of(n, ctx))
        if isinstance(obj, (list, tuple)) and name in ("Count", "Length"):
            return len(obj)
        if isinstance(obj, str) and name == "Length":
            return len(obj)
        if isinstance(obj, TypeRef):
            if obj.name in ("string", "String") and name == "Empty":
                return ""
            return ("builtin", obj.name + "." + name)
        if isinstance(obj, (int, float, str, EnumVal)):
            return ("boundmethod", obj, name)
        return U(self.src_of(n, ctx))

    def call(self, n: N, env, ctx, this) -> Any:
        fn_n, args = n.a
        # method chains on vars (`.WithMultiplier(...)`): keep the receiver
        if fn_n.t == "member" and fn_n.a[1].startswith("With"):
            recv = self.ev(fn_n.a[0], env, ctx, this)
            if isinstance(recv, Obj):
                return recv
        fn = self.ev(fn_n, env, ctx, this)
        argv = [self.ev(a, env, ctx, this) for _, a in args]
        if isinstance(fn, tuple) and fn and fn[0] in ("method", "gmethod"):
            m: Member = fn[1]
            if m.expr is None:
                return U(self.src_of(n, ctx))
            benv = {}
            for k, pname in enumerate(m.params):
                if k < len(argv):
                    benv[pname] = argv[k]
            return self.ev(m.expr, benv, m.cls, this)
        if isinstance(fn, tuple) and fn and fn[0] == "builtin":
            name = fn[1]
            nums = [a for a in argv if isinstance(a, (int, float)) and not isinstance(a, bool)]
            if name == "Math.Clamp" and len(nums) == 3:
                return max(nums[1], min(nums[2], nums[0]))
            if name == "Math.Max" and len(nums) == 2:
                return max(nums)
            if name == "Math.Min" and len(nums) == 2:
                return min(nums)
            if name in ("string.Join", "String.Join") and len(argv) == 2 \
                    and isinstance(argv[1], (list, tuple)) and isinstance(argv[0], str):
                return argv[0].join(str(x) for x in argv[1])
            if name in ("string.Concat", "String.Concat"):
                return "".join(str(x) for x in argv)
            return U(self.src_of(n, ctx))
        if isinstance(fn, tuple) and fn and fn[0] == "boundmethod":
            recv, name = fn[1], fn[2]
            if name == "ToString":
                return fmt_value(recv, argv[0] if argv and isinstance(argv[0], str) else "")
            if isinstance(recv, str):
                if name == "ToUpperInvariant" or name == "ToUpper":
                    return recv.upper()
                if name == "ToLowerInvariant" or name == "ToLower":
                    return recv.lower()
                if name == "Replace" and len(argv) == 2 and all(isinstance(a, str) for a in argv):
                    return recv.replace(argv[0], argv[1])
                if name == "Trim":
                    return recv.strip()
            return U(self.src_of(n, ctx))
        if isinstance(fn, tuple) and fn and fn[0] == "gcall":
            return ("gref", fn[1], fn[2])
        if isinstance(fn, tuple) and fn and fn[0] == "lambda":
            _, ln, lenv, lctx, lthis = fn
            params, body = ln.a
            if body is None:
                return U(self.src_of(n, ctx))
            benv = dict(lenv)
            for k, pname in enumerate(params):
                if k < len(argv):
                    benv[pname] = argv[k]
            return self.ev(body, benv, lctx, lthis)
        return U(self.src_of(n, ctx))


def _hashable(v: Any) -> Any:
    if isinstance(v, list):
        return tuple(_hashable(x) for x in v)
    if isinstance(v, (Obj, U)):
        return str(v) if isinstance(v, U) else id(v)
    if isinstance(v, EnumVal):
        return f"{v.enum}.{v.name}"
    return v


def pattern_matches(pat: list[Tok], subj: Any) -> bool:
    if len(pat) == 1 and pat[0].kind == "id" and pat[0].val == "_":
        return True
    alts, cur = [], []
    for tk in pat:
        if tk.kind == "id" and tk.val == "or":
            alts.append(cur); cur = []
        else:
            cur.append(tk)
    alts.append(cur)
    for alt in alts:
        if not alt:
            continue
        if isinstance(subj, EnumVal):
            names = [t.val for t in alt if t.kind == "id"]
            if names and names[-1] == subj.name and (len(names) == 1 or names[-2] == subj.enum):
                return True
        elif isinstance(subj, bool):
            if len(alt) == 1 and alt[0].kind == "id" and alt[0].val == str(subj).lower():
                return True
        elif isinstance(subj, (int, float)):
            if len(alt) == 1 and alt[0].kind == "num":
                try:
                    if float(alt[0].val.rstrip("mMfFdD")) == float(subj):
                        return True
                except ValueError:
                    pass
        elif isinstance(subj, str):
            if len(alt) == 1 and alt[0].kind == "str" and alt[0].val == subj:
                return True
    return False


def fmt_num(v: Any) -> str:
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return f"{v:g}"
    return str(v)


def fmt_value(v: Any, fmt: str = "") -> str:
    if isinstance(v, U):
        return str(v)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if fmt.startswith(("0.", "#.", "F", "N")) and isinstance(v, float):
            return f"{v:g}"
        return fmt_num(v)
    if isinstance(v, EnumVal):
        return v.name
    if isinstance(v, TypeRef):
        return v.name
    if v is None:
        return ""
    if isinstance(v, (Obj, tuple, list, dict)):
        return "{?" + type(v).__name__ + "}"
    return str(v)


def binop(op: str, a: Any, b: Any, src: str) -> Any:
    if op == "+":
        if isinstance(a, str) or isinstance(b, str):
            return fmt_value(a) + fmt_value(b)
        if isinstance(a, U) or isinstance(b, U):
            return U(src)
    if isinstance(a, U) or isinstance(b, U):
        return U(src)
    numeric = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b))
    try:
        if op == "+" and numeric:
            return a + b
        if op == "-" and numeric:
            return a - b
        if op == "*" and numeric:
            r = a * b
            return int(r) if isinstance(r, float) and r.is_integer() and isinstance(a, int) else r
        if op == "/" and numeric:
            if isinstance(a, int) and isinstance(b, int):
                return a // b
            return a / b
        if op == "%" and numeric:
            return a % b
        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        if op in ("<", ">", "<=", ">=") and numeric:
            return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]
        if op == "&&" and isinstance(a, bool) and isinstance(b, bool):
            return a and b
        if op == "||" and isinstance(a, bool) and isinstance(b, bool):
            return a or b
        if op == "??":
            return b if a is None else a
    except (TypeError, ZeroDivisionError):
        pass
    return U(src)


def to_text(v: Any) -> str:
    """A value as display text, unresolved parts as {?...}."""
    if isinstance(v, str):
        return v
    return fmt_value(v)


# ---------------------------------------------------------------------------
# TEXT: SmartFormat placeholders and markup
# ---------------------------------------------------------------------------

_MARKUP = re.compile(r"\[/?[a-zA-Z_]+(?:=[^\]]*)?\]")
#: Placeholders the game fills at run time that no sheet number feeds.
RUNTIME = "X"


def strip_markup(text: str) -> str:
    return _MARKUP.sub("", text)


def _split_top(s: str, sep: str) -> list[str]:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


class Smart:
    """Renders a SmartFormat template. `vals` maps var name -> (base, up);
    `mode` is 'base', 'up' or 'both' ('both' prints "8 [11]")."""

    def __init__(self, vals: dict[str, tuple[Any, Any]], mode: str = "base"):
        self.vals, self.mode = vals, mode
        self.unresolved: list[str] = []
        self.in_combat_parts: list[str] = []

    def val(self, name: str) -> Any:
        if name in self.vals:
            b, u = self.vals[name]
            return u if self.mode == "up" else b
        return None

    def show(self, name: str) -> str:
        if name in self.vals:
            b, u = self.vals[name]
            if isinstance(b, U) or b is None:
                self.unresolved.append(name)
                return RUNTIME
            if self.mode == "up":
                return fmt_num(u) if not isinstance(u, U) else RUNTIME
            if self.mode == "both" and not isinstance(u, U) and u != b:
                return f"{fmt_num(b)} [{fmt_num(u)}]"
            return fmt_num(b)
        self.unresolved.append(name)
        return RUNTIME

    def render(self, text: str) -> str:
        out, i = [], 0
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth, j = 0, i
                while j < len(text):
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                out.append(self.hole(text[i + 1:j]))
                i = j + 1
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def hole(self, body: str) -> str:
        if body.startswith("?"):                     # an unresolved C# expr
            return "{" + body + "}"
        name, _, rest = body.partition(":")
        if name == "InCombat":
            opts = _split_top(rest, "|")
            mark = len(self.unresolved)
            inside = self.render(opts[0])
            del self.unresolved[mark:]          # in-combat previews are run-time by nature
            shown = strip_markup(inside).strip()
            if shown and re.search(r"[A-Za-z]{2}", shown):
                self.in_combat_parts.append(shown)
            return self.render(opts[1]) if len(opts) > 1 else ""
        if name == "IfUpgraded":
            _fmt, _, opts_s = rest.partition(":")
            opts = _split_top(opts_s, "|")
            up = self.mode == "up"
            pick = opts[0] if up else (opts[1] if len(opts) > 1 else "")
            return self.render(pick)
        if not rest:
            return self.show(name)
        fmt, _, opts_s = rest.partition(":")
        if not re.fullmatch(r"[A-Za-z]+(\([^)]*\))?", fmt):
            # `{Flag:A|B}`: SmartFormat's implicit conditional on a bool the
            # card adds at run time. Out of combat the flag is false: the
            # last branch shows.
            opts = _split_top(rest, "|")
            v = self.val(name)
            if isinstance(v, bool):
                return self.render(opts[0] if v else opts[-1])
            return self.render(opts[-1])
        if fmt.startswith("diff") or fmt in ("", "inverseDiff", "abs"):
            return self.show(name)
        if fmt.startswith("energyIcons"):
            m = re.match(r"energyIcons\((\d+)\)", fmt)
            if m:
                return f"{m.group(1)} Energy"
            return f"{self.show(name)} Energy"
        if fmt.startswith("starIcons"):
            return f"{self.show(name)} Stars"
        if fmt.startswith(("plural", "cond", "choose")):
            opts = _split_top(opts_s, "|")
            v = self.val(name)
            if fmt.startswith("plural") and len(opts) >= 2:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    return self.render(opts[0] if v == 1 else opts[1])
                return self.render(opts[1])
            if fmt.startswith("cond") and opts:
                if isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= int(v) < len(opts):
                    return self.render(opts[int(v)])
                return self.render(" / ".join(opts))
            if opts:
                return self.render(" / ".join(opts))
        self.unresolved.append(name)
        return RUNTIME


def clean(text: str) -> str:
    text = strip_markup(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# OWNERSHIP
# ---------------------------------------------------------------------------

_OWNER_TOKEN = re.compile(
    r"Klee(?!Mod|Pck|Patch|Art|Asset|CardTool|Keyword|PowerIcon|SelfCheck)|Kokomi|Furina|Varka|Yae")
_NEUTRAL_DIRS = {"Diagnostics", "RunStats", "Patches"}
_NEUTRAL_STEMS = {"KleeMod", "KleePatchBootstrap", "KleePck", "KleeArt", "KleeAssetPathFallback",
                  "KleeCardTooltips", "KleeKeywords", "KleePowerIcons", "KleeSelfCheck",
                  "KleeOffPoolCards", "PrototypeRoster", "RosterAncientCards"}


def owner_of_path(path: Path) -> str | None:
    stem = path.stem
    if path.parent == GENERATED_CARDS:
        for pre, own in (("ProtoKo", "Klee"), ("ProtoKk", "Kokomi"), ("ProtoFs", "Furina"),
                         ("ProtoVk", "Varka"), ("ProtoYm", "Yae"), ("ProtoM", "Shared")):
            if stem.startswith(pre):
                return own
        return None
    if any(part in _NEUTRAL_DIRS for part in path.parts) or stem in _NEUTRAL_STEMS:
        return None
    if "Companion" in stem or "Abyss" in stem or "Teyvat" in path.as_posix():
        return "Shared"
    m = _OWNER_TOKEN.search(stem) or _OWNER_TOKEN.search(path.parent.name)
    if m:
        return m.group(0)
    return None


def owner_from_text(text: str) -> str | None:
    m = _OWNER_TOKEN.search(text)
    return m.group(0) if m else None


class Owners:
    """Who a class belongs to: its own name, its file's owner, else the one
    owner whose files mention it, else Shared."""

    def __init__(self, files: list[CsFile]):
        self.file_owner = {f.path: owner_of_path(f.path) for f in files}
        self.mentions: dict[str, set[str]] = {}
        for f in files:
            own = self.file_owner[f.path]
            if own is None:
                continue
            for t in f.toks:
                if t.kind == "id" and t.val[:1].isupper():
                    self.mentions.setdefault(t.val, set()).add(own)

    def of_class(self, ci: ClassInfo | None) -> str:
        if ci is None:
            return "Shared"
        c = ci
        while c is not None:
            m = _OWNER_TOKEN.search(c.name)
            if m:
                return m.group(0)
            c = c.outer
        own = self.file_owner.get(ci.file.path)
        if own:
            return own
        votes = self.mentions.get(ci.name, set())
        if len(votes) == 1:
            return next(iter(votes))
        return "Shared"


def walk(n: Any):
    """Every node under (and including) `n`."""
    if isinstance(n, N):
        yield n
        for a in n.a:
            yield from walk(a)
    elif isinstance(n, (list, tuple)):
        for a in n:
            yield from walk(a)


# ---------------------------------------------------------------------------
# THE CENSUS
# ---------------------------------------------------------------------------

def yaml_rows() -> list[dict]:
    import yaml
    data = yaml.safe_load(SHEET.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else (data or {}).get("cards", [])
    return [r for r in rows if isinstance(r, dict) and r.get("id")]


def _sheet_lines() -> dict[str, int]:
    out = {}
    for k, line in enumerate(SHEET.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"- \{id: (proto_\w+)", line)
        if m:
            out[m.group(1)] = k
    return out


VAR_NAME = {"SpotlitBlockVar": "Block", "SpotlitDamageVar": "Damage",
            "FrontFoldedDamageVar": "CalculatedDamage",
            "FoldedCalculatedBlockVar": "CalculatedBlock",
            "HitsTotalDamageVar": "TotalDamage"}
#: Computed in combat only; out of combat the template hides them.
COMBAT_ONLY_VARS = {"CalculatedDamage", "CalculatedBlock", "TotalDamage"}
_GENERIC_CARD = re.compile(r"ModelDb\.Card<(?:[\w.]+\.)?(\w+)>")


class Census:
    def __init__(self):
        self.files = [scan_file(p) for p in sorted(CS_ROOT.rglob("*.cs"))]
        self.idx = Index(self.files)
        self.owners = Owners(self.files)
        self.out: dict[str, dict[str, list[dict]]] = {c: {} for c in CHARACTERS}
        self.gaps: dict[str, Any] = {"parse_errors": [], "unresolved": [], "eval_errors": []}
        for f in self.files:
            self.gaps["parse_errors"].extend(f.errors)
        self.card_titles: dict[str, str] = {}      # class name -> title
        self.done_classes: set[int] = set()
        self.keyword_json_keys: set[str] = set()
        self.tey_meta: dict[str, Any] = {}
        self.card_rows: dict[str, tuple[str, str]] = {}
        self.titles: dict[str, str] = {}
        self.tip_seen: set[tuple[str, str]] = set()

    # -- output
    def add(self, owner: str, section: str, item: dict) -> None:
        text = item.get("text")
        if text is None or not str(text).strip():
            self.gaps.setdefault("empty_dropped", []).append(item.get("source", "?"))
            return
        if owner not in CHARACTERS:
            owner = "Shared"
        for k in ("text", "upgraded_text", "name"):
            if k in item and isinstance(item[k], str) and "{?" in item[k]:
                self.gaps["unresolved"].append(
                    {"source": item["source"], "field": k, "text": item[k]})
        ordered = {k: item[k] for k in ("id", "name", "kind", "text", "upgraded_text",
                                        "variants", "source", "context") if k in item}
        self.out.setdefault(owner, {}).setdefault(section, []).append(ordered)

    @staticmethod
    def src(f: CsFile, line: int) -> str:
        return f"{rel(f.path)}:{line}"

    # -- per-class helpers
    def class_loc(self, ci: ClassInfo, env=None) -> tuple[dict, dict] | None:
        m = self.idx.find_member(ci, "Localization")
        if m is None or m.expr is None:
            return None
        expr = m.expr
        self.idx.dyn = ci
        try:
            val = self.idx.ev(expr, env or {}, m.cls)
        finally:
            self.idx.dyn = None
        nodes = []
        if expr.t == "new" and expr.a[2]:
            nodes = [el[1] for el in expr.a[2] if el[0] == "item"]
        rows, lines = {}, {}
        self.loc_nodes = {}
        if isinstance(val, list):
            for k, v in enumerate(val):
                if isinstance(v, tuple) and len(v) == 2:
                    key = to_text(v[0])
                    rows[key] = v[1]
                    lines[key] = nodes[k].line if k < len(nodes) else expr.line
                    if k < len(nodes) and nodes[k].t == "tuple" and len(nodes[k].a[0]) == 2:
                        self.loc_nodes[key] = (nodes[k].a[0][1], m.cls)
        if not rows:
            self.gaps["eval_errors"].append(
                f"{rel(ci.file.path)}:{m.line}: {ci.name}.Localization did not evaluate "
                f"({' '.join(m.file.src[expr.pos:expr.end].split())[:120]})")
            return None
        return rows, lines

    def vars_of(self, ci: ClassInfo, upgraded: bool) -> dict[str, Any]:
        m = self.idx.find_member(ci, "CanonicalVars")
        out: dict[str, Any] = {}
        if m is None or m.expr is None:
            return out
        env = {"IsUpgraded": upgraded}
        self.idx.dyn = ci
        try:
            val = self.idx.ev(m.expr, env, m.cls)
        finally:
            self.idx.dyn = None
        if not isinstance(val, list):
            return out
        for v in val:
            if not isinstance(v, Obj):
                continue
            venv = dict(v.env or {})
            venv.setdefault("IsUpgraded", upgraded)
            args = [self.idx.ev(a, venv, v.cls_ctx) for a in v.args]
            custom = self.custom_var(v.type, args)
            alias = None
            if custom is not None:
                name, num, alias = custom
            else:
                if args and isinstance(args[0], str):
                    name, rest = args[0], args[1:]
                elif v.type == "DynamicVar":
                    continue
                else:
                    name = VAR_NAME.get(v.type, v.type[:-3] if v.type.endswith("Var") else v.type)
                    rest = args
                num = next((a for a in rest if isinstance(a, (int, float))
                            and not isinstance(a, bool)), None)
            if alias and alias in out and not num:
                num = out[alias]
            out[name] = num if num is not None else U(name)
        return out

    def custom_var(self, type_name: str, args: list) -> tuple | None:
        """A mod-defined DynamicVar subclass: read its constructor's
        `: base(name, value, ...)` with the call's arguments bound."""
        if type_name in VAR_NAME:
            return None
        for ci in self.idx.classes(type_name):
            src = ci.file.src[ci.span[0]:ci.span[1]]
            m = re.search(re.escape(ci.name) + r"\s*\(([^)]*)\)\s*:\s*base\(", src)
            if not m:
                continue
            start = ci.span[0] + m.end() - 1          # at the '(' of base(
            toks = lex(ci.file.src[start:ci.span[1]], 1, start)
            p = Parser(toks, 0)
            try:
                p.take()
                bargs = p.parse_args(")")
            except (ParseError, IndexError):
                return None
            params = _param_names(lex(m.group(1)))
            env = {pn: args[k] for k, pn in enumerate(params) if k < len(args)}
            vals = [self.idx.ev(a, env, ci) for _, a in bargs]
            if not vals or not isinstance(vals[0], str):
                return None
            num = next((x for x in vals[1:] if isinstance(x, (int, float))
                        and not isinstance(x, bool)), None)
            alias = next((x for x in args if isinstance(x, str) and x != vals[0]), None)
            return vals[0], num, alias
        return None

    @staticmethod
    def member_body(m: Member | None) -> str:
        if m is None:
            return ""
        if m.body_span:
            return m.file.src[m.body_span[0]:m.body_span[1]]
        if m.expr is not None:
            return m.file.src[m.expr.pos:m.expr.end]
        return ""

    def upgrade_of(self, ci: ClassInfo) -> dict:
        body = self.member_body(self.idx.find_member(ci, "OnUpgrade"))
        up: dict[str, Any] = {"vars": {}, "cost": 0}
        for name, d in re.findall(r"DynamicVars\.(\w+)\.UpgradeValueBy\((-?[\d.]+)m?\)", body):
            up["vars"][name] = up["vars"].get(name, 0) + float(d)
        for name, d in re.findall(r'DynamicVars\["(\w+)"\]\.UpgradeValueBy\((-?[\d.]+)m?\)', body):
            up["vars"][name] = up["vars"].get(name, 0) + float(d)
        for d in re.findall(r"EnergyCost\.UpgradeBy\((-?\d+)\)", body):
            up["cost"] += int(d)
        up["add"] = re.findall(r"AddKeyword\(CardKeyword\.(\w+)\)", body)
        up["remove"] = re.findall(r"RemoveKeyword\(CardKeyword\.(\w+)\)", body)
        return up

    def card_header(self, ci: ClassInfo) -> dict:
        """cost, type, rarity from the `: base(...)` call (the class or a base)."""
        for c in self.idx.base_chain(ci):
            src = c.file.src[c.span[0]:c.span[1]]
            m = re.search(r":\s*base\(\s*(-?\d+)\s*,\s*CardType\.(\w+)\s*,\s*CardRarity\.(\w+)", src)
            if m:
                return {"cost": int(m.group(1)), "type": m.group(2), "rarity": m.group(3)}
        return {}

    def keywords_of(self, ci: ClassInfo) -> list[str]:
        return re.findall(r"CardKeyword\.(\w+)",
                          self.member_body(self.idx.find_member(ci, "CanonicalKeywords")))

    def render_card(self, ci: ClassInfo) -> dict | None:
        loc = self.class_loc(ci)
        if loc is None:
            return None
        rows, lines = loc
        title = to_text(rows.get("title", ci.name))
        if "description" not in rows:
            return None
        desc = to_text(rows["description"])
        base_vars = self.vars_of(ci, False)
        up_vars = self.vars_of(ci, True)
        up = self.upgrade_of(ci)
        vals = {}
        for name in set(base_vars) | set(up_vars) | set(up["vars"]):
            b = base_vars.get(name, U(name))
            u = up_vars.get(name, b)
            if name in up["vars"] and isinstance(u, (int, float)) and not isinstance(u, U):
                u = u + up["vars"][name]
                if isinstance(u, float) and u.is_integer():
                    u = int(u)
            vals[name] = (b, u)
        # Out of combat a calculated number prints its base (the multiplier
        # reads the combat, which is not there).
        for calc in ("CalculatedDamage", "CalculatedBlock"):
            if calc in vals and isinstance(vals[calc][0], U) and "CalculationBase" in vals:
                vals[calc] = vals["CalculationBase"]
            elif calc not in vals and "CalculationBase" in vals and "{" + calc in desc:
                vals[calc] = vals["CalculationBase"]
        r_both, r_up, r_base = Smart(vals, "both"), Smart(vals, "up"), Smart(vals, "base")
        text = clean(r_both.render(desc))
        up_text = clean(r_up.render(desc))
        base_text = clean(r_base.render(desc))
        hdr = self.card_header(ci)
        kws = self.keywords_of(ci)
        ctx = []
        if hdr:
            cost = hdr["cost"]
            c = "X" if cost < 0 else str(cost)
            if up["cost"]:
                c += f" [{cost + up['cost']}]"
            ctx.append(f"Cost {c}")
        if kws:
            ctx.append("Keywords: " + ", ".join(kws))
        if up["add"]:
            ctx.append("Upgrade adds: " + ", ".join(up["add"]))
        if up["remove"]:
            ctx.append("Upgrade removes: " + ", ".join(up["remove"]))
        if r_both.in_combat_parts:
            ctx.append("In combat also shows: " + " / ".join(dict.fromkeys(r_both.in_combat_parts)))
        unresolved = sorted(set(r_both.unresolved) - COMBAT_ONLY_VARS)
        if unresolved:
            ctx.append("Run-time values shown as X: " + ", ".join(unresolved))
        for key, val in rows.items():
            if key not in ("title", "description"):
                ctx.append(f"{key}: {clean(Smart(vals, 'both').render(to_text(val)))}")
        item = {"name": clean(title), "text": text}
        if up_text != base_text:
            item["upgraded_text"] = up_text
        return {"item": item, "ctx": ctx, "hdr": hdr,
                "line": lines.get("description", ci.line)}

    # -- cards
    def cards(self) -> None:
        by_id = {r["id"]: r for r in yaml_rows()}
        sheet_line = _sheet_lines()
        gen = {}
        for f in self.files:
            if f.path.parent != GENERATED_CARDS:
                continue
            m = re.search(r"Sheet entry: id=(\w+)", f.src)
            if m and f.classes:
                gen[m.group(1)] = f.classes[0]
        for cid, ci in sorted(gen.items()):
            r = self.render_card(ci)
            if r is None:
                self.gaps["eval_errors"].append(f"{rel(ci.file.path)}: card {cid} has no description")
                continue
            self.done_classes.add(id(ci))
            self.card_titles[ci.name] = r["item"]["name"]
            row = by_id.get(cid, {})
            owner = next((o for p, o in PREFIX_OWNER.items() if cid.startswith(p)), "Shared")
            hdr = r["hdr"]
            kind = " ".join(dict.fromkeys(x for x in (hdr.get("rarity"), hdr.get("type")) if x)) or "Card"
            item = {"id": cid, **r["item"], "kind": kind,
                    "source": f"{rel(ci.file.path)}:{r['line']}"}
            ctx = list(r["ctx"])
            if cid in sheet_line:
                ctx.append(f"sheet row {rel(SHEET)}:{sheet_line[cid]}")
            if ctx:
                item["context"] = "; ".join(ctx)
            if owner == "Shared":
                section = f"Companion cards: {(row.get('nation') or 'other').title()}"
            else:
                section = "Cards"
            self.add(owner, section, item)
            self.card_rows[cid] = (owner, section)

    def ancient_card_owners(self) -> dict[str, str]:
        out = {}
        for ci in self.idx.classes("RosterAncientCards"):
            for name in ("Klee", "Kokomi", "Furina", "Varka", "Yae"):
                for cls in _GENERIC_CARD.findall(self.member_body((ci.members.get(name) or [None])[0])):
                    out[cls] = name
        return out

    def other_cards(self) -> None:
        """Hand-written card classes: Ancient cards, curses, tokens, modal options."""
        ancients = self.ancient_card_owners()
        for f in self.files:
            if f.path.parent == GENERATED_CARDS:
                continue
            for ci in f.classes:
                if id(ci) in self.done_classes or ci.kind != "class":
                    continue
                if not ({"CardModel", "CustomCardModel"} & self.idx.base_names(ci)):
                    continue
                if "Localization" not in ci.members:
                    continue
                r = self.render_card(ci)
                if r is None:
                    continue
                self.done_classes.add(id(ci))
                self.card_titles[ci.name] = r["item"]["name"]
                hdr = r["hdr"]
                if ci.name in ancients:
                    owner, section = ancients[ci.name], "Ancient cards"
                else:
                    owner = self.owners.of_class(ci)
                    section = "Other cards (tokens, curses, options)"
                kind = " ".join(dict.fromkeys(x for x in (hdr.get("rarity"), hdr.get("type")) if x)) or "Card"
                item = {"id": ci.name, **r["item"], "kind": kind,
                        "source": f"{rel(f.path)}:{r['line']}"}
                if r["ctx"]:
                    item["context"] = "; ".join(r["ctx"])
                self.add(owner, section, item)

    def _follow(self, ci: ClassInfo, member: str) -> tuple[str, str]:
        """A member's body text and source, following one `Roster.Member()` hop."""
        m = self.idx.find_member(ci, member)
        txt = self.member_body(m)
        src = self.src(m.file, m.line) if m else self.src(ci.file, ci.line)
        mm = re.search(r"(\w+)\." + member + r"\(\)", txt)
        if mm:
            for rc in self.idx.classes(mm.group(1)):
                sm = (rc.members.get(member) or [None])[0]
                if sm is not None:
                    return self.member_body(sm), self.src(sm.file, sm.line)
        return txt, src

    def starters(self) -> None:
        for char in ("Klee", "Kokomi", "Furina", "Varka", "Yae"):
            for ci in self.idx.classes(char):
                if "CustomCharacterModel" not in self.idx.base_names(ci):
                    continue
                txt, src = self._follow(ci, "StartingDeck")
                counts: dict[str, int] = {}
                for cls in _GENERIC_CARD.findall(txt):
                    counts[cls] = counts.get(cls, 0) + 1
                for cls, n in counts.items():
                    if cls.startswith(("Strike", "Defend")):
                        name = cls[:6]
                        text = f"The base game's {name} ({cls}), unchanged."
                    else:
                        name = self.card_titles.get(cls, cls)
                        text = next((it["text"] for sec in self.out[char].values()
                                     for it in sec if it.get("name") == name and it.get("text")),
                                    name)
                    self.add(char, "Starter deck", {"id": cls, "name": name, "kind": f"starter x{n}",
                                                    "text": text, "source": src})
                rtxt, rsrc = self._follow(ci, "StartingRelics")
                for cls in re.findall(r"ModelDb\.Relic<(?:[\w.]+\.)?(\w+)>", rtxt):
                    title, text = cls, ""
                    for rc in self.idx.classes(cls):
                        loc = self.class_loc(rc)
                        if loc:
                            title = clean(to_text(loc[0].get("title", cls)))
                            text = clean(Smart({}, "base").render(to_text(loc[0].get("description", ""))))
                    self.add(char, "Starter deck", {"id": cls, "name": title, "kind": "starting relic",
                                                    "text": text or f"Starting relic: {title}.",
                                                    "source": rsrc})

    # -- other Localization blocks
    def loc_classes(self) -> None:
        for f in self.files:
            for ci in f.classes:
                if id(ci) in self.done_classes or "Localization" not in ci.members:
                    continue
                bases = self.idx.base_names(ci)
                if {"CardModel", "CustomCardModel"} & bases:
                    continue
                try:
                    loc = self.class_loc(ci)
                except Exception as exc:     # noqa: BLE001 - reported, never fatal
                    self.gaps["eval_errors"].append(f"{rel(f.path)}:{ci.line}: {ci.name}: {exc!r}")
                    continue
                if not loc:
                    continue
                rows, lines = loc
                self.done_classes.add(id(ci))
                if "CustomCharacterModel" in bases:
                    owner = CHAR_IDS.get(ci.name.lower(), self.owners.of_class(ci))
                    for key, val in rows.items():
                        txt = to_text(val)
                        self.add(owner, "Character select & profile",
                                 {"id": f"{ci.name}.{key}", "name": key, "kind": "character text",
                                  "text": clean(txt), "source": self.src(f, lines.get(key, ci.line))})
                    continue
                body = f.src[ci.span[0]:ci.span[1]]
                if {"RelicModel", "CustomRelicModel"} & bases or any("Relic" in b for b in bases):
                    kind, section, rx = "Relic", "Relics", r"RelicRarity\.(\w+)"
                elif {"PotionModel", "CustomPotionModel"} & bases or any("Potion" in b for b in bases):
                    kind, section, rx = "Potion", "Potions", r"PotionRarity\.(\w+)"
                elif any("Enchantment" in b for b in bases):
                    kind, section, rx = "Enchantment", "Enchantments", None
                elif any("Power" in b for b in bases) or "PowerType." in body:
                    kind, section, rx = "Power", "Powers & statuses", r"PowerType\.(\w+)"
                elif any("Ancient" in b for b in bases):
                    kind, section, rx = "Ancient", "Ancients", None
                elif any("Event" in b for b in bases):
                    kind, section, rx = "Event", "Events (other)", None
                else:
                    kind, section, rx = "Loc block", "Other loc blocks", None
                if rx:
                    rm = re.search(rx, body)
                    if rm:
                        kind = f"{rm.group(1)} {kind}" if kind != "Power" else f"Power ({rm.group(1)})"
                owner = self.owners.of_class(ci)
                if "Abyss" in f.path.as_posix():
                    owner, section = "Shared", "Spiral Abyss: " + section
                title = clean(to_text(rows.get("title", ci.name)))
                vals = {k: (v, v) for k, v in self.vars_of(ci, False).items()}
                main_key = "description" if "description" in rows else None
                nodes = dict(self.loc_nodes)
                self.idx.dyn = ci
                if "{?" in title and "title" in nodes:
                    title = " / ".join(dict.fromkeys(clean(v) for v in self.variants(*nodes["title"])))
                for key, val in rows.items():
                    if key == "title":
                        continue
                    texts = [to_text(val)]
                    if "{?" in texts[0] and key in nodes:
                        texts = list(dict.fromkeys(self.variants(*nodes[key]))) or texts
                    for vi, vtext in enumerate(texts):
                        sm = Smart(vals, "both")
                        many = len(texts) > 1
                        item = {"id": ci.name + ("" if key == main_key else f".{key}")
                                + (f"#{vi + 1}" if many else ""),
                                "name": title,
                                "kind": (kind if key == main_key else f"{kind}: {key}")
                                + (f" (variant {vi + 1} of {len(texts)})" if many else ""),
                                "text": clean(sm.render(vtext)),
                                "source": self.src(f, lines.get(key, ci.line))}
                        ctx = []
                        if sm.in_combat_parts:
                            ctx.append("In combat also shows: "
                                       + " / ".join(dict.fromkeys(sm.in_combat_parts)))
                        if sm.unresolved:
                            ctx.append("Run-time values shown as X: "
                                       + ", ".join(sorted(set(sm.unresolved))))
                        if ctx:
                            item["context"] = "; ".join(ctx)
                        self.add(owner, section, item)
                self.idx.dyn = None
                if not main_key and "title" in rows:
                    self.add(owner, section, {"id": ci.name, "name": title, "kind": kind,
                                              "text": title, "source": self.src(f, lines.get("title", ci.line))})

    # -- the story tables
    def _o(self, o: Obj, name: str) -> Any:
        return self.idx.obj_member(o, name)

    def stories(self) -> None:
        for f in self.files:
            if f.path.parent.name != "Story":
                continue
            for ci in f.classes:
                tm = ci.members.get("Table")
                if tm and tm[0].expr is not None:
                    o = self.idx._member_value(tm[0])
                    if isinstance(o, Obj) and o.type == "CharacterStory":
                        self.story_table(ci.name.replace("Story", ""), o, f)
                        continue
                for ms in ci.members.values():
                    m = ms[0]
                    if m.expr is None or m.expr.t != "new" \
                            or (m.expr.a[0] or m.type).split(".")[-1] != "StoryEvent":
                        continue
                    o = self.idx._member_value(m)
                    if isinstance(o, Obj):
                        self.story_event("Shared", "Co-op story event", o, f)

    def story_table(self, owner: str, o: Obj, f: CsFile) -> None:
        def line(nm: str, obj: Obj = o) -> int:
            n = obj.fields.get(nm) or obj.named.get(nm)
            return n.line if n is not None else obj.node.line
        for nm, label in (("IntroTitle", "Intro title"), ("IntroLine", "Intro line")):
            self.add(owner, "Story: intro", {"id": f"{owner}.{nm}", "name": label, "kind": "intro",
                                             "text": clean(to_text(self._o(o, nm))),
                                             "source": self.src(f, line(nm))})
        for a in self._o(o, "Ancients") or []:
            if not isinstance(a, Obj):
                continue
            anc = to_text(self._o(a, "Ancient"))
            entry = to_text(self._o(a, "AncientEntry"))
            self.add(owner, "Ancient dialogue", {"id": f"{owner}.{entry}", "name": anc,
                                                 "kind": "Ancient's line",
                                                 "text": clean(to_text(self._o(a, "AncientLine"))),
                                                 "source": self.src(f, a.node.line)})
            self.add(owner, "Ancient dialogue", {"id": f"{owner}.{entry}.reply", "name": owner,
                                                 "kind": f"reply to {anc}",
                                                 "text": clean(to_text(self._o(a, "CharacterLine"))),
                                                 "source": self.src(f, a.node.line)})
        lines = self._o(o, "Lines")
        if isinstance(lines, Obj):
            for nm in ("BossEntry", "LowHp", "Signature", "BossKill", "RunLoss", "RunWin"):
                v = self._o(lines, nm)
                if v:
                    self.add(owner, "Combat lines (barks)", {"id": f"{owner}.lines.{nm}", "name": nm,
                                                             "kind": "combat line",
                                                             "text": clean(to_text(v)),
                                                             "source": self.src(f, line(nm, lines))})
        for p in self._o(o, "Pairs") or []:
            if not isinstance(p, Obj):
                continue
            partner = to_text(self._o(p, "PartnerName"))
            seq = [(partner, self._o(p, "PartnerLine")), (owner, self._o(p, "OwnLine"))]
            if self._o(p, "OwnFirst") is True:
                seq.reverse()
            for k, (who, ln) in enumerate(seq):
                self.add(owner, "Co-op pair lines", {"id": f"{owner}.pair.{partner}.{k}",
                                                     "name": who, "kind": f"pair with {partner}",
                                                     "text": clean(to_text(ln)),
                                                     "source": self.src(f, p.node.line)})
        for e in self._o(o, "Events") or []:
            if isinstance(e, Obj):
                self.story_event(owner, "Story events", e, f)

    def story_event(self, owner: str, section: str, e: Obj, f: CsFile) -> None:
        def line(nm: str) -> int:
            n = e.named.get(nm) or e.fields.get(nm)
            return n.line if n is not None else e.node.line
        act = self._o(e, "ActIndex")
        title = clean(to_text(self._o(e, "Title")))
        et = self._o(e, "EventType")
        eid = et.name if isinstance(et, TypeRef) else title
        flags = [f"act {act + 1}" if isinstance(act, int) and act >= 0 else "any act"]
        if self._o(e, "Home") is True:
            flags.append("home event")
        fn = e.fields.get("Follows")
        if fn is not None:
            names = re.findall(r"typeof\((?:[\w.]+\.)?(\w+)\)", f.src[fn.pos:fn.end])
            if names:
                flags.append("follows " + ", ".join(names))
        base_ctx = f"{title} ({'; '.join(flags)})"
        self.add(owner, section, {"id": eid, "name": title, "kind": "event title", "text": title,
                                  "source": self.src(f, line("Title")), "context": base_ctx})
        for op in self._o(e, "Openings") or []:
            if not isinstance(op, Obj):
                continue
            when = op.args[1] if len(op.args) > 1 else op.named.get("When")
            cond = " ".join(f.src[when.pos:when.end].split()) if when is not None else ""
            self.add(owner, section, {"id": f"{eid}.opening.{to_text(self._o(op, 'Key'))}",
                                      "name": title, "kind": "opening line",
                                      "text": clean(to_text(self._o(op, "Line"))),
                                      "source": self.src(f, op.node.line),
                                      "context": f"{base_ctx}; opens the page when {cond}"})
        self.add(owner, section, {"id": f"{eid}.page", "name": title, "kind": "page",
                                  "text": clean(to_text(self._o(e, "Body"))),
                                  "source": self.src(f, line("Body")), "context": base_ctx})
        for opt in self._o(e, "Options") or []:
            if not isinstance(opt, Obj):
                continue
            key = to_text(self._o(opt, "Key"))
            label = clean(to_text(self._o(opt, "Title")))
            ctx = base_ctx
            if "ShownIf" in opt.fields:
                c = opt.fields["ShownIf"]
                ctx += "; offered only if " + " ".join(f.src[c.pos:c.end].split())
            self.add(owner, section, {"id": f"{eid}.{key}", "name": label, "kind": "option",
                                      "text": clean(to_text(self._o(opt, "Description"))),
                                      "source": self.src(f, opt.node.line), "context": ctx})
            res = self._o(opt, "Result")
            if res:
                self.add(owner, section, {"id": f"{eid}.{key}.result", "name": label,
                                          "kind": "option result", "text": clean(to_text(res)),
                                          "source": self.src(f, opt.node.line), "context": base_ctx})

    # -- Spiral Abyss
    def abyss(self) -> None:
        texts = self.idx.classes("AbyssText")
        if not texts:
            self.gaps["eval_errors"].append("AbyssText not found")
            return
        ci = texts[0]
        durations = self.idx.classes("AbyssDurations")
        for enum, section, kind in (("AbyssBlessing", "Spiral Abyss: Blessings", "Blessing"),
                                    ("AbyssShadow", "Spiral Abyss: Shadows", "Shadow")):
            ens = [c for c in self.idx.classes(enum) if c.kind == "enum"]
            if not ens:
                continue
            for member in ens[0].enum_members:
                if member == "None":
                    continue
                ev = EnumVal(enum, member)
                env = {"b": ev, "s": ev}
                # Keyed rows since the localization census (2026-10-23): the
                # name and text are templates, the act's numbers their vars.
                name = self._overload(ci, "NameTemplate", env)
                template = to_text(self._overload(ci, "TextTemplate", env))
                vs = [clean(self._abyss_fill(template, a)) for a in range(3)]
                dur = ""
                if durations:
                    d = self._overload(durations[0], "Of", env)
                    if isinstance(d, EnumVal):
                        dur = "This act" if d.name == "ThisAct" else "Whole run"
                item = {"id": f"{enum}.{member}", "name": to_text(name),
                        "kind": kind + (f" ({dur})" if dur else ""), "text": vs[0],
                        "source": f"{rel(ci.file.path)}:{self._arm_line(ci, 'TextTemplate', enum, member)}"}
                if len(set(vs)) > 1:
                    item["variants"] = {f"act {k + 1}": v for k, v in enumerate(vs)}
                    item["context"] = "The numbers are the act the entry is taken in; text shown is act 1."
                self.add("Shared", section, item)

    def _abyss_fill(self, template: str, act: int) -> str:
        """An Abyss text row's vars for act `act`: each `{Name}` is
        `AbyssNumbers.Name(act)` (or the constant), the element of the act
        and its counter golded, as `AbyssText.Numbers` fills them."""
        nums = self.idx.classes("AbyssNumbers")
        src = (REPO / "klee-mod" / "KleeCode" / "Abyss" / "AbyssEntries.cs").read_text(encoding="utf-8")
        by_act = re.findall(r"Element\.(\w+)", re.search(r"ByAct = \{([^}]*)\}", src).group(1))
        counters = dict(re.findall(r"Element\.(\w+) => Element\.(\w+),", src))
        element = by_act[min(max(act, 0), len(by_act) - 1)]

        def hole(m: re.Match) -> str:
            name = m.group(1)
            if name == "Element":
                return f"[gold]{element}[/gold]"
            if name == "Counter":
                return counters.get(element, "")
            if name == "HeraldHpPercent":
                bonus = re.search(r"HeraldHpBonus = ([0-9.]+)m;", src)
                return str(int(round(float(bonus.group(1)) * 100))) if bonus else m.group(0)
            if nums:
                v = self._overload(nums[0], name, {"act": act})
                if not isinstance(v, U):
                    return to_text(v)
            return m.group(0)
        return re.sub(r"\{(\w+)\}", hole, template)

    def _overload(self, ci: ClassInfo, name: str, env: dict) -> Any:
        best = None
        for m in ci.members.get(name, []):
            if not all(p in env for p in m.params):
                continue
            v = self.idx.ev(m.expr, {p: env[p] for p in m.params}, ci)
            if not isinstance(v, U) and not (isinstance(v, str) and "{?" in v):
                return v
            best = best or v
        return best if best is not None else U(name)

    @staticmethod
    def _arm_line(ci: ClassInfo, member: str, enum: str, name: str) -> int:
        for m in ci.members.get(member, []):
            if m.expr is not None and m.expr.t == "switch":
                for pat, body in m.expr.a[1]:
                    ids = [t.val for t in pat if t.kind == "id"]
                    if name in ids and enum in ids:
                        return body.line
        return ci.line

    # -- loc dictionaries anywhere in the tree
    def dictionaries(self) -> None:
        kw = json.loads(KEYWORD_JSON.read_text(encoding="utf-8")) if KEYWORD_JSON.exists() else {}
        self.keyword_json_keys = set(kw)
        teyvat_rows: dict[str, list] = {}
        for f in self.files:
            toks = f.toks
            comment_map = {}
            if f.path.name == "TeyvatEventsGenerated.cs":
                for k, ln in enumerate(f.src.splitlines(), 1):
                    m = re.match(r"\s*// (\w+) \((\w+) / (\w+)\)", ln)
                    if m:
                        comment_map[k] = m.groups()
            for i, t in enumerate(toks):
                if not (t.kind == "id" and t.val == "new" and toks[i + 1].kind == "id"
                        and toks[i + 1].val in ("Dictionary", "SortedDictionary")):
                    continue
                try:
                    node, _ = parse_expr_at(toks, i)
                except (ParseError, IndexError) as exc:
                    self.gaps["parse_errors"].append(f"{rel(f.path)}:{t.line}: dictionary: {exc}")
                    continue
                if node.t != "new" or not node.a[2] or not (node.a[0] or "").endswith(",string>"):
                    continue
                ctx = self.class_at(f, t.pos)
                stmt = f.src[max(0, t.pos - 400):t.pos]
                stmt = stmt[stmt.rfind(";") + 1:]
                tm = re.findall(r'GetTable\("(\w+)"\)', stmt)
                table = tm[-1] if tm else ("card_keywords" if "keywordFallback" in stmt else "")
                for el in node.a[2]:
                    if el[0] != "kv":
                        continue
                    key = self.idx.ev(el[1], {}, ctx)
                    val = self.idx.ev(el[2], {}, ctx)
                    if isinstance(key, tuple):
                        key = ".".join(to_text(x) for x in key)
                    if not isinstance(val, (str, U)):
                        continue
                    key_s, val_s = to_text(key), to_text(val)
                    if not self.is_text(val_s):
                        continue
                    if re.fullmatch(r"\{\?.*\}", val_s.strip(), re.S):
                        self.gaps.setdefault("unresolved_rows", []).append(
                            {"source": f"{rel(f.path)}:{el[2].line}", "key": key_s, "value": val_s})
                        continue
                    if f.path.name == "TeyvatEventsGenerated.cs":
                        entry = key_s.split(".")[0]
                        teyvat_rows.setdefault(entry, []).append((key_s, val_s, el[2].line, f))
                        if entry not in self.tey_meta:
                            self.tey_meta[entry] = next(
                                (comment_map[ln] for ln in range(el[1].line, el[1].line - 4, -1)
                                 if ln in comment_map), None)
                        continue
                    self.dict_row(f, ctx, table, key_s, val_s, el)
        if kw:
            lines = {}
            for k, ln in enumerate(KEYWORD_JSON.read_text(encoding="utf-8").splitlines(), 1):
                m = re.match(r'\s*"([^"]+)"\s*:', ln)
                if m:
                    lines[m.group(1)] = k
            for key, val in kw.items():
                if key.endswith(".title"):
                    self.titles[key[:-6]] = val
                if not key.endswith(".description"):
                    continue
                base = key[:-len(".description")]
                self.keyword_item(base, kw.get(base + ".title", base), val,
                                  f"{rel(KEYWORD_JSON)}:{lines.get(key, 1)}",
                                  "packaged tip (card_keywords.json)")
        self.teyvat_events(teyvat_rows)

    @staticmethod
    def class_at(f: CsFile, pos: int) -> ClassInfo | None:
        best = None
        for ci in f.classes:
            if ci.span[0] <= pos <= ci.span[1] and (best is None or ci.span[0] >= best.span[0]):
                best = ci
        return best

    @staticmethod
    def is_text(val: str) -> bool:
        v = val.strip()
        if not v or v.startswith(("res://", "user://", "http")):
            return False
        if v == "...":
            return True
        if not re.search(r"[A-Za-z]", v):
            return False
        if " " not in v and re.fullmatch(r"[A-Z0-9_]+(\.[A-Za-z0-9_-]+)*|[a-z0-9_]+", v):
            return False                  # an id, not a line
        if re.fullmatch(r"[\w./-]+\.(png|tscn|tres|ogg|wav|json|webp|jpg)", v):
            return False
        return True

    def dict_row(self, f: CsFile, ctx, table: str, key: str, val: str, el) -> None:
        source = f"{rel(f.path)}:{el[2].line}"
        if key.endswith(".title"):
            self.titles.setdefault(key[:-6], val)
        if table == "card_keywords" or (key.startswith("KLEEMOD-") and not table):
            if key.endswith(".title") or key in self.keyword_json_keys:
                return              # the title rides with its body; the pck copy ships
            base = key.rsplit(".", 1)[0]
            title_node = None
            self.keyword_item(base, self.dll_title(f, ctx, base) or base, val, source,
                              "DLL-only tip (not in card_keywords.json)")
            return
        path = f.path.as_posix()
        sm = Smart({}, "base")
        txt = clean(sm.render(val))
        src_text = f.src[el[1].pos:el[2].end]
        if "Teyvat" in path:
            owner = "Shared"
            if "Ancient" in path or table == "ancients":
                section = "Teyvat frame: Ancients"
            elif "Creature" in path or table == "monsters":
                section = "Teyvat frame: enemy names"
            elif table == "acts":
                section = "Teyvat frame: act names"
            else:
                section = "Teyvat frame: other text"
        else:
            owner = owner_from_text(src_text) or self.owners.of_class(ctx)
            if "Abyss" in path:
                owner, section = "Shared", "Spiral Abyss: UI"
            elif "Prompt" in src_text or "prompt" in key.lower():
                section = "Prompts & screen text"
            else:
                section = f"Loc rows ({table or 'misc'})"
        item = {"id": key, "name": key, "kind": f"loc row ({table})" if table else "loc row",
                "text": txt, "source": source}
        if sm.unresolved:
            item["context"] = "Run-time values shown as X: " + ", ".join(sorted(set(sm.unresolved)))
        self.add(owner, section, item)

    def dll_title(self, f: CsFile, ctx, base: str) -> str | None:
        """The `.title` row beside a DLL-only tip body, if the same file has it."""
        cache = getattr(self, "_dll_titles", None)
        if cache is None:
            cache = self._dll_titles = {}
        if f.path not in cache:
            rows = {}
            for i, t in enumerate(f.toks):
                if t.kind == "op" and t.val == "[" and i and f.toks[i - 1].val in ("{", ","):
                    try:
                        p = Parser(f.toks, i + 1)
                        k = p.parse_expr()
                        p.expect("]")
                        p.expect("=")
                        v = p.parse_expr()
                    except (ParseError, IndexError):
                        continue
                    c = self.class_at(f, t.pos)
                    ks = to_text(self.idx.ev(k, {}, c))
                    if ks.endswith(".title"):
                        rows[ks[:-6]] = to_text(self.idx.ev(v, {}, c))
            cache[f.path] = rows
        return cache[f.path].get(base)

    def keyword_item(self, base: str, title: str, val: str, source: str, origin: str) -> None:
        sm = Smart({}, "base")
        title = clean(to_text(title))
        if (base, clean(val)) in self.tip_seen:
            return
        self.tip_seen.add((base, clean(val)))
        item = {"id": base, "name": title, "kind": "keyword tip", "text": clean(sm.render(val)),
                "source": source, "context": origin}
        if sm.unresolved:
            item["context"] += "; run-time values shown as X: " + ", ".join(sorted(set(sm.unresolved)))
        self.add(self.keyword_owner(base, title), "Keyword & glossary tips", item)

    def keyword_owner(self, key: str, title: str) -> str:
        m = re.search(r"(KLEE|KOKOMI|FURINA|VARKA|YAE)", key.replace("KLEEMOD", ""))
        if m:
            return m.group(1).title()
        word = re.escape(title.lower())
        users = set()
        for owner in ("Klee", "Kokomi", "Furina", "Varka", "Yae"):
            for it in self.out.get(owner, {}).get("Cards", []):
                if re.search(r"\b" + word + r"\b", it["text"].lower()):
                    users.add(owner)
                    break
        return next(iter(users)) if len(users) == 1 else "Shared"

    def teyvat_events(self, rows: dict) -> None:
        for entry, items in rows.items():
            meta = self.tey_meta.get(entry)
            cls, nation, mirror = meta if meta else (entry, "Other", "?")
            vals: dict = {}
            for ci in self.idx.classes(cls):
                vals = {k: (v, v) for k, v in self.vars_of(ci, False).items()}
                break
            title = clean(next((v for k, v, *_ in items if k == entry + ".title"), entry))
            section = f"Teyvat frame events: {nation}"
            ctx0 = f"{title} ({nation}; dresses the base event {mirror})"
            opts: dict[str, dict] = {}
            for key, val, line, f in items:
                rest = key[len(entry) + 1:]
                sm = Smart(vals, "base")
                txt = clean(sm.render(val))
                ctx = ctx0 + ("; run-time values shown as X: " + ", ".join(sorted(set(sm.unresolved)))
                              if sm.unresolved else "")
                src = f"{rel(f.path)}:{line}"
                if rest == "title":
                    self.add("Shared", section, {"id": entry, "name": title, "kind": "event title",
                                                 "text": title, "source": src, "context": ctx0})
                    continue
                om = re.match(r"pages\.(\w+)\.options\.(\w+)\.(title|description)$", rest)
                if om:
                    okey = f"{om.group(1)}.{om.group(2)}"
                    o = opts.setdefault(okey, {"id": f"{entry}.{okey}",
                                               "kind": f"option ({om.group(1)} page)",
                                               "source": src, "context": ctx})
                    o["name" if om.group(3) == "title" else "text"] = txt
                    if om.group(3) == "description":
                        o["source"], o["context"] = src, ctx
                    if "name" in o and "text" in o and not o.get("_done"):
                        o["_done"] = True
                        self.add("Shared", section, {k: v for k, v in o.items() if k != "_done"})
                    continue
                pm = re.match(r"pages\.(\w+)\.description$", rest)
                self.add("Shared", section, {"id": key, "name": title,
                                             "kind": f"page {pm.group(1)}" if pm else rest,
                                             "text": txt, "source": src, "context": ctx})
            for o in opts.values():
                if not o.get("_done"):
                    o.setdefault("name", "(no title)")
                    o.setdefault("text", o["name"])
                    self.add("Shared", section, {k: v for k, v in o.items() if k != "_done"})

    # -- hover tips built in code: With(inherited, Key, body) and friends
    def variants(self, n: N, ctx: ClassInfo, env: dict | None = None, depth: int = 0) -> list[str]:
        """A string expression's possible texts: both arms of a ternary, and a
        helper called with each truth value of the flags it cannot know."""
        env = env or {}
        v = self.idx.ev(n, env, ctx)
        if isinstance(v, str) and "{?" not in v:
            return [v]
        if depth > 3:
            return [to_text(v)]
        if n.t == "ternary":
            return (self.variants(n.a[1], ctx, env, depth + 1)
                    + self.variants(n.a[2], ctx, env, depth + 1))
        if n.t == "call":
            fn = self.idx.ev(n.a[0], env, ctx)
            if isinstance(fn, tuple) and fn and fn[0] == "method" and fn[1].expr is not None:
                m = fn[1]
                argv = [self.idx.ev(a, env, ctx) for _, a in n.a[1]]
                free = [k for k, a in enumerate(argv) if isinstance(a, U)]
                benv0 = {p: argv[k] for k, p in enumerate(m.params) if k < len(argv)}
                if free and len(free) <= 2:
                    out: list[str] = []
                    for combo in itertools.product((True, False), repeat=len(free)):
                        benv = dict(benv0)
                        for k, b in zip(free, combo):
                            if k < len(m.params):
                                benv[m.params[k]] = b
                        out += self.variants(m.expr, m.cls, benv, depth + 1)
                    return list(dict.fromkeys(out))
                if m.expr.t in ("ternary", "call", "switch"):
                    return self.variants(m.expr, m.cls, benv0, depth + 1)
        return [to_text(v)]

    def code_tips(self) -> None:
        for f in self.files:
            for ci in f.classes:
                for ms in ci.members.values():
                    for m in ms:
                        if m.expr is None:
                            continue
                        for node in walk(m.expr):
                            if node.t != "call" or len(node.a[1]) < 2:
                                continue
                            args = node.a[1]
                            key, body_n = None, None
                            for k, (_, a) in enumerate(args[:-1]):
                                kv = self.idx.ev(a, {}, m.cls)
                                if isinstance(kv, str) and kv.startswith("KLEEMOD-") and " " not in kv:
                                    key, body_n = kv, args[k + 1][1]
                                    break
                            if key is None:
                                continue
                            texts = [t for t in self.variants(body_n, m.cls)
                                     if self.is_text(t) and " " in t]
                            title = self.titles.get(key) or key.split("-", 1)[-1].replace("_", " ").title()
                            for k, t in enumerate(texts):
                                self.keyword_item(
                                    key, title, t, f"{rel(f.path)}:{body_n.line}",
                                    f"hover tip built in code ({ci.name}.{m.name})"
                                    + (f", variant {k + 1} of {len(texts)}" if len(texts) > 1 else ""))

    # -- data lists of records that carry a line of text (Teyvat Ancients' dialogue)
    _TEXT_PARAMS = ("Text", "Line", "Body", "Title", "Description", "Label")

    def record_lists(self) -> None:
        for f in self.files:
            for ci in f.classes:
                for ms in ci.members.values():
                    m = ms[0]
                    if m.expr is None or m.expr.t != "new" or not m.expr.a[2]:
                        continue
                    for el in m.expr.a[2]:
                        if el[0] != "item" or el[1].t != "new" or not el[1].a[0]:
                            continue
                        rtype = el[1].a[0].split(".")[-1]
                        recs = [c for c in self.idx.classes(rtype) if c.record_params]
                        if not recs:
                            continue
                        params = [p for p, _ in recs[0].record_params]
                        tidx = [k for k, p in enumerate(params) if p in self._TEXT_PARAMS]
                        if not tidx:
                            continue
                        o = self.idx.ev(el[1], {}, m.cls)
                        if not isinstance(o, Obj):
                            continue
                        vals = [self.idx.ev(a, o.env, m.cls) for a in o.args]
                        for k in tidx:
                            if k >= len(vals) or not isinstance(vals[k], str) \
                                    or not self.is_text(vals[k]) or " " not in vals[k]:
                                continue
                            ctx = ", ".join(f"{params[j]}={to_text(vals[j])}" for j in range(len(vals))
                                            if j != k and j < len(params))
                            owner = self.owners.of_class(ci)
                            section = ("Teyvat frame: Ancient dialogue" if "Teyvat" in f.path.as_posix()
                                       else f"Text data ({ci.name}.{m.name})")
                            self.add(owner, section, {
                                "id": f"{ci.name}.{m.name}:{el[1].line}", "name": to_text(vals[0]),
                                "kind": f"{rtype}.{params[k]}", "text": clean(vals[k]),
                                "source": f"{rel(f.path)}:{el[1].line}", "context": ctx})

    # -- the Architect's finale lines (build_pck.ps1 writes them into the pck)
    def architect(self) -> None:
        if not BUILD_PCK.exists():
            return
        for k, line in enumerate(BUILD_PCK.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r'\s*"THE_ARCHITECT\.talk\.(KLEEMOD-\w+)\.([\w-]+)\.(\w+)"\s*:\s*"(.*)",?\s*$',
                         line)
            if not m:
                continue
            owner = ARCHITECT_CHAR.get(m.group(1), "Shared")
            who = {"ancient": "The Architect", "char": owner, "next": "button"}.get(m.group(3), m.group(3))
            self.add(owner, "Architect finale", {
                "id": f"THE_ARCHITECT.{m.group(1)}.{m.group(2)}.{m.group(3)}", "name": who,
                "kind": f"finale {m.group(3)}", "text": json.loads('"' + m.group(4) + '"'),
                "source": f"{rel(BUILD_PCK)}:{k}"})

    # -- leftovers: player-looking literals that no extractor read
    _SKIP_CTX = re.compile(
        r"(Log\.\w+|GD\.\w+|Exception|Assert\w*|Debug\.\w+|Console\.\w+|HarmonyPatch|"
        r"Obsolete|Regex\w*|Fail\w*|Warn\w*|Error\w*|Trace\w*|Throw\w*|nameof|AccessTools\.\w+|"
        r"GetNode\w*|FindChild|Environment\.\w+|Reason|Skip|Note|Describe\w*|Diag\w*|"
        r"Telemetry\w*|Record\w*|Report\w*)\s*[(<]")

    _DIAG_IDS = re.compile(r"^(Log|GD|Debug|Console|Trace|Assert|Fail|Warn|Error|Throw|throw|"
                           r"nameof|AccessTools|HarmonyPatch|Obsolete|Regex|Diag\w*|Telemetry\w*|"
                           r"\w*Exception|Environment|GetNode\w*|FindChild|Note|Reason|Skip|"
                           r"Describe\w*|Record\w*|Report\w*|LogLine|Print\w*)$")

    def in_diagnostic_statement(self, f: CsFile, ti: int) -> bool:
        """Is token `ti` inside a log call, an exception, an attribute or a
        diagnostic helper? Walks back to the start of its statement."""
        depth = 0
        k = ti - 1
        while k >= 0:
            t = f.toks[k]
            if t.kind == "op":
                if t.val in (")", "]"):
                    depth += 1
                elif t.val in ("(", "["):
                    if depth == 0:
                        # the callee or attribute this literal is an argument of
                        j = k - 1
                        while j >= 0 and f.toks[j].kind == "op" and f.toks[j].val in (">", "<"):
                            j -= 1
                        if j >= 0 and f.toks[j].kind == "id" and self._DIAG_IDS.match(f.toks[j].val):
                            return True
                        if t.val == "[" and (j < 0 or f.toks[j].kind == "op"):
                            return True          # an attribute
                    else:
                        depth -= 1
                elif t.val in (";", "{", "}") and depth == 0:
                    return False
            elif t.kind == "id" and depth == 0 and self._DIAG_IDS.match(t.val)                     and k + 1 < len(f.toks) and f.toks[k + 1].val in (".", "("):
                return True
            k -= 1
        return False

    def leftovers(self) -> None:
        self.gaps["unextracted_literals"] = []
        for f in self.files:
            if any(p in ("Diagnostics", "RunStats") for p in f.path.parts):
                continue
            for ti, t in enumerate(f.toks):
                if t.kind not in ("str", "istr") or (f.path, t.pos) in self.idx.consumed:
                    continue
                text = t.val if t.kind == "str" else "".join(
                    p if isinstance(p, str) else "{" + p[3] + "}" for p in t.val)
                plain = strip_markup(text).strip()
                if " " not in plain or len(re.findall(r"[A-Za-z][a-z']+", plain)) < 3 \
                        or "res://" in plain:
                    continue
                if re.search(r"\b(null|NRE|dll|pck|json|Harmony|BaseLib|ModelDb|LocTable|"
                             r"Godot|rng|EB-\d+|R\d{3})\b", plain):
                    continue
                if self.in_diagnostic_statement(f, ti):
                    continue
                if not (plain[:1].isupper() or "[gold]" in text or plain.endswith((".", "!", "?"))):
                    continue
                ci = self.class_at(f, t.pos)
                owner = self.owners.of_class(ci) if ci else (owner_of_path(f.path) or "Shared")
                if "Abyss" in f.path.as_posix():
                    owner = "Shared"
                src = f"{rel(f.path)}:{t.line}"
                self.gaps["unextracted_literals"].append({"source": src, "owner": owner,
                                                          "text": clean(plain)})
                self.add(owner, "Other UI text (code literals)", {
                    "id": f"{f.path.stem}:{t.line}", "name": ci.name if ci else f.path.stem,
                    "kind": "code literal", "text": clean(plain), "source": src,
                    "context": "Found by the literal sweep, not a loc extractor; may be part of "
                               "a line built in code."})

    def run(self) -> dict:
        for step in (self.cards, self.other_cards, self.loc_classes, self.starters,
                     self.stories, self.abyss, self.dictionaries, self.code_tips,
                     self.record_lists, self.architect, self.leftovers):
            try:
                step()
            except Exception as exc:          # noqa: BLE001 - one step must not sink the rest
                import traceback
                self.gaps["eval_errors"].append(
                    f"step {step.__name__} failed: {exc!r}\n{traceback.format_exc(limit=4)}")
        chars = {}
        for c in CHARACTERS:
            secs = {k: v for k, v in self.out.get(c, {}).items() if v}
            chars[c] = dict(sorted(secs.items(), key=lambda kv: _section_rank(kv[0])))
        gaps = dict(self.gaps)
        gaps["counts"] = {k: len(v) for k, v in self.gaps.items() if isinstance(v, list)}
        return {"generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
                "commit": _commit(), "characters": chars, "gaps": gaps}


_ORDER = ["Character select & profile", "Story: intro", "Starter deck", "Cards", "Ancient cards",
          "Other cards (tokens, curses, options)", "Relics", "Potions", "Powers & statuses",
          "Enchantments", "Keyword & glossary tips", "Story events", "Co-op story event",
          "Ancient dialogue", "Combat lines (barks)", "Co-op pair lines", "Architect finale",
          "Prompts & screen text"]


def _section_rank(name: str) -> tuple:
    if name in _ORDER:
        return (0, _ORDER.index(name), name)
    for k, pre in enumerate(("Companion cards", "Spiral Abyss", "Teyvat", "Loc rows", "Other")):
        if name.startswith(pre):
            return (k + 1, 0, name)
    return (9, 0, name)


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def census() -> dict:
    return Census().run()


def summary(data: dict) -> str:
    lines = []
    for c, secs in data["characters"].items():
        lines.append(f"{c}: {sum(len(v) for v in secs.values())}")
        for s, items in secs.items():
            lines.append(f"    {len(items):5d}  {s}")
    lines.append("gaps: " + ", ".join(f"{k} {v}" for k, v in data["gaps"]["counts"].items()))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Every piece of player-facing text, per character.")
    ap.add_argument("--out", required=True, help="the JSON file to write")
    ap.add_argument("--summary", action="store_true", help="print item counts per section")
    args = ap.parse_args(argv)
    data = census()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(len(v) for s in data["characters"].values() for v in s.values())
    print(f"wrote {out} ({total} items)")
    if args.summary:
        print(summary(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
