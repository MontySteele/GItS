Status: RECORD (EB-758/763 deploy proofs and the EB-762 fairness read; feasibility only, nothing measured)

# The music goes quiet, the boot gets a budget, and the coin is a coin

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
The statistics below are sanity arithmetic on a feasibility read, not a result.

**Installed.** `deploy_round.py --arms klee,companion,kokomi,furina-stage,teyvat`. Read
back: **`0.2.3272+proto.dirty`**, bridge present at `mods\STS2_MCP`, 406 staged card
png(s). **The arm is ON in the installed build** — the next calibration deploy must turn
it off. Profile untouched.

## EB-758 — the music fall-through: MET

Acceptance: *"A dev deploy with the arm on and no track logs nothing from the music
patches across a three-fight soak."*

`--runs 1 --character KLEEMOD-KLEE --max-fights 3` → **`bounded seed=0QWH9S4WQAUA
actions=65 fights=3 defects=0`** on `Version=0.2.3272.0`. Grepping that launch's
`godot.log` for `TeyvatMusic`, `NRunMusicController`, `res://teyvat/music` and
`Couldn't open directory` gives **0 lines** — where the same grep gave an engine ERROR
and a 31-frame backtrace per `UpdateMusic` two builds ago. The path was exercised, not
skipped: the run logged four `Preloading 'Act=MONDSTADT'` (run start and act start both
route through `UpdateMusic`). **Met verbatim.**

## EB-763 — the menu-ready budget: MET, and the stall is not gone

Acceptance: *"A soak on this profile boots without the timeout and the warning names the
count."*

The WARN prints **before** the launch and names the count:

```
WARN lane lane0: the profile's run-history store holds 1229 files (50.2 MB) and the game
rewrites all of it at boot; menu-ready wait raised 180s -> 426s. Nothing here deletes it
(EB-763).
```

1229 is high hundreds and then some — not the `0` a missed glob would give — and it
matches `min(900, 180 + N/5)`: `180 + 1229/5 = 425.8 → 426`. The soak booted well inside
it; the whole three-fight soak took **82 s** wall clock end to end.

**The cost line, disclosed rather than buried.** Over the 30 launches this record cost,
boot was **min 18.8 s, max 26.2 s, mean 22.3 s** on the 24 that worked — and **6 attempts
still exceeded the raised 426-428 s wait entirely**. So the budget is correctly sized and
correctly announced, and the underlying stall is intermittent and not fixed by sizing the
wait. The store also grows by one file per embark (1229 → 1238 across this record), so a
long unattended batch makes its own weather. The acceptance is about the soak, and the
soak met it; this paragraph is the part the row does not ask about.

## EB-762 — the act-1 coin: FAIR, on 24 embarks, and the suspect is ruled out

Acceptance: *"A record stating fair or not with the mechanism named; nothing on it
quotable."*

**One process per embark, and the brief's "one process" is not reachable.** The wire has
no in-run exit: `soak_navigate.RunDriver._to_main_menu` raises on any non-menu screen
("Get to the menu the only way the wire offers: there is none"), and `abandon_run` is a
main-menu option. Measured rather than assumed — a second `_embark` in one process failed
**23 times out of 23** with `unexpected_start_state: found 'event'` (Neow). So each embark
is its own launch, which is what the soak does between runs.

**Discovery state, read off `…\modded\profile1\saves\progress.save` (`discovered_acts`):**

- **before:** `['ACT.OVERGROWTH', 'ACT.UNDERDOCKS', 'ACT.HIVE', 'ACT.GLORY', 'ACT.MONDSTADT', 'ACT.LIYUE']`
- **after:** identical — unchanged across all 24.

Both dressings were already discovered going in, so nothing could turn on discovering one.

**The ordered tally, 24 embarks:**

```
L L M L L M M L L M M M M M L M L L L L M L L L
```

- **MONDSTADT 10, LIYUE 14**; two-sided binomial **p = 0.54**.
- **11 runs, 10 switches.** A fair coin at this split expects **12.67 runs (sd 2.33)**;
  observed 11 is **z = −0.72**.

Neither the balance nor the ordering gives any reason to doubt a fair coin.

**The mechanism, and the suspect is ruled out on the code rather than on the data.**
EB-762 named `ActModel.cs:563` — the branch that FORCES a *non-default*, unlocked,
*undiscovered* act past the roll on a single-player run. It cannot fire for either
dressing at all: `Mondstadt.IsDefault => true` and `Liyue.IsDefault => true`
(`Acts/Mondstadt.cs:177`, `Acts/Liyue.cs:76`), both `IsUnlocked => true`, and
Mondstadt's own doc-comment says that is exactly why — *"Marking both faces default keeps
the pair a genuine coin from the first run."* A default act is never forced, discovered or
not, so the branch was never able to produce the earlier ordering.

**Which leaves the earlier reading unexplained, and it should be said plainly.** The
14-embark sequence in `teyvat-spike-proofs-2026-09-15.md` (8 Mondstadt then 6 Liyue) was 2
runs against 7.86 expected, **z = −3.33** — it did look real. It is not reproduced here at
nearly twice the sample, the branch that would have explained it cannot fire, and I did
not record discovery state then, so I cannot test the discovery story retrospectively. The
honest reading is: the better-powered read says fair, the suspect is eliminated, and the
earlier order has no mechanism behind it that this record can find.

No row is retired here.
