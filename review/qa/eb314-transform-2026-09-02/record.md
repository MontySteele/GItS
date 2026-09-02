# EB-314 — the blind render's transform screen, live on lane 1

A live read of the Neow "Transform 1 card" screen, taken to close `EB-314`'s
acceptance: *a scripted transform on lane 1 prints the source and result the
deck then shows.* It does now, with one correction the defect itself forced —
**the result is not printed at all, because at the moment the tester confirms,
the game has not chosen one.** That is stated on the page in words rather than
guessed at, and this record is the evidence for both halves.

Nothing here is a measurement. It is a lane-1 run, which is never a run of
record, and no number in it is comparable with anything.

## Identity

| | |
|---|---|
| Lane / port | lane 1, port 15527, `%LOCALAPPDATA%\gits-lanes\lane1` |
| Run seed | `GXRJRQVLUL1G`, read back off the wire (R95); chosen with `--seed` to reproduce the r5 seat's Neow offer |
| Character | Sangonomiya Kokomi (`KLEEMOD-KOKOMI`), Act 1 floor 1, ascension 3 |
| Deployed mod build | `0.2.2083+proto.dirty`, off `mods\klee\manifest.json` `version` |
| Game build | `v0.111.0`, off the game's own `release_info.json` `version` |
| Harness | `understudy.embark` / `understudy.blindplay` from the `transform-screen-2026-09-02` worktree; the game side is the main checkout's already-deployed package |
| Teardown | `python -m understudy.embark --teardown --lane 1`, all five ledger rows **REVERTED**; the shared `mods\STS2_MCP` was left in place (`EB-310`) and verified still on disk afterwards |

## What the screen actually does

Three raw wire envelopes are beside this file, captured with
`understudy.bridge.get_state()` and written out unedited:
`transform-fresh.json` (nothing picked), `transform-picked.json` (the preview
open) and `transform-picked-later.json` (**the same screen, one read later,
nothing touched in between**).

The two picked captures differ in exactly one card:

```
transform-picked        preview_cards = ['Strike', 'Tools of the Trade']
transform-picked-later  preview_cards = ['Strike', 'Fan of Knives']
```

with `cards` byte-identical between them, `selection_known: true`, and **no
grid card marked `selected` on either**.

The decompile of `v0.111.0` says why, and it is not a re-roll.
`NDeckTransformSelectScreen.OpenPreviewScreen` unhighlights every picked card
as it opens — which is why the grid's own selection channel goes empty — and
hands `NTransformPreview.Initialize` one `CardTransformation` per pick. Where
that transformation carries no `Replacement`, which is every *random*
transform and what the screen's own doc comment says the screen is FOR, the
preview starts `CycleThroughCards`: a loop that reassigns the right-hand
holder to another card out of `CardFactory.GetDefaultTransformationOptions`
**every 0.2 seconds**, on `Rng.Chaotic`, until the screen closes. It is an
animation. `CompleteSelection` then returns the SELECTED CARDS and the caller
rolls the replacement afterwards, so nothing the reel lands on is ever taken.

The r5 Opus seat's three "re-rolls" (Barricade → Dark Embrace → Hemokinesis)
were three frames of that reel, and what it confirmed was never on the screen.

## The page, before and after

Same fixture, `transform-picked.json`, rendered by the committed page.

**Before this row** — and read it twice, because the second read is the whole
defect:

```
## What you have picked

- **Strike** — cost 1, attack
    Deal 6 damage.
- **Tools of the Trade** — cost 1, power
    At the start of your turn, draw 1 card and discard 1 card.

Confirm is available.

You may skip this.
```

```
## What you have picked                     ← transform-picked-later.json,
                                              the SAME screen a moment on
- **Strike** — cost 1, attack
    Deal 6 damage.
- **Fan of Knives** — cost 2, power
    Shivs now hit ALL enemies. Add 4 Shivs into your Hand.
    *Shiv* — Deal 4 damage. Exhaust.
```

and `choose "Defend (1)"` over that open preview resolved `ok` and posted
`{"action": "select_card", "index": 4}` — changing which card the game would
transform without changing a word of what the tester was being shown.

**After:**

```
## What you have picked

- **Strike** — cost 1, attack
    Deal 6 damage.

*The card this becomes has NOT been chosen yet. This screen rolls it at random
when you confirm, and the card it is showing on the right is an animation
cycling through the possibilities several times a second — it is not the
result, so it is not printed here. Confirming means accepting an unknown
card.*

Confirm is available.

You may say `skip` to undo this pick and choose again; it does not leave the
screen.

## What you can say

- `confirm`
- `skip`
```

Both picked captures now render **the same page, byte for byte**. And the
command that used to go through is refused in words:

```
$ GITS_LANE=1 python -m understudy.blindplay act 'choose "Defend (1)"'
{
 "ok": false,
 "verb": "choose",
 "post": null,
 "printed": {},
 "refusal": "your pick is already made and this screen is showing it back to
             you; naming another card here would change what gets taken
             without changing what you are being shown. Say `confirm` to take
             it, or `skip` to put it back and choose again"
}
```

## The acceptance, live

The scripted transform, in order, all on lane 1:

1. `choose "New Leaf"` — the Neow boon, *Transform 1 card*.
2. The transform screen's grid, which is the deck: **Strike ×4, Defend ×4,
   Kurage's Oath (proto), Slack Water (proto)** — ten cards
   (`transform-fresh.json`).
3. `choose "Strike (1)"` → the preview opened; the page named **Strike** as
   the card going in and made no claim about what comes out.
4. Three raw reads of that unchanged screen: the reel showed *Tools of the
   Trade*, *Tools of the Trade*, *Fan of Knives*. The page did not move.
5. `choose "Defend (1)"` — **refused**, nothing posted (the re-selection that
   cost the r5 seat a Defend).
6. `confirm`, `proceed`, then into the first fight to read the deck back.

The deck after, off the combat wire (`player.hand` + `player.draw_pile`, the
piles being the whole ten-card deck on turn one):

```
hand       Defend, Defend, Defend, Strike, Kurage's Oath (proto)
draw_pile  Defend, Slack Water (proto), Strike, Strike, Shadowmeld
```

| | before | after |
|---|---|---|
| Strike | 4 | **3** |
| Defend | 4 | 4 |
| Kurage's Oath (proto) | 1 | 1 |
| Slack Water (proto) | 1 | 1 |
| Shadowmeld | — | **1** |

**The source the page printed is the card that left.** A Strike went, all four
Defends stayed, and the deck is still ten cards. The card that arrived is
**Shadowmeld** — neither of the two reel frames the wire showed, which is the
positive evidence that the reel is not the result and that a page printing one
would have been wrong again here.

## What this record does not carry

- **No bridge change.** Everything above is the deployed bridge's own wire,
  read differently. `_selectedCards` — the screen's real selection set — is
  not on the wire at all while a preview is open, and rather than add a read
  and be unable to deploy it, the page removes the way of getting the two out
  of step: the pick cannot be re-taken over an open preview, so the preview's
  own `%Before` half IS the game's selection, always.
- **No second-card case.** Every transform this repo has met takes one card,
  so the halves rule (`%Before` first, `%After` second, one holder each per
  pick) is exercised live at N=1 only. An N>1 preview is handled by the same
  rule and a preview that will not pair off at all names none of its cards
  and says so, rather than guessing.
- **No claim about the upgrade screen's result.** The campfire smith's second
  card is decided (`_singlePreview.Card` plus the game's own `+` face) and is
  still printed. Only the re-pick closed there, and for the sharper reason
  that `CompleteSelection` upgrades everything in `_selectedCards` — a second
  `choose` would have upgraded two cards on a one-card boon.
