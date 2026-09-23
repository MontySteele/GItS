Status: OPEN (three picks, §4; replaces the open picks on PR #476)

# Furina: the Stage is promising and too thin, and you have not played it yet

Written 2026-09-23 by Claude (Opus 5.5), from the Stage brief (draft 2,
R269), rounds one to three, the round-three packet on PR #476, your reframe
run (`review/ruled/furina-user-run-1-2026-09-07.md`), and a census of the
live build (26 draftable cards, read off the generated C# and checked
against the game's own log).

## 1. What is working

The Stage is the right idea, and it is the most Genshin-faithful of the
three kits. Her three Salon members stand in front of her as pets with
visible bars. Enemies hit her Block, then the lead performer, then her.
She spends the performers' applause (Fanfare) for bigger numbers, and one
emptied by a Spend takes a bow. Round three was the best read in the
kit's history. No seat died, every seat beat the act-1 elite, the three
performers read as three distinct characters, and "spend the bar or keep
it" was a live choice because the answer kept moving.

This is her third foundation in a month (the Fanfare kit, the reframe, the
Stage). The first two were abandoned partly because you could not read the
screen. The Stage's screen is now readable to seats, and you have not
played it yet. That is the most important next step for her, and nothing
below should delay it much.

## 2. What is not working

**Two rules point the wrong way, and three rounds agree.** Spend and the
Fanfare readers take from the *lead*, the performer hits are deleting. Raise
(her refill) goes to the *back*, where Fanfare survives. So the bank you
build is never the one you spend. Separately, a Spend bigger than the lead's
bar still pays out in full, and the lead takes a bow. Summoning a 1-Fanfare
body and spending 5 off it therefore beats growing a performer, and six of
nine seats called it a loophole. Round three proposed a default for each.
I agree with both, and together they give each seat a job: **the front
performer is the shield, the back performer is the bank.**

**The pool is too thin to be her kit yet.** She has 26 draftable cards.
Only 14 are Stage cards; the other 12 are shipped cards that happened to
survive the filter that removes retired words. None of the 14 is a Power,
so no card lets a deck become "a Stage deck" the way Grounded or Alice's
Recipe does for Klee. Round three also saw five hands with nothing to do,
all stage-dependent Skills with an empty stage. The brief names that
weakness, but at 26 cards it comes up too often.

**Her starter isn't what the brief says.** An old patch that gives
characters starting companion cards still runs for her. Every Stage run
opens with two Fontaine companions in place of one Solicitation and one
Stage Presence. Klee and Kokomi get none under their prototypes. Whether
characters start with a companion belongs to the direction document's
pick 3. Until that is ruled, I would make Furina match the brief.

## 3. What I would do

1. **Build the two rule fixes.** Spend needs the full price, so a short
   lead cannot choose the Spend mode, and a bow comes from an exact
   emptying. Spend and the readers take from the back performer, the lead
   absorbs hits and regenerates, and when one performer stands it is
   both. Scene Change moves a fat reserve forward as a shield, or a hurt
   lead back to be refilled.
2. **Write a Stage pool pass of about ten cards**, so the pool is mostly
   hers:
   - two or three Powers that make a deck a Stage deck (for example,
     performers act twice at end of turn, or a bow also raises the next
     performer);
   - two cards that are good on an empty stage, so an empty stage is a
     weaker turn rather than a dead one;
   - a Rare built around her Pneuma/Ousia swap, which is the half of her
     Genshin identity the Stage doesn't touch yet.

   The twelve leftover shipped cards stay until the new ones are read.
3. **Then two seats, then you play her.** This is the first time you
   would play the Stage, which is exactly when the norms say you should.
4. **Hygiene, without asking:**
   - Her Ancient card grants Encore, which is retired.
   - The retired reframe's drain code still runs on every card play.
   - The brief's card names are stale.
   - Crabaletta's Hydro is not on her face.
   - Round three's six display bugs are open, and their ids collide with
     Klee rows minted since. They get new ids.

## 4. Picks

**Pick 1: the over-sized Spend.**
1. **(default)** The rider needs the full price, and a short lead cannot
   choose it. A bow comes from an exact emptying.
2. Keep the current rule: the rider fires in full, and the lead pays what
   it has and bows.

**Pick 2: where Spend and the readers take their Fanfare.**
1. **(default)** From the back performer, the bank. The lead is the
   shield.
2. Raise targets a performer you choose. Spend and the readers stay on
   the lead.
3. Keep as is.

**Pick 3: the Stage pool pass.**
1. **(default)** About ten Stage cards, including Powers, empty-stage
   answers and a Pneuma/Ousia Rare, built with picks 1 and 2. Two seats,
   then your first Stage run.
2. Build picks 1 and 2 only, and you play first. The pool pass follows
   your notes.
