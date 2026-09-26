// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// 2026-09-26 (wave-3 seat round, Furina lane 3 and Klee lane 2b): DOES A
// PICK CLOSE THIS SCREEN BY ITSELF?
//
// THE FIND. On event card pickers (Brain Leech, Room Full of Cheese's Gorge)
// the page said "say `confirm` after `choose`", and the last `choose` closed
// the picker at once, so the `confirm` was refused ("nothing waiting to be
// confirmed"). Both seats lost a refusal to it, twice each.
//
// THE CAUSE, off the 0.111.0 decompile of `NSimpleCardSelectScreen`:
//
//     if (!_prefs.RequireManualConfirmation) CheckIfSelectionComplete();
//     ...
//     private void CheckIfSelectionComplete()
//     { if (_selectedCards.Count >= _prefs.MaxSelect) CompleteSelection(); }
//
// So on that screen, with `RequireManualConfirmation` off, the pick that
// reaches `MaxSelect` completes the selection and removes the screen; there is
// no confirm. The other grid screens (upgrade, transform, removal, enchant)
// open a preview with its own confirm instead, which is what the page's
// two-command note describes.
//
// WHAT CROSSES: `closes_on_last_pick` (true, false, or absent where the prefs
// could not be read) and `picks_needed` (`MaxSelect`). Read by reflection off
// the private `_prefs` field and its public members, by name, so a renamed
// member leaves the keys absent rather than guessing. Never throws.
//
// READ-ONLY.

using System;
using System.Collections.Generic;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>
    /// Add `closes_on_last_pick` and `picks_needed` to a card-select state
    /// where <paramref name="screen"/> carries a readable `_prefs`. Adds
    /// nothing otherwise.
    /// </summary>
    internal static void GitsAddSelectPrefs(Node screen,
                                            Dictionary<string, object?> state)
    {
        try
        {
            var prefsField = screen.GetType().GetField(
                "_prefs",
                BindingFlags.Instance | BindingFlags.NonPublic
                | BindingFlags.Public);
            var prefs = prefsField?.GetValue(screen);
            if (prefs == null) return;
            var type = prefs.GetType();
            var manual = GitsMember(type, prefs, "RequireManualConfirmation");
            var max = GitsMember(type, prefs, "MaxSelect");
            if (max is int picks) state["picks_needed"] = picks;
            // Only the screens whose click handler completes on its own: the
            // other grids keep a preview-and-confirm whatever the prefs say.
            // 2026-09-26 (control seat, Defect): the combat pile picker
            // (Hologram, from the discard pile) runs the same
            // `CheckIfSelectionComplete` (0.111.0 decompile), and the page
            // told the seat to `confirm` after a `choose` that had closed it.
            var name = screen.GetType().Name;
            if ((name == "NSimpleCardSelectScreen"
                 || name == "NCombatPileCardSelectScreen")
                && manual is bool needsConfirm)
            {
                state["closes_on_last_pick"] = !needsConfirm;
            }
        }
        catch (Exception)
        {
            // Absent keys are the page's "could not ask".
        }
    }

    private static object? GitsMember(Type type, object target, string name)
    {
        const BindingFlags flags = BindingFlags.Instance | BindingFlags.Public
                                   | BindingFlags.NonPublic;
        var property = type.GetProperty(name, flags);
        if (property != null) return property.GetValue(target);
        return type.GetField(name, flags)?.GetValue(target);
    }
}
