using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Abyss;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.ControllerInput;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// CODE-BUILT TEXT, KEYED, STEP 3 (the localization census, 2026-10-23):
/// Kokomi's plan strip and view, Yae's Annotations, Tenko clause and shrine
/// row, the Spiral Abyss, and the leftovers.
///
/// THE PARITY PROOF, on step 1's terms (<see cref="CodeTextTests"/>).
/// <c>Fixtures/code_text_before_step3_2026_10_23.json</c> is the English each
/// case below printed BEFORE the rows were keyed, dumped off the old assembly
/// (main 2b5f235b1) by these same calls; its <c>literal:</c> entries are the
/// sentences the old code printed inline (no method of their own to call),
/// copied from the literal. Each is rendered here from its keyed row and
/// must match character for character.
/// </summary>
public class CodeTextStep3Tests
{
    private static readonly Assembly Mod = typeof(CodeText).Assembly;
    private const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;

    internal static string FixturePath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "review"))) dir = dir.Parent;
        return Path.Combine(dir!.FullName, "klee-mod", "KleeTests", "Fixtures",
                            "code_text_before_step3_2026_10_23.json");
    }

    private static SortedDictionary<string, string> Before() =>
        JsonSerializer.Deserialize<SortedDictionary<string, string>>(File.ReadAllText(FixturePath()))!;

    private static string Static(string type, string name)
    {
        var t = Mod.GetType(type)!;
        return t.GetField(name, Any)?.GetValue(null) as string
               ?? (string)t.GetProperty(name, Any)!.GetValue(null)!;
    }

    private static readonly YaeAnnotation[][] Stacks =
    {
        Array.Empty<YaeAnnotation>(),
        new[] { YaeAnnotation.RedInk },
        new[] { YaeAnnotation.RedInk, YaeAnnotation.RedInk, YaeAnnotation.Reprint },
        new[] { YaeAnnotation.Footnote, YaeAnnotation.SakuraSeal, YaeAnnotation.Footnote, YaeAnnotation.Royalties },
        new[] { YaeAnnotation.FoxFire, YaeAnnotation.DeadlineExtension },
    };

    /// <summary>Every case, by name: the English it prints. The same calls
    /// before and after keying.</summary>
    internal static SortedDictionary<string, string> Cases()
    {
        var c = new SortedDictionary<string, string>(StringComparer.Ordinal);

        // ---- Kokomi: the strip's captions ----------------------------------
        c["kk:copies:null"] = KokomiPlan.CopiesCaption(null);
        c["kk:copies:plain"] = KokomiPlan.CopiesCaption("Juuga");
        c["kk:copies:companion"] = KokomiPlan.CopiesCaption("Gorou — Juuga: Shield Up");
        foreach (var n in new[] { 0, 1, 7 }) c[$"kk:deals:{n}"] = KokomiPlan.LiveDeals(n);
        foreach (var n in new[] { 0, 1, 2, 5 }) c[$"kk:hits:{n}"] = KokomiPlan.LiveHits(n);
        c["kk:hplost"] = KokomiPlan.HpLostCaption;
        c["kk:blocked:7"] = KokomiPlan.LiveBlocked(7);
        c["kk:blocked:7:7"] = KokomiPlan.LiveBlocked(7, 7);
        c["kk:blocked:7:11"] = KokomiPlan.LiveBlocked(7, 11);
        c["kk:taken:3"] = KokomiPlan.LiveTaken(3);
        c["kk:taken:3:3"] = KokomiPlan.LiveTaken(3, 3);
        c["kk:taken:3:6"] = KokomiPlan.LiveTaken(3, 6);
        c["kk:noattackdeals:0"] = KokomiPlan.NoAttackDeals(0);
        c["kk:noattackdeals:4"] = KokomiPlan.NoAttackDeals(4);
        c["kk:noattackyet"] = KokomiPlan.NoAttackYet;
        c["kk:noattackintended"] = KokomiPlan.NoAttackIntended;
        c["kk:strip:nowline"] = KokomiPlan.StripCaption(true, true, null, 0, false)!;
        c["kk:strip:nowline:lost"] = KokomiPlan.StripCaption(true, true, null, 0, false, null, true)!;
        c["kk:strip:block"] = KokomiPlan.StripCaption(false, false, 29, 0, false)!;
        c["kk:strip:kept"] = KokomiPlan.StripCaption(false, false, null, 8, false)!;
        c["kk:strip:defends"] = KokomiPlan.StripCaption(false, false, null, 0, true)!;
        c["kk:strip:planline"] = KokomiPlan.StripCaption(true, false, null, 0, false)!;
        c["kk:pager:more"] = KokomiPlanPages.PagerCaption(0, KokomiPlanPages.PerPage + 3);
        c["kk:pager:back"] = KokomiPlanPages.PagerCaption(1, KokomiPlanPages.PerPage + 3);
        c["kk:position:first"] = KokomiPlanPages.PositionCaption(0, 0, 2)!;
        c["kk:position:later"] = KokomiPlanPages.PositionCaption(KokomiPlanPages.PerPage + 1, 1, KokomiPlanPages.PerPage + 3)!;
        c["kk:strip:first"] = Static("KleeMod.Vfx.KokomiPlanStrip", "FirstCaption");

        // ---- Kokomi: the view -----------------------------------------------
        var oneLine = new KokomiPlan.Entry(null, Array.Empty<KokomiPlan.Planned>(), Label: "Kelp Wall");
        var planLine = new KokomiPlan.Entry(new ProtoKkAmbush(), Array.Empty<KokomiPlan.Planned>(), Label: "Ambush");
        var nowLine = planLine with { Now = true };
        c["kk:view:planonly"] = KokomiPlanViewRows.PlanOnlyCaption;
        c["kk:view:hint"] = KokomiPlanViewRows.HintCaption;
        c["kk:view:caption:oneline"] = KokomiPlanViewRows.Caption(0, oneLine);
        c["kk:view:caption:planline"] = KokomiPlanViewRows.Caption(2, planLine);
        c["kk:view:caption:nowline"] = KokomiPlanViewRows.Caption(1, nowLine);
        c["kk:view:caption:nowline:lost"] = KokomiPlanViewRows.Caption(1, nowLine, true);
        c["kk:view:flip:oneline"] = KokomiPlanViewRows.FlipSent(oneLine);
        c["kk:view:flip:tonow"] = KokomiPlanViewRows.FlipSent(planLine);
        c["kk:view:flip:tonow:gambit"] = KokomiPlanViewRows.FlipSent(planLine, true);
        c["kk:view:flip:toplan"] = KokomiPlanViewRows.FlipSent(nowLine, true);
        c["kk:view:losesdouble"] = KokomiPlanViewRows.NowLineLosesDouble;
        c["kk:view:hint:pad"] = KokomiPlanViewRows.HintText(InputType.Controller, "S")!;
        c["kk:view:hint:keys"] = KokomiPlanViewRows.HintText(InputType.KeyboardOnlyMode, "S")!;
        c["kk:view:hint:mouse"] = KokomiPlanViewRows.HintText(InputType.MouseAndKeyboard, "Space")!;
        c["kk:view:hint:mouse:unbound"] = KokomiPlanViewRows.HintText(InputType.MouseAndKeyboard, null)!;
        c["kk:scry:autotake"] = ScryTake.AutoTakeLine("Shoal");

        // ---- Yae: the Annotations -------------------------------------------
        foreach (var a in YaeAnnotationText.All)
        {
            c[$"ym:name:{a}"] = YaeAnnotationText.Name(a);
            c[$"ym:rule:{a}"] = YaeAnnotationText.Rule(a);
            c[$"ym:sakurarule:{a}"] = YaeAnnotationText.SakuraRule(a);
            c[$"ym:tip:{a}:False"] = YaeAnnotationText.TipBody(a, false);
            c[$"ym:tip:{a}:True"] = YaeAnnotationText.TipBody(a, true);
            c[$"ym:clause:{a}"] = YaeAnnotationText.PromptClause(a);
            c[$"ym:edit:{a}"] = YaeEditing.EditPromptTextFor(a);
            c[$"ym:editupto:{a}"] = YaeEditing.EditUpToPromptTextFor(a);
            c[$"ym:mark:{a}"] = YaeSakuraSlots.MarkLetter(a);
        }
        for (var i = 0; i < Stacks.Length; i++)
        {
            c[$"ym:list:{i}"] = YaeAnnotationText.List(Stacks[i]);
            c[$"ym:face:{i}"] = YaeAnnotationText.FaceLine(Stacks[i]);
            foreach (var temp in new[] { YaeAnnotation.None, YaeAnnotation.Footnote })
            {
                foreach (var used in new[] { false, true })
                {
                    foreach (var times in new[] { 1, 2 })
                    {
                        c[$"ym:summary:{i}:{temp}:{used}:{times}"] =
                            YaeAnnotationText.Summary(Stacks[i], temp, used, times);
                    }
                }
            }
        }
        c["ym:published"] = YaeAnnotationText.PublishedHead;
        c["ym:thiscombat"] = YaeAnnotationText.ThisCombatHead;
        c["ym:reprintused"] = YaeAnnotationText.ReprintUsed;
        c["ym:redinkplants"] = YaeAnnotationText.RedInkPlantClause;

        // ---- Yae: Tenko's live clause and the shrine row --------------------
        foreach (var (d, e, b) in new[] { (0, 0, 0), (13, 0, 0), (0, 0, 5), (5, 2, 5), (12, 18, 0), (0, 4, 0) })
        {
            c[$"ym:tenko:{d}:{e}:{b}"] = YaeShrineFace.TenkoWords(d, e, b);
        }
        foreach (var kind in new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune })
        {
            c[$"ym:amount:{kind}"] = YaeShrineFace.Amount(kind, "5");
        }
        c["ym:nosakura"] = YaeShrineFace.NoSakura;
        c["ym:tenkoprefix"] = YaeShrineFace.TenkoPrefix;
        foreach (var p in new[] { YaeSlotPreview.Plants, YaeSlotPreview.Refreshes, YaeSlotPreview.Replaces })
        {
            c[$"ym:preview:{p}"] = YaeSakuraSlots.PreviewText(p)!;
        }
        c["ym:slot:rules"] = YaeSakuraSlots.RulesLine;
        c["ym:slot:empty"] = YaeSakuraSlots.EmptyLine;

        // ---- The Spiral Abyss -----------------------------------------------
        var acts = new[] { AbyssText.NoAct, 0, 1, 2, 3 };
        foreach (var b in AbyssDraft.AllBlessings)
        {
            c[$"ab:name:{b}"] = AbyssText.Name(b);
            foreach (var act in acts)
            {
                c[$"ab:text:{b}:{act}"] = AbyssText.Text(b, act);
                c[$"ab:text:{b}:{act}:-1"] = AbyssText.Text(b, act, AbyssText.NoAct);
                c[$"ab:text:{b}:{act}:2"] = AbyssText.Text(b, act, 2);
            }
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            c[$"ab:name:{s}"] = AbyssText.Name(s);
            foreach (var act in acts)
            {
                c[$"ab:text:{s}:{act}"] = AbyssText.Text(s, act);
                c[$"ab:text:{s}:{act}:-1"] = AbyssText.Text(s, act, AbyssText.NoAct);
                c[$"ab:text:{s}:{act}:2"] = AbyssText.Text(s, act, 2);
            }
        }
        foreach (var act in acts) c[$"ab:actelement:{act}"] = AbyssText.ActElement(act);
        c["ab:elementsbyact"] = AbyssText.ElementsByAct();
        c["ab:tag:WholeRun"] = AbyssDurations.Tag(AbyssDuration.WholeRun);
        c["ab:tag:ThisAct"] = AbyssDurations.Tag(AbyssDuration.ThisAct);
        c["ab:overlay:heading"] = AbyssOverlayContent.Heading;
        c["ab:overlay:whisper"] = AbyssOverlayContent.Whisper;
        c["ab:overlay:wholerun"] = AbyssOverlayContent.WholeRunTag;
        c["ab:overlay:thisact"] = AbyssOverlayContent.ThisActTag;
        c["ab:overlay:band"] = AbyssOverlayContent.ShadowBandLabel;
        c["ab:overlay:blessings"] = AbyssOverlayContent.BlessingsLabel;
        c["ab:overlay:shadows"] = AbyssOverlayContent.ShadowsLabel;
        foreach (var act in new[] { -1, 0, 1, 2 }) c[$"ab:overlay:title:{act}"] = AbyssOverlayContent.TitleFor(act);
        foreach (var coop in new[] { false, true })
        {
            foreach (var split in new[] { false, true })
            {
                c[$"ab:result:{coop}:{split}:shadow"] = AbyssOverlayFlow.ResultLineFor("Moonlit Rest", "Blood in the Water", coop, split);
                c[$"ab:result:{coop}:{split}:none"] = AbyssOverlayFlow.ResultLineFor("Moonlit Rest", null, coop, split);
            }
        }
        c["ab:shadows:none"] = AbyssDisplay.ShadowsText(Array.Empty<(AbyssShadow, int)>());
        c["ab:shadows:two"] = AbyssDisplay.ShadowsText(new[] { (AbyssShadow.Clock, 1), (AbyssShadow.MageShield, 0) });
        c["ab:shadows:two:act2"] = AbyssDisplay.ShadowsText(new[] { (AbyssShadow.Clock, 1), (AbyssShadow.MageShield, 0) }, 2);
        foreach (var (key, value) in AbyssChoicePage.LocRows())
        {
            // The strip title rows are named by value: their keys are built
            // from the enum since step 3.
            c[key.Contains(".strip.") ? "ab:strip:" + value : "ab:row:" + key] = value;
        }

        // ---- The leftovers --------------------------------------------------
        c["x:wholebank"] = Static("KleeMod.Vfx.MeterCostBadge", "WholeBankPrice");
        foreach (var nation in new[] { "mondstadt", "liyue", "inazuma", "fontaine" })
        {
            c[$"x:nation:{nation}"] = NationEmblem.StyleFor(nation)!.Value.Initial;
        }
        return c;
    }

    [Fact]
    public void Every_case_reads_as_it_did()
    {
        var before = Before();
        var now = Cases();
        foreach (var (name, english) in before.Where(p => !p.Key.StartsWith("literal:") && !p.Key.StartsWith("ab:strip:")))
        {
            Assert.True(now.ContainsKey(name), name);
            Assert.Equal(english, now[name]);
        }
        Assert.Equal(before.Count(p => !p.Key.StartsWith("literal:") && !p.Key.StartsWith("ab:strip:")),
                     now.Count(p => !p.Key.StartsWith("ab:strip:")));
    }

    [Fact]
    public void The_inline_sentences_read_as_their_old_literals()
    {
        var before = Before();
        Assert.Equal(before["literal:kk:energy:2"], KokomiPlan.LiveEnergy(2));
        Assert.Equal(before["literal:kk:attackers:1"], KokomiPlan.LiveAttackers(1));
        Assert.Equal(before["literal:kk:attackers:3"], KokomiPlan.LiveAttackers(3));
        Assert.Equal(before["literal:kk:view:nolongerwaiting"], KokomiPlanText.Text(KokomiPlanText.NoLongerWaiting));
        // No player, no Bake-Kurage: the view's sentence beside the bridge's words.
        Assert.Equal("there is no Bake-Kurage here", KokomiPlan.RequestFlip(null, 0));
        Assert.Equal(before["literal:kk:refused:nokurage"], KokomiPlan.FlipRefusalShown(null, 0));
        Assert.Equal(before["literal:kk:refused:notyourturn"], KokomiPlanText.Text(KokomiPlanText.NotYourTurn));
        Assert.Equal(before["literal:kk:refused:noplan:3"], KokomiPlanText.Text(KokomiPlanText.NoPlanAt, ("N", 3)));
        Assert.Equal(before["literal:kk:refused:oneline"], KokomiPlanText.Text(KokomiPlanText.OneLine, ("Title", "Kelp Wall")));
        var all = (CodeRow)typeof(FurinaStageCueNodes).GetField("AllRow", Any)!.GetValue(null)!;
        Assert.Equal(before["literal:x:all"], CodeText.Format(all));
    }

    [Fact]
    public void The_abyss_strip_titles_are_the_names_rows_keyed_by_the_enum()
    {
        var before = Before();
        var names = AbyssDraft.AllBlessings.Select(b => (Key: AbyssChoicePage.StripTitleKey(b), Name: AbyssText.Name(b)))
            .Concat(AbyssDraft.AllShadows.Select(s => (Key: AbyssChoicePage.StripTitleKey(s), Name: AbyssText.Name(s))))
            .ToList();
        // Every old strip title is a name row, and every name had one.
        Assert.Equal(before.Keys.Where(k => k.StartsWith("ab:strip:")).Select(k => k[9..]).OrderBy(n => n),
                     names.Select(n => n.Name).OrderBy(n => n));
        var rows = CodeText.Sources().ToDictionary(r => (r.Table, r.Key), r => r.English);
        foreach (var (key, name) in names)
        {
            Assert.Equal(name, rows[("events", key)]);
        }
        // The rename that moved the old key: Riptide shows as Blood in the Water.
        Assert.Equal("KLEE_SPIRAL_ABYSS.strip.RIPTIDE.title", AbyssChoicePage.StripTitleKey(AbyssShadow.Riptide));
        // The event page no longer writes them: the name rows are CodeText's.
        Assert.DoesNotContain(AbyssChoicePage.LocRows().Keys, k => k.Contains(".strip."));
    }

    [Fact]
    public void A_row_that_is_itself_english_reads_the_english()
    {
        foreach (var b in AbyssDraft.AllBlessings)
        {
            Assert.Equal(AbyssText.Text(b, 1), AbyssText.English(b, 1));
            Assert.Equal(AbyssText.Name(b), AbyssText.NameEnglish(b));
        }
        foreach (var a in YaeAnnotationText.All)
        {
            Assert.Equal(YaeAnnotationText.Rule(a), YaeAnnotationText.RuleEnglish(a));
            Assert.Equal(YaeAnnotationText.Name(a), YaeAnnotationText.NameEnglish(a));
        }
    }

    [Fact]
    public void The_step_3_rows_have_their_own_keys_and_quote_no_law_number()
    {
        var rows = CodeText.Sources().ToList();
        Assert.Equal(rows.Count, rows.Select(r => (r.Table, r.Key)).Distinct().Count());
        // The law's numbers are vars, never baked into the English.
        Assert.Contains(rows, r => r.Key == "KLEEMOD-ARM_YAE_REDINK.description" && r.English.Contains("{RedInkAmount}"));
        Assert.Contains(rows, r => r.Key == "KLEE_SPIRAL_ABYSS.shadows.CLOCK.description"
                                   && r.English.Contains("{ClockStrength}") && r.English.Contains("{ClockFromRound}"));
        // A plural is SmartFormat's, never an English "s" glued on.
        Assert.Contains(rows, r => r.Key == "KLEEMOD-KOKOMI_PLAN_STRIP.hits" && r.English.Contains(":plural:"));
        Assert.Contains(rows, r => r.Key == "KLEEMOD-KOKOMI_PLAN_STRIP.attackers" && r.English.Contains(":plural:"));
    }
}
