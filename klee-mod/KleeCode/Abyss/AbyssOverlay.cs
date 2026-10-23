using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using KleeMod.Story;
using MegaCrit.Sts2.Core.Entities.Ancients;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// THE SPIRAL ABYSS BLESSING SCREEN, IN THE ROOM (owner, 2026-10-12: "All of
/// these options are tiny text on the Ancient screen. Could we get a pop-up
/// on-screen with the choice of three blessings before the Ancient screen
/// loads?").
///
/// WHAT STAYS. The choice is still the Ancient event's first page
/// (<see cref="AbyssChoicePage"/>): its three options, the shared vote in
/// co-op (host draws a split at random), the save behaviour, the bridge's
/// vote report. What changes is only what the player SEES of that page: the
/// Ancient's layout is hidden and this screen is drawn over the room in its
/// place, and a click on a card is the click the page's option button would
/// have made (<c>NEventRoom.OptionButtonClicked</c>, the call
/// <c>NEventOptionButton.OnRelease</c> makes).
///
/// HOW THE DIALOGUE WAITS. <c>NEventRoom.SetupLayout</c> hands the Ancient's
/// greeting to <c>NAncientEventLayout.SetDialogue</c> before the options; while
/// the Abyss page is up that call is held here (the lines are kept, nothing is
/// shown), so the layout sets up as a page with no dialogue, and this screen
/// opens from <c>OnSetupComplete</c>. When the pick lands, the page goes back
/// to the Ancient's own (<c>AbyssChoicePage.OnChosen</c>), the screen shows
/// its result line (the pick and the Shadow the enemies took) for
/// <see cref="AbyssOverlayFlow.ResultSeconds"/>, fades, and then the held lines are given
/// to the layout and <c>OnSetupComplete</c> runs again: the greeting plays
/// and the Ancient's options follow it, exactly as in a normal run.
///
/// THE SEAT BRIDGE reads this screen off the node: the root carries
/// <see cref="PageMeta"/>, a JSON page (title, body, options), and each card's
/// clickable is a game <c>NClickableControl</c> named
/// <see cref="AbyssOverlayView.CardNodeName"/>, so the bridge's
/// <c>ForceClick</c> runs the same handler a mouse release does. Once the
/// pick lands, the room itself carries <see cref="ResultMeta"/>, the result
/// line, for as long as the room lasts: the screen is up for seconds, and a
/// seat that looks after it has gone still reads which Shadow the enemies
/// took (co-op Abyss run, 2026-10-14: "the page does not say which Shadow
/// lands on the enemies").
///
/// Normal runs: every patch asks <see cref="AbyssChoicePage.IsShowing"/>
/// first, which is only ever true in a run carrying the Abyss.
/// </summary>
public static class AbyssOverlay
{
    /// <summary>The bridge's contract: the root's JSON page.</summary>
    public const string PageMeta = "gits_abyss_page";

    /// <summary>The bridge's contract: the room's result line, after the
    /// pick (the bridge's <c>GitsAbyssPage.ResultMetaKey</c>).</summary>
    public const string ResultMeta = "gits_abyss_result";

    public static readonly FieldInfo? LayoutEventField = AccessTools.Field(typeof(NEventLayout), "_event");
    internal static readonly FieldInfo? RoomEventField = AccessTools.Field(typeof(NEventRoom), "_event");

    /// <summary>The game's clickable wires its own input in
    /// <c>ConnectSignals</c> (FocusEntered/MouseEntered to its Focused
    /// signal, MousePressed/MouseReleased to Released), and only its
    /// subclasses call it, from their <c>_Ready</c>. A bare
    /// <c>new NClickableControl()</c> never does, so the card never said it
    /// was focused or hovered (no highlight, owner 2026-10-12: "I don't see a
    /// way to select a Blessing from my controller"). The screen calls it
    /// itself, after the view has set the card's focus mode.</summary>
    public static readonly MethodInfo? ConnectSignalsMethod =
        AccessTools.Method(typeof(NClickableControl), "ConnectSignals");

    private sealed class Session
    {
        public NAncientEventLayout Layout = null!;
        public EventModel Event = null!;
        public AbyssOffer Offer = null!;
        public AbyssOverlayContent Content = null!;
        public AbyssOverlayView View = null!;
        public readonly AbyssOverlayFlow Flow = new();
        public readonly List<NMultiplayerVoteContainer> VoteContainers = new();
        public Action<Player>? VoteHandler;
        public bool Coop;
    }

    private static readonly ConditionalWeakTable<NAncientEventLayout, Session> Sessions = new();

    /// <summary>The Ancient's greeting, held while the screen is up.</summary>
    private static readonly ConditionalWeakTable<NAncientEventLayout, List<AncientDialogueLine>> Held = new();

    /// <summary>The last shared Abyss vote, read before the game clears it:
    /// the votes in player-slot order and the option the host drew.</summary>
    private static (EventModel? Event, List<int?> Votes, int Chosen)? _lastVote;

    internal static EventModel? EventOf(NEventLayout layout) => LayoutEventField?.GetValue(layout) as EventModel;

    // ---- Seams (called from the patches below) ------------------------------

    /// <summary>SetDialogue prefix: hold the greeting while the page is up.
    /// Returns false to skip the layout's own call.</summary>
    internal static bool HoldDialogue(NAncientEventLayout layout, IReadOnlyList<AncientDialogueLine> lines)
    {
        if (!AbyssChoicePage.IsShowing(EventOf(layout))) return true;
        Held.AddOrUpdate(layout, lines.ToList());
        return false;
    }

    /// <summary>OnSetupComplete postfix: open the screen over the room.</summary>
    internal static void OpenIfShowing(NAncientEventLayout layout)
    {
        var ev = EventOf(layout);
        if (!AbyssChoicePage.IsShowing(ev) || Sessions.TryGetValue(layout, out _)) return;
        var offer = AbyssChoicePage.OfferOf(ev!);
        var abyss = SpiralAbyss.In(ev!.Owner?.RunState);
        if (offer == null || abyss == null) return;
        var room = NEventRoom.Instance;
        if (room == null) return;

        var session = new Session
        {
            Layout = layout,
            Event = ev,
            Offer = offer,
            Content = AbyssOverlayContent.For(offer, abyss.Record),
            Coop = (ev.Owner?.RunState.Players.Count ?? 1) > 1,
        };
        if (!session.Flow.Open()) return;

        session.View = AbyssOverlayView.Build(ViewData(session.Content), Fonts(), i => MakeHit(session, i));
        for (var i = 0; i < session.View.CardCount; i++) WireClickable(session.View.Hit(i));
        session.View.Root.SetMeta(PageMeta, PageJson(session));
        room.AddChildSafely(session.View.Root);
        Sessions.AddOrUpdate(layout, session);

        SetLayoutContentVisible(layout, false);
        WireStrip(session);
        if (session.Coop) WireVotes(session);
        session.View.Root.TreeExiting += () => Unwire(session);
        // AddChildSafely may defer the add; the tweens and the focus wait for
        // the tree.
        if (session.View.Root.IsInsideTree()) Started(session);
        else session.View.Root.Connect(Node.SignalName.TreeEntered, Callable.From(() => Started(session)),
                                       (uint)GodotObject.ConnectFlags.OneShot);
    }

    private static void Started(Session session)
    {
        session.View.FadeIn();
        session.View.EqualizeOverFrames();
        session.View.Hit(0).TryGrabFocus();
    }

    /// <summary>While the screen is up, controller focus belongs to it: the
    /// room's and the layout's default focus is the first card.</summary>
    internal static Control? FocusFor(NAncientEventLayout layout) =>
        Sessions.TryGetValue(layout, out var s) && s.Flow.Phase != AbyssOverlayPhase.Closed
            ? s.View.Hit(Math.Clamp(s.Flow.LocalVote ?? 0, 0, s.View.CardCount - 1))
            : null;

    /// <summary>The layout's split-vote animation plays on its own (hidden)
    /// buttons; while the screen is up it owns the vote display instead.</summary>
    internal static bool OwnsSharedVote(NEventLayout layout) =>
        layout is NAncientEventLayout ancient && Sessions.TryGetValue(ancient, out var s)
        && s.Flow.Phase != AbyssOverlayPhase.Closed;

    /// <summary>ChooseOptionForSharedEvent prefix: the votes, before the
    /// game clears them.</summary>
    internal static void CaptureVotes(EventSynchronizer sync, uint chosen)
    {
        var local = sync.GetLocalEvent();
        if (!AbyssChoicePage.IsShowing(local)) return;
        var players = local.Owner?.RunState.Players;
        if (players == null) return;
        var votes = new List<int?>();
        foreach (var p in players)
        {
            uint? v = null;
            try { v = sync.GetPlayerVote(p); } catch { /* slot gone */ }
            votes.Add(v.HasValue ? (int)v.Value : null);
        }
        _lastVote = (local, votes, (int)chosen);
    }

    /// <summary>The page's option ran on this event copy (from
    /// <see cref="AbyssChoicePage"/>, after the Ancient's page is back). Only
    /// the copy this machine's room shows has a screen.</summary>
    internal static void OnChosen(EventModel ev, AbyssOffer offer, int index)
    {
        var room = NEventRoom.Instance;
        if (room?.Layout is not NAncientEventLayout layout) return;
        if (!Sessions.TryGetValue(layout, out var session) || !ReferenceEquals(session.Event, ev)) return;

        var name = AbyssText.Name(offer.Options[index].Blessing);
        var split = false;
        if (session.Coop && _lastVote is { } last && ReferenceEquals(last.Event, ev))
        {
            split = AbyssVoteOutcome.Split(last.Votes, last.Chosen);
        }
        var shadow = offer.ShadowIfChosen(index);
        var shadowName = shadow == AbyssShadow.None ? null : AbyssText.Name(shadow);
        var hold = session.Flow.Resolve(index, name, shadowName, session.Coop, split);
        if (hold == null) return;
        if (session.Flow.ResultLine is { } said && GodotObject.IsInstanceValid(room))
        {
            room.SetMeta(ResultMeta, said);
        }

        session.View.Root.SetMeta(PageMeta, PageJson(session));
        session.View.SetCardChosen(index);
        session.View.DimAllBut(index);
        RefreshVotes(session);
        if (session.Flow.ResultLine is { } line) session.View.ShowResult(line);

        var tree = session.View.Root.GetTree();
        if (hold.Value > 0 && tree != null)
        {
            tree.CreateTimer(hold.Value).Timeout += () => Fade(session);
        }
        else
        {
            Fade(session);
        }
    }

    private static void Fade(Session session)
    {
        if (!GodotObject.IsInstanceValid(session.View.Root) || !session.Flow.BeginFade()) return;
        session.View.FadeOut(AbyssOverlayFlow.FadeSeconds, () => Close(session));
    }

    /// <summary>The screen is gone: show the layout again and let the Ancient
    /// speak, as <c>NEventRoom.SetupLayout</c> would have.</summary>
    private static void Close(Session session)
    {
        if (!session.Flow.FinishFade()) return;
        var layout = session.Layout;
        Sessions.Remove(layout);
        if (GodotObject.IsInstanceValid(session.View.Root)) session.View.Root.QueueFreeSafely();
        if (!GodotObject.IsInstanceValid(layout)) return;
        try
        {
            SetLayoutContentVisible(layout, true);
            if (Held.TryGetValue(layout, out var lines))
            {
                Held.Remove(layout);
                if (lines.Count > 0) layout.SetDialogue(lines);
            }
            layout.OnSetupComplete();
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen: the Ancient's dialogue could not resume: {e}");
        }
    }

    // ---- Building ---------------------------------------------------------------

    /// <summary>Run the game clickable's own signal wiring on a card (see
    /// <see cref="ConnectSignalsMethod"/>). Its focus mode must be set first:
    /// the clickable reads it to know it is controller-navigable.</summary>
    internal static void WireClickable(Control hit)
    {
        if (hit is not NClickableControl clickable) return;
        if (ConnectSignalsMethod == null)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen: NClickableControl.ConnectSignals is gone; the cards will not highlight.");
            return;
        }
        ConnectSignalsMethod.Invoke(clickable, null);
    }

    private static Control MakeHit(Session session, int index)
    {
        var hit = new NClickableControl();
        hit.Connect(NClickableControl.SignalName.Released,
            Callable.From<NClickableControl>(_ => Click(session, index)));
        hit.Connect(NClickableControl.SignalName.Focused,
            Callable.From<NClickableControl>(_ => session.View?.SetCardFocused(index, true)));
        hit.Connect(NClickableControl.SignalName.Unfocused,
            Callable.From<NClickableControl>(_ => session.View?.SetCardFocused(index, false)));
        return hit;
    }

    /// <summary>A card was released (mouse, controller, or the bridge's
    /// ForceClick): the click the page's own option button makes.</summary>
    private static void Click(Session session, int index)
    {
        try
        {
            var options = session.Event.CurrentOptions;
            if (!AbyssChoicePage.IsShowing(session.Event) || index >= options.Count) return;
            if (!session.Flow.Vote(index, options.Count)) return;
            session.View.SetCardChosen(index);
            NEventRoom.Instance?.OptionButtonClicked(options[index], index);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen: the pick failed: {e}");
        }
    }

    private static AbyssOverlayViewData ViewData(AbyssOverlayContent content)
    {
        var data = new AbyssOverlayViewData
        {
            Title = content.Title,
            Whisper = AbyssOverlayContent.Whisper,
            WholeRunTag = AbyssOverlayContent.WholeRunTag,
            ShadowBandLabel = AbyssOverlayContent.ShadowBandLabel,
            BlessingsLabel = AbyssOverlayContent.BlessingsLabel,
            ShadowsLabel = AbyssOverlayContent.ShadowsLabel,
        };
        foreach (var c in content.Cards)
        {
            data.Cards.Add(new AbyssOverlayViewData.Card
            {
                BlessingName = c.BlessingName,
                BlessingText = c.BlessingText,
                ShadowName = c.ShadowName,
                ShadowText = c.ShadowText,
                BlessingIcon = Icon(c.BlessingIconFile),
                ShadowIcon = Icon(c.ShadowIconFile),
                Tag = c.BlessingTag,
                ThisAct = c.BlessingTag == AbyssOverlayContent.ThisActTag,
            });
        }
        data.Blessings.AddRange(content.BlessingsTaken.Select(Strip));
        data.Shadows.AddRange(content.ShadowsInForce.Select(Strip));
        return data;
    }

    private static AbyssOverlayViewData.StripIcon Strip(AbyssOverlayStripEntry e) =>
        new()
        {
            Name = e.Name, TitleKey = e.TitleKey, Text = e.HoverText, Icon = Icon(e.IconFile),
            Caption = e.ThisAct ? e.Duration : "",
        };

    private static Texture2D? Icon(string file)
    {
        var path = KleePck.Path(file);
        return path == null ? null : ResourceLoader.Load<Texture2D>(path);
    }

    private static AbyssOverlayFonts Fonts() => new()
    {
        Bold = LoadFont("res://themes/kreon_bold_shared.tres"),
        Regular = LoadFont("res://themes/kreon_regular_shared.tres"),
    };

    private static Font? LoadFont(string path) =>
        ResourceLoader.Exists(path) ? ResourceLoader.Load<Font>(path) : null;

    private static void SetLayoutContentVisible(NAncientEventLayout layout, bool visible)
    {
        if (AncientDialogueClose.ContentContainerField?.GetValue(layout) is Control content)
        {
            content.Visible = visible;
        }
    }

    private static void WireStrip(Session session)
    {
        foreach (var (node, data) in session.View.StripIcons)
        {
            var tip = new HoverTip(new LocString(AbyssChoicePage.LocTable, data.TitleKey),
                                   data.Text, data.Icon);
            node.MouseEntered += () =>
            {
                try { NHoverTipSet.CreateAndShow(node, tip, HoverTip.GetHoverTipAlignment(node)); }
                catch (Exception e) { Log.Warn($"[{KleeMod.ModId}] Abyss strip hover skipped: {e.Message}"); }
            };
            node.MouseExited += () => NHoverTipSet.Remove(node);
        }
    }

    /// <summary>Co-op: each card carries the game's own vote markers (the
    /// shared event's <c>NMultiplayerVoteContainer</c>), refreshed on every
    /// vote the synchronizer reports.</summary>
    private static void WireVotes(Session session)
    {
        var sync = RunManager.Instance.EventSynchronizer;
        var players = session.Event.Owner!.RunState.Players;
        for (var i = 0; i < session.View.CardCount; i++)
        {
            var index = (uint)i;
            try
            {
                var container = SceneHelper.Instantiate<NMultiplayerVoteContainer>("ui/multiplayer_vote_container");
                container.Initialize(p => Voted(sync, p, index), players);
                session.View.VoteSlot(i).AddChildSafely(container);
                session.VoteContainers.Add(container);
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] Abyss vote markers unavailable: {e.Message}");
            }
        }
        session.VoteHandler = _ => RefreshVotes(session);
        sync.PlayerVoteChanged += session.VoteHandler;
        RefreshVotes(session);
    }

    private static bool Voted(EventSynchronizer sync, Player p, uint index)
    {
        try { return sync.GetPlayerVote(p) == index; }
        catch { return false; }
    }

    private static void RefreshVotes(Session session)
    {
        foreach (var c in session.VoteContainers)
        {
            if (GodotObject.IsInstanceValid(c)) c.RefreshPlayerVotes();
        }
    }

    private static void Unwire(Session session)
    {
        if (session.VoteHandler != null)
        {
            try { RunManager.Instance.EventSynchronizer.PlayerVoteChanged -= session.VoteHandler; }
            catch { /* run gone */ }
            session.VoteHandler = null;
        }
        foreach (var (node, _) in session.View.StripIcons)
        {
            try { NHoverTipSet.Remove(node); } catch { /* already gone */ }
        }
    }

    // ---- The bridge's page ---------------------------------------------------

    /// <summary>The JSON page the seat bridge reads off the root: the title,
    /// the whisper line, the three options (Blessing name; Blessing text and
    /// "Shadow: name - text") and, once the pick lands, the result.</summary>
    public static string PageJson(AbyssOverlayContent content, AbyssOverlayFlow flow)
    {
        var resolved = flow.Phase != AbyssOverlayPhase.Open;
        var page = new Dictionary<string, object?>
        {
            ["title"] = AbyssOverlayContent.Heading,
            ["subtitle"] = content.Title,
            ["body"] = AbyssOverlayContent.Whisper,
            ["resolved"] = resolved,
            ["chosen"] = flow.Chosen.HasValue ? content.Cards[flow.Chosen.Value].BlessingName : null,
            ["result"] = flow.ResultLine,
            ["blessings_taken"] = content.BlessingsTaken.Select(e => e.Name).ToList(),
            ["shadows_in_force"] = content.ShadowsInForce.Select(e => e.Name).ToList(),
            ["options"] = resolved
                ? new List<Dictionary<string, object?>>()
                : content.Cards.Select(c => new Dictionary<string, object?>
                {
                    ["index"] = c.Index,
                    ["title"] = c.BlessingName,
                    ["description"] = AbyssOverlayContent.BridgeDescription(c),
                    ["blessing"] = c.BlessingName,
                    ["blessing_text"] = c.BlessingText,
                    ["blessing_duration"] = c.BlessingTag,
                    ["shadow"] = c.ShadowName,
                    ["shadow_text"] = c.ShadowText,
                    ["shadow_duration"] = c.ShadowTag,
                }).ToList(),
        };
        return JsonSerializer.Serialize(page);
    }

    private static string PageJson(Session session) => PageJson(session.Content, session.Flow);
}

// ---- Patches --------------------------------------------------------------------

[HarmonyPatch(typeof(NAncientEventLayout), nameof(NAncientEventLayout.SetDialogue))]
internal static class NAncientEventLayout_SetDialogue_AbyssOverlay_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(NAncientEventLayout __instance, IReadOnlyList<AncientDialogueLine> lines)
    {
        try
        {
            return AbyssOverlay.HoldDialogue(__instance, lines);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen: could not hold the greeting: {e}");
            return true;
        }
    }
}

[HarmonyPatch(typeof(NAncientEventLayout), nameof(NAncientEventLayout.OnSetupComplete))]
internal static class NAncientEventLayout_OnSetupComplete_AbyssOverlay_Patch
{
    [HarmonyPostfix]
    private static void Postfix(NAncientEventLayout __instance)
    {
        try
        {
            AbyssOverlay.OpenIfShowing(__instance);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen failed to open: {e}");
        }
    }
}

[HarmonyPatch(typeof(NAncientEventLayout), nameof(NAncientEventLayout.DefaultFocusedControl), MethodType.Getter)]
internal static class NAncientEventLayout_DefaultFocusedControl_AbyssOverlay_Patch
{
    [HarmonyPostfix]
    private static void Postfix(NAncientEventLayout __instance, ref Control? __result)
    {
        try
        {
            if (AbyssOverlay.FocusFor(__instance) is { } focus) __result = focus;
        }
        catch
        {
            // The layout's own answer stands.
        }
    }
}

[HarmonyPatch(typeof(NEventLayout), nameof(NEventLayout.BeforeSharedOptionChosen))]
internal static class NEventLayout_BeforeSharedOptionChosen_AbyssOverlay_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(NEventLayout __instance, ref Task __result)
    {
        try
        {
            if (!AbyssOverlay.OwnsSharedVote(__instance)) return true;
            __result = Task.CompletedTask;
            return false;
        }
        catch
        {
            return true;
        }
    }
}

[HarmonyPatch(typeof(EventSynchronizer), "ChooseOptionForSharedEvent")]
internal static class EventSynchronizer_ChooseOptionForSharedEvent_AbyssOverlay_Patch
{
    [HarmonyPrefix]
    private static void Prefix(EventSynchronizer __instance, uint optionIndex)
    {
        try
        {
            AbyssOverlay.CaptureVotes(__instance, optionIndex);
        }
        catch
        {
            // A missed read only loses the "split" word on the result line.
        }
    }
}
