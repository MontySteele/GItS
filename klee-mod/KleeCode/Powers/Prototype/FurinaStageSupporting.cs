using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE -- THE SUPPORTING POOL (2026-09-26).
///
/// The design is <c>review/active/furina-supporting-pool-2026-09-26.md</c>,
/// ruled with all four defaults and swept before the build: twenty-eight of
/// its twenty-nine cards (Sold Out, the fourth seat, is built beside them).
/// This file is their verbs -- the ones the generated `proto_fs_` rows call --
/// and the powers they place. Every bar move is the ledger's
/// (<see cref="FurinaStageLedger"/>), every verb is one early return with the
/// arm off, and every rule has its sim twin in
/// <c>tier0/engine/furina_stage.py</c>, named on each method.
///
/// WHERE EACH RULE SITS, for the reader looking for one:
///
///   * the seat moves -- Plot Twist, Lyney's swap, Stage Whisper, Revolving
///     Stage -- are ledger methods, so the end-of-turn forecast runs them;
///   * the fade's three benders (Held Applause, Echoing Hall, Eternal
///     Applause) are <see cref="FadeRules"/> and
///     <see cref="FurinaStageLedger.Fade(int, bool)"/>;
///   * Oratrice's Verdict is <see cref="ActTarget"/>, which every act's
///     random pick goes through;
///   * the turn-start powers are <see cref="TurnStartPowers"/>, called by
///     <c>FurinaStageHooks</c> right after rule 4's regen;
///   * Tide of Applause is <see cref="OnReaction"/>, called from the one site
///     the mod resolves a reaction.
/// </summary>
public static partial class FurinaStage
{
    /// <summary>
    /// Rule 12's line and Echoing Hall's echo for this owner, from the powers
    /// in play: the line is 10 with <see cref="EternalApplausePower"/> (any
    /// number of copies) and 5 without; the echo is on with any
    /// <see cref="EchoingHallPower"/>. The end-of-turn fade and the forecast
    /// both read it, so the two cannot disagree. Sim twin:
    /// <c>furina_stage.fade_threshold</c> and <c>furina_stage.fade</c>.
    /// </summary>
    public static (int Threshold, bool Echo) FadeRules(Creature owner) =>
        (owner.Powers.OfType<EternalApplausePower>().Any()
             ? FurinaStageLaw.EternalFadeThreshold
             : FurinaStageLaw.FadeThreshold,
         owner.Powers.OfType<EchoingHallPower>().Any());

    /// <summary><i>Counterclaim</i>'s predicate, `stage_front_hit`: did an
    /// enemy's hit reach the front performer's bar since the end of her last
    /// turn?</summary>
    public static bool FrontHitSinceLastTurn(Creature? owner) =>
        LiveFor(owner) && FurinaStageLedger.For(owner!).FrontHitSinceLastTurn;

    /// <summary><i>Da Capo</i>'s count, `stage_bows`: every Bow this combat,
    /// all causes.</summary>
    public static int Bows(CardModel? card) =>
        card?.Owner?.Creature is { } owner && LiveFor(owner)
            ? FurinaStageLedger.For(owner).BowsThisCombat
            : 0;

    /// <summary>`EB-747`'s two-moment reader for <i>Bring the House Down</i>:
    /// the front performer's live bar before the play, what the play took
    /// after.</summary>
    public static int SpentOrLeadFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : LeadFanfare(card);
    }

    /// <summary><i>Plot Twist</i>: reverse the order of the performers. Sim
    /// twin: <c>furina_stage.reverse</c>.</summary>
    public static void Reverse(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        if (!FurinaStageLedger.For(owner!).Reverse()) return;
        FurinaStagePlacement.Reflow(owner);
        Vfx.FurinaStageCues.Refresh(owner);
    }

    /// <summary><i>Stage Whisper</i>: move up to <paramref name="amount"/> of
    /// the back performer's Fanfare to the front performer; the back keeps at
    /// least 1. Sim twin: <c>furina_stage.whisper</c>.</summary>
    public static int Whisper(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        var moved = FurinaStageLedger.For(owner!).Whisper(amount);
        if (moved > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageCues.Refresh(owner);
        }
        return moved;
    }

    /// <summary><i>Held Applause</i>: at the end of this turn, the performers
    /// do not fade. Sim twin: <c>furina_stage.hold_fade</c>.</summary>
    public static void HoldFade(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).FadeHeld = true;
        Vfx.FurinaStageCues.Refresh(owner);
    }

    /// <summary>
    /// <i>Intermission</i>: "Your back performer Bows and leaves. Draw 1 card
    /// for every 3 Fanfare it had" (every 2 upgraded). A real Bow -- its act,
    /// the Bow readers, A Five-Century Act's return -- and a cash-out like
    /// Final Bow's, so the Bow holds nothing; then floor(F /
    /// <paramref name="every"/>) cards, F its Fanfare before the Bow. Returns
    /// F. Sim twin: <c>furina_stage.intermission</c>.
    /// </summary>
    public static async Task<int> Intermission(
        PlayerChoiceContext choiceContext, Creature? owner, int every)
    {
        if (!LiveFor(owner)) return 0;
        var exit = FurinaStageLedger.For(owner!).FinalBow(out var bar);
        if (exit == null) return 0;
        await Bow(choiceContext, owner!, exit.Value);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageCues.Refresh(owner);
        var cards = bar / System.Math.Max(1, every);
        if (cards > 0 && owner!.Player is { } player && !CombatOver())
        {
            await CardPileCmd.Draw(choiceContext, cards, player);
        }
        return bar;
    }

    /// <summary><i>Bring the House Down</i>: spend ALL of the front
    /// performer's Fanfare; the emptied front Bows (rule 7). Returns what was
    /// spent, which the card's damage reads through `stage_spent`. Sim twin:
    /// <c>furina_stage.spend_all_of_front</c>.</summary>
    public static async Task<int> SpendAllOfFront(
        PlayerChoiceContext choiceContext, Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var result = FurinaStageLedger.For(owner!).SpendAllOfFront();
        if (!result.Fired) return 0;
        if (result.Exit is { } exit) await Bow(choiceContext, owner!, exit);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageCues.Refresh(owner);
        return result.Paid;
    }

    /// <summary>
    /// <i>Grand Finale</i>: "All your performers Bow without leaving." Front
    /// first, each a real Bow -- its act, free, then every Bow reader
    /// (Thunderous Applause draws and Raises) -- but the performer keeps its
    /// seat and its Fanfare, so A Five-Century Act has nobody to return. The
    /// Bow reads the bar the performer holds (Navia) and what it lost since
    /// its last act (Wriothesley), and like every act it resets that count.
    /// Every one counts for Da Capo. Sim twin: <c>furina_stage.grand_finale</c>.
    /// </summary>
    public static async Task GrandFinale(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        foreach (var seat in Of(owner).ToList())
        {
            if (owner!.IsDead || CombatOver()) break;
            if (!ledger.Holds(seat)) continue;
            var exit = new StageExit(seat.Who, StageDeparture.Spent,
                                     seat.Fanfare, ledger.IndexOf(seat),
                                     seat.LostSinceAct)
            {
                Stayer = seat,
            };
            await Bow(choiceContext, owner, exit, mayReturn: false);
            seat.LostSinceAct = 0;
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageCues.Refresh(owner);
    }

    /// <summary><i>Oratrice's Verdict</i>: this turn, an act that hits a
    /// random enemy hits <paramref name="target"/> instead, while it lives
    /// (<see cref="ActTarget"/>). Cleared after the end-of-turn sweep. Sim
    /// twin: <c>furina_stage.set_verdict</c>.</summary>
    public static void SetVerdict(Creature? owner, Creature? target)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).VerdictTarget = target;
        Vfx.FurinaStageCues.Refresh(owner);
    }

    /// <summary>
    /// <i>Dual Nature</i>: "Choose Ousia or Pneuma for this turn." Arkhe
    /// Alignment's own screen and faces, once, for this turn only
    /// (<see cref="ArkheAlignmentPower.ChooseForTurn"/>). Sim twin:
    /// <c>furina_stage.dual_nature</c>.
    /// </summary>
    public static async Task DualNature(PlayerChoiceContext choiceContext,
                                        Player? player)
    {
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var combatState = owner!.CombatState;
        if (combatState == null) return;
        var options = new List<CardModel>
        {
            combatState.CreateCard(ModelDb.Card<ArkheOusiaOption>(), player!),
            combatState.CreateCard(ModelDb.Card<ArkhePneumaOption>(), player!),
        };
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, player!, canSkip: false);
        ArkheAlignmentPower.ChooseForTurn(owner,
                                          selected is ArkhePneumaOption);
        Vfx.FurinaStageCues.Refresh(owner);
    }

    /// <summary><i>Star Billing</i>: "Whenever a Guest Star joins the stage,
    /// draw 2 cards", after the arrival, whichever way it arrived. Copies
    /// add.</summary>
    private static async Task StarBilling(PlayerChoiceContext choiceContext,
                                          Creature owner)
    {
        var cards = (int)owner.Powers.OfType<StarBillingPower>()
            .Sum(p => p.Amount);
        if (cards <= 0 || owner.Player is not { } player || CombatOver())
        {
            return;
        }
        await CardPileCmd.Draw(choiceContext, cards, player);
    }

    /// <summary>
    /// <i>Tide of Applause</i>: "Whenever you trigger an Elemental Reaction,
    /// your back performer gains 2 Fanfare." Called from
    /// <c>ReactionEffects.Resolve</c>, the one site the mod resolves a
    /// reaction, with the reaction's dealer -- Furina for her cards and her
    /// performers' acts. A Raise, so on an empty stage it summons (rule 5).
    /// Sim twin: <c>furina_stage.note_reaction</c>.
    /// </summary>
    internal static async Task OnReaction(PlayerChoiceContext choiceContext,
                                          Creature? dealer)
    {
        if (!LiveFor(dealer)) return;
        var amount = (int)dealer!.Powers.OfType<TideOfApplausePower>()
            .Sum(p => p.Amount);
        if (amount <= 0) return;
        await Raise(dealer, amount);
    }

    /// <summary>
    /// THE SUPPORTING POOL'S TURN-START POWERS, in this order, right AFTER
    /// rule 4's regen (<c>FurinaStageHooks.AfterPlayerTurnStart</c>), so the
    /// lead's 1 went to the performer that led last turn:
    ///
    ///   1. <i>One-Woman Show</i>, first, on the stage the turn found: if no
    ///      one is on stage, gain 1 Energy and draw 1 card per copy -- asked
    ///      before Season Tickets, whose Raise on an empty stage summons;
    ///   2. <i>Revolving Stage</i>: the back performer moves to the front,
    ///      once per copy;
    ///   3. <i>Season Tickets</i>: the back performer gains N (summons on an
    ///      empty stage);
    ///   4. <i>Regina of All Waters</i>: Hydro on ALL enemies, reactions and
    ///      all.
    ///
    /// Sim twin: <c>furina_stage.supporting_pool_turn_start</c>.
    /// </summary>
    public static async Task TurnStartPowers(PlayerChoiceContext choiceContext,
                                             Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var furina = owner!;
        var show = (int)furina.Powers.OfType<OneWomanShowPower>()
            .Sum(p => p.Amount);
        if (show > 0 && !Occupied(furina) && furina.Player is { } player)
        {
            await PlayerCmd.GainEnergy(show, player);
            await CardPileCmd.Draw(choiceContext, show, player);
        }
        var turns = (int)furina.Powers.OfType<RevolvingStagePower>()
            .Sum(p => p.Amount);
        for (var i = 0; i < turns; i++) StepForward(furina);
        var tickets = (int)furina.Powers.OfType<SeasonTicketsPower>()
            .Sum(p => p.Amount);
        if (tickets > 0) await Raise(furina, tickets);
        if (furina.Powers.OfType<ReginaOfAllWatersPower>().Any())
        {
            foreach (var enemy in Enemies(furina).ToList())
            {
                if (furina.IsDead || CombatOver()) break;
                await ElementalHit.ApplyOnly(choiceContext, enemy,
                                             Element.Hydro, furina);
            }
        }
    }
}

// ======================================================================
// THE SUPPORTING POOL'S POWERS. The same terms as batch two's
// (FurinaStagePowers.cs): each is a switch the rule it bends asks about, and
// every bar move is the ledger's. Soliloquy is the one that hooks the damage
// itself, as the shipped flat attack riders do.
// ======================================================================

/// <summary><i>Revolving Stage</i>: "At the start of your turn, your back
/// performer moves to the front." Each copy moves it once
/// (<see cref="FurinaStage.TurnStartPowers"/>).</summary>
public sealed class RevolvingStagePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Revolving Stage"),
        ("description",
            "At the start of your turn, your back performer moves to the "
          + "front."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Season Tickets</i>: "At the start of your turn, your back
/// performer gains 2 Fanfare" (3 upgraded). A Raise, so on an empty stage it
/// summons (rule 5). Copies add.</summary>
public sealed class SeasonTicketsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Season Tickets"),
        ("description",
            "At the start of your turn, your back performer gains "
          + "[blue]{Amount}[/blue] [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Star Billing</i>: "Whenever a Guest Star joins the stage, draw
/// 2 cards", a second copy's recast included. Copies add.</summary>
public sealed class StarBillingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star Billing"),
        ("description",
            "Whenever a Guest Star joins the stage, draw "
          + "[blue]{Amount}[/blue] {Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Echoing Hall</i>: "Whenever a performer fades, your front
/// performer gains the Fanfare lost." A MOVE: what the fade took goes to the
/// front once, so a second copy moves nothing more.</summary>
public sealed class EchoingHallPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Echoing Hall"),
        ("description",
            "Whenever a performer fades, your front performer gains the "
          + "[gold]Fanfare[/gold] lost."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Eternal Applause</i>: "Your performers fade only above 10
/// Fanfare, not 5." Rule 12's line, bent; copies do not stack further.
/// </summary>
public sealed class EternalApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Eternal Applause"),
        ("description",
            "Your performers fade only above "
          + FurinaStageLaw.EternalFadeThreshold + " [gold]Fanfare[/gold], "
          + "not " + FurinaStageLaw.FadeThreshold + "."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Tide of Applause</i>: "Whenever you trigger an Elemental
/// Reaction, your back performer gains 2 Fanfare" (3 upgraded), paid at the
/// one site the mod resolves a reaction (<see cref="FurinaStage.OnReaction"/>).
/// Copies add.</summary>
public sealed class TideOfApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tide of Applause"),
        ("description",
            "Whenever you trigger an [gold]Elemental Reaction[/gold], your "
          + "back performer gains [blue]{Amount}[/blue] "
          + "[gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Regina of All Waters</i>: "At the start of your turn, apply
/// Hydro to ALL enemies", through the ordinary aura pipeline, so reactions
/// trigger as any application does. A second copy applies nothing more.
/// </summary>
public sealed class ReginaOfAllWatersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Regina of All Waters"),
        ("description",
            "At the start of your turn, apply [gold]Hydro[/gold] to ALL "
          + "enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Soliloquy</i>: "While no one is on stage, your Attacks deal 3 more
/// damage" (4 upgraded). Strength's shape: added to EVERY HIT of an Attack
/// card, so a two-hit Attack gains it twice, read per hit off the live stage.
/// Copies add. Sim twin: <c>effects.flat_attack_bonus</c>, which reads the
/// stage once at the play's start; the two agree unless a card empties or
/// fills the stage between its own hits.
/// </summary>
public sealed class SoliloquyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Soliloquy"),
        ("description",
            "While no one is on stage, your Attacks deal "
          + "[blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (!FurinaStage.LiveFor(Owner) || FurinaStage.Occupied(Owner))
        {
            return 0m;
        }
        return Amount;
    }
}

/// <summary><i>One-Woman Show</i>: "At the start of your turn, if no one is
/// on stage, gain 1 Energy and draw 1 card", asked first of the turn-start
/// powers, on the stage the turn found (<see cref="FurinaStage.TurnStartPowers"/>).
/// Copies add.</summary>
public sealed class OneWomanShowPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "One-Woman Show"),
        ("description",
            "At the start of your turn, if no one is on stage, gain "
          + "[blue]{Amount}[/blue] [gold]Energy[/gold] and draw "
          + "[blue]{Amount}[/blue] {Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
