# Shop companion channel — re-run registration (COUNTERSIGNED, unrun)

> **Status: COUNTERSIGNED 2026-08-26, not yet run.** No number in this document
> was measured. The instrument was repaired and the shop world was changed on
> 2026-08-10; this packet asks to re-run the measurement in the new world.
> **That world is `RT12/D17/P10/C19` — §2 enumerates it in full, and it is the
> world the re-run measures.** (Re-stamped a third time 2026-08-24 on `M14`'s
> own instruction, after the settle-first batch emptied: `RT11/D14/P7/C9` →
> `RT12/D14/P7/C11`; a **fourth** time the same day, `D14` → `D15`, when
> `EB-43`'s staged drafter change landed as step (5) of `R121`'s countersigned
> six-step order — see item 11 in §2; and a **fifth** time 2026-08-25,
> `RT12/D15/P7/C11` → `RT12/D17/P10/C19`, when `EB-118`'s three-character
> richness pass ran to completion and `EB-136`'s same-target binding landed
> inside the same span — see items 12–15. `C9`'s X7/X8 rarity erratum is still
> in the world; it is now inside `C19` rather than at the stamp's edge.)
> **The §4 `n` and the six §5 predictions are ENTERED, [USER] 2026-08-26**, in
> §7 step 1's order and before any seed was run. §5 records that the entered
> slate REPLACES the one R182 held outside the repo rather than transcribing
> it, and it carries two corrections raised at review and adopted with it.

**Plain English is a standing requirement for this packet.** Terms are glossed
where they first appear.

---

## 1. Why re-run at all

The shop sells companions from two slots. In July we measured how that channel
behaves and wrote down three predictions (P1, P2, P3). Two things have since
gone wrong with that measurement, and both were confirmed on 2026-08-10.

**The world changed.** [USER] restored the *rarity floor* on slot 2. A rarity
floor means the slot will not offer a card below a set quality band — here,
nothing below Uncommon. Between R116 and 2026-08-10 slot 2 had no floor, so
roughly six offers in ten were Commons at 50 gold. Now both slots offer
Uncommon or better, and the cheapest companion in the shop is 75 gold. A shelf
that stops selling cheap cards changes what a purse buys at every visit, so
the old numbers describe a shop that no longer exists. The world stamp moved
from `CONSTANTS_VERSION` 8 to 9 to record that.

**The instrument was broken.** Two defects, both in
`tier05/exp_shop_companion_channel.py`:

- **It credited purchases to the wrong shop visits.** A run walks into several
  shops. The record of what was *offered* and the record of what was *bought*
  are both kept as one flat list per run, and the old code matched a purchase
  to an offer by slot number alone. So one purchase at the third shop was
  counted as a purchase at the first and second shops too. The reported
  "slot-1 buy rate" (P1) therefore counted the visits where the player
  *declined* as visits where they bought. It was too high, and by an amount
  that grows with the number of shops a run enters.
- **It guessed the rarity of what was bought.** For slot 2 it inferred rarity
  from the price paid — "150 gold means Rare, anything else means Uncommon" —
  with a comment claiming rarity was recoverable from the price. It was not:
  while slot 2 could sell Commons at 50 gold, every Common purchase was filed
  as an Uncommon. That is precisely the bucket P3 grades, so P3 graded a
  number it had partly invented.
- **It said "gold was never the constraint" when it did not know that**
  (found 2026-08-11). The shop wrote down whether each companion offer was
  affordable *when the player walked in*, and nothing else. But a card can be
  inside the purse at the door and outside it a moment later, once the same
  visit has bought something else — and the shop had two exits that recorded
  nothing at all: the buy loop dropping a card the pilot wanted but could no
  longer pay for, and the visit ending the instant the purse fell below the
  cheapest thing left on the shelf. With no offer unaffordable *on arrival*,
  the report printed "gold was never the constraint" even if both of those
  had happened at every shop in the run. That line asserted a conclusion the
  data could not support.

All three are fixed. The purchase and offer records now carry a *visit index* (a
plain counter: which shop of this run is this), so a purchase is joined to the
offer it actually answered; the purchase record carries the card's true
rarity instead of a guess from its price; and the shop now keeps a
*priced-out log* — one line every time gold could not reach a card, written at
the moment it could not — so the money question is answered by counting
events rather than by asserting that none occurred.

## 2. One window, one world

**The registered world is `RT12/D17/P10/C19`, still including the X7/X8 rarity
erratum.** In plain English, and as the standing requirement for this
re-run: this is the world the re-run measures. Everything listed below is
inside one window, and a run of this instrument that does not report this
exact stamp is not the registered measurement.

What that one window contains, in full:

1. **The slot-2 rarity floor, restored** ([USER] 2026-08-10, S4-G10). The
   shop's wildcard companion slot rolls Uncommon-or-better in both engines;
   Commons leave the paid channel and the 50-gold band is unreachable.
2. **The instrument fixes** to `exp_shop_companion_channel` — per-visit
   purchase attribution, true slot-2 purchase rarity, the
   gold/affordability/crowd-out logging, and (2026-08-11) the priced-out log
   described below.

   The priced-out log is what makes Q2 answerable, so here is what it
   records. Every time the shop cannot reach a card, it writes one line. Each
   line says which shop of the run it was (`visit`), which card and at what
   price (`id`, `price`, `rarity`), which door it came from (`channel`:
   the character shelf or the companion channel, and `slot` for the two
   companion slots), the gold held at that instant (`gold_now`), the gold
   held when the visit began (`gold_at_visit`), and how much of it had
   already been spent at this shop (`spent_before`). Lines come in two kinds,
   marked by `residual`:

   - **the pilot's preferred pick** — it named a card and could not pay for
     it. `spent_before` of 0 means the card was out of reach the moment it
     walked in; anything higher means *this visit's own earlier purchases*
     put it out of reach, which is the case the arrival check structurally
     cannot see.
   - **the stranded shelf** — what was still for sale, and still out of
     reach, when the visit ended. A field named `exit` says whether the visit
     ended because the purse fell below the cheapest remaining card
     (`guard`) or because the pilot stopped wanting anything (`skip`); on a
     skip, only cards gold could not have covered anyway are written down, so
     "stranded" never counts a card that was merely declined.

   **This changes nothing about how a run plays.** All randomness in a run
   comes from one random number generator, and the draft policies sort rather
   than draw from it; writing a line into a list draws nothing. The proof is
   an equality, not an argument: the same seeds produce byte-identical runs
   before and after the log was added.
3. **The five R82-reopen enchant events**, which arrived with
   `RUNTEMPLATE_VERSION` 10 and move the event-pool odds in every act for
   every character. This is why the stamp read `RT10` and not `RT9`, and it is
   why no number from the original cell is a cheaper sample of this one.
4. **The three rarity promotions** (R161/R162): `friendly_visit`,
   `chain_fuse` and `careful_arrangement` move Common → Uncommon. They joined
   `C9` under its own open-window clause, before any number was published
   under `C9`. They are named here because they change what Klee's draft
   offers, and Klee is one of the three characters this cell runs — the
   companion channel is not the only thing competing for the purse.
5. **`POLICY_VERSION` 7** (R176, `fbe6e13`, 2026-08-11). The pilot — the
   automatic player that plays the cards the drafter picked — now places a
   value on two card effects it previously valued at nothing: copying a
   companion held in hand, and replaying the next companion played
   (`PILOT_COMPANION_COPY_VALUE` = 1.5 inside `_tempo_value`;
   `PILOT_WEIGHTS_VERSION` 1 → 2). Cards carrying those effects used to score
   at or below zero and so were never played at all; now they are reachable.
   **Said plainly: this moves every Klee tier0.5 number.** Klee (demolition) is
   one of the three characters this cell runs, so the Klee arm's baseline is
   not the baseline any P6-era intuition was formed against. **Write the §5
   predictions knowing that.** The stamp reads `P7`, not `P6`, for this reason,
   and no pre-P7 Klee number is a cheaper sample of this one.
6. **The Nimble enchantment repair** (`5c9c01a`, 2026-08-11). Three defects in
   the enchantment rider that grants Block: it was being bought more than once
   per card play, it was inert on cards that gain Block *next* turn, and it
   could weld itself onto a skill that gains no Block at all. This is defect
   work and it rides inside `RUNTEMPLATE` 10 with no version bump, because it
   moves no number that this cell reads: the three profiles this cell runs —
   `klee`/demolition, `furina`/salon, `kokomi`/priest — were re-run on the same
   seeds either side of the repair and came back byte-identical. It is named
   here for completeness, not because it changes the world under measurement.

7. **`RUNTEMPLATE_VERSION` 11** (the coordinated 2026-08-13 window,
   `EB-82` + `EB-85`). **This packet is re-stamped `RT10` → `RT11` for it, on
   `M14`'s own instruction** — the row says the window lands, the packet is
   re-stamped if the world moved, and only then is the slate entered. The
   world moved, so the re-stamp is done and **entering the slate is the next
   step**; nothing in `§5` has been filled and no seed has been run.
   What `RT11` adds that this cell can see:
   - **A third act-3 event.** `grave_of_the_forgotten` joins the act-3 pool
     (2 own → 3 own), so act-3 event odds move for every character — the same
     shape of change as item 3, one act further in. Its Accept branch grants
     an **event** relic, `forgotten_soul`, which no reward, Neow or Ancient
     roll can reach; the shop cannot sell it and this cell's arms cannot draft
     it, but a run that took it carries `damage_per_exhaust` into every later
     fight, which moves how far a run gets and therefore how many shops it
     visits.
   - **What an enchant event may target and pay** (five fixes against
     `sts2.dll` v0.107.1). The one that reaches this cell hardest is Swift:
     it has no card-type override in the game, so **Self-Help Book's third
     reading is live on Klee's printed starter**, where it was locked for all
     of `RT10`. Klee/demolition is one of the three profiles this cell runs.
   **Unlike item 6, this is not named for completeness.** Item 6 was proved
   byte-identical on these three profiles either side of the repair; this one
   is not, and is not claimed to be. Every Klee and Furina number in the
   `RT10` world is archive for this cell. The twelve-arm re-baseline taken at
   this bump was `review/active/sitting-reads-2026-08-13.md`, **and it is no
   longer the table to author the `§5` predictions against** — it has been
   superseded twice since, and the current one is named at §2.1. Each
   superseded table stands as published and is not rewritten (R101b).

8. **`RUNTEMPLATE_VERSION` 12** (the window-2 correctness batch, `EB-104`,
   2026-08-13 — five run-layer fixes under one coordinated bump). Two of them
   are this cell's own subject:
   - **`EB-102` — the shop finally receives the run's Featured Banner.**
     `RunContext.resolve_shop` omitted `banner=`, so the shop could sell a
     5-star the banner had excluded from every reward screen. This is the
     engineering blocker `M14` named, and it landed **before** this re-run
     exactly as `EB-104`'s first ordering constraint required. It changes which
     card `rng.choice` lands on, so **every §4.7 shop-channel figure taken
     under `C9` renumbers** — including any figure quoted while this packet was
     stamped `RT11`.
   - **`EB-112` — event card-reward screens roll rarity through
     `RARITY_ODDS`** like every other reward screen: 20.0% Rare per offer
     becomes 5.0%, on three shipped options in acts 1 and 2, for every
     character. `RARITY_ODDS` itself is unmoved; only the site that failed to
     consult it.
   The other three — `EB-103` (potion capacity derived from held relics on
   read), `EB-110` (the rest-site heal floors where it rounded) and `EB-111`
   (Book of Five Rings counts event deck-adds) — sell nothing, but they change
   how far a run gets and therefore how many shops it visits.
9. **`CONSTANTS_VERSION` 10, then 11.** `C10` is the tier0 engine half of the
   same window-2 batch: seven combat-kernel fixes, one of which (`EB-96`, a
   sleeping enemy is a side-turn participant) moves a frozen
   calibration-battery number and two Act-1 bodies. `C11` is the
   Artifact-coexistence + Kokomi-rotation ruling of 2026-08-23. Its Artifact
   half is C#-only and moves **no** sim number. Its **Kokomi half is engine
   behaviour and does move numbers**: a Status or a Curse is never one of her
   cards, so she pays no Charge and no Burst particle for exhausting one, and
   every pre-`C11` Kokomi combat number is archive. Kokomi (priest) is one of
   the three profiles this cell runs.
10. **`EB-69`, the Kokomi pool fill** (R198, 2026-08-23) — **content, carrying
    no version integer of its own, and the largest single change to what this
    cell measures.** Fourteen cards and fourteen upgrade rows land on Kokomi's
    sheet, 62 → 76 rows, and her draftable reward pool goes **56 → 70 cards**
    (common / uncommon / rare, 27/20/9 → 31/26/13). The character shelf and the
    companion channel compete for one purse, so this changes what the shelf
    offers at every Kokomi visit. **No pre-fill Kokomi number is a cheaper
    sample of this one.** It is enumerated here precisely because it carries no
    stamp: leaving it to the stamp to imply would leave it invisible.
11. **`DRAFTER_VERSION` 15** (`EB-43`, 2026-08-24 — step (5) of `R121`'s
    countersigned six-step order, landed once step (4)'s blind grade released
    the `D14` pin the branch had been staged behind since 2026-08-06). The
    drafter's "is this deck's core finished?" test (`core_complete`) and its
    progress meter (`_core_progress`) now ask the **spotlight** plan for a
    machinery *payoff* as well as machinery, so `limelight` alone stops
    counting as a finished engine.

    **Does this cell read anything drafter-side? Yes, and directly.** The shop
    instrument is a tier-0.5 instrument, and the shop's buy policy **reuses the
    draft policy's valuation verbatim** (`shop.visit_shop`, §5 of the shop
    rules: buy a card iff the policy would draft it and gold allows). A `D`
    move is therefore not a distant world change for this cell — it sits inside
    the shelf decision this cell measures, as well as inside every draft screen
    the run walks. That is why the field is named here rather than left to the
    stamp to imply, and it is why the re-stamp was owed at all.

    **What this particular `D` move reaches, stated exactly.** Both changed
    sites sit inside `if archetype == "spotlight":`. None of the three profiles
    this cell runs — `klee`/demolition, `furina`/salon, `kokomi`/priest — is a
    spotlight arm, so for all three the predicate and the meter return at
    `D15` exactly what they returned at `D14`. The twelve-arm re-baseline taken
    at the bump agrees: eleven of the twelve arms printed identically on every
    column, and the only arm that moved is `furina`/spotlight, which this cell
    does not run. **This is neither item 6's proof nor item 7's disclaimer.**
    No same-seed re-run of *this cell's own* arms was taken either side of the
    bump, so nothing byte-identical is claimed here; what is claimed is a
    code-path argument that is exact, corroborated by the re-baseline. Every
    tier-0.5 number taken at `D14` is archive under R68 whichever arm it came
    from. **The "must read `D15`" clause this item carried is superseded by
    item 13: the registered `D` is now 17, and a report of this cell that does
    not read `D17` is not this registration's measurement.** Item 11's own
    conclusion — that the `D` move reached none of these three arms — was true
    of `D15` and is **not** true of `D16` or `D17`, which is why item 13 says so
    in its own words rather than inheriting this one's.

12. **`CONSTANTS_VERSION` 11 → 19 — eight bumps, and they are the `EB-118`
    three-character richness pass plus `EB-136`.** Named one by one, with what
    each reaches of `klee`/demolition, `furina`/salon and `kokomi`/priest,
    because "eight bumps" left to the stamp would hide which arms moved:
    - **`C12`** (2026-08-24, `9d7c9a2`; ground R179/M15) — the Phase-1 cleanup
      batch: twenty sheet rows, fifteen Furina cards losing an incidental
      `raise_fanfare_cap` rider, the Block-reader family losing zero-base
      Fanfare readers, `blast_radius` gaining a chosen discard. **klee YES,
      furina YES, kokomi NO.**
    - **`C13`** (2026-08-24, `1499dcc`; R201/R203/R204/R194) — the Phase-2
      integration window: `big_badda_boom` re-bodied, **twelve `place_bomb`
      rows leave `target: random_enemy`**, Explosives Workshop becomes a
      per-rotation power, `deep_breath` converts to `choose_one`. **klee YES
      (heavily), furina YES, kokomi NO** — her sheet and engine path are
      untouched, which the block calls her arms' own control.
    - **`C14`** (R205, [USER] 2026-08-24) — `deep_breath`'s mode 2 alone.
      **furina YES** (it is a Furina Uncommon any arm can draft), **klee NO,
      kokomi NO** — neither pool holds a modal card. Its drafted price is
      measured unmoved (0.6000 → 0.6000 on both faces), so this is a combat
      reach, not a shelf-score one.
    - **`C15`** (R202, [USER] 2026-08-24; landed 2026-08-25) — Window 1's
      label pass: sixteen `role` conversions and five `archetypes` changes over
      nineteen cards, no body or cost moving. **YES, ALL THREE, and it is the
      widest DRAFTING reach in the range** — `is_on_plan_payoff` is literally
      `role == "payoff" and archetype in card.archetypes`, which is inside the
      shelf decision this cell measures. Payoff supply: klee/demolition
      **10 → 7**, furina/salon **9 → 5**, kokomi/priest **14 → 11**.
    - **`C16`** (R202 + R205, [USER] 2026-08-24; landed 2026-08-25) —
      Window 2's three Kokomi bodies plus `encore_performance`'s ruled
      `{retain: true}`. **kokomi YES** (`moon_signal` −0.5000 → 1.0000,
      `crane_wing` 6.0000 → 4.0000, `tighten_the_cords` 3.0000 → 5.0000).
      **furina YES on the run layer** — `model.rest_action` filters smith
      candidates through `upgrades.has_upgrade`, so a Rare that had no upgrade
      path was never a candidate and now is. **klee NO** — the block states
      "KLEE IS UNTOUCHED".
    - **`C17`** (R208, with item (f) ruled late by R209, [USER] 2026-08-25) —
      Window 2b's five bodies across all three sheets. **YES, ALL THREE.**
      Prices moved on every one: `sparkly_explosion` 9.7500 → 10.5000,
      `standing_room_only` 10.0000 → 3.0000, `dramatic_entrance`
      6.0000 → 7.0000, `undertow` 5.0000 → 6.0000, `depths_judgment`
      6.0000 → 11.0000.
    - **`C18`** (R210, [USER] 2026-08-25) — `EB-136`'s same-target binding.
      **Not a sheet window: no printed number, label, delta or dial moves, so
      `_static_power` is unchanged and the shelf SCORE does not move.** What
      moves is how the resolver aims — `target: enemy` ops bind to one creature
      at card-play construction instead of re-resolving per op. **YES, ALL
      THREE, and the anchor too.** Its route into this cell is the one items
      8's `EB-103`/`EB-110`/`EB-111` travel: combat resolution → HP and run
      length → **how many shops a run visits and with what purse**.
    - **`C19`** (R211, [USER] 2026-08-25, `487dc9a`) — Window 3's card-body
      pass: eight rows, five new and three rewrites keeping their ids.
      **YES, ALL THREE.** Klee gains three `spend_spark` sinks, Furina gains
      `change_the_bill` and `take_it_from_the_top`, and Kokomi's `pearl_barrage`,
      `shell_of_sanctuary` and `the_tide_remembers` are rewritten in place.
      **Two things ride with it that this cell must carry.** (i) A named
      two-engine gap: the generator cannot emit `conditional_block` /
      `conditional_damage` deltas, so `hold_the_line` and
      `take_it_from_the_top` ship a campfire upgrade **in the sim and none in
      the live game** (BACKLOG `EB-140`). **This cell is the sim, so both
      upgrades are live for it.** (ii) `W3`'s numbers were declared
      **DIAGNOSTIC** at the ruling: the pilot has no hold-versus-spend term for
      Sparks, so it spends the bank the moment a sink is legal, and its scorer
      reads neither new Furina row's state nor Tide of Names' payout. Those
      rows contribute **floors**, and a null on them is not evidence.

13. **`DRAFTER_VERSION` 15 → 16 → 17, and this is the field that matters most
    to this cell.** Item 11 established why: the shop's buy policy reuses the
    draft policy's valuation verbatim, so a `D` move sits inside the shelf
    decision this cell measures. **Item 11 then concluded that `D15` reached
    none of these three arms because it was confined to the spotlight limb.
    That reasoning does NOT carry forward, and the difference is the single
    most important sentence in this re-stamp:** `D16` and `D17` are **price
    table** moves, and a price is read on every shelf entry in every arm.
    - **`D16`** (`EB-118` Phase 2, 2026-08-24, `6056a05`; the 0.6 share
      ratified by R205, the ratify-or-move call filed as QUEUE `M41`). No
      drafter code and no dial value moved — what moved is which rows the
      existing dials reach. `STATIC_ETHEREAL_SHARE` now reaches a draftable
      row: **`big_badda_boom` prices 8.0000 → 4.8000**. It is a Klee **Common**,
      so it is on the shelf constantly. **klee YES, furina NO, kokomi NO.**
    - **`D17`** (R211, [USER] 2026-08-25) — the first bump in the series where
      the drafter learns a **cost** rather than a value.
      `STATIC_SPARK_SPEND_COST = 2.5` gives the `spend_spark` branch of
      `_op_price` its own live dial, and `spotlight_moved_this_turn` joins
      `STATIC_STATE_CONDITIONS` at share 0.167. **Both values are
      [USER]-overridable and each lives in exactly one constant.** **Exactly
      five rows move, and no others** — `STATIC_SPARK_VALUE` stayed at 0.0, so
      all eleven shipped Klee Spark rows are unchanged to four decimals:

      | row | character | base | upgraded |
      |---|---|---|---|
      | `powder_charge` | klee | 7.0000 → **2.0000** | 10.0000 → **5.0000** |
      | `hold_the_line` | klee | 5.0000 → **0.0000** | 8.0000 → **3.0000** |
      | `smoke_and_sparks` | klee | 6.0000 → **1.0000** | 8.0000 → **3.0000** |
      | `take_it_from_the_top` | furina | 5.0000 → **6.6700** | 5.0000 → **7.3380** |
      | `curtain_cue` | furina | 0.0000 → **0.4002** | → **0.7002** |

      (`directors_cut` does **not** move at any share — both its branches pay
      in dead dials.) **klee YES, furina YES, kokomi NO** — no Kokomi row
      prints either construct. **And the offer-screen consequence is named
      rather than left implicit:** in a `demolition` draft `hold_the_line`
      scores **0.00**, below `DRAFT_SKIP_THRESHOLD`. This dial can turn a Klee
      shelf entry into one the buy policy will not buy at all, which is
      precisely the decision this cell instruments.

14. **`POLICY_VERSION` 7 → 8 → 9 → 10, with `PILOT_WEIGHTS_VERSION` 2 → 5
    beside it** (one weights bump per policy bump). The pilot is what plays the
    cards the drafter and the shop bought, so it moves run length and therefore
    shop count.
    - **`P8`** (`EB-118` Phase 2A, 2026-08-24, `d3bf0e0`; window order R191, the
      gate that held it retired by R204) — `PILOT_POLICIES_ENABLED` False →
      True. Klee bomb placement stops resolving to lowest-HP and asks
      `bomb_placement_target`; a chosen `exhaust_from` stops spending
      `_worst_card` and asks `exhaust_victim`. **klee YES, kokomi YES, furina
      NO — and the furina answer is MEASURED, not argued: `furina/salon` was
      byte-identical across the switch.**
    - **`P9`** (`EB-118` Phase 2C, 2026-08-24, `b343008`) — `MODE_CHOOSER_ENABLED`
      False → True; `effects._chosen_mode` asks `policy.choose_mode`. **furina
      YES** (`deep_breath` is the only modal card in the repo), **klee NO,
      kokomi NO.** The drafter's number does not move with it, so like `C14`
      this is a combat reach, not a shelf-score one.
    - **`P10`** (R211, [USER] 2026-08-25) — `policy.exhaust_victim`'s default
      payout hook becomes `formula_aware_payout`. **kokomi YES, klee NO,
      furina NO.** Exactly two rows on any sheet print an `exhaust_selection_*`
      formula — `pearl_barrage` and `the_tide_remembers`, both Kokomi, both
      draftable on-plan `priest` payoffs — and the hook returns 0.0 for every
      card printing none. **Grade that evidence as a third kind:** it is
      neither item 6's byte-identity proof nor item 11's pure code-path
      argument, but a **test assertion** (`test_eb118_policies.test_no_existing_carriers_pick_moved`
      sweeps every chosen-Exhaust carrier on every sheet), and that test exists
      *because* it replaced a scratch run that would have been provably
      bit-identical to baseline. No same-seed re-run of this cell's own klee or
      furina arms was taken across it.

15. **Content and derived pools that carry no version integer, on item 10's
    precedent — and one of them is the sharpest change in this whole
    re-stamp.**
    - **The draftable pool grew for two of the three characters, which
      RENUMBERS THE SHELF.** `shop_offer` rolls `rarity` through the unmoved
      `RARITY_ODDS` and then `rng.choice` over the character's whole bucket
      (`tier05/shop.py:88-95`, `tier05/rewards.character_pool`) — **not**
      archetype-filtered. Klee's draftable pool goes **71 → 74** and Furina's
      **76 → 78**, both entirely in the **Uncommon** bucket (klee 28 → 31,
      furina 35 → 37), from `C19`'s five new rows. So **the same rng draw maps
      to a different card from the first Uncommon roll of the run onward** for
      klee/demolition and furina/salon: a hard renumber of the shelf itself, on
      top of every price move above, and invisible from the stamp unless
      written down. **Kokomi's pool is unmoved in membership AND in order** —
      the same 76 sheet ids at the same file positions, 70 draftable at
      31/26/13, exactly item 10's figures — so the same rng state yields her
      the same card; what moved for her is the **price** of what appears, not
      which card appears.
    - **`demolition_commons` 8 → 7 members** (`C15`). The pool is derived at
      load as every non-kit Common carrying the `demolition` tag, so
      `big_badda_boom`'s tag drop takes `secret_stash`'s in-fight add-pool from
      eight to seven, in both engines. **klee/demolition only**, and it is an
      in-fight distribution change rather than a drafting one.
    - **The smith candidate set moved for Furina** (`C16`). `model.rest_action`
      filters smith candidates through `upgrades.has_upgrade`, so
      `encore_performance` — a Rare with no upgrade path — was never a
      candidate and now is. **The candidate set moved even though the card's
      own drafted price did not.**

### 2.1 The table to author the `§5` predictions against

**`review/active/sitting-reads-2026-08-25-c19-d17-p10.md`** — twelve arms at
`RT12/D17/P10/C19`, taken on `main` = `a247f25`, all twelve in one pass with
`game_ref/` present, so both `real_*` floors sit in the main tables
(`real_ironclad` 5.2% win / 65.5% act-1, `real_silent` 1.2% / 54.1%). It
supersedes `review/active/sitting-reads-2026-08-24.md`, which item 11 and the
`M14` row used to name, and `review/active/sitting-reads-2026-08-24-c13-d16.md`
before that; each stands as published (R101b).

**It is the read at this packet's world, and that is checkable rather than
assumed.** The only diff between `a247f25` and this packet's re-stamp point,
`main` = `1eb5b45`, is four documentation files and one lint tool — no
`tier0/`, `tier05/` or `content/` file, and no version integer. So no re-take
was owed at the re-stamp and none was made.

**Three properties of it a prediction-writer must know.** (i) **Its Δ column
spans `C13` → `C19`**, five `CONSTANTS_VERSION` bumps plus `D16` → `D17` and
`P7` → `P10`, so **no row's Δ is attributable to any one of items 12–14
alone**, and none is attempted. (ii) **It has no control set and says so**:
`C18` moved the anchor's own combat behaviour, so `ref_ironclad` and both
`real_*` floors moved with the roster. (iii) **It publishes DIAGNOSTIC-SCOPED,
not as a milestone table** — three of `W3`'s eight rows are measured by an
instrument that cannot see what they print, so their contribution is a floor.
The three arms this cell runs read **`klee/demolition` 5.1%** win / 82.4%
act-1, **`furina/salon` 2.5%** / 50.5%, **`kokomi/priest` 0.9%** / **45.0%** —
and that last act-1 figure, 39.9% → 45.0%, is the one interval separation
anywhere in the table.

**`M14`'s settle-first batch is still empty, and this is the FIFTH re-stamp.**
The batch emptied on 2026-08-24: `EB-70` left it at R195 ([USER] paused the
starter-offer retune pending the Klee-rework design sweep) and `EB-69` was the
last item to land. Nothing has re-entered it. **What moved between the fourth
re-stamp and this one is not `M14`'s batch at all** — it is `EB-118`'s
three-character richness pass running to completion (`C12`–`C17`, `C19`, `D16`,
`D17`, `P8`–`P10`) with `EB-136`'s `C18` inside the same span, work this cell
does not gate and did not wait for.

**The third re-stamp called itself final and it was not; the fourth said so and
did not repeat the claim; this one does not make it either.** What R182
guarantees is the *sequence*, not that no further field moves before [USER]
reaches the slate — and the sequence has now handled the case three times
running, identically: the world moves, the packet catches up, then the slate is
entered, then the countersign.

**One honest note on how large this catch-up is, because it is much larger than
the last two.** The fourth re-stamp moved one field by one integer and could
argue, exactly, that the change reached none of this cell's three arms. This
one moves three fields across thirteen bumps, and **it cannot make that
argument and does not try**: items 12–15 reach all three arms, the shelf is
renumbered for two of them (item 15), and `D16`/`D17` move prices the buy
policy reads on every shelf entry (item 13). Everything above is nonetheless
inside one settled world, and the within-cell arm contrast Q1–Q4 asks is
unaffected for the reason it always was — both arms sit in that one world and
differ only by the `companions` flag.

What remains on the `M14` row is **entering the ruled §5 slate and then the
countersign** — in that order, and neither is done here.

The floor restoration, the instrument repair and the rarity erratum land
together, in the same commit range, under one stamp (`CONSTANTS_VERSION` 9).
The pilot change is a separate stamp component (`POLICY_VERSION`), and it
landed after them, on 2026-08-11; the registered world is the one that holds
all of it.

On the one-variable rule (EXPERIMENTS, D4: one measurement window contains
one change to the *world*), stated without softening:

- The **instrument repair** is not a world change at all. It changes only
  what we write down about a game that plays identically either way. The new
  fields are additive: nothing reads them to make a decision and none of them
  draws from the run's random number stream, so a run plays out the same
  whether or not they are recorded. That was checked by re-running the cell's
  own arms on the same seeds and comparing the results before and after: they
  match exactly.
- The **slot-2 floor** is the world change this cell is *about*, and it is
  the only change inside the channel under measurement.
- The **enchant events** and the **rarity promotions** are world changes
  outside the channel. They are not variables this cell manipulates — they
  are the same in both arms, and the arms differ only by the `companions`
  flag — but they are honestly part of the world, and that is why they are
  named above rather than left to the stamp to imply. The cost of carrying
  them is that this cell's absolute numbers are not comparable to any
  pre-C9 read; the within-cell arm contrast, which is what Q1–Q4 ask, is
  unaffected because both arms sit in the same world.
- The **pilot change (P7)** is the same kind of thing: a world change outside
  the channel. It is identical in both arms, so it cannot create or hide an
  arm difference. What it does do is move the Klee arm's absolute level, which
  is why it is named rather than left to the stamp. Any Klee number from
  before 2026-08-11 is a different world.
- The **Nimble repair** is not a world change for this cell at all: the three
  profiles it runs are byte-identical across it on the same seeds.
- The **window-2 batch, `C11` and `EB-69`** (items 8–10) are world changes
  outside the channel, on the same footing as the enchant events and `P7`:
  identical in both arms, so none of them can create or hide an arm
  difference, and all of them named rather than left to the stamp. `EB-102` is
  the one exception to "outside the channel" — it is inside it, and it is a
  **repair to the shop this cell measures**, landed before the run precisely so
  the run does not measure the defect. The cost is the same cost item 4 and
  item 5 carry, one size larger: this cell's absolute numbers are comparable to
  no earlier read at all, and the within-cell arm contrast that Q1–Q4 ask is
  unaffected because both arms sit in one world.
- The **`D15` drafter change** (item 11) is a world change **inside** the
  machinery this cell uses — the shop buys through the draft policy's own
  valuation — but it is confined to the spotlight limb, which none of this
  cell's three arms selects. It is therefore identical in both arms twice over:
  once because both arms sit in one world, and once because neither arm reaches
  the changed code at all. It is named rather than left to the stamp because
  "the shop cannot see the drafter" would be false, and the reason it moves no
  number here is a specific one worth writing down rather than a general one.
- The **`EB-118` richness pass and `EB-136`** (items 12–15) are world changes
  outside the channel, on the same footing as everything above: identical in
  both arms, so none of them can create or hide an arm difference, and all of
  them named rather than left to the stamp. **Two of them are inside the
  machinery this cell uses, and the previous bullet's escape hatch is not
  available to either.** `D16` and `D17` move the drafter's PRICE TABLE, and
  the shop buys a card iff the draft policy would draft it — so a price move is
  read on every shelf entry in every arm, not confined to a limb no arm
  selects. And item 15's pool growth **renumbers the shelf** for klee and
  furina: the rarity odds are unmoved, but `rng.choice` now maps the same draw
  to a different card out of a larger Uncommon bucket. The cost is the cost
  items 4, 5 and 8 already carry, larger again: **this cell's absolute numbers
  are comparable to no earlier read at all.** The within-cell arm contrast is
  unaffected, and that is the only thing Q1–Q4 rest on.
- **What is NOT claimed for items 12–15.** No same-seed byte-identity re-run of
  this cell's own three arms was taken either side of any of these bumps, and
  none is asserted — item 6's proof shape is not available here and is not
  borrowed. What is offered instead is per-bump reach, named arm by arm, with
  the evidence for each labelled as what it is: measured (`furina/salon`
  byte-identical across `P8`), code-path (`P10`'s two-carrier scope, `C14`'s
  and `P9`'s "no modal card in this pool"), or test-asserted (`P10`'s
  carrier sweep). **Where a bump reaches an arm, it is stated plainly rather
  than argued down.**

Landing them apart would be worse, not better. It would mean either measuring
the new world with a broken instrument, or measuring the old world with the
fixed one — and the old world is already archive. One window is the honest
shape.

**What this costs:** every §4.7 shop number published under C6, C7 or C8 —
including the whole original SHOP-P1/P2/P3 cell — is archive. Archived numbers
are banner-marked where they were published and are never rewritten (R101b).

## 3. Questions

**Q1 — the true slot-2 purchase mix under the floor.** Of the slot-2
companions actually bought, what fraction are Uncommon and what fraction are
Rare? This is P3 asked honestly for the first time: with true rarities off the
purchase record, and in a world where Common is not on the shelf at all.

**Q2 — the money question.** Was a preferred purchase ever priced out? S4-G10
raises this because runs end with roughly 220 gold unspent, which suggests
money is *not* the constraint. A purchase log cannot settle it, since a
purchase log only records what the purse could already reach.

The question is now answerable, and in three separate parts rather than one.
The instrument reports each of them as a count:

1. **Priced out at the door.** How many companion offers cost more than the
   gold held when the visit began. This is the arrival check that already
   existed.
2. **Priced out during the visit.** How many times the pilot named a card it
   then could not pay for — and, of those, how many were affordable when it
   walked in and stopped being affordable because it had already bought
   something else at that same shop. Until 2026-08-11 this event was dropped
   on the floor; it is now the priced-out log's first kind of line
   (`spent_before` greater than zero is the "priced out by its own earlier
   buys" case).
3. **Left on the shelf.** How many cards were still for sale and still out of
   reach when the visit ended — the purse having run below the cheapest thing
   left. This exit was also silent before; it is the log's second kind of
   line.

Together these are what "was a preferred purchase ever priced out?" actually
means. Note that part 2 is the *narrowest* reading of "preferred": it is the
pilot's own top pick at that moment, not merely something on the shelf.

**Q3 — the true P1 buy rate.** With purchases joined to their own visit, what
fraction of the visits that offered slot 1 ended in a slot-1 purchase? The
pre-registered band for P1 was 10–35% of visits. The old figure was inflated
by the attribution defect, so this is a first honest read rather than a
comparison.

**Q4 — crowding out, at visit resolution (descriptive).** Within a single
visit, companions are resolved before the relic shelf is offered, so a
companion purchase always comes first in time. The question is whether it
leaves the purse too thin for the relic: what is the relic buy rate in visits
where a companion was bought, against visits where none was? The existing
crowd-out block compares run totals across two arms; this is the same question
at the resolution where the trade-off actually happens.

**Not asked here.** Whether any of these numbers is good or bad, and whether
the channel should be re-priced or re-stocked. That is a design call and it is
[USER]'s, downstream of the grade.

## 4. What is measured, and with what

- Instrument: `tier05/exp_shop_companion_channel.py`, as repaired 2026-08-10
  and extended with the priced-out log 2026-08-11.
- Arms: unchanged — `companions` off against `companions` on. That flag is the
  only difference between the two arms; same seeds, same characters, same
  policy, same everything else.
- Characters: unchanged — `klee`/demolition, `furina`/salon, `kokomi`/priest.
- World: **`RT12/D17/P10/C19`** — the world enumerated in §2, the X7/X8 rarity
  erratum included. The report must carry the full run-cell stamp (`RT/D/P/C`)
  or it is not citable (R68), and it must read `RT12/D17/P10/C19` or it is not
  *this* registration's measurement.
- **The instrument PRINTS that stamp but does not ROUTE through a `Cell`, and
  the remaining fix is procedural, not an edit to the instrument.** As of
  `EB-141(a)` (`26b4b2c`, 2026-08-25) the instrument's first output line is
  `print(cells.world_stamp())` (`tier05/exp_shop_companion_channel.py:133`),
  above the byte-unchanged `§4.7 companion channel -- N runs/arm, seed
  20260725` header — so the run's own stdout names the world it came from, and
  step (0)'s check gains a witness inside the artifact. `cells.world_stamp()`
  is the same single producer `Cell.stamp()` formats, so that header cannot
  spell the world differently than a `Cell` would. **What is still missing is
  the ROUTING:** `arm()` calls `model.run_many` directly rather than running a
  `Cell` (`:109-112`). That is `EB-141(b)`, and it is **gated on this
  registration's grade** — a `Cell` carries its own seed, runs, plan
  resolution and run entry, so rerouting could move seeding or behaviour while
  the registered seed is staged to fire. **§7.1's provenance header therefore
  STAYS.** The printed stamp does not retire it: what makes the report citable
  is binding that stdout to a registration, a commit and an `n`, and no line
  the instrument prints does that. The instrument is not edited inside this
  window — a script is not tuned inside the window of the registration that is
  about to run it.
- Every output line the instrument printed **before the 2026-08-10 repair**
  still prints, so the pre-existing reads stay reproducible. The new reads are
  printed on lines labelled `NEW`. **Two of those `NEW` lines were themselves
  replaced on 2026-08-11 and the packet says which**, because "every line still
  prints" would otherwise be read as covering them: the money header gained
  `, AND DURING THE VISIT`, the counter `priced_out` was renamed
  `unaffordable_on_arrival`, and the line `NEW priced out: none -- gold was
  never the constraint` — the unsupported conclusion §1 indicts — was
  **deleted** and replaced by three counted lines. Nothing above the file's own
  `--- NEW reads (2026-08-10)` marker moved at all.

**`n` and seed — ENTERED, [USER] 2026-08-26.** These replace the packet's own
proposal, which was `RUNS = 500` per arm per character from the prior run's
convention — the only convention this cell had.

- **`RUNS` = 1,000 per arm per character** (3 characters × 2 arms × 1,000 =
  **6,000 runs**). R182 already specified this figure on 2026-08-12 and the
  `M14` row has carried it since; the entry is where it finally lands in the
  packet.
- **`SEED = 20260725`, RETAINED.** It is a module constant, not a command-line
  argument, and §7.1 does not pass it.

Keeping the seed does not make the old and new numbers comparable — the world
moved, and switching the channel on consumes randomness, so runs diverge
rather than pairing. It is kept because changing it would buy nothing and
would remove the one thing still held fixed. **The packet named raising `RUNS`
as the lever for tighter intervals on the slot-2 mix (Q1) — slot-2 purchases
are a small fraction of runs, so that count is the binding sample, not the run
count — and the doubling above is exactly that lever, taken.** Neither number
is open any longer.

## 5. Predictions — SLATE ENTERED BY [USER], 2026-08-26

Measurement law: predictions are written from design intent, before the
numbers exist, and are never revised against the run that grades them. All six
slots below are now filled, and the run had not been taken when they landed.
That is the whole of the blind, and no command enforces it (§7.1 step 3).

**This slate REPLACES the one R182 settled on 2026-08-12; it is not a
transcription of it.** R182's six values plus its trigger were decided and
held **outside the repo**, were never written into this packet, and **are not
recoverable from it** — so nothing below is claimed to reproduce them, and no
reader should treat this as R182's slate restored. It is authored fresh and
stands on its own terms. The one figure that genuinely does carry over from
R182 is §4's `n`, which the `M14` row has held in writing since 2026-08-12.
The slate was proposed at review, corrected in two places by Claude (both
marked below), and adopted by [USER] on 2026-08-26.

**Grading vocabulary**, fixed here before the read: each slot grades
**PREDICTED** (the result is inside the entered band or matches the entered
direction), **MISS** (it is not), or **SPLIT** (a slot with more than one
clause, where some clauses hold and others do not). A slot's grade never
depends on another slot's.

**One instrument note the grader needs, and it is not a prediction.** The
script prints three legacy verdict lines of its own — `P1 ... IN BAND
(10-35%)`, `P2 ... IN BAND (positive, <= +2.00pp)` and `P3 ... IN BAND
(>= 60%, DIAGNOSTIC)` — whose bands are **hardcoded from the original July
cell, not from this slate**. Two of them happen to coincide with what is
entered below (P1 with Q3's retained acceptance band, P2 with the carried-
forward winrate band). **The third does not: Q1's entered band is 80–95%, and
the instrument's `>= 60%` verdict says nothing about it.** Grade the printed
*percentages* against this section; never the instrument's own IN BAND / OUT
OF BAND word.

> **Q1 — slot-2 purchase mix. ENTERED.** Expected share of slot-2 purchases
> that are Uncommon rather than Rare: **80% – 95%**.
> **DIAGNOSTIC-ONLY — not an acceptance target.** A result outside the band
> records a fact about the shelf and the purse and nothing more; the redesign
> trigger below says in its own words that a Q1 miss alone reopens nothing.
>
> *Context for the call, not a prediction:* the old P3 band was "≥ 60%
> Uncommon", graded as a diagnostic under R14 discipline. Under the restored
> floor the offer table is 87.5% Uncommon / 12.5% Rare, and Rares cost twice
> as much, so both the shelf and the purse point the same way.

> **Q2 — the money question. ENTERED.** Is gold ever the binding constraint on
> a companion purchase? **YES, but uncommon.** Band for the share of companion
> offers that are unaffordable **on arrival**: **0% – 5%**.
>
> **"Price is not governing this channel" — BOTH clauses must hold:**
> **(1)** the arrival-unaffordable share of companion offers is **≤ 5%**, and
> **(2)** companion-slot `pick_priced_out` events **÷ shop visits ≤ 5%**.
>
> **Correction 1 (Claude, adopted 2026-08-26): clause (2) is stated in the
> units the instrument actually prints, and the mismatch is declared rather
> than glossed.** The instrument emits a **raw per-EVENT count**, not a
> per-visit share. `pick_priced_out` is a `Counter` keyed by `(where, rarity)`,
> where `where` is `"slot 1"` / `"slot 2"` for the companion channel and
> `"character shelf"` otherwise
> (`tier05/exp_shop_companion_channel.py:226-234`); the count and that
> distinguishing detail print on the `NEW preferred picks priced out
> mid-visit:` line (`:322-331`). The denominator comes from the gold line,
> `NEW gold on arrival: ... (N visits)` (`:297-303`), whose `N` is the number
> of distinct ON-arm shop visits that offered a companion — the same total the
> crowd-out block splits into `companion bought` + `none bought`. **So clause
> (2) reads: the two `slot N` keys of that detail, with the `character shelf`
> key EXCLUDED, over `N` — a per-EVENT numerator over a per-VISIT
> denominator.** That differs from a true per-visit share only where a single
> visit produces two such events, in which case this ratio reads slightly
> **high**. That is the conservative direction for a clause whose job is to
> clear the channel of suspicion, and no per-visit denominator for these
> events is printed, so it is this ratio or nothing.
>
> *Note on the slot, not a prediction:* the YES/NO stays exactly as written,
> and the instrument now supports it. Before 2026-08-11 it did not — a `NO`
> could only ever have been read off the arrival check, which is blind to a
> card that goes out of reach mid-visit, so the honest answer would have been
> "unmeasured" no matter what the run printed. The priced-out log closes that
> gap: `YES` is now falsifiable against three counts (the three parts of Q2
> in §3), and the run reports all three. The 0–5% band above refers to the
> arrival share specifically; the other two counts carry no band and are
> reported.

> **Q3 — true P1 buy rate. ENTERED.** Expected slot-1 buy rate, as a share of
> the visits that offered slot 1: **15% – 30%**. **The original 10–35% band
> STANDS as the acceptance band** in the new world; it is not replaced.
> The two are graded separately, because they do different jobs: a result
> inside 15–30% is PREDICTED; a result outside 15–30% but still inside 10–35%
> is a MISS on the prediction that does **not** breach acceptance; a result
> outside 10–35% is a MISS **and** fires the redesign trigger below.

> **Q4 — crowding out. ENTERED.** Direction: **YES** — buying a companion
> reduces the relic buy rate in the same visit. Magnitude: **approximately
> −15 pp**, relic-buy rate in visits with a companion purchase against visits
> without.
>
> *How "approximately" is read, fixed here before the run (Claude's reading of
> the entered slate, recorded rather than left to grading time):* **PREDICTED**
> if the drop lands in **−10 pp to −20 pp**; **SPLIT** if the direction holds
> (any drop at all) but the magnitude falls outside that range; **MISS** if the
> relic buy rate is equal or higher in companion-purchase visits, i.e. the
> direction is wrong.

> **P2 (winrate delta), carried forward. ENTERED — the original band STANDS:
> positive and no more than +2.0 percentage points.** Not replaced. The floor
> removes the cheap tier, so the channel is now strictly more expensive per
> card, which pushes the delta in an unobvious direction: fewer purchases,
> better ones. Graded on the instrument's mean delta across the three
> characters, which is the figure its own `P2` line prints.

> **Redesign trigger — ENTERED.** Reopen the shop design — as a design call
> for [USER] at `QUEUE`, never an engineering fix taken here — if **ANY ONE**
> of these fires:
> 1. the slot-1 buy rate falls **outside 10–35%** (Q3's acceptance band);
> 2. companion-slot `pick_priced_out` events ÷ shop visits is **> 10%** — the
>    ratio defined in Q2's Correction 1, at double the 5% clearance threshold;
> 3. the relic-buy rate falls by **≥ 20 pp** in companion-purchase visits
>    against visits without — Q4's direction at a magnitude that is crowding
>    rather than trading; or
> 4. the mean winrate delta lands **below 0 or above +2 pp** — P2's band
>    breached in either direction.
>
> **A Q1 miss ALONE does not reopen anything.** Q1 is diagnostic-only, and
> that is written here as well as at the slot so the trigger cannot be read as
> sweeping it back in.

## 6. Contamination and known limits

- **The sim models one seat.** Co-op shop behaviour is not measured here and
  cannot be; nothing in this packet speaks to it.
- **The arms are not strictly paired.** Turning the channel on consumes
  randomness, so run *N* in the on-arm is not run *N* in the off-arm with one
  thing changed — it is a different run. The read is a distribution over many
  runs, not a per-seed difference. Unchanged from the original cell.
- **Companions get first claim on the purse** by construction: the shop buys
  cards before the relic and potion shelves are offered. Q4 measures the
  consequence; it does not remove it.
- **Affordability is measured at the door *and* during the visit** (this
  limit was partly lifted on 2026-08-11). The `affordable` flag on each
  companion offer still means only what it always meant: the price was within
  the gold held when the visit began, before anything else was bought. What
  is no longer missing is the rest of the visit — the priced-out log records
  a card the pilot wanted and could not pay for after its own earlier
  purchases, and a card still for sale and still out of reach when the visit
  ended. So "was there change left afterwards" is now measured too, and it is
  reported separately from the arrival figure rather than folded into it.

  What remains unmeasured is narrower: the log records the *moments the shop
  actually reached for a card*. A card the pilot never wanted and could not
  have afforded either way is counted only if it is still on the shelf at the
  end; and no counterfactual is computed — nothing says what the run would
  have bought with more gold.
- **The drafter is a pilot, not a player.** It buys what its valuation ranks
  highest and it does not save for later. A low buy rate is evidence about
  the drafter as much as about the shop, and that limit applies to P1 and Q3
  as it always did.
- **No C# side.** The mod moved with the sim (same floor, same omission
  behaviour), but there is no C# test project and no mod-side instrument.
  Nothing in this packet is a prediction about the mod's behaviour.

## 7. What happens when it is countersigned

1. [USER] enters the ruled slate into §4 and §5 and countersigns — **in that
   order**; the filled predictions land as their own commit, before any seed in
   the registered range is run.
2. The cell runs at the §4 n and seed, under the §2 registered world
   stamp as re-stamped (`RT12/D17/P10/C19` at the fifth re-stamp).
   **The exact commands are at §7.1; nothing is left to decide at run time.**
3. The report is published with its full stamp, graded against §5 blind.
4. This packet and its EXPERIMENTS pointer leave HEAD when the grade lands.

### 7.1 The exact run, once §4/§5 are entered and the packet is countersigned

**Nothing here is a decision.** The arms, characters, seed and instrument are
all fixed above; the one value that comes from the slate is `n`. Run from the
repo root; `PYTHONPATH=.` is required for the sim entry points
(`OPERATIONS.md`).

**(0) Confirm the world, before anything else.** §2's stamp is a precondition,
not a label, and the instrument cannot check it for you (§4):

```
PYTHONPATH=. python3 -c "from tier05 import cells; v=cells.CANONICAL.versions; print('RT{RT}/D{D}/P{P}/C{C}'.format(**v))"
```

This must print exactly `RT12/D17/P10/C19`. **If it prints anything else the
world has moved again: stop, re-stamp, and do not run.**

**(1) The run.** The script takes one positional argument, the runs per arm per
character:

```
PYTHONPATH=. python3 -m tier05.exp_shop_companion_channel <RUNS> | tee review/active/shop-rerun-results-2026-08-25.txt
```

- `<RUNS>` is **§4's `n` as entered by the slate**, and the slate is now
  entered: §4 reads **1,000 per arm per character**, so the command reads
  `... 1000`, giving 3 characters × 2 arms × 1,000 = **6,000 runs**. §4
  governs; this line does not set it.
- **`SEED = 20260725` is a module constant and is not a command-line
  argument.** It is not passed and must not be changed.
- **There is no `--jobs` and there must not be**: the two arms differ by a
  monkeypatch of `shop.visit_shop`, which worker processes would not inherit.
  This runs single-process by construction.
- **THIS INSTRUMENT HAS NO SMOKE PATH, AND THAT IS A HAZARD.** Unlike the
  `EB-17p` sweep, there is
  no `--smoke` flag and no excluded seed base: *every* invocation, at any `n`,
  runs on the registered seed `20260725`. **A "does it run" check is therefore
  a read of the registered range.** The only pre-run check that is safe is an
  import, which executes no runs:
  `PYTHONPATH=. python3 -c "import tier05.exp_shop_companion_channel"` —
  verified clean at this world on 2026-08-25.

**(2) Publish the raw output with a provenance header**, on the payoff-reach
precedent — the instrument's own stdout, unedited, under a header naming the
registration, the run date, the world, the instrument and the commit. **The
instrument DOES print the live `RT/D/P/C` as its first output line** since
`EB-141(a)` (2026-08-25), so the stdout is self-stamping and step (0)'s check
has a witness inside the artifact — **but it still does not route through a
`Cell`** (`EB-141(b)`, gated on this grade), and the printed line does not
retire the header. **The provenance header is what makes the report citable**,
because it is what binds that stdout to this registration, to a commit and to
an `n` (§4). The header must carry, at minimum:

```
registration  review/active/shop-rerun-registration-2026-08-10.md §2, §4
run date      <date>
world         RT12/D17/P10/C19   (verified by step (0) at run time)
commit        <the main SHA the run was taken at>
instrument    tier05/exp_shop_companion_channel.py
n / seed      <RUNS> per arm per character / 20260725
arms          companions off vs companions on; klee/demolition,
              furina/salon, kokomi/priest
```

**(3) Grade blind against §5**, which is not edited by the grade. The grade is
its own commit.

**The output of (1) is not opened by whoever filled §5 before (3) is
recorded.** That is the blind in blind grading, and no command can enforce it.

---

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

`COUNTERSIGN` — [USER] 2026-08-26.

**No slot is open. The packet is cleared to launch**, and §7.1 fires on §4's
entered `n` = 1,000 with the registered seed. The world freezes from this line
to the graded read (R182's sequence), which is also `EB-141(b)`'s gate.

**Correction 2 (Claude, adopted 2026-08-26): this packet had no countersign
line at all.** Its three sibling registrations each end with one in exactly
this shape (`review/active/m17-sweep-reregistration-p7-2026-08-13.md`,
`review/active/eb17p-registration-draft-2026-08-08.md`,
`review/active/charge-reads-per-turn-registration-2026-08-13.md`), and both §7
step 1 and the `M14` row require a countersign before any seed is run — but
there was nowhere in the document to record one. The line is added so the act
has a home, and so that "countersigned" is a fact a reader can check here
rather than infer from a register row.

**Slate ENTERED 2026-08-26**, in §7 step 1's order and as its own commit ahead
of any run: §4's `n` = 1,000 per arm per character with `SEED = 20260725`
retained, and all six §5 slots. **It REPLACES R182's slate rather than
transcribing it** — see §5's opening.
