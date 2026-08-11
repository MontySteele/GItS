namespace KleeMod.Cards;

/// <summary>
/// A card whose power application is FLOOR-NOT-CLAMP: it raises the power
/// toward <see cref="NeverReducingCap"/> and never lowers a higher standing
/// stack (sheet `never_reduces: true`; EB-26 D2, ruled 2026-08-10 option (d)).
///
/// The mode is a property of the SHEET ROW, not of the power -- two rows can
/// apply the same power with different caps and different modes. The mod's
/// only per-application channel that carries the row's identity is the
/// <c>cardSource</c> argument (PowerCmd.Apply -> Hook.BeforePowerAmountChanged;
/// ModifyPowerAmountReceived does NOT receive it), so the card declares the
/// mode and the power reads it off the card that applied it. See
/// <see cref="KleeMod.Powers.PreventExhaustWardPower"/>.
///
/// Emitted by tools/gen_klee_cards.py; a row asking for the mode on a power
/// with no floor implementation is refused at generation time
/// (NEVER_REDUCES_POWERS).
/// </summary>
public interface INeverReducingApplier
{
    /// <summary>The row's `max_stacks`: the ceiling THIS card may raise the
    /// power to. A standing stack above it is left untouched.</summary>
    int NeverReducingCap { get; }
}
