# Enchantments design pass (2026-07-27)

The pass [USER] ordered in sprint log §13, which sent Blade Of Ink out of
the pool until it happened. §13's five questions are answered in its own
order, each from evidence read off the DLL today (described, never
pasted — reference material stays out of the repo per §0.3).

## The evidence

**What Blade Of Ink does.** Cost 1 Skill, Rare, self-target: create two
Shivs in hand (three upgraded — the upgrade raises the existing Cards
var, i.e. the `cards` upgrade key tier0 already has) and enchant each
with Inky at one stack.

**What Inky does.** Two things, both carried BY the enchanted card
itself: its attacks deal +1 damage (powered attacks only), and playing it
applies Weak 1 to its target (all enemies if the card targets all).
`ShowAmount` is false and nothing queries the stack count beyond these
two hooks.

**Who reads enchantments.** In the base game, enchantments are a real
subsystem — a model hierarchy of ~20 enchantment types, deck screens,
rest-site options, and a dozen relics that grant them run-wide. But
**within the Silent's pool, nothing reads an enchantment**: Inky is
self-contained, no other Silent card creates, removes, counts, or
conditions on one, and the run-wide granting machinery (relics, rest
options) is outside the parity world by the standing PARITY-NOT-FIDELITY
rule (no relics, no events).

## §13's five questions

**1. Does tier0 model enchantments at all?** As a SUBSYSTEM, no — and
that refusal should be recorded once: the run-wide enchantment economy
(grant screens, enchanting relics) is out of the parity world with
relics and events, category `unavailable`-adjacent, not card by card.
But Blade Of Ink does not need the subsystem. What it needs is a
per-card-instance rider, and pass 6 already built exactly that data
pattern (`cost_delta_this_combat`, `free_this_turn`, `sly_this_turn` —
"state that lives on the CARD OBJECT").

**2. Parity feature or Teyvat Spire feature?** Parity, implemented as the
minimal rider — NOT a general mechanic offered to house design. If a
house character later wants per-card enchantment state, that design pass
starts from its own wants; nothing proposed here would need undoing.

**3. Where does the state live, and what copies it?** Two fields on the
Card instance: `enchant_damage: int` (flat damage added to the card's
attack damage) and `enchant_effects: list` (effects appended on play,
after the card's own). Both travel with the instance: deepcopy-based
clone sites (Nightmare's copies, the house copy ops) carry them for
free because they are plain dataclass fields — and that is the CORRECT
base-game answer for Nightmare copying an enchanted card. The
identity-membership law from the review (state.remove_instance) already
protects two same-id cards that differ in enchantment.

**4. What does it DO in a world with no enchantment payoffs?** Inky needs
no payoff reader — the enchanted card itself is the payoff (+1 damage,
Weak on hit). The CO-OP-ONLY trap (a buff nothing reads) does not apply:
implementing exactly Inky's two hooks produces a card that measurably
does what it says.

**5. Tokens and upgrades.** Enchant-at-creation attaches the rider in
the same `add_card` resolution that creates the Shiv, so "a card that
never existed in the deck" is not a special case. The upgrade is on
Blade Of Ink's card count, not on the enchantment — the existing `cards`
key covers it; Inky itself does not scale on upgrade.

## PROPOSED

1. `Card.enchant_damage` + `Card.enchant_effects`, wired at the two
   hooks (damage resolution; post-play effect append). No registry, no
   enchantment vocabulary — the row spells the rider out.
2. Blade Of Ink enters the pool as a supplement row: `add_card` ×2
   (upgrade key `cards` → 3) with an `enchant:` block carrying
   `damage: 1` and the Weak-1-on-target rider. Emitted denominator moves
   85→86 of 86; the pool completes.
3. The extractor records the SUBSYSTEM refusal once (run-wide
   enchantment machinery is outside the parity world), so the next
   enchanted card in a future anchor pool gets triaged against a written
   category instead of reopening this.
4. The distinctness gate re-reads after the row lands (a new row can
   move `uniq`/`neardup`; the gate is ratified now, so the reading is a
   pass/fail event, not a note).

**RULING: ___**
