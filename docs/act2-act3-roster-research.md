# Act 2 / Act 3 roster research (STS2 wiki harvest)

**Status:** RESEARCH NOTES — 2026-07-23. Raw source data for the multi-act
extension (`run-model-rework-plan.md` §10). Nothing here is a modeling
decision; the curated codeable subsets live in the plan doc.

Source: slaythespire.wiki.gg (`Slay_the_Spire_2:` namespace) — per-enemy pages
plus the per-zone Lua data modules (Hive, Glory, Underdocks). Numbers are
Ascension 0, early-access build current as of 2026-07-23. Damage format
`NxM` = N damage, M hits. HP ranges are spawn-time rolls.

**Structural facts (load-bearing):**

- STS2 has 3 acts. **Act 1 randomly picks one of two zones (Overgrowth or
  Underdocks). Act 2 = the Hive. Act 3 = Glory.** Some aggregator sites
  mislabel Underdocks as "Act 2" — it is an Act 1 alternate. Our shipped
  `act1_pool.yaml` is Overgrowth-based (+ Phantasmal Gardener, an Underdocks
  elite, imported for AoE coverage — plan §4.3).
- Easy/hard pool rule: Act 1 first **3** monster fights from the easy pool;
  Acts 2–3 first **2**; everything after from the hard pool. No encounter
  repeats within an act.
- Floor layout: Act 1 = floors 1–17 (mid-act all-Treasure floor, Rest before
  boss, boss floor 16, boss chest 17). Act 2 = 18–34 (boss floor 33). Act 3
  boss at floor 48. A Rest always precedes the boss; Treasure sits mid-act.
- **Act transition:** boss drops 100 gold + a choice of 3 **Rare** cards
  (sometimes a potion). The next floor is an **Ancient** floor: the Ancient
  heals **100% of missing HP** (80% on higher difficulty) and offers a choice
  of 3 boons/Ancient relics — this replaces STS1's post-boss boss-relic pick.
  Each act has its own Ancient pool; each act has 3 possible bosses.
- Scaling conventions (derived, for sim calibration):
  - Normals HP: Act 1 ~17–80 → Act 2 ~21–136 (solo normals 79–136) → Act 3
    ~31–266 (solo normals 148–266). Roughly ×1.6–1.8 HP per act for solos.
  - Normal hit sizes: Act 1 ~8–14/turn → Act 2 ~13–23 → Act 3 ~16–35.
    Roughly +40–60% per act.
  - Elite HP: Act 1 ~75–140 → Act 2 ~138–171 (plus a 3×46–52 splitter) →
    Act 3 ~234–300 (plus a 276-total gang). Elite burst: Act 2 ~18–31/turn →
    Act 3 ~29–35/turn.
  - Boss HP: Act 2 321–408 (Kaiser two-part total) → Act 3 400–600. Boss
    burst: Act 2 ~16–31/turn → Act 3 ~30–45/turn.
  - Act 2/3 signature design: heavy **status-card pollution** (Dazed / Burn /
    Wither / Slimed / Wounds / Toxic shuffled into the player's deck),
    stat-theft (The Lost / The Forgotten), self-scaling Strength ramps
    everywhere, and multi-part / multi-phase fights.

---

## 1. Act 2 — the Hive

### 1.1 Normals

| Enemy | HP | Moves / pattern | Notes |
|---|---|---|---|
| Bowlbug (Rock) | 45–48 | Headbutt 15; Dizzy (self-stun) | starts with 2 Imbalanced |
| Bowlbug (Egg) | 21–22 | Bite 7 + 7 Block | worker |
| Bowlbug (Silk) | 40–43 | Thrash 4x2; Spin Web (applies Weak) | worker |
| Bowlbug (Nectar) | 35–38 | Thrash 3; buff: +15 Strength (to Rock) | worker; kill first |
| Exoskeleton | 24–28 | Skitter 1x3; Mandibles 8; Enrage +2 Str | starts with 9 Hard to Kill |
| Chomper | 60–64 | Clamp 8x2; Screech (shuffle 3 Dazed) | starts with Artifact 2 |
| Thieving Hopper | 79 | Thievery 17 + steals a card; Hat Trick 21; Nab 14; Escape (flees) | Escape Artist 5 |
| Tunneler | 87 | Bite 13; Burrow (+32 Block, untargetable); Attack from Below 23; Emerging Strike (stun) | |
| Hunter Killer | 121 | Tenderizing Goop (applies Tender); Bite 17; Puncture 7x3 | |
| Louse Progenitor | 134–136 | Web Cannon 9 + 2 Frail; Curl and Grow +14 Block +5 Str; Pounce 14 | Curl Up 14 |
| Myte | 61–67 | Toxic Cornucopia (adds 2 Toxic status); Bite 13; Suck 4 + gains 2 Str | fight is 2 Mytes |
| Ovicopter | 124–130 | Lay Eggs (summon 3 Tough Eggs); Smash 16; Tenderizer 7 + 2 Vulnerable; Nutritional Paste +3 Str | |
| Tough Egg (minion) | 14–18 | Hatch → Hatchling (19–22 HP); Nibble 4 | |
| Slumbering Beetle | 86 | Snore (asleep 3 turns); Roll Out 16 + 2 Str | Plating 15 |
| Spiny Toad | 116–119 | Protruding Spikes +5 Thorns; Spike Explosion 23 (loses 5 Thorns); Tongue Lash 17 | |
| The Obscura | 123 | Illusion (summons Parafright); Piercing Gaze 10; Wail (all enemies +3 Str); Hardening Strike 6 + 6 Block | |
| Parafright (minion) | 21 | Slam 16 | Illusion status |

**Encounter pools** (first 2 fights easy):

- Easy: `Bowlbug(Rock)+1 worker` · `3x Exoskeleton` · `1x Thieving Hopper` ·
  `1x Tunneler`
- Hard: `Bowlbug(Rock)+2 workers (max 1/type)` · `2x Chomper` ·
  `4x Exoskeleton` · `1x Hunter Killer` · `1x Louse Progenitor` · `2x Myte` ·
  `1x Ovicopter (+Tough Eggs)` · `Bowlbug(Rock)+Bowlbug(Silk)+Slumbering
  Beetle` · `1x Spiny Toad` · `1x The Obscura (+Parafright)`

### 1.2 Elites

| Elite | HP | Pattern / moves | Gimmick |
|---|---|---|---|
| Decimillipede | 3 segments, 46–52 each | each segment cycles Bulk 7 + 2 Str → Writhe 6x2 → Outgas 9 + 1 Weak (offset starts) | dead segments Reattach after 2 turns at 25 HP if any segment lives |
| Entomancer | 145 (A8 155) | cycle: Beeeees! 3x7 → Spear! 18 → Pheromone Spit (+1 Personal Hive, +1 Str; +2 Str if Hive at 3) | Personal Hive X: every hit against it shuffles X Dazed into your draw pile |
| Infested Prism | 161 (A8 171) | cycle: Jab 15 → Radiate 11 + 16 Block → Whirlwind 5x3 → Pulsate 8 + 20 Block + Vital Spark 2 | Vital Spark X: all your Skills are Tainted X (take X extra attack damage this turn) |

### 1.3 Bosses (floor 33; 3 possible)

| Boss | HP | Pattern | Key numbers |
|---|---|---|---|
| **The Insatiable** | 321 (A8 341) | opens Liquify Ground, then cycle Thrash → Lunging Bite → Salivate → Thrash | Liquify Ground: 4 Sandpit + shuffles 6 Frantic Escape cards into your deck (an "in X turns you are eaten and die" timer). Thrash 8x2; Lunging Bite 28; Salivate +2 Str |
| **Knowledge Demon** | 379 (A8 399) | cycle: Curse of Knowledge → Slap → Knowledge Overwhelming → Ponder (Curse skipped after 3rd use) | Curse: pick-your-poison debuff (Disintegration 6/7/8 dmg per turn OR draw −1 / hand cap 3 / energy −1). Slap 17; Knowledge Overwhelming 8x3; Ponder 11 + heals self 30 + 2 Str |
| **Kaiser Crab** | 2 parts: Crusher 209, Rocket 199 | Crusher cycle: Thrash 12 → Enlarging Strike 4 → Bug Sting 6x2 + 2 Weak + 2 Frail → Adapt +2 Str → Guarded Strike 12 + 18 Block. Rocket cycle: Targeting Reticle 3 → Precision Beam 18 → Charge Up +2 Str → Laser 31 → Recharge | both: Back Attack (+50% damage from behind); Crab Rage: when the other claw dies, survivor gains 6 Str + 99 Block |

---

## 2. Act 3 — Glory

### 2.1 Normals

| Enemy | HP | Moves / pattern | Notes |
|---|---|---|---|
| Devoted Sculptor | 162 (A8 172) | Forbidden Incantation (+9 Ritual); Savage 12 | Cultist-style ramp |
| Scroll of Biting | 31–38 each | Chomp 14; More Teeth +2 Str; Chew 5x2 | starts with 2 Paper Cuts; fights of 3–4 |
| Living Shield | 55 | Shield Slam 6; Smash 16 + Str | starts with 25 Rampart |
| Turret Operator | 41 | Unload! 3x5; Loading +1 Str | paired with Living Shield |
| Axebot | 70–78 | Boot Up +10 Block +3 Str; The One-Two 9x2; Hammer Uppercut 12 + Weak/Frail | starts with 2 Stock |
| Punch Construct | 55 | READY +10 Block → Strong Punch 14 → Fast Punch 5x2 + 1 Weak (cycle) | Artifact 1; appears with 2 Cubex |
| Cubex Construct | 65 | Charge Up +2 Str → then Repeater Blast 7 + 2 Str, Repeater Blast, Expel Blast 5x2 (cycle) | Artifact 1; Str snowball |
| Fabricator | 150 (A8 155) | Fabricate (summon bots); Fabricating Strike 18 + summon; Disintegrate 11 | summons below |
| Zapbot / Stabbot / Noisebot (minions) | 18–23 | Zap 14 / Stab 11 + Frail / Noise (2 Dazed) | |
| Guardbot (minion) | 16–20 | Guard: Fabricator +15 Block | |
| Frog Knight | 191 (A8 199) | Tongue Lash 13 + Frail; Strike Down Evil 21; For the Queen +5 Str; Beetle Charge 35 | Plating 15 |
| Globe Head | 148 (A8 158) | Shocking Slap 13 + Frail; Thunder Strike 6x3; Galvanic Burst 16 + Str | Galvanic 6 |
| Owl Magistrate | 234 (A8 243) | Magistrate Scrutiny 16; Peck Assault 4x6; Judicial Flight (Soar); Verdict 33 + Vulnerable | biggest normal HP with Slimed Berserker |
| Slimed Berserker | 266 (A8 276) | Vomit Ichor (10 Slimed cards!); Furious Pummeling 4x4; Leeching Hug (Weak, +Str); Smother 30 | |
| The Lost | 93 | Debilitating Smog (steals your Strength); Eye Lasers 4x2 | Possess Strength |
| The Forgotten | 106 | Miasma (steals your Dexterity, gains Block/Dex); Dread 13 + Dex bonus | Possess Speed; paired with The Lost |

**Encounter pools** (first 2 fights easy):

- Easy: `1x Devoted Sculptor` · `3x Scroll of Biting` · `Living Shield +
  Turret Operator`
- Hard: `1x Axebot` · `Punch Construct + 2 Cubex Constructs` ·
  `1x Fabricator (+bots)` · `1x Frog Knight` · `1x Globe Head` ·
  `1x Owl Magistrate` · `4x Scroll of Biting` · `1x Slimed Berserker` ·
  `The Lost + The Forgotten`

### 2.2 Elites

| Elite | HP | Pattern / moves | Gimmick |
|---|---|---|---|
| Knight Gang (3 knights) | Flail 101 / Spectral 93 / Magi 82 | Flail: Ram 15, Flail 9x2, Breaker +3 Str. Spectral: Hex (2 Hex), Soul Slash 15, Soul Flame 3x3. Magi: Power Shield 6 + 5 Block, Dampen, Ram 10, Prep +5 Block, Magic Bomb 35 | Spectral alive: all your cards Ethereal. Magi alive: all your cards Downgraded |
| Mecha Knight | 300 (A8 320) | Charge 25 → then cycle Flamethrower (4 Burns into hand) → Windup +15 Block +5 Str → Heavy Cleave 35 | Artifact 3 |
| Soul Nexus | 234 (A8 254) | opens Soul Burn 29, then random no-repeat: Soul Burn 29 / Maelstrom 6x4 / Drain Life 18 + 2 Vuln + 2 Weak | pure damage check |

### 2.3 Bosses (floor 48; 3 possible)

| Boss | HP | Pattern | Key numbers |
|---|---|---|---|
| **Queen** (+ Torch Head Amalgam) | Queen 400 (A8 419); Amalgam 199 | Queen: Puppet Strings (3 Chains of Binding) → You're Mine (99 Frail + 99 Weak + 99 Vulnerable!) → repeats Burn Bright for Me (+1 Str to Amalgam, +20 Block self) while Amalgam lives; after it dies: Enrage +2 Str, then Off with Your Head 3x5 (7x5 with your Vuln) → Execution 15 (25 with Vuln) → Enrage | Amalgam fixed loop: Strong Tackle 26 → Tackle 18 → Beam 8x3 → Weak Tackle 14 → Weak Tackle → Beam |
| **Test Subject** | 3 phases: 100 → 200 → 300 | P1 (Enrage 2): alternates Bite 20 / Skull Bash 14 + 1 Vuln. P2 (Painful Stabs — unblocked damage shuffles Wounds into your discard): Multi-Claw 10x3, +1 hit per turn. P3 (gains 1 Intangible every other turn): Lacerate 10x3 → Big Pounce 45 → Burning Growl (3 Burns, +2 Str) | Adaptable: revives into next phase; 600 HP total |
| **Aeonglass** | 512 (A8 535) | cycle: Ebb 22 + 33 Block → Eye Lasers 11x2 → Increasing Intensity (shuffle Wither+X into your discard, +2+X Str, upgrades all Withers) | Withering Presence: every 6 cards you play adds a Wither to hand (Wither: end of turn in hand → take 3 (6 upgraded) damage). Artifact 3 |

---

## 3. Bonus: Underdocks (Act 1 alternate zone — NOT Act 2)

Harvested because fan sites mislabel it; useful as an Act-1 boss/variety
source, not for Acts 2/3.

Normals: Corpse Slug 25–27 (Whip Slap 3x2 / Glomp 8 / Goop 2 Frail;
Ravenous); Toadpole 21–25 (Thorns 2, Spike Spit 3x3); Two-Tailed Rat 17–21
(Scratch 8, summons up to 3 more rats); Sludge Spinner 37–39 (Slam 11, Oil
Spray 8 + 1 Weak); Calcified Cultist 38–41 (2 Ritual, Dark Strike 9) + Damp
Cultist 51–53 (5 Ritual, Dark Strike 1); Seapunk 44–46 (Sea Kick 11, Spinning
Kick 2x4); Gremlin Merc 47–49 (Gimme 7x2, Thievery 20, spawns Fat 13–17 /
Sneaky 10–14 gremlins on death); Fossil Stalker 51–53 (Latch 12, Suck 3:
+3 Str on unblocked hit); Punch Construct 55; Sewer Clam 56 (Plating 8,
Jet 10, Pressurize +4 Str); Haunted Ship 63 (Haunt: 5 Dazed + 3 Weak, Swipe
13, Stomp 4x3); Living Fog 80 (summons Gas Bombs 7 HP that Explode for 8).

Elites: Skulking Colony 75 (Hardened Shell 20 — max 20 HP lost/turn; Zoom 14,
Piercing Stabs 7x2); Phantasmal Gardener (4× 26–31 HP — already in our Act-1
elite pool); Terror Eel 140 (Crash 16, Thrash 3x3x3, at 70 HP stunned then
Terror: 99 Vulnerable).

Underdocks bosses (Act 1 pool) include Soul Fysh (Scream 13/15) — not fully
harvested.

---

---

## 4. Act 1 boss pools — full statlines (second harvest, 2026-07-23)

Both zones' 3-boss pools (6 total). Harvested for the §10.5 boss-pool
expansion; **Lagavulin Matriarch locked as boss #2** (user pick — note there
is NO literal crab in Act 1; Kaiser Crab is Act 2's).

### Overgrowth

| Boss | HP | Moves (A0) | Gimmick |
|---|---|---|---|
| Ceremonial Beast | 252 | P1 (until HP ≤ 150): Stamp, then Plow 18 + 2 Str every turn. P2 (3-cycle): Beast Cry (1 Ringing — play only 1 card next turn), Stomp 15, Crush 17 + 3 Str | Threshold: at ≤150 HP it stuns and loses ALL Strength — racing resets its ramp |
| The Kin | Priest 190 + 2 Followers 58–59 | Priest cycle: Orb of Frailty 8 + 1 Frail / Orb of Weakness 8 + 1 Weak / Soul Beam 3x3 / Dark Ritual +2 Str. Followers (offset): Quick Slash 5 / Boomerang 2x2 / Power Dance +2 Str | Minions flee when Priest dies; the multi-body AoE boss |
| Vantom | 173 | Ink Blot 7 / Inky Lance 6x2 / Dismember 27 + 3 Wounds into discard / Prepare +2 Str | Slippery 9 (next 9 HP-losses → 1); anti-big-hit |

### Underdocks

| Boss | HP | Moves (A0) | Gimmick |
|---|---|---|---|
| Waterfall Giant | 240 | Opens Pressurize (+15 Steam Eruption), then 5-cycle (+3 Steam Eruption each move): Stomp 15 + 1 Weak / Ram 10 / Siphon (self-heal 15/player) / Pressure Gun 20 **+5 per use** / Pressure Up 13 | Steam Eruption X: on death → invulnerable, then explodes for X — a growing death bomb; soft timer |
| Soul Fysh | 211 | 5-cycle: Beckon (2 Beckon statuses into piles) / De-Gas 16 / Gaze 7 + 1 Beckon / Fade (+2 Intangible) / Scream 11 + 3 Vuln | Beckon: 6 HP if in hand at end of turn; pollution + Intangible throttle |
| **Lagavulin Matriarch** ✅ | 222 | Asleep 3 turns with 12 Plating, then 4-cycle: Slash 19 / Disembowel 9x2 / Slash 12 + 12 Block / Soul Siphon: player loses 2 Str + 2 Dex PERMANENTLY, she gains 2 Str | The anti-turtle clock — long fights bleed your scaling dry. Modeled in `act1_pool.yaml` (her ramp half; player-drain + Plating on the §10.9 backlog) |

## 5. Ancients — the real boon pools (harvest, 2026-07-23)

Mechanic per wiki: each act BEGINS by meeting an Ancient offering a choice
of 3 boons (Act 1 = Neow, always; Act 2 pool: Orobas / Pael / Tezcatara
+ Darv; Act 3 pool: Nonupeipe / Tanx / Vakuu + Darv). CAVEAT: the
"heals 100% of missing HP" number comes from the Mobalytics guide; the wiki
proper confirms the choice-of-3 but not the heal fraction. Sim rule stays
full-heal (ratified §3.3/§10.1). Some numbers drift between mirror wikis
(EA patches).

Shipped sim sample (relics.yaml `ancient:`, §10.1 — 1:1 on existing hooks):
Sand Castle (Orobas, upgrade 6 random) · Yummy Cookie (Tezcatara, upgrade 4)
· Very Hot Cocoa (Tezcatara, +4 energy/combat start) · Pael's Blood (+1
draw/turn) · Looming Fruit (Nonupeipe, +31 max HP) · Signet Ring (Nonupeipe,
+999 gold) · Diamond Diadem (Nonupeipe, 20 start-block; 1-turn retention
skipped).

Notable NOT-shipped boons (need ops on the §10.9 backlog or UI choices):
Prismatic Gem / Blessed Antler / Philosopher's Stone (+1 energy **per turn**
riders), Alchemical Coffer & Delicate Frond (potion-fill), Sai (per-turn
block), Meat Cleaver (rest-site remove-for-maxhp), Seal of Gold
(gold→energy), Pumpkin Candle (5-combat counter), Empty Cage (removal —
no pickup_remove hook yet), plus all transform / card-content / enchant /
map-rewrite boons (New Leaf, Toy Box, Astrolabe-STS2, Snecko Eye, …).

Wiki sources: STS2 Bosses / Monsters / Elites / Acts / Map Locations pages and
the Hive / Glory / Underdocks enemy data modules on slaythespire.wiki.gg;
individual pages for each boss/elite/Ancient named above (Ceremonial Beast,
The Kin, Vantom, Waterfall Giant, Soul Fysh, Lagavulin Matriarch, Neow,
Orobas, Pael, Tezcatara, Nonupeipe, Tanx, Vakuu, Darv); roadmap coverage
(PCGamesN); Ancients guides (Mobalytics, sts2wiki.org, TheGamer). Roadmap
items still pending upstream: alternate Act 2/3 zones, 4th character,
bestiary, True Victory — the rosters above are shipped early-access content.
