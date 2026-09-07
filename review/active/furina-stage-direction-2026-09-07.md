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

The board: stage Crabaletta (front), Usher, Usher. Encore 2, Fanfare 13
(bonus +1). Hand: Chevreuse (a Companion, 1), Salon Début (a Deploy, 1),
Aria of Recompense (1: gain 5 Encore), a Strike. Energy 3. The enemy
intends 12.

**A. The rotating ensemble (today's rules).** Chevreuse first: Crabaletta
performs for 7, pays 1 Encore, rotates to the back; the front is now an
Usher. Salon Début next onto the full stage: it Evokes that Usher for 9
Block, deploys a new member, which performs and pays the last Encore. Début
first instead: Crabaletta is Evoked for 14 damage, and Chevreuse then
performs the new front for its number. The decision: the order of two cards
picks which member is Evoked (14 damage or 9 Block). Real, and one turn
deep. To see it the player holds five rules: the Companion trigger,
rotation, Evoke on a full stage, the arrival's performance, and the Encore
price. Aria is a third play that decides whether the second performance is
dry.

**B. The featured performer (no rotation).** The front stays front until
it leaves. Chevreuse: Crabaletta performs for 7 and stays. Début: Crabaletta
is Evoked for 14, the new member arrives behind the Ushers. The decision:
keep the featured member performing 7 per Companion card, or cash her for
14 and promote the next. That is Klee's cook-or-cash on a member, and it is
one rule fewer. What it loses: the two back slots never perform; they wait
to be featured, so a stage of three is one act and two understudies, and
"walk the company with Companion plays" (the user's own brief line) is gone.
Deploy order still decides who is front and who leaves.

**C. The ensemble performs together.** A Companion card makes every member
perform, once, for its number; the play pays 1 Encore (per act, not per
member). A Deploy adds a member; onto a full stage it Evokes the front. The
front matters for one thing only: who is Evoked next, which is deploy
order. Chevreuse: 7 damage, 3 Block, 3 Block, one Encore. Début: Evoke
Crabaletta for 14, arrival performs. The decisions: how many members to
stack before Evoking (three performing per Companion card is the engine;
Evoking one is the burst), what to put at the front (the next Evoke), and
how to spend Encore (each Companion play is one act of the whole stage,
the Spotlight is two). This is the Orb structure exactly: all orbs fire on
the passive, the front Evokes. The panel is three colours and three
numbers, and the only word is the cone on the front.

Against the user's brief (R220 §1.1): A is the brief as written. B drops
"rotating". C keeps "Companion card plays trigger the Salon" and drops
"a single member": the ensemble is the trigger's object. C also answers the
brief's other line, "obviously legible to the player", best.

Numbers under C need re-pricing, since a Companion play now performs three
members: Crabaletta's tick would sit nearer 4 than 6, Usher's nearer 2, or
the Encore price of a play rises. That is a sim question, decided at
Prototype by play, and it is not what this pick is about.

## 4. Encore, on its own

Two jobs by the brief: deferred Block (absorbs after Block, before HP) and
the currency that directs the stage. The decision it creates today is
rationing performances: with 2 at the start and 1 per performance, the
third performance in a fight is dry unless a card refills. Round 16 read
that as a switch rather than a ration, because the refills are card-sized
(Aria 5, Chevalmarin 3) and the price is performance-sized. Would the
decision survive with one fewer rule? Yes, if the dry state goes and Encore
becomes permission (at 0 the stage does not perform): the ration is the
same and sharper, and the object has one state. The reframe chose the dry
cut to avoid dead turns; under C there are fewer performances to pay for
(one per Companion play), so dead turns are rarer and the dry cut has less
to do. Under A it stays load-bearing. Recommendation: under C, try Encore
as permission; under A, keep the dry cut.

## 5. Fanfare, on its own

The Focus: 2 per trigger, 5 per Evoke, 20% decay, +1 on every member
number per 10. The decision it creates is a pace: keep performing or the
scaling decays. That is pressure, not a choice, and the per-10 bonus is
invisible until it is folded into the number. What does create choices is
its readers (Aria's second half at 3, Universal Revelry's 8, the Rare
drains): draft decisions, and they read the meter on their own faces. So
Fanfare survives with one fewer rule shown: folded into the member numbers
as Focus is, one compact figure on the panel for the readers, thresholds on
hover. GPT's caveat is right that a card asking you to spend or cross a
threshold needs the meter visible; the compact figure is that, and the
card's own face carries the threshold.

## 6. Pick, for [USER]

**Pick 1, the stage's main verb.** An A pick: a design direction the brief
cannot settle, since the brief wrote A.

1. **(default) C, the ensemble performs together.** A Companion card
   performs every member for 1 Encore; Deploys add and, on a full stage,
   Evoke the front; no rotation. Encore tried as permission. Rewritten as a
   brief revision first (two pages), then a prototype flag beside today's
   rules, re-priced by the sim, and played by [USER] at the rule change.
   The sparse panel (three colours, three numbers, a cone) is built on it,
   not on A.
2. A, today's rules, with the sparse panel and hover captures (GPT's
   first three picks). The rule faults in §2 stay and the panel carries
   them.
3. B, the featured performer: no rotation, the front performs and is
   cashed. One rule fewer than A, two slots idle.
4. Keep polishing the current panel; no direction change.

Either way, the hover states on the current build have never been seen: a
hover step goes into the scenario runner and Companion-hover and
Deploy-hover frames are taken before any new pass, as the baseline.

## 7. What this does not touch

Klee, Kokomi, any shipped number, the Balance stage. Round 17's hypothesis
waits on this pick.
