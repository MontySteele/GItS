# Phrog Parasite — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `PhrogParasite`
- **Kind:** elite
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `PhrogParasiteElite` — five slots (`phrog`, `wriggler1`–`wriggler4`), but the generator places **only the Phrog**. The four wriggler slots sit empty for the whole first phase and are filled by the death trigger described below. The encounter also declares its own scene and pre-loads the `Infection` status card's overlay art, which is a fair tell that the status dump is core to the design rather than incidental.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

### Phase 1 — the Phrog itself

A two-state machine with **zero effective randomness**. Each move's follow-up is hard-wired to the other:

1. **Infect** (status-card intent, count 3) — the **initial** state, so this is turn 1, every time.
2. **Lash** (multi-attack intent, 4 hits) — follow-up of Infect.
3. Lash's follow-up is Infect again.

The fight opens **Infect → Lash → Infect → Lash → …** forever. No block move, no debuff, no HP-threshold branch, no enrage state.

> **Dead-code note for the model:** the move machine also builds a random-branch node (both moves registered, each flagged *cannot repeat*) — but nothing ever routes to it, because both moves point at each other as follow-ups. The randomizer is registered and unreachable. Anyone porting this fight should model the **deterministic alternation**, not the branch; treating this as a 50/50 coin flip would be wrong.

Because the machine refuses to transition away from its initial state until a move has actually resolved, the opening Infect is guaranteed — there is no "skips its first turn" behaviour.

### Phase 2 — the wrigglers

Killing the Phrog does **not** end the fight (see Gimmicks). Four Wrigglers spawn into the four reserved slots, all **stunned on their first turn** (they telegraph a stun intent and do nothing). From their second turn on, each runs its own hard alternation, seeded by slot position:

- **Slots 1 and 3** open on **Nasty Bite**, then alternate Bite → Wriggle → Bite → …
- **Slots 2 and 4** open on **Wriggle**, then alternate Wriggle → Bite → Wriggle → …

So the swarm is permanently split into two out-of-phase pairs: **every turn, exactly two of them bite and two of them wriggle** (until one dies and the parity breaks). Bite and Wriggle are also both hidden from the bestiary preview on the wriggler entry, so a first-time player gets no warning about the second phase's shape.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Phrog initial HP band | 61–64 (rolled) | 66–68 (Tough Enemies tier and above) |
| Lash damage per hit | 4 | 5 (Deadly Enemies tier and above) |
| Lash hit count | 4 | 4 (no ascension scaling) |
| Lash total per turn | 16 | 20 (Deadly) |
| Infect status count | 3 `Infection` per player, into the **discard** pile | 3 (no ascension scaling) |
| Phrog block | none | none |
| Wriggler initial HP band, each | 17–21 (rolled, distinct per wriggler) | 18–22 (Tough Enemies) |
| Wriggler Nasty Bite | 6 | 7 (Deadly Enemies) |
| Wriggler Wriggle | 1 `Infection` per player + **2 Strength to itself, permanent** | same |
| Wrigglers spawned on Phrog death | 4, all stunned one turn | 4 (no ascension scaling) |

**`Infection`** is a cost-less, **unplayable Status** card with no upgrade. It does nothing in the discard pile, nothing on draw, and nothing on play — it only bites if it is **still in hand at end of turn**, where it deals **3 damage** to its holder. It is not Ethereal and does not exhaust, so it recirculates for the whole fight.

### Phase 1 damage clock (base values, per seat)

| Phrog turn | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Move | Infect | Lash ×4 | Infect | Lash ×4 | Infect | Lash ×4 |
| Direct damage | 0 | 16 | 0 | 16 | 0 | 16 |
| Statuses added (cumulative) | 3 | 3 | 6 | 6 | 9 | 9 |

Direct output averages only **8/turn**, which is soft for an Act 1 elite — the fight is deliberately paying for that with deck pollution. Against a starting deck, three Infections by turn 1 and six by turn 3 is a meaningful draw-quality tax: on a ten-card deck, by the second reshuffle roughly a **third of the deck is dead cardboard**, and any of it left in hand at end of turn is 3 damage a copy.

### Phase 2 damage clock (base values, per seat, all four alive)

| Wriggler turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Behaviour | all stunned | 2 bite / 2 wriggle | 2 bite / 2 wriggle | … | … | … | … |
| Bite damage each | — | 6 | 8 | 8 | 10 | 10 | 12 |
| Team damage that turn | 0 | 12 | 16 | 16 | 20 | 20 | 24 |
| Infections added | 0 | 2 | 2 | 2 | 2 | 2 | 2 |

Every Wriggle is **+2 permanent Strength on that wriggler**, so the pair that is wriggling this turn bites for 2 more next turn. Output steps up **+4 per turn on average** and never stops. With Deadly Enemies the base bite is 7, so the same curve starts at 14 and runs 14 / 18 / 18 / 22 / …

**Whole-fight HP pool:** ~61–64 (Phrog) + ~68–84 (four wrigglers) ≈ **130–148**, delivered in two chunks with a free stun turn between them. That is a large body for Act 1, but it is spent on a slow opening, not a burst.

## Gimmicks

- **Infested — the fight cannot be won by killing the boss.** On entering the room the Phrog applies **Infested (amount 4) to itself**. Infested is flagged as a **buff**, is single-stack, and does two things: it **prevents combat from ending while it exists**, and on the owner's death it spawns **four Wrigglers**, one per reserved slot, each starting stunned. The music controller is explicitly told to switch to an "elite second phase" track at that moment. Practical consequence: the visible HP bar is a **lie about fight length**. A player who dumps their whole burst into the Phrog wins the wrong race and meets a fresh 70–85 HP swarm with an empty hand and a deck full of Infection.
- **The stun turn is the design's mercy window.** All four wrigglers waste their first turn. That is the player's one free turn to set up, cycle Infections out of hand, or land a pre-emptive AoE — and it is the single most valuable turn in the fight. Any plan that plays around the fight should be built to *arrive* at the Phrog's death with resources for exactly that window.
- **Deck pollution as the primary phase-1 pressure.** 3 Infections per Infect turn, plus 2 more per turn once the swarm is up, all into the discard. They are unplayable, so they cannot be spent — only drawn, held, and paid for at 3 HP a copy, or answered with exhaust/discard/card-removal tech. The damage source is *the player's own draw*, which means block does not stop it.
- **Two escalating Strength engines that are not on the boss.** Nothing in phase 1 ramps; all the scaling lives in the wrigglers, and it is *self-inflicted per creature*. That makes single-target kills unusually valuable in phase 2 — killing a wriggler deletes both its bite and its accumulated Strength permanently. It also means Strength removal is worth less than it looks (it is spread across four bodies) while **focused single-target damage is worth more than it looks**.
- **Multi-hit vs. flat texture flip.** Phase 1 is a 4×4 spread (per-hit mitigation, thorns, and flat-reduction effects are excellent; a single big block is fine too). Phase 2 is two chunky 6+ hits from separate bodies. Block-efficiency tech that shines in phase 1 can be worth much less in phase 2 and vice versa — the fight deliberately changes the answer mid-way.
- **HP rolls are forced distinct.** Each enemy on the side rolls a *unique* max HP from its band where possible, so the four wrigglers will normally sit at four different HP values (17/18/19/20-ish). Expect breakpoint-based AoE ("deal 18 to all") to kill some and not others — this is intentional, not a rounding artifact.
- **No block, no heal, no artifact anywhere in the encounter.** Every debuff the player owns lands at face value on both phases.

## Scaling by act / ascension

- **Act:** none. Act 1 content only; no per-act variant, and no combat value reads the act index. (Act index feeds only the *multiplayer* scaler, below.) On a player's very first run the act deliberately pins this encounter into elite slot 2, so it is the intended **second** elite most players ever meet.
- **Ascension:**
  - *Tough Enemies tier:* Phrog HP band 61–64 → 66–68 (~+8%); wriggler band 17–21 → 18–22 (~+5%). Total fight HP goes from ~130–148 to ~138–156.
  - *Deadly Enemies tier:* Lash 4 → 5 per hit (**16 → 20 per Lash turn**, a +25% swing because the bump is multiplied by the hit count) and Nasty Bite 6 → 7 (**12 → 14 per swarm turn at base Strength**, and the whole escalation ladder shifts up with it).
  - The Infect count (3), the Wriggle status count (1), the +2 Strength per Wriggle, the spawn count (4), the stun turn, and the alternation are **identical at every ascension**. Ascension makes both phases hit harder and last longer; it does not change the fight's shape or add a mechanic.
  - *Swarming Elites tier* does not touch this fight's internals — it raises the number of elite rooms on the map, so its only effect here is that you are more likely to meet the Phrog at all.

## Multiplayer / seat-count adjustments

- **HP scales hard, and it scales twice.** Enemy max HP is multiplied by (player count × act factor); the Act 1 factor is **1.1**. That is roughly **134–141 Phrog at 2 players** and **201–211 at 3**. Critically, the **wrigglers get the same treatment when they spawn** — mid-combat creature creation runs the same scaler — so they land at ~**37–46 HP each at 2P** and ~**56–69 at 3P**, i.e. a phase-2 pool of ~150–185 / ~225–277. Total table HP at 3 players is on the order of **430–490**.
- **Every attack hits every seat, at full value.** Both Lash and Nasty Bite are built as monster attacks targeting *all opponents*, refreshed between hits. In co-op each player eats the **full 4×4 Lash** and the **full bite from each biting wriggler** — nothing is split. Team-wide phase-1 damage is 32 at 2P / 48 at 3P per Lash turn.
- **Status dump is per-seat too.** Infect adds its 3 `Infection` to **each** player's discard, and each Wriggle adds 1 to each player. Every seat runs its own polluted deck; there is no shared pile and no dilution benefit from extra players. At 3 players a single Infect turn creates nine dead cards across the table.
- **Damage numbers and the +2 Strength per Wriggle do not scale with seats** — but their *effect* does, since each point is paid by every seat. One Wriggle tick is worth 6 team damage at 3 players.
- **Block scaling is irrelevant here** — the multiplayer scaler that inflates enemy block only touches enemies that gain block, and nothing in this encounter blocks.
- Net co-op read: the HP wall grows ~2.2×/3.3× **in both phases**, per-round damage grows 2×/3× and still accelerates, and the deck pollution is duplicated per seat rather than shared. The free stun turn is the one thing that does *not* scale — it is still exactly one turn no matter how many seats — which makes co-op's phase transition proportionally tighter than solo's.

## Fight-class reasoning — `mixed`

The two phases ask genuinely different questions, and that is the point of the encounter. Phase 1 is a low-damage grind (8/turn averaged) whose real pressure is **deck pollution** — the player is being asked to keep their hand clean and their draw functional, not to survive a burst. Phase 2 flips to a **swarm with a per-body Strength ramp**: four separate HP bars, escalating +4 team damage per turn, and a demand for AoE-or-focus-fire target selection that phase 1 never tested. Because the Infested trigger makes the phase change **mandatory and unskippable**, no single demand curve describes the fight: a deck that clears phase 1 comfortably (chunky single-target, no exhaust) is often exactly the deck that loses phase 2, which is the signature of `mixed` rather than `attrition` or `swarm` alone. `gimmick` was considered — the "killing it doesn't end the fight" hook is real — but the hook only *sequences* two conventional demands rather than posing a lock the player must solve.
