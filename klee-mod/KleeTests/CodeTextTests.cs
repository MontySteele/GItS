using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// CODE-BUILT TEXT, KEYED (the localization census, 2026-10-23, step 1).
///
/// THE PARITY PROOF. <c>Fixtures/code_text_before_2026_10_23.json</c> is the
/// English every touched surface rendered BEFORE the rows were keyed, dumped
/// off the old assembly (main 3c23c6043): the player's tip bodies, the seat's
/// long forms, the guests' sentences and halves, the reaction tips, cells,
/// notes and chart labels. Each is rendered here from its keyed row and its
/// vars, through SmartFormat as the English table would, and must match
/// character for character. When a sentence is reworded on purpose, its
/// entry here is reworded with it.
///
/// THE MECHANISM: every row lands in the English table, no key is written
/// twice with different English, and the formatter reads plurals and
/// escapes the way the game's does.
/// </summary>
public class CodeTextTests
{
    private static readonly Assembly Mod = typeof(CodeText).Assembly;
    private static readonly Type Player = Mod.GetType("KleeMod.Cards.PlayerTips")!;
    private const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;

    private static SortedDictionary<string, string> Before()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "review"))) dir = dir.Parent;
        var path = Path.Combine(dir!.FullName, "klee-mod", "KleeTests", "Fixtures",
                                "code_text_before_2026_10_23.json");
        return JsonSerializer.Deserialize<SortedDictionary<string, string>>(File.ReadAllText(path))!;
    }

    private static string Text(string key) =>
        (string)Player.GetMethod("Text", Any)!.Invoke(null, new object[] { key, Array.Empty<(string, object)>() })!;

    private static string Static(Type type, string name) =>
        type.GetField(name, Any)?.GetValue(null) as string
        ?? (string)type.GetProperty(name, Any)!.GetValue(null)!;

    private static Dictionary<string, string> PlayerBodiesBefore(SortedDictionary<string, string> before) =>
        before.Where(p => p.Key.StartsWith("player:")).ToDictionary(p => p.Key[7..], p => p.Value);

    // ---- the player's tip bodies -------------------------------------------

    [Fact]
    public void Every_old_player_body_renders_the_same_from_its_row()
    {
        foreach (var (key, english) in PlayerBodiesBefore(Before()))
        {
            Assert.Equal(english, Text(key));
        }
        Assert.Equal(Before()["playerspark:True"], (string)Player.GetMethod("SparkBody", Any)!.Invoke(null, new object[] { true })!);
        Assert.Equal(Before()["playerspark:False"], (string)Player.GetMethod("SparkBody", Any)!.Invoke(null, new object[] { false })!);
    }

    /// <summary>The tips whose one body the seat and the player read alike:
    /// the old literal in the attach method is now the row.</summary>
    [Theory]
    [InlineData("ForPlanElement", nameof(ArmKeywordTips.PlanElementKey))]
    [InlineData("ForMend", nameof(ArmKeywordTips.MendKey))]
    [InlineData("ForLightfallSword", nameof(ArmKeywordTips.LightfallSwordKey))]
    [InlineData("ForCompanion", nameof(ArmKeywordTips.CompanionKey))]
    [InlineData("ForAscensionReturn", nameof(ArmKeywordTips.AscensionReturnKey))]
    [InlineData("ForAscensionNoOath", nameof(ArmKeywordTips.AscensionNoOathKey))]
    [InlineData("ForEmptyField", nameof(ArmKeywordTips.EmptyFieldKey))]
    [InlineData("ForSakura", nameof(ArmKeywordTips.SakuraKey))]
    public void A_shared_body_renders_the_old_literal(string method, string keyName)
    {
        var key = (string)typeof(ArmKeywordTips).GetField(keyName)!.GetRawConstantValue()!;
        var before = Before();
        // Sakura's [0] is the Yae branch's character id; EmptyField's [1] is
        // its variant (below).
        var old = before[$"seat:{method}:{(method == "ForSakura" ? 1 : 0)}"];
        Assert.Equal(old, Text(key));
        // The attach method prints no English of its own any more.
        var literals = Il.Strings(typeof(ArmKeywordTips).GetMethod(method)!)
            .Where(s => !s.StartsWith("KLEEMOD-") && s != "yae" && s != " " && s != "own_line").ToList();
        Assert.Empty(literals);
    }

    [Fact]
    public void The_variant_rows_render_the_old_literals()
    {
        var before = Before();
        Assert.Equal(before["seat:ForEmptyField:1"],
            (string)Player.GetMethod("Variant", Any)!.Invoke(null, new object[] { ArmKeywordTips.EmptyFieldKey, "own_line" })!);
        foreach (var e in ElementWords.All)
        {
            var old = before["seat:ForElementSwitch:0"] + e + before["seat:ForElementSwitch:1"];
            var now = (string)Player.GetMethod("Text", Any)!.Invoke(null, new object[]
            {
                ArmKeywordTips.ElementSwitchKey,
                new (string, object)[] { ("Element", ElementWords.Name(e)) },
            })!;
            Assert.Equal(old, now);
        }
    }

    [Theory]
    [InlineData("YaeSakuraTip")]
    [InlineData("YaeEditTip")]
    [InlineData("YaeTenkoTip")]
    [InlineData("YaeFoxfireSakuraTip")]
    [InlineData("YaeKitsuneSakuraTip")]
    [InlineData("YaeFullShrineTip")]
    [InlineData("FanfareBody")]
    [InlineData("FlipBody")]
    [InlineData("BankDamageBody")]
    [InlineData("KnightTipText")]
    [InlineData("YaeSakuraTargetRule")]
    [InlineData("SpendUpToSentence")]
    [InlineData("DrainBody")]
    [InlineData("RepayBody")]
    public void A_named_body_reads_as_it_did(string name)
    {
        Assert.Equal(Before()["static:" + name], Static(typeof(ArmKeywordTips), name));
    }

    [Fact]
    public void The_seats_long_forms_are_unchanged()
    {
        var before = Before();
        Assert.Equal(before["seatspark:True"], ArmKeywordTips.SparkBody(true));
        Assert.Equal(before["seatspark:False"], ArmKeywordTips.SparkBody(false));
        // The methods that keep a seat sentence keep its literals, word for word.
        foreach (var method in new[] { "ForBomb", "ForSetOff", "ForMine", "ForOz", "ForPlan", "ForPlanOnly",
                                       "ForPlanNoLine", "ForSwirl", "ForElementalReaction", "ForOath",
                                       "ForCurrentElement", "ForSpend", "ForSummon", "ForGuestStar",
                                       // The riders only a seat's chain carries: seat text, no row.
                                       "ForPlanTwice", "ForNereidsTwice", "ForFinalBowInTurn",
                                       "ForBigBaddaBoomTotal", "ForBoomBadgeTurn", "ForLionsFangLastTurn",
                                       "ForPassTheMatchActing", "ForOldestGuest" })
        {
            var old = before.Where(p => p.Key.StartsWith($"seat:{method}:")).Select(p => p.Value).ToHashSet();
            var now = Il.Strings(typeof(ArmKeywordTips).GetMethod(method)!)
                .Where(s => !s.StartsWith("KLEEMOD-")).ToHashSet();
            Assert.Equal(old, now);
        }
    }

    // ---- the guests -----------------------------------------------------------

    [Fact]
    public void Every_guest_sentence_reads_as_it_did()
    {
        foreach (var (name, english) in Before().Where(p => p.Key.StartsWith("act:")))
        {
            var parts = name.Split(':');
            var who = Enum.Parse<StagePerformer>(parts[1]);
            Assert.Equal(english, StagePerformerBadge.ActText(who, bool.Parse(parts[2])));
        }
    }

    [Fact]
    public void Every_guest_tip_picks_the_half_it_picked_from_the_english_face()
    {
        // The old rule read the card's English face; the generator now stamps
        // the answer on the class. Each Guest Star card's tip, base and
        // upgraded, as the old rule printed it.
        var badge = typeof(StagePerformerBadge);
        var cases = Before().Where(p => p.Key.StartsWith("guest:")).ToList();
        Assert.Equal(22, cases.Count);
        foreach (var (name, english) in cases)
        {
            var parts = name.Split(':');
            var type = Mod.GetType("KleeMod.Cards.Prototype.Generated." + parts[1])!;
            var who = Enum.Parse<StagePerformer>(parts[2]);
            var upgraded = bool.Parse(parts[3]);
            var method = typeof(IPrintsGuestAct).IsAssignableFrom(type) ? "LineText"
                : typeof(IPrintsGuestLine).IsAssignableFrom(type) ? "ActOnlyText"
                : "GuestText";
            var now = (string)badge.GetMethod(method, Any)!.Invoke(null, new object[] { who, upgraded })!;
            Assert.Equal(english, now);
        }
    }

    [Fact]
    public void The_guest_tip_reads_no_english_face()
    {
        var guest = Player.GetMethod("Guest", Any)!;
        var calls = Il.Calls(guest);
        Assert.DoesNotContain(calls, c => c.Contains("Contains") || c.Contains("IndexOf")
                                          || c.Contains("Localization"));
    }

    // ---- the reaction guide and chart ----------------------------------------

    [Fact]
    public void Every_reaction_tip_cell_and_note_reads_as_it_did()
    {
        var before = Before();
        foreach (var e in ReactionGuide.Elements)
        {
            Assert.Equal(before["tip:" + e], ReactionGuide.TipBody(e));
            foreach (var h in ReactionGuide.Elements)
            {
                Assert.Equal(before[$"cell:{e}:{h}"], ReactionGuide.Cell(e, h));
            }
            Assert.Equal(before["chart:header:" + e], ElementWords.Name(e));
        }
        var notes = ReactionGuide.Notes;
        Assert.Equal(3, notes.Count);
        for (var i = 0; i < notes.Count; i++) Assert.Equal(before["note:" + i], notes[i]);

        string Label(string row) =>
            ReactionGuide.Label((CodeRow)typeof(ReactionGuide).GetField(row, Any)!.GetValue(null)!);
        Assert.Equal(before["chart:heading"], Label("HeadingRow"));
        Assert.Equal(before["chart:legend"], Label("LegendRow"));
        Assert.Equal(before["chart:corner"], Label("CornerRow"));
        Assert.Equal(before["chart:close"], Label("CloseRow"));
        Assert.Equal(before["chart:button"], Label("ButtonTipRow"));
    }

    // ---- step 2: Varka and Furina, and the reaction riders --------------------

    [Fact]
    public void Every_step_2_line_renders_the_same_from_its_rows()
    {
        // The face lines, Oath gains, Stage lines, counters, forecast and
        // reaction riders, each over the inputs that reach its branches
        // (`CodeTextStep2Cases`), against the English dumped off main
        // 2b5f235b1.
        var before = Before();
        var cases = CodeTextStep2Cases.All(KleeCardTooltips.SetOffFirstBody, KleeCardTooltips.FoldedHereBody,
                                           KleeCardTooltips.FoldedElsewhereBody, KleeCardTooltips.WithBoot)
            .ToList();
        Assert.Equal(before.Keys.Count(k => k.StartsWith("s2:")), cases.Count);
        foreach (var (key, render) in cases)
        {
            Assert.True(before.ContainsKey(key), key);
            Assert.Equal(before[key], render());
        }
    }

    [Fact]
    public void A_step_2_surface_builds_no_english_of_its_own()
    {
        // The methods the rows replaced print no English literal any more:
        // every sentence they hand a player is a row. A one-word literal is a
        // var's name or an identifier the cards pass (the Repay floor's
        // `PayBlock`, a cue target `random_aura`), never printed; a line
        // break between list lines is layout.
        var surfaces = new (Type Type, string[] Methods)[]
        {
            (typeof(VarkaOath), new[] { "SwitchWords", "SwirlWords", "WildfireWords", "SwirlPays",
                                        "GainClause", "GainLine" }),
            (typeof(FurinaStageBowPreview), new[] { "Line" }),
            (typeof(FurinaStageFacePreview), new[] { "DrainTag", "SplitTag", "DrainBlock", "BlockFrom",
                                                     "LostThisCombatWords", "SpendUpToHitsWords", "Line" }),
            (typeof(Vfx.DrainedCounter), new[] { "BufferSentence", "DrainedPhrase", "HoverBody",
                                                 "ReturnsLine", "ComingLines" }),
            (typeof(Vfx.FanfareCounter), new[] { "HoverBody" }),
            (typeof(Vfx.FurinaStageCues), new[] { "ForecastLine" }),
            (typeof(HalfHpFace), new[] { "Words" }),
            (typeof(SwirlAuraFace), new[] { "Words" }),
            (typeof(KleeCardTooltips), new[] { "OverriddenElementBody", "AmplifiedBody", "FrozenArtifactBody",
                                               "DebuffArtifactSentence", "NoHitBody", "SwirlPreviewBody",
                                               "SpendOnly" }),
        };
        var checkedMethods = 0;
        foreach (var (type, methods) in surfaces)
        {
            foreach (var method in type.GetMethods(Any).Where(m => methods.Contains(m.Name)))
            {
                checkedMethods++;
                var literals = Il.Strings(method)
                    .Where(s => s != "\n" && !System.Text.RegularExpressions.Regex.IsMatch(s, "^[A-Za-z_]*$"))
                    .ToList();
                Assert.True(literals.Count == 0, $"{type.Name}.{method.Name}: {string.Join(" | ", literals)}");
            }
        }
        Assert.True(checkedMethods >= 30, checkedMethods.ToString());
    }

    // ---- the mechanism ---------------------------------------------------------

    [Fact]
    public void Every_row_has_its_own_key_and_no_number_is_baked_where_a_var_reads_it()
    {
        var rows = CodeText.Sources().ToList();
        Assert.Equal(rows.Count, rows.Select(r => (r.Table, r.Key)).Distinct().Count());
        // Our rows, in the table the surface's own rows live in: the keyword
        // table, or the Spiral Abyss's event rows (step 3).
        Assert.All(rows, r => Assert.True(
            (r.Table == "card_keywords" && r.Key.StartsWith("KLEEMOD-"))
            || (r.Table == "events" && r.Key.StartsWith("KLEE_SPIRAL_ABYSS.")), r.Table + "/" + r.Key));
        // A row a var fills names the var, never the law's number.
        Assert.Contains(rows, r => r.English.Contains("{BombGrowth}"));
        Assert.DoesNotContain(rows, r => r.Key.StartsWith("KLEEMOD-ARM_BOMB.") && r.English.Contains(
            KleeOverhaulLaw.BombGrowth.ToString()));
    }

    [Fact]
    public void No_row_overwrites_a_row_another_merge_or_the_pck_writes()
    {
        // The rows the other injectors and the pck's English file write, then
        // ours over them: a key both write must carry the same English
        // (Knight's player body is `.description_named` for exactly this:
        // `.description` is the Knight keyword's row).
        var reference = LocReferenceTests.Build();
        var others = new Dictionary<string, string>(StringComparer.Ordinal);
        var file = Path.Combine(Path.GetDirectoryName(LocReferenceTests.ReferencePath())!, "..", "..",
                                "pck-src", "klee", "localization", "eng", "card_keywords.json");
        if (File.Exists(file))
        {
            foreach (var (k, v) in JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(file))!)
            {
                others[k] = v;
            }
        }
        foreach (var row in CodeText.Sources())
        {
            Assert.Equal(row.English, reference[row.Table][row.Key]);
            if (others.TryGetValue(row.Key, out var theirs)) Assert.Equal(theirs, row.English);
        }
        Assert.Equal(Static(typeof(ArmKeywordTips), "KnightTipText"), reference["card_keywords"]["KLEEMOD-ARM_VARKA_KNIGHT.description"]);
    }

    [Fact]
    public void The_rows_go_to_the_english_table_and_not_the_local_one()
    {
        var english = new Dictionary<string, LocTable>(StringComparer.Ordinal);
        var local = new Dictionary<string, LocTable>(StringComparer.Ordinal);
        LocTable En(string n) => english.TryGetValue(n, out var t) ? t : english[n] = new LocTable(n, new Dictionary<string, string>());
        LocTable? Zh(string n) => local.TryGetValue(n, out var t) ? t : local[n] = new LocTable(n, new Dictionary<string, string>());
        var inject = typeof(CodeText).GetMethod("Inject", Any)!;
        EnglishLoc.Within(En, Zh, () => inject.Invoke(null, null));
        var row = CodeText.Sources().First();
        Assert.Equal(row.English, english[row.Table].GetRawText(row.Key));
        Assert.True(!local.TryGetValue(row.Table, out var zh) || !zh.HasEntry(row.Key));
    }

    [Fact]
    public void The_headless_formatter_reads_plurals_vars_and_escapes_like_the_games()
    {
        Assert.Equal("draw 1 card.", CodeText.FormatEnglish("draw {N} card{N:plural:|s}.", CodeText.Vars(("N", 1))));
        Assert.Equal("draw 2 cards.", CodeText.FormatEnglish("draw {N} card{N:plural:|s}.", CodeText.Vars(("N", 2))));
        Assert.Equal("1.5x", CodeText.FormatEnglish("{M}x", CodeText.Vars(("M", CodeText.Num(1.50m)))));
        Assert.Equal("50%", CodeText.FormatEnglish("{P}%", CodeText.Vars(("P", CodeText.Num(50.00m)))));
        Assert.Equal("Aura \\ Hit", CodeText.FormatEnglish("Aura \\\\ Hit", null));
    }

    [Fact]
    public void An_element_token_row_reaches_the_english_reference()
    {
        // Group 3: a card face's hit element is a token in its row.
        var cards = LocReferenceTests.Build()["cards"];
        Assert.Contains(cards.Values, v => v.Contains("[gold]{Hydro}[/gold] damage"));
        Assert.Contains(cards.Values, v => v.Contains("Apply [gold]{Hydro}[/gold]"));
    }

    [Fact]
    public void A_face_with_element_tokens_reads_its_english_when_nothing_overrides()
    {
        // Every one of our card faces, tokens filled with their own names,
        // is the face the generator wrote, character for character.
        var faces = 0;
        foreach (var type in Mod.GetTypes().Where(t => !t.IsAbstract && typeof(CardModel).IsAssignableFrom(t)))
        {
            var model = (AbstractModel)RuntimeHelpers.GetUninitializedObject(type);
            if (model is not BaseLib.Abstracts.ILocalizationProvider provider || provider.Localization is not { } rows) continue;
            foreach (var (key, value) in rows)
            {
                var written = EnglishLoc.ModelRowText(model, key, value);
                if (written == BaseLib.Patches.Localization.SimpleLoc.TrySimplify(value)) continue;
                faces++;
                var filled = ElementWords.All.Aggregate(written, (t, e) => t.Replace("{" + e + "}", e.ToString()));
                Assert.Equal(BaseLib.Patches.Localization.SimpleLoc.TrySimplify(value), filled);
            }
        }
        Assert.True(faces > 100, faces.ToString());
    }
}
