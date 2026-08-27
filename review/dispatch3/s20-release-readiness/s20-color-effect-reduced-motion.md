# S20 — colour / effect / reduced-motion surface census

> **This decides nothing.** It is an inventory of what exists today, not a
> promise that any of it will be supported, changed, or shipped. Every taste,
> scope, spend and ship call below is [USER]'s and is written as a numbered
> pick list, never as a blank or a recommendation.
>
> Stream S20, family "colour / effect / reduced-motion". Six sibling families
> (save/update/removal, player-count, packaging/credits, performance/size,
> controller/resolution/text, localization seams) run concurrently; where a
> case touches theirs it carries a one-line pointer and stops.
>
> Written 2026-08-26. Base game read at the pinned build (v0.107.1, commit
> `59260271`, Steam buildid `23811903` — `docs/current/STATE.md`, "Mod build
> environment (pinned)"). Mod read from the primary checkout, read-only.

---

## 1. The one-paragraph answer

**The base game has no colour-blind mode and no reduced-motion mode.** Neither
string, nor any synonym, appears anywhere in the decompiled `sts2.dll`. What it
does have is four adjacent switches — **Screenshake** (5 steps, including a
true zero), **Phobia Mode**, **Text Effects**, and **Fast Mode** — and our mod
touches none of them, because it never shakes the screen, never animates text,
and never registers a phobia-toggleable animation player. The mod's own moving
parts are eight scene animations, all one-shot or slow loops, all small-area,
none looping a strobe. The real exposure in our surfaces is **colour-only
encoding**, and it splits into one large inherited case (the base game's
green/red "this number changed" convention, which 246 of our 309 card files
opt into by writing `{X:diff()}`) and one case we created ourselves (Furina and
Kokomi ship near-identical cyan seat colours, which in co-op are the *only*
channel identifying who drew a map line and who is aiming at what). Everything
else we encode by colour also carries a shape, an icon, a number, or a hover
tip alongside it.

---

## 2. What the base game exposes (inventory, not a promise)

`MegaCrit.Sts2.Core.Saves.PrefsSave` is the whole gameplay-preference surface;
`SettingsSave` is the graphics/audio/input half. Every field of both was read.

| Base switch | Field | Values | Where it bites | Does a mod get it free? |
|---|---|---|---|---|
| **Screenshake** | `PrefsSave.ScreenShakeOptionIndex` (default 2) | 5 steps, multiplier `0 / 0.5 / 1 / 2 / 4` (`NScreenshakePaginator.cs:97-107`) | `NScreenShake.Shake` / `.Rumble` multiply strength by `_multiplier` (`NScreenShake.cs:169`, `:181`); trauma too (`:205`) | **Yes** — any mod calling `NGame.Instance.ScreenShake/ScreenShakeTrauma/ScreenRumble` is scaled automatically. Index 0 is a true off. |
| **Phobia Mode** | `PrefsSave.PhobiaMode` (default off) | on/off | `NPhobiaAnimationToggler.UpdatePhobiaMode` sets `_animationPlayer.Active = !PhobiaMode` (`NPhobiaAnimationToggler.cs:80-84`); driven by the `NGame.PhobiaModeToggled` signal | **Only if the mod opts in** — it is a *node type* you must put in your scene, not a global. Our scenes contain none. |
| **Text Effects** | `PrefsSave.TextEffectsEnabled` (default on) | on/off | Gated centrally in `AbstractMegaRichTextEffect.ShouldTransformText()` (`AbstractMegaRichTextEffect.cs:52-58`) — every `[jitter]`, `[sine]`, `[flyin]`, `[fadein]` tag | **Yes** — any mod text using base rich-text tags honours it with no code. Note this kills *motion* tags; the *colour* tags (`[gold]`, `[green]`, `[red]`, …) are separate classes and are **not** switched off by it. |
| **Fast Mode** | `PrefsSave.FastMode` (`None/Normal/Fast/Instant`, default `Normal`) | 4 steps | `Cmd.Wait` and `Cmd.WaitFast` short-circuit on `Instant` (`Cmd.cs:37`, `:66-84`); card tweens shorten (`CardPileCmd.cs:171`, `:553-577`, `:755-758`) | **Only through `Cmd.Wait`.** Scene `AnimationPlayer` animations are unaffected. Ours are all `AnimationPlayer`. |
| **MP map drawings** | `PrefsSave.ShowMultiplayerDrawings` (default on) | on/off | the co-op map-drawing layer | Yes (it hides the whole layer, ours included). |
| — | *no colour-blind field* | — | — | — |
| — | *no reduced-motion field* | — | — | — |

**Search boundary for the two absences.** Case-insensitive regex
`colou?rblind|daltoni|deuteran|protan|tritan|reduce[dD]?motion|motion.?reduc|photosensit|epilep`
over the full 3,425-file decompile of `sts2.dll` returns **zero hits**. The
settings screen's own node list (69 files under
`MegaCrit.Sts2.Core.Nodes.Screens.Settings/`) contains no such control. That is
as strong a negative as a decompile can give; it does not rule out a
shader-level option added in a later build.

---

## 3. Case table — colour-only encodings

Columns: **case / reproduction / status / evidence / automation candidate /
defect-or-scope-call.** "Defect" means something is wrong against its own
stated intent. "Scope call" means nothing is broken and the question is what
[USER] wants to support.

### C1 — Furina and Kokomi ship near-identical co-op seat colours

| | |
|---|---|
| **Case** | Every character declares `MapDrawingColor` and `RemoteTargetingLineColor`. In co-op these are the **only** channel identifying whose map line / map ping / targeting line is whose — the consumers set a `Line2D.DefaultColor` and a `Modulate` and draw no label. Furina is `#4AA6C8`; Kokomi is `#6FC8D6`. Both cyan. |
| **Reproduction** | Not reproducible tonight — needs the game and a second seat. Steps: 2-player co-op, seat A = Furina, seat B = Kokomi, open the map, both players draw a line and drop a ping; then in combat both remote-target the same enemy. Compare. |
| **Status** | **UNKNOWN in play, CONFIRMED in code.** The two hex values are 1.44:1 in relative luminance (computed from the declared values below), so under any red-green deficiency the pair separates on brightness alone at that ratio. Whether that is legible at line width on the map screen is an eyes-on question nobody has asked. |
| **Evidence** | `klee-mod/KleeCode/Furina.cs:159-161`; `klee-mod/KleeCode/Kokomi.cs:207-209`; `klee-mod/KleeCode/Klee.cs:268-272`. Consumers: `NMapDrawings.cs:460` (`line2D.DefaultColor = player.Character.MapDrawingColor`), `NMapScreen.cs:1648` (`nMapPingVfx.Modulate = …`), `NRemoteTargetingIndicator.cs:133` and `:140`. Base-game precedent that every character is a *different* hue: Ironclad `#CB282B`, Silent `#2F6729`, Defect `#0D638C`, Necrobinder `#AC0486`, Regent `#935206`, Deprived `#462996` (`Models.Characters/*.cs`, lines as grepped). |
| **Automation candidate** | **Yes.** Seam: a pytest beside `tier0/tests/test_visual_contract_gaps.py` (it already parses `klee-mod/KleeCode` and `pck-src` as text and asserts cross-character distinctness for the icon-outline gap, `:105-130`). A pairwise minimum-ΔE / minimum-luminance-ratio assertion over the six declared colours per character is the same shape of check and needs no game. |
| **Defect or scope call** | **[USER] scope call, not a defect.** Nothing violates a stated rule — no rule about seat-colour separation exists. Colour picks are taste and are [USER]'s (charter §3.1). Numbered pick list in §7. |

### C2 — `{X:diff()}` renders "changed from printed" as green vs red

| | |
|---|---|
| **Case** | Our generated card text writes `{Damage:diff()}`, `{Block:diff()}`, etc. That formatter resolves to `[green]…[/green]` when the live value is above the printed one and `[red]…[/red]` when below — the classic red/green pair — with **no** second cue (no arrow, no sign, no weight change). **246 of 309 card source files** use it. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: any run, gain Strength, look at a `{Damage:diff()}` card in hand; then take Weak and look again. The number is green in the first case and red in the second and identical in shape. |
| **Status** | **NOT-SUPPORTED-BY-DESIGN (base game).** This is base rendering, invoked by a base formatter, through base rich-text colour tags. The mod cannot change it without patching base text rendering globally, which is out of this stream's scope to propose. |
| **Evidence** | Chain, each step read: our cards `klee-mod/KleeCode/Cards/**` (e.g. `Furina/Generated/ApplauseLine.cs:48`) → `HighlightDifferencesFormatter.TryEvaluateFormat` calls `dynamicVar.ToHighlightedString(inverse:false)` (`HighlightDifferencesFormatter.cs:22-30`) → `DynamicVar.ToHighlightedString` (`DynamicVar.cs:171-176`) → `StsTextUtilities.HighlightChangeText` inserts `[green]` or `[red]` (`StsTextUtilities.cs:15-31`). The same file also fixes the damage-popup pair at `#77ff67` / `#ff6563` (`:7-11`). |
| **Automation candidate** | **No, not usefully.** A lint could count `:diff()` uses, but the encoding is base-owned; counting our own uses measures nothing actionable. |
| **Defect or scope call** | **Neither — it is an inherited platform property.** Recorded so a public-release readiness answer can say so honestly rather than discover it. |

### C3 — Keyword-ness is carried by `[gold]` alone at a glance

| | |
|---|---|
| **Case** | Card text marks keywords with `[gold]` (250 of our card files). At rest, "this word is a keyword" is a hue difference and nothing else. The redundant cue is the hover tip, which requires an action to reach. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: hover any card; the gold words are the hoverable ones. |
| **Status** | **NOT-SUPPORTED-BY-DESIGN (base game convention), and it is the ecosystem convention.** Gold-on-cream is a large luminance step, so the hue is not doing the work alone in practice; the mitigation is contrast, not shape. |
| **Evidence** | Ours: `klee-mod/KleeCode/Cards/**` (e.g. `Furina/Generated/BlockingNotes.cs:48`). Downfall does the identical thing in its own loc tables — `Downfall@32e6113:Automaton/localization/eng/cards.json:2,12,16` — across 476 files that carry the tag. |
| **Automation candidate** | No. |
| **Defect or scope call** | **Neither.** Pointer only: whether keyword styling survives translation is the **localization-seams** family's question, not mine. |

### C4 — Salon member identity: colour is redundant, and deliberately so

| | |
|---|---|
| **Case** | The Salon stage tints each member's underglow pool, beam and chip edge with a per-member accent (`#f0708c` / `#e8bb52` / `#5fe0d2`). If that hue were the only channel it would be a colour-only encoding of *which member is on stage*. It is not: each member also has its own **sprite** and its own **role glyph**, and the chip carries a **live number**. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: play Furina, deploy one of each Salon member, look at the stage under the creature. |
| **Status** | **WORKS.** Three independent channels (sprite, glyph, number) survive total desaturation. The code says this explicitly: the sprint-1 failure being repaired was "three blue silhouettes … read as three identical smudges", and colour was added *on top of* art, not instead of it. |
| **Evidence** | `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:70-76` (per-member sprites), `:78-94` (accent hues + the stated rationale), `:96-108` (per-member role glyphs, white masters tinted through `Modulate`), `:440-487` (chip = glyph + live number from the same expression the tick resolves through). |
| **Automation candidate** | **Yes, already partly built.** `tier0/tests/test_visual_contract_gaps.py:197` pins that the chip and the tick share one expression; `:105-130` is a working precedent for a "these two must be visually distinct or be a listed gap" ledger. |
| **Defect or scope call** | Neither — a working case, recorded as the house pattern the other cases can be measured against. |

### C5 — Elemental aura badges are shape-distinct, not colour-distinct

| | |
|---|---|
| **Case** | `AuraPower` routes its icon to `klee/powers/aura_<element>.png`, one file per element. If those six files were one silhouette in six colours, element identity would be colour-only. |
| **Reproduction** | Reproducible tonight, offline: open `ImageGen/images/powers/aura_{pyro,hydro,cryo,electro,anemo,geo}.png`. Done — all six are distinct Genshin element sigils (flame, wave, six-point snowflake, etc.), not recolours of one shape. |
| **Status** | **WORKS.** The two nearest-hue pairs (hydro/cryo both cyan; anemo/geo) are the ones that most need shape separation and have the most of it — a wave curl versus a six-point star. |
| **Evidence** | `klee-mod/KleeCode/Powers/KleePowerIcons.cs:142-143` (the per-element path expression); assets at `ImageGen/images/powers/aura_*.png`, packed copies at `klee-mod/dist/pck-work/klee/powers/aura_*.png`. |
| **Automation candidate** | Marginal. A perceptual-hash "no two element icons are near-identical" check could hang off `tools/art_lint.py` (it already opens PNGs with PIL and already runs an identical-crop hash, L12, `art_lint.py:310-320`). Low value while the six are hand-picked sigils. |
| **Defect or scope call** | Neither — a working case. |

### C6 — Overhead gauges: colour + skin + icon + number

| | |
|---|---|
| **Case** | Klee, Furina and Kokomi share **one** overhead slot for their Burst meter, and the three are told apart by fill colour. Furina and Kokomi are both hydro, so the hues are close by design. |
| **Status** | **WORKS.** Colour is one of four channels: each gauge also has a distinct *skin* (Klee a fuse-and-bomb with a bomb cap icon; Furina a swallow-tail ribbon plate; Kokomi a plain pearl with a pearl cap icon) and a numeric label, and Kokomi's Charge row deliberately has **no bar at all** so it cannot be confused with a Burst. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: three solo runs, one per character, screenshot the overhead slot at 0 / half / full. |
| **Evidence** | `klee-mod/KleeCode/Vfx/GaugeBridge.cs:116-138` (Klee, `CapIconPath` bomb), `:139-161` (Furina, `RibbonColor` plate — the comment names the "must not be confusable" requirement), `:162-184` (Kokomi, pearl cap), `:185-212` (Charge, `VisualSpan = null`, bar suppressed), `:104-106` (`LabelMax` — the number). |
| **Automation candidate** | Yes, cheap: assert in pytest that no two `GaugeSpec`s share both a near-identical `FillColor` and a null `CapIconPath`/`RibbonColor`. Seam as C1. |
| **Defect or scope call** | Neither. |

### C7 — "Buffed above printed" on the Salon chip is hue-only at 1.25:1

| | |
|---|---|
| **Case** | The Salon chip's tick number renders `#b7f79b` (green) when the live value is above the printed base and white otherwise. Same convention as C2, but this one is **ours**, drawn by our bridge, not by base text rendering. The luminance ratio between the two states is **1.25:1** — effectively hue-only. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: Furina, deploy a Salon member, note the chip number; play Grand Salon (or take Fanfare Focus); the same chip's number turns green without changing shape. |
| **Status** | **UNKNOWN.** It is a colour-only encoding by construction, but it encodes a *nice-to-know* (the number is above its printed base), not a required read — the number itself is always correct and always shown. Whether that makes it acceptable is a judgment nobody has made. |
| **Evidence** | `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:113-116` (`BuffedNumber` / `PlainNumber` / `DryNumber` / `DryEdge` declared), `:481-486` (the three-way choice). Ratio computed from the declared floats by the sRGB relative-luminance formula. |
| **Automation candidate** | **Yes.** A contrast-ratio assertion over the bridge's declared `Color` constants — pure arithmetic, no game, no art. Seam as C1. |
| **Defect or scope call** | **[USER] scope call.** Numbered pick list in §7. |

### C8 — "Dry" (can't afford the tick) is dim, not just differently-hued

| | |
|---|---|
| **Case** | When Encore is short of the tick cost, the whole Salon stage renders "dry": the member sprite is modulated to `(0.55, 0.60, 0.68)`, the chip edge to a dark navy, the glyph and number to `#5C7093`. |
| **Status** | **WORKS.** Dry-vs-live is a **luminance** step, not a hue step: the number's ratio against its live white is **4.89:1**, and the sprite loses ~40% of its brightness. That survives full desaturation. |
| **Reproduction** | Not reproducible tonight — needs the game. Steps: Furina, deploy members, spend Encore below the tick cost, watch the stage dim. |
| **Evidence** | `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:113-116` (`DryNumber` / `DryEdge`) and `:161-165` (`ActiveTint` / `DryTint` / `PoolDry` / `BeamActive`); applied at `:287`, `:466`, `:472`, `:481-486`. Ratios computed from the declared floats. |
| **Automation candidate** | Same seam as C7 — the same assertion covers both. |
| **Defect or scope call** | Neither. |

---

## 4. Case table — flashing, particles, and motion

### E1 — Every mod flash is one-shot, small-area, and at most two pulses

| Surface | Animation | Length | Peak alpha | Rect | Evidence |
|---|---|---|---|---|---|
| Overhead gauge threshold flash | `flash` | 0.60 s, 2 pulses (0.85 then 0.55) | 0.85 | 64 × 10 px | `klee-mod/pck-src/shared/gauge.tscn:18-31`, node at `:87-95` |
| Turn-end docket slot fire | `fire1`–`fire4` | 0.42 s, **1** pulse | 0.85 | 44 × 50 px | `klee-mod/pck-src/shared/turn_end_docket.tscn:54-68`, node at `:149-158` |
| Salon Encore overdraw | `overdraw` | 0.90 s, 2 pulses (0.90 then 0.60) + a 0.72 stage dim | 0.90 | 184 × 16 px | `klee-mod/pck-src/furina/ui/salon_stage.tscn:158-185`, node at `:666-673` |

**Reproduction:** offline for the parameters (read the four `.tscn` files);
in-game for the perceived result, which is not reproducible tonight.

**Status: WORKS.** No mod animation loops a flash, and none reaches three
flashes in any one second — the general-flash threshold every photosensitivity
guideline uses. The largest flashing rect is 184 × 16 px against a 1920 × 1080
default window (`SettingsSave.WindowSize`, `SettingsSave.cs:36`), i.e. well
under one percent of the screen. `AnimationPlayer.Play` is called from exactly
five sites and every one plays a named one-shot: `GaugeBridge.cs:398`,
`KleeCombatVfx.cs:86`, `SalonVisualsBridge.cs:334`/`:338`/`:646`,
`TurnEndPreviewBridge.cs:209`.

**Automation candidate: yes.** A pytest that parses `klee-mod/pck-src/**.tscn`,
walks each `Animation` sub-resource whose track path ends `:modulate`, counts
alpha zero-crossings per second and multiplies by the node's rect area — a
budget check, entirely offline. Seam: `tier0/tests/test_visual_contract_gaps.py`
already parses these same `.tscn` files as text.

**Defect or scope call: neither** — a working case, and the numbers above are
what a future budget would be written against.

### E2 — Particle counts

| Scene | Node | `amount` | `lifetime` | `one_shot` | Evidence |
|---|---|---|---|---|---|
| `klee/vfx/bomb_lob.tscn` | `Boom` | 24 | 0.55 s | true | `:100-107` |
| `klee/vfx/dodoco_pop.tscn` | `Sparkle` | 14 | 0.50 s | true | `:138-145` |
| `furina/vfx/spotlight_shine.tscn` | `Motes` | 18 | 1.00 s | true | `:163-169` |

**Status: WORKS.** Three emitters, 56 particles total, all one-shot, none
autoplaying on a loop. Whether that is *cheap enough* is the
**performance/size/load** family's question, not mine.

**Defect or scope call:** neither.

### E3 — Idle sway loops are the mod's only continuous motion, and nothing can turn them off

| | |
|---|---|
| **Case** | Klee's and Furina's combat scenes each run a looping `idle` animation for as long as the creature is on screen. These are the only continuously-moving things the mod adds. The base game's one motion switch that could stop them — Phobia Mode — works by *node type*: you must place an `NPhobiaAnimationToggler` in the scene and hand it the `AnimationPlayer`. Neither of our two scenes contains one. |
| **Reproduction** | Offline for the fact (`grep -r Phobia klee-mod/pck-src` → no hits); in-game for the effect: tick Settings → Phobia Mode, enter combat, observe that Klee keeps swaying. Not reproducible tonight. |
| **Status** | **UNKNOWN, leaning NOT-SUPPORTED-BY-DESIGN.** Phobia Mode's *intent* (from its own toast strings and its single use site) is not documented in the decompile beyond "disable this animation player", so whether a gentle idle sway is even in scope for it is a guess. The amplitude is small and the period is long: Klee's idle is 3.0 s with ±1.4 px of travel; Furina's is 3.5 s with ±1.4 px. |
| **Evidence** | `klee-mod/pck-src/klee/model/combat.tscn:144-160` (`idle`, `length = 3.0`, `loop_mode = 1`); `klee-mod/pck-src/furina/model/combat.tscn:131-145` (`length = 3.5`, `loop_mode = 1`). Base mechanism: `NPhobiaAnimationToggler.cs:64-84`; the signal it listens to is `NGame.SignalName.PhobiaModeToggled`, emitted by `NPhobiaModeTickbox.cs` `OnTick`/`OnUntick`. |
| **Automation candidate** | **Yes.** A `.tscn` lint: "every `AnimationPlayer` that owns a `loop_mode = 1` animation must be reachable from an `NPhobiaAnimationToggler`, or be on a named exemption list." Same seam and same shape as the existing curated-gap ledger in `test_visual_contract_gaps.py:130`. |
| **Defect or scope call** | **[USER] scope call.** It is not a defect against any stated rule; it is a question about whether the mod opts into a base switch whose intended reach is itself unclear. Numbered pick list in §7. |

### E4 — The mod never shakes the screen, so the screenshake setting is moot for it

| | |
|---|---|
| **Case** | Screenshake is the one base switch that has a true "off" and that mods get for free. Our mod calls none of the four entry points. |
| **Reproduction** | Offline: `grep -rn "ScreenShakeTrauma\|ScreenRumble\|DoHitStop\|Particle" klee-mod/KleeCode --include=*.cs` → zero hits outside `pck-src`. |
| **Status** | **NON-FINDING / WORKS by absence.** Nothing to honour. Recorded because it flips the moment any future mod VFX wants a punch: the correct call is `NGame.Instance.ScreenShake(...)` or `.ScreenShakeTrauma(...)`, and the player's setting is then applied inside `NScreenShake` with no further work. |
| **Evidence** | Absence as above. Multiplier plumbing: `NScreenShake.cs:161-183` (`* _multiplier`), `:202-206`. |
| **Automation candidate** | Yes, trivially: a source lint asserting mod VFX never touches `_screenShake` directly. Currently vacuous. |
| **Defect or scope call** | Neither. |

---

## 5. Compared against Downfall (`@32e6113`)

| Surface | Downfall | Us |
|---|---|---|
| Screen shake | **Calls it** — `NGame.Instance?.ScreenShake(ShakeStrength.Medium, ShakeDuration.Short)` at `Downfall@32e6113:DownfallCode/Vfx/NHemokinesisParticle.cs:102` and `Strong` at `NShockWaveVfx.cs:27`. Both therefore honour the player's screenshake setting automatically. | Never calls it (E4). |
| `[gold]` keyword colour | Same convention, 476 loc files (`Automaton/localization/eng/cards.json:2` ff.). | Same convention, 250 card files (C3). |
| `{X:diff()}` green/red | Same convention (`…/cards.json:2`, `:14`). | Same convention, 246 card files (C2). |
| A mod-owned options screen | **Yes** — `DownfallConfig : SimpleModConfig` with two sections (`DownfallCode/Config/DownfallConfig.cs:6-22`), registered at `DownfallMainFile.cs:42`. Options are *character hiding* and *dev mode*. **No accessibility option.** | **None.** No `ModConfig` type exists in `klee-mod/KleeCode`. |
| Colour-blind / reduced-motion handling | **None found.** | None. |

**One trap, recorded so nobody else falls into it.** Downfall's
`Downfall/scenes/voting/voting.tscn:117-123` contains
`accessibility_name`, `accessibility_description`, `accessibility_live`,
`accessibility_controls_nodes` and friends. These are **Godot's own default
`Control` properties**, serialised empty by the editor. They are **not**
evidence of accessibility work in Downfall. A filename or a property name is
not proof (charter §3.5).

---

## 6. The one implementation seam that exists today

**BaseLib ships a complete mod-options UI system**, and it is proven in a
released mod. If [USER] ever wants a mod-owned toggle — "reduce this mod's
flashes", "high-contrast Salon accents", "still portraits" — this is the seam,
and it costs no base-game patching:

- `BaseLib.Config.SimpleModConfig` — the base class a mod subclasses.
- `BaseLib.Config.ModConfigRegistry.Register(modId, instance)` — the entry point.
- Attributes available: `ConfigSection`, `ConfigSlider`, `ConfigColorPicker`,
  `ConfigTextInput`, `ConfigButton`, `ConfigHoverTip`, `ConfigVisibleIf`,
  `ConfigHideInUI`, `ConfigIgnoreRestoreDefaults`.
- A main-menu entry point exists (`NMainMenu_Ready_Patch.cs`,
  `BaseLibConfig.ShowModConfigInMainMenu`).
- Read from the decompiled BaseLib 3.3.7.0 at
  `…/scratchpad/S13/baselib/Baselib/Config/` (pin: `klee-mod/local.props`
  `BaseLibDll`, Workshop item `3737335127`; version pinned in
  `docs/current/STATE.md`).

Note what this seam is **not**: the base game's own `ModSettings`
(`MegaCrit.Sts2.Core.Modding/ModSettings.cs:8-27`) is enable/disable only — it
carries `mods_enabled` and a per-mod on/off list and nothing else. The options
UI is BaseLib's, not MegaCrit's.

*This is a technical statement of what exists. It is `PROPOSED` only in the
sense that it names a mechanism; whether to spend anything on it is §7.*

---

## 7. What returns to [USER] — numbered pick lists

Nothing below is a recommendation and none of it has a default.

**Q1 — Furina/Kokomi seat colour (C1).** The pair is 1.44:1 in luminance and
both cyan; in co-op it is the only who-is-who channel on the map and the
targeting line.
1. Leave both hues as they are.
2. Move one of the two (which one, and to what, is a taste call).
3. Leave the hues and add a non-colour cue — but note that the map line, the
   ping and the targeting line are all base-drawn, so a second cue is a base
   patch, not a colour swap.
4. Declare it out of scope until co-op is a shipping concern.

**Q2 — the buffed-number green on the Salon chip (C7).** Hue-only at 1.25:1,
ours, and it encodes a nice-to-know rather than a required read.
1. Leave it (it matches the base game's own convention).
2. Raise the contrast of the buffed state against the plain state.
3. Add a non-colour mark (a `+`, a weight change) beside the number.
4. Drop the distinction and always render the live number plain.

**Q3 — idle sway loops and Phobia Mode (E3).** Two scenes loop a 3–3.5 s,
±1.4 px sway that no player setting can stop.
1. Leave them; Phobia Mode's reach is undocumented and a gentle sway is
   probably not what it is for.
2. Wire `NPhobiaAnimationToggler` into both combat scenes so the base tickbox
   stops them.
3. Neither — add a mod-owned toggle through the BaseLib seam in §6.
4. Defer until there is a public-release decision to hang it on.

**Q4 — whether a mod-owned options screen is in scope at all (§6).** The seam
exists and Downfall proves it works.
1. No mod options screen; the mod stays option-free.
2. An options screen, but not for accessibility (the Downfall shape).
3. An options screen carrying motion/contrast toggles.
4. Decide after a public-release scope call, since a private-playtest build has
   an audience of one.

**Q5 — whether any of this becomes an automated gate.** Four offline
automation candidates are named above (C1/C6/C7/C8 as one contrast-and-distance
assertion over declared `Color` constants; E1 as a flash-budget parse of
`pck-src/**.tscn`; E3 as a loop/toggler reachability lint). Each is a normal
pytest beside `tier0/tests/test_visual_contract_gaps.py` and needs no game.
1. Build none of them.
2. Build the colour-constant assertion only (cheapest, covers C1/C6/C7/C8).
3. Build the flash-budget parse only.
4. Build all three as one small suite.

---

## 8. UNKNOWN

- **U1.** Whether the screenshake multiplier is applied at all before the
  settings screen is first opened in a session. `NScreenShake._multiplier` is a
  plain `float` field, never initialised in `_Ready` (`NScreenShake.cs:107`,
  `:114-126`), and its **only** writer in the entire decompile is
  `NScreenshakePaginator` (`:78` in `SetFromSettings`, `:91` in
  `OnIndexChanged`). Whether that paginator's node enters the tree at boot
  depends on scene instantiation that the decompile does not show. This is a
  **base-game** observation, cited because it is the seam any future mod shake
  would ride; it is not ours to fix and it is not evidence of a bug.
- **U2.** Whether the Phobia Mode tickbox is *intended* to cover gentle idle
  motion at all. Its only mechanism is "deactivate this one AnimationPlayer"
  and its toast strings are in a loc table inside `sts2.pck`, not read here.
- **U3.** Every in-game perceptual question in §3 and §4 — legibility at real
  scale, at real distance, under a real colour-vision deficiency. Nothing in
  this census was seen running. [USER] is playtesting on `0.2-1159`; no agent
  launched, deployed to, or wrote under the game installation tonight.
- **U4.** Kokomi has no `pck-src/kokomi/model/combat.tscn` in this checkout, so
  E3's idle-loop inventory covers two of three roster characters. Whether that
  is a gap or a different rendering route is the **S16 animation** stream's
  question, not mine.

## 9. NON-FINDINGS

- **N1.** No colour-blind mode, colour-blind palette, or daltonisation shader
  exists in Slay the Spire 2 v0.107.1. Search boundary in §2.
- **N2.** No reduced-motion, motion-sensitivity, or photosensitivity setting
  exists in the same build. Same boundary.
- **N3.** No public StS2 mod examined tonight exposes a colour or motion
  accessibility option. Boundary: Downfall at the pinned commit (the only
  released StS2 mod in this dispatch's reference set) plus BaseLib 3.3.7.0.
  Widened once to BaseLib's own config surface, which carries logging and
  mod-source options only (`BaseLibConfig.cs:1-60`). Absence stays absence.
- **N4.** Our mod contains no screen shake, no rumble, no hit-stop, and no
  looping flash. (E1, E4.)
- **N5.** No mod surface was found where colour is the *sole* channel for a
  read the player must make in order to play correctly. The two colour-only
  cases that exist are C7 (a nice-to-know, ours) and C2/C3 (base-owned
  conventions). C1 is the closest thing to an exception and it is co-op-only
  and unverified in play.

---

## 10. What this does NOT establish

This is a census of what the code and the assets say, read offline. It does not
establish that any surface here is legible, comfortable, or safe for any real
player — nothing was seen running, no capture was taken, and no player was
observed. It does not measure contrast against real backgrounds (the ratios
quoted are between two declared foreground constants, not against what is
behind them). It does not prove the base game lacks a shader-level accessibility
option in some build other than the pinned one. It rules nothing in and nothing
out about what the mod should support: no accessibility promise, no language or
player-count promise, and no ship-scope claim is made or implied anywhere above.
