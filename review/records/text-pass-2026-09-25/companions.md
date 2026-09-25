# Companion text census — klee / companion / kokomi / furina-stage arms

Surface read: the 72 `proto_mc_*` / `proto_mi_*` Universal + Personal rows
`CompanionOverhaulRoster.Roster()` offers (`docs/prototype-surface.yaml` via
`klee-mod/KleeCode/Cards/Prototype/Generated/ProtoMc*.cs` / `ProtoMi*.cs`), the
19 shipped Fontaine companion rows still offered under the arm
(`docs/fontaine-companions.yaml`, untouched because `CompanionOverhaulRoster`
only replaces the `mondstadt`/`inazuma` nations — `klee-mod/KleeCode/Powers/
Prototype/CompanionOverhaulRoster.cs`), every `ArmKeywordTips` /
`KleeMod.cs` keyword tip that a call graph in those 91 cards actually attaches
(`ExtraHoverTips` on each generated card, checked by grep), the six
Applies-Element and nine reaction-preview tips (`KleeMod.cs` `card_keywords`
fallback table), and the power badges three companion cards grant
(`SoumetsuPower`, `SesshouSakuraPower`, `LightfallSwordPower`,
`klee-mod/KleeCode/Powers/Prototype/CompanionOverhaulInazuma.cs` and
`CompanionOverhaulHooks.cs`). Lengths are rendered — BBCode stripped, holes
one numeral — using `tools/lint_text_conventions.py`'s own `render()`, the
same function the shipped/prototype gate measures with.

**Counts.** 91 companion card faces read (72 proto + 19 shipped Fontaine),
plus 2 mode faces on the one modal Power (`proto_mc_durin_binary_form`); 20
companion-attached keyword/reaction tips read clean, 4 more (`Bomb`, `Set
off`, `Mine`, `Plan`) are pre-existing, ruled, over-ceiling exceptions
already carried by name in `tools/lint_text_conventions.py` and are not
re-litigated here; 3 power badges read. **8 rows flagged** (6 card faces + 2
power badges beyond what the ceiling lint already knows about), plus 1 card
(`proto_mc_durin_binary_form`) carrying its already-ruled ceiling exception,
noted for completeness and not counted as new. **83 card faces clean**, **20
keyword/reaction tips clean**, **1 power badge clean** (`LightfallSwordPower`
gets flagged too, so 0 of the three sampled powers are fully clean — see
below).

No F1 ceiling violation in this surface is NEW: the only card over its
ceiling (`proto_mc_durin_binary_form`, 184 of 120) and the only four tips
over theirs (`Bomb`/`Set off`/`Mine`/`Plan`) are already named, ruled
exceptions in `tools/lint_text_conventions.py` with their own reasons on
file. What this pass found instead is a phrasing-consistency class the
ceiling lint cannot see: a repeated deviation from `docs/current/
text-conventions.md` rule 8 ("a bonus is 'N additional damage'") into "plus
N" / "N more", one restated keyword tooltip, one word ("Counts") used for two
different jobs across sibling cards, and one semicolon on a plain sequential
clause where the house style reserves semicolons for either/or.

## Flagged rows

| id | kind | current text (rendered) | chars | flags | note |
|---|---|---|---|---|---|
| `lynette_enigmatic_feint` (shipped Fontaine) | card | "Swirl an enemy's aura onto ALL enemies. Gain 6 Block." | 53 | F2, F4 | Spells out exactly what the `Swirl` keyword tip already says ("the aura is consumed and copied onto ALL enemies"); every `proto_mc_`/`proto_mi_` Swirl card instead uses the verb form ("Swirl the enemy.", "Swirl ALL enemies.") |
| `lynette_astonishing_shift` (shipped Fontaine) | card | "Swirl an enemy's aura onto ALL enemies. Deal 6 damage to ALL enemies." | 69 | F2, F4 | Same restatement/phrasing break as above, on Lynette's other card |
| `SoumetsuPower.description` (power badge, Ayaka's kit) | power | "At the end of your turn, deal 6 Cryo damage to ALL enemies. 6 turns left; on the last, 6 more." | 94 | F4, F5 | Semicolon joins two plain facts, not an either/or (text-conventions rule 14); "6 more" is the "plus N"/"N more" deviation from rule 8's "N additional damage" |
| `proto_mi_ayaka_soumetsu` | card | "At the end of each of your next 6 turns, deal 8 Cryo damage to ALL enemies. On the last of them, deal 16 more." | 110 | F4 | "deal 16 more" — verified against `SoumetsuPower.FireVolley` (klee-mod/KleeCode/Powers/Prototype/CompanionOverhaulInazuma.cs:941) that this is a true, correct extra hit, so not F8 — but the wording breaks rule 8's "N additional damage" and matches the card's own power badge's deviation |
| `SesshouSakuraPower.description` (power badge, Yae's kit) | power | "At the end of your turn, each Sakura deals 6 Electro damage to a random enemy, plus 6 after the first. 6 out." | 109 | F4, F5 | "plus N" instead of "N additional damage"; "6 out" is unexplained shorthand for how many Sakura are deployed, terser than any sibling badge |
| `proto_mi_yae_sesshou_sakura` | card | "Place a Sakura, up to 3. At the end of your turn each deals 4 Electro damage to a random enemy, plus 3 after the first." | 119 (+"Draw 1 card." on upgrade) | F4 | Same "plus N" deviation, matches its own badge; verified against `SesshouSakuraPower.FireVolley` (CompanionOverhaulInazuma.cs:820) as accurate |
| `LightfallSwordPower.description` (power badge, Eula's kit) | power | "Counts its owner's Attacks. When it falls, deals 6 damage plus 6 per Attack counted. Falls in 6 turns." | 102 | F4 | "plus N per Attack" is the same rule-8 deviation; "Counts" here means "tallies a running total", a different sense of the same verb `proto_mi_heizou_heartstopper` uses for a per-unit damage rate |
| `proto_mi_heizou_heartstopper` | card | "Deal 6 damage. Counts 4 for each Swirl made before it this turn." | 64 | F4, F5 | "Counts 4 for each Swirl" breaks rule 8's "N additional damage" pattern every other per-stack companion card uses (e.g. `proto_mi_sara_tengu_stormcall`: "deal 5 additional damage"); "Counts" here means "is worth 4 per", the opposite sense from `LightfallSwordPower`'s "tallies" |
| `proto_mc_eula_glacial_illumination` | card | "Place a Lightfall Sword on the enemy. After 6 turns it deals 8 damage, plus 5 for each Attack you played meanwhile." | 115 | F4, F5 | Same "plus N" deviation as its own badge; "meanwhile" is an unusual word choice for this pool (no sibling card uses it) |
| `proto_mc_durin_binary_form` (noted, not new) | card | "Deal 6 damage to ALL enemies, then choose one for the combat. White: enemies take 50% more damage from Elemental Reactions. Dark: your Pyro Attacks that react deal 8 additional damage." (hole rendered as "6", per `lint_text_conventions.render()`; the live in-game number is higher) | 184 | F1 | Already a named, ruled exception in `tools/lint_text_conventions.py` ("a two-mode Power must print both modes on the reward screen"); listed here only for completeness of the companion-card census, not a new finding |

## Patterns

1. **"Plus N" / "N more" instead of the ruled "N additional damage."**
   `text-conventions.md` rule 8 fixes the base game's own spelling for a
   per-instance bonus ("Deals 3 additional damage for each card..."). Six
   rows in this pool independently drift to "plus N" or "N more" instead:
   `proto_mc_eula_glacial_illumination` + `LightfallSwordPower`,
   `proto_mi_ayaka_soumetsu` + `SoumetsuPower`,
   `proto_mi_yae_sesshou_sakura` + `SesshouSakuraPower`. Each pair (card and
   its own power badge) is internally consistent, which suggests one author
   wrote all three together rather than three independent slips — worth a
   single find-and-replace pass rather than three separate edits.

2. **"Swirl" spelled as a restated sentence instead of the pool's verb.**
   Every `proto_mc_`/`proto_mi_` card that Swirls uses the verb directly
   ("Swirl the enemy.", "Swirl ALL enemies.", bare "Swirl." on two Personals)
   and leaves the mechanics to the `Swirl` keyword tip. The two shipped
   Fontaine Lynette cards instead write out what Swirl does in the card body
   ("Swirl an enemy's aura onto ALL enemies"), which is both longer and a
   near-verbatim restatement of the tip beside it.

3. **One word, two jobs.** "Counts" means "is worth N per instance" on
   `proto_mi_heizou_heartstopper` and "tallies a running total" on
   `LightfallSwordPower`. Both are companion-kit rows a player can hold in
   the same run; the same verb doing two unrelated jobs is the kind of
   thing that reads as a typo on the one it isn't.

4. **A semicolon outside an either/or.** `SoumetsuPower.description` joins
   "N turns left" and "on the last, N more" with a semicolon.
   `text-conventions.md` rule 14 reserves the semicolon for either/or halves;
   this is a plain sequential pair and reads naturally as two sentences.

5. **Terse, unglossed shorthand on one badge only.** `SesshouSakuraPower`
   ends "...plus 3 after the first. 3 out." — "3 out" has no antecedent on
   the badge itself (the card face's "up to 3" is what makes it legible).
   No sibling companion power badge in the sample compresses its own count
   this far; `LightfallSwordPower`'s "Falls in 6 turns." is the same kind of
   fact spelled in full.

6. **Upgrade draw-clause placement is unruled.** `proto_mc_albedo_solar_isotoma`
   and `proto_mc_fischl_oz` put `{IfUpgraded:show:Draw 1 card. |}` at the
   FRONT of the sentence; `proto_mc_amber_explosive_puppet`,
   `proto_mc_dahlia_sacramental_shower`, `proto_mi_heizou_heartstopper` and
   `proto_mi_yae_sesshou_sakura` put the same clause at the END. All six grant
   the identical upgrade effect ("Draw 1 card"); nothing in the sheet or the
   codegen appears to decide which end it goes on. Minor, but worth a single
   rule if a new row is added.

## Clean

**72 `proto_mc_`/`proto_mi_` card faces, 68 clean** (all of the census below
minus the 4 flagged above): `proto_mc_albedo_solar_isotoma`,
`proto_mc_albedo_tectonic_tide`, `proto_mc_amber_explosive_puppet`,
`proto_mc_amber_fiery_rain`, `proto_mc_barbara_front_row_seat`,
`proto_mc_barbara_melody_loop`, `proto_mc_barbara_show_begin`,
`proto_mc_bennett_fantastic_voyage`, `proto_mc_bennett_passion_overload`,
`proto_mc_dahlia_favonian_favor`, `proto_mc_dahlia_sacramental_shower`,
`proto_mc_diona_icy_paws`, `proto_mc_diona_shaken_not_purred`,
`proto_mc_diona_signature_mix`, `proto_mc_fischl_nightrider`,
`proto_mc_fischl_oz`, `proto_mc_fischl_sinful_hex`,
`proto_mc_jean_dandelion_breeze`, `proto_mc_jean_gale_blade`,
`proto_mc_jean_lions_fang`, `proto_mc_kaeya_cold_blooded_strike`,
`proto_mc_kaeya_frostgnaw`, `proto_mc_kaeya_glacial_waltz`,
`proto_mc_lisa_lightning_rose`, `proto_mc_lisa_violet_arc`,
`proto_mc_mika_starfrost_swirl`, `proto_mc_mona_stellaris_phantasm`,
`proto_mc_nicole_ladder_of_ascent`, `proto_mc_nicole_revelation`,
`proto_mc_noelle_breastplate`, `proto_mc_noelle_i_got_your_back`,
`proto_mc_noelle_sweeping_time`, `proto_mc_prune_hexhunter_chime`,
`proto_mc_qiqi_herald_of_frost`, `proto_mc_razor_claw_and_thunder`,
`proto_mc_razor_lightning_fang`, `proto_mc_rosaria_ravaging_confession`,
`proto_mc_sayu_silencers_secret`, `proto_mc_sucrose_astable`,
`proto_mc_sucrose_catalyst_conversion`, `proto_mc_sucrose_gust`,
`proto_mc_sucrose_mollis_favonius`, `proto_mc_varka_sturm_und_drang`,
`proto_mc_venti_grand_ode`, `proto_mc_yaoyao_yuegui_throwing_mode`,
`proto_mi_ayato_kyouka`, `proto_mi_chiori_hasode`,
`proto_mi_gorou_crystal_collapse`, `proto_mi_gorou_inuzaka`,
`proto_mi_gorou_juuga`, `proto_mi_gorou_war_banner`,
`proto_mi_itto_superlative_superstrength`, `proto_mi_kazuha_slash`,
`proto_mi_kirara_surprise_dispatch`, `proto_mi_mizuki_anraku`,
`proto_mi_raiden_musou_no_hitotachi`, `proto_mi_sara_crowfeather_cover`,
`proto_mi_sara_tengu_stormcall`, `proto_mi_sayu_daruma`,
`proto_mi_sayu_fuuin_dash`, `proto_mi_sayu_naptime`,
`proto_mi_shinobu_grass_ring`, `proto_mi_shinobu_sanctifying_ring`,
`proto_mi_shinobu_thundergrust`, `proto_mi_thoma_blazing_barrier`,
`proto_mi_thoma_crimson_ooyoroi`, `proto_mi_yoimiya_aurous_blaze`.
(`proto_mc_durin_binary_form` sits outside this clean count — see the
flagged table; its 2 mode faces are themselves clean, under their own
ceiling.)

**19 shipped Fontaine card faces, 17 clean** (all offered under the arm
since `CompanionOverhaulRoster` only replaces Mondstadt/Inazuma):
`chevreuse_interdiction_fire`, `chevreuse_vanguards_valor`,
`chevreuse_bursting_grenades`, `lynette_box_trick`,
`charlotte_freezing_point`, `charlotte_enduring_frosthelm`,
`charlotte_snappy_silhouette`, `freminet_pers_deploy`,
`freminet_pressurized_floe`, `freminet_shattering_pressure`,
`navia_cannon_fire_support`, `clorinde_impale_the_night`,
`neuvillette_ancient_sea_authority`, `arlecchino_masque_red_death`,
`guest_neuvillette_tears`, `guest_neuvillette_droplets`,
`guest_neuvillette_judgment`.

**20 companion-attached keyword/reaction tips, all clean:**
`ArmKeywordTips.SwirlKey` (77 of 135), `ArmKeywordTips.CovenSparkKey` (119
of 135, and note it prints nothing at all while `KleeOverhaul.Enabled`),
`ArmKeywordTips.GroundedKey` (124), `ArmKeywordTips.OzKey` (127),
`ArmKeywordTips.MendKey` (65); the six Applies-Element tips
(`KLEEMOD-APPLIES_PYRO/HYDRO/ELECTRO/CRYO` at 94, `ANEMO`/`GEO` at 114); the
nine reaction-preview tips (`VAPORIZE_PREVIEW` 67, `MELT_PREVIEW` 67,
`OVERLOAD_PREVIEW` 76, `SUPERCONDUCT_PREVIEW` 88, `ELECTRO_CHARGED_PREVIEW`
118, `FROZEN_PREVIEW` 120, `FROZEN_BOSS_PREVIEW` 86, `SWIRL_PREVIEW` 70,
`CRYSTALLIZE_PREVIEW` 86 — all rendered lengths against the 135 tip
ceiling).

**4 companion-attached tips carried, not re-flagged:** `ArmKeywordTips.BombKey`,
`SetOffKey`, `MineKey`, `PlanKey` are each already over the 135 tip ceiling
and already named, individually, in `tools/lint_text_conventions.py`'s
`EXCEPTIONS` with their own multi-paragraph ruled rationale (R248 and
several seat-read findings each); re-litigating them here would just repeat
work already decided. They attach to `proto_mc_barbara_front_row_seat`,
`proto_mc_jean_lions_fang`, `proto_mc_diona_shaken_not_purred`,
`proto_mc_yaoyao_yuegui_throwing_mode`, `proto_mc_prune_hexhunter_chime`,
`proto_mc_sayu_silencers_secret`, `proto_mc_noelle_i_got_your_back` (Bomb/
Mine), `proto_mc_kaeya_cold_blooded_strike` (Grounded + Set off), and
`proto_mi_gorou_crystal_collapse` (Plan).

**Out of scope, checked and excluded:** the `Burst Energy` keyword tip
(`KleeCardTooltips.BurstKey`, 374 rendered characters — itself a large,
unflagged-by-the-lint over-ceiling rules essay) does not attach to any
`proto_mc_`/`proto_mi_` companion card in this build (only to Klee's/
Kokomi's/Furina's own cards, e.g. `Pop.cs`, `SparksNSplash.cs`,
`CeremonialGarment.cs`, `LetThePeopleRejoice.cs`), so it is out of this
pass's surface and not counted above.
