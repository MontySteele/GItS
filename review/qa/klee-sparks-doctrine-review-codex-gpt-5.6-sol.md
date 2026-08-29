# Klee Sparks — the independent seat's doctrine review, verbatim

**2026-08-29.** The repo-visible doctrine seat, run under the clause-only
protocol (`docs/current/OPERATIONS.md`, "Doctrine seat protocol") on
`review/active/klee-sparks-2026-08-29.md` as committed at `412b929`.

Everything below the provenance block is the seat's own words, **unedited**. I
have not argued with a verdict. Where the seat's verdict turns on a repository
fact I checked the repository and recorded the check below its own words,
marked as my check and not as its claim.

---

## Provenance

**Seat:** `understudy/seat.py`'s repo-visible review door — OpenAI Codex CLI
`0.150.1`, logged in through [USER]'s ChatGPT subscription, model
**`gpt-5.6-sol`**. Independent by model family (R217 C): Claude authored the
packet's card proposals and its pick lists, GPT reads them. NOT blind — this
seat is meant to read doctrine.

**Exact command, both rounds:**

```
python -m understudy.seat review <prompt> --model gpt-5.6-sol --out <out>
```

which `understudy/seat.py::review_argv` builds as `codex exec -C <repo>
--sandbox read-only --ignore-user-config --ephemeral --color never -o <out>
-m gpt-5.6-sol -`, with the prompt on stdin.

**The prompts are inlined, not fetched.** The Windows command policy rejects
every file read this seat attempts (recorded when it happened, on the Klee
slice-1 doctrine review), so both prompts paste verbatim and unsummarised: the
whole packet, the whole of `docs/current/research/regent-stars-economy.md`,
`docs/current/characters/klee-character-design.md`, LAW's "Character
identity — Klee", LAW's D1–D9 design charter, and LAW's card-sheet rules.

| round | prompt | sha256 | bytes |
|---|---|---|---|
| 1 | `review/qa/klee-sparks-doctrine-review-prompt.txt` | `f02bc50c4793b7d925b6eb935eda96a72d986d8960ed81e2f4fd05889925b8a9` | 82241 |
| 2 | `review/qa/klee-sparks-doctrine-review-r2-prompt.txt` | `0cee0ae6456c408cef38618a05a7f6d2fd359e51567abc716a6af3f32ee0b2b3` | 86355 |

**What the seat was told it may not grade.** [USER] has already ruled the
direction — retire the automatic free-Attack base rule; Sparks become a card
cost; no cap; match Regent's generation pattern; re-stock with Spark-cost
Attacks plus a Rare Power converting Attacks to a 3-Spark cost. The seat's own
family co-authored that direction with [USER], so the prompt states the
direction as CLOSED and instructs the seat to gate the **cards and the picks
only**, never the direction (packet §7). It issued no verdict on the direction.

**Why two rounds.** Round 1 answered the doctrine half of every question
(FOLLOWS / REQUIRES_MODIFICATION plus the clause) and did not name which
printed option it was selecting. Round 2 re-asked **only** that half, with
round 1's reply pasted back verbatim and declared standing. Round 2 is a
selection among options somebody else already wrote — the seat was told
explicitly it may not invent, alter or renumber an option — so it is a verdict
under the protocol and not an authored remedy.

**Clause-only compliance: clean, both rounds.** The seat supplied no card text,
no number, no mode and no rewritten row. **It volunteered no remedy**, so there
is nothing here to mark DISCARDED, and its model family stays eligible to grade
these rows later (`EB-190`).

---

## The seat's reply — round 1, verbatim

PICK 1 — FOLLOWS — D2: “The control must be reachable early and reliably — starter kit, starting relic, base system, or the ordinary pool — not only through a rare.”

PICK 2 — FOLLOWS — D2: “Every persistent resource and every automatic engine must feed a decision the player can steer.”

PICK 3 — REQUIRES_MODIFICATION — R69 / R29d: “Display names live in the unique-names namespace, reserved names annotated with the owning kind.”

PICK 4 — FOLLOWS — D7: “Each pool carries linear signposts AND modular tools.”

PICK 5 — FOLLOWS — D2: “Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing.” D4: “At the decision point the player can perceive and forecast the consequences that matter.”

PICK 6 — FOLLOWS — D4: “Text that cannot bind in the shipped world, invisible feeds and misleading calculated displays are defects.”

PICK 7 — FOLLOWS — D4: “At the decision point the player can perceive and forecast the consequences that matter.”

PICK 8 — FOLLOWS — D4: “At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule.”

G1 — REQUIRES_MODIFICATION — R69 / R29d: “Display names live in the unique-names namespace, reserved names annotated with the owning kind.”

G2 — FOLLOWS — D2: “Every persistent resource and every automatic engine must feed a decision the player can steer.” D4: “At the decision point the player can perceive and forecast the consequences that matter.”

G3 — FOLLOWS — D2: “Every persistent resource and every automatic engine must feed a decision the player can steer.” D4: “At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule.”

---

## The seat's reply — round 2, verbatim

PICK 1 — 1, Relic keeps its body, and a Basic card carries the buffer; 5, Convert one Basic Attack into the starter’s spark sink; best: 1.  
PICK 2 — 1, Match Regent exactly.  
PICK 3 — 2, Tinder Toss; 3, Bang Bang!; 4, Dodoco Blast; 5, Firework Finale; best: 2. Option 1 ruled out — R69 / R29d.  
PICK 4 — 1, The tight set.  
PICK 5 — 1, STRICT conversion.  
PICK 6 — 1, `SPARK_ALT_COST_ENABLED = False`.  
PICK 7 — 3, derive it from the new sink prices once §4’s numbers are ruled.  
PICK 8 — 2, Keep `SparkPower` and build a Klee Spark badge.  
PICK 5 sub-pick — (a), already-priced Attacks are unaffected; (b) ruled out — D2.  
PICK 1 combination — Options 1 and 5 together follow.

---

## My check on the one REQUIRES_MODIFICATION

Not a comment on the verdict — the verdict stands as written. The seat ruled
`PICK 3` option 1 and gate question `G1` against LAW's card-sheet rule quoted
above, and the repository agrees with it: **`Sizzle` is already a shipped Klee
card.** `docs/klee-cards.yaml:158` carries
`{id: sizzle, name: "Sizzle", cost: 1, type: attack, rarity: common, …}` and
`docs/klee-upgrades.yaml:46` carries its upgrade row. The packet's §4.2
candidate 1 proposed the name `Sizzle` for a NEW Common Attack; the character
design doc's §4 also names Sizzle as an existing Reaction-archetype payoff.
The collision is real and the seat found it unaided.

The seat left the other four candidate names standing on that clause. It named
no other clause against the set, and it named no clause the packet had not
already put in front of it.
