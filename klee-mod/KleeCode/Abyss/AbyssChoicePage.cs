using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// THE CHOICE SCREEN (paper sec.4): "Before each act's Ancient (Neow in act
/// 1), an event with three options."
///
/// BUILT AS THE ANCIENT'S FIRST PAGE, not as a room of its own. The Ancient is
/// the act's first map point, and the game has no seam for putting a second
/// event room in front of it (the room stack only pushes combats on events).
/// So when an Abyss run enters an Ancient whose act has no pick yet, the
/// Ancient's own opening page is set aside, the Abyss page is shown in its
/// place, and the chosen option puts the Ancient's page back exactly as the
/// Ancient drew it. One room, one save point: a reload before the pick
/// re-enters the Ancient and draws the same page (<see cref="AbyssDraft"/> is
/// a pure function of the seed and the record).
///
/// SHARED IN CO-OP. An Ancient is a per-player event, so while the Abyss page
/// is up the event reports itself shared -- the game's own vote, where the
/// host settles a split vote at random -- and the moment the pick lands every
/// player is back on their own Ancient. Every copy of the event runs the
/// chosen option; the run-wide record takes it once
/// (<see cref="AbyssRecord.Record"/> is idempotent per act), and Fateful
/// Fortune's Max HP is each player's own.
///
/// SEEN AS ITS OWN SCREEN (owner, 2026-10-12: "All of these options are tiny
/// text on the Ancient screen"). The page is still the model; the player sees
/// it through <see cref="AbyssOverlay"/>, a full-screen Blessing screen over
/// the room that hides the Ancient's layout, holds its greeting until the
/// pick lands, and clicks this page's options for the player.
///
/// Normal runs: every patch here starts by asking whether the run carries
/// <see cref="SpiralAbyss"/>, and returns untouched if it does not.
/// </summary>
public static class AbyssChoicePage
{
    internal const string LocTable = "events";
    internal const string KeyPrefix = "KLEE_SPIRAL_ABYSS";
    internal const string PageKey = KeyPrefix + ".pages.CHOICE.description";

    internal static string OptionTitleKey(AbyssBlessing b) => $"{KeyPrefix}.options.{b}.title";

    internal static string OptionDescriptionKey(AbyssBlessing b, AbyssShadow s) =>
        $"{KeyPrefix}.options.{b}.{s}.description";

    /// <summary>The Abyss page's rows for the <c>events</c> table: the page,
    /// and one title per Blessing and one description per (Blessing, Shadow)
    /// pair, since an option shows both.</summary>
    public static Dictionary<string, string> LocRows()
    {
        var rows = new Dictionary<string, string>
        {
            [PageKey] =
                "[gold]The Spiral Abyss[/gold] stirs before the Ancient. Take one "
              + "Blessing. The enemies take one of the two Shadows you pass, at random.",
        };
        foreach (var s in AbyssDraft.AllShadows)
        {
            rows[StripTitleKey(AbyssText.Name(s))] = AbyssText.Name(s);
        }
        foreach (var b in AbyssDraft.AllBlessings)
        {
            rows[StripTitleKey(AbyssText.Name(b))] = AbyssText.Name(b);
            rows[OptionTitleKey(b)] = AbyssText.Name(b);
            foreach (var s in AbyssDraft.AllShadows)
            {
                rows[OptionDescriptionKey(b, s)] = OptionDescription(b, s);
            }
        }
        return rows;
    }

    internal static string OptionDescription(AbyssBlessing b, AbyssShadow s) =>
        $"{AbyssText.Text(b)}\n[red]Shadow:[/red] [gold]{AbyssText.Name(s)}[/gold]. "
        + AbyssText.Text(s);

    /// <summary>Events showing the Abyss page right now. A weak table, so a
    /// finished event is never kept alive by it.</summary>
    private static readonly ConditionalWeakTable<EventModel, AbyssOffer> Showing = new();

    internal static bool IsShowing(EventModel? e) => e != null && Showing.TryGetValue(e, out _);

    /// <summary>The offer an event copy is showing, or null.</summary>
    internal static AbyssOffer? OfferOf(EventModel e) => Showing.TryGetValue(e, out var offer) ? offer : null;

    /// <summary>The Blessing screen's strip tooltips: one title row per
    /// Blessing and Shadow name.</summary>
    public static string StripTitleKey(string name) =>
        $"{KeyPrefix}.strip.{new string(name.Where(char.IsLetterOrDigit).ToArray()).ToUpperInvariant()}.title";

    private static readonly MethodInfo? SetEventStateMethod = AccessTools.Method(
        typeof(EventModel), "SetEventState",
        new[] { typeof(LocString), typeof(IEnumerable<EventOption>) });

    private static readonly FieldInfo? IsFinishedField =
        AccessTools.Field(typeof(EventModel), "_isFinished");

    /// <summary>The postfix body: put the Abyss page over the Ancient's.</summary>
    internal static void Install(AncientEventModel ancient, bool isPreFinished)
    {
        if (isPreFinished) return;
        var owner = ancient.Owner;
        var runState = owner?.RunState;
        var abyss = SpiralAbyss.In(runState);
        if (abyss == null || runState == null) return;

        var act = runState.CurrentActIndex;
        if (abyss.Record.HasPicked(act)) return;

        if (SetEventStateMethod == null || IsFinishedField == null)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss: EventModel.SetEventState or "
                      + "_isFinished did not resolve; the choice page cannot be shown.");
            return;
        }

        var offer = AbyssDraft.Offer(runState.Rng.Seed, act, abyss.Record);
        if (offer.Options.Count == 0) return;

        // What the Ancient drew, to put back after the pick.
        var ancientDescription = ancient.Description;
        var ancientOptions = ancient.CurrentOptions.ToList();
        var ancientFinished = ancient.IsFinished;
        if (ancientFinished)
        {
            // An Ancient with no options of its own (e.g. Neow under another
            // modifier) finishes on entry. The page still comes first; the
            // Ancient finishes again after the pick.
            IsFinishedField.SetValue(ancient, false);
        }

        var options = new List<EventOption>();
        for (var i = 0; i < offer.Options.Count; i++)
        {
            var index = i;
            var option = offer.Options[i];
            options.Add(new EventOption(
                ancient,
                () => OnChosen(ancient, offer, index, ancientDescription, ancientOptions, ancientFinished),
                new LocString(LocTable, OptionTitleKey(option.Blessing)),
                new LocString(LocTable, OptionDescriptionKey(option.Blessing, option.Shadow)),
                $"{KeyPrefix}.{option.Blessing}",
                Array.Empty<MegaCrit.Sts2.Core.HoverTips.IHoverTip>()));
        }

        Showing.AddOrUpdate(ancient, offer);
        SetEventStateMethod.Invoke(ancient, new object[] { new LocString(LocTable, PageKey), options });
    }

    private static async Task OnChosen(
        AncientEventModel ancient, AbyssOffer offer, int index,
        LocString? ancientDescription, List<EventOption> ancientOptions, bool ancientFinished)
    {
        var runState = ancient.Owner?.RunState;
        var abyss = SpiralAbyss.In(runState);
        var option = offer.Options[index];

        // Run-wide, once: the first copy of the shared event to resolve records.
        abyss?.Record.Record(offer.ActIndex, option.Blessing, offer.ShadowIfChosen(index));
        Showing.Remove(ancient);

        // Per player: each copy belongs to one player.
        if (option.Blessing == AbyssBlessing.FatefulFortune && ancient.Owner?.Creature is { } creature)
        {
            await CreatureCmd.GainMaxHp(creature, AbyssNumbers.FatefulFortuneMaxHp);
        }

        // Per player, display only: this copy's owner gets a relic for the
        // Blessing and the Abyss Shadows relic (AbyssDisplay; idempotent).
        if (abyss != null && ancient.Owner is { } player)
        {
            await AbyssDisplay.GrantTo(player, abyss.Record, offer.ActIndex);
        }

        if (ancientFinished || ancientOptions.Count == 0)
        {
            ancient.StartPreFinished();
        }
        else
        {
            SetEventStateMethod!.Invoke(ancient, new object[]
            {
                ancientDescription ?? ancient.InitialDescription, ancientOptions,
            });
        }

        // The Blessing screen over this machine's room (if this is its copy)
        // shows the result, fades, and lets the Ancient's greeting play.
        try
        {
            AbyssOverlay.OnChosen(ancient, offer, index);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss screen could not close: {e}");
        }
    }
}

/// <summary>The install seam: after the Ancient has drawn its opening page.</summary>
[HarmonyPatch(typeof(AncientEventModel), "SetInitialEventState")]
internal static class AncientEventModel_SetInitialEventState_Abyss_Patch
{
    [HarmonyPostfix]
    private static void Postfix(AncientEventModel __instance, bool isPreFinished)
    {
        try
        {
            AbyssChoicePage.Install(__instance, isPreFinished);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss choice page failed: {e}");
        }
    }
}

/// <summary>
/// The page is shared: the vote seam. <c>EventSynchronizer.IsShared</c>
/// decides whether a click is a vote, and it reads the CANONICAL event, which
/// cannot know a page is up, so it asks whether any player's copy is showing
/// the Abyss page.
/// </summary>
[HarmonyPatch(typeof(EventSynchronizer), nameof(EventSynchronizer.IsShared), MethodType.Getter)]
internal static class EventSynchronizer_IsShared_Abyss_Patch
{
    [HarmonyPostfix]
    private static void Postfix(EventSynchronizer __instance, ref bool __result)
    {
        if (__result) return;
        try
        {
            if (__instance.Events.Any(AbyssChoicePage.IsShowing)) __result = true;
        }
        catch
        {
            // Not in an event: the original answer stands.
        }
    }
}

/// <summary>The same answer on the event copy itself, which the event room
/// reads to keep the buttons up while the vote is open and to show the
/// "shared" label. Only a copy showing the Abyss page changes, and the page is
/// installed after the event seeds its own Rng, so the Ancient's per-player
/// seed is untouched.</summary>
[HarmonyPatch(typeof(EventModel), nameof(EventModel.IsShared), MethodType.Getter)]
internal static class EventModel_IsShared_Abyss_Patch
{
    [HarmonyPostfix]
    private static void Postfix(EventModel __instance, ref bool __result)
    {
        if (!__result && AbyssChoicePage.IsShowing(__instance)) __result = true;
    }
}

/// <summary>
/// NEOW KEEPS HER BLESSINGS. With any modifier on the run, Neow offers only
/// the modifiers' own Neow options (<c>Neow.GenerateInitialOptions</c>), and
/// the Abyss offers none -- so an Abyss run would meet a Neow with nothing to
/// give. The paper puts the Abyss pick BEFORE the Ancient, not in its place,
/// so while Neow draws her options, a run whose only modifier is the Abyss
/// reads as a run with none. A run with other modifiers too keeps the base
/// game's behaviour.
/// </summary>
[HarmonyPatch(typeof(Neow), "GenerateInitialOptions")]
internal static class Neow_GenerateInitialOptions_Abyss_Patch
{
    private static readonly MethodInfo? ModifiersSetter =
        AccessTools.PropertySetter(typeof(RunState), nameof(RunState.Modifiers));

    [ThreadStatic] private static IReadOnlyList<ModifierModel>? _held;
    [ThreadStatic] private static RunState? _heldRun;

    [HarmonyPrefix]
    private static void Prefix(Neow __instance)
    {
        _held = null;
        _heldRun = null;
        if (ModifiersSetter == null) return;
        if (__instance.Owner?.RunState is not RunState run) return;
        var mods = run.Modifiers;
        if (mods.Count == 0 || !mods.All(m => m is SpiralAbyss)) return;
        _held = mods;
        _heldRun = run;
        ModifiersSetter.Invoke(run, new object[] { Array.Empty<ModifierModel>() });
    }

    [HarmonyFinalizer]
    private static void Finalizer()
    {
        if (_held != null && _heldRun != null)
        {
            ModifiersSetter?.Invoke(_heldRun, new object[] { _held });
        }
        _held = null;
        _heldRun = null;
    }
}
