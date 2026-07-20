using System;
using System.Collections.Generic;
using BaseLib.Abstracts;
using Godot;
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

    // C1 STUB: Klee has no relic/potion pools yet. Borrowing Silent's keeps the
    // run loop functional; character relics/potions v0.1 are a C3 item.
    public override RelicPoolModel RelicPool => ModelDb.RelicPool<SilentRelicPool>();

    public override PotionPoolModel PotionPool => ModelDb.PotionPool<SilentPotionPool>();

    /// <remarks>Spec C1.4: 4x Kaboom, 4x Duck and Cover, 1x Jumpy Dumpty, 1x Pop.</remarks>
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
    /// C1 STUB: borrows Ironclad's Burning Blood. Klee's real starting relic is
    /// Pounding Surprise, which depends on the Sparks system (spec C2.3).
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
        ModelDb.Relic<BurningBlood>(),
    };

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
