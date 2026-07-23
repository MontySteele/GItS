# Furina Art Pass Requirements

**Date:** 2026-07-23

**Status:** implementation handoff; art work is intentionally separate from the Furina codegen pass
**Canonical content:** `docs/furina-cards.yaml`, `docs/fontaine-companions.yaml`, `docs/mondstadt-companions.yaml`, and `tier0/content/cards/tokens.yaml`

## 1. Outcome

Deliver complete, source-tracked portrait coverage for Furina's playable card
surface, including the generated Neuvillette Guest Stars and every currently
missing shared Companion card. Also deliver the minimum character, resource,
power, and relic art needed for Furina to read as a distinct playable character
in the roster mod.

The card-sized output bill is:

| Surface | Required portraits |
|---|---:|
| Furina personal sheet | 76 |
| Ethereal Spotlight token | 1 |
| Missing Companion cards (all kinds) | 24 |
| **Total card-sized outputs** | **101** |

The 24 missing Companion cards break down as 18 normal 4-star cards, the 3
Neuvillette Guest Stars, and the 3 five-star rares. The Companion sheets hold
31 rows (28 normal + 3 rare); seven normal rows already have files.

**RATIFIED 2026-07-23 — bill corrected from 102 to 101.** The first draft of
this section was transcribed prose and disagreed with the canonical sheets
three ways at once:

- `dahlia_sacramental_shower` was billed as missing ("never reached the final
  output directory"). It had: 500×380 opaque RGBA, from the same
  2026-07-21 14:04 batch as the six this doc did count, with three candidate
  rows in `art/SOURCES.tsv`. Re-fetching it would have overwritten
  eyes-on-approved art. The older “21 missing” note in `klee-mod/DECISIONS.md`
  was right and should not have been overridden.
- `albedo_solar_isotoma`, `durin_witchs_flame` and `nicole_celestial_gift` are
  `rarity: rare` (5-star, one card each) and were listed under *normal*
  Companion portraits, so they could not reconcile against a 28-normal-row
  denominator.
- The three Neuvillette Guest Stars are ordinary rows in
  `fontaine-companions.yaml`, but were billed as a surface separate from the
  Companion count — double-counting them against any sheet-driven check.

The last two cancelled numerically (three rares in, three Guest Stars out),
which is why the arithmetic looked self-consistent while being wrong in both
directions. **The bill is now a DERIVED number: `tools/art_coverage.py` owns
it, and this table is a snapshot of that tool's output.** If the two ever
disagree, the tool is right — that is the whole lesson of this correction.

The existing `xingqiu_raincutter.png` is not in the current Companion sheets
and therefore does not count as roster coverage; it is carried as a recorded
`KNOWN_STALE` entry in the coverage tool.

## 2. Policy and visual language

The existing three-tier policy remains binding:

- **Tier P — programmatic:** safe placeholders for development. A missing
  portrait must degrade to this, never to a broken card node.
- **Tier F — found/official/fan:** private playtest builds only. Every source
  must be logged when fetched.
- **Tier O — original/commissioned:** the only art permitted in a public build.

Official Genshin art is useful for a consistent private playtest, but is not
distribution-safe. Nothing in this pass changes the public-release rule in
`teyvat-spire-design-principles.md` §9.

### Furina register rules

Use the Klee art-pass registers and lint rules:

- `splash`: character, story, birthday, Wish, or other full illustrations.
- `tcg`: direct talent/skill matches and coherent Companion identity art.
- `vfx`: attacks and elemental moments only when the effect fills the crop.
- `sticker`: personality, emotion, comedy, and theatrical reaction cards.
- `item`: props, food, invitations, scripts, tickets, and stage objects;
  always contain/autocrop-contain on an opaque backing.
- `icon`: forbidden for card portraits; reserved for powers, resources,
  relics, and UI.

Additional direction for Furina:

- **Salon:** aqua/teal, bubbles, the three Salon Members, domestic hospitality,
  and off-stage motion. Member identities should remain legible at card size.
- **Fanfare:** indigo, white, rose, and gold; crowds, applause, musical
  escalation, emotional flux, and visible performance energy.
- **Spotlight:** hard white/blue beams, stage machinery, invitations, casts,
  billing, and clearly shared frames with Companions.
- **Courtroom/generic:** Fontaine blue, navy, silver, and restrained gold;
  poised swordwork, judgment, testimony, and Regina-versus-vulnerable Furina.
- Avoid UI, damage numbers, subtitles, watermarks, or a tiny character lost in
  a gameplay field. No constellation sigils as card portraits.
- Reuse is allowed across registers and within a single Companion character's
  sibling cards when differentiated by crop.

**Source-uniqueness rule — AMENDED & RATIFIED 2026-07-23.** The original rule
("one effective source should not serve two unrelated Furina cards") assumed a
Furina illustration inventory that does not exist. The art hunt established that
the wiki holds only ~20–25 clean, single-figure, text-free Furina illustrations;
the rest are version-banner splashscreens (burnt-in text — see L9), UI
infographics, multi-character scene art where Furina is a small background figure,
turnaround sheets, and namecards. 76 unique clean sources cannot be sourced. The
rule is therefore scoped by rarity:

- **Basics + rares (20 cards): STRICT** — one unique effective source each, no
  reuse by any other card. These are the identity-defining cards and must look
  distinct. Enforced by a blank `source_group` (strict L1).
- **Commons + uncommons (56 cards): crop-reuse allowed** — may share a source
  with another common/uncommon *provided the crop differs*, exactly the
  Companion sibling pattern. Enforced by `source_group = furina_pool` (L7). A
  pool card may NOT reuse a strict card's source (group mismatch → L1 fires),
  which is what protects the 20 unique sources.

This is the same "the gate assumed data the repo can't see" lesson as the bill
correction: the rule is only as good as the inventory it presumed.

## 3. Output layout and processing contract

### Paths

- Furina cards and selector:
  `ImageGen/images/cards/furina/<sheet_id>.png`
- Normal Companions and Guest Stars:
  `ImageGen/images/cards/companions/<sheet_id>.png`
- Furina UI:
  `ImageGen/images/furina/ui/<asset>.png`
- Furina powers/resources:
  `ImageGen/images/furina/powers/<asset>.png`
- Furina relics:
  `ImageGen/images/furina/relics/<asset>.png`
- Furina model source/output:
  `ImageGen/images/furina/model/<asset>.png`

The character-aware code pass must stage these without overwriting the existing
Klee files and pack them under `res://furina/`.

### Card processing

- Final dimensions: **500×380 RGBA**.
- Final portrait must be fully opaque. Composite transparent sources onto the
  established parchment backing rather than leaving alpha holes.
- Default illustration processing: `cover_autocrop`, figure-centered,
  `cover@0.06`.
- Companion default: the ratified Wish/splash `cover_autocrop` treatment.
  Use the same strong source for sibling cards and change framing:
  full-body/signature crop, action crop, and close/support crop.
- Item sources: `contain` or `cover_autocrop` with `contain`; never fill-crop.
- Any crop that loses a face, hand, weapon, Salon Member, or core VFX returns
  to the contact sheet rather than being patched after promotion.

### Source ledger

Every candidate and promoted output needs:

`filename → source URL → tier → replacement priority`

Card portraits, the selection splash, and model art are `high` replacement
priority for a future Tier O pass. Power/relic icons are `medium`; small UI
pieces are `low` unless they are character-select-facing.

## 4. Furina personal-card portrait inventory

The `register` column is the preferred starting class, not a prohibition
against a stronger candidate from another legal register.

### Basics — 5

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `soloists_solicitation` | Soloist's Solicitation | Furina's restrained normal sword/cane strike; intentionally modest, not a Burst-scale image. | vfx/tcg |
| `stage_presence` | Stage Presence | Furina holding her poise beneath a stage light or water guard; defensive confidence. | splash |
| `regal_bearing` | Regal Bearing | The Regina's commanding stare stopping an opponent in their tracks. | splash/sticker |
| `aria_of_recompense` | Aria of Recompense | A solitary Hydro aria restoring composure; blue notes, heart, or gentle water motif. | splash |
| `salon_debut` | Salon Début | The curtain rises on the Salon Members; first entrance should show the ensemble identity immediately. | tcg/splash |

### Common Salon — 9

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `gentilhomme_usher` | Gentilhomme Usher | Usher's octopus silhouette and a protective bubble/shield swell. | tcg/splash |
| `surintendante_chevalmarin` | Surintendante Chevalmarin | Chevalmarin's seahorse silhouette amid restorative bubbles. | tcg/splash |
| `mademoiselle_crabaletta` | Mademoiselle Crabaletta | Crabaletta's crab silhouette making a heavy, forceful entrance. | tcg/splash |
| `dinner_service` | Dinner Service | Salon Members serving or stealing an extravagant meal/tea setting. | splash/item |
| `usher_the_waves` | Usher the Waves | Furina directing a clean Hydro wave at one target. | vfx/tcg |
| `torrential_turn` | Torrential Turn | A sweeping water turn or sword flourish exploiting an elemental opening. | vfx |
| `matinee_performance` | Matinée Performance | Bright daytime stage, script/page, and a light Hydro performance. | splash |
| `rising_tide` | Rising Tide | Water visibly climbing around the stage while reserve bubbles gather. | vfx/splash |
| `house_call` | House Call | The Salon arriving together to surround or harry an enemy. | splash |

### Common Fanfare — 9

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `curtain_up` | Curtain Up | Curtains opening on a small reserve of blue performance energy. | splash/item |
| `dramatic_entrance` | Dramatic Entrance | Furina's emphatic entrance or opening strike before a reacting crowd. | splash/vfx |
| `crowd_work` | Crowd Work | Furina engaging the audience directly; hands, cards, or reactions flowing back to her. | splash/sticker |
| `suffering_for_art` | Suffering for Art | A knowingly theatrical wound: pain converted into renewed performance, not gore. | splash/sticker |
| `thunderous_ovation` | Thunderous Ovation | Applause becoming a broad sound/water shield around Furina. | splash/vfx |
| `tempo_change` | Tempo Change | A conductor's beat or snapping musical transition that accelerates the turn. | splash/item |
| `warmup_act` | Warm-up Act | A quick, light rehearsal strike; energetic but deliberately small. | vfx/sticker |
| `audience_participation` | Audience Participation | Tickets, raised hands, or audience members feeding the performance. | splash/item |
| `ebb_and_flow` | Ebb and Flow | Two-way tide or alternating heart/water motion showing spend and refill. | vfx/splash |

### Common Spotlight — 6

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `an_invitation` | An Invitation | Ornate Fontaine invitation or tea-party card opening a door for a Guest Star. | item |
| `limelight` | Limelight | One concentrated spotlight finding a performer; strong light/dark separation. | splash/vfx |
| `shared_billing` | Shared Billing | Furina and a Companion sharing one marquee/frame while Hydro crosses between them. | splash |
| `blocking_notes` | Blocking Notes | Stage marks, blocking diagram, or Furina physically re-staging a performer. | item/splash |
| `stage_lights` | Stage Lights | Multiple beams flaring across the stage and dazzling the audience. | vfx/splash |
| `curtain_cue` | Curtain Cue | A hand, rope, bell, or curtain signal at the exact moment the light moves. | item/splash |

### Common Generic — 7

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `graceful_retreat` | Graceful Retreat | Elegant evasive step behind curtain or water, preserving composure. | splash/sticker |
| `poised_riposte` | Poised Riposte | Controlled sword counter with a narrow Hydro flourish. | vfx/tcg |
| `commanding_gaze` | Commanding Gaze | Wide, imperious stare weakening a whole group. | splash/sticker |
| `witness_stand` | The Witness Stand | Fontaine courtroom testimony, evidence, or a pointed accusation. | splash |
| `macaron_break` | Macaron Break | A literal macaron respite with a small protective/buffer read. | item/sticker |
| `swelling_overture` | Swelling Overture | Sheet music and water rising together toward a larger movement. | splash/item |
| `undercurrent` | Undercurrent | Broad Hydro force moving beneath the stage and striking the full enemy line. | vfx |

### Uncommon Salon — 7

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `full_ensemble` | Full Ensemble | All three Salon Members together, clearly separated and readable. | tcg/splash |
| `grand_salon` | Grand Salon | Lavish persistent Salon stage; opulent environment rather than a single attack. | splash |
| `many_waters_melody` | Melody of Many Waters | The Singer's restorative Hydro melody with the Salon in attendance. | splash/tcg |
| `dress_rehearsal` | Dress Rehearsal | Script, costume, and one Member rehearsing before the real show. | splash/item |
| `crashing_waves` | Crashing Waves | Large multi-target Hydro crash exploiting aura-bearing enemies. | vfx |
| `overflowing_hospitality` | Overflowing Hospitality | Guest service so excessive it spills into water, bubbles, and another Member. | splash |
| `waters_embrace` | The Water's Embrace | Protective water wrapping Furina or the company in a clear defensive silhouette. | splash/vfx |

### Uncommon Fanfare — 7

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `crescendo` | Crescendo | Audience and music visibly mounting into a damaging peak. | vfx/splash |
| `showstopper` | Showstopper | One decisive finishing pose or strike freezing the room. | splash/vfx |
| `florid_cadenza` | Florid Cadenza | Ornate, fast musical run represented by elaborate notes/script pages. | splash/item |
| `hearts_swelling` | Hearts Swelling | Emotion and audience affection visibly filling Furina's reserve. | splash/sticker |
| `rapturous_applause` | Rapturous Applause | Sustained applause as a persistent offensive engine, not a one-time clap. | splash |
| `pit_orchestra` | Pit Orchestra | Orchestra beneath the stage throwing up a protective wall of sound/water. | splash |
| `flood_of_emotion` | Flood of Emotion | Tears or intense feeling breaking into a powerful Hydro surge. | splash/vfx |

### Uncommon Spotlight — 7

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `leading_role` | Leading Role | The selected performer steps forward while the rest of the stage recedes. | splash |
| `supporting_cast` | Supporting Cast | Ensemble poised behind the lead; readable “first supporting beat” composition. | splash |
| `guest_list` | The Guest List | A richer invitation ledger or roster with several anticipated guests. | item |
| `directors_cut` | Director's Cut | Clapboard, edit splice, or repeated performance under Furina's direction. | item/splash |
| `top_billing` | Top Billing | Illuminated marquee/name at the top of the theatre bill. | item/splash |
| `duet` | Duet | Furina and one Companion mirroring or echoing the same performance. | splash |
| `standing_ovation` | Standing Ovation | Whole audience rising while Furina converts the response into renewed stage power. | splash |

### Uncommon Generic — 4

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `fortissimo_guard` | Fortissimo Guard | Loud musical accent rendered as a hard defensive barrier. | vfx/splash |
| `courtroom_drama` | Courtroom Drama | Accusation, shocked gallery, or vulnerable defendant with evidence in motion. | splash |
| `quick_change` | Quick Change | Costume/stance swap, discarded prop, and new card/role appearing immediately. | splash/item |
| `deep_breath` | Deep Breath | Quiet composure between acts; close portrait with water settling. | splash |

### Rares — 15

Rare portraits should receive the strongest identity art and the most generous
manual crop review.

| ID | Card | Visual brief | Register |
|---|---|---|---|
| `let_the_people_rejoice` | Let the People Rejoice | Furina's Burst-scale public performance: Hydro spectacle, audience, and triumph. | tcg/vfx/splash |
| `encore_performance` | Encore Performance | A lit performance duplicated in a mirror, second stage, or echoed card frame. | splash |
| `singer_of_many_waters` | Singer of Many Waters | Pneuma/Singer identity delivering unmistakable true restoration. | tcg/splash |
| `unheard_confession` | Unheard Confession | Private vulnerability and healing after the audience is gone. | splash |
| `endless_waltz` | Endless Waltz | Salon Members dancing in a persistent circular pattern around Furina. | splash |
| `grand_gala` | Grand Gala | Overfull company and extravagant gala, with displaced Members taking final bows. | splash |
| `the_sea_is_my_stage` | The Sea Is My Stage | Furina commanding a stage made from the sea despite a visible personal cost. | splash/vfx |
| `universal_revelry` | Universal Revelry | Full-house celebration converted into a sweeping attack. | splash/vfx |
| `star_of_the_show` | Star of the Show | One performer isolated as the unmistakable star beneath a brilliant beam. | splash |
| `prima_donna` | Prima Donna | Commanding soloist at the center of an elaborate, high-status production. | splash |
| `high_tide` | High Tide | The largest conventional Hydro wave in the deck, filling the entire frame. | vfx |
| `rain_of_roses` | Rain of Roses | Roses and Hydro falling through a shared Spotlight onto Furina and cast. | splash/vfx |
| `the_final_verdict` | The Final Verdict | Courtroom judgment resolving into a decisive sword/Hydro strike. | splash/vfx |
| `command_performance` | Command Performance | Furina directing several Guest Stars or invitations into one grand production. | splash |
| `reginas_mercy` | The Regina's Mercy | Regal compassion: Furina extending genuine aid without losing authority. | splash |

## 5. Token portrait

| ID | Surface | Visual brief | Register |
|---|---|---|---|
| `ethereal_spotlight` | Ethereal Spotlight | A portable theatrical light or selector beam with two readable destinations: Furina/Center Stage and the wider Guest Cast. It must remain legible when generated every turn. | vfx/item |

## 6. Neuvillette Guest Star portraits — 3

These are temporary Companion cards and belong in the Companion directory.
Use one strong Neuvillette Wish/splash source with three deliberately different
crops; same-source sibling reuse is intended here.

They are ordinary rows in `fontaine-companions.yaml`, so they are **counted
inside** the 24 missing Companion cards in §1 and §7, not added on top of it.
This section exists to give them their own crop brief, not a second line item.

| ID | Card | Crop/visual brief |
|---|---|---|
| `guest_neuvillette_tears` | Neuvillette — O Tears, I Shall Repay | Action crop with cane/hand and a narrow Hydro strike; closest framing of the three. |
| `guest_neuvillette_droplets` | Neuvillette — Sourcewater Droplets | Support crop emphasizing droplets, Hydro field, and protective space. |
| `guest_neuvillette_judgment` | Neuvillette — Equitable Judgment | Signature full-body/wide crop with the charged beam spanning the frame; preserve the personal-cost gravity. |

## 7. Missing Companion portraits — 24

The source rule from `companion-art-plan-addendum.md` remains the default:
Wish/splash art, `cover_autocrop`, cover fill, with sibling differentiation by
crop. Dahlia may use the previously accepted Character Card fallback. If a
direct TCG talent card is materially stronger and coherent with that
character's existing portrait, include it as a contact-sheet alternative.

Run `python tools/art_coverage.py` for the live list; the tables below are a
snapshot of it. The 24 are 6 Mondstadt normals + 3 five-star rares + 12
Fontaine normals + the 3 Neuvillette Guest Stars from §6.

`dahlia_sacramental_shower` is **already covered** and is deliberately absent
from these tables. Do not re-fetch it (see the ratification note in §1).

### Mondstadt/shared normal set — 6

| ID | Card | Visual/crop requirement |
|---|---|---|
| `dahlia_favonian_favor` | Dahlia — Favonian Favor | Same Dahlia family source as the shipped `dahlia_sacramental_shower`, wider support/blessing crop; use contain if cover clips the head/hat. |
| `fischl_oz` | Fischl — Oz, at Your Side | Fischl/Oz source with Oz dominant and readable; differentiate from the existing Nightrider attack. |
| `barbara_shining_idol` | Barbara — Shining Idol | Wider support/idol crop with melody or healing field; not the same framing as `barbara_melody`. |
| `sucrose_astable` | Sucrose — Astable Anemohypostasis | Alchemical/Anemo experiment crop with apparatus or vortex prominent. |
| `bennett_fantastic_voyage` | Bennett — Fantastic Voyage | Burst/support field crop, wider and more triumphant than the existing Passion attack. |
| `diona_icy_paws` | Diona — Icy Paws | Icy shield/paw motif; preserve Diona's figure rather than filling with a generic Cryo icon. |

### Five-star rares — 3

`rarity: rare`, one card each, no siblings to differentiate against. They get
rare-grade identity art and the generous manual crop review of §4's rares, not
the 4-star sibling-crop treatment.

| ID | Card | Visual/crop requirement |
|---|---|---|
| `albedo_solar_isotoma` | Albedo — Solar Isotoma | Geo flower/platform clearly visible; persistent-power composition. |
| `durin_witchs_flame` | Durin — Witch's Flame | Dark Pyro/dragon identity, persistent and ominous rather than a generic explosion. |
| `nicole_celestial_gift` | Nicole — Celestial Gift | Celestial/support image with a clear beneficent gift or blessing read. |

### Fontaine set — 12

Each character uses one source family and three crops: the uncommon signature
gets the widest/fullest crop; the common attack and support receive tighter,
mechanically distinct crops.

| ID | Card | Visual/crop requirement |
|---|---|---|
| `chevreuse_interdiction_fire` | Chevreuse — Interdiction Fire | Tight musket/action crop with Pyro shot. |
| `chevreuse_vanguards_valor` | Chevreuse — Vanguard's Valor | Support crop emphasizing command/valor rather than the projectile. |
| `chevreuse_bursting_grenades` | Chevreuse — Ring of Bursting Grenades | Wide signature crop preserving grenade ring and musket flash. |
| `lynette_enigmatic_feint` | Lynette — Enigmatic Feint | Defensive/evasive close crop, reserved expression and misdirection. |
| `lynette_box_trick` | Lynette — Box Trick | Prop/box and Anemo trick prominent; medium crop. |
| `lynette_astonishing_shift` | Lynette — Magic Trick: Astonishing Shift | Wide signature magic-stage crop with full shift effect. |
| `charlotte_freezing_point` | Charlotte — Framing: Freezing Point Composition | Camera/action crop and Cryo impact. |
| `charlotte_enduring_frosthelm` | Charlotte — Enduring Frosthelm | Protective/support crop with frost field or guard silhouette. |
| `charlotte_snappy_silhouette` | Charlotte — Snappy Silhouette | Wide signature journalism/photo composition with clear camera identity. |
| `freminet_pers_deploy` | Freminet — Pers, Deploy! | Pers-forward action crop; companion/device must remain visible. |
| `freminet_pressurized_floe` | Freminet — Pressurized Floe: Backstroke | Underwater/flowing Cryo attack crop distinct from Pers. |
| `freminet_shattering_pressure` | Freminet — Shattering Pressure | Wide signature crop emphasizing pressure, diving weight, and Shatter payoff. |

### Existing roster portraits outside this required set

The six current in-sheet files are:

`fischl_nightrider`, `barbara_melody`, `sucrose_gust`,
`bennett_passion`, `kaeya_frostgnaw`, and `prune_witch_hunt`.

They do not need to be redone to complete missing coverage. A later consistency
refresh may move them from the older TCG/one-off framing to the ratified
Wish-family treatment. Any such refresh is a taste decision and should not
silently expand this pass.

## 8. Furina non-card assets

### Required UI and model outputs

| Asset | Dimensions | Requirement |
|---|---:|---|
| `ui/select_portrait.png` | 132×195 | Furina roster tile; face and hat/hair silhouette readable at native size. |
| `ui/select_portrait_locked.png` | 132×195 | Derived desaturated/darkened variant. |
| `ui/char_icon.png` | 88×88 | In-run top-panel icon; strong facial silhouette, transparent background. |
| `ui/energy_icon_74.png` | 74×74 | Furina/Hydro energy symbol for card UI. |
| `ui/energy_icon_22.png` | 22×22 | Crisp small derivation; inspect at 1:1 rather than trusting downscale. |
| `ui/map_marker.png` | 49×64 | High-contrast Furina silhouette or hat/crown motif. |
| `ui/selection_splash.png` | 1920×1200 | Full selection-screen composition with safe room for UI text/panels. |
| `ui/select_bg.png` | 1920×1080 | Character-select backdrop behind the splash. **Added 2026-07-23** — `tools/build_pck.ps1` requires it and this table omitted it. Furina's scene tints it `Color(0.33, 0.55, 0.68)` where Klee's is warm red, so a shared neutral backdrop is legitimate; a Furina-specific one is optional polish, not a gap. |
| `ui/transition_wipe.png` | procedural | Select-transition wipe texture for `materials/furina_transition_mat.tres`. **Added 2026-07-23** — same omission. Generated by `tools/gen_transition_wipe.py`, not hunted; sharing Klee's is fine. |
| `model/combat_model.png` | 240×280 minimum output | Transparent full-body sprite, feet bottom-anchored; also serves the static rest/merchant fallback. |

**`energy_icon_74` / `energy_icon_22` have no consumer yet.** No C# in the mod
references them, and `Furina.cs` currently points `CustomEnergyCounterPath` at
the base game's `ironclad_energy_counter.tscn`. Producing them changes nothing
in-game until someone authors a Furina energy-counter scene. Keep them in the
bill — they are real §11 smoke-test items — but treat the scene as the blocking
work, not the art.

### Klee fallback fill — how §11's "no Klee assets" is actually checked

As of `def4c50`, `build_pck.ps1` copies eight required assets from Klee's
namespace into Furina's when Furina has no file of her own, so her resource
*paths* could go character-specific before her art existed. It is a genuinely
good call — but it means a missing Furina asset now renders as **Klee art**
rather than as an obvious hole, and the §11 criterion "render without falling
back to Klee assets" is no longer verifiable by eye.

The signal is the build log: each fill prints `Furina fallback: <path> <- Klee`
in dark yellow. **A clean Furina art pass ends with zero such lines** (except
any deliberately shared neutral asset, currently `select_bg` and
`transition_wipe`). Check the build output, not the screen.

Optional polish after the static model is proven:

- Layer the combat source into back hair/cape, body, head, arms, and front
  ornament for idle bob/attack lunge/hurt shake.
- Add victory transition art and co-op minigame poses during the C4 pass.
- Author a custom Hydro card-frame material; borrowing an existing blue frame
  remains acceptable for the first private playtest.

### Starting relic — 1

| Asset ID | Dimensions | Brief |
|---|---:|---|
| `relics/ethereal_spotlight_relic.png` | 256×256 | Furina's starting talent/relic: a theatrical lens, crown, or spotlight apparatus that communicates “one selector every turn.” Final display name may change in the lore pass; keep the file slug mechanical. |

### Power/resource icon set — 14 minimum

All icons are **256×256 transparent**. Constellation/talent sigils are legal
private-build sources here because this is the register they suit.

| Asset ID | Gameplay read |
|---|---|
| `powers/encore.png` | Unbounded blue buffer remaining. |
| `powers/fanfare.png` | Capped audience/activity resource. |
| `powers/burst_meter.png` | Furina's 70-point Burst Energy meter. |
| `powers/salon_member.png` | Active Member count, capped at three. |
| `powers/salon_damage_up.png` | Salon tick/final-bow damage increase. |
| `powers/fanfare_attack.png` | Attack bonus per 10 Fanfare. |
| `powers/spotlight_boost.png` | Percentage boost to Spotlighted numbers; turn and combat variants may share it. |
| `powers/spotlight_damage.png` | Flat Spotlighted damage; turn and combat variants may share it. |
| `powers/spotlight_discount.png` | First Spotlighted card Energy discount. |
| `powers/spotlight_draw.png` | First Spotlighted card draws. |
| `powers/ovation_spend_boost.png` | Encore-spend event strengthens the Spotlight this turn. |
| `powers/spotlight_encore.png` | First Spotlighted play grants Encore. |
| `powers/center_stage.png` | Current designation is Furina/Center Stage. |
| `powers/guest_cast.png` | Current designation is all Companions/Guest Cast. |

Weak, Vulnerable, and Hydro-aura icons are already supplied by the base game or
the shared roster mod and are not Furina art-pass work.

## 9. Pipeline changes required before execution

1. **DONE (2026-07-23)** — no code change needed. `tools/art_process.py`
   already creates each output's parent directory, so the character-aware
   paths in §3 come into being when their rows are processed; verified no
   Klee-specific hardcoding in the processor.
2. Extend `art/plan.tsv` with rows for every required output.
3. **DONE (2026-07-23)** — `source_group` column in `art/plan.tsv`, enforced by
   `tools/art_lint.py` (rule **L7**) and gated by
   `tier0/tests/test_art_lint_source_group.py`. Same-source/different-crop
   reuse is legal within a group and illegal across groups; same-source
   *same-crop* inside a group is L7, since that is one picture on two cards.
   Blank `source_group` keeps the original strict L1 — Furina's own 76 cards
   are deliberately ungrouped, because grouping them by character would have
   legalised exactly the reuse §2 forbids.
4. **DONE (2026-07-23)** — `tools/art_contact_sheet.py` is roster-aware:
   `--batch` renders the §10 batches, `--list` prints batch sizes. Routing is
   by output path first so another character's cards cannot fall into Furina's
   archetype batches, and anything unclassified lands in `unsorted` rather
   than being silently dropped.
5. **DONE (2026-07-23)** — `tools/art_coverage.py`, gated by
   `tier0/tests/test_art_coverage.py`. Reads the canonical YAML sheets and
   token file, compares expected IDs to final PNG stems, and reports stale
   outputs such as `xingqiu_raincutter.png` separately from missing ones.
   Built first, before any fetching: it is what caught the §1 bill error, and
   it is now the authority on the count.
6. **DONE (2026-07-23, commit `def4c50`)** — `tools/build_pck.ps1` stages
   `ImageGen/images/furina/**` under `res://furina/**`, authors Furina's
   scenes and transition material, and fills missing Furina assets from Klee
   so her paths could go character-specific ahead of her art. `Furina.cs` now
   points at `furina/...` throughout. See the §8 note on how that fallback
   changes the way §11's "no Klee assets" criterion must be checked.
7. **Already implemented** — `tools/art_fetch.py` merges `art/SOURCES.tsv` by
   filename and keeps existing rows verbatim. Added after a real incident
   (2026-07-20) where a rewrite from a partial fetch truncated the ledger from
   115 rows to 30. Verified, unchanged by this pass.

## 10. Review batches

Avoid one 101-card wall. Produce four labeled contact-sheet batches:

1. **Furina identity:** basics, generic/courtroom, and all 15 rares.
2. **Salon + Fanfare:** verify Member readability and separate applause/music
   cards from generic blue VFX.
3. **Spotlight:** verify invitations, billing, selector, and shared-cast cards
   do not collapse into identical beams.
4. **Companions:** all 24 missing Companion cards — 18 normals, the 3 Guest
   Stars, and the 3 five-star rares — grouped by character so sibling crop
   differentiation is reviewed together.

UI/model/power/relic assets receive their own small native-size sheet.

## 11. Acceptance criteria

### Coverage

- All 101 card-sized output paths exist or have an explicitly approved Tier P
  fallback; there are no accidental BaseLib “BETA” portraits.
- Every ID in the four inventories resolves to the correct filename.
- Stale files are reported but never counted as coverage.
- `python tools/art_coverage.py --strict` exits 0. This is the gate that owns
  the coverage number; the counts written above are a snapshot of it and are
  expected to be re-derived, never hand-maintained.

### Mechanical validation

- Every card portrait is exactly 500×380 RGBA and fully opaque.
- Icons and UI pieces match their required dimensions and alpha treatment.
- No effective unrelated card pair shares an identical source/crop or output
  hash.
- No portrait contains visible gameplay UI, damage numbers, watermarks, or
  clipped primary subjects.
- `tools/art_lint.py` and the new coverage check pass.
- The generated gallery renders all Furina and Companion cards without missing
  image warnings.

### Provenance and taste

- Every Tier F candidate and promoted output has a source-ledger row.
- Every promoted output has a declared register.
- User selections from all four contact-sheet batches are applied and recorded.
- Rare cards, the selector, the three Salon Members, and Companion sibling
  crops receive explicit eyes-on approval.

### In-game smoke test

- Character select, top panel, map marker, energy icon, starting relic, and
  combat model render without falling back to Klee assets. **Verify from the
  `build_pck.ps1` log, not the screen** — the Klee fallback fill makes a
  missing asset look like working Klee art (see §8).
- Draw at least one card from each Furina rarity, each archetype, each
  Companion character, and the Neuvillette Guest Star set.
- Inspect the 22×22 energy icon, 88×88 character icon, and power badges at
  native scale; large-source quality does not guarantee small-icon legibility.

## 12. Explicitly out of scope

- Audio/SFX and voice work.
- Public-release Tier O commissioning itself; this document only makes its
  replacement bill enumerable.
- Repainting Klee's remaining portraitless cards.
- Refreshing the six already-covered normal Companion cards unless separately
  approved as a consistency pass.
- Future Fontaine five-star banner cards beyond the three temporary
  Neuvillette Guest Stars.
- Furina relic/potion pools beyond the starting relic; those designs are not
  yet a stable art manifest.
