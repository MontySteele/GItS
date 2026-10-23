using System.Collections.Generic;
using System.Globalization;
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
/// <see cref="Effect"/> per cell.
///
/// Pure: no Godot, no game node, so the headless suite reads it whole.
/// </summary>
public static class ReactionGuide
{
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

    /// <summary>What the reaction does, short, numbers from the constants.</summary>
    public static string Effect(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize => $"{Mult(ReactionConstants.VaporizeMult)}x damage",
        Reaction.Melt => $"{Mult(ReactionConstants.MeltMult)}x damage",
        Reaction.Overload =>
            $"{ReactionConstants.OverloadSplash} damage to ALL enemies, {ReactionConstants.OverloadWeak} [gold]Weak[/gold]",
        Reaction.Superconduct => $"{ReactionConstants.SuperconductVuln} [gold]Vulnerable[/gold]",
        Reaction.ElectroCharged => $"{ReactionConstants.ElectroChargedDot} [gold]Poison[/gold]",
        Reaction.Frozen =>
            $"its next action deals {Percent(1m - ReactionConstants.FrozenDamageMult)}% less damage",
        Reaction.Swirl => TriggerRules.SwirlPays
            ? $"{ReactionConstants.SwirlDamage} damage to ALL enemies, spreads the aura"
            : "spreads the aura",
        Reaction.Crystallize => $"gain {ReactionConstants.CrystallizeBlock} [gold]Block[/gold]",
        _ => "",
    };

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

    /// <summary>One line: "+ [gold]Hydro[/gold]: Vaporize, 1.5x damage."</summary>
    public static string Line(Element partner, Reaction reaction) =>
        $"+ [gold]{partner}[/gold]: {Name(reaction)}, {Effect(reaction)}.";

    /// <summary>
    /// The hover tip's body for one element.
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
    public static string TipBody(Element element)
    {
        var partners = Partners(element);
        if (element.LeavesAura())
        {
            return string.Join("\n", partners
                .Where(p => p.Partner.LeavesAura())
                .Select(p => Line(p.Partner, p.Reaction)));
        }
        if (partners.Count == 0) return "";
        var names = partners.Select(p => $"[gold]{p.Partner}[/gold]").ToList();
        var joined = names.Count == 1
            ? names[0]
            : string.Join(", ", names.Take(names.Count - 1)) + " or " + names[^1];
        // One reaction for every aura (Swirl, or Crystallize): one line.
        var reaction = partners[0].Reaction;
        return $"+ {joined}: {Name(reaction)}, {Effect(reaction)}.";
    }

    /// <summary>The tip's title, "Pyro Reactions".</summary>
    public static string TipTitle(Element element) => $"{element} Reactions";

    /// <summary>The chart's cell for an aura hit by an element: the reaction
    /// and its effect, or the refresh when the hit is the aura's own.</summary>
    public static string Cell(Element aura, Element hit)
    {
        if (aura == hit) return "Refreshes the aura";
        var r = ReactionTable.Lookup(aura, hit);
        return r == Reaction.None ? "" : $"{Name(r)}\n{Capitalise(Effect(r))}";
    }

    /// <summary>The chart's footnotes: the rules a cell has no room for.</summary>
    public static IReadOnlyList<string> Notes { get; } = new[]
    {
        "[gold]Anemo[/gold] and [gold]Geo[/gold] never stay on an enemy.",
        $"In a boss fight a non-minion can't be Frozen; it gains {ReactionConstants.FrozenBossVuln} [gold]Vulnerable[/gold] instead.",
        $"Attacking a Frozen enemy ends the freeze and deals {ReactionConstants.ShatterDamage} unblockable damage.",
    };

    /// <summary>BBCode tags out, newlines as spaces: the length the text lint
    /// measures (<c>tools/lint_text_conventions.py</c>).</summary>
    public static string Rendered(string text) =>
        System.Text.RegularExpressions.Regex.Replace(text, @"\[/?[a-z]+(=[^\]]*)?\]", "")
            .Replace("\n", " ");

    private static string Capitalise(string s) =>
        s.Length == 0 ? s : char.ToUpperInvariant(s[0]) + s[1..];

    /// <summary>1.5m -> "1.5", 1.75m -> "1.75", invariant so a comma locale
    /// never prints "1,5x" (the reason `KleeMod`'s preview rows keep literals).</summary>
    private static string Mult(decimal m) => m.ToString("0.##", CultureInfo.InvariantCulture);

    private static string Percent(decimal fraction) =>
        (fraction * 100m).ToString("0.##", CultureInfo.InvariantCulture);
}
