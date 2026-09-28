# Furina Stage: second text pass (2026-09-28)

[USER], after a blind seat misread Wriothesley's full-stage rule: "I'm fine
with editing the card text to clean this up. Can we do a full legibility pass
over Furina while we're at it? She is especially prone to wordy or confusing
text. ... This goes for both her card text and the relevant tooltips."

Scope: every Stage string written since the 2026-09-25 pass
(`furina-text-pass-2026-09-25.md`). That covers the Guest Cast, the supporting
pool, her relics and potions, and the tips that grew clauses since. The
census was taken at `ca525caf` and lives in the session scratchpad; the
checks below cite the code directly.

**Text only. No rule and no number changes.** Every string below was checked
against the code it describes.

## What was wrong

1. **The ordinary full-stage rule was never printed where a Guest Star is
   played.** The trio's cards say "Summon", which carries the Summon tip, and
   that tip states that on a full stage the front one Bows. The ten Guest Star
   cards say "joins the stage" instead, so that tip never appears on them.
   Wriothesley's card is the only Guest Star that prints a full-stage rule,
   and his is the exception (the back one Bows). A seat that played Lynette on
   a full stage with Wriothesley in front had learned the exception as the
   rule. The code agrees with both cards (`FurinaStageGuests.cs:105-114`).
2. **The back-performer tip says "it fades".** The fade takes every performer
   behind the front, not just the back one (`FurinaStageLedger.Fade`, the loop
   from seat 1; `FurinaStageLaw.cs:164`). "Fade" is also printed on Held
   Applause, Echoing Hall, Eternal Applause and Grand Theater Program with no
   tip attached.
3. **Bring the House Down says "Spend all of your front performer's
   Fanfare".** Spend is defined as paying from the back performer, and this
   card has no Spend tip.
4. **Pneuma's "It summons nobody."** The empty-stage summon applies to every
   gain (`FurinaStageLedger.cs:1101`), but not to Pneuma's, which is a regain
   (`ArmKeywordTips.cs:916`). Saying "regains", as the front-performer tip
   already does, makes the patch clause unnecessary.
5. **Edge clauses and garbled grammar in performer tips.** Navia's "Her Bow
   uses what she had before she was emptied" is an edge case. Wriothesley's
   "plus 2 per Fanfare hits took and 1 per damage Block stopped in front" does
   not parse. Lynette's "one with an aura if any" and Escoffier's "give each
   other performer 2" (2 of what?) are unclear.

## Tips

| Key | Now | New |
|---|---|---|
| Fanfare | ...Hits take your Block, then the front performer's, then you. Gained on an empty stage, it summons a performer. | A performer's health. Hits take your [gold]Block[/gold], then your front performer's, then you. Gaining it on an empty stage summons a performer. |
| Summon | ...On a full stage, the front one Bows and leaves its Fanfare to the newcomer. | A performer joins at the back with 1 [gold]Fanfare[/gold]. On a full stage, the front one [gold]Bow[/gold]s first and gives the newcomer its Fanfare. |
| back performer | Gains and Spends Fanfare. End of your turn: it fades, losing half its Fanfare above 5. A lone performer is both, and never fades. | Your last performer in line. [gold]Spend[/gold] pays from it. A lone performer is both front and back. |
| **fade (new tip)** | (none) | At the end of your turn, each performer behind the front loses half its [gold]Fanfare[/gold] above 5, rounded down. |
| Pneuma | ...your front performer gains 2 Fanfare. It summons nobody. | This turn, your performers' acts give double [gold]Block[/gold], and your front performer regains 2 [gold]Fanfare[/gold]. |
| Guest Star | A Guest Star card's performer. Unlike Usher, Chevalmarin and Crabaletta, one of each: a copy makes it Bow and return with more Fanfare. | You can have one of each on stage. Summoning one already there makes it [gold]Bow[/gold], then return with the new [gold]Fanfare[/gold] added. |
| Navia | ...Her Bow uses what she had before she was emptied. | End of your turn: deal [gold]Geo[/gold] damage equal to her Fanfare to a random enemy. |
| Wriothesley | ...plus 2 per Fanfare hits took and 1 per damage Block stopped in front. | End of your turn: deal 4 [gold]Cryo[/gold] damage to a random enemy, plus 2 per Fanfare he lost to hits and 1 per damage [gold]Block[/gold] saved him. |
| Lynette | ...to a random enemy, one with an aura if any. | End of your turn: deal 3 [gold]Anemo[/gold] damage to a random enemy, preferring one with an aura. |
| Escoffier | ...give each other performer 2 and deal 3 Cryo... | End of your turn: pay 3 of her Fanfare to give each other performer 2 Fanfare and deal 3 [gold]Cryo[/gold] damage to ALL enemies. |

- The fade tip is a tip for a word already on four faces, not a new keyword,
  and the numbers stay interpolated (`FadeThreshold`). It attaches to Held
  Applause, Echoing Hall and Eternal Applause, and to the back-performer tip's
  cards wherever the old tip was the only place fade was explained.
- Every performer tip's twin, the badge `description` and `smartDescription`,
  takes the same text, with `{Act}` kept where the badge has it.
- Numbers stay interpolated from `FurinaStageLaw`, as today.

## Card faces

| Card | New face |
|---|---|
| The ten Guest Stars except Wriothesley | Summon *Name* with {GuestFanfare} [gold]Fanfare[/gold]. The Summon tip is attached, ahead of the Guest Star tip. |
| Guest Star: Wriothesley | Summon Wriothesley at the front with {GuestFanfare} [gold]Fanfare[/gold]. On a full stage, the back one [gold]Bow[/gold]s instead and gives him its Fanfare. |
| Held Applause | Gain {Block} [gold]Block[/gold]. Your performers don't [gold]fade[/gold] this turn. |
| Oratrice's Verdict | This turn, your performers' random hits target this enemy. Draw {Cards} card(s). |
| Let the People Rejoice | Deal damage to ALL enemies equal to twice your performers' total [gold]Fanfare[/gold]. They all [gold]Bow[/gold], then return with 1. |
| Bring the House Down | Your [gold]front performer[/gold] loses all its [gold]Fanfare[/gold]. Deal {ExtraDamage} damage to ALL enemies per point lost. |

- "Summon X with N Fanfare" is the form Gala Premiere already uses. The Summon
  tip's "with 1" is the default, and the face's number overrides it.
- Echoing Hall and Eternal Applause keep their faces and gain the fade tip.

## Badges, relics, glossary

- **The Stage badge:** Up to {Seats} performers act at the end of your turn.
  Then each one behind the front loses half its Fanfare above 5. The
  no-fade variant is unchanged.
- **The Curtain Never Falls (Stage face):** Start each combat with
  [gold]Usher[/gold] in front with 3 [gold]Fanfare[/gold]. Your
  [gold]front performer[/gold] regains 2 Fanfare each turn, not 1.
- **The seat glossary follows the tips word for word,** with a new row for
  fade. The riders appended to the front and back rows (`STAGE_ACTS`,
  `STAGE_BOW_ON_HIT`) are dropped: each performer's own row carries its act,
  and a hit's Bow is learned in play.

Left alone: the Spend-mode cards, the trio's faces, the chooser labels, Salon
Solitaire, and the potions. Every string that was not named here is
unchanged.

## As built (2026-09-28)

- **Wriothesley's tip, badge and glossary row are unchanged.** The new
  sentence renders at 135 characters, over the 125 power ceiling the badge
  is measured against (`tools/lint_text_conventions.py`). The tip and the
  badge are held word for word, so neither moved. It needs a shorter
  sentence.
- **Wriothesley's face golds its second "Fanfare"** ("gives him its
  [gold]Fanfare[/gold]"). The words are the table's; `lint_keyword_meters`
  refuses a face that prints the bar's name as plain text.
- The Summon tip is on all ten Guest Star cards, Wriothesley's included,
  which his face's "instead" reads against.
- The fade tip attaches off the row's ops (`gen_klee_cards.bends_the_fade`):
  Held Applause, Echoing Hall and Eternal Applause.

**Wriothesley, after the build.** The spec's sentence was 130 characters against
the 125-character badge limit. It ships as "...plus 2 per Fanfare he lost to hits
and 1 per damage Block saved him." (124) on the tip, the badge and the glossary.
