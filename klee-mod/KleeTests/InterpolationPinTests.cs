using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Relics;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (b): pure logic that needs no combat -- the localization builders.
///
/// WHY THIS IS WORTH A TEST. The tooltip text is the one projection of the
/// balance constants that `lint_constant_parity` structurally cannot see: it
/// compares named consts between the engines and has no opinion about prose.
/// Both of these descriptions were literal strings once, and both went stale
/// against a repricing. M24's own note records the consequence: signing the
/// six salon numbers is a ONE-file edit only because the power interpolates
/// SalonConstants instead of restating it.
///
/// The power models are allocated uninitialised -- their real constructors
/// register with the game's model tables, and these properties are pure
/// string builders that read nothing off the instance.
/// </summary>
public class InterpolationPinTests
{
    private static T Bare<T>() => (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    private static string Loc<T>(T model, string key) where T : notnull
    {
        var rows = (System.Collections.Generic.List<(string, string)>)
            model.GetType()
                .GetProperty("Localization", Harness.HeadlessGame.All)!
                .GetValue(model)!;
        return rows.First(r => r.Item1 == key).Item2;
    }

}
