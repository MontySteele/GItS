# Furina review: Drain, Spend and the guest-star style, 2026-10-12

This is the Furina half of the review you asked for after the two take-rate waves. Your agenda:
- "where her damage comes from, with tension regarding Fanfare spend ... the simplest knob to turn is going to be how big her Drain floor ought to be, and what her Fanfare Spend looks like";
- "She's supposed to feel like a character that swings her HP around violently but gets rewarded for it, with distinct styles centering on her as the prima donna of the stage vs her guest stars";
- on the floor: "I'm fine with increasing the Drain limit to 1/3 or 1/2 if we want to, but it sounds like that's not really the issue."

**Evidence.** The packet is `scratchpad/furina-review/packet.md` (gitignored). It covers:
- 65 Furina runs since 2026-10-09, from telemetry and the records;
- your human run;
- the base five's fights since 2026-10-05, through `tools/telemetry_report.py` and `tools/offer_report.py`.

Wave 2 (build 0.2.5032) is only 6 runs. Where a number comes from that wave alone, I say so.

## Where she stands

- **She wins more than the base five do under the same seats.** She won 12 of 65 runs, and 6 of 20 in the whole-run rounds 1 to 5. The base five went 0 of 5 at A0, all dying in act 3 (`base-five-baseline-2026-10-05.md`). The last three rounds went 1 of 2, 0 of 4 and 1 of 6, on small samples.
- **Her damage matches base and outgrows it late.** Normal fights, damage a turn, acts 1 to 3: 19.5, 30.2 and 49.2, against base 19.0, 29.5 and 37.8.
- **She swings her HP as intended.** In normal fights she loses 1.24 to 1.56 times base HP inside the fight. After drained HP returns at the end of combat, her net loss is about base: 6.4, 15.4 and 5.5% against 5.9, 13.7 and 2.5%. That is your design working: she swings violently and gets most of it back.
- **Her wall is the act-2 boss, as for everyone.** 18 of her 50 deaths came there, and 10 more at act-2 elites.

## 1. The Drain floor is not what kills her

The buffer, a quarter of Max HP (19 at 78), almost never runs out:
- it emptied in 7 of 99 fights in wave 2;
- elites and bosses use a median 10 to 13 HP of it;
- HP lost past the line averages 1 to 2 a fight.

Her deaths are enemy hits:
- in 47 of 50, the final turn showed incoming damage at or above her HP;
- the median was 9 HP against 28 incoming.

Raising the buffer to a third (26 HP) would refund more after fights she already survives, and would change none of those deaths. **Leave it at a quarter.** That's pick 1, as you suspected.

## 2. The bank with no Block

The real pattern is the one the wave-2 seat put in words: Fanfare "pays out as damage but not as survival."
- Median Fanfare left at death is 21; 10 deaths held 30 or more, and 8 held 50 or more.
- Two of wave 2's five deaths held 59 and 72.
- Her Block against incoming per turn matches base (0.4 to 0.6 for both), so she isn't Block-poor overall. She is Block-poor **in the turn the bank should save her**.

The two cards that turn the bank into Block are taken:
- Hold the Stage, 21 of 42 (50%), the best Block per play in her pool at 14.7;
- Packed House, 2 of 10 since it became Block.

Hold the Stage is an Uncommon, so most decks never see it before the act-2 boss. The Common that should do this job, Bubble Aria ("Gain 6 Block. Spend 3: also draw 2 cards"), spends Fanfare on cards, not on survival, and is taken 25%.

**Proposal (pick 2):**
- Bubble Aria becomes a Common Hold the Stage at half the cap: "Gain 6 [8] Block. Spend up to 8: gain 1 more for each." Its most is 14, against Hold the Stage's 22. It also drops the draw, which your new rule on Commons asks for anyway.
- Packed House reads "plus 1 for every 3 Fanfare you have", up from 4. At the median death bank of 21, that gives 7 Block on top of 5.

## 3. The Spend shape is fine

- Spend cards make 21 to 35% of her damage, more in elite and boss fights.
- The raised caps landed: Spirited Aria hit its cap with Fanfare left on 8 of 19 plays, down from 11 of 17.
- Bravura or the Spend core appears in most wins.
- The unspent third, 31% of Fanfare, sits mostly in hoard decks, which keep it on purpose (Prima Donna, Star Turn).

**No change.**

## 4. The guest-star style doesn't get drafted

This is the gap between what you want and what plays. Your two styles:
- **(1) Furina hits and the stars support.** It is alive. Bravura, Headliner and Leading Lady appear in 7 of 12 wins.
- **(2) The stars are the main offense.** It shows up in one run: yours.
  - Your win had 52% of its damage from guests: Lyney 24, Charlotte 19 and Neuvillette 17 summons, and Showstopper played 14 times.
  - In every other win, guests did 0 to 19%.
  - Since 2026-10-09, the seats have almost never drafted the company cards:

| Card | Text | Taken |
|---|---|---|
| Encore! (Common, 0) | Spend 4. Your oldest guest acts. Draw 1 card. | 5 of 99 |
| Tutti! (Common, 1) | Each guest acts. Draw 1 card. | 2 of 43 |
| Final Bow (Uncommon) | Draw 1. A guest acts twice, then leaves. | 1 of 56 |
| Casting Call (Uncommon) | Put a Guest Star from your Draw Pile into your hand. | 0 of 27 |
| Ensemble Cast (Rare) | 4 guest seats; summon a random guest. | 0 of 23 |
| Showstopper (Rare) | End of turn, Spend 5: your guests act again. | 0 of 18 |

**Why:**
- A guest's act is small: Wriothesley 4, Chevreuse 4, Clorinde 6, Lyney 8 to ALL. Acts take no Strength.
- So a card that makes a guest act once more is worth about 4 to 8 damage.
- And a seat holds only one or two Guest Stars, so these cards have little to repeat.

Your run had three guests on stage most fights, and that's when the style works. The fix is to make each guest worth seating, so decks seat more of them. The Rare payoffs then have something to multiply.

**Proposal (pick 3):**
- **Every damaging guest act +2:**
  - Wriothesley 6 [9];
  - Chevreuse 6;
  - Lynette 5 [8];
  - Clorinde 8 [11];
  - Lyney 10 [13] to ALL;
  - Escoffier 6 [8] to ALL.
- **Freminet's act Block +2:** 5 [8].
- **Repay acts unchanged:** Charlotte and Sigewinne.
- **Encore!:** "Your oldest guest acts." It costs 0 [Retain] and no longer Spends or draws. It stops competing with her own Spend, and there's no cycling at Common.
- **Tutti!:** its upgrade draws 2 instead of costing 0, so an upgraded copy doesn't become a 0-cost cycler.
- **The Rares (Showstopper, Ensemble Cast) stay as they are.** They are payoffs, and they should come alive once decks hold three guests. They're re-read after the next round.

**Not proposed:** cutting anything. A few cards were 0 of 4 to 7 in wave 2 alone: Undercurrent, All In, Interval Bell, Star Turn, High Stakes, Rising Tide, Private Box and Fountain of Lucine. One wave is too small a sample, so they stay on the watch list.

## For [USER]

1. **Drain buffer.**
   - **(a) Default:** stays at a quarter of Max HP.
   - (b) A third.
2. **Bank-to-Block on a Common.**
   - **(a) Default:** Bubble Aria becomes "Gain 6 [8] Block. Spend up to 8: gain 1 more for each"; Packed House counts every 3 Fanfare.
   - (b) Packed House only.
   - (c) No change: she already wins more than base.
3. **The guest-star style.**
   - **(a) Default:** guest acts +2, Encore! and Tutti! as above.
   - (b) Acts only.
   - (c) Wait for another round first.

After the build, a two-seat Furina round reads picks 2 and 3. The guest-damage share is the number to watch.
