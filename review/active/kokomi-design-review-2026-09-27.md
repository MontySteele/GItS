Status: OPEN (Paper; picks for [USER])

# Kokomi: design review, 2026-09-27

**Ask ([USER], 2026-09-27):** "can you please do a design review of Kokomi?
The design goals, how that aligns with her character, and what seems to work
well vs what's unsound design. Let's prepare to get that moving if the Klee and
Furina playtest results come back positive."

**Sources:**
- the brief, draft 7 (`review/active/kokomi-brief-2026-09-01.md`);
- the R276 review (`review/ruled/kokomi-review-2026-09-23.md`);
- your first run (`review/ruled/kokomi-user-run-1-2026-09-07.md`);
- the last seat round (`review/records/seat-round-2026-09-23.md`);
- the live pool: 39 cards in `KokomiOverhaulRoster.Slice()`, with faces in
  `docs/prototype-surface.yaml`.

You have not yet played the R276 rewrite. Only the seats have.

## 1. What she is meant to be

The brief says: "Kokomi wins the fight before it starts. She writes the plan;
the Bake-Kurage carries it out at the start of her next turn."

- **Plan.** A card with a Plan line can be played on the jellyfish instead, and
  it lands next turn.
- **Nothing happens by itself.** The jellyfish acts only on a card's order.
- **Every card has two halves.** The now-line answers this turn; the Plan line
  buys what only a head start can buy (R276).
- **Three loops:**
  - the Tactician: Plans and their payoffs;
  - the Priestess: Block through the jellyfish;
  - the Commander: companions.
- **Her relic, Tamakushi Casket:** every debuff she applies is also a 2-damage
  Hydro hit.

## 2. How that fits the character

Genshin's Kokomi rests on three things.

- **The strategist who plans to spare her soldiers.** This is Plan, and it is a
  strong match. No base-game character casts on a delay, so it is both hers and
  new. Keep it.
- **The healer.**
  - In Genshin her HP scales her damage, her jellyfish heals and hits on its
    own, and her Burst turns her attacks into heals.
  - Here almost none of that is left:
    - The healing law (Rare and Exhaust, `LAW.md`) leaves one Mend card: The
      Moon, A Ship O'er the Seas, Mend 6.
    - Sango Isshin is the one card that scales with her HP.
    - The jellyfish acts on its own only through the Casket's 2.
    - Nereid's Ascension carries her Burst's name but plays as "your first Plan
      happens twice".
- **The Hydro support for a team.**
  - Every damaging card of hers applies Hydro (R276), but solo nothing reacts
    with it. The seats wrote: "Hydro auras never mattered in six fights".
  - The aura counts as a buff, not a debuff (`AuraPower.cs:74`), so it does not
    feed her own debuff cards either (Undertow, Well Laid, Riptide).

**So the mind is hers, but her other two pillars are not there yet.** Starting
from the strategist was the right call, since it is her most distinctive trait
and the one that suits Slay the Spire best. Of the other two, healing is
limited by the healing law, and Hydro does nothing in a solo run.

## 3. What works

- **Plan itself.** Your run: "better than before". The seats' best turns were
  all Plan turns:
  - leaving an enemy at 2 HP for the Plan to finish;
  - turning down a sure two-Plan lethal for the Block line;
  - Opening Gambit before Kurage's Oath, for a doubled, Vulnerable-boosted hit.
- **Timing edges the seats found without being told.** A Plan is not a hit, so
  it gets past Thorns and Skittish. A Plan cannot strip Block the enemy is
  already holding.
- **The Casket.** It ties her debuffs to her element, gives every Weak and
  Vulnerable card a second job, and the seats liked it.
- **Cards whose halves do different jobs.** Read the Field, Slack Water, Flank,
  Opening Gambit, Feigned Retreat and Tide Wall. Tide Wall's Block is sized to
  the next attack, which only a head start can know. These are the cards the
  seats argued over (R276 review, section 2).

## 4. What is unsound

1. **A safe turn still plays itself.**
   - On 8 of her 22 Plan cards the only now-half is Block, and Kurage's Oath
     makes 9 of 24:
     - Ambush;
     - Coral Bulwark;
     - Cleansing Wave;
     - Tide Wall;
     - The Moon, A Ship;
     - Ripple;
     - Feigned Retreat;
     - Second Wave.
   - When the enemy is not attacking, Block now is worth nothing, so these are
     written every time. The seats said so after the rewrite. Claude: the trade
     "was always Block this turn against damage next turn". GPT: Ripple was
     "automatic".
   - R276 made the halves different jobs. But when one of the jobs is Block,
     the enemy's intent still decides alone. Your autopilot complaint is
     smaller now, not gone.
2. **Three cards still break the halves rule.** Each one's two halves are the
   same effect at two sizes:
   - Cleansing Wave (5 Block now, 10 Block planned);
   - Chain of Command (3 per Companion now, 6 planned);
   - Ripple (2 Block now; 1 Energy and 4 Block planned).
3. **The payoffs check a condition that is nearly always true.**
   - These all pay when "a Plan was carried out this turn":
     - Treatise;
     - Song of Pearls;
     - Feint;
     - Sango Isshin;
     - Princess of Watatsumi (her Ancient);
     - Sangonomiya's Counsel (co-op).
   - In a Plan deck that is every turn after the first. R268 already found that
     "a reliably satisfied clause is a tax on the intuitive order, not a
     choice".
   - They work as engine pieces, but they add no decision, and they all push
     the same way: always keep a Plan queued.
4. **Hydro does nothing on her own.**
   - Her team role is her main job in Genshin, yet her Commander loop is her
     thinnest: Rally, Vanguard, The General's Banner and Chain of Command. None
     of them mentions an element.
   - Klee has a React plan, which now includes Alice's Teapot, and Furina has
     her Guest Cast. Kokomi has no reaction plan at all.
5. **The pool is half size.**
   - She has 39 cards (23 Common, 12 Uncommon, 4 Rare) against the 78 target,
     so drafts repeat.
   - About a quarter of the pool works on the queue itself: Dusk, three riders,
     Second Thoughts, Change of Plans, Moon's Reflection, Tide Chart and Scout
     Ahead. The seats reach few of them.
   - Her complexity budget went into the order puzzle, which only appears when
     three or more Plans are queued.
6. **Smaller notes:**
   - Nereid's Ascension is a strong Rare that shares nothing with its namesake.
   - Her relics and potions are still the Silent's Poison and Shiv pool, as
     Klee's and Furina's were until today.

## 5. The pass I would run, once Klee and Furina come back positive

1. **The core, on the 39 cards.**
   - Give most Block-only now-halves a job that counts on a safe turn: draw,
     filter, a debuff, or Hydro set-up. Keep Block only where the card's whole
     job is defence (Tide Wall, Breakwater). Target: at most 3 Plan cards
     whose only now-half is Block.
   - Fix the three breaches.
   - Re-key two or three payoffs to a choice. For example:
     - a Plan landing on a debuffed or Hydro enemy;
     - your first Plan being an Attack;
     - a Power that pays when the jellyfish has nothing queued. This one
       rewards *not* writing, which is the missing counterweight on a safe
       turn. Because it is a card you played, rule 4 ("nothing happens by
       itself") still holds.
   - Then one short seat (one act) and your run. The question it answers is
     the one from your first run.
2. **The team: "plan the reaction".** Rebuild the Commander so she puts Hydro
   on now and plans a companion's Electro, Pyro or Cryo to land next turn on
   the wet enemy. The reaction is one she scheduled, which is the strategist's
   version of Klee's React.
   - The prototype Gorou (Crystal Collapse) is already a "plan a companion"
     card.
   - In co-op the partner supplies the second element, and her ruled co-op pair
     (including the Rare, Exhaust ally heal) fits the same loop.
3. **Grow to 78** in batches, as Furina's supporting pool did. Each loop gets
   depth, and queue cards that are never played get cut.
4. **Her relics and potions.** This is where the healer can come back legally.
   The healing law exempts potions and relic-scale trickles (`LAW.md`,
   card-sheet rules), so her own relic set can heal in small amounts without
   touching the card law.

## 6. Picks

1. **The safe-turn fix.**
   - **(a, default)** The core pass above: most Block-only now-halves
     rewritten (at most 3 left), the three breaches fixed, and two or three
     payoffs re-keyed, one of them rewarding an empty queue. No rule changes.
   - **(b)** The same pass, plus R276's second option: unblocked damage you
     take knocks your last Plan off the queue. That is a rule change.
   - **(c)** Play the current build yourself first and decide after.
2. **Her team role.**
   - **(a, default)** Rebuild the Commander as "plan the reaction", 5 or 6
     cards, as the first growth batch.
   - **(b)** Hydro stays a colour for companions and co-op partners, with no
     reaction plan of her own.
3. **The healer.**
   - **(a, default)** Healing comes back through her relics and potions. Mend
     stays on one Rare card.
   - **(b)** Also rebuild Nereid's Ascension into a mode like her Burst. The
     "first Plan twice" effect moves to a card with a constellation name.
4. **Order.**
   - **(a, default)** Core pass, then one short seat, then your run, then the
     team batch, then growth to 78, then relics and potions.
   - **(b)** Grow to 78 first and fix the core along the way.
