# EB-788 — the capture that was two thirds of a picture (2026-09-16)

Two frames of one moment, on **lane 1** (port 15527, disposable profile,
`pid 38388`, build `0.2.3480+proto.dirty`), taken seconds apart through
`understudy.frames` **by pid** — before the fix and after it. Both are
downscaled to 1280x720 from the 3841x2160 capture, which is the same thing
`live-looks-8c` did and for the same reason: the defect is visible at a third
of the size and the bytes are not.

**GUARDRAIL.** A frame here is MATERIAL, not evidence. Nothing a bot or an LLM
derives from one is a claim about look, legibility, readability or fun — those
stay [USER]-only instruments (Guardrail-7, and the no-fun rule). The only
claims made off these two are mechanical: this region is in the frame, that one
is not.

| frame | what it is |
|---|---|
| `before-printwindow-clipped.png` | The capture as `EB-788` found it. Act 1 floor 2, Klee, round 2. The HUD bar and the player render; **there is no hand**, the right-hand HUD buttons are gone, and of the two Corpse Slugs only a sliver of one reaches the right edge. |
| `after-printwindow-whole-client.png` | The same combat, same pid, same `printwindow` route, after the fix. The hand reads **Defend, Strike, Defend, Defend** — which is exactly what `blindplay observe` reported off the wire for that turn — with both Corpse Slugs (20/26 and 3/27) and their intents, the energy orb at 3/3, draw 1 / discard 6, and `End Turn 2`. |

## What the two frames are of

The window's client rectangle is **3841x2160**. `PrintWindow` renders the
window at **5762x3240** — exactly 1.5x — and a client-sized bitmap clips
everything past that, which on a 16:9 screen is the bottom strip (the hand) and
the right strip (the enemies). The before frame is the top-left two thirds of
the game, upscaled by nothing and cropped by silence: `PrintWindow` returned
true, the bitmap was the size the manifest claimed, and the surface was not
blank, so no check in the apparatus had anything to fail on.

The after frame is the same render, measured rather than clipped, and resampled
back down to the client size. Its manifest row carries the measurement:

```
"size": "3841 2160", "client_size": "3841 2160", "render_extent": "5762 3240",
"render_scale": [1.5001, 1.5], "complete": true
```

**Where the 1.5 comes from is not settled, and the fix does not depend on it.**
It is not the obvious suspect: the capture host is per-monitor-v2 aware
(checked — `SetProcessDpiAwarenessContext(-4)` returns true), and
`GetDpiForWindow`, `GetDpiForSystem` and the screen's `LOGPIXELSX` all read
**288** on this machine, so window-over-system DPI is 1.0 and would predict no
scaling at all. So the factor is measured every capture and written onto the
row, rather than derived from a formula that holds here and nowhere else.

The record this belongs to is the `EB-788` row in
[`BACKLOG.md`](../../../docs/current/BACKLOG.md).
