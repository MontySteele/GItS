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
/// STAGED: no shipped card is modal yet. Nothing in the roster calls this.
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
