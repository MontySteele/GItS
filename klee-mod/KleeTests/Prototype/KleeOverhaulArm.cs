using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The xunit collection every test that READS OR MOVES <c>KleeOverhaul.Enabled</c>
/// belongs to.
///
/// The arm is one static for the whole process -- settable on purpose, so a
/// single build can pin both sides of the switch (KleeCode `KleeOverhaul`'s own
/// doc). xunit parallelises across collections, so a test that flips it and a
/// test that asserts it ships off would otherwise be free to run at the same
/// time and disagree at random. One collection makes them queue.
/// </summary>
[CollectionDefinition(Name)]
public sealed class KleeOverhaulArm
{
    public const string Name = "KleeOverhaulArm";
}
