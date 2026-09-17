using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod.Teyvat.Acts;

/// <summary>
/// LIYUE -- Underdocks, dressed (spike item 4.1), on exactly the terms
/// <see cref="Mondstadt"/> is written on: every mechanical member delegates to
/// <c>ModelDb.Act&lt;Underdocks&gt;()</c>, so the encounter table, the event pool
/// and the Ancient pool are the base zone's own object references.
///
/// TWO DIFFERENCES FROM MONDSTADT, and both come from the zone it dresses.
///
/// First, `ApplyActDiscoveryOrderModifications` is EMPTY here rather than
/// replicated, because Underdocks' is empty (`Underdocks.cs:103-105`). So this
/// class carries no copied body at all and no drift risk with it.
///
/// Second, `IsUnlocked`. Underdocks is gated on `UnderdocksEpoch` and is
/// `IsDefault => false`; this dressing answers TRUE and `IsDefault => true`
/// for the reason <see cref="Mondstadt.IsDefault"/> gives -- a non-default
/// undiscovered act is FORCED past the roll on the first single-player run
/// (`ActModel.cs:563`), which would make the pair's first appearance a
/// certainty rather than a coin. It is disclosed as a deliberate difference
/// from the zone it dresses: under this arm, act 1's second face needs no
/// epoch, where in the base game Underdocks does.
/// </summary>
public sealed class Liyue : ActModel
{
    /// <summary>The zone this one dresses.</summary>
    private static Underdocks Base => ModelDb.Act<Underdocks>();

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="Mondstadt.AllAncients"/>
    public override IEnumerable<AncientEventModel> AllAncients =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Liyue, Base.AllAncients);

    /// <summary>
    /// The base zone's own unlocked pool, dressed. `Dress` is downstream of
    /// the filter, so every epoch gate the base act applies still applies --
    /// the Hive removes Orobas behind `OrobasEpoch`, and a face act hides
    /// Xbalanque / the Sacred Sakura on exactly the same save.
    /// </summary>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Liyue, Base.GetUnlockedAncients(state));

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <inheritdoc cref="Mondstadt.GetMapPointTypes"/>
    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) => Base.GetMapPointTypes(mapRng);

    /// <summary>Underdocks' fifteen (`Underdocks.cs:42`); `protected`, so not
    /// reachable to delegate.</summary>
    protected override int BaseNumberOfRooms => 15;

    /// <summary>Underdocks' three (`Underdocks.cs:40`).</summary>
    protected override int NumberOfWeakEncounters => 3;

    /// <summary>Underdocks' is empty (`Underdocks.cs:103`), so this one is
    /// too, and nothing here can drift from it.</summary>
    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
    }

    /// <summary>Underdocks' index, which is Overgrowth's index, which is 0.
    /// All four faces of act 1 stand here.</summary>
    public override int Index => 0;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsDefault => true;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsUnlocked(UnlockState unlockState) => true;

    /// <summary>Underdocks' `180F24` (`Underdocks.cs:60`).</summary>
    public override Color MapTraveledColor => new Color("180F24");

    /// <summary>Underdocks' `534A62` (`Underdocks.cs:62`).</summary>
    public override Color MapUntraveledColor => new Color("534A62");

    /// <summary>Underdocks' `9F95A5` (`Underdocks.cs:64`).</summary>
    public override Color MapBgColor => new Color("9F95A5");

    /// <inheritdoc cref="Mondstadt.BgMusicOptions"/>
    public override string[] BgMusicOptions => Base.BgMusicOptions;

    /// <inheritdoc cref="Mondstadt.BgMusicOptions"/>
    public override string[] MusicBankPaths => Base.MusicBankPaths;

    /// <inheritdoc cref="Mondstadt.BgMusicOptions"/>
    public override string AmbientSfx => Base.AmbientSfx;

    /// <inheritdoc cref="Mondstadt.ChestSpineResourcePath"/>
    public override string ChestSpineResourcePath => Base.ChestSpineResourcePath;

    /// <inheritdoc cref="Mondstadt.ChestSpineResourcePath"/>
    public override string ChestSpineSkinNameNormal => Base.ChestSpineSkinNameNormal;

    /// <inheritdoc cref="Mondstadt.ChestSpineResourcePath"/>
    public override string ChestSpineSkinNameStroke => Base.ChestSpineSkinNameStroke;

    /// <inheritdoc cref="Mondstadt.ChestSpineResourcePath"/>
    public override string ChestOpenSfx => Base.ChestOpenSfx;
}
