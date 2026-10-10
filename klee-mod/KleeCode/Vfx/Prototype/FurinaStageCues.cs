using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Vfx;

/// <summary>The picture a cue card carries: the base game's intent icons,
/// the energy icon, and the Salon's support glyph for a Fanfare gift.</summary>
public enum StageCueIcon
{
    Block,
    Attack,
    Energy,
    Support,
}

/// <summary>
/// ONE PERFORMER'S CUE, as drawn: an icon, one number, and the few marks
/// around it. Built only by <see cref="FurinaStageCues.From"/>, off the
/// forecast; nothing here is computed.
/// </summary>
/// <param name="Number">The act's number, -1 for none (a resting returnee).
/// </param>
/// <param name="Element">The damage's element (Hydro, Electro, Geo, Cryo,
/// Anemo), empty for the trio's plain damage and for every other act.</param>
/// <param name="All">The act hits ALL enemies.</param>
/// <param name="Price">The gold "−N" under the icon: what a priced act pays
/// (Neuvillette, Chevreuse). 0 for none.</param>
/// <param name="Times">The "×N" beside the card, shown from 2.</param>
/// <param name="Greyed">The act will do nothing this turn: it cannot pay,
/// it comes to 0, or the performer is resting.</param>
/// <param name="Forecast">The hover's forecast line(s), one per line.</param>
public sealed record StageCueView(
    StagePerformer Who, int Key, StageCueIcon Icon, int Number,
    string Element, bool All, int Price, int Times, bool Greyed,
    string Forecast);

/// <summary>
/// THE CHIPS ON ONE BAR. Performers have no bars since the re-founding, so
/// the forecast draws none; the type stays for the drawing's one code path.
/// </summary>
public sealed record StageBarChips(
    int Key, int Paid, int Faded, int Hits, bool Empties)
{
    /// <summary>Anything to draw at all.</summary>
    public bool Any => Paid > 0 || Faded > 0 || Hits > 0 || Empties;
}

/// <summary>Everything the cues draw for one Furina, at one moment.</summary>
public sealed record StageCueBoard(
    IReadOnlyList<StageCueView> Cues, IReadOnlyList<StageBarChips> Bars,
    StageBarChips Furina);

/// <summary>
/// FURINA'S TURN PREDICTOR, AS CUES ON THE PERFORMERS (2026-09-26).
///
/// [USER], the Furina balance review, pick 2: "The overhead turn predictor is
/// a decent start, but we should think of how to rework the element to be less
/// mechanical and more flavorful" -- ruled "a) sounds good": each performer
/// shows its act over its head the way an enemy shows its intent; the fade and
/// incoming hits show as chips on its bar; the text box goes.
///
/// The blind seat page keeps its own text forecast off the wire
/// (<c>FurinaStageLedger.Snapshot</c>) -- seats read text.
///
/// THE PREVIEW-TRUTH RULE, which is why this file is two halves. Every number
/// a cue or a chip shows is a field of <see cref="FurinaStage.Forecast"/>'s
/// result (<see cref="StageForecast.Cues"/>). <see cref="From"/> maps
/// it to what is drawn and is PURE, so a pin can script a board and read the
/// cue; the drawing (<see cref="FurinaStageCueNodes"/>) reads only that map.
///
/// SHOWN ON HER TURN. The forecast is "the end of this turn"; once her turn
/// has ended the acts have happened, and a cue would forecast a
/// second sweep that is not coming. So the cues come down at the end of her
/// turn (<see cref="CurtainDown"/>) and back up at her next turn start.
/// </summary>
public static class FurinaStageCues
{
    /// <summary>Furinas whose cues are down until her next turn start.
    /// </summary>
    private static readonly ConditionalWeakTable<Creature, object> _down = new();

    /// <summary>Does this creature draw cues? Furina, and only while the arm
    /// is live.</summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaStage.LiveFor(creature);

    /// <summary>Are her cues up right now?</summary>
    public static bool Showing(Creature? creature) =>
        AppliesTo(creature) && !_down.TryGetValue(creature!, out _);

    /// <summary>The end of her turn: the acts are done; the cues come down
    /// until her next turn start. Every chip goes with them.</summary>
    public static void CurtainDown(Creature? creature)
    {
        if (!AppliesTo(creature)) return;
        _down.AddOrUpdate(creature!, true);
        Refresh(creature);
    }

    /// <summary>Her turn start (and a combat's opening): the cues go up.
    /// </summary>
    public static void CurtainUp(Creature? creature)
    {
        if (creature == null) return;
        _down.Remove(creature);
        Refresh(creature);
    }

    /// <summary>
    /// What to draw now, or null for nothing: the arm off, her turn over, or
    /// a forecast that could not be made (a preview never throws at its
    /// caller).
    /// </summary>
    public static StageCueBoard? Read(Creature? creature)
    {
        if (!Showing(creature)) return null;
        try
        {
            return FurinaStage.Forecast(creature) is { } forecast
                ? From(forecast)
                : null;
        }
        catch (System.Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// THE MAP, forecast to picture. Pure: one cue per performer on stage,
    /// in seat order. Performers have no bars since the re-founding, so no
    /// chips are drawn; Furina's own chip stays empty.
    /// </summary>
    public static StageCueBoard From(StageForecast forecast)
    {
        var cues = new List<StageCueView>(forecast.Cues.Count);
        foreach (var cue in forecast.Cues)
        {
            cues.Add(new StageCueView(
                cue.Who, cue.Key, IconOf(cue.Kind), cue.Amount,
                cue.Kind == StageCueKind.Damage ? cue.Element : "",
                cue.Kind == StageCueKind.Damage
                    && cue.Target == StageForecastCue.All,
                0, 1, false, ForecastLine(cue)));
        }
        return new StageCueBoard(cues, new List<StageBarChips>(),
                                 new StageBarChips(-1, 0, 0, 0, false));
    }

    /// <summary>The icon an act's cue carries.</summary>
    public static StageCueIcon IconOf(StageCueKind kind) => kind switch
    {
        StageCueKind.Damage => StageCueIcon.Attack,
        StageCueKind.Block => StageCueIcon.Block,
        _ => StageCueIcon.Support,
    };

    /// <summary>The hover's forecast line. The act's rule is the other half
    /// of the hover, the guest's own badge.</summary>
    public static string ForecastLine(StageForecastCue cue) =>
        cue.Kind == StageCueKind.Repay
            ? $"Repays {cue.Amount} of your drained HP."
            : cue.Kind == StageCueKind.Block
                ? $"Gives you {cue.Amount} Block."
            : cue.Target == StageForecastCue.Aura
                ? "Hits an enemy with an aura, if any."
                : "Acts at the end of your turn.";

    /// <summary>
    /// REDRAW: every stage mutation funnels here (it was the strip's funnel,
    /// <c>FurinaStageStrip.Refresh</c>, and keeps every one of its call
    /// sites). Headless-safe: the drawing needs a combat room, which
    /// `dotnet test` never has.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        if (!AppliesTo(creature) || !FurinaStageCueNodes.HasRoom) return;
        FurinaStageCueNodes.Draw(creature!, Read(creature));
    }
}
