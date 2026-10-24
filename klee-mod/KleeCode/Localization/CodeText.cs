using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using SmartFormat;
using SmartFormat.Extensions;

namespace KleeMod;

/// <summary>
/// One row of player English that code builds: a table, a key and the
/// English template. The template is SmartFormat, the same syntax as every
/// other row (<c>{Name}</c> for a var, <c>{Name:plural:|s}</c> for a plural).
/// </summary>
public sealed record CodeRow(string Table, string Key, string English);

/// <summary>
/// CODE-BUILT TEXT, KEYED (the localization census, 2026-10-23, step 1;
/// [USER]: "I do want to have localization support").
///
/// A hover body or a caption a C# surface builds used to be an English string
/// handed straight to the screen, so a translation file had nothing to
/// replace. Now such a line is a <see cref="CodeRow"/>: authored here in
/// English, merged into the ENGLISH table with every other row of ours
/// (<see cref="Inject"/>, called from <see cref="EnglishLoc.RunInjectors"/>),
/// and read at display time as a <c>LocString</c> (<see cref="Format"/>), so a
/// translated row in the local table wins per key and the vars fill its holes.
///
/// THE RULES, which the two later steps follow:
/// <list type="bullet">
/// <item>A row is a whole sentence (or a whole box). Code never glues English
/// fragments; where two sentences join, the join is a row of its own
/// (<c>{Line} {Act}</c>), so a translator can reorder it.</item>
/// <item>A number is a var read from the law constant it quotes, never baked
/// into the English. A plural is SmartFormat's (<c>{N:plural:|s}</c>).</item>
/// <item>A word filled in at runtime that is itself player text (an element's
/// name) is a var whose value is another row (<see cref="ElementWords"/>).</item>
/// <item>The key is the surface's own key with a leaf for the box:
/// <c>KLEEMOD-ARM_MEND.description</c>, a variant
/// <c>KLEEMOD-ARM_SPARK.description_opening_bank</c>.</item>
/// </list>
///
/// A NEW SURFACE adds its rows to <see cref="Sources"/>; the English
/// reference (<c>klee-mod/localization/reference/eng.json</c>) picks them up
/// because it runs the same injectors.
///
/// HEADLESS (the C# suite, where <c>LocManager.Instance</c> is null) a row is
/// formatted from its English by a SmartFormat formatter built the way
/// <c>LocManager.LoadLocFormatters</c> builds the game's, minus the game's own
/// icon formatters, under English culture. So the suite renders a keyed row
/// exactly as the game's English table would.
/// </summary>
public static class CodeText
{
    private static readonly CultureInfo EnglishCulture = CultureInfo.GetCultureInfo("en");

    /// <summary>Every surface that authors code-built rows. A row source is a
    /// pure function: it may run headless and at boot, before any run.</summary>
    public static IEnumerable<CodeRow> Sources() =>
        Cards.PlayerTips.Rows()
            .Concat(Powers.StagePerformerBadge.TipRows())
            .Concat(Elements.ReactionGuide.Rows())
            .Concat(Elements.ElementWords.Rows())
            // Step 2: Varka and Furina, their face lines, captions and
            // counters, and the card-hover reaction riders.
            .Concat(Powers.VarkaOath.TextRows())
            .Concat(Powers.FurinaStageBowPreview.TextRows())
            .Concat(Vfx.DrainedCounter.TextRows())
            .Concat(new[] { Vfx.FanfareCounter.BodyRow })
            .Concat(Vfx.FurinaStageCues.TextRows())
            .Concat(new[] { Cards.SwirlAuraFace.NoAuraRow, Cards.HalfHpFace.Row })
            .Concat(Cards.KleeCardTooltips.TextRows())
            // Step 3: Kokomi's strip and view, Yae's Annotations, Tenko
            // clause and shrine row, the Spiral Abyss, the leftovers.
            .Concat(Vfx.KokomiPlanText.Rows())
            .Concat(Powers.YaeAnnotationText.Rows())
            .Concat(Powers.YaeShrineFace.Rows())
            .Concat(Vfx.YaeSakuraSlots.Rows())
            .Concat(Abyss.AbyssText.Rows())
            .Concat(Abyss.AbyssOverlayText.Rows())
            .Concat(Vfx.MeterCostBadge.Rows())
            .Concat(Vfx.NationEmblem.Rows())
            .Concat(Vfx.FurinaStageCueNodes.Rows());

    /// <summary>Merge every row into the ENGLISH table it names.</summary>
    internal static void Inject()
    {
        try
        {
            foreach (var group in Sources().GroupBy(r => r.Table))
            {
                EnglishLoc.Table(group.Key).MergeWith(
                    group.ToDictionary(r => r.Key, r => r.English, StringComparer.Ordinal));
            }
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] code-built loc rows failed to merge: {e}");
        }
    }

    /// <summary>
    /// The row as the player reads it: the local table's row where a
    /// translation has one, else our English, with <paramref name="vars"/>
    /// filling the holes. Never throws: a row the tables do not hold (a boot
    /// that failed to merge) prints its English.
    /// </summary>
    public static string Format(CodeRow row, IReadOnlyDictionary<string, object>? vars = null)
    {
        var manager = LocManager.Instance;
        if (manager != null)
        {
            try
            {
                var loc = new LocString(row.Table, row.Key);
                if (loc.Exists())
                {
                    if (vars != null)
                    {
                        foreach (var (name, value) in vars) loc.AddObj(name, value);
                    }
                    return loc.GetFormattedText();
                }
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] {row.Table}/{row.Key} fell back to English: {e.Message}");
            }
        }
        return FormatEnglish(row.English, vars);
    }

    /// <summary>The row's English, formatted, whatever the language: for text
    /// that is itself an English row (a model's description captured at
    /// boot), and the headless path.</summary>
    public static string English(CodeRow row, IReadOnlyDictionary<string, object>? vars = null) =>
        FormatEnglish(row.English, vars);

    /// <summary>A SmartFormat template, formatted under English culture.</summary>
    public static string FormatEnglish(string template, IReadOnlyDictionary<string, object>? vars)
    {
        var args = vars == null
            ? new Dictionary<string, object>(StringComparer.Ordinal)
            : new Dictionary<string, object>(vars, StringComparer.Ordinal);
        return Formatter.Value.Format(EnglishCulture, template, args);
    }

    /// <summary>A decimal law constant as a var: trailing zeros dropped, so
    /// 1.50 prints "1.5" and 50.00 prints "50", as the old literals did. The
    /// culture is the row's (a comma locale's translation prints "1,5").</summary>
    public static decimal Num(decimal value) => value / 1.000000000000000000000000000000000m;

    /// <summary>Vars from name/value pairs.</summary>
    public static IReadOnlyDictionary<string, object> Vars(params (string Name, object Value)[] pairs)
    {
        var vars = new Dictionary<string, object>(StringComparer.Ordinal);
        foreach (var (name, value) in pairs) vars[name] = value;
        return vars;
    }

    /// <summary>Two var sets as one, the second winning.</summary>
    public static IReadOnlyDictionary<string, object> With(
        IReadOnlyDictionary<string, object> vars, params (string Name, object Value)[] more)
    {
        var merged = new Dictionary<string, object>(vars, StringComparer.Ordinal);
        foreach (var (name, value) in more) merged[name] = value;
        return merged;
    }

    private static readonly Lazy<SmartFormatter> Formatter = new(() =>
    {
        // `LocManager.LoadLocFormatters`' list, minus the game's own
        // formatters (energy and star icons, diff highlights, percent,
        // show-if-upgraded, locale numbers), which a code-built row does not
        // use and which need the game running.
        var formatter = new SmartFormatter();
        var list = new ListFormatter();
        formatter.AddExtensions(list, new DictionarySource(), new ValueTupleSource(),
                                new ReflectionSource(), new DefaultSource());
        formatter.AddExtensions(list, new PluralLocalizationFormatter(), new ConditionalFormatter(),
                                new ChooseFormatter(), new SubStringFormatter(), new IsMatchFormatter(),
                                new DefaultFormatter());
        return formatter;
    });
}
