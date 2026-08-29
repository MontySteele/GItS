# Furina E4 — the independent seat's doctrine review, verbatim

**2026-08-29.** The repo-visible doctrine seat, run under the clause-only
protocol (`docs/current/OPERATIONS.md`, "Doctrine seat protocol") on
`review/active/furina-e4-2026-08-29.md` as committed at `b25485d`.

Everything below the provenance block is the seat's own words, **unedited**. I
have not argued with a verdict and I have not corrected a fact inside one.

---

## Provenance

**Seat:** `understudy/seat.py`'s repo-visible review door — OpenAI Codex CLI
`0.150.1`, logged in through [USER]'s ChatGPT subscription, model
**`gpt-5.6-sol`**. Independent by model family (R217 C). NOT blind — this seat
is meant to read doctrine.

**Exact command:**

```
python -m understudy.seat review review/qa/furina-e4-review-prompt.txt     --model gpt-5.6-sol --out understudy/logs/seat/furina-e4-doctrine.md
```

which `understudy/seat.py::review_argv` builds as `codex exec -C <repo>
--sandbox read-only --ignore-user-config --ephemeral --color never -o <out>
-m gpt-5.6-sol -`, with the prompt on stdin. The session rollout lands in
`understudy/logs/seat/`, which is gitignored; this file and the prompt are the
committed artifacts.

**The prompt is inlined, not fetched.** `review/qa/furina-e4-review-prompt.txt`,
sha256 `5538382fc7142598e6715618c53f8844b9ba8e3461557cf28e777ddd2c661c71`,
92746 bytes. It pastes the packet whole plus the governing law the
gate needs — D1–D9, LAW's Combat & reactions block (including the clause §3.1
replaces), the Economy block (including the clause §3.2 amends), the whole of
"Character identity — Furina", the funnel/animation contract, the card-sheet
material-edit rule, and kickoff §§1–9 — because the sandbox's command policy
rejects file reads and a seat that cannot read cannot be asked to cite.

**The direction was declared settled and out of scope in the prompt**, in
those words, because the architecture is GPT-co-authored with [USER]. The gate
was scoped to four items: G1 the E4 ruling text and its retirements, G2 the
two LAW amendment wordings, G3 the §4 architecture specifics, G4 the §9 pick
list.

**No remedy was volunteered.** The seat named clauses and stopped, which is
what the protocol asks for and is not what always happens. Nothing below had
to be marked DISCARDED, and the seat's family therefore stays eligible to
grade these rows later.

---

## The seat's verdicts, verbatim

G1: REQUIRES_MODIFICATION  
Clause: Furina kickoff §3.1, “In co-op, the selector may instead be passed to a teammate”; and §4, “partner HP/Encore flux counts toward Fanfare.”  
Why: E4 removes the selector and the flux-based Fanfare legs while leaving these binding co-op provisions neither operative nor explicitly retired.

G2: REQUIRES_MODIFICATION  
Clause: D4 — “Text that cannot bind in the shipped world… [is a defect].”  
Why: The Burst-scope amendment says only a Featured performance generates Furina’s meter, while the ruling and architecture also make deliberate Encore spending an independent generation leg.

G3: REQUIRES_MODIFICATION  
Clause: D4 — “At the decision point the player can perceive and forecast the consequences that matter.”  
Why: The Salon lane designates a lane whose hook fires for each member act, but the Featured outcome refers to a particular member without defining how that member is selected.

G4: REQUIRES_MODIFICATION  
Clause: R213 sequencing — “Then Klee’s reaction slice, then Furina after the Companion result. Not three explorations in parallel.”  
Why: P1 presents parallel Furina implementation as an unsettled choice even though the governing sequence already excludes it.

OVERALL: REQUIRES_MODIFICATION  
Clause: D4 — “Text that cannot bind in the shipped world… [is a defect].”  
Why: The unresolved rule contradiction and undefined Featured-member selection prevent the proposed architecture from binding unambiguously.
