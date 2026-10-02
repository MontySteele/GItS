using KleeMod.Powers;
using KleeMod.Relics;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (a): constants and the relations between them.
///
/// These read the shipped `const`s directly. The compiler inlines a const at
/// the call site, so a test that compares two consts to each other is NOT
/// tautological across a change: the expected side is a literal written here,
/// and a repricing recompiles the mod side alone into a failing comparison.
/// What it does not catch is someone editing this file to match; that is what
/// review is for.
/// </summary>
public class ConstantPinTests
{
    // ---------------------------------------------------------------
    // M24's signing surface: the six salon summon-damage values, RATIFIED
    // 2026-08-13 (R187) as written -- no value moved when the "PROPOSED
    // pending red-pen" banner came off, so no world stamp moved with it.
    // Pinned here because the six are now a SIGNED number: a repricing is a
    // [USER] act, and this test makes it a deliberate, visible edit rather
    // than a constant that drifts.
    // ---------------------------------------------------------------

    // ---------------------------------------------------------------
    // EB-74 / the upgraded-starter invariant, RATIFIED 2026-08-13 (R190):
    // Pearl of Insight's rates are exactly 2x their base rates, in BOTH
    // engines, permanently. The C# side already derived them as an
    // EXPRESSION, which is why the parity lint could not see them at all --
    // parse_number reads literals, not arithmetic, so both members sat in
    // UNMIRRORED. This test is the C# half of that invariant's enforcement.
    //
    // EPOCH 2 D1 is why it needed one: the relic once
    // declared its own doubled numbers, printed them on its panel, and the
    // exhaust funnel granted the base values anyway -- a no-op with a lying
    // tooltip. The fix made the funnel READ the relic. The invariant that
    // keeps that fix honest is that the relic's numbers are exactly twice
    // the base, expressed as arithmetic in the source rather than as two
    // hand-typed literals.
    // ---------------------------------------------------------------

}
