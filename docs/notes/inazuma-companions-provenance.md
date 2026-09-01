# inazuma-companions.yaml - comment provenance

Long comment blocks that used to sit in `docs/inazuma-companions.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## header

```
# Lifecycle: LIVING — expected to change; read it to work on the project. Status index: docs/registry/identifiers.md §15.  (lint-ok)
# Inazuma companion pool — v0.1 KICKOFF DRAFT (ships with Kokomi; docs/kokomi-kickoff-v1.md §4 governs).
# Shared colorless-style pool, same schema as mondstadt/fontaine sheets. ALL numbers PROPOSED — nothing red-penned yet.
# Roster v0.1: the starter-reserved trio (Gorou / Sayu / Shinobu, user ruling) + Thoma + Kujou Sara (4-star bench)
# + Itto as the ONE designed 5-star Rare (eligible per the slot-4 ruling: Zhongli takes slot 4; conscription's jackpot).
# RULED 2026-08-06 (R108 addendum clause, second sitting) — verbatim: "Itto enters as a COMPANION CARD, not a
#   character." His presence on this sheet stops being an inference from the reserved-character rule (unsigned R88,
#   in tension with ratified R52) and becomes a direct registration: COMPANION CARD, no roster slot, not a slot-5
#   candidate. NOTHING ON THIS SHEET CHANGED — no card was drafted, no rarity moved, no row was added by the ruling.
#   Cross-refs: tier0/DECISIONS.md R108 addendum; docs/archive/slot5-candidates-2026-08-05.md §2.3/§2.5.
# Conventions: 4-star caps at Uncommon; heals below Rare convert to Block (Charlotte precedent); 5-star Rares are the
# only true-heal slots (none designed here yet). All applies_element flags EXPLICIT (catalyst-cadence drafters must not
# auto-apply through companion hits; the Fontaine-sheet discipline).
# ERRATA NOTE (kickoff §4, on the record so it isn't "rediscovered"): Kuki Shinobu's canonical self-HP cost is DROPPED
# per Kokomi character law 1 (no self-damage in her kit or shared-pool errata). Her cards are authored costless-to-HP.
# RULED (R52, ask 9): Raiden authored below — playable characters may exist as Rare companion cards and surface in
# the conscript pool, but ONLY as a Rare payoff; the opposed lore carries the flavor. Natural rare odds (N5).
# FRAMING (v0.4 lore overlay §3) — THE POOL IS THE PEACE, NOT HER ARMY. This roster spans every Inazuma faction:
#   resistance (Gorou), Shogunate (Kujou Sara, Raiden), Yashiro (Thoma, and Sayu's Shuumatsuban), Arataki Gang
#   (Itto, Shinobu). That is not a roster accident and it is not a resistance muster — it is POST-DECREE INAZUMA
#   ANSWERING WATATSUMI'S CALL. The framing does three jobs at once: it explains why non-resistance names are in
#   a Kokomi pool at all; it sharpens Sara, who was the OPPOSING field commander and now answers to the strategist
#   who beat her; and it gives Raiden her best gloss (see her card). Read every companion here as someone who
#   CHOSE to come. Nobody in this pool was conscripted — the display family is Muster/Enlist/Rally for exactly
#   this reason, and the exhaust voice is ROTATION, never sacrifice (voice law, kokomi-cards.yaml header).
# Later scope: Kazuha (Sly/discard flavor), Heizou, Ayaka, Ayato, Yoimiya, Yae Miko 5-stars (banner roll per v1.8).
```

## gorou_inuzaka_charge

```
   # The vanguard's opening arrow. Geo leaves no aura in the reaction table (Crystallize CONSUMES); applies_element
   # false is explicit so no cadence dial can re-tag it. Starter attack-slot card (randomized_starter).
   # RENAMED to canon 2026-08-10 ([USER], QUEUE N3+N4): "Inuzaka" was canon but "Inuzaka Charge" was not — his
   # Elemental Skill is "Inuzaka All-Round Defense", the skill that plants the General's War Banner two rows down.
   # Display-only: ids are not slugs of titles here, so `gorou_inuzaka_charge` and its art key are unchanged.
```

## gorou_heart_of_the_clan

```
   # The standing banner: 2 Block a turn while the fight lasts. Sustain-through-armor, never healing (the law).
   # RENAMED to canon 2026-08-10 ([USER], QUEUE N3+N4): "Heart of the Clan" named no Gorou talent. [USER] picked
   # his Burst, "Forward Unto Victory" — checked against reserved-card-names.txt, every card sheet and the relic
   # titles before it was taken. Display-only: id `gorou_heart_of_the_clan` and its art key are unchanged.
```

## before raiden_musou_no_hitotachi

```
# ---------- RAIDEN SHOGUN (5-star Rare | the opposed apex — R52 ask 9) ----------
# Lorewise Kokomi and the Shogun are OPPOSED: Watatsumi bled for the Vision Hunt, and the Almighty answers no
# conscription. The card is therefore the DOCTRINE, not the woman — one borrowed instant of Musou, and the
# resistance leader's bitterest irony that it works. Rare payoff ONLY, per the ruling.
```

## raiden_musou_no_hitotachi

```
   # RATIFIED 2026-07-25 [USER], from 2 cost / 18 damage / no rider / no Exhaust: "3 cost, 40 damage, (lint-ok: superseded pre-ratification value)
   # vulnerable 2, applies electricity, exhaust — massive payoff for a very high cost. Rares in general
   # tend to be undertuned, so I think this is fine for a front-loaded rare, and has natural Kokomi
   # exhaust synergy." The same session ruled Navia fine as-is and Neuvillette weak-but-deferred.
   # WHAT THE BUFF CHANGES, recorded because it moves the card's class, not just its number:
   #   - It RESOLVES the Clorinde/Raiden domination flag opened one commit earlier (the open item that
   #     no lint could raise, since the two live in different nations' sheets). Clorinde is 2 cost for
   #     20 + a permanent power; Raiden is 3 cost for 40 + Vulnerable and then she is GONE. Different (lint-ok: sibling card's number)
   #     cost, different shape, and the strictly-better reading is dead in both directions.
   #   - Exhaust converts her from a recurring jackpot into a ONE-SHOT, which is what pays for 40. It is
   #     also the first companion Exhaust that is a PAYOFF rather than a brake, and it lands in the one
   #     kit that wants it: Kokomi's exhaust voice is ROTATION (sheet header, line 19), so a card that (lint-ok: sheet line number, not a game number)
   #     leaves the deck after firing is thinning it on purpose.
   #   - Vulnerable is applied AFTER the damage (StS Bash ordering), so the 40 does NOT amplify itself.
   #   - 3 cost is the FIRST in the shared companion pool (the only other 3-costs anywhere are Klee's
   #     bombs_away/all_my_treasures/playtime_forever) — so it is precedented, but it is a whole turn's
   #     energy for any character, which is the intended price and not an oversight.
   # The single slash of Musou: still the pool's biggest one-card hit by a wide margin, and electro on
   # Kokomi's ubiquitous hydro is the Electro-Charged apex. Deliberately SHAPELESS defensively — no
   # Block, no draw, no sustain: eternity is one perfect cut, and then the blade is sheathed.
   # Itto is the bruiser jackpot (14+6, 2 cost, repeatable); Raiden is the executioner jackpot.
   # The call-up can find her at natural rare odds (R52/N5 — revisit only if the sims show her busted).
   # GLOSS ([USER] ruling, v0.4 §3): the card KEEPS Musou no Hitotachi, and the reading is RECONCILIATION, not
   # irony. The retired framing called this 'the bitterest irony' — Kokomi fishing for the blade that executed
   # her people's Visions. That reading breaks the peace the whole roster is built on. The true gloss: this is
   # the peace's crowning proof. The Shogun's blade defends Watatsumi now, and Watatsumi's strategist is the
   # one who calls it. Never write the irony version again.
```
