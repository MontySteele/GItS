using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Patches.Content;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CO-OP NOTES PAPER'S RULINGS (<c>review/active/coop-notes-2026-10-02.md</c>,
/// ruled 2026-10-02). Pick 2: Assembly at the Cathedral pays on every element
/// applied, and every Knight prints a "Knight." first line through a real
/// keyword that shares one tip with the cards that name Knights. Pick 4:
/// Neuvillette's Rare applies Hydro at the start of the turn. Pinned the
/// headless way: values by value, live sites by their call graph. Sim twins:
/// <c>tier0/tests/test_varka_expansion.py::test_assembly</c> and
/// <c>tier0/tests/test_fontaine.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class CoopNotesRulingsTests
{
    public CoopNotesRulingsTests()
    {
        HeadlessGame.Arm();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.ILocalizationProvider)card).Localization!
            .Single(row => row.Item1 == "description").Item2;

    // ---- pick 2 (a): Assembly at the Cathedral ------------------------------

    [Fact]
    public void Assembly_pays_on_every_element_applied_not_on_a_knights_play()
    {
        var note = Il.CallSequence(Il.Method("VarkaOath", "NoteApplication")).ToList();
        var assembly = note.IndexOf("AssemblyAtTheCathedralPower.OnElementApplied");
        Assert.True(assembly >= 0, string.Join(", ", note));
        // After the credit, so its Oath and Dawn Wind's March land first.
        Assert.True(note.IndexOf("VarkaOath.Gain") < assembly, string.Join(", ", note));
        Assert.DoesNotContain("AssemblyAtTheCathedralPower.OnElementApplied",
                              Il.Calls(Il.Method("VarkaOath", "EndPlay")));
        // Every application reaches that site: an element hit, a damage-less
        // apply, and an Attack card's own hit.
        Assert.Contains("VarkaOath.NoteApplication", Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("VarkaOath.NoteApplication", Il.Calls(Il.Method("ElementalHit", "ApplyOnly")));
        // Its own hit is element-less, so it can never pay itself.
        var hit = Il.Calls(Il.Method("AssemblyAtTheCathedralPower", "OnElementApplied"));
        Assert.Contains("ElementalHit.DealUnelemented", hit);
        Assert.DoesNotContain("ElementalHit.Deal", hit);
    }

    [Fact]
    public void Assembly_is_two_and_three_upgraded_on_the_same_card()
    {
        var card = new ProtoVkAssemblyAtTheCathedral();
        Assert.Equal(2m, Var(card, "PowerAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkAssemblyAtTheCathedral>(), "PowerAmount"));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardType.Power, card.Type);
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardRarity.Uncommon, card.Rarity);
        Assert.StartsWith("Whenever you apply an element, deal ", Face(card));
    }

    // ---- pick 2 (b): the printed "Knight." line ------------------------------

    /// <summary>Does this card's <c>CanonicalKeywords</c> load
    /// <c>KleeKeywords.Knight</c>? A static field read is <c>ldsfld</c>, which
    /// <c>Il.Calls</c> cannot see; the same byte scan the badge tests use.
    /// </summary>
    private static bool DeclaresKnight(Type card)
    {
        var getter = card.GetProperty("CanonicalKeywords", HeadlessGame.All)?.GetGetMethod();
        if (getter == null || getter.DeclaringType != card) return false;
        var body = getter.GetMethodBody()!.GetILAsByteArray()!;
        for (var i = 0; i < body.Length - 4; i++)
        {
            if (body[i] != 0x7E) continue;              // ldsfld
            try
            {
                var field = card.Module.ResolveField(BitConverter.ToInt32(body, i + 1));
                if (field?.DeclaringType == typeof(KleeKeywords) && field.Name == "Knight")
                {
                    return true;
                }
            }
            catch
            {
                // Not a field token. Expected while byte-scanning.
            }
        }
        return false;
    }

    [Fact]
    public void Every_knight_and_only_a_knight_declares_the_keyword()
    {
        var cards = typeof(VarkaRules).Assembly.GetTypes()
            .Where(t => t.Namespace == typeof(ProtoVkWindboundExecution).Namespace
                        && typeof(CardModel).IsAssignableFrom(t) && !t.IsAbstract
                        && t.GetConstructor(Type.EmptyTypes) != null)
            .ToList();
        var knights = cards.Where(t =>
            VarkaRules.IsKnight((CardModel)Activator.CreateInstance(t)!)).ToList();
        // The 17: thirteen pool Knights and the four starter-only ones.
        Assert.Equal(17, knights.Count);
        Assert.All(knights, t => Assert.True(DeclaresKnight(t), t.Name));
        Assert.All(cards.Except(knights), t => Assert.False(DeclaresKnight(t), t.Name));
        // Jean is a Varka card titled with an em dash, not a Knight; the
        // shared Companion in his fourth slot is not one either.
        Assert.DoesNotContain(typeof(ProtoVkJeanDandelionBreeze), knights);
        Assert.DoesNotContain(typeof(ProtoMcAmberExplosivePuppet), knights);
    }

    [Fact]
    public void The_keyword_prints_first_and_shares_the_knight_tip()
    {
        var field = typeof(KleeKeywords).GetField("Knight")!;
        // `Before`: the base game's before-description rail, which prints
        // "[gold]Knight[/gold]." at the top of the rules box.
        Assert.Equal(AutoKeywordPosition.Before,
                     field.GetCustomAttribute<KeywordPropertiesAttribute>()!.Position);
        // The key BaseLib builds ("KLEEMOD-" + name) is the arm tip's key, so
        // the printed line and the golded word hover one tip.
        var name = field.GetCustomAttribute<CustomEnumAttribute>()!.Name!;
        Assert.Equal(ArmKeywordTips.KnightKey, "KLEEMOD-" + name.ToUpperInvariant());
        var registered = Il.Strings(typeof(global::KleeMod.KleeMod)
            .GetMethod("InjectLocStrings", HeadlessGame.All)!);
        Assert.Contains(ArmKeywordTips.KnightKey + ".title", registered);
        Assert.Contains(ArmKeywordTips.KnightKey + ".description", registered);
        Assert.Equal("One of Varka's Companions. "
                   + "Playing one makes its element your current element.",
                     (string)typeof(ArmKeywordTips).GetField("KnightTipText",
                         HeadlessGame.All)!.GetRawConstantValue()!);
    }

    [Fact]
    public void No_knight_face_types_the_word_itself()
    {
        // The line is the keyword's; a row that hand-typed "Knight." would
        // print it twice.
        foreach (var card in VarkaKnights())
        {
            Assert.False(Face(card).StartsWith("Knight", StringComparison.Ordinal),
                         card.GetType().Name);
        }
    }

    private static IEnumerable<CardModel> VarkaKnights() =>
        typeof(VarkaRules).Assembly.GetTypes()
            .Where(t => t.Name.StartsWith("ProtoVk", StringComparison.Ordinal)
                        && typeof(CardModel).IsAssignableFrom(t)
                        && t.GetConstructor(Type.EmptyTypes) != null)
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .Where(VarkaRules.IsKnight);

    // ---- pick 2 (c): the Knight language pass --------------------------------

    [Fact]
    public void Every_varka_face_that_names_a_knight_golds_the_bare_word()
    {
        var faces = typeof(VarkaRules).Assembly.GetTypes()
            .Where(t => t.Name.StartsWith("ProtoVk", StringComparison.Ordinal)
                        && typeof(CardModel).IsAssignableFrom(t)
                        && t.GetConstructor(Type.EmptyTypes) != null)
            .Select(t => (t.Name, Face((CardModel)Activator.CreateInstance(t)!)))
            .ToList();
        foreach (var (name, face) in faces)
        {
            var plain = face.Replace("[gold]Knight[/gold]", "")
                            .Replace("[gold]Knights[/gold]", "");
            Assert.DoesNotContain("Knight", plain);
            Assert.DoesNotContain("Knight card", face);
        }
    }

    // ---- pick 4: Neuvillette's Rare ----------------------------------------

    [Fact]
    public void Neuvillette_applies_hydro_at_the_start_of_the_turn()
    {
        var hook = typeof(AncientSeaAuthorityPower).GetMethod("AfterPlayerTurnStart",
                                                              HeadlessGame.All)!;
        Assert.Equal(typeof(AncientSeaAuthorityPower), hook.DeclaringType);
        Assert.Contains("AncientSeaAuthorityPower.ApplyHydro", Il.Calls(hook));
        var apply = Il.Calls(Il.Method("AncientSeaAuthorityPower", "ApplyHydro"));
        Assert.Contains("ElementalHit.ApplyOnly", apply);
        var card = new ProtoMfNeuvilletteAncientSeaAuthority();
        Assert.Equal("At the start of your turn, apply [gold]Hydro[/gold] to a "
                   + "random enemy. Elemental auras you apply last 1 extra turn.",
                     Face(card));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardRarity.Rare, card.Rarity);
    }
}
