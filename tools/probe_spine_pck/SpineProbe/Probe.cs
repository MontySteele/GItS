using System;
using Godot;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;

namespace SpineProbe;

/// <summary>
/// Track M, M-Q3: does a .tscn that names SpineSkeletonFileResource /
/// SpineAtlasResource / SpineSprite load at runtime, in a pack built by an
/// editor (MegaDot 4.5.1) that has never heard of those types?
///
/// THROWAWAY. Deployed by deploy_probe.ps1, removed by cleanup_probe.ps1.
/// It registers no content, patches nothing, and subscribes to nothing --
/// every line below either reads a resource or prints.
///
/// The three arms, so a failure says WHICH failure it is:
///
///   probe_control.tscn   plain Sprite2D. If this arm fails, the pack or the
///                        mount is broken and spine was never the subject.
///   probe_raw.tscn       SpineSprite -> rig.skel + rig.atlas (the shape
///                        Downfall's repo HEAD ships).
///   probe_imported.tscn  SpineSprite -> rig.spskel + rig.spatlas (the shape
///                        Downfall's installed 0.1.7 pack ships).
///
/// and four observables per arm, printed as one line each to godot.log:
///
///   EXISTS      ResourceLoader.Exists -- the file is in the mounted pack.
///               False here means the pack build dropped it (phase 1 showed
///               the strict preset does exactly that to the rig data files).
///   LOADED      the PackedScene parsed. False means type resolution failed:
///               the engine could not find SpineSkeletonFileResource etc.
///   ROOT        the instantiated root's class name. "SpineSprite" is the
///               proof the GDExtension resolved the type from a pack MegaDot
///               could not parse.
///   SKELETON    bone count off the loaded skeleton data. A SpineSprite that
///               instantiates but reports 0 bones is the silent-no-render
///               mode, and it is the one that would otherwise look like a
///               taste problem instead of a pipeline problem.
///
/// The instance is also parented to the scene root at a fixed position, so a
/// human at the main menu can say whether anything is on screen. It is never
/// added to combat and never touches a run.
/// </summary>
[ModInitializer(nameof(Initialize))]
public static class SpineProbeMod
{
    private const string Tag = "[spineprobe]";

    private static readonly string[] Scenes =
    {
        "res://spineprobe/probe_control.tscn",
        "res://spineprobe/probe_raw.tscn",
        "res://spineprobe/probe_imported.tscn",
    };

    public static void Initialize()
    {
        Log.Info($"{Tag} M-Q3 probe starting.");

        foreach (var path in Scenes)
        {
            try
            {
                Report(path);
            }
            catch (Exception ex)
            {
                Log.Info($"{Tag} {path} THREW {ex.GetType().Name}: {ex.Message}");
            }
        }

        Log.Info($"{Tag} M-Q3 probe done.");
    }

    private static void Report(string path)
    {
        var exists = ResourceLoader.Exists(path);
        Log.Info($"{Tag} {path} EXISTS={exists}");
        if (!exists)
        {
            return;
        }

        var scene = ResourceLoader.Load<PackedScene>(path);
        Log.Info($"{Tag} {path} LOADED={scene != null}");
        if (scene == null)
        {
            return;
        }

        var node = scene.Instantiate();
        Log.Info($"{Tag} {path} ROOT={node.GetClass()} name={node.Name}");

        // Bone count without a typed reference to anything spine: the game
        // itself talks to this extension by class-name binding (S5), and so
        // does this probe. GodotObject.Call on a class the editor never knew
        // is precisely the capability under test.
        if (node.GetClass() == "SpineSprite")
        {
            try
            {
                var data = node.Get("skeleton_data_res");
                if (data.Obj is GodotObject res)
                {
                    var loaded = res.Call("is_skeleton_data_loaded");
                    Log.Info($"{Tag} {path} SKELETON data_loaded={loaded}");
                    var skeleton = res.Call("get_skeleton_file_res");
                    Log.Info($"{Tag} {path} SKELETON file_res={skeleton.Obj?.GetType().Name ?? "null"}");
                }
                else
                {
                    Log.Info($"{Tag} {path} SKELETON skeleton_data_res is null");
                }
            }
            catch (Exception ex)
            {
                Log.Info($"{Tag} {path} SKELETON query failed: {ex.GetType().Name}: {ex.Message}");
            }
        }

        // Visible arm. Deferred, because mod init runs before the tree is in a
        // state that tolerates reparenting.
        Callable.From(() => Attach(path, node)).CallDeferred();
    }

    private static void Attach(string path, Node node)
    {
        try
        {
            if (Engine.GetMainLoop() is not SceneTree tree || tree.Root == null)
            {
                Log.Info($"{Tag} {path} ATTACH skipped -- no scene tree");
                return;
            }

            if (node is Node2D n2d)
            {
                n2d.Position = new Vector2(640, 540);
            }

            tree.Root.AddChild(node);
            Log.Info($"{Tag} {path} ATTACHED to root at (640,540) -- look for it on screen");
        }
        catch (Exception ex)
        {
            Log.Info($"{Tag} {path} ATTACH failed: {ex.GetType().Name}: {ex.Message}");
        }
    }
}
