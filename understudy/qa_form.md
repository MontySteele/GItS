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
    {"card": "Pearl Barrage", "target": "Jaw Worm", "exhaust": "Coral Guard"},
    {"card": "Itto - Oni Rush", "choose": "Deal 14 damage"}
  ],
  "q1_what_did_you_play": "...",
  "q2_other_line_considered": "...",
  "q3_what_it_gave_up": "...",
  "q4_different_intent": "...",
  "q4_changed": true,
  "forecast": ["0", "3", "0"]
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
| `exhaust` | optional, per play: if the card asked which card to **Exhaust**, the printed title of the one chosen |
| `choose` | optional, per play: if the card asked to **choose one**, the printed text of the option taken, exactly as the card prints it (`"Deal 14 damage"`) |
| `q1`–`q4` | the four answers, in prose |
| `q4_changed` | the fourth answer as a boolean, so a refusal cannot hinge on parsing prose. `false` REFUSES the form; so does a `q4` that reads as a flat "no" |
| `forecast` | OPTIONAL, and required only where the packet printed a **Before you decide** block. One answer per numbered question, in that order, written **before** the line is chosen. A board that asks and gets fewer answers than questions is REFUSED `forecast_missing` |

## The forecast, where a board asks for one (`EB-236` (d), `EB-229`'s twin)

The four questions above are all **past tense**: they ask what you played and
what you gave up. A registration that wants to know what a reader **expected**
has nowhere to put it, and that is why `KURAGEMEM002` graded three of its
slots UNREACHED — not because the display failed, but because the question was
never asked.

So a board may register a short list of questions, printed at the **top** of
the packet under **Before you decide**, numbered. Answer them there and then,
before you settle on a line, and write the answers into `forecast` in the same
order — one entry per question, a bare number where the question asks for one.
A forecast collected after the line is a rationalisation, which is the whole
reason for the position on the page.

Most boards ask for none, print no such block, and are graded exactly as they
always were.

A line is **replayed on the live game** after it is graded, so a choice the
form does not state is a choice the replayer cannot make: it stops at the
prompt and records `modal_unanswered` rather than guessing. That is the whole
reason for the two optional keys.

## What a refusal means

`grade` writes `review/qa/<turn-id>/verdict.json` and names the rule that
refused the turn. `SURVIVES` means **not yet falsified** — it is not a pass, a
score, or an opinion. A turn that survives has its line **replayed live** on
the staged board — the grader's arithmetic set against what the game actually
did — and then goes to the seat's pair read, which RETURNS an arm or ADVANCES
it. **[USER] plays no forms and no turns during iteration** (R217 A); a
SURVIVES is never ship approval.
