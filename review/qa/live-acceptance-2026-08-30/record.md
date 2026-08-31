# Live acceptance — 2026-08-30, phase 1

Wire-verified, not blind-graded. No Codex/GPT call was made in this window and
no graded turn or seat was run. Every number below is read off a log or a wire
row named beside it.

## Build

| fact | value |
|---|---|
| branch | `live-acceptance-2026-08-30` off `main` `cc6f323c` |
| package | **`0.2.1786+proto.dirty`** (dev, `-p:PrototypeCards=true`) |
| pck | 9,776,476 bytes, contract `roster-pck-v3`, 144 resources |
| pck build id | `20260830-212957+cc6f323c` |
| game | v0.111.0, `public-beta`, appid 2868840 |
| gates before build | `gen_roster_cards --check` OK, `gen_prototype_cards --check` OK, `run_lints --lane ci` 31/31, `validate.ps1` OK |

`pytest tier0/tests tier05/tests` was **1 failed / 5225 passed** BEFORE
`build_pck.ps1` and clean after. The failure was
`test_the_built_contract_names_every_referenced_scene`, and it was correct:
the committed contract predated `EB-40`'s scene, so `Furina references
furina/ui/energy_counter.tscn, and the built pck contract does not list it`.
The test exists to say exactly that, and the build cleared it.

New in this pack's contract, all three first-time surfaces:

```
resource=res://furina/ui/energy_counter.tscn
resource=res://furina/ui/energy_orb/layer1_backglow.png
resource=res://furina/ui/energy_orb/layer2_body.png
resource=res://furina/ui/energy_orb/layer3_caustics.png
resource=res://furina/ui/energy_orb/layer4_ring.png
resource=res://furina/ui/energy_orb/layer5_gloss.png
resource=res://klee/relics/dodoco_tales.png
```

## `EB-162` — the ledger line

`tools/art_ledger.py --root .` reports **7** `MISSING-PACKED`, and
`pck:klee/relics/dodoco_tales.png` is no longer one of them. The seven that
remain are six unrendered Furina power icons and `kokomi/model/combat.tscn`,
which the tool itself marks *[requested only by the diagnostics probe list]*.
None is Klee's relic. **CLEARED.**

## Gate — the three-fight soak (R225 / M66)

```
python -m understudy.soak --runs 1 --character KLEEMOD-KLEE --max-fights 3
bounded  seed=AR2G3FZJXB75  actions=55  fights=3  defects=0
```

**GREEN.** Reversibility log all four rows REVERTED.

## `EB-40` — the five `GetNode`s, live → **PASS**

Acceptance as the row words it: *the five `GetNode`s resolve LIVE*.

Static half, from the boot log of every launch in this window:

```
[INFO] [klee] convention scene ok: res://furina/ui/energy_counter.tscn root=Control
```

and **no** `has no node named "…"` warning for `Label`, `Layers`,
`RotationLayers`, `EnergyVfxBack` or `EnergyVfxFront` — `KleeSceneTelemetry`
walks all five by name and prints one per miss.

Live half — a real Furina combat:

```
python -m understudy.soak --runs 1 --character KLEEMOD-FURINA --max-fights 1
bounded  seed=07G8YGNTQHKX  actions=42  fights=1  defects=0
```

`godot.log`, in the fight:

```
[INFO] Embarking on a singleplayer KLEEMOD-FURINA run. Ascension: 2 Seed: 07G8YGNTQHKX
[INFO] [BaseLib] Auto-converted 'res://furina/ui/energy_counter.tscn' from Control to NEnergyCounter
[INFO] Player 1 playing card KLEEMOD-ETHEREAL_SPOTLIGHT (no target)
```

That auto-convert line IS the hard cast the row is about:
`NEnergyCounter._Ready` `GetNode`s all five and throws on a null while the
combat HUD is being built. The run continues past it for 42 actions and
`godot.log` carries **no exception, no `[ERROR]`, no stack trace** on the
session. The five resolved.

## `EB-240` — seen to fail, live → **PASS (both halves)**

Acceptance: *one board's refusal seen live*. All three committed
`understudy/turns/klee-sparks-bt2r/` boards were staged **as they stand**
(R101b — read, never edited). All three refused before a packet was written,
each naming the mismatch:

| board | refusal |
|---|---|
| `klee-sparks-bt2r-t01` | `hp: the board declares 'first' at 55 and the wire reads 45` |
| `klee-sparks-bt2r-t02` | `hp: the board declares 'first' at 55 and the wire reads 46` |
| `klee-sparks-bt2r-t03` | `hp: the board declares 'first' at 55 and the wire reads 40` |

45 / 46 / 40 are exactly the three live bodies `EB-240`'s row names. Each
refusal is prefixed by the row's own sentence — *"the board's declared
assumptions are not the wire's, so the packet would print a falsehood a reader
does arithmetic on (`EB-240`)"* — and each exited 2 with no `packet.md`
written.

**The control half.** A preflight that refuses everything proves nothing, so a
correct current-world board must still stage. A scratch COPY of
`klee-sparks-bt3/t01` (id changed; the registered board was not staged and is
not edited) staged clean:

```
packet: review/qa/eb240-live-control/packet.md
sha256: be932c7798c6266955d7159e000acf6f3e1cc79d2ba6b426ec6296f3d0bad91e
seed:   YX7PB48WR7R4  (game-generated)
        4 card(s) in hand, 1 enem(ies)
```

That packet is deliberately **not committed**, and neither is the scratch board
that produced it. Both are a control on a board id no round owns; committing
either would put an orphan row in `review/qa/ledger.tsv` that a later reader
could mistake for a staged turn. The sha256 above and the scenario log path are
the record.

**A find on the way there, and it is `EB-243`.** The control's FIRST attempt
was also refused, on the other leg:

```
relics: the board declares 'Pounding Surprise', 'Fishing Rod' and the wire
carries 'Pounding Surprise', 'Stone Humidifier' -- missing 'Fishing Rod'
-- unexpected 'Stone Humidifier'
```

The `hp.first: 40` leg matched; only the relic leg is wrong. That is BT3's own
board declaring a run-start gift the seed does not produce on this build — a
real defect in a registered-not-run board, filed as `EB-243` rather than
repaired here, because re-drafting a committed board is a disclosure act
(R212) and not a hygiene fix. The control was corrected in scratch only.

## `EB-184` — the refused line replays → **PASS (both halves)**

Acceptance: *the Block mode replays with no target*. Kokomi slice 1 round 4
`t02`'s line, recreated on a staged board through the bridge. Two committed
scenarios, and the second is **seen to fail by construction**.

**`understudy/scenarios/eb184-modal-block-no-target.yaml` — PASS, 2 expects held.**
The wire row, verbatim from the scenario log:

```json
{"step": "play Thoma - Blazing Ooyoroi",
 "action": {"action": "play_card", "card_index": 5,
            "mode": "Gain 3 Block, applying no element"},
 "status": "ok",
 "message": "Playing 'Thoma - Blazing Ooyoroi' aimed at Fuzzy Wurm Crawler (inert: the chosen mode 'Gain 3 Block, applying no element' aims at nobody)"}
```

No `target` key in the action. `status: ok`. Player Block 0 → 3.

**`understudy/scenarios/eb184-modal-damage-needs-target.yaml` — REFUSED, which is its pass.**
Same card, same absent target, the DAMAGE mode named:

```json
{"action": {"action": "play_card", "card_index": 5,
            "mode": "Deal 8 damage, applying its element"},
 "status": "error",
 "message": "Card requires a target. Provide 'target' with an entity_id. The chosen mode aims at one enemy; the other mode(s) of 'Thoma - Blazing Ooyoroi' may not. Name the mode with 'mode' to be told which. Modes: 'Deal 8 damage, applying its element' | 'Gain 3 Block, applying no element'"}
```

A fix that had simply switched aiming off would pass the first file and fail
the second. That is why there are two, and why the second file's header says
in full that a PASS there is the defect.

## `EB-183` — the flag stays invisible

Confirmed by construction rather than by absence of evidence: `EB-183`'s whole
C# surface is `Cards/Prototype/Generated/ProtoMusterSubsidyFunnel.cs`, which is
quarantined off-pool and compiled only under `-p:PrototypeCards=true`, and
**no shipped caller passes `subsidyWaived: true`** — every non-prototype call
site takes the parameter's `false` default. Nothing in tonight's four live
sessions granted the row and no subsidy behaviour appears in any log.

## Teardown — the reversibility ledger, final state

Each session tore down its own ledger and printed all four rows REVERTED.
Proved again after the last session, from the game directory itself:

```
PID: NONE - SlayTheSpire2.exe is not running
steam_appid.txt present: False
mods\STS2_MCP present: False
mods\klee manifest version: 0.2.1786+proto.dirty
```

| # | change | state |
|---|---|---|
| 1 | `steam_appid.txt` (2868840) at the game root | **REVERTED** (absent) |
| 2 | `mods\STS2_MCP\` from vendor pin `55e0648` | **REVERTED** (absent) |
| 3 | `SlayTheSpire2.exe` launched directly | **REVERTED** (PID proven gone) |
| 4 | `FastMode=Instant`, `TimeScale=3.0` via `/gits/speed` | **REVERTED** (captured originals restored) |

The mod package is deliberately NOT reverted: `0.2.1786+proto.dirty` is left
installed as the window's product, the way `0.2.1627+proto.dirty` was before
it. `klee-mod\build\deploy.ps1` restores the release build before any measured
run or handoff.
