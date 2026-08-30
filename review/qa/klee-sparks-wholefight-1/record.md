# Blind play session `kleespark-w1`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1517+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: 21H4Y89QDRP6
- **arms_granted**: KLEEMOD-PROTO_POP_SPARK, KLEEMOD-PROTO_KABOOM_SINK, KLEEMOD-PROTO_SPARK_STRIKE, KLEEMOD-PROTO_SPARK_SWEEP, KLEEMOD-PROTO_SPARK_DOUBLE_TAP, KLEEMOD-PROTO_SPARK_FINISHER
- **arms_granted_source**: the embark sidecar `embark-20260829-201635.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 20
- **termination**: tool_blocked

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I opened with Kaboom! on the attacking Toadpole and spent both Duck and Covers to prevent its damage. On round two, I Swirled the existing Pyro aura across both enemies, used the resulting Sparks to kill the non-attacker, then Bombed and attacked the remaining Toadpole. On round three, Powder Pop into Ka-pow! finished it.

2. I seriously considered focusing the empowering Toadpole immediately, or saving Bang Bang! to avoid Thorns. That would have reduced retaliation damage, but given up the fast 15-damage Bomb-and-attack sequence against the dangerous attacker.

3. Yes. If both enemies had attacked, I would have prioritized block or Bomb-based attack reduction. A draw without Prune would have prevented the efficient Spark generation and aura spread; more defensive cards would also have made me less willing to trade health into Thorns.

4. Prune became automatic while a Pyro aura was available because it spread the aura and generated Sparks. Powder Pop was also automatic when followed by an attack, since it generated a Spark, reduced an attack, and added detonation damage. Firework Finale was dead without 3 Sparks, and the Spark attacks were dead whenever the resource was unavailable.

5. The plan changed on round two. I began by controlling the attacking enemy, but after Prune generated 2 Sparks I saw a guaranteed kill on the empowering enemy with Fwoosh! plus Kaboom!, then accepted damage to push the remaining enemy into easy finishing range.

6. The Bake-Kurage memory repeatedly said I had played no card even after several cards had been played, which was confusing. Bang Bang! also appeared to spend only 1 Spark despite printing a cost of 2, and Powder Pop’s attack reduction changed from 3x3 to 2x3 before returning to 3x3 after the Bomb detonated, so the exact duration of that protection was initially unclear.

## The run, in the tester's own words

1. The character appears to build Sparks with skills and reactions, then spend them on free Pyro attacks. Bombs add delayed damage, reduce an enemy’s first attack, and can be detonated early with an attack. Mixing elements also seems important because reactions generate Burst and can spread or consume auras.

2. The recurring tension was whether to spend Sparks immediately for damage or preserve them for stronger cards such as Bang Bang! and Firework Finale. There was also a health-versus-tempo choice: blocking attacks was safe, while attacking through Thorns ended the fight faster at a real HP cost.

3. Powder Pop and Prune — Little Witch’s Hunt defined the run. Powder Pop enabled Spark generation, Bomb damage, and attack reduction at no energy cost; Prune converted an existing aura into spread Pyro, extra Spark, and Burst. Kaboom! and the Spark attacks then supplied dependable finishing damage.

4. Play became repetitive once Powder Pop followed by an attack was clearly the default sequence. Applying Pyro, generating Sparks, and spending them on zero-cost attacks also repeated quickly, though the run ended before that pattern could be tested across several battles.

5. I would avoid Powder Charge without drafting substantially more Bomb generation first, because spending 2 Sparks to improve or trigger too few Bombs looks narrow. I would also hesitate to draft additional expensive Spark spenders when Firework Finale already became unusable whenever the resource engine did not line up.

## Turn by turn, in the tester's own words

One line per answered turn: the command the tester gave and the sentence it gave for it, verbatim, off `turn-*/reply.json`. The same R217 G label rides on it as on the fight records — it is one model's account, not a measurement.

| turn | command | the tester's sentence |
|---|---|---|
| `turn-001` | `play "Kaboom!" on "Toadpole (2)"` | Start damaging the attacking Toadpole while applying Pyro; this also leaves enough energy to block its incoming hit. |
| `turn-002` | `play "Duck and Cover (1)"` | Gain block against the incoming 7 damage; a second copy can then cover the remaining damage. |
| `turn-003` | `play "Duck and Cover"` | Raise block to 10, fully absorbing the incoming 7 damage. |
| `turn-004` | `end turn` | No remaining card is playable, and the 10 Block fully covers the incoming attack. |
| `turn-005` | `play "Prune — Little Witch's Hunt" on "Toadpole (2)"` | Swirling the existing Pyro aura should trigger a reaction, spread Pyro to both enemies, and generate 2 Sparks for the zero-cost attacks. |
| `turn-006` | `play "Fwoosh!" on "Toadpole (2)"` | Spend 1 Spark to bring the non-attacking Toadpole within range of Kaboom!, setting up a guaranteed kill this turn. |
| `turn-007` | `play "Kaboom!" on "Toadpole (2)"` | Deal the remaining 6 damage and remove this enemy before it can buff. |
| `turn-008` | `play "Powder Pop" on "Toadpole"` | Bomb the attacking enemy to reduce its first attack, gain a Spark, and unlock Bang Bang!. |
| `turn-009` | `play "Bang Bang!" on "Toadpole"` | With only one enemy, both hits are guaranteed to land and should also detonate the Bomb, dealing 15 total damage despite the Thorns. |
| `turn-010` | `end turn` | The hand is empty, so there is no further action available this turn. |
| `turn-011` | `play "Powder Pop" on "Toadpole"` | Place a 5-damage Bomb and gain a Spark; a follow-up attack can detonate it and finish the 9-HP enemy. |
| `turn-012` | `play "Ka-pow!" on "Toadpole"` | The 7-damage hit will trigger the 5-damage Bomb, comfortably finishing the 9-HP enemy. |
| `turn-013` | `` |  |
| `turn-014` | `choose "Card"` | Inspecting a card reward may improve the deck; the specific card choices should appear next. |
| `turn-015` | `choose "Kaeya — Frostgnaw"` | Cryo gives the deck a reliable second element, enabling reactions with its frequent Pyro applications instead of adding more conditional Bomb or Spark dependence. |
| `turn-016` | `choose "Gold"` | Claim the guaranteed currency before moving on; the remaining potion can likely be collected afterward. |
| `turn-017` | `choose "Potion"` | Claim the Flex Potion since it is still available and may provide useful combat flexibility. |
| `turn-018` | `proceed` | All available rewards have been collected. |
| `turn-019` | `go "Shop (path 1)"` | This is the only available route. |
| `turn-020` | `proceed` | Every item is unnamed, so there is no rules text or distinct valid name to support an informed purchase. |
| `turn-021` | `go "Monster (path 1)"` | The two destinations provide no distinguishing information, so I am taking the first path. |
| `turn-022` | `` |  |

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 22
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
