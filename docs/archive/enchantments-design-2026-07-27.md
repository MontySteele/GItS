> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/enchantments-design-2026-07-27.md` — new path: `docs/archive/enchantments-design-2026-07-27.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Enchantments design pass (2026-07-27)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

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
minimal rider — and, AMENDED AT RATIFICATION ([USER] 2026-07-27): the
rider IS design space offered to house design. The original proposal
fenced it off; [USER] reversed that clause, because the house is actively
trying to EXPAND the design space of existing characters to match the
official ones, and per-card enchantment state is exactly such an
expansion. What ships today is still only Inky's two hooks; a house card
that wants an enchantment rider starts from these fields, not from a
subsystem.

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

**RULING: RATIFIED [USER] 2026-07-27, with one amendment** — "fine for
now to just have Blade of Ink make special shivs with the appropriate
characteristics, but let's make a note that we have the design space to
apply enchantments — we're actively trying to expand the design space of
existing characters to make the official ones." Items 1–4 execute as
written; question 2's house-design fence is struck (see the amended
paragraph above). Recorded as R82.

## EXECUTED (same day)

1. `Card.enchant_damage` / `Card.enchant_effects` live in
   `tier0/engine/state.py` beside the pass-6 per-instance cost fields;
   the damage half folds in with `current_attack_bonus` in `_op_damage`,
   the effects half resolves after the card's own effects in
   `resolve_card`, and `_op_add_card` attaches both from the row's
   `enchant:` block. `_op_apply_power` learned the same
   `target_all_if_power` widen the damage op has, because Inky's Weak
   reads the card's LIVE TargetType — under Fan of Knives it goes wide
   with the damage. Behavior pins: `tier0/tests/test_si_pass7.py`.
2. Blade Of Ink is `game_ref/silent_pool_pass7.yaml` (layer registered in
   loader + builder); the extractor recovered its upgrade mechanically
   (`cards: +1`, i.e. three Shivs upgraded). **The pool is COMPLETE:
   86 of 86, 87 rows with the Shiv token.**
3. The subsystem refusal is recorded in
   `tools/extract_base_game_pool.py` next to the supplement machinery,
   as the standing triage category for the next enchanted card.
4. Gate re-read (ratified thresholds): OFFICIAL:silent at 87 rows reads
   uniq 72% / maxclu 5 / neardup 0.356 per card — **PASS**, sitting on
   the official band's edge on uniq and inside it elsewhere. No new
   breaches; the curated debt list is unchanged.
