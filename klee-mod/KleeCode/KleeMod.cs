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
                    .Concat(Powers.KokomiGarmentHooks.Subscribe(combatState))
                    // EB-19/races-a + races-c: the four end-of-turn tenants
                    // that share the player's Block and the enemy reaction
                    // board no longer each override BeforeSideTurnEnd. This
                    // one listener drives them in the sim's fixed order.
                    .Concat(Powers.TurnEndSequencer.Subscribe(combatState))
#if PROTOTYPE_CARDS
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
#endif
                    // Track B's human feed: per-fight telemetry from normal
                    // play, in the schema the soak writes. Reads only -- see
                    // the three rules in PlayTelemetry.cs, the first of which
                    // is that a measurement must never desync a co-op table.
                    .Concat(Diagnostics.PlayTelemetryHooks.Subscribe(combatState)));

        Log.Info($"[{ModId}] Klee, Furina and Kokomi registered.");
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
#if PROTOTYPE_CARDS
                // QUARANTINED (the Kokomi overhaul, draft 6). Moon's
                // Reflection's exhaust-pile screen, on exactly the terms the three rows
                // above have: a LocString is a table plus a key with no
                // raw-text constructor, so the copy can only reach the screen
                // as a row, and this dictionary is its only source. Inside the
                // compile switch because the verb it names does not exist in a
                // release build.
                [Powers.KokomiPlan.ReflectionPromptKey] =
                    Powers.KokomiPlan.ReflectionPromptText,
#endif
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
                    ["KLEEMOD-ELEMENTAL_SKILL.title"] = "Elemental Skill",
                    ["KLEEMOD-ELEMENTAL_SKILL.description"] =
                        $"Playing this card grants {Powers.BurstConstants.PerSkillTag} Burst Energy.",
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
                        "Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. No aura: nothing happens. [gold]Anemo[/gold] never stays on a body.",
                    ["KLEEMOD-APPLIES_GEO.title"] = "Applies Geo",
                    ["KLEEMOD-APPLIES_GEO.description"] =
                        "Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. No aura: nothing happens. [gold]Geo[/gold] never stays on a body.",
                    ["KLEEMOD-BOMB.title"] = "Bomb",
                    // R249 pick 2(a): the SHIPPED Bomb keeps "detonates"
                    // until the overhaul replaces this kit.
                    ["KLEEMOD-BOMB.description"] =
                        "Detonates at the start of your turn, or early when its enemy takes unblocked Attack damage. That enemy's first attack deals 25% less.",
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
                        $"[gold]Pyro[/gold] meets [gold]Electro[/gold]: [blue]{Elements.ReactionConstants.OverloadSplash}[/blue] damage to ALL enemies and [blue]{Elements.ReactionConstants.OverloadWeak}[/blue] [gold]Weak[/gold] on the reacted enemy.",
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
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.description"] =
                        $"[gold]Hydro[/gold] meets [gold]Electro[/gold]: the reacted enemy loses [blue]{Elements.ReactionConstants.ElectroChargedDot}[/blue] HP at the start of its turn, 1 less each turn.",
                    ["KLEEMOD-FROZEN_PREVIEW.title"] = "Reaction preview: Frozen",
                    ["KLEEMOD-FROZEN_PREVIEW.description"] =
                        $"[gold]Hydro[/gold] meets [gold]Cryo[/gold]: its next action deals half damage, and until it acts the first Attack to hit it Shatters for [blue]{Elements.ReactionConstants.ShatterDamage}[/blue] damage.",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] = "Reaction preview: Frozen (Boss)",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.description"] =
                        $"Bosses cannot be Frozen. [gold]Hydro[/gold] plus [gold]Cryo[/gold] is consumed and applies [blue]{Elements.ReactionConstants.FrozenBossVuln}[/blue] [gold]Vulnerable[/gold] instead.",
                    ["KLEEMOD-SWIRL_PREVIEW.title"] = "Reaction preview: Swirl",
                    ["KLEEMOD-SWIRL_PREVIEW.description"] =
                        "[gold]Anemo[/gold] meets an aura: the aura is consumed and copied onto ALL enemies.",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.title"] = "Reaction preview: Crystallize",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.description"] =
                        $"[gold]Geo[/gold] meets an aura: the aura is consumed and you gain [blue]{Elements.ReactionConstants.CrystallizeBlock}[/blue] [gold]Block[/gold].",

                    // Legibility sprint L-C: titles for the re-homed rider
                    // tips (FurinaRiderTips). These are NOT card keywords --
                    // they are hover-tip titles, which need a LocString --
                    // but they live in the same table so the one merge point
                    // covers them and a code-only rebuild never shows a raw
                    // key. The bodies are built per card in C#, because a
                    // shared row cannot carry a per-card rate.
                    [Cards.FurinaRiderTips.FanfareKey + ".title"] =
                        "Fanfare scaling",
                    [Cards.FurinaRiderTips.AuraKey + ".title"] =
                        "Elemental aura bonus",
                    [Cards.FurinaRiderTips.SalonKey + ".title"] =
                        "Salon scaling",
                    // The fourth rider tip had no row and shipped as the raw
                    // key: `Blocking Notes+` rendered
                    // "card_keywords.KLEEMOD-COMPANION_RIDER.title" on the
                    // card-reward screen of a live run (0.2-589). The pck's
                    // card_keywords.json carries none of these four either, so
                    // this dictionary is their only source and a missing entry
                    // is directly player-visible.
                    [Cards.FurinaRiderTips.CompanionKey + ".title"] =
                        "Companion scaling",
                    // `EB-475`: three words that gated decisions with no
                    // definition anywhere. Same dictionary, same reason as the
                    // four above -- a missing row here is directly
                    // player-visible as the raw key.
                    [Cards.FurinaRiderTips.SpotlightMoveKey + ".title"] =
                        "Moved the Spotlight",
                    [Cards.FurinaRiderTips.GuestStarKey + ".title"] =
                        "Guest Star",
                    [Cards.FurinaRiderTips.BowKey + ".title"] =
                        "Takes their bow",
                    // `EB-477`: the half of a Companion card that went missing
                    // in silence on an empty stage.
                    [Cards.FurinaRiderTips.CompanionPerformKey + ".title"] =
                        "Performs a member",
                    // `EB-485`: how long the lighting lasts, on the card that
                    // pays for it. Same dictionary and the same reason as
                    // every row above -- the pck's `card_keywords.json`
                    // carries none of these, so a missing row here is
                    // directly player-visible as the raw key.
                    [Cards.FurinaRiderTips.SpotlightLastsKey + ".title"] =
                        "Lit for this combat",

                    // B5: the member tips the deploy faces hand off to. Only
                    // the TITLES are rows -- the bodies are built live in
                    // SalonMemberTips, because the numbers live in
                    // SalonConstants and the cap is a per-player stat.
                    [Cards.SalonMemberTips.CrabalettaKey + ".title"] =
                        "Mademoiselle Crabaletta",
                    [Cards.SalonMemberTips.UsherKey + ".title"] =
                        "Gentilhomme Usher",
                    [Cards.SalonMemberTips.ChevalmarinKey + ".title"] =
                        "Surintendante Chevalmarin",
                    [Cards.SalonMemberTips.SalonRulesKey + ".title"] =
                        "Salon",

                    // EB-53/N1: the end-of-turn docket's per-slot hovers.
                    // TITLES only, the same bargain as the member tips above --
                    // every body is built live in TurnEndAttribution from the
                    // constants the resolution reads, so a repricing cannot
                    // leave a row quoting a retired number.
                    [Powers.TurnEndAttribution.MasqueKey + ".title"] =
                        "Bond of Life",
                    [Powers.TurnEndAttribution.SparksKey + ".title"] =
                        "Sparks 'n' Splash",
                    [Powers.TurnEndAttribution.OzKey + ".title"] =
                        "Oz, at Your Side",
                    [Powers.TurnEndAttribution.KurageKey + ".title"] =
                        "Bake-Kurage",

                    // Kokomi's two hidden reads (KokomiRiderTips). Both
                    // resolve somewhere no card face can print -- the pulse at
                    // end of turn, the Garment rider on OTHER cards -- so the
                    // tip is the only surface either number has.
                    [Cards.KokomiRiderTips.PulseKey + ".title"] =
                        "Bake-Kurage pulse",
                    [Cards.KokomiRiderTips.GarmentKey + ".title"] =
                        "Ceremonial Garment is active",
                    // L4b: the printed Charge rider's rate. Unlike the two
                    // above, the NUMBER was always visible -- this row titles
                    // the tip that says what the number is made of.
                    [Cards.KokomiRiderTips.ChargeKey + ".title"] =
                        "Charge scaling",
                    // EB-64's shape, one key over: Muster had no row and
                    // shipped as the raw key -- `Reinforcements` rendered
                    // "card_keywords.KLEEMOD-MUSTER.title" as the keyword name
                    // on a live shop screen (0.2-634, EB-53 capture session).
                    [Cards.KokomiRiderTips.MusterKey + ".title"] = "Muster",
                    // `EB-484`: both numbers of a `bonus_vs_debuff` fold, on
                    // a screen with no enemy to resolve it. Same bargain and
                    // the same raw-key hazard as every row here.
                    [Cards.KokomiRiderTips.DebuffRiderKey + ".title"] =
                        "Against a debuffed enemy",
                    // QUARANTINED (R213 E1): the Charge KEYWORD's title. The
                    // BODY is built live in KokomiRiderTips, because it
                    // quotes CHARGE_PER_EXHAUST and reads the current bank --
                    // the same bargain the Muster and pulse tips already
                    // make. Distinct from CHARGE_RIDER above, which titles a
                    // per-card RATE tip on a card that READS the meter.
                    [Cards.KokomiRiderTips.ChargeWordKey + ".title"] =
                        "Charge",
                    // The Charge keyword's twin, one meter over and three
                    // characters wide: the Burst KEYWORD's title. The body is
                    // built live in KleeCardTooltips because the meter's size
                    // is per character and the tip says what the owner holds.
                    // The retired BurstMeterPower badge used to be the only
                    // surface that ever defined the word; nothing replaced it
                    // until now.
                    [Cards.KleeCardTooltips.BurstKey + ".title"] =
                        "Burst Energy",
#if PROTOTYPE_CARDS
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
                    // `ARM_BOMB` is titled "Bomb" and `KLEEMOD-BOMB` is too,
                    // which is correct rather than a collision: they are the
                    // same WORD under two different rules, and no single face
                    // ever raises both (see the attach rule in
                    // `gen_klee_cards.arm_keyword_tip_calls`).
                    [Cards.ArmKeywordTips.BombKey + ".title"] = "Bomb",
                    [Cards.ArmKeywordTips.SetOffKey + ".title"] = "Set off",
                    [Cards.ArmKeywordTips.SparkKey + ".title"] = "Spark",
                    [Cards.ArmKeywordTips.MineKey + ".title"] = "Mine",
                    // R244, Klee's fifth: the coven's one-word family mark.
                    // Eighteen faces printed it and nothing defined it, because
                    // until her three readers existed it had no rule to state.
                    [Cards.ArmKeywordTips.HexereiKey + ".title"] = "Hexerei",
                    // `EB-372`, Klee's sixth: a Power of hers that Kaeya's
                    // Cold-Blooded Strike is written against, so the word
                    // reaches a player who may never have drafted it.
                    [Cards.ArmKeywordTips.GroundedKey + ".title"] = "Grounded",
                    // `EB-446`, Klee's seventh: the raven ANOTHER companion
                    // card puts out, named on a face that cannot grant him.
                    [Cards.ArmKeywordTips.OzKey + ".title"] = "Oz",
                    // `EB-418`. The second rider, not a keyword: the Spark her
                    // KIT mints on a play of one of her own Companions, which
                    // LAW:145 keeps off the Companion's own face and which
                    // therefore had no surface at all.
                    [Cards.ArmKeywordTips.CovenSparkKey + ".title"] =
                        "Sparks from your Companion",
                    [Cards.ArmKeywordTips.MendKey + ".title"] = "Mend",
                    [Cards.ArmKeywordTips.PlanKey + ".title"] = "Plan",
                    // `EB-378`. The rider, not a keyword: the rows whose Hydro
                    // arrives with the jellyfish's carry-out rather than with
                    // the play.
                    [Cards.ArmKeywordTips.PlanElementKey + ".title"] =
                        "Hydro on the carry-out",
                    [Cards.ArmKeywordTips.SwirlKey + ".title"] = "Swirl",
                    // The Furina reframe's three (slice two). `Deploy`
                    // is the one word here a shipped Furina card also
                    // uses in prose, and it is the same correctness as
                    // `Bomb` above: the shipped deploy performs nobody,
                    // the arm's does, and no single face raises both.
                    [Cards.ArmKeywordTips.DeployKey + ".title"] = "Deploy",
                    [Cards.ArmKeywordTips.EvokeKey + ".title"] = "Evoke",
                    [Cards.ArmKeywordTips.DrainKey + ".title"] = "Drain",
                    // `EB-407`. The one word in this block the arm did not
                    // invent: Encore is shipped machinery, and its only
                    // statement of itself is `EncoreMeterPower`'s badge, which
                    // renders once the meter is on the board -- while the word
                    // is printed on the Neow screen and on opening-hand faces
                    // before that. No collision: the shipped meter power
                    // titles itself and hangs no keyword tip.
                    [Cards.ArmKeywordTips.EncoreKey + ".title"] = "Encore",
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
#endif
                };
            keywordTable.MergeWith(keywordFallback
                .Where(pair => !keywordTable.HasEntry(pair.Key))
                .ToDictionary(pair => pair.Key, pair => pair.Value));

#if PROTOTYPE_CARDS
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
                    ["VULNERABLE_POWER.description"] =
                        "Vulnerable creatures take [blue]50%[/blue] more "
                      + "damage from cards, a potion's aside.",
                    ["VULNERABLE_POWER.smartDescription"] =
                        "Receive [blue]{DamageIncrease:percentMore()}%[/blue] "
                      + "more damage from cards for [blue]{Amount}[/blue] "
                      + "{Amount:plural:turn|turns}.",

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
                });
#endif

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

/// <summary>Injects our loc strings once LocManager has built its tables.</summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => KleeMod.InjectLocStrings();
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
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForReward),
    new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) })]
internal static class CardFactory_CreateForReward_Clamp_Patch
{
    [HarmonyPrefix]
    public static void Prefix(Player player, ref int cardCount,
                              CardCreationOptions options)
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
        var available = options.GetPossibleCards(player).Count(c => uniform
            ? c.Rarity != CardRarity.Basic && c.Rarity != CardRarity.Ancient
            : c.Rarity == CardRarity.Common
              || c.Rarity == CardRarity.Uncommon
              || c.Rarity == CardRarity.Rare);

        if (cardCount > available)
        {
            Log.Warn($"[{KleeMod.ModId}] clamped a {cardCount}-card reward draw "
                   + $"to {available}: the pool cannot generate more without "
                   + "exhausting its blacklist and throwing.");
            cardCount = available;
        }
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
