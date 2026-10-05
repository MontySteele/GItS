using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
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

/// <summary>
/// Sangonomiya Kokomi -- the Hydro strategist who plans a turn ahead.
///
/// Her kit is the Plan: a card played on the Bake-Kurage
/// (Powers/Prototype/BakeKuragePet.cs) writes its Plan line, and at the
/// start of her next turn the jellyfish carries it out
/// (Powers/Prototype/KokomiPlan.cs). The Tamakushi Casket counts those
/// carry-outs. Her cards are the `proto_kk_` rows of
/// docs/prototype-surface.yaml.
///
/// IKokomiCharacter is the identity gate for all of that. It is on the
/// CHARACTER, not the cards, so a Kokomi card acquired by Klee in co-op does
/// not hand him her engine.
/// </summary>
public sealed class Kokomi : CustomCharacterModel, IKokomiCharacter
{
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kokomi"),
        ("description",
            "Divine Priestess of Watatsumi Island, a strategist who plans "
          + "a turn ahead."),
        ("titleObject", "Kokomi"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
        // The rest of the base game's per-character rows (BaseLib's
        // CharacterLoc set plus bestiaryQuote). A missing row renders as
        // its raw key: the co-op end-turn ping bubble did (playtest
        // 2026-10-03). CharacterLocCompletenessTests pins the set.
        ("aromaPrinciple", "[sine][blue]Every move is planned. I will not be rushed.[/blue][/sine]"),
        ("banter.alive.endTurnPing", "Whenever you're ready. The plan holds."),
        ("banter.dead.endTurnPing", "..."),
        ("bestiaryQuote", "I have no notes on this one yet."),
        ("eventDeathPrevention", "Watatsumi still needs its Priestess."),
        ("goldMonologue", "[sine]This will keep Watatsumi's army supplied...[/sine]"),
        ("cardsModifierTitle", "Kokomi Cards"),
        ("cardsModifierDescription", "Kokomi cards will now appear in rewards and shops."),
    };

    public override Color NameColor => new("6FC8D6");

    public override CharacterGender Gender => CharacterGender.Feminine;

    protected override CharacterModel? UnlocksAfterRunAs => null;

    /// <summary>tier0 characters/kokomi.yaml `hp: 80`. RULED R52 ask 8 at
    /// 70 -- higher than Klee's and Furina's because the stability fantasy
    /// wants headroom, and because her deck is a second resource bar she is
    /// already paying out of. Raised to 80 by sitting slate 2026-08-29 --
    /// "Furina and Kokomi are canonically HP-scalers ... Kokomi be high,
    /// relative to the base cast." High = the base cast's top, Ironclad's
    /// 80 (Defect 75 / Regent 75 / Silent 70 / Necrobinder 66).</summary>
    public override int StartingHp => 80;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool =>
        ModelDb.CardPool<KokomiCardPool>();

    public override RelicPoolModel RelicPool =>
        ModelDb.RelicPool<KokomiRelicPool>();

    public override PotionPoolModel PotionPool =>
        ModelDb.PotionPool<SilentPotionPool>();

    /// <summary>
    /// The base Strike x4, Defend x4, Kurage's Oath and Slack Water
    /// (<c>KokomiOverhaulRoster.StartingDeck</c>).
    /// </summary>
    public override IEnumerable<CardModel> StartingDeck =>
        Powers.KokomiOverhaulRoster.StartingDeck();

    /// <summary>Tamakushi Casket (<c>KokomiOverhaulRoster.StartingRelics</c>).</summary>
    public override IReadOnlyList<RelicModel> StartingRelics =>
        Powers.KokomiOverhaulRoster.StartingRelics();

    // ART: none of these files exist yet (Track D). Every KleePck.Path call
    // returns null on a miss and the game falls back to its own defaults, so
    // she is PLAYABLE on placeholders -- which is the point of landing the
    // shell before the art hunt. Paths are declared now so the art pass is a
    // pure file drop with no code change, and so KleeSceneTelemetry names
    // each miss at boot instead of leaving it to be noticed on screen.
    public override string? CustomCharacterSelectIconPath =>
        KleePck.Path("kokomi/ui/select_portrait.png");
    public override string? CustomCharacterSelectLockedIconPath =>
        KleePck.Path("kokomi/ui/select_portrait_locked.png");
    public override string? CustomIconTexturePath =>
        KleePck.Path("kokomi/ui/char_icon.png");
    // The halo behind the icon, not a stroke around it -- see the note on
    // Klee.CustomIconOutlineTexturePath for the measured convention (EB-37).
    // Derived from the fill by tools/gen_char_icon_outlines.py.
    public override string? CustomIconOutlineTexturePath =>
        KleePck.Path("kokomi/ui/char_icon_outline.png");
    /// <summary>
    /// combat_visuals.tscn, NOT the convention combat.tscn Klee and Furina
    /// use. Hers does not exist -- there is no rig to put in it until the art
    /// pass lands -- and the `?? ` chain that used to name it anyway was the
    /// exact shape S6c exists to catch: source that references a PCK resource
    /// nothing produces, made invisible by a fallback. The gate cannot read
    /// intent, and neither can the next person.
    ///
    /// The aspiration lives in KleeSceneTelemetry's EXPECTED MISSING list,
    /// which is the honest home for it. When her rig ships, the scene and the
    /// reference come back together.
    /// </summary>
    public override string? CustomVisualPath =>
        KleePck.Path("kokomi/model/combat_visuals.tscn");
    public override string? CustomIconPath =>
        KleePck.Path("kokomi/ui/character_icon.tscn");
    public override string? CustomEnergyCounterPath =>
        "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn";
    public override string? CustomTrailPath =>
        "res://scenes/vfx/card_trail_ironclad.tscn";
    public override string? CustomMapMarkerPath =>
        KleePck.Path("kokomi/ui/map_marker.png");
    public override string? CustomCharacterSelectBg =>
        KleePck.Path("kokomi/ui/char_select_bg_kokomi.tscn");
    public override string? CustomCharacterSelectTransitionPath =>
        KleePck.Path("kokomi/materials/kokomi_transition_mat.tres");
    public override string? CustomRestSiteAnimPath =>
        KleePck.Path("kokomi/model/rest_character.tscn");
    public override string? CustomMerchantAnimPath =>
        KleePck.Path("kokomi/model/merchant_character.tscn");

    /// <summary>
    /// Combat model, scene-first like Klee and Furina: the layer-cut rig at
    /// kokomi/model/combat.tscn (fences in tools/combat_layer_fences/kokomi.yaml),
    /// which carries %Facing and %AnimationTree, so CreatureAnimationRouter,
    /// the death seam and the facing fix all apply with no code of hers.
    /// Falls back to the static 240x280 combat_model.png when the pck predates
    /// the rig; a null return hands the game its own scene lookup.
    /// </summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        string? scenePath = KleePck.Path("kokomi/model/combat.tscn");
        if (scenePath != null)
        {
            var visuals = NodeFactory<NCreatureVisuals>.CreateFromScene(scenePath);
            MegaCrit.Sts2.Core.Logging.Log.Info(
                $"[{KleeMod.ModId}] combat visuals from convention scene "
                + $"{scenePath}: {visuals.GetType().Name}");
            return visuals;
        }

        MegaCrit.Sts2.Core.Logging.Log.Warn(
            $"[{KleeMod.ModId}] Kokomi convention combat scene missing; falling "
            + "back to static combat_model.png (pck stale? rebuild with "
            + "tools/build_pck.ps1)");
        var path = KleePck.Path("kokomi/model/combat_model.png");
        return path == null
            ? null
            : NodeFactory<NCreatureVisuals>.CreateFromResource(
                ResourceLoader.Load<Texture2D>(path));
    }

    // Started at the roster's shared values. Hers are a taste call that
    // cannot be made before there is an animation to time them against, so
    // they stay parked rather than guessed.
    public override float AttackAnimDelay => 0.15f;

    public override float CastAnimDelay => 0.25f;

    public override Color EnergyLabelOutlineColor => new("1E5A6B");
    public override Color DialogueColor => new("2E7C8E");
    public override VfxColor SpeechBubbleColor => VfxColor.Swamp;
    public override Color MapDrawingColor => new("6FC8D6");
    public override Color RemoteTargetingLineColor => new("6FC8D6FF");
    public override Color RemoteTargetingLineOutline => new("1E5A6BFF");

    public override List<string> GetArchitectAttackVfx() => new()
    {
        "vfx/vfx_attack_slash",
    };
}
