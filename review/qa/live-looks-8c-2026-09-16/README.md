# Live looks 8c frames — 2026-09-16

Material for a person to look at, taken off the running game on **lane 0**
(port 15526, the owner's profile) against the installed build
`0.2.3480+proto.dirty`, arms `klee,companion,kokomi,furina-stage,teyvat`.
Every frame was captured **by pid** through `understudy.frames`
(`PrintWindow`), never by image name, so none of them can be another lane's
window. `frames-manifest.jsonl` carries one row per capture with its pid, its route and
its note. It is the literal capture log and has **seven** rows for **five**
committed files: it also records the two extra shop captures that were taken to
locate the portrait and not kept, and the `eb652-*` rows name the full-window
captures that the committed crops were cut from. No row was edited after the
fact; a row whose `path` no longer exists is a capture that happened and whose
bytes were not worth committing.

**GUARDRAIL.** A frame here is MATERIAL, not evidence. Nothing a bot or an LLM
derives from one is a claim about look, legibility, readability or fun — those
stay [USER]-only instruments (Guardrail-7, and the no-fun rule). The only
claims the record makes off these frames are mechanical: this region changed;
this region contains no character.

The record these belong to is
[`review/records/live-looks-8c-2026-09-16.md`](../../records/live-looks-8c-2026-09-16.md).

| frame | what it is |
|---|---|
| `eb38-shop-screen-no-portrait.png` | `EB-38`, shop half. The shop at act 1 floor 6, downscaled to 1600px. It is here to show what the screen IS: shelf, prices, relics and cave wall, and **no character portrait anywhere in the window**. The only thing that moves between two frames 0.6 s apart is a lantern flame on the wall left of the shelf. The shop half of the row is NOT DONE and this frame is the reason, not the answer. |
| `eb652-w1-standing-panel.png` | `EB-652` capture window 1 — the Salon panel standing, three chips, nothing under the cursor. The baseline the three hovers are read against. |
| `eb652-w2-hover-companion.png` | `EB-652` capture window 2 — `KLEEMOD-CHEVREUSE_INTERDICTION_FIRE` (a Companion) under the cursor. The row expects the front chip's word to turn FRONT → PERFORMS. |
| `eb652-w3-hover-deploy-full-stage.png` | `EB-652` capture window 3 — `KLEEMOD-SALON_DEBUT` (a Deploy) under the cursor on a FULL stage. The row expects LEAVES on the front chip and a bright footer. |
| `eb652-w4-hover-spotlight.png` | `EB-652` capture window 4 — `KLEEMOD-ETHEREAL_SPOTLIGHT` under the cursor. The row expects the pips it would spend to be tinted. |

The four `eb652-*` frames are **crops** of the full window, to the panel band
(x 700–1700, y 1700–2160 of a 3841x2160 capture), because the panel is what the
row is about and a full frame is eight times the bytes. Each was taken 4 s into
its own capture window, triggered off the bridge's own `debug_state: hover`
line, so each is tied to the hover it names. **Read the record's `EB-652`
section before reading them**: the card hand is missing from every frame this
job captured, so the captured rectangle does not reach the bottom of the game's
UI, and a panel footer drawn below the `0` bar would be outside these crops and
outside the frames they were cut from.
