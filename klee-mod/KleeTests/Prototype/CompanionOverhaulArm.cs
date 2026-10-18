using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// An xunit collection left from the retired <c>CompanionOverhaul.Enabled</c>
/// switch (removed 2026-10-01). It now only keeps its members serial.
/// </summary>
[CollectionDefinition(Name)]
public sealed class CompanionOverhaulArm
{
    public const string Name = "CompanionOverhaulArm";
}
