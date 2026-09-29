#if PROTOTYPE_CARDS && VARKA_PROTOTYPE
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// VARKA, Grand Master of the Knights of Favonius -- the fourth character,
/// prototype batch one (<c>review/active/varka-paper-kit-2026-09-28.md</c>
/// sec.10). Anemo: his Attacks carry the Swirl trigger; his cards Absorb the
/// auras his Knights paint; each element absorbed is a Wind that pays on
/// every Swirl he makes (<see cref="VarkaPrototype"/> states the rules).
///
/// COMPILED ONLY WITH <c>-p:VarkaPrototype=true</c> (on by default beside the
/// other current kits), so a <c>-p:ShippedKits=true</c> build has no Varka on
/// the select screen at all: he ships nowhere else, and there is no shipped
/// kit for an arm switch to fall back to.
/// </summary>
public sealed class Varka : CustomCharacterModel, IVarkaCharacter
{
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Varka"),
        ("description",
            "Grand Master of the Knights of Favonius, who fights with every "
          + "wind in Mondstadt."),
        ("titleObject", "Varka"),
        ("pronounSubject", "he"),
        ("pronounObject", "him"),
        ("pronounPossessive", "his"),
        ("possessiveAdjective", "his"),
    };

    /// <summary>Mondstadt's Anemo teal.</summary>
    public override Color NameColor => new("4CC2A8");

    public override CharacterGender Gender => CharacterGender.Masculine;

    protected override CharacterModel? UnlocksAfterRunAs => null;

    /// <summary>sec.10.2: "Varka, 80 HP, 99 gold".</summary>
    public override int StartingHp => 80;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool =>
        ModelDb.CardPool<VarkaCardPool>();

    public override RelicPoolModel RelicPool =>
        ModelDb.RelicPool<VarkaRelicPool>();

    /// <summary>The Silent's potions, the borrow Kokomi runs on, until his
    /// relic and potion pass (sec.5's flavour list).</summary>
    public override PotionPoolModel PotionPool =>
        ModelDb.PotionPool<SilentPotionPool>();

    public override IEnumerable<CardModel> StartingDeck =>
        VarkaRoster.StartingDeck();

    public override IReadOnlyList<RelicModel> StartingRelics =>
        VarkaRoster.StartingRelics();

    // ART (the varka-art pass): every KleePck.Path returns null on a miss, and
    // tools/build_pck.ps1 fills each of these paths from Klee's files when his
    // own are absent (Copy-VarkaFallback), so the select screen and the map
    // never receive a dead path (KleeSelfCheck R9). The scenes are authored by
    // build_pck.ps1, Kokomi's shapes.
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("varka/ui/select_portrait.png");
    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("varka/ui/select_portrait_locked.png");
    public override string? CustomIconTexturePath =>
        KleePck.Path("varka/ui/char_icon.png");
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("varka/ui/char_icon_outline.png");
    public override string? CustomVisualPath =>
        KleePck.Path("varka/model/combat_visuals.tscn");
    public override string? CustomIconPath =>
        KleePck.Path("varka/ui/character_icon.tscn");
    public override string? CustomEnergyCounterPath =>
        "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";
    public override string? CustomTrailPath =>
        "res://scenes/vfx/card_trail_ironclad.tscn";
    public override string? CustomMapMarkerPath =>
        KleePck.Path("varka/ui/map_marker.png");
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("varka/ui/char_select_bg_varka.tscn");
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("varka/materials/varka_transition_mat.tres");
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("varka/model/rest_character.tscn");
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("varka/model/merchant_character.tscn");

    /// <summary>
    /// The static combat model (240x280, bottom-anchored), Kokomi's half of
    /// the chain: he has no rig. A null return hands the game its own scene
    /// lookup, so he is visible and playable with no file at all.
    /// </summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        var path = KleePck.Path("varka/model/combat_model.png");
        return path == null
            ? null
            : NodeFactory<NCreatureVisuals>.CreateFromResource(
                ResourceLoader.Load<Texture2D>(path));
    }

    public override float AttackAnimDelay => 0.15f;

    public override float CastAnimDelay => 0.25f;

    public override Color EnergyLabelOutlineColor => new("1D5E52");
    public override Color DialogueColor => new("2E8A76");
    public override VfxColor SpeechBubbleColor => VfxColor.Cyan;
    public override Color MapDrawingColor => new("4CC2A8");
    public override Color RemoteTargetingLineColor => new("4CC2A8FF");
    public override Color RemoteTargetingLineOutline => new("1D5E52FF");

    public override List<string> GetArchitectAttackVfx() => new()
    {
        "vfx/vfx_attack_slash",
    };
}
#endif
