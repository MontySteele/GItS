using System;
using System.Linq;
using System.Reflection;
using BaseLib.Patches.Content;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE ELEMENT INDICATOR, pinned.
///
/// [USER], 2026-09-01, after playing Klee: "instead of saying 'applies pyro' -
/// maybe make it a card indicator as well to remove text overhead? That would
/// be a universal shift."
///
/// WHAT IS REACHABLE HERE. Painting is not: it needs Godot nodes, which are
/// process death in this host (README, the headless boundary) -- the same wall
/// <see cref="MeterCostBadgeTests"/> records. Everything the gem DEPENDS on is a
/// plain read: the switch that stopped the sentence printing (an attribute on a
/// field), the element a card declares (a keyword on the model), the icon each
/// element declares (a pure switch), and the structural facts that keep the
/// display honest -- that the gem asks the same declaration the tip is built
/// from, and that it holds no engine-owned object across a scene.
///
/// THE KEYWORD VALUES ARE ASSIGNED BY BaseLib at `ModelDb.Init`
/// (`GenEnumValues`), which does not run here, so all four fields read `0`, i.e.
/// `CardKeyword.None`, and `ElementOf` cannot tell them apart on a stock test
/// host. <see cref="WithKeywordValues"/> does what the game does -- four
/// distinct values for the duration of one test, restored after -- which is the
/// <c>ArmKeywordTipTests</c> idiom one field over.
///
/// The GENERATOR's half of the same join, every prototype row that applies an
/// element carrying the keyword that draws its gem, is
/// `tier0/tests/test_element_badge.py`: which faces owe which keyword is decided
/// by `gen_klee_cards.aura_elements_for` reading the sheet's cadence.
/// </summary>
public class ElementBadgeTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>`ElementBadge` is internal, like most of the mod: resolved off
    /// the shipped assembly the way `MeterCostBadgeTests` reaches its badge.
    /// </summary>
    private static readonly Type Badge =
        Il.Method("ElementBadge", "Paint").DeclaringType!;

    /// <summary>The four `AppliesX` fields, found by their `CustomEnum` name
    /// rather than from a list here -- a curated list would have to be updated
    /// in the same commit that adds a fifth element, and the failure this
    /// guards against IS the commit that adds one and forgets it.</summary>
    private static FieldInfo[] AppliesFields() => typeof(KleeKeywords)
        .GetFields(BindingFlags.Public | BindingFlags.Static)
        .Where(f => f.GetCustomAttribute<CustomEnumAttribute>()?.Name
                     ?.StartsWith("applies_", StringComparison.Ordinal) == true)
        .ToArray();

    /// <summary>Run <paramref name="body"/> with the four element keywords
    /// carrying distinct values, as BaseLib gives them at `ModelDb.Init`, and
    /// put them back afterwards. The numbers are arbitrary and deliberately not
    /// 1..4: nothing may depend on WHICH value an element got.</summary>
    private static void WithKeywordValues(Action body)
    {
        var fields = AppliesFields();
        var saved = fields.Select(f => f.GetValue(null)).ToArray();
        try
        {
            for (var i = 0; i < fields.Length; i++)
            {
                fields[i].SetValue(null, Enum.ToObject(
                    typeof(CardKeyword), 9000 + i));
            }

            body();
        }
        finally
        {
            for (var i = 0; i < fields.Length; i++)
            {
                fields[i].SetValue(null, saved[i]);
            }
        }
    }

    private static Element ElementOf(CardModel card) => (Element)Badge
        .GetMethod("ElementOf", All)!.Invoke(null, new object[] { card })!;

    /// <summary>The `KleeKeywords` field a card's `CanonicalKeywords` LOADS.
    /// A static field read is `ldsfld`, not a call, so `Il.Calls` cannot see
    /// it; this is that same byte scan one opcode over.</summary>
    private static string KeywordFieldOf(Type card)
    {
        var body = card.GetProperty("CanonicalKeywords", All)!
            .GetGetMethod()!.GetMethodBody()!.GetILAsByteArray()!;
        for (var i = 0; i < body.Length - 4; i++)
        {
            if (body[i] != 0x7E) continue;              // ldsfld
            try
            {
                var field = card.Module.ResolveField(
                    BitConverter.ToInt32(body, i + 1));
                if (field?.DeclaringType == typeof(KleeKeywords)
                    && field.Name.StartsWith("Applies", StringComparison.Ordinal))
                {
                    return field.Name;
                }
            }
            catch
            {
                // Not a field token. Expected while byte-scanning.
            }
        }

        return "";
    }

    // --- the switch that stopped the sentence ------------------------------

    [Fact]
    public void No_element_keyword_auto_prints_a_line_any_more()
    {
        // THE WHOLE OF THE REMOVAL, read off the compiled attribute rather than
        // off a source line. `AutoKeywordPosition.After` is what printed
        // "Applies Pyro": BaseLib's `GenEnumValues` puts an `After` keyword into
        // `AutoKeywordText.AdditionalAfterKeywords`, from there into the base
        // game's `CardKeywordOrder.afterDescription`, and
        // `CardModel.BuildDescription` appends its card text as a line of the
        // rules box. One field returning to `After` puts the sentence back on
        // every face of that element at once, and nothing else in this repo
        // would notice.
        var fields = AppliesFields();

        // `EB-454` MADE IT SIX. Anemo and Geo leave no aura and still get no
        // gem (`IconPathFor` answers null for both, and `AuraApplication` still
        // answers `None`), but they carry the WORD now: a face that names no
        // element reads as untyped, and the r13 seat read `Jean -- Gale Blade`
        // that way until a reaction preview named Anemo mid-fight. The claim
        // this test makes is about the POSITION, and it is unchanged.
        Assert.Equal(6, fields.Length);
        Assert.All(fields, f => Assert.Equal(
            AutoKeywordPosition.None,
            f.GetCustomAttribute<KeywordPropertiesAttribute>()!.Position));
    }

    [Fact]
    public void The_tip_survives_the_switch_because_it_never_read_the_text()
    {
        // WHY THE FLIP IS SAFE, stated as a property of the BASE GAME rather
        // than as a hope: `CardModel.HoverTips` walks `Keywords` and calls
        // `HoverTipFactory.FromKeyword` on each of them -- it never consults the
        // printed description. So a keyword at `None` still hovers, which
        // `Bomb`, `Confiscated` and the eight reaction previews have
        // demonstrated since they were written, having never printed a line and
        // always hovered.
        var hoverTips = typeof(CardModel).GetProperty("HoverTips", All)!
            .GetGetMethod()!;

        Assert.Contains(Il.Calls(hoverTips),
                        c => c.EndsWith("HoverTipFactory.FromKeyword"));

        // And the keyword is still ON the faces, which is what makes that walk
        // reach them -- the flip moved the POSITION and nothing else.
        Assert.Equal("AppliesPyro", KeywordFieldOf(typeof(Snap)));
        Assert.Equal("AppliesHydro", KeywordFieldOf(typeof(PearlBarrage)));
        Assert.Equal("", KeywordFieldOf(typeof(CoralGuard)));
    }

    // --- the gem reads the tip's own declaration ---------------------------

    [Fact]
    public void The_gem_and_the_tip_are_one_declaration()
    {
        // STRUCTURAL PIN, and it is the property the whole change rests on: the
        // badge asks the CARD's keywords, through the same `AuraApplication`
        // table `KleeCardTooltips` and codegen use, rather than carrying its own
        // element list or reading `IElementalCard`. A card can therefore no more
        // wear a gem it does not explain than explain an element it does not
        // wear -- the display-versus-gate argument `MeterCostBadge` makes about
        // a price, made about a word.
        var calls = Il.Calls(Badge.GetMethod("ElementOf", All)!);

        Assert.Contains(calls, c => c.EndsWith("KleeKeywords.AuraApplication"));
        Assert.Contains(calls, c => c.EndsWith("CardModel.get_Keywords"));
    }

    [Fact]
    public void A_card_reads_back_the_element_its_keyword_declares()
        => WithKeywordValues(() =>
        {
            // The one BEHAVIOURAL read this host allows, with the keyword values
            // the game would have assigned. The cards are constructed inside the
            // block on purpose: `CardModel` caches `LocalKeywords` off
            // `CanonicalKeywords` on first read, so one built before the
            // assignment would have cached four `CardKeyword.None`s.
            Assert.Equal(Element.Pyro, ElementOf(new Snap()));
            Assert.Equal(Element.Hydro, ElementOf(new PearlBarrage()));
            // A card that applies nothing wears nothing. `Coral Guard` blocks.
            Assert.Equal(Element.None, ElementOf(new CoralGuard()));
        });

    // --- the gem's art -----------------------------------------------------

    [Fact]
    public void Every_element_that_leaves_an_aura_declares_a_gem_of_its_own()
    {
        // Three facts, each a way the repair could rot, on
        // `MeterCostBadgeTests.Every_meter_resolves_a_glyph_of_its_own`'s terms:
        //
        //   * every aura-leaving element declares a path -- a keyword whose
        //     element has no icon draws NOTHING, invisible in exactly the way
        //     EB-272's missing tooltips were,
        //   * no two share one, since a shared gem would read as intentional
        //     (the reason `KleePowerIcons` names its powers one by one), and
        //   * Anemo and Geo declare NONE, because they leave no aura (LAW,
        //     combat: "Anemo/Geo leave no aura -- they only trigger") and so
        //     have no aura icon to paint. `EB-454` gave both a KEYWORD, which
        //     is the word and the tip; the gem is still the four that leave
        //     something on a body.
        //
        // The FILES are the art pipeline's business (`art/plan.tsv` rows
        // `power_aura_*`); no pck is present in this host, so what is provable
        // here is the declaration.
        var iconPathFor = Badge.GetMethod("IconPathFor", All)!;
        var gems = Enum.GetValues(typeof(Element)).Cast<Element>()
            .ToDictionary(e => e,
                          e => (string?)iconPathFor.Invoke(
                              null, new object[] { e }));

        var drawn = gems.Where(kv => kv.Value != null).ToList();
        Assert.Equal(4, drawn.Count);
        Assert.Equal(4, drawn.Select(kv => kv.Value).Distinct().Count());
        Assert.All(drawn, kv => Assert.StartsWith("klee/powers/aura_", kv.Value));
        Assert.Null(gems[Element.Anemo]);
        Assert.Null(gems[Element.Geo]);
        Assert.Null(gems[Element.None]);

        // The AURA's own icon, by name: the badge a player will see on the
        // enemy is the picture on the card that puts it there.
        Assert.Equal("klee/powers/aura_pyro.png", gems[Element.Pyro]);
    }

    // --- EB-222: the badge holds no texture across scenes ------------------

    [Fact]
    public void The_badge_caches_no_engine_owned_object_in_a_static_field()
    {
        // EB-222, inherited whole. The game frees a room's assets WITH the room,
        // so a `Texture2D` reachable from a static of ours is a corpse by the
        // first card of the next combat and `TextureRect.SetTexture` throws
        // `ObjectDisposedException` out of the TURN LOOP -- combat stuck, run
        // over. FIELD TYPES ONLY: no Godot object is touched, which is itself
        // the headless boundary.
        var offenders = Badge
            .GetFields(BindingFlags.Static | BindingFlags.Public
                       | BindingFlags.NonPublic)
            .Where(f => IsEngineOwned(f.FieldType))
            .Select(f => f.Name)
            .ToList();

        Assert.Empty(offenders);
    }

    private static bool IsEngineOwned(Type type)
        => (type.FullName ?? string.Empty)
               .StartsWith("Godot.", StringComparison.Ordinal)
           || type.GetGenericArguments().Any(IsEngineOwned)
           || (type.IsArray && IsEngineOwned(type.GetElementType()!));

    [Fact]
    public void The_gem_is_resolved_from_the_loader_on_every_paint()
    {
        // The other half of EB-222's fix, in the one method the badge asks for a
        // texture through: it goes to `ResourceLoader` each time (so the engine's
        // own cache, which knows what it has freed, is the source) and asks
        // `IsInstanceValid` before answering.
        var calls = Il.Calls(Badge.GetMethod("Glyph", All)!);

        Assert.Contains(calls, c => c.EndsWith("ResourceLoader.Load"));
        Assert.Contains(calls, c => c.EndsWith("GodotObject.IsInstanceValid"));
    }

    [Fact]
    public void A_freed_gem_degrades_to_no_gem_and_never_throws_at_the_turn()
    {
        // The EB-221 shape: warn once, draw less, never propagate. `Paint` runs
        // from `UpdateStarCostVisuals`, i.e. inside the turn loop, so the ONE
        // thing it may never do is throw -- and a card that loses its gem still
        // carries the keyword, so the tip still explains the aura.
        var handled = Badge.GetMethod("Show", All)!
            .GetMethodBody()!.ExceptionHandlingClauses
            .Where(c => c.Flags == ExceptionHandlingClauseOptions.Clause)
            .Select(c => c.CatchType?.Name)
            .ToList();

        Assert.Contains("ObjectDisposedException", handled);
        Assert.Contains(Il.Calls(Badge.GetMethod("WarnFreedGlyph", All)!),
                        c => c.EndsWith("Log.Warn"));
    }

    [Fact]
    public void The_gem_hangs_on_the_type_plaque_and_is_named_once()
    {
        // THE SEAM, pinned by the two strings that make it one. `%TypePlaque` is
        // the base game's own per-card classification badge -- the pill reading
        // "Attack" / "Skill" / "Power" -- and is resolved by its SCENE-UNIQUE
        // NAME, what `NCard._Ready` itself resolves, so the two cannot drift and
        // a scene that drops it makes the badge inert instead of throwing
        // (`NonFiniteCardGuard` reads it the same way and says so). The node name
        // is a constant because a pooled `NCard` has to find the gem it already
        // carries rather than stack a second.
        Assert.Equal("%TypePlaque",
                     Badge.GetField("PlaquePath", All)!.GetValue(null));
        Assert.Contains(
            (string)Badge.GetField("NodeName", All)!.GetValue(null)!,
            Il.Strings(Badge.GetMethod("Build", All)!));

        // ANCHORED, NOT POSITIONED, and that is correctness rather than style:
        // `NCard.UpdateTypePlaqueSizeAndPosition` is DEFERRED, so any plaque rect
        // read at patch time is a frame stale, and a gem placed from it would
        // jump by the width difference between "Attack" and "Power". Anchoring
        // hands the recompute to the engine's own layout pass.
        var build = Il.Calls(Badge.GetMethod("Build", All)!);
        Assert.DoesNotContain(build, c => c.EndsWith("Control.set_Position"));
        Assert.DoesNotContain(build, c => c.EndsWith("Control.set_Size"));
    }
}
