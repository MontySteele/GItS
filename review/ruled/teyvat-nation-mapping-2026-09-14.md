Status: RULED R273 2026-09-14

# Which nations dress acts 2 and 3

Written 2026-09-14 under R272 pick 2; amended the same evening after
[USER]'s read (the Abyss reserved, the default flipped, Nod-Krai and
Snezhnaya carried as later faces). The three tables behind this page are
`teyvat-nation-mapping-act1-2026-09-14.md`, `-act2-` and `-act3-` (Sonnet,
one per act, scored by the rule in the kickoff packet §7.1); the feasibility
read is `review/records/teyvat-spike-zone-read-2026-09-14.md` (Opus, off
the installed 0.111.0 decompile). This page is the curation and ends in two
picks.

## 1. The precondition holds, and it generalises

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
back.

Two things follow. **A third face on an act costs the same as the second:**
the patches are written once, and a face is content only (a mapping
against that zone's table, portraits, an event pool). So a nation left out
today is not locked out; it is a later face. **Sibling faces must carry
the same number of events,** because events are shuffled once at run start
off one random stream, and a pool of a different size moves every later
roll, bosses and Ancients included.

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
| "Snezhnaya" (see §3) | 2 | top | 0 | 0 | 3 | 1, under protest | 0 | 0 |

The tables' own rankings were Sumeru, Inazuma, Fontaine for the Hive and
Fontaine, Sumeru, Inazuma for Glory.

## 3. How to read them

**The event column is not a fit signal.** The event gallery was drafted in
August with exactly three faction voices, Melusines for Fontaine, the
Sangonomiya resistance for Inazuma and the Akademiya and Aranara for
Sumeru, so those three nations "own" every event and the other three own
none. That measures what was written, not what fits. Under R272 an event
text is hygiene-grade work, so drafting cost is a cost line, not a score,
and every layout in §4 costs about the same on it: between 35 and 42 new
event variants across both acts, plus about a dozen Mondstadt variants and
the ten unconverted Underdocks events for act 1.

**The "Snezhnaya" column is mislabelled.** Every body it scored is a
Nod-Krai Fatui body (the Oprichniki ranks, the Operatives), because the
August atlas covers Nod-Krai only through its Fatui and covers Snezhnaya
proper not at all: Snezhnaya released in Genshin 7.0 last month, after the
atlas was cut. Neither region has a family pass, so neither is scored here;
both are carried in §5 as later faces.

Read on enemies, bosses, Ancients and the zone's own character instead,
the picture changes. The Hive is an organic zone (bowlbugs, exoskeletons,
chompers, the Entomancer, the Decimillipede), and its two richest exclusive
rosters are Natlan's Saurians and Sumeru's Fungi and Eremites. Glory is a
machine-and-knight zone (Axebot, Guardbot, the Cubex gang, the Fabricator,
the Frog, Flail and Mecha Knights), and its exclusive rosters are
Fontaine's Meks, which alone clear the Axebot slot, and Sumeru's ritual
casters and devotees, which clear nine of the twelve slots.

**The Abyss is reserved for a fourth act.** Its canon role is the bottom
of the descent, which is what an act 4 or an ending is; StS1 shipped one
and StS2 is early access with three. Spending it as a face of Glory is only
half reversible (the Glory readings would not travel, and act 3 would need
a replacement face built from nothing), and reserving it costs nothing,
since Fontaine and Sumeru each hold two Glory boss readings. Its strongest
reading, Aeonglass as the Abyss Lector, Fathomless Flames, stays recorded
in the act-3 table. Whether the mod can add an act 4 itself, or waits for
MegaCrit to ship one, is a scoping read (`BACKLOG.md`, the act-4 row); the
spike already found one hard wall, the rest site throwing on any act index
past the third.

Sumeru is the strongest nation in both zones and can take only one.
Inazuma is a solid second-tier fit in both and Kokomi's home, which the
kickoff packet makes a tie-break and not a rule.

## 4. The layouts

Exclusive enemy slots covered, Hive plus Glory, and what each leaves out:

1. **Natlan + Inazuma, then Fontaine + Sumeru.** 6+4 and 9+5 = 24. The
   highest count, Sumeru where its roster is widest, both roster homes in
   the run. An organic act of beasts and hounds, then a machine act with
   Fontaine's Meks and Sumeru's ritual rows.
2. **Sumeru + Natlan, then Fontaine + Inazuma.** 5+6 and 5+6 = 22. Sumeru's
   jungle on the Hive; Inazuma's Kairagi and knights on Glory.
3. **Sumeru + Inazuma, then Fontaine + Natlan.** 5+4 and 5+2 = 16. The Hive
   table's own pair; Natlan's two Glory slots are thin.

The losers' best slots are recorded in each act table's §5 so nothing is
lost: Natlan's Iktomisaurus for the Ovicopter and Chanca of the Weary Inn
for the Tezcatara Ancient where Natlan is not on the Hive, Inazuma's Knight
Gang and Mecha Knight readings where Inazuma is not on Glory.

## 5. Carried, not decided

- **Nod-Krai and Snezhnaya are later faces,** atlased and scored as
  native columns (act-2 table §7, act-3 table §7, 2026-09-15): both carry
  nation in the enemy column only, so neither outranks a ruled pair. The
  default carried into any third-face pick is Nod-Krai on Glory (strong on
  both bosses) and Snezhnaya on the Hive (nine enemy slots, the only
  Reattach candidate). A third face is content only (§1) and asks no new
  engineering.
- **The Abyss** is the act-4 face (§3).
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

1. **CHOOSE the act-2 pair.** (1, default) Natlan + Inazuma; (2) Sumeru +
   Natlan; (3) Sumeru + Inazuma.
2. **CHOOSE the act-3 pair.** (1, default) Fontaine + Sumeru, which needs
   pick 1 at (1); (2) Fontaine + Inazuma, with pick 1 at (2); (3)
   Fontaine + Natlan, with pick 1 at (3).

Layout 1 in §4 is both defaults. Whatever is ruled, the spike's build half
proceeds on act 1 with Mondstadt and Liyue, which no pick touches.
