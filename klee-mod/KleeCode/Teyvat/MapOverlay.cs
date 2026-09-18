using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Teyvat;

/// <summary>
/// THE NATION OVERLAY ON THE MAP SCREEN -- what replaced the map plates
/// (2026-09-17).
///
/// THE PROBLEM IT ANSWERS, in [USER]'s words: *"the map is harder to read than
/// the normal Slay the Spire 2 map; I like the basic idea but perhaps we went
/// off the rails replacing the map background with Genshin images and we should
/// instead try to come up with a Genshin-themed map overlay that keeps the
/// basic idea of the map intact."* The eighteen real location stills that were
/// the six faces' map ground are gone
/// (`Patches/ActMapBgPathPatch` sends the three getters back to the base zone's
/// files); the game's own painted ground draws again, and the nation is carried
/// by three things drawn OVER it that never touch the middle of the frame:
///
///   1. a WORDMARK -- the nation's white loading-screen emblem -- in a
///      transparent 900x160 strip at the top centre;
///   2. a faint COLOUR GRADE, one <see cref="ColorRect"/> at the nation's tint
///      and <see cref="TintAlpha"/>;
///   3. a VIGNETTE -- the face's own location still, darkened and multiplied by
///      a radial mask that is fully transparent across the central 70% of the
///      width and 80% of the height, so it exists only in the outer margins
///      where no node, path or legend is drawn.
///
/// WHY AN OVERLAY AND NOT A GROUND. The map's node icons, its travelled and
/// untravelled path lines and its legend were all drawn for the base game's
/// low-contrast ground. A photograph underneath them takes contrast away
/// everywhere at once, and the two faces it hurt worst were named on sight
/// (Sumeru's teal icons over a bright plate, Natlan's top reading celestial).
/// An overlay cannot do that: the tint is 12% of one flat colour and the
/// vignette's alpha is ZERO where the map is read.
///
/// THE ARM-OFF BUILD IS BYTE-IDENTICAL. <see cref="ShouldAttach"/> is the only
/// gate and it leads with <see cref="TeyvatFrame.Enabled"/>; with the flag off,
/// or with a base zone current, <see cref="Attach"/> removes any overlay it
/// previously added and adds nothing. A missing parent, a missing texture and a
/// screen whose tree a game patch reshaped are all the same answer: add
/// nothing, throw nothing, and leave the game's map exactly as it was.
/// </summary>
public static class MapOverlay
{
    /// <summary>
    /// The overlay root's node name. One name, because
    /// <see cref="Attach"/> is idempotent by looking for it: the map screen is
    /// opened many times a run and every `Open` must find the overlay it added
    /// last time rather than stack a second one.
    /// </summary>
    public const string NodeName = "TeyvatMapOverlay";

    /// <summary>The pck directory the three overlay pictures live in.</summary>
    public const string Root = "res://teyvat/map/";

    /// <summary>
    /// The colour grade's alpha. ONE constant rather than six, because the
    /// choice being made is "faint" and it is the same choice on every face;
    /// a per-nation alpha would be six numbers nobody could defend against each
    /// other. 0.12 sits in the 10-15% band the design asked for.
    /// </summary>
    public const float TintAlpha = 0.12f;

    /// <summary>
    /// THE NATION TINT TABLE: dressing `Id.Entry` -> the grade's RGB, as the
    /// six-digit hex `Godot.Color`'s string constructor takes.
    ///
    /// HELD AS HEX AND NOT AS `Color` SO THE SUITE CAN READ IT. `KleeTests`
    /// runs headless and may not CALL GodotSharp (`KleeTests/README.md`, the
    /// headless boundary), so a table of constructed `Color`s could not be
    /// pinned at all. The one place a `Color` is built is
    /// <see cref="Attach"/>, inside the game.
    ///
    /// The hues are the nations' own and they are the same ones
    /// `tools/gen_act_placeholders.py`'s `NATIONS` tuple has always used for
    /// the placeholder gradients, so the grade over the game's map and the
    /// fallback plate under a face with no art of its own read as one palette:
    /// Mondstadt teal-green, Liyue amber, Natlan ember-red, Inazuma violet,
    /// Fontaine blue, Sumeru green.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> Tints =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [TeyvatFrame.Mondstadt] = "5FA98C",
            [TeyvatFrame.Liyue] = "D6A456",
            [TeyvatFrame.Natlan] = "C6543C",
            [TeyvatFrame.Inazuma] = "926CC4",
            [TeyvatFrame.Fontaine] = "4E8FD0",
            [TeyvatFrame.Sumeru] = "5C9C58",
        };

    /// <summary>
    /// Does the map screen get an overlay right now?
    ///
    /// The whole gate, and it is pure so both directions are pinned headlessly.
    /// A base zone reached while the flag is on dresses nothing, exactly as
    /// `MonsterNamePatch` and `PullNextEventPatch` already answer.
    /// </summary>
    public static bool ShouldAttach(string? entry) =>
        TeyvatFrame.Enabled && entry != null && Tints.ContainsKey(entry);

    /// <summary>The wordmark's pck path for a face.</summary>
    public static string WordmarkPath(string entry) =>
        Root + entry.ToLowerInvariant() + "_wordmark.png";

    /// <summary>The vignette's pck path for a face.</summary>
    public static string VignettePath(string entry) =>
        Root + entry.ToLowerInvariant() + "_vignette.png";

    /// <summary>The wordmark strip's authored size; see the art plan rows.</summary>
    public static readonly Vector2I WordmarkSize = new(900, 160);

    /// <summary>
    /// Pixels of clear air above the wordmark strip. The act banner the map
    /// screen draws for itself is at the top too (`NActBanner.Create`,
    /// `review/records/teyvat-act4-scoping-2026-09-15.md`), so the mark sits
    /// under it rather than on it.
    /// </summary>
    public const int WordmarkTopMargin = 24;

    /// <summary>
    /// WHERE THE OVERLAY IS INSERTED, as a list of candidate node names tried
    /// in order before the screen itself.
    ///
    /// THE TREE IS NOT IN THE REPO. `game_ref/` holds no decompile of the map
    /// screen and the only pinned fact about `NMapScreen`'s children is that
    /// `NMapPoint`s are somewhere under it
    /// (`vendor/STS2_MCP/McpMod.Actions.cs:509`) -- so this list is a guess and
    /// says so. Every entry is asked with `GetNodeOrNull`; when none answers,
    /// the screen itself is the parent and the overlay is moved to child index
    /// <see cref="GroundChildIndex"/>, which puts it above the first child (the
    /// ground) and below everything drawn after it.
    ///
    /// <see cref="LogTree"/> is what closes the guess: the first time an
    /// overlay is attached the whole child tree goes to `godot.log` behind the
    /// arm, so the next session reads the real names off a lane log instead of
    /// guessing again.
    /// </summary>
    public static readonly IReadOnlyList<string> ParentCandidates = new[]
    {
        "%MapContents",
        "MapContents",
        "%MapContainer",
        "MapContainer",
        "ScrollContainer/MapContainer",
    };

    /// <summary>
    /// The child index the overlay is moved to when it hangs off the screen
    /// root: 1, i.e. directly above the first child.
    ///
    /// A Godot `Control` draws its children in child order, so index 1 is "over
    /// whatever is drawn first and under everything else". The map ground is
    /// three `TextureRect`s and they are the only thing that can sensibly be
    /// first; if the tree says otherwise, the log line below is how we find
    /// out, and moving this constant is the whole repair.
    /// </summary>
    public const int GroundChildIndex = 1;

    private static bool _treeLogged;

    /// <summary>
    /// Attach (or remove) the overlay on <paramref name="screen"/>.
    ///
    /// EVERY EXIT IS "THE MAP IS UNTOUCHED". A null screen, the arm off, a base
    /// zone, a pck with no overlay pictures in it, or any exception at all:
    /// nothing is added and nothing throws. This runs as a Harmony postfix on
    /// the map screen's own open, so a throw here would take the map screen
    /// with it and end the run.
    /// </summary>
    public static void Attach(Node? screen)
    {
        try
        {
            if (screen == null)
            {
                return;
            }

            // Idempotent: the map screen opens many times a run. Searched
            // recursively rather than by name off the root, because the parent
            // the last attach chose is whichever of ParentCandidates answered
            // then -- and a game patch could change that between two opens.
            var existing = screen.FindChild(NodeName, recursive: true, owned: false);
            if (existing != null)
            {
                existing.GetParent()?.RemoveChild(existing);
                existing.QueueFree();
            }

            var entry = TeyvatFrame.CurrentActEntry;
            if (!ShouldAttach(entry))
            {
                return;
            }

            LogTree(screen);

            var overlay = Build(entry!);
            if (overlay == null)
            {
                return;
            }

            var parent = ResolveParent(screen);
            parent.AddChild(overlay);
            if (ReferenceEquals(parent, screen))
            {
                parent.MoveChild(overlay, GroundChildIndex);
            }
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] teyvat: map overlay not attached: {e}");
        }
    }

    /// <summary>
    /// The first candidate node that exists, or the screen itself.
    ///
    /// `GetNodeOrNull` throughout and never `GetNode`: the names above are a
    /// guess about a tree nobody has read, and `GetNode` on a miss throws
    /// inside the postfix.
    /// </summary>
    private static Node ResolveParent(Node screen)
    {
        foreach (var name in ParentCandidates)
        {
            var found = screen.GetNodeOrNull(name);
            if (found != null)
            {
                return found;
            }
        }

        return screen;
    }

    /// <summary>
    /// Build the overlay, or null when the pack carries none of its pictures
    /// and there is nothing to draw but a tint.
    ///
    /// DRAW ORDER IS CHILD ORDER: the grade first, the vignette over it, the
    /// wordmark last. All three are `MouseFilterEnum.Ignore`, so the map's own
    /// node hit-testing is untouched -- a click must reach the `NMapPoint`
    /// under the overlay exactly as it did before.
    /// </summary>
    private static Control? Build(string entry)
    {
        var overlay = new Control
        {
            Name = NodeName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        overlay.SetAnchorsPreset(Control.LayoutPreset.FullRect);

        var tint = new ColorRect
        {
            Name = "NationTint",
            Color = new Color(Tints[entry]) { A = TintAlpha },
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        tint.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        overlay.AddChild(tint);

        var vignette = LoadRect(VignettePath(entry), "NationVignette");
        if (vignette != null)
        {
            vignette.ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize;
            vignette.StretchMode = TextureRect.StretchModeEnum.Scale;
            vignette.SetAnchorsPreset(Control.LayoutPreset.FullRect);
            overlay.AddChild(vignette);
        }

        var wordmark = LoadRect(WordmarkPath(entry), "NationWordmark");
        if (wordmark != null)
        {
            wordmark.ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize;
            wordmark.StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered;
            // TOP-WIDE AND CENTRED BY THE STRETCH, not by arithmetic on the
            // screen's width: the plate is a 900x160 strip whose emblem is
            // already centred in transparency, so a full-width band of the
            // strip's own height puts the mark over the middle of the map at
            // every resolution without this file knowing one.
            wordmark.SetAnchorsPreset(Control.LayoutPreset.TopWide);
            wordmark.OffsetTop = WordmarkTopMargin;
            wordmark.OffsetBottom = WordmarkTopMargin + WordmarkSize.Y;
            overlay.AddChild(wordmark);
        }

        return overlay;
    }

    /// <summary>
    /// A `TextureRect` for a pck path, or null when the path is not in the
    /// pack.
    ///
    /// `ResourceLoader.Exists` first, the same guard
    /// `Patches/MonsterVisualsPathPatch` and `TeyvatVisuals` already use: a
    /// build whose pck predates the overlay art must draw the base map, not a
    /// missing-resource error.
    /// </summary>
    private static TextureRect? LoadRect(string path, string name)
    {
        if (!ResourceLoader.Exists(path))
        {
            return null;
        }

        var texture = GD.Load<Texture2D>(path);
        if (texture == null)
        {
            return null;
        }

        return new TextureRect
        {
            Name = name,
            Texture = texture,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
    }

    /// <summary>
    /// ONE-TIME DEBUG READ OF THE MAP SCREEN'S TREE, behind the arm.
    ///
    /// The insertion point above is a guess (see <see cref="ParentCandidates"/>)
    /// and this is how the guess stops being one: two levels of the screen's
    /// children, each with its Godot class, go to `godot.log` the first time an
    /// overlay is attached, so the main session reads the real names off a lane
    /// log. Grep `teyvat:maptree`.
    ///
    /// ONCE PER PROCESS and only with the arm on, because the map screen opens
    /// many times a run and a per-open dump would bury the rest of the log.
    /// </summary>
    private static void LogTree(Node screen)
    {
        if (_treeLogged)
        {
            return;
        }

        _treeLogged = true;

        try
        {
            foreach (var child in screen.GetChildren())
            {
                Log.Info($"[{KleeMod.ModId}] teyvat:maptree {screen.Name}/{child.Name} "
                       + $"({child.GetClass()})");
                foreach (var grandchild in child.GetChildren())
                {
                    Log.Info($"[{KleeMod.ModId}] teyvat:maptree {screen.Name}/{child.Name}/"
                           + $"{grandchild.Name} ({grandchild.GetClass()})");
                }
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] teyvat:maptree unread: {e.Message}");
        }
    }
}
