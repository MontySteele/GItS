using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Models.RelicPools;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod;

/// <summary>Furina — Skill-grade Hydro support and Salon ramp character.</summary>
public sealed class Furina : CustomCharacterModel, IFurinaCharacter
{
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Furina"),
        ("description",
            "The Regina of All Waters, Kindreds, Peoples and Laws."),
        ("titleObject", "Furina"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
    };

    public override Color NameColor => new("4AA6C8");

    public override CharacterGender Gender => CharacterGender.Feminine;

    protected override CharacterModel? UnlocksAfterRunAs => null;

    public override int StartingHp => 60;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool =>
        ModelDb.CardPool<FurinaCardPool>();

    public override RelicPoolModel RelicPool =>
        ModelDb.RelicPool<FurinaRelicPool>();

    public override PotionPoolModel PotionPool =>
        ModelDb.PotionPool<SilentPotionPool>();

    public override IEnumerable<CardModel> StartingDeck => new CardModel[]
    {
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<RegalBearing>(),
        ModelDb.Card<AriaOfRecompense>(),
        ModelDb.Card<SalonDebut>(),
        ModelDb.Card<AnInvitation>(),
    };

    public override IReadOnlyList<RelicModel> StartingRelics =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.EtherealSpotlightRelic>(),
        };

    // Temporary playtest visuals live under a Furina namespace even while the
    // PCK builder fills missing files from Klee. Distinct scene paths are
    // future-proofing: BaseLib's conversion registry is keyed by path, so a
    // shared path cannot later carry character-specific conversion behavior.
    // The separate Furina art pass replaces the fallback PNGs in place.
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("furina/ui/select_portrait.png");
    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("furina/ui/select_portrait_locked.png");
    public override string? CustomIconTexturePath =>
        KleePck.Path("furina/ui/char_icon.png");
    // The halo behind the icon, not a stroke around it -- see the note on
    // Klee.CustomIconOutlineTexturePath for the measured convention (EB-37).
    // Derived from the fill by tools/gen_char_icon_outlines.py.
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("furina/ui/char_icon_outline.png");
    // combat.tscn is her animated convention scene (animation sprint 2,
    // Track B2 — she joins Klee on the pck-src authoring channel and off the
    // build_pck.ps1 heredoc). combat_visuals.tscn stays as the fallback that
    // keeps a pre-sprint-2 pck bootable; BaseLib registers whichever path this
    // returns for NCreatureVisuals conversion, and KleeSceneTelemetry shouts
    // at boot when the convention scene is missing.
    public override string? CustomVisualPath =>
        KleePck.Path("furina/model/combat.tscn")
        ?? KleePck.Path("furina/model/combat_visuals.tscn");
    public override string? CustomIconPath =>
        KleePck.Path("furina/ui/character_icon.tscn");
    public override string? CustomEnergyCounterPath =>
        "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";
    public override string? CustomTrailPath =>
        "res://scenes/vfx/card_trail_ironclad.tscn";
    public override string? CustomMapMarkerPath =>
        KleePck.Path("furina/ui/map_marker.png");
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("furina/ui/char_select_bg_furina.tscn");
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("furina/materials/furina_transition_mat.tres");
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("furina/model/rest_character.tscn");
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("furina/model/merchant_character.tscn");

    /// <summary>On-screen combat model, scene-first as of animation sprint 2
    /// (Track B2). Same three-step chain Klee.cs ships, for the same reason:
    /// a silent path miss falls back to static art and looks like "nothing
    /// happened", so every step logs.
    ///
    /// Preferred: the convention scene furina/model/combat.tscn — a layered
    /// rig (coat-back / sword / body / hat) with an %AnimationTree the
    /// character-agnostic router already drives. Fallback 1: the static
    /// 240x280 combat_model.png, exactly the pre-sprint-2 behaviour.
    /// Fallback 2: null, base scene lookup.</summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        string? scenePath = KleePck.Path("furina/model/combat.tscn");
        if (scenePath != null)
        {
            var visuals = NodeFactory<NCreatureVisuals>.CreateFromScene(scenePath);
            MegaCrit.Sts2.Core.Logging.Log.Info(
                $"[{KleeMod.ModId}] combat visuals from convention scene "
                + $"{scenePath}: {visuals.GetType().Name}");
            return visuals;
        }

        MegaCrit.Sts2.Core.Logging.Log.Warn(
            $"[{KleeMod.ModId}] Furina convention combat scene missing; falling "
            + "back to static combat_model.png (pck stale? rebuild with "
            + "tools/build_pck.ps1)");
        var path = KleePck.Path("furina/model/combat_model.png");
        return path == null
            ? null
            : NodeFactory<NCreatureVisuals>.CreateFromResource(
                ResourceLoader.Load<Texture2D>(path));
    }

    // Sync the damage numbers to the flourish-lunge contact frame. Started at
    // Klee's values (plan B3 says to); her lunge peaks at 0.15s by scene
    // construction, so the attack delay is already right and only the cast
    // delay is a taste call pending the B5 look pass.
    public override float AttackAnimDelay => 0.15f;

    public override float CastAnimDelay => 0.25f;

    public override Color EnergyLabelOutlineColor => new("174B67");
    public override Color DialogueColor => new("246B87");
    public override VfxColor SpeechBubbleColor => VfxColor.Swamp;
    public override Color MapDrawingColor => new("4AA6C8");
    public override Color RemoteTargetingLineColor => new("4AA6C8FF");
    public override Color RemoteTargetingLineOutline => new("174B67FF");

    public override List<string> GetArchitectAttackVfx() => new()
    {
        "vfx/vfx_attack_slash",
    };
}
