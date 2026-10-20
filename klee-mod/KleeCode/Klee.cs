using System;
using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;
using KleeMod.Cards;
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
/// the root to a real NCreatureVisuals), and Vfx.CreatureAnimationRouter routes
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
///
/// IKleeCharacter is her identity gate, and it arrives late on purpose
/// (`EB-281`): she is the compatibility baseline, so every shipped site tests
/// <c>is Klee</c> directly and still does. The interface exists for the
/// prototype surface, where a patch runs on
/// every seat at the table and has to be able to say whose creature it is about
/// in the idiom Furina and Kokomi already use
/// (<c>tools/lint_prototype_patch_scope.py</c>). It declares nothing, so
/// carrying it costs her nothing.
/// </summary>
public sealed class Klee : CustomCharacterModel, Powers.IKleeCharacter
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
        // The intro (Klee story batch 1 sec.1), from her story table.
        ("description", Story.KleeStory.Table.Intro),
        ("titleObject", "Klee"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
        // The rest of the base game's per-character rows (BaseLib's
        // CharacterLoc set plus bestiaryQuote). A missing row renders as
        // its raw key: the co-op end-turn ping bubble did (playtest
        // 2026-10-03). CharacterLocCompletenessTests pins the set.
        ("aromaPrinciple", "[sine][red]Ooh... can I light the fuse?[/red][/sine]"),
        ("banter.alive.endTurnPing", "Hurry, hurry! Klee's ready!"),
        ("banter.dead.endTurnPing", "..."),
        ("bestiaryQuote", "I haven't seen this one before. Do you think it bites?"),
        ("eventDeathPrevention", "I'm still here! Don't leave without me!"),
        ("goldMonologue", "[sine]Enough for bomb supplies... and snacks for everyone![/sine]"),
        ("cardsModifierTitle", "Klee Cards"),
        ("cardsModifierDescription", "Klee cards will now appear in rewards and shops."),
    };

    // Klee red per spec C1.4; artist's final call later.
    public override Color NameColor => new Color("E85A4F");

    public override CharacterGender Gender => CharacterGender.Feminine;

    /// <remarks>C1: always available, no unlock gate while testing.</remarks>
    protected override CharacterModel? UnlocksAfterRunAs => null;

    /// <remarks>70 HP, Silent's (Klee final pass, 2026-10-02,
    /// review/active/klee-final-pass-2026-10-02.md pick 1; 62 before).</remarks>
    public override int StartingHp => 70;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool => ModelDb.CardPool<KleeCardPool>();

    // KleeRelicPool = Silent's borrowed contents + Pounding Surprise. The own
    // pool is REQUIRED, not cosmetic: RelicModel.Pool resolves through
    // AllRelicPools and throws for a relic in no pool, aborting character
    // select mid-method (finding 27). Her own seven are the Klee arm's
    // (Relics/KleeArmRelics.cs), offered only under it.
    public override RelicPoolModel RelicPool => ModelDb.RelicPool<KleeRelicPool>();

    // Her own three potions (review/active/relics-potions-klee-furina-2026-09-27.md,
    // pick 1(a)); the Silent borrow is gone.
    public override PotionPoolModel PotionPool =>
        ModelDb.PotionPool<Potions.KleePotionPool>();

    /// <remarks>
    /// The base Strike x4, Defend x4 and two kit cards
    /// (<c>KleeOverhaulRoster.StartingDeck</c>; sim twin
    /// <c>tier0/content/loader._starter_ids</c>).
    /// </remarks>
    public override IEnumerable<CardModel> StartingDeck =>
        Powers.KleeOverhaulRoster.StartingDeck();

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

    /// <summary>The halo BEHIND the icon, not a stroke around it. The base
    /// game's own outline texture is the fill's silhouette re-emitted as pure
    /// white with the shape entirely in alpha, grown ~4.5px on an 85px canvas
    /// (measured off character_icon_ironclad_outline.png in the shipped pack);
    /// NMultiplayerVoteContainer and NAncientDialogueLine both parent it under
    /// an "Outline" TextureRect. Returning the FILL here -- which all three
    /// characters did until EB-37 -- draws the icon twice and the halo never
    /// appears. tools/gen_char_icon_outlines.py derives it from the fill.</summary>
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("klee/ui/char_icon_outline.png");

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

    // Her own energy orb (card frames stage 2, 2026-10-20): a Pyro orb with
    // a scalloped ring, tools/gen_energy_orb_layers.py set "klee", in Furina's scene shape
    // (see Furina.CustomEnergyCounterPath for the five nodes and why the
    // base counter is the fallback for a stale pck).
    public override string? CustomEnergyCounterPath =>
        KleePck.Path("klee/ui/energy_counter.tscn")
        ?? "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";

    // Temporary shared base-game surface. It is a real N* scene, so unlike
    // an id-derived missing path it is safe to preload and instantiate.
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

    // NMerchantCharacter._Ready unconditionally builds a MegaSpineBinding on
    // its first child and throws on a static Sprite2D. Godot's bridge logged
    // and swallowed one per shop, for every character here, and that was
    // carried from 2026-07-20 as "unfixable without patching game code --
    // accepted". EB-274 patched the game code:
    // Patches/MerchantSpineBindingPatch.cs skips the binding when child 0 is
    // not a SpineSprite, which is the same test NRestSiteCharacter already
    // applies to its own children. The exception is gone.
    //
    // Since her model frames (2026-10-12) Klee has her own shop idle:
    // merchant_character.tscn (generated by tools/klee_rig) is stance B at
    // the base merchant's 1.7x, feet on the anchor, breathing on an
    // autoplaying AnimationPlayer -- no Spine needed. The old single-sprite
    // scene stays the fallback for a pack built before it.
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("klee/model/merchant_character.tscn")
        ?? KleePck.Path("klee/model/character_sprite.tscn");

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

    /// <summary>
    /// The hit lands as her thrown bomb does: the attack clip releases it at
    /// 0.45 s (combat.tscn %ThrownProjectile metadata/release) and it flies
    /// <see cref="Vfx.ThrownProjectile.FlightSeconds"/>. At the base's 0.15
    /// the damage landed before the bomb left her hand. Fast mode caps the
    /// wait at 0.25 s regardless (<c>CreatureCmd.TriggerAnim</c>).
    /// </summary>
    public override float AttackAnimDelay => 0.6f;

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
