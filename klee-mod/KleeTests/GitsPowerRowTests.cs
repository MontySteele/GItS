using System.Collections.Generic;
using STS2_MCP;
using Xunit;

namespace KleeTests;

/// <summary>
/// KOKOMI REVIEW R8 (2026-10-14, item 10): a power whose text throws keeps
/// its row. At Water's Edge vanished from a seat's list for a screen against
/// Hunter Killer; the bridge's per-power catch skipped the whole row. The
/// rule lives in <c>vendor/STS2_MCP/gits/GitsPowerRow.cs</c> (compiled here,
/// one file, no fork). Page twin:
/// <c>tier0/tests/test_kokomi_review_r8_2026_10_14.py</c>.
/// </summary>
public class GitsPowerRowTests
{
    [Fact]
    public void The_row_keeps_what_needs_no_text_and_says_why()
    {
        var row = GitsPowerRow.Unreadable(
            "KLEEMOD-AT_WATERS_EDGE_POWER", "At Water's Edge", 1, "Counter",
            "Buff", "NullReferenceException");
        Assert.Equal("At Water's Edge", row["name"]);
        Assert.Equal(1, row["amount"]);
        Assert.Equal("Counter", row["stack"]);
        Assert.Equal("Buff", row["type"]);
        Assert.Null(row["description"]);
        Assert.Empty((List<Dictionary<string, object?>>)row["keywords"]!);
        Assert.Equal("NullReferenceException", row["unreadable"]);
    }

    [Fact]
    public void A_power_with_no_title_is_named_by_its_id()
    {
        var row = GitsPowerRow.Unreadable("SOME_POWER", null, 2, "Counter",
                                          "Debuff", "InvalidOperationException");
        Assert.Equal("SOME_POWER", row["name"]);
    }
}
