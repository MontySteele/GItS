"""A small, honest reader for Godot 4 text scenes (.tscn) and resources (.tres).

This is NOT a Godot parser. It reads the ~10% of the format the pck-src scenes
actually use, and it is written so that anything it does not understand is
carried through as raw text rather than silently dropped -- a reader that
quietly loses a section would make the gates above it report "clean" about a
file they never saw.

Format facts this relies on (all observable in klee-mod/pck-src/*.tscn):

  * a file is a sequence of ``[section key=value ...]`` headers, each followed
    by ``key = value`` property lines;
  * a value may span lines when it opens a ``{``, ``[`` or ``(``, so property
    accumulation is bracket-balanced rather than line-based;
  * resources are referenced as ``ExtResource("id")`` / ``SubResource("id")``;
  * ``StringName`` literals are written ``&"name"``;
  * node identity is ``[node name="X" type="T" parent="A/B"]`` where ``parent``
    is omitted for the root and is ``"."`` for a direct child of the root.

`load_steps` is read but deliberately NOT trusted as a hard invariant -- see
`Scene.declared_load_steps`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_SECTION = re.compile(r"^\[([A-Za-z_][A-Za-z0-9_]*)(?:\s+(.*?))?\]\s*$")
_ATTR = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:[^"\\]|\\.)*"|[^\s\]]+)')
_PROP_START = re.compile(r'^([A-Za-z_][A-Za-z0-9_/\.]*)\s*=\s*(.*)$')

EXT_REF = re.compile(r'ExtResource\(\s*"([^"]+)"\s*\)')
SUB_REF = re.compile(r'SubResource\(\s*"([^"]+)"\s*\)')
STRING_NAME = re.compile(r'&"((?:[^"\\]|\\.)*)"')


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


@dataclass
class Section:
    kind: str
    attrs: dict[str, str]
    props: dict[str, str]
    line: int
    body: str

    def ref_ids(self) -> tuple[set[str], set[str]]:
        """(ext ids, sub ids) referenced anywhere in this section's body."""
        return set(EXT_REF.findall(self.body)), set(SUB_REF.findall(self.body))


@dataclass
class Node:
    name: str
    type: str
    parent: str | None
    props: dict[str, str]
    line: int
    #: the node header's own key="value" pairs, so a consumer can see
    #: `instance=ExtResource("...")` and `index=` without re-reading the text.
    attrs: dict[str, str] = field(default_factory=dict)

    @property
    def is_instance(self) -> bool:
        return "instance" in self.attrs

    @property
    def path(self) -> str:
        """The node's path from the scene root, root itself being ``"."``."""
        if self.parent is None:
            return "."
        if self.parent == ".":
            return self.name
        return f"{self.parent}/{self.name}"


@dataclass
class Scene:
    path: Path
    kind: str                       # "gd_scene" | "gd_resource" | other
    header_attrs: dict[str, str]
    sections: list[Section]
    ext_resources: dict[str, Section] = field(default_factory=dict)
    sub_resources: dict[str, Section] = field(default_factory=dict)
    nodes: list[Node] = field(default_factory=list)
    #: sections that are neither header, ext_resource, sub_resource, node, nor
    #: [resource] -- kept so a gate can say "I did not understand this".
    unknown: list[Section] = field(default_factory=list)

    # -- header ------------------------------------------------------------
    @property
    def declared_load_steps(self) -> int | None:
        raw = self.header_attrs.get("load_steps")
        return int(raw) if raw and raw.isdigit() else None

    @property
    def expected_load_steps(self) -> int:
        """Godot writes ``len(ext) + len(sub) + 1``.

        ADVISORY only. In Godot 4 the value feeds the loader's progress
        counter, not correctness -- a too-large number is harmless, which is
        why the gate that checks it emits a WARNING and not an ERROR. Two
        scenes in this repo already disagree with it (see the lane handoff).
        """
        return len(self.ext_resources) + len(self.sub_resources) + 1

    # -- nodes -------------------------------------------------------------
    def node_paths(self) -> set[str]:
        return {n.path for n in self.nodes}

    def unique_names(self) -> set[str]:
        """Nodes marked ``unique_name_in_owner = true`` -- the ``%Name`` form."""
        return {
            n.name
            for n in self.nodes
            if n.props.get("unique_name_in_owner", "").strip() == "true"
        }

    def find_node(self, path: str) -> Node | None:
        for node in self.nodes:
            if node.path == path:
                return node
        return None

    # -- animation ---------------------------------------------------------
    def animation_libraries(self) -> dict[str, dict[str, str]]:
        """sub_resource id -> {animation name: sub_resource id of the Animation}."""
        out: dict[str, dict[str, str]] = {}
        for sub_id, section in self.sub_resources.items():
            if section.attrs.get("type") != "AnimationLibrary":
                continue
            data = section.props.get("_data", "")
            entries: dict[str, str] = {}
            for match in re.finditer(
                r'&"((?:[^"\\]|\\.)*)"\s*:\s*SubResource\(\s*"([^"]+)"\s*\)', data
            ):
                entries[match.group(1)] = match.group(2)
            out[sub_id] = entries
        return out

    def animation_names(self) -> set[str]:
        """Every animation name declared by any library in this scene."""
        names: set[str] = set()
        for entries in self.animation_libraries().values():
            names.update(entries)
        return names

    def animation_players(self) -> list[Node]:
        return [n for n in self.nodes if n.type == "AnimationPlayer"]

    def animation_trees(self) -> list[Node]:
        return [n for n in self.nodes if n.type == "AnimationTree"]

    def animation_node_animations(self) -> dict[str, str]:
        """sub_resource id -> the animation StringName it plays."""
        out = {}
        for sub_id, section in self.sub_resources.items():
            if section.attrs.get("type") != "AnimationNodeAnimation":
                continue
            match = STRING_NAME.search(section.props.get("animation", ""))
            if match:
                out[sub_id] = match.group(1)
        return out

    def state_machines(self) -> dict[str, tuple[set[str], list[tuple[str, str]]]]:
        """sub id -> (state names, [(from, to), ...]) for each state machine."""
        out: dict[str, tuple[set[str], list[tuple[str, str]]]] = {}
        for sub_id, section in self.sub_resources.items():
            if section.attrs.get("type") != "AnimationNodeStateMachine":
                continue
            states = {
                m.group(1)
                for m in re.finditer(r"^states/([^/]+)/", section.body, re.MULTILINE)
            }
            transitions: list[tuple[str, str]] = []
            raw = section.props.get("transitions", "")
            # transitions = ["a", "b", SubResource("T"), "b", "c", ...] -- flat
            # triples of (from, to, transition resource). The SubResource id is
            # ALSO a quoted string, so it must be removed before the state
            # names are read positionally; not doing that pairs every state
            # with a transition id and turns the whole check into noise.
            flat = SUB_REF.sub("", raw)
            names = re.findall(r'"([^"]*)"', flat)
            for i in range(0, len(names) - 1, 2):
                transitions.append((names[i], names[i + 1]))
            out[sub_id] = (states, transitions)
        return out

    def animation_track_paths(self) -> list[tuple[str, str, str]]:
        """[(animation sub id, raw NodePath, node part)] for every value track."""
        out: list[tuple[str, str, str]] = []
        for sub_id, section in self.sub_resources.items():
            if section.attrs.get("type") != "Animation":
                continue
            for match in re.finditer(
                r'tracks/\d+/path\s*=\s*NodePath\("([^"]*)"\)', section.body
            ):
                raw = match.group(1)
                node_part = raw.split(":", 1)[0]
                out.append((sub_id, raw, node_part))
        return out


def _split_sections(text: str) -> list[Section]:
    lines = text.splitlines()
    sections: list[Section] = []
    current: Section | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current, buffer
        if current is not None:
            current.body = "\n".join(buffer)
            current.props = _parse_props(buffer)
            sections.append(current)
        current, buffer = None, []

    for index, line in enumerate(lines, start=1):
        match = _SECTION.match(line)
        if match:
            flush()
            attrs = {
                m.group(1): _unquote(m.group(2))
                for m in _ATTR.finditer(match.group(2) or "")
            }
            current = Section(match.group(1), attrs, {}, index, "")
            continue
        if current is not None:
            buffer.append(line)
    flush()
    return sections


def _balanced(value: str) -> bool:
    """True when every bracket opened in `value` has been closed.

    Quote-aware: a ``(`` inside a string literal (Godot writes
    ``"Vector2(0, 0)"`` inside dictionaries) must not hold the accumulator
    open.
    """
    depth = 0
    in_string = False
    escape = False
    for char in value:
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth -= 1
    return depth <= 0


def _parse_props(lines: list[str]) -> dict[str, str]:
    props: dict[str, str] = {}
    key: str | None = None
    acc: list[str] = []
    for line in lines:
        if key is None:
            match = _PROP_START.match(line)
            if not match:
                continue
            key, acc = match.group(1), [match.group(2)]
            if _balanced(match.group(2)):
                props[key] = match.group(2).strip()
                key, acc = None, []
            continue
        acc.append(line)
        joined = "\n".join(acc)
        if _balanced(joined):
            props[key] = joined.strip()
            key, acc = None, []
    if key is not None:                     # unterminated value: keep what we saw
        props[key] = "\n".join(acc).strip()
    return props


def parse(path: Path, text: str | None = None) -> Scene:
    """Read one .tscn/.tres. `text` overrides the file body (tests, fixtures)."""
    if text is None:
        text = path.read_text(encoding="utf-8")
    sections = _split_sections(text)
    header_kind, header_attrs = "", {}
    body_sections: list[Section] = []
    for section in sections:
        if section.kind in ("gd_scene", "gd_resource") and not header_kind:
            header_kind, header_attrs = section.kind, dict(section.attrs)
            continue
        body_sections.append(section)

    scene = Scene(path, header_kind, header_attrs, body_sections)
    for section in body_sections:
        if section.kind == "ext_resource":
            scene.ext_resources[section.attrs.get("id", f"?{section.line}")] = section
        elif section.kind == "sub_resource":
            scene.sub_resources[section.attrs.get("id", f"?{section.line}")] = section
        elif section.kind == "node":
            scene.nodes.append(
                Node(
                    name=section.attrs.get("name", ""),
                    type=section.attrs.get("type", ""),
                    parent=section.attrs.get("parent"),
                    props=section.props,
                    line=section.line,
                    attrs=dict(section.attrs),
                )
            )
        elif section.kind in ("resource", "editable", "connection"):
            continue
        else:
            scene.unknown.append(section)
    return scene


def iter_scene_files(root: Path) -> list[Path]:
    """Every .tscn/.tres under `root`, in a stable order."""
    return sorted(
        [p for p in root.rglob("*") if p.suffix in (".tscn", ".tres") and p.is_file()],
        key=lambda p: p.as_posix(),
    )
