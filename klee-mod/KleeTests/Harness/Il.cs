using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace KleeMod.Tests.Harness;

/// <summary>
/// Which methods does this method call?
///
/// WHY THIS EXISTS. Some parity facts are about ORDER between two engine
/// hooks, not about a value -- audit finding M1 is exactly that: the mod
/// RECORDS a Supporting Cast draw in <c>BeforeCardPlayed</c> and RESOLVES it in
/// <c>AfterCardPlayed</c>, so the triggering card resolves against a hand that
/// does not yet contain the drawn cards. Reproducing that end to end would need
/// a live combat, which is outside the headless boundary. Reading the two
/// hooks' call sets is not: it pins the fact that the record and the resolve
/// sit in different hooks, which IS the divergence.
///
/// This is a structural pin and is labelled as one wherever it is used. It
/// cannot see a reordering INSIDE a single method.
///
/// Async methods compile to a state machine, so the real call sites live in
/// the generated <c>MoveNext</c>; both are walked.
/// </summary>
internal static class Il
{
    /// <summary>`Type.Method` for every call/callvirt/newobj in the body.</summary>
    internal static IReadOnlyCollection<string> Calls(MethodBase method)
    {
        var found = new HashSet<string>(StringComparer.Ordinal);
        foreach (var body in Bodies(method))
        {
            var il = body.GetMethodBody()?.GetILAsByteArray();
            if (il == null) continue;

            for (var i = 0; i < il.Length - 4; i++)
            {
                // 0x28 call, 0x6F callvirt, 0x73 newobj. Scanning raw bytes
                // rather than decoding the full instruction stream can in
                // principle mistake an operand for an opcode; a FALSE POSITIVE
                // here would have to resolve to a real method token AND match
                // the name a test asserts on, and the assertions below are all
                // "this hook does call X", so a stray match is not a way for a
                // real regression to pass.
                //
                // ldftn (0xFE 0x06) is included because a method GROUP passed
                // to LINQ -- `.Where(SpotlightSystem.IsSpotlighted)`, which is
                // exactly how Encore Performance filters the hand -- compiles
                // to a cached delegate, not to a call.
                var operandAt = i + 1;
                if (il[i] == 0xFE && i + 1 < il.Length && il[i + 1] == 0x06)
                {
                    operandAt = i + 2;
                }
                else if (il[i] != 0x28 && il[i] != 0x6F && il[i] != 0x73)
                {
                    continue;
                }

                if (operandAt + 4 > il.Length) continue;
                var token = BitConverter.ToInt32(il, operandAt);
                try
                {
                    var target = body.Module.ResolveMethod(
                        token,
                        body.DeclaringType?.GetGenericArguments(),
                        null);
                    if (target != null)
                    {
                        found.Add($"{target.DeclaringType?.Name}.{target.Name}");
                    }
                }
                catch
                {
                    // Not a method token. Expected while byte-scanning.
                }
            }
        }

        return found;
    }

    /// <summary>
    /// The same scan as <see cref="Calls"/>, but ORDERED and with duplicates
    /// kept, and naming a generic method's type argument.
    ///
    /// `Calls` returns a set of `Type.Method`, which answers "does this method
    /// call X" and cannot answer "how many times, and with what". Klee's
    /// starting deck is ten `ModelDb.Card&lt;T&gt;()` calls and the fact worth
    /// pinning about it is a COUNT -- ONE Ka-boom! of four becomes the Spark
    /// sink, not all four -- so this exists beside the set rather than
    /// replacing it.
    ///
    /// THE FALSE-POSITIVE CAVEAT IS SHARPER HERE and is why this is separate:
    /// `Calls`' assertions are all "does call X", where a stray byte that
    /// happens to resolve cannot make a real regression pass. A COUNT can be
    /// moved by one, so an assertion on this should be a count of a call the
    /// method demonstrably makes, never a count of zero standing in for
    /// "never".
    /// </summary>
    internal static IReadOnlyList<string> CallSequence(MethodBase method)
    {
        var found = new List<string>();
        foreach (var body in Bodies(method))
        {
            var il = body.GetMethodBody()?.GetILAsByteArray();
            if (il == null) continue;

            for (var i = 0; i < il.Length - 4; i++)
            {
                if (il[i] != 0x28 && il[i] != 0x6F && il[i] != 0x73) continue;
                if (i + 5 > il.Length) continue;
                var token = BitConverter.ToInt32(il, i + 1);
                try
                {
                    var target = body.Module.ResolveMethod(
                        token, body.DeclaringType?.GetGenericArguments(), null);
                    if (target == null) continue;
                    var args = target.IsGenericMethod
                        ? "<" + string.Join(",", target.GetGenericArguments()
                                                       .Select(a => a.Name)) + ">"
                        : string.Empty;
                    found.Add($"{target.DeclaringType?.Name}.{target.Name}{args}");
                }
                catch
                {
                    // Not a method token. Expected while byte-scanning.
                }
            }
        }

        return found;
    }

    /// <summary>Every string literal (`ldstr`) in the body.
    ///
    /// Used to pin a hand-rolled serializer's KEY NAMES without running it:
    /// PlayTelemetry.ToJson reaches Godot's ProjectSettings through its intent
    /// lookup, so calling it takes the process down (README, the headless
    /// boundary). The key names are the shared schema, and they are literals
    /// in that method, so this reads exactly the thing the schema promise is
    /// about.</summary>
    internal static IReadOnlyCollection<string> Strings(MethodBase method)
    {
        var found = new HashSet<string>(StringComparer.Ordinal);
        foreach (var body in Bodies(method))
        {
            var il = body.GetMethodBody()?.GetILAsByteArray();
            if (il == null) continue;

            for (var i = 0; i < il.Length - 4; i++)
            {
                if (il[i] != 0x72) continue; // ldstr
                try
                {
                    found.Add(body.Module.ResolveString(BitConverter.ToInt32(il, i + 1)));
                }
                catch
                {
                    // Not a string token. Expected while byte-scanning.
                }
            }
        }

        return found;
    }

    private static IEnumerable<MethodBase> Bodies(MethodBase method)
    {
        yield return method;

        // An async method compiles to a state machine, and so does an ITERATOR
        // (`yield return`). In both cases the declared body is a stub that news
        // up the machine and the real call sites live in the generated
        // MoveNext. The iterator arm is what EB-130's death-teardown pin needs:
        // it reads the game's own hook-listener iterator, whose declared body
        // calls nothing but the state machine's constructor.
        var machine =
            method.GetCustomAttribute<AsyncStateMachineAttribute>()?.StateMachineType
            ?? method.GetCustomAttribute<IteratorStateMachineAttribute>()?.StateMachineType;
        if (machine == null) yield break;

        var moveNext = machine.GetMethod("MoveNext", HeadlessGame.All);
        if (moveNext != null) yield return moveNext;
    }

    internal static MethodBase Method(string typeName, string methodName)
    {
        var type = typeof(global::KleeMod.Powers.FurinaResources).Assembly
            .GetTypes()
            .FirstOrDefault(t => t.Name == typeName)
            ?? throw new InvalidOperationException($"no type named {typeName} in klee.dll");
        return type.GetMethod(methodName, HeadlessGame.All)
            ?? throw new InvalidOperationException($"{typeName} has no method {methodName}");
    }
}
