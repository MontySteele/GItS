# Two game instances, one install — the platform evidence

**2026-08-29.** The experiment behind `EB-202`, run before any of the funnel
code existed. It answers one question and deliberately leaves one open.

## What was proved

Two `SlayTheSpire2.exe` processes run **side by side from the SAME Steam
install**:

- Steam initialises twice on one account. No "restart if necessary", no second
  library entry, no second copy of the game on disk.
- Setting the **`APPDATA`** environment variable per process gives each a
  fully separate `user://` tree — saves, settings, shader cache, `mod_configs`
  and logs. The trees do not see each other.
- **The mod profile loads only if `settings.save` is copied into the new tree
  first**, at `%APPDATA%\SlayTheSpire2\steam\<steamid>\settings.save`. Without
  it the second instance boots vanilla: a game with no klee mod in it, wearing
  the harness's name. `understudy/instances.seed_profile` is that copy, done
  once and never overwriting a lane's own file.
- **Cost: roughly 1.3 GiB of VRAM and 1 GB of RAM per extra instance.** Two is
  what was measured. Nothing here says three works.

`both-up.png` is the screenshot: both windows up, both at their own main menu.

## What was NOT proved, and what closed it

**The MCP bridge port.** The mod reads its listener port from
`STS2_MCP.conf`, which lives beside the mod dll — i.e. *inside the shared
game directory*. One conf is one port, so two listeners needed either two
installs or another port source. The experiment could not answer that and did
not try.

`EB-202` closed it with the third source rather than a second install:
`vendor/STS2_MCP/gits/GitsPort.cs` resolves the port **env > conf > default**
and logs which won, and `understudy/instances.py` sets `STS2_MCP_PORT` per
launched process. With the variable absent the conf behaviour is upstream's,
unchanged.

## Files

| File | Tracked | What it is |
|---|---|---|
| `both-up.png` | yes | both game windows up at once, from one install |
| `B-godot.log` | **no** | lane B's own `godot.log`, proving the log went to the second `APPDATA` tree. Left untracked: it is a 27 KB machine artifact, and the fact it carries is stated here. |

## The live proof, 2026-08-29

`live-proof.json` is the record; `understudy/twolane_proof.py` and
`twolane_frames.py` are the scripts that produced it.

- Both lanes up in **30.6 s**, both bridges answering `menu` at once on
  **15526** and **15527**, each on its own pid and its own `APPDATA`.
- One board staged **per lane, concurrently** — `kokomi-slice2-t01` on lane 0,
  `kokomi-slice2-t02` on lane 1 — and both packets read back with their own
  hashes, which is the check that says the boards did not cross.
- One frame per lane, captured **by pid**, with two identical game windows on
  the screen: `frame-*-eb202-lane0.png` and `frame-*-eb202-lane1.png`.
- Wall clock, two boards: **52.4 s concurrent vs 59.6 s serial on one lane**.
  The concurrent number carries a 37 s `EB-191` retry on lane 1; a stage that
  does not retry takes ~14 s on either lane.

Both games were closed by pid. What is NOT proven: a GRADED two-lane round —
no model, grade or replay ran here — and `EB-191` is unfixed and fires often
enough with two games on one machine to need a retry.

**One hazard the proof left behind, and put back.** Staging an EXISTING turn
id rewrites that turn's `review/qa/<id>/packet.*` in place. The proof re-staged
`kokomi-slice2-t01` and `-t02`, which overwrote slice 2's published packets
with a board off a different build (max HP 80 rather than 70, Bake Kurage in
the base kit). Both were reverted with `git checkout` and are byte-identical to
what slice 2 published; nothing here is a new reading of either turn. A future
throughput proof should stage a scratch turn id, not a graded one.
