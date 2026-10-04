using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE'S CARDS ON ANYONE, the way the base game treats the Regent's Stars.
///
/// [USER], 2026-10-04: "Klee's cards need to work universally like Regent's --
/// the rest can wait." Every card of Klee's kit (her pool, her starter's own
/// two, her Ancients, her multiplayer tier and the cards those generate; not
/// the Companions) is swept here as if an IRONCLAD held it.
///
/// WHAT IS REAL. The face, the card's numbers and its playability gate run for
/// real on an Ironclad-owned copy and are compared with the same card held by
/// Klee on the same bank: a card that works like the Regent's answers the same
/// for both.
///
/// WHAT IS STRUCTURAL, and labelled. Playing a card (`OnPlay`) needs a live
/// combat, which is outside the headless boundary (README). So the play is
/// read as its call closure instead: every method the card's own code can
/// reach inside this mod, including the powers it applies and the objects it
/// builds, is walked, and no Klee identity test may sit on that closure
/// except at the named sites below, each of which is Klee-only by design.
/// </summary>
public class KleeOffCharacterSweepTests
{
    private static readonly Assembly Mod = typeof(SparkPower).Assembly;

    /// <summary>The kit: every generated `ProtoKo` card that is not a
    /// Companion, plus her two Ancients.</summary>
    internal static IReadOnlyList<Type> KitCards() =>
        Mod.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && t.Name.StartsWith("ProtoKo", StringComparison.Ordinal)
                        && typeof(CardModel).IsAssignableFrom(t)
                        && !t.IsAbstract
                        && !typeof(ICompanionCard).IsAssignableFrom(t))
            .Concat(new[] { typeof(JumpyDumptyMkOmega), typeof(AlicesMasterpiece) })
            .OrderBy(t => t.Name)
            .ToList();

    [Fact]
    public void The_sweep_covers_the_whole_kit()
    {
        var kit = KitCards().Select(t => t.Name).ToList();
        // A filter that silently matched nothing would pass every test below.
        Assert.True(kit.Count >= 80, $"only {kit.Count} kit cards found");
        Assert.Contains(nameof(ProtoKoKapow), kit);
        Assert.Contains(nameof(ProtoKoSparksForEveryone), kit);
        Assert.Contains(nameof(AlicesMasterpiece), kit);
    }

    // --- the play: no Klee identity on any card's closure -----------------

    /// <summary>
    /// The methods that MAY test for Klee, and why each is Klee-only by
    /// design rather than a card reading Klee-only state.
    /// </summary>
    private static readonly Dictionary<string, string> ByDesign = new()
    {
        // The counter by the energy orb shows from 0 for Klee, as the
        // Regent's does; anyone else's appears on their first Spark.
        ["SparkGauge.AppliesTo"] = "display: Klee's counter is always shown",
        // An Attack that declares no element takes its dealer's; every Klee
        // Attack declares Pyro (pinned below), so no Klee card reaches it.
        ["CatalystCadence.NativeElementOf"] = "element of a card that names none",
        // Random Companions are drawn from the OWNER's personal pool; an
        // Ironclad gets the universal ones.
        ["CompanionPool.CharacterId"] = "companion personal pool of the owner",
        ["CompanionPool.HomeNation"] = "companion nation of the owner",
        // Tip text: the Oz word (a Companion's) and the Spark word's opening
        // bank, which is Klee's kit rule and not her cards'.
        ["ArmKeywordTips.KleesRuleBelongsHere"] = "tip: Oz is Klee's Power",
        ["ArmKeywordTips.KleeAmongTheRunsPlayers"] = "tip: run has a Klee",
        ["ArmKeywordTips.KleeOpensWithASpark"] = "tip: the opening Spark is Klee's",
    };

    [Fact]
    public void No_kit_card_reads_klee_identity_when_played()
    {
        var findings = new List<string>();
        foreach (var card in KitCards())
        {
            foreach (var hit in IdentityReads(card))
            {
                if (!ByDesign.ContainsKey(hit.Site)) findings.Add(hit.Site + " via " + hit.Path);
            }
        }

        Assert.True(findings.Count == 0,
            "Klee identity read on a kit card's closure:\n  "
            + string.Join("\n  ", findings.Distinct()));
    }

    [Fact]
    public void The_closure_walk_bites()
    {
        // The walk must find the one Klee test every Spark card reaches (the
        // counter's scope), or the sweep above is reading nothing.
        var hits = IdentityReads(typeof(ProtoKoDigIn)).Select(h => h.Site);
        Assert.Contains("SparkGauge.AppliesTo", hits);
    }

    [Fact]
    public void Every_klee_attack_names_its_own_element()
    {
        // Why `CatalystCadence.NativeElementOf` is on the by-design list: an
        // Attack that declares its element never asks the dealer, so Klee's
        // Pyro comes with her card to anyone's hand.
        foreach (var type in KitCards())
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            if (card.Type != CardType.Attack) continue;
            Assert.True(card is global::KleeMod.Elements.IElementalCard,
                        $"{type.Name} is an Attack with no element of its own");
        }
    }

    private readonly record struct Hit(string Site, string Path);

    private static IEnumerable<Hit> IdentityReads(Type card)
    {
        var seen = new HashSet<MethodBase>();
        var seenTypes = new HashSet<Type> { card };
        var queue = new Queue<(MethodBase Method, string Path, int Depth)>();
        foreach (var m in card.GetMethods(HeadlessGame.All | BindingFlags.DeclaredOnly))
        {
            queue.Enqueue((m, card.Name + "." + m.Name, 0));
        }

        while (queue.Count > 0)
        {
            var (method, path, depth) = queue.Dequeue();
            if (!seen.Add(method)) continue;

            if (Il.TypesTested(method).Any(t => t == typeof(IKleeCharacter)
                                              || t == typeof(global::KleeMod.Klee)))
            {
                yield return new Hit(SiteOf(method), path);
            }

            if (depth >= 12) continue;
            foreach (var callee in Il.Callees(method))
            {
                // The objects a play builds and the powers it applies
                // (`PowerCmd.Apply<T>`) carry their own hooks: walk them whole.
                var built = new List<Type>();
                if (callee.IsGenericMethod) built.AddRange(callee.GetGenericArguments());
                if (callee.IsConstructor && callee.DeclaringType != null)
                {
                    built.Add(callee.DeclaringType);
                }
                foreach (var type in built.Where(t => t.Assembly == Mod && seenTypes.Add(t)))
                {
                    foreach (var m in type.GetMethods(HeadlessGame.All | BindingFlags.DeclaredOnly))
                    {
                        queue.Enqueue((m, path + " >> " + type.Name + "." + m.Name, depth + 1));
                    }
                }

                if (callee.DeclaringType?.Assembly != Mod) continue;
                queue.Enqueue((callee,
                    path + " > " + callee.DeclaringType!.Name + "." + callee.Name,
                    depth + 1));
            }
        }
    }

    /// <summary>`Type.Method` of the site. A lambda or a state machine is
    /// named for the method it came from.</summary>
    private static string SiteOf(MethodBase method)
    {
        var type = method.DeclaringType!;
        var name = method.Name;
        var lambda = Regex.Match(name, "^<([^>]+)>");
        if (lambda.Success) name = lambda.Groups[1].Value;
        while (type.Name.Contains('<') && type.DeclaringType != null)
        {
            var machine = Regex.Match(type.Name, "^<([^>]+)>");
            if (machine.Success && !lambda.Success) name = machine.Groups[1].Value;
            type = type.DeclaringType;
        }
        return type.Name + "." + name;
    }

    // --- the face: every variable resolves, and reads the same ------------

    /// <summary>Format names the game supplies itself rather than a card's
    /// DynamicVars.</summary>
    private static readonly HashSet<string> BuiltIns = new(StringComparer.Ordinal)
    {
        "IfUpgraded", "energyPrefix", "singleStarIcon", "InCombat",
    };

    private static CardModel HeldBy(Type type, Seat seat)
    {
        var card = (CardModel)Activator.CreateInstance(type)!;
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    [Fact]
    public void Every_face_resolves_and_reads_the_same_on_an_ironclad()
    {
        var problems = new List<string>();
        foreach (var type in KitCards())
        {
            var ironclad = HeldBy(type, Seat.Of(new Ironclad()).WithPower<SparkPower>(3));
            var klee = HeldBy(type, Seat.Klee().WithPower<SparkPower>(3));

            var keys = new HashSet<string>(ironclad.DynamicVars.Keys, StringComparer.Ordinal);
            foreach (var (entry, text) in ((CustomCardModel)ironclad).Localization!)
            {
                foreach (Match m in Regex.Matches(text, @"\{([A-Za-z_][A-Za-z0-9_]*)"))
                {
                    var name = m.Groups[1].Value;
                    if (!keys.Contains(name) && !BuiltIns.Contains(name))
                    {
                        problems.Add($"{type.Name} {entry}: {{{name}}} is not a variable");
                    }
                }
            }

            foreach (var key in keys)
            {
                string onIronclad, onKlee;
                try
                {
                    onIronclad = ironclad.DynamicVars[key].ToString()!;
                    onKlee = klee.DynamicVars[key].ToString()!;
                }
                catch (Exception e)
                {
                    problems.Add($"{type.Name} {{{key}}} threw {e.GetType().Name}");
                    continue;
                }
                if (onIronclad != onKlee)
                {
                    problems.Add($"{type.Name} {{{key}}}: Klee {onKlee}, Ironclad {onIronclad}");
                }
            }
        }

        Assert.True(problems.Count == 0, string.Join("\n", problems));
    }

    // --- the price: any owner's bank pays it ------------------------------

    [Fact]
    public void Every_playability_gate_answers_the_same_for_an_ironclad()
    {
        var gate = typeof(CardModel).GetProperty("IsPlayable", HeadlessGame.All)!;
        var problems = new List<string>();
        var priced = 0;
        foreach (var type in KitCards())
        {
            if (type.GetProperty("IsPlayable",
                    HeadlessGame.All | BindingFlags.DeclaredOnly) == null)
            {
                continue;
            }
            foreach (var bank in new[] { 0, 1, 2, 5, 10 })
            {
                var onIronclad = Ask(gate, HeldBy(type, Bank(Seat.Of(new Ironclad()), bank)));
                var onKlee = Ask(gate, HeldBy(type, Bank(Seat.Klee(), bank)));
                if (onIronclad != onKlee)
                {
                    problems.Add($"{type.Name} at {bank} Sparks: Klee {onKlee}, Ironclad {onIronclad}");
                }
            }

            if (SparkCost.PrintedPriceOf(HeldBy(type, Seat.Klee())) <= 0) continue;
            priced++;
            // The Regent's rule: no bank, no play, whoever holds it.
            Assert.Equal("False", Ask(gate, HeldBy(type, Seat.Of(new Ironclad()))));
        }

        Assert.True(priced >= 10, $"only {priced} Spark-priced kit cards found");
        Assert.True(problems.Count == 0, string.Join("\n", problems));
    }

    private static Seat Bank(Seat seat, int sparks) =>
        sparks > 0 ? seat.WithPower<SparkPower>(sparks) : seat;

    private static string Ask(PropertyInfo gate, CardModel card)
    {
        try
        {
            return gate.GetValue(card)!.ToString()!;
        }
        catch (TargetInvocationException e)
        {
            return "throws " + e.InnerException!.GetType().Name;
        }
    }

    // --- the tip: the Spark word tells a non-Klee only what is true -------

    [Fact]
    public void The_spark_tip_drops_klees_opening_bank_for_anyone_else()
    {
        var onIronclad = ArmKeywordTips.SparkBody(ArmKeywordTips.KleeOpensWithASpark(
            HeldBy(typeof(ProtoKoDigIn), Seat.Of(new Ironclad()))));
        var onKlee = ArmKeywordTips.SparkBody(ArmKeywordTips.KleeOpensWithASpark(
            HeldBy(typeof(ProtoKoDigIn), Seat.Klee())));

        Assert.DoesNotContain("Start each combat", onIronclad);
        Assert.Contains("Start each combat with " + KleeOverhaulLaw.OpeningSpark, onKlee);
        Assert.Contains("Some cards cost [gold]Sparks[/gold] instead of Energy", onIronclad);
        Assert.Contains("Gone after combat.", onIronclad);
    }
}
