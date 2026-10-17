using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Varka's Oath dial by the Energy orb (<see cref="VarkaOathDial"/>, [USER]'s
/// option 2, 2026-10-14). Godot nodes cannot be built in this host (README,
/// the headless boundary), so what is pinned here is every DECISION: which
/// pip is current and lit, which pip a card previews, which counts pulse,
/// where the column lands, whose old badge is hidden, and that the dial rides
/// the funnels that already exist. How it looks is a frame on the next deploy.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaOathDialTests : IDisposable
{
    public VarkaOathDialTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose() => VarkaOathLedger.ResetAll();

    private static readonly Element[] Order =
        { Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo };

    private static Func<Element, int> Counts(int pyro, int hydro, int electro,
                                             int cryo) =>
        e => e switch
        {
            Element.Pyro => pyro,
            Element.Hydro => hydro,
            Element.Electro => electro,
            Element.Cryo => cryo,
            _ => 0,
        };

    private static Dictionary<Element, int> Map(int pyro, int hydro,
                                                int electro, int cryo) =>
        Order.ToDictionary(e => e, Counts(pyro, hydro, electro, cryo));

    private static void AsLocalSeat(ulong me, Action body)
    {
        var was = LocalContext.NetId;
        try
        {
            LocalContext.NetId = me;
            body();
        }
        finally
        {
            LocalContext.NetId = was;
        }
    }

    // ---- which pip is current ---------------------------------------------

    [Fact]
    public void Four_pips_in_the_ledgers_order_each_with_its_count()
    {
        var pips = VarkaOathDial.Pips(Element.Hydro, Counts(2, 5, 0, 1),
                                      readsAllFour: false, Element.None);
        Assert.Equal(Order, pips.Select(p => p.Element));
        Assert.Equal(new[] { 2, 5, 0, 1 }, pips.Select(p => p.Oath));
    }

    [Fact]
    public void The_current_elements_pip_is_large_and_lit_and_the_rest_dim()
    {
        var pips = VarkaOathDial.Pips(Element.Cryo, Counts(3, 0, 0, 1),
                                      readsAllFour: false, Element.None);
        Assert.Equal(Element.Cryo, pips.Single(p => p.IsCurrent).Element);
        Assert.Equal(Element.Cryo, pips.Single(p => p.Lit).Element);
        // A bigger count elsewhere does not make it current.
        Assert.False(pips.Single(p => p.Element == Element.Pyro).Lit);
    }

    [Fact]
    public void Before_any_current_element_all_four_are_dim()
    {
        var pips = VarkaOathDial.Pips(Element.None, Counts(1, 1, 0, 0),
                                      readsAllFour: false, Element.None);
        Assert.DoesNotContain(pips, p => p.IsCurrent);
        Assert.DoesNotContain(pips, p => p.Lit);
        // Geo keeps no Oath: it is never a pip, and never current.
        Assert.Equal(Element.None, VarkaOathDial.CurrentPip(Element.Geo));
    }

    [Fact]
    public void A_read_all_four_turn_lights_every_pip_with_the_current_still_large()
    {
        var pips = VarkaOathDial.Pips(Element.Pyro, Counts(1, 2, 3, 4),
                                      readsAllFour: true, Element.None);
        Assert.All(pips, p => Assert.True(p.Lit));
        Assert.Equal(Element.Pyro, pips.Single(p => p.IsCurrent).Element);
    }

    [Fact]
    public void The_dial_reads_the_ledger_the_badge_reads()
    {
        var varka = Seat.Varka().WithCombatState().Creature;
        var ledger = VarkaOathLedger.For(varka);
        ledger.Add(Element.Electro, 3);
        ledger.SetCurrent(Element.Electro);
        var pips = VarkaOathDial.Pips(ledger.Current, ledger.Oath,
                                      ledger.ReadsAllFour, Element.None);
        var current = pips.Single(p => p.IsCurrent);
        Assert.Equal(Element.Electro, current.Element);
        Assert.Equal(ledger.CurrentOath, current.Oath);
    }

    // ---- the preview ------------------------------------------------------

    [Fact]
    public void A_card_that_would_switch_previews_the_pip_it_makes_current()
    {
        Assert.Equal(Element.Hydro,
            VarkaOathDial.PreviewTarget(Element.Pyro, Element.Hydro, true));
        Assert.Equal(Element.Hydro,
            VarkaOathDial.PreviewTarget(Element.None, Element.Hydro, true));
        // Not while the play would not switch (Unwavering Banner, no fight).
        Assert.Equal(Element.None,
            VarkaOathDial.PreviewTarget(Element.Pyro, Element.Hydro, false));
        // Not onto the element already current.
        Assert.Equal(Element.None,
            VarkaOathDial.PreviewTarget(Element.Hydro, Element.Hydro, true));
        // Not onto an element that keeps no Oath.
        Assert.Equal(Element.None,
            VarkaOathDial.PreviewTarget(Element.Pyro, Element.Geo, true));
    }

    [Fact]
    public void The_previewed_pip_is_marked_and_the_current_one_never_is()
    {
        var pips = VarkaOathDial.Pips(Element.Pyro, Counts(1, 0, 0, 0),
                                      readsAllFour: false, Element.Cryo);
        Assert.Equal(Element.Cryo, pips.Single(p => p.Preview).Element);
        Assert.False(pips.Single(p => p.Element == Element.Cryo).Lit);

        var same = VarkaOathDial.Pips(Element.Pyro, Counts(1, 0, 0, 0),
                                      readsAllFour: false, Element.Pyro);
        Assert.DoesNotContain(same, p => p.Preview);
    }

    [Fact]
    public void A_card_names_the_element_its_switch_line_names()
    {
        Assert.Equal(Element.Hydro,
            VarkaOathDial.SwitchElementOf(new ProtoVkBarbaraShowBegin()));
        Assert.Equal(Element.Pyro,
            VarkaOathDial.SwitchElementOf(new ProtoVkStokeTheFlames()));
        Assert.Equal(Element.None, VarkaOathDial.SwitchElementOf(null));
        // A canonical copy has no owner and no fight: no preview, no throw.
        Assert.Equal(Element.None,
            VarkaOathDial.PreviewFor(new ProtoVkBarbaraShowBegin()));
        Assert.Equal(Element.None, VarkaOathDial.PreviewFor(null));
    }

    [Fact]
    public void Every_switch_card_the_codegen_marks_names_an_oath_element()
    {
        var marked = typeof(IVarkaSwitchCard).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(IVarkaSwitchCard).IsAssignableFrom(t))
            .ToList();
        Assert.True(marked.Count >= 50, $"only {marked.Count} switch cards");
        foreach (var type in marked)
        {
            var card = (IVarkaSwitchCard)Activator.CreateInstance(type)!;
            Assert.True(VarkaOath.IsOathElement(card.VarkaSwitchElement),
                        $"{type.Name} switches to {card.VarkaSwitchElement}");
        }
    }

    // ---- the pulse --------------------------------------------------------

    [Fact]
    public void A_pip_pulses_when_its_oath_rose_since_the_last_paint()
    {
        Assert.Equal(new[] { Element.Hydro },
            VarkaOathDial.Risen(Map(1, 0, 0, 0), Map(1, 2, 0, 0)));
        // A Swirl that pays two elements pulses both, in the ledger's order.
        Assert.Equal(new[] { Element.Pyro, Element.Cryo },
            VarkaOathDial.Risen(Map(1, 0, 0, 0), Map(2, 0, 0, 1)));
        // A count that fell (the Banner moving it away) does not pulse.
        Assert.Empty(VarkaOathDial.Risen(Map(3, 0, 0, 0), Map(0, 0, 0, 0)));
        Assert.Empty(VarkaOathDial.Risen(Map(1, 1, 1, 1), Map(1, 1, 1, 1)));
        // The first paint of a fight pulses nothing.
        Assert.Empty(VarkaOathDial.Risen(null, Map(4, 0, 0, 0)));
    }

    // ---- geometry ---------------------------------------------------------

    [Fact]
    public void The_column_sits_above_the_energy_panel_like_the_star_counter()
    {
        var energy = new Rect2(new Vector2(100f, 806f), new Vector2(128f, 128f));
        var size = new Vector2(72f, VarkaOathDial.Height(72f));
        var at = VarkaOathDial.PlaceDial(energy, size,
                                         new Vector2(1920f, 1080f));
        Assert.Equal(energy.Position.X, at.Position.X);
        Assert.Equal(energy.Position.Y - VarkaOathDial.Margin,
                     at.End.Y, 3);
        // Within the star counter's X span: never right of slot 0.
        Assert.True(at.End.X <= energy.Position.X + 72f);
    }

    [Fact]
    public void With_no_room_above_it_falls_right_of_the_panel()
    {
        var energy = new Rect2(new Vector2(100f, 50f), new Vector2(128f, 128f));
        var size = new Vector2(72f, VarkaOathDial.Height(72f));
        var at = VarkaOathDial.PlaceDial(energy, size,
                                         new Vector2(1920f, 1080f));
        Assert.Equal(energy.End.X + VarkaOathDial.Margin, at.Position.X);
        Assert.True(at.Position.Y >= 0f);
    }

    [Fact]
    public void Pips_stack_in_one_column_with_the_current_one_large()
    {
        const float side = 72f;
        var rects = VarkaOathDial.PipRects(side, Element.Hydro);
        Assert.Equal(4, rects.Count);
        Assert.Equal(side, rects[1].Size.X);
        Assert.Equal(side * VarkaOathDial.SmallScale, rects[0].Size.X, 3);
        for (var i = 1; i < rects.Count; i++)
        {
            Assert.True(rects[i].Position.Y >= rects[i - 1].End.Y);
        }
        Assert.All(rects, r => Assert.True(r.Position.X >= 0f
                                           && r.End.X <= side + 0.001f));
        // The column's bottom is the same whichever pip is current.
        Assert.Equal(VarkaOathDial.Height(side), rects[3].End.Y, 3);
        Assert.Equal(VarkaOathDial.Height(side),
                     VarkaOathDial.PipRects(side, Element.None)[3].End.Y, 3);
    }

    [Fact]
    public void A_varka_holding_sparks_draws_them_above_the_dial()
    {
        var varka = Seat.Varka().Creature;
        var slot = SparkCounter.SlotFor(varka);
        Assert.Equal(VarkaOathDial.SlotsTall(72f), slot);
        // Slot `slot`'s bottom edge clears the dial's top.
        const float side = 72f;
        var clear = slot * (side + VarkaOathDial.Margin) - VarkaOathDial.Margin;
        Assert.True(clear >= VarkaOathDial.Height(side));
        Assert.Equal(0, SparkCounter.SlotFor(Seat.Klee().Creature));
    }

    // ---- scope and the old badge ------------------------------------------

    [Fact]
    public void Varka_gets_the_dial_and_nobody_else_does()
    {
        Assert.True(VarkaOathDial.AppliesTo(Seat.Varka().Creature));
        Assert.False(VarkaOathDial.AppliesTo(Seat.Klee().Creature));
        Assert.False(VarkaOathDial.AppliesTo(Seat.Furina().Creature));
        Assert.False(VarkaOathDial.AppliesTo(null));
    }

    [Fact]
    public void The_old_badge_hides_on_his_screen_and_shows_to_a_partner()
    {
        var seat = Seat.Varka();
        Seat.Set(seat.Player, "NetId", 1UL);
        seat.WithPower<PyroOathPower>(1);
        var badge = seat.Creature.Powers.OfType<PyroOathPower>().Single();

        AsLocalSeat(1UL, () => Assert.True(VarkaOathDial.HidesBadge(badge)));
        AsLocalSeat(2UL, () => Assert.False(VarkaOathDial.HidesBadge(badge)));

        // The left-element flag keeps its own badge.
        seat.WithPower<HydroOathLeftPower>(1);
        var left = seat.Creature.Powers.OfType<HydroOathLeftPower>().Single();
        AsLocalSeat(1UL, () => Assert.False(VarkaOathDial.HidesBadge(left)));

        // A canonical model has no owner to ask, and must not throw.
        Assert.False(VarkaOathDial.HidesBadge(new PyroOathPower()));
    }

    [Fact]
    public void The_badge_stays_on_the_model_so_the_seat_page_keeps_it()
    {
        // Suppressed at the container, never through IsVisibleInternal: the
        // bridge's power list skips an invisible power, and the seat page
        // reads his Oath off the badge's title and sentence.
        var declared = typeof(PyroOathPower)
            .GetProperty("IsVisibleInternal", HeadlessGame.All)
            ?.GetGetMethod(nonPublic: true)
            ?.DeclaringType;
        Assert.Equal(typeof(PowerModel), declared);
    }

    // ---- the funnels ------------------------------------------------------

    [Fact]
    public void The_refresh_is_headless_safe()
    {
        var seat = Seat.Varka().WithCombatState();
        VarkaOathDial.Refresh(seat.Creature);
        VarkaOathDial.Refresh(Seat.Klee().Creature);
        VarkaOathDial.Refresh(null);
    }

    [Fact]
    public void The_dial_rides_the_badge_funnel_and_the_combat_setup()
    {
        Assert.Contains(Il.Calls(Il.Method("OathBadge", "Sync")),
            c => c.EndsWith("VarkaOathDial.Refresh", StringComparison.Ordinal));
        Assert.Contains(Il.Calls(Il.Method("VarkaOath", "TurnStart")),
            c => c.EndsWith("VarkaOathDial.Refresh", StringComparison.Ordinal));
        var activate = Il.Calls(typeof(VarkaOathDial).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Activate_GaugeSetup")!
            .GetMethod("Postfix", HeadlessGame.All)!);
        Assert.Contains(activate,
            c => c.EndsWith("VarkaOathDial.Setup", StringComparison.Ordinal));
        // The star counter's size, as every counter in the corner takes it.
        Assert.Contains(Il.Calls(Il.Method("VarkaOathDial", "Setup")),
            c => c.EndsWith("SparkCounter.SideOf", StringComparison.Ordinal));
    }

    [Fact]
    public void Each_pip_wears_the_vision_his_oath_badge_wears()
    {
        Assert.Equal("varka/powers/pyro_wind.png",
                     VarkaOathDial.GlyphPathFor(Element.Pyro));
        Assert.Equal("varka/powers/hydro_wind.png",
                     VarkaOathDial.GlyphPathFor(Element.Hydro));
        Assert.Equal("varka/powers/electro_wind.png",
                     VarkaOathDial.GlyphPathFor(Element.Electro));
        Assert.Equal("varka/powers/cryo_wind.png",
                     VarkaOathDial.GlyphPathFor(Element.Cryo));
    }
}
