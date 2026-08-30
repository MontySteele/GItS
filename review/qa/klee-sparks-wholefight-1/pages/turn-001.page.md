You are playing a turn-based card game — a run through a branching map, with
battles, shops, rest sites and events along the way. You have never seen this
game before and there is nothing to look up.

**Everything you know is on the page.** Each message you get is one screen,
printed the way a player sees it: your health, your block, your energy, the
cards in your hand with their costs and their rules text, what the enemies are
about to do, or whatever the current screen is offering. There is no strategy
guide, no card list, no score, no recommendation, and no way to ask for one.
Read the screen and decide.

**Answer with exactly one command,** in this grammar, with every name in
double quotes exactly as the screen prints it:

    play "<card title>"                  play "<card title>" on "<enemy>"
    use potion "<potion>"                use potion "<potion>" on "<enemy>"
    end turn
    choose "<option, card or reward>"    skip            confirm     proceed
    go "<map node>"                      buy "<shop item>"
    rest                                 upgrade         remove

**When two things on one screen print the same name,** the screen numbers
them in the order it prints them — `Water's Edge (1)` and `Water's Edge (2)`,
`Slug (1)` and `Slug (2)` — and you name the one you want with its number. A
name that appears only once is never numbered: say it exactly as printed. A
card the screen marks `(upgraded)` can also be named that way, and
`(not upgraded)` names the other copy.

Every screen lists the commands it accepts under **What you can say**. A
command the screen cannot take is refused and told back to you in one line;
read the refusal and try something else. Nothing is hidden from you as a
punishment — a refusal means the game itself would not accept that click.

Answer as JSON: `command` is the one command, and `thinking` is one or two
sentences on why. Keep `thinking` short; it is recorded, not graded.

**At the end of each fight, and at the end of the run,** you will be asked to
write a short record instead of a command. Write it in plain language, in your
own words, as long or as short as it deserves:

At the end of a fight — the line you took and why; the other line you seriously
considered and what it would have given up; whether a different enemy intent or
a different draw would have changed your choice; which cards became automatic
and which became dead; whether your plan changed during the fight and where;
and whether anything on the screen was confusing to read.

At the end of the run — how you think the character works; which tension came
up again and again; which cards defined the run; where play started to feel
repetitive; and what you would avoid drafting next time.

Say what you actually thought, including where you were bored, confused or
guessing. **None of this is a judgement of whether the game is fun or good that
anyone will treat as approval.** It is one model's account of one run, recorded
so the people building it can iterate.


---

# Battle — round 1

- HP 62/62
- Block 0
- Energy 3/3
- Piles: 11 in the draw pile, 0 discarded, 0 exhausted

## The Bake-Kurage's memory

- Charge: 0
- The memory is empty. Nothing is queued and nothing fires next turn.
- At the end of this turn the jellyfish will do nothing, because you have played no card this turn.

## Your hand

- **Duck and Cover (1)** — cost 1, skill
    Gain 5 Block.
    *Block* — Until next turn, prevents damage.
- **Duck and Cover (2)** — cost 1, skill
    Gain 5 Block.
    *Block* — Until next turn, prevents damage.
- **Ka-pow!** — cost 0, attack
    Spend 1 Spark. Deal 7 damage. Applies Pyro.
    *Applies Pyro* — If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead.
    CANNOT BE PLAYED: BlockedByCardLogic
- **Kaboom!** — cost 1, attack
    Deal 7 damage. Applies Pyro.
    *Applies Pyro* — If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead.
- **Firework Finale** — cost 0, attack
    Spend 3 Sparks. Deal 18 damage. Exhaust. Applies Pyro.
    *Exhaust* — Removed until the end of combat.
    *Applies Pyro* — If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead.
    CANNOT BE PLAYED: BlockedByCardLogic

*Two cards here print the same name. The game's data feed does not report a card's enchantment, so if one of them is enchanted, this page cannot show which.*

## The other side

- **Toadpole (1)** — HP 24/24
    Intent: Empower, This enemy intends to use a Buff.
- **Toadpole (2)** — HP 21/21
    Intent: Aggressive, 7, This enemy intends to Attack for 7 damage.

## What you can say

- `play "<card title>" [on "<enemy>"]`
- `use potion "<potion>" [on "<enemy>"]`
- `end turn`

you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval


Answer with ONE command from the grammar.
