# Art Sprint Spec — Slice Assets (Tier F, private build)

**Runs:** before/alongside C1. **Executor:** Claude Code on the user's machine (wiki-hosted official assets are automatable; anything requiring taste gets a shortlist for the user to pick from). **Governing docs:** art-asset-manifest.md (dims/counts), principles §9 (Tier F never ships).

## 0. Policy, stated precisely
Official-first, for the *right* reasons: official assets are NOT lower-risk for distribution (they're the primary DMCA category — nothing Tier F ever ships, official or fan). They're preferred for the private build because they're stylistically uniform, systematically complete via wiki hosting, carry no individual-artist ethics questions, and make eventual replacement a clean enumerable operation instead of an archaeology project. Fanart remains the fallback for gaps only.
**Discipline:** `assets/SOURCES.tsv` — one row per asset: `filename → source_url → tier(F/P) → replace_priority`. Maintained from the first download. This file IS the future public-release checklist.

## 1. Source map (slice: 31 cards + 7 companions + icons + model)

**Direct official matches (the mod's ability names ARE Genshin ability names — the TCG and skill-icon art maps 1:1):**
| Asset | Official source |
|---|---|
| kaboom, jumpy_dumpty, sparks_n_splash | Genius Invokation TCG card art for Klee's three combat talents (same names) |
| pounding_surprise (relic) | TCG talent-card art "Pounding Surprise" (yes, it exists, same name) |
| da_da_da | The famous Klee sticker — official Paimon's Paintings emoji set |
| pop, mine_toss, bomb_voyage, all bomb cards | Jumpy Dumpty / mine visuals: skill preview stills, TCG art crops at different zooms |
| Aura power icons ×6 | Official element symbols (Pyro/Hydro/Cryo/Electro/Anemo/Geo) — instantly legible, shared mod-wide forever |
| Companion cards ×7 | Each companion's TCG skill-card art (Dahlia's psalter, Fischl's Oz, Kaeya's Frostgnaw, Sucrose's gust, Bennett, Barbara, Prune's kit art) |
| char select / selection screen / icon | Klee splash art (wish art) at crops; official chibi/icon renders for the 88×88 |
| energy icon | Pyro symbol variant |

**Category guidance for invented cards (no 1:1 ability exists):**
- Flavor/personality cards (sorry_jean, hide_and_seek, eager_to_help, cant_catch_me, sparkly_treasure): official stickers, event art, character-story illustrations, screenshots — Klee's sticker coverage is unusually deep; shortlist 3 candidates per card for user pick.
- Generic combat cards (big_badda_boom, blast_radius, rapid_fire, crackle): skill VFX screenshots, explosion stills from trailers/event cutscenes.
- Abstract/utility (combustion_study, spark_collection, explosives_workshop): namecard art (official abstract designs), item icons (Klee's bombs exist as materials/items).

## 2. Pipeline
1. **Fetch:** wiki-hosted official images (character page, TCG card list, sticker galleries, namecards). Automatable; log every URL to SOURCES.tsv at download time, not after.
2. **Name:** target filenames are the YAML card ids — the sheet is already the manifest (`jumpy_dumpty.png` etc.), dropping straight into the ImageGen input layout (`ImageGen/images/cards/klee/<id>.png`).
3. **Process:** batch script — cards center-crop/resize to 500×380; icons to 256×256 on transparent; UI pieces per manifest dims. Flag any image whose crop loses the subject for manual reframe.
4. **Gaps:** any card with no acceptable match keeps its Tier P programmatic frame — art never blocks the build. Report the gap list.
5. **User-taste queue:** for the shortlist categories, emit a single contact-sheet HTML (3 candidates per card, click to select) rather than 30 one-off questions.

## 3. Combat model (the one hand-work item)
Source: Klee splash art or official full-body render (transparent-BG renders exist on wiki). Cut 4 layers — back (cape/backpack), body, head, **Dodoco (own layer, mandatory)** — any editor, 30–60 min. Godot scene per hexaghost2.tscn pattern: idle bob 2–3px sinusoidal with per-layer phase offset (Dodoco offset largest), attack lunge tween, hurt shake + spark particles. If the cut is annoying, Tier P fallback: single uncut render with whole-sprite bob — still perfectly playable.

## 4. Also in this sprint (content, not art, but same "before playtest" bucket)
- **Keyword tooltip strings** (Downfall pattern: card_keywords.json): Pyro/Hydro/etc. auras, Reaction names, Bomb, Spark, Shatter, Burst, Encore-reserved. ~15 one-sentence strings; draft from principles §2, chat reviews in the same pass as C2 card text.

## 5. Acceptance
Slice assets present or gap-listed; SOURCES.tsv complete; contact sheet delivered for taste picks; model layers cut or fallback invoked; keywords drafted. Nothing here gates C1 — the sprint and "Boots" run in parallel.
