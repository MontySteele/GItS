# The blind grader prompt (EB-149)

The exact text an orchestrator hands a **fresh** agent, together with the
packet. Nothing else goes with it: no repo access, no tools, no file
system, no conversation history, no name of the game, no character sheet, no
prior turn. The agent that answers must never be the one that designed the
cards it is reading — that is R213's first guard, and it is procedural: a new
agent, the packet inline, and the model recorded in the form.

Paste everything between the rules. Replace `<PACKET>` with the contents of
`review/qa/<turn-id>/packet.md`, and `<SHA>` with the `packet_sha256` from
`packet.json`.

---

You are playing one turn of a card battle. Everything you are allowed to know
is on the page below — the cards in your hand exactly as the game prints them,
your health, your shield, your energy, and what the enemies are about to do.
There is no other information, and you should not assume any.

Play the turn: decide which cards you play, in what order, at which targets.
You may play any subset of your hand you can afford, including none of it.

Then answer four questions.

1. What did you play?
2. What other line did you seriously consider?
3. What did your chosen line give up?
4. Would a different enemy intent have changed it?

Answer question two honestly. If you genuinely weighed nothing else, say so —
"none" is a real answer and it is more useful than an invented alternative.
The same goes for question four: if nothing the enemy could have telegraphed
would have moved you, say no.

**You are not being asked whether this is fun.** You are not being asked
whether the cards are good, whether the turn is interesting, whether the
design works, or what you would change. Any judgement of quality is outside
what you were given and outside what is wanted. Play the turn and describe the
decision you made.

Reply with **one JSON object and nothing else** — no preamble, no code fence,
no commentary:

```
{
  "turn_id": "<the id printed at the top of the page>",
  "packet_sha256": "<SHA>",
  "grader": {"id": "<your agent id>", "kind": "llm",
             "model": "<your model name>", "designed_these_cards": false},
  "chosen_line": [{"card": "<printed card title>", "target": "<enemy name, or omit>",
                   "exhaust": "<printed title of the card you Exhausted, or omit>",
                   "choose": "<printed text of the option you took, or omit>"}],
  "q1_what_did_you_play": "<prose>",
  "q2_other_line_considered": "<prose, or 'none'>",
  "q3_what_it_gave_up": "<prose>",
  "q4_different_intent": "<prose>",
  "q4_changed": true
}
```

Name cards by the exact printed titles on the page. `chosen_line` is ordered:
first play first. Set `q4_changed` to `false` if your answer to question four
is no.

If a card you played asks you to **Exhaust a card**, say which one on that
play as `"exhaust": "<the printed title>"`. If a card says **Choose one**, say
which half you took as `"choose": "<the printed text of that option>"`. Leave
both out for a card that asks neither.

<PACKET>

---

## For the orchestrator

* One agent, one turn, one packet. Do not carry an agent across turns: a
  grader that has seen the previous board is no longer reading this one cold.
* Record the model in `grader.model` and a stable string in `grader.id`. The
  ledger groups by `grader.id`, and the down-weighting in
  `staged_turn.is_down_weighted` needs that string to be stable across turns
  for the same grader.
* `grader.id` **`user`** is reserved for [USER]'s own cold play and is the
  form every other grader is compared against.
* **There is a built seat for this: `python -m understudy.seat grade
  <turn-id>`** runs OpenAI's Codex CLI as the fresh agent and does all of the
  above. It proves blindness from the TRANSCRIPT rather than from the
  sandbox — the `--json` event stream, codex's session rollout and stderr,
  each an allowlist where an unknown type refuses — because a read-only
  sandbox stops writing, not reading. A refused seat never reaches `grade`.
  It fills exactly three fields the model cannot know about itself
  (`grader.id`, `grader.kind`, `grader.model`) and touches nothing else; the
  unedited reply is kept beside the filled form as `form-raw.json`.
* Save the reply verbatim to a `.json` file and run
  `python -m understudy.staged_turn grade <turn-id> <form.json>`. Do not edit
  the answers on the way — a form tidied by the orchestrator is a form the
  orchestrator co-wrote.
