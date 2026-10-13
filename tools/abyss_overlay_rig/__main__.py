"""Render the Spiral Abyss Blessing screen with MegaDot, at 1920x1080.

    python -m tools.abyss_overlay_rig --out <scratch dir> [--art-root <ImageGen/images>]

A scratch MegaDot C# project is written under ``<out>/_project``: it compiles
the SAME view file the mod ships (``klee-mod/KleeCode/Abyss/AbyssOverlayView.cs``),
the paper's strings (``AbyssEntries.cs``, ``Elements/Element.cs``) and the rig
driver (``godot/RigMain.cs``). The driver loads the game's pack READ-ONLY for
the game's fonts, builds the screen for each state below, and saves one PNG
per state to ``<out>``. Nothing touches the install, the pck build or a
running game. Art is read from the main checkout's gitignored ``ImageGen/``
by absolute path (``--art-root``); nothing is copied into the repo.

The driver prints each card's rect and whether it leaves the screen; the run
fails if any card is clipped.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2")

# Blessing / Shadow save numbers (klee-mod/KleeCode/Abyss/AbyssEntries.cs).
LEY_LINE, ABYSSAL_MOON, MOONLIT_REST, FIRST_STRIKE = 1, 2, 3, 4
ELEMENTAL_BURST, RESONANCE, JADE_SHIELD, FATEFUL_FORTUNE = 5, 6, 7, 8
CLOCK, MAGE_SHIELD, SHEER_COLD, ELEMENTAL_MARK = 1, 2, 3, 4
HERALD, RALLY, RIPTIDE, FATUI = 5, 6, 7, 8


def megadot() -> Path:
    env = os.environ.get("GITS_MEGADOT")
    if env:
        return Path(env)
    text = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
    m = re.search(r"\[string\]\$MegaDot = '([^']+)'", text)
    if not m:
        raise SystemExit("cannot find the MegaDot path in tools/build_pck.ps1; set GITS_MEGADOT")
    return Path(m.group(1))


def states(art_root: Path) -> list[dict]:
    klee = str(art_root / "ui" / "char_icon.png")
    kokomi = str(art_root / "kokomi" / "ui" / "char_icon.png")
    return [
        # Neow, solo, first visit: no strip. The longest Shadow text (Mage
        # Shield) and the longest Blessing text (The Ley Line) on one page.
        {"name": "solo_act1", "act": 0,
         "blessings": [LEY_LINE, MOONLIT_REST, FIRST_STRIKE],
         "shadows": [MAGE_SHIELD, SHEER_COLD, RIPTIDE], "focused": 1},
        # Act 2, co-op, mid-vote: each player's marker under their card, the
        # local vote outlined, the strip showing one Blessing and one Shadow.
        {"name": "coop_vote_act2", "act": 1,
         "blessings": [ABYSSAL_MOON, RESONANCE, JADE_SHIELD],
         "shadows": [ELEMENTAL_MARK, HERALD, FATUI],
         "taken_blessings": [MOONLIT_REST], "taken_shadows": [MAGE_SHIELD],
         "chosen": 0, "focused": 2, "votes": [[klee], [], [kokomi]]},
        # The same vote resolved: the result line.
        {"name": "coop_result_act2", "act": 1,
         "blessings": [ABYSSAL_MOON, RESONANCE, JADE_SHIELD],
         "shadows": [ELEMENTAL_MARK, HERALD, FATUI],
         "taken_blessings": [MOONLIT_REST], "taken_shadows": [MAGE_SHIELD],
         "chosen": 2, "votes": [[klee], [], [kokomi]],
         "result": "The vote split; the draw gave Jade Shield."},
        # Act 3 with a full strip (two of each).
        {"name": "solo_act3_strip", "act": 2,
         "blessings": [ELEMENTAL_BURST, FATEFUL_FORTUNE, ABYSSAL_MOON],
         "shadows": [CLOCK, RALLY, ELEMENTAL_MARK],
         "taken_blessings": [MOONLIT_REST, JADE_SHIELD],
         "taken_shadows": [MAGE_SHIELD, RIPTIDE]},
    ]


def write_project(work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    nupkgs = megadot().parent / "GodotSharp" / "Tools" / "nupkgs"
    (work / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="AbyssOverlayRig"\n'
        'run/main_scene="res://main.tscn"\n\n[display]\n\n'
        "window/size/viewport_width=480\nwindow/size/viewport_height=270\n\n"
        '[dotnet]\n\nproject/assembly_name="AbyssOverlayRig"\n',
        encoding="utf-8", newline="\n")
    (work / "main.tscn").write_text(
        '[gd_scene load_steps=2 format=3]\n\n'
        '[ext_resource type="Script" path="res://RigMain.cs" id="1"]\n\n'
        '[node name="RigMain" type="Node"]\nscript = ExtResource("1")\n',
        encoding="utf-8", newline="\n")
    abyss = ROOT / "klee-mod" / "KleeCode" / "Abyss"
    links = [abyss / "AbyssOverlayView.cs", abyss / "AbyssEntries.cs",
             ROOT / "klee-mod" / "KleeCode" / "Elements" / "Element.cs"]
    compile_items = "\n".join(
        f'    <Compile Include="{p}" Link="Linked/{p.name}" />' for p in links)
    (work / "AbyssOverlayRig.csproj").write_text(
        '<Project Sdk="Godot.NET.Sdk/4.5.1">\n  <PropertyGroup>\n'
        "    <TargetFramework>net8.0</TargetFramework>\n"
        "    <Nullable>enable</Nullable>\n    <LangVersion>latest</LangVersion>\n"
        "    <EnableDynamicLoading>true</EnableDynamicLoading>\n"
        "    <RestoreAdditionalProjectSources>"
        f"{nupkgs}</RestoreAdditionalProjectSources>\n"
        "  </PropertyGroup>\n  <ItemGroup>\n"
        f"{compile_items}\n  </ItemGroup>\n</Project>\n",
        encoding="utf-8", newline="\n")
    (work / "nuget.config").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<configuration>\n  <packageSources>\n'
        f'    <add key="megadot" value="{nupkgs}" />\n'
        '    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />\n'
        "  </packageSources>\n</configuration>\n",
        encoding="utf-8", newline="\n")
    (work / "RigMain.cs").write_text(
        (HERE / "godot" / "RigMain.cs").read_text(encoding="utf-8"),
        encoding="utf-8", newline="\n")


def run(cmd: list[str], cwd: Path, timeout: int = 900) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    log = proc.stdout + proc.stderr
    if proc.returncode != 0:
        raise SystemExit(f"{cmd[0]} failed ({proc.returncode}):\n{log[-4000:]}")
    return log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--art-root", type=Path,
                    default=ROOT.parent / "GItS" / "ImageGen" / "images")
    args = ap.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    work = out / "_project"
    write_project(work)
    run(["dotnet", "build", "-nologo", "-v", "q"], work)
    run([str(megadot()), "--headless", "--path", str(work), "--import"], work)
    art = args.art_root.resolve()
    job = {
        "Out": out.as_posix(),
        "GamePck": (GAME / "SlayTheSpire2.pck").as_posix(),
        "ArtRoot": art.as_posix(),
        "Backdrop": (art / "teyvat" / "map_bgs" / "mondstadt" / "map_middle_mondstadt.png").as_posix(),
        "States": [{k[0].upper() + "".join(p.title() for p in k.split("_"))[1:]: v
                    for k, v in s.items()} for s in states(art)],
    }
    (work / "job.json").write_text(json.dumps(job), encoding="utf-8")
    log = run([str(megadot()), "--path", str(work), "--", str(work / "job.json")], work)
    rig = [line for line in log.splitlines() if line.startswith("RIG|")]
    print("\n".join(rig))
    if "RIG|done" not in log:
        print(log[-4000:], file=sys.stderr)
        return 1
    return 1 if any("clipped=True" in line for line in rig) else 0


if __name__ == "__main__":
    raise SystemExit(main())
