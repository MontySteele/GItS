# Understudy P0 - Findings and Ruling Proposals

Sprint: Understudy (bot playtest apparatus). Phase: P0, evaluate only.
Brief: `docs/understudy-kickoff-brief.md`. Date: 2026-08-04. Worktree G4.
Status: PROPOSED. Every ruling below is a PROPOSAL; [USER] countersigns.

Nothing was built. Three community artifacts were evaluated, one of them
end-to-end against a live GItS build. Two throwaway probes (a source clone
tree and a decompile scratch) live outside the repo and are not committed.

## The headline

The apparatus we were going to build mostly exists, and it works with our
mod today. The state/action bridge reads our cards, our relics and our
powers with no vocabulary work on our side, and it can inject plays through
the game's own action queue. It compiles clean against the exact game build
we ship on. Measured, not inferred: a Furina run was started, driven into
combat, and played through this bridge during this pass.

The half we assumed we needed a bridge for -- the overnight soak -- is a
different story, and it comes with a correction to something the repo
already believes. See "AutoSlay is a god-mode runner" below.

| # | Artifact | Ruling PROPOSAL | Confidence |
|---|---|---|---|
| 1 | STS2MCP (Gennadiyev) | **ADOPT**, as a pinned vendored fork | High - tested live against GItS |
| 1b | STS2-Agent (CharTyr) | **DECLINE** | High - license + architecture |
| 1c | sts2-modding-mcp (Nexus 345) | **DECLINE for Understudy** | Medium - Nexus page blocked |
| 2 | LocalCoop (STS2CouchCoop) | **HOLD for P3**, do not adopt yet | Low-Medium - not boot-tested |
| 3 | Speed affordances | **BUILD** (ours, ~10 lines) | High - verified in the assembly |

## Environment pins

Everything below was measured against one build. Record it; a later pass
that disagrees should check this first.

| Thing | Value |
|---|---|
| Game | v0.107.1, commit 59260271, dated 2026-06-18 |
| main_assembly_hash | -1555940892 |
| Game dir | `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2` |
| Installed mods at eval time | klee (GItS), quick_fingers, STS2AutoSlayMod, + Workshop BaseLib / Downfall / PengoTarot |
| Suite at close | 1425 passed, 41 skipped |

---

## Artifact 1 - the state/action bridge

### The repo is STS2MCP, and there are two candidates, not one

The GitHub `slay-the-spire-2` topic surfaces two mods matching the brief's
description. They are not the same project and they are not equivalent.

**STS2MCP** - `github.com/Gennadiyev/STS2MCP`, Nexus mod 791, author
"kunology". MIT. C# `net9.0` Godot mod plus an optional Python MCP server.
Local REST API on `localhost:15526`, no auth. ~12,600 lines across the mod
and the server.

**STS2-Agent** - `github.com/CharTyr/STS2-Agent`, Nexus mod 155. AGPL-3.0-only.
Port 8080. Latest release v0.8.0, 2026-07-06.

### Version pin - the important half

The brief flagged game-version conflicts as stop-and-surface. There is one,
and it resolves in our favour, but only if we build from source.

- STS2MCP's latest *tagged release* is **0.4.0, 2026-05-05**. That binary
  predates our game build.
- STS2MCP's **HEAD is `55e0648`, 2026-07-29, "Fix game API compatibility
  with STS2 v0.107 (#123)"**. That is our game line.

So: **do not use the Nexus/GitHub release artifact. Pin commit `55e0648`
and build it.** I built it against our install:

```
dotnet build -c Release -p:STS2GameDir="...\Slay the Spire 2"
Build succeeded. 0 Warning(s). 0 Error(s). Time Elapsed 00:00:03.32
```

Its `.csproj` references `sts2.dll`, `GodotSharp.dll` and `0Harmony.dll`
out of `data_sts2_windows_x86_64` -- the same three references, the same
target framework and the same GameDir-from-a-property pattern as
`klee-mod/Directory.Build.props`. It drops into our build world without
argument.

### Does it expose MODDED content? Yes - completely, and by construction

This is the question the brief cared most about, so it was answered live
rather than by reading code.

The mod was installed, the game booted with GItS loaded alongside it, and
the bridge was driven from the main menu into a seeded Furina fight. The
character list came back with our roster as first-class entries:

```
KLEEMOD-FURINA | Furina | hp 60 | cards 89 | relics 10 | locked False
   deck: Soloist's Solicitation, Soloist's Solicitation, ... Stage Presence ...
KLEEMOD-KLEE   | Klee   | hp 62 | cards 126 | relics 10
KLEEMOD-KOKOMI | Kokomi | hp 70 | cards 62  | relics 10
```

In combat, the hand serialized with full GItS semantics -- ids, real rules
text, and our *custom keywords*:

```
0 KLEEMOD-ARIA_OF_RECOMPENSE | Aria of Recompense | cost 1 | target Self | can_play True
    desc: Gain 5 Encore. Gain 0 Block. Scales with Fanfare.
    kw: ['Fanfare scaling', 'Block']
2 KLEEMOD-SALON_DEBUT | Salon Debut | cost 1 | target Self | can_play True
    desc: Add 1 random Salon Member to your Salon.  Elemental Skill.
    kw: ['Mademoiselle Crabaletta', 'Gentilhomme Usher', 'Surintendante Chevalmarin',
         'Salon', 'Elemental Skill']
5 KLEEMOD-ETHEREAL_SPOTLIGHT | Ethereal Spotlight | cost 0 | target Self
    desc: Ethereal. Choose Center Stage or Guest Cast. ...
```

Our relic came through as `KLEEMOD-ETHEREAL_SPOTLIGHT_RELIC`, and after a
`Salon Debut` the Salon power appeared in player status with its full
description text.

The reason this works is architectural, not lucky. `BuildCardInfo` reads
the *live* `CardModel`:

```csharp
["id"]          = card.Id.Entry,
["name"]        = SafeGetText(() => card.Title),
["type"]        = card.Type.ToString(),
["rarity"]      = card.Rarity.ToString(),
["description"] = SafeGetCardDescription(card, pile),
["keywords"]    = BuildHoverTips(card.HoverTips)
```

There is no card catalog, no enum whitelist, no baked id table anywhere in
the read path. Anything that is a `CardModel` serializes. Every GItS card
derives from BaseLib's `CustomCardModel` (112 + 42 + 36 + ... = all 347
source files resolve to `CustomCardModel`, `PowerModel`, `CustomRelicModel`
or `CustomCharacterModel`), so we are `CardModel`s all the way down.

**What our custom ops look like on the wire: they do not.** There are no
custom ops. A GItS card is played by the same `play_card` verb as a Strike,
addressed by hand index, targeted by `entity_id`. The protocol is
vocabulary-free. That is the single most important finding in this pass --
it means no bridge-side work is owed per card, per character, or per sprint.

### Can it INJECT actions? Yes - through the game's own action queue

Not read-only. Verified live: two GItS cards were played through the HTTP
API, damage landed (enemy 56 -> 50 HP), the Salon power applied, and energy
decremented 3 -> 1.

```csharp
// McpMod.Actions.cs:140
RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(new PlayCardAction(card, target));
```

That is exactly the mechanism the brief nominated for our own build
("Harmony hooks on the action queue"). The fallback design and the existing
mod are the same design; theirs is finished.

Coverage is broad: `play_card`, `use_potion`, `discard_potion`, `end_turn`,
`choose_map_node`, `choose_event_option`, `advance_dialogue`,
`select_card_reward`, `skip_card_reward`, `claim_reward`,
`choose_rest_option`, `shop_purchase`, `claim_treasure_relic`,
`select_card`/`confirm_selection`, `select_relic`, bundle selection, the
Crystal Sphere minigame, `menu_select` (including character select with an
explicit `seed`), profile switch/delete, and a multiplayer verb set.

Seeded starts are first-class, which P1 needs: `menu_select` accepts
`seed`. I used `1A2B3C4D`.

### Why not STS2-Agent

Three independent reasons, any one sufficient:

1. **AGPL-3.0-only.** GItS is a public repo. Vendoring or forking an
   AGPL bridge into our mod tree is a licensing decision with reach well
   beyond this sprint. STS2MCP is MIT. This alone settles it.
2. **Baked catalogs.** It ships static `mcp_server/data/eng/*.json` for
   cards, relics, monsters, powers, events. A static base-game catalog is
   precisely the "base-game vocabulary only" failure mode the brief asked
   about. Its live path may be fine; its knowledge layer is not ours.
3. **Stale against our build.** v0.8.0 is 2026-07-06 with no v0.107 compat
   commit visible; STS2MCP has one dated 2026-07-29.

### Nexus mod 345 - BLOCKER, and a partial answer

`nexusmods.com/slaythespire2/mods/345` returns **HTTP 403** to an
unauthenticated fetch. Recorded as a blocker per the brief; evaluated from
source instead. The source-side match is `github.com/elliotttate/sts2-modding-mcp`
("STS2 Modding MCP", 151 tools).

It is a **modding-development assistant**, not a play bridge: decompilation,
entity indexing, code generation, build/deploy, Godot scene inspection, 29
guides. The overlap with Understudy is narrow -- it also ships a test mod
with an automated-playtest surface and a `set_game_speed` tool.

Overlap verdict: it duplicates infrastructure GItS already owns and has
ratified (our own deploy/validate tooling, our decompile workflow, our
lints), its HEAD is `ed38d78` dated **2026-03-31** -- four months stale,
well before v0.107 -- and its unique contribution to this sprint is one
three-line function. **DECLINE for Understudy.** If [USER] wants it as a
dev-side convenience that is a separate ruling on a separate sprint; it is
not on the apparatus path.

### Ruling PROPOSAL 1: ADOPT STS2MCP as a pinned vendored fork

ADOPT, not plain-adopt: pin commit `55e0648`, build from source, and vendor
it as a sibling component rather than depending on a Nexus binary. Rationale:

- The released binary is version-stale; only HEAD matches our game.
- A pinned commit is reproducible; "latest Nexus" is not, and a co-op
  lockstep project already knows what unpinned build identity costs (R70).
- MIT permits vendoring cleanly.
- We will want small additions (telemetry hooks, a speed verb, a policy
  callback). Owning the tree makes those cheap, and upstreaming stays open.

FORK-with-injection is *not* needed: injection already exists. The word
"fork" here means version control, not capability.

Estimated cost of the alternative (BUILD our own bridge, for the record):
STS2MCP covers roughly 20 distinct screen/state types and ~30 action verbs,
in ~12.6k lines. The screens are not optional -- a bot that cannot answer a
bundle-select overlay soft-locks the soak, which is the exact failure P1 is
built to detect. Reaching parity on only the screens a real run traverses is
a 3-5 session build plus a recurring per-patch maintenance tax that upstream
is currently paying for us. **Write-our-own is the more expensive path**, so
this is not a stop-and-surface trigger -- it is the reverse.

---

## Artifact 2 - LocalCoop

`github.com/Bahnerbd/STS2CouchCoop`, Nexus mod 1314.

### The version pin is better than the brief assumed

The README and Nexus page both say "tested against v0.103.3", and the brief
inherited that. The release list says otherwise:

| Tag | Date | Note |
|---|---|---|
| 0.1.2 | 2026-07-18 | **built and tested on STS2 v0.107.1** |
| 0.1.1 | 2026-07-13 | built and tested on STS2 v0.107.1 |
| 0.1.0 | 2026-06-23 | built and tested on STS2 v0.103.3 |

**v0.107.1 is our exact build.** The prose is stale, not the mod. The
version-pin stop-and-surface does not fire.

### Steam networking - bypassed, and that answers the brief's question

The brief asked whether any Steam-networking dependency survives loopback.
From the source: LocalCoop substitutes the lobby/net service and runs its
own TCP broker. The patch set is explicit --
`BrokerLobbyServiceSubstitutionPatch`, `BrokerHostStartupBypassPatches`,
`BrokerClientJoinFlowPatch`, `BrokerClientLobbyHandshakePatch`,
`BrokerLocalPlayerIdPatch`, plus `BrokerTcpServer` and
`InMemoryBrokerSession` in a separate broker assembly.

So the native multiplayer transport is replaced by loopback TCP, not
tunnelled over Steam. No Steam-networking stop-and-surface.

It also ships a `BaseLibHealthBarForecastCompatibilityPatch` -- meaning
upstream has already hit and fixed at least one BaseLib interaction, which
is mildly encouraging for a BaseLib-dependent mod like ours.

### The controller question - UNRESOLVED, and I did not test it

The brief asked: does a bot-driven client work with no controller attached?
**I did not boot two clients.** That is a deliberate scope call -- it needs
a two-client session, a second profile, and the bridge running in both, and
the brief scoped P3 as deferred and gated. Reporting it as untested rather
than guessing.

What the source says, which is suggestive but not sufficient:

- Supported: one controller per client, OR one mouse/keyboard driving all
  clients. Explicitly unsupported: mixing mouse and controller across
  clients, because STS2 switches globally into controller mode when any
  active player uses one. That is a game input-system limitation, and
  LocalCoop says rewriting it is out of scope.
- Controller assignment comes from "Steam Input's stable session inventory"
  after the developer logo, via `DynamicControllerStartupPatches` and
  `ControllerInputOwnershipPatches`.

The reason for optimism: a bot seat needs no input device at all. The bridge
drives lobby and character select through `menu_select` and its multiplayer
verbs (`McpMod.MultiplayerActions.cs`, `McpMod.MultiplayerState.cs`), which
enqueue actions directly and never touch the input stack. The reason for
caution: LocalCoop's *ownership* model is built around controller slots, and
a seat with no assigned input may never be granted ownership in the first
place, which would strand it before the bridge can act.

That is the P3 gating experiment, and it is one experiment: boot 2 clients,
attach zero controllers, and see whether the bridge can ready up both seats.

### Ruling PROPOSAL 2: HOLD for P3

Do not adopt, do not install, do not fork yet. It is a live option -- right
game version, Steam dependency genuinely bypassed, source available and
patch-shaped in a way we can read -- but it is self-described Experimental
Alpha with no promise of arbitrary mod compatibility, and GItS is exactly
an arbitrary mod. Revisit after P1 is stable, and let the single ownership
experiment above be the gate.

One useful thing it taught us regardless of the ruling, see below.

---

## Artifact 3 - speed, and the AutoSlay correction

### There is no speed problem. There are two switches, both ours

**1. The game ships an undocumented instant mode.** Decompiled from *our*
`sts2.dll`:

```csharp
namespace MegaCrit.Sts2.Core.Settings;
/// <summary>Enum used for changing how fast the game runs.
/// This is NOT a multiplier-based speed setting.</summary>
public enum FastModeType { None, Normal, Fast, Instant }
```

The settings UI exposes Normal/Fast. `Instant` exists in the enum and is
reachable by writing `SaveManager.Instance.PrefsSave.FastMode`. STS2MCP
already injects a checkbox for it (`McpMod.SettingsUI.cs`), which is both a
proof it works and a ready-made reference implementation.

**2. Godot's own time scale.** `Godot.Engine.TimeScale = speed` -- the
mechanism behind the "20x speed" claim in the modding-assistant repo, which
is literally three lines there.

Neither needs a bridge, a fork, or a negotiation. Both are ours.

### AutoSlay is a god-mode runner - and this corrects a repo document

The game contains a full first-party automated runner, `MegaCrit.Sts2.Core.AutoSlay`:
`AutoSlayer`, `AutoSlayConfig`, `AutoSlayLog`, a `Watchdog`, a
`MemoryProfiler`, an `AutoSlayTimeoutException`, and screen/room handlers for
every screen a run traverses. `mods/STS2AutoSlayMod` (Nexus, "AutoSlay
Unlock" v1.5.0) is already installed on this machine and already configured
for `"character": "KLEEMOD-FURINA"`, `"afterRun": "loop"`. `tier1/analyze.py`
already reads the resulting run histories. This half of the apparatus has
existed all along.

But `CombatRoomHandler` does this, first thing, every fight:

```csharp
await PowerCmd.Apply<PlatingPower>(..., playerCreature, 999m, ...);
await PowerCmd.Apply<RegenPower>(..., playerCreature, 999m, ...);
```

999 Plating and 999 Regen. Then it plays a **uniformly random** playable
card at a **random** target until none remain, and dumps every potion
immediately. Its own summary line is "Applies massive defensive buffs and
plays all cards each turn." Config: 25-minute run timeout, floor cap 49,
30-second watchdog.

AutoSlay is a **coverage** runner. It is designed to walk every screen
without dying, not to play.

`tier1/analyze.py`'s scope caveat is therefore right in its conclusion and
wrong in its reason. It says AutoSlay is bad for validating winrate because
it "drives the base game's heuristics" and "does not draft the way Tier
0.5's pilots draft". The truth is stronger: there are no heuristics, the
drafting is random (`AutoSlayCardSelector` shuffles and takes N; card
rewards are `_random.NextInt(options.Count)`), and the player is
functionally immortal. Any winrate, HP trajectory, damage-taken or
killed-by-encounter figure from an AutoSlay soak is not pilot-limited --
it is **invalid**, and a near-100% winrate from it means nothing at all.

Two consequences, neither of which I acted on (out of P0 scope, and
`tier1/` is not mine to edit this pass):

- **Recommended follow-up:** correct that docstring, and consider whether
  `summarize()` should refuse to print `winrate` for AutoSlay-sourced runs
  rather than printing a number no one may quote. This is the
  structurally-invisible-defect pattern: the caveat is prose, and prose
  does not stop a number from being read off a report at 3am.
- **For P1 design:** the brief's per-fight telemetry (damage by source, HP
  trajectory, incoming attacks/turn) **cannot** come from an AutoSlay soak.
  It has to come from policy-driven play through the bridge. AutoSlay
  remains excellent for what it is: crash, softlock, unreachable-state and
  pool-coverage hunting, which is genuinely half of P1's acceptance bar.

### A first-party policy seam exists, for later

`AutoSlayCardSelector` implements `MegaCrit.Sts2.Core.TestSupport.ICardSelector`.
A first-party interface for "who chooses the cards" is a real seam -- our
policy could implement it. Noting it, not proposing it: with the bridge
adopted we do not need it, and taking both paths would give us two policies
that can disagree. Recorded so a later session does not have to rediscover
it.

### Ruling PROPOSAL 3: BUILD (trivially), and keep AutoSlay in its lane

BUILD the speed control ourselves -- `FastModeType.Instant` plus an optional
`Engine.TimeScale` multiplier, roughly ten lines, in our fork of the bridge
so it is drivable over HTTP by the soak harness. ADOPT nothing for speed.
Keep AutoSlay as the crash-soak instrument it already is, with its numbers
firewalled from anything gradeable.

---

## P0 acceptance questions, answered

**Q: Does the state bridge expose MODDED content, or only base-game
vocabulary? If schema-driven, what do our custom ops look like on the wire?**
Fully modded. Verified live: all three GItS characters, our cards with real
ids and rules text, our custom keywords (Fanfare scaling, Salon, Elemental
Skill), our relic, our Salon power. It reads live `CardModel`/`PowerModel`
objects; there is no catalog to extend. Our custom ops look like *nothing
special on the wire* -- there are none. A GItS card is played with the same
`play_card` verb as a Strike.

**Q: Can it INJECT actions, or is it read-only?**
It injects, via `ActionQueueSynchronizer.RequestEnqueue` -- the same path
the game UI uses. Verified live by playing two GItS cards and observing
damage, energy and a power applied. Card plays, targeting, rewards, map
paths, events, shops, rest sites, card/relic/bundle selection, menus and
seeded run starts are all covered. The read-only contingency ("then we fork
and add injection") does not fire.

**Q: Does LocalCoop boot 2 clients with GItS + the bridge loaded, and does a
bot-driven client work with no controller attached?**
**UNTESTED - not attempted this pass.** Scoped to the P3 gate. What is
established: the right game version exists (0.1.2 on v0.107.1), Steam
networking is genuinely bypassed by a loopback TCP broker, and the bridge's
multiplayer verbs need no input device. What is unknown: whether LocalCoop's
Steam-Input-derived seat-ownership model will grant a seat to a client with
no controller. One experiment settles it.

**Q: If bridges are unusable, estimate our own bridge.**
The bridges are usable, so this is recorded as a rejected alternative rather
than a plan: 3-5 sessions to reach traversal parity across ~20 screen types
and ~30 verbs, plus a per-game-patch maintenance tax that upstream currently
absorbs. Write-our-own is the *more* expensive path. Downfall was not needed
as an architecture reference -- STS2MCP already implements the exact
action-queue design the brief proposed.

---

## Stop-and-surface

1. **Nexus is unreachable to me (blocker).** `nexusmods.com/.../345` returns
   HTTP 403 unauthenticated; the brief's fallback (evaluate from source) was
   taken. Any future task that requires a Nexus download comes back to
   [USER]. Note that nothing in the proposed path needs one -- STS2MCP is
   built from GitHub source, and LocalCoop is on GitHub too.
2. **Pin the commit, not the release.** If a later session installs STS2MCP
   from Nexus/releases (0.4.0) instead of commit `55e0648`, it will be
   running a pre-v0.107 binary against a v0.107.1 game. This is the one way
   to get the version-pin failure the brief worried about, and it is easy to
   do by accident.
3. **AutoSlay numbers are invalid, not merely limited** (999 Plating + 999
   Regen + random play). `tier1/analyze.py` currently prints a `winrate` for
   such runs and explains the caveat only in prose. Flagged for a ruling; not
   edited this pass.
4. **A run was left in progress on the local profile.** Seed `1A2B3C4D`,
   Furina, Act 1 floor 1, one fight partly played. It will show as a
   resumable run. Abandon it in-game (or just start a new run) to clear it.
   No save files were edited or deleted by me.
5. **P1's telemetry cannot come from AutoSlay.** If the soak harness is
   built expecting AutoSlay to supply HP trajectories and damage-by-source,
   it will produce god-mode data that looks plausible. Policy-driven play
   through the bridge is the only source for the brief's per-fight surface.
6. **Not a blocker, but a P1 design input:** scripted launching needs
   `steam_appid.txt` in the game root (Steam running, but the exe launched
   directly). Without it the game hard-fails at
   `SteamInitializer.InitializeInternal` and never loads mods -- I hit this
   before finding that LocalCoop solves it the same way. A soak launcher must
   create that file; it is a game-dir write, so it belongs in the harness's
   own setup/teardown rather than being left behind.

---

## Appendix A - reversibility log (game dir)

Every change made to `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2`
during this pass, and how each was undone. **All of them have been reverted;
the game dir is back to its pre-pass state.** Verified by listing after.

| # | Change | Undo | State |
|---|---|---|---|
| 1 | Created `mods\STS2_MCP\` containing `STS2_MCP.dll` (built from source, 236,544 bytes) and `STS2_MCP.json` (upstream `mod_manifest.json`, renamed) | `rm -rf mods\STS2_MCP` | **REVERTED** - `mods\` now lists exactly `STS2AutoSlayMod`, `klee`, `quick_fingers`, as before |
| 2 | Created `steam_appid.txt` containing `2868840` at the game root, to allow launching the exe directly with Steam running | `rm steam_appid.txt` | **REVERTED** - file absent |
| 3 | Launched the game twice (once failed on Steam init, once succeeded); both processes terminated | n/a | Not running |

Not modified, for the avoidance of doubt: `mods\klee\` (our deployed build),
`mods\STS2AutoSlayMod\autoslay_settings.json`, any Workshop content, any
`.pck`, and anything under `%APPDATA%\SlayTheSpire2\` other than what the
game itself wrote during a normal boot (its own logs, `settings.save`, and
the in-progress run noted in stop-and-surface item 4).

## Appendix B - artifacts evaluated

Clones and decompiler output live in the session scratchpad, outside the
repo, and are not committed. Decompiled MegaCrit material was read for
assessment only and none of it is reproduced here beyond the short quotations
above, per the IP rule (.gitignore `sts2_decompiled/`).

| Repo | Pinned at | Date | License |
|---|---|---|---|
| Gennadiyev/STS2MCP | `55e0648` | 2026-07-29 | MIT |
| CharTyr/STS2-Agent | `6957e27` (v0.8.0) | 2026-07-06 | AGPL-3.0-only |
| Bahnerbd/STS2CouchCoop | release 0.1.2 | 2026-07-18 | see repo LICENSE |
| elliotttate/sts2-modding-mcp | `ed38d78` | 2026-03-31 | see repo LICENSE |

## Appendix C - what P1 should inherit from this pass

Not a plan, just the load-bearing facts, so the next session does not re-derive them.

- Bridge: build `55e0648`, install as `mods\STS2_MCP\{STS2_MCP.dll,STS2_MCP.json}`,
  health-check `GET http://localhost:15526/` before driving anything.
- Launch: `steam_appid.txt` = `2868840` at the game root, Steam client running,
  then run `SlayTheSpire2.exe` directly. Boot to a usable bridge took ~50s here.
- Seeded start: `menu_select` with `option` = `KLEEMOD-FURINA` (or `-KLEE` /
  `-KOKOMI`) and `seed`, then `menu_select` `confirm` to embark.
- Screens are turn-taking: `GET` to see `state_type`, `POST` the verb that
  `state_type` advertises. `state_type: "overlay"` is the catch-all for an
  unhandled screen and is the shape a soft-lock will take -- watchdog on it.
- Run outcomes still land in the game's own `saves/history/*.run`, which
  `tier1/analyze.py` already parses. Policy-driven runs and AutoSlay runs
  will land in the same tree; they must be distinguishable before both are
  read as "the soak".
