using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Kokomi.Generated;
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
/// Sangonomiya Kokomi -- the card-economy Hydro strategist.
///
/// She converts CARDS into damage and never HP: every card rotated off the
/// line pays Charge through the Pearl of Wisdom funnel, and Charge is read,
/// never spent. Her four sheet laws are enforced elsewhere and named here so
/// the character file is not the one place they are invisible: LAW 1 no
/// self-damage, LAW 2 no heals, LAW 3 she cannot gain Strength (converted to
/// Charge at the apply chokepoint, see KokomiResourceHooks), LAW 4 Commons
/// never grow the deck.
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
            "Divine Priestess of Watatsumi Island, and the strategist who "
          + "wins by spending everything except lives."),
        ("titleObject", "Kokomi"),
        ("pronounSubject", "she"),
        ("pronounObject", "her"),
        ("pronounPossessive", "hers"),
        ("possessiveAdjective", "her"),
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
    /// TWELVE cards, not ten -- the Silent shape, [USER]-ruled in the v0.4
    /// starter rework and transcribed from characters/kokomi.yaml
    /// `starting_deck` in sheet order.
    ///
    /// Two reasons, both hers. (1) Her opening deck already exhausts, and a
    /// 10-card deck that mills itself risks decking out early; the extra two
    /// are the buffer. (2) Starters are supposed to be bad and supposed to
    /// leave -- two more mediocre cards is a real dilution cost, and
    /// Tactical Retreat's thinning is how she pays it down.
    ///
    /// Shape: 4 Strike + 4 Defend + 2 Companions + 2 mechanic cards (the
    /// Charge teacher and the exhaust teacher). NO AoE, by ruling: "no one
    /// starts the game with AoE; if you need it, you draft it" -- Surging
    /// Shoal and Waterspout both stay in the pool.
    ///
    /// Sayu is the RANDOMIZED slot (Sayu or Shinobu, rolled off the run
    /// seed); Gorou always enlists, for lore reasons (R52 N3). The swap
    /// happens in KokomiStartingCompanionsPatch, because seeded RNG does not
    /// exist yet at the moment this property is read.
    /// </summary>
    public override IEnumerable<CardModel> StartingDeck => new CardModel[]
    {
        ModelDb.Card<WatersEdge>(),
        ModelDb.Card<WatersEdge>(),
        ModelDb.Card<WatersEdge>(),
        ModelDb.Card<WatersEdge>(),
        ModelDb.Card<CoralGuard>(),
        ModelDb.Card<CoralGuard>(),
        ModelDb.Card<CoralGuard>(),
        ModelDb.Card<CoralGuard>(),
        ModelDb.Card<GorouInuzakaCharge>(),
        ModelDb.Card<SayuDarumaGift>(),
#if PROTOTYPE_CARDS
        // QUARANTINED, v4 BASE KIT (sec.12.6 items 5 and 6). THE ONE STARTER
        // SEAM: with the flag on this slot is "To the Front!" and with it off
        // it is Bake-Kurage, byte for byte. The sheet does not move -- only
        // this list does, and only under the flag. The reasoning, the three
        // Musters that lost and the sim twin (`loader._starter_ids`) are on
        // KurageMemory.StarterSlotEleven.
        Powers.KurageMemory.StarterSlotEleven(),
#else
        ModelDb.Card<BakeKurage>(),
#endif
        ModelDb.Card<TacticalRetreat>(),
    };

    /// <summary>
    /// Pearl of Wisdom. It is the FICTION of the exhaust rule and the place
    /// its tooltip lives; the accrual itself is gated on character identity
    /// in KokomiResourceHooks, so a player who somehow loses the relic does
    /// not lose the character.
    /// </summary>
    public override IReadOnlyList<RelicModel> StartingRelics =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.PearlOfWisdomRelic>(),
        };

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
    /// Combat model. Klee and Furina run a scene-first chain against their
    /// convention combat.tscn; Kokomi has no rig yet, so this is the static
    /// half of that chain and nothing else.
    ///
    /// Deliberately NOT written as "try the scene, then fall back". A branch
    /// that probes a path no build step produces is dead on every run, and a
    /// dead branch reads as a working feature -- the failure mode this file's
    /// own logging discipline is aimed at. When her rig ships, the scene
    /// branch comes back with it, together with the scene.
    ///
    /// A null return is correct and safe here: the base scene lookup takes
    /// over, so she is visible and playable while Track D is outstanding.
    /// </summary>
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        MegaCrit.Sts2.Core.Logging.Log.Info(
            $"[{KleeMod.ModId}] Kokomi has no convention combat scene yet; "
            + "using static combat_model.png (expected until her art pass "
            + "lands -- see KleeSceneTelemetry's EXPECTED MISSING list)");
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
