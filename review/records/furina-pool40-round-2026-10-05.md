# Furina pool-40 seat round, with an Ironclad control, 2026-10-05

**What ran.**
- Build 0.2.4437: Furina's pool at 34 reward cards (#918, `review/active/furina-pool-40-2026-10-05.md`), Universal Revelry reading Drain and Repay only, and the new seat page (#919: enemy briefing, incoming line, events line).
- Ascension 0. Three lanes, with a Sonnet seat (medium effort) for each act and only a state handoff between acts. Lane 3 is base Ironclad on the same build, as a control.
- Raw records are in the session scratchpad and are gitignored.

| Lane | Character | Seed | Act 1 | Act 2 | Act 3 |
|---|---|---|---|---|---|
| 1 | Furina | JF391WG2NN0X | Vantom, ended 50/90 | Kaiser Crab, ended 44/90 | lost on floor 46 to a Slimed Berserker, entered at 13/84 after the Soul Nexus elite |
| 2 | Furina | WDETA8RRGH98 | Vantom, ended 59/78 | The Insatiable, ended 57/78 | **won**, Aeonglass on turn 8 |
| 3 | Ironclad | PPW4N6WX70LS | Vantom, ended 58/80 | The Insatiable, ended 45/80 | **won**, the Queen on turn 5 |

**Verdict: Furina's pool is at a base character's level, and it now plays more than one way.**
- Both Furina runs cleared two acts, and one won. Last round one cleared act 2 and the other lost there.
- The control won from similar HP. Both Furina seats called act 1 easy.
- Two plans showed up:
  - Lane 2's act 1 deck was built on Drain with payoffs (Critics' Darling+, two copies of Salon's Encore, Wriothesley).
  - Both lanes finished on a Fanfare bank cashed by an all-enemy or spend-all card.
- Repay never became a plan.

## What played well
- **Let the People Rejoice+ beat the Kaiser Crab cleanly.** Lane 1 killed both arms on the same turn, so Crab Rage never fired. The same boss killed last round's lane 2.
- **Drain payoffs made Drain a deck.** Lane 2: "one Drain card with Encore, Darling and Wriothesley out pops four hits", which beat Vantom's Slippery (act 1, fight 7). The sim gave Critics' Darling a 2% pick rate; a seat built around it.
- **Bis! closed the winning run.** Lane 2, Aeonglass turn 8: Bravura+ for 114, then Standing Ovation+ off the half that Bis!+ kept.
- **The Drain line now bites at the right time.** It refused Drain cards at act-2 and act-3 elites and bosses with "Too close to your Drain line" (#916). Below it, the seat has to find another way.
- **Revelry's new text did its job.** No 250-damage hits taken off skipped Block. The biggest hits were 131 and 121 into bosses and elites, banked over several turns.

## What did not
- **HP is the bottleneck in act 3.**
  - Both Furina seats fell to 10 to 12 HP at the Soul Nexus elite.
  - Lane 1 then had no rest before the next fight. At 7 HP every Drain card was shut off, and it died.
  - Furina's only sustain is Salon Solitaire's Repay 2 a turn.
- **Pneuma (Repay) never formed.** Seats could not tell the payoff of Fountain of Lucine, Pneuma Refrain or Endless Waltz from the page. A Five-Century Act's "Drain down to 1 HP" gave "no hint of what it does at 1 HP".
- **Guest Stars went undrafted on lane 1.** The card face says only "Summon Lyney"; see the page section below.
- **Chevreuse's end-of-turn act previews "4 Energy next turn",** though she deals 4 damage. A text bug.

## The new seat page (the harness question)
| Line | Verdict | Evidence |
|---|---|---|
| Enemy briefing | **The most useful line, on all three lanes** | "Bygone Effigy sleeps" made every seat spend turn 1 on setup (Ironclad lost 3 HP to that elite); Vantom's Slippery line shaped lane 2's plays. But it failed to print for the Decimillipede (lane 3, act 2) and on every brief page in lane 3's act 3 |
| Incoming this turn | **Decisive where shown** | Ironclad: "drove most decisions and was exact every time". It is left off Furina's stage boards, so neither Furina seat saw it |
| Since last page | Mostly noise | Repeats like "Slow fired x2" and "Slippery fired x2" on one hit confused a seat. A Shatter that removed Frozen went unreported, so a seat thought Frozen had failed (lane 2, act 1, fight 4) |

Being fixed now, with no pick needed:
- the briefing printing once per fight;
- the incoming line on Furina's boards;
- a quieter events line, with Shatter and "Drained N HP returned" added;
- the guest's effects printed on its card;
- Chevreuse's preview;
- named effects on vague intents ("steals a card", "applies Frail 2");
- the Drain line saying where it comes from;
- the brief warning seats off bare `python`, which hung twice.

## What to change
1. **The page fixes above.** Then a Sonnet effort test (low, medium and high on one seed and one character), as [USER] asked.
2. **Furina's act-3 HP.** Watch [USER]'s run before touching it. If it holds, the lever is a Pneuma card that seats can read, not more Block.
3. **Repay's legibility.** Once guest and Repay faces print in full, see whether seats draft Pneuma before any number moves.

Not ours: Enthralled and Doubt (curses), the Pen Nib preview, Spoils Map's silent payout, and Chains of Binding. These are base-game behaviours.

**Seat cost (medium effort, 9 seat-acts).** 1.42M cache-write tokens and 82.5M cache-read tokens, with context peaking at 120k to 200k per seat. That is about 5.9M fresh-input equivalent, counting reads at 1/20 and writes at 1.25. The transcripts under-log output tokens, so the effort test compares cache writes, which include everything a seat generated.
