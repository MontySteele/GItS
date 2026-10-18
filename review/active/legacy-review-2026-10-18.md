# Legacy review: early rules still running (2026-10-18)

The user, 2026-10-18, after finding the Featured Banner: "Now might also be a good time to revisit our other early
decisions... Can you kick off a full project review of all of the mod's surfaces and rules and look for any other
weird legacy items that crept in?"

Five read-only sweeps covered rewards and the shop, companions, the run frame and modes, every Harmony patch (about
150), and LAW, the kit checklist and `tier0/constants.py` checked against the code. Each finding below names its
file. Most of these rules came from July and August, when the Python sim decided balance. STATE now says the sim
"does not gate balance", so a rule whose only reason is "the sim does it" has lost that reason.

## What changes what you see in a run (picks 1–4)

1. **Klee's first rewards are quietly seeded with a Spark card.** On floors 1–3, if a post-fight reward rolls no
   card that costs Sparks, one offer is swapped for one (`SparkSeededReward.cs`, `KleeOverhaul.SparkSeedFloors = 3`).
   It came from seat rounds r17–r21 on 2026-09-05 ("Sparks are inert until a sink is drafted"). It runs on every
   Klee run, no current doc mentions it, and its comment still describes a switch that no longer exists. Klee is at
   Balance, so removing it moves her shipped behaviour.
2. **The shop almost never sells a Rare companion.** For the five mod characters, the shop's two colorless slots
   sell companions. Each slot rolls 87.5% Uncommon and 12.5% Rare (`MerchantCompanionSlots.cs`), where the base game
   sells one fixed Uncommon and one fixed Rare. The written reason is "Fontaine designs ZERO Rare companions", but
   Fontaine has had Rares since July.
3. **The free companion in card rewards ignores the base reward rules.** It always rolls 60/35/5, with no pity and no
   better odds after elites, and it never comes upgraded (`CompanionSlot.cs`). Both rules exist only to match the
   sim. After a boss it is forced to Rare, and it is simply missing if no Rare can be offered.
4. **Every shared companion wears Klee's red frame.** All 79 shared companions are filed under `character: klee`, so
   they sit in Klee's card pool in every character's run (`KleeCardPool.cs`). A July comment deferred moving them
   "for [USER] at sprint close-out", and that never happened.

## Rules that are written but not followed (picks 5–7)

5. **LAW lines that every kit breaks, enforced by nothing:**
   - "At most two new keywords per character". Every kit has four or more (Yae has seven).
   - "Constellation names for Rares and upgrades, talent names for relics". Many relics and Rares don't follow it.
   - "Threshold cards pay once; meter bars are Uncommon or higher" and "every meter declared bounded or unbounded,
     cap in `constants.py`". The only lint covers Charge and Burst, both retired.
   - "Neutral energy and draw are legal Companion utility when one-shot, costed and Exhaust-gated". 15 companions
     break it, and so do the new Inazuma Rares (Chihayaburu, Hanega).
   - "A 5-star is a support payoff, never its own scaling damage engine". Albedo, Durin, Neuvillette and Arlecchino
     break it.
   - "Upgraded starter cards get a distinct name". The source rule was about the upgraded starter relic.
   - "Builds stay private until the distribution point is ruled". It was ruled today: closed beta now, public once
     one more kit reaches Balance.
   - "Personal companions may enter through an optional, declinable run-start offer". No code does this, the
     Personal lists are empty, and QUEUE still carries a deferred pick about it (P5a).
6. **Hair Trigger breaks "cycling engines are Uncommon or higher".** It is a 0-cost Common that draws a card, on
   Klee's Balance sheet. That's the same line as your "no cycling at Common" rule.
7. **Varka's Knights count as Companions.** They carry the Companion tag, so everything that counts companions
   counts them, and his starter holds one. STATE says "No kit starts with a Companion."

## Fixing now, no pick (hygiene)

- **Done:** Yae's reward slot could offer her own Sesshou Sakura. The shop and the sim hid it, the reward slot didn't
  (#1440).
- **About 60 code comments say "quarantined, not compiled in a release build".** The switch they describe was removed
  on 2026-10-01, and all of that code ships. Corrected.
- **Dead code:**
  - the borrowed Silent relics (members of each pool, never offered);
  - the empty Personal-companion lists (Varka's Knight tag stays);
  - the shop's "no Power in the pool" fallback, which ran for every player;
  - the three orphan Neuvillette guest rows (Common 5-stars that nothing generates);
  - sim modes that were ruled out (companion pity, choose-3);
  - the sim's "kept shipped rows" roster half;
  - the retired-rule constants (`SPARKS_FOR_FREE_ATTACK`, the Fanfare cap and fade, Burst, Salon, the
    companion-Spark cap that cites a deleted LAW line).
- **Guards made real:**
  - The healing test only reads the retired card sheets, so nothing checks the live cards; it now does.
  - The 4-star rule ("at most Uncommon") gets a lint, now that the banner's Star reader is gone.
- **Qiqi** is moved to Mondstadt, as LAW says. Today she is a one-card Liyue that no one gets home weighting for.
- **Stale text:** STATE's stamp table and its "last release package", the kit checklist's pointer to a LAW section
  that no longer exists, and wrong counts in the co-op and companion-slot comments.

## Looked at, left alone

- **The Teyvat frame** (about 150 events, 34 patches) is compiled into the release but switched off, as STATE says
  ("stays off").
- **The reward-row probe** only logs; it stays until its off-screen bug is closed.
- **The event-reward widening** stays as a safety net. It lets an event's reward draw widen when a pool can't fill a
  rarity and type, and 78-card pools rarely trigger it.
- **No character has an unlock gate,** which is still what we want.
- **The base-game hang guards** (Bezier, Punch Off) are still needed on game version 0.111.0.
- **The kits' card frames and energy orbs borrow base colours** (Klee red, Kokomi, Furina and Varka green, Yae blue).
  That's a look for another day.

## Picks

1. **Klee's Spark seeding.** **(a, default)** Remove it. (b) Keep it and write it into STATE.
2. **Shop companion slots.** **(a, default)** Base shape: slot 1 Uncommon, slot 2 Rare (Uncommon if none can be
   offered). (b) Keep 87.5 / 12.5.
3. **Free companion reward.** **(a, default)** It rolls like the three cards beside it: the reward's own rarity odds,
   pity and upgrade chance. After a boss it stays Rare, with an Uncommon fallback. (b) Keep 60/35/5 with no upgrades.
4. **Companion frame.** **(a, default)** Shared companions move to their own pool with a neutral frame, out of Klee's.
   (b) Keep Klee's red.
5. **The unfollowed LAW lines.** **(a, default)** Delete all eight bullets above, and P5a from QUEUE. The delete-test
   and the rarity rules stay as the guards. (b) Keep them and enforce them, which means changing the cards that break
   them.
6. **Hair Trigger.** **(a, default)** It becomes Uncommon, as LAW and your "no cycling at Common" rule say. (b) Leave
   it as a noted exception.
7. **Varka's Knights.** Ruled 2026-10-18 (a). The user: "Varka's Knight are actually supposed to count as
   companion cards to make relevant synergies work. That one is not a bug." STATE is corrected in this PR.

## Ruled 2026-10-18

The user: "Agreed on all 6 legacy picks". All six are (a):
1. Klee's Spark seeding is removed.
2. The shop's companion slots take the base shape: slot 1 Uncommon, slot 2 Rare (Uncommon if no Rare can be offered).
3. The free companion rolls like the cards beside it: the reward's rarity odds, pity and upgrade chance. After a boss
   it stays Rare, with an Uncommon fallback.
4. Shared companions move to their own pool with a neutral frame.
5. The eight unfollowed LAW lines are deleted in this PR, and P5a leaves QUEUE.
6. Hair Trigger becomes Uncommon.

Pick 7 was ruled earlier (Varka's Knights stay Companions).
