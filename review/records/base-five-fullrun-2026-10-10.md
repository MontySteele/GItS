# Base-five baseline, whole-run seats, 2026-10-10

This reruns the 10-05 baseline (`base-five-baseline-2026-10-05.md`, per-act seats) with one Sonnet seat per lane for the whole run, as [USER] ruled on #1045.
- Same characters and seeds, A0. Build 0.2.4790+next; base characters carry no mod content.
- Embark `20261010-200940`.
- The records and the comparison are in the session scratchpad (`base-five-fullrun/`, with `compare.md`), which is gitignored.

## Result: 0 of 5, every run dead in act 2

| Character | Seed | Tonight | 10-05 (per-act) |
|---|---|---|---|
| Ironclad | 30KMHAVG9SMQ | floor 33, The Insatiable | floor 48 |
| Silent | CYHZM9S0VPW6 | floor 33, Knowledge Demon | floor 48 |
| Defect | DJCAV76ZKAUN | floor 24, Spiny Toad (act-2 normal) | floor 48 |
| Necrobinder | YEWA0B7AVE45 | floor 33, Knowledge Demon | floor 46 |
| Regent | R41TX5Q0ZQYN | floor 33, Kaiser Crab | floor 48 |

## Why the two baselines differ: variance, not the build

- **Same game both nights:** the same map and encounters, the same act bosses, and the same offers, slot for slot. No mod content reached a base run.
- **10-05 barely scraped through.** Its act-2 bosses were won with 1, 6, 6, 13 and 33 HP left.
- **Tonight's seats drafted worse from the same offers:**
  - the Silent took 6 of 19 offers and built no Shiv engine;
  - the Ironclad kept 6 Strikes and had no scaling;
  - two runs ended with 344 and 782 gold unspent.
- So the same bosses fell the other way. Act-2 boss damage a turn was down 25% to 67%.
- The seat format is not the explanation. The Ironclad control on its own seed reached floor 48 in 7 of 11 whole-run runs.

## The reference from now on

**Pooled, 10 base runs on these five seeds:**
- 0 wins.
- 5 reached act 3 and 5 died in act 2. None died in act 1.
- Mean death floor about 39.

One run per seed is a coin flip at these act-2 bosses, even for base characters. Kit verdicts on these seeds use the pooled base number and state their own n.

Against this reference:
- **Varka:** 6 of 15 wins on these seeds. Clearly above base.
- **Furina:** 3 of 8 on her own seeds. At or above base.
- **Kokomi:** 0 of 5, mean death floor 28.6. Below base. The clearest signal is two act-1 boss deaths in 5 runs, against 0 in 10 for base.
