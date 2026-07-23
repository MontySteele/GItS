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
/// GenerateAnimator is STILL deliberately NOT overridden — and as of
/// animation sprint 1 the reason is sharper than "the base works": NCreature
/// only builds a CreatureAnimator when Visuals.HasSpineAnimation, and Klee
/// ships no spine rig, so any override here would be dead code. The animation
/// regime is instead: combat visuals load from the script-less convention
/// scene klee/model/combat.tscn (BaseLib's NCreatureVisualsFactory converts
/// the root to a real NCreatureVisuals), and Vfx.KleeAnimationRouter routes
/// NCreature.SetAnimationTrigger / StartDeathAnim into the scene's
/// %AnimationTree when one exists. The Track-A scene is static (no tree), so
/// the router is inert until Track B ships klee2.tscn. Verified against
/// decompiled CharacterModel/NCreature v0.107.1 and BaseLib 2026-07-21.
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

    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("klee/ui/char_icon.png");

    // CharacterModel.AssetPaths preloads four id-derived scenes before any
    // room starts. CreateCustomVisuals and the texture overrides below affect
    // instantiation, not that preload list, so all four path overrides are
    // mandatory even when the visible art is created another way.
    //
    // combat.tscn is the animation-sprint convention scene (Track A). The
    // combat_visuals.tscn fallback keeps a pre-sprint pck bootable: BaseLib
    // registers whichever path this returns for NCreatureVisuals conversion,
    // and KleeSceneTelemetry shouts at boot when the convention scene is
    // missing.
    public override string? CustomVisualPath =>
        KleePck.Path("klee/model/combat.tscn")
        ?? KleePck.Path("klee/model/combat_visuals.tscn");

    public override string? CustomIconPath =>
        KleePck.Path("klee/ui/character_icon.tscn");

    // Temporary shared base-game surfaces. They are real N* scenes, so unlike
    // an id-derived missing path they are safe to preload and instantiate.
    public override string? CustomEnergyCounterPath =>
        "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";

    public override string? CustomTrailPath =>
        "res://scenes/vfx/card_trail_ironclad.tscn";

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

    /// <summary>On-screen combat model, scene-first as of animation sprint 1.
    ///
    /// Preferred path: instantiate the convention scene klee/model/combat.tscn
    /// through BaseLib's factory, which converts the script-less Node2D root
    /// into a real NCreatureVisuals and fills any missing named nodes
    /// (%Visuals / Bounds / %CenterPos / IntentPos). The scene's inventory
    /// mirrors what the texture route generated, so Track A is a pure
    /// re-plumbing: same art, same geometry, new channel — proven by boot
    /// telemetry rather than by eyeballing.
    ///
    /// Fallback 1 (pck predates the sprint): build from the bare 240x280
    /// bottom-anchored combat_model.png, exactly the pre-sprint behavior.
    /// Fallback 2 (no pck at all): null, base scene lookup. Every step logs —
    /// a silent path miss looks like "nothing happened" (sprint ordering law).
    /// </summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        string? scenePath = KleePck.Path("klee/model/combat.tscn");
        if (scenePath != null)
        {
            var visuals = NodeFactory<NCreatureVisuals>.CreateFromScene(scenePath);
            MegaCrit.Sts2.Core.Logging.Log.Info(
                $"[{KleeMod.ModId}] combat visuals from convention scene "
                + $"{scenePath}: {visuals.GetType().Name}");
            return visuals;
        }

        MegaCrit.Sts2.Core.Logging.Log.Warn(
            $"[{KleeMod.ModId}] convention combat scene missing; falling back "
            + "to static combat_model.png (pck stale? rebuild with "
            + "tools/build_pck.ps1)");
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
