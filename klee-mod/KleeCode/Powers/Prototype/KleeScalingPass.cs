using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE KLEE SCALING PASS (staging branch `klee-next`, 2026-10-05,
/// `review/active/klee-scaling-pass-2026-10-05.md` sec.4, ruled at its
/// defaults). Where its four pieces live:
///
///   * A, Klee's Secret Base, is v3 now ("At the start of your turn, place a
///     Bomb 4 [6] on a random enemy"): <see cref="SecretBasePower"/> and the
///     start-of-turn sequencer, not here. The first draft's placement bonus
///     and its card-face fold are gone.
///   * B, Witch's Homework (the grant-only `proto_ko_witchs_homework_next`
///     row): "Place a Bomb 6. When it goes off, this card's Bomb is 2 [3]
///     larger for the rest of the run." The charge carries a MARK
///     (<see cref="ProtoBombPower.ProtoCharge.Homework"/>) that a jump and a
///     merge keep and a copy never gets, and the card's growth persists the
///     base game's Genetic Algorithm way: a <c>[SavedProperty]</c> on the card,
///     written on the combat copy and on its <c>DeckVersion</c>.
///   * D's test relic lives in <c>Relics/PoundingSurpriseNext.cs</c>.
///
/// C (Boom Badge) is a number in <see cref="BoomBadgePower.FactorFor"/>.
/// </summary>
public static class KleeScalingPass
{
    /// <summary>
    /// Every Witch's Homework card these two marks name, once each. A merge
    /// (Exquisite Compound) carries ALL the marks it swallowed, so two
    /// Homework Bombs merged into one still grow both cards.
    /// </summary>
    public static CardModel[]? MergeMarks(CardModel[]? into, CardModel[]? more)
    {
        if (more == null || more.Length == 0) return into;
        if (into == null || into.Length == 0) return more;
        return into.Concat(more).Distinct(ReferenceEqualityComparer.Instance)
                   .Cast<CardModel>().ToArray();
    }

    /// <summary>
    /// Witch's Homework's play: one Bomb of the card's printed (grown) size on
    /// <paramref name="target"/>, marked with the card. The Dodoco Charm
    /// still applies -- it is a placement.
    /// </summary>
    public static async Task PlaceHomework(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel card, int size)
    {
        if (target == null) return;
        await ProtoBombPower.Place(choiceContext, target, size, isMine: false,
                                   payloadMineAll: 0, applier, card,
                                   homework: new[] { card });
    }

    /// <summary>
    /// A charge went off (<c>ProtoBombPower.Explode</c>). For each Homework
    /// card its mark names, grow that card once this combat
    /// (<see cref="KleeOverhaulLedger.TakeHomework"/>): "It grows at most
    /// once a combat, whatever replays it."
    /// </summary>
    public static void AfterHomeworkWentOff(
        Creature applier, ProtoBombPower.ProtoCharge charge)
    {
        if (charge.Homework == null || charge.Homework.Length == 0) return;
        var ledger = KleeOverhaulLedger.For(applier);
        foreach (var card in charge.Homework)
        {
            if (card is not IHomeworkCard homework) continue;
            if (!ledger.TakeHomework(DeckKey(card))) continue;
            Grow(card, homework.HomeworkStep);
        }
    }

    /// <summary>The run-long Bomb a Witch's Homework card places now: its
    /// base plus its saved growth. Fight telemetry's
    /// <c>homework_bomb_size</c> reads it off each deck card.</summary>
    public static int RunBombSize(IHomeworkCard card) =>
        card.HomeworkBaseSize + card.HomeworkGrowth;

    /// <summary>The card the once-a-combat latch is keyed by: the deck card
    /// this combat copy came from, or the card itself.</summary>
    public static CardModel DeckKey(CardModel card) => card.DeckVersion ?? card;

    /// <summary>
    /// "This card's Bomb is N larger for the rest of the run": the combat
    /// copy grows (a replay this fight places the bigger Bomb) and so does
    /// its deck card, which is what persists -- Genetic Algorithm's
    /// <c>BuffFromPlay</c> on <c>this</c> and on <c>DeckVersion</c>.
    /// </summary>
    public static void Grow(CardModel card, int step)
    {
        if (step <= 0) return;
        if (card is IHomeworkCard combatCopy) combatCopy.HomeworkGrowth += step;
        if (card.DeckVersion is IHomeworkCard deck
            && !ReferenceEquals(card.DeckVersion, card))
        {
            deck.HomeworkGrowth += step;
        }
    }
}

/// <summary>
/// The generated Witch's Homework card (the `plant_homework_bomb` op). Its
/// growth is a <c>[SavedProperty]</c> on the card, so a save and load keep it.
/// </summary>
public interface IHomeworkCard
{
    /// <summary>How much this card's Bomb has grown this run.</summary>
    int HomeworkGrowth { get; set; }

    /// <summary>What one growth adds: 2, or 3 upgraded.</summary>
    int HomeworkStep { get; }

    /// <summary>The printed Bomb before any growth: 6.</summary>
    int HomeworkBaseSize { get; }
}
