Status: RECORD (a design review, not a doctrine read; 2026-09-05)

# Klee's first turn: a design review with alternatives, GPT 6 Astra

[USER] asked for it on 2026-09-05 ("Can you ask GPT for a review pass that
proposes alternatives? if it agrees that this is the best option, then I'll
approve"), on the round-17 Klee pick (the starter's second placer, PR #398)
after declining Pop! in the starter and hearing the author's relic proposal
(the relic plants a Bomb 4 at combat start). This is NOT the doctrine gate:
the seat's protocol forbids a remedy, so the call went to the model directly
with the same flags and no protocol, and it is recorded here rather than in
the card-audit ledger. The model had no repo access.

**Outcome.** GPT proposed two alternatives and recommended one of its own:
option 5, the starting relic guarantees Jumpy Dumpty and Ka-pow! in the
opening hand of every combat while they are in the deck, adding no damage
text and no card. It read the relic-Bomb option (4) as "not demonstrably too
strong" at about 6 added damage and one Spark a fight on average, and
declined it anyway because it "stacks free payload onto an already
productive relic". The author's recommendation follows below the reply.

## Prompt, verbatim

```
# Design review: Klee's first turn, alternatives wanted

You are reviewing a design question for a Slay the Spire 2 character mod, at
the owner's request. This is NOT the doctrine gate: the owner wants you to
PROPOSE alternatives, weigh them, and recommend one. Read adversarially; the
author is a different model family; the owner will take your recommendation
if you agree with the author's, and something else if you do not.

## The kit, in seven rules

Klee (62 HP, 3 energy). Her Attacks apply Pyro. A **Bomb** is a charge on an
enemy that grows by 4 at the start of each of her turns and goes off only
when a card says **Set off** (every Bomb on that enemy, one at a time, each
its own Pyro hit; an explosion is not an Attack, so no when-hit power fires
and Thorns does not answer it). Each Bomb grows separately. A Bomb whose
enemy dies jumps to a survivor at its size. A **Mine** is a Bomb that also
goes off when its enemy attacks her, before the hit. **Spark**: she starts
each combat with 1, gains 1 per Bomb going off (the starting relic, Pounding
Surprise), and Spark-priced cards spend Sparks instead of energy; no cap,
lost at the end of combat. Nothing fires by itself.

**Starter (ruled R242, the owner's "basics are supposed to be bad"):** 4
Strike, 4 Defend, Ka-pow! (basic Attack, 0 energy, Retain: Set off, 4
damage), Jumpy Dumpty (basic Skill, 1: Place a Bomb 8; when it goes off,
place a Mine 3 on ALL enemies). Two kit cards in ten. Two of the ten are
replaced at run start by a randomized Mondstadt companion pair.

**The pool:** 47 prototype rows; 13 place a Bomb (basic 1 of 2, Common 7 of
21, Uncommon 3 of 16, Rare 2 of 8). For scale, the Silent's shipped pool has
8 Shiv makers in 87 (Common 3 of 20, Uncommon 2 of 35, Rare 3 of 25) and a
starter that works without them.

## What nine rounds of blind seats said

Turn one of fight one presented no kit decision on nine rounds running
whenever Jumpy Dumpty was not in the opening hand, which is most of the
time: "the first Bomb card I saw was Ka-pow!, a detonator with nothing to
detonate"; "the kit arrived on turn 2 when Jumpy Dumpty and Ka-pow! came up
together, and either alone is filler"; "three cards referencing Bombs and no
Bomb source; Chain Fuse was strictly inert". An assembled Cook deck held
Stoke the Fuse and Sparks 'n' Splash dead in five of twelve fights until a
second placer was drafted; the moment one was, "the problem vanished". Every
natural seat that was offered a placer took it. The seats otherwise call
the kit's decisions real and good: ordering, cook-or-cash, leaving an enemy
alive for its own Mine.

## The options on the table

1. **Pop! (0 energy: Place a Bomb 5) replaces one Strike in the starter.**
   The author's first default. The owner declined it: "I still would rather
   avoid putting too many actually good cards in the starting deck."
2. **Ka-pow! becomes a flex basic**: "Place a Bomb 4, or Set off. Deal 4
   damage." No card count moves; the starter's only detonator gains a mode.
3. **Access off the starter**: the Neow bundles always carry a placer, or
   Pop! and Mine Toss get a higher act-1 offer weight.
4. **The starting relic plants a Bomb at combat start**: Pounding Surprise
   puts a Bomb 4 on a random enemy when the fight opens, so every detonator
   has a target from turn one and Jumpy Dumpty stays the starter's only
   placer. The author's current recommendation, by analogy with the
   Necrobinder's Osty being out from the start and the Defect's opening orb,
   an analogy the owner has just accepted for Furina's stage. The owner's
   worry, verbatim: "I can't tell if that's too strong (a few free damage
   per turn that pays off when you do draw a set off piece)." The arithmetic:
   a Bomb 4 grows to 8, 12, 16 on turns 2, 3, 4 and pays 1 Spark when it
   goes off; Ka-pow! is Retained and free, so the relic's Bomb is cashed
   whenever Ka-pow! turns up, for 4 + the pile.

## What the owner wants from you

1. Propose at least two alternatives the author did not list (a rule, a
   relic shape, a starter shape, an access shape; no new card is required
   but one is allowed), each in two sentences.
2. Weigh every option, listed and proposed, against: the kit's rule that
   nothing fires by itself; the owner's rule that the starter carries no
   good cards; "not strictly better" against the Silent's and Defect's
   starters; and whether the option makes cook-or-cash a decision on turn
   one or just hands out damage. Say plainly whether option 4 is too strong
   and by how much (a number per fight, not a feeling), and whether a
   smaller relic Bomb (2, or 3, or a Mine 2) changes that answer.
3. Recommend one option, in one sentence, with the number that decided it.

Under 500 words. Do not restate the kit back.
```

## Reply, verbatim

```
**I recommend fixing opening access, not adding another damage engine.** Repository reading was blocked; this review uses your supplied rulings.

Two additional alternatives:

5. **Guaranteed basic pair:** Pounding Surprise puts Jumpy Dumpty and Ka-pow! into two of the normal five opening-hand slots, provided they remain in the deck. This adds no cards or damage text, but guarantees the choice between spending one energy to cash 8 immediately and retaining Ka-pow! to cook.

6. **Spark-funded ignition:** Once per combat, playing Defend lets you spend one Spark to place a Bomb 0 on its target enemy. This preserves weak starter cards and charges a resource for setup, although immediate detonation earns that Spark back and supplies no Bomb damage.

All six preserve explicit detonation; **Mine 2 uses the existing enemy-attack exception**, surrendering control over cooking.

| Option | Weak basics / comparison with Silent and Defect | Turn-one decision |
|---|---|---|
| **1. Pop!** | Violates the owner’s explicit rejection; free placement improves both damage and Spark generation. No evidence establishes whole-starter dominance. | Requires drawing both a placer and detonator; improves odds without guaranteeing choice. |
| **2. Flex Ka-pow!** | Strictly upgrades an existing basic into a free, retained utility card. Particularly generous repeatable setup. | Without Dumpty, choosing placement spends the only detonator: cooking becomes compulsory until it returns. |
| **3. Access outside starter** | A guaranteed good companion placer relocates the starter-quality problem; weighted rewards preserve weak basics. Neither establishes dominance. | Rewards cannot fix fight one; a bundled placer still needs drawing alongside detonation. |
| **4. Opening Bomb** | Preserves bad cards but stacks free payload onto an already productive relic. Cross-character superiority remains unproved. | Cash-or-cook only when a detonator appears; otherwise automatic accumulation. |
| **5. Guaranteed pair** | Cards stay weak; certainty costs two random opening draws. Unlike Silent’s extra opening draws, hand size stays five; unlike Defect’s opening Lightning, no payload is added. | Guaranteed access to both actions, with an energy cost for setup. |
| **6. Spark ignition** | Cards stay weak; placement costs the starting resource, though later Spark income can fund it. Less free payload than 4, without proving overall parity. | Conditional on Defend plus detonation; otherwise setup only. |

The comparator relics provide [two additional opening cards or one opening Lightning](https://sts2.runthesim.ai/relics); neither analogy establishes Klee’s balance.

**Option 4 is not demonstrably too strong.** Its added payload is **4/8/12/16 damage per fight** when cashed on turns 1/2/3/4, plus one Spark—not Ka-pow!’s existing 4 damage. Assuming uniform five-card draws through ten cards and immediate cashing, it averages **6 added damage plus one Spark per fight**; overkill can reduce realized damage.

Bomb 2 and Bomb 3 reduce that average to **4 and 5**, respectively; they retain identical growth. Mine 2 changes timing and control, not merely magnitude. A numerical *excess above balance* is unknown.

**Choose option 5: it guarantees both actions in 100% of opening hands while adding zero damage text.**
```

## The author's reading

Option 5 is the Furina ruling (R260) in its access form: the Defect's orb
and Osty are already out because the character's first question needs
them; here the first question needs two cards, and the relic hands them to
the opening hand instead of adding a third. It keeps the starter bad (both
cards are basics), adds no damage, and makes turn one the same real
question every fight (cash the 8 now with Ka-pow!, or Retain Ka-pow! and
cook). The cost is a fixed opening: the two cards displace two random draws,
which is the Defect's fixed orb by another name. Recommended to [USER] as
the pick's new default; if approved it is R261 and builds under a new row.
