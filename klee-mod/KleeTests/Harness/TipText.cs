using System;
using System.Linq;
using System.Reflection;

namespace KleeMod.Tests.Harness;

/// <summary>
/// The keyed tip rows (<c>KleeMod.Cards.PlayerTips</c>, internal), read the
/// way a player reads them: headless, a row renders from its English through
/// SmartFormat (<c>CodeText</c>), so a pin on a tip's words reads this.
/// </summary>
internal static class TipText
{
    private const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;

    private static readonly Type Player =
        typeof(CodeText).Assembly.GetType("KleeMod.Cards.PlayerTips")!;

    /// <summary>The tip key's body, rendered.</summary>
    internal static string Of(string key) =>
        (string)Player.GetMethod("Text", Any)!.Invoke(null, new object[] { key, Array.Empty<(string, object)>() })!;

    /// <summary>Every row of the tip key (its body and its variants), raw
    /// English templates, joined by a space.</summary>
    internal static string RowsOf(string key) =>
        string.Join(" ", CodeText.Sources()
            .Where(r => r.Key.StartsWith(key + ".", StringComparison.Ordinal))
            .Select(r => r.English));

    /// <summary>A named body on <c>ArmKeywordTips</c>, a const or a property.</summary>
    internal static string Named(string name)
    {
        var type = typeof(global::KleeMod.Cards.ArmKeywordTips);
        var field = type.GetField(name, Any);
        if (field != null) return (string)(field.IsLiteral ? field.GetRawConstantValue() : field.GetValue(null))!;
        return (string)type.GetProperty(name, Any)!.GetValue(null)!;
    }
}
