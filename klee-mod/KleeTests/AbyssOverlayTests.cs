using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using KleeMod.Abyss;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SPIRAL ABYSS BLESSING SCREEN (owner, 2026-10-12: "a pop-up on-screen
/// with the choice of three blessings before the Ancient screen loads").
///
/// On the suite's usual terms (README.md, the headless boundary): the words,
/// the open/close sequence, the co-op result and the bridge's page run for
/// real; the Harmony seams and the order "page back, then screen closes, then
/// greeting" are STRUCTURAL pins, because a room, a layout and a vote need the
/// game. What only the game can show -- the screen over the room, the fade,
/// controller focus, two machines voting -- is the PR's live-check list, and
/// the look is the rig's (tools/abyss_overlay_rig).
/// </summary>
public class AbyssOverlayTests
{
    private static AbyssOffer Offer(int act = 0) => new(act, new[]
    {
        new AbyssOption(AbyssBlessing.LeyLine, AbyssShadow.MageShield),
        new AbyssOption(AbyssBlessing.MoonlitRest, AbyssShadow.SheerCold),
        new AbyssOption(AbyssBlessing.FirstStrike, AbyssShadow.Riptide),
    }, 0);

    // ---- The words ------------------------------------------------------------

    [Fact]
    public void The_title_names_the_act_and_Neow_is_act_one()
    {
        Assert.Equal("The Spiral Abyss · Act 1", AbyssOverlayContent.TitleFor(0));
        Assert.Equal("The Spiral Abyss · Act 3", AbyssOverlayContent.TitleFor(2));
        // Co-op Abyss run, 2026-10-14: the page says where the enemies'
        // Shadow comes from, so a Shadow beside a Blessing is not read as
        // the one that comes with it.
        Assert.Equal("The Abyss whispers, urging you deeper. Take one Blessing. "
                     + "The enemies take one Shadow, at random, from the Blessings you pass.",
                     AbyssOverlayContent.Whisper);
    }

    [Fact]
    public void Each_card_carries_its_Blessing_and_the_Shadow_it_brings_if_passed()
    {
        var content = AbyssOverlayContent.For(Offer(), new AbyssRecord());
        Assert.Equal(3, content.Cards.Count);
        var card = content.Cards[0];
        Assert.Equal("The Ley Line", card.BlessingName);
        Assert.Equal(AbyssText.Text(AbyssBlessing.LeyLine, 0), card.BlessingText);
        Assert.Equal("Abyss Mage Shield", card.ShadowName);
        Assert.Equal(AbyssText.Text(AbyssShadow.MageShield, 0), card.ShadowText);
        Assert.Equal(new[] { 0, 1, 2 }, content.Cards.Select(c => c.Index));
        Assert.Equal("The Ley Line text\nIf you pass this, the enemies may take its Shadow: Rally — Rally text",
            AbyssOverlayContent.BridgeDescription(card with
            {
                BlessingText = "The Ley Line text", ShadowName = "Rally", ShadowText = "Rally text",
            }));
    }

    [Fact]
    public void The_strip_is_empty_on_the_first_visit_and_lists_what_the_run_holds_after()
    {
        Assert.False(AbyssOverlayContent.For(Offer(), new AbyssRecord()).HasStrip);

        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.Crystallize, AbyssShadow.Herald);
        record.Record(1, AbyssBlessing.Resonance, AbyssShadow.Clock);
        var content = AbyssOverlayContent.For(Offer(2), record);
        Assert.True(content.HasStrip);
        Assert.Equal(new[] { "Jade Shield", "Resonance" }, content.BlessingsTaken.Select(e => e.Name));
        Assert.Equal(new[] { "Abyss Herald", "The Clock" }, content.ShadowsInForce.Select(e => e.Name));
        // Each strip entry prints the numbers of the act it was taken in
        // (review/active/abyss-act-scaling-2026-10-18.md): Jade Shield and the
        // Herald act 1's, the Clock act 2's, on act 3's page.
        Assert.Equal(AbyssText.Text(AbyssShadow.Clock, 1), content.ShadowsInForce[1].Text);
        Assert.Equal("Start each combat with 8 Block.", content.BlessingsTaken[0].Text);
    }

    [Fact]
    public void The_icons_are_the_ones_the_relics_and_badges_already_wear()
    {
        foreach (var b in AbyssDraft.AllBlessings)
        {
            var relic = RuntimeHelpers.GetUninitializedObject(AbyssDisplay.RelicTypeFor(b));
            var file = relic.GetType().GetProperty("IconFile", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public)!
                .GetValue(relic);
            Assert.Equal(file, AbyssOverlayContent.BlessingIconFile(b));
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            var power = (AbyssShadowPower)RuntimeHelpers.GetUninitializedObject(AbyssDisplay.PowerTypeFor(s));
            Assert.Equal(power.IconFile, AbyssOverlayContent.ShadowIconFile(s));
        }
    }

    [Fact]
    public void Every_strip_entry_has_a_tooltip_title_row()
    {
        var rows = AbyssChoicePage.LocRows();
        foreach (var name in AbyssDraft.AllBlessings.Select(AbyssText.Name)
                     .Concat(AbyssDraft.AllShadows.Select(AbyssText.Name)))
        {
            Assert.Equal(name, rows[AbyssChoicePage.StripTitleKey(name)]);
        }
    }

    // ---- The sequence -------------------------------------------------------

    [Fact]
    public void Solo_the_screen_opens_holds_the_dialogue_takes_one_pick_and_closes_once()
    {
        var flow = new AbyssOverlayFlow();
        Assert.False(flow.HoldsDialogue);
        Assert.True(flow.Open());
        Assert.False(flow.Open());
        Assert.True(flow.HoldsDialogue);

        Assert.False(flow.Vote(3, 3));
        Assert.True(flow.Vote(1, 3));
        Assert.False(flow.Vote(1, 3));

        // Solo shows its result line too (co-op Abyss run, 2026-10-14: the
        // page never said which Shadow the enemies took).
        Assert.Equal(AbyssOverlayFlow.ResultSeconds, flow.Resolve(1, "Moonlit Rest", "Riptide", coop: false, split: false));
        Assert.Equal("You chose Moonlit Rest. The enemies took Riptide.", flow.ResultLine);
        Assert.Equal(AbyssOverlayPhase.Resolving, flow.Phase);
        Assert.True(flow.HoldsDialogue);
        Assert.False(flow.Vote(0, 3));

        Assert.True(flow.BeginFade());
        Assert.True(flow.FinishFade());
        Assert.False(flow.FinishFade());
        Assert.False(flow.HoldsDialogue);
        // A pick already made is never offered again by this screen.
        Assert.False(flow.Open());
    }

    [Fact]
    public void In_coop_a_vote_can_change_and_the_result_line_shows_before_the_fade()
    {
        var flow = new AbyssOverlayFlow();
        flow.Open();
        Assert.True(flow.Vote(0, 3));
        Assert.True(flow.Vote(2, 3));
        Assert.Equal(2, flow.LocalVote);

        Assert.Equal(AbyssOverlayFlow.ResultSeconds, flow.Resolve(0, "The Ley Line", "Sheer Cold", coop: true, split: true));
        Assert.Equal(2.5, AbyssOverlayFlow.ResultSeconds);
        Assert.Equal(AbyssOverlayPhase.Resolving, flow.Phase);
        Assert.Equal("The vote split; the draw gave The Ley Line. The enemies took Sheer Cold.", flow.ResultLine);
        Assert.True(flow.HoldsDialogue);
        // The other copy of the shared event resolves too: nothing more.
        Assert.Null(flow.Resolve(0, "The Ley Line", "Sheer Cold", coop: true, split: true));
        Assert.False(flow.FinishFade());
        Assert.True(flow.BeginFade());
        Assert.True(flow.FinishFade());
    }

    [Fact]
    public void The_result_line_says_whether_the_vote_split()
    {
        Assert.Equal("The party chose Moonlit Rest. The enemies took Riptide.",
                     AbyssOverlayFlow.ResultLineFor("Moonlit Rest", "Riptide", coop: true, split: false));
        Assert.Equal("The vote split; the draw gave Moonlit Rest. The enemies took Riptide.",
                     AbyssOverlayFlow.ResultLineFor("Moonlit Rest", "Riptide", coop: true, split: true));
        Assert.Equal("You chose Moonlit Rest. The enemies took Riptide.",
                     AbyssOverlayFlow.ResultLineFor("Moonlit Rest", "Riptide", coop: false, split: false));
        // An offer with no Shadow to give names none.
        Assert.Equal("You chose Moonlit Rest.",
                     AbyssOverlayFlow.ResultLineFor("Moonlit Rest", null, coop: false, split: false));

        Assert.False(AbyssVoteOutcome.Split(new int?[] { 1, 1 }, 1));
        Assert.True(AbyssVoteOutcome.Split(new int?[] { 0, 2 }, 2));
        Assert.True(AbyssVoteOutcome.Split(new int?[] { 0, 1, 1 }, 1));
        // A client that never received the host's vote: its own lost, so
        // the partner's was the result and the vote split.
        Assert.True(AbyssVoteOutcome.Split(new int?[] { 0, null }, 2));
        Assert.False(AbyssVoteOutcome.Split(new int?[] { 2, null }, 2));
    }

    // ---- The seams (structural) -----------------------------------------------

    [Fact]
    public void The_screen_hooks_the_layout_before_the_dialogue_and_owns_the_vote_display()
    {
        Assert.Equal((typeof(NAncientEventLayout), nameof(NAncientEventLayout.SetDialogue)),
                     Target("NAncientEventLayout_SetDialogue_AbyssOverlay_Patch"));
        Assert.Equal((typeof(NAncientEventLayout), nameof(NAncientEventLayout.OnSetupComplete)),
                     Target("NAncientEventLayout_OnSetupComplete_AbyssOverlay_Patch"));
        Assert.Equal((typeof(NAncientEventLayout), nameof(NAncientEventLayout.DefaultFocusedControl)),
                     Target("NAncientEventLayout_DefaultFocusedControl_AbyssOverlay_Patch"));
        Assert.Equal((typeof(NEventLayout), nameof(NEventLayout.BeforeSharedOptionChosen)),
                     Target("NEventLayout_BeforeSharedOptionChosen_AbyssOverlay_Patch"));
        Assert.Equal((typeof(EventSynchronizer), "ChooseOptionForSharedEvent"),
                     Target("EventSynchronizer_ChooseOptionForSharedEvent_AbyssOverlay_Patch"));
        // The patched members exist on this game build.
        Assert.NotNull(AccessTools.Method(typeof(EventSynchronizer), "ChooseOptionForSharedEvent"));
        Assert.NotNull(AbyssOverlay.LayoutEventField);
    }

    [Fact]
    public void The_pick_puts_the_Ancient_page_back_before_the_screen_closes_and_the_greeting_resumes_last()
    {
        var chosen = Il.Calls(Il.Method("AbyssChoicePage", "OnChosen"));
        Assert.Contains("AbyssOverlay.OnChosen", chosen);
        Assert.Contains("MethodBase.Invoke", chosen);

        var click = Il.Calls(Il.Method("AbyssOverlay", "Click"));
        Assert.Contains("NEventRoom.OptionButtonClicked", click);
        Assert.Contains("AbyssOverlayFlow.Vote", click);

        var close = Il.Calls(Il.Method("AbyssOverlay", "Close"));
        Assert.Contains("AbyssOverlayFlow.FinishFade", close);
        Assert.Contains("NAncientEventLayout.SetDialogue", close);
        // A virtual call resolves to the declaring type.
        Assert.Contains("NEventLayout.OnSetupComplete", close);
    }

    // ---- Controller focus (owner, 2026-10-12: "I don't see a way to select a
    // Blessing from my controller") ---------------------------------------------

    [Fact]
    public void The_cards_run_the_game_clickables_own_wiring()
    {
        // ConnectSignals is what turns FocusEntered / MouseEntered into the
        // clickable's Focused signal, and MousePressed into Released. Only the
        // game's subclasses call it (from _Ready); a bare NClickableControl
        // never did, so the cards never lit up.
        var connect = AbyssOverlay.ConnectSignalsMethod;
        Assert.NotNull(connect);
        Assert.Equal(typeof(NClickableControl), connect!.DeclaringType);
        Assert.Empty(connect.GetParameters());

        Assert.Contains("MethodBase.Invoke", Il.Calls(Il.Method("AbyssOverlay", "WireClickable")));
        // ... after the view has set the focus mode: Build runs first.
        var open = Il.CallSequence(Il.Method("AbyssOverlay", "OpenIfShowing")).ToList();
        Assert.Contains("AbyssOverlay.WireClickable", open);
        Assert.True(open.IndexOf("AbyssOverlayView.Build") < open.IndexOf("AbyssOverlay.WireClickable"));

        // Hover and focus reach the card through the one signal pair.
        Assert.Contains("AbyssOverlayView.SetCardFocused", Il.Calls(Il.Method("AbyssOverlay", "MakeHit")));
    }

    [Fact]
    public void The_room_and_the_layout_hand_controller_focus_to_the_cards()
    {
        // NEventRoom.DefaultFocusedControl asks the layout; the Ancient layout
        // declares its own getter, which the screen patches.
        var getter = AccessTools.PropertyGetter(typeof(NAncientEventLayout), nameof(NAncientEventLayout.DefaultFocusedControl));
        Assert.NotNull(getter);
        Assert.Equal(typeof(NAncientEventLayout), getter!.DeclaringType);
        var patch = typeof(AbyssOverlay).Assembly.GetType(
            "KleeMod.Abyss.NAncientEventLayout_DefaultFocusedControl_AbyssOverlay_Patch", throwOnError: true)!;
        Assert.Equal((MethodType?)MethodType.Getter, patch.GetCustomAttributes<HarmonyPatch>().Single().info.methodType);
        Assert.Contains("AbyssOverlayView.Hit", Il.Calls(Il.Method("AbyssOverlay", "FocusFor")));
        // The first card is focused when the screen opens.
        Assert.Contains("NodeUtil.TryGrabFocus", Il.Calls(Il.Method("AbyssOverlay", "Started")));
    }

    [Fact]
    public void Left_and_right_walk_the_three_cards_and_wrap()
    {
        Assert.Equal((2, 1), AbyssOverlayView.Neighbors(0, 3));
        Assert.Equal((0, 2), AbyssOverlayView.Neighbors(1, 3));
        Assert.Equal((1, 0), AbyssOverlayView.Neighbors(2, 3));

        // Every direction is named, so Godot never looks for a neighbour of
        // its own behind the screen.
        var wire = Il.Calls(Il.Method("AbyssOverlayView", "WireFocusNeighbors"));
        foreach (var setter in new[]
                 {
                     "set_FocusNeighborLeft", "set_FocusNeighborRight", "set_FocusNeighborTop",
                     "set_FocusNeighborBottom", "set_FocusNext", "set_FocusPrevious",
                 })
        {
            Assert.Contains("Control." + setter, wire);
        }
        Assert.Contains("AbyssOverlayView.Neighbors", wire);
        Assert.Contains("AbyssOverlayView.WireFocusNeighbors", Il.Calls(Il.Method("AbyssOverlayView", "Build")));
    }

    // ---- The SHADOW label and the X ---------------------------------------------

    [Fact]
    public void The_lower_band_is_labelled_SHADOW()
    {
        Assert.Equal("Shadow", AbyssOverlayContent.ShadowBandLabel);
        Assert.Equal("SHADOW", AbyssOverlayView.BandLabel(AbyssOverlayContent.ShadowBandLabel));
        Assert.Contains("AbyssOverlayView.BandLabel", Il.Calls(Il.Method("AbyssOverlayView", "BuildCard")));
    }

    [Fact]
    public void The_X_marks_the_focused_card_and_this_players_pick_only()
    {
        Assert.False(AbyssOverlayView.ShowsCross(focused: false, chosen: false));
        Assert.True(AbyssOverlayView.ShowsCross(focused: true, chosen: false));
        Assert.True(AbyssOverlayView.ShowsCross(focused: false, chosen: true));
        Assert.Contains("AbyssOverlayView.ShowsCross", Il.Calls(Il.Method("AbyssOverlayView", "Animate")));
    }

    [Fact]
    public void The_X_is_one_outline_from_corner_to_corner()
    {
        var box = new Godot.Rect2(30, 26, 340, 200);
        var points = AbyssOverlayView.CrossPolygon(box, 13f);
        Assert.Equal(12, points.Length);
        var centre = box.Position + box.Size / 2f;
        // Point-symmetric about the band's centre: arm i mirrors arm i + 2.
        for (var i = 0; i < 6; i++)
        {
            var mirrored = centre * 2f - points[i];
            Assert.True(mirrored.DistanceTo(points[i + 6]) < 0.01f, $"point {i}");
        }
        // The inner corners sit close to the centre, the outer ones at the tips.
        for (var i = 0; i < 4; i++)
        {
            Assert.True(points[i * 3 + 2].DistanceTo(centre) < 40f);
            Assert.True(points[i * 3].DistanceTo(centre) > 150f);
        }
    }

    private static (Type, string) Target(string patchName)
    {
        var patch = typeof(AbyssOverlay).Assembly.GetType("KleeMod.Abyss." + patchName, throwOnError: true)!;
        var attr = patch.GetCustomAttributes<HarmonyPatch>().Single().info;
        return (attr.declaringType, attr.methodName);
    }

    // ---- The bridge's page ----------------------------------------------------

    [Fact]
    public void The_bridge_reads_the_screen_as_its_own_page()
    {
        Assert.Equal(GitsAbyssPage.MetaKey, AbyssOverlay.PageMeta);
        Assert.Equal(GitsAbyssPage.RootName, AbyssOverlayView.RootName);

        var content = AbyssOverlayContent.For(Offer(), new AbyssRecord());
        var flow = new AbyssOverlayFlow();
        flow.Open();
        var json = AbyssOverlay.PageJson(content, flow);
        Assert.True(GitsAbyssPage.IsOpen(json));

        var state = new Dictionary<string, object?>
        {
            ["event_name"] = "Neow", ["in_dialogue"] = true, ["options"] = new List<Dictionary<string, object?>>(),
        };
        Assert.True(GitsAbyssPage.Apply(state, json));
        Assert.Equal("The Spiral Abyss", state["event_name"]);
        Assert.Equal(AbyssOverlayContent.Whisper, state["body"]);
        Assert.Equal(false, state["in_dialogue"]);
        var options = (List<Dictionary<string, object?>>)state["options"]!;
        Assert.Equal(new[] { "The Ley Line", "Moonlit Rest", "First Strike" }, options.Select(o => o["title"]));
        Assert.Equal(new object?[] { 0, 1, 2 }, options.Select(o => o["index"]));
        Assert.Equal(AbyssText.Text(AbyssBlessing.MoonlitRest, 0) + "\nIf you pass this, the enemies may take its Shadow: Sheer Cold — "
                     + AbyssText.Text(AbyssShadow.SheerCold, 0), options[1]["description"]);
        var screen = (Dictionary<string, object?>)state["abyss_screen"]!;
        Assert.Equal("The Spiral Abyss · Act 1", screen["subtitle"]);
        Assert.Equal(false, screen["resolved"]);
    }

    [Fact]
    public void Once_the_pick_lands_the_page_offers_nothing_and_says_what_was_taken()
    {
        var content = AbyssOverlayContent.For(Offer(), new AbyssRecord());
        var flow = new AbyssOverlayFlow();
        flow.Open();
        flow.Vote(1, 3);
        flow.Resolve(1, "Moonlit Rest", "Abyss Mage Shield", coop: true, split: false);
        var json = AbyssOverlay.PageJson(content, flow);
        Assert.False(GitsAbyssPage.IsOpen(json));

        var state = new Dictionary<string, object?>();
        GitsAbyssPage.Apply(state, json);
        Assert.Empty((List<Dictionary<string, object?>>)state["options"]!);
        var screen = (Dictionary<string, object?>)state["abyss_screen"]!;
        Assert.Equal(true, screen["resolved"]);
        Assert.Equal("Moonlit Rest", screen["chosen"]);
        Assert.Equal("The party chose Moonlit Rest. The enemies took Abyss Mage Shield.", screen["result"]);
        Assert.Equal(screen["result"], state["abyss_result"]);
    }

    [Fact]
    public void After_the_screen_the_room_still_says_which_Shadow_the_enemies_took()
    {
        // Co-op Abyss run, 2026-10-14: "the page does not say which Shadow
        // lands on the enemies". The screen is up for seconds; the room
        // carries the result line for as long as it lasts.
        Assert.Equal(GitsAbyssPage.ResultMetaKey, AbyssOverlay.ResultMeta);

        var state = new Dictionary<string, object?> { ["event_name"] = "Neow" };
        GitsAbyssPage.ApplyResult(state, "You chose Overflow. The enemies took Fatui Skirmishers.");
        Assert.Equal("You chose Overflow. The enemies took Fatui Skirmishers.", state["abyss_result"]);
        Assert.Equal("Neow", state["event_name"]);
        var empty = new Dictionary<string, object?>();
        GitsAbyssPage.ApplyResult(empty, null);
        GitsAbyssPage.ApplyResult(empty, " ");
        Assert.Empty(empty);

        // STRUCTURAL: the glue names the Shadow the record takes (the same
        // ShadowIfChosen roll) and puts the line on the room.
        var chosen = Il.Calls(typeof(AbyssOverlay).GetMethod("OnChosen", BindingFlags.NonPublic | BindingFlags.Static)!);
        Assert.Contains("AbyssOffer.ShadowIfChosen", chosen);
        Assert.Contains("GodotObject.SetMeta", chosen);
    }

    [Fact]
    public void Unreadable_json_leaves_the_room_as_it_was()
    {
        var state = new Dictionary<string, object?> { ["event_name"] = "Neow" };
        Assert.False(GitsAbyssPage.Apply(state, "not json"));
        Assert.Equal("Neow", state["event_name"]);
        Assert.False(GitsAbyssPage.IsOpen("not json"));
    }
}
