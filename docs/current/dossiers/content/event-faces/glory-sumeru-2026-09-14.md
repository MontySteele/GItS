# Glory — Sumeru face — event text

> **Fable curation pass, 2026-09-14.** Selection and lore only, no mechanics
> touched. Four Kshahrewar scenes had been set at Pardis Dhyai, which is the
> Amurta garden, and now sit in Sumeru City and the House of Daena; the courier
> dodges a Matra checkpoint, not a Consecrated Beast patrol. The Merchant___
> draft is HELD as text only until the page is re-harvested with its options;
> until then both Glory faces keep the base text for that event, so the faces'
> counts stay equal (17 converted each). Reflections keeps its unreversed
> title pending the gallery's open call.


Face: Sumeru (Akademiya / Forest Rangers & Aranara registers).
Zone: Act 3, Glory (both faces share the zone; a run rolls one face).
Events covered: 18 — 14 Glory-own (harvest `[act3]`/`[act2/act3]` tags) + 4
all-acts (research §2.1: Self-Help Book, Slippery Bridge, The Future of
Potions?, This or That?).
Reused from `event-conversion-gallery.md` (verbatim, kept Sumeru variant):
9 — Crystal Sphere, Grave of the Forgotten, Hungry for Mushrooms, Ranwid the
Elder, Self-Help Book, Symbiote, The Trial, The Future of Potions?, War
Historian Repy.
Drafted fresh (no kept Sumeru variant existed): 9 — Battleworn Dummy, Potion
Courier, Reflections snoitcelfeR, Relic Trader, Slippery Bridge, The
Merchant___, The Round Tea Party, This or That?, Tinker Time.
Mechanics frozen to `docs/sts2-events-harvest.txt`; only words change.
Order: harvest's own (alphabetical) ordering over the Glory + all-acts subset.
tier05/content/events.yaml gap: only 3 of the 14 Glory-own events are
modelled (`grave_of_the_forgotten`, `the_trial`, `reflections`; `symbiote`
reaches act 3 via `also_acts`) — the other 10 are unshipped per the
no-substitution rule (§3.7.2); all 4 all-acts events are modelled.

---

## - [ ] Battleworn Dummy

### The Kshahrewar Proving Cage — Sumeru / Akademiya (Kshahrewar darshan, Sumeru City) — literal — DRAFTED

In a fenced yard behind the Kshahrewar workshops below the Akademiya, mechanists have rigged a padded practice construct to a calibrated spring-drum, patched and re-patched past counting. A darshan proctor times every bout against a water-clock she refuses to slow down for anyone. "Three turns," she says, already resetting the gauge. "Higher tension, better data, better prize. The construct does not care how tired you are."

- **Setting 1** — Fight a 75 HP dummy. Procure 1 random Potion.
- **Setting 2** — Fight a 150 HP dummy. Upgrade 2 random cards.
- **Setting 3** — Fight a 300 HP dummy. Obtain a random Relic.
- **(all settings)** — You have 3 turns to defeat the dummy. Failing results in no reward.

Mechanics check: matches harvest.

@pages.VICTORY.description — The spring-drum winds down before the proctor's count does. He marks the bout complete and unlocks that setting's prize.
@pages.DEFEAT.description — The proctor's count runs out with the construct still on its feet. He marks the bout incomplete and unlocks nothing.

---

## - [ ] Crystal Sphere

### Rtawahist's Starfall Glass — Sumeru / Rtawahist astrologer, with Dori Sangemah Bay holding the paper — literal — REUSED `event-conversion-gallery.md` § Crystal Sphere, variant 3

In a cold observation cell high in the Akademiya, a lens of starfall glass hangs in a gimbal ring, its face ruled into eleven by eleven wards. The Rtawahist scholar explains that each reading burns the clouding away — one ward, or a three-by-three quarter — and that a horoscope half-read is no horoscope at all. Downstairs, Dori Sangemah Bay has already drafted a contract with one very small clause.

- **Pay the Bench Fee** — Pay 51-99 Mora (Gold). Divine 3 times.
- **Sign with Dori** — Gain a Debt. Divine 6 times.
- Every fortune you bare in full is offered afterward, to accept or decline in any order — save the reading the scholars refuse to transcribe (Doubt), which enters your ledger the moment it clears.

Mechanics check: matches harvest (11x11 grid, small/big divination, reward table, Doubt instant-add, relic 4x4 uncoverable on the 3-divination branch — all inherited from the gallery source verbatim).

---

## - [ ] Grave of the Forgotten

### Hollow of the Struck Name — Sumeru / Forest Rangers, against the Akademiya — quiet, accusatory — REUSED `event-conversion-gallery.md` § Grave of the Forgotten, variant 3

In a withered hollow off Avidya Forest, a Forest Ranger's marker names no one. The Akademiya struck this researcher from the Akasha, and what remains of them drifts here, half-remembered, thinning at the edges like everything the withering touches. A ranger's offering-bowl sits beside the marker. So does an unsealed field journal.

- **Take the Unnamed Keepsake** — Obtain Unnamed Keepsake (Forgotten Soul relic).
- **Speak the Struck Name Aloud** — Add Withering (Decay curse) to your Deck. Enchant a card that Exhausts with Soul's Power.
- Speaking the name is locked if you have no cards with Exhaust that can be Enchanted.

Mechanics check: matches harvest (this is a flavor-alternate variant; the shipped name pass under R231 took variant 1, Liyue's The Nameless Cairn — recorded, not re-litigated here since the mechanics are identical across all three kept variants).

---

## - [ ] Hungry for Mushrooms

### The Aranara's Two Caps — Sumeru / Aranara + Forest Rangers — literal — REUSED `event-conversion-gallery.md` § Hungry for Mushrooms, variant 1

Off the trail in Ardravi Valley, an Aranara called Arapacati tugs your sleeve toward a hollow beneath a rotting Zaytun stump. Two fungi have grown there side by side: one swollen and pale as a drum, one small and giving off a sweet, resinous smell that carries further than it should. The Forest Rangers say everything edible in the rainforest is also, in some sense, a test. "Nara must choose," Arapacati says. "Aranara will not choose for Nara."

- **Eat the Bulging Cap** — Obtain Bulging Cap (Big Mushroom, relic). Upon pickup, raise your Max HP by 20. At the start of each combat, draw 2 fewer cards.
- **Eat the Rukkhashava Bloom** — Obtain Rukkhashava Bloom (Fragrant Mushroom, relic). Upon pickup, lose 15 HP and Upgrade 3 random cards.

Mechanics check: matches harvest.

---

Loss: {character} ate the Rukkhashava Bloom and never got up at the [gold]{event}[/gold].

## - [ ] Potion Courier

### The Spilled Satchel at Sumeru City's Gate — Sumeru / Akademiya (Amurta darshan courier) — loose — DRAFTED

At the western gate of Sumeru City, an Amurta darshan courier has upended her satchel dodging the bell of a Matra checkpoint. Half her stock is common field-brews nobody at the Akademiya will miss; the other case still carries an uncommon-grade tincture sealed for a professor's private study, and she has not yet decided whether to report it lost.

- **Gather the Spilled Brews** — Procure 3 field brews (Foul Potion).
- **Claim the Sealed Tincture** — Procure 1 random uncommon-grade tincture (Uncommon Potion).

Mechanics check: matches harvest.

---

## - [ ] Ranwid the Elder

### Aranwid, Eldest of Vanarana — Sumeru / Aranara of Vanarana — literal — REUSED `event-conversion-gallery.md` § Ranwid the Elder, variant 1

In the dream-lit hollow of Vanarana, past the singing seelie-lamps of Vissudha Field, sits an Aranara so old its leaves have gone silver. Around it lies a nest of small kept things — gifts from Nara who passed through and never came back for them. "Aranara remember," it hums. "Nara gives, Aranara gives back."

- **Offer a Potion** — Obtain a random Relic.
- **Offer 100 Mora (Gold)** — Obtain a random Relic.
- **Offer the greater gift** — Obtain 2 random Relics. (harvest strips the offered item on this option: base reads "[Give ]")

Mechanics check: matches harvest except the third option's named cost, which the harvest itself cannot supply (template-stripped) — flag: the base wiki page's third option lost its offered item to stripping; a re-harvest is needed before the "greater gift" can be named or costed in any variant, Sumeru included.

---

## - [ ] Reflections snoitcelfeR

### The Rtawahist Twinning Glass — Sumeru / Akademiya (Rtawahist darshan) — literal — DRAFTED

In a cold observation loft above the House of Daena, a Rtawahist scholar keeps a pane of starfall glass that does not merely reflect — it corrects, showing the observer back sharpened in some ways and reversed in others. She has one working pane and one cracked spare. "Touch the true glass, and it edits generously," she says. "Break the spare, and everything you are gets a duplicate — including the parts that shouldn't have one."

- **Touch the True Glass** — Downgrade 2 random cards. Upgrade 4 random cards.
- **Break the Spare Pane** — Duplicate your entire Deck. Add Reflected Doubt (Bad Luck curse) to your Deck.

Mechanics check: matches harvest. Flag carried from the gallery's own note on this event: whole-deck duplication has no plausible Teyvat agent under any faction (every variant is forced to a supernatural device), and the mirrored-title gimmick is an English text joke — this draft keeps the base (unreversed) title rather than inventing a mirrored Teyvat transliteration, pending the same [USER] call the gallery flags.

---

## - [ ] Relic Trader

### The Kshahrewar Surplus Office — Sumeru / Akademiya (Kshahrewar darshan, Sumeru City) — loose — DRAFTED

Behind the Akademiya's confiscations depot in Sumeru City, a Kshahrewar clerk has racked three items seized from students' unauthorized projects on a tiered shelf — top, middle, bottom — each tagged and cross-filed. He will not sell; departmental policy, which he cites by filing number, permits only like-for-like exchange. "One of yours for one of the shelf's," he says. "Choose the tier. I do not choose for you."

- **Take the Top Shelf** — Trade for the top one.
- **Take the Middle Shelf** — Trade for the middle one.
- **Take the Bottom Shelf** — Trade for the bottom one.

Mechanics check: matches harvest except the traded relic names, which the harvest itself cannot supply (template-stripped on all three base options) — flag: same open item the gallery carries for this event; a targeted wiki re-harvest is needed before any variant, Sumeru included, can state what the trade costs or gives.

---

## - [ ] Self-Help Book

### Six Weeks to a Better You, Illuminated — Sumeru / Akademiya (Vahumana dropout bookseller) — literal — REUSED `event-conversion-gallery.md` § Self-Help Book, variant 1

A warped stall in the shadow of the House of Daena, where a Vahumana dropout hawks the treatise the Sages refused to shelve: SIX WEEKS TO A BETTER YOU, ILLUMINATED. The spine cracks like nothing has ever opened it. He swears every chapter is field-tested, then admits the field was his dormitory.

- **Read the Back** — Choose an Attack to Enchant with Sharp 2.
- **Read a Random Passage** — Choose a Skill to Enchant with Nimble 2.
- **Read the Entire Book** — Choose a Power to Enchant with Swift 2.
- **Move On** — Nothing happens.
- Each reading is offered only if you hold a card of that type to enchant; Move On is offered only when you hold none.

Mechanics check: matches harvest.

---

## - [ ] Slippery Bridge

### The Rope Line Over Ardravi Valley — Sumeru / Forest Rangers — loose — DRAFTED

A Forest Ranger's rope bridge sags over a Withering-scarred ravine in Ardravi Valley, one cable frayed past its posted weight marker. The ranger stationed at the near post says nothing beyond pointing at the sign; she has watched three travelers cross overloaded and does not care to watch a fourth. Something in your pack will have to go, or the crossing will take it anyway.

- **Cut It Loose** — [Specific card] is removed from your deck.
- **Grip the Rope** — Lose 3 HP as the frayed cable saws at your palms. The item hanging over the ravine is randomized. Each further grip costs 1 more HP than the last, and the ranger keeps pointing at the same sign until you finally cut something away. Gear marked for the Ranger corps' own use (Eternal) never sways loose, and the wind never picks the same bundle twice while others remain.

Mechanics check: matches harvest (first card never Basic unless deck is all-Basic; same card never repeats until every other card has been offered; escalating +1 HP per Hold On — all carried from the base rule, unchanged from the gallery's other variants).

---

Loss: {character} let go of the rope over Ardravi Valley at the [gold]{event}[/gold].

## - [ ] Symbiote

### The Withering Graft — Sumeru / Forest Rangers — literal — REUSED `event-conversion-gallery.md` § Symbiote, variant 2

In a hollow below Chatrakam Cave, a withered branch has swollen into a soft black bulb that pulses in time with your heartbeat. A Forest Ranger's abandoned trail-marker warns of it in three languages and one Aranara pictogram. As you lean in, the growth leans back — patient, and very interested in the hand that holds your weapon.

- **Let It Graft** — Enchant an Attack with Corrupted.
- **Burn It Out** — Choose a card to Transform.

Mechanics check: matches harvest (Corrupted: +50% damage, lose 2 HP per the wiki's number, recorded over Mobalytics's conflicting 3 — this repo's standing call, unchanged here).

---

## - [ ] The Future of Potions?

### The Future of Elixirs — Sumeru / Akademiya (Amurta darshan researcher) — literal — REUSED `event-conversion-gallery.md` § The Future of Potions_, variant 2

In a greenhouse annex off the Vissudha Field, an Amurta researcher's prototype still hisses and drips. "Drinking a phial teaches you nothing. Feed it here and the apparatus reads out the technique the brew was hiding." She gestures at an intake tray; only the first three bottles on your belt will fit, leftmost first.

- **Feed the Common Phial** — Lose a specified Common potion. Obtain an Upgraded Common [Attack/Skill] card reward.
- **Feed the Uncommon Phial** — Lose a specified Uncommon potion. Obtain an Upgraded Uncommon [Attack/Skill/Power] card reward.
- **Feed the Rare Phial** — Lose a specified Rare potion. Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Feed the Anomalous Phial** — Lose a specified Event potion (only Foul Potion and Glowwater Potion qualify). Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Feed the Worthless Phial** — Lose a specified Token potion (only Potion-Shaped Rock qualifies). Obtain an Upgraded Common [Attack/Skill] card reward.

Mechanics check: matches harvest.

@pages.DONE.description — The apparatus stops hissing and prints the technique on a strip of damp paper. The researcher tears it off for you without looking up from her notes.

---

## - [ ] The Merchant___

### The Unlicensed Stall Outside the Akademiya Gate — Sumeru / Akademiya-adjacent, unofficial trade — literal — DRAFTED

Just past the checkpoint outside the Akademiya's outer gate, where student patrols rarely bother to look, a peddler has set up a folding table with wares that carry no Akademiya provenance tag at all. He knows exactly how far his welcome extends and has never once been caught overstaying it. Mora is accepted. Questions about the goods' paperwork are not.

- **(no options)** — [—] harvest carries `<<NO OPTIONS SECTION ON PAGE>>` for The Merchant___ — nothing mechanical exists to convert. Option count, prices, rewards and any escalation are inherited from base verbatim once the page is re-harvested; this draft changes name, setting and flavor only, matching the gallery's own two Merchant___ drafts.

Mechanics check: flag: harvest has no options section for The Merchant___ — no mechanics exist to freeze. Cannot be verified against the harvest until a namespace-prefixed re-harvest of the wiki page lands.

---

## - [ ] The Round Tea Party

### The Round Table at the House of Daena — Sumeru / Akademiya — literal — DRAFTED

Five senior researchers of the Akademiya take their seminar tea at a table built perfectly round, specifically so no darshan can claim the head seat. It has not stopped four of them from suspecting the fifth authored an anonymous ethics complaint. A junior scholar sets a sixth cup before you without asking your darshan and returns to her own argument mid-sentence.

- **Take the Cup** — Obtain Seminar Reserve (Royal Poison, relic). Heal to full HP.
- **Name the Suspect** — Lose 11 HP. Obtain a random Relic.

Mechanics check: matches harvest.

---

## - [ ] The Trial

### Three Dossiers Before Sabzeruz — Sumeru / Akademiya scholars at the House of Daena — loose (fraud inquest, not a courtroom) — REUSED `event-conversion-gallery.md` § The Trial, variant 2

The lamps of the House of Daena have burned down to their last oil. A Kshahrewar proctor drops three sealed dossiers on your desk: manuscripts accused of forged findings, all of which the sages want ruled on before the Sabzeruz festival crowds the halls. Akademiya custom hands the first ruling to the newest reader in the room. Only one author is awake to hear it.

**The Trader's Treatise (Merchant Trial)**
- **RULE: Forged (Guilty)** — Add Regret (curse) to your Deck. Obtain 2 random Relics.
- **RULE: Sound (Innocent)** — Add Shame (curse) to your Deck. Upgrade 2 cards.

**The Patron's Treatise (Noble Trial)**
- **RULE: Forged (Guilty)** — Heal 10 HP.
- **RULE: Sound (Innocent)** — Add Regret (curse) to your Deck. Gain 300 Gold.

**The Unsigned Treatise (Nondescript Trial)**
- **RULE: Forged (Guilty)** — Add Doubt (curse) to your Deck. Gain 2 card rewards.
- **RULE: Sound (Innocent)** — Add Doubt (curse) to your Deck. Transform 2 cards.

Mechanics check: matches harvest (one of the three sub-trials rolled per visit, exactly as `tier05/content/events.yaml`'s `variants` ships).

@pages.INITIAL.options.ACCEPT | Open the Dossiers — Rule on one treatise. The proctor picks which.
@pages.INITIAL.options.REJECT | Refuse the Desk — Push the dossiers back across the desk.
@pages.REJECT.description — The proctor does not pick them up. "The sages assigned you this desk. Sabzeruz begins at dawn, and no one leaves the House of Daena with an open docket." The lamps gutter.
@pages.REJECT.options.ACCEPT | Rule After All — Open the dossiers. One treatise is put before you.
@pages.REJECT.options.DOUBLE_DOWN | Walk Out of the House — Leave the desk, the docket and the Akademiya behind. This ends the run.
@pages.MERCHANT.description — The Trader's Treatise: a Port Ormos merchant's account of a rare ink, suspiciously profitable and suspiciously well cited. The proctor waits with the seal.
@pages.NOBLE.description — The Patron's Treatise: a rich patron's name on a paper his scribes plainly wrote, with a footnote that flatters a sage. The proctor waits with the seal.
@pages.NONDESCRIPT.description — The Unsigned Treatise: no author, no darshan, and findings nobody has managed to repeat or to disprove. The proctor waits with the seal.
@pages.MERCHANT_GUILTY.description — Forged. The merchant's samples are seized, and the proctor lets you keep two of them. The seal you pressed is Regret.
@pages.MERCHANT_INNOCENT.description — Sound. The merchant sells his ink at a premium the next morning, and the proctor notes your leniency as Shame. Your fee is technique, refined.
@pages.NOBLE_GUILTY.description — Forged. The patron is struck from the roll, and the House stewards bring you tea and a bandage.
@pages.NOBLE_INNOCENT.description — Sound. The patron's steward leaves a very heavy purse on the desk, and you carry the seal out as Regret.
@pages.NONDESCRIPT_GUILTY.description — Forged, you rule, and nobody can prove otherwise. The proctor files it under Doubt and hands you the next two manuscripts from the pile.
@pages.NONDESCRIPT_INNOCENT.description — Sound, you rule, and nobody can prove otherwise. The proctor files it under Doubt, and two of your own notes come back to you rewritten.

---

## - [ ] This or That?

### The Caravan Ribat Leavings — Sumeru / Forest Rangers — loose — DRAFTED

A Forest Ranger patrol out of Caravan Ribat turned up two items scattered from a raided trade caravan, and neither carries a manifest tag to say who they belonged to. The ranger captain has no patience for a full inventory report over two loose objects; she holds them out, one in each hand, and waits for you to pick.

- **Take the Locked Coffer** — The seized latch bites your knuckles clearing the lid. Lose 6 HP. Gain 57 Mora.
- **Take the Unmarked Kit** — It is unmistakably well-made gear, fitted for nobody in particular — least of all you. Add Clumsy (curse) to your Deck. Obtain a random Relic.

Mechanics check: matches harvest.

---

Loss: {character} bled out on a coffer latch at the [gold]{event}[/gold].

## - [ ] Tinker Time

### The Kshahrewar Workbench — Sumeru / Akademiya (Kshahrewar darshan, Sumeru City) — literal — DRAFTED

In a cluttered annex of the Kshahrewar darshan's fabrication hall in Sumeru City, a mechanist clears bench space and slides forward a half-built chassis. "One design per visitor, and please stand behind the containment glass," she says, already reaching for the parts bin. Two of three frames are laid out; two of three riders wait beside them.

**Step 1: Choose a Frame** (two of the three offered at random)
- **Calibrated Striker** — Create an Attack. (Deal 12 damage.)
- **Ward Plate** — Create a Skill. (Gain 8 Block.)
- **Field Array** — Create a Power.

**Step 2: Choose a Rider** (two of that frame's three offered at random)
- Attack riders: **Corrosive Filing** (Sapping) Apply 2 Weak. Apply 2 Vulnerable. / **Repeater Coil** (Violence) Hits 2 additional times. / **Bleed-Off Valve** (Choking) Whenever you play a card this turn, the enemy loses 6 HP.
- Skill riders: **Surplus Charge** (Energized) Gain 2 energy. / **Annotated Draft** (Wisdom) Draw 3 cards. / **Improvised Patch** (Chaos) Add a random card into your Hand. It's free to play this turn.
- Power riders: **Field Calibration** (Expertise) Gain 2 Strength. Gain 2 Dexterity. / **Peer-Reviewed Design** (Curious) Powers cost 1 less. / **Ongoing Revision** (Improvement) At the end of combat, Upgrade a random card.

You leave with a custom Proving Draft (Mad Science) card.

Mechanics check: matches harvest.

@pages.INITIAL.options.CHOOSE_CARD_TYPE | Choose a Frame — Pick one of the two frames on the bench.
@pages.CHOOSE_CARD_TYPE.description — The mechanist lays two frames on the bench. "One design per visitor. Pick the frame, then the rider that goes in it."
@pages.CHOOSE_CARD_TYPE.options.ATTACK | Calibrated Striker — Create an Attack. (Deal 12 damage.)
@pages.CHOOSE_CARD_TYPE.options.SKILL | Ward Plate — Create a Skill. (Gain 8 Block.)
@pages.CHOOSE_CARD_TYPE.options.POWER | Field Array — Create a Power.
@pages.CHOOSE_RIDER.description — She opens the drawer beneath the chosen frame. Two riders fit it. "Choose. I will not tell you which one I would take."
@pages.CHOOSE_RIDER.options.SAPPING | Corrosive Filing — Apply 2 Weak. Apply 2 Vulnerable.
@pages.CHOOSE_RIDER.options.VIOLENCE | Repeater Coil — Hits 2 additional times.
@pages.CHOOSE_RIDER.options.CHOKING | Bleed-Off Valve — Whenever you play a card this turn, the enemy loses 6 HP.
@pages.CHOOSE_RIDER.options.ENERGIZED | Surplus Charge — Gain 2 energy.
@pages.CHOOSE_RIDER.options.WISDOM | Annotated Draft — Draw 3 cards.
@pages.CHOOSE_RIDER.options.CHAOS | Improvised Patch — Add a random card into your Hand. It's free to play this turn.
@pages.CHOOSE_RIDER.options.EXPERTISE | Field Calibration — Gain 2 Strength. Gain 2 Dexterity.
@pages.CHOOSE_RIDER.options.CURIOUS | Peer-Reviewed Design — Powers cost 1 less.
@pages.CHOOSE_RIDER.options.IMPROVEMENT | Ongoing Revision — At the end of combat, Upgrade a random card.
@pages.DONE.description — The Proving Draft comes off the bench warm. She logs it under your name and points you at the containment glass on your way out.

---

## - [ ] War Historian, Repy

### War Historian, Rapiya — Sumeru / Akademiya Matra (Haravatat dissident) — literal — REUSED `event-conversion-gallery.md` § War Historian, Repy, variant 1

Deep beneath Ardravi Valley, the Akademiya buries what it would rather not teach. In a forgotten Matra holding-cell sits Rapiya, a Haravatat war-historian condemned for reading the Archon War the wrong way — and beside her cage stands the Matra's confiscation strongbox, still sealed. Your Lantern Key turns once, and only once.

- **Open the Cage** — Lose Lantern Key. Obtain Chronicle of the Archon War (History Course).
- **Open the Strongbox** — Lose Lantern Key. Procure 2 random Potions. Obtain 2 random Relics.
- If a Lantern Key remains in your deck afterwards, the other option must also be chosen.

Mechanics check: matches harvest. Flag carried from the gallery: this event is hard-gated on the Lantern Key quest card from The Lantern Key, and neither event is shipped in `tier05/content/events.yaml` — the two must ship as a pair, and the duplicate-key clause stays an unvoiceable footnote until they do.

---

## Coverage summary

18 of 18 Glory + all-acts events covered (14 Glory-own by harvest `[act3]`/`[act2/act3]` tag + 4 all-acts). None missing from the harvest. 9 reused verbatim from the gallery's kept Sumeru variants; 9 drafted fresh under the Akademiya/Forest-Ranger/Aranara register rules. Flags carried forward (none newly raised): Ranwid the Elder's stripped third-option name, Relic Trader's stripped traded-relic names, The Merchant___'s missing options section entirely, Reflections' whole-deck-duplication agent question, and War Historian's Lantern Key pairing gate.
