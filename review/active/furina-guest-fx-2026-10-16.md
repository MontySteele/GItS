# Furina's guest effects, 2026-10-16

This is Furina's plan item "guest-star pizazz" ([USER]: "unique particle effects or similar for each guest"). Until now, when a guest acted, the only things on screen were its lunge (`StagePerformerBeat`) and the damage number. Now each of the eleven guests also plays one short effect of its own. Every effect runs 0.5 to 0.7 s at 20 fps and plays on top of the lunge, at the moment the act lands. Each one is drawn the same way as the Spend, Drain and Repay effects: a colourless heat layer, tinted in the game from the mod's one element table (`ReactionFx.ElementFlashHex`). Nothing waits on an effect, so the rules never slow down for one. Headless, nothing plays.

## As built

| Guest | When | Where | Look | Colour | Length |
|---|---|---|---|---|---|
| Wriothesley | act (Cryo hit) | the target, at its feet | an upward shock (a flattened ring on the ground and five rising streaks), with six angular ice shards flung up and out | Cryo | 0.60 s |
| Lynette | act (Anemo hit) | the target | three swirl arms tightening onto the target and ending in a small flash, with three star sparkles | Anemo | 0.65 s |
| Clorinde | act (Electro hit) | the target | two crossing slashes cut one after the other (an X), then a flash and sparks at the cross | Electro | 0.55 s |
| Lyney | act (Pyro to ALL) | each enemy | six small playing cards flipping out from the centre, each trailing a flickering flame tip | Pyro | 0.70 s |
| Escoffier | act (Cryo to ALL) | each enemy, at its feet | a low ring of frosty steam puffs that widens and settles, with snow sparkles falling | Cryo | 0.70 s |
| Charlotte | act (Repay) | Furina | a camera flash: a white rectangular frame with corner brackets snaps in over a burst of light, then fades | white core, Cryo rim | 0.50 s |
| Sigewinne | act (Repay) | Furina | six bubbles rising, with one small heart-shaped sparkle at the top | Hydro | 0.70 s |
| Freminet | act (Block) | in front of Furina | a hexagonal ice plate flashes in and fades | Cryo | 0.60 s |
| Navia | her Spend discount applies | Navia | a spray of gold crystal shards and a few confetti bits | Geo gold `#ffd36b` | 0.60 s |
| Neuvillette | his bonus adds to a Hydro hit | the target | a thin water ring that widens fast, with a fainter second ring behind it | Hydro | 0.50 s |
| Chevreuse | her line fires (each Spend) | Chevreuse | a small crackle spark that re-strikes every two frames | Overloaded pink `#ff6fd0` (`ReactionFx.For(Overload)`) | 0.50 s |

Repeats play the effect again. Showstopper's second sweep, Bottled Encore, Encore!, Tutti!, a Bow and a repeat summon all run the act again, and so the effect too (`KleeTests/Prototype/FurinaGuestFxTests.cs`). An act to ALL plays one copy on each enemy. Full House's Spend is not an act, so it plays nothing extra. It does count as a Spend, though, so it fires Chevreuse's line and, on the turn's first Spend, Navia's discount.

**How it is built.** `tools/char_render/fx.py` draws the effects (`GUEST_EFFECTS`), and `pack.py --guest-fx-only` packs them into `furina_gfx_<name>.png` and the manifest's `guest_fx`. Neither needs a render. `tools/furina_rig/guest_fx.py` writes one `guest_fx_<name>.tscn` for each guest. `KleeMod.Vfx.FurinaGuestFx` (`Vfx/Prototype/`) loads that scene onto the creature and frees it when it ends. The hooks live on the game board: the act's lunge, the act's hit and the line's cue. Neuvillette's ring is hooked in the two places his bonus is added: guest and Power hits (`ElementalHit.Deal`) and her card hits (`FanfarePower.AfterDamageGiven`).

## What was not possible, or differs

- **Chevreuse** does have a runtime trigger: her line ("Whenever you Spend, apply 1 Vulnerable") fires on every Spend. Her spark plays there, not when she is summoned.
- **Navia's, Neuvillette's and Chevreuse's own acts** get no effect of their own beyond the lunge, as the table asks. There are two exceptions. Neuvillette's act is a Hydro hit to ALL, so his ring plays on each enemy. Navia's act Spends, so if that is the turn's first Spend, her discount spray plays.
- **Freminet's plate** always stands to Furina's right. If she is turned the other way, it does not flip.
- **Texture cost:** the eleven sheets add 13.9 Mpx (her own 13 sheets are 29.7 Mpx), imported VRAM-compressed like her other sheets.
- **Not seen in motion in the game.** No deploy was made. The in-game check is now part of the Furina model-art line in `BACKLOG.md`.

**Review sheet:** `review/qa/furina-guest-fx-2026-10-16/sheet.png`. It has one row per guest with six key frames each, at game scale on a dark backdrop. A red tick marks where each effect is anchored. `review/qa/` is gitignored, like the 2026-10-13 sheets, so the sheet is not committed. To redraw it, run `pack.py --char furina --guest-fx-sheet <png>`.

## Picks
1. **The guest effects.**
   - **(a) Default:** keep them as built; look at them in motion on the next deploy and name any to change.
   - (b) Change named effects before they ship.
   - (c) Drop them.
