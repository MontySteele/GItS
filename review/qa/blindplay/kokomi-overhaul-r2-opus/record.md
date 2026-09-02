# Blind play session `kokomi-overhaul-r2-opus`

**R217 G, and same model family as the author: subjective feedback from a Claude Opus subagent playing the real game through the blind render. Useful for iteration; not human validation, not balance evidence, not approval.** None of this is a judgement of whether the game is fun or good that anyone will treat as approval. It is one model's account of one run, recorded for iteration.

## Identity
- model: claude-opus (this agent)
- build_version: not printed to the tester
- run_seed: DLTN172Y4QDB (given by the operator)
- actions: 40 posted (a 41st was attempted and never reached the game)
- termination: tool failure. Four calls in a row died with `understudy.bridge.BridgeError: bridge connection failed at http://localhost:15526/api/v1/singleplayer: TimeoutError: timed out` — one `act` and three `observe`. At the moment it broke I was at HP 55/80, floor 3 (the second Monster node), on the Battle round-3 screen of fight 2, energy 5/3 spent down to 4, Fire Potion unused. Twig Slime (M) was at 2 HP and my Water's Edge on it had posted OK; Leaf Slime (S) was at 6 HP and the killing Water's Edge on it is the command that never landed. So the run was one card off winning fight 2 and I never saw its rewards screen.

## Fight 1 — Shrinker Beetle (HP 40/40), in the tester's own words

1. I front-loaded. The beetle's turn-1 intent was "Strategic, This enemy intends to apply a Debuff to you" — no damage — so I spent everything on offence and put the cards that are useless in hand onto the jellyfish. Two Water's Edge for 6 each, and Kurage's Oath written as a Plan. That last one is not really a decision: Kurage's Oath prints *only* a Plan line, so the jellyfish is the only thing it can be aimed at. From turn 2 on the beetle's Shrink debuff ("While Shrinker Beetle is alive, your Attacks deal 30% less damage") quietly cut my card damage — Water's Edge started printing 4 instead of 6 — so the fight turned into a race where my two *non-attack* damage sources, the planned Oath (a skill, so Shrink never touched its 5) and the relic's Hydro pings, did more of the work than my actual attacks. That was the moment the character clicked for me.

2. The real alternative was planning Battle Plan on turn 1 for the +2 energy and a card. I passed because the beetle's intent jumped to 13 on round 3 and I would rather have had a 5-block Coral Guard in that slot than two energy in a fight I could already see the end of. I think that was right — I finished the fight at 56/80 having eaten exactly one 8.

3. Yes, badly. If turn 1 had shown an attack intent instead of the debuff, I would have blocked instead of double-attacking and the fight runs two turns longer under Shrink, which is the worst thing that can happen to me. And the draw mattered a lot: turn 2 gave me three Coral Guards and one attack. If that hand had come up on turn 1 I would have had almost no pressure at all.

4. Automatic: Water's Edge, every time, at the only enemy — there is never a reason not to. Dead as *cards*: Vanguard and Kurage's Oath, which do nothing if you play them normally, so "put it on the jellyfish" is not a choice, it is the card's only mode. Deep Current went dead in a single-target fight (4 damage to every enemy became 2 under Shrink, against one enemy, for a full energy).

5. Yes, on round 3 when the intent went to 13. Up to then I was thinking about ramping; after that I just paid one card per turn for block and let the jellyfish carry the offence. Also on round 3 I realised Vanguard is effectively a free 6 damage rather than a debuff card, because it costs 0 and the relic converts each of its two debuffs into a Hydro ping.

6. Three things. Hydro Aura shows on the enemy tagged **(buff)** in the same list as Vulnerable and Weak, which read (debuff) — so the thing I applied to hurt them reads as their buff. Vanguard prints "Exhaust." twice in one line. And Shrink silently rewrote the damage numbers on my own cards with no marker saying they had been modified, so I was re-deriving my damage from scratch every turn.

## Fight 2 — Twig Slime (S) (HP 8/8), Twig Slime (M) (HP 26/26), Leaf Slime (S) (HP 15/15) — in progress at cutoff

1. The three-enemy board is where this kit wants to be, so I opened with the AoE and used the extra bodies to make the jellyfish pay. Deep Current for 4 to all, then Water's Edge to finish Twig Slime (S) — the only one of the three with an attack intent — which meant I took zero damage on round 1 and could spend the leftover on two Plans instead of block: Vanguard (free) and Battle Plan. Round 2 opened at 5 energy with the front slime already Vulnerable and Weak and 6 HP lighter from the relic. I spent it on Slack Water into the Vulnerable target (9 damage off one card), two more Plans, and 10 block against 11 incoming.

2. I seriously considered the Fire Potion on Twig Slime (M) on round 2 — 20 damage, 30 into Vulnerable, an instant kill on a 16 HP body — and taking only the Leaf Slime's 3. I turned it down because I am at 55/80 on floor 3 and I would rather hold a 20-damage button for an elite or the boss than spend it saving myself six HP against slimes. What that gave up was tempo: killing the medium slime a turn early would have ended the fight on round 2.

3. Yes. The whole round-1 line existed because exactly one of the three had an attack intent; if all three had been aggressive I would have blocked and the fight becomes a grind under two status cards a turn. And if Kurage's Oath had not come back to hand on round 2 I would have had no way to hit both slimes at once.

4. Automatic: putting Battle Plan on the jellyfish, every single turn it appears. Net +1 energy and a card for a one-turn delay is never wrong once the fight is longer than two rounds, and I did it twice without thinking. Dead: nothing was truly dead, but the two Slimed status cards ("Draw 1 card. Exhaust.") sat in hand as 1-energy taxes I never had a spare energy for.

5. Only in the sense that round 2's 5-energy turn was bigger than I had planned for — I had written Battle Plan expecting to spend it on block and instead got to write two more Plans *and* block, which is the point of the card. The 5/3 energy display is the first time the deck felt like an engine rather than a hand of singles.

6. The intent number did not move when I reapplied Weak: Slack Water took Twig Slime (M) from "Weak 1" to "Weak 2" and its intent stayed "Aggressive, 8". I could not tell from the screen whether that was correct (already weakened, stacking duration not magnitude) or whether the second application did nothing.

## The run, in the tester's own words

1. She is a delayed-action character built around a second board slot. The Bake-Kurage is not a pet that attacks; it is a place to *store a card until next turn*, and the interesting cards are the ones that are strictly worse — or completely blank — if you play them yourself. Kurage's Oath, Battle Plan and Vanguard have no non-Plan text at all. Read the Field goes from 3 block to 8. So a turn is really two decisions: what do I do now, and what does tomorrow-me get. Layered on top is a Hydro/aura system and a relic that turns every debuff I apply into a free 2-damage Hydro ping, which quietly made debuff cards into damage cards — Vanguard, a 0-cost card that only writes "1 Vulnerable and 1 Weak", was worth 6 damage both times I used it because the Vulnerable landed before the pings resolved.

2. Now versus next turn, and it is a genuinely sharp tension because the cost is paid immediately either way. Every energy I put on the jellyfish is energy I do not have for block *this* turn, and I have to price it against an intent I can see. Twice I chose block over Battle Plan and once I chose Battle Plan over block, and all three felt like real reads rather than defaults. The second tension is smaller and less interesting: Shrink and similar attack-damage debuffs slide off the planned damage, because most Plan cards are skills, so a debuff aimed at my attacks pushes me toward the jellyfish rather than punishing me.

3. Battle Plan, easily — it is the card that turns a 3-energy turn into a 5-energy turn and makes multi-Plan turns possible, and I took a second copy as my only card reward. Vanguard, because 0 cost plus the relic makes it free damage plus a damage amplifier. And Water's Edge, which is just the honest attack the deck is built on. Coral Guard at 5 block for 1 was fine and never exciting.

4. Not yet — 40 actions and two fights is too short for repetition to set in, and the second fight played very differently from the first. The one thing I can already feel wearing thin is that Coral Guard is an undifferentiated block card I play whenever an intent is bigger than my damage, and that the Plan-only cards have exactly one legal target, so "play X on Bake-Kurage" is a keystroke rather than a choice.

5. I would avoid Shikanoin Heizou — Heartstopper Strike, which was offered as the relic's fourth Companion pick: "Deal 6 damage. Deals 4 more for each Swirl this turn", where Swirl requires Anemo, and nothing in Kokomi's starting deck or in either bundle applies anything but Hydro. Without an Anemo source it is a vanilla 6-damage attack in a deck that already has 6-damage attacks. I would also be careful about a third or fourth Coral Guard — block that does not interact with the jellyfish is the flattest thing in the deck — and about Moon's Reflection, whose text ("Choose a card in your exhaust pile: Plan: the jellyfish carries out its Plan line, or the card itself if it has none. Exhaust.") I could not confidently parse under time pressure.

## Defects and oddities

- **Tool/bridge failure ended the session.** Four consecutive calls returned `understudy.bridge.BridgeError: bridge connection failed at http://localhost:15526/api/v1/singleplayer: TimeoutError: timed out`, starting with the `act 'play "Water's Edge (proto) (1)" on "Leaf Slime (S)"'` that would have ended fight 2. The command before it had posted normally. Nothing on the game side looked wrong first.
- **Vanguard prints "Exhaust" twice**, once at the head of the line and once at the tail: `Exhaust. Plan: the front enemy gains 1 Vulnerable and 1 Weak. Exhaust.`
- **Plan-only cards never say what happens if you play them normally.** Kurage's Oath is `cost 1, skill / Plan: Deal 5 damage to every enemy.` and Battle Plan is `cost 1, skill / Plan: Gain 2 Energy and draw 1.` — and the grammar line offers `play "<card title>" [on "<enemy>"]` for them just like any other card. If the normal play is a null that burns the energy, the card should say so; I never risked finding out, which means the screen made a legal-looking action untestable.
- **An enemy's aura is tagged as that enemy's buff.** `Hydro Aura 2 (buff) — Hydro clings to this enemy for 2 more turns.` appears in the same block as `Vulnerable 1 (debuff)` and `Weak 1 (debuff)`. The aura I put on them to set up a Reaction reads as something helping them.
- **The relic's arithmetic does not match a plain read of its text.** `Tamakushi Casket — ... Whenever you apply a debuff to an enemy, it strikes that enemy for 2 Hydro damage.` Vanguard's plan applies two debuffs (1 Vulnerable, 1 Weak), so the printed text reads as 4 damage. Observed both times it fired: **6** (Shrinker Beetle 7 → 1; Twig Slime (M) 22 → 16). It is self-consistent if the Vulnerable is applied before *both* pings resolve and amplifies each 2 into 3, but nothing on screen states the ordering, and a player pricing the card off its text will be wrong by 50%.
- **Damage numbers on my own cards were silently rewritten by a debuff with no marker.** Under `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage`, Water's Edge printed `Deal 6 damage` on round 1 and `Deal 4 damage` on round 2; Deep Current printed `Deal 4 damage to every enemy` then `Deal 2 damage to every enemy`; Slack Water printed `Deal 2 damage` in fight 1 and `Deal 4 damage` in fight 2. Nothing distinguishes a printed base number from a printed modified number.
- **Reapplying Weak did not move the intent.** Slack Water took Twig Slime (M) from `Weak 1` to `Weak 2` and the intent stayed `Aggressive, 8, This enemy intends to Attack for 8 damage`. Correct or not, the screen gives the player no way to tell whether the second stack bought anything.
- **Bundle selection gives no feedback.** On the `# Choose a bundle.` screen, `choose "Deep Current"` answered `ok Selecting bundle 0`, but re-observing printed the identical page with no mark on either bundle. I had to send `confirm` on faith that the right one was armed.
- **A reward screen with nothing to choose still advertises a chooser.** After taking both fight-1 rewards the page printed `# What the fight left behind` / `- (nothing here to take)` and still listed `choose "<reward>"` under "What you can say".
- **The map is unplannable.** It prints only the immediately adjacent nodes as bare labels (`Monster (path 1)`, `Unknown (path 1)`) with no floors ahead and no elite/shop/campfire distinction, so route choice is a coin flip. The `Unknown (path 1)` I took turned out to be a `# Wellspring` event.
- **The Companion card offered by the relic is unusable by this character's deck.** `Shikanoin Heizou — Heartstopper Strike — cost 1, attack / Deal 6 damage. Deals 4 more for each Swirl this turn.` with the tooltip `*Swirl* — Anemo meets an existing aura...`. Nothing in the Kokomi starting deck, either Scroll Boxes bundle, or any card I saw applies Anemo, and there is no tooltip for Anemo itself — only for Swirl. As offered it is a 6-damage vanilla attack with a rider that cannot fire.
- **The duplicate-name footnote is inaccurate and fires when it isn't needed.** `*Two cards here print the same name. The game's data feed does not report a card's enchantment, so if one of them is enchanted, this page cannot show which.*` printed on a hand holding three Coral Guards already disambiguated as `(1) (2) (3)`, on a hand with two *separate* duplicate pairs (two Water's Edge and two Coral Guards), and on a hand with three Water's Edge and two Slimed. It says "Two cards" regardless.
- **The numbered suffixes renumber inside a turn**, so playing two different Coral Guards meant sending `play "Coral Guard (proto) (1)"` twice in a row, and the second `Water's Edge (proto) (1)` in a hand is `(1)` again as soon as the first is gone. It works, but it invites misfires and makes a queued plan unsafe to write in advance.
- **Unexplained starting HP.** The first combat screen of the run printed `HP 64/80` before I had taken any damage; the Neow option I took (`Scroll Boxes — Choose 1 of 2 packs of cards to add to your Deck.`) prints no HP cost, and the option that does (`Leafy Poultice ... Lose 12 Max HP`) was not taken. If 64/80 is the intended start, nothing on any screen says so.

## Transcript

1. Neow → `choose "Scroll Boxes"`
2. bundle select → `choose "Deep Current"`
3. bundle select → `confirm`
4. Neow → `proceed`
5. map → `go "Monster (path 1)"`
6. battle r1 → `play "Kurage's Oath (proto)" on "Bake-Kurage"`
7. battle r1 → `play "Water's Edge (proto) (1)" on "Shrinker Beetle"`
8. battle r1 → `play "Water's Edge (proto)" on "Shrinker Beetle"`
9. battle r1 → `end turn`
10. battle r2 → `play "Slack Water (proto)" on "Shrinker Beetle"`
11. battle r2 → `play "Water's Edge (proto)" on "Shrinker Beetle"`
12. battle r2 → `play "Coral Guard (proto) (1)"`
13. battle r2 → `end turn`
14. battle r3 → `play "Vanguard" on "Bake-Kurage"`
15. battle r3 → `play "Water's Edge (proto) (1)" on "Shrinker Beetle"`
16. battle r3 → `play "Water's Edge (proto)" on "Shrinker Beetle"`
17. battle r3 → `play "Coral Guard (proto)"`
18. battle r3 → `end turn`
19. battle r4 → `play "Water's Edge (proto) (1)" on "Shrinker Beetle"` (kill)
20. rewards → `choose "Gold"`
21. rewards → `choose "Card"`
22. card reward → `choose "Battle Plan"`
23. rewards → `proceed`
24. map → `go "Unknown (path 1)"`
25. Wellspring → `choose "Bottle"`
26. rewards → `choose "Fire Potion"`
27. event → `proceed`
28. map → `go "Monster (path 2)"`
29. battle r1 → `play "Deep Current"`
30. battle r1 → `play "Water's Edge (proto)" on "Twig Slime (S)"` (kill)
31. battle r1 → `play "Vanguard" on "Bake-Kurage"`
32. battle r1 → `play "Battle Plan" on "Bake-Kurage"`
33. battle r1 → `end turn`
34. battle r2 → `play "Slack Water (proto)" on "Twig Slime (M)"`
35. battle r2 → `play "Kurage's Oath (proto)" on "Bake-Kurage"`
36. battle r2 → `play "Battle Plan" on "Bake-Kurage"`
37. battle r2 → `play "Coral Guard (proto) (1)"`
38. battle r2 → `play "Coral Guard (proto) (1)"`
39. battle r2 → `end turn`
40. battle r3 → `play "Water's Edge (proto) (1)" on "Twig Slime (M)"`
41. battle r3 → `play "Water's Edge (proto) (1)" on "Leaf Slime (S)"` — NOT POSTED, bridge timeout; three `observe` retries also timed out, session ended
