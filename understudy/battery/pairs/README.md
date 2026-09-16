# Matched-telegraph pairs — the fixture, and what is OWED (`EB-212`)

R223's `intent` category is SELF-REPORT: `qualify.score_intent` passes any
form whose question four is not a flat *no*, so a seat that learns to answer
*yes* passes it without the telegraph ever entering its line.

`qualify.score_intent_pair` is the answer: **two packets identical but for the
enemy intent**, read blind, scored on whether the seat's two LINES DIFFER. An
identical line across the pair FAILS, and there is nothing to answer *yes* to
— the evidence is the play.

## What is here

One SYNTHETIC pair, `fixture-attack` and `fixture-block`, which exists to
exercise the scorer and its guard in CI and **is not a battery item**. The two
packets differ on exactly one line — the `- Intent:` line — which is the
condition `pair_differences` enforces.

## What is OWED, and it is game time

**No telegraph-only pair exists in the sealed record.** Every matched pair
this funnel has run differs in the ARM under test, not in the telegraph, which
is why `qualify.py`'s header has said since R223 that the category is scored
one board at a time. Staging real pairs means staging one board twice with the
enemy's intent as the only difference, and that is a launch and a round's
game time — not this row's.

Until they exist the shipped `battery.yaml` carries **no `intent_pairs:`
section**, `qualify.load_pairs` reads an empty list off it, and every
scorecard says so in `intent_pairs.owed`. When they are staged, add them:

```yaml
intent_pairs:
  - {id: P1, left: <turn-id>, right: <turn-id>, why: "..."}
```

and the mark they are scored against stays [USER]'s to move.
