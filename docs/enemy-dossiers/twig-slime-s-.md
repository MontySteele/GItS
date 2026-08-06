# Twig Slime (S) — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TwigSlimeS`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounters:** `SlimesWeak` (weak/early-Act-1 pool), `SlimesNormal`, `SlitheringStranglerNormal`
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Where it comes from

Twig Slime (S) is the small brown/spiny half of the Act 1 slime family — the mirror of Leaf Slime (S). It never spawns alone; every encounter that can produce it produces it beside other slimes:

| Encounter | Composition | Twig Slime (S) role |
| --- | --- | --- |
| `SlimesWeak` (tagged weak; force-placed as the second normal encounter of a brand-new player's very first run) | 3 bodies: small, medium, small — the two smalls are one Twig and one Leaf in randomised order, the medium is a coin-flip Twig/Leaf | one of two smalls |
| `SlimesNormal` | 4 bodies: Twig Slime (M), Leaf Slime (M), plus both smalls (Twig + Leaf) in randomised order | one of two smalls |
| `SlitheringStranglerNormal` | Slithering Strangler plus one secondary roll of three; the "small slimes" branch adds **two** smalls drawn independently, so a double Twig Slime (S) is possible | filler body |

The family shares the `Slimes` encounter tag and slime hit sound/impact VFX; the tag changes no numbers. When several slimes of the same model share a side, spawn HP rolls are deliberately made distinct where the band allows, so two Twig Slimes in the same room will usually show different HP totals.

## Intent pattern

This is the simplest AI in the Act 1 pool. The move machine holds **exactly one move state**, and that state's follow-up is itself:

1. **Tackle** — a single-hit attack (attack intent showing one damage number).

There is no random branch, no status move, no block move, no cooldown, no repeat limit, no threshold or HP-reactive behaviour, no self-buff, no death trigger, and no summon. The intent is Tackle on turn 1 and Tackle on every turn afterwards, telegraphed a full turn ahead and never varying.

| Turn | Intent |
| --- | --- |
| 1 | Tackle |
| 2 | Tackle |
| 3+ | Tackle, forever |

Contrast with its Leaf counterpart: Leaf Slime (S) alternates Tackle and a Slimed-generating cast and therefore deals damage on only half its turns. Twig Slime (S) trades that deck pollution for **damage every single turn** at a slightly higher hit and a much thinner body. Within the pair, Twig is the pressure half and Leaf is the clog half — and every slime encounter that can roll one small can roll both, so the room usually contains one of each.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 7–11 | 8–12 (*Tough Enemies*) |
| Tackle damage | **4** | **5** (*Deadly Enemies*) |
| Block gained | **none** | none |
| Status cards generated | **none** | none |
| Debuffs / powers applied | **none** | none |

HP is rolled inside the band at spawn (and de-duplicated against same-side slimes where possible).

For scale against the rest of its family:

| Sibling, for context | HP (base → *Tough*) | Attack (base → *Deadly*) | Other |
| --- | --- | --- | --- |
| Twig Slime (S) | 7–11 → 8–12 | 4 → 5 every turn | — |
| Leaf Slime (S) | 11–15 → 12–16 | 3 → 4 every *other* turn | 1 Slimed on the off turns |
| Twig Slime (M) | 26–28 → 27–29 | 11 → 12 (Clump Shot) | 1 Slimed (Sticky Shot); opens on the status move, and the attack branch may repeat up to twice in a row |
| Leaf Slime (M) | 32–35 → 33–36 | 8 → 9 (Clump Shot) | 2 Slimed (Sticky Shot); strict alternation |

Twig Slime (S) is the **lowest-HP, highest-damage-rate small** in the family: it is the only slime that attacks on 100% of its turns, and it has the thinnest body in the encounter by a clear margin.

## Gimmicks

- **It has none, and that is the point.** No block, no status, no scaling, no phase, no reactive rule. It is a pure 4-damage-per-turn metronome attached to a ~9 HP body — the game's cleanest "one card kills this" teaching object.
- **Highest damage-per-HP in the room.** At 4 damage from 7–11 HP it is the most cost-effective thing on the board to remove, which makes kill-order the only decision it participates in. Leaving it alive while clearing the mediums is a measurable mistake; it is the correct first target in nearly every slime room.
- **Sustained, not spiky.** 4 (5 at the *Deadly Enemies* tier) never crosses a mitigation threshold on its own. The threat is the sum: a `SlimesNormal` board can present Twig (S) 4 + Twig (M) 11 + Leaf (M) 8 + Leaf (S) 3 in a single turn, which is a genuine Act 1 spike — but Twig (S) is the *smallest* term in that sum and the easiest to delete.
- **Its family's status pressure comes from elsewhere.** Twig (S) generates no Slimed at all; the Slimed clog in a slime room comes from the two mediums and the Leaf small. Killing Twig first lowers incoming damage but does nothing about deck pollution, which is the real kill-order tension in the encounter.
- **First-run legal.** `SlimesWeak` is force-placed early in a brand-new player's first run, so these numbers are tuned against an unmodified starter deck.
- **Cosmetic note:** unlike its medium counterpart it carries no alternate spine-free skin variant, i.e. no accessibility-skin branch to account for. No gameplay effect.

## Scaling by act / ascension

- **Act:** none. Twig Slime (S) is Act 1 content only and reads no act index. Act index enters solely through the multiplayer scaler below (Act 1 factor 1.1).
- **Ascension:**
  - *Tough Enemies* tier: HP band 7–11 → **8–12** (one point at each end).
  - *Deadly Enemies* tier: Tackle 4 → **5**, a 25% bump to its only number and the only ascension change that alters play — at 5 it starts trading meaningfully against early block cards.
  - Nothing else changes at any ascension: same single move, same cycle, no added mechanics.

## Multiplayer / seat-count adjustments

- **HP scales with seats.** On combat entry, enemy max HP is multiplied by (player count × act factor), Act 1's factor being **1.1**. A 2-seat Twig Slime (S) sits around **15–24 HP** and a 3-seat one around **23–36 HP**, up from a 7–11 solo roll. That is the single largest change to its play profile: the "one card kills it" property evaporates at 3 seats, and the thing that made it a free first target becomes a body that survives a turn or two while attacking every turn.
- **Tackle hits every seat.** Monster attacks target the whole opposing side rather than selecting one player, so Tackle is 4 (5 at *Deadly Enemies*) to **each** player, not 4 split among them. Party-wide incoming from this one small body is 4 × seat count, every turn, for as long as it lives.
- **Block scaling is irrelevant** — it gains no block, so the multiplayer block multiplier never touches it.
- Net: seat count leaves the per-turn demand identical per player while multiplying both the body's durability and the total damage it puts out across the party. Twig (S) is the family member whose threat compounds worst with seats, because unlike the Leaf slimes it never spends a turn on a non-damage move.

## Fight-class reasoning — `swarm`

What this enemy demands per turn is *board removal*, not defense: 4 damage is below any block-planning threshold in isolation, and there is nothing to play around — no telegraphed spike, no timer, no gimmick to solve. The pressure only exists because three or four slime bodies attack and clog on the same turn, and Twig (S) is the term you are supposed to delete first because it has the family's worst damage-to-HP ratio; the correct play is cheap targeted kills and AoE, which is the defining ask of a swarm. `spike` is wrong because a single 4-damage hit never threatens; `attrition` is wrong because the body dies to one card in single-player and the room is short; `gimmick` overstates a monster with literally one move and no rules attached; `mixed` would misreport the room, since Twig (S) contributes only to the damage half and resolves to the same instruction as the rest of the encounter — clear the small bodies fast.
