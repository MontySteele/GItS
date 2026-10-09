# Furina pool-75 round, with an Ironclad control and a Fable review, 2026-10-09

**What ran.**
- Build 0.2.4644+next: Furina's pool at 75 cards and the new guest rule
  (`review/active/furina-pool-growth-2026-10-09.md`, #990), plus the
  playtest trims (#988).
- Ascension 0, one Sonnet 5.5 seat per run, full runs. Raw records are in
  the session scratchpad and are gitignored.
- [USER]'s ask: "If the initial Furina playtest looks promising (or workable
  with minor corrections), then please do 5 runs and share the results with
  a Fable reviewer for feedback on the design and balance level." The
  first round went 1–1, so the five runs followed.

| Run | Seed | Result |
|---|---|---|
| Round 1, Furina | JF391WG2NN0X | Died on floor 24 to the act-2 elite Decimillipede (pool 40 reached floor 46 on this seed) |
| Round 1, Furina | WDETA8RRGH98 | **Won** all three acts at 44/78 HP (pool 40 also won here) |
| Round 1, Ironclad control | PPW4N6WX70LS | Died at the act-3 boss, the Queen, on floor 48 |
| Five runs, lane 1 | 0J427L1YQV15 | Died on floor 33 to the act-2 boss Kaiser Crab |
| Five runs, lane 2 | U11C39H9TMZ2 | Died on floor 31 to the act-2 elite Entomancer |
| Five runs, lane 3 | U1G91B5BNG2P | Died on floor 31 to the act-2 Hunter Killer |
| Five runs, lane 4 | TYXJLVY31QN7 | Died on floor 40 to the act-3 elite Soul Nexus |
| Five runs, lane 5 | 39A9PJH5097H | Died on floor 48 to the Queen |

**Verdict.** On win rate, Furina is at or a little under a base character:
1 win in 7, against 0 in 5 for the base five's baseline
(`review/records/base-five-baseline-2026-10-05.md`). **But she dies a full act
earlier.** Four of her six losses were in act 2. The median death floor is
about 32, against about 48 for the base seats.

The Fable review traced this to three rules that switch off at the same
moment:
- Fanfare pays most for enemy hits, so seats skip Block.
- Low HP then puts every fixed-Drain card past the Drain line.
- With nothing drained, Repay and every guest or Power keyed on Repay do
  nothing.

Three of the act-2 deaths came in forced elites entered at about half HP,
with the Drain half of the kit locked.

**Squaring this with "very OP".** The human co-op run played the 34-card pool
before the trims: Salon Solitaire at Repay 2, Usher at 7/13 and Interval
Bell at Common. Both humans blocked well, and the partner shortened fights.
This round changed the trims and 41 new cards at once, so it cannot say
which of the two moved her. Pick 4 separates them.

## What played well

- **The Fanfare bank and cash-out carried every run.** The standouts:
  - Standing Ovation killed all three Wrigglers in one turn.
  - Bravura+ hit 72 to 152.
  - Let the People Rejoice finished fights.
  - The win came from banking Fanfare and dumping it through the
    spend-all cards.
- **Real decisions found:**
  - Drain or Repay before Spend, because the printed number updates live.
  - Taking a hit on purpose to feed Lynette.
  - Exact Block to stun a Bowlbug.
  - Hold the Stage as the one Fanfare-to-Block fork. It saved three runs.
- **Guests were the engine where they keyed on damage.**
  - Lyney's Pyro fed Vaporize in the win.
  - Navia's discount made an exact 33 Block that survived a Berserker hit.
  - Clorinde's Electro with Hydro was "my best damage source".
- **The guest rule caused no complaint and no loops.** Guests were drafted in
  5 of the 7 runs.
- **Salon's Encore with 0-cost Drain cards** won most fights in one or two
  turns in r2 lane 1.

## What did not

- **The Drain line, in every record.** It sits at half the HP she entered the
  fight with. A hurt Furina gets a low line and still cannot Drain. The line
  is printed only on the Stage page, and cards refuse partway through a turn.
- **Repay cards do nothing when nothing is drained.**
  - Gentle Current (NEVER AGAIN, r2 lane 2), Soothing Waters and Hymn
    printed "Repay 4" and returned 0.
  - Charlotte "Repay 0 most turns".
  - Endless Waltz never fired (NEVER AGAIN, r1 lane 1).
- **Guests keyed on Drain switch off when she is low.** Freminet ("its Block
  needs Drain I could not afford") and Neuvillette ("0 Hydro damage") were
  NEVER AGAIN cards.
- **The new guest cards were never drafted:** Encore!, Tutti!, Final Bow,
  Casting Call, Showstopper, Ensemble Cast. "Made no sense with an empty
  stage." Ruled pick 3 (guests scale by buying acts) has no play evidence yet.
- **Rising Applause** is dead after turn 2 (five records). It is a starter
  card, so it stays.
- **Too strong for their slot:** Crabaletta (Common, 24 damage for 2) and
  Soloist's Solicitation (0 cost) are "automatic" picks. Bravura+'s
  3-per-point upgrade outdoes a Rare.
- **Fanfare resets each fight, and nothing says so.** One seat banked 30 for
  a fight that never came.

## Legibility fixes (no pick needed; Claude builds them)

- Print the Drain line, and where it comes from, on every Drain card's hover.
  Say on the Fanfare tip that it resets each fight.
- Always print "(Repays 0)" when nothing is drained, on every Repay face.
- Say on Salon's Encore that copies stack.
- Ousia Pledge's own Drain was logged as Thorns damage (r2 lane 2). Find out
  whether that is a label error or a real double count.
- Off-kit companion cards (Itto, Sara, Gorou and others) appeared in Furina's
  rewards in three runs. Confirm this is the intended colorless set.

## Picks (ruled 2026-10-09)

[USER] ruled: "Otherwise the defaults make sense to me." On pick 1: "Let's
try it. It feels like we're making a mechanics change to accommodate the
agents' poor play, but we can see how changing it looks in practice first."

1. **The Drain line, revised in discussion.** [USER]'s point: "if you start
   a fight at full health, you shouldn't lose half your health over the
   course of a fight, so draining half of it for more damage is just free
   power." The review's "Drain up to N" would have added free effects past
   the line, so it is replaced. The new rule:
   - The line moves up to **3/4 of the HP she entered the fight with**,
     which halves the free room.
   - **Drain can go past the line,** so no card locks.
   - **HP drained past the line does not come back** when the fight ends.
   - A Five-Century Act gets a new Rare text.

   **Simmed against the current rule first.** The sim result and the
   card-by-card list come back to [USER] before anything is built.
2. **The Repay floor, card by card.** [USER]: "I'm thinking this should be
   card by card, and can have more than just these ideas." Each Repay card
   gets its own no-drain effect (Vigor, Block, a guest act, or draw where it
   fits), proposed as a list. Endless Waltz is cut.
3. **Card numbers: default, ruled.** They are built together with picks 1
   and 2.
4. **Two seeds with the relic at Repay 2: default, ruled.**
5. **A guest-forward seat: default, ruled.**

**Built 2026-10-09:** picks 1-3 as ruled ("Yes - let's test it with a seat"); Soothing Waters keeps no leftover payout (its Vigor looped); readings and the loop probe are in `docs/notes/prototype-surface-provenance.md`.

**Process.** Every seat reports "Repo files read: none". Most declared a
`grep` on their own observe output. One seat was stopped by the permission
check on a compound first command. A fresh seat ran the same lane with one
command per call and was not stopped.
