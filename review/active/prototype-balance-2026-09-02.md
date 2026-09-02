Status: OPEN (the number changes below are applied as D defaults in the next build; two watch items wait on your Kokomi run; picks at the end)

# Prototype balance pass: Klee and Kokomi, 2026-09-02

You asked for a quick audit of the two playtest builds so that no card
reads as weak or overpowered for no reason. This is that pass. The
numbers come from `review/records/balance-read-prototype-2026-09-02.md`
(PR #290): every card priced in a vacuum against the base game's Strike
(6 damage for 1 energy) and Defend (5 Block for 1), plus 1,500 sim runs
of the Kokomi arm. Two limits on what that read can see, both now
register rows:

- **The sim cannot run the Klee arm.** Its eight Bomb operations are
  registered as unbuilt in `tier0/engine/effects.py`. Every Klee number
  here is arithmetic off the sheet.
- **The sim's drafter never prices a Plan line.** Sixteen of Kokomi's 28
  rows score exactly zero at offer, so the eleven cards the sim "never
  picked" are unpriced, not judged. Its pick rates are not evidence
  either way; its play rates and its shop removals are.

Under R212 these are D picks: applied at the default, disclosed here,
yours to veto. Nothing moves in the game until the next deploy, which
waits for a closed-game window.

Four rows in section 1 are NOT D picks and are marked in their own line:
Treatise, Song of Pearls, The General's Banner and The Moon, A Ship
O'er the Seas are yours, ruled from live play on 2026-09-02 and built as
you called them. Sango Isshin is a redesign rather than a number, on
your verdict that it needed no setup.

## 1. Kokomi

**Applied.**

| Card | Was | Now | Why |
|---|---|---|---|
| Kurage's Oath | Plan: 5 to every enemy | Plan: 7 to every enemy | 5 a turn late is under a Strike at one enemy; the sim's shop binned Oath 213 times against Slack Water's 7. At 7 it is a Strike plus one for the wait, and 14 from two enemies. |
| Feint | 4 now, Plan 9 | 6 now, Plan 10 | The now-line is a Strike; the Plan buys 4 more damage for a turn of patience. Before, the now-line was a bad Strike and the card read as a tax. |
| Read the Field | 4 Block now, Plan 10 | 5 Block now, Plan 10 | The now-line is a Defend; the Plan doubles it for the wait. |
| Deep Current | 4 to every enemy | 6 to every enemy | 4 to one enemy was two under a Strike; the Opus seat called it dead in a single-target fight. |
| Coral Bulwark | 6 Block; Plan 6 Block and 1 Weak | 6 Block; Plan 8 Block and 1 Weak | The Plan line was the now-line plus a Weak, too thin to wait for. 8 and a Weak is Read the Field's 10 in a different shape. |
| Change of Plans | 0 energy, Exhaust | 1 energy, Exhaust | The wait is the kit's price, worth about 1 energy on the two-line cards. A free skip was the one card that beat the rule for nothing. The upgrade still loses Exhaust, as ruled in round 2. |
| Treatise | draw 1 per Plan carried out | draw 1 once per turn, on the first Plan carried out | [USER], live: one draw per Plan is too abusable; one per turn if a Plan fired is fine. |
| Song of Pearls | 3 Block per Plan carried out | 3 Block once per turn, on the first Plan | [USER]: likewise. |
| The General's Banner | 1 Weak per Companion card played | 1 Weak once per turn, on the first Companion card | [USER]: applies a lot of Weak, too strong; once per turn applied as the default. |

Upgrades keep their current deltas over the new bases.

**Held for your run**, as round 2 promised: Battle Plan (the Opus seat
called it never wrong; the change on the table is "Plan: gain 1 Energy
and draw 2") and Vanguard's cost (0 energy for two debuffs and two
casket hits, 9.25 damage for nothing; the sim played it on all 13
draws). Your answers to round 2's four questions decide both.

**Left alone, with the reason.** The Moon Overlooks the Waters is the
Rare that switches the delay off for the fight, and a Rare power that
solves its own kit is the base game's shape; Nereid's Ascension holds
the other shape, doubling the dawn instead of skipping it. Ambush (12 at
dawn, nothing now) and Exposed Flank (2 Vulnerable on every enemy at
dawn) are the Plan-only premium, the same one Oath now gets. Undertow,
Song of Pearls, Stolen Chapter and Rally are fine; Rally and the two
Companion cards read low in the sim only because its priest plan drafts
few Companions.

## 2. Klee

**Applied.**

| Card | Was | Now | Why |
|---|---|---|---|
| Chain Fuse | each Bomb on the target grows by 3 | grows by 6 | 3 on one Bomb was half a Strike for 1 energy, and Pop! plants a 5 for free. 6 on one Bomb is a Strike that keeps growing; 12 on two. |
| Fish-Flavored Bait | 5 damage, Bomb 5 | 4 damage, Bomb 4 | It was the auto-pick: 10 damage per energy the turn it lands with the free Ka-pow!, 16 two dawns later. Now 8, 11, 14: one under Pocket Fireworks today, ahead after a night. |
| Alice's Recipe | Bombs grow by 4 instead of 3, 1 energy | Bombs grow twice each turn, 2 energy | It was Explosives Workshop's twin at Rare and strictly weaker (a second Workshop reaches 5; a second Recipe still reads 4). Doubling growth is the Rare; Workshop stays the stacking +1. |
| Careful Arrangement | merge onto one enemy, grows by 2 | grows by 5 | +2 for 1 energy was the weakest line on the sheet; the merge is the card's point and it now pays close to Chain Fuse for setting up the big cash. |
| Sorry, Jean... | 1 energy | 0 energy | Ka-pow! cashes a Bomb for damage for free; paying 1 to cash it for Block instead made the safe play the expensive one. Free, it is Ka-pow!'s defensive twin, and it still forfeits the Spark, since the Bomb is removed rather than set off. |
| Sparks 'n' Splash | 2: at the end of your turn, Set off a random enemy's Bombs | 2: at the start of your turn, after your Bombs grow, Set off a random enemy's Bombs | Rule 7 grants the Rare its own explosion, so the auto-detonation stays; but firing at the end of the turn, before growth, it meant no Bomb it touched ever saw a dawn. At the start of the turn the Bombs it pops have grown, and the Sparks arrive when she can spend them. |

**Left alone, with the reason.** Big Badda Boom (14 per energy on a
grown Bomb) and The Big One (22 on two) read "over" only because the
yardstick credits the Bomb twice, once to the plant and once to the
cash; their own margin is the fight they end, and that is the kit.
Grounded is R242's pick 2 as a card instead of a rule: a turn she does
not detonate earns 6 Block, so choosing the wait is the tension, not a
trap. Flame Dance's rider fires only on a companion's aura, so solo it
is 5 to every enemy plus Pyro; it is the co-op card and stays. Ten of
Klee's thirty rows cost no energy (three free, seven in Sparks), eleven
after this pass; that is rule 4's economy, not a defect, and the round-5
seats are the check on it.

## 3. What happens next

An Opus build carries these twelve rows into the sheet, the codegen, the
C# (Alice's growth doubling, the new Sparks 'n' Splash power, Sorry,
Jean's cost) and the Kokomi sim twin, with tests; it deploys in the next
closed-game window after your Kokomi run. The two register rows: the
drafter pricing Plan lines (with a delay discount in the pilot), and a
tier-0 Bomb twin so the Klee arm can be read at all.

## 4. Picks

None owed. Every change above is a D default you can veto by card name;
Battle Plan and Vanguard wait on your round-2 answers.
