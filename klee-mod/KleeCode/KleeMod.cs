using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves.Managers;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Mod entry point. The game looks for a class carrying [ModInitializer] and
/// invokes the named method during ModManager initialization.
/// </summary>
[ModInitializer(nameof(Initialize))]
public static class KleeMod
{
    public const string ModId = "klee";

    public static void Initialize()
    {
        Log.Info($"[{ModId}] Initializing Teyvat Spire roster...");

        // F2: per-type patching, NOT harmony.PatchAll. PatchAll aborts the
        // whole walk on the first patch class that throws, so one dead
        // reflection lookup silently disarms every patch after it -- including
        // the two shop/reward softlock guards below. KleePatchBootstrap applies
        // each class in its own try/catch and names any casualty at boot.
        KleePatchBootstrap.ApplyAll(new Harmony(ModId), typeof(KleeMod).Assembly);

        // The game already merged klee.pck (has_pck) before invoking us; this
        // logs proof-of-merge so a stale/missing pack shows up in godot.log.
        KleePck.LogStatus();

        // THE TEYVAT RUN FRAME ARM's still portraits (spike item 3,
        // -p:TeyvatFrame=true). A no-op with the arm off, one dictionary write
        // per dressed body with it on.
        //
        // THIS one belongs at [ModInitializer] and the arm's loc merge did NOT
        // (EB-759, one commit back): registering a scene for auto-conversion
        // writes into a registry BaseLib owns from the moment it loads — and
        // BaseLib is a manifest dependency, so it loads before us — and it
        // only has to be in place before the scene is INSTANTIATED, which is
        // first combat at the earliest. No table has to exist for it to be
        // correct. Teyvat/TeyvatVisuals.cs carries the argument in full.
        Teyvat.TeyvatVisuals.RegisterStillPortraits();

        // The same mechanism, a second type: the two act-1 dressings' own
        // combat-background ROOTS. `NCombatBackground.Create` casts the
        // instantiated scene, our root is a script-less Control, and BaseLib
        // ships no factory for that type — so this builds the missing factory
        // and registers the two scenes. It also logs, per dressing, whether the
        // dressed asset set reached the pck, which is the one thing that
        // decides whether the get_FilePathIdentifier alias still fires.
        Teyvat.TeyvatActAssets.RegisterActBackgrounds();

        // Convention-scene + build-id telemetry (animation sprint 1, A3 —
        // permanent). One line per shipped scene: path, found/missing, root
        // node type. A missing scene falls back quietly at the use site, so
        // this is where the miss gets loud.
        Diagnostics.KleeSceneTelemetry.LogStatus();

        // Aura application (R23): a standing combat-hook listener, registered
        // through the game's own mod-subscriber API. Elemental card hits apply
        // auras; AuraPower handles everything after that. See ElementalApplication.cs.
        // ModHelper keys subscriptions by id and silently rejects a duplicate.
        // Keep the roster behind ONE delegate so every character hook is live.
        ModHelper.SubscribeForCombatStateHooks(
            ModId,
            combatState =>
                Powers.KleeElementalHooks.Subscribe(combatState)
                    .Concat(Powers.FurinaResourceHooks.Subscribe(combatState))
                    .Concat(Powers.KokomiResourceHooks.Subscribe(combatState))
                    // EB-19/races-a + races-c: the four end-of-turn tenants
                    // that share the player's Block and the enemy reaction
                    // board no longer each override BeforeSideTurnEnd. This
                    // one listener drives them in the sim's fixed order.
                    .Concat(Powers.TurnEndSequencer.Subscribe(combatState))
                    // QUARANTINED (R213 B). The Mondstadt companion overhaul's
                    // own end-of-turn tenant, on the same argument one line up:
                    // six of its powers fire at the end of the player's turn,
                    // four of the six put an element on the board and five draw
                    // from Rng.CombatTargets, so they get ONE listener in a
                    // fixed order. Not compiled at all in a release build, and
                    // inert with the arm off -- the powers it drives can only
                    // reach a creature that played an overhaul card, and with
                    // the arm off no such card is offerable.
                    .Concat(Powers.CompanionOverhaulTurnEnd.Subscribe(combatState))
                    // The same arm's SECOND WAVE, on the same argument again.
                    // Three of its powers answer an enemy's hit and two of the
                    // three can kill the attacker and put an element on the
                    // board, so they get ONE listener in a fixed order. The
                    // play watcher counts Attacks for two cards that can be in
                    // a deck while no power of this arm is on anybody -- one of
                    // them lives on the ENEMY -- which is why it cannot be a
                    // power. Both are inert on a board carrying none of the
                    // arm's rows, which is every board with the arm off.
                    .Concat(Powers.CompanionOverhaulIncomingHit.Subscribe(combatState))
                    .Concat(Powers.CompanionOverhaulPlayWatcher.Subscribe(combatState))
                    // EB-279. The Klee overhaul's rule-3 sweep, on the same
                    // argument as the three lines above: the two moments a
                    // Bomb can be orphaned that the arm itself does not cause
                    // -- any creature's death, and any card play -- are
                    // BROADCAST hooks, and a power on the dying enemy cannot
                    // hear either of them. Not compiled in a release build,
                    // and inert with the arm off: with no proto Bomb on any
                    // board the register is empty and the sweep is a walk over
                    // nothing. See KleeOverhaulSweep.cs for why AfterDeath is
                    // trustworthy where the enemy's own hooks are not.
                    .Concat(Powers.KleeOverhaulSweepHooks.Subscribe(combatState))
                    // THE FURINA STAGE'S TWO CLOCKS, on the same argument as
                    // the four lines above: the lead's regen at her turn start
                    // and the performers' acts at her turn end are BROADCAST
                    // moments, and the stage is a ledger rather than a power,
                    // so nothing on the board can hear them for it. LAST in
                    // the concat, which is the ordering: the shipped
                    // end-of-turn tenants are what her docket accounts for,
                    // and an act resolving before them would move a number the
                    // docket had already drawn. Not compiled in a release
                    // build, and inert with the arm off -- every method's
                    // first line is `FurinaStage.LiveFor`.
                    .Concat(Powers.FurinaStageHooks.Subscribe(combatState))
                    // Track B's human feed: per-fight telemetry from normal
                    // play, in the schema the soak writes. Reads only -- see
                    // the three rules in PlayTelemetry.cs, the first of which
                    // is that a measurement must never desync a co-op table.
                    .Concat(Diagnostics.PlayTelemetryHooks.Subscribe(combatState)));

        Log.Info($"[{ModId}] Klee, Furina and Kokomi registered"
                 + ", and Varka (prototype)"
                 + ".");
    }

    /// <summary>English strings for the character and the four starter stubs.</summary>
    internal static void InjectLocStrings()
    {
        try
        {
            // Keys are ModelId.Entry, which is UPPER_SNAKE_CASE derived from the
            // class name (DuckAndCover -> DUCK_AND_COVER), NOT lowercase.
            // CardModel.Description reads "cards" -> "<ENTRY>.description".
            LocManager.Instance.GetTable("cards").MergeWith(new Dictionary<string, string>
            {
                // Two separate syntaxes are in play here, and both bit us:
                //
                // 1. Values are SmartFormat templates over DynamicVarSet, whose
                //    keys are "Damage" / "Block" (see BlockVar.defaultName).
                //    SmartFormat uses SINGLE braces - "{{Damage}}" is not a
                //    placeholder and is emitted literally.
                //
                // 2. Square brackets are BBCode, NOT keyword markup. The game
                //    wraps descriptions in [center]...[/center], so a stray
                //    "[Block]" parses as an unclosed tag and throws
                //    "Found end tag center, expected Block". Custom keyword
                //    ids are allocated by BaseLib from KleeKeywords; their
                //    strings ship in the pck's card_keywords loc table.
                // ONLY plain CardModel stubs belong here. Cards that derive from
                // BaseLib's CustomCardModel get a prefixed id (KLEEMOD-KABOOM),
                // so they declare loc via an ILocalizationProvider.Localization
                // override on the model instead -- see Kaboom.Localization.
                // KleeSelfCheck.Run() enforces that split at boot.
                ["JUMPY_DUMPTY.title"] = "Jumpy Dumpty",
                ["JUMPY_DUMPTY.description"] = "Deal {Damage:diff()} damage twice.",

                // Pop is now a CustomCardModel and declares its own loc.

                // EB-122: the three SELECTION-SCREEN prompts, ruled copy
                // 2026-08-25. Not card rows and not an exception to the split
                // above -- `<ENTRY>.selectionScreenPrompt` in the `cards`
                // table is the base game's own shape for this screen
                // (HAND_TRICK's and HEADBUTT's rows are exactly these two
                // verbs), and a LocString is a table plus a key with no
                // raw-text constructor, so ruled copy can only reach the
                // screen as a row. They are keyed on the VERB rather than on a
                // card id because one screen serves every carrier that prints
                // it -- the same "one member, one string" discipline the three
                // Prompt properties were written with. The pck carries no copy
                // of these, so this dictionary is their only source and a
                // missing entry is directly player-visible as a raw key.
                [Powers.SlyGrant.PromptKey] = Powers.SlyGrant.PromptText,
                [Powers.RecallFromDiscard.PromptKey] =
                    Powers.RecallFromDiscard.PromptText,
                [Powers.RecallFromExhaust.PromptKey] =
                    Powers.RecallFromExhaust.PromptText,
                // `EB-655`. The `scry_bottom` screen, on the same terms: one
                // verb, one ruled string, and this dictionary is its only
                // source. OUTSIDE the compile switch below, because the op is
                // a sheet verb any character may print and not a prototype
                // rule.
                [Powers.ScryBottom.PromptKey] = Powers.ScryBottom.PromptText,
                // `EB-679`. The `scry_take` screen -- the same verb one door
                // over, with the pick coming to hand instead of going to the
                // bottom. Outside the compile switch for the row above's
                // reason: a sheet verb, not a prototype rule.
                [Powers.ScryTake.PromptKey] = Powers.ScryTake.PromptText,
                // QUARANTINED (the Kokomi overhaul, draft 6). Moon's
                // Reflection's exhaust-pile screen, on exactly the terms the three rows
                // above have: a LocString is a table plus a key with no
                // raw-text constructor, so the copy can only reach the screen
                // as a row, and this dictionary is its only source. Inside the
                // compile switch because the verb it names does not exist in a
                // release build.
                [Powers.KokomiPlan.ReflectionPromptKey] =
                    Powers.KokomiPlan.ReflectionPromptText,
                // THE STATUS BATCH (2026-10-01): Tidecleanse's and Turning
                // Tide's hand screens, on the same terms.
                [Powers.KokomiStatusBatch.ExhaustPromptKey] =
                    Powers.KokomiStatusBatch.ExhaustPromptText,
                [Powers.KokomiStatusBatch.DiscardPromptKey] =
                    Powers.KokomiStatusBatch.DiscardPromptText,
                // R276, the Klee pool expansion's two discard-pile picks
                // (Treasure Map, Come Back and Play!), on the same terms.
                [Powers.KleeExpansion.SetOffPromptKey] =
                    Powers.KleeExpansion.SetOffPromptText,
                [Powers.KleeExpansion.CompanionPromptKey] =
                    Powers.KleeExpansion.CompanionPromptText,
                // FURINA, THE POOL TO 75 (2026-10-09): Casting Call's draw
                // pile pick and Final Bow's guest pick, on the same terms.
                [Powers.FurinaCards.TutorPromptKey] =
                    Powers.FurinaCards.TutorPromptText,
                [Powers.FurinaCards.BowPromptKey] =
                    Powers.FurinaCards.BowPromptText,
                // VARKA (the Oath rework): Knights' Roll Call+'s grid and
                // Change of Guard's, on the same terms.
                [Powers.VarkaRules.KnightPromptKey] =
                    Powers.VarkaRules.KnightPromptText,
                [Powers.VarkaRules.ElementPromptKey] =
                    Powers.VarkaRules.ElementPromptText,
            });

            // Runtime copy of the custom-keyword loc. The pck carries the
            // same table for normal packaged builds, but keeping these rows in
            // the DLL makes a code-only playtest rebuild safe: newly generated
            // aura badges and combat-aware reaction tips never render raw keys
            // merely because the local art pack predates this code pass.
            //
            // EB-89: the numerals here are INTERPOLATED from the constants
            // they quote, never hand-typed. The pck's card_keywords.json wins
            // wherever it has a row (see the MergeWith below), so the two
            // copies still read identically today -- but a repricing must not
            // be able to leave the code-only playtest build telling a player a
            // retired number. The MULTIPLIERS (1.5x, 1.75x) stay literals on
            // purpose: they are floats, and interpolating a float renders it
            // under the host's culture, so a comma locale would print "1,5x".
            var keywordTable = LocManager.Instance.GetTable("card_keywords");
            var keywordFallback = new Dictionary<string, string>
                {
                    // `EB-345` / R249. The shared tips took the text pass.
                    // The Applies-X four said one rule in two long clauses
                    // and named no keyword; the eight reaction previews all
                    // opened with the same 60-character preamble about what
                    // the CARD supplies, which is the one thing a player
                    // reading the card already knows. Every tip now leads
                    // with the pair that reacts and then says what happens,
                    // keywords golded and numerals blue. No number, no
                    // constant and no rule moved -- the interpolations are
                    // the same interpolations.
                    ["KLEEMOD-APPLIES_PYRO.title"] = "Applies Pyro",
                    ["KLEEMOD-APPLIES_PYRO.description"] =
                        $"No aura: applies [gold]Pyro[/gold] for [blue]{Elements.ReactionConstants.AuraDurationTurns}[/blue] turns. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers.",
                    ["KLEEMOD-APPLIES_HYDRO.title"] = "Applies Hydro",
                    ["KLEEMOD-APPLIES_HYDRO.description"] =
                        $"No aura: applies [gold]Hydro[/gold] for [blue]{Elements.ReactionConstants.AuraDurationTurns}[/blue] turns. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers.",
                    ["KLEEMOD-APPLIES_ELECTRO.title"] = "Applies Electro",
                    ["KLEEMOD-APPLIES_ELECTRO.description"] =
                        $"No aura: applies [gold]Electro[/gold] for [blue]{Elements.ReactionConstants.AuraDurationTurns}[/blue] turns. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers.",
                    ["KLEEMOD-APPLIES_CRYO.title"] = "Applies Cryo",
                    ["KLEEMOD-APPLIES_CRYO.description"] =
                        $"No aura: applies [gold]Cryo[/gold] for [blue]{Elements.ReactionConstants.AuraDurationTurns}[/blue] turns. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers.",
                    // `EB-454`. The two that TRIGGER: a reaction happens and
                    // no aura is left, so the sentence is the four above with
                    // the duration clause replaced by the reason there is none.
                    ["KLEEMOD-APPLIES_ANEMO.title"] = "Applies Anemo",
                    ["KLEEMOD-APPLIES_ANEMO.description"] =
                        "No aura: nothing happens. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. [gold]Anemo[/gold] never stays on an enemy.",
                    ["KLEEMOD-APPLIES_GEO.title"] = "Applies Geo",
                    ["KLEEMOD-APPLIES_GEO.description"] =
                        "No aura: nothing happens. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. [gold]Geo[/gold] never stays on an enemy.",
                    ["KLEEMOD-CONFISCATED.title"] = "Confiscated",
                    ["KLEEMOD-CONFISCATED.description"] =
                        "A 1-cost Status card that does nothing.",
                    ["KLEEMOD-VAPORIZE_PREVIEW.title"] = "Reaction preview: Vaporize",
                    ["KLEEMOD-VAPORIZE_PREVIEW.description"] =
                        "[gold]Pyro[/gold] meets [gold]Hydro[/gold]: this hit deals 1.5x damage and consumes the aura.",
                    ["KLEEMOD-MELT_PREVIEW.title"] = "Reaction preview: Melt",
                    ["KLEEMOD-MELT_PREVIEW.description"] =
                        "[gold]Pyro[/gold] meets [gold]Cryo[/gold]: this hit deals 1.75x damage and consumes the aura.",
                    ["KLEEMOD-OVERLOAD_PREVIEW.title"] = "Reaction preview: Overloaded",
                    ["KLEEMOD-OVERLOAD_PREVIEW.description"] =
                        $"[gold]Pyro[/gold] meets [gold]Electro[/gold]: deals [blue]{Elements.ReactionConstants.OverloadSplash}[/blue] damage to ALL enemies and applies [blue]{Elements.ReactionConstants.OverloadWeak}[/blue] [gold]Weak[/gold] to the reacted enemy.",
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.title"] = "Reaction preview: Superconduct",
                    // `EB-472`. THE ORDER, because this is the one reaction whose debuff
                    // changes the number of the hit that caused it. `ElementalHit.Deal`
                    // resolves the reaction and only then reads
                    // `SimDamagePipeline.TargetMods`, so the Vulnerable it applies
                    // multiplies THIS hit -- pinned by
                    // `tier0/tests/test_reaction_phase_parity.py`, and worth 50% of a
                    // card the Klee r15 run-2 seat had to reverse-engineer out of the HP
                    // numbers ("that is a 4-point swing on a 1-cost card and it is
                    // nowhere on the screen"). The comment sits ABOVE the key: this row
                    // is scraped by `tools/gen_keyword_loc.py`, whose reader wants the
                    // string to follow the `=` directly.
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.description"] =
                        $"[gold]Electro[/gold] meets [gold]Cryo[/gold]: the reacted enemy gains [blue]{Elements.ReactionConstants.SuperconductVuln}[/blue] [gold]Vulnerable[/gold], which applies before this hit.",
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.title"] = "Reaction preview: Electro-Charged",
                    // `EB-665` (Klee r24 lane 1). THE PREVIEW NAMES THE DEBUFF
                    // THE BODY SHOWS. The dot IS the core's own PoisonPower
                    // (`ReactionEffects`, the ElectroCharged case), so the
                    // enemy's panel prints `Poison 4` while this sentence said
                    // only "loses 4 HP": the seat read a preview and a body
                    // that named two different things and could not tell which
                    // number was which. Text pass 2026-09-25: the tick clause
                    // left, because Poison's own tip (attached beside this one
                    // by `KleeCardTooltips.ForCard`) says how Poison ticks.
                    // The comment sits ABOVE the key, for
                    // `gen_keyword_loc.py`'s reader.
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.description"] =
                        $"[gold]Hydro[/gold] meets [gold]Electro[/gold]: the reacted enemy gains [blue]{Elements.ReactionConstants.ElectroChargedDot}[/blue] [gold]Poison[/gold].",
                    ["KLEEMOD-FROZEN_PREVIEW.title"] = "Reaction preview: Frozen",
                    // Text pass 2026-10-08: the boss sentence left this row,
                    // because `KleeCardTooltips` already swaps in the boss row
                    // below for any non-minion in a boss room
                    // (`ReactionEffects.FrozenBossVulnWillApply`), and a
                    // Shatter now says it ends the freeze (`FrozenPower`
                    // removes itself when it Shatters). The comment sits
                    // ABOVE the key, for `gen_keyword_loc.py`'s reader.
                    ["KLEEMOD-FROZEN_PREVIEW.description"] =
                        $"[gold]Hydro[/gold] meets [gold]Cryo[/gold]: its next action deals 50% less. Until it acts, an Attack on it Shatters for [blue]{Elements.ReactionConstants.ShatterDamage}[/blue] unblockable damage and ends the freeze.",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] = "Reaction preview: Frozen (Boss)",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.description"] =
                        $"[gold]Hydro[/gold] meets [gold]Cryo[/gold]: in a boss fight a non-minion can't be Frozen; it gains [blue]{Elements.ReactionConstants.FrozenBossVuln}[/blue] [gold]Vulnerable[/gold] instead.",
                    ["KLEEMOD-SWIRL_PREVIEW.title"] = "Reaction preview: Swirl",
                    // THE ELEMENT PORT (sec.4 A, 2026-09-28; spent removed
                    // 2026-10-03): Swirl removes the aura, deals a flat 2 to
                    // all and copies the element onto the others.
                    // The comment sits ABOVE the key, for `gen_keyword_loc.py`.
                    ["KLEEMOD-SWIRL_PREVIEW.description"] =
                        $"[gold]Anemo[/gold] meets an aura: remove it, deal [blue]{Elements.ReactionConstants.SwirlDamage}[/blue] unblockable damage to ALL enemies, and apply that element to the others.",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.title"] = "Reaction preview: Crystallize",
                    // `EB-613` (R263 sec.5 item 1). THE BLOCK IS NOT THE
                    // POINT OF THIS ROW; THE AURA IS. A Geo hit is a COST to
                    // a reaction deck -- it eats the standing aura for 4
                    // Block -- and the seats already sequence around it
                    // ("Gorou must come after the Electro hit or its
                    // Crystallize eats the aura the reaction needs", Kokomi r5
                    // run 3, under the heading "element ordering is the
                    // deepest decision this deck has, and it is entirely
                    // undocumented"). The old sentence named the consumption
                    // in a trailing subclause behind a gain. Text pass
                    // 2026-09-25: two short sentences, the gain and then the
                    // price, each with its own verb. The comment sits ABOVE
                    // the key, for `gen_keyword_loc.py`'s reader.
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.description"] =
                        $"[gold]Geo[/gold] meets an aura: gain [blue]{Elements.ReactionConstants.CrystallizeBlock}[/blue] [gold]Block[/gold]. The aura is removed.",

                    // `EB-160`. THE ONE PLAYER-FACING STRING BAKED INTO A
                    // SCENE. `shared/turn_end_docket.tscn`'s header node
                    // carried `text = "END OF TURN"` as scene data, which is
                    // in no loc table, reaches no translator and cannot
                    // follow a locale switch. It is a UI LABEL and not a
                    // keyword, so it takes a `.header` suffix rather than
                    // `.title`; it lives in this table for the reason the
                    // rider titles below do, which is that this is the mod's
                    // one merge point and a code-only rebuild must never show
                    // a raw key. A plain literal key, so `gen_keyword_loc.py`
                    // derives it into the pck copy the game merges over ours.
                    //
                    // The scene keeps the words as its FALLBACK: a docket
                    // built from a pack older than this row still reads
                    // correctly, because `TurnEndPreviewBridge` overwrites the
                    // node's text only where the row resolves to something.
                    ["KLEEMOD-TURN_END_DOCKET.header"] = "END OF TURN",

                    // EB-53/N1: the end-of-turn docket's per-slot hovers.
                    // TITLES only --
                    // every body is built live in TurnEndAttribution from the
                    // constants the resolution reads, so a repricing cannot
                    // leave a row quoting a retired number.
                    [Powers.TurnEndAttribution.MasqueKey + ".title"] =
                        "Bond of Life",

                    // `EB-272`. QUARANTINED, and inside the switch for the
                    // reason Rally's prompt is: `Cards/Prototype/**` is
                    // Compile Remove'd from a release build, so
                    // `Cards.ArmKeywordTips` does not exist there and these
                    // eleven keys name nothing. Under the switch they are the
                    // only source of the titles, exactly as the four rider
                    // rows above are -- the pck's card_keywords.json carries
                    // none of them, and a missing row renders as the raw key
                    // on a card face (0.2-589, 0.2-634).
                    //
                    // TITLES ONLY, the bargain every tip in this block makes:
                    // the bodies are built in ArmKeywordTips because two of
                    // them interpolate an arm's law constant and one of them
                    // reads which Klee arm is live.
                    //
                    // `KLEEMOD-BOMB`, the old shipped Bomb's keyword, left
                    // with the text pass of 2026-10-08: no card raised it.
                    [Cards.ArmKeywordTips.BombKey + ".title"] = "Bomb",
                    [Cards.ArmKeywordTips.SetOffKey + ".title"] = "Set off",
                    [Cards.ArmKeywordTips.SparkKey + ".title"] = "Spark",
                    [Cards.ArmKeywordTips.MineKey + ".title"] = "Mine",
                    // Klee's fifth, Hexerei, was retired by R276 pick 2.
                    // `EB-372`, Klee's sixth: a Power of hers that Kaeya's
                    // Cold-Blooded Strike is written against, so the word
                    // reaches a player who may never have drafted it.
                    [Cards.ArmKeywordTips.GroundedKey + ".title"] = "Grounded",
                    // `EB-446`, Klee's seventh: the raven ANOTHER companion
                    // card puts out, named on a face that cannot grant him.
                    [Cards.ArmKeywordTips.OzKey + ".title"] = "Oz",
                    // `EB-575`. The fourth rider here that titles no keyword,
                    // and the only one whose sentence comes and goes with the
                    // board: a Set off or a merge played with no Bomb on the
                    // field is accepted, charged for, and silent.
                    [Cards.ArmKeywordTips.EmptyFieldKey + ".title"] =
                        "No Bomb on the field",
                    // `EB-573`. The fifth rider here that titles no keyword:
                    // what a merge keeps besides the Mine, on the card that
                    // does the merging.
                    [Cards.ArmKeywordTips.MergeRidersKey + ".title"] =
                        "Riders survive the merge",
                    [Cards.ArmKeywordTips.MendKey + ".title"] = "Mend",
                    [Cards.ArmKeywordTips.PlanKey + ".title"] = "Plan",
                    // `EB-643` (R265): the pool pass's one new word, and it is
                    // a rule about WHEN -- the Bake-Kurage carries a Dusk Plan
                    // out at the end of the turn it was written on. Same
                    // raw-key hazard as every row here.
                    [Cards.ArmKeywordTips.DuskKey + ".title"] = "Dusk",
                    // `EB-625`: the relic behind Shell Guard's payout, on
                    // the face that names it. Same raw-key hazard as every
                    // row here.
                    [Cards.ArmKeywordTips.CasketKey + ".title"] =
                        "Tamakushi Casket",
                    // THE CASKET PASS (2026-09-28): the token the relic deals.
                    [Cards.ArmKeywordTips.OpenTheCasketKey + ".title"] =
                        "Open the Casket",
                    // `EB-378`. The rider, not a keyword: the rows whose Hydro
                    // arrives with the jellyfish's carry-out rather than with
                    // the play.
                    [Cards.ArmKeywordTips.PlanElementKey + ".title"] =
                        "Hydro on the carry-out",
                    // `EB-709`. The rider, not a keyword: how many Plans a
                    // doubled carry-out is, on the card that doubles it.
                    [Cards.ArmKeywordTips.PlanTwiceKey + ".title"] =
                        "Twice means two Plans",
                    // `EB-389`. The line a card grows while a rider overrides
                    // the element it prints. A title row, not a keyword: it is
                    // a fact about THIS card on THIS board, and it comes and
                    // goes with the buff.
                    [Cards.KleeCardTooltips.OverriddenElementKey + ".title"] =
                        "Element overridden",
                    [Cards.ArmKeywordTips.SwirlKey + ".title"] = "Swirl",
                    // 2026-09-25: the word Klee's readers and the other arms'
                    // Companion cards print. Same raw-key hazard as every row
                    // here.
                    [Cards.ArmKeywordTips.CompanionKey + ".title"] =
                        "Companion",
                    // VARKA (the Oath rework): his three words.
                    [Cards.ArmKeywordTips.OathKey + ".title"] = "Oath",
                    [Cards.ArmKeywordTips.CurrentElementKey + ".title"] =
                        "Current element",
                    [Cards.ArmKeywordTips.KnightKey + ".title"] = "Knight",
                    // Co-op notes pick 2 (2026-10-02): the key is also
                    // `KleeKeywords.Knight`'s, the printed "Knight." line,
                    // and the keyword's own hover reads this row.
                    [Cards.ArmKeywordTips.KnightKey + ".description"] =
                        Cards.ArmKeywordTips.KnightTipText,
                    // Element identities sec.7: a rider, titling no keyword.
                    [Cards.ArmKeywordTips.ElementSwitchKey + ".title"] =
                        "Element switch",
                    // FURINA, THE SALON'S TAB (2026-10-05): her four words,
                    // the summon, the Guest Star keyword and each guest
                    // titled by its own name (the ledger's, `EB-735`).
                    [Cards.ArmKeywordTips.SpendKey + ".title"] = "Spend",
                    [Cards.ArmKeywordTips.FanfareKey + ".title"] =
                        "Fanfare",
                    [Cards.ArmKeywordTips.DrainKey + ".title"] = "Drain",
                    [Cards.ArmKeywordTips.RepayKey + ".title"] = "Repay",
                    // The "Drained N" counter's hover title.
                    [Vfx.DrainedCounter.TitleKey + ".title"] = "Drained",
                    [Cards.ArmKeywordTips.SummonKey + ".title"] = "Summon",
                    // The text pass of 2026-10-08: three golded words that
                    // hovered nothing, and the Plan tip for a plan-only card.
                    [Cards.ArmKeywordTips.ElementalReactionKey + ".title"] =
                        "Elemental Reaction",
                    [Cards.ArmKeywordTips.SakuraKey + ".title"] = "Sakura",
                    [Cards.ArmKeywordTips.LightfallSwordKey + ".title"] =
                        "Lightfall Sword",
                    [Cards.ArmKeywordTips.PlanOnlyKey + ".title"] = "Plan",
                    [Cards.ArmKeywordTips.GuestStarKey + ".title"] =
                        "Guest Star",
                    [Cards.ArmKeywordTips.CharlotteKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Charlotte),
                    [Cards.ArmKeywordTips.WriothesleyKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Wriothesley),
                    [Cards.ArmKeywordTips.LynetteKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Lynette),
                    [Cards.ArmKeywordTips.ClorindeKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Clorinde),
                    [Cards.ArmKeywordTips.LyneyKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Lyney),
                    [Cards.ArmKeywordTips.SigewinneKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Sigewinne),
                    [Cards.ArmKeywordTips.ChevreuseKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Chevreuse),
                    // The pool to 75 (2026-10-09): Encore!'s "oldest
                    // guest", and its four guests.
                    [Cards.ArmKeywordTips.OldestGuestKey + ".title"] =
                        "Oldest guest",
                    [Cards.ArmKeywordTips.FreminetKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Freminet),
                    [Cards.ArmKeywordTips.NaviaKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Navia),
                    [Cards.ArmKeywordTips.NeuvilletteKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Neuvillette),
                    [Cards.ArmKeywordTips.EscoffierKey + ".title"] =
                        Powers.FurinaStageLedger.DisplayName(
                            Powers.StagePerformer.Escoffier),
                    // `EB-377`. The BASE game's five, restated on the face
                    // that names one. Same switch and same bargain as the
                    // eleven rows above -- titles here, bodies in
                    // `BaseKeywordTips` -- and the same non-collision: each
                    // title is the base game's own word, because it is the
                    // base game's own rule said where the card is.
                    [Cards.BaseKeywordTips.VulnerableKey + ".title"] =
                        "Vulnerable",
                    [Cards.BaseKeywordTips.WeakKey + ".title"] = "Weak",
                    [Cards.BaseKeywordTips.FrailKey + ".title"] = "Frail",
                    [Cards.BaseKeywordTips.StrengthKey + ".title"] =
                        "Strength",
                    [Cards.BaseKeywordTips.DexterityKey + ".title"] =
                        "Dexterity",
                    [Cards.BaseKeywordTips.VigorKey + ".title"] = "Vigor",
                };
            keywordTable.MergeWith(keywordFallback
                .Where(pair => !keywordTable.HasEntry(pair.Key))
                .ToDictionary(pair => pair.Key, pair => pair.Value));

            // `EB-481`, THE HALF THIS MOD DOES NOT OWN A KEYWORD FOR.
            //
            // The row was closed once on the tips and reopened on 2026-09-05,
            // because a tip is not where a player meets Vulnerable: the seat
            // met it on the ENEMY, whose status line is the base game's own
            // `VULNERABLE_POWER` row and reads "more damage from Attacks"
            // while `BaseKeywordTips.ForVulnerable` and the sim's glossary
            // read the engine's rule. Two texts disagreeing about whether a
            // Skill is safe is a player sequencing badly (Kokomi r16/r17),
            // and the box was the one telling the truth.
            //
            // A ROW AND NOT A PATCH, because a description is a table lookup:
            // the base game's own `powers` table is the only printer of that
            // line, so the only way to correct it is to carry a row. The keys
            // are the shipped ones, read off `SlayTheSpire2.pck` v0.111.0 --
            // "Vulnerable creatures take [blue]50%[/blue] more damage from
            // Attacks." and "Receive [blue]{DamageIncrease:percentMore()}%
            // [/blue] more damage from Attacks for [blue]{Amount}[/blue]
            // {Amount:plural:turn|turns}." -- so this is those two sentences
            // with one word moved, holes and BBCode untouched.
            //
            // THE ONE WORD IS "CARDS", and `EB-497` is why it is not "hits":
            // `VulnerablePower.ModifyDamageMultiplicative` gates on
            // `ValueProp.IsPoweredAttack()`, which every damage clause the
            // generator emits carries and a POTION's damage does not (a
            // Vulnerable Sewer Clam took 10 off Explosive Ampoule, not 15 --
            // Klee r17 lane 1). The sim says the same thing structurally:
            // `potions.fire_potion` goes through `refpowers.unpowered_damage`,
            // which never reaches `modify_damage_taken`.
            //
            // UNDER THE QUARANTINE, like the five keyword bodies above and for
            // the same reason: a release build does not police the base game's
            // English (`KleeSelfCheck` says so in as many words), and the
            // glossary these words have to agree with is itself arm-only.
            LocManager.Instance.GetTable("powers").MergeWith(
                new Dictionary<string, string>
                {
                    // `EB-523` PUT THE ATTACK BACK IN, and it is `EB-497`'s own
                    // correction meeting the side of the board that row did
                    // not read. "From cards" is complete on an ENEMY, where
                    // everything that hits is a card or a potion, and silent on
                    // the PLAYER, where the number that matters is a monster's
                    // swing: the Kokomi r18 lane-2 seat wore `Vulnerable 99 --
                    // Receive 50% more damage from cards for 99 turns` in front
                    // of a 24-damage intent and could not price it. "That is
                    // the single most decision-relevant number on the screen
                    // and I could not price it."
                    //
                    // AND IT DOES COUNT. `VulnerablePower` gates on
                    // `ValueProp.IsPoweredAttack()` -- a property of the HIT,
                    // and a monster's move carries it; the sim says the same
                    // structurally, `combat._enemy_attack` running every hit
                    // through `powers.modify_damage_taken(state.player, ...)`.
                    // So the sentence names both kinds of hit and keeps
                    // `EB-497`'s potion clause, which is the one thing that
                    // takes no multiplier on either engine.
                    ["VULNERABLE_POWER.description"] =
                        "Vulnerable creatures take [blue]50%[/blue] more "
                      + "damage from any attack or card hit, a potion's aside.",
                    ["VULNERABLE_POWER.smartDescription"] =
                        "Receive [blue]{DamageIncrease:percentMore()}%[/blue] "
                      + "more damage from any attack or card hit for "
                      + "[blue]{Amount}[/blue] {Amount:plural:turn|turns}.",

                    // `EB-521`, AND IT IS THE THIRD ROUND OF ONE FINDING.
                    //
                    // Kokomi r18 lane 2, fight 1: "Thorns printed 'When hit by
                    // an attack, deal 2 damage back'. I played Kurage's Oath --
                    // a SKILL -- into a Thorns-2 body and lost 2 HP ...
                    // Vulnerable and Weak both print the clause 'a Skill's
                    // damage too'; Thorns does not, and behaves as though it
                    // did."
                    //
                    // THE ENGINE IS RIGHT AND ONLY THE WORDS ARE WRONG, which
                    // is `EB-469`'s and `EB-481`'s sentence for the third time.
                    // `ThornsPower.BeforeDamageReceived` asks for a dealer and
                    // a POWERED attack and nothing else -- it never looks at
                    // the `DamageResult`, which is why a fully blocked hit is
                    // still thorned (`tier0/engine/refpowers.py`, written off
                    // the decompile, and `test_si_powers`' two pins). A powered
                    // attack is a property of the HIT, and every damage clause
                    // the generator emits carries `ValueProp.Move` whatever
                    // `type:` its sheet row declares. So "an attack" in the
                    // game's sentence means an attack HIT, exactly as it does
                    // in Weak's and Vulnerable's, and a potion's damage --
                    // Unpowered on both engines -- is not one.
                    ["THORNS_POWER.description"] =
                        "When hit by an attack, deal your [gold]Thorns[/gold] "
                      + "damage back. Every card hit is one, a Skill's too; a "
                      + "potion's is not.",
                    ["THORNS_POWER.smartDescription"] =
                        "When hit by an attack, deal [blue]{Amount}[/blue] "
                      + "damage back. Every card hit is one, a Skill's too; a "
                      + "potion's is not.",

                    // `EB-597`, AND IT IS THE SAME FINDING A FOURTH TIME.
                    //
                    // Kokomi r22 lane 1, fight 2: "Shrink's own text says
                    // `your Attacks deal 30% less damage`, but Kurage's Oath
                    // is printed `cost 1, skill` and it still fell 3 to 2.
                    // Weak's glossary on the same screen goes out of its way
                    // to say 'a Skill's damage too'; Shrink's does not, and
                    // Shrink hits Skills anyway. That is a contradiction
                    // between a debuff's text and its behaviour."
                    //
                    // THE ENGINE IS RIGHT AND ONLY THE WORDS ARE WRONG, which
                    // is `EB-469`'s, `EB-481`'s and `EB-521`'s sentence again.
                    // MEASURED on the shipped assembly rather than assumed:
                    // `ShrinkPower.ModifyDamageMultiplicative` gates on
                    // `ValuePropExtensions.IsPoweredAttack` and on nothing
                    // else -- the identical gate `WeakPower` uses, which the
                    // arm's own Weak row already says "a Skill's damage too"
                    // about. "Attacks" in the game's sentence means attack
                    // HITS, and every damage clause the generator emits
                    // carries `ValueProp.Move` whatever `type:` its sheet row
                    // declares.
                    //
                    // THE APPLIER CLAUSE AND THE VARS ARE THE GAME'S OWN.
                    // `ShrinkPower`'s canonical vars are `DamageDecrease` (30,
                    // already a percentage) and `ApplierName`, so the two
                    // holes below are the two the power fills; what changed is
                    // the noun the sentence is about.
                    //
                    // 2026-09-26 (control seat, Regent): AND THE GAME'S TWO
                    // BRANCHES. `ApplierName` is filled only when a MONSTER
                    // applied it (`ShrinkPower.AfterApplied`); the game's own
                    // row branches on it with `:cond:` and names the wearer
                    // otherwise, plus the turn count. This row dropped both,
                    // so Beetle Juice on an enemy read "While  is alive, you
                    // deal 30% less damage".
                    ["SHRINK_POWER.description"] =
                        "The wearer deals "
                      + "[blue]30%[/blue] less damage with every hit it "
                      + "lands, a Skill's damage too, until it wears off.",
                    ["SHRINK_POWER.smartDescription"] =
                        "{ApplierName.StringValue:cond:While {} is alive, "
                      + "you deal|[gold]{OwnerName}[/gold] deals} "
                      + "[blue]{DamageDecrease}%[/blue] less damage with "
                      + "every hit{Amount:cond:==1? next turn|>1? for the "
                      + "next [blue]{}[/blue] turns|}, a Skill's damage too.",
                });

            // Klee's character strings moved onto the model itself
            // (Klee.Localization) when she became a CustomCharacterModel:
            // BaseLib prefixed her id to KLEEMOD-KLEE, so the hardcoded
            // "KLEE.*" keys that used to live here targeted an id nothing
            // looks up -- finding 23, same failure mode R4 documents for
            // cards. The self-check's R5 rule caught it at boot.


            Log.Info($"[{ModId}] Localization strings injected.");
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Failed to inject loc strings: {e}");
        }
    }

    // O5: ProbeBaseGameLocSyntax removed. It existed to read base-game loc
    // templates at runtime and settle the SmartFormat syntax question (single
    // braces, :diff()); that is now settled, encoded in the codegen emitter,
    // and enforced by KleeSelfCheck R6a/R6b. Keeping it meant a dozen INFO
    // lines per boot in the log we now read for telemetry.
}

// ---------------------------------------------------------------------------
//  Harmony patches
// ---------------------------------------------------------------------------

/// <summary>
/// Injects our loc strings once LocManager has built its tables.
///
/// BOTH MERGES RIDE THIS ONE SEAM (EB-759). The Teyvat arm's rows used to be
/// merged from <c>KleeMod.Initialize</c>, a <c>[ModInitializer]</c>, which runs
/// well before <c>LocManager.Initialize</c> — so <c>LocManager.Instance</c>
/// had no tables and <c>TeyvatLoc.Inject</c>'s own try/catch caught an
/// <c>NullReferenceException</c> on EVERY boot, merged zero rows, and left
/// every dressed string rendering as its raw key
/// (<c>review/records/teyvat-spike-proofs-2026-09-15.md</c>). The call-site
/// comment there reasoned about when a table is READ; the constraint is when
/// it EXISTS. The card rows never had the bug because they have always been
/// here, and the arm's rows are here now for the same reason.
///
/// ORDER INSIDE THE POSTFIX DOES NOT MATTER: the two merges touch disjoint
/// tables (cards/card_keywords/powers/characters against acts/monsters/
/// intents/events) and neither reads the other's. Both swallow their own
/// exceptions, so one failing cannot cost the other its text.
/// </summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Patch
{
    [HarmonyPostfix]
    public static void Postfix()
    {
        KleeMod.InjectLocStrings();

        // THE TEYVAT RUN FRAME ARM's rows (spike, -p:TeyvatFrame=true). A
        // no-op with the arm off — `TeyvatLoc.Inject`'s first line is the
        // flag — so a release build merges not one row.
        Teyvat.TeyvatLoc.Inject();
    }
}

// ---------------------------------------------------------------------------
// ModelDb_AllCharacters_Patch — REMOVED (finding 27). BaseLib's
// AddCustomCharacters postfix appends every CustomContentDictionary character
// to ModelDb.AllCharacters, unconditionally and with no duplicate check.
// Klee has been in that dictionary since the CustomCharacterModel migration
// (her base ctor registers her), so from finding 21 onward BOTH appends ran
// and character select showed two Klees. Finding 21's "verified BaseLib does
// not append custom characters" was wrong — that check found the
// GetVisibleCharacters FILTER transpiler and stopped there, missing the
// separate append postfix. The append is BaseLib's job now; a mod-side
// append patch would be reintroducing the duplicate.
// ---------------------------------------------------------------------------

/// <summary>
/// Finding 22: any effect that draws N reward cards throws once N exceeds the
/// character's generatable pool, and Klee's pool is smaller than the largest N
/// in the game.
///
/// CardFactory.CreateForReward(player, cardCount, options) loops cardCount
/// times against an accumulating blacklist. Once every generatable card is
/// blacklisted, the surviving options are all Basic, RollForRarity walks
/// Common->Uncommon->Rare->Common, revisits its own start, returns None, and
/// the method throws (`sts2.decompiled.cs:452947`).
///
/// The largest N in the base game is SealedDeck's Neow option, which asks for
/// 30 (`:403214`). Klee ships 24 cards, 4 of them Basic, so 20 are generatable
/// and draw 21 is a guaranteed throw. RoomFullOfCheese.Gorge asks for 8 Commons
/// against her 14 and survives, but only by margin.
///
/// CLAMPING RATHER THAN BLOCKING THE OPTION, deliberately. Sealed Deck's
/// selector asks the player to keep 10, so offering 20 instead of 30 is a
/// smaller, still-playable choice rather than a missing Neow option — and the
/// clamp stops applying by itself the moment the pool grows past 30, which is
/// what C3 does. Removing the option would have to be remembered and undone.
///
/// Base characters are unaffected: their pools exceed every N in the game, so
/// the clamp never triggers for them. The rarity test mirrors the two branches
/// of CreateForReward exactly — Uniform excludes Basic and Ancient, everything
/// else can only roll Common/Uncommon/Rare — because a pool of Curses passes a
/// naive "not Basic" count and still throws.
///
/// `EB-363`: AND THE CLAMP'S OWN FLOOR, which is the second half of this patch.
/// A clamp to ZERO is not a softlock and it is not a card either — it is a
/// selection screen with no rows in it, which is exactly what [USER]'s Kokomi
/// r5 run got twice when The Future of Potions took a Regen Potion for an
/// "Upgraded Uncommon Attack" and her arm pool held no Uncommon Attack. The
/// clamp turned the base game's descriptive throw into a silent nothing, so
/// the event ate a potion and handed back an empty grid.
///
/// The cause is a CELL, not a count: a base effect can ask the character's pool
/// for a rarity x type cell (`TheFutureOfPotions`), a rarity (`GlassEye`,
/// `SeaGlass`, `ArcaneScroll`, `HeftyTablet`, `RoomFullOfCheese`) or a type
/// (`InfestedAutomaton`), and a 40-row arm pool leaves cells that a 75-row
/// shipped pool fills by sheer size. The full census of queried cells, and
/// which ones each arm leaves empty or short, is
/// `KleeTests/Prototype/PoolCellCoverageTests.cs` — that file is the ledger and
/// this is the seam it walks.
///
/// THE WIDENING LADDER, and it runs BEFORE the clamp because the clamp is what
/// it is trying not to reach:
///
///   1. THE CELL AS ASKED. If it can fill the draw, nothing here happens, and
///      that is every draw on every shipped pool.
///   2. THE NEIGHBOUR CELL — same rarity, any type. Taken only when the cell is
///      non-empty (the surviving cards are where the rarity is read from) and
///      only when it can fill the draw. Rarity is preserved ahead of type on
///      purpose: a Rare potion traded for three Rares of mixed type is still
///      the trade the event described, where three Commons would not be.
///   3. THE WHOLE POOL. The fallback when the cell is EMPTY (there is no rarity
///      to preserve) or when the neighbour cell cannot fill the draw either.
///
/// WHAT IS GIVEN UP, said plainly: a widened draw no longer matches the line
/// the event printed — the "Uncommon Attack" it promised may arrive as an
/// Uncommon Skill. That is the trade this row was opened to make. An event that
/// hands back a card of the wrong type is a smaller defect than one that hands
/// back nothing, and the widening stops by itself the day the cell is filled by
/// a card, which is the real fix and a design pick, not a seam.
///
/// SELF-LIMITING TWICE OVER. An unfiltered draw (`Trial`, `LostCoffer`, Sealed
/// Deck) has nothing to widen to — rungs 2 and 3 resolve to the same set the
/// cell already is — so it falls straight through to the clamp exactly as
/// before. And the roster gate above still stands in front of all of it.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForReward),
    new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) })]
internal static class CardFactory_CreateForReward_Clamp_Patch
{
    [HarmonyPrefix]
    public static void Prefix(Player player, ref int cardCount,
                              ref CardCreationOptions options)
    {
        if (cardCount <= 0)
        {
            return;
        }

        // C2: gate on OUR roster before touching anything.
        //
        // The clamp was written to be self-limiting -- base pools exceed every
        // N in the game, so `cardCount > available` is false for them and the
        // patch returns having changed nothing. That is true today and it is
        // an argument, not a guarantee: it rests on a claim about six pools
        // this mod does not own and cannot test. If it were ever wrong, the
        // failure would be this mod silently reducing a base character's Neow
        // reward, which is the one thing a roster mod must never do.
        //
        // The gate also stops us counting a base character's whole generatable
        // pool on every reward draw, which is what the check below costs.
        if (!CompanionPool.IsRosterCharacter(player))
        {
            return;
        }

        var uniform = options.RarityOdds == CardRarityOddsType.Uniform;
        var cell = Rollable(options, player, uniform);

        // `EB-363`. Rungs 2 and 3, before the clamp can floor the draw at zero.
        if (cell.Count < cardCount && options.CardPoolFilter != null)
        {
            var widened = Widen(player, options, cardCount, cell, uniform);
            if (widened != null)
            {
                options = widened;
                cell = Rollable(options, player, uniform);
            }
        }

        var available = cell.Count;

        if (cardCount > available)
        {
            Log.Warn($"[{KleeMod.ModId}] clamped a {cardCount}-card reward draw "
                   + $"to {available}: the pool cannot generate more without "
                   + "exhausting its blacklist and throwing.");
            cardCount = available;
        }
    }

    /// <summary>
    /// The cards this draw could actually roll: what the options offer, minus
    /// the rarities the two branches of <c>CreateForReward</c> can never select.
    ///
    /// Mirrors those branches exactly — Uniform excludes Basic and Ancient,
    /// everything else can only roll Common/Uncommon/Rare — because a pool of
    /// Curses passes a naive "not Basic" count and still throws.
    /// </summary>
    internal static List<CardModel> Rollable(
        CardCreationOptions options, Player player, bool uniform) =>
        options.GetPossibleCards(player).Where(c => uniform
            ? c.Rarity != CardRarity.Basic && c.Rarity != CardRarity.Ancient
            : c.Rarity == CardRarity.Common
              || c.Rarity == CardRarity.Uncommon
              || c.Rarity == CardRarity.Rare).ToList();

    /// <summary>
    /// `EB-363`. Rung 2 then rung 3 of the ladder in the class comment, or null
    /// when neither rung holds more cards than the cell already does (an
    /// unfiltered draw, or a pool that is simply this small — the clamp owns
    /// that case and always did).
    ///
    /// THE WIDENED FILTER IS A SET MEMBERSHIP TEST, not a rewritten predicate,
    /// because the predicate this is widening is an opaque <c>Func</c> the mod
    /// cannot take apart: it is the event's own lambda, closed over an
    /// <c>Rng</c>-chosen <c>CardType</c> in <c>TheFutureOfPotions</c>'s case.
    /// What CAN be read is which cards survive it, and a rung is defined by the
    /// cards it admits rather than by the shape of the question.
    ///
    /// A COPY, NEVER A MUTATION. <c>CardCreationOptions.WithFilter</c> writes
    /// through to the instance, and that instance is the caller's — a
    /// <c>CardReward</c> keeps it for its reroll and an event may hold it
    /// across two draws. Widening one draw must not widen a later one that the
    /// pool might by then be able to answer as asked, so this returns a fresh
    /// options object and the <c>ref</c> parameter above swaps it in for this
    /// call alone.
    /// </summary>
    private static CardCreationOptions? Widen(
        Player player, CardCreationOptions options, int wanted,
        IReadOnlyList<CardModel> cell, bool uniform)
    {
        var whole = Rollable(
            new CardCreationOptions(
                options.CardPools, options.Source, options.RarityOdds, null),
            player,
            uniform);

        var admitted = WidenedAdmissions(wanted, cell, whole);
        if (admitted == null)
        {
            return null;
        }

        Log.Warn($"[{KleeMod.ModId}] a {wanted}-card draw asked a pool cell holding "
               + $"{cell.Count}; widened to {admitted.Count} cards "
               + $"({(admitted.Count == whole.Count ? "the whole pool" : "the same rarity at any type")}). "
               + "EB-363's seam: the event hands back a card of another rarity or "
               + "type rather than an empty selection, and it stops the moment the "
               + "cell holds enough cards of its own.");

        var ids = admitted.Select(c => c.Id).ToHashSet();
        return Clone(options,
            admitted.Count == whole.Count ? null : c => ids.Contains(c.Id));
    }

    /// <summary>
    /// `EB-363`. THE LADDER ITSELF, as a decision over two lists and nothing
    /// else: the cards the cell admits, and the cards the whole pool admits.
    /// Null means "do not widen".
    ///
    /// SEPARATED FROM THE OPTIONS PLUMBING ON PURPOSE. Everything above this
    /// needs a live <c>Player</c> — <c>GetPossibleCards</c> reads its unlock
    /// state and its run's multiplayer constraint — and a live Player is
    /// outside the headless boundary (KleeTests/README.md). The DECISION needs
    /// neither, so it is pinned for real rather than structurally, in
    /// <c>PoolCellCoverageTests</c>.
    /// </summary>
    internal static List<CardModel>? WidenedAdmissions(
        int wanted, IReadOnlyList<CardModel> cell, IReadOnlyList<CardModel> whole)
    {
        // Rung 1: the cell as asked, and an unfiltered draw, which has nothing
        // to widen to. Either way this is not the clamp's problem to dodge.
        if (cell.Count >= wanted || whole.Count <= cell.Count)
        {
            return null;
        }

        // Rung 2: same rarity, any type -- but only if it can fill the draw. A
        // neighbour cell that is ALSO short buys nothing over rung 3 and would
        // cost the rows rung 3 would have found.
        var rarities = cell.Select(c => c.Rarity).ToHashSet();
        if (rarities.Count > 0)
        {
            var neighbour = whole.Where(c => rarities.Contains(c.Rarity)).ToList();
            if (neighbour.Count >= wanted)
            {
                return neighbour;
            }
        }

        // Rung 3: the whole pool. The cell is empty (there is no rarity to
        // preserve) or its rarity cannot fill the draw either.
        return whole.ToList();
    }

    /// <summary>
    /// <paramref name="options"/> with a different filter and everything else
    /// carried across by hand. The record's own copy constructor is protected
    /// and <c>with</c> is not reachable from outside the assembly that declares
    /// it, so the four remaining members are named here; a fifth added by a
    /// game update would be dropped silently, which is why
    /// <c>PoolCellCoverageTests</c> pins the member set.
    /// </summary>
    private static CardCreationOptions Clone(
        CardCreationOptions options, Func<CardModel, bool>? filter)
    {
        var copy = new CardCreationOptions(
                options.CardPools, options.Source, options.RarityOdds, filter)
            .WithFlags(options.Flags);
        return options.RngOverride == null
            ? copy
            : copy.WithRngOverride(options.RngOverride);
    }
}

/// <summary>
/// Finding 24: entering ANY shop soft locks the run while Klee's pool has no
/// Power cards.
///
/// MerchantInventory.PopulateCharacterCardEntries stocks a hardcoded slot
/// layout — 2 Attacks, 2 Skills, 1 Power — and CreateForMerchant(player,
/// options, type) rolls a rarity that must contain a card of that type.
/// GetNextAllowedRarity wraps Common->Uncommon->Rare and returns None when no
/// rarity has one, and the method throws. The throw happens inside
/// MerchantRoom.EnterInternal's async continuation, so the room never finishes
/// entering: black screen, no crash dialog, run lost. Klee ships 24 cards and
/// not one is a Power, so this was every shop, deterministically.
///
/// SUBSTITUTING THE TYPE RATHER THAN EMPTYING THE SLOT, deliberately. The
/// merchant's 5-slot layout is load-bearing UI — Populate has no "no card"
/// path — so the safe degradation is offering a Skill or Attack where the
/// Power would sit. The fallback order prefers Skill (the closer analogue of
/// a Power purchase: utility, not damage). Like the reward-draw clamp above,
/// this patch stops changing anything the moment the pool contains a Power
/// card, which is the real fix and a C3 content item.
///
/// The eligibility test mirrors CreateForMerchant exactly: it excludes Basic
/// (the method's own filter) and demands Common/Uncommon/Rare, because the
/// shop rarity roll can only ever land on those three (same reasoning as
/// self-check R3a). Base characters stock every type and never hit the
/// fallback.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForMerchant),
    new[] { typeof(Player), typeof(IEnumerable<CardModel>), typeof(CardType) })]
internal static class CardFactory_CreateForMerchant_TypeFallback_Patch
{
    [HarmonyPrefix]
    public static void Prefix(IEnumerable<CardModel> options, ref CardType type)
    {
        // Callers pass materialized lists; guard anyway so a lazy sequence is
        // only enumerated here once.
        var pool = options as IReadOnlyCollection<CardModel> ?? options.ToList();

        bool Stocks(CardType t) => pool.Any(c => c.Type == t
            && (c.Rarity == CardRarity.Common
                || c.Rarity == CardRarity.Uncommon
                || c.Rarity == CardRarity.Rare));

        if (Stocks(type))
        {
            return;
        }

        foreach (var fallback in new[] { CardType.Skill, CardType.Attack, CardType.Power })
        {
            if (Stocks(fallback))
            {
                Log.Warn($"[{KleeMod.ModId}] merchant slot wanted a {type} card but the "
                       + $"pool has none at a rollable rarity; offering a {fallback} "
                       + "instead. This stops happening once the pool stocks that type.");
                type = fallback;
                return;
            }
        }

        // Nothing of any type is rollable; fall through and let the game's own
        // descriptive exception surface the truly-broken pool.
    }
}

/// <summary>
/// Finding 21: winning an Elite or Boss room SOFT LOCKS the run for any
/// character outside the base six.
///
/// ProgressSaveManager.CheckFifteenElitesDefeatedEpoch and its Boss twin are
/// closed type-switches over Ironclad/Silent/Regent/Defect/Necrobinder/Deprived
/// that end in `throw new ArgumentOutOfRangeException("character", ...)`. They
/// are called from UpdateAfterCombatWon, which runs inside
/// CombatManager.EndCombatInternal -> CheckWinCondition. The throw escapes into
/// an async continuation, so EndCombatInternal never completes: the enemies are
/// dead, the win is logged, and combat simply never ends. No crash dialog, no
/// recovery — End Turn does nothing and the run is lost.
///
/// NOW A CANARY, NOT THE FIX. The real cause was that Klee derived from
/// CharacterModel instead of CustomCharacterModel, so BaseLib's own prefix on
/// these exact three methods — `return !(localPlayer.Character is ICustomModel)`
/// — never skipped them. That is fixed at the source in Klee.cs, which means
/// BaseLib now short-circuits both methods before they can throw and this
/// finalizer should NEVER run again.
///
/// It is kept precisely because it logs when it fires. If that line ever
/// appears, BaseLib's guard has stopped applying to Klee — most likely because
/// someone changed her base type back or a BaseLib upgrade moved the interface
/// — and the log line is a far cheaper way to learn that than another soft
/// locked playtest. Deleting it would remove the detector, not dead code.
///
/// A Finalizer rather than a Prefix, deliberately: a Prefix would have to name
/// the six base types to decide whether to skip, and would break again the day
/// MegaCrit adds a seventh. Both methods read Character and then immediately
/// switch, with no side effect before the throw, so suppressing after the fact
/// loses nothing. The ParamName test keeps this narrow — any other exception
/// from these methods still propagates rather than being swallowed.
/// </summary>
[HarmonyPatch]
internal static class ProgressSaveManager_EpochCheck_Patch
{
    // F2: null-guarded. AccessTools.Method returns null when a name stops
    // resolving, and yielding that null makes Harmony throw about a null
    // element rather than about the method that died. Routing through
    // KleePatchBootstrap records the miss BY NAME and drops the null, so a
    // rename of one of these two costs the one canary rather than the batch.
    // If BOTH die the class arms nothing, which the bootstrap reports as a
    // failure -- the alternative is a canary that silently stopped watching.
    [HarmonyTargetMethods]
    public static IEnumerable<MethodBase> TargetMethods()
    {
        var targets = new[]
        {
            KleePatchBootstrap.ResolveMethod(typeof(ProgressSaveManager),
                "CheckFifteenElitesDefeatedEpoch"),
            KleePatchBootstrap.ResolveMethod(typeof(ProgressSaveManager),
                "CheckFifteenBossesDefeatedEpoch"),
        };

        return targets.Where(m => m != null)!;
    }

    [HarmonyFinalizer]
    public static Exception? Finalizer(Exception __exception, MethodBase __originalMethod)
    {
        if (__exception is ArgumentOutOfRangeException { ParamName: "character" })
        {
            Log.Warn($"[{KleeMod.ModId}] CANARY: suppressed {__originalMethod.Name}. "
                   + "BaseLib's ICustomModel prefix should have skipped this "
                   + "already -- check that Klee still derives from "
                   + "CustomCharacterModel (DECISIONS finding 21).");
            return null;                 // suppress; combat can now end
        }

        return __exception;              // anything else is not ours to eat
    }
}
