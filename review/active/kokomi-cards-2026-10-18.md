# Kokomi: every card placed, and what changes (v2), 2026-10-18

This follows `review/active/kokomi-archetypes-2026-10-18.md`, where the user ruled three archetypes (pick 1
(a)): **Grand Strategy**, **Read the Tide** (not a turtle), and **the Shoal** (the "Silent-like Sting / Ward
strategy"), with Companions in the middle.

**Why there is a v2.** The user had GPT review v1. GPT's verdict: v1's six changes "would give the Shoal
a stronger engine", but would not make Kokomi "feel more deliberate". The user then ruled: "Yeah, let's try
a v2 on the Kokomi paper." I checked GPT's claims against the sheet, and they hold:
- **The Exhaust pair made one action answer everything.** With Tidepool and Receding Tide out, Shoal Call
  and its three Stings gave 12 damage, 8 Block and 4 draws for 1 Energy, and fed The Tide Returns too.
  Exhaust is a cost for the Ironclad, who burns cards he wanted. Kokomi's Exhausted cards are free Stings
  and Companions, so for her the payoffs were pure bonus.
- **Undertide Lance's "3+ Plans" bar was cheap.** Shoal Call writes three 0-cost Plans.
- **Coral Bulwark's +3 against an attack was efficiency, not foresight.** You play Block then anyway.
- **Damage-dealing payoffs don't stop a turtle.** Tidal Riposte's retaliation is automatic. The test is
  whether the player has to choose when to turn safety into an attack.
- **The Shoal converges on planning.** Endless Shoal turns a carried-out Sting Plan back into a Sting, and
  Following Current pays on the way. "Play now, play many" then gets planning's rewards as well.

v2 keeps Plan, the three archetypes and Stings' Plan lines. It changes fewer cards, and each change asks for
a choice.

**Ruled 2026-10-18.** GPT reviewed v2 as well, and recommended picks 1 (b), 2 (a) and 3 (a), with three
corrections. The user: "On Kokomi, I'm good with all three - let's try that and see if it works." The
corrections are made in place below:
- Nereid's Ascension (sec.2, change 2);
- the stored Riposte's rules (change 4);
- flipping and healing (secs. 1 and 3).

## 1. What Kokomi promises

**She makes room to prepare, protects the preparation, and chooses the moment to take control.** This is
GPT's line, adopted here. In Genshin her kit is protection (the jellyfish's healing and Hydro) and
stepping in personally (her Burst). Here protection is mostly Block, Weak and
support. True healing is allowed only on a Rare that Exhausts (`LAW.md`, card authoring), which is
where her Mend cards already sit.

Each archetype gets one **winning turn** and one **cost**:

| Archetype | The winning turn | What makes it a choice |
|---|---|---|
| **Grand Strategy** | A morning where a sequence you arranged fires in order: Opening Gambit doubling the next Plan, Second Wave running one twice, Pincer playing your first Attack twice, into Masterstroke or Tamakushi's Wrath. | The setup turn spends Energy and cards for nothing now. You either protect the sequence, or break it to survive by flipping a waiting Plan or using Change of Plans. |
| **Read the Tide** | Commit an answer before the enemy acts (Kelp Wall, Brine Sting, Turnabout, Tide Wall), then spend what it built on one counterattack. | Block you spend is safety you lose. Plans are committed before the next intents are known. |
| **The Shoal** | Many Stings in one turn into Watchful Shoal and The Shape of Water. | Each Sting is 4 damage now, or 3 to ALL next morning. Planning it should cost the "now" payoff, not collect both. |

## 2. The changes (five cards)

**Grand Strategy: afford the setup turn, and get a moment to cash it.**
1. **Shell of Sanctuary → Draft the Orders** (Common Skill, 1): "Gain 5 [8] Block. The next card you plan
   this turn costs 1 less." This is unchanged from v1. It pays for a setup turn and protects it, and Shell
   of Sanctuary was plain Block.
2. **Nereid's Ascension: kept as it is for this prototype** (pick 1 (b)). v2's version ("Carry out all your
   waiting Plans now. This turn, your Attacks deal double damage") had its timing wrong:
   - Yesterday's Plans fire at the start of your turn (`KokomiPlan.cs`), before you could play it. So
     "waiting Plans" would be the ones you wrote that same turn. That makes it a one-turn combo, not
     prepare, survive, take command.
   - Read the Tide's example fails for the same reason: a Plan written this turn has seen no attack yet.
   - The current version ("your first Plan is carried out twice") isn't free-standing after all: it makes
     the order of your Plans matter.

   **Next to try** is a card with only a Plan line, like Masterstroke: "Plan: This turn, your Attacks deal
   double damage." You write it, the enemy takes its turn, and the morning is Kokomi's counteroffensive.
   It needs a no-stacking clause, or Second Wave would make it quadruple. This version is not in this
   build.

**Read the Tide: trade safety for the counterattack.**

3. **Tidal Rebuke** (Rare Attack, 2 [1], Retain): "Lose all your Block. Deal twice that in Hydro damage to
   ALL enemies." Today it deals your Block once and keeps it. Now it's the decision itself: you're
   defenceless after a big AoE.
   - Watatsumi's Grace ("keep up to 10 [15] Block") gains a purpose: bank Block across a turn, then spend
     it.
   - Coral Crash stays the Common Body Slam that keeps your Block.
4. **Tidal Riposte** (Rare Power, 1): "Whenever you fully Block an enemy's attack, your next Attack deals
   8 [11] more damage." Today it deals 8 back automatically. Now the bonus stacks until you attack, so the
   deck wins only by choosing to strike. The rules, so it doesn't compound the way the old per-hit version
   would:
   - **It triggers once per enemy attack** whose hits are all blocked, not once per hit.
   - **It applies like Vigor:** the stored total adds to every hit of the next Attack card you play, then
     clears.
   - **A Plan carried out in the morning doesn't spend it.** You choose which card gets it.
   - Pearl Current (2 damage, 4 hits) is the biggest multiplier. Seats watch it.

**The Shoal: playing now and planning stop collecting the same rewards.**

5. **Endless Shoal** (Uncommon Power, 1): "Whenever the Bake-Kurage carries out a Plan that is not a Sting
   or Ward, add a Sting to your Hand." The bridge from Grand Strategy into the Shoal stays. A planned Sting
   no longer replaces itself. Kurage Canopy gets the same clause for Wards.

So **four changes are built**: 1, 3, 4 and 5.

**What v1 changed that v2 does not:**
- Undertide Lance and Coral Bulwark stay as they are.
- Kurage Vanguard, Pearl Current and Suffocating Deep are not replaced. A good attack is allowed to be a
  good attack.

Tidal Rebuke's and Tidal Riposte's numbers are first guesses for the seats to test.

## 3. Exhaust: held

In our kits, 80 cards Exhaust and none rewards it. The user is right that this is a gap. v1's package is
held (pick 2 (a)) because it let one action answer every need: offense, Block, draw and a finisher, all
from free Stings. It is not held because Kokomi can't have Exhaust. Rewarding disposable cards can be good
design: generators and payoff Powers still cost a draft pick, a draw and Energy.

One idea is still open: **salvage a failed Plan**, by Exhausting a waiting Plan for an immediate effect.
Flipping a Plan doesn't do this. A flip changes which line fires, not when it fires. It goes in BACKLOG for
a later look.

## 4. Where every card goes

Card texts are in `docs/prototype-surface.yaml`.

| Group | Count | Cards |
|---|---|---|
| **Grand Strategy** | 18 | Feint, Turning Tide, Breakwater, Press the Advantage, *Draft the Orders*, Tideturn, Opening Gambit, Second Wave, Change of Plans, Pincer, Undertide Lance, Following Current, Masterstroke, Sango Isshin, Shoal of Spears, Battle Formation, *Nereid's Ascension*, Grand Design |
| **Read the Tide** | 23 | Kelp Wall, Coral Crash, Undertow, Coral Bulwark, Brine Sting, Flank, Evening Watch, Prepared Retreat, Tide Wall, Undercurrent Snare, Drowning Pressure, Spearhead, Ambush, Riptide, War Council, Turnabout, *Tidal Rebuke*, *Tidal Riposte*, Sea's Reproach, At Water's Edge, Watatsumi's Grace, The Moon a Ship, Suffocating Deep |
| **The Shoal** | 18 | Jellyfish Drift, Kurage's Wake, Watatsumi Drill, Bubble Ward, Shoal Call, Tidecleanse, Brine Spray, Kurage Barrage, The Shape of Water, Flotsam Surge, Sea Glass Harvest, *Endless Shoal*, Kurage Bloom, Kurage Canopy, Watchful Shoal, All Streams Flow to the Sea, Grand Strategist, Dawn Tide |
| **Companions** | 9 | Orders from the Shrine, Watatsumi Muster, Call the Generals, Sangonomiya's Orders, Treatise, and the four Gorou cards |
| **Co-op** | 5 | unchanged |
| **Glue** | 10 | Tidal Surge, Tidal Screen, Surging Shoal, Read the Field, Steady Tide, Resolve of Watatsumi, Riptide Ruin, Tamakushi's Wrath, Kurage Vanguard, Pearl Current |

18 + 23 + 18 + 9 + 5 + 10 = 83: the 78-card pool plus the five co-op cards. Changed cards are in italics.

**Not addressed in v2:** Battle Formation ("the first time each turn 2 or more Plans are carried out") is
still a count that every deck meets. If the seats show it as an automatic pick, it's next.

## 5. Next

Build the four changes, with their sim twins and tips. Then run five Kokomi seats:
- **three draft freely.** They show whether ordinary drafting finds different decks, or the same pile of
  Powers.
- **two are briefed** toward Grand Strategy and Read the Tide. They show that those two can win.

Each seat record answers: what was the winning turn, and what did you give up for it? A run of yours
follows.

## Picks

**All three ruled 2026-10-18: 1 (b), 2 (a), 3 (a).** The user: "On Kokomi, I'm good with all three - let's
try that and see if it works."

1. **The five changes.**
   - **(a, default)** Build all five.
   - (b) Build them, but leave Nereid's Ascension as it is. It's the biggest change, and it moves her Rare
     build-around.
2. **Exhaust.**
   - **(a, default)** Hold it: no Kokomi Exhaust payoffs, and a BACKLOG line for a future kit.
   - (b) Try one card that salvages a Plan, "Exhaust a waiting Plan: …", in the same seat round.
3. **Tidal Rebuke's cost.**
   - **(a, default)** "Lose all your Block. Deal twice that." You give up the Block.
   - (b) "Deal damage equal to your Block. Then lose half of it." A softer trade.

## 6. After the v2 round: two changes (2026-10-18, ruled)

GPT reviewed the v2 round (`review/records/kokomi-v2-round-2026-10-18.md`). The user ruled both of its Kokomi
picks: "Makes sense! ... let's do both."

**1. The four damage cards that count Plans stop counting Stings and Wards.** On the printed numbers, planning
three Stings and then playing Tideturn deals 32 now plus 9 to every enemy next turn. Playing the same three now
and then The Shape of Water deals 32 now and nothing more. So planning won outright, and Shape was offered seven
times and never taken. The new texts:

- Tideturn: "Deal 8 Hydro damage, plus 8 for each Plan waiting (not Stings or Wards)."
- Feint: "Deal 8 Hydro damage. Plan: Deal 6 Hydro damage for each Plan carried out this turn (not Stings or
  Wards)."
- Turning Tide: "Deal 9 Hydro damage. Plan: Deal 5 Hydro damage to ALL enemies per Plan carried out this turn
  (not Stings or Wards)."
- Shoal of Spears: "Deal 5 Hydro damage to ALL enemies, plus once more for each Plan waiting (not Stings or
  Wards)."

Under these texts, three planned Stings with Tideturn give 8 now and 9 next turn, against Shape's 32 now. The
Shoal is now the deck that wants damage this turn, and Grand Strategy is the one that arranges real Plans.

Breakwater and Battle Formation keep counting every Plan. They are defensive or once a turn, and GPT advised
against applying the same rule to them. Shape is looked at again after the round.

**2. Read the Tide gets an Uncommon that rewards blocking an attack completely.** Kelp Wall (Common) pays back the
damage you blocked, and Tidal Riposte (Rare) pays for each attack you blocked completely. Nothing in between
asks you to commit to a perfect defense:

- **Unbroken Tide**, Uncommon Skill, 1 Energy: "Gain 8 [11] Block. Plan: If you lost no HP since you planned
  this, deal 12 [16] Hydro damage to ALL enemies."

Planning it costs its own Block, so the rest of the turn has to hold the line. It also teaches the habit Tidal
Riposte pays for. The pool becomes 79. A cut, if one is needed, comes to the user with card texts and evidence.

**The round:** two seats, both drafting freely. Each record answers two questions:
- did you ever play Stings now, instead of planning them, and why?
- did you ever give up damage to prepare a particular future turn?
