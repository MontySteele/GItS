using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE COMPANION STAND-IN SEAM (QUARANTINED, <c>COMPANION_OVERHAUL</c>).
///
/// A STAND-IN IS NOT A POOL MEMBER. It is a whole Klee-only card, with its own
/// unique name, handed to Klee IN PLACE of one named Universal (Klee brief pick
/// 6; the approved Mondstadt workshop sec.1; R236 sec.3). Everything below
/// follows from that one sentence:
///
///   * it never enters ANY pool on its own. None of the types is in
///     <see cref="CompanionOverhaulRoster"/>, which is the ONE door
///     <see cref="CompanionPool.All"/> opens, so the reward slot, the shop and
///     the Featured Banner are all structurally unable to see one;
///   * it is reached at the HAND-OFF and nowhere else. Each offer surface calls
///     <see cref="HandOff"/> on the card it has already PICKED, so the
///     eligibility lists, the rarity roll and the weighted draw are the
///     Universal's own and THE OFFER ODDS DO NOT MOVE;
///   * every other character is handed the Universal, because the swap is
///     keyed on the stand-in's own <c>PersonalPool</c>.
///
/// SIM TWIN: <c>tier0.engine.companion_standins</c>, called from the same two
/// mouths (<c>tier05.rewards.roll_rewards</c> and
/// <c>tier05.shop.companion_offers</c>).
///
/// THE PAIR TABLE IS LISTED BY TYPE, the same asymmetry
/// <see cref="CompanionOverhaulRoster"/> argues for its own list: a deleted row
/// takes its class with it and this file stops building, where a table of id
/// strings would fail silently the day a row is renamed. The sim derives the
/// same map from the sheet's <c>replaces:</c> key, and
/// <c>tier0/tests/test_companion_standins.py</c> pins the two against each
/// other by id.
///
/// PUBLIC rather than internal, for the reason <c>ProtoBombPower.Charges</c>
/// gives: KleeTests is a separate assembly, the decision <see cref="HandOffTo"/>
/// takes is the whole of this seam, and the alternative was an
/// <c>InternalsVisibleTo</c> nothing else in this mod needs or an IL-shape
/// assertion standing in for the decision itself -- which is exactly the
/// substitution that let the defect below ship.
/// </summary>
public static class CompanionStandIns
{
    /// <summary>
    /// The pairs, Universal -> stand-in, in the sheet's own order. EMPTY SINCE
    /// THE KLEE-ONLY COMPANIONS (2026-10-03,
    /// <c>review/active/mondstadt-companions-2026-10-03.md</c> sec.4): four
    /// caretakers were cut (Diona, Noelle, Kaeya, Barbara) and Jean's Lion's
    /// Fang is in Klee's own draftable pool. The seam stays with nothing to
    /// hand off; <c>C.COMPANION_STANDIN_IDS</c> is its empty sim twin.
    /// </summary>
    private static IReadOnlyList<(CardModel Universal, CardModel StandIn)>? _pairs;

    private static IReadOnlyList<(CardModel, CardModel)> Pairs() =>
        _pairs ??= Array.Empty<(CardModel, CardModel)>();

    /// <summary>Test seam: forget the cache. The mod never calls it.</summary>
    internal static void ResetAll() => _pairs = null;

    /// <summary>
    /// THE HAND-OFF, and the whole seam in this engine.
    ///
    /// Called on a card a surface has already picked, immediately before it is
    /// instantiated for the player: <see cref="CompanionSlot.Roll"/> (the
    /// fourth reward slot) and <c>MerchantCompanionSlots.AddSlot</c> (both shop
    /// slots). Returns <paramref name="picked"/> unchanged for every character
    /// but the stand-in's own, and with the arm off.
    ///
    /// THE BANNER IS NOT A MOUTH, deliberately. It decides WHICH five-stars are
    /// featured, and it decides that about Universals; a stand-in carries a
    /// <c>PersonalPool</c>, which the banner's roster excludes by the same rule
    /// that keeps Klee's Personals off it.
    /// </summary>
    internal static CardModel HandOff(CardModel picked, Player player)
    {
        return HandOffTo(picked, CompanionPool.CharacterId(player), Pairs());
    }

    /// <summary>
    /// THE DECISION, with the pair table handed in instead of resolved, and
    /// the only reason it is a second method is that the PINS could not reach
    /// the first: <see cref="Pairs"/> goes through <c>ModelDb</c> and
    /// <see cref="HandOff"/> takes a <c>Player</c>, both outside the headless
    /// boundary (KleeTests/README), so the seam's own rule had no C# pin at all
    /// -- which is how it shipped broken. `CompanionStandInHandOffTests` calls
    /// THIS with two cards it constructed itself.
    ///
    /// THE COMPARISON IS THE WHOLE RULE, and it is a STRING one: the stand-in's
    /// <c>PersonalPool</c> must BE the character id
    /// <see cref="CompanionPool.CharacterId"/> returns. It was not. The codegen
    /// emitted a Python list repr (<c>"['klee']"</c>) for a row that spells
    /// `personal_pool:` as a one-member list, so this loop matched the pair,
    /// failed the second test and handed Klee the Universal at both mouths --
    /// silently, and in the engine the player plays, while the sim swapped
    /// correctly the whole time (`tools/gen_klee_cards.personal_pool_id` is the
    /// fix and `tier0.engine.state.Card.from_dict` the twin it was missing).
    /// </summary>
    public static CardModel HandOffTo(
        CardModel picked, string? characterId,
        IReadOnlyList<(CardModel Universal, CardModel StandIn)> pairs)
    {
        if (characterId == null) return picked;
        foreach (var (universal, standIn) in pairs)
        {
            if (!ReferenceEquals(universal, picked)) continue;
            if ((standIn as ICompanionCard)?.PersonalPool != characterId)
            {
                continue;
            }
            return standIn;
        }
        return picked;
    }
}

/// <summary>
/// Jean, Lion's Fang, Fair Protector: "At the start of your turn, if none of
/// your Bombs went off last turn, gain 8 Block and draw 1 card."
///
/// GROUNDED'S SHAPE WITH A CARD ON IT, and it reads the ledger the same way for
/// the same reason: <c>For</c> rolls to this round, so <c>SetOffLastTurn</c> is
/// exactly the count that stood when the player last passed.
///
/// In Klee's own draftable pool since the Klee-only companions (2026-10-03);
/// no longer a stand-in.
/// </summary>
public sealed class LionsFangPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lion's Fang, Fair Protector"),
        ("description",
            "At the start of your turn, if none of your [gold]Bombs[/gold] "
          + "went off last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and draw 1 card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        if (Amount <= 0) return;
        if (KleeOverhaulLedger.For(Owner).SetOffLastTurn > 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
        // A LITERAL 1, in both engines and for the reason tier0's
        // `MC_LIONS_FANG_DRAW` comment gives: naming it would make
        // `lint_prose_constants` read every "Draw 1 card" in the mod as an
        // un-interpolated copy of this slice's constant. The row's own
        // `description:` is what both engines print.
        await CardPileCmd.Draw(choiceContext, 1, player);
    }
}
