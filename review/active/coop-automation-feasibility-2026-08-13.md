# Can we drive a two-seat co-op game? — a one-page feasibility note

**For [USER], as the input to the P3 decision. Nothing was adopted, nothing
was installed, no soak was run, and the HOLD is untouched.**

Your P0 ruling put LocalCoop (`STS2CouchCoop`) on **HOLD for P3**: do not
adopt, do not install, do not fork yet, and let one experiment be the gate —
*boot two clients, attach zero controllers, and see whether the bridge can
ready up both seats.* This note does the evaluation that ruling anticipated,
and reports why the boot itself was **not attempted tonight**.

## The short version

There is a blocker nobody had found yet, it is on our side rather than
LocalCoop's, and it is cheap to fix — but it has to be fixed *before* the
gating experiment can even be attempted, because without it the experiment
cannot produce an answer either way.

**Two game clients on one machine cannot both serve the bridge.** The
vendored STS2MCP binds a fixed HTTP port (`15526` by default) and reads that
port from `STS2_MCP.conf` **inside the mod directory**. Two clients launched
from one game install read the *same* mod directory, so they get the *same*
port, and the second one's `HttpListener` loses the bind. Our harness makes
it worse in the same direction: `understudy/bridge.py` hardcodes
`http://localhost:15526`, so it has no way to address a second seat even if
one existed.

So the honest state of the P3 gate is: the experiment your ruling names is
**not yet runnable**, and the reason is ours.

## What is genuinely fine, from reading the source

Everything the P0 pass established still holds and none of it is the problem:

- **Version.** LocalCoop 0.1.2 is built and tested on STS2 **v0.107.1** — our
  exact build. The stale "v0.103.3" prose was the README, not the mod.
- **Steam networking.** Genuinely bypassed. LocalCoop substitutes the
  lobby/net service and runs its own loopback TCP broker; the patch names say
  so plainly. Nothing tunnels over Steam.
- **Input.** A bot seat needs no controller. The bridge's multiplayer verbs
  enqueue actions directly and never touch the input stack.
- **Our own multiplayer verbs exist** (`McpMod.MultiplayerActions.cs`,
  `McpMod.MultiplayerState.cs`) and are what a second seat would be driven
  through.

The open question the P0 pass could not answer is still open and still the
right question: whether LocalCoop's seat-ownership model, which is built
around Steam Input's controller slots, will grant a seat to a client with no
input device at all.

## Why I did not boot it tonight

Four reasons, in order of weight:

1. **The port collision above makes the experiment unanswerable.** Two
   clients would boot, one bridge would answer, and "the second seat never
   readied" would be indistinguishable from "the second seat has no bridge".
   That is a result nobody could act on.
2. **Installing it means writing into the live game directory** while an
   unattended soak is scheduled to run in that same directory tonight. The
   install itself is reversible — it is a folder under `mods/` — but a
   Harmony mod that *substitutes the lobby and net service* is not a change
   whose blast radius stops at its own folder, and the soak's own
   reversibility ledger would have no row for it.
3. **It needs a second Steam profile**, which is not mine to create.
4. **The HOLD says do not install.** With the experiment unanswerable anyway,
   there is no reading of tonight under which installing it is the right call.

## What would make the gate runnable — the actual ask

Small, all on our side, none of it adopting anything:

1. **Let the bridge's port be set per process.** An environment variable read
   before the config file (config stays the fallback) is a few lines in the
   vendored `McpMod.cs`, under PROVENANCE discipline. Then two clients from
   one install can serve `15526` and `15527`.
2. **Let the harness address a chosen port** — `bridge.BASE` becomes a
   parameter rather than a constant.
3. **Then, and only then, run your experiment**: two clients, zero
   controllers, and ask each bridge whether its seat can ready up.

Steps 1 and 2 are worth doing on their own merits: they are also what any
future side-by-side of two builds on one machine would need.

## The recommendation

**Keep the HOLD.** Nothing found here argues for adopting LocalCoop, and one
thing argues against attempting the gate yet. If you want P3 to move, the
cheapest next step is the two-line port change above — after which the single
experiment your ruling already named becomes a thing that can be run in one
sitting, and its answer will mean something.

*(Scope note: none of this touches the co-op reaction-potency watch item `W3`,
or the standing fact that co-op defects are play-derived because tier 0.5
models one seat.)*
