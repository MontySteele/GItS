Status: OPEN (one A pick, §5, and the open pick's default moved; six rows, §6)

# Furina, the Stage: round three, read

Three blind Opus seats on one seed (`KMLHTPTD4XWG`), build `0.2.3181+proto`
(main `8e1b94fe`, arms klee / companion / kokomi / furina-stage), the morning
of 2026-09-09. Same three decks: lane 1 natural; lane 2 with the Preserve
deck granted; lane 1 again with the Expend deck granted. Records:
`review/qa/furina-stage-round-3-2026-09-09/opus-lane1-natural.md`,
`opus-lane2-preserve.md`, `opus-lane1-expend.md`. The build carried round
two's rows: Spend is a choice on play (`EB-746`), the event lines name their
effect (`EB-743`), the glossary is the Stage's (`EB-744`), the shipped meters
are never granted (`EB-745`), readers print the live number (`EB-747`), a
refusal names its power (`EB-748`).

## 1. The runs

| seat | actions | ended | fights |
|---|---|---|---|
| natural | 216 | budget, alive at 30 of 78 on floor 12 | 7, the elite won |
| Preserve | 237 | budget, alive at 25 of 78 on floor 14 | 7, the elite won |
| Expend | 219 | budget, alive at 53 of 78 on floor 14 | 8, the elite won |

The first round in which no seat died, and the first in which every seat
beat the act-1 elite.

## 2. The choice on play works

"The kit's real decision is spend the bar or keep it, and it stays live
because the answer moves: keep it at 3; spend 3 of 4 and the performer
survives; spend the last of it for the Bow" (natural). Block cards read as
bar maintenance, and three fights were won at zero HP cost on that reading.
Round two's finding is closed: the wager happens at play time now.

## 3. What three rounds have converged on

**The reserve is the engine and the lead is doomed.** The Expend seat lost
the elite for three turns because every body summoned at 1 died to the
next hit, and won it the turn Crabaletta stood at 9 in the back. The
Preserve seat: "a bar broken by a hit pays nothing", so raising the lead is
correct only when a reader cashes it before an attack eats it. The natural
seat: Rising Applause is dead with two performers up because it raises the
back while every Spend and reader takes the lead. Four seats across three
rounds have now said the same thing from different decks: the back seat is
where Fanfare survives and grows, and the cards that spend or read it are
pointed at the front, where it dies. Ousia Surge, which reads the lead, went
unplayed by one seat all run for exactly that reason.

**The over-sized Spend is a loophole, and now a dominant one.** Six of nine
seats have called it a loophole; this round's Preserve seat won three
fights and the elite by summoning a 1-bar body and paying 3 or 5 off it for
the full number and the bow, and called the honest line "strictly worse",
which "makes the whole Raise half of the kit optional". The Expend seat:
"paying less when you're poorer, plus a bonus for going bankrupt, plus a
resource that is doomed by default, makes 'should I spend' answer itself."
The open pick's default moves on that evidence (§5).

**The three read as three.** Distinct act, distinct bow, and only
Chevalmarin paints Hydro (Expend). Round one's "one anonymous pool" is
answered by the printed stage and the named event lines.

**The empty stage is still the kit's floor.** Five hands in one run had no
card that did anything (stage-dependent skills on an empty stage), and
Smoggy, one Skill a turn, switches a skill-built kit off. Neither is a row
yet; both are the brief's "thin deck" weakness observed and are carried to
the next design pass with the pick below.

## 4. Defects, this round

- The Spend mode chooser needs `choose` twice: the first returns ok and the
  chooser stays open; about eight occurrences a run, two refusals spent on
  it (`EB-749`).
- Outside combat the reader faces print a literal 0: "Deal 0 damage to ALL
  enemies" on the Rare at the Neow screen, "Deal 0 damage" on Ousia Surge at
  a reward; two seats turned down a Rare on it (`EB-750`).
- The Companion glossary alternates between two sentences on consecutive
  screens of one fight (the arm signal is combat-only and keyed per screen)
  (`EB-751`).
- The mode chooser's option faces print sheet literals: unupgraded (8/12 in
  hand, 5/9 in the chooser) and unfolded under Weak (7/15 in hand, 10/20 in
  the chooser); asking by the hand's wording is refused (`EB-752`).
- Two copies of one card in hand print as two rows with no numbering
  (`EB-753`).
- Let the People Rejoice printed "Deal 2" with the lead at 12 and no Weak, a
  stale forecast from an earlier play (`EB-754`).
- Wording folded into `EB-744`'s next pass rather than minted: the Raise
  keyword says "back performer" while Gentilhomme Usher's "Raise 3 on him"
  lands on him; "middle seat" appears with no gloss; every chooser prints
  "Say confirm after choose" above "Confirm is not available"; an act that
  applied an aura printed "nothing landed"; Crabaletta's Hydro (Chevalmarin's
  bow, read as hers) is not named at its source.

## 5. Asked

**The open pick's default moves.** `furina-stage-round-2 5.1`, the
over-sized Spend: its default is now option 3, the rider needs the full
price and a short lead cannot choose it, with a bow on an exact emptying.
The register row on PR #473 says so.

**One new pick (A): where Spend and the readers take their Fanfare.** Rule 5
sends Raise to the back; rules 8 and the readers take the lead. Three rounds
say that split makes the reserve the engine and the lead's bar a thing hits
delete.

1. Keep: Raise loads the back, Spend and readers take the lead, Scene
   Change bridges them.
2. Raise targets a performer of your choice (a chooser; the lead when
   alone); Spend and readers stay on the lead.
3. **Default:** Spend and the readers take the back-most performer, the
   reserve; the lead is the shield that absorbs and regenerates; when one
   performer stands it is both. Scene Change then moves a fat reserve
   forward to shield or a hurt lead back to refill, and the bow comes from
   emptying the reserve on purpose.

Gate: a build on both picks, then round four on the same three decks.

## 6. Rows

| row | what |
|---|---|
| `EB-749` | the Spend mode chooser resolves on one `choose` |
| `EB-750` | reader faces print the rule outside combat, the number inside |
| `EB-751` | the Companion glossary holds one sentence per arm on every screen |
| `EB-752` | chooser option faces print the upgraded, folded numbers |
| `EB-753` | duplicate cards in hand are numbered |
| `EB-754` | the Rare's forecast reads the bars at hand time, never a stale spend |

## 7. Round four

After both picks are ruled and built: the same three decks on a fresh seed,
the five questions with question 2 as this round asked it, and one new
question: "did the back seat feel like a battery or a bench."
