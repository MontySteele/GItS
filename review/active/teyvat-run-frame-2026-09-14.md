Status: OPEN (picks: the act-2 and act-3 nation pairs, posed when §3's mapping reports; nothing is open today)

# The Teyvat run frame: two nations per act, and the layer that can be built beside the kits

Written 2026-09-14 from [USER]'s answers of the same day, ruled R272. This
is the kickoff for a second Fable session in its own worktree; it starts
from this page and the four galleries, not from the repo.

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
  Whether a zone can be dressed two ways from one mod is the spike's first
  question.
- **Events are C# classes** (`MegaCrit.Sts2.Core.Events.Custom.*`), added
  the way cards are. The 47 converted texts in
  `dossiers/content/event-conversion-gallery.md` are ready to become them.
- **Text is a localisation layer** (`Localization.LocString`), so enemy
  names, intents' words, relic and potion names are strings the mod
  overrides without touching behaviour.
- **Enemy visuals are Spine rigs** (`Bindings.MegaSpine`); a still portrait
  is the pck scene route. Cost a body as text-only, portrait, or rig.
- **Music is FMOD** (`Core.Audio`). A custom track is either an FMOD bank
  or a Godot `AudioStreamPlayer` in the pck driven from a Harmony patch on
  the act and combat music calls with the FMOD music bus ducked. The spike
  proves one or the other; nothing here assumes which.

## 3. The mapping exercise (Sonnet or Opus research, Fable curation)

For each base zone, the deliverable is one table: every encounter slot
(easy pool, hard pool, elites, the boss slots), every event, and the
Ancient, against each candidate nation, scored on the mechanics the slot
already has. The reskin gallery and the boss candidates did this once
without a nation constraint; this pass re-cuts them with one.

1. **Act 1.** Overgrowth and Underdocks each take one of Mondstadt and
   Liyue. Score both assignments; the table says which zone's mechanics
   (Overgrowth's Nibbit, Slimes, Fogmog, Byrdonis, Vantom; Underdocks'
   Sewer Clam, Phantasmal Gardeners) read more naturally as which nation's
   families (hilichurls, slimes, Abyss Mages, Ruin Guards; Treasure
   Hoarders, Geovishaps, Millelith, Fatui). A default is proposed, not
   picked.
2. **Acts 2 and 3.** Candidates: Inazuma, Sumeru, Fontaine, Natlan,
   Snezhnaya, the Abyss. Each act's zone (Hive; Glory) is scored against
   every candidate on its encounter and event mechanics; the top two per
   act become the proposed pair, with the losing candidates' best slots
   noted so nothing good is lost. The roster's homes (Inazuma, Fontaine)
   are a tie-break, not a rule.
3. **Bosses.** Behaviour is frozen, so a boss slot takes the candidate
   whose canon body fits the existing pattern
   (`dossiers/bosses/pattern-memo.md` lists which patterns translate).
4. **Output.** `review/active/teyvat-nation-mapping-<date>.md`: the tables,
   a proposed pair per act with the reason in one line each, and the
   acts 2 and 3 picks as a numbered list with defaults. That packet is
   [USER]'s; this one closes into it.

## 4. The spike (Opus, one week, throwaway flag)

Behind `-p:TeyvatFrame=true`, on a dev build, prove four things and report
each as works / works with a cost / does not work:

1. One event from the gallery registered and reachable on the act-1 map.
2. One enemy renamed with its intents' words changed and a still portrait
   in place of its rig, in one zone only.
3. One act's music replaced by a packaged track, with the original ducked,
   surviving a combat start and a rest site.
4. One zone dressed two ways, chosen at act start by a coin the mod flips.

Nothing measured on the spike is quotable; it is a feasibility read. Its
report lands in `review/records/`.

## 5. Rules this stream runs under

- **Design is Fable's; the second session is a Fable session.** Research
  and execution are Opus and Sonnet. Art picks ship at shortlist rank 1
  (R212). Text conversions are hygiene-grade.
- **It never takes the seats, the lanes or the GPU while a Klee
  calibration round or [USER]'s run is up** (`no-seats-during-steam-play`).
- **It returns to [USER] twice:** the nation pairs for acts 2 and 3 (§3.4),
  and a contact sheet when a body lands. Everything else is disclosed in
  its packets.
- **Mechanics stay frozen.** A finding that a slot cannot be dressed
  without changing behaviour is recorded as such and parked, never fixed
  by moving a number.
- **Music and art sources are [USER]'s to supply** into the gitignored
  raw directories; the pipeline packages what it finds and commits
  nothing.

## 6. Order of work for the second session

1. Read this page, `CLAUDE.md`, `STATE.md`, then the four galleries and
   the two research pages named in §2, and nothing else.
2. Run §3 as one Sonnet fan-out per act, curate, and post the mapping
   packet.
3. Start §4 in parallel with §3, on its own worktree.
4. Write the music and portrait raw-directory conventions into
   `docs/current/operations/` beside the art pipeline's, before any file
   is placed.
