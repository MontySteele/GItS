using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// FURINA POOL COMPLETION (2026-10-01, QUARANTINED under the Stage arm):
/// paper sec.5's three new rules -- The Last Act's seat discount (the cost
/// hook is <c>FurinaStageHooks.TryModifyEnergyCostInCombat</c>), Casting
/// Agent's choice, Critics' Darling and Star Turn -- and her second Ancient's
/// free Spend (Center of Attention, game-side only). Paper
/// <c>review/active/pool-completion-2026-10-01.md</c>. Sim twins:
/// <c>tier0/engine/furina_stage.py</c>, same names.
/// </summary>
public static partial class FurinaStage
{
    /// <summary>How many of her seats hold nobody: capacity (three, four
    /// under Sold Out) less the performers on stage, never below 0. <i>The
    /// Last Act</i>'s discount. Sim twin: <c>furina_stage.empty_seats</c>.
    /// </summary>
    public static int EmptySeats(Creature? owner) =>
        !LiveFor(owner) ? 0 : System.Math.Max(0, CapacityOf(owner) - Of(owner).Count);

    /// <summary>
    /// <i>Casting Agent</i>: "Choose 1 of 3 random Guest Star cards and add it
    /// to your hand. It costs 0 this turn [and is upgraded]."
    ///
    /// THREE DIFFERENT CARDS, drawn without replacement from the Guest Cast's
    /// ten (<see cref="FurinaStageRoster.GuestStarCards"/>) on the shared
    /// <c>CombatTargets</c> stream, shown on the game's choose-a-card screen
    /// (Dual Nature's door). The chosen copy is a combat card: it costs 0
    /// this turn (<c>EnergyCost.SetThisTurn</c>, the Guest Star generator's
    /// call) and is upgraded when <paramref name="card"/> is. A full hand
    /// takes nothing. Sim twin: <c>furina_stage.casting_agent</c>, whose pilot
    /// takes the first offered.
    /// </summary>
    public static async Task CastingAgent(PlayerChoiceContext choiceContext,
                                          CardModel card)
    {
        var player = card.Owner;
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var combat = owner!.CombatState;
        if (combat == null || player == null) return;
        if (CardPile.Get(PileType.Hand, player) is { } hand
            && hand.Cards.Count >= KokomiPoolCompletion.MaxHandSize)
        {
            return;
        }
        var remaining = FurinaStageRoster.GuestStarCards().ToList();
        var rng = player.RunState?.Rng?.CombatTargets;
        var options = new List<CardModel>();
        while (options.Count < FurinaStageLaw.CastingAgentOffer
               && remaining.Count > 0)
        {
            var pick = rng != null ? rng.NextItem(remaining) : remaining[0];
            if (pick == null) break;
            remaining.Remove(pick);
            options.Add(combat.CreateCard(pick, player));
        }
        if (options.Count == 0) return;
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, player, canSkip: false);
        if (selected == null) return;
        if (card.IsUpgraded && !selected.IsUpgraded) selected.UpgradeInternal();
        selected.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(selected, PileType.Hand,
                                                    player);
    }

    /// <summary>
    /// <i>Critics' Darling</i>: "Whenever you choose a Spend mode, deal damage
    /// equal to the Fanfare spent to ALL enemies." From <see cref="Spend"/>,
    /// which only a chosen Spend mode reaches, after the payment and its Bow;
    /// unpowered and unelemented, like an act; once per copy. A payment of 0
    /// (Center of Attention's free Spend) deals nothing. Sim twin:
    /// <c>furina_stage.critics_darling</c>.
    /// </summary>
    internal static async Task CriticsDarling(PlayerChoiceContext choiceContext,
                                              Creature owner, int paid)
    {
        if (paid <= 0 || !LiveFor(owner)) return;
        var copies = (int)owner.Powers.OfType<CriticsDarlingPower>()
            .Sum(p => p.Amount);
        for (var i = 0; i < copies; i++)
        {
            foreach (var enemy in Enemies(owner).ToList())
            {
                if (enemy.IsDead) continue;
                await ElementalHit.DealUnelemented(choiceContext, enemy, paid,
                                                   owner, powered: false);
            }
        }
    }

    /// <summary>
    /// <i>Star Turn</i>: "Whenever a Guest Star joins the stage, it performs at
    /// once." Bends rule 3 (`EB-738`: a newcomer never acts on arrival). From
    /// <see cref="GuestStar"/>, after the arrival and Star Billing's draw,
    /// however the guest arrived; its own seat acts once per copy through
    /// <see cref="Perform"/>, the one act every caller uses (so it pays as any
    /// act does). A guest no longer on stage does not act. Sim twin:
    /// <c>furina_stage.star_turn</c>.
    /// </summary>
    internal static async Task StarTurn(PlayerChoiceContext choiceContext,
                                        Creature owner, StagePerformer who)
    {
        if (!LiveFor(owner)) return;
        var copies = (int)owner.Powers.OfType<StarTurnPower>().Sum(p => p.Amount);
        for (var i = 0; i < copies; i++)
        {
            if (owner.IsDead || CombatOver()) return;
            if (FurinaStageLedger.For(owner).SeatOf(who) is not { } seat) return;
            await Perform(choiceContext, owner, seat);
        }
    }
}

/// <summary><i>Critics' Darling</i> (pool completion): the Power is read at the
/// Spend site (<see cref="FurinaStage.CriticsDarling"/>). Copies add.</summary>
public sealed class CriticsDarlingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Critics' Darling"),
        ("description",
            "Whenever you choose a [gold]Spend[/gold] mode, deal damage equal "
          + "to the [gold]Fanfare[/gold] spent to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Star Turn</i> (pool completion): read at the guest's arrival
/// (<see cref="FurinaStage.StarTurn"/>). Copies add.</summary>
public sealed class StarTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star Turn"),
        ("description",
            "Whenever a Guest Star joins the stage, it acts at once."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// CENTER OF ATTENTION, Furina's second Ancient (pool completion, 2026-10-01;
/// <c>Cards/Furina/CenterOfAttention.cs</c>): "The first Spend you choose each
/// turn takes no Fanfare." The Furina rules pass (2026-10-01) dropped its
/// "and you can choose it even when your back performer has too little"
/// clause: rule 8 now pays back first, then forward, so the mode is offered
/// on the same board as any Spend (the whole stage holds the price).
///
/// <see cref="Covers"/> is a READ (nothing gates on it since the rules pass);
/// <see cref="TryClaim"/> is the payment's CLAIM (<c>FurinaStage.Spend</c>
/// takes nothing). The latch is this power's own
/// round number, so it opens again at the next turn. Game-side only, like
/// every Ancient (the sim models no events).
/// </summary>
public sealed class CenterOfAttentionPower : PowerModel, ILocalizationProvider
{
    private int _claimedRound = -1;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Center of Attention"),
        ("description",
            "The first [gold]Spend[/gold] you choose each turn takes no "
          + "[gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    private static int Round(Creature owner) =>
        owner.CombatState?.RoundNumber ?? 0;

    private static CenterOfAttentionPower? Open(Creature? owner)
    {
        if (owner == null || !FurinaStage.Occupied(owner)) return null;
        var power = owner.Powers.OfType<CenterOfAttentionPower>().FirstOrDefault();
        if (power == null || power._claimedRound == Round(owner)) return null;
        return power;
    }

    /// <summary>Is the turn's free Spend still open, with someone on stage?
    /// A read: the chooser may ask as often as it likes.</summary>
    public static bool Covers(Creature? owner) => Open(owner) != null;

    /// <summary>Take the turn's free Spend: true once a turn, with someone on
    /// stage.</summary>
    public static bool TryClaim(Creature owner)
    {
        var power = Open(owner);
        if (power == null) return false;
        power._claimedRound = Round(owner);
        return true;
    }
}
