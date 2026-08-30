using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// The generic choose-one / modal surface, C# leg (EB-118 §5.4). A modal card
/// offers 2+ labelled modes and resolves exactly the one the player picks.
///
/// THIS INVENTS NO UI. The game already owns a card-level player choice, and
/// the decompile of sts2.dll v0.107.1 names every part of it:
///
///   * <c>PlayerChoiceContext</c> — the sequencing handle every
///     <c>CardModel.OnPlay</c> already receives, with
///     <c>SignalPlayerChoiceBegun</c>/<c>Ended</c> around the decision point.
///   * <c>CardSelectCmd.FromChooseACardScreen</c> — the ≤3-option screen the
///     base game uses for Splash, Discovery, Quasar and the four generation
///     Potions. It syncs the co-op seats itself, as
///     <c>PlayerChoiceResult.FromIndex</c> / <c>AsIndex</c> — and
///     <c>PlayerChoiceType.Index</c> is documented in the binary as "the
///     player is choosing an option out of a deterministically generated list
///     of options", which is precisely a mode selection.
///   * <c>CardSelectCmd.Selector</c> (<c>ICardSelector</c>) — the automation
///     seam tests and AutoSlay answer through, so a modal card is not a wall
///     to the understudy bot.
///
/// A parallel prompt would have to re-solve all three. EtherealSpotlight has
/// shipped on this exact pattern since the salon rework; this class is that
/// pattern generalized so codegen can emit it.
///
/// ONE SHIPPED CARD IS MODAL: Furina's `deep_breath`. EB-182 added the
/// per-option half below -- a mode the bank cannot pay is not offered.
/// </summary>
public static class ModalChoice
{
    /// <summary>
    /// The mode-taken record, pinned to tier0's emit. `tier0.engine.effects`
    /// emits <c>{"event": "mode_chosen", "card": ..., "index": ...,
    /// "label": ...}</c>; these two members are the C# mirror of that name and
    /// those fields, and <c>tier0/tests/test_eb118_modal_parity.py</c> reads
    /// them straight out of this source so the two engines cannot drift.
    /// </summary>
    public const string EventName = "mode_chosen";

    public static readonly string[] EventFields = { "card", "index", "label" };

    /// <summary>
    /// The non-UI half, factored out so it can be graded headlessly: which
    /// mode did an answered screen name? Reference identity, not title —
    /// two modes of one card may legitimately print the same words.
    ///
    /// Falls back to mode 0 rather than throwing. The screen is opened with
    /// <c>canSkip: false</c>, so a null or unrecognised answer is an
    /// instrument failure, not a player action, and a modal card that
    /// resolves nothing is a worse outcome for the seat than one that resolves
    /// its first mode. The fallback is LOUD.
    /// </summary>
    public static int ResolveIndex<T>(IReadOnlyList<T> options, T? selected)
        where T : class
    {
        for (var i = 0; i < options.Count; i++)
        {
            if (ReferenceEquals(options[i], selected)) return i;
        }
        Log.Warn($"[{KleeMod.ModId}] modal choice: the answered option is not "
               + "one of the offered modes; resolving mode 0.");
        return 0;
    }

    /// <summary>
    /// Build one mode option as a COMBAT-SCOPED OWNED instance.
    ///
    /// The choose-a-card screen dereferences the first option's Owner
    /// (asserting mutability, then initializing the pile viewer from it), so
    /// canonical ModelDb templates softlock it and so do bare ToMutable()
    /// copies (Owner == null). CombatState.CreateCard is the base game's own
    /// pattern for screen options — the same note EtherealSpotlight carries.
    /// </summary>
    public static CardModel CreateOption<T>(Player owner) where T : CardModel =>
        owner.Creature!.CombatState!.CreateCard(ModelDb.Card<T>(), owner);

    /// <summary>
    /// Ask the player which mode to take. Returns the mode INDEX, in the order
    /// the sheet printed the modes, which is the order both engines record.
    /// </summary>
    public static async Task<int> SelectMode(
        PlayerChoiceContext choiceContext, Player owner,
        IReadOnlyList<CardModel> options)
    {
        if (options.Count == 0)
        {
            throw new InvalidOperationException(
                "a modal card was played with no modes");
        }
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, owner, canSkip: false);
        return ResolveIndex(options, selected);
    }

    /// <summary>
    /// EB-182: ask the player which mode to take, offering ONLY the modes the
    /// bank can pay for. Returns the index in the SHEET's order, so the
    /// generated if/else ladder is unaffected by what was filtered.
    ///
    /// WHY OMISSION AND NOT GREYING. The 0.111.0 decompile is the constraint:
    /// <c>CardSelectCmd.FromChooseACardScreen</c> takes no per-option filter,
    /// the screen's <c>SelectHolder</c> guards only a debounce, and
    /// <c>CanPlay</c> is never read on an option — so there is no disabled
    /// state to paint, and a mode we cannot grey out we must not offer. The
    /// price stays legible either way, because a priced mode's LABEL is its
    /// price ("Spend 3 Encore: draw 3"), and a Spark-priced mode option also
    /// carries the ordinary Spark cost badge (it implements
    /// <c>ISparkPricedCard</c>, so <c>SparkCostBadge</c> paints it with no
    /// second look invented).
    ///
    /// THE EMPTY CASE IS LOUD, not silent. The card's own <c>IsPlayable</c>
    /// gate (codegen: <c>modal_gate_member</c>) already refuses a card with no
    /// affordable mode, so reaching here with nothing offered is an instrument
    /// failure; every mode is offered and the paying calls refuse where they
    /// stand, which is the pre-EB-182 behaviour rather than a resolved
    /// nothing. Sim twin: <c>effects._chosen_mode</c>'s identical fallback.
    ///
    /// A DISTINCT NAME rather than an overload of <see cref="SelectMode"/>:
    /// the structural pins reach a method by name through
    /// <c>Type.GetMethod</c>, which is ambiguous across an overload pair, and
    /// an unpinned selection path is exactly the co-op/automation seam those
    /// pins exist to guard.
    /// </summary>
    public static async Task<int> SelectAffordableMode(
        PlayerChoiceContext choiceContext, Player owner,
        IReadOnlyList<CardModel> options, IReadOnlyList<ModePrice?> prices)
    {
        var offered = Offered(owner, prices);
        if (offered.Count == 0)
        {
            Log.Warn($"[{KleeMod.ModId}] modal choice: no mode is affordable "
                   + "on a card that was played anyway -- "
                   + $"{Refusals(owner, options, prices)}; offering every "
                   + "mode.");
            return await SelectMode(choiceContext, owner, options);
        }
        if (offered.Count == options.Count)
        {
            return await SelectMode(choiceContext, owner, options);
        }
        var shown = new List<CardModel>();
        foreach (int i in offered)
        {
            shown.Add(options[i]);
        }
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, shown, owner, canSkip: false);
        return offered[ResolveIndex(shown, selected)];
    }

    /// <summary>
    /// Why each priced mode was refused, naming the price and the bank. The
    /// C# half of tier0's <c>combat.modal_refusal</c> -- one sentence per dead
    /// mode, so a log line says what was short rather than only that nothing
    /// was offered.
    /// </summary>
    public static string Refusals(
        Player owner, IReadOnlyList<CardModel> options,
        IReadOnlyList<ModePrice?> prices)
    {
        var parts = new List<string>();
        for (var i = 0; i < prices.Count; i++)
        {
            ModePrice? price = prices[i];
            if (price == null || price.Value.Affordable(owner)) continue;
            string label = i < options.Count
                ? options[i].Id.ToString() : $"mode {i}";
            parts.Add(price.Value.Refusal(owner, label));
        }
        return string.Join("; ", parts);
    }

    /// <summary>
    /// The mode indexes this bank can pay for, in sheet order. A null entry is
    /// an UNPRICED mode and is always offered.
    /// </summary>
    public static List<int> Offered(
        Player owner, IReadOnlyList<ModePrice?> prices)
    {
        var offered = new List<int>();
        for (var i = 0; i < prices.Count; i++)
        {
            ModePrice? price = prices[i];
            if (price == null || price.Value.Affordable(owner))
            {
                offered.Add(i);
            }
        }
        return offered;
    }

    /// <summary>
    /// Is ANY mode payable? The card-level half of per-option playability, and
    /// what the generated <c>IsPlayable</c> override asks. Sim twin:
    /// <c>combat.modal_refusal</c> reached through <c>card_playable</c>.
    /// </summary>
    public static bool AnyAffordable(
        Player? owner, IReadOnlyList<ModePrice?> prices) =>
        owner == null || Offered(owner, prices).Count > 0;

    /// <summary>
    /// The emit-stream row, formatted so a log line and a tier0 event carry the
    /// same three fields under the same names.
    /// </summary>
    public static string FormatChoice(string cardId, int index, string label) =>
        $"{EventName} {EventFields[0]}={cardId} {EventFields[1]}={index} "
      + $"{EventFields[2]}={label}";

    /// <summary>Record the taken mode. EMIT-ONLY — it changes nothing.</summary>
    public static void RecordChoice(CardModel card, int index, string label)
    {
        Log.Info($"[{KleeMod.ModId}] "
               + FormatChoice(card.Id.ToString(), index, label));
    }
}

/// <summary>
/// EB-182: the price ONE mode prints, and the bank it is read against.
///
/// THE RULE, one sentence: a mode whose body OPENS with a resource spend is
/// that mode's COST LINE, and a mode the bank cannot pay is not offered. The
/// colon in "Spend 3 Encore: draw 3" is the boundary — a spend further down a
/// body is a consequence of the mode rather than its admission fee, and the
/// paying calls keep refusing those where they stand.
///
/// The bank read is a delegate rather than a switch on a meter name, so this
/// type references no resource class: Sparks, Encore and Charge live in three
/// places and one of them is behind <c>PROTOTYPE_CARDS</c>. The codegen emits
/// the accessor beside the number it belongs to.
///
/// Sim twin: <c>tier0.engine.effects.mode_price</c> / <c>mode_refusal</c>.
/// </summary>
public readonly struct ModePrice
{
    private readonly Func<Player, int> _bank;

    public ModePrice(string meter, int amount, Func<Player, int> bank)
    {
        Meter = meter;
        Amount = amount;
        _bank = bank;
    }

    /// <summary>The meter's printed name — "Encore", "Sparks", "Charge".</summary>
    public string Meter { get; }

    /// <summary>The printed price, a literal off the sheet.</summary>
    public int Amount { get; }

    public bool Affordable(Player owner) => _bank(owner) >= Amount;

    /// <summary>
    /// Why this mode is not offered, naming the PRICE and the BANK. The log
    /// half of the rule; tier0's <c>mode_refusal</c> prints the same sentence
    /// so a refused line reads the same in either engine.
    /// </summary>
    public string Refusal(Player owner, string label) =>
        $"'{label}' needs {Amount} {Meter}, bank holds {_bank(owner)}";
}

/// <summary>
/// The face of one mode on the choose-a-card screen. It is a card only because
/// that screen takes cards; it is never played, never in a pile, and never in
/// a pool — <c>OnPlay</c> is a no-op by construction.
///
/// Rails ("no new named keyword"): a mode's title and description are ORDINARY
/// card text. Nothing here registers a keyword or a tooltip.
/// </summary>
public abstract class ModalOptionCard : CustomCardModel
{
    protected ModalOptionCard()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self,
               autoAdd: false)
    {
    }

    public override Texture2D? CustomPortrait => null;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        Array.Empty<DynamicVar>();

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        Task.CompletedTask;

    protected override void OnUpgrade()
    {
    }
}
