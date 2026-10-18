using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE OFF-CHARACTER SWEEP'S SHARED HALF (the off-character fix, 2026-10-18):
/// the closure walk and the face and gate comparisons
/// <see cref="KleeOffCharacterSweepTests"/> first wrote for Klee, made
/// generic over a kit so Varka's and Furina's sweeps ask the same questions.
///
/// THE WALK. Playing a card needs a live combat, outside the headless
/// boundary, so a play is read as its call closure: every method the card's
/// own code can reach inside this mod, the powers it applies and the objects
/// it builds included. An IDENTITY READ is a site that tests for the
/// character's type, or calls the character's identity predicate; the site
/// is named for the method it sits in (a lambda or a state machine for the
/// method it came from).
/// </summary>
internal static class OffCharacterSweep
{
    internal static readonly Assembly Mod = typeof(SparkPower).Assembly;

    internal readonly record struct Hit(string Site, string Path);

    /// <summary>Every generated card whose class name starts with
    /// <paramref name="prefix"/>, plus <paramref name="extra"/>.</summary>
    internal static IReadOnlyList<Type> Cards(string prefix, params Type[] extra) =>
        Mod.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && t.Name.StartsWith(prefix, StringComparison.Ordinal)
                        && typeof(CardModel).IsAssignableFrom(t)
                        && !t.IsAbstract
                        // A modal card's two options are its own models, not
                        // cards anyone holds.
                        && !Regex.IsMatch(t.Name, "Mode[A-Z]$"))
            .Concat(extra)
            .OrderBy(t => t.Name)
            .ToList();

    /// <summary>The identity reads on <paramref name="card"/>'s closure: a
    /// method that tests for one of <paramref name="types"/>, or calls
    /// <paramref name="predicate"/>.</summary>
    internal static IEnumerable<Hit> IdentityReads(
        Type card, IReadOnlyCollection<Type> types, MethodBase predicate)
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

            var callees = Il.Callees(method);
            if (Il.TypesTested(method).Any(types.Contains)
                || callees.Any(c => c == predicate))
            {
                yield return new Hit(SiteOf(method), path);
            }

            if (depth >= 12) continue;
            foreach (var callee in callees)
            {
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

    /// <summary>`Type.Method` of the site.</summary>
    internal static string SiteOf(MethodBase method)
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

    /// <summary>The sites on any kit card's closure not named in
    /// <paramref name="byDesign"/>.</summary>
    internal static List<string> Unexpected(
        IEnumerable<Type> kit, IReadOnlyCollection<Type> types,
        MethodBase predicate, IReadOnlyDictionary<string, string> byDesign)
    {
        var findings = new List<string>();
        foreach (var card in kit)
        {
            foreach (var hit in IdentityReads(card, types, predicate))
            {
                if (!byDesign.ContainsKey(hit.Site)) findings.Add(hit.Site + " via " + hit.Path);
            }
        }
        return findings.Distinct().ToList();
    }

    // --- the face and the gate --------------------------------------------

    internal static CardModel HeldBy(Type type, Seat seat)
    {
        var card = (CardModel)Activator.CreateInstance(type)!;
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>Every face variable of every card resolves on
    /// <paramref name="other"/>'s copy and reads as on
    /// <paramref name="owner"/>'s.</summary>
    internal static List<string> FaceProblems(
        IEnumerable<Type> kit, Func<Seat> other, Func<Seat> owner)
    {
        var problems = new List<string>();
        foreach (var type in kit)
        {
            var offCard = HeldBy(type, other());
            var onCard = HeldBy(type, owner());

            // The kit-word tokens ({StageDrainLine}) are not DynamicVars, so
            // only the variables are compared here; Klee's sweep keeps its
            // own every-token check.
            var keys = new HashSet<string>(offCard.DynamicVars.Keys, StringComparer.Ordinal);
            foreach (var key in keys)
            {
                string off, on;
                try
                {
                    off = offCard.DynamicVars[key].ToString()!;
                    on = onCard.DynamicVars[key].ToString()!;
                }
                catch (Exception e)
                {
                    problems.Add($"{type.Name} {{{key}}} threw {e.GetType().Name}");
                    continue;
                }
                if (off != on) problems.Add($"{type.Name} {{{key}}}: owner {on}, Ironclad {off}");
            }
        }
        return problems;
    }

    internal static readonly PropertyInfo Gate =
        typeof(CardModel).GetProperty("IsPlayable", HeadlessGame.All)!;

    /// <summary>Does <paramref name="type"/> declare its own gate?</summary>
    internal static bool Gated(Type type) =>
        type.GetProperty("IsPlayable", HeadlessGame.All | BindingFlags.DeclaredOnly) != null;

    internal static string Ask(CardModel card)
    {
        try
        {
            return Gate.GetValue(card)!.ToString()!;
        }
        catch (TargetInvocationException e)
        {
            return "throws " + e.InnerException!.GetType().Name;
        }
    }
}
