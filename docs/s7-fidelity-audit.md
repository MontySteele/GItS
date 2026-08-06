# S7 — the sim fidelity replay audit

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Opened and closed 2026-08-05, Surplus Dispatch 2, item S7. Worker pass only:
this document **inventories, measures and files**. It classifies nothing and
proposes nothing. A separate pass reads `docs/s7-divergences.tsv` and decides
what the rows mean; that decision is not made here and no row below should be
read as though it had been.

Guardrail 7 applies unchanged. Every engine-side number in this audit came out
of a bot soak, which is a bot-limited floor. Nothing here is a balance finding,
a winrate, or evidence about how the game feels.

Zero design authority was exercised. No constant, card, sheet or rule was
touched; the only files this pass adds are `understudy/replay.py`, this
document and the TSV.

---

## 1. Inventory

The R100 close-out recorded that the 87-fight input corpus behind
`docs/track-b-curves.md` "no longer exists in one piece." That is accurate
about *that* corpus. It is not the whole picture: the machine still holds the
soak output that produced it, spread across the agent worktrees that ran the
soaks, plus a second, independent recording of a subset of the same fights
written by the C# mod.

### 1.1 What exists

| location | files | fights | action sequences? |
|---|---|---|---|
| `\.claude\worktrees\agent-a34f8b1ce5f780915\understudy\logs\soak\` | 14 run JSONLs, soaks `20260804-221045`, `-222105`, `-224517`, `-225937` | 61 | **full** |
| `\.claude\worktrees\agent-a391c0e492a6c05ba\understudy\logs\soak\` | 19 run JSONLs, soaks `20260804-205525` … `-212539` (9 of the 19 runs died before a fight closed) | 48 | **full** |
| `\.claude\worktrees\agent-a689914dafb122c14\understudy\logs\soak\` | 6 run JSONLs, soaks `20260805-003056`, `-004135` | 30 | **full** |
| `%APPDATA%\SlayTheSpire2\gits_telemetry\` | 6 `play-*.jsonl`, 2026-08-04 22:46 → 2026-08-05 00:47 | 55 | **summary only** |
| `understudy\logs\phase0-SSRWEGLNRG.jsonl` (committed, in every worktree) | 1 | 0 | Phase-0 decisions, pre-schema — no `record` field, no `fight` rows |

**Totals: 39 soak run logs, 5 704 `decision` rows, 139 closed `fight` records,
18 `defect` rows, 97 `forced_default` rows.** All 139 bot fights carry a full
posted action stream: 2 738 `play_card` actions with resolved card name,
target, hand contents at the moment of the play, and — on 1 267 of them — the
target's HP as read immediately before the action.

The Godot user dir is `%APPDATA%\SlayTheSpire2\`, not an
`app_userdata\<game>\` path; `%APPDATA%\Godot\app_userdata\` on this machine
contains only `KleePck`.

### 1.2 The second recording

The `gits_telemetry` rows are stamped `feed: "bot"`, `source: "mod"` — the C#
`PlayTelemetry.cs` writer was live *inside the game process* while the soak
drove it from outside. Pairing on timestamp (±10 s) matches **53 of the 55
mod-feed fights to a soak-feed fight**, i.e. 53 fights were recorded twice by
two instruments that share no code.

That is not a sim comparison and it is not treated as one. It is a control:
where the two readings of the same fight disagree, the disagreement is a
property of the instruments, and any sim divergence measured against either
reading inherits that uncertainty. Those rows are in the TSV under the
`xfeed.*` prefix and every one of them is emitted with
`suspected_reading_corruption = 1` by construction.

### 1.3 Verdict

**Replayable.** 139 fights, all with full action sequences. The audit
proceeds.

---

## 2. Method

`understudy/replay.py` (new). It reads soak run JSONLs, splits each into
fights (a `fight` record closes the combat `decision` rows before it, which is
the order `soak.py` writes them), resolves every card display name to a tier0
card, and drives `tier0.engine` directly. It does not retype any game rule:
`effects.resolve_card`, `combat.play_card` and `resources.decay_fanfare` are
the tier0 entry points, and `loader.build_player` builds the character.

Two levels run over every fight.

**L1 — per card.** Two consecutive targeted plays at the same target in the
same turn bracket exactly one card in the engine's own readings:
`target_hp[n] − target_hp[n+1]`. The sim is asked the same question in
isolation — a fresh `CombatState`, the player's meters loaded from that turn's
opening reading, one enemy at the bracketing HP, one `resolve_card`. Because
only one enemy is present, tier0's implicit lowest-HP targeting cannot pick
the wrong one. **544 comparisons.**

**L2 — per turn.** The turn's opening reading (HP, block, fanfare, salon
members, salon cap, encore) is loaded, the recorded hand is dealt by name, the
recorded cards are played in the recorded order through `combat.play_card`,
and the turn's closing numbers are compared against the log: block at turn
end, the enemy-pool drop across the turn, and the next turn's opening fanfare,
salon members and encore. **277 block, 262 pool, 262 fanfare, 262 salon, 85
encore comparisons.**

Two record-integrity checks run alongside, and their rows are flagged as
reading questions rather than sim questions: `record.cards_played` (the
`fight` record against the posted actions **in the same log, by the same
writer**) and `xfeed.*` (soak feed against mod feed on the 53 paired fights).

### 2.1 Declared confounders

These are stated once, apply to every row, and are the reason the
classification pass exists.

1. `combat.play_card` takes **no target**. Single-target aim in tier0 is always
   the lowest-HP living enemy. L1 presents one enemy so this cannot bite; L2
   carries `n_enemies` in every row's context because on a multi-enemy fight a
   targeting difference is a live alternative explanation for a pool row.
2. **Relics, potions, pile order and exhaust contents are not on the wire** and
   are not reconstructed. A relic that adds damage or block is invisible on the
   sim side of every row.
3. **Enemy block and enemy powers are not carried per enemy.** `target_hp` is
   an HP reading, so a card partly eaten by enemy block reads short.
4. **Player Strength / Vulnerable accrued within a turn is not reconstructed at
   L1** — each card resolves from the turn-opening reading — so an L1 row for a
   card played late in a long turn understates the sim by that turn's own ramp.
   L2 does accrue it.
5. **Base-game cards have no tier0 row at all.** 35 plays across five names
   (Drain Power 16, Ball Lightning 9, Fisticuffs 5, Boost Away 3, Finesse 2)
   were skipped, never approximated. Non-playable strays in hand (Slimed,
   Infection, Dazed, Catastrophe, Spoils Map) were skipped in hand
   reconstruction and counted in each row's context.
6. **Phase-0 adapter defects.** Five were found and fixed during Phase 0
   (enemies nested under `battle`; intent damage only in the label; hand field
   `target_type`; the "Cryo Aura" string; a Strength double-fold). Logs written
   before those fixes can carry corrupted *readings*. Rows whose engine side
   fails an internal consistency check are flagged
   `suspected_reading_corruption = 1` and are not conflated with sim
   divergence.
7. **The fanfare sampling seam.** The engine samples `meters_by_turn` at the
   turn opening; `combat._player_turn` decays Fanfare at the true top of the
   turn, before any turn-start generation. Both readings of that seam are
   filed — `l2.fanfare_after_turn` (sim's raw end-of-turn value) and
   `l2.fanfare_next_open_post_decay` (the same value after the sim's own
   decay). Which is the fair comparison is a question for the classification
   pass; this pass declines to pick one.

### 2.2 Reproducing

```
python -m understudy.replay \
  --logs "<repo>/.claude/worktrees/*/understudy/logs/soak/*.jsonl" \
  --mod-logs "%APPDATA%/SlayTheSpire2/gits_telemetry/*.jsonl" \
  --out docs/s7-divergences.tsv
```

The inputs are per-machine run output and are not committed (the soak `logs/`
directory is gitignored for that reason). The TSV is committed; it is the
artefact the classification pass reads.

---

## 3. Coverage

| | |
|---|---|
| fights found | **139** |
| fights replayed | **139** (100%) |
| posted plays in those fights | 2 738 |
| plays skipped, no tier0 card | 35 (1.3%) |
| divergence rows written | **1 635** |
| of which flagged `suspected_reading_corruption` | 683 (42%) |

---

## 4. The raw divergence log

Signed as `sim − engine`. "over" means the sim's number was the larger one.
The denominator is the number of comparisons attempted, not the number of
rows.

| field | diverged / compared | agree | median (sim−eng) | mean | range | sim over / under |
|---|---|---|---|---|---|---|
| `l1.damage` | 165 / 544 | 70% | −2.0 | −0.20 | −32 … +37 | 65 / 100 |
| `l2.block_at_turn_end` | 133 / 277 | 52% | +2.0 | +1.08 | −8 … +11 | 91 / 42 |
| `l2.enemy_pool_drop` | 199 / 262 | 24% | +2.0 | +1.40 | −30 … +74 | 118 / 81 |
| `l2.fanfare_after_turn` | 221 / 262 | 16% | −3.0 | −3.38 | −17 … +6 | 46 / 175 |
| `l2.fanfare_next_open_post_decay` | 248 / 262 | 5% | −5.0 | −5.67 | −18 … +3 | 7 / 241 |
| `l2.salon_members_after_turn` | **0 / 262** | **100%** | — | — | — | — |
| `l2.encore_after_turn` | 27 / 85 | 68% | +5.0 | +4.44 | +2 … +5 | 27 / 0 |

Record-integrity rows (not sim comparisons, all flagged):

| field | rows |
|---|---|
| `record.cards_played[*]` | 244 across 139 fights |
| `xfeed.meters.encore` | 221 |
| `xfeed.n_cards_played` | 53 (every paired fight) |
| `xfeed.outcome` | 53 (every paired fight) |
| `xfeed.damage_dealt` | 40 |
| `xfeed.hp_end` / `hp_lost` | 9 / 9 |
| `xfeed.damage_taken` | 4 |
| `xfeed.meters.salon_cap` | 3 |
| `xfeed.hp_start`, `max_hp`, `turns`, `floor`, `enemy_pool`, `hp_trajectory` | 1 each |

### 4.1 Observations, stated flat

No interpretation beyond what the numbers say.

- **`fight.cards_played` under-counts the actions the same log posted.** All
  139 fights mismatch. The largest single term is Ethereal Spotlight: **707
  plays** appear in the posted action stream (each answered `ok` by the
  bridge) and do not appear in the fight record. The next terms are
  Soloist's Solicitation (52), Freminet — Pers, Deploy! (10), Chevreuse —
  Interdiction Fire (8). Both feeds' `n_cards_played` disagree on every one of
  the 53 paired fights, and on those the mod feed is the higher number.
- **Salon membership agrees exactly, 262/262.** Every reading of
  `salon_members` in the corpus is 0, so the agreement is real but the
  comparison is uninformative about a populated salon.
- **The sim's Fanfare after a turn is lower than the engine's next opening in
  175 of 221 divergent turns.** On turn 1 specifically, 51 turns diverge and
  the sim reads 0 against engine readings of 1, 3, 5, 6, 7, 8 and 11 —
  i.e. the engine generated Fanfare on the opening turn where the sim's
  reconstruction of the same played cards generated none. Applying the sim's
  own decay before comparing widens the gap rather than closing it (5%
  agreement vs 16%).
- **`l2.block_at_turn_end` shows a clustered +2 offset.** The four most common
  pairs are sim 7 / engine 5 (21 turns), sim 13 / engine 11 (13), sim 6 /
  engine 4 (9), sim 10 / engine 8 (9).
- **Every `l2.encore_after_turn` row runs one way** (sim over, 27/27, by 2–5),
  and in all 27 the engine value is 0. Those fights read Encore as 0 at every
  turn opening while their mod-feed twin shows the meter moving, so the whole
  set is flagged: the current writer records `-1` for "unseen" and an earlier
  soak build appears to have written `0` for the same condition. 221
  `xfeed.meters.encore` rows say the same thing from the other side.
- **Nine L1 brackets are negative** — the target's HP read *higher* at the next
  play than at this one. All nine are Corpse Slug, Toadpole or Wriggler at
  `n_enemies = 2`, i.e. an enemy id reused across a split/hatch. Flagged, not
  compared.
- **High Tide+ is the largest unflagged single-card gap in the corpus**: sim 19
  against engine readings of 34, 39, 43 and 51 on four separate plays.

### 4.2 Ten rows verbatim from the TSV

```
soak-20260804-212539-run002#f8  l1.damage  t7  sim=19  eng=51  card=High Tide+ target=Ceremonial Beast target_hp=98->47 n_enemies=1  corrupt=0
soak-20260804-212539-run002#f8  l1.damage  t3  sim=19  eng=43  card=High Tide+ target=Ceremonial Beast target_hp=223->180 n_enemies=1  corrupt=0
soak-20260804-212539-run002#f7  l1.damage  t3  sim=19  eng=39  card=High Tide+ target=Bygone Effigy target_hp=95->56 n_enemies=1  corrupt=0
soak-20260804-225937-run002#f3  l2.enemy_pool_drop  t8  sim=6   eng=36  cards=3/3 hand_unresolved=3 n_enemies=1 pool=57->21  corrupt=0
soak-20260804-224517-run001#f1  l2.fanfare_after_turn  t1  sim=0  eng=3   cards=4/4 hand_unresolved=0 n_enemies=1  corrupt=0
soak-20260804-224517-run001#f1  l2.fanfare_after_turn  t2  sim=3  eng=9   cards=5/5 hand_unresolved=0 n_enemies=1  corrupt=0
soak-20260804-211110-run003#f3  l1.damage  t3  sim=14  eng=-23 card=Itto — Superlative Superstrength target=Corpse Slug target_hp=3->26 n_enemies=2  corrupt=1
soak-20260805-003056-run001#f5  l2.enemy_pool_drop  t7  sim=0  eng=-74 cards=3/3 hand_unresolved=2 n_enemies=1 pool=2->76  corrupt=1
soak-20260804-224517-run001#f1  record.cards_played[Ethereal Spotlight]  sim(record)=0  engine(posted)=5  corrupt=1
soak-20260804-224517-run001#f1  xfeed.outcome  soak=survived  mod=interrupted  corrupt=1
```

(The last two are shown with their columns named, because in those rows
`sim_value` is the fight record and `engine_value` is the posted stream —
the TSV column names are kept fixed for machine reading and their meaning per
prefix is documented in §5.)

---

## 5. `docs/s7-divergences.tsv`

One row per divergence, tab-separated, 1 635 rows.

| column | meaning |
|---|---|
| `fight_id` | `<run log stem>#f<n>`, `n` counting `fight` records within that log |
| `turn` | the round the divergence was measured in; empty for whole-fight rows |
| `field` | prefixed by level: `l1.*` per-card sim replay, `l2.*` per-turn sim replay, `record.*` fight record vs posted actions **in the same log**, `xfeed.*` soak feed vs mod feed |
| `sim_value` | the simulator's number for `l1.*`/`l2.*`; the **fight record's** number for `record.*`; the **soak feed's** number for `xfeed.*` |
| `engine_value` | the real game's number for `l1.*`/`l2.*`; the **posted action stream's** number for `record.*`; the **mod feed's** number for `xfeed.*` |
| `action_context` | card, target, the bracketing HP readings, enemy count, how many hand entries failed to resolve |
| `suspected_reading_corruption` | 1 where the engine side fails an internal check (negative HP bracket, Encore sentinel written as 0) or where the row is instrument-vs-instrument by construction (`record.*`, `xfeed.*`) |

---

## 6. Stop-and-surface

Two things this pass will not do, recorded rather than improvised around.

1. **Nothing here is classified.** The families are the next pass's to name.
   In particular the turn-1 Fanfare rows, the +2 block cluster and the High
   Tide+ gap each have at least two live explanations under §2.1 and this
   document does not choose between them.
2. **`fight.cards_played` disagreeing with its own log's posted actions on
   139/139 fights is a property of the telemetry writer, not of the game.**
   It is filed because anything downstream that counted cards from that key —
   Track B's B2 curves read this schema — counted a different number than the
   one the driver posted. Whether that matters, and to what, is not this
   pass's call.
