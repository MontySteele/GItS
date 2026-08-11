# Un-modelled mechanics — the `SKIP-10.9` living skip list

> **Reference, not work.** This is the living list of mechanics the sim
> deliberately does not model, kept so a logged approximation never reads as an
> unlogged fake. An entry is **promoted to a BACKLOG item only when a pass
> needs it** — nothing here is scheduled, and nothing is tuned on the strength
> of being listed. (Ex-BACKLOG `SKIP-10.9`, routed here 2026-08-11; originally
> run-model-rework-plan §10.9, restored in full 2026-08-06 after the migration
> dropped ~14 entries — EB-29c.)

## Enemy mechanics

- Back Attack (Kaiser Crab)
- untargetable Burrow (Tunneler)
- Ethereal / Hex auras (Knight Gang)
- pick-your-poison curse choice (Knowledge Demon)
- damage caps (Hard to Kill / Plating / Hardened Shell)
- Artifact
- Thorns
- on-hit status injection
- every-N-cards cadence intents
- buff-all-enemies
- block-an-ally
- random-no-repeat AI
- self-stun
- Slimed self-exhaust
- the minor-power list (Imbalanced / Ringing / Paper Cuts / Stock / Galvanic /
  Rampart)
- Soul Siphon stat-theft class (the Matriarch's player-half drain landed with
  EB-25)
- the two Ancient relic hooks — Blessed Antler and Philosopher's Stone

## C#-side structures with no sim twin (EB-19)

- **Deferred-settle machinery** — `SpotlightSystem` PendingDraws /
  `CurtainCallPowers` NoteEncoreSpent / `FurinaResources` PendingDeltaBlock.
  Parity rests on every flush site being reached; a stranded draw is the
  failure mode.
- **Per-dealer reaction windows** — ruled co-op divergence (red-pen R1); solo
  is byte-identical.
