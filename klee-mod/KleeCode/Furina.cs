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

    // Temporary playtest visuals: borrow the known-good packaged character
    // surfaces so Furina can enter every room without resolving missing
    // id-derived resources. The separate Furina art pass replaces these
    // paths; card portraits already use Furina-specific loose-image slugs.
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("klee/ui/select_portrait.png");
    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("klee/ui/select_portrait_locked.png");
    public override string? CustomIconTexturePath =>
        KleePck.Path("klee/ui/char_icon.png");
    public override string? CustomMapMarkerPath =>
        KleePck.Path("klee/ui/map_marker.png");
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("klee/ui/char_select_bg_klee.tscn");
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("klee/materials/klee_transition_mat.tres");
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("klee/model/rest_character.tscn");
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("klee/model/character_sprite.tscn");

    public override NCreatureVisuals? CreateCustomVisuals()
    {
        var path = KleePck.Path("klee/model/combat_model.png");
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
