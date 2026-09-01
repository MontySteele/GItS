# Kokomi — identity record

**A record of what LAW used to pin, not law.** These lines were `LAW.md`
§*Character identity — Kokomi* (lines 225 to 272) until 2026-09-01, when the
machinery review's change 6 moved character identity out of LAW. They are moved
verbatim, PROSPECTIVE markers and all. They are revised by a sentence in
Kokomi's brief when that brief is written, not by a LAW amendment; until then
this file is where they are read.

---

- **No self-damage anywhere** in her kit or personal pool (extends to shared-pool
  errata); her risk axis is tempo and card economy only. (Law 1)
- **No healing exception:** the conjunctive healing law stands unmodified for
  her; her healer fantasy is Block, Charge, and prevention — no healing
  amendment, ever. (Law 2; R52 ask 1)
- **Flawless Strategy: Kokomi cannot gain Strength** — any Strength she would
  gain becomes Charge. (Law 3)
- **Deck-size grammar:** in her personal pool, Common cards never increase deck
  size (net delta ≤ 0); only Uncommon/Rare may create cards. Machine-checked;
  her personal pool only. (Law 4)
- **Charge is spent by the Bake-Kurage and by nothing else** — uncapped, accrued
  at 1 per Exhaust of one of her own cards, Companions included, Status and Curse
  excluded; card-event-driven with no passive accrual *(Ancient carve-out: R127,
  see card-sheet rules)*. It has exactly one destination: at the threshold the
  jellyfish pays it to play the front of its memory for 0 energy, one card per
  turn. **No card prints a Charge price and no card reads the bank
  proportionally** — the firewall R80 built against Regent-Stars convergence
  moves from "never spent" to "spent one way, by the kit, on tempo and never on
  magnitude." The engine is kit-level (relic + starter), never draft-gated; the
  relic holds only bookkeeping, all payoff magnitude lives in cards.
  ***PROSPECTIVE (R213), countersigned R226:*** *this bullet binds when
  `C.KURAGE_MEMORY` flips; until the flip the shipped rule is the one it
  replaces — **Charge is never spent**, read but never consumed.*
  (kokomi §0, §2.1; R80 amended by R226; R16)
- **The Bake-Kurage's memory can hold one of her own non-Companion cards.**
  Every Companion-only reading of the memory is wrong under Rule 1.
  ***PROSPECTIVE (R213), countersigned R226:*** *binds when `C.KURAGE_MEMORY`
  flips.* (kokomi §11.7; R226)
- **A memory copy is removed from combat and is not an Exhaust.** It is a
  lifecycle statement, not an implementation detail, and it binds every
  exhaust-counting row on her sheet. ***PROSPECTIVE (R213), countersigned
  R226:*** *binds when `C.KURAGE_MEMORY` flips.* (kokomi §11.7; R226)
- **Elite pair A2 Scaling + A6 Utility;** acceptance signature is HP-trajectory
  flatness (the stability band); ward prevention stays reported telemetry, never
  axis-credited. Canonical archetypes: priest / commander / assist (+ generic).
  (R51; R66)
- **Rotation law: Kokomi only Exhausts her own cards.** A Status or a Curse is
  never one of her cards: Muster and every chosen-Exhaust card never select
  one, and no Charge (or Burst particle) accrues from a Status/Curse exhaust
  by any route. Discard is unchanged. An explicit `filter:` on a card is the
  opt-in (Dodge Roll's shape); a dedicated Uncommon/Rare that can eat those
  types is reserved future design space. ([USER] 2026-08-23)
- **VOICE LAW: Exhaust is rotation, never sacrifice.** Weak/Vulnerable enter her
  pool only as riders on exhaust/Sly engine pieces. Conscripted companions count
  as self-sourced kit for `SUPPORT_CARRY`; drafted Inazuma-pool cards count
  normally. (R55; R51; R52 ask 7)

---

**What is still enforced in code, and by what.** Moving these lines out of LAW
did not switch anything off. The rotation law lives at three seams off
`Card.is_junk` (`tier0/engine/state.py`, and `EB-241` widens it at the Kokomi
fold); the deck-size grammar and the no-self-damage rule are sheet lints; the
Charge rules ride `C.KURAGE_MEMORY`. A change to any of those is still a code
change with a test, whatever this file says.
