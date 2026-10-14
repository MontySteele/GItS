using System;
using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Abyss;

/// <summary>One card on the Blessing screen: the Blessing it gives (upper
/// half) and the Shadow that joins the enemies' roll if it is passed (lower
/// half). Every string is the paper's, through <see cref="AbyssText"/>. The
/// tags are each entry's duration, "Whole run" or "This act"
/// (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>, pick 1 (a)).</summary>
public sealed record AbyssOverlayCard(
    int Index, AbyssBlessing Blessing, AbyssShadow Shadow,
    string BlessingName, string BlessingText, string ShadowName, string ShadowText,
    string BlessingIconFile, string ShadowIconFile,
    string BlessingTag = AbyssOverlayContent.WholeRunTag,
    string ShadowTag = AbyssOverlayContent.WholeRunTag);

/// <summary>One icon in the top-right strip: a Blessing or Shadow in force,
/// with its hover text and its duration.</summary>
public sealed record AbyssOverlayStripEntry(
    string Name, string Text, string IconFile, string Duration = AbyssOverlayContent.WholeRunTag)
{
    /// <summary>The hover text: the entry's text, then its duration.</summary>
    public string HoverText => $"{Text}\n[gold]{Duration}[/gold]";

    public bool ThisAct => Duration == AbyssOverlayContent.ThisActTag;
}

/// <summary>
/// THE SPIRAL ABYSS BLESSING SCREEN'S WORDS (owner, 2026-10-12: "a pop-up
/// on-screen with the choice of three blessings before the Ancient screen
/// loads ... three vertical banner choices, and the lower half explaining the
/// Shadow"). PURE: built from the act's offer and the run's record, so the
/// headless suite pins every line the screen and the seat bridge print.
/// </summary>
public sealed class AbyssOverlayContent
{
    public const string Heading = "The Spiral Abyss";

    /// <summary>Co-op Abyss run, 2026-10-14: in all three acts both seats
    /// read the Shadow beside a Blessing as the one that came with it. The
    /// line now says where the enemies' Shadow comes from.</summary>
    public const string Whisper =
        "The Abyss whispers, urging you deeper. Take one Blessing. "
      + "The enemies take one Shadow, at random, from the Blessings you pass.";

    public const string WholeRunTag = "Whole run";

    public const string ThisActTag = "This act";

    /// <summary>The label over each card's lower band; the view prints it in
    /// capitals. Owner, 2026-10-12: "IF PASSED" renamed "SHADOW". Co-op
    /// Abyss run, 2026-10-14: "SHADOW" beside a Blessing read as the Shadow
    /// that comes with it, three acts running, so the band keeps the word
    /// and says when it applies.</summary>
    public const string ShadowBandLabel = "Shadow if you pass this";

    public const string BlessingsLabel = "Blessings";

    public const string ShadowsLabel = "Shadows";

    /// <summary>"The Spiral Abyss · Act N". Neow is act 1: the act index is
    /// zero-based.</summary>
    public static string TitleFor(int actIndex) => $"{Heading} · Act {Math.Max(0, actIndex) + 1}";

    public AbyssOverlayContent(
        string title, IReadOnlyList<AbyssOverlayCard> cards,
        IReadOnlyList<AbyssOverlayStripEntry> blessingsTaken,
        IReadOnlyList<AbyssOverlayStripEntry> shadowsInForce)
    {
        Title = title;
        Cards = cards;
        BlessingsTaken = blessingsTaken;
        ShadowsInForce = shadowsInForce;
    }

    public string Title { get; }

    public IReadOnlyList<AbyssOverlayCard> Cards { get; }

    public IReadOnlyList<AbyssOverlayStripEntry> BlessingsTaken { get; }

    public IReadOnlyList<AbyssOverlayStripEntry> ShadowsInForce { get; }

    /// <summary>Is there anything for the top-right strip? Empty on the first
    /// visit.</summary>
    public bool HasStrip => BlessingsTaken.Count > 0 || ShadowsInForce.Count > 0;

    /// <summary>The screen for <paramref name="offer"/>'s act. The strip
    /// lists what is in force in that act: a This act entry of an earlier act
    /// has dropped off by the time the next act's page is up.</summary>
    public static AbyssOverlayContent For(AbyssOffer offer, AbyssRecord record)
    {
        var cards = offer.Options.Select((o, i) => new AbyssOverlayCard(
            i, o.Blessing, o.Shadow,
            AbyssText.Name(o.Blessing), AbyssText.Text(o.Blessing),
            AbyssText.Name(o.Shadow), AbyssText.Text(o.Shadow),
            BlessingIconFile(o.Blessing), ShadowIconFile(o.Shadow),
            AbyssDurations.Tag(AbyssDurations.Of(o.Blessing)),
            AbyssDurations.Tag(AbyssDurations.Of(o.Shadow)))).ToList();
        var blessings = record.BlessingsInForce(offer.ActIndex)
            .Select(b => new AbyssOverlayStripEntry(
                AbyssText.Name(b), AbyssText.Text(b), BlessingIconFile(b),
                AbyssDurations.Tag(AbyssDurations.Of(b))))
            .ToList();
        var shadows = record.ShadowsInForce(offer.ActIndex)
            .Select(s => new AbyssOverlayStripEntry(
                AbyssText.Name(s), AbyssText.Text(s), ShadowIconFile(s),
                AbyssDurations.Tag(AbyssDurations.Of(s))))
            .ToList();
        return new AbyssOverlayContent(TitleFor(offer.ActIndex), cards, blessings, shadows);
    }

    /// <summary>The seat bridge's option text for a card: the Blessing's
    /// text, then the card's Shadow under the screen's own label.</summary>
    public static string BridgeDescription(AbyssOverlayCard card) =>
        $"{card.BlessingText}\nIf you pass this, the enemies may take its Shadow: "
        + $"{card.ShadowName} — {card.ShadowText}";

    /// <summary>The Blessing's icon in the pack: the same file its display
    /// relic wears (<c>Relics/AbyssRelics.cs</c>).</summary>
    public static string BlessingIconFile(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine => "abyss/relics/ley_line.png",
        AbyssBlessing.AbyssalMoon => "abyss/relics/abyssal_moon.png",
        AbyssBlessing.MoonlitRest => "abyss/relics/moonlit_rest.png",
        AbyssBlessing.FirstStrike => "abyss/relics/first_strike.png",
        AbyssBlessing.ElementalBurst => "abyss/relics/elemental_burst.png",
        AbyssBlessing.Resonance => "abyss/relics/resonance.png",
        AbyssBlessing.Crystallize => "abyss/relics/crystallize.png",
        AbyssBlessing.FatefulFortune => "abyss/relics/fateful_fortune.png",
        AbyssBlessing.Overflow => "abyss/relics/elemental_burst.png",
        AbyssBlessing.VigorOfTheAbyss => "abyss/relics/first_strike.png",
        AbyssBlessing.MoonlitSpring => "abyss/relics/moonlit_rest.png",
        AbyssBlessing.BattleRhythm => "abyss/relics/resonance.png",
        AbyssBlessing.WaveringMoon => "abyss/relics/abyssal_moon.png",
        AbyssBlessing.StarfellDraft => "abyss/relics/fateful_fortune.png",
        _ => throw new ArgumentOutOfRangeException(nameof(b)),
    };

    /// <summary>The Shadow's badge icon: the same file its enemy badge wears
    /// (<see cref="AbyssShadowPower.IconFile"/>).</summary>
    public static string ShadowIconFile(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock => "abyss/powers/shadow_clock.png",
        AbyssShadow.MageShield => "abyss/powers/shadow_mage_shield.png",
        AbyssShadow.SheerCold => "abyss/powers/shadow_sheer_cold.png",
        AbyssShadow.ElementalMark => "abyss/powers/shadow_elemental_mark.png",
        AbyssShadow.Herald => "abyss/powers/shadow_herald.png",
        AbyssShadow.Rally => "abyss/powers/shadow_rally.png",
        AbyssShadow.Riptide => "abyss/powers/shadow_riptide.png",
        AbyssShadow.FatuiSkirmishers => "abyss/powers/shadow_fatui_skirmishers.png",
        AbyssShadow.ThornyGround => "abyss/powers/shadow_herald.png",
        AbyssShadow.Bulwark => "abyss/powers/shadow_fatui_skirmishers.png",
        AbyssShadow.Frenzy => "abyss/powers/shadow_rally.png",
        AbyssShadow.Withering => "abyss/powers/shadow_sheer_cold.png",
        _ => throw new ArgumentOutOfRangeException(nameof(s)),
    };
}

/// <summary>Where the Blessing screen is in its life.</summary>
public enum AbyssOverlayPhase
{
    /// <summary>Not up. The Ancient's dialogue is free to play.</summary>
    Closed,

    /// <summary>Up and taking a pick (solo) or votes (co-op).</summary>
    Open,

    /// <summary>The pick has landed; the result line shows.</summary>
    Resolving,

    /// <summary>Fading out. The dialogue is released when the fade ends.</summary>
    Closing,
}

/// <summary>
/// THE SCREEN'S SEQUENCE, as a pure state machine, so the headless suite
/// pins it: it opens before the Ancient's dialogue, holds the dialogue while
/// it is up, takes a vote only while open, shows its result line for
/// <see cref="ResultSeconds"/> and then fades for
/// <see cref="FadeSeconds"/>, and only then lets the Ancient speak. The game
/// glue (<c>AbyssOverlay</c>) does what each step says.
/// </summary>
public sealed class AbyssOverlayFlow
{
    /// <summary>How long the result line stays up. Co-op Abyss run,
    /// 2026-10-14: the seats said the page never said which Shadow the
    /// enemies took, so the line now names it, solo too, and stays long
    /// enough to read.</summary>
    public const double ResultSeconds = 2.5;
    public const double FadeSeconds = 0.3;

    public AbyssOverlayPhase Phase { get; private set; } = AbyssOverlayPhase.Closed;

    /// <summary>The card this machine's player last voted for.</summary>
    public int? LocalVote { get; private set; }

    /// <summary>The result line, once the pick resolves: what was chosen
    /// and the Shadow the enemies took.</summary>
    public string? ResultLine { get; private set; }

    public int? Chosen { get; private set; }

    /// <summary>The Ancient's dialogue waits for every phase but Closed.</summary>
    public bool HoldsDialogue => Phase != AbyssOverlayPhase.Closed;

    /// <summary>Cards answer clicks only while the screen is open.</summary>
    public bool TakesVotes => Phase == AbyssOverlayPhase.Open;

    /// <summary>Open the screen. Returns false if it was already up (a second
    /// setup of the same room opens nothing new).</summary>
    public bool Open()
    {
        if (Phase != AbyssOverlayPhase.Closed || Chosen.HasValue) return false;
        Phase = AbyssOverlayPhase.Open;
        return true;
    }

    /// <summary>A click on card <paramref name="index"/> of
    /// <paramref name="count"/>. Returns whether it should be sent as this
    /// player's vote. In co-op a player may change their vote while the vote
    /// is open, as on any shared event; clicking the card already voted for
    /// sends nothing.</summary>
    public bool Vote(int index, int count)
    {
        if (!TakesVotes || index < 0 || index >= count) return false;
        if (LocalVote == index) return false;
        LocalVote = index;
        return true;
    }

    /// <summary>The pick landed. Returns how long to hold the result line
    /// before fading. A second call (the other copy of the shared event)
    /// changes nothing and answers null.</summary>
    public double? Resolve(int chosen, string chosenName, string? shadowName, bool coop, bool split)
    {
        if (Phase != AbyssOverlayPhase.Open) return null;
        Chosen = chosen;
        ResultLine = ResultLineFor(chosenName, shadowName, coop, split);
        Phase = AbyssOverlayPhase.Resolving;
        return ResultSeconds;
    }

    /// <summary>The result line's time is up: start the fade.</summary>
    public bool BeginFade()
    {
        if (Phase == AbyssOverlayPhase.Resolving)
        {
            Phase = AbyssOverlayPhase.Closing;
            return true;
        }
        return Phase == AbyssOverlayPhase.Closing;
    }

    /// <summary>The fade ended. Returns true exactly once: the moment the
    /// Ancient's dialogue is released.</summary>
    public bool FinishFade()
    {
        if (Phase != AbyssOverlayPhase.Closing) return false;
        Phase = AbyssOverlayPhase.Closed;
        return true;
    }

    /// <summary>The result line: who chose what, then the Shadow the
    /// enemies took (none named when the offer had no Shadow to give).</summary>
    public static string ResultLineFor(string chosenName, string? shadowName, bool coop, bool split)
    {
        var chose = !coop ? $"You chose {chosenName}."
            : split ? $"The vote split; the draw gave {chosenName}."
            : $"The party chose {chosenName}.";
        return string.IsNullOrEmpty(shadowName) ? chose : $"{chose} The enemies took {shadowName}.";
    }
}

/// <summary>
/// WHAT A SHARED VOTE GAVE, as the screen reports it. The votes are read the
/// moment before the game clears them (<c>EventSynchronizer
/// .ChooseOptionForSharedEvent</c>), where the host has drawn one of them at
/// random. On a client the host's vote message can arrive after the result,
/// so with two players a client whose own vote lost knows the partner's: it
/// is the result (the bridge's <c>GitsCoopOutcomes</c> makes the same
/// inference).
/// </summary>
public static class AbyssVoteOutcome
{
    public static bool Split(IReadOnlyList<int?> votes, int chosen)
    {
        var known = votes.ToList();
        if (known.Count == 2 && known.Count(v => v.HasValue) == 1)
        {
            var only = known.First(v => v.HasValue)!.Value;
            if (only != chosen)
            {
                var missing = known.FindIndex(v => !v.HasValue);
                known[missing] = chosen;
            }
        }
        return known.Where(v => v.HasValue).Select(v => v!.Value).Distinct().Count() > 1;
    }
}
