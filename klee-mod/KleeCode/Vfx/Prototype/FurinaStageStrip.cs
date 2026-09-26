using System.Collections.Generic;
using System.Linq;
using System.Text;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Vfx;

/// <summary>
/// THE THREE-BAR STRIP, and it is a STRIP rather than a panel on purpose.
///
/// WHAT IT REPLACES. The Salon panel (`EB-627`-`EB-629`: a member strip,
/// Encore pips and a Fanfare badge) is 1,500 lines of HUD Control drawing a
/// board this arm does not have -- Encore is retired, the Fanfare counter is
/// retired, and a "member" is now a body with its own bar standing on the
/// field. Under <see cref="FurinaStage"/> it gives way to this.
///
/// WHAT IT HAS TO SAY, and it is one sentence: brief sec.8's last failure mode.
/// "The enemy's arrow points at Furina while the damage lands on the lead.
/// Block already has this property and players read it; the panel must show
/// the lead's bar beside her Block, IN THE DAMAGE ORDER." So the strip is the
/// damage order, left to right, and nothing else:
///
///     BLOCK  >  LEAD'S BAR  >  HER HP
///
/// and the middle and back performers BEHIND it, on a second line, because
/// they are not in the order -- rule 6's absorption never runs on past the
/// lead, and a strip that listed all three in a row would say it does.
///
/// A GAUGE AND NOT A CONTROL. It rides <see cref="GaugeBridge"/>'s
/// <c>furina_stage</c> spec: one script-less scene tracked to her creature
/// node, bar-less (the strip's numbers have no shared ceiling to draw
/// against), with this class's <see cref="Label"/> as its whole text. That
/// buys the refresh funnel, the room-lifetime teardown and the reload rebuild
/// for free, and it is the shape <c>KurageMemoryCard</c> and
/// <c>KokomiPlanStrip</c> already established for an arm's own display.
///
/// PURE, WHICH IS WHY IT CAN BE PINNED. <see cref="Label"/> takes a creature
/// and returns a string; it reads the ledger and the creature's own Block and
/// HP and computes nothing. A display that did its own arithmetic is the
/// preview-truth defect this repo has a rule against
/// (<c>klee-mod-runtime.md</c> sec.3, "a preview reads the resolution's own
/// accessor, never its own arithmetic").
/// </summary>
public static class FurinaStageStrip
{
    /// <summary>Does this creature draw the strip? Furina, and only while the
    /// arm is live -- one read, so the gauge and the pins cannot disagree
    /// about when it is on screen.</summary>
    public static bool AppliesTo(Creature creature) =>
        FurinaStage.LiveFor(creature);

    /// <summary>
    /// The gauge's own value, which is THE LEAD'S BAR: the number the strip is
    /// about and the one a flash would be about. Zero on an empty stage, which
    /// is the honest reading -- there is nothing between her and the intent.
    /// </summary>
    public static int Read(Creature creature) =>
        !FurinaStage.LiveFor(creature)
            ? 0
            : FurinaStageLedger.For(creature).Lead?.Fanfare ?? 0;

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

    /// <summary>Redraw. One line, because the gauge bridge owns the rebuild,
    /// the staleness check and the tracking; every stage mutation funnels
    /// through <c>FurinaStagePets.Sync</c> or a hook that calls this.</summary>
    public static void Refresh(Creature? creature)
    {
        if (creature == null || !FurinaStage.LiveFor(creature)) return;
        GaugeBridge.Refresh(creature);
    }
}
