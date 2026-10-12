using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Screens.CustomRun;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// THE MENU BUTTON (paper sec.4): "A patch on NSingleplayerSubmenu._Ready and
/// NMultiplayerHostSubmenu copies the Custom button as 'Spiral Abyss'. The
/// button opens the Custom screen with the Abyss modifier already ticked and
/// locked."
///
/// The copy is CuratedChallenges2's pattern (duplicate the Custom button, give
/// it its own shader material and labels), duplicated WITHOUT signals so the
/// copy cannot also fire the Custom button's handler. The click raises
/// <see cref="Pending"/> and runs the Custom button's own route; the postfix
/// on the Custom screen's initialisers spends the flag, ticking the Abyss
/// modifier alone and locking its tickbox. Opened from the plain Custom button
/// the screen unlocks and unticks it again, so the ordinary Custom mode keeps
/// working exactly as before.
///
/// CO-OP comes from the Custom lobby itself: the host's ticked modifiers go to
/// every client by ModelId (<c>StartRunLobby</c>), so the clients' runs carry
/// the modifier with no message of ours.
/// </summary>
public static class AbyssMenu
{
    internal const string LocPrefix = "KLEE_SPIRAL_ABYSS";

    /// <summary>Set by the Abyss button, spent by the next Custom-screen init.</summary>
    internal static bool Pending;

    /// <summary>True while this mod has the Abyss tickbox locked.</summary>
    private static bool _locked;

    internal static Dictionary<string, string> LocRows() => new()
    {
        [LocPrefix + ".title"] = "Spiral Abyss",
        [LocPrefix + ".description"] =
            "Before each act's Ancient, take a Blessing. The enemies take a Shadow. "
          + "Both last the whole run.",
        [LocPrefix + ".LOCKED.description"] = "Unlocks with Custom runs.",
    };

    private static readonly AccessTools.FieldRef<NSubmenu, NSubmenuStack> Stack =
        AccessTools.FieldRefAccess<NSubmenu, NSubmenuStack>("_stack");

    private static readonly AccessTools.FieldRef<NCustomRunScreen, NCustomRunModifiersList> ModifiersList =
        AccessTools.FieldRefAccess<NCustomRunScreen, NCustomRunModifiersList>("_modifiersList");

    private static readonly AccessTools.FieldRef<NCustomRunModifiersList, List<NRunModifierTickbox>> Tickboxes =
        AccessTools.FieldRefAccess<NCustomRunModifiersList, List<NRunModifierTickbox>>("_modifierTickboxes");

    /// <summary>Duplicate <paramref name="custom"/> into a fourth button after
    /// it, re-spacing the row so four fit where three were.</summary>
    internal static NSubmenuButton? AddButton(
        Control parent, NSubmenuButton standard, NSubmenuButton daily, NSubmenuButton custom,
        Action onPressed)
    {
        var spacing = daily.Position.X - standard.Position.X;
        var y = standard.Position.Y;
        var left = standard.Position.X - spacing / 2f;
        standard.Position = new Vector2(left, y);
        daily.Position = new Vector2(left + spacing, y);
        custom.Position = new Vector2(left + spacing * 2f, y);

        // Groups | Scripts | UseInstantiation: everything but the signals.
        var button = (NSubmenuButton)custom.Duplicate(2 | 4 | 8);
        button.Name = "SpiralAbyssButton";
        parent.AddChild(button);
        button.Position = new Vector2(left + spacing * 3f, y);

        var bg = button.GetNodeOrNull<Control>("BgPanel");
        if (bg?.Material is ShaderMaterial material)
        {
            var own = (ShaderMaterial)material.Duplicate();
            bg.Material = own;
            AccessTools.Field(typeof(NSubmenuButton), "_hsv")?.SetValue(button, own);
            own.SetShaderParameter("h", 0.62f);
        }

        button.Connect(NClickableControl.SignalName.Released,
            Callable.From<NButton>(_ => onPressed()));
        button.SetIconAndLocalization(LocPrefix);
        return button;
    }

    internal static void OpenSingleplayer(NSingleplayerSubmenu submenu)
    {
        var stack = Stack(submenu);
        var screen = stack.GetSubmenuType<NCustomRunScreen>();
        Pending = true;
        try
        {
            screen.InitializeSingleplayer();
        }
        finally
        {
            Pending = false;
        }
        stack.Push(screen);
    }

    internal static void OpenHost(NMultiplayerHostSubmenu submenu, Control loadingOverlay)
    {
        TaskHelper.RunSafely(HostAsync(loadingOverlay, Stack(submenu)));
    }

    private static async Task HostAsync(Control loadingOverlay, NSubmenuStack stack)
    {
        Pending = true;
        try
        {
            await NMultiplayerHostSubmenu.StartHostAsync(GameMode.Custom, loadingOverlay, stack);
        }
        finally
        {
            Pending = false;
        }
    }

    /// <summary>Postfix body for the Custom screen's singleplayer and host
    /// initialisers.</summary>
    internal static void AfterCustomScreenInitialized(NCustomRunScreen screen)
    {
        var list = ModifiersList(screen);
        if (list == null) return;
        var tick = Tickboxes(list).FirstOrDefault(t => t.Modifier is SpiralAbyss);
        if (tick?.Modifier == null) return;

        if (Pending)
        {
            Pending = false;
            list.SetTickedModifiers(new List<ModifierModel> { tick.Modifier });
            tick.Disable();
            _locked = true;
        }
        else if (_locked)
        {
            _locked = false;
            tick.Enable();
            list.SetTickedModifiers(list.GetModifiersTickedOn()
                .Where(m => m is not SpiralAbyss).ToList());
        }
    }
}

[HarmonyPatch(typeof(NSingleplayerSubmenu))]
internal static class NSingleplayerSubmenu_Abyss_Patch
{
    private static readonly AccessTools.FieldRef<NSingleplayerSubmenu, NSubmenuButton> StandardButton =
        AccessTools.FieldRefAccess<NSingleplayerSubmenu, NSubmenuButton>("_standardButton");
    private static readonly AccessTools.FieldRef<NSingleplayerSubmenu, NSubmenuButton> DailyButton =
        AccessTools.FieldRefAccess<NSingleplayerSubmenu, NSubmenuButton>("_dailyButton");
    private static readonly AccessTools.FieldRef<NSingleplayerSubmenu, NSubmenuButton> CustomButton =
        AccessTools.FieldRefAccess<NSingleplayerSubmenu, NSubmenuButton>("_customButton");

    private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<NSingleplayerSubmenu, NSubmenuButton> Buttons = new();

    [HarmonyPostfix]
    [HarmonyPatch("_Ready")]
    private static void ReadyPostfix(NSingleplayerSubmenu __instance)
    {
        try
        {
            var button = AbyssMenu.AddButton(
                __instance, StandardButton(__instance), DailyButton(__instance), CustomButton(__instance),
                () => AbyssMenu.OpenSingleplayer(__instance));
            if (button != null) Buttons.AddOrUpdate(__instance, button);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss singleplayer button failed: {e}");
        }
    }

    [HarmonyPostfix]
    [HarmonyPatch("RefreshButtons")]
    private static void RefreshPostfix(NSingleplayerSubmenu __instance)
    {
        if (!Buttons.TryGetValue(__instance, out var button)) return;
        button.SetEnabled(CustomButton(__instance).IsEnabled);
        button.RefreshLabels();
    }
}

[HarmonyPatch(typeof(NMultiplayerHostSubmenu))]
internal static class NMultiplayerHostSubmenu_Abyss_Patch
{
    private static readonly AccessTools.FieldRef<NMultiplayerHostSubmenu, NSubmenuButton> StandardButton =
        AccessTools.FieldRefAccess<NMultiplayerHostSubmenu, NSubmenuButton>("_standardButton");
    private static readonly AccessTools.FieldRef<NMultiplayerHostSubmenu, NSubmenuButton> DailyButton =
        AccessTools.FieldRefAccess<NMultiplayerHostSubmenu, NSubmenuButton>("_dailyButton");
    private static readonly AccessTools.FieldRef<NMultiplayerHostSubmenu, NSubmenuButton> CustomButton =
        AccessTools.FieldRefAccess<NMultiplayerHostSubmenu, NSubmenuButton>("_customButton");
    private static readonly AccessTools.FieldRef<NMultiplayerHostSubmenu, Control> LoadingOverlay =
        AccessTools.FieldRefAccess<NMultiplayerHostSubmenu, Control>("_loadingOverlay");

    private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<NMultiplayerHostSubmenu, NSubmenuButton> Buttons = new();

    [HarmonyPostfix]
    [HarmonyPatch("_Ready")]
    private static void ReadyPostfix(NMultiplayerHostSubmenu __instance)
    {
        try
        {
            var button = AbyssMenu.AddButton(
                __instance, StandardButton(__instance), DailyButton(__instance), CustomButton(__instance),
                () => AbyssMenu.OpenHost(__instance, LoadingOverlay(__instance)));
            if (button != null) Buttons.AddOrUpdate(__instance, button);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss co-op button failed: {e}");
        }
    }

    [HarmonyPostfix]
    [HarmonyPatch("RefreshButtons")]
    private static void RefreshPostfix(NMultiplayerHostSubmenu __instance)
    {
        if (!Buttons.TryGetValue(__instance, out var button)) return;
        button.SetEnabled(CustomButton(__instance).IsEnabled);
        button.RefreshLabels();
    }
}

[HarmonyPatch(typeof(NCustomRunScreen))]
internal static class NCustomRunScreen_Abyss_Patch
{
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NCustomRunScreen.InitializeSingleplayer))]
    private static void SingleplayerPostfix(NCustomRunScreen __instance) => Run(__instance);

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NCustomRunScreen.InitializeMultiplayerAsHost))]
    private static void HostPostfix(NCustomRunScreen __instance) => Run(__instance);

    private static void Run(NCustomRunScreen screen)
    {
        try
        {
            AbyssMenu.AfterCustomScreenInitialized(screen);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss could not tick its modifier: {e}");
        }
    }
}

/// <summary>
/// DAILIES AND RANDOMIZE NEVER ROLL THE ABYSS. BaseLib appends every Good
/// <c>CustomModifierModel</c> to <c>ModelDb.GoodModifiers</c>, which is also
/// the pool <c>ModifierModel.Pick2Good1Bad</c> draws a Daily's modifiers from
/// (and the Custom screen's Randomize). Inside that one call the Abyss is
/// taken back out, so a Daily draws from exactly the pool it would without
/// this mod's modifier.
/// </summary>
[HarmonyPatch]
internal static class AbyssModifierListPatches
{
    [ThreadStatic] private static int _picking;

    [HarmonyPrefix]
    [HarmonyPatch(typeof(ModifierModel), nameof(ModifierModel.Pick2Good1Bad))]
    private static void PickPrefix() => _picking++;

    [HarmonyFinalizer]
    [HarmonyPatch(typeof(ModifierModel), nameof(ModifierModel.Pick2Good1Bad))]
    private static void PickFinalizer() => _picking = Math.Max(0, _picking - 1);

    [HarmonyPostfix]
    [HarmonyPriority(Priority.Last)]
    [HarmonyPatch(typeof(ModelDb), nameof(ModelDb.GoodModifiers), MethodType.Getter)]
    private static void GoodPostfix(ref IReadOnlyList<ModifierModel> __result)
    {
        if (_picking <= 0) return;
        if (!__result.Any(m => m is SpiralAbyss)) return;
        __result = __result.Where(m => m is not SpiralAbyss).ToList();
    }
}

/// <summary>The mode's rows, merged once the tables exist (the same seam as
/// <c>LocManager_Initialize_Patch</c>, for the reason recorded there).</summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Abyss_Patch
{
    [HarmonyPostfix]
    private static void Postfix()
    {
        try
        {
            LocManager.Instance.GetTable(AbyssChoicePage.LocTable).MergeWith(AbyssChoicePage.LocRows());
            LocManager.Instance.GetTable("main_menu_ui").MergeWith(AbyssMenu.LocRows());
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss loc rows failed to merge: {e}");
        }
    }
}
