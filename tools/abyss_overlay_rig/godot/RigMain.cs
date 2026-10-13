// The Spiral Abyss Blessing screen's render rig (tools/abyss_overlay_rig).
// Compiled into a scratch MegaDot C# project beside the SAME view file the
// mod ships (klee-mod/KleeCode/Abyss/AbyssOverlayView.cs) and the paper's
// strings (AbyssEntries.cs). It loads the game's pack read-only for the
// game's fonts, builds the screen at 1920x1080 for each job state and saves
// a PNG per state. Review material only; nothing here ships.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Godot;
using KleeMod.Abyss;

public partial class RigMain : Node
{
    private sealed class Job
    {
        public string Out { get; set; } = "";
        public string GamePck { get; set; } = "";
        public string ArtRoot { get; set; } = "";
        public string Backdrop { get; set; } = "";
        public List<State> States { get; set; } = new();
    }

    private sealed class State
    {
        public string Name { get; set; } = "";
        public int Act { get; set; }
        public int[] Blessings { get; set; } = Array.Empty<int>();
        public int[] Shadows { get; set; } = Array.Empty<int>();
        public int[] TakenBlessings { get; set; } = Array.Empty<int>();
        public int[] TakenShadows { get; set; } = Array.Empty<int>();
        public int Focused { get; set; } = -1;
        public int Chosen { get; set; } = -1;
        /// <summary>Per card, the vote-icon files to show under it.</summary>
        public string[][] Votes { get; set; } = Array.Empty<string[]>();
        public string Result { get; set; } = "";
    }

    public override async void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        var job = JsonSerializer.Deserialize<Job>(System.IO.File.ReadAllText(args[0]))!;
        if (!string.IsNullOrEmpty(job.GamePck)) ProjectSettings.LoadResourcePack(job.GamePck, false);
        var fonts = new AbyssOverlayFonts
        {
            Bold = ResourceLoader.Exists("res://themes/kreon_bold_shared.tres")
                ? ResourceLoader.Load<Font>("res://themes/kreon_bold_shared.tres") : null,
            Regular = ResourceLoader.Exists("res://themes/kreon_regular_shared.tres")
                ? ResourceLoader.Load<Font>("res://themes/kreon_regular_shared.tres") : null,
        };
        GD.Print($"RIG|fonts bold={fonts.Bold != null} regular={fonts.Regular != null}");

        foreach (var state in job.States)
        {
            var vp = new SubViewport
            {
                Size = new Vector2I(1920, 1080),
                RenderTargetUpdateMode = SubViewport.UpdateMode.Always,
                TransparentBg = false,
            };
            AddChild(vp);
            var stage = new Control { Size = new Vector2(1920, 1080) };
            vp.AddChild(stage);
            var bg = new TextureRect
            {
                Texture = Png(job.Backdrop),
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
                Size = new Vector2(1920, 1080),
            };
            stage.AddChild(bg);
            // A stand-in for the run's top bar, so overlap with it shows.
            stage.AddChild(new ColorRect { Color = new Color(0.1f, 0.09f, 0.12f), Size = new Vector2(1920, 72) });

            var data = new AbyssOverlayViewData
            {
                Title = $"{AbyssOverlayContentRig.Heading} · Act {state.Act + 1}",
                Whisper = AbyssOverlayContentRig.Whisper,
                WholeRunTag = "Whole run",
                ShadowBandLabel = "Shadow",
                BlessingsLabel = "Blessings",
                ShadowsLabel = "Shadows",
            };
            for (var i = 0; i < state.Blessings.Length; i++)
            {
                var b = (AbyssBlessing)state.Blessings[i];
                var s = (AbyssShadow)state.Shadows[i];
                data.Cards.Add(new AbyssOverlayViewData.Card
                {
                    BlessingName = AbyssText.Name(b),
                    BlessingText = AbyssText.Text(b),
                    ShadowName = AbyssText.Name(s),
                    ShadowText = AbyssText.Text(s),
                    BlessingIcon = Png(job.ArtRoot + "/" + AbyssOverlayContentRig.BlessingIcon(b)),
                    ShadowIcon = Png(job.ArtRoot + "/" + AbyssOverlayContentRig.ShadowIcon(s)),
                });
            }
            foreach (var b in state.TakenBlessings.Select(x => (AbyssBlessing)x))
            {
                data.Blessings.Add(new AbyssOverlayViewData.StripIcon
                {
                    Name = AbyssText.Name(b), Text = AbyssText.Text(b),
                    Icon = Png(job.ArtRoot + "/" + AbyssOverlayContentRig.BlessingIcon(b)),
                });
            }
            foreach (var s in state.TakenShadows.Select(x => (AbyssShadow)x))
            {
                data.Shadows.Add(new AbyssOverlayViewData.StripIcon
                {
                    Name = AbyssText.Name(s), Text = AbyssText.Text(s),
                    Icon = Png(job.ArtRoot + "/" + AbyssOverlayContentRig.ShadowIcon(s)),
                });
            }

            var view = AbyssOverlayView.Build(data, fonts, _ => new Control());
            stage.AddChild(view.Root);
            for (var i = 0; i < state.Votes.Length && i < view.CardCount; i++)
            {
                foreach (var file in state.Votes[i])
                {
                    view.VoteSlot(i).AddChild(new TextureRect
                    {
                        Texture = Png(file),
                        ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                        StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
                        CustomMinimumSize = new Vector2(40, 40),
                    });
                }
            }
            for (var f = 0; f < 4; f++)
            {
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                view.EqualizeSections();
            }
            if (state.Chosen >= 0) view.SetCardChosen(state.Chosen);
            if (state.Focused >= 0) view.SetCardFocused(state.Focused, true);
            if (!string.IsNullOrEmpty(state.Result))
            {
                view.DimAllBut(state.Chosen);
                view.ShowResult(state.Result);
            }
            for (var f = 0; f < 30; f++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
            var img = vp.GetTexture().GetImage();
            var path = $"{job.Out}/{state.Name}.png";
            img.SavePng(path);
            GD.Print($"RIG|wrote {path}");
            ReportOverflow(view, state.Name);
            vp.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        }
        GD.Print("RIG|done");
        GetTree().Quit(0);
    }

    /// <summary>Print every card's rect and whether it leaves the screen, so
    /// the driver can fail on clipping without a human looking.</summary>
    private static void ReportOverflow(AbyssOverlayView view, string state)
    {
        for (var i = 0; i < view.CardCount; i++)
        {
            var r = view.Hit(i).GetGlobalRect();
            var clipped = r.Position.Y < 72 || r.End.Y > 1080 || r.Position.X < 0 || r.End.X > 1920;
            GD.Print($"RIG|rect {state} card{i} {r.Position.X:0},{r.Position.Y:0} {r.Size.X:0}x{r.Size.Y:0} clipped={clipped}");
        }
    }

    private static Texture2D? Png(string path)
    {
        if (string.IsNullOrEmpty(path) || !System.IO.File.Exists(path)) return null;
        var img = Image.LoadFromFile(path);
        return img == null ? null : ImageTexture.CreateFromImage(img);
    }
}

/// <summary>The few strings and icon files the rig needs from
/// AbyssOverlayModel.cs, which itself needs the game's Rng and so is not
/// compiled here. Pinned equal to the model's by
/// tier0/tests/test_abyss_overlay_bridge_page.py.</summary>
internal static class AbyssOverlayContentRig
{
    public const string Heading = "The Spiral Abyss";

    public const string Whisper =
        "The Abyss whispers, urging you deeper. Take one Blessing; "
      + "the enemies take one of the Shadows you pass.";

    public static string BlessingIcon(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine => "abyss/relics/ley_line.png",
        AbyssBlessing.AbyssalMoon => "abyss/relics/abyssal_moon.png",
        AbyssBlessing.MoonlitRest => "abyss/relics/moonlit_rest.png",
        AbyssBlessing.FirstStrike => "abyss/relics/first_strike.png",
        AbyssBlessing.ElementalBurst => "abyss/relics/elemental_burst.png",
        AbyssBlessing.Resonance => "abyss/relics/resonance.png",
        AbyssBlessing.Crystallize => "abyss/relics/crystallize.png",
        AbyssBlessing.FatefulFortune => "abyss/relics/fateful_fortune.png",
        _ => "",
    };

    public static string ShadowIcon(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock => "abyss/powers/shadow_clock.png",
        AbyssShadow.MageShield => "abyss/powers/shadow_mage_shield.png",
        AbyssShadow.SheerCold => "abyss/powers/shadow_sheer_cold.png",
        AbyssShadow.ElementalMark => "abyss/powers/shadow_elemental_mark.png",
        AbyssShadow.Herald => "abyss/powers/shadow_herald.png",
        AbyssShadow.Rally => "abyss/powers/shadow_rally.png",
        AbyssShadow.Riptide => "abyss/powers/shadow_riptide.png",
        AbyssShadow.FatuiSkirmishers => "abyss/powers/shadow_fatui_skirmishers.png",
        _ => "",
    };
}
