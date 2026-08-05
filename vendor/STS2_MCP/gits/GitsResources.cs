// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// Understudy P1.5, spec item 2: RESOURCE VISIBILITY. R100/6b made wire-visible
// meters a precondition for grading any Furina-meter claim off the BOT feed.
// This is that precondition.
//
// THE GAP, EXACTLY
//
// The bridge's `BuildPlayerState` serialises `creature.Powers`, so every meter
// with a badge is on the wire and every meter without one is invisible. Furina's
// Encore lost its badge in animation sprint 2 (E1) -- its ambient home became the
// Salon stage ribbon -- and its live value is a BaseLib CustomResource, which
// `Powers` does not contain. `understudy/soak.py` has recorded `encore: -1`
// (UNSEEN, not empty) on every bot fight since.
//
// WHAT THIS READS, AND WHY IT IS GENERIC
//
// BaseLib registers every custom resource in one place:
//
//   internal static class BaseLib.Abstracts.CustomResourcePatches
//       internal static readonly List<ResourceHandler> RegisteredResources
//
//   internal class BaseLib.Abstracts.ResourceHandler
//       public string Id { get; }
//       public Func<PlayerCombatState, CustomResource> GetResource { get; }
//
//   public abstract class BaseLib.Abstracts.CustomResource
//       public string Id { get; }
//       public virtual int Amount { get; set; }
//
// So this walks the registry and reports `{ resource id -> amount }`. It knows
// nothing about Furina, about klee, or about any particular mod: it reports
// whatever custom resources are registered, which is the only shape that stays
// true when the next character lands. KLEEMOD_ENCORE, KLEEMOD_FANFARE,
// KLEEMOD_FANFARE_FLOOR, KLEEMOD_FANFARE_CAP_BONUS and KLEEMOD_FURINA_BURST all
// arrive by construction, and so does anyone else's.
//
// REFLECTION, NOT A REFERENCE, AND THAT IS DELIBERATE. The registry is
// `internal` and BaseLib is a Workshop mod that may not be installed at all.
// A compile-time reference would make the bridge refuse to load without it;
// reflection makes a missing BaseLib mean "no custom resources", which is the
// truth. Every lookup is cached after the first hit and every failure is
// swallowed into an empty map -- a state read must never throw.
//
// READ-ONLY. Nothing here sets an Amount, calls Spend, or touches a handler
// other than to invoke its getter. It is a serialiser.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsResourceRegistryType =
        "BaseLib.Abstracts.CustomResourcePatches";
    private const string GitsResourceRegistryField = "RegisteredResources";

    private static bool _gitsResourcesProbed;
    private static FieldInfo? _gitsResourceRegistry;

    /// <summary>
    /// Locate BaseLib's registry once. A null result is cached too: if BaseLib
    /// is not installed, that fact does not change mid-session and a state read
    /// should not pay for a full assembly walk on every poll.
    /// </summary>
    private static FieldInfo? GitsResourceRegistry()
    {
        if (_gitsResourcesProbed) return _gitsResourceRegistry;
        _gitsResourcesProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsResourceRegistryType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsResourceRegistry = type?.GetField(
                GitsResourceRegistryField,
                BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
            if (_gitsResourceRegistry == null)
            {
                GD.Print("[STS2 MCP][GItS] no BaseLib custom-resource registry found; "
                         + "player.resources will be empty");
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] resource registry probe failed: {ex.Message}");
            _gitsResourceRegistry = null;
        }
        return _gitsResourceRegistry;
    }

    /// <summary>
    /// `{ resource id -> current amount }` for one player's combat state.
    ///
    /// ALWAYS RETURNS A MAP, never null and never throws: an empty map means
    /// "no custom resources are registered", and the ABSENCE of the key on the
    /// wire means "this bridge predates P1.5". Those are different facts and a
    /// reader is entitled to tell them apart.
    /// </summary>
    internal static Dictionary<string, object?> GitsResourceSnapshot(
        object? playerCombatState)
    {
        var snapshot = new Dictionary<string, object?>();
        if (playerCombatState == null) return snapshot;

        var registry = GitsResourceRegistry();
        if (registry == null) return snapshot;

        try
        {
            if (registry.GetValue(null) is not IEnumerable handlers) return snapshot;
            foreach (var handler in handlers)
            {
                if (handler == null) continue;
                try
                {
                    var handlerType = handler.GetType();
                    var getter = handlerType.GetProperty("GetResource")
                        ?.GetValue(handler) as Delegate;
                    if (getter == null) continue;
                    var resource = getter.DynamicInvoke(playerCombatState);
                    if (resource == null) continue;
                    var resourceType = resource.GetType();
                    // The RESOURCE's own Id, not the handler's: they agree today
                    // and the resource is the thing being reported.
                    var id = resourceType.GetProperty("Id")?.GetValue(resource)
                        as string;
                    if (string.IsNullOrEmpty(id)) continue;
                    if (resourceType.GetProperty("Amount")?.GetValue(resource)
                        is int amount)
                    {
                        snapshot[id!] = amount;
                    }
                }
                catch
                {
                    // One misbehaving mod's resource must not cost the state read
                    // every other mod's. Skip it and keep walking.
                }
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] resource snapshot failed: {ex.Message}");
        }
        return snapshot;
    }
}
