using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Multiplayer.Game.Lobby;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// THE MENU BUTTON. A patch on NSingleplayerSubmenu._Ready and
/// NMultiplayerHostSubmenu copies the Custom button as "Spiral Abyss".
///
/// THE BUTTON OPENS THE ORDINARY CHARACTER SELECT (owner, 2026-10-12: "I'd
/// prefer it have the normal screen where you select the character and
/// ascension rather than the custom mode screen"). The click raises
/// <see cref="Armed"/> and runs the Standard button's own route; the postfix
/// on the character select's singleplayer and host initialisers spends the
/// flag by putting a fresh Spiral Abyss into the new lobby's modifier list.
/// From there <see cref="AbyssLane"/>'s seams 2 and 3 carry it into the run
/// (the Standard screen's <c>BeginRun</c> drops modifiers, so the list is held
/// past it and handed to <c>RunState.CreateForNewRun</c>).
///
/// WHERE "ARMED" LIVES. In <see cref="Armed"/> only for the instant between
/// the click and the screen's initialiser; after that in the lobby itself. The
/// lobby dies when the player backs out (<c>CleanUpLobby</c>) and the screen
/// builds a new one every time it opens, so backing out and pressing Standard
/// gives a plain lobby with nothing to clear. The main menu clears the flag
/// and any held list as well (<see cref="Disarm"/>).
///
/// CO-OP. The host lobby's list reaches every client in the game's own
/// messages, neither of which looks at the game mode: the join answer
/// (<c>ClientLobbyJoinResponseMessage.modifiers</c>, read by
/// <c>StartRunLobby.InitializeFromMessage</c>), which is how a joining
/// client's screen shows the banner, and the run start
/// (<c>LobbyBeginRunMessage.modifiers</c>). This mod sends nothing.
///
/// THE RUN STAYS A STANDARD RUN (<see cref="GameMode.Standard"/>): it counts
/// for ascension, wins, streaks and epochs like any run at its ascension, and
/// the run history files it as Standard.
///
/// The Custom screen is untouched: Spiral Abyss is an ordinary tickbox there.
///
/// The copy is CuratedChallenges2's pattern (duplicate the Custom button, give
/// it its own shader material and labels), duplicated WITHOUT signals so the
/// copy cannot also fire the Custom button's handler.
/// </summary>
public static class AbyssMenu
{
    internal const string LocPrefix = "KLEE_SPIRAL_ABYSS";

    /// <summary>The official Spiral Abyss emblem: the menu button's icon and
    /// the modifier tickbox's (<see cref="SpiralAbyss"/>).</summary>
    internal const string IconFile = "abyss/ui/spiral_abyss.png";

    /// <summary>The banner's node name on the character select.</summary>
    internal const string BannerName = "SpiralAbyssBanner";

    /// <summary>Set by the Abyss button, spent by the next character-select
    /// initialiser (<see cref="TakeArmed"/>).</summary>
    public static bool Armed { get; private set; }

    public static void Arm() => Armed = true;

    /// <summary>The flag, cleared as it is read: one press arms one lobby.</summary>
    public static bool TakeArmed()
    {
        var armed = Armed;
        Armed = false;
        return armed;
    }

    /// <summary>Back at the main menu: nothing armed, nothing held.</summary>
    public static void Disarm()
    {
        Armed = false;
        AbyssLane.ClearHold();
    }

    /// <summary>Whether a new lobby takes the Abyss: armed by the button, a
    /// Standard lobby, not a client (a client's list comes from the host), and
    /// not already carried. PURE.</summary>
    public static bool ShouldArmLobby(bool armed, GameMode mode, bool isClient, bool alreadyHas) =>
        armed && mode == GameMode.Standard && !isClient && !alreadyHas;

    /// <summary>Put <paramref name="abyss"/> into the lobby's own list, once.
    /// Answers whether it was added.</summary>
    public static bool ArmList(List<ModifierModel> lobbyModifiers, ModifierModel abyss)
    {
        if (AbyssLane.Carries(lobbyModifiers)) return false;
        lobbyModifiers.Add(abyss);
        return true;
    }

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

    private static readonly AccessTools.FieldRef<StartRunLobby, List<ModifierModel>> LobbyModifiers =
        AccessTools.FieldRefAccess<StartRunLobby, List<ModifierModel>>("_modifiers");

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
        SetIcon(button);
        return button;
    }

    /// <summary>The copy wears the Custom button's icon until this swaps it
    /// for the Abyss emblem. A missing pack leaves the borrowed icon.</summary>
    private static void SetIcon(NSubmenuButton button)
    {
        var path = KleePck.Path(IconFile);
        var icon = button.GetNodeOrNull<TextureRect>("Icon");
        if (path == null || icon == null) return;
        var texture = ResourceLoader.Load<Texture2D>(path);
        if (texture != null) icon.Texture = texture;
    }

    /// <summary>The Standard button's route
    /// (<c>NSingleplayerSubmenu.OpenCharacterSelect</c>), armed.</summary>
    internal static void OpenSingleplayer(NSingleplayerSubmenu submenu)
    {
        var stack = Stack(submenu);
        var screen = stack.GetSubmenuType<NCharacterSelectScreen>();
        Arm();
        try
        {
            screen.InitializeSingleplayer();
        }
        finally
        {
            Armed = false;
        }
        stack.Push(screen);
    }

    /// <summary>The Standard host button's route
    /// (<c>NMultiplayerHostSubmenu.StartHostAsync(GameMode.Standard)</c>),
    /// armed.</summary>
    internal static void OpenHost(NMultiplayerHostSubmenu submenu, Control loadingOverlay)
    {
        TaskHelper.RunSafely(HostAsync(loadingOverlay, Stack(submenu)));
    }

    private static async Task HostAsync(Control loadingOverlay, NSubmenuStack stack)
    {
        Arm();
        try
        {
            await NMultiplayerHostSubmenu.StartHostAsync(GameMode.Standard, loadingOverlay, stack);
        }
        finally
        {
            Armed = false;
        }
    }

    /// <summary>Postfix body for the character select's singleplayer and host
    /// initialisers: spend the flag into the new lobby.</summary>
    internal static void AfterCharacterSelectInitialized(NCharacterSelectScreen screen)
    {
        var armed = TakeArmed();
        var lobby = screen.Lobby;
        if (lobby == null) return;
        var list = LobbyModifiers(lobby);
        if (!ShouldArmLobby(armed, lobby.GameMode,
                lobby.NetService.Type == NetGameType.Client, AbyssLane.Carries(list)))
        {
            return;
        }
        if (ArmList(list, ModelDb.Modifier<SpiralAbyss>().ToMutable()))
            Log.Info($"[{KleeMod.ModId}] Spiral Abyss: this lobby's run carries the Spiral Abyss.");
    }

    /// <summary>Postfix body for the character select opening: the banner
    /// shows exactly when the lobby carries the Abyss (a joining client's
    /// lobby included) and hides on every other opening of the same
    /// screen.</summary>
    internal static void RefreshBanner(NCharacterSelectScreen screen)
    {
        var show = AbyssLane.Carries(screen.Lobby?.Modifiers);
        var banner = screen.GetNodeOrNull<Control>(BannerName);
        if (banner == null)
        {
            if (!show) return;
            banner = MakeBanner(screen);
            if (banner == null) return;
        }
        banner.Visible = show;
    }

    /// <summary>The screen's own character-name label, duplicated without
    /// signals, so the banner wears the game's font, size and outline. Top
    /// centre of the screen.</summary>
    private static Control? MakeBanner(NCharacterSelectScreen screen)
    {
        var source = screen.GetNodeOrNull<MegaLabel>("InfoPanel/VBoxContainer/Name");
        if (source == null) return null;
        var label = (MegaLabel)source.Duplicate(2 | 4 | 8);
        label.Name = BannerName;
        label.MouseFilter = Control.MouseFilterEnum.Ignore;
        screen.AddChild(label);
        label.AnchorLeft = 0.5f;
        label.AnchorRight = 0.5f;
        label.AnchorTop = 0f;
        label.AnchorBottom = 0f;
        label.OffsetLeft = -400f;
        label.OffsetRight = 400f;
        label.OffsetTop = 28f;
        label.OffsetBottom = 118f;
        label.HorizontalAlignment = HorizontalAlignment.Center;
        label.VerticalAlignment = VerticalAlignment.Center;
        label.SetTextAutoSize(new LocString("main_menu_ui", LocPrefix + ".title").GetFormattedText());
        return label;
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

/// <summary>The character select: the armed lobby on the host or
/// singleplayer initialisers, and the banner on every opening (a joining
/// client's included).</summary>
[HarmonyPatch(typeof(NCharacterSelectScreen))]
internal static class NCharacterSelectScreen_Abyss_Patch
{
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NCharacterSelectScreen.InitializeSingleplayer))]
    private static void SingleplayerPostfix(NCharacterSelectScreen __instance) => Arm(__instance);

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NCharacterSelectScreen.InitializeMultiplayerAsHost))]
    private static void HostPostfix(NCharacterSelectScreen __instance) => Arm(__instance);

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NCharacterSelectScreen.OnSubmenuOpened))]
    private static void OpenedPostfix(NCharacterSelectScreen __instance)
    {
        try
        {
            AbyssMenu.RefreshBanner(__instance);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss banner failed: {e}");
        }
    }

    private static void Arm(NCharacterSelectScreen screen)
    {
        try
        {
            AbyssMenu.AfterCharacterSelectInitialized(screen);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss could not arm the lobby: {e}");
        }
    }
}

/// <summary>Back at the main menu nothing is armed and nothing is held, so a
/// later run is never an Abyss run by accident.</summary>
[HarmonyPatch(typeof(NMainMenu), "_Ready")]
internal static class NMainMenu_Ready_Abyss_Patch
{
    [HarmonyPostfix]
    private static void Postfix()
    {
        try
        {
            AbyssMenu.Disarm();
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss disarm failed: {e}");
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
