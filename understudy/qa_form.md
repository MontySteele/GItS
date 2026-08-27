# The four-question play form (EB-149; R213's "Play form")

One staged turn, one form, one grader. The four questions are R213's, verbatim:

1. **What did you play?**
2. **What other line did you seriously consider?**
3. **What did your chosen line give up?**
4. **Would a different enemy intent have changed it?**

The form is a **falsifier**, not a score. Nobody is asked whether the turn is
good, interesting or fun, and no answer here rates it. Two answers can refuse
the turn outright: a second question with no answer, and a fourth question
answered *no*. A refused turn never reaches [USER].

## The file a grader writes

JSON, one object. `python -m understudy.staged_turn grade <turn-id> <form.json>`
reads it.

```json
{
  "turn_id": "kokomi-first-turn-example",
  "packet_sha256": "the sha256 printed at the top of the packet's json",
  "grader": {
    "id": "opus-5",
    "kind": "llm",
    "model": "claude-opus-5",
    "designed_these_cards": false
  },
  "chosen_line": [
    {"card": "Bake-Kurage"},
    {"card": "Pearl Barrage", "target": "Jaw Worm"}
  ],
  "q1_what_did_you_play": "...",
  "q2_other_line_considered": "...",
  "q3_what_it_gave_up": "...",
  "q4_different_intent": "...",
  "q4_changed": true
}
```

## Every field, and why it is there

| field | what it is |
|---|---|
| `turn_id` | the id printed at the top of the packet |
| `packet_sha256` | the hash of the packet that was actually read. A form answered against a different packet is REFUSED — a turn re-staged is a different board |
| `grader.id` | the one string the ledger groups by. `user` is reserved for [USER]'s own cold play |
| `grader.kind` | `llm` or `user` |
| `grader.model` | the model that answered, so a verdict names who made it |
| `grader.designed_these_cards` | R213's first guard, declared rather than assumed. `true` REFUSES the form |
| `chosen_line` | the line played, in order, as **printed card titles** — the only spelling the grader was shown. `target` is an enemy's printed name, and is omitted for a card that needs none |
| `q1`–`q4` | the four answers, in prose |
| `q4_changed` | the fourth answer as a boolean, so a refusal cannot hinge on parsing prose. `false` REFUSES the form; so does a `q4` that reads as a flat "no" |

## What a refusal means

`grade` writes `review/qa/<turn-id>/verdict.json` and names the rule that
refused the turn. `SURVIVES` means **not yet falsified** — it is not a pass, a
score, or an opinion. A turn that survives goes to [USER] as a five-minute
puzzle; that is the next step, and the only one that reads anything into it.
