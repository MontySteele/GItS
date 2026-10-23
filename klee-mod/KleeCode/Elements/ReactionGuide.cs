using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Elements;

/// <summary>
/// THE REACTION CHART'S WORDS, generated from the live table so they cannot
/// drift ([USER], 2026-10-22: "hover tips are a good idea if you're about to
/// trigger one, but it would help to have some way to find them all in-game").
///
/// Every pair is read from <see cref="ReactionTable.Lookup"/> and every number
/// from <see cref="ReactionConstants"/>; nothing here names a reaction for a
/// pair by hand. Two surfaces read it: the per-element hover tip
/// (<see cref="TipBody"/>, on the element's card keyword and on its aura) and
/// the in-run chart (<c>Vfx.ReactionChart</c>), which prints the same
/// effect per cell.
///
/// KEYED (the localization census, 2026-10-23). The generator writes
/// TEMPLATES, not text: each element's tip
/// (<c>KLEEMOD-REACTIONS_PYRO.description</c>), each reaction's chart cell
/// (<c>KLEEMOD-REACTION_CHART.cells.VAPORIZE</c>), the chart's notes and
/// labels are whole rows (<see cref="Rows"/>) with the numbers as vars
/// (<see cref="Vars"/>), so a translation replaces a whole tip or cell and the
/// table still decides which pairs are in it.
///
/// Pure: no Godot, no game node, so the headless suite reads it whole.
/// </summary>
public static class ReactionGuide
{
    private const string Table = "card_keywords";
    private const string Chart = "KLEEMOD-REACTION_CHART";

    /// <summary>The six elements the engine has, in the chart's order. The
    /// engine has no Dendro (<see cref="Element"/>), so the chart has six.</summary>
    public static IReadOnlyList<Element> Elements { get; } = new[]
    {
        Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo, Element.Anemo, Element.Geo,
    };

    /// <summary>The four that stay on an enemy, the chart's rows.</summary>
    public static IReadOnlyList<Element> AuraElements { get; } =
        Elements.Where(e => e.LeavesAura()).ToArray();

    /// <summary>The reaction's printed name, the preview tips' own.</summary>
    public static string Name(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize => "Vaporize",
        Reaction.Melt => "Melt",
        Reaction.Overload => "Overloaded",
        Reaction.Superconduct => "Superconduct",
        Reaction.ElectroCharged => "Electro-Charged",
        Reaction.Frozen => "Frozen",
        Reaction.Swirl => "Swirl",
        Reaction.Crystallize => "Crystallize",
        _ => "",
    };

    /// <summary>The numbers the templates quote, read off the constants.</summary>
    public static IReadOnlyDictionary<string, object> Vars => CodeText.Vars(
        ("VaporizeMult", CodeText.Num(ReactionConstants.VaporizeMult)),
        ("MeltMult", CodeText.Num(ReactionConstants.MeltMult)),
        ("OverloadSplash", ReactionConstants.OverloadSplash),
        ("OverloadWeak", ReactionConstants.OverloadWeak),
        ("SuperconductVuln", ReactionConstants.SuperconductVuln),
        ("ElectroChargedDot", ReactionConstants.ElectroChargedDot),
        ("FrozenLessPercent", CodeText.Num((1m - ReactionConstants.FrozenDamageMult) * 100m)),
        ("SwirlDamage", ReactionConstants.SwirlDamage),
        ("CrystallizeBlock", ReactionConstants.CrystallizeBlock),
        ("FrozenBossVuln", ReactionConstants.FrozenBossVuln),
        ("ShatterDamage", ReactionConstants.ShatterDamage));

    /// <summary>What the reaction does, short: the template, numbers as vars.</summary>
    private static string EffectTemplate(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize => "{VaporizeMult}x damage",
        Reaction.Melt => "{MeltMult}x damage",
        Reaction.Overload =>
            "{OverloadSplash} damage to ALL enemies, {OverloadWeak} [gold]Weak[/gold]",
        Reaction.Superconduct => "{SuperconductVuln} [gold]Vulnerable[/gold]",
        Reaction.ElectroCharged => "{ElectroChargedDot} [gold]Poison[/gold]",
        Reaction.Frozen => "its next action deals {FrozenLessPercent}% less damage",
        Reaction.Swirl => TriggerRules.SwirlPays
            ? "{SwirlDamage} damage to ALL enemies, spreads the aura"
            : "spreads the aura",
        Reaction.Crystallize => "gain {CrystallizeBlock} [gold]Block[/gold]",
        _ => "",
    };

    /// <summary>What the reaction does, short, in English (the suite's
    /// reading of a cell or a tip line; no surface prints it alone).</summary>
    public static string Effect(Reaction reaction) =>
        CodeText.FormatEnglish(EffectTemplate(reaction), Vars);

    /// <summary>The reacting partners of <paramref name="element"/>, each with
    /// its reaction, in <see cref="Elements"/> order. An aura element lists
    /// the other aura elements it reacts with; Anemo and Geo list every aura
    /// they react with. Read from the table both ways round (aura first, then
    /// hit first), so a pair either side can start is found.</summary>
    public static IReadOnlyList<(Element Partner, Reaction Reaction)> Partners(Element element)
    {
        var list = new List<(Element, Reaction)>();
        foreach (var other in Elements)
        {
            if (other == element) continue;
            // Only an element that stays on an enemy can be the aura side:
            // the table's trigger check would otherwise answer Anemo-then-Geo
            // with a Crystallize no board can hold.
            var r = element.LeavesAura() ? ReactionTable.Lookup(element, other) : Reaction.None;
            if (r == Reaction.None && other.LeavesAura()) r = ReactionTable.Lookup(other, element);
            if (r != Reaction.None) list.Add((other, r));
        }
        return list;
    }

    private static string LineTemplate(Element partner, Reaction reaction) =>
        $"+ [gold]{partner}[/gold]: {Name(reaction)}, {EffectTemplate(reaction)}.";

    /// <summary>One line, in English: "+ [gold]Hydro[/gold]: Vaporize, 1.5x
    /// damage."</summary>
    public static string Line(Element partner, Reaction reaction) =>
        CodeText.FormatEnglish(LineTemplate(partner, reaction), Vars);

    /// <summary>
    /// The hover tip's template for one element; "" for an element with no
    /// reaction.
    ///
    /// AN AURA ELEMENT lists its partners among the other three auras, one
    /// line each. Anemo and Geo react with every aura the same way, so those
    /// two pairs live in the Anemo and Geo tips and in the chart; carried on
    /// all four aura tips they would put each past the tip ceiling
    /// (<c>docs/current/text-conventions.md</c>, 135).
    ///
    /// ANEMO AND GEO name the four auras on one line, since their reaction is
    /// the same with each.
    /// </summary>
    private static string TipTemplate(Element element)
    {
        var partners = Partners(element);
        if (element.LeavesAura())
        {
            return string.Join("\n", partners
                .Where(p => p.Partner.LeavesAura())
                .Select(p => LineTemplate(p.Partner, p.Reaction)));
        }
        if (partners.Count == 0) return "";
        var names = partners.Select(p => $"[gold]{p.Partner}[/gold]").ToList();
        var joined = names.Count == 1
            ? names[0]
            : string.Join(", ", names.Take(names.Count - 1)) + " or " + names[^1];
        // One reaction for every aura (Swirl, or Crystallize): one line.
        var reaction = partners[0].Reaction;
        return $"+ {joined}: {Name(reaction)}, {EffectTemplate(reaction)}.";
    }

    /// <summary>The element's tip row, or null for one with no reaction.</summary>
    public static CodeRow? TipRow(Element element)
    {
        var template = TipTemplate(element);
        return template.Length == 0
            ? null
            : new CodeRow(Table, "KLEEMOD-REACTIONS_" + element.ToString().ToUpperInvariant()
                                 + ".description", template);
    }

    /// <summary>The hover tip's body for one element, as the player reads it;
    /// "" for an element with no reaction.</summary>
    public static string TipBody(Element element) =>
        TipRow(element) is { } row ? CodeText.Format(row, Vars) : "";

    /// <summary>The tip's title, "Pyro Reactions".</summary>
    public static string TipTitle(Element element) => $"{element} Reactions";

    private static CodeRow CellRow(Reaction reaction) =>
        new(Table, Chart + ".cells." + reaction.ToString().ToUpperInvariant(),
            $"{Name(reaction)}\n{Capitalise(EffectTemplate(reaction))}");

    private static readonly CodeRow RefreshRow = new(Table, Chart + ".cells.REFRESH", "Refreshes the aura");

    /// <summary>The chart's cell for an aura hit by an element: the reaction
    /// and its effect, or the refresh when the hit is the aura's own.</summary>
    public static string Cell(Element aura, Element hit)
    {
        if (aura == hit) return CodeText.Format(RefreshRow);
        var r = ReactionTable.Lookup(aura, hit);
        return r == Reaction.None ? "" : CodeText.Format(CellRow(r), Vars);
    }

    private static readonly CodeRow[] NoteRows =
    {
        new(Table, Chart + ".notes.NO_AURA",
            "[gold]Anemo[/gold] and [gold]Geo[/gold] never stay on an enemy."),
        new(Table, Chart + ".notes.FROZEN_BOSS",
            "In a boss fight a non-minion cannot be Frozen; it gains {FrozenBossVuln} "
          + "[gold]Vulnerable[/gold] instead."),
        new(Table, Chart + ".notes.SHATTER",
            "Attacking a Frozen enemy ends the freeze and deals {ShatterDamage} "
          + "unblockable damage."),
    };

    /// <summary>The chart's footnotes: the rules a cell has no room for.</summary>
    public static IReadOnlyList<string> Notes => NoteRows.Select(r => CodeText.Format(r, Vars)).ToList();

    // The chart's own labels and the top-bar button's hover.
    internal static readonly CodeRow HeadingRow = new(Table, Chart + ".heading", "Elemental Reactions");
    internal static readonly CodeRow LegendRow = new(Table, Chart + ".legend",
        "Rows: the aura on the enemy. Columns: the element of the hit.");
    // SmartFormat reads a backslash as an escape, so the one the corner
    // prints is written twice.
    internal static readonly CodeRow CornerRow = new(Table, Chart + ".corner", "Aura \\\\ Hit");
    internal static readonly CodeRow CloseRow = new(Table, Chart + ".close",
        "Click outside or press Esc to close.");
    internal static readonly CodeRow ButtonTipRow = new(Table, Chart + ".description",
        "Every element and what it reacts with.");

    /// <summary>A chart label as the player reads it.</summary>
    public static string Label(CodeRow row) => CodeText.Format(row);

    /// <summary>Every row (<see cref="CodeText.Sources"/>): a tip per
    /// reacting element, a cell per reaction the chart shows, the notes and
    /// the labels.</summary>
    public static IEnumerable<CodeRow> Rows()
    {
        foreach (var element in Elements)
        {
            if (TipRow(element) is { } tip) yield return tip;
        }
        var shown = AuraElements
            .SelectMany(aura => Elements.Select(hit => ReactionTable.Lookup(aura, hit)))
            .Where(r => r != Reaction.None)
            .Distinct();
        foreach (var reaction in shown) yield return CellRow(reaction);
        yield return RefreshRow;
        foreach (var note in NoteRows) yield return note;
        yield return HeadingRow;
        yield return LegendRow;
        yield return CornerRow;
        yield return CloseRow;
        yield return ButtonTipRow;
    }

    /// <summary>BBCode tags out, newlines as spaces: the length the text lint
    /// measures (<c>tools/lint_text_conventions.py</c>).</summary>
    public static string Rendered(string text) =>
        System.Text.RegularExpressions.Regex.Replace(text, @"\[/?[a-z]+(=[^\]]*)?\]", "")
            .Replace("\n", " ");

    private static string Capitalise(string s) =>
        s.Length == 0 ? s : char.ToUpperInvariant(s[0]) + s[1..];
}
