# Noisebot — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Noisebot`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** none of its own. Noisebot is a **summon-only** body: it is one of the two "defensive" bots the `Fabricator` can build in the `FabricatorNormal` encounter. It is listed in that encounter's possible-monsters set for bestiary purposes but is never part of the starting board.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Noisebot has the simplest move machine in the Act 3 bot family: **one state, wired to itself.** There is no branch, no randomness, no HP threshold, no opener exception. Every turn it is alive it shows the same *status-card* intent, labelled with the count **2**, and performs the same move.

The move, in plain language: play a cast animation, then for **each** opposing player creature, manufacture two Dazed status cards for that player —

1. one placed into that player's **discard pile**, and
2. one shuffled into that player's **draw pile at a random position**.

A pet or summon on the player side routes its cards to its owner, so companions do not multiply the tax. The local player gets a brief on-screen preview of where the two cards landed (a ~1 second beat); remote seats do not stall on someone else's preview.

Sequence, from spawn to death:

| Turn alive | Intent | Effect |
| --- | --- | --- |
| 1 | Status ×2 | 1 Dazed → discard, 1 Dazed → random slot in draw |
| 2 | Status ×2 | same |
| 3 | Status ×2 | same |
| n | Status ×2 | same, forever |

A bot that is fabricated mid-turn does not act on the turn it appeared; if it is created during the player's turn it immediately rolls and displays its intent, so you see the "status ×2" telegraph before the enemy turn begins.

## Numbers

| Value | Base | Tough-Enemies tier |
| --- | --- | --- |
| Starting HP roll | 18–23 | 19–24 |
| Attack damage | **none — it never attacks** | — |
| Block granted | **none — it never blocks** | — |
| Dazed generated per player per turn | 2 | 2 (not ascension-scaled) |
| Dazed split | 1 to discard, 1 shuffled into draw | unchanged |

HP is rolled inside the band, and the game prefers a distinct max-HP value per enemy currently on the side when the band allows — so two bots standing together will usually show different bars.

**What a Dazed actually costs.** Dazed is a Status card with no upgrade level, no playable cost, and two keywords: **Unplayable** and **Ethereal**. It cannot be played, and if it is in hand at end of turn it exhausts itself. So the damage is entirely to *draw quality and tempo*, not to the deck's permanent composition inside the fight:

- The copy shuffled into the **draw pile** is live immediately — it can be the very next card you draw, and it is dead weight in whatever hand it lands in until end of turn.
- The copy sent to the **discard pile** is inert until the draw pile is exhausted and reshuffled, at which point it joins the live pool. In a long fight the discard copies accumulate into a reshuffle that is meaningfully worse than the last one.

Two per turn means a Noisebot that lives five turns has injected **ten** dead cards, five of them already live in the draw pile. Against a lean deck that is a large fraction of the draw pool; against a bloated deck it is proportionally less punishing, which inverts the usual deck-size incentive.

## Gimmicks

- **Zero-threat body, non-zero clock.** Noisebot never deals damage and never blocks anything. Every point of pressure it exerts is indirect: it degrades your draws so the *other* enemies on the board (Fabricator's 18/21 Fabricating Strike, plus whatever aggro bots are standing) connect against a worse hand.
- **Both piles, deliberately.** The two-way split is the design: one card to punish you now, one card to punish you at reshuffle. Discard-pile manipulation and draw-pile filtering each only answer half of it.
- **Ethereal is the mercy valve.** Because Dazed exhausts from hand at end of turn, the clutter is self-cleaning *if you draw it*. Heavy-draw decks convert the tax into a small per-turn friction; low-draw decks let the copies sit in the pile and re-appear every cycle.
- **Kill-priority bait.** It is the cheapest body on the board (18–24 HP, no armor behaviour beyond a metallic damage sound) and the only one that does nothing if you leave it alive except make you worse. That is a real targeting decision every turn, and it competes directly with the Fabricator's own health bar.
- **Minion status.** Fabricated bots are tagged as minions/secondary enemies. Two consequences worth knowing: killing the Fabricator does **not** kill the bots, and a bot's own death is never fatal to the encounter. The tag also survives its owner's death.
- **It is a spawn, so its supply is throttled by the Fabricator, not by itself.** The Fabricator only builds while it has fewer than four living teammates; at the cap it switches to a straight 11/13 Disintegrate attack instead. The room's four bot slots are therefore the ceiling on simultaneous Noisebots.
- **The anti-repeat filter does not protect you.** The Fabricator refuses to build the same model it built *last*, but it tracks only a single "last built" value across both its defensive and aggressive picks, and its full Fabricate move builds a defensive bot and then an aggressive one. By the time it chooses defensively again, its last-built memory is holding an *aggressive* model, which is not a candidate on the defensive list — so the exclusion never bites there. In practice each Fabricate is a fresh **coin flip between Guardbot and Noisebot**, and back-to-back Noisebots are entirely possible.
- **Cosmetic:** it drops in from above on spawn (the encounter repositions its fall anchor), and it reads as armor when hit.

## Scaling by act / ascension

- **Act:** none. Act 3 content only; nothing in its kit reads the act index. The only act-derived factor that touches it is the multiplayer HP scaler below.
- **Ascension:** exactly one bump, and it is small.
  - *Tough Enemies* tier: HP band 18–23 → **19–24** (+1 at both ends).
  - Its output is **not** ascension-scaled at all — two Dazed per player per turn at every ascension. Noisebot is one of the few Act 3 bodies whose threat is flat across the ladder; what scales around it is its parent (Fabricating Strike 18 → 21, Disintegrate 11 → 13 at the *Deadly Enemies* tier, Fabricator HP 150 → 155 at *Tough Enemies*).

## Multiplayer / seat-count adjustments

- **HP scales hard; output does not.** Enemy max HP is multiplied by (player count × an act factor) on creature creation; for a non-boss Act 3 room that factor is **1.2**. That gives roughly:

| Seats | HP (base band) | HP (Tough-Enemies band) |
| --- | --- | --- |
| 1 | 18–23 | 19–24 |
| 2 | ~43–55 | ~46–58 |
| 3 | ~65–83 | ~68–86 |

  The scaling is applied when the bot is created, so **every fabricated Noisebot is scaled** — the Fabricator's replacements are never cheap.
- **The status tax is per seat and does not dilute.** The move iterates every opposing player creature and mints a fresh pair of Dazed for each one. Two players means four cards created per turn, three players means six — but each individual player still eats exactly two. A larger party does not share the burden, it multiplies it.
- **The block scaler is irrelevant here** (Noisebot grants no block), and the status count is untouched by seat count or ascension.
- **Net effect for co-op:** the pain point is that killing it costs 2–3× as much damage while the reason to kill it is unchanged for each individual seat. A three-player party pays roughly triple the removal cost for the same per-player relief, which makes ignoring it the tempting line and makes the accumulated draw pollution correspondingly worse.

## Fight-class reasoning — `gimmick`

Noisebot demands nothing of the player's defensive turn — no block to buy, no burst to survive, no debuff to play around — and it never touches the HP bar directly, so both `spike` and `attrition` misdescribe the ask. What it actually demands, every turn it lives, is a *deck-hygiene decision*: spend removal on a body that threatens nothing, or accept two dead cards per turn that split deliberately across the live draw pile and the next reshuffle. That is a resource/consistency puzzle rather than a damage-race one, and the correct answer depends on properties of the player's deck (draw density, deck size, pile manipulation) that no other Act 3 normal interrogates. It arrives as one component of the Fabricator board — that whole encounter grades `mixed` — but the enemy in isolation is a pure `gimmick` body, and Track B should price it as a demand on hand quality, not on block or throughput.
