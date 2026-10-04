Status: OPEN (picks at the end)

# Furina: re-founding the Stage (paper, 2026-10-03)

**Where it comes from.** [USER], after the co-op run: "Furina 'technically
works' in the sense that no individual component is broken, but they do not
play well with one another, and getting this any cleaner requires
fundamental design work." He named four mechanics: "Salon members in the
style of Defect orbs, Guest stars in the style of Osty, Fanfare, Tracking 3
separate HP bars to make this feel distinct from a Necrobinder run", plus
"the missing piece ... something to make all of this scale". And: "I think
we could handle Salon members OR guest stars easily enough, but combining
them both is causing issues."

## 1. Why it is messy: one number, four jobs

Fanfare is a performer's bar (`furina-stage-brief-2026-09-08.md` §3), and
that one bar does four jobs at once:

| Job | Rule | What drains it |
|---|---|---|
| the front performer's HP | rule 6 | every enemy hit past her Block |
| the bank her Spend modes pay from | rule 8 | her own cards |
| the fuel the star guests burn | guest paper, table | Neuvillette 3 per act, Escoffier 3, Lyney 2, Clorinde 1 from each other performer |
| the number the scaling cards read | §5.2 | nothing; they just want it high |

On top of those, the fade (rule 12) takes a quarter of every bar each turn.
That is four drains and one tap (the Raise cards: Rising Applause 5, Warm
Reception 3, and the rest). Each time we tuned one drain we starved the
others. When Spends got strong, the scaling cards went hungry. When the fade
began to bite, the guests burned out. So the guests survive only by being
recast, which is the rotation [USER] named.

Two more facts follow from it:

- **Nothing scales the stage.** Rule 10 says the acts are flat and "never
  read the bar": Usher gives 3 Block on turn 1 and on turn 20. Every bit of
  scaling sits in Furina's own cards and competes for the same bar.
- **The bars are everywhere.** 30 of the 85 `proto_fs_` rows name a seat's
  bar ("your front performer", "your back performer", "each performer").
  The seat-arranging family (Step Forward, Plot Twist, Revolving Stage,
  Stage Whisper) exists only to move bars between the shield seat and the
  bank seat.

## 2. The proposal: two systems, not four

**Performers are the orbs. Fanfare is the Focus.**

- **Performers.** The stage keeps its three seats. A performer acts at the
  end of every turn, and when a summon finds the stage full, the front
  performer Bows: it acts once more and leaves. That is Defect's channel and
  evoke, and it is what the stage already does. The Salon trio and the
  guests become the **same kind of thing**: a guest is a rarer, stronger
  performer, the way Plasma and Dark are rarer orbs. **Performers have no
  bars and take no hits.** A cast you do not recast stays on stage all
  fight, so "keep a party alive onstage" becomes the default rather than a
  feeding chore.
- **Fanfare.** One number on Furina, as in Genshin, where Fanfare is a
  single stack. It does two jobs, and they pull against each other on
  purpose:
  1. **It scales every act**, as Focus scales every orb. Every performer's
     number goes up by 1 for each point of Fanfare. Area acts get a smaller
     rate, which the sim sets.
  2. **It pays her Spend modes.** "Spend 3: deal 13 instead" takes 3 from
     the same number.

  So the decision every turn is to hold applause to make the whole stage
  stronger, or to cash it for a burst now. Holding has a cost, which is the
  burst you did not take, so **the fade is retired**.

How this answers [USER]'s list:

| Mechanic | Becomes |
|---|---|
| Salon orbs | kept as the stage's floor |
| guest pets | performers too; one of each, as now |
| Fanfare | Furina's one number: scaling and Spend currency |
| three HP bars | retired, along with the shield, the bank, absorption and the fade |
| the missing scaling | Fanfare itself |

**What keeps her from being Defect in a dress.**

- The Spend trade-off, which Defect never faces: Focus is never cashed.
- Every leaving performer acts once more, and each one is a named character
  with its own act and element.
- Hydro plus guest elements, which means reactions.
- The Solo path (Solo Verse, Soliloquy, One-Woman Show), where an empty
  stage is a choice.

Genshin's "Fanfare rises when the party's HP changes" stays available as a
Power. It is not a base rule (pick 4).

**Defence** becomes Usher's act, which now scales, plus her Block cards. The
Necrobinder comparison goes away with the bars, so the bars have no job left.

## 3. Alternatives considered

- **B. Trio only.** Keep the bars, cut the guests, and add Fanfare scaling
  to the acts. This is the smaller change, but the four-jobs problem stays
  with three jobs, and losing the guests throws out [USER]'s stated vision
  ("allow for character-effect cards to reach the Stage").
- **C. Guests only, Osty-style.** One guest on stage at a time with a bar,
  and the trio as plain cards. This loses the Defect chassis the kit was
  built on, and it puts the Necrobinder overlap at its sharpest.

## 4. What it costs

- **Pool.** Most of the 30 bar-reading rows become "Gain N Fanfare" or read
  Fanfare directly (Ousia Surge, Leading Lady and Pneuma Refrain already
  read it per point). Several cards lose their premise and need rework:
  - the seat-arranging family (seat order now decides only who Bows next);
  - Wriothesley, whose whole job was holding the front;
  - Sigewinne, the medic;
  - Counterclaim, Interposition, and Guest of Honor (co-op).

  The pool stays 78. Card numbers are mine at Prototype.
- **Starter.** Rising Applause ("Your back performer gains 5 Fanfare") has
  to change, and a starter change is [USER]'s (pick 3).
- **Engines.** The rules and the roughly 30-row rewrite go out as one batch
  in both engines. It is the biggest build since the Stage itself. No new
  art; the stage bodies lose their bars.
- **Proof.** A rule change, so [USER] plays and a two-seat round reads it.
  The sim gives the starting numbers: a Fanfare range of about 0 to 10 a
  fight, Spends at 2 to 4, Raise cards at 1 to 3, and the act rates.
- **Already built today, and kept:** Tutti! at 1 and Gala Premiere at 1. The
  decay timing change becomes moot once the fade is retired. Critics'
  Darling takes [USER]'s idea in the batch: "Whenever your Fanfare changes,
  deal that much damage to a random enemy."

## Picks

1. **Re-found on two systems.** Performers are orbs with no bars. Fanfare
   is Furina's one number: it scales every act and pays her Spends. The
   bars, absorption, the shield and bank roles, and the fade are retired.
   Default: yes. (Or B, trio only; or C, guests only. See sec.3.)
2. **Guests stay, as performers** (one of each, rarer and stronger than the
   trio), or they are cut. Default: they stay.
3. **Starter: Rising Applause becomes "Gain 3 Fanfare."** It keeps cost 1,
   and the upgrade gives 4. Default: yes.
4. **Where Fanfare comes from:** her cards and Powers only (default), or
   also a base rule "Whenever you lose HP, gain 1 Fanfare" (Genshin's
   drain). The default keeps the drain as a Power a deck can draft.
