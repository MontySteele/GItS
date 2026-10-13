# Varka's story in the run (2026-10-13)

**Why.** [USER]: "let's do a similar dialogue touchup pass for Varka that Klee
got". Same shape and rules as Klee's two batches
(`review/ruled/klee-story-batch-1-2026-10-12.md`,
`klee-story-batch-2-2026-10-12.md`): American English, every word ours, each
event offered only to Varka, one per act. Klee's machinery takes another
character by data (`Story/KleeStory.cs` is one table), so nothing new is
built beyond his table and three event classes.

**The test is your friend:** after one run he should know who Varka is, who
he answers to, and why he is climbing.

**Lore.** The census is `varka-lore-census-2026-10-13.md` beside this file.
The wiki and HoYoLAB refused the fetch, so it rests on secondary sources.
These lines use only what several sources agree on: he is Grand Master of the
Knights of Favonius and the Knight of Boreas, he marched most of the Knights
away to fight the Abyss and left Jean as Acting Grand Master, he dodges
paperwork, he taught Razor (raised by Andrius's wolves) to fight, and he
promoted Eula. Nothing here leans on the single-source parts (the Nod-Krai
plot beats).

## 1. The introduction (character select)

> **The Grand Master of the Knights of Favonius.** He marched most of the Knights north to fight the Abyss and left Jean the paperwork. The Spire is on the way home, more or less.

## 2. The Ancients greet him

| Ancient | The Ancient | Varka |
|---|---|---|
| Neow | "A knight. A large one." | "Grand Master, if we're being formal. We're not." |
| Orobas | "Your trinket hums. Let me make it sing." | "Teach it a marching song and we have a deal." |
| Pael | "You have bitten off more than you can chew." | "Every expedition starts that way." |
| Tezcatara | "Warm yourself by my light." | "Gladly. It's been a long winter up north." |
| Nonupeipe | "Two blades. One will." | "And four winds behind them." |
| Tanx | "Do you fight for glory?" | "I fight so my knights get home. Glory can find its own way." |
| Vakuu | "Trade with me." | "I have a stack of unsigned reports. Jean would pay you to take them." |
| Darv | "I collect what others leave behind." | "Then you'll want my desk. I left it to Jean." |

## 3. Act 1: Dispatch from Mondstadt

> A Favonius courier catches up with Varka on the stairs, out of breath, a satchel of reports under one arm. "From the Acting Grand Master, sir. She says you'll know which ones."

| Option | Effect | Why |
|---|---|---|
| **Sign every one of them.** | Upgrade 2 random cards. | Jean won't believe it. |
| **Send them back to Jean.** | Gain 75 Gold. Add **Overdue Reports** to your deck. | The courier carries his travel pay too. The reports follow him anyway. |
| **Write to the expedition.** | Choose 1 of 3 random Knights to add to your deck. | The Knights answer their Grand Master. |

**Overdue Reports** is a Varka-only curse built like Klee's Confinement: "Unplayable. After 3 combats, remove this from your deck." Jean always catches up with him eventually.

## 4. Act 2: The Wolf of the North

> A grey wolf the size of a cart lies across the landing, and frost creeps out from under it. Andrius, the Wolf of the North, has come to see whether the Knight of Boreas still deserves the name.
>
> *"You have grown slow, Knight."* — *"And you've grown grey. Shall we?"*

| Option | Effect | Why |
|---|---|---|
| **Spar with him.** | Lose 12 HP. Upgrade 3 random cards. | The old god never goes easy. Neither did Varka, with Eula. |
| **Bow to the old god.** | Heal 20 HP. | Even a Grand Master knows when to kneel. |
| **Ask after the pack.** | Add an upgraded **Razor: Awakening** to your deck. | "The boy is eating well?" The wolves raised him; Varka taught him to fight. |

## 5. Act 3: The Long Way Home

> Campfires on the stairs below, and banners in Favonius blue. Most of the expedition has come the long way round to walk him home. Three faces step out of the ranks first.

| Option | Effect | Their line |
|---|---|---|
| **Jean** | Add an upgraded **Jean — Wind Companion** to your deck. | "You owe me eleven months of reports, Grand Master." |
| **Eula** | Add an upgraded **Eula: Icetide Vortex** to your deck. | "You still owe me a rematch. Don't you dare go easy." |
| **Kaeya** | Add an upgraded **Kaeya: Hidden Strength** to your deck. | "The tavern's been quiet. Diluc almost misses you." |

These are his existing cards (`proto_vk_jean_dandelion_breeze`, `proto_vk_eula_icetide_vortex`, `proto_vk_kaeya_glacial_waltz`). Varka answers whichever knight steps out: "Good. Then we climb together, and we all go home."

## 6. Lines in combat (speech bubbles)

| When | Varka says |
|---|---|
| Entering a boss fight | "Knights, with me! ...Right. Just me, then." |
| Below a third of his HP | "Still standing. That's the job." |
| Four Winds' Ascension | "By the four winds!" |
| Killing a boss | "Someone write that down. Not me." |
| Losing the run | "Tell Jean... the reports are in my left boot." |
| Winning the run | "Knights of Favonius, we're going home." |

## 7. Co-op pair lines (at each boss)

| Pair | Lines |
|---|---|
| Varka and Klee | (written with Klee's batch) Varka: "Spark Knight. Same orders as always." Klee: "No bombs indoors. ...Is this indoors?" |
| Varka and Kokomi | Varka: "A strategist. Good. I usually just charge." Kokomi: "I noticed. It's already in the plan." |
| Varka and Furina | Furina: "The Grand Master himself! Do try not to upstage me." Varka: "Wouldn't dream of it. I'll be at the back, hitting things." |

## The arc in one line

He left on an expedition and kept walking (intro), Mondstadt's paperwork finds him (act 1), the old god of the north tests the Knight of Boreas (act 2), and his Knights come to walk him home (act 3). His victory line closes it.

## For [USER]

1. **The batch.**
   - **(a) Default:** build it as written.
   - (b) Changes first (name the lines).
