# Newcomer round 1 (2026-10-19)

The first round of the newcomer seat (#1480, ruled in the release pass:
"see if the seats can actually independently figure out how to pilot the
characters"). Five Sonnet seats played one kit each. Each seat saw only the
player's page: the game's own text and hover tips, with no ledger, no
previews, no glossary and no strategy brief. Each seat finished with a
four-question exit form. All five ran at A0 on seed `30KMHAVG9SMQ` (the
Ironclad seed of the suites), so each kit has a full-information run on the
same seed to compare with. One seat per kit on one seed: this is a reading,
not a measurement. Raw records are in the scratchpad and gitignored.

| Lane | Kit | Newcomer end | Actions | Full-information runs, same seed |
|---|---|---|---|---|
| 1 | Klee | floor 25, Decimillipede elite (entered at 10 HP) | 297 | 48 **won** (suite 6); 25, same elite (suites 2, 3) |
| 2 | Varka | floor 40, Slimed Berserker | 511 | 40, same enemy (Varka-next suite 1) |
| 3 | Furina | floor 40, Slimed Berserker (entered at 25/78) | 585 | 24 / 39 / 39 / 33 (suites 1 to 4) |
| 4 | Kokomi | floor 25, Decimillipede elite (entered at 14 HP) | 304 | 48, Test Subject (v2 round, an older pool) |
| 5 | Yae | floor 48, Test Subject phase 2, boss at 7 HP | 808 | 48 **won** (round 11) |

## What played well

- **All five newcomers found the central loop by themselves**, and all five
  named it correctly in the exit form's question (a).
  - Klee: grow a pile of Bombs, then pick the turn to set them all off.
  - Varka: apply an element with a Knight, then react with another, while
    Oath builds.
  - Furina: spend HP for Fanfare, then cash it in for burst.
  - Kokomi: play a card now, or Plan it for a bigger effect next turn.
  - Yae: keep timed Sakura alive and choose damage or Block from each.
- **Most kits clicked within a few fights:** Klee by fight 3 or 4, Varka by
  fights 3 to 5, Furina by fight 3, Kokomi by fight 4. Yae took longest, until
  floor 7.
- **All five said yes to another run**, and each named a combo turn as the
  best moment.
  - Klee killed Soul Fysh (211 HP) with one 228-damage Kaboom!.
  - Furina took the act 1 boss from 157 to 92 HP in one turn.
  - Varka's late Four Winds' Ascension+ hit for 30 or more.
- **Results held up.** Varka matched its full-information floor exactly, and
  Furina reached at least as far as any of her suites. Yae came within 7 boss
  HP of a win.

## What did not

**Comprehension gaps that cost HP or a run, by kit:**

- **Furina.** The seat never learned how much HP the Drain refund returns. It
  assumed the refund covered all its spending, entered act 3 at 16 to 25 HP,
  and died for it. This is her open Next item ("make her HP legible"), now
  reported first-hand by a newcomer.
- **Yae.**
  - Dawn Prayer hits the "newest" Sakura, and Twin Sakura plants its Kitsune
    last. The seat misplayed this twice, and the second time cost the run.
  - The planting rule ("Same kind: it refreshes and gains a Level") never made
    sense to it: two Evocations made two separate Level 1 Sakura.
  - It only learned the shrine's "withers" rule on floor 33.
- **Klee.** Anemo and Swirl never visibly changed a number ("I could not see
  Anemo change any number"), so Chime read as a bare 10-damage attack.
- **Varka.** Oath, Swirl and "current element" were unclear until fight 3.
  Windborne Resolve was played to no effect because Cryo was already the
  current element. Durin's Dark/White choice was still unclear in act 3.
- **Kokomi.**
  - It couldn't tell whether Strength and Vulnerable are read when a Plan is
    made or when it resolves.
  - Plan hits did full damage through Flutter's "50% less damage from
    Attacks", which nothing on the page explains.
  - It was surprised that planned cards sit in the discard pile.

**Not the kits:**

- Hunter Killer's Tender (a base-game debuff) caught Klee and Kokomi out, and
  every seat over-spent HP on route greed.
- Four seats filtered `observe` output through `grep`, which the brief
  forbids. On the newcomer page this hides hover tips, so it may have
  contributed to some misreads.

**Page and text faults found:**

- **Fixed in the round (#1481).** The newcomer page printed power text raw.
  Blazing Delight's energy icon tripped the leak guard, and lane 1 was stuck
  mid-fight until the fix landed.
- **Kujou Sara's Electro rider** prints "Applies Electro — Applies Hydro for 2
  turns" (lane 4).
- **The newcomer page left the enemy list blank** for a whole turn during Test
  Subject's revive. A human sees the reviving boss (lane 5).
- **The Ancient's full heal** in act 2 was not printed (lane 5).
- **A stale reward screen** showed after the Potions event (lane 5).
- **The run-over page** doesn't print the deck.

**Environment.** RitsuLib, a Workshop library [USER] subscribed to for a look
at another mod, loaded in all five lanes and put a "telemetry permission"
popup on each screen. No seat reported it affecting play. Embark now switches
off every mod except BaseLib, the bridge and the kits (this PR).

## What to change

1. **Furina:** show the refund. Make the HP she will get back at combat end
   visible during the fight. This is her Next item; the newcomer reading
   confirms it is the first thing to build.
2. **Yae:** check the planting rule live against its text. Either the text is
   wrong or two Evocations should have stacked. Reword Dawn Prayer's "newest",
   because Twin Sakura's planting order is invisible.
3. **Klee and Varka (frozen; wording and previews only):** make the Swirl
   contribution visible on the card or in the hit. Klee's Chime is the
   clearest case.
4. **Kokomi:** in her finish pass, say on the page when a Plan reads Strength
   and Vulnerable, and that Plan hits are not Attacks.
5. **Text and page:**
   - fix the Sara rider text;
   - show reviving enemies on the newcomer page;
   - print the Ancient's heal;
   - add the deck to the run-over page.

   These are in `BACKLOG.md`.
6. **Next newcomer round:** run it after items 1 and 2, on the same seed, so
   the two readings compare directly.
