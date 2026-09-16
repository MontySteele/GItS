# Hive — Natlan Face

> **Fable curation pass, 2026-09-14.** Selection and lore only, no mechanics
> touched. The Scions of the Canopy now sit on Coatepec Mountain and the
> Children of Echoes at Tepeacac Rise, their canon homes; one invented beetle
> and one Guild aside removed. The Collective of Plenty's placement at Mictlan
> is unverified and rides until an EB-757-style check reaches Natlan. Count
> matches the Inazuma face at 25; The Merchant___ keeps base text on both.


Face: Natlan
Zone: Act 2 (the Hive)
Event count: 25 — 21 Hive events + 4 all-acts events (docs/current/research/sts2-map-and-events-research.md §2.1/§2.3)
Register: tribal (Flower-Feather Clan, Scions of the Canopy, Children of Echoes, People of the Springs, Masters of the Night-Wind, Collective of Plenty); frank, competitive, warm; Saurians as companions; Night Kingdom/Wayob/Pilgrimage/Ode of Resurrection spoken plainly; canon places only
Mechanics frozen to docs/sts2-events-harvest.txt
Excluded — The Merchant___ (act2/act3): harvest page carries `<<NO OPTIONS SECTION ON PAGE>>`, nothing to freeze; research doc's Hive count of 21 already excludes it
Excluded — War Historian, Repy: harvest tags it [act2/act3], but research doc §2.4 places it in Glory (act 3), not the Hive; out of scope here
Order: Hive events alphabetically (matching §2.3's own ordering, with the three shared events — Brain Leech, Room Full of Cheese, Tea Master — inserted alphabetically), then the four all-acts events in §2.1's order
Drafted 2026-09-14 (Natlan register ruled same day), one draft per event, no variants
Curation: none applied yet — first pass

---

## - [ ] Amalgamator
### The Cookfire Forge — Natlan / Collective of Plenty — literal

At the cookfires of Mictlan, a Collective of Plenty smith has two worn practice blades and two dented practice bucklers laid on the anvil-stone, and no patience for carrying four mediocre things when the forge could make two good ones. "Every warrior in this camp bets on one pairing or the other," she says, banging her hammer flat for quiet. "Feed me your strikes, or feed me your guards — I only fold one kind at a time, and I fold it right." A Tatankasaur snorts approval from its stall, already used to being right about these things.

- **Combine Strikes** — Remove 2 Strike (Ironclad) from your Deck. Add Ultimate Strike to your Deck.
- **Combine Defends** — Remove 2 Defend (Ironclad) from your Deck. Add Ultimate Defend to your Deck.

Mechanics check: matches harvest.

---

## - [ ] Brain Leech
### The Ear-Whisperer — Natlan / Children of Echoes — literal

On the scree slopes of Tepeacac Rise, a Children of Echoes tracker finds you first — an old memory-leech has fastened behind your ear, feeding you fragments of something it half-remembers. "Let it finish the lesson," she says, "or I rip it clear myself." Either way you learn something today, she promises; the tribe just disagrees on the price. A Qucusaur circles overhead, unbothered, the way it always is when the Echoes start arguing about the past.

- **Share Knowledge** — Choose 1 of 5 random cards to add to your Deck.
- **Rip the Leech Off** — Lose 5 HP. Gain a companion (Colorless) card reward — two cards, following the gallery's own reading of the harvest's template-stripped "Colorless 2 card reward."

Mechanics check: flag — the harvest's "Colorless 2 card reward" is template-lossy; text follows `docs/current/dossiers/content/event-conversion-gallery.md`'s own reading (two companion cards) rather than inventing a count. Separately, `tier05/content/events.yaml` ships this branch as `card_reward: 3` drawn from the character pool (no colorless loot pool exists in the engine) — an engine substitution, not a text discrepancy.

---

Loss: {character} ripped the leech free and did not survive the lesson at the [gold]{event}[/gold].

## - [ ] Bugslayer
### Sweep or Stomp — Natlan / Scions of the Canopy — literal

Deep in the canopy of Coatepec Mountain, a Scions of the Canopy ranger has been thinning a swarm of biting beetles for three days straight and has worn her arm down to two moves. "Sweep or stomp," she says, tossing you the choice like a dare. "Learn one clean and you'll never fumble the other one in." A Yumkasaur chitters at her heel, already scorching the stragglers she missed.

- **Learn Extermination Technique** — Add Exterminate to your Deck.
- **Learn Squash Technique** — Add Squash to your Deck.

Mechanics check: matches harvest.

---

## - [ ] Colorful Philosophers
### The Racing Camp's Wager — Natlan / Masters of the Night-Wind — loose

At the racing camp above Tequemecan Valley, three Masters of the Night-Wind riders corner you between heats, each certain their mount-style is the only one worth learning. Three will get a word in before the starting horn; the rest already know you ride your own way. Each rider bets a full set on their color — one common trick, one solid one, and one they'll only show you if you lose.

- **Red — the Flame-Runner's wager** — Obtain 3 Ironclad cards.
- **Green — the Wind-Strider's wager** — Obtain 3 Silent cards.
- **Blue — the Storm-Rider's wager** — Obtain 3 Defect cards.
- **Pink — the Bone-Caller's wager** — Obtain 3 Necrobinder cards.
- **Orange — the Sun-Chaser's wager** — Obtain 3 Regent cards.

Mechanics check: matches harvest (up to 3 of the 5 are shown per visit, per the harvest's own "Up to 3 options are shown"); the pool names (Ironclad, Silent, Defect, Necrobinder, Regent) are the engine's own card-pool ids and are kept verbatim rather than translated, as the harvest states them. Flag — not modelled in tier05/content/events.yaml (skip list: cross-character card pools); no Teyvat-native referent exists for those five pools regardless of face.

---

## - [ ] Colossal Flower
### The Bloom of Tequemecan — Natlan / Flower-Feather Clan — literal

In the high meadows of Tequemecan Valley grows a flower the size of a war-drum, and the Flower-Feather Clan has been daring each other into it for a generation. Reach past the outer petals and the nectar runs sweet and easy. Reach again, and the bud tightens around your arm like it means it. The clan's oldest racer grins at you over the rim: "Third reach or nothing, if you've got the nerve for the heart of it."

- **Tap the Nectar** — Gain 35 Gold.
- **Reach Deeper** — Lose 5 HP. Advance to the next level.
  - *Level 2:* **Tap the Nectar** — Gain 75 Gold. **Reach Deeper** — Lose 6 HP. Advance to the next level.
  - *Level 3:* **Tap the Nectar** — Gain 135 Gold. **Reach the Bloom's Heart** — Lose 7 HP. Obtain the Bloom's Heart (Pollinous Core, relic).

Mechanics check: matches harvest and tier05/content/events.yaml (`colossal_flower` / `colossal_flower_2` / `colossal_flower_3`) exactly.

@pages.INITIAL.options.EXTRACT_CURRENT_PRIZE_1 | Tap the Nectar — Gain 35 Gold.
@pages.INITIAL.options.REACH_DEEPER_1 | Reach Deeper — Lose 5 HP. Advance to the next level.
@pages.REACH_DEEPER_1.description — Past the outer petals the nectar thickens and the flower closes a little around your arm. The clan's drummer starts a slow beat: the count for how long you keep it in.
@pages.REACH_DEEPER_1.options.EXTRACT_CURRENT_PRIZE_2 | Tap the Nectar — Gain 75 Gold.
@pages.REACH_DEEPER_1.options.REACH_DEEPER_2 | Reach Deeper — Lose 6 HP. Advance to the next level.
@pages.REACH_DEEPER_2.description — Shoulder-deep now. The drumming is faster, the petals are tight enough to bruise, and something at the flower's heart is warm and pulsing under your fingers.
@pages.REACH_DEEPER_2.options.EXTRACT_INSTEAD | Tap the Nectar — Gain 135 Gold.
@pages.REACH_DEEPER_2.options.POLLINOUS_CORE | Reach the Bloom's Heart — Lose 7 HP. Obtain the Bloom's Heart.
@pages.EXTRACT_CURRENT_PRIZE.description — You pull free with your arm slick to the elbow, and the drummer stops mid-beat. The clan pays out the wager without complaint.
@pages.EXTRACT_INSTEAD.description — You pull free with your whole side aching, and the drummer stops. The clan pays out the biggest wager of the season and says nothing about the heart.
@pages.POLLINOUS_CORE.description — The flower shudders and lets go. What you hold is warm, heavy and humming, and every Flower-Feather warrior in the meadow is looking at it.

---

## - [ ] Crystal Sphere
### The Springs' Grid — Natlan / People of the Springs — loose

At the Toyac Springs, a People of the Springs elder keeps a broad basin of still water ruled into an eleven-by-eleven grid of stones, each one hiding something under the silt. Clear a stone at a time, she says, or sweep a handful at once — either way you're paying for the clearing, not for what's under it. One custom you settle now; the other, she says, the springs settle after.

- **Pay the Springs' Toll** — Pay 51-99 Gold. Divine 3 times.
- **Take the Springs' Long Debt** — Gain a Debt. Divine 6 times.

Mechanics check: matches harvest for the two entry options and numbers. Flag — the grid-uncover minigame (11×11 grid, tile sizes, the reward table) is spatial/UI mechanics the text cannot fully carry, and is not modelled in tier05/content/events.yaml (skip list: Divine/Debt unmodeled).

---

## - [ ] Doll Room
### The Totem Shelf — Natlan / Children of Echoes — loose

Before a warrior enters the Stadium of the Sacred Flame, the Children of Echoes keep a shelf of small carved totems — each one holding a scrap of an ancestor's luck, the kind the Wayob still remembers even when the living don't. Take one blind and trust the shelf. Or spend a little of yourself sorting through it, and trust your own eye instead.

- **Take One Blind** — Obtain a random totem charm (Doll Relic).
- **Sort Through Two** — Lose 5 HP. Choose 1 of 2 totem charms (Doll Relics).
- **Read Every Totem on the Shelf** — Lose 15 HP. Choose 1 of 3 totem charms (Doll Relics).

Mechanics check: matches harvest. Flag — the Doll Relic family (which specific relics these totems grant) has no Teyvat naming hook of its own; text stays generic ("totem charm"), and this event is not modelled in tier05/content/events.yaml (skip list: three new hooks needed, plus a "choose 1 of N" op).

---

Loss: {character} read every totem and had no luck left at the [gold]{event}[/gold].

## - [ ] Field of Man-Sized Holes
### The Cookfire Pits — Natlan / Collective of Plenty — literal

The cookfire grounds at Mictlan are pocked with holes this season, each one sized exact to a person, rims smooth as a mold. Nobody dug them and nobody's found the bottom. The Collective's cooks have started betting on who fits which hole. "Get in," says the eldest, not looking up from the spit. "Or walk off and let two things go instead — your call, but the pot's already opened."

- **Enter Your Hole** — Enchant a card with Perfect Fit.
- **Resist** — Remove 2 cards from your Deck. Add Normality (curse) to your Deck.

Mechanics check: matches harvest and tier05/content/events.yaml (`field_of_man_sized_holes`) exactly.

---

## - [ ] Infested Automaton
### The Ticking Relic — Natlan / Children of Echoes — literal

Half-buried on the Tepeacac Rise scree, a machine older than any tribe's memory still ticks with something inside it — Night Kingdom make, the Children of Echoes say, plain as anything, the way they say most things that would scare another tribe silent. Study the ticking and it teaches you something with weight to it. Touch the core direct and it hands you something instant, no weight at all.

- **Study** — Obtain a random Power card.
- **Touch the Core** — Obtain a random 0-cost card.

Mechanics check: matches harvest and tier05/content/events.yaml (`infested_automaton`) exactly.

---

## - [ ] Potion Courier
### The Overshot Drop — Natlan / Masters of the Night-Wind — literal

A Night-Wind courier overshot her drop on the ridge above Tequemecan Valley and the satchel burst wide — three bottles of something rough and mostly spoiled, and underneath, sealed better, one bottle she was actually paid to carry. "Grab the cheap stuff by the handful," she calls down, already remounting, "or dig for the one that's worth the climb. I'm not waiting on your decision."

- **Grab Potions** — Procure 3 Foul Potions.
- **Ransack** — Procure 1 random Uncommon Potion.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: Foul Potion card not authored; "3 Foul Potions" would strictly beat "1 random potion" without it).

---

## - [ ] Ranwid the Elder
### The Canopy Elder's Ledger of Gifts — Natlan / Scions of the Canopy — literal

An elder of the Scions of the Canopy keeps a nest of everything the forest has handed back to her over a long life, high in the branches of Coatepec Mountain. She trades plain: give something, get something, no counting owed either way. A potion earns a relic. A hundred coin earns a relic. And if you've got something rarer to offer — she won't name it for you, but she'll know it when she sees it — she'll match it with two.

- **Offer a Potion** — Obtain a random Relic.
- **Offer 100 Gold** — Obtain a random Relic.
- **Offer the Greater Gift** — Obtain 2 random Relics. (The harvest's third option reads "[Give ]" — the offered item is stripped by template-stripping.)

Mechanics check: flag — the harvest's third option name is template-lossy ("[Give ]"), unresolved without a targeted re-harvest; text follows the gallery's own reading (an unnamed "greater gift") rather than inventing a name. Flag — not modelled in tier05/content/events.yaml (skip list: HeldRelics has no removal op for trading away a held relic, if that is what the blank names).

---

## - [ ] Relic Trader
### The Mictlan Trade-Circle — Natlan / Collective of Plenty — loose

At the Mictlan trade-circle, a Collective broker has three things laid out on a woven mat — top, middle, bottom — and won't say what any of them are until you've already reached. "Half the fun's in not knowing," he says, "and I'm not explaining it. Point, and it's yours."

- **Take the Top One** — Trade for the top item.
- **Take the Middle One** — Trade for the middle item.
- **Take the Bottom One** — Trade for the bottom item.

Mechanics check: flag — all three options are template-lossy on the wiki ("Trade for ."), the traded item names stripped entirely; text follows the gallery's own generic reading (top/middle/bottom) rather than inventing names. Flag — not modelled in tier05/content/events.yaml (skip list: options are generated from the run's own held relics; the wiki page has no static text to harvest).

---

## - [ ] Room Full of Cheese
### The Under-Stands Cellar — Natlan / Flower-Feather Clan — literal

Under the stands at the Stadium of the Sacred Flame, the Flower-Feather Clan keeps a cellar of festival prizes nobody claimed — eight of them laid out, no two alike. Pick your two and walk off happy, or dig past the racks for the one prize the clan swears is still down there, buried deep enough to cost you something getting to it.

- **Gorge** — Choose 2 of 8 random Common cards to add to your Deck (the eight are never duplicates).
- **Search** — Lose 14 HP. Obtain the Buried Prize (The Chosen Cheese, relic): at the end of combat, gain 1 Max HP.

Mechanics check: matches harvest. Flag — tier05/content/events.yaml ships the Search branch as a plain random relic (`relic: true`) rather than The Chosen Cheese — the file's one flagged substitution (no `post_fight` max-HP hook yet). This text keeps the harvest's real relic per the "options exactly as the harvest gives them" instruction, so the shipped engine reward currently understates what this text promises.

---

Loss: {character} was buried under the stands at the [gold]{event}[/gold].

## - [ ] Spirit Grafter
### The Springs' Rooted Thing — Natlan / People of the Springs — loose

At the Toyac Springs, something has rooted in the wet stone that isn't quite plant and isn't quite anything the People of the Springs have a clean word for. It offers to knit into you and close every wound at once. Their binder warns you plainly, the way her people always do: it heals wonderful, and it stays.

- **Let It In** — Heal 25 HP. Add Metamorphosis to your Deck.
- **Rejection** — Lose 9 HP. Remove 1 card from your Deck.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: Metamorphosis creates 3 random Attacks in the draw pile free this combat; no card-creation op).

---

Loss: {character} tore the rooted thing out and did not survive it at the [gold]{event}[/gold].

## - [ ] Stone of All Time
### The Slab on the Ancient Sacred Mountain — Natlan / Masters of the Night-Wind — literal

On the Ancient Sacred Mountain, a slab older than any tribe's founding sits where it fell, and the Night-Wind riders dare each other at it between races. Drink something down first and lift with a clear head, or refuse the bottle and put your whole back into it instead. Either way something in you changes for good.

- **Drink and Lift** — Lose a random potion. Gain 10 Max HP.
- **Push** — Lose 6 HP. Enchant an Attack with Vigorous 8.

Mechanics check: matches harvest and tier05/content/events.yaml (`stone_of_all_time`) exactly.

---

Loss: {character} was crushed under the slab at the [gold]{event}[/gold].

## - [ ] Symbiote
### The Blade That Breathes — Natlan / Children of Echoes — literal

A blade left out on a Tepeacac Rise slope has picked something up that moves along the steel like it's breathing. The Children of Echoes know this for what it is and don't flinch from naming it: take it up and it hits harder for what it costs you every swing, or burn it clean and let the weapon become something else entirely.

- **Approach** — Enchant an Attack with Corrupted.
- **Kill with Fire** — Choose a card to Transform.

Mechanics check: matches harvest and tier05/content/events.yaml (`symbiote`, `also_acts: [3]`) exactly.

---

## - [ ] Tea Master
### The Festival Brew-Stand — Natlan / Flower-Feather Clan — literal

At the festival grounds, a Flower-Feather brewer pours three cups and names her price for each before you've even sat down — that's the custom, she says, not a courtesy. Pay for the sharp one and your opening hand comes out honed. Pay more for the slow-burning one and you run hot for five whole bouts. Or take the free cup, which she pours for anyone, and warns you about first.

- **Bone Tea** — Pay 50 Gold. At the start of the next combat, Upgrade your starting hand.
- **Ember Tea** — Pay 150 Gold. At the start of the next 5 combats, gain 2 Strength.
- **Tea of Discourtesy** — At the start of the next combat, shuffle 2 Dazed into your Draw Pile.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: no next-combat buff channel; relics inject into combat, events currently do not).

---

## - [ ] The Lantern Key
### The Marker Off the Racetrack — Natlan / Masters of the Night-Wind — loose

A Night-Wind racer clipped a marker-lantern off its post mid-race and hasn't slowed down long enough to feel bad about it. Turn it back in at the circuit and the stewards pay the standing bounty, no questions. Or keep it — but whatever's been guarding that post is already climbing down to ask for it back, in the one language a guard post understands.

- **Return the Key** — Gain 100 Gold.
- **Keep the Key** — Enter combat against a Mysterious Knight for the Lantern Key card.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: quest cards, including the Lantern Key card itself, are not modeled).

---

## - [ ] The Lost Wisp
### The Drifting Light — Natlan / Children of Echoes — literal

A stray light drifts loose over the Tepeacac Rise scree, guttering like it's lost its court. The Children of Echoes have a plain rule for such things, the same one they have for most of what the mountain keeps: bottle it and it answers you back, at a cost the tribe never pretends is free. Or leave it be and work the ground it's hovering over instead, where something older than the light has been sitting untouched.

- **Capture the Wisp** — Add Decay (curse) to your Deck. Obtain the Lost Wisp (relic).
- **Search the Nearby Area** — Gain 45-75 Gold.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: needs an on-card-played combat hook for "whenever you play a Power, 8 AoE damage").

---

## - [ ] Welcome to Wongo's
### The Mictlan Tally Stall — Natlan / Collective of Plenty — literal

At the busiest stall in Mictlan, a Collective trader keeps a running tally chalked on a hide behind the counter — every purchase you make here follows your name for good, she says plainly, same as every debt does. The bargain crate is cheap and quick. The featured piece is pricier and named up front, no surprises. The sealed box costs the most and pays out slow, after five bouts have come and gone. Walk off with nothing, and she'll still take a look at your gear on the way past.

- **Wongo's Bargain Bin** — Pay 100 Gold. Obtain 1 random Common Relic. Also receive 32 Wongo Points.
- **Wongo's Featured Item** — Pay 200 Gold. Obtain a named Rare Relic (randomly selected from the standard rare relic pool). Also receive 8 Wongo Points.
- **Wongo's Mystery Box** — Pay 300 Gold. Obtain 3 random Relics after 5 combats (carry Wongo's Mystery Ticket until then). Also receive 16 Wongo Points.
- **Leave** — Downgrade a random card.

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: needs relic-rarity tiers, a delayed grant after N combats, and a downgrade-targeting op); Wongo Points are cross-run, profile-level meta-currency that the tally framing gestures at but does not implement.

---

## - [ ] Zen Weaver
### The Springs' Eight-Strand Weaver — Natlan / People of the Springs — loose

At the Toyac Springs, a weaver works eight strands at once, and half her trade isn't cloth at all — it's people, and the bad habits she says are only knots a patient hand can work loose. Pay the least and she teaches your hands to move lighter. Pay more and she picks a single tangle out of you for good. Pay the most and she takes two.

- **Breathing Techniques** — Pay 50 Gold. Add 2 Enlightenment to your Deck.
- **Emotional Awareness** — Pay 125 Gold. Remove 1 card from your Deck.
- **Arachnid Acupuncture** — Pay 250 Gold. Remove 2 cards from your Deck. (Emotional Awareness and Arachnid Acupuncture lock if you don't have enough Gold.)

Mechanics check: matches harvest. Flag — not modelled in tier05/content/events.yaml (skip list: Enlightenment sets every card in hand to cost 1; no cost-rewrite op).

---

## - [ ] Self-Help Book
### The Hollow-Tree Guide — Natlan / Scions of the Canopy — loose

A Scions of the Canopy scout found a stitched-together guide wedged in a hollow tree on Coatepec Mountain, left by some outsider who clearly meant to come back for it. Every page bets on a different discipline — a sharpened swing, a lighter guard, a quicker draw — and she's read enough to know only one page will actually apply to what you're carrying. "Take the page that fits your kit," she says, "or don't bother — I'm not walking you through pages that don't."

- **Read the Back** — Choose an Attack to Enchant with Sharp 2.
- **Read a Random Passage** — Choose a Skill to Enchant with Nimble 2.
- **Read the Entire Book** — Choose a Power to Enchant with Swift 2.
- **Move On** — Nothing happens. (Each reading is offered only if you hold a card of that type; Move On is offered only when you hold none.)

Mechanics check: matches harvest and tier05/content/events.yaml (`self_help_book`) exactly.

---

## - [ ] Slippery Bridge
### The Rope Crossing at Coatepec — Natlan / Masters of the Night-Wind — literal

The rope-and-plank crossing above Coatepec Mountain has seen better seasons, and it groans under your kit the moment you commit to the middle span. A Night-Wind rider waiting on the far side calls out the wager the crossing always makes: let it take one thing from your pack now, clean, or hold on and let the wind decide which piece hangs loose next — at a steeper price every time you refuse to choose.

- **Overcome** — A specific card is removed from your Deck.
- **Hold On** — Lose 3 HP. The card named in the above option is randomized, and the HP cost rises by 1 each further time you choose this option. (The card is drawn from all cards without Eternal; the first card offered is never Basic rarity unless every card you hold is; the same card is never offered twice while others remain unoffered.)

Mechanics check: matches harvest.

---

Loss: {character} fell from the rope crossing at the [gold]{event}[/gold].

## - [ ] The Future of Potions?
### The Mictlan Rig — Natlan / Collective of Plenty — loose

A Collective trader at Mictlan has built a rig that reads a concoction for the technique hidden in it, rather than just drinking it down like everyone else does. Only the first three bottles on your belt fit the rig, leftmost first — she's not sorting your pack for you. Whatever you feed it, you walk away better armed than you walked in, upgraded to match what the bottle was worth.

- **Insert Common Potion** — Lose a specified Common potion. Obtain an Upgraded Common [Attack/Skill] card reward.
- **Insert Uncommon Potion** — Lose a specified Uncommon potion. Obtain an Upgraded Uncommon [Attack/Skill/Power] card reward.
- **Insert Rare Potion** — Lose a specified Rare potion. Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Insert Event Potion** — Lose a specified Event potion (only Foul Potion or Glowwater Potion qualify). Obtain an Upgraded Rare [Attack/Skill/Power] card reward.
- **Insert Token Potion** — Lose a specified Token potion (only Potion-Shaped Rock qualifies). Obtain an Upgraded Common [Attack/Skill] card reward.

Mechanics check: matches harvest's full 5-tier version (the first 3 potions in your slots are offered, leftmost first; each option's Attack/Skill/Power split is randomized). Flag — tier05/content/events.yaml ships a collapsed 2-option version (`spend_potion` + `card_reward: 3` + `upgraded: true`, plus Leave) rather than the harvest's 5-tier ladder; an engine simplification, not a text discrepancy.

@pages.DONE.description — The rig chews through the bottle, clicks twice, and hands back the technique on a strip of scorched hide. The trader is already reaching for your belt again.

---

## - [ ] This or That?
### The Unclaimed Crates — Natlan / Flower-Feather Clan — literal

Two crates turned up unclaimed after the last relay through Tequemecan Valley, and the Flower-Feather quartermaster running the prize table isn't in the mood to sort them. Pry the first and something in the latch bites back on the way to a fistful of coin. Or take the second, gear that's plainly worth more and plainly cursed to trip you on every third step — she'll let you decide which kind of trouble you'd rather carry.

- **This** — Lose 6 HP. Gain 57 Gold.
- **That** — Add Clumsy (curse) to your Deck. Obtain a random Relic.

Mechanics check: matches harvest and tier05/content/events.yaml (`this_or_that`) exactly.

Loss: {character} bled out on a crate latch at the [gold]{event}[/gold].

