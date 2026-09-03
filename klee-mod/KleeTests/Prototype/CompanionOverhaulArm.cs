using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The xunit collection every test that READS OR MOVES
/// <c>CompanionOverhaul.Enabled</c> belongs to.
///
/// <see cref="KleeOverhaulArm"/>'s reason, second arm: the flag is one static
/// for the whole process -- settable on purpose, so a single build can pin both
/// sides of the switch -- and xunit parallelises across collections, so a test
/// that turns the arm ON and <c>CompanionOverhaulTests.The_arm_ships_off</c>
/// would otherwise be free to run at the same time and disagree at random. One
/// collection makes them queue.
/// </summary>
[CollectionDefinition(Name)]
public sealed class CompanionOverhaulArm
{
    public const string Name = "CompanionOverhaulArm";
}
