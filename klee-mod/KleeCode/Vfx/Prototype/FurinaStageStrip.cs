using System.Collections.Generic;
using System.Linq;
using System.Text;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Vfx;

/// <summary>
/// THE STAGE'S TEXT FORECAST, which is no longer drawn.
///
/// This was the overhead strip: a <c>furina_stage</c> gauge on
/// <see cref="GaugeBridge"/>'s second row whose whole text was
/// <see cref="Label"/> -- the damage order (Block > the lead's bar > her HP),
/// the reserve, and the end-of-turn forecast as lines. The Furina balance
/// review (2026-09-26, pick 2a) retired the text box: "each performer shows
/// its act over its head the way an enemy shows its intent; the fade and
/// incoming hits show as chips on its bar; the text box goes." The gauge spec
/// is deleted and the drawing is <see cref="FurinaStageCues"/>'s.
///
/// WHAT STAYS, and why: <see cref="Label"/> and <see cref="ForecastLines"/>
/// are the forecast in words, pinned by the stage's tests, and
/// <see cref="NameOf"/> is the short name the pins read. Nothing on screen
/// draws them; the blind seat page prints its own text forecast off the wire
/// (<c>FurinaStageLedger.Snapshot</c>), unchanged.
///
/// PURE: <see cref="Label"/> reads the ledger, the forecast and the
/// creature's own Block and HP, and computes nothing.
/// </summary>
public static class FurinaStageStrip
{
    /// <summary>Short names, because the strip is a strip. The full names live
    /// on the bodies themselves (<c>StagePerformerMonster.DisplayName</c>),
    /// which is where a player hovers to read one.</summary>
    private static readonly Dictionary<StagePerformer, string> Short = new()
    {
        [StagePerformer.Usher] = "Usher",
        [StagePerformer.Chevalmarin] = "Cheval",
        [StagePerformer.Crabaletta] = "Crab",
        // THE GUEST CAST (2026-09-25): a guest's name is short already.
        [StagePerformer.Neuvillette] = "Neuvillette",
        [StagePerformer.Clorinde] = "Clorinde",
        [StagePerformer.Navia] = "Navia",
        [StagePerformer.Chevreuse] = "Chevreuse",
        [StagePerformer.Wriothesley] = "Wriothesley",
        [StagePerformer.Sigewinne] = "Sigewinne",
        [StagePerformer.Charlotte] = "Charlotte",
        [StagePerformer.Lynette] = "Lynette",
    };

    public static string NameOf(StagePerformer who) =>
        Short.TryGetValue(who, out var name) ? name : who.ToString();

    /// <summary>
    /// The strip's whole text.
    ///
    /// LINE ONE IS THE DAMAGE ORDER and always has three terms, even on an
    /// empty stage -- where the middle one is an em dash, because "nobody is
    /// standing there" is exactly the fact a player about to eat a posted
    /// intent needs. Dropping the term instead would make the empty stage look
    /// like a shorter sentence rather than a missing buffer.
    ///
    /// LINE TWO IS THE RESERVE, front to back, and is omitted entirely when
    /// there is none. It is the Ovation plan's board (sec.5.2 reads the back
    /// performer) and the Refill's target (rule 5), so it prints the same
    /// numbers in the same order the Raise will find them in.
    /// </summary>
    public static string Label(Creature creature)
    {
        if (!FurinaStage.LiveFor(creature)) return string.Empty;
        var ledger = FurinaStageLedger.For(creature);
        var seats = ledger.Seats;

        var lead = seats.Count > 0
            ? $"{NameOf(seats[0].Who)} {seats[0].Fanfare}"
            : "--";
        var line = new StringBuilder()
            .Append(Blocked(creature))
            .Append(" > ")
            .Append(lead)
            .Append(" > ")
            .Append(Hp(creature));

        if (seats.Count > 1)
        {
            line.Append('\n').Append(string.Join(
                "  ",
                seats.Skip(1).Select(s => $"{NameOf(s.Who)} {s.Fanfare}")));
        }
        foreach (var more in ForecastLines(creature)) line.Append('\n').Append(more);
        return line.ToString();
    }

    /// <summary>
    /// THE GUEST CAST's RULE 7 (2026-09-25): "You can see the end of the turn
    /// before you end it." One line of each performer's bar after this
    /// turn's acts, payments and fade (<c>Neuvillette 6 → 3</c>), and one of
    /// the posted attacks' split, given her Block after the acts. Read off
    /// <see cref="FurinaStage.Forecast"/>, which does the arithmetic once for
    /// the strip and the page alike; a forecast that throws draws nothing.
    /// </summary>
    public static IEnumerable<string> ForecastLines(Creature creature)
    {
        StageForecast? forecast;
        try
        {
            forecast = FurinaStage.Forecast(creature);
        }
        catch (System.Exception)
        {
            yield break;
        }
        if (forecast == null || forecast.Seats.Count == 0) yield break;
        var rows = forecast.Seats
            .Select(r => $"{NameOf(r.Who)} {r.Now} → {r.After}"
                         + (r.Leaves ? " (leaves)" : ""))
            .Concat(forecast.Arrivals
                .Select(r => $"{NameOf(r.Who)} back at {r.After}"));
        yield return "End: " + string.Join("  ", rows);
        // 2026-09-25 night (the granted-guest seat round): what the acts
        // deal, and in all where every act lands on one body or on ALL.
        if (forecast.Acts.Count > 0)
        {
            yield return "Acts: " + string.Join("  ",
                forecast.Acts.Select(ActLine));
            if (forecast.ActTotal >= 0)
            {
                yield return $"Acts in all: {forecast.ActTotal} to "
                             + TargetWord(forecast.ActTotalTarget);
            }
        }
        if (forecast.IntentKnown)
        {
            // Hit by hit, performer by performer: the next one steps up when
            // the front empties and Bows.
            var takes = forecast.Takers
                .Select(t => $"{NameOf(t.Who)} {t.Takes}"
                             + (t.Leaves ? " (leaves)" : ""))
                .Concat(new[] { $"you {forecast.ReachesFurina}" });
            yield return "Hits: " + string.Join(", ", takes);
        }
    }

    /// <summary>One act of the forecast: "Crabaletta 5 to a random enemy",
    /// "Neuvillette 8 Hydro to ALL".</summary>
    private static string ActLine(StageForecastAct act) =>
        $"{NameOf(act.Who)}{(act.Bow ? " Bow" : "")} {act.Amount}"
        + (act.Element.Length > 0 ? " " + act.Element : "")
        + " to " + TargetWord(act.Target);

    /// <summary>A forecast target in the base game's words.</summary>
    internal static string TargetWord(string target) => target switch
    {
        StageForecastAct.All => "ALL",
        StageForecastAct.Random => "a random enemy",
        StageForecastAct.RandomAura => "a random enemy with an aura",
        _ => target,
    };

    /// <summary>Her Block, the FIRST term of the damage order and the engine's
    /// own number.</summary>
    private static int Blocked(Creature creature) => (int)creature.Block;

    /// <summary>Her HP, the LAST term. Rule 11: nothing in this kit touches
    /// it, which is exactly why it belongs on the strip -- it is the thing the
    /// two terms in front of it are protecting.</summary>
    private static int Hp(Creature creature) => (int)creature.CurrentHp;
}
