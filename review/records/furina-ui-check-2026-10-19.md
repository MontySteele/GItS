# Furina UI check, 2026-10-19

Build: main 0.2.6058 (release build). Two Sonnet 5.5 seats, whole runs, A0,
suite seeds; each record adds a section on what the screen left unclear about
her HP. Frames: 16 shots, one every 4 minutes per lane, kept in the session
scratchpad (`furina-ui/frames`, not committed). Raw records gitignored.

| Seed | End | Bosses beaten |
|---|---|---|
| 30KMHAVG9SMQ (lane 1) | floor 43, Soul Nexus (act 3 elite), 1 HP short | Soul Fysh, The Insatiable |
| DJCAV76ZKAUN (lane 2) | floor 33, Kaiser Crab (act 2 boss) | act 1 boss |

## What played well

- Ordering: Drain cards first, then Rising Applause+ or Let the People
  Rejoice+ turning the lost HP into one hit (six fights ended this way in
  lane 1; exact lethal off 123 Fanfare).
- Lyney re-seeding Pyro each turn into Vaporize; the reaction preview line
  ("Vaporize ... lands 28") was read before every such play.
- Kaiser Crab's back-attack was the best problem of lane 2's run.

## What did not: her HP on the screen

Both seats, independently:

1. **The refund after combat is never previewed.** Lane 2 saw "you would be
   at 0/85" on a turn it would have survived after the refund, and "Drained
   22 HP returned" (17 to 39) only after the fight. A "returns after combat: N"
   figure would have changed plays in two fights.
2. **A Drain card's HP cost is not on the card.** Curtain Rise, Grand Deluge,
   Crabaletta, Gentilhomme Usher show their Drain, not what it costs her; no
   turn total of drains (Regina, Lyney, Deluge ...) before End Turn. Lane 1:
   only Grand Deluge and Coup de Théâtre say whether a drain is inside or past
   the Drain buffer.
3. **The HP change line disagrees with the header.** "HP A -> B, down 3"
   counts the drain only; the header already includes Repay and Regina's
   start-of-turn drain. After a fight, Drain returned is netted against Drain
   paid.
4. **Unexplained costs and numbers:** Critics' Darling and Crescendo+ cost HP
   with no reason on the card; Facade+ ("HP you have lost this combat") gave
   3 Block, then 12, and lane 2 could not tell net from total and stopped
   trusting it.
5. Lane 1 could not tell whether Salon Solitaire's end-of-turn Repay lands
   before the enemy's hit, on the turn it died by 1 HP.

Weak or dead: Ousia Pledge, Critics' Darling, Grand Entrance, Commanding Gaze.

## What to change

Her HP-legibility pass (`STATE.md`, Furina, Next) takes items 1 to 5 as its
brief: a returns-after-combat figure, each Drain card's cost and buffer state
on its face, one HP-change line that matches the header, and Facade's count
named. Her starter pick comes back with it.
