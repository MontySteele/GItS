using System;
using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Models.RelicPools;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod;

/// <summary>
/// Klee — Spark Knight of Mondstadt.
///
/// GenerateAnimator is deliberately NOT overridden — it is virtual with a
/// working base implementation, so C1 needs no spine art (verified against
/// decompiled CharacterModel, v0.107.1).
///
/// DERIVES FROM CustomCharacterModel, NOT CharacterModel — see DECISIONS
/// finding 21. BaseLib gates 29 separate guards on <c>is ICustomModel</c>,
/// which only CustomCharacterModel implements. Deriving from the raw game
/// type compiled and booted fine and silently opted us out of every one of
/// them, including the prefix that skips base-character epoch tracking; the
/// visible symptom was that winning any Elite or Boss soft locked the run.
/// It also adds no abstract members of its own — everything it declares is
/// virtual with a default — so there is no cost to being on the right base
/// type and no signal when you are not.
/// </summary>
public sealed class Klee : CustomCharacterModel
{
    /// <remarks>
    /// Loc MUST live here, not in KleeMod's hand-rolled dictionary. BaseLib
    /// prefixes custom model ids (KLEE -> KLEEMOD-KLEE) and writes these
    /// against Id.Entry itself (AddModelLoc), so the keys can never drift.
    /// Hardcoded "KLEE.*" keys stopped resolving the moment the base type
    /// changed to CustomCharacterModel -- see DECISIONS finding 23.
    /// </remarks>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Klee"),
        ("description", "The Spark Knight of Mondstadt."),
        ("titleObject", "Klee"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
    };

    // Klee red per spec C1.4; artist's final call later.
    public override Color NameColor => new Color("E85A4F");

    public override CharacterGender Gender => CharacterGender.Feminine;

    /// <remarks>C1: always available, no unlock gate while testing.</remarks>
    protected override CharacterModel? UnlocksAfterRunAs => null;

    /// <remarks>62 HP per spec C1.4 — run-level fragility is a design premise
    /// under test (playtest checklist: "do you notice being fragile?").</remarks>
    public override int StartingHp => 62;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool => ModelDb.CardPool<KleeCardPool>();

    // KleeRelicPool = Silent's borrowed contents + Pounding Surprise. The own
    // pool is REQUIRED, not cosmetic: RelicModel.Pool resolves through
    // AllRelicPools and throws for a relic in no pool, aborting character
    // select mid-method (finding 27). Real Klee relics (~8) are a C3 item.
    public override RelicPoolModel RelicPool => ModelDb.RelicPool<KleeRelicPool>();

    public override PotionPoolModel PotionPool => ModelDb.PotionPool<SilentPotionPool>();

    /// <remarks>
    /// Printed template: 4x Kaboom, 4x Duck and Cover, 1x Jumpy Dumpty,
    /// 1x Pop. KleeStartingCompanionsPatch replaces one Kaboom with Dahlia or
    /// Kaeya and one Duck and Cover with Barbara or Prune after the run seed
    /// exists. Keeping the template here makes character-select/self-check
    /// reads stable; only actual new-run creation resolves the random pair.
    /// </remarks>
    public override IEnumerable<CardModel> StartingDeck => new CardModel[]
    {
        ModelDb.Card<Kaboom>(),
        ModelDb.Card<Kaboom>(),
        ModelDb.Card<Kaboom>(),
        ModelDb.Card<Kaboom>(),
        ModelDb.Card<DuckAndCover>(),
        ModelDb.Card<DuckAndCover>(),
        ModelDb.Card<DuckAndCover>(),
        ModelDb.Card<DuckAndCover>(),
        ModelDb.Card<JumpyDumpty>(),
        ModelDb.Card<Pop>(),
    };

    /// <remarks>
    /// Pounding Surprise (+1 Spark per Bomb detonation) — the real starting
    /// relic, replacing the C1 Burning Blood stub now that the Sparks system
    /// exists (C3 gap-list unlock #1).
    ///
    /// This MUST be non-empty. NCharacterSelectScreen.SelectCharacter does an
    /// unconditional <c>StartingRelics[0]</c>, so an empty list throws
    /// ArgumentOutOfRangeException mid-method: the panel text updates, but the
    /// relic widget keeps the previous character's data and the lobby's
    /// character assignment never runs -- the character reads as selected while
    /// the run silently starts as whoever was chosen before. A character with no
    /// starting relic is not a supported state in this game.
    /// </remarks>
    public override IReadOnlyList<RelicModel> StartingRelics => new RelicModel[]
    {
        ModelDb.Relic<Relics.PoundingSurprise>(),
    };

    // ---- pck-backed art (klee.pck; the game loads it via manifest has_pck).
    // Each override returns null when the resource is absent, which BaseLib's
    // prefixes treat as "fall through to the base game's default" -- so a
    // build without the pack behaves exactly like today.

    /// <summary>Roster tile on the character-select screen. This is the
    /// surface that casts to CompressedTexture2D, which forced the pck route
    /// in the first place (see KleeArt / KleePck).</summary>
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("klee/ui/select_portrait.png");

    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("klee/ui/select_portrait_locked.png");

    /// <summary>Top-panel character icon during a run.</summary>
    public override string? CustomIconTexturePath =>
        KleePck.Path("klee/ui/char_icon.png");

    public override string? CustomMapMarkerPath =>
        KleePck.Path("klee/ui/map_marker.png");

    /// <summary>The big splash behind the info panel when Klee is picked on
    /// the select screen. The scene mirrors the base game's char_select_bg_*
    /// structure (center-anchored Control) with the Klee Wish splash as a
    /// covered TextureRect instead of a spine rig.</summary>
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("klee/ui/char_select_bg_klee.tscn");

    /// <summary>Threshold-wipe ShaderMaterial (same shader as the base game's
    /// transition materials) over a procedural radial-blast texture.</summary>
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("klee/materials/klee_transition_mat.tres");

    // Rest-site and merchant art: BaseLib registers these paths for scene
    // conversion (RegisterSceneConversions) and its factories accept a bare
    // Sprite2D root, generating the full NRestSiteCharacter /
    // NMerchantCharacter node trees around the texture.
    //
    // The two paths MUST differ even though the scenes are identical:
    // BaseLib's conversion registry is keyed by path, and a second
    // registration overwrites the first -- sharing one scene sent an
    // NMerchantCharacter to the campfire and softlocked NRestSiteRoom._Ready
    // on the cast (first-campfire softlock, fixed 2026-07-20).
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("klee/model/rest_character.tscn");

    // Known-benign log error at each merchant visit: NMerchantCharacter._Ready
    // unconditionally builds a MegaSpineBinding on its first child and throws
    // on a static Sprite2D. Godot's bridge logs and swallows it; the sprite
    // still renders, only the "relaxed_loop" idle is lost. Unfixable without
    // patching game code -- accepted.
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("klee/model/character_sprite.tscn");

    /// <summary>On-screen combat model. BaseLib's factory builds the whole
    /// NCreatureVisuals tree (Bounds, CenterPos, IntentPos, ...) from a bare
    /// Texture2D, sized from the texture with feet at ground level -- which is
    /// exactly how combat_model.png is authored (alpha-trimmed, bottom
    /// anchored, 240x280). Null falls through to the base scene lookup.</summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        string? path = KleePck.Path("klee/model/combat_model.png");
        if (path == null)
        {
            return null;
        }
        return NodeFactory<NCreatureVisuals>.CreateFromResource(
            ResourceLoader.Load<Texture2D>(path));
    }

    public override float AttackAnimDelay => 0.15f;

    public override float CastAnimDelay => 0.25f;

    public override Color EnergyLabelOutlineColor => new Color("7A2418FF");

    public override Color DialogueColor => new Color("8C2F22");

    public override VfxColor SpeechBubbleColor => VfxColor.Swamp;

    public override Color MapDrawingColor => new Color("C4472F");

    public override Color RemoteTargetingLineColor => new Color("E85A4FFF");

    public override Color RemoteTargetingLineOutline => new Color("7A2418FF");

    public override List<string> GetArchitectAttackVfx() => new()
    {
        "vfx/vfx_attack_slash",
    };
}
