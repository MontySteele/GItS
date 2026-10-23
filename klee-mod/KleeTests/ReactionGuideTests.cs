using System.Linq;
using KleeMod.Abyss;
using KleeMod.Elements;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE REACTION TIPS AND THE CHART, pinned to the live table ([USER],
/// 2026-10-22: "hover tooltips are a good idea if you're about to trigger
/// one, but it would help to have some way to find them all in-game").
/// The chart's nodes are Godot (process death here); its words and its
/// open/closed state are not.
/// </summary>
public class ReactionGuideTests
{
    /// <summary>The tip ceiling, `docs/current/text-conventions.md`.</summary>
    private const int TipCeiling = 135;

    [Fact]
    public void The_Pyro_tip_reads_the_table_and_the_constants()
    {
        Assert.Equal(
            "+ [gold]Hydro[/gold]: Vaporize, 1.5x damage.\n"
            + "+ [gold]Electro[/gold]: Overloaded, 6 damage to ALL enemies, 1 [gold]Weak[/gold].\n"
            + "+ [gold]Cryo[/gold]: Melt, 1.75x damage.",
            ReactionGuide.TipBody(Element.Pyro));
    }

    [Fact]
    public void Every_reacting_pair_appears_in_a_tip_and_in_the_chart()
    {
        var all = ReactionGuide.Elements;
        var pairs = 0;
        foreach (var aura in all.Where(e => e.LeavesAura()))
        {
            foreach (var hit in all)
            {
                var r = ReactionTable.Lookup(aura, hit);
                if (r == Reaction.None) continue;
                pairs++;
                var name = ReactionGuide.Name(r);
                Assert.False(string.IsNullOrEmpty(name));
                Assert.False(string.IsNullOrEmpty(ReactionGuide.Effect(r)));

                // The pair is in the tip of the element that names the other:
                // an aura pair in both aura tips, a Swirl or a Crystallize in
                // the Anemo or Geo tip.
                var line = ReactionGuide.Line(hit, r);
                if (hit.LeavesAura())
                {
                    Assert.Contains(line, ReactionGuide.TipBody(aura));
                    Assert.Contains(ReactionGuide.Line(aura, r), ReactionGuide.TipBody(hit));
                }
                else
                {
                    var tip = ReactionGuide.TipBody(hit);
                    Assert.Contains($"[gold]{aura}[/gold]", tip);
                    Assert.Contains($"{name}, {ReactionGuide.Effect(r)}.", tip);
                }

                Assert.Equal($"{name}\n", ReactionGuide.Cell(aura, hit)[..(name.Length + 1)]);
            }
        }
        // Six aura pairs, each counted from both sides, plus four Swirls and
        // four Crystallizes.
        Assert.Equal(6 * 2 + 4 + 4, pairs);
    }

    [Fact]
    public void A_pair_that_does_not_react_is_in_no_tip()
    {
        Assert.DoesNotContain("Geo", ReactionGuide.TipBody(Element.Anemo));
        Assert.DoesNotContain("Anemo", ReactionGuide.TipBody(Element.Geo));
        Assert.Equal("Refreshes the aura", ReactionGuide.Cell(Element.Hydro, Element.Hydro));
    }

    [Fact]
    public void Every_tip_is_under_the_tip_ceiling()
    {
        foreach (var element in ReactionGuide.Elements)
        {
            var body = ReactionGuide.TipBody(element);
            Assert.NotEqual("", body);
            Assert.True(ReactionGuide.Rendered(body).Length <= TipCeiling,
                $"{element}: {ReactionGuide.Rendered(body).Length} > {TipCeiling}: {body}");
        }
    }

    [Fact]
    public void The_numbers_follow_the_constants()
    {
        Assert.Contains($"{ReactionConstants.SuperconductVuln} [gold]Vulnerable[/gold]",
                        ReactionGuide.TipBody(Element.Cryo));
        Assert.Contains($"{ReactionConstants.ElectroChargedDot} [gold]Poison[/gold]",
                        ReactionGuide.TipBody(Element.Hydro));
        Assert.Contains($"gain {ReactionConstants.CrystallizeBlock} [gold]Block[/gold]",
                        ReactionGuide.TipBody(Element.Geo));
        Assert.Contains("50% less damage", ReactionGuide.TipBody(Element.Hydro));
    }

    [Fact]
    public void The_chart_opens_closes_and_takes_a_dismiss_only_when_open()
    {
        var state = new ReactionChartState();
        Assert.False(state.IsOpen);
        Assert.False(state.OnDismiss());     // Esc with nothing open is not the chart's
        Assert.True(state.Toggle());         // the button opens
        Assert.True(state.IsOpen);
        Assert.False(state.Toggle());        // the button again closes
        Assert.True(state.Toggle());
        Assert.True(state.OnDismiss());      // a click outside, or Esc
        Assert.False(state.IsOpen);
        Assert.False(state.Close());         // a second close does nothing
    }

    [Fact]
    public void The_chart_turns_the_games_tags_into_Godots()
    {
        Assert.Equal("1 [color=#efc851]Weak[/color]", ReactionChartState.ToGodotBbcode("1 [gold]Weak[/gold]"));
    }

    // ---- The Ley Line names the element (2026-10-22) -----------------------

    [Theory]
    [InlineData(0, "Hydro")]
    [InlineData(1, "Pyro")]
    [InlineData(2, "Electro")]
    [InlineData(5, "Electro")]
    public void The_Ley_Line_names_the_acts_element(int act, string element)
    {
        Assert.Equal(
            $"Each enemy turn, every enemy without an aura takes [gold]{element}[/gold]. "
            + "An enemy wearing an aura deals 1 less damage.",
            AbyssText.Text(AbyssBlessing.LeyLine, act));
    }

    [Fact]
    public void A_Ley_Line_held_since_act_1_names_the_element_of_the_act_being_played()
    {
        Assert.Contains("[gold]Pyro[/gold]", AbyssText.Text(AbyssBlessing.LeyLine, 0, elementAct: 1));
        Assert.Contains("a shield of [gold]Electro[/gold]", AbyssText.Text(AbyssShadow.MageShield, 0, elementAct: 2));
    }

    [Fact]
    public void With_no_act_known_the_text_lists_all_three()
    {
        Assert.Equal(
            "Each enemy turn, every enemy without an aura takes this act's element. "
            + "An enemy wearing an aura deals 1 less damage. The element is "
            + "[gold]Hydro[/gold] in act 1, [gold]Pyro[/gold] in act 2, [gold]Electro[/gold] in act 3.",
            AbyssText.Text(AbyssBlessing.LeyLine, AbyssText.NoAct));
        Assert.EndsWith(
            "Shields are [gold]Hydro[/gold] in act 1, [gold]Pyro[/gold] in act 2, [gold]Electro[/gold] in act 3.",
            AbyssText.Text(AbyssShadow.MageShield, AbyssText.NoAct));
    }

    [Fact]
    public void No_Abyss_text_says_this_acts_element_where_the_act_is_known()
    {
        foreach (var b in AbyssDraft.AllBlessings)
        {
            for (var act = 0; act < 3; act++) Assert.DoesNotContain("this act's element", AbyssText.Text(b, act));
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            for (var act = 0; act < 3; act++) Assert.DoesNotContain("this act's element", AbyssText.Text(s, act));
        }
    }
}
