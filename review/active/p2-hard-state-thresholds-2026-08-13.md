Status: OPEN (picks 1-4, the four threshold proposals)

# P2: what counts as a "hard state"? — a proposal, with the first numbers

**For [USER]. One decision, and it is a decision you already reserved.**

When you amended Phase 2's default to hard-state turn sampling (R94, the
understudy countersign package), you named the *shape* of the trigger —
"incoming above a set fraction of HP, more than one enemy alive, or lethal
within reach" — and then wrote, deliberately, that **the trigger thresholds
are P2 design work, not set here.** This packet is that work coming back to
you with numbers attached and nothing settled behind your back.

## What has been built, and what it does not do

The sampling leg exists and runs. It is `understudy/p2capture.py`, it is off
unless a soak passes `--p2-capture`, and it **calls no model from the game
loop, ever**. At each combat turn opening it asks "is this state hard?", and
if the answer is yes it writes down the whole state the bot saw plus what
*both* heuristics wanted to do there. That is all. It is a corpus builder.

Nothing in it is evidence about the game. A count of hard states is a count
of states that tripped these particular numbers.

## The placeholder I ran it on, and why each number is where it is

Every record stamps `definition: placeholder-conservative-2026-08-13` and
carries the four numbers with it, so nothing captured under this guess can
later be mistaken for something captured under your ruling.

| trigger | placeholder | reasoning |
|---|---|---|
| incoming ≥ this fraction of **current** HP | **0.35** | A turn that can cost a third of what is left is not routine. Against Klee's 62 max HP the soaks show 8–18 incoming per turn, so this is meant to fire on the fights that actually threaten. |
| enemies alive | **2 or more** | Your literal wording. It is the one trigger with no free parameter in it. |
| "lethal within reach": weakest enemy's HP ≤ this × the biggest attack in hand | **1.5** | 1.0 would mean "I can kill it with one card". 1.5 lets in the two-card line, which is where the sequencing disagreement you are aiming at actually lives. |
| player HP ≤ this fraction of max | **0.30** | **Not one of your three.** I added it because a low-HP turn is where mistakes end runs. It is flagged separately in every record, so you can strike it without touching the others. |

## The first measurement, and the thing it says

Two Klee runs, 2026-08-13, package `0.2-738`:

- **56 turn openings** seen, **33 captured** — so the placeholder fires on
  **59%** of turns.
- Which triggers fired (a state can trip several): more than one enemy **23**,
  incoming over the HP fraction **16**, lethal within reach **14**, low HP **5**.
- About **8 KB** per record, so a 20-run night is on the order of 3 MB. Storage
  is not the constraint.

**59% is the finding, and it is an argument against my own placeholder.** The
whole point of hard-state sampling is that the expensive tier engages where it
matters and stays out of the way everywhere else. A trigger that fires on
three turns in five is not selecting hard states; it is very nearly saying
"every turn with a second monster on the screen". The multi-enemy trigger is
doing most of that work on its own.

## What I would propose, if you want a recommendation

Not shipped — this is the ask, not a change:

1. **Make "more than one enemy" a modifier, not a trigger.** On its own it
   fires constantly. As "two or more enemies *and* incoming above some
   fraction" it describes the turn you actually meant.
2. **Raise the incoming fraction to 0.45** and measure again. 0.35 is a third
   of the bar; 0.45 is closer to "this turn could halve me".
3. **Keep the lethal-reach trigger as it is.** It fired 14 times in 56 and
   is the one aimed squarely at the sequencing disagreement the Phase-0 run
   measured.
4. **Rule on the low-HP trigger** — it is mine, not yours, and it should
   either be adopted on purpose or dropped.

A reasonable target is something like one turn in five or six. That is a
taste call about where the budget goes, which is why it is yours.

## What happens after you rule

The numbers move to a ratified definition, the placeholder captures are
either re-taken or filtered by their `definition` stamp, and the LLM leg gets
built against a corpus everyone agrees is the right corpus. None of that
starts before you rule.

Guardrail-7 is unchanged by all of it: a bot cannot see the screen, and a
capture is a record of what it saw, not a claim about the game.
