# Glory — Fontaine face (event text)

> **Fable curation pass, 2026-09-14.** Selection only; the one fresh draft
> (the Coral Mirror) reads in register and is kept. The two demoted lines the
> gallery carries (Ranwid's honorific, the Merusee spelling in This or That?)
> ride along unchanged and are fixed in the gallery, not here.


Face: Fontaine. Zone: Glory (act 3), one of the two act-3 faces a run rolls
between (paired with Sumeru per `teyvat-nation-mapping-act3-2026-09-14.md`).
Event count: 17 (13 Glory-own + 4 all-acts, per
`sts2-map-and-events-research.md` §2's table and the harvest's own act tags).
Reused: 16, copied verbatim from `event-conversion-gallery.md`'s existing
kept Fontaine variants, cited per section below. Drafted: 1 (Reflections
snoitcelfeR — the one Glory-reachable event `teyvat-nation-mapping-
act3-2026-09-14.md` §2 flags as lacking a Fontaine row; 16/17 elsewhere).
Mechanics frozen to `docs/sts2-events-harvest.txt`: no option, number, lock,
or outcome was changed below, only words.
`tier05/content/events.yaml` currently models only 8 of these 17 as
shippable pool entries (grave_of_the_forgotten, reflections, self_help_book,
slippery_bridge, symbiote, the_future_of_potions, the_trial, this_or_that);
the other 9 (Battleworn Dummy, Crystal Sphere, Hungry for Mushrooms, Potion
Courier, Ranwid the Elder, Relic Trader, The Round Tea Party, Tinker Time,
War Historian Repy) are text-complete here but not yet in the modelled pool,
each for the reason its `events.yaml` skip-list entry already states.
Order below follows the harvest's own (alphabetical) listing order, filtered
to the act3 / act2-act3 / all-acts / untagged entries that reach Glory.
The companion Sumeru face is a separate file and workstream, not authored
here. Sources: `sts2-map-and-events-research.md` §2.1/§2.4 (which events
exist), `sts2-events-harvest.txt` (frozen mechanics), `event-conversion-
gallery.md` (reuse source + the Melusine register rules), `teyvat-nation-
mapping-act3-2026-09-14.md` §2 (the 16/17 count this file resolves to 17/17).

---

## - [ ] Battleworn Dummy

### Pressure Trial at the Institute — Fontaine / Fontaine Research Institute, Melusine technician — loose — REUSED event-conversion-gallery.md, Battleworn Dummy variant 1

Beneath the Institute's glass roof, a Melusine technician in oversized overalls wheels out a padded clockwork meka on a rail. Her ledger is already open: every strike will be logged, and the water-clock beside her drains in three measured pours. "Set the pressure valve first," she chirps. "Higher pressure, better data, better prize. But the clock does not negotiate."

- **First Valve** — Fight a 75 HP dummy. Procure 1 random Potion.
- **Second Valve** — Fight a 150 HP dummy. Upgrade 2 random cards.
- **Third Valve** — Fight a 300 HP dummy. Obtain a random Relic.
- **(all valves)** — You have 3 turns to defeat the dummy. Failing results in no reward.

Mechanics check: matches harvest (75/150/300 HP dummy, 3-turn cap, potion / 2-upgrade / relic rewards, no reward on failure).

@pages.VICTORY.description — The water-clock is not yet empty when the meka's padding gives way. The technician closes her ledger and hands over what that valve was rated for.
@pages.DEFEAT.description — The water-clock runs dry with the meka still standing. The technician closes her ledger without writing anything, which is somehow worse.

---

## - [ ] Crystal Sphere

### Sounding the Beryl Shelf — Fontaine / Melusines of Merusea Village, salvage crew voice — loose — REUSED event-conversion-gallery.md, Crystal Sphere variant 2

The Melusines of Merusea Village have gridded a sunken freight lot on the Beryl Region shelf: eleven squares by eleven of grey silt, cargo somewhere beneath it. A harbormistress in an oilskin cap explains the sounding charges — one clears a single square, or a three-by-three sweep — and warns that only crates bared completely can be winched up. The big one at the lot's heart is four squares across; three soundings will never strip it.

- **Buy Sounding Charges** — Pay 51-99 Gold. Divine 3 times.
- **Take the Meropide Tab** — Gain a Debt. Divine 6 times.
- (Surfaced cargo can be claimed in any order or waved off entirely. One crate is not cargo (Doubt); it opens itself on the deck.)

Mechanics check: matches harvest (51-99 gold for 3 divinations vs. a Debt for 6; the 11x11 grid, small/big divination sizes, reward table, and Doubt's instant add are all unchanged). Flag: not in `tier05/content/events.yaml`'s pool — the grid-uncover minigame and Divine/Debt ops are unbuilt, per the file's own skip list; text only, nothing invented.

---

## - [ ] Grave of the Forgotten

### The Ledger of Sunken Names — Fontaine / Melusines of Merusea Village — gentle, bureaucratic grief — REUSED event-conversion-gallery.md, Grave of the Forgotten variant 2

Beneath Merusea Village, a Melusine tends a coral shelf of keepsakes left by people the Court of Fontaine never entered among the drowned. She has copied every name into a ledger nobody has ever asked to read. You may take one keepsake away with you, she says, or you may read a name aloud — though the primordial water still remembers how to take back what it made.

- **Accept the Keepsake** — Obtain Sunken Keepsake (Forgotten Soul relic): whenever you Exhaust a card, deal 1 damage to a random enemy.
- **Read the Name Aloud** — Add Dissolution (Decay curse) to your Deck. Enchant a card that Exhausts with Soul's Power (this card loses Exhaust).
- (Reading aloud is locked if you have no cards with Exhaust that can be Enchanted.)

Mechanics check: matches harvest and the shipped `grave_of_the_forgotten` row (relic_id forgotten_soul / curse_decay + souls_power enchant, same lock). Flag: the shipped in-game text uses the gallery's Liyue variant (The Nameless Cairn, ruled R231) for the world at large; this Fontaine face uses the gallery's own kept Fontaine variant (#2) instead — ids, costs and effects are identical, only the words differ.

---

## - [ ] Hungry for Mushrooms

### The Meropide Infirmary Rounds — Fontaine / Melusines of the Fortress of Meropide — loose — REUSED event-conversion-gallery.md, Hungry for Mushrooms variant 3

Down in the Fortress of Meropide, a Melusine nurse pulls a curtain around your cot and sets two vials on the tray with great ceremony. One is cloudy and thick, brewed from Fontemer kelp to "make you bigger, and slower to wake." The other is clear and stings the eyes from across the room; she assures you it sharpens everything a person already knows how to do. Both are, regrettably, non-refundable.

- **Drink the Deepwater Draught** — Obtain Deepwater Draught (Big Mushroom relic). Upon pickup, raise your Max HP by 20. At the start of each combat, draw 2 fewer cards.
- **Drink the Clarity Tincture** — Obtain Clarity Tincture (Fragrant Mushroom relic). Upon pickup, lose 15 HP and Upgrade 3 random cards.

Mechanics check: matches harvest. Flag: not in `events.yaml`'s pool — Big Mushroom's draw-penalty needs a hook the sim doesn't have yet (`combat_start_draw` ignores negative amounts), per the file's own skip list; text only, no mechanic invented.

---

Loss: {character} did not wake from the Clarity Tincture at the [gold]{event}[/gold].

## - [ ] Potion Courier

### The Undeliverable Parcels — Fontaine / Melusines (Merusea Village postal run, Beryl Region) — loose — REUSED event-conversion-gallery.md, Potion Courier variant 3

The aquabus to Merusea Village has stalled off the Beryl Region shallows, and its Melusine postmistress has laid the undeliverable parcels along the pier in tidy, apologetic rows. Most are returns from the Fontaine Research Institute — labels dissolved, contents entirely unrepentant. One box, set slightly apart, still smells of the Court of Fontaine's better apothecaries.

- **Take the Returned Batch** — Procure 3 unlabelled draughts (Foul Potion).
- **Ask After the Good Box** — Procure 1 random Court apothecary tonic (Uncommon Potion).

Mechanics check: matches harvest. Flag: not in `events.yaml`'s pool — Foul Potion is unmodelled (without it, "3 Foul Potions" would invert against "1 random potion"), per the file's own skip list; text only.

---

## - [ ] Ranwid the Elder

### Grandmother Coralie of Merusea Village — Fontaine / Melusines beneath the Salacia — loose — REUSED event-conversion-gallery.md, Ranwid the Elder variant 3

Merusea Village hangs quiet in the blue below Fontaine, and the oldest Melusine there keeps a driftwood counter of everything the water has handed back. She has no use for any of it; she simply likes the ceremony of exchange, and the Marechaussee Phantom long ago stopped asking where her stock comes from. "A courtesy for a courtesy, monsieur adventurer."

- **Hand Over a Potion** — Obtain a random Relic.
- **Hand Over 100 Gold** — Obtain a random Relic.
- **Hand Over the greater courtesy** — Obtain 2 random Relics. (The harvest itself strips the offered item's name on this option; base reads "[Give ]".)

Mechanics check: matches harvest as far as the harvest states it (its third option is template-lossy — the traded item's name is missing on the wiki page itself, not just here). Flag: reused verbatim per the reuse rule even though the gallery's own curation note demotes this variant for a register slip (the closing line's "monsieur" honorific trips the Melusine register's "never French honorifics" rule) — it is the only kept Fontaine draft for this event, so it is not rewritten here. Also not in `events.yaml`'s pool — the third option needs a relic-removal op `HeldRelics` doesn't have, per the file's own skip list.

---

## - [ ] Reflections snoitcelfeR

### The Coral Mirror rorriM laroC ehT — Fontaine / Melusines of Merusea Village — loose — DRAFTED

Merusea Village keeps one wall of grown coral that no diver touches without asking first — polished by the current into something that reflects a little wrong on purpose. A Melusine archivist keeps a ledger of every change it has ever made and reads you the relevant page before you get close, at some length, with diagrams. Touched carefully, she explains, the wall corrects two of your habits for the worse and four for the better. Broken outright, it keeps no favorites: it copies everything you are, all at once, and hands back a second you that carries its own bad luck. She will not choose for you, and she is sorry either way.

- **Touch a Mirror** — Downgrade 2 random cards. Upgrade 4 random cards.
- **Shatter** — Duplicate your entire Deck. Add Bad Luck (curse) to your Deck.

Mechanics check: matches harvest and the shipped `reflections` row (downgrade_random 2 / upgrade_random 4 resolving before upgrade; duplicate_deck + curse_bad_luck). Flag: this is the one Glory-reachable event `teyvat-nation-mapping-act3-2026-09-14.md` §2 records as having no Fontaine row in the gallery (Sumeru's draft was cut for redundancy; only Inazuma and Liyue survive there) — drafted fresh here under the Melusine register (plain address, correct "Merusea Village" spelling, no invented institute name, an honest warning before the choice), following the mirrored-title convention the gallery's two surviving kept variants (Mirror Ward draW rorriM; Twin Stele eletS niwT) already use.

---

## - [ ] Relic Trader

### The Found-Things Shelf, Merusea Village — Fontaine / Melusines of Merusea Village — loose — REUSED event-conversion-gallery.md, Relic Trader variant 2

Merusea Village's hollow glows tide-blue and smells of kelp and candle wax. A Melusine keeps the village's shelf of found things, three of them set out on grown coral — one high, one at eye level, one down by her boots. Nothing here can be bought, she explains gravely; a thing without a story attached to it is only ballast. So you must leave a story behind to take one away.

- **Reach for the Top Shell** — Trade for the top one.
- **Reach for the Middle Shell** — Trade for the middle one.
- **Reach for the Bottom Shell** — Trade for the bottom one.

Mechanics check: matches harvest as far as the harvest states it (template-stripping ate the traded relic names on all three base options — "Trade for ." — on the wiki page itself, not just here). Flag: not in `events.yaml`'s pool — the options are generated from the player's own held relics and the wiki page has no static text to harvest, per the file's own skip list.

---

## - [ ] Self-Help Book

### A Melusine's Pamphlet of Encouragement — Fontaine / Melusines (Merusea Village) — loose — REUSED event-conversion-gallery.md, Self-Help Book variant 2

In Merusea Village a small Melusine in a rain hat presses a hand-stitched pamphlet on you, all pressed sumeru rose petals and enormous cheerful handwriting. She has been practising the speech that goes with it for some weeks. She will read you as much of it as you can bear, and takes no offence either way.

- **Take the Cover Line** — Choose an Attack to Enchant with Sharp 2.
- **Let Her Pick a Page** — Choose a Skill to Enchant with Nimble 2.
- **Sit Through the Whole Speech** — Choose a Power to Enchant with Swift 2.
- **Thank Her and Go** — Nothing happens.
- (Each reading is offered only if you hold a card of that type to enchant; Thank Her and Go is offered only when you hold none.)

Mechanics check: matches harvest and the shipped `self_help_book` row (each enchant option gated on its own eligibility rule; Move On carries `if_no_enchant_target: true`).

---

## - [ ] Slippery Bridge

### Ballast Check on the Meropide Lift — Fontaine / Melusines of the Fortress works — loose — REUSED event-conversion-gallery.md, Slippery Bridge variant 1

The pressure lift running down from Poisson to the Fortress of Meropide is rated to the ounce, and the Melusine attendant's brass ballast wheel says your kit is over it. She spins the wheel with one webbed hand; it ticks to a stop above a single item. Outside the porthole the water goes from green to black.

- **Let the Wheel Decide** — A specific card is removed from your deck.
- **Spin Again** — Lose 3 HP as the cable lurches and the pressure squeezes your ears. The wheel selects a different item at random. Every further spin costs 1 more HP than the last, and the attendant will patiently re-offer both choices until you surrender something. The wheel skips anything bolted to the frame (Eternal) and will not land twice on the same item while others remain.

Mechanics check: matches harvest and the shipped `slippery_bridge` row (Overcome = remove_random 1; Hold On = hp -3, remove 1, escalating +1 HP per re-spin, Eternal cards skipped, no repeats while others remain).

---

Loss: {character} was crushed in the pressure lift at the [gold]{event}[/gold].

## - [ ] Symbiote

### The Guest in the Hull — Fontaine / Melusines of Merusea Village — loose — REUSED event-conversion-gallery.md, Symbiote variant 3

A Melusine dockhand at Romaritime Harbor waves you over to an overturned skiff with the delight of someone showing off a pet. Something soft and iridescent has taken up residence in the hull; it hums, and it has plainly been reading the salvage logs of everyone who touched it. "It gets lonely down there," she explains. "It only wants to come along with somebody." A lumidouce lantern hangs by the mooring post, already lit.

- **Let It Come Along** — Enchant an Attack with Corrupted (deal 50% more damage; lose 2 HP each time the card is played).
- **Set the Lantern to It** — Choose a card to Transform.

Mechanics check: matches harvest and the shipped `symbiote` row (`also_acts: [3]`; enchant Corrupted / transform 1). The 2 HP figure follows this repo's stated authority (slaythespire.wiki.gg) over the conflicting mobalytics figure of 3, per the shipped row's own note.

---

## - [ ] The Future of Potions?

### What the Melusines Trade For — Fontaine / Melusines of Merusea Village — loose — REUSED event-conversion-gallery.md, The Future of Potions_ variant 3

The Melusines of Merusea Village have decided that bottles are the finest currency in Fontaine. Hand one over, they promise, and they will sing you the trick that kept a friend alive down in the Primordial Sea — Sigewinne taught them triage, and the songs stick better than any lecture. Three bottles on your belt catch their eyes, the leftmost ones first.

- **Trade the Plain Bottle** — Lose a specified Common potion. Obtain an Upgraded Common [Attack/Skill] card reward.
- **Trade the Pretty Bottle** — Lose a specified Uncommon potion. Obtain an Upgraded Uncommon [Attack/Skill/Power] card reward.
- **Trade the Treasured Bottle** — Lose a specified Rare potion. Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Trade the Strange Bottle** — Lose a specified Event potion (only Foul Potion and Glowwater Potion qualify). Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Trade the Silly Bottle** — Lose a specified Token potion (only Potion-Shaped Rock qualifies). Obtain an Upgraded Common [Attack/Skill] card reward.

Mechanics check: matches harvest's full 5-option, potion-tier-gated shape. Flag: the shipped `the_future_of_potions` row in `events.yaml` compresses this to 2 options (spend any held potion for an upgraded 3-card reward screen, or Leave) rather than the harvest's tier-gated 5 — an existing sim simplification, orthogonal to this face and not something this pass changes.

---

## - [ ] The Round Tea Party

### The Round Table at Café Lutece — Fontaine / Court of Fontaine (aristocracy) — literal — REUSED event-conversion-gallery.md, The Round Tea Party variant 1

Five aristocrats of the Court of Fontaine take their afternoon service at Café Lutece, at a table made perfectly round so that no one can be seated below anyone else. Seating rank is thereby a solved problem; the arsenic is not. A Melusine attendant sets a sixth cup before you without being asked, and the conversation does not pause for you.

- **Take the Cup** — Obtain Vintage Reserve (Royal Poison relic). Heal to full HP.
- **Name the Poisoner** — Lose 11 HP. Obtain a random Relic.

Mechanics check: matches harvest. Flag: not in `events.yaml`'s pool — Royal Poison's effect text (magnitude and trigger) is absent from the wiki entirely, per the file's own skip list ("needs a published number, not a hook"); no number is guessed here.

---

## - [ ] The Trial

### The Empty Seat in the Gallery — Fontaine / Court of Fontaine (Opera Epiclese) — literal — REUSED event-conversion-gallery.md, The Trial variant 1

The Opera Epiclese is packed to the rafters, and the Oratrice Mecanique d'Analyse Cardinale hums cold above the dock. A gardes usher finds you in the aisle: a juror has fainted, and the Chief Justice will not open a docket a seat short. The Oratrice weighs the gallery's conviction — so tonight your opinion is evidence. The bailiff calls one case only.

The Merchant's Case (Merchant Trial):
- **VERDICT: Guilty** — Add Regret (curse) to your Deck. Obtain 2 random Relics.
- **VERDICT: Innocent** — Add Shame (curse) to your Deck. Upgrade 2 cards.

The Noble's Case (Noble Trial):
- **VERDICT: Guilty** — Heal 10 HP.
- **VERDICT: Innocent** — Add Regret (curse) to your Deck. Gain 300 Gold.

The Nameless Case (Nondescript Trial):
- **VERDICT: Guilty** — Add Doubt (curse) to your Deck. Gain 2 card rewards.
- **VERDICT: Innocent** — Add Doubt (curse) to your Deck. Transform 2 cards.

Mechanics check: matches harvest and the shipped `the_trial` row (one of the three variants rolled per visit; every verdict a curse-for-payout trade, numbers unchanged).

@pages.INITIAL.options.ACCEPT | Take the Empty Seat — Sit on the jury. One case is called, and you deliver its verdict.
@pages.INITIAL.options.REJECT | Decline the Summons — Try to leave the gallery.
@pages.REJECT.description — The usher's smile does not move. "The Chief Justice does not open a docket a seat short, and the doors do not open until the docket closes." Behind him the gardes have already turned to face the aisle.
@pages.REJECT.options.ACCEPT | Take the Seat After All — Sit on the jury. One case is called.
@pages.REJECT.options.DOUBLE_DOWN | Walk Out of the Opera — Push past the gardes and leave Fontaine's justice behind. This ends the run.
@pages.MERCHANT.description — The defendant is a Fleuve Cendre smuggler in a Court-issued suit, accused of moving unlicensed potions through the Poisson canals. The Oratrice hums. The gallery waits on the empty seat.
@pages.NOBLE.description — The defendant is a Palais Mermonia heir accused of paying a duel's loser to lose. The Oratrice hums. The gallery waits on the empty seat.
@pages.NONDESCRIPT.description — The defendant gives no name, and the docket lists no crime beyond "obstruction of the Oratrice." The Oratrice hums. The gallery waits on the empty seat.
@pages.MERCHANT_GUILTY.description — The Oratrice agrees with you. The smuggler's confiscated stock is offered to the jury first, and the verdict follows you out of the Opera as Regret.
@pages.MERCHANT_INNOCENT.description — The Oratrice disagrees. The gardes release the smuggler, and a clerk quietly notes the dissent beside your name: Shame. The Court pays its jurors in technique, not Mora.
@pages.NOBLE_GUILTY.description — The Oratrice agrees. The heir is fined, the gallery cheers, and a Melusine attendant presses a tonic into your hand on the way out.
@pages.NOBLE_INNOCENT.description — The Oratrice disagrees, loudly. The heir's family thanks you with a very full purse, and you carry the verdict out as Regret.
@pages.NONDESCRIPT_GUILTY.description — The Oratrice returns no reading at all. The nameless defendant is led away, the docket closes, and Doubt closes with it. The clerk hands you two files from the evidence table.
@pages.NONDESCRIPT_INNOCENT.description — The Oratrice returns no reading at all. The nameless defendant walks, thanks you, and leaves you with Doubt and two techniques you no longer recognise as your own.

---

## - [ ] This or That?

### Two Gifts from the Fontemer — Fontaine / Melusines — loose — REUSED event-conversion-gallery.md, This or That_ variant 3

Beneath the roots of Elynas, Kiara has laid out the week's salvage on a flat stone, and two pieces have no owner listed in any Merusee ledger. She is delighted to give one away and firmly unwilling to give away both. She will not tell you which is the better find; she says that would spoil it.

- **Take the Coin-Purse** — Lose 6 HP. Gain 57 Gold.
- **Take the Whirring Apparatus** — Add Clumsy (curse) to your Deck. Obtain a random Relic.

Mechanics check: matches harvest and the shipped `this_or_that` row (hp -6 / gold [57,57]; curse_clumsy + relic true). Flag: reused verbatim per the reuse rule even though the gallery's own curation note demotes this variant for spelling "Merusea Village" as "Merusee" — it is the only kept Fontaine draft for this event, so it is not corrected here.

---

Loss: {character} bled out over a coin-purse at the [gold]{event}[/gold].

## - [ ] Tinker Time

### Prototype Hour at the Institute — Fontaine / Fontaine Research Institute of Kinetic Energy Engineering (Melusine engineer) — literal — REUSED event-conversion-gallery.md, Tinker Time variant 2

A Melusine engineer waves you past a wall of half-built clockwork at the Fontaine Research Institute of Kinetic Energy Engineering. "One prototype per visitor. Pick a chassis, pick a modification, and please stand behind the blast glass."

Chassis (two of the three offered at random):
- **Harpoon** — Create an Attack. (Deal 12 damage.)
- **Bulwark Plate** — Create a Skill. (Gain 8 Block.)
- **Aetheric Core** — Create a Power.

Modification (two of that chassis's three offered at random):
- **Corrosive** (Attack) — Apply 2 Weak. Apply 2 Vulnerable.
- **Repeater** (Attack) — Hits 2 additional times.
- **Pressure Leak** (Attack) — Whenever you play a card this turn, the enemy loses 6 HP.
- **Overcharge** (Skill) — Gain 2 energy.
- **Blueprints** (Skill) — Draw 3 cards.
- **Misfire** (Skill) — Add a random card into your Hand. It's free to play this turn.
- **Calibration** (Power) — Gain 2 Strength. Gain 2 Dexterity.
- **Curiosity** (Power) — Powers cost 1 less.
- **Field Testing** (Power) — At the end of combat, Upgrade a random card.

The result is your custom Prototype (Mad Science) card.

Mechanics check: matches harvest (two-step chassis/modification chooser, both steps randomly offering two of three, all rider numbers unchanged). Flag: not in `events.yaml`'s pool — absent from the modelled pool with no named blocker in the file's skip list; an engine gap, not a mechanics mismatch.

@pages.INITIAL.options.CHOOSE_CARD_TYPE | Choose a Chassis — Pick one of the two chassis on offer.
@pages.CHOOSE_CARD_TYPE.description — The Melusine engineer sets two chassis on the bench and taps the blast glass. "One prototype per visitor. Chassis first, then the modification."
@pages.CHOOSE_CARD_TYPE.options.ATTACK | Harpoon — Create an Attack. (Deal 12 damage.)
@pages.CHOOSE_CARD_TYPE.options.SKILL | Bulwark Plate — Create a Skill. (Gain 8 Block.)
@pages.CHOOSE_CARD_TYPE.options.POWER | Aetheric Core — Create a Power.
@pages.CHOOSE_RIDER.description — She slides open the drawer for that chassis. Two modifications fit it. "Pick one. Both are tested. Neither is safe."
@pages.CHOOSE_RIDER.options.SAPPING | Corrosive — Apply 2 Weak. Apply 2 Vulnerable.
@pages.CHOOSE_RIDER.options.VIOLENCE | Repeater — Hits 2 additional times.
@pages.CHOOSE_RIDER.options.CHOKING | Pressure Leak — Whenever you play a card this turn, the enemy loses 6 HP.
@pages.CHOOSE_RIDER.options.ENERGIZED | Overcharge — Gain 2 energy.
@pages.CHOOSE_RIDER.options.WISDOM | Blueprints — Draw 3 cards.
@pages.CHOOSE_RIDER.options.CHAOS | Misfire — Add a random card into your Hand. It's free to play this turn.
@pages.CHOOSE_RIDER.options.EXPERTISE | Calibration — Gain 2 Strength. Gain 2 Dexterity.
@pages.CHOOSE_RIDER.options.CURIOUS | Curiosity — Powers cost 1 less.
@pages.CHOOSE_RIDER.options.IMPROVEMENT | Field Testing — At the end of combat, Upgrade a random card.
@pages.DONE.description — The Prototype comes off the bench ticking. She stamps the Institute's mark on it and waves you back behind the glass.

---

## - [ ] War Historian, Repy

### The Sealed Testimony of Repie — Fontaine / Court of Fontaine, Melusine archivist — loose — REUSED event-conversion-gallery.md, War Historian, Repy variant 2

Beneath the Palais Mermonia, past Gardemek that no longer recognize anyone's warrant, lies the Court's Remurian evidence vault. Repie — the Melusine archivist who inherited the keyring and lost most of it — walks you down without comment. Two seals remain intact, and your Lantern Key will spend itself on exactly one: the war tribunal's testimony reel, or the contraband locker shelved beside it.

- **Unseal the Testimony Reel** — Lose Lantern Key. Obtain Remurian Tribunal Record (History Course).
- **Unseal the Contraband Locker** — Lose Lantern Key. Procure 2 random Potions. Obtain 2 random Relics.
- (If a Lantern Key remains in your deck afterwards, the other seal must also be opened.)

Mechanics check: matches harvest. Flag: not in `events.yaml`'s pool — hard-gated on the Lantern Key quest card from the unshipped The Lantern Key event (the two events must ship as a pair), per the gallery's own flag and the file's quest-card skip note.
