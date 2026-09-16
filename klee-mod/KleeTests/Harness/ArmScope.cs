using System;

namespace KleeMod.Tests.Harness;

/// <summary>
/// `EB-781`. A SCOPE THAT PUTS ONE ARM BACK WHERE A SHIPPED PIN CAN SEE IT.
///
/// THE FIND. `dotnet test -p:PrototypeCards=true -p:FurinaStage=true` stood at
/// nine failures on main -- four in <c>CoopSeamTests</c>, three in
/// <c>DerivationPinTests</c>, one in <c>MeterCostBadgeTests</c> and one in
/// <c>SalonVerbTests</c>. Every one of the nine is a SHIPPED pin: it mints
/// Fanfare or Encore on a Furina seat and asserts the shipped number that
/// comes back. `EB-745` retires exactly those two meters under the Stage --
/// <c>FurinaResources.StageRetiresTheShippedMeters</c> returns early at each
/// MINT -- so under the arm the mint is a no-op, the meter reads 0 and the
/// literal in the pin is wrong. The guard is right and the pins are right; what
/// was missing is a statement of WHICH WORLD each pin is about.
///
/// WHY A SCOPE AND NOT AN <c>#if</c>. An <c>#if FURINA_STAGE</c> would delete
/// the nine pins from the arm's configuration, and the shipped meter
/// arithmetic is not a thing the arm changes -- it is a thing the arm stops
/// REACHING. Deleting the pin would lose the shipped fact in the very
/// configuration a dev spends their day in. So the pin keeps running and the
/// scope says, for the length of one test method, that the seat it is about is
/// a seat with no stage.
///
/// WHY NOT A CLASS-LEVEL CONSTRUCTOR, which is what the arm's OWN suites use
/// (<c>FurinaStageRoundTwoTests</c> and its siblings turn the arm ON for a
/// whole class): the four classes here are shipped-surface suites and most of
/// their pins never touch a meter. A class-wide flip would quietly put dozens
/// of unrelated pins in a world the class never named.
///
/// SAFE BECAUSE THE ASSEMBLY IS SERIAL. <c>HeadlessGame.cs</c> carries
/// <c>[assembly: CollectionBehavior(DisableTestParallelization = true)]</c>, so
/// a static flipped inside one test cannot be read by another; the arm's own
/// suites already rely on exactly that.
///
/// A NO-OP WITHOUT THE QUARANTINE. <c>FurinaStage</c> lives under
/// <c>Powers/Prototype/</c> and is <c>Compile Remove</c>d from a release build,
/// so in that configuration there is no arm to move and the scope holds
/// nothing.
/// </summary>
public sealed class ArmScope : IDisposable
{
    private readonly Action _restore;

    private ArmScope(Action restore) => _restore = restore;

    /// <summary>
    /// The Furina seat in this test has NO STAGE, so the shipped Fanfare and
    /// Encore meters mint as they ship (`EB-745`'s guard is off). Restores the
    /// previous value on dispose, whatever the build's default was.
    /// </summary>
    public static ArmScope ShippedMetersLive()
    {
#if PROTOTYPE_CARDS
        var was = global::KleeMod.Powers.FurinaStage.Enabled;
        global::KleeMod.Powers.FurinaStage.Enabled = false;
        return new ArmScope(() => global::KleeMod.Powers.FurinaStage.Enabled = was);
#else
        return new ArmScope(() => { });
#endif
    }

    public void Dispose() => _restore();
}
