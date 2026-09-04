# Kokomi round 9 — run 1, act 2 — blind TESTER seat

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, Kokomi round 9, run 1, act 2
  (second of chained seats).
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Seed:** `F3BMW33EX9H6`.
- **Ascension:** 2.
- **Act:** 2. The map printed its boss as **The Insatiable** ("At the top of this
  act: **The Insatiable**").
- **Actions accepted:** **1** (`go "Ancient (path 1)"`).
- **Termination reason:** **TOOL-BLOCKED**, not a budget. After the single map
  move, every subsequent command — `observe` and `act` alike — died with the
  same guard:

  ```
  REFUSED: 1 design-vocabulary leak(s) in the packet:
    mod-id-prefix: 'KLEEMOD-' in 'relics.SEA_GLASS.KLEEMOD-FURINA.title'
  ```

  Three consecutive refusals, all identical, and the third one (an `act`) showed
  why there is no way around it: `act` calls `observation(state)` before it
  resolves anything, so the guard fires on the read path that `act` shares with
  `observe`. Traceback: `blindplay.py:222 cmd_act` → `blindplay_grammar.py:871
  act` → `blindplay_observe.py:378 observation` → `qa_packet.py:233
  assert_blind` → `PacketLeak`. There is no command in my grammar that does not
  go through that call, so the lane cannot be driven forward at all. Per the
  brief I stopped rather than looking for another way through.
- **HP trajectory:** **unknown / not printed.** The only screen I ever saw was
  the act-2 map, and this bridge's map screen prints no HP, gold, potions, deck
  or relic list. I never reached a combat, a rest, a shop or a reward screen, so
  I have no honest number to give for HP, gold or potions, and no end-of-run
  deck or relic list. I am not going to reconstruct any of it from anywhere
  else.
- **Gold:** unknown / not printed.
- **Potions held:** unknown / not printed.
- **Deck and relics at the end:** unknown / not printed. The one thing the
  blocked packet does tell me about the relic pool is the leaked key itself —
  there is a relic the packet calls `SEA_GLASS` filed under an owner
  `KLEEMOD-FURINA`, and its **title** field is what carries the raw mod id.
- **Neow pick:** **none — not mine to make.** Neow is a floor-1 act-1 screen and
  act 1 was played by the previous seat in the chain. I was handed the lane on
  the act-2 map, and per the coordinator's instruction I did not open the act-1
  record, so I do not know what that seat took and I am not guessing.

### What actually happened, in order

1. `observe` — the act-2 map printed cleanly. Exactly one reachable node:
   **Ancient (path 1)**, leading on to Monster, Monster. Sixteen floors to the
   boss.
2. `go "Ancient (path 1)"` — **accepted**. `ok Traveling to Ancient at (3,0)`.
3. `observe` — **refused**, PacketLeak on
   `relics.SEA_GLASS.KLEEMOD-FURINA.title`.
4. `observe` again, to check whether it was transient — **refused**, byte-for-byte
   the same message. It is deterministic.
5. `act 'proceed'` — **refused**, same PacketLeak, this time as an uncaught
   traceback rather than the tidy `REFUSED:` line. That is where I learned that
   `act` reads through `observation()` first, so the block is total and not
   specific to the verb I picked.

The map screen immediately before the move was clean, so whatever put a relic
block into the packet did so on arrival at the Ancient node — which is the screen
that offers ancient relics. That is consistent with the leak being in the offered
relic list rather than in something already held, but I only ever saw the key, not
the screen, so I am flagging that as inference and not as something I observed.

## Fights

**None.** I never reached a combat. There is nothing to report in this section and
I am not going to invent it. The round produced no turns, therefore no rejected
alternatives, therefore no data on whether act-2 turns present real decisions.

## The kit, after 0 fights

I saw one map screen and no card, no enemy, no keyword and no turn. Every one of
these answers is "no evidence", and saying so is the whole of what this round
found. I am not going to launder impressions from a node list into kit judgements.

- **(a) Which decisions felt like real choices, and what they traded off.** No
  evidence. The single navigation decision was not a decision: the act-2 map
  offered exactly one reachable node, **Ancient (path 1)**. There was nothing to
  trade off — the move was forced, and I recorded no rejected alternative because
  none existed on the screen.
- **(b) What felt automatic, and what never seemed worth playing.** No evidence
  on cards. The one thing that was automatic was the map move above, for the
  structural reason that there was only one edge out.
- **(c) What you could not understand, or that seemed to contradict its own
  printed text.** The only thing I could not get past is the bridge itself, and
  it is worth stating plainly because it is the finding of the round: **a relic
  in the act-2 pool carries the raw internal mod id `KLEEMOD-` in its `title`
  field**, and the blindness guard is doing exactly its job by refusing to show
  me a screen with a developer identifier printed on a card face. A title is
  player-facing text; `KLEEMOD-FURINA` is not player-facing text. Whatever a
  human player sees on that Ancient screen, they are seeing something with a mod
  id where a name should be. The guard turns that from a cosmetic blemish into a
  hard stop for any blind seat that walks onto an Ancient node in this act, which
  means this run — and, if the relic is in the general pool, any run that reaches
  an Ancient node — is unplayable by a blind seat until the title is fixed.
  Secondary, smaller, and also real: the refusal surfaces two different ways for
  the same underlying condition — a clean `REFUSED: ...` line from `observe`, and
  an unhandled Python traceback from `act`. The `act` path should catch
  `PacketLeak` and print the same one-line refusal; a seat should not have to
  read a stack trace to find out its command was declined.
- **(d) The card you never wanted to play, and the one you were happiest to
  draw.** No evidence. I drew no cards and played none.
- **(e) Did the first turn of the first fight already present a decision?** No
  evidence — there was no first fight. The question is unanswered for act 2 and
  should be re-run once the relic title is fixed.

### What this round is worth

One thing, cleanly: **a blind seat cannot play act 2 of this seed.** The block is
deterministic, reproduced three times, and sits on the read path shared by both
allowed commands. The fix is a text fix in the relic's `title`, not a change to
the guard — the guard caught a genuine leak of a developer identifier into
player-facing text, which is what it is for. A re-run of this act after that fix
would cost the chained seat nothing, since it stops on floor 1 of 16 and no game
state past the map move was consumed.

## Non-blindness declaration

- **Repo files read: none.**
- **Allowed game commands used** (3 distinct forms, 4 invocations, 1 accepted):
  - `GITS_LANE=1 python -m understudy.blindplay observe` — ×3 (1 accepted, 2
    refused)
  - `GITS_LANE=1 python -m understudy.blindplay act 'go "Ancient (path 1)"'` —
    ×1 (accepted)
  - `GITS_LANE=1 python -m understudy.blindplay act 'proceed'` — ×1 (refused)
- **Commands run outside the two allowed ones** — 1, scratch only:
  - `mkdir -p "<scratchpad>/kokomi-r9-seat-act2" && echo ok` — created the
    scratch directory the coordinator named. Nothing was ever written into it;
    the round ended before there were notes to keep.
  - I also piped two of the calls above through `head -40` (`... 2>&1 | head
    -40`) purely to bound output length. No filtering of game content, and no
    other shell work.
- **Tools used:** Bash (the four game calls plus the one `mkdir`), and Write
  (once, for this record). No Read, no Grep, no Glob, no Agent, no other
  understudy subcommand. I did not run `harness state`, `scenario`,
  `staged_turn`, `soak`, or anything else that prints a pilot recommendation.
- I did not open the act-1 record, nor any other seat's record.
- The one piece of internal vocabulary that reached my eyes —
  `relics.SEA_GLASS.KLEEMOD-FURINA.title` and the file/line names in the
  traceback — arrived unbidden in the tool's own refusal text. I did not go
  looking for it and I did not follow it into any file. It is disclosed here in
  full so the round carries the caveat rather than hiding it. It gave me a relic
  key and an owner tag, no card text and no kit information, so I do not think it
  contaminates the (a)–(e) answers — but since those answers are all "no
  evidence" anyway, there is nothing there for it to contaminate.
