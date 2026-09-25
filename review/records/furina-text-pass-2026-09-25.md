# Furina Stage: text cleanup pass (2026-09-25)

[USER], after the overnight tooltip pass: "for the Furina work, I also wanted a
text cleanup pass. It's not just that some text was missing - it's that the
existing text is often very verbose and unintuitive."

## The diagnosis

Too many terms, and card faces that restate rules the tooltips already carry. A
first-time player met Fanfare, Raise, Spend, Bow, lead performer, back performer,
Rotate, act and perform, seat and stage, plus Ousia and Pneuma. Three of those
name one idea twice: "lead" and "front", "act" and "perform", and "Raise" meaning
"gains Fanfare".

## The vocabulary after this pass

- **Keywords kept, each with a tooltip:** Fanfare, Spend, Bow, Summon, front
  performer, back performer, Ousia, Pneuma, and the three performer names.
- **Retired as keywords:**
  - **Raise.** Faces say "gains N Fanfare".
  - **Rotate.** Faces just say what moves.
  - **"lead performer".** It becomes "front performer" everywhere: tooltips,
    faces, badges, the seat page, the glossary and the log.
- "act" is the one plain verb for what performers do at the end of your turn.
  "perform" is retired from player-facing text.
- "Bow" is used as a verb: "X Bows". Tag it as [gold]Bow[/gold]s or whatever
  markup keeps the tip attached.

NO RULE CHANGES. Every number and behaviour stays exactly as it is. This pass is
text only.

## Tooltips (ArmKeywordTips, plus the seat glossary in the same words)

| Key | New text |
|---|---|
| Fanfare | A performer's health. Hits land on your [gold]Block[/gold], then your [gold]front performer[/gold]'s Fanfare, then you. At 0 it leaves. |
| Spend | Pay Fanfare from your [gold]back performer[/gold]. Offered only if it can pay in full. If that empties it exactly, it [gold]Bow[/gold]s. |
| Bow | A performer's parting effect (see each performer). Spending its last Fanfare triggers it; losing it to a hit doesn't. |
| Summon (random) | A performer joins at the back with 1 [gold]Fanfare[/gold]. If the stage is full, your front performer [gold]Bow[/gold]s and moves to the back instead. |
| Summon (named) | A performer joins at the back with 1 [gold]Fanfare[/gold]. |
| front performer | Takes hits first. Regains 1 [gold]Fanfare[/gold] at the start of your turn. |
| back performer | Gains and Spends [gold]Fanfare[/gold]. Hits reach it last. With no one on stage, Fanfare it would gain summons a random performer instead. |
| Ousia | This turn, your performers' acts deal double damage. |
| Pneuma | This turn, your performers' acts give double [gold]Block[/gold], and your front performer gains 2 [gold]Fanfare[/gold]. |
| Usher / Chevalmarin / Crabaletta | unchanged ("End of your turn: … [gold]Bow[/gold]: …") |

- Numbers stay interpolated from FurinaStageLaw (LeadRegen, SummonFanfare,
  Pneuma's regain and so on). Never write them as literals.
- A lone performer is both front and back. Say so only where needed: the back
  performer tip's empty-stage clause covers the empty case, and A Rapt Audience's
  face covers its own case.
- The Rotate tip is deleted. Scene Change and Step Forward say what moves.
- The "stage reader" tips (which bar a card's number reads) are deleted wherever
  the face now names the performer. Every reader face below says "your back
  performer's" or "your front performer's" outright.

## Badges

- **The Stage:** `Up to 3 performers act at the end of your turn. Hits land on your [gold]Block[/gold], then your front performer's [gold]Fanfare[/gold], then you.`
- **Relic, Salon Solitaire:** `Start each combat with Usher in front with 3 [gold]Fanfare[/gold].` The 3 is OpeningFanfare.
- **The power badges** (Full House, Thunderous Applause, A Rapt Audience, A
  Five-Century Act, Arkhe Alignment, and the co-op People of Fontaine) print their
  card's new face below, with the amount interpolated.

## Card faces

Keep every `{Var:diff()}` token where the old face had one. Numbers shown here
are the base values, for reading.

| Card | New face |
|---|---|
| Take the Stage | Summon a random performer. |
| Curtain Rise | Deal 7 damage. [gold]Spend[/gold] 3: deal 13 instead. |
| Rising Applause | Your [gold]back performer[/gold] gains 5 [gold]Fanfare[/gold]. |
| Gentilhomme Usher | Summon Usher. If he's already on stage, he gains 3 [gold]Fanfare[/gold]. |
| Surintendante Chevalmarin | Summon Chevalmarin. If she's already on stage, she gains 3 [gold]Fanfare[/gold]. |
| Mademoiselle Crabaletta | Summon Crabaletta. If she's already on stage, she gains 3 [gold]Fanfare[/gold]. |
| Understudy | Summon a random performer. Exhaust. |
| Warm Reception | Your [gold]back performer[/gold] gains 3 [gold]Fanfare[/gold]. Draw 1 card. |
| Tidal Flourish | Deal X damage to ALL enemies. [gold]Spend[/gold] 2: deal Y instead. |
| Interposition | Gain X [gold]Block[/gold]. [gold]Spend[/gold] 2: gain Y instead. |
| Scene Change | Move your [gold]front performer[/gold] to the back. |
| Grand Entrance | Deal X damage. [gold]Spend[/gold] 5: deal Y instead. |
| Ousia Surge | Deal damage equal to your [gold]back performer[/gold]'s [gold]Fanfare[/gold]. |
| Pneuma Refrain | Gain [gold]Block[/gold] equal to your [gold]front performer[/gold]'s [gold]Fanfare[/gold]. |
| Bis! | Your [gold]front performer[/gold] acts now. |
| Final Bow | Your [gold]back performer[/gold] [gold]Bow[/gold]s and leaves. Gain [gold]Block[/gold] equal to its [gold]Fanfare[/gold]. |
| Let the People Rejoice | Deal damage to ALL enemies equal to all your performers' [gold]Fanfare[/gold]. They all [gold]Bow[/gold], then return with 1. |
| Improvised Number | Deal 6 damage. If no one is on stage, Summon a random performer. |
| Between Acts | Gain 5 [gold]Block[/gold]. If no one is on stage, draw 2 cards. |
| Ensemble Piece | Deal X damage for each performer on stage. |
| Hold Your Places | Gain 5 [gold]Block[/gold]. Your [gold]front performer[/gold] gains 2 [gold]Fanfare[/gold]. |
| Quick Cue | Deal X damage. [gold]Spend[/gold] 2: deal Y instead. |
| Step Forward | Move your [gold]back performer[/gold] to the front. Gain 3 [gold]Block[/gold]. |
| Gala Dinner | Each performer gains 3 [gold]Fanfare[/gold]. |
| Double Casting | Summon 2 random performers. |
| Tutti! | All your performers act now. |
| Bravura | [gold]Spend[/gold] all of your [gold]back performer[/gold]'s [gold]Fanfare[/gold]. Deal X damage per point. |
| Full House | If all 3 seats are filled at the end of your turn, your performers act twice. |
| Thunderous Applause | Whenever a performer [gold]Bow[/gold]s, draw 1 card and your [gold]back performer[/gold] gains 2 [gold]Fanfare[/gold]. |
| A Rapt Audience | Whenever an enemy hits your [gold]front performer[/gold], your [gold]back performer[/gold] gains half the [gold]Fanfare[/gold] lost, rounded up. Needs 2 performers. (Upgraded: "gains the [gold]Fanfare[/gold] lost". Keep the IfUpgraded branch shape.) |
| Arkhe Alignment | At the start of your turn, choose [gold]Ousia[/gold] or [gold]Pneuma[/gold]. |
| A Five-Century Act | Whenever a performer [gold]Bow[/gold]s, it returns at the back with 1 [gold]Fanfare[/gold]. |
| Guest of Honor (co-op) | Until your next turn, hits on another player land on their [gold]Block[/gold], then your [gold]front performer[/gold]'s [gold]Fanfare[/gold], then them. |
| Share the Spotlight (co-op) | Your [gold]back performer[/gold] gives all its [gold]Fanfare[/gold] to another player as [gold]Block[/gold], then [gold]Bow[/gold]s. |
| The People of Fontaine (co-op) | Whenever another player plays an Attack, your [gold]back performer[/gold] gains 1 [gold]Fanfare[/gold]. |

- **Spend-mode cards** (Curtain Rise, Tidal Flourish, Interposition, Grand
  Entrance, Quick Cue): the face drops "Choose one:" and the "|". The chooser
  opens only when Spend can be paid (#662) and explains itself. The mode rows keep
  their #662 titles ("Deal damage" / "Spend N").
- **"Needs 2 performers."** Keep A Rapt Audience's single-performer truthfulness
  clause, shortened to this.
- **"Summon" on faces is capitalised** and carries the Summon tip (random or named,
  as in #662).
- **Arkhe Alignment's face** no longer spells out the two modes; the Ousia and
  Pneuma tips carry them.

## The seat page and log

- The per-turn log's "Raise N on X: a → b" becomes "X gains N Fanfare: a → b".
- Any printed "lead" becomes "front": "front: Usher 2 · back: Crabaletta 1".
- Any "performed:" becomes "acted:".
- The glossary follows the tooltips word for word.

## Everywhere else

- Update the brief's face table (`review/active/furina-stage-brief-2026-09-08.md`
  §12) to the new faces, with a dated note quoting [USER].
- The co-op record's Furina rows follow.
- Text lint: every new face and tip must fit the ceilings (card 120, tip 135,
  power 125). If one doesn't, shorten it minimally and report.
