Status: OPEN (one A pick, §6)

# Furina's stage: what its main verb is, and three shapes it could take

Written 2026-09-07, evening, at [USER]'s question after the fourth Salon
panel pass: the panel is better, but it lacks the Defect Orb's elegance,
where a colour and one number say everything. Is that the stage theme, the
character's complexity, or something else? GPT's second read moved to "the
rules are probably the main constraint now" and asked for the two stage
directions compared on one hand and board, then Encore and Fanfare examined
separately. This packet does that. The rules cited are R220's
(`review/ruled/furina-reframe-2026-08-29.md` §3) and the numbers are the
mod's (`klee-mod/KleeCode/Powers/SalonPowers.cs`, `Prototype/FurinaReframe.cs`).
Prototype stage; nothing here moves a shipped number.

## 1. Why an Orb reads with one number

Three things line up on an Orb and none of them is art. The number is the
effect, with Focus already inside it. There is one passive trigger (every
orb fires at end of turn) and one verb (Evoke the front), and the slot
order is the behaviour (new on the right, front leaves first). Because the
structure never varies, nothing on the orb explains itself.

## 2. The stage against that, rule by rule

The stage has the Orb skeleton: three slots, a front, arrivals, an Evoke.
Five things break the compression, and they sort into two kinds.

**Presentation (fixable on the panel):**

- The number is not the effect yet. The panel prints "6 damage" and beside
  it "Fanfare 13 · Bonus +1" and "Encore 0 · Reduced". An Orb never shows
  Focus; it shows what Focus produced.
- Portraits say who, not what. Three blue creatures carry no function; an
  Orb's colour is its function.

**Rules (not fixable on the panel):**

- **Two triggers on one object.** A Companion card performs the front
  member; a Deploy performs the member it adds; a Deploy onto a full stage
  first Evokes the front. An Orb has one passive trigger and one verb.
  Round 16 recorded the misread this causes (`EB-601`: "a Companion card
  into a full stage Evokes").
- **Rotation on performance.** On a Companion card the front member
  performs and moves to the back. That is what moved Crabaletta from the
  front to the back between the pass-four frames; it is the rule, and it
  means "who is front" changes on every Companion play, which a Deploy then
  reads (who leaves). The panel has to keep announcing it.
- **Encore degrades instead of stopping.** A performance pays 1 Encore; at
  0 the stage still performs at three quarters. The same object has a paid
  state and a dry state, and every display carries both. Round 16 read the
  economy as "a switch": with Aria in hand every performance is full and
  nothing reaches HP; without it, performances print dry and the Spotlight
  and Second Course read CANNOT BE PLAYED.

So: the theme is not the constraint. Two presentation faults and three rule
faults, and the rule faults are the ones that make the panel a dashboard.
GPT's revised order is right.

## 3. One hand, one board, three directions

The numbers below are the mod's, corrected after GPT's read of the first
draft: a paid performance is the base plus 1 per 10 Fanfare
(`SalonPowers.Scaled`); an Evoke is the base bow plus 3 per 10 Fanfare, and
it pays 1 Encore like any performance or resolves at three quarters when the
pool is dry (`EB-587`); a performance mints 2 Fanfare and an Evoke 5; Aria
grants 5 Encore and 5 more at 3 Fanfare or above, so 10 on this board.

The board: stage Crabaletta (front), Usher, Usher. Encore 2, Fanfare 13.
Hand: Chevreuse (a Companion, 1), Salon Début (a Deploy of Crabaletta, 1),
Aria of Recompense (1), a Strike (1). Energy 3. The enemy intends 12. Encore
absorbs damage after Block, so a hit of 12 into 5 Block costs 7 Encore
before it costs HP.

**A. The rotating ensemble (today's rules).** Three lines, each of three
cards.

| line | actions | damage | Block | Encore | Fanfare | stage after |
|---|---|---|---|---|---|---|
| Chevreuse, Début, Aria | Crabaletta performs 7 (paid, 2→1), rotates; Début Evokes the front Usher for 12 Block (paid, 1→0), Crabaletta arrives and performs dry 6; Aria +10 | 13 | 12 | 10 | 22 | Usher, Crabaletta, Crabaletta |
| Aria, Chevreuse, Début | Aria +10 (12); Crabaletta 7 (11), rotates; Evoke Usher 12 Block (10); arrival Crabaletta 8 (9) | 15 | 12 | 9 | 22 | Usher, Crabaletta, Crabaletta |
| Aria, Début, Chevreuse | Aria +10; Début Evokes Crabaletta for 17 (11); arrival Crabaletta 7 (10); Chevreuse performs the front Usher for 5 Block (9), rotates | 24 | 5 | 9, then 2 after the hit | 22 | Usher, Crabaletta, Crabaletta |

The decisions on this hand: pay before performing (Aria first turns a dry 6
into a paid 8), and which member the Début Evokes, set by whether Chevreuse
goes first (12 Block or 17 damage). Two real choices, one turn deep, and to
see them the player holds five rules: the Companion trigger, rotation, Evoke
on a full stage, the arrival's performance, and the Encore price on each of
them. Line three is 24 damage for 7 Encore lost to the hit; line two is 15
and nothing lost. Neither is wrong.

**B. The featured performer (no rotation).** The front stays front until it
leaves. Aria, Chevreuse, Début: Crabaletta performs 7 and stays; the Début
Evokes her for 17 and the new Crabaletta arrives behind the Ushers and
performs 8. 32 damage, 0 Block, Encore 9. Or hold the Début: Crabaletta
performs 7 per Companion card for as long as she is front. The decision is
keep-or-cash on one member, Klee's cook-or-cash shape, one rule fewer than
A. What it loses: the two Ushers never perform until Crabaletta leaves, so a
stage of three is one act and two understudies, and the user's own line
"walk the company with Companion plays" is gone.

**C. The ensemble performs together.** Stated in full this time, since the
first draft left the arrival open:

- A Deploy adds a member and nothing performs. Onto a full stage it first
  Evokes the front member, whose departure payoff is the shipped bow (14
  damage, 9 Block, or Hydro to ALL and 3 Encore) scaled by the Fanfare term,
  paid by no Encore: it is the member leaving, not performing.
- A Companion card activates the whole cast: every member performs once for
  its number, and the play pays 1 Encore for the act. Fanfare is minted per
  activation (2) and per Evoke (5), not per member, so a larger cast raises
  output and not the rate of scaling.
- The front matters for one thing: who leaves next. That is deploy order.

| line | actions | damage | Block | Encore | Fanfare | stage after |
|---|---|---|---|---|---|---|
| Aria, Chevreuse, Strike | Aria +10; the cast performs: 7, 4, 4 (12→11); Strike 6 | 13 | 8 | 11 | 15 | Crabaletta, Usher, Usher (kept) |
| Aria, Chevreuse, Début | as above, then the Début Evokes Crabaletta for 17 and a new Crabaletta arrives silent | 24 | 8 | 11 | 20 | Usher, Usher, Crabaletta |
| Aria, Début, Chevreuse | Evoke Crabaletta 17 first (Fanfare 18); then the cast performs 4, 4, 7 | 24 | 8 | 11 | 20 | Usher, Usher, Crabaletta |

Two things show. The order of Chevreuse and Début no longer changes the
result: under C the order decision of A is gone, and what replaces it is
keep-or-replace. On this board replacing wins (24 to 13) because the Début
re-deploys the same member; the cast is unchanged. Change the Deploy to
Chevalmarin and it reads the other way: the Evoke still pays 17 now, but
the cast becomes Usher, Usher, Chevalmarin, whose activation is 4, 4, 3
against 7, 4, 4, and a long single-target fight prefers the cast kept. That
is the composition decision GPT named, and it is made at the draft and the
deploy, not on the turn. Against an intended 12, both C lines take 4 into
Encore (12 minus 8 Block); the hand cannot avoid that, which is the Encore
question below.

So "the Orb structure exactly" was too strong. C shares the Orb's shape
(all fire on the passive, the front leaves first) and differs from it in
three named places: the activation is a card play, the resource that pays
for it is also the deferred Block, and the departure payoff is free. Each
has to earn its place in the brief.

## 4. Encore, on its own

Two jobs by the brief: deferred Block (it absorbs after Block, before HP)
and the currency that directs the stage. The decision it creates today is
rationing performances: 2 to open, 1 per performance, and every Evoke pays
too. Round 16 read that as a switch rather than a ration, because the
refills are card-sized (Aria 10, Chevalmarin 3) and the price is
performance-sized.

**The coupling GPT named is real and the first draft skipped it.** Under
permission, an enemy hit past Block eats the Encore that the next
activation needs, and the Ushers' Block is inside that activation. The
cycle: take a hit, lose Encore, lose the cast's Block, take a larger hit.
The recovery turn at 0 Encore under C, with the hand Chevreuse, Début
(Chevalmarin), Strike and an intended 12: Chevreuse does its own card
effect and the cast stays silent; the Début Evokes the front for its
departure payoff free; if the front is Chevalmarin that is Hydro to ALL and
3 Encore, and the next Companion card activates the cast again. So the
designed recovery is a Chevalmarin on the stage or an Encore card in hand,
and a cast with no Chevalmarin and no Aria has no way back except taking
the hit on HP. Whether that is a ration or a death spiral is the sim's to
say (dead-turn rate at act 1 with and without the dry state) and the
user's to feel, and it is why the brief carries both: permission as the
default to test, the dry cut as the fallback that the reframe already
proved avoids dead turns at the cost of the two-state object.

Under A the dry cut stays load-bearing; under C, one activation pays for
three performances, so there is less to pay for and the dry state has less
work, but "dead turns are rarer" is a claim for the sim, not a fact.

## 5. Fanfare, on its own

The Focus: 2 per trigger, 5 per Evoke, 20% decay, +1 on every member
number per 10 and 3 per 10 on an Evoke. The decision it creates is a pace:
keep performing or the scaling decays. That is pressure, not a choice, and
the per-10 bonus is invisible until it is folded into the number. What does
create choices is its readers (Aria's second half at 3, Universal Revelry's
8, the Rare drains): draft decisions, and they read the meter on their own
faces. So Fanfare survives with one fewer rule shown: folded into the
member numbers as Focus is, one compact figure on the panel for the
readers, thresholds on hover. GPT's caveat holds: a card that asks you to
spend or cross a threshold needs the meter visible, and the compact figure
is that; the card's own face carries its threshold. Under C the trigger
rule is per activation, stated in §3, so the meter's rate does not grow
with the cast.

## 6. Pick, for [USER]

**Pick 1, the stage's main verb.** An A pick: a design direction the brief
cannot settle, since the brief wrote A.

1. **(default) C, the ensemble performs together, as a brief revision
   first**: a Deploy assembles and nothing performs on arrival; a Companion
   card activates the cast for 1 Encore; a replacement pays the departing
   member's payoff free; no rotation; Fanfare per activation. Encore keeps
   its deferred-Block job and is tried as permission, with the dry cut as
   the named fallback, the zero-Encore recovery turn written into the brief
   and the dead-turn rate measured in the sim before the flag is built.
   Then a prototype flag beside today's rules, re-priced by the sim, played
   by [USER] at the rule change. The sparse panel (three colours, three
   numbers, a cone) is built on it, not on A.
2. A, today's rules with the sparse panel and GPT's first three picks.
   The rule faults in §2 stay and the panel carries them.
3. B, the featured performer: no rotation, the front performs and is
   cashed. One rule fewer than A, two slots idle.
4. Keep polishing the current panel; no direction change.

Owed either way, and started now: a hover step in the scenario runner and
Companion-hover and Deploy-hover frames on the current build, as the
baseline any pass is judged against.

## 7. What this does not touch

Klee, Kokomi, any shipped number, the Balance stage. Round 17 has no
hypothesis yet; the pick in §6 (QUEUE §3) sets it.
