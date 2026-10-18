# Spiral Abyss: numbers by act, and the snowballs bounded, 2026-10-18 (v2, ruled)

The user, on Bulwark (2026-10-18): "4 is fine for now, but we probably need to make per-act effects scale by
act. That's a high amount in act 1 and trivial in act 3."

v1 of this paper scaled every "This act" entry by how much fights grow. GPT's review (2026-10-18) found four
faults in it, and the user ruled the rewrite: "Makes sense! ... let's do both." What v2 changes:

- **Bulwark** was priced against your damage per turn, but its Block goes on every enemy. Its numbers are now lower.
- **Riptide** was left alone because "it already grows". It is a feedback loop: in the 2026-10-14 round it took
  Insatiable to 14 Strength and ended a co-op pair (`review/records/spiral-abyss-round-2-2026-10-14.md`).
  It is now bounded, and so is Elemental Mark.
- **Moonlit Spring** was scaled up because 14 "covers most of a fight". That is the reason not to, since the base
  game has almost no healing. It stays at 8.
- **Duration.** In act 3, a Whole-run entry and a This-act entry both last one act. So an entry is priced by the
  act it is *taken* in, Whole-run entries too. An entry taken early keeps its number. Nothing grows by itself.

## 1. The rule

Every number below is fixed when the entry is taken. The card and the strip show the number for that act, so the text stays one
sentence with one number. Act-1 numbers don't move unless a row says so. Act 2 and act 3 are first guesses for
the seats to test.

Fights grow by about 1.8× into act 2 and 2.5× into act 3. The base five's normal fights, bot runs since
2026-09-01, `tools/telemetry_report.py --character base5`:

| Act | Enemy HP | Damage per turn | Block per turn | HP lost per fight |
|---|---|---|---|---|
| 1 | 60 | 15.8 | 2.5 | 5.9 |
| 2 | 105 | 29.0 | 6.0 | 11.1 |
| 3 | 159 | 37.1 | 9.4 | 16.5 |

An entry whose effect already grows with fight length (Thorns, per-hit effects, multipliers) scales less than
this.

## 2. Shadows

| Entry | Lasts | Act 1 / 2 / 3 | Why |
|---|---|---|---|
| Bulwark, "each enemy gains N Block" | This act | **4 / 6 / 8** | It is per enemy, so it scales slower than damage |
| Frenzy, "start with N Strength" | This act | **2 / 3 / 4** | Per enemy hit, about +20% |
| Thorny Ground, "start with N Thorns" | This act | **2 / 2 / 3** | It already grows with fight length |
| Riptide | This act | cap **3 / 4 / 5** | Bounded, see below |
| Elemental Mark | Whole run | unchanged | Bounded, see below |
| Abyss Mage Shield | Whole run | **6 hits** | Narrowed, see below |
| The Clock, "from turn 5, +N Strength" | Whole run | **2 / 2 / 3** | Taken late, it has one act to bite |
| Rally, "+N Strength when an enemy dies" | Whole run | **2 / 3 / 3** | |
| Sheer Cold, "lose N HP" | Whole run | **3 / 4 / 5** | |
| Fatui Skirmishers, "N Plated Armor" | Whole run | **3 / 4 / 6** | |
| Abyss Herald (+15% HP), Withering (1 Weak) | Whole run | unchanged | |

**Riptide, new text:** "This act, the first time each turn an enemy's attack deals you unblocked damage, it gains
1 Strength, up to N times per combat." It counts per enemy. Within a turn, one hit per enemy feeds it. This keeps
the punishment for leaving an enemy open and removes the multi-hit spiral.

**Elemental Mark, new text:** "The first time each turn an enemy attack deals you unblocked damage, add a Burn to
your discard pile." Today a multi-hit attack can add several Burns in one turn.

**Abyss Mage Shield, new text:** "Elites enter combat with a shield of this act's element, 6 hits deep, that
stops all damage. A hit removes 1. A reaction or a counter-element hit removes 3." Today it is 8 hits for a
character without elements, and one hit for a character holding the counter element (`AbyssEntries.cs`, "the counter
element breaks it"). The gap narrows from 8 against 1 to 6 against 2. Every character still has an answer, and
the elemental ones still have the better one.

**Thorny Ground** keeps its text. Thorns tax Attacks, so the Silent and Varka pay more than Kokomi's Plans or
Klee's Bombs, as base Thorns do. The round measures HP lost to Thorns per character before anything moves.

## 3. Blessings

| Entry | Lasts | Act 1 / 2 / 3 | Why |
|---|---|---|---|
| Vigor of the Abyss, "+N per Attack" | This act | **3 / 4 / 5** | Per hit |
| Moonlit Spring, "heal N" | This act | **5 / 5 / 5** | Round 3 (2026-10-18): 8 healed 70 to 80 HP in one act. The user: "Agreed on (a)" |
| Battle Rhythm, "N Strength and N Dexterity" | This act | **1 / 2 / 2** | Strength and Dexterity multiply across cards |
| Moonlit Rest, "heal N" | Whole run | **2 / 3 / 5** | Its whole-run total comes to about Spring's one act (round 3, 2026-10-18) |
| Jade Shield, "start with N Block" | Whole run | **8 / 12 / 16** | Block per fight grows 2.3× |
| Elemental Burst, "N to ALL per Power" | Whole run | **6 / 9 / 12** | |
| Abyssal Moon, "every third card, N to ALL" | Whole run | **4 / 5 / 6** | It fires more often in longer fights |
| Wavering Moon, "N to ALL per reaction" | Whole run | **3 / 4 / 5** | Reactions come several a turn |
| Fateful Fortune, "+N Max HP" | Whole run | **12 / 16 / 20** | |
| Overflow, First Strike, Resonance, Starfell Draft, The Ley Line | either | unchanged | Multipliers or no number |

## 4. What stays

- **The veto draft.** Taking a blessing removes its paired Shadow, then one of the passed Shadows applies. The round
  records both possible Shadows on each page, and not only the one that applied.
- **Stacking.** The Clock and Abyss Herald compounding across acts is as built. The strip already names a Shadow
  still in force from an earlier act. The round counts extra enemy turns per fight against plain runs.

## 5. Build

- `AbyssNumbers` gets a value per act for each row above. Text and effect read the act the entry was taken in,
  which the run record already keeps. The save format doesn't change.
- New Riptide, Elemental Mark and Mage Shield texts and rules.
- The word-for-word text tests get one row per act.
- Each changed entry in `review/ruled/abyss-pools-2-2026-10-12.md` gets a dated line pointing here.

## 6. The round

There are three Abyss lanes at A0, and they share one build with a Kokomi round:
- one base-character control, the Silent, who pays Thorns and Mage Shield the most;
- one co-op pair.

The round reads:
- peak enemy Strength;
- extra enemy turns per fight;
- healing received;
- HP lost to Thorns;
- how often a Shadow changed a play.

GPT's full matrix (encounter types, low and high ascension, seeded normal-against-Abyss runs) waits for Balance.
