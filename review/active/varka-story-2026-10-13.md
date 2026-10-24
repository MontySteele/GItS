# Varka's story in the run (2026-10-13)

*Rewards repriced 2026-10-19 by the story rewards pass (`story-rewards-pass-2026-10-19.md`, ruled all (a)); the rows below carry the new effects.*

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

> **The Grand Master of the Knights of Favonius.** He led the Knights north against the Abyss, leaving Mondstadt in Jean's care. The Abyss's trail runs up the Spire, so up he goes.

Trimmed 2026-10-20 to fit the character-select box (the last sentence pushed the starter relic out of it). [USER] picked keeping Jean over "getting his people home".

## 2. The Ancients greet him

| Ancient | The Ancient | Varka |
|---|---|---|
| Neow | "[sine]...knight...<br>..will you go... ..up...?[/sine]" | "Up, then home. My people are waiting." |
| Orobas | "Big knight! Big pack! What inside? Show!!" | "Rations, mostly. And a few things worth more than they look." |
| Pael | "[thinky_dots]So many walk behind you...<br>Let my strength carry some of them...[/thinky_dots]" | "I'll take it. They're heavier than they look." |
| Tezcatara | "Such a big strong boy! Eat something. Can't climb on an empty stomach!" | "Now that's an order I can follow." |
| Nonupeipe | "That armor has seen better days. Come forth, knight, and be made splendid." | "Splendid's fine. Sturdy's better." |
| Tanx | "TWO SWORDS! NOW THAT IS MORE LIKE IT!!" | "Ha! I knew you'd approve." |
| Vakuu | "You realize your knights may [sine]never[/sine] see home?" | "They will. Name your price, and keep it honest." |
| Darv | "Grand Master! Got just the thing for ya... somewhere in here..." | "Got a whetstone in there? Mine's about worn through." |

## 3. Act 1: Dispatch from Mondstadt

> A Favonius courier catches up with Varka on the stairs, out of breath, a satchel of reports under one arm. "From the Acting Grand Master, sir. She says you'll know which ones."

| Option | Effect | Why |
|---|---|---|
| **Stop to sign every one of them.** | Upgrade 2 random cards. | Jean won't believe it. |
| **Sign them later.** | Gain 75 Gold. Add **Overdue Reports** to your deck. | The courier carries his travel pay too. The reports follow him anyway. |
| **Request reinforcements for the expedition.** | Choose 1 of 3 random Uncommon Companions to add to your deck. | The Knights answer their Grand Master. |

**Overdue Reports** is a Varka-only curse built like Klee's Confinement: "Unplayable. After 3 combats, remove this from your deck." Jean always catches up with him eventually.

## 4. Act 2: The Wolf of the North

> Frost spreads across the landing. Andrius takes shape beside Varka, stretches, and bares his teeth. The Wolf of the North gave him his title, and Varka knows that look well enough: his old partner wants a spar.
>
> *"You've gone soft, Knight."* — *"Soft? Come over here and say that."*

| Option | Effect | Why |
|---|---|---|
| **Spar with him.** | Lose 12 HP. Upgrade 3 random cards. | Boreas never goes easy. Neither did Varka, with Eula. |
| **Rest at his side.** | Heal 20 HP. | Even a Grand Master can take a breather. |
| **Ask after the pack.** | Choose 1 of 3 random Uncommon Attacks to add to your deck. | "The boy is eating well?" The wolves raised him; Varka taught him to fight. |

## 5. Act 3: The Long Way Home

> Favonius banners come into view on the stairs below. His expedition has caught up, with familiar faces from Mondstadt among them. After five years away, Varka has quite a welcome waiting. Jean folds her arms. "You owe me five years of reports, Grand Master." Eula, Noelle, and Diluc step forward.

| Option | Effect | Their line |
|---|---|---|
| **Eula** | Choose 1 of 3 random upgraded Uncommon Attacks to add to your deck. | "You still owe me a rematch. Don't you dare go easy." |
| **Noelle** | Choose 1 of 3 random upgraded Uncommon Skills to add to your deck. | "Welcome back, Grand Master! Please, let me take the front line." |
| **Diluc** | Choose 1 of 3 random upgraded Uncommon Powers to add to your deck. | "There's a bottle at Angel's Share with your name on it. You're paying." |
| **Wave them back to the column.** | Nothing. | "Stay with the others. I'll meet you all at the foot of the stairs." |

Each knight offers an Uncommon of his pool by type (Eula Attacks, Noelle Skills, Diluc Powers; until the story rewards pass, the three named cards `proto_vk_eula_icetide_vortex`, `proto_vk_noelle_steadfast_maid`, `proto_vk_diluc_searing_onslaught`). Diluc left the Knights and never liked Varka's ways, but he still keeps a table for him at his tavern. When one steps out, Varka answers: "Ha, good to have you here! Come on, we're nearly there."

## 6. Lines in combat (speech bubbles)

| When | Varka says |
|---|---|
| Entering a boss fight | "Well, you're a big one! Let's make some room." |
| Below a third of his HP | "Easy now. I've got another round in me." |
| Four Winds' Ascension | "By Lord Barbatos!" |
| Killing a boss | "Someone write that down. Not me!" |
| Losing the run | "Tell Jean... we're running a little late." |
| Winning the run | "Knights of Favonius, we're going home!" |

## 7. Co-op pair lines (at each boss)

| Pair | Lines |
|---|---|
| Varka and Klee | (written with Klee's batch) Varka: "Spark Knight. Same orders as always." Klee: "No bombs indoors. ...Is this indoors?" |
| Varka and Kokomi | Varka: "See that gap on the left? Bet I can get us through." Kokomi: "I see it. Go ahead; I'll cover you." |
| Varka and Furina | Furina: "The Grand Master himself! Do try not to upstage me." Varka: "Wouldn't dream of it." |

## The arc in one line

He left on an expedition and kept walking (intro), Mondstadt's paperwork finds him (act 1), Boreas tests his partner (act 2), and his Knights come to walk him home (act 3). His victory line closes it.

## Revised 2026-10-13

[USER]'s edits are in place: the Neow, Orobas, Nonupeipe and Vakuu replies,
the act 1 option names, Jean's "five years", the Ascension, boss-kill, loss
and win lines, and the shorter Furina reply. "The lore on Andreas looks a
little wrong. Boreas is Varka's partner - he is a fragment of Andreas, who
faded back to the Ley Lines during Varka's story quest. I think the act 2
event works using Boreas instead, though. Line 2 seems a touch too formal."
"The expedition was gone for 5 whole years." "Also - are all of these cards
the same rarity?" (No: act 3 now offers three Commons.) "The kokomi line
needs a rework. Varka's own role in Nod-Krai is that of a strategist; he's
not a dumb brute." Rewritten by Claude: the intro's third line, act 2, act
3's Kaeya and Mika, the Kokomi pair.

Second round, 2026-10-13. [USER]: "For an act 3 event, 3 commons is kinda
meh. Can we upgrade it to give one of three uncommons and have an option to
skip as well? For Varka's Kokomi co-op - reads too formal. Varka's pretty
laid back. Otherwise the changes sounds good!" Act 3 now offers Eula, Noelle
or Diluc (Uncommons) or a skip; Jean's line moved to the scene.

Third round, 2026-10-13. [USER]: "I like the Eula line, but the Noelle line
sounds off, and Diluc reads a little too edgy." Both rewritten.

## Ruled

[USER], 2026-10-13: "Sounds good! Let's go with it." Built as written.

## For [USER] (ruled above)

1. **The batch.**
   - **(a) Default:** build it as written.
   - (b) Changes first (name the lines).

## Dialogue cleanup, 2026-10-13

[USER]: "I want to do a clean-up pass on both, since some things feel oddly stilted to me." The current lines above reflect that pass. Voice, lore caveats, and the other dialogue surfaces are reviewed in `review/active/klee-varka-dialogue-review-2026-10-13.md`. Event effects and story outcomes are unchanged.
