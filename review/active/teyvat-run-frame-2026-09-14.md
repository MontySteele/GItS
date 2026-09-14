Status: OPEN (picks: the act-2 and act-3 nation pairs, posed when §3's mapping reports; nothing is open today)

# The Teyvat run frame: two nations per act, and the layer that can be built beside the kits

Written 2026-09-14 from [USER]'s answers of the same day, ruled R272; §7 and
the corrections in §2-§6 added the same day after a second read. This is the
kickoff for the Teyvat stream in its own worktree (`../GItS-teyvat`, branch
`teyvat`); it starts from this page and the four galleries, not from the
repo.

## 1. What [USER] ruled (R272, the words in the commit)

1. **The freeze is lifted for the non-mechanical layer.** R213 A's "enemy
   production waits" no longer binds events, printed text, names, still
   portraits, act theming and the nation frame. Enemy intents and numbers,
   boss behaviour, relic and potion mechanics stay frozen until a kit
   passes its done gate; the measurement windows Win10 and Win11 stay
   frozen as R213 left them.
2. **Two nations per act,** in the shape the base game already has: act 1
   rolls Overgrowth or Underdocks, so a Teyvat act 1 rolls **Mondstadt or
   Liyue**. Acts 2 and 3 take two nations each, chosen by the mapping
   exercise in §3, not by canon order.
3. **First deliverable is this frame plus the mapping, then a spike.**
4. **Music: official tracks as locally packaged placeholders,** handled
   exactly as art is (gitignored raw directory, a manifest, packaged into
   the pck on the main checkout, never committed). A copyright pass is
   owed before anything is public; [USER]: "right now this is just a mod
   I'm building to play with my friends where I put the code on github
   but package the art assets myself."
5. **Enemy visuals scale the character animation pipeline.** The Furina
   rebuild proved the route; each body is a matter of scaling up and
   testing the model.

## 2. What the engine gives us, checked 2026-09-14

- **Zones.** Act 1 is Overgrowth or Underdocks (16 and 14 events);
  act 2 is the Hive (21 events); act 3 is Glory (14); four events appear in
  every act (`research/sts2-map-and-events-research.md`,
  `research/act2-act3-roster-research.md`). The base game ships ONE zone
  each for acts 2 and 3, so a second nation there is a mod-side variant:
  the same zone's encounter table dressed two ways, rolled at act start.
  Whether a zone can be dressed two ways from one mod is the spike's
  first question, and everything in §3.2 rests on its answer.
- **Underdocks is a gap the repo has not filled.** The run sim models
  Overgrowth only (`tier05/content/events.yaml` §Underdocks: "the Act 1
  ALTERNATE we do not model"); the event gallery excluded the ten
  Underdocks-only events on the same ground; and the reskin gallery's
  Underdocks rows are RESEARCH status, thinner than Overgrowth's. Nothing
  on this layer is measured (R272), so the sim gap does not block, but the
  nation that takes Underdocks owes about ten more event conversions and a
  thinner enemy table. Cost it in §3.1.
- **Events are C# classes** added the way cards are. The model lives under
  `MegaCrit.Sts2.Core.Models.Events` (`FakeMerchant`, `DenseVegetation`
  are the ones the repo has already named) and an event with its own
  screen carries a second class under `Core.Nodes.Events.Custom` (the
  Crystal Sphere is the base example). One event is one model class; a
  bespoke layout is two. The 47 converted texts in
  `dossiers/content/event-conversion-gallery.md` are ready to become them.
- **Text is a localisation layer** (`Localization.LocString`), so enemy
  names, intents' words, relic and potion names are strings the mod
  overrides without touching behaviour.
- **Enemy visuals are Spine rigs** (`Bindings.MegaSpine`); a still portrait
  is the pck scene route. The mod already walks that route out of combat
  (`klee-mod/KleeCode/Vfx/StaticPortraitIdle.cs`: the rest site and the
  shop gate their idles on a `SpineSprite` our characters lack). An enemy
  without a rig will hit the combat-side gates of the same kind, and the
  spike reports which. Cost a body as text-only, portrait, or rig.
- **Music is FMOD** (`Core.Audio`). The default route is a Godot
  `AudioStreamPlayer` in the pck driven from a Harmony patch on the act and
  combat music calls, with the FMOD music bus ducked; an FMOD bank needs
  the studio tooling and the game's bank layout for the same prize, so it
  is the fallback if the duck cannot hold. The spike proves the duck across
  a combat start, a rest site, the map screen and a boss intro.

## 3. The mapping exercise (Sonnet or Opus research, Fable curation)

For each base zone, the deliverable is one table: every encounter slot
(easy pool, hard pool, elites, the boss slots), every event, and the
Ancient, against each candidate nation, scored on the mechanics the slot
already has. The reskin gallery and the boss candidates did this once
without a nation constraint; this pass re-cuts them with one. §7.1 says
what a nation constraint scores and what it does not.

1. **Act 1.** Overgrowth and Underdocks each take one of Mondstadt and
   Liyue. The proposed default is Overgrowth as Mondstadt and Underdocks
   as Liyue (§7.2); the table's job is to confirm or overturn it in one
   pass, not to spend research budget on it. Score both assignments; the
   table says which zone's mechanics (Overgrowth's Nibbit, Slimes, Fogmog,
   Byrdonis, Vantom; Underdocks' Sewer Clam, Phantasmal Gardeners) read
   more naturally as which nation's families (hilichurls, slimes, Abyss
   Mages, Ruin Guards; Treasure Hoarders, Geovishaps, Millelith, Fatui).
2. **Acts 2 and 3.** Candidates: Inazuma, Sumeru, Fontaine, Natlan,
   Snezhnaya, the Abyss. Each act's zone (Hive; Glory) is scored against
   every candidate on its encounter and event mechanics, and **every
   candidate is ranked, not just the top two:** the top one is the
   single-nation fallback if §4.1 reports that a zone cannot be dressed
   two ways, and the top two are the proposed pair if it can. The losing
   candidates' best slots are noted so nothing good is lost. The roster's
   homes (Inazuma, Fontaine) are a tie-break, not a rule.
3. **Bosses.** Behaviour is frozen, so a boss slot takes the candidate
   whose canon body fits the existing pattern. The sources are the boss
   rows of `dossiers/remap/reskin-gallery.md` and the act-boss pool
   gallery `dossiers/bosses/candidates.md`, both of which fit a Genshin
   body onto a frozen StS2 behaviour. (`dossiers/bosses/pattern-memo.md`
   runs the other way, Genshin patterns into StS vocabulary, and is not
   the source for this.)
4. **Output.** `review/active/teyvat-nation-mapping-<date>.md`: the tables,
   a proposed pair per act with the reason in one line each, and the
   acts 2 and 3 picks as a numbered list with defaults. That packet is
   [USER]'s; this one closes into it.

## 4. The spike (Opus, one week, throwaway flag)

Behind `-p:TeyvatFrame=true`, on a dev build, prove four things and report
each as works / works with a cost / does not work. **Item 1 is the
load-bearing one and runs first:** it decides whether acts 2 and 3 get a
pair or a single nation, and §3.2 is shaped so its output survives either
answer. Its first half is a decompile read, no build needed.

1. One zone dressed two ways, chosen at act start by a coin the mod flips:
   the same encounter table, two sets of names, intent words, portraits
   and event pool. First from the decompile (where a zone's identity is
   held, what reads it, whether a Harmony patch can fork it), then on a
   build.
2. One event from the gallery registered and reachable on the act-1 map.
3. One enemy renamed with its intents' words changed and a still portrait
   in place of its rig, in one zone only. Report every `SpineSprite`-gated
   door the body hits, since that list is the cost line for every later
   body.
4. One act's music replaced by a packaged track, with the original ducked,
   surviving a combat start, a rest site, the map screen and a boss intro.

Nothing measured on the spike is quotable; it is a feasibility read. Its
report lands in `review/records/`.

## 5. Rules this stream runs under

- **Design is Fable's.** Research and execution are Opus and Sonnet. Art
  picks ship at shortlist rank 1 (R212). Text conversions are
  hygiene-grade.
- **It never takes the seats, the lanes or the GPU while a Klee
  calibration round or [USER]'s run is up** (`no-seats-during-steam-play`).
- **It never moves the calibration seed.** The Klee fun calibration
  (`review/records/klee-fun-calibration-2026-09-14.md`) rides the next
  three builds on one fixed seed, and an event registered into the act-1
  pool changes that seed's map and event rolls. `TeyvatFrame` is one more
  arm on the same `+proto` build, OFF on every calibration deploy; the
  spike's event, dressing and music exist only when the arm is on.
- **It returns to [USER] twice:** the nation pairs for acts 2 and 3 (§3.4),
  and a contact sheet when a body lands. Everything else is disclosed in
  its packets.
- **Mechanics stay frozen.** A finding that a slot cannot be dressed
  without changing behaviour is recorded as such and parked, never fixed
  by moving a number.
- **Music and art sources are [USER]'s to supply** into the gitignored
  raw directories; the pipeline packages what it finds and commits
  nothing.

## 6. Order of work

1. Read this page, `CLAUDE.md`, `STATE.md`, then the four galleries and
   the two research pages named in §2, and nothing else.
2. Start §4.1's decompile read (Opus) at once; the rest of §4 follows on
   its own worktree.
3. Run §3 as one Sonnet fan-out per act, with §3.1 confirming its default
   and §3.2 ranking every candidate; curate; post the mapping packet once
   §4.1's read is in.
4. Write the music and portrait raw-directory conventions into
   `docs/current/operations/` beside the art pipeline's, before any file
   is placed. Each track's manifest row records its source from day one,
   the way `art/SOURCES.tsv` does, so the copyright pass is a lookup.

## 7. Design views carried into the stream (Fable, 2026-09-14)

1. **Nation is carried by events, the Ancient, the boss and the theming,
   not by the common enemies.** Most Genshin families are pan-national:
   hilichurls, slimes, Abyss Mages, Ruin machines, Treasure Hoarders,
   Fatui. Scored against every slot, all six nations tie on the swarm
   rows and the table says nothing. The mapping scores only
   nation-exclusive families (Geovishaps and Millelith for Liyue;
   Rifthounds, Kairagi and Nobushi for Inazuma; Eremites and Fungi for
   Sumeru; Meks and the Fontemer for Fontaine; Saurians for Natlan;
   Oprichniki for Snezhnaya; the Abyss's own), plus the events, the Ancient
   and the boss. A pan-national family takes the nation's palette wherever
   it lands and is not a tie-break.
2. **Act 1 barely needs the exercise.** Forest, slimes and birds read
   Mondstadt; docks, clams and gardeners read Liyue harbour, and the reskin
   gallery already carries Primo Geovishap as the top body for the
   Underdocks boss. The default stands unless the table finds a slot that
   fights it.
3. **Music defaults to the Godot player with the FMOD bus ducked** (§2).
   The raw directory carries provenance per track from the first file.
