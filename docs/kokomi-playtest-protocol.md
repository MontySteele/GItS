# Kokomi playtest protocol — first play, artefact `0.2-247` (commit `29f5ce6`)

> **Build pin re-stamped 2026-07-29.** This protocol was written against
> `750a9cc` and that pin went ~70 commits stale. The current deployed
> artefact is **0.2-247**, built from commit **`29f5ce6`** on a clean tree
> (pck build id `20260729-125659+29f5ce6`) — the same build the Furina
> playtest runs on, and safe to hand to a co-op partner. Anything below
> describing "the build" describes that one. Two changes since the protocol
> was written that this file does *not* otherwise account for: her character
> shell is now her own (see the art note below) and the C# bug-fix pass of
> 2026-07-29 (`docs/sprint-bugfix-log-2026-07-29.md`) changed player-visible
> behaviour in five places, none Kokomi-specific.

The Kokomi sprint's own definition of done is *"[USER] has played her — not
before."* This is the form that play should take, and it is a **protocol, not
a wishlist**: seven questions the simulation is structurally unable to answer,
each with what a useful answer looks like.

Fill in the answers section as you go. Everything else here is context to read
first.

---

## Read this before treating anything as a bug

### Art: the shell IS hers now, and it wants judging — the card faces do not

> **CORRECTED 2026-07-29.** The blanket "do not report art" below was written
> when *every* Kokomi surface was a Klee fallback. That stopped being true on
> 2026-07-25: her **character shell** — select portrait, locked portrait, char
> icon, map marker, selection splash, select backdrop, transition wipe and
> combat model — is hers, shipped, and has had **no eyes on it in-game**.
> `docs/open-playtest-items.md` §2.2 asks you to judge exactly those, and
> **§2.2 is the authoritative instruction where the two disagree.** What §2.2
> asks: does she sit left of centre over the Watatsumi reef with the right
> third clear for the info panel; are the char icon and map marker centred on
> her *head* rather than her bounding box; does the 240x280 static combat
> model read acceptably flat next to Furina (she has **no layered combat
> rig** — no idle, no lunge, no death animation, and that is expected); does
> the rising-tide transition wipe read.
>
> Still not worth reporting, and this is the part the section below gets
> right: her **58 card faces and 15 Inazuma companion faces** are provisional
> rank-1 picks nobody has chosen (Track D taste pass). "The card art is a
> guess" is already in the ledger. Report card art only if it looks *broken*
> rather than *unchosen*.

### Her card faces are provisional, on purpose (the original note)

`tools/build_pck.ps1` copies eight required assets from Klee's directories into
Kokomi's paths (`Copy-KokomiFallback`). This is not laziness — a null
`Custom*Path` override does *not* fall back safely. It resolves to an
id-derived path that does not exist, the background preloader fails, and the
run crashes later with an incomplete `AssetCache`. Shipping the fallback is
what makes her playable before the art exists.

~~**So: do not report art.** Her portrait, her combat model, her select
background and her relic icon are all Klee's~~ — **superseded 2026-07-29:
the shell is hers (see the corrected note above); the fallback machinery is
what shipped her before it existed, and is recorded here for why a null
override is not safe.** What remains true: `tools/art_coverage.py` says the
bill is **58 personal faces + 15 Inazuma companion faces**, that ledger is
already accurate, and a note saying "the card art is a guess" tells us
nothing new.

The one visual thing worth reporting is anything that looks *broken* rather
than *borrowed* — a missing gauge, a card face with a raw loc key, text that
overflows its box.

### Every number on her is PROPOSED

Not one of her balance constants has had red-pen. The whole sheet was declared,
simulated, and written up; none of it has been ratified. Where a number feels
wrong, the note is evidence, not a complaint.

Two carry specific standing flags:

- **`KuragePulsePerCharge = 3`** (was 4; R73 ruled 2, and E1 fired the
  pre-committed ×3 fallback — see `tier05/exp_neap_tide_e1.py`). It was
  originally ratified at 4 over the assistant's objection (Necrobinder
  precedent, R56). The objection was that a **basic** card's pulse out-reads
  both rate-limited Rare readers: at bank 10 it hit for 44 against Nereid's
  Ascension's 17, and at bank 25 it was 104 against 24. If the starter
  dominates the pool, that is the prediction landing, and Q4 below is where it
  goes.

  **The flag did not close when the number moved.** At the landed ×3 the
  hierarchy is upright at baseline (bank 10: 34 vs 17), but G2 ratified a
  *stacking* "Before Sun and Moon" that adds +1 (+2 upgraded) to this same
  coefficient with no cap — so one Uncommon draft puts a **basic** card back
  above the Rare readers (bank 10, ×5: 54 vs 17). What playtest three is
  looking at is therefore the **pair**, not the constant. C4 telemetry reports
  co-draft rate and stack counts with no threshold (R14); a hand's read of
  whether that pair feels like a purchase or an autopilot is the part no
  column can supply.
- **`burst_max = 20`** was chosen off a 300-run bracket to hit a pre-registered
  35–50% Burst-uptime band. Q2 is whether that band feels right in a hand.

### One number has no instrument at all

`PrincessOfWatatsumi` (her Ancient card) grants **3 Charge at the start of each
turn**, +1 upgraded. Ancients are game-side-only content — tier0 does not model
the run layer, so that number was never simulated and cannot be. It is the
single least-defended value in the build. If the Darv event offers it, take it,
and say what happened.

---

## The seven questions

### Q1 — Does the bank feel like a scaling identity, or like a counter that ticks?

Charge is uncapped, never spent, and accrues at one funnel: every card that
Exhausts pays 1. The sim can tell us her winrate; it cannot tell us whether
*watching the number go up* reads as building toward something.

**A useful answer names a turn.** "Around turn 5 of the first elite I started
routing plays to feed it" is worth more than "it felt good."

**The specific failure to watch for:** a bank that climbs steadily while
nothing in hand can spend it on. Charge has no sink by design; the question is
whether that reads as *patience* or as *waiting*.

### Q2 — How often does the Burst actually fire, and does the window land?

Meter 20. Income: 2 per Exhaust, 5 per skill-tagged card, 5 per Elemental
Reaction. She is a catalyst, so every attack applies Hydro and reactions are a
large share of the fill.

**Count the casts.** Per normal fight, per elite, per boss. The bracket that
chose 20 targeted roughly 35–50% of fights seeing one cast.

**Then judge the window, separately.** Ceremonial Garment is 3 turns during
which every attack deals +1 per 2 Charge and grants 2 Block. A Burst that fires
often but does nothing, and a Burst that is enormous but never fires, are
opposite defects with opposite fixes — say which one you had.

### Q3 — Can you tell the Garment is up?

This is the legibility question, and it is the one most likely to have a real
bug behind it, because the Garment's damage rider **did not exist in C# until
this build**.

While it holds: the status strip shows the power, and hovering any attack shows
a tip reading *"Ceremonial Garment is active: this attack deals +N damage…"*
with the live number.

**Check that the tip's number matches what the hit actually does.** If they
disagree, that is a defect and outranks every balance note in this document.

### Q4 — Does Bake-Kurage take over the deck?

The flagged risk above, stated as a play question: it is a **basic** card, so
it is in the opening deck, and its pulse reads the bank at ×3 — ×5 or more
once "Before Sun and Moon" is drafted, and that card stacks.

**Watch for:** plays chosen to set up the pulse rather than to win the turn;
the jellyfish out-damaging your rares by act 2; a hand where Bake-Kurage is
always the correct play.

Its duration is 1 turn (2 upgraded) precisely so it must be re-bought every
time. If it feels *permanent* in practice, say so — that would mean the
re-buy cost is not being felt.

### Q5 — Does Exhaust read as rotation, or as sacrifice?

Binding voice law (R55): her exhaust is **rotation** — troops rotating off the
line — and never sacrifice, burning, or spending. The display family is
Muster / Enlist / Rally.

**The question is whether the fiction survives contact with the mechanic.**
Exhausting a card in Slay the Spire has always meant losing it. If her cards
read as "I am destroying my deck to power a meter," the voice has failed even
though every individual word is correct.

### Q6 — Does the deck stay thin?

LAW 4: her Commons have a net card delta ≤ 0, machine-checked by
`tools/lint_kokomi_decksize.py`. The intent is a deck that stays sharp because
rotation removes as much as drafting adds.

**Report the deck size at the end of each act.** If it bloats anyway, the law
is being satisfied on paper and defeated by the reward screen.

### Q7 — Do you draft enough Companions to build Commander?

Her Commander archetype is built entirely out of Companions, and Companions are
in **no rollable pool** — the fourth card-reward slot is their only door, and
it hangs off Pearl of Wisdom.

**Count the offers.** If Commander is unbuildable because the door is too
narrow, that is a structural finding, not a balance one, and it would look
exactly like "commander feels bad" from inside the run.

---

## Answers

> Fill in during or immediately after the run. Verbatim reactions are more
> useful than tidied ones — the `ebb_and_flow` *"???"* from the co-op A0 note
> was the single most informative line in that document.

**Run 1** — date: ____ · ascension: ____ · result: ____ · final deck size: ____

| Q | Answer |
|---|--------|
| Q1 Charge pacing | |
| Q2 Burst frequency / window | |
| Q3 Garment legibility | |
| Q4 Kurage dominance | |
| Q5 Rotation voice | |
| Q6 Deck size | |
| Q7 Companion offers | |

**Anything that crashed, softlocked, or rendered wrong:**

**Cards that felt dead (name them — a dead card is worth more than a weak one):**

**Cards that felt broken:**

---

## Known gaps, so they are not re-reported

| Gap | Status |
|-----|--------|
| ~~All personal art is Klee's~~ | **Corrected 2026-07-29** — the character SHELL is hers and is a *review ask* (`open-playtest-items.md` §2.2). Still owed and not worth reporting: Track D's 58 card faces + 15 companion faces |
| `kokomi/model/combat.tscn` missing | Expected — no rig until the art pass; logged as EXPECTED MISSING at boot |
| Ancient card's 3 Charge/turn is unmeasured | Known — no instrument exists for Ancients |
| Every balance number is PROPOSED | Known — none has had red-pen |
| ~20 cards short of roster parity | Known — pool is 58 against Klee 76 / Furina 78; the fill is deliberately partial pending exactly this playtest |
