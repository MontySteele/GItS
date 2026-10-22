using KleeMod.Patches;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// BaseLib's source labels name this mod "Teyvat Spire", not the root
/// namespace "KleeMod" its fallback prints (contact sheet, 2026-10-22).
/// Pure, plus a structural pin on the postfix.
/// </summary>
public class ModSourceNameTests
{
    [Fact]
    public void Our_types_read_Teyvat_Spire_and_everything_else_passes_through()
    {
        Assert.Equal("Teyvat Spire",
            WhatMod_FindModName_TeyvatSpire_Patch.Rename(typeof(KleeMod), "KleeMod"));
        // Another assembly's answer is BaseLib's own.
        Assert.Equal("Downfall",
            WhatMod_FindModName_TeyvatSpire_Patch.Rename(typeof(string), "Downfall"));
        // A name BaseLib chose not to print stays unprinted.
        Assert.Null(WhatMod_FindModName_TeyvatSpire_Patch.Rename(typeof(KleeMod), null));
    }

    [Fact]
    public void The_postfix_goes_through_the_pure_rename()
    {
        Assert.Contains("WhatMod_FindModName_TeyvatSpire_Patch.Rename", Il.Calls(
            Il.Method("WhatMod_FindModName_TeyvatSpire_Patch", "Postfix")));
    }
}
