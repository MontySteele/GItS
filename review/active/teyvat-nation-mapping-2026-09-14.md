Status: OPEN (picks 1 and 2: the act-2 and act-3 nation pairs; the kickoff packet `teyvat-run-frame-2026-09-14.md` closes into this one when they are ruled)

# Which nations dress acts 2 and 3

Written 2026-09-14 under R272 pick 2. The three tables behind this page are
`teyvat-nation-mapping-act1-2026-09-14.md`, `-act2-` and `-act3-` (Sonnet,
one per act, scored by the rule in the kickoff packet §7.1); the feasibility
read is `review/records/teyvat-spike-zone-read-2026-09-14.md` (Opus, off
the installed 0.111.0 decompile). This page is the curation and ends in two
picks.

## 1. The precondition holds

A zone can be dressed two ways from the mod. The spike's decompile read
found that an act is one model object, rolled at run start by the game's
own `ActModel.GetRandomList` and saved by id, and that the background, the
rest site, the map images and colours, the title, the music, the event pool
and the Ancient pool all derive from that one object. A second dressing is
a sibling act at the same index that returns the very same encounter
objects, so mechanics cannot drift and the coin, its co-op sync and its
save/load are the game's, not ours. The cost is three Harmony patches (the
hardcoded act list, monster names, monster visuals) and a complete asset
set per dressing, because the background loader throws rather than falls
back. So acts 2 and 3 each take a pair, and the single-nation fallbacks in
§4 are recorded only in case the build half of the spike overturns the
read.

One constraint falls out of it for everything below: **sibling dressings
must carry the same number of events.** Events are shuffled once at run
start off one random stream, so a pool of a different size moves every
later roll in the run, bosses and Ancients included.

## 2. What the tables found

**Act 1 is settled.** Overgrowth as Mondstadt and Underdocks as Liyue
scores 4 and 1 on nation-exclusive fits (Vantom as Andrius, Ceremonial
Beast as Golden Wolflord, two Knights-of-Favonius events; Lagavulin as Primo
Geovishap, who is an Underdocks boss by origin). The reverse scores 0 and
0. No slot fights it.

**Acts 2 and 3, as the tables ranked them:**

| | Hive: enemies (of 12) | boss | Ancient | events drafted | Glory: enemies (of 12) | boss | Ancient | events drafted |
|---|---|---|---|---|---|---|---|---|
| Sumeru | 5 | top | 3 | 8 top, 7 alt | 9 | 2 | 3 | 9 |
| Inazuma | 4 | alt | 1 | 6 top, 12 alt | 6 | 0 | 1 | 10 |
| Fontaine | 2 | 0 | 0 | 2 top, 13 alt | 5 | 2 | 1 | 16 |
| Natlan | 6 | 0 | 1 top | 0 | 2 | 1 | 0 | 0 |
| The Abyss | 4 | 2 alt | 0 | 0 | 7 | 1, the strongest | 0 | 0 |
| Snezhnaya | 2 | top | 0 | 0 | 3 | 1, under protest | 0 | 0 |

The tables' own rankings were Sumeru, Inazuma, Fontaine for the Hive and
Fontaine, Sumeru, Inazuma for Glory.

## 3. How to read them

The event column is not a fit signal. The event gallery was drafted in
August with exactly three faction voices, Melusines for Fontaine, the
Sangonomiya resistance for Inazuma and the Akademiya and Aranara for
Sumeru, so those three nations "own" every event and the other three own
none. That measures what was written, not what fits. Under R272 an event
text is hygiene-grade work, so drafting cost is a cost line, not a score,
and every layout in §4 costs about the same on it: between 35 and 42 new
event variants across both acts, plus about a dozen Mondstadt variants and
the ten unconverted Underdocks events for act 1.

Read on enemies, bosses, Ancients and the zone's own character instead,
the picture changes. The Hive is an organic zone (bowlbugs, exoskeletons,
chompers, the Entomancer, the Decimillipede), and its two richest exclusive
rosters are Natlan's Saurians and Sumeru's Fungi and Eremites. Glory is a
machine-and-knight zone (Axebot, Guardbot, the Cubex gang, the Fabricator,
the Frog, Flail and Mecha Knights), and its exclusive rosters are
Fontaine's Meks, which alone clear the Axebot slot, and the Abyss's Black
Serpent Knights, Heralds and Lectors, which also hold the strongest single
boss reading in either gallery (Aeonglass as the Abyss Lector, Fathomless
Flames). The Abyss as the final act's second face also serves the frame
[USER] named, a run that feels like a Spiral Abyss clear.

Sumeru is the strongest nation in both zones and can take only one.
Snezhnaya is thin in both: the Fatui rank and file are pan-national, and
its one great boss reading, La Signora, is under its own gallery's protest
for turning her sequential fight into a simultaneous one. Inazuma is a
solid second-tier fit in both zones and Kokomi's home, which the kickoff
packet makes a tie-break and not a rule.

## 4. The layouts

Exclusive enemy slots covered, Hive plus Glory, and what each leaves out:

1. **Sumeru + Natlan, then Fontaine + the Abyss.** 5+6 and 5+7 = 23. An
   organic act, then a machine-and-knight act that ends in the Abyss.
   Leaves out Inazuma and Snezhnaya. Fallbacks: Sumeru, Fontaine.
2. **Sumeru + Inazuma, then Fontaine + the Abyss.** 5+4 and 5+7 = 21. The
   Hive table's own pair, both roster homes in the run. Leaves out Natlan,
   whose six Hive slots are the richest exclusive roster of any nation in
   either zone, and Snezhnaya.
3. **Natlan + Inazuma, then Sumeru + Fontaine.** 6+4 and 9+5 = 24. The
   highest count, with Sumeru where its roster is widest. Leaves out the
   Abyss, and with it the Aeonglass reading and the Spiral Abyss finale,
   and Snezhnaya.

The losers' best slots are recorded in each act table's §5 so nothing is
lost: Inazuma's Knight Gang and Mecha Knight readings, Natlan's Iktomisaurus
for the Ovicopter and Chanca of the Weary Inn for the Tezcatara Ancient,
Snezhnaya's Frost Operative and Oprichniki squad.

## 5. Parked, not proposed

- Tanx, the act-3 Ancient, has no candidate in any of the six nations, and
  Queen, Glory's third boss, has no candidate in any family and ships
  dropped already.
- The Obscura with Parafright and the Decimillipede have no
  nation-exclusive body; they take the act's palette.
- Knowledge Demon as Shouki no Kami collides with a playable character
  (the Wanderer); the boss gallery calls it a curation call, not a
  mechanics one.
- Every reading that leans on an unimplemented status (Plating, Galvanic,
  Artifact 3, Reattach) is a pre-existing sim gap, not something this
  pick changes.

## 6. Picks

1. **CHOOSE the act-2 pair.** (1, default) Sumeru + Natlan; (2) Sumeru +
   Inazuma; (3) Natlan + Inazuma, which sends Sumeru to act 3.
2. **CHOOSE the act-3 pair.** (1, default) Fontaine + the Abyss; (2)
   Fontaine + Sumeru, only with pick 1 at (3); (3) Fontaine + Inazuma.

Layout 1 in §4 is picks 1(1) and 2(1). Whatever is ruled, the spike's build
half proceeds on act 1 with Mondstadt and Liyue, which no pick touches.
