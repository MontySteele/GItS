using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Powers;

/// <summary>
/// A GUEST'S NAME AS PLAYER TEXT (the localization census, 2026-10-23, step
/// 2), the way <see cref="Elements.ElementWords"/> names an element. Where
/// code fills a guest into a sentence -- "(Clorinde acts, then leaves)",
/// "(+3 Block: Freminet)" -- the name is a var whose value is this row, so a
/// translation names the guest in its own words. <c>card_keywords</c>,
/// <c>KLEEMOD-STAGE_PERFORMER_NAME.CLORINDE</c>; its English is
/// <see cref="FurinaStageLedger.DisplayName"/>.
/// </summary>
public static class PerformerWords
{
    private const string Table = "card_keywords";

    /// <summary>The guest's row.</summary>
    public static CodeRow RowOf(StagePerformer who) =>
        new(Table, "KLEEMOD-STAGE_PERFORMER_NAME." + who.ToString().ToUpperInvariant(),
            FurinaStageLedger.DisplayName(who));

    /// <summary>The guest's name as the player reads it.</summary>
    public static string Name(StagePerformer who) => CodeText.Format(RowOf(who));

    public static IEnumerable<CodeRow> Rows() =>
        System.Enum.GetValues<StagePerformer>().Select(RowOf);
}
