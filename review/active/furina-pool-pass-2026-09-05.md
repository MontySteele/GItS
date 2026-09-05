Status: OPEN (no pick; the defaults in §5 are applied; four rows through the audit door)

# Furina pool pass one: a stage with people on it

Written 2026-09-05 from the readings rounds 7 to 10 carried to "the pool
pass" (`review/active/furina-reframe-round-7-2026-09-04.md` to `-10-`), read
against the reframe packet (`review/ruled/furina-reframe-2026-08-29.md`, §4.2
deploy rules, §5 starter) and the arm as it stands
(`tier0/engine/furina_reframe.py`, `POOL_SUBS` and `STARTER_SUBS`; ten
`proto_fr_` rows). Prototype stage: no slate, no stamp, no number here is
quotable. Every row went through the doctrine audit before a tester sees it
(`review/records/card-audit-2026-09-04.md` §5.5); all four are FOLLOWS and
build C# first for round 17 on.

## 1. What the rounds said

**The Salon was furniture.** Rounds 9 and 10, one Deploy in the deck (the
starter's Salon Début), most Companion plays printing "No member on stage:
performs nobody", the kit's headline mechanic spent as text explaining why
nothing happened; the two turns it was live were the best of the run. The
shipped sheet offers three single-deploy Commons in twenty-three, all
Skills of one shape, and neither seat drafted one.

**No legal way to make her act.** Round 9: one dead turn with a member idle
and no Companion card in hand. Under the arm a member performs on a
deploy, a Companion play or an Evoke; her own cards never ask her to.
The shipped sheet's own perform verb (`salon_perform`, one row) is the
third route the reframe packet §2.2 says already exists.

**Companion density.** The trigger is a Companion card, drafted from its
own reward slot; the starter's An Invitation adds one and exhausts. Between
draws of the companion slot the stage waits.

**Not this pass.** The starter stays two kit cards (R254). The scaling
member (reframe F1) and the cap carriers (F9) are slice items, not rows.
The starter's dead Regal Bearing is the basics ruling of 2026-09-02.

## 2. The four rows, as audited

Each is an arm-only Common that replaces one shipped Common at the same
rarity through the pool seam (`replaces:`, `POOL_SUBS`), so the offer odds
do not move and the shipped sheet stands (R213 B). The replaced row leaves
the offer under the arm and returns with the flag off. Member numbers:
Crabaletta performs 6 Hydro to a random enemy, Usher 3 Block, Chevalmarin
2 and Hydro (`SALON_MEMBERS`); a performance mints 2 Fanfare.

1. **Curtain Rises** — Common Attack, 1; replaces House Call (6 damage plus
   2 per member). *Deal 6 damage. Deploy Gentilhomme Usher.* Upgrade: 9.
   The second Deploy shape: a deploy on an Attack, with Usher's 3 Block as
   she arrives. Against Cold Snap (1: 6 damage, channel Frost): the same
   line with a member for an orb. Audit: FOLLOWS on C6.
2. **Second Course** — Common Skill, 1; replaces Dinner Service (2 Block
   plus 2 per member). *Spend 3 Encore. Deploy Mademoiselle Crabaletta. She
   performs once more.* Upgrade: spend 2. Unplayable below 3 Encore. Two
   performances (12 random Hydro, 4 Fanfare) for an energy and three
   Encore, which is three Block she would otherwise hold: the hold-or-spend
   tension on a deploy. Against the shipped Mademoiselle Crabaletta (1:
   deploy her): the second performance is bought with Encore. Audit:
   FOLLOWS on C2, C5, C8.
3. **Rolling Tide** — Common Attack, 2; replaces Undercurrent (2 to ALL
   three times). *Deal 2 damage to ALL enemies twice. The front Salon
   member performs.* Upgrade: 3. The kit's own perform verb, one hit of
   the shipped card traded for it; with an empty stage it is a worse
   Undercurrent, which is the losing line. Audit: FOLLOWS on C3, C5, C8.
4. **Guest List** — Common Skill, 1; replaces Blocking Notes (5 Block plus
   2 per Companion played this turn). *Gain 3 Block. Add a random common
   Companion card to your hand.* Upgrade: 5 Block. An Invitation's verb in
   the pool at a price: an energy and no Exhaust, three Block short of a
   Stage Presence. Audit: FOLLOWS on C1, C6.

Arm after the pass: fourteen `proto_fr_` rows; Deploy shapes 2 (Skill,
Attack); kit-owned perform 1; Companion generators in the pool 1.

## 3. What the pass does not do

No starter change. No Evoke row: Curtain Call and Exit Stage Left stand
and the Encore opening (R258) is what they were waiting for. No Fanfare
reader: the four rider copies are unread at their bars and stay. No member
roster change. Nothing here is a number pick.

## 4. The audit and the build

One read (record §5.5): four FOLLOWS, each with clauses, no line, on GPT 6
Astra at low effort; the census was the shipped sheet's twenty-three
Commons rendered from their effects by a script (the shipped rows carry no
prose) and the arm's ten rows from the surface. FOLLOWS rows build C#
first, then the tier0 twin, then the surface with `replaces:` and the four
`POOL_SUBS` entries; engine work: a deploy op on an Attack (the shipped
`salon_member` power on an Attack row), a priced second performance, the
shipped `salon_perform` op under the arm's trigger accounting, and
`generate_guest_star` on a non-exhaust row.

## 5. Defaults applied (D and E), disclosed

- **E:** four rows, one per reading; the next pass writes against what
  these do.
- **D:** the four replaced Commons are House Call, Dinner Service,
  Undercurrent and Blocking Notes, chosen because each is a plain number
  card of the same type and cost as its replacement; the choice moves on
  the seats' word.
- **D:** Second Course's Encore price is 3, Aria's own printed 5 less the 2
  she opens with (R258); it moves on the seats' word.
- **E:** one register row for the build (`EB-493`).
