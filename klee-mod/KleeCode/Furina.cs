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
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("furina/ui/char_icon.png");
    public override string? CustomVisualPath =>
        KleePck.Path("furina/model/combat_visuals.tscn");
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

    public override NCreatureVisuals? CreateCustomVisuals()
    {
        var path = KleePck.Path("furina/model/combat_model.png");
        return path == null
            ? null
            : NodeFactory<NCreatureVisuals>.CreateFromResource(
                ResourceLoader.Load<Texture2D>(path));
    }

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
