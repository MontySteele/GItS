Status: RULED R245 2026-09-03

# Furina card audit: the shipped sheet, read by design against the reframe

Ruled R245 (§4): picks 1 and 2 at their defaults, Singer of Many Waters on your own shape. Twelve rows change, seventy-two stand. No sheet number moves
in this packet: Furina's sheet is at Balance and a sheet edit is a stamp
event, so every change below is the fold's worksheet (R220 B, Furina last),
ruled now so the fold has its answers.

Written 2026-09-03. You asked for a designer's read of the Furina cards,
suspecting they were Opus-driven; they were, across the July sprints, and
against the Salon as it shipped then. This reads all 84 rows of
`docs/furina-cards.yaml`, base and upgrade (`docs/furina-upgrades.yaml`),
against the design that is now ruled: R220 A's reframe
(`review/ruled/furina-reframe-2026-08-29.md`) and R228's one-mode Spotlight.
The yardstick is the roster's: Strike 6 and Defend 5 for 1 energy, Cleave
8 to all for 1. The Fontaine Companion rows are a separate sheet and are not
read here.

What the reframe changes underneath these cards, in one paragraph: members
no longer perform by themselves; a Companion play makes the front member
perform and rotate; a deploy performs at once and a deploy onto a full
stage Evokes the front member for free; Furina's own Evoke cards aim, apply
Focus three times, mint 5 Fanfare and pay Encore; Fanfare is minted only by
performing, never by losing HP, spending or absorbing Encore, or playing a
Spotlighted card; Fanfare readers still read it; Spotlight is Guest Cast
alone and aiming it costs 2 Encore; the Burst meter is gone. Most of the
sheet survives that intact, because most of it gains Encore, reads Fanfare,
or pays off Companion plays, and none of those verbs moved.

## 1. Rows that change

The first six are D defaults, applied at the fold and disclosed here; the
last three are your picks (§4).

| Card | Today | At the fold | Why |
|---|---|---|---|
| Take Your Bow (U, 0) | Evoke the front member, no price; upgrade repeats it | Evoke, 3 Encore; upgrade 2 Encore | F7 (1) is ruled: every Evoke card prints an Encore price. A free Evoke at 0 energy beside Curtain Call at 1 energy and 2 Encore is the dominated pair §11.5 was written to prevent. |
| Lasting Impression (C, 1, Exhaust) | Gain 4 Encore | Gain 6 Encore, Exhaust | Aria of Recompense is a basic that gains 5 with no Exhaust. A common has to beat the basic at something; this one beats it at nothing. |
| Macaron Break (C, 1) | 2 Encore and 2 Block | the same at cost 0 | Aria gives 5 Encore for the energy and Stage Presence 6 Block. At 1 it is half of either; at 0 it is the cantrip the private register lacks. |
| Undercurrent (C, 2) | 2 damage to ALL; upgrade twice | the same at cost 1 | Cleave is 8 to all for 1. Two energy for 2 and Hydro on every enemy is the aura setup priced as an attack; Rain of Roses does the aura job at 1. |
| Stagehands (U power, 1) | "final bow" in the text | "Evoke" | Wording only; the bow is the Evoke now. Lint proves it cosmetic (R179). |
| Stage Presence (basic, 1) | Gain 6 Block | noted for F16 | Klee's and Kokomi's Defend is 5 and R244 said the basics are meant to be bad. F16's starter delta already rewrites this starter; the number rides it. |
| Full Ensemble (U, 2) | deploys all three members | fills the empty seats only (R245) | On a full stage it is three free Evokes and three performances for 2 energy. |
| The Final Verdict (R, 2) | damage equal to Fanfare, then the meter crashes and its floor drops 30 | retired (R245) | It is a drain, and slice 2 builds the two the packet ruled. A third drain makes draining the default (§4.6). |
| Singer of Many Waters (R, 1, Exhaust) | heal 6 | "Heal 1 for 6 turns", Exhaust (R245) | The base game removed healing outside Ironclad, and a Rare that heals 6 once is neither on genre nor Rare. |

## 2. Rows read and left alone

- **The five basics** stand as F16 rewrites them: the named Salon Début is
  built in slice 2, Aria is the Encore tension in one card, Regal Bearing
  and Soloist's Solicitation are plain and meant to be.
- **The deploys** (Gentilhomme Usher 4 Block, Surintendante Chevalmarin 3
  Encore, Mademoiselle Crabaletta bare, Dress Rehearsal at 2 Encore with a
  draw, Overflowing Hospitality, Endless Waltz, Grand Gala): every one now
  performs on the turn it is played, which is the tempo the old sheet
  lacked. Crabaletta's bare row is right because her performance is 6
  Hydro. Grand Gala's four deploys onto three seats are the Rare's overflow
  Evoke, and Exhaust keeps it a moment.
- **The stage's glue** (Dinner Service, House Call, Casting Call, Grand
  Salon, Fortissimo Guard, Many Waters Melody, The Water's Embrace, Double
  Time, Change the Bill): Change the Bill is the one to watch, a
  trigger-and-rotate on Furina's own card, and it is exactly the "perform
  without a Companion" glue a starter draws into. Casting Call's second
  carrier at uncommon is F2 (1), owed by the fold, not by this audit.
- **The Encore cards** (Suffering for Art, Ebb and Flow, Breathless, Slip
  Backstage, Compose Herself, Hearts Swelling, Deep Breath, In the Wings,
  The House Rises, Poised Riposte, The Regina's Mercy): all survive because
  Encore did not move. Breathless spends 4 Encore for 9 and reads worse
  beside an Evoke, which is the point: it is the Encore-to-damage line for
  an empty stage.
- **The Fanfare readers** (Applause Line, The House Holds Its Breath,
  Crescendo, Florid Cadenza, Dramatic Entrance, Universal Revelry, High
  Tide, Thunderous Ovation, Flood of Emotion, Rapturous Applause, Unheard
  Confession, The Sea Is My Stage): the brief keeps "read the meter for
  direct effects", and every reader here reads without draining. The Sea Is
  My Stage is the one that changes character: a floor of 15 under a 20%
  decay is a permanent Focus point and the end of the hold-or-spend
  decision below 15. Rare is the right tier for that and it stays.
- **The Spotlight family**, eighteen rows, all keyed to Companion plays
  under R228 (Limelight, Shared Billing, Blocking Notes, Stage Lights,
  Curtain Cue, Leading Role, Supporting Cast, The Guest List, Director's
  Cut, Take It From the Top, Top Billing, Duet, Standing Ovation, Encore
  Performance, Star of the Show, Prima Donna, Command Performance, An
  Invitation). Coherent as written: the three that key off "the light
  moved this turn" pay the aim's 2 Encore back with interest, and Duet is
  the strongest card in the family and should be.
- **The generic glue** (Stage Combat, Usher the Waves, Commanding Gaze,
  Crashing Waves, Torrential Turn, Matinée Performance, The Witness Stand,
  The Crowd Answers, Courtroom Drama, Quick Change, Showstopper, Rain of
  Roses): plain and priced at the roster's yardstick. Let the People
  Rejoice is F11 (1), built as a proto twin in slice 2.

Two notes with no action. The sheet's header still claims 78 cards against
84, the hygiene fix the reframe packet owes (§10 item 7). And the salon
register has two Rares to the archon register's twelve; slice 2's
Intermission is the third, and the fold should not add archon Rares before
it adds salon ones.

## 3. The pool as a whole

**The economy has one currency now.** Encore is deferred Block and the
price of every aimed thing, an Evoke or a Spotlight. Twenty rows gain it,
nine spend it, and the readers of it (Poised Riposte, The House Rises,
Compose Herself) give the hold side a reason. That is the tension the
brief asked for, "hold Encore as Block, or spend it to direct the Stage",
and the sheet already carries it without a new card.

**The Fanfare feeds the reframe retires touched no card face.** Losing HP,
spending Encore, absorbing with Encore and playing a Spotlighted card minted
Fanfare invisibly, by engine rule; no row printed any of it. So retiring
them costs the sheet nothing a player could read, which is the strongest
argument the reframe had and the audit confirms it.

**Redundancy.** Two pairs, both resolved above: Lasting Impression under
Aria, Macaron Break under Aria and Stage Presence. One near-pair stands:
Thunderous Ovation reads Fanfare for Block while Intermission drains it for
Block, and the two are different decisions at the same slot, which is what
a reader beside a drain is for.

**Rares need setup.** Endless Waltz, Grand Gala, Universal Revelry, High
Tide, Flood of Emotion, Rapturous Applause, The Sea Is My Stage all pay on
a stage or a meter that took turns to build. Showstopper and The Regina's
Mercy are the two that pay flat, and both are one-shots. Nothing on the
sheet is "press button, delete act one".

**What the sheet cannot answer** is the reframe's own open question, the
fourth member (F1) and its cards; none of these 84 rows deploys a member
that does not exist, and the audit does not invent one.

## 4. Picks, ruled R245 (2026-09-03)

[USER], verbatim: "On Furina, I'm fine with the defaults, but let's reauthor
Singer of Many Waters as "Heal 1 for 6 turns". Strictly speaking it breaks
the "no heals" rule, but Furina is canonically a healer and thus can have it
as a Rare + Exhaust. At that going rate, you usually don't get the full
amount unless you deliberately stall. Otherwise approved."

1. **Full Ensemble.** RULED at the default: "Deploy every member not on
   stage." The setup card; Grand Gala keeps the overflow Evoke as the Rare's
   payoff. Upgrade stays cost 1.
2. **The Final Verdict.** RULED at the default: retired at the fold. Two
   drains, as F12 (1) ruled; its art goes to the crop pool.
3. **Singer of Many Waters.** RULED on your own shape, not on any of the
   three options: "Exhaust. For 6 turns, at the start of your turn heal 1
   HP." Rare, cost 1. The base game keeps healing to Ironclad; Furina is
   canonically the healer, and the rate is the price: six turns is longer
   than most fights, so the full 6 is paid only to a player who stalls for
   it. Upgrade, derived: eight turns, not 2 a turn, because doubling the
   rate is what the stall shape exists to refuse.

The six D defaults in §1 stand as applied. All nine land at the fold with
the sheet's re-authoring (R220 B), none before.
