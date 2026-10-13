# Klee and Varka: dialogue cleanup (2026-10-13)

[USER]: "I want to do a clean-up pass on both, since some things feel oddly stilted to me."

**Verdict:** both are recognizable, but the old lines often reduce Klee to bombs and punishment and Varka to paperwork and slogans. The issue is mostly voice and repetition, with a few relationship and continuity problems. This pass edits text only. The revised story papers and runtime tables agree; event choices, rewards, combat triggers, and cards retain their behavior.

## What I checked

| Surface | Source and disposition |
|---|---|
| Character-select title and introduction | `KleeCode/Story/KleeStory.cs`, `VarkaStory.cs`; both introductions revised. |
| Aroma principle, living/dead end-turn ping, bestiary quote, event death prevention, gold monologue | `KleeCode/Klee.cs`, `Varka.cs`; all six rows per character read, eight revised in total. Dead pings remain silence. |
| Eight Ancient exchanges per character | Both story tables; every greeting and reply read. Klee's replies revised throughout; Varka keeps five of eight. Ancient speakers retain their existing lines. This is a character-voice review, not a separate certification of the eight Ancients' voices. |
| Six combat/run lines per character | Both story tables; Klee keeps KABOOM, Varka keeps his signature, boss-kill, loss, and victory lines. |
| Five co-op exchanges involving either character | Both story tables; Klee/Furina and Varka/Kokomi revised; Klee/Kokomi, Klee/Varka, and Varka/Furina retained. |
| Architect finales | `tools/build_pck.ps1`, the `ancients.json` here-string; both character replies and Varka's prompt revised. Repeating keys and speaker order retained. These lines live outside the story tables. |
| Six custom events | Both story tables; every body, option title, effect description, and result read. Revised Jean's letter, Klee's reunion, and Varka's wolf/reunion narration. Act-1 scenes and all effect descriptions retained. |
| Adjacent text | Confinement/Overdue Reports, relic/potion localization, story localization and event-result fallbacks, and Teyvat event/Ancient routing checked. Relics and potions contain rule descriptions rather than a separate character-dialogue bank. Generic Teyvat conversion prose is not Klee/Varka speech; the Teyvat frame is off in `STATE.md`. Card rules and names were not rewritten as dialogue. |

Paths beginning `KleeCode/` are under `klee-mod/`. Source papers: `review/ruled/klee-story-batch-1-2026-10-12.md`, `review/active/klee-story-batch-2-2026-10-12.md`, and `review/active/varka-story-2026-10-13.md`.

## Klee

The clearest relationship problem was offering "a Dodoco" in a trade. Dodoco is her treasured friend. She can offer a pebble while explicitly keeping Dodoco. Her English speech mixes first person with occasional self-naming; constant "Klee" made the old batch sound like an imitation of a small child. Her curiosity, generosity, and attachment to people should appear alongside her enthusiasm for explosives. Those readings follow the game's [English voice-over transcript](https://genshin-impact.fandom.com/wiki/Klee/Voice-Overs).

The cleanup also removes an invented claim about small hands being necessary for good bombs. The old Tanx answer made avoiding Jean her reason to fight; the replacement returns to the adventure and bringing presents home. Jean's letter now sounds concerned and firm. Kaeya no longer conceals something Jean already knows; Noelle offers practical care, and Albedo sounds like someone responsible for Klee rather than a spectator taking notes on her explosions.

| Before | After |
|---|---|
| "Klee has... three pebbles and a Dodoco." | "You can have this shiny pebble! But Dodoco stays with me." |
| "Klee leaves craters. Do you want one?" | "Oh! Have you seen any little round bombs? I dropped one..." |
| "I brought snacks. And a shield. Mostly the shield." — Noelle | "Are you hurt, Klee? Here, have something to eat. I'll stay with you." |

## Varka

His [English voice-over transcript](https://genshin-impact.fandom.com/wiki/Varka/Voice-Overs) supports a relaxed, boastful, protective leader who enjoys jokes and takes practical responsibilities seriously. Formal language is possible when he makes a pledge; it should not turn every exchange into an inscription. The old "my own hungers" aroma line and "Mondstadt's wind was never mine to keep" finale were especially stiff. Borrowing Kokomi's "planning face" also weakened his own competence.

He keeps the drinking-song joke, the unsigned reports, his short Furina reply, and the existing Eula/Noelle/Diluc reunion lines. His new Kokomi exchange has him spot an opening and her cover his advance. His ordinary boss entry no longer declares that he is alone when Knights or co-op allies may be present. The reunion distinguishes the expedition from the familiar faces who came from Mondstadt, avoiding the implication that Jean, Noelle, and Diluc all served on that expedition.

| Before | After |
|---|---|
| "You've got your planning face on. Mind if I borrow it?" | "See that gap on the left? Bet I can get us through." |
| "Then you'll want my desk. I left it to Jean." | "Found a whetstone, by any chance? Mine's about worn through." |
| "All four. A knight never rides alone, and Mondstadt's wind was never mine to keep." | "After all those stairs? Come on, let's finish this. My people are waiting." |

## Lore limits and review

This is an original crossover story. Alice's treasure advice, visits to the Spire, the courier and pigeon, and the reunions are inventions, not claims about Genshin quests. The five-year expedition and Boreas-as-partner details retain the user's explicit corrections in the Varka story paper. Indexed [Lonely Warrior quest dialogue](https://www.hoyodex.com/wiki/genshin-impact/lonely-warrior) supports the distinction between Andrius returning to the Ley Lines and Varka retaining a vessel for the soul; it does not establish this invented sparring scene.

The official Varka teaser page exposed no readable transcript, and direct wiki fetches failed. The comparison therefore uses search-indexed reproductions of in-game English dialogue, not a fresh in-game viewing. I would not treat the older `varka-lore-census-2026-10-13.md` as verified canon. Whether a line feels natural is an editorial judgment; these patterns do not prove AI authorship.

## Verification

The final full Python run passed: **8,142 passed, 129 skipped**. All **27 CI lints** passed, and `git diff --check` was clean. A separate text check confirmed that all changed story prose appears in its source paper, the four edited C# files retain their non-text structure, and the Architect JSON retains every key with only the three intended values changed. **44 text entries** were revised.

The C# story tests could not run because this machine has no configured `GameDir`. No game build or live visual check was performed. The first Python run's 16 Git-tooling failures were resolved by selecting the installed Git 2.53 instead of the worktree's default Git 2.13. The cleanup is a local draft on `dialogue-cleanup-1013`, not a deployed build.

1. **Recommended:** review this text-only cleanup as the next dialogue draft. The source papers contain every revised story line; the diff includes the character barks and Architect text. No gameplay pick is needed.
