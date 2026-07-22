"""Extract a base-game character's card pool from the local sts2.dll.

WHY THIS EXISTS
---------------
tier0's `ref_ironclad` is a SIX-card calibration construct, not a card
pool -- `tier05/rewards.character_pool` special-cases him to his own
`archetype_package`. That makes him a fine 3.0 scoring anchor and a
useless CONTENT baseline: any claim of the form "our pool has too few
defensive cards / too many commons / weak block numbers" has had nothing
real to be measured against. This produces that reference.

First run (2026-07-21) settled one such claim immediately: real Ironclad
is 15% defensive vs Klee's 17%, with a 51% vs 52% chance a reward screen
shows no defence at all. Low defensive density is NORMAL StS2, not a Klee
defect -- while his block-per-energy floor (5.0, a Defend) is far above
hers (2.0). Density was fine; quality was not.

IP / REPO RULE  (.gitignore:28, csharp-build-spec.md §0.3)
----------------------------------------------------------
Decompiled base-game material is REFERENCE ONLY and stays out of the
repo. THIS SCRIPT contains no game data and is safe to commit; everything
it WRITES is game data and must not be. Output therefore goes to
`game_ref/`, which is gitignored. ILSpy's full temporary source tree is also
deleted after each run. The extract is a local build artifact, never a
checked-in asset.

USAGE
-----
    python tools/extract_base_game_pool.py Ironclad
    python tools/extract_base_game_pool.py Silent --json game_ref/silent.json
    python tools/extract_base_game_pool.py Ironclad --emit-sheet

Requires: ilspycmd on PATH (`dotnet tool install -g ilspycmd`) and a
local install; the game path is read from klee-mod/local.props so there
is exactly one place a machine path is configured.

--emit-sheet
------------
Writes a Tier 0 card sheet (`game_ref/<char>-cards.yaml`) plus its upgrade
companion, so the real pool can be SCORED on the same seven axes as Klee
and Furina instead of against the six-card `ref_ironclad` construct. If the
conventional local supplement (`game_ref/<char>_pool_pass4.yaml`) exists, its
rows are validated and their upgrade deltas are derived from the same DLL in
that pass. Both outputs remain gitignored reference artifacts.

Two rules govern that translation and they are the reason this mode is
worth having at all:

  PARITY, NOT FIDELITY. Klee is measured in a world with no relics, no
  potions and no events. Nothing here invents any of those.

  NEVER APPROXIMATE. A card whose behaviour the Tier 0 DSL cannot express
  is EXCLUDED with a stated reason, never rounded off into the nearest op.
  A silent approximation would bias the very comparison this exists to
  make, so the emitted/excluded split is itself a headline result: it
  measures how much of a real base-game pool our DSL can even hold.

The translator is STRUCTURAL on purpose -- it recognises decompiled
statement shapes, never card names. There is no per-card table here, so
this file stays free of base-game data (see the IP note above) and a card
can only be emitted if its actual shape was understood.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCAL_PROPS = REPO / "klee-mod" / "local.props"
OUT_DIR = REPO / "game_ref"
CARD_NS = "MegaCrit.Sts2.Core.Models.Cards."
POOL_NS = "MegaCrit.Sts2.Core.Models.CardPools."

# `: base(COST, CardType.X, CardRarity.Y, ...)` -- the CardModel ctor.
CTOR = re.compile(r":\s*base\(\s*(-?\d+)\s*,\s*CardType\.(\w+)\s*,\s*"
                  r"CardRarity\.(\w+)")
# `new DamageVar(6m, ...)` / `new BlockVar(5m, ...)` / `new MagicVar(...)`
VAR = re.compile(r"new (\w+)Var\(\s*(-?[\d.]+)m")
# `DynamicVars.Damage.UpgradeValueBy(2m)`
UPG = re.compile(r"DynamicVars\.(\w+)\.UpgradeValueBy\((-?[\d.]+)m\)")
# Every `SomethingCmd.Method(` call in the body -- the effect vocabulary.
CMD = re.compile(r"\b(\w+Cmd)\.(\w+)\(")
# The power vocabulary. Powers are reached three ways and all three matter:
#   PowerCmd.Apply<StrengthPower>(...)     -- application
#   new PowerVar<StrengthPower>(2m)        -- the canonical amount
#   HoverTipFactory.FromPower<XPower>()    -- referenced-but-not-applied
# so match any `<...Power>` type argument rather than one call shape.
POWER = re.compile(r"<(\w+Power)>")


def game_dll() -> Path:
    """Read GameDir from local.props so machine paths live in one place."""
    if not LOCAL_PROPS.exists():
        sys.exit(f"missing {LOCAL_PROPS} -- copy local.props.example first")
    m = re.search(r"<GameDir>(.*?)</GameDir>", LOCAL_PROPS.read_text())
    if not m:
        sys.exit("no <GameDir> in local.props")
    game_dir = Path(m.group(1)).expanduser()
    resource_roots = (
        game_dir,
        game_dir / "SlayTheSpire2.app" / "Contents" / "Resources",
    )
    data_dirs = (
        "data_sts2_windows_x86_64",
        "data_sts2_macos_arm64",
        "data_sts2_macos_x86_64",
    )
    candidates = [root / data_dir / "sts2.dll"
                  for root in resource_roots for data_dir in data_dirs]
    for dll in candidates:
        if dll.exists():
            return dll
    searched = "\n  ".join(str(path) for path in candidates)
    sys.exit(f"sts2.dll not found; searched:\n  {searched}")


def _run_ilspy_project(dll: Path, output_dir: Path) -> None:
    """Decompile the assembly once into an ephemeral source tree.

    Starting ilspycmd dominates runtime: loading and analysing sts2.dll once
    per card took roughly eight minutes for Ironclad. Project mode does the
    same work once (about 13 seconds on the reference machine), after which
    individual types are ordinary file reads. The caller owns ``output_dir``;
    production uses a TemporaryDirectory so decompiled game source never
    becomes a persistent repository artifact.
    """
    try:
        # Resolving the game's adjacent assemblies is required for ILSpy to
        # reconstruct async methods. Without it, OnPlay is left as a generated
        # state-machine wrapper and the structural translator sees no effects.
        p = subprocess.run([
            "ilspycmd", "--disable-updatecheck",
            "-r", str(dll.parent),
            "--project", "--nested-directories",
            "-o", str(output_dir),
            str(dll),
        ], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        sys.exit("ilspycmd not on PATH -- dotnet tool install -g ilspycmd")
    except subprocess.TimeoutExpired:
        sys.exit("ilspycmd timed out while decompiling sts2.dll")
    if p.returncode:
        sys.exit(f"ilspycmd failed ({p.returncode}):\n{p.stderr}")


def _read_decompiled_type(root: Path, type_name: str) -> str:
    """Read one project-mode type, rejecting same-name namespace collisions."""
    namespace, short_name = type_name.rsplit(".", 1)
    namespace_decl = re.compile(
        rf"\bnamespace\s+{re.escape(namespace)}(?:;|\s*\{{)"
    )
    matches: list[tuple[Path, str]] = []
    for path in root.rglob(f"{short_name}.cs"):
        src = path.read_text()
        if namespace_decl.search(src):
            matches.append((path, src))
    if not matches:
        sys.exit(f"{type_name} not found in the decompiled project")
    if len(matches) > 1:
        paths = "\n  ".join(str(path.relative_to(root)) for path, _ in matches)
        sys.exit(f"multiple decompiled files matched {type_name}:\n  {paths}")
    return matches[0][1]


def decompile_character(
        dll: Path, character: str) -> tuple[list[str], dict[str, str]]:
    """Return the pool's card names and sources from one ILSpy invocation."""
    started = time.monotonic()
    print("  decompiling sts2.dll once...", file=sys.stderr, flush=True)
    with tempfile.TemporaryDirectory(prefix="gits-ilspy-") as temp_dir:
        root = Path(temp_dir)
        _run_ilspy_project(dll, root)
        pool_src = _read_decompiled_type(root, f"{POOL_NS}{character}CardPool")
        names = re.findall(r"ModelDb\.Card<(\w+)>", pool_src)
        if not names:
            sys.exit(f"no cards found in {character}CardPool -- check the name")
        sources = {
            name: _read_decompiled_type(root, f"{CARD_NS}{name}")
            for name in names
        }
    elapsed = time.monotonic() - started
    print(f"  decompiled and loaded {len(names)} card types in {elapsed:.1f}s",
          file=sys.stderr)
    return names, sources


def parse_card(src: str, name: str) -> dict | None:
    m = CTOR.search(src)
    if not m:
        return None
    cmds = sorted({f"{a}.{b}" for a, b in CMD.findall(src)})
    powers = sorted(set(POWER.findall(src)))
    return {
        "name": name,
        "cost": int(m.group(1)),
        "type": m.group(2),
        "rarity": m.group(3),
        "vars": {k: float(v) for k, v in VAR.findall(src)},
        "upgrades": {k: float(v) for k, v in UPG.findall(src)},
        "cmds": cmds,
        "powers": powers,
        "exhaust": "Exhaust" in src,
        "innate": "Innate" in src,
        "body_lines": src.count("\n"),
    }


def defensive(card: dict) -> bool:
    return ("Block" in card["vars"]
            or any(c.startswith("BlockCmd") for c in card["cmds"])
            or any("Heal" in c for c in card["cmds"]))


def summarize(cards: list[dict], character: str) -> None:
    n = len(cards)
    print(f"\n=== {character}: {n} cards ===")
    print("  rarity:", dict(Counter(c["rarity"] for c in cards)))
    print("  type  :", dict(Counter(c["type"] for c in cards)))

    dfn = [c for c in cards if defensive(c)]
    print(f"\n  defensive: {len(dfn)}/{n} = {len(dfn)/n:.0%}")
    odds = {"Common": 0.60, "Uncommon": 0.35, "Rare": 0.05}
    by_r: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for c in cards:
        by_r[c["rarity"]][1] += 1
        if defensive(c):
            by_r[c["rarity"]][0] += 1
    p_any = 0.0
    for rar in ("Basic", "Common", "Uncommon", "Rare", "Ancient", "Special"):
        if rar not in by_r:
            continue
        d, t = by_r[rar]
        p_any += odds.get(rar, 0.0) * (d / t)
        print(f"    {rar:<10}{d:>4}/{t:<4} {d/t:>5.0%}")
    print(f"  P(offer is defensive) = {p_any:.1%}   "
          f"P(3-card screen has none) = {(1 - p_any) ** 3:.0%}")

    bpe = sorted((c["vars"]["Block"] / c["cost"], c["name"], c["cost"],
                  c["vars"]["Block"])
                 for c in cards if "Block" in c["vars"] and c["cost"] > 0)
    if bpe:
        print(f"\n  block per energy: floor {bpe[0][0]:.1f} ({bpe[0][1]})  "
              f"median {bpe[len(bpe)//2][0]:.1f}  "
              f"ceiling {bpe[-1][0]:.1f} ({bpe[-1][1]})")

    vocab = Counter(cmd for c in cards for cmd in c["cmds"])
    print(f"\n  effect vocabulary: {len(vocab)} distinct Cmd calls")
    for cmd, k in vocab.most_common(15):
        print(f"    {k:>3}x  {cmd}")
    pw = Counter(p for c in cards for p in c["powers"])
    print(f"  powers referenced: {len(pw)} distinct")


# ---------------------------------------------------------------------------
# --emit-sheet: decompiled card -> Tier 0 DSL sheet row
# ---------------------------------------------------------------------------
#
# The vocabulary below is the WHOLE contract. Anything outside it excludes
# the card. Keeping it as data (rather than scattered `if`s) is what makes
# the exclusion list auditable: when tier0 grows an op or a power, one entry
# here moves a card from `excluded:` to the sheet, and the count moves with
# it.

ID_PREFIX = "ic_"          # keeps base-game ids out of the Klee/Furina
                           # namespace; docs/reserved-card-names.txt records
                           # the reverse direction (our names vs theirs).

# Powers tier0/engine/powers.py actually implements. Everything else
# (Barricade, DarkEmbrace, Juggernaut, ...) is a real mechanic we do not
# have; those cards leave rather than pretend.
#
# THIS SET IS THE DIAL. The emitted/excluded split is a measurement OF THE
# DSL, not a fact about Ironclad, so it is only meaningful next to the set
# it was measured against. Widen this table as tier0 grows powers (the
# base-game parity work lives in tier0/engine/refpowers.py) and re-run:
# every entry added here moves cards out of `excluded:` and the headline
# number moves with it.
#
# Every entry below names a power tier0 implements AND that has been through
# an adversarial verification pass against its decompiled source. The two
# conditions are separate on purpose: refpowers.py implements more powers than
# appear here, and an implementation nobody has tried to refute is not evidence
# the card can be scored. Powers awaiting their own pass stay off the dial and
# their cards stay excluded -- with a reason that says which of the two is
# missing (see _power_gap), because the old blanket "not implemented in tier0"
# was a false audit record for every power refpowers.py had already grown.
SUPPORTED_POWERS = {"StrengthPower": "strength",
                    "WeakPower": "weak",
                    "VulnerablePower": "vulnerable",
                    # verified 2026-07-21 (refpowers adversarial pass)
                    "CrimsonMantlePower": "crimson_mantle",
                    "FeelNoPainPower": "feel_no_pain",
                    "FreeAttackPower": "free_attack",
                    "InfernoPower": "inferno",
                    "JuggernautPower": "juggernaut",
                    "JugglingPower": "juggling",
                    "ManglePower": "temp_strength_down",
                    "SetupStrikePower": "temp_strength",
                    "RupturePower": "rupture",
                    "UnmovablePower": "unmovable"}


def _power_gap(power: str) -> str:
    """Why a power's cards leave the sheet -- the two reasons are different.

    `refpowers.UNIMPLEMENTED` is tier0 refusing to model a mechanic at all
    (Stampede's autoplay, Hellraiser's reentrant draw). Everything else is the
    DIAL: the engine may well have the power, but it has not been verified, so
    the card is held back rather than scored on trust. Reading the refusal list
    from the engine keeps this record from going stale the way the old blanket
    string did.
    """
    try:
        if str(REPO) not in sys.path:      # run as a script from tools/
            sys.path.insert(0, str(REPO))
        from tier0.engine import refpowers
    except Exception:                      # tools/ must run without tier0
        return f"{power} is not on the SUPPORTED_POWERS dial"
    key = _snake(power[:-len("Power")]) if power.endswith("Power") else None
    if key in refpowers.UNIMPLEMENTED:
        return f"{power} is UNIMPLEMENTED in tier0: " \
               f"{refpowers.UNIMPLEMENTED[key].split('.')[0]}"
    return (f"{power} is not on the SUPPORTED_POWERS dial "
            "(unverified or unimplemented in tier0/engine/refpowers.py)")

# Who a PowerCmd.Apply lands on, in the decompiler's own spelling.
POWER_TARGET = {"base.Owner.Creature": "self",
                "cardPlay.Target": "enemy",
                "base.CombatState.HittableEnemies": "all_enemies"}

# Statements with no game effect. Dropping them is not an approximation --
# it is why an attack card reads as one op instead of five.
COSMETIC_CALL = re.compile(
    r"^(?:await )?(?:VfxCmd|SfxCmd|NPowerUpVfx|NCombatRoom|NRun|Log"
    r"|CreatureCmd\.TriggerAnim|ArgumentNullException\.ThrowIfNull)\b")
# ...and locals that only exist to feed those calls (a vfx node, an alias
# for the enemy list a loop plays particles over).
COSMETIC_LOCAL = re.compile(
    r"^[\w<>?\[\], ]+ \w+ = .*?(?:N\w+Vfx|new Color\(|SaveManager|Mathf"
    r"|base\.CombatState\.HittableEnemies)")
CONTROL_FLOW = re.compile(r"^(?:if|for|foreach|while|do|else|switch|try)\b")

# `base.DynamicVars.Damage.BaseValue`, `base.DynamicVars["Power"].IntValue`,
# and the bare `base.DynamicVars.Block` that GainBlock takes.
VARREF = re.compile(r'base\.DynamicVars(?:\.(\w+)|\["(\w+)"\])'
                    r'(?:\.(?:BaseValue|IntValue))?$')
NUMBER = re.compile(r"(-?\d+(?:\.\d+)?)m?$")

# CanonicalVars shapes. Note `new CardsVar(1)` / `new RepeatVar(3)` carry NO
# `m` suffix -- the summary regex above misses them, which is harmless for
# statistics and fatal for a sheet, so this mode parses vars itself.
VAR_PLAIN = re.compile(r"new (\w+)Var\(\s*(-?[\d.]+)m?\s*[,)]")
VAR_POWER = re.compile(r"new PowerVar<(\w+)Power>\(\s*(-?[\d.]+)m")
VAR_NAMED = re.compile(r'new DynamicVar\("(\w+)",\s*(-?[\d.]+)m\)')
# Runtime-computed damage/block/hits (Body Slam, Perfected Strike, ...).
VAR_CALC = re.compile(r"new Calculated\w*Var\(")

# Upgrade sheet keys tier0/content/upgrades.py can actually apply, keyed by
# the op+shape the upgraded var feeds. A var feeding anything else yields an
# UNEXPRESSIBLE note rather than a key the applier would reject at load.
#
# `power_amount` is upgrades.py's generic "bump the first apply_power amount"
# key, which is exactly the shape of every Ironclad power card whose OnUpgrade
# raises its PowerVar. Only weak/vulnerable need their own keys, because the
# applier disambiguates those two by name when a card applies both.
UPGRADE_POWER_KEY = {"strength": "power_amount",
                     "weak": "weak", "vulnerable": "vulnerable",
                     "crimson_mantle": "power_amount",
                     "feel_no_pain": "power_amount",
                     "free_attack": "power_amount",
                     "inferno": "power_amount",
                     "juggernaut": "power_amount",
                     "juggling": "power_amount",
                     "temp_strength_down": "power_amount",
                     "temp_strength": "power_amount",
                     "rupture": "power_amount",
                     "unmovable": "power_amount"}


def _num(text: str) -> int | float:
    val = float(text)
    return int(val) if val.is_integer() else val


def _method_body(src: str, name: str) -> str:
    """The brace-balanced body of `name`, or '' when the card lacks it."""
    m = re.search(rf"\b{name}\([^)]*\)\s*\n\s*\{{", src)
    if not m:
        return ""
    start = src.index("{", m.end() - 1)
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1:i]
    return ""


def _statements(body: str) -> list[str]:
    """One statement per entry, with fluent chains rejoined.

    ilspy breaks `DamageCmd.Attack(..).Targeting(..).Execute(..)` across
    lines; a chain is one statement and must be matched as one.
    """
    out, cur = [], ""
    for raw in body.split("\n"):
        line = raw.strip()
        if not line:
            continue
        cur = f"{cur} {line}" if cur else line
        if cur.endswith((";", "{", "}")):
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def _drop_cosmetic_blocks(stmts: list[str]) -> list[str]:
    """Remove cosmetic statements, and any block left empty by that.

    A `foreach` that only spawns particles is not control flow the sim has
    to model. A block with ANY surviving statement is kept intact, header
    and all, so it will hit the control-flow check and exclude the card --
    which is the safe direction.
    """
    out, i = [], 0
    while i < len(stmts):
        s = stmts[i]
        if s.endswith("{"):
            depth, j = 1, i + 1
            while j < len(stmts) and depth:
                if stmts[j].endswith("{"):
                    depth += 1
                elif stmts[j] == "}":
                    depth -= 1
                j += 1
            inner = _drop_cosmetic_blocks(stmts[i + 1:j - 1])
            if inner:
                out.append(s)
                out.extend(inner)
                out.append("}")
            i = j
        elif s == "}":
            i += 1
        elif COSMETIC_CALL.match(s) or COSMETIC_LOCAL.match(s):
            i += 1
        else:
            out.append(s)
            i += 1
    return out


def _split_args(text: str) -> list[str]:
    args, depth, cur = [], 0, ""
    for ch in text:
        if ch in "(<[":
            depth += 1
        elif ch in ")>]":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def _call_args(stmt: str, marker: str) -> list[str] | None:
    """Balanced argument list of the call opened by `marker`."""
    at = stmt.find(marker)
    if at < 0:
        return None
    i = at + len(marker)
    depth, start = 1, i
    while i < len(stmt) and depth:
        if stmt[i] == "(":
            depth += 1
        elif stmt[i] == ")":
            depth -= 1
        i += 1
    return _split_args(stmt[start:i - 1])


def _canonical_vars(src: str) -> dict:
    vals = {}
    for name, raw in VAR_PLAIN.findall(src):
        vals[name] = _num(raw)
    for power, raw in VAR_POWER.findall(src):
        # Reachable as both `DynamicVars["StrengthPower"]` and the typed
        # accessor `DynamicVars.Strength` -- register both spellings.
        vals[f"{power}Power"] = _num(raw)
        vals[power] = _num(raw)
    for name, raw in VAR_NAMED.findall(src):
        vals[name] = _num(raw)
    return vals


class _Untranslatable(Exception):
    """Carries the reason a card leaves the sheet."""


def _value(expr: str, vals: dict, locs: dict):
    expr = expr.strip()
    if expr in locs:
        return locs[expr]
    m = VARREF.fullmatch(expr)
    if m:
        return vals.get(m.group(1) or m.group(2))
    m = NUMBER.fullmatch(expr)
    return _num(m.group(1)) if m else None


def _feed(fed: dict, expr: str, fx: dict, field: str, origin: dict) -> None:
    """Record which CanonicalVar supplied an effect field, so OnUpgrade's
    `DynamicVars.X.UpgradeValueBy(n)` can be resolved to a sheet key
    without guessing from the delta's size.

    `origin` carries provenance through locals: Uppercut reads its var once
    into an `int amount` and applies it to two powers, so losing the trail
    at the assignment would lose the whole upgrade.
    """
    expr = expr.strip()
    key = origin.get(expr)
    if key is None:
        m = VARREF.fullmatch(expr)
        key = (m.group(1) or m.group(2)) if m else None
    if key:
        fed.setdefault(key, []).append((fx, field))


def _fed_get(fed: dict, var: str) -> list:
    """A PowerVar is reachable as `Strength` or `StrengthPower` and OnPlay
    and OnUpgrade need not agree on which; treat the spellings as one."""
    for spelling in (var, f"{var}Power", var[:-5] if var.endswith("Power")
                     else var):
        if spelling in fed:
            return fed[spelling]
    return []


def _translate_statement(stmt: str, vals: dict, locs: dict, fed: dict,
                         origin: dict) -> list[dict]:
    """One decompiled statement -> zero or more Tier 0 effects."""
    if "DamageCmd.Attack(" in stmt:
        args = _call_args(stmt, "DamageCmd.Attack(")
        amount = _value(args[0], vals, locs)
        if amount is None:
            raise _Untranslatable("damage amount is runtime-calculated")
        if ".TargetingAllOpponents(" in stmt:
            target = "all_enemies"
        elif ".TargetingRandomOpponents(" in stmt:
            target = "random_enemy"
        elif ".Targeting(cardPlay.Target)" in stmt:
            target = "enemy"
        else:
            raise _Untranslatable("unrecognised attack targeting")
        fx = {"op": "damage", "amount": amount, "target": target}
        _feed(fed, args[0], fx, "amount", origin)
        hits = _call_args(stmt, ".WithHitCount(")
        if hits is not None:
            times = _value(hits[0], vals, locs)
            if times is None:
                raise _Untranslatable("hit count is runtime-calculated")
            if times != 1:
                fx["times"] = times
                _feed(fed, hits[0], fx, "times", origin)
        return [fx]

    if "CreatureCmd.GainBlock(" in stmt:
        args = _call_args(stmt, "CreatureCmd.GainBlock(")
        if args[0] != "base.Owner.Creature":
            raise _Untranslatable("block is granted to another creature")
        amount = _value(args[1], vals, locs)
        if amount is None:
            raise _Untranslatable("block amount is runtime-calculated")
        fx = {"op": "block", "amount": amount}
        _feed(fed, args[1], fx, "amount", origin)
        return [fx]

    if "CardPileCmd.Draw(" in stmt:
        args = _call_args(stmt, "CardPileCmd.Draw(")
        if len(args) != 3:
            raise _Untranslatable("conditional / open-ended draw")
        amount = _value(args[1], vals, locs)
        if amount is None:
            raise _Untranslatable("draw count is runtime-calculated")
        fx = {"op": "draw", "amount": amount}
        _feed(fed, args[1], fx, "amount", origin)
        return [fx]

    if "PlayerCmd.GainEnergy(" in stmt:
        args = _call_args(stmt, "PlayerCmd.GainEnergy(")
        amount = _value(args[0], vals, locs)
        if amount is None:
            raise _Untranslatable("energy gain is runtime-calculated")
        fx = {"op": "energy", "amount": amount}
        _feed(fed, args[0], fx, "amount", origin)
        return [fx]

    if "CreatureCmd.Damage(" in stmt:
        args = _call_args(stmt, "CreatureCmd.Damage(")
        if args[1] != "base.Owner.Creature":
            raise _Untranslatable("non-self HP loss")
        amount = _value(args[2], vals, locs)
        if amount is None:
            raise _Untranslatable("HP loss is runtime-calculated")
        # tier0's `damage / target: self` IS unblockable HP loss, which is
        # what ValueProp.Unblockable|Unpowered means here.
        fx = {"op": "damage", "amount": amount, "target": "self"}
        _feed(fed, args[2], fx, "amount", origin)
        return [fx]

    if "CreatureCmd.Heal(" in stmt:
        args = _call_args(stmt, "CreatureCmd.Heal(")
        if args[0] != "base.Owner.Creature":
            raise _Untranslatable("heal targets another creature")
        amount = _value(args[1], vals, locs)
        if amount is None:
            raise _Untranslatable("heal amount is runtime-calculated")
        fx = {"op": "heal", "amount": amount}
        _feed(fed, args[1], fx, "amount", origin)
        return [fx]

    m = re.search(r"PowerCmd\.Apply<(\w+)>\(", stmt)
    if m:
        power = m.group(1)
        if power not in SUPPORTED_POWERS:
            raise _Untranslatable(_power_gap(power))
        args = _call_args(stmt, m.group(0))
        target = POWER_TARGET.get(args[1])
        if target is None:
            raise _Untranslatable("unrecognised power target")
        amount = _value(args[2], vals, locs)
        if amount is None:
            raise _Untranslatable("power amount is runtime-calculated")
        fx = {"op": "apply_power", "power": SUPPORTED_POWERS[power],
              "amount": amount, "target": target}
        _feed(fed, args[2], fx, "amount", origin)
        return [fx]

    m = re.fullmatch(r"(?:int|decimal|var) (\w+) = (.+);", stmt)
    if m:
        name, rhs = m.group(1), m.group(2).strip()
        if rhs == "ResolveEnergyXValue()":
            locs[name] = "X"           # X-cost card: the sim's own formula
            return []
        val = _value(rhs, vals, locs)
        if val is None:
            raise _Untranslatable("depends on runtime combat history")
        locs[name] = val
        var = VARREF.fullmatch(rhs)
        if var:                       # keep the upgrade trail across the alias
            origin[name] = var.group(1) or var.group(2)
        return []

    # Name the call we could not translate: an exclusion reason is only
    # useful if it says which mechanic is missing.
    call = re.search(r"\b([A-Z]\w*(?:\.\w+)?)\(", stmt)
    raise _Untranslatable(f"no tier0 op for {call.group(1)}" if call
                          else "unrecognised effect statement")


def _sheet_row(card: dict, src: str) -> tuple[dict, dict]:
    """(row, upgrade_delta). Raises _Untranslatable with the reason."""
    if VAR_CALC.search(src):
        raise _Untranslatable("damage/block scales off runtime state")
    # An override that fires OUTSIDE OnPlay is a whole second behaviour
    # (replay-from-exhaust, cost reduction per attack played, ...). Only the
    # vfx hook is safe to ignore.
    for method in re.findall(r"public override [\w<>?\[\], ]+ (\w+)\(", src):
        if method != "OnEnqueuePlayVfx":
            raise _Untranslatable(f"out-of-play hook {method}")

    body = _method_body(src, "OnPlay")
    if not body:
        raise _Untranslatable("no OnPlay body found")
    stmts = _drop_cosmetic_blocks(_statements(body))
    for s in stmts:
        if CONTROL_FLOW.match(s):
            raise _Untranslatable("behaviour branches on runtime state")

    vals = _canonical_vars(src)
    locs: dict = {}
    fed: dict = {}
    origin: dict = {}
    effects: list[dict] = []
    for s in stmts:
        effects.extend(_translate_statement(s, vals, locs, fed, origin))
    if not effects:
        raise _Untranslatable("no expressible effects")

    cost = "X" if re.search(r"HasEnergyCostX\s*=>\s*true", src) else card["cost"]
    row = {
        "id": ID_PREFIX + _snake(card["name"]),
        "name": _display(card["name"]),
        "cost": cost,
        "type": card["type"].lower(),
        "rarity": card["rarity"].lower(),
        "solve": _solve(effects, card["type"]),
        "archetypes": ["generic"],
        "role": _role(effects, card["type"]),
        "effects": effects,
    }
    # Self-exhaust is a printed keyword; a card that exhausts SOMETHING ELSE
    # only mentions Exhaust in a hover tip, and must not be marked.
    if re.search(r"CanonicalKeywords[^;]*CardKeyword\.Exhaust", src, re.S):
        row["exhaust"] = True
    return row, _upgrade_delta(src, fed)


def _upgrade_delta(src: str, fed: dict) -> dict:
    """OnUpgrade -> the *-upgrades.yaml delta grammar.

    Keys the applier in tier0/content/upgrades.py does not know are NOT
    emitted; they come back as `_unexpressible` so the count of upgrades we
    cannot model is visible next to the count of cards we cannot model.
    """
    body = _method_body(src, "OnUpgrade")
    delta: dict = {}
    unexpressible: list[str] = []
    for stmt in _statements(body):
        if "AddKeyword(CardKeyword.Innate)" in stmt:
            delta["innate"] = True
            continue
        if "RemoveKeyword(CardKeyword.Exhaust)" in stmt:
            delta["remove"] = "exhaust"
            continue
        m = re.search(r"base\.EnergyCost\.UpgradeBy\((-?\d+)\)", stmt)
        if m:
            delta["cost"] = int(m.group(1))
            continue
        m = re.search(r'base\.DynamicVars(?:\.(\w+)|\["(\w+)"\])'
                      r'\.UpgradeValueBy\((-?[\d.]+)m\)', stmt)
        if not m:
            unexpressible.append("unrecognised upgrade statement")
            continue
        var, amount = m.group(1) or m.group(2), _num(m.group(3))
        targets = _fed_get(fed, var)
        if not targets:
            unexpressible.append(f"{var} feeds nothing the sheet expresses")
            continue
        for fx, field in targets:
            key = _delta_key(fx, field)
            if key is None:
                unexpressible.append(f"{var} -> {fx['op']}.{field}")
            else:
                delta[key] = amount
    if unexpressible:
        delta["_unexpressible"] = unexpressible
    return delta


def _delta_key(fx: dict, field: str) -> str | None:
    if field == "times" and fx["op"] == "damage":
        return "times"
    if field != "amount":
        return None
    op = fx["op"]
    if op == "damage":
        return None if fx.get("target") == "self" else "damage"
    if op in ("block", "heal", "draw"):
        return op
    if op == "energy":
        return "energy"
    if op == "apply_power":
        return UPGRADE_POWER_KEY.get(fx["power"])
    return None


def _walk_row_effects(effects: list[dict]):
    """Yield supplement effects, including conditional branches."""
    for fx in effects:
        yield fx
        for branch in ("then", "else"):
            nested = fx.get(branch)
            if isinstance(nested, list):
                yield from _walk_row_effects(nested)


def _row_delta_key(row: dict, var: str) -> str | None:
    """Map one DLL DynamicVar upgrade onto a hand-translated row.

    The supplement supplies effect provenance that the structural translator
    could not derive. This function still matches by effect shape, never card
    id: values continue to come from the local DLL and no per-card data enters
    the committed tool.
    """
    effects = list(_walk_row_effects(row["effects"]))
    if var == "Damage" and any(
            fx.get("op") == "damage" and fx.get("target") != "self"
            for fx in effects):
        return "damage"
    if var == "Block" and any(fx.get("op") == "block" for fx in effects):
        return "block"
    if var == "MaxHp" and any(fx.get("op") == "gain_max_hp"
                              for fx in effects):
        return "max_hp"
    if var == "Repeat" and any(fx.get("op") == "damage"
                               and isinstance(fx.get("times"), int)
                               for fx in effects):
        return "times"
    if var in ("Cards", "Draw") and any(
            fx.get("op") == "draw" for fx in effects):
        return "draw"
    if var == "Energy" and any(fx.get("op") == "energy" for fx in effects):
        return "energy"
    if sum(fx.get("op") == "apply_power" for fx in effects) == 1:
        return "power_amount"
    return None


def _supplement_upgrade_delta(row: dict, src: str) -> dict:
    """Derive a supplement row's upgrade from its DLL source and DSL shape."""
    delta: dict = {}
    unexpressible: list[str] = []
    for stmt in _statements(_method_body(src, "OnUpgrade")):
        if "AddKeyword(CardKeyword.Innate)" in stmt:
            delta["innate"] = True
            continue
        if "RemoveKeyword(CardKeyword.Exhaust)" in stmt:
            delta["remove"] = "exhaust"
            continue
        m = re.search(r"base\.EnergyCost\.UpgradeBy\((-?\d+)\)", stmt)
        if m:
            delta["cost"] = int(m.group(1))
            continue
        m = re.search(r'base\.DynamicVars(?:\.(\w+)|\["(\w+)"\])'
                      r'\.UpgradeValueBy\((-?[\d.]+)m\)', stmt)
        if not m:
            unexpressible.append("unrecognised upgrade statement")
            continue
        var, amount = m.group(1) or m.group(2), _num(m.group(3))
        key = _row_delta_key(row, var)
        if key is None:
            unexpressible.append(f"{var} feeds nothing the row expresses")
        elif key in delta:
            unexpressible.append(f"multiple upgrade vars map to {key}")
        else:
            delta[key] = amount

    # Two base-game upgrades change an IsUpgraded branch rather than a
    # DynamicVar. The local row tells us which generic DSL operation the
    # branch controls; no card-name table or extracted value is committed.
    if "IsUpgraded" in src:
        effects = list(_walk_row_effects(row["effects"]))
        if any(fx.get("op") == "upgrade_in_hand" for fx in effects):
            delta["upgrade_scope"] = "all"
        if any(fx.get("op") == "exhaust_from" and "select" not in fx
               for fx in effects):
            delta["exhaust_select"] = "chosen"

    if unexpressible:
        delta["_unexpressible"] = unexpressible
    return delta


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _display(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name)


def _solve(effects: list[dict], ctype: str) -> list[str]:
    """DERIVED from the effects, never authored -- these tags drive the
    scorecard, and a hand-assigned tag on a reference pool would be us
    choosing the answer the comparison is supposed to produce."""
    tags = []
    for fx in effects:
        if fx["op"] == "damage" and fx.get("target") != "self":
            tags.append("utility" if fx["target"] == "all_enemies"
                        else "frontload")
        elif fx["op"] == "block":
            tags.append("block")
        elif fx["op"] in ("draw", "energy"):
            tags.append("velocity")
        elif fx["op"] == "heal":
            tags.append("sustain")
        elif fx["op"] == "apply_power":
            tags.append("scaling" if fx["power"] == "strength" else "utility")
    return list(dict.fromkeys(tags)) or ["utility"]


def _role(effects: list[dict], ctype: str) -> str:
    if ctype == "Power":
        return "payoff"
    return "enabler" if any(f["op"] == "apply_power" for f in effects) else "glue"


def _flow(value) -> str:
    """Compact YAML flow style, matching the hand-written design sheets."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_flow(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {_flow(v)}" for k, v in value.items()) + "}"
    text = str(value)
    return text if re.fullmatch(r"[A-Za-z_][\w' .!-]*", text) else f'"{text}"'


def _delta_flow(delta: dict) -> str:
    """Upgrade deltas are written signed (`{damage: +3}`) in every hand-made
    sheet -- YAML reads `+3` as 3, so this is grammar, not arithmetic."""
    parts = []
    for key, val in delta.items():
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            parts.append(f"{key}: {val:+g}")
        else:
            parts.append(f"{key}: {_flow(val)}")
    return "{" + ", ".join(parts) + "}"


SHEET_HEADER = """\
# {char} card pool -- MACHINE-GENERATED by tools/extract_base_game_pool.py
# from the local sts2.dll. GITIGNORED base-game reference: never copy these
# rows (or these names) into docs/ or tier0/content/.
#
# WHY: to score a real base-game pool on the same seven axes as our own
# characters, instead of against the six-card `ref_ironclad` construct that
# every statline in the project is currently normalised to.
#
# PARITY, NOT FIDELITY: no relics, potions or events -- the world Klee is
# measured in. Numbers are the printed base-game values; `solve`, `role` and
# `archetypes` are DERIVED from the effects (see _solve) because authoring
# them would be choosing the answer this comparison exists to find.
#
# Document 1 (this one) is the loader-shaped card list. Document 2 is the
# `excluded:` section: cards the Tier 0 DSL cannot express, with the reason.
# They are NOT approximated -- a wrong number wearing the right name is how
# sim findings stop being trustworthy.
#
# emitted {n_ok} / {n_all}   excluded {n_bad} / {n_all}
"""


def emit_sheet(cards: list[dict], sources: dict[str, str],
               character: str) -> tuple[int, int]:
    rows, upgrades, excluded = [], {}, {}
    for card in cards:
        try:
            row, delta = _sheet_row(card, sources[card["name"]])
        except _Untranslatable as exc:
            excluded[ID_PREFIX + _snake(card["name"])] = {
                "name": _display(card["name"]),
                "rarity": card["rarity"].lower(),
                "reason": str(exc)}
            continue
        rows.append(row)
        if delta:
            upgrades[row["id"]] = delta

    # A hand-translated local supplement may carry DSL rows that the strict
    # structural card translator refuses to invent. Its upgrades are still
    # recoverable mechanically: values come from OnUpgrade in the DLL, while
    # the local row supplies the effect provenance needed to choose a delta
    # key. The conventional name keeps this generic for future characters.
    supplement = OUT_DIR / f"{character.lower()}_pool_pass4.yaml"
    supplement_upgrades = 0
    if supplement.exists():
        try:
            import yaml
        except ImportError:
            sys.exit("PyYAML is required to derive supplement upgrades")
        supplement_rows = yaml.safe_load(supplement.read_text()) or []
        if not isinstance(supplement_rows, list):
            sys.exit(f"{supplement}: expected a list of card rows")
        source_by_id = {
            ID_PREFIX + _snake(card["name"]): sources[card["name"]]
            for card in cards
        }
        seen: set[str] = set()
        for row in supplement_rows:
            cid = row.get("id")
            if not cid or cid in seen:
                sys.exit(f"{supplement}: missing or duplicate card id {cid!r}")
            if cid in upgrades:
                sys.exit(f"{supplement}: {cid} overlaps the emitted sheet")
            if cid not in source_by_id:
                sys.exit(f"{supplement}: no DLL card source found for {cid}")
            seen.add(cid)
            delta = _supplement_upgrade_delta(row, source_by_id[cid])
            if not delta:
                sys.exit(f"{supplement}: no upgrade recovered for {cid}")
            upgrades[cid] = delta
            supplement_upgrades += 1

    OUT_DIR.mkdir(exist_ok=True)
    sheet = OUT_DIR / f"{character.lower()}-cards.yaml"
    out = [SHEET_HEADER.format(char=character, n_ok=len(rows),
                               n_bad=len(excluded), n_all=len(cards))]
    for row in rows:
        out.append(f"- {_flow(row)}")
    out.append("\n---\n# Cards the Tier 0 DSL cannot express. Each reason is a\n"
               "# concrete gap: implement it, or the card stays out.\nexcluded:")
    for cid, info in sorted(excluded.items()):
        out.append(f"  {cid}: {_flow(info)}")
    sheet.write_text("\n".join(out) + "\n")

    # R20: upgrades live in their OWN sheet, never inline on a card row.
    ups = OUT_DIR / f"{character.lower()}-upgrades.yaml"
    lines = [f"# {character} upgrade deltas -- MACHINE-GENERATED, gitignored.",
             f"# {len(rows)} extractor rows + {supplement_upgrades} local "
             "supplement rows.",
             "# Grammar: docs/upgrade-conventions.md. `_unexpressible` lists "
             "deltas",
             "# tier0/content/upgrades.py has no key for; they are reported, "
             "not faked."]
    for cid, delta in sorted(upgrades.items()):
        lines.append(f"{cid}: {_delta_flow(delta)}")
    ups.write_text("\n".join(lines) + "\n")

    print(f"\n=== sheet: {len(rows)} emitted / {len(excluded)} excluded "
          f"of {len(cards)} ===")
    by_reason = Counter(i["reason"] for i in excluded.values())
    for reason, k in by_reason.most_common():
        print(f"  {k:>3}x  {reason}")
    n_unexp = sum(1 for d in upgrades.values() if "_unexpressible" in d)
    print(f"  upgrades: {len(upgrades) - n_unexp} clean, "
          f"{n_unexp} with unexpressible deltas")
    print(f"  wrote {sheet.relative_to(OUT_DIR.parent)} + "
          f"{ups.relative_to(OUT_DIR.parent)} in {OUT_DIR}  "
          f"(gitignored -- reference only, do not commit)")
    return len(rows), len(excluded)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("character", help="e.g. Ironclad, Silent, Defect")
    ap.add_argument("--json", default=None,
                    help="output path (default game_ref/<char>.json)")
    ap.add_argument("--emit-sheet", action="store_true",
                    help="also write a Tier 0 card sheet + upgrade sheet to "
                         "game_ref/ (gitignored)")
    args = ap.parse_args(argv)

    dll = game_dll()
    names, sources = decompile_character(dll, args.character)
    cards, failed = [], []
    for i, name in enumerate(names, 1):
        print(f"\r  {i}/{len(names)} {name:<26}", end="", file=sys.stderr)
        card = parse_card(sources[name], name)
        (cards if card else failed).append(card or name)
    print(f"\r  parsed {len(cards)}/{len(names)}"
          f"{f', {len(failed)} FAILED: {failed}' if failed else ''}"
          + " " * 24, file=sys.stderr)

    summarize(cards, args.character)

    OUT_DIR.mkdir(exist_ok=True)
    out = Path(args.json) if args.json else OUT_DIR / f"{args.character.lower()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cards, indent=1))
    print(f"\n  wrote {out.relative_to(REPO)}  "
          f"(gitignored -- reference only, do not commit)")

    if args.emit_sheet:
        emit_sheet(cards, sources, args.character)
    return 0


if __name__ == "__main__":
    sys.exit(main())
