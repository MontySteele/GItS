# The live screen shapes (`EB-262` / `EB-263`, round four)

Nine raw wire envelopes, captured off a real Klee run on 2026-09-02 against
the deployed `0.2.1966+proto.dirty` build, one per screen the round-three Opus
seat reported. They are the bytes `GET /api/v1/singleplayer/state` returned,
written out unedited; nothing was hand-shaped and nothing was trimmed.

## Why they exist

Both rows closed once already on SYNTHETIC fixtures built from the vendored
bridge's own builder, and both reopened on live evidence: *"Their fixtures
passed; the live shapes do not."* A fixture somebody wrote from a source file
is a statement about what the source says. These are a statement about what
the wire sends — which is the only thing the blind page ever reads.

## What is in each, and what it settled

| file | screen | the fact it carries |
|---|---|---|
| `shop-stocked.json` | a stocked shop | every card shelf carries `card_cost` (the card's ENERGY cost), which nothing read; the page printed the gold alone |
| `shop-bought.json` | the same shop, one card bought | the bought shelf is `{index, category, price, is_stocked: false, can_afford, on_sale}` and **nothing else** — no `card_name`, no `card_cost`. `MerchantCardEntry.IsStocked` IS `CreationResult != null`, so the purchase clears the only field the face was read from. The lost name is the GAME's, not ours |
| `rest-fresh.json` | a rest site with its choice untaken | two options (`Rest`, `Smith`), no card removal, and `can_proceed: false` |
| `rest-spent.json` | the same room, after resting | `{"options": [], "can_proceed": true}` — the room drops its options, and the page was advertising four verbs over them |
| `chest-opening.json` | a treasure room mid-open | `{"message": "Opening chest..."}` and no other key. `BuildTreasureState` force-clicks the chest itself and answers a bare message for the frames that takes; `relics` appears only once the relic collection is visible |
| `enchant-fresh.json` / `enchant-chosen.json` | the deck enchant picker, before and after a pick | the two differ in exactly ONE field, `can_confirm`. The card list is byte-identical and there is no `preview_cards`: the bridge carries **no per-card selection state** on this screen |
| `upgrade-fresh.json` / `upgrade-chosen.json` | the campfire smith picker, before and after a pick | the same screen family WITH an answer: a preview container opens, so `preview_showing` goes true and `preview_cards` holds the chosen card and its `+` face |

## Two things a reader should not mistake

**The card faces in these files are the DEPLOYED build's**, so several of them
print `{Block:diff()}` and `{PowerAmount:diff()}` raw — `Barbara — Melody
Loop` and `Kirara — Surprise Dispatch` on the shop shelves. That is `EB-285`
caught a second time, independently, on a screen nobody was looking at; it is
fixed in the generator in the same round, and these files keep the evidence.
The Bomb keyword tip in them still says the pre-round-four growth number for
the same reason.

**No capture shows a chest with its relics up.** Four runs were driven and
every treasure room was read mid-open; the runs ended before another came
round. The opening frame is the one the seat reported and the one that is
fixed (it is a transient now, so a live read waits it out), but the settled
chest is still covered only by the synthetic fixture in
`tier0/tests/test_understudy_blindplay.py`.

## How they were captured

`python -m understudy.embark --character KLEEMOD-KLEE` to open a run, a
throwaway driver that posted `understudy.blindplay.act`'s own resolutions and
wrote `understudy.bridge.get_state()` at each screen, then
`python -m understudy.embark --teardown` — whose ledger read REVERTED on all
four rows. Nothing was deployed, no soak was run, and nothing here is a
measurement: these are shapes, not numbers.
