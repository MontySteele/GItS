# Base-five Sonnet baseline, full unlocks, A0

2026-10-05. One blind Sonnet 5.5 run (medium effort) per base character, through act 3 at ascension 0, with a fresh seat for each act and the previous act's record as its handoff. Build 0.2.4441, seat page 4 (#923). All 57 epochs were revealed and every ascension was open (#924). Before #924 the lanes were missing 22 character epochs (Ironclad 3-7, Defect 2-7, Necrobinder 3-7, Regent 2-7), whose cards and relics were therefore absent, so earlier base-character control runs played with reduced pools. A first attempt at this round, still on those reduced pools, was stopped and is not counted. Raw records and transcripts are gitignored.

## Result: 0 of 5

| Character | Seed | HP after act 1 / act 2 | End | Cause, in the seat's words |
|---|---|---|---|---|
| Ironclad | 30KMHAVG9SMQ | 26/80, 39/80 | lost, floor 48, Test Subject form 3 (227/300 left) | reached form 3 at 13 HP with no Block cards |
| Silent | CYHZM9S0VPW6 | 27/70, 6/70 | lost, floor 48, the Queen (38/400 left) | 99-turn Weak, Frail and Vulnerable; Torch Head grew with Strength; Bound slot spent on Backflip |
| Defect | DJCAV76ZKAUN | 26/75, 13/82 | lost, floor 48, Test Subject form 3 (149/300 left) | Panic Button discarded at end of turn; Gambler's Brew under Fiddle drew nothing |
| Necrobinder | YEWA0B7AVE45 | 17/66, 1/66 | lost, floor 46, Mecha Knight elite | four hard fights in a row with no rest or shop, then a 40 hit at 6 HP |
| Regent | R41TX5Q0ZQYN | 42/92, 6/102 | lost, floor 48, Aeonglass (306/512 left) | no steady Block; Wither cards clogged the deck; Conqueror+ into Artifact |

**The five counted runs, by telemetry `run_instance`** (115 fight rows; grade against these with `tools/telemetry_report.py --baseline-run-instance`, not a date window): Ironclad `20261005-105504#0`, Necrobinder `20261005-105505#0`, Silent `20261005-105508#0`, Defect `20261005-105510#0`, Regent `20261005-113940#0`. Other base rows from 2026-10-05 are not this round: the stopped reduced-pool attempt (`20261005-1032xx`), earlier Ironclad runs on seed PPW4N6WX70LS (`20261005-0031xx`, `-0151xx`) and a second Ironclad run on 30KMHAVG9SMQ (`20261005-125503#0`).

Every run ended in act 3, four of them at the final boss. Every act ended with the seat low: across the ten act-1 and act-2 finishes, the median HP was about 30% of max, and three were under 10%. The Ancients' heals kept the runs alive into acts 2 and 3. **A0 is not too easy for Sonnet,** so raising ascension would add no signal yet.

The pattern repeats the effort test (`sonnet-effort-test-2026-10-05.md`): the seats race damage instead of blocking, and the bill comes at the boss. Two decision faults recur:
- Block shortage planned at the draft. Three decks reached the act 3 boss with no reliable Block.
- Card-rule slips under pressure: a held Retain card, a draw under Fiddle, a power into Artifact, a curse taken for a heal.

## Page findings, and what was built

- **Every seat sliced its pages** with grep, sed, head or tail, against the brief. Necrobinder's act 1 seat did it 90 times. Pages are short (median about 1,500 characters), but each enemy intent carried about 200 characters of repeated boilerplate. **#925** cut intent lines by about 64% and keeps every number.
- **The incoming line was wrong in four ways:** it ignored Osty, Beating Remnant's cap, Frost orb Block at end of turn, and end-of-turn damage from cards and powers (Disintegration, Burn). Several times it said "you would be at 0" to a seat that would have lived. **#926** counts each of these where the wire sends the number and names the effect where it does not.
- **Open, not built:**
  - Shiv previews print the Phantom Blades bonus on every Shiv, but only the first Shiv each turn gets it.
  - The 10-card hand cap drops generated cards silently.
  - Petrified Toad's rock is skipped silently when the potion belt is full.
  - Fiddle's text does not warn that it cancels draw effects.
  - Hologram+ on an empty discard pile does nothing and says nothing.
- **The briefing and "Since last page" held up.** No seat found a wrong line. The briefing decided boss and elite plans in every run.

## Cost

| Character | Calls | Cache writes | Cache reads | Context peak per act | Fresh-input equivalent |
|---|---|---|---|---|---|
| Ironclad | 325 | 487k | 28.6M | 105k / 163k / 224k | 2.04M |
| Silent | 384 | 655k | 43.6M | 144k / 191k / 325k | 3.00M |
| Defect | 349 | 639k | 37.8M | 132k / 253k / 258k | 2.69M |
| Necrobinder | 353 | 496k | 31.9M | 136k / 144k / 221k | 2.21M |
| Regent | 323 | 610k | 33.2M | 140k / 235k / 243k | 2.42M |
| **All five** | 1,734 | 2.89M | 175M | | **12.4M** |

The fresh-input equivalent counts cache reads at 1/20 and writes at 1.25: reads come to 8.75M and writes to 3.61M, so reads are about 71% of the cost and writes about 29%.

## Next

This is the baseline the kits are measured against: 0/5 base characters at A0 with the full pools. The next base round should run on pages 5 and 6 (#925, #926), so their effect can be read against this one. A Teyvat kit that matches this (ends in act 3, mostly at the final boss) is playing at a base character's level.
