using System.Collections.Generic;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// <i>Cover Your Ears!</i>'s this-turn Strength loss (Klee final pass,
/// 2026-10-02, <c>review/active/klee-final-pass-2026-10-02.md</c>, "Ruled").
/// The base game's <c>PiercingWailPower</c> exactly: a
/// <c>TemporaryStrengthPower</c> with <c>IsPositive</c> false, applied at plus
/// N to each enemy, which takes N Strength now and gives it back at the end of
/// that enemy's turn. Its origin is the card, so its title is the card's.
/// Emitted by the codegen's <c>lose_strength</c> with <c>this_turn: true</c>
/// (<c>{CardClass}Power</c>). Sim twin: <c>temp_strength_down</c>
/// (<c>tier0/engine/refpowers.py</c>).
///
/// ITS OWN ROWS, as <see cref="RaiseAToastPower"/>'s: the boot self-check
/// (R8) asks every power this assembly registers for a title and a
/// description under its own id.
/// </summary>
public sealed class ProtoKoCoverYourEarsPower : TemporaryStrengthPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Cover Your Ears!"),
        ("description",
            "Lose [blue]{Amount}[/blue] [gold]Strength[/gold] this turn."),
    };

    public override AbstractModel OriginModel =>
        ModelDb.Card<ProtoKoCoverYourEars>();

    protected override bool IsPositive => false;
}

/// <summary>
/// Amber, Explosive Puppet's "Enemy loses 3 Strength this turn" (the co-op
/// run, 2026-10-02): <see cref="ProtoKoCoverYourEarsPower"/>'s shape on the
/// one chosen enemy. Sim twin: <c>temp_strength_down</c>.
/// </summary>
public sealed class ProtoMcAmberExplosivePuppetPower : TemporaryStrengthPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosive Puppet"),
        ("description",
            "Lose [blue]{Amount}[/blue] [gold]Strength[/gold] this turn."),
    };

    public override AbstractModel OriginModel =>
        ModelDb.Card<ProtoMcAmberExplosivePuppet>();

    protected override bool IsPositive => false;
}
