# tools/ index

Generated from each script's module docstring (its first sentence); regenerate
after adding, deleting or re-describing a script. What runs each lint: `tools/run_lints.py`
(lanes) and `klee-mod/build/validate.ps1` (deploy gates). A grep cannot see a script
someone types by hand, so an unreferenced script here is not necessarily dead.

| script | what it does |
|---|---|
| `agent_worktree.py` | Open a sibling worktree for one workstream, and print what to read in it. |
| `art_contact_sheet.py` | Emit an art contact sheet — shortlist candidates, click to select. |
| `art_coverage.py` | Card-art coverage check, ROSTER-WIDE (docs/furina-art-pass-requirements.md §9.5). |
| `art_fetch.py` | Fetch wiki-hosted official art per art/plan.tsv (docs/art-sprint-spec.md §2). |
| `art_hunt.py` | Discover REAL wiki file titles for an art hunt (furina-art-pass-requirements 9.2). |
| `art_ledger.py` | Art coverage + provenance LEDGER, joined across every expected visual surface. |
| `art_lint.py` | Plan lint for art/plan.tsv (docs/archive/art-taste-pass.md process directives 3-4). |
| `art_process.py` | Process art/raw/ into ImageGen targets per art/plan.tsv (spec §2 step 3). |
| `art_source_census.py` | Recount a character's art source census: sources, (source, anchor) SLOTS, deficit. |
| `backup_game_assemblies.py` | EB-172: keep a copy of the PINNED managed assemblies where Steam cannot reach it. |
| `backup_game_ref.py` | Mirror the primary checkout's `game_ref/` into the OneDrive vault. |
| `build_ironclad_sheet.py` | Thin Ironclad entry point for tools/build_official_sheet.py. |
| `build_official_sheet.py` | Build the loader-shaped real_<character> artifacts from local inputs. |
| `canon_role_tempo.py` | The canon role x tempo baseline, read STRUCTURALLY out of the local dll. |
| `card_connectivity_report.py` | EB-118 — the card CONNECTIVITY instrument. |
| `card_distinctness_report.py` | Quantify card-pool DISTINCTNESS -- the "interestingness" instrument. |
| `char_stills.py` | Shared framing math for the per-character still surfaces. |
| `ci_changed_paths.py` | Classify a CI diff: is this change docs-only, or does it need the full suite? |
| `ci_shards.py` | Split the CI test suite into N shards by file, balanced by measured time. |
| `colorless_census.py` | Census the base game's COLORLESS card pool from the local sts2.dll. |
| `cut_combat_layers.py` | Cut a character render into animated combat-model layers. |
| `cut_guest_bodies.py` | Cut the Guest Stars' stage bodies. |
| `cut_kurage_summon.py` | Cut the Bake-Kurage out of the summon art as a field entity sprite. |
| `cut_salon_members.py` | Cut the three Salon members out of the summon art as stage mini-sprites. |
| `deploy_round.py` | Decide and drive one round's deploy: pck if it is stale, the deploy, verify. |
| `dump_claimed_sources.py` | Dump the art source claim map -> docs/art-claimed-sources.tsv. |
| `effect_walk.py` | The shared sheet-effect walk for `tools/` (S1 sweep lint L4). |
| `extract_base_game_pool.py` | Extract a base-game character's card pool from the local sts2.dll. |
| `gates.py` | Run the gates and print ONE LINE EACH. |
| `gen_act_placeholders.py` | Placeholder-but-complete act asset sets for the six Teyvat act dressings. |
| `gen_char_icon_outlines.py` | Generate the top-panel character-icon OUTLINE textures (derived, procedural). |
| `gen_energy_orb_layers.py` | EB-88: candidate Hydro orb LAYER SETS for Furina's energy counter. |
| `gen_furina_stills.py` | Re-derive Furina's still surfaces from the governing render. |
| `gen_keyword_loc.py` | One source for the custom-keyword loc rows: the C#. |
| `gen_klee_cards.py` | Emit C# card classes from canonical character YAML design sheets. |
| `gen_kokomi_stills.py` | Re-derive Kokomi's still surfaces from the governing render. |
| `gen_meter_glyphs.py` | Generate the METER COST BADGE glyphs for Encore and Charge (Tier O, procedural). |
| `gen_mod_image.py` | Generate the Mods-screen identity badge, res://klee/mod_image.png (EB-161). |
| `gen_multiplayer_hands.py` | Generate the multiplayer treasure-room hands for Klee, Furina, Kokomi and Varka. |
| `gen_prototype_cards.py` | DEV-ONLY codegen for the prototype surface (R213 B, EB-147). |
| `gen_salon_glyphs.py` | Generate the Salon role-chip glyphs (Tier O, procedural). |
| `gen_teyvat_ancients.py` | Generate the Teyvat arm's DRESSED ANCIENTS from `ancient-faces.tsv`. |
| `gen_teyvat_creature_scenes.py` | Generate the Teyvat arm's STILL ENEMY BODIES from one table (`EB-811`). |
| `gen_teyvat_events.py` | Generate the Teyvat arm's DRESSED EVENTS from the curated event faces. |
| `gen_transition_wipe.py` | Generate the character-select transition wipe textures (Tier O, procedural). |
| `gen_varka_stills.py` | Derive Varka's still surfaces from his governing render. |
| `godot_log_sweep.py` | EB-154: sweep a headless MegaDot log for the failures its exit code hides. |
| `kokomi_expansion_sim.py` | KOKOMI EXPANSION, BATCH ONE -- the paper's sec.5 sim (exploration, not quotable, R215 B). |
| `land_pr.py` | Land a PR that asks nothing of [USER]: check CI, merge, purge the worktree, fast-forward. |
| `lint_ancient_coverage.py` | Every visible roster character must ship >= 1 Ancient-rarity pool card. |
| `lint_arm_pool_parity.py` | A prototype arm's OFFER roster must be the arm's sheet rows, in both engines. |
| `lint_companion_shop_coverage.py` | The companion roster must be able to fill BOTH shop slots, always. |
| `lint_conflict_markers.py` | A tracked file carrying a git conflict marker is never right. |
| `lint_constant_parity.py` | Parity lint: C# mirrored constants vs tier0, the single source of truth. |
| `lint_effect_branch_scans.py` | L4: nothing may read a card's `effects` as a flat list by accident. |
| `lint_element_text.py` | Every prototype face that applies an element NAMES it. |
| `lint_enchant_parity.py` | Parity lint: tier0's enchantment vocabulary vs what the mod's cards allow. |
| `lint_face_defects.py` | EB-169: the funnel's open-face-defect register may not go stale. |
| `lint_face_scaling.py` | A card face states a scaling EXACTLY ONCE. |
| `lint_furina_registers.py` | Register lint for the Furina pool (Curtain Call sweep, R85 / sprint §3+§5E). |
| `lint_game_assemblies_backup.py` | Tripwire: is the pinned-assembly vault present, complete and honest? |
| `lint_game_ref_backup.py` | Tripwire: is the OneDrive vault a current mirror of local `game_ref/`? |
| `lint_generated_structure.py` | Structural gate on the GENERATED C# cards. |
| `lint_handwritten_parity.py` | Parity lint: hand-written C# cards vs the ratified sheets. |
| `lint_keyword_meters.py` | Every face that names a METER must carry that meter's keyword tip, and every face that names a RESOURCE must print it as a keyword. |
| `lint_op_parity.py` | Parity lint: the engine's OPS registry vs the drafter's priced-op set. |
| `lint_pool_membership.py` | Every card class must belong to a card pool. |
| `lint_power_icons.py` | EB-153: every power this mod ships is either ICONED, EXEMPT, or NAMED DEBT. |
| `lint_prose_constants.py` | Prose lint: player-facing strings that HAND-TYPE a named balance constant. |
| `lint_prototype_authorship.py` | EB-190: recorded authorship on the prototype surface, and the grades it bans. |
| `lint_prototype_patch_scope.py` | EB-225 (R225 item 6, M66 pick 2): every prototype Harmony patch is character-scoped and seat-guarded. |
| `lint_prototype_titles.py` | No two rows on the prototype surface may print ONE TITLE. |
| `lint_recall_exhaust.py` | EB-118: the six constraints on exhaust-pile retrieval, swept. |
| `lint_register_isolation.py` | Nothing in the engine or the tier 0.5 model may READ a card's `register`. |
| `lint_roster_registry.py` | Every roster site knows every registered character. |
| `lint_run_name_clashes.py` | No two cards one run can hold may differ only in punctuation. |
| `lint_sheet_comment_blocks.py` | The sheet comment diet: a card sheet is rows, not an essay. |
| `lint_sly_grammar.py` | Parity lint: ONE Sly grammar, on both sides of the C# wall (EB-71, R174). |
| `lint_stamp_rows.py` | Correction D: STATE.md's live-cell rows are STAMPS, and a stamp is short. |
| `lint_text_conventions.py` | Player-facing TEXT against `docs/current/text-conventions.md`. |
| `lint_text_encoding.py` | Every text read/write must declare its encoding. |
| `lint_unique_names.py` | Player-facing display-name uniqueness lint. |
| `lint_upgrade_comment_arithmetic.py` | L7: the `# a -> b` arithmetic on an upgrade row must still be true. |
| `lint_upgrade_coverage.py` | G-C1: every draftable card can be upgraded, in the sim AND in the game. |
| `lint_upgrade_suffix_appends.py` | Every `<id> + upgrades.SUFFIX` site declares how it survives an ENCHANTED id. |
| `lint_vendor_pin.py` | Vendored third-party source has not drifted off its pin. |
| `local_model_sanity.py` | Is the local model any use as a playtester? |
| `module_map.py` | module_map -- a def-level map of a Python module, for orientation without a read. |
| `open_pr.py` | Open a pull request with the mandatory footer, and print the number and URL. |
| `patch_sentinel.py` | Patch sentinel: does the CURRENT sts2.dll still agree with our baselines? |
| `payoff_census.py` | The canonical PAYOFF CENSUS -- R137 step (2a), BACKLOG `EB-56`. |
| `prototype_card_read.py` | PER-CARD READ of a quarantined prototype arm, from the tier-0.5 sim. |
| `purge_worktree.py` | Remove a git worktree, and REFUSE if it is holding gitignored data. |
| `real_battery_calibration.py` | Run real, boss-reaching Act-1 builds through the frozen Tier-0 battery. |
| `realistic_axis_scores.py` | The 7-axis scorecard measured IN REALISTIC RUNS -- everything ON. |
| `regret_distribution.py` | The REGRET DISTRIBUTION PRINTER -- BACKLOG `EB-72` leg (1), QUEUE `M13`. |
| `render_card_gallery.py` | Render every card -- numbers AND art -- into one self-contained HTML page. |
| `role_tempo.py` | The role x tempo taxonomy: vocabulary, classifiers, and the tag-through. |
| `run_lints.py` | Run the repo's lint battery CONCURRENTLY and report every result. |
| `seat.py` | One blind seat, end to end: embark the lane, play the run, tear the lane down. |
| `shipped_card_art.py` | The shipped card-image set: the one list deploy stages into images/cards. |
| `telemetry_report.py` | The Balance telemetry report: per-fight medians by character, act and kind. |
| `track_b_curves.py` | Track B's demand (B1) and output (B2) curves, from both feeds. |
| `varka_expansion_sim.py` | VARKA EXPANSION -- the paper's sec.5 sim (Prototype stage, exploration, not a Balance measurement). |
| `build_pck.ps1` | Build klee.pck from ImageGen art with the MegaDot editor. |

## Directories

- `animation_bakeoff/`
- `combat_layer_fences/`
- `data/`
- `hooks/`
- `probe_spine_pck/` (see its README)
- `skeleton2d_spike/` (see its README)
- `visual_qa/` (see its README)
