Status: RECORD

# The basics audit: what the three shipped sheets print on a Basic

2026-09-02. R242 ruled, for all three characters, that "where a character's
basics are a renamed Strike or Defend with the same stat line, the base game's
Strike and Defend replace them", and that Furina's basics "carry register text
and are read by the audit before anything moves". This is that audit.

**It changes nothing.** The shipped sheets are Balance-stage artefacts and a
change to one is a separate PR the owner merges; the PR this record lands with
moves only the two quarantined overhaul arms. Read this, then decide.

## What "PLAIN" means here

PLAIN = the base game's own stat line and nothing else on the card: 1 energy,
Attack, 6 damage to one enemy (Strike), or 1 energy, Skill, 5 Block (Defend),
with no second effect, no keyword, no tag, no register word. A PLAIN row is a
renamed base card and is what R242 is about. Everything else is NOT PLAIN and
stays where it is unless somebody rules otherwise.

No row on any of the three sheets carries a `description:` field — that key is
the prototype surface's alone — so the printed text below is read off each
row's `effects:` list.

## Klee — `docs/klee-cards.yaml`, four Basics

| id | name | cost | type | printed text | verdict |
|---|---|---|---|---|---|
| `kaboom` | Kaboom! | 1 | Attack | Deal 7 damage. | **NOT PLAIN** — 7, not 6, and the sheet's cadence header makes every Attack apply Pyro |
| `duck_and_cover` | Duck and Cover | 1 | Skill | Gain 5 Block. | **PLAIN** — a Defend exactly |
| `jumpy_dumpty` | Jumpy Dumpty | 2 | Attack | Deal 8 damage to a random enemy twice. Place a Bomb dealing 6 damage. | **NOT PLAIN** — cost 2, random target, two hits, a second op, `skill_tag` |
| `pop` | Pop! | 0 | Skill | Place a Bomb dealing 5 damage. | **NOT PLAIN** — cost 0, no Block and no damage at all, `skill_tag` |

Upgrades: `kaboom` +3 damage (7 → 10, *not* Strike+-exact), `duck_and_cover`
+3 Block (5 → 8, Defend-exact), `jumpy_dumpty` +2 damage and +2 bomb damage
(two numbers move), `pop` +2 bomb damage.

**One candidate**: `duck_and_cover`. Note what taking it would cost her —
`KleeStartingCompanionsPatch.ReplaceFirst` matches on
`typeof(Kaboom)` and `typeof(DuckAndCover)` to seat her two starting
companions, so replacing either type removes a slot the roll needs. That is a
real consequence, not a blocker, and it is the same one the overhaul arm
already reports for itself.

## Kokomi — `docs/kokomi-cards.yaml`, five Basics

| id | name | cost | type | printed text | verdict |
|---|---|---|---|---|---|
| `waters_edge` | Water's Edge | 1 | Attack | Deal 6 damage. | **PLAIN** — a Strike exactly |
| `coral_guard` | Coral Guard | 1 | Skill | Gain 5 Block. | **PLAIN** — a Defend exactly |
| `bake_kurage` | Bake-Kurage | 1 | Skill | Summon a Bake-Kurage. Gain 1 Charge. | **NOT PLAIN** — a summon plus a meter, `skill_tag` |
| `tactical_retreat` | Tactical Retreat | 0 | Skill | Draw 1 card. Discard 1 card. | **NOT PLAIN** — cost 0, a pure filter |
| `tide_reading` | Stolen Chapter | 1 | Skill | Gain 2 Block. Draw 1 card. | **NOT PLAIN** — Block cut to 2 to pay for a draw rider (and the id does not match the printed name) |

Upgrades: `waters_edge` +3 damage (6 → 9, Strike+-exact), `coral_guard` +3
Block (5 → 8, Defend-exact), `bake_kurage` +1 Kurage turn (the Charge grant
never moves — resource-curve law), `tactical_retreat` +1 draw and +1 discard,
`tide_reading` +2 Block with the draw held at 1.

**Two candidates, and they are the clearest on any sheet**: `waters_edge` and
`coral_guard` are the base line to the number, base upgrade included, and her
own sheet says so out loud ("R53: base stays at Strike parity; Strike+ slope";
"Standard Defend. Her distinctive durability comes from the ward/Charge
economy, not inflated basics"). Her prototype arm has already made the swap —
this PR deletes `proto_kk_waters_edge` and `proto_kk_coral_guard` — so the
shipped question is only whether the SHIPPED kit follows.

## Furina — `docs/furina-cards.yaml`, five Basics

Every Furina row carries a `register:` key (`salon` / `archon` / `private`).
It is a voice band, not a game effect, but it is printed metadata the other two
sheets do not have, which is the thing R242 sent to this audit.

| id | name | register | cost | type | printed text | verdict |
|---|---|---|---|---|---|---|
| `soloists_solicitation` | Soloist's Solicitation | salon | 1 | Attack | Deal 6 damage. | **NOT PLAIN — but only just**: the body is a Strike exactly; the `register:` key is the whole difference |
| `stage_presence` | Stage Presence | salon | 1 | Skill | Gain 6 Block. | **NOT PLAIN** — 6, one above a Defend, deliberately |
| `regal_bearing` | Regal Bearing | archon | 1 | Skill | Gain 3 Block. Apply 1 Weak. | **NOT PLAIN** — Block cut to 3 to pay for a debuff rider |
| `aria_of_recompense` | Aria of Recompense | private | 1 | Skill | Gain 5 Encore. | **NOT PLAIN** — no Block, no damage; a pure meter card |
| `salon_debut` | Salon Début | salon | 1 | Skill | Deploy a random Salon member. | **NOT PLAIN** — deploys into the Salon subsystem, `skill_tag` |

Upgrades: `soloists_solicitation` +3 damage (6 → 9), `stage_presence` +3 Block
(6 → 9), `regal_bearing` +2 Block with the Weak held at 1,
`aria_of_recompense` +3 Encore **and gains Innate**, `salon_debut` **gains a
whole new op** (`gain_encore 2`). Her sheet's own header flags the whole
upgrade set as PROPOSED pending the owner's red pen.

**No candidate.** She has no plain Defend at all: `stage_presence` is a
Defend+1 and the other three skills spend the Block budget elsewhere. Her one
arguable row is `soloists_solicitation`, whose body IS a Strike — the question
there is whether the `register:` key and the name are worth keeping, which is
a taste call and not a stat-line one. Reported, not touched.

## The count, and one thing worth knowing

Fourteen Basics across three sheets. **Three are mechanically plain**:
`duck_and_cover`, `waters_edge`, `coral_guard`. Two more are off by exactly one
point on purpose (`kaboom` at 7 damage, `stage_presence` at 6 Block) and would
be a re-price, not a rename, if they moved. Four carry `skill_tag`
(`jumpy_dumpty`, `pop`, `bake_kurage`, `salon_debut`). Three touch a meter
(`bake_kurage` Charge, `aria_of_recompense` Encore, `salon_debut` the Salon
slots). Not one of the fourteen has a conditional, an Exhaust, an Ethereal, a
Retain or an Innate at base.

One discrepancy of record, since both sheets describe the same numbers in
opposite terms: `soloists_solicitation`'s upgrade note says 6 → 9 "is no longer
Strike-exact", while `waters_edge`'s says its identical 6 → 9 is "Strike
parity; Strike+ slope". 6 base and 9 upgraded IS the base game's Strike and
Strike+ (verified off the 0.111.0 decompile: `DamageVar(6m)`, `OnUpgrade`
`+3m`). The Furina note is wrong on its face; nothing depends on it, so it is
recorded here rather than edited into a Balance-stage sheet in a prototype PR.
