using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod;

/// <summary>
/// YAE MIKO, Guuji of the Grand Narukami Shrine and editor-in-chief of the
/// Yae Publishing House -- the fifth character
/// (<c>review/active/yae-card-paper-2026-10-13.md</c>, ruled 2026-10-13).
/// Electro, catalyst-grade: her Attacks deal Electro. Her shrine is up to
/// three Sesshou Sakura that strike at the end of her turn
/// (<see cref="YaeShrine"/>); her publishing house is the Edit and the
/// Publish (<see cref="YaeEditing"/>).
///
/// PROTOTYPE VISUALS: every art path is hers and falls back to Klee's files
/// at her paths (<c>tools/build_pck.ps1</c>'s Copy-YaeFallback), Varka's
/// first prototype's arrangement: a flat borrowed portrait and sprite, no
/// rig. Her model art (phase A, 2026-10-14) replaces them path by path as
/// its files land (<see cref="CreateCustomVisuals"/>). No switch: she
/// compiles in every build.
/// </summary>
public sealed class Yae : CustomCharacterModel, IYaeCharacter
{
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Yae Miko"),
        ("description",
            "Guuji of the Grand Narukami Shrine and editor-in-chief of the "
          + "Yae Publishing House. Her Sakura strike at the end of every "
          + "turn, and her edits make good cards better."),
        ("titleObject", "Yae Miko"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
        // The rest of the base game's per-character rows (BaseLib's
        // CharacterLoc set plus bestiaryQuote); a missing row renders as its
        // raw key. CharacterLocCompletenessTests pins the set.
        ("aromaPrinciple", "[sine][purple]How tempting. I think I will pass.[/purple][/sine]"),
        ("banter.alive.endTurnPing", "Take your time. I am enjoying this."),
        ("banter.dead.endTurnPing", "..."),
        ("bestiaryQuote", "Hmm. That one would make a fine chapter."),
        ("eventDeathPrevention", "Oh my. Not quite the ending I had in mind."),
        ("goldMonologue", "[sine]Royalties, of a sort...[/sine]"),
        ("cardsModifierTitle", "Yae Miko Cards"),
        ("cardsModifierDescription", "Yae Miko cards will now appear in rewards and shops."),
    };

    /// <summary>Electro violet.</summary>
    public override Color NameColor => new("B07FE0");

    public override CharacterGender Gender => CharacterGender.Feminine;

    protected override CharacterModel? UnlocksAfterRunAs => null;

    /// <summary>Paper sec.1: "HP 72 (between Klee's 70 and Kokomi's 80: she
    /// is a catalyst who ends fights through her shrine, not a tank)".
    /// </summary>
    public override int StartingHp => 72;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool => ModelDb.CardPool<YaeCardPool>();

    public override RelicPoolModel RelicPool => ModelDb.RelicPool<YaeRelicPool>();

    /// <summary>Her own three (the Yae pass, 2026-10-16,
    /// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.4); the
    /// Defect's borrow left, as Kokomi's Silent borrow did.</summary>
    public override PotionPoolModel PotionPool => ModelDb.PotionPool<Potions.YaePotionPool>();

    public override IEnumerable<CardModel> StartingDeck => YaeRoster.StartingDeck();

    public override IReadOnlyList<RelicModel> StartingRelics => YaeRoster.StartingRelics();

    // ART: placeholders. Every KleePck.Path returns null on a miss, and
    // tools/build_pck.ps1 fills each of these paths from Klee's files when
    // hers are absent (Copy-YaeFallback), so the select screen and the map
    // never receive a dead path (KleeSelfCheck R9). The scenes are authored
    // by build_pck.ps1, Varka's first shapes.
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("yae/ui/select_portrait.png");
    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("yae/ui/select_portrait_locked.png");
    public override string? CustomIconTexturePath =>
        KleePck.Path("yae/ui/char_icon.png");
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("yae/ui/char_icon_outline.png");
    public override string? CustomVisualPath =>
        KleePck.Path("yae/model/combat_visuals.tscn");
    public override string? CustomIconPath =>
        KleePck.Path("yae/ui/character_icon.tscn");
    public override string? CustomEnergyCounterPath =>
        "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";
    public override string? CustomTrailPath =>
        "res://scenes/vfx/card_trail_ironclad.tscn";
    public override string? CustomMapMarkerPath =>
        KleePck.Path("yae/ui/map_marker.png");
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("yae/ui/char_select_bg_yae.tscn");
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("yae/materials/yae_transition_mat.tres");
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("yae/model/rest_character.tscn");
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("yae/model/merchant_character.tscn");

    /// <summary>
    /// Combat model, scene-first like Varka and Kokomi: yae/model/combat.tscn,
    /// frame sheets rendered from her official model (tools/char_render,
    /// phase A, a temporary model, 2026-10-14) and generated by
    /// tools/yae_rig from tools/char_render/yae_frames.json. It carries %Facing and
    /// %AnimationTree, so CreatureAnimationRouter, the death seam and the
    /// facing fix apply, plus the element layer KleeMod.Vfx.ElementTrail
    /// colours. Without the scene (a build without her art) she keeps the
    /// static combat_model.png (Klee's, borrowed by Copy-YaeFallback); a
    /// null return hands the game its own scene lookup.
    /// </summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        string? scenePath = KleePck.Path("yae/model/combat.tscn");
        if (scenePath != null)
        {
            var visuals = NodeFactory<NCreatureVisuals>.CreateFromScene(scenePath);
            MegaCrit.Sts2.Core.Logging.Log.Info(
                $"[{KleeMod.ModId}] combat visuals from convention scene "
                + $"{scenePath}: {visuals.GetType().Name}");
            return visuals;
        }

        var path = KleePck.Path("yae/model/combat_model.png");
        return path == null
            ? null
            : NodeFactory<NCreatureVisuals>.CreateFromResource(
                ResourceLoader.Load<Texture2D>(path));
    }

    /// <summary>The flick's release: frame 8 of her attack clip, 0.4 s
    /// (tools/char_render/yae_frames.json, <c>events.main</c>), as Kokomi's
    /// push lands on hers. It was 0.15 s, the roster's shared value, until
    /// her model clips existed. The cast delay stays parked at the shared
    /// value.</summary>
    public override float AttackAnimDelay => 0.4f;

    public override float CastAnimDelay => 0.25f;

    public override Color EnergyLabelOutlineColor => new("4B2A6E");
    public override Color DialogueColor => new("7A4FB0");
    public override VfxColor SpeechBubbleColor => VfxColor.Purple;
    public override Color MapDrawingColor => new("B07FE0");
    public override Color RemoteTargetingLineColor => new("B07FE0FF");
    public override Color RemoteTargetingLineOutline => new("4B2A6EFF");

    public override List<string> GetArchitectAttackVfx() => new()
    {
        "vfx/vfx_attack_slash",
    };
}
