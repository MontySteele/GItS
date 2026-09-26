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
/// THE CHIPS ON ONE BAR, in the order they happen: the Fanfare the acts'
/// payments and taxes take (gold), then the fade (grey), both at the end of
/// her turn, then what the enemy's hits take (red). <see cref="Key"/> is the
/// seat's, or -1 for Furina's own HP bar (hits only).
/// <see cref="Empties"/> marks a bar that will empty and leave.
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
/// SO THIS REPLACES THE STRIP'S GAUGE. The overhead text box
/// (<see cref="FurinaStageStrip"/>'s <c>furina_stage</c> gauge) no longer
/// mounts; its <see cref="FurinaStageStrip.Label"/> stays as the text form
/// the pins read, and the blind seat page keeps its own text forecast off the
/// wire (<c>FurinaStageLedger.Snapshot</c>), unchanged -- seats read text.
///
/// THE PREVIEW-TRUTH RULE, which is why this file is two halves. Every number
/// a cue or a chip shows is a field of <see cref="FurinaStage.Forecast"/>'s
/// result (<see cref="StageForecast.Cues"/>, the seat rows' payments and fade,
/// the hit-by-hit <see cref="StageForecast.Takers"/>). <see cref="From"/> maps
/// it to what is drawn and is PURE, so a pin can script a board and read the
/// cue; the drawing (<see cref="FurinaStageCueNodes"/>) reads only that map.
///
/// SHOWN ON HER TURN. The forecast is "the end of this turn"; once her turn
/// has ended the acts and the fade have happened, and a cue would forecast a
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
    /// in seat order; one set of chips per performer; Furina's own chip.
    /// </summary>
    public static StageCueBoard From(StageForecast forecast)
    {
        var rows = forecast.Seats;
        var cues = new List<StageCueView>(forecast.Cues.Count);
        foreach (var cue in forecast.Cues)
        {
            cues.Add(new StageCueView(
                cue.Who, cue.Key, IconOf(cue.Kind), cue.Amount,
                cue.Kind == StageCueKind.Damage ? cue.Element : "",
                cue.Kind == StageCueKind.Damage
                    && cue.Target == StageForecastAct.All,
                cue.Price, cue.Times,
                cue.Resting || cue.Times == 0,
                ForecastLine(cue, rows)));
        }
        var bars = rows
            .Select(row => new StageBarChips(
                row.Key, row.Paid, row.Faded,
                forecast.IntentKnown
                    ? forecast.Takers.Where(t => t.Key == row.Key)
                        .Sum(t => t.Takes)
                    : 0,
                row.Leaves || (forecast.IntentKnown
                               && forecast.Takers.Any(t => t.Key == row.Key
                                                           && t.Leaves))))
            .ToList();
        var furina = new StageBarChips(
            -1, 0, 0, forecast.IntentKnown ? forecast.ReachesFurina : 0,
            false);
        return new StageCueBoard(cues, bars, furina);
    }

    /// <summary>The icon an act's cue carries.</summary>
    public static StageCueIcon IconOf(StageCueKind kind) => kind switch
    {
        StageCueKind.Block => StageCueIcon.Block,
        StageCueKind.Energy => StageCueIcon.Energy,
        StageCueKind.Gift => StageCueIcon.Support,
        _ => StageCueIcon.Attack,
    };

    /// <summary>
    /// The hover's forecast line: what this performer's act does to the
    /// Fanfare, in the forecast's own numbers. The act's rule is the other
    /// half of the hover, and is the performer's own badge.
    /// </summary>
    public static string ForecastLine(StageForecastCue cue,
                                      IReadOnlyList<StageForecastSeat> rows)
    {
        if (cue.Resting) return "Came back this turn: does not act.";
        var row = rows.FirstOrDefault(r => r.Key == cue.Key);
        if (cue.Unpaid)
        {
            return cue.Who switch
            {
                StagePerformer.Neuvillette =>
                    $"Cannot pay {cue.Price} of his Fanfare: does nothing.",
                StagePerformer.Chevreuse =>
                    $"Your back performer cannot pay {cue.Price}: "
                    + "does nothing.",
                StagePerformer.Clorinde =>
                    "No other performer to take Fanfare from: does nothing.",
                _ => "Cannot pay: does nothing.",
            };
        }
        var lines = new List<string>();
        if (cue.Who == StagePerformer.Wriothesley && cue.Times == 0)
        {
            lines.Add("Nothing has hit him since his last act.");
        }
        if (cue.Price > 0 && cue.Who == StagePerformer.Chevreuse
            && rows.Count > 0 && rows[^1].Key != cue.Key)
        {
            var bank = rows[^1];
            lines.Add($"Your back performer pays {cue.Price}: "
                      + $"{bank.Now} → {bank.After}.");
        }
        else if (cue.Price > 0)
        {
            var whose = cue.Who == StagePerformer.Neuvillette ? "his" : "her";
            lines.Add($"Pays {cue.Price} of {whose} Fanfare: "
                      + $"{row.Now} → {row.After}.");
        }
        else
        {
            lines.Add($"Fanfare at the end of your turn: "
                      + $"{row.Now} → {row.After}.");
        }
        if (cue.Times > 1) lines.Add($"Acts {cue.Times} times.");
        if (cue.Leaves) lines.Add("Then leaves and takes a Bow.");
        return string.Join("\n", lines);
    }

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
