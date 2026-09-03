Status: OPEN (paper; four picks)

# Klee's Hexerei readers: the three cards in her own pool that read the tag

Written 2026-09-02, the night the coven Personals and both sets of stand-ins
were built (PRs #314, #315 and the Hexerei stand-ins that follow). Paper only:
no sheet row, no code, no register id. This is the "slice two" the Klee brief
left open in §7.4 (`review/active/klee-brief-2026-09-01.md`): Hexerei is a
one-word tag on companion cards with no effect of its own, and the payoff
lives on Klee's side, in three or four cards inside her own pool. Those cards
did not exist. Here they are, priced at a first honest guess and ruled on
taste, which is what Paper is for.

## 1. What is already true

- **The tag is on the cards.** Thirteen Mondstadt rows carry Hexerei today
  (Albedo, Fischl x2, Sucrose x3, Nicole, Mona, Venti, Durin, Razor x2,
  Varka), Prune's Personal makes fourteen, and the four family stand-ins
  (Tectonic Tide, Undone Be Thy Sinful Hex, Mollis Favonius, Ladder of Divine
  Ascent) carry it too. Nothing reads it yet.
- **Klee is herself Hexerei** (your refinement, brief §7.4), so "two witches
  make a circle" is, for her, Klee plus any one Hexerei card.
- **Her pool's verbs** are Bomb, Mine, Set off, Spark and Elemental Reaction,
  all printed as keywords (LAW, R237-era pick 5). A reader uses those and
  the word Hexerei, and nothing new.
- **The bound the brief set:** three or four readers, no more, "a bridge into
  the companion layer and not a fourth loop."
- **Every card has a place alone** (D6). A reader is companion-fed by
  nature, so each one below says what it does in a deck with no Hexerei
  card in it. Where the honest answer is "nothing", the pick says so.

## 2. The three cards

Numbers are a first honest price against her live pool (Pop! is a 0-cost
Bomb 5; Fish-Flavored Bait is 1 for 4 damage and a Bomb 4; Chained Reactions
is a Rare Power at 1 that places a Bomb 3 whenever a Bomb goes off).

**Coven Errand** (Common, 1, Skill). *Place a Bomb 5. If you played a
Hexerei card this turn, place a Bomb 5 on ALL enemies instead.* Upgrade:
Bomb 7. Alone it is a Pop! that costs 1, a little under the Common bar,
which is the price of the upside; with one witch played first it is Mine
Toss without the Mine. The read is cheap on the board: you already know
whether you played a companion this turn.

**Witches' Circle** (Uncommon, 1, Power). *Whenever you play a Hexerei
card, place a Bomb 3 on a random enemy.* Upgrade: Bomb 5. This is Chained
Reactions' shape with a rarer trigger, so it sits one rarity down. Alone it
is dead, and that is pick 2: the brief's own sketch accepted a dead-alone
Power as the bridge card, drafted only by a deck that already holds witches,
but a one-line floor ("When you play this, gain 1 Spark") would keep it
from ever being a blank draw.

**Alice's Letters** (Rare, 2, Power). *Hexerei cards cost 1 less. Whenever
a Hexerei card triggers an Elemental Reaction, the next Bomb you set off
this turn deals that element instead of Pyro.* Upgrade: cost 1. The second
line is Prune's Hexhunter Chime made general: the engine hook exists from
her Personal (the next-Bomb element override, PR #314), so every witch who
reacts hands her the off-element bomb the React loop wants, and the law on
earned reactions does not move (the element still arrives through a
companion). The first line is the one number the seats decide; a deck
holds two to six Hexerei cards, so it is worth at most an Energy or two a
turn, and pick 3 offers the tighter form if that reads as an engine.

## 3. The fourth, if wanted

**Hex and Wick** (Common, 1, Attack). *Deal 6 damage. If you played a
Hexerei card this turn, Set off.* Alone it is a weak Pocket Fireworks; with
a witch it is a cheap detonator that does not spend a Spark. It is the
card the brief did not sketch, and the pool already has five Set off
Attacks, so my default is to leave it out until the round-8 read says the
coven wants a cheaper fuse.

## 4. What this costs and what it touches

Three rows in `docs/prototype-surface.yaml` under the Klee arm, a keyword
tip for Hexerei on Klee's side ("Hexerei: a Companion card from the witches'
circle"), one new hook in each engine (a Hexerei-play trigger, which the
Nicole stand-in already needs, so it lands once), and three illustrations.
No LAW change. Built behind `KLEE_OVERHAUL` like the rest of her pool.

## 5. Picks

1. **How many.** (1) *The three in §2* [default]. (2) Four, adding Hex and
   Wick now.
2. **Witches' Circle alone.** (1) *Dead alone, as the brief's bridge card;
   the draft decides* [default]. (2) Add "When you play this, gain 1
   Spark" so it is never a blank.
3. **Alice's Letters' first line.** (1) *"Hexerei cards cost 1 less"*
   [default]. (2) "The first Hexerei card you play each turn costs 0",
   which is one Energy at most and reads less like an engine.
4. **When they are built.** (1) *For round 8, after the round-7 seat read
   and your run, so her pool does not move mid-round* [default]. (2) Now,
   into round 7's build, so the seats read them on the same night as the
   coven.
