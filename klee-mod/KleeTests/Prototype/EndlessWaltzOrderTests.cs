using System;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-412` -- Endless Waltz's +3 reaches the two members it deploys.
///
/// THE FIND (Furina r4 run 2 (c) 2, again at r7 fight 6). Under the reframe a
/// Deploy performs the member it fields at once, and the card printed its two
/// deploys above its crescendo -- so the pair joined at the unbumped 4 and 2
/// while a Companion play one beat later performed at 6.
///
/// THE FIX IS ON THE SHEET, not here: `docs/furina-cards.yaml` prints the
/// `salon_damage_up` line first and `tools/gen_roster_cards.py` re-emits
/// `OnPlay` in that order, so both engines take the order from one place.
/// What this file pins is the emitted order, because a number in this mod
/// needs a live `CombatState` (the README's headless boundary) and the
/// behavioural claim is pinned in tier0
/// (`test_eb412_endless_waltz_buffs_before_it_deploys.py`).
///
/// THE SNAPSHOT LINE IS THE OTHER HALF. `SalonMemberPower.ReplacementDelta`
/// asks `WillReplace` off the PRE-PLAY company, so the scaled value has to be
/// captured above all three calls for the replacement doubling to survive the
/// move. It still is, and that is the assertion order below.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class EndlessWaltzOrderTests
{
    [Fact]
    public void The_crescendo_is_applied_before_either_deploy()
    {
        var source = Generated("EndlessWaltz.cs");

        var snapshot = source.IndexOf("var salonScaledPowerAmount =",
            StringComparison.Ordinal);
        var apply = source.IndexOf("PowerCmd.Apply<SalonDamageUpPower>",
            StringComparison.Ordinal);
        var crabaletta = source.IndexOf("SalonMember.Crabaletta)",
            StringComparison.Ordinal);
        var usher = source.IndexOf("SalonMember.Usher)",
            StringComparison.Ordinal);

        Assert.True(snapshot >= 0 && apply >= 0 && crabaletta >= 0
                    && usher >= 0);
        Assert.True(snapshot < apply, "the scaled value is captured first");
        Assert.True(apply < crabaletta, "the buff stands before the pair");
        Assert.True(crabaletta < usher);
    }

    [Fact]
    public void The_buff_still_spends_the_replacement_scaled_value()
    {
        // Not the raw 3: on a full stage the crescendo doubles, and the
        // closed form is what lets it do so from ABOVE the deploys.
        Assert.Contains("(int)salonScaledPowerAmount", Generated("EndlessWaltz.cs"));
    }

    [Fact]
    public void The_face_reads_in_the_order_the_card_resolves()
    {
        var source = Generated("EndlessWaltz.cs");
        var description = source.IndexOf("(\"description\", \"",
            StringComparison.Ordinal);
        Assert.True(description >= 0);

        var line = source.Substring(description,
            source.IndexOf('\n', description) - description);
        Assert.True(
            line.IndexOf("numbers are", StringComparison.Ordinal)
            < line.IndexOf("Mademoiselle Crabaletta", StringComparison.Ordinal),
            "the printed order must follow the resolved order");
    }

    private static string Generated(string fileName) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode", "Cards",
            "Furina", "Generated", fileName));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
