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
/// SUMERU -- Glory's second face (R273 pick 2 at its default, layout 1), and
/// <see cref="Fontaine"/>'s twin in every mechanical respect.
///
/// Read <see cref="Fontaine"/> for the shape and <see cref="Natlan"/> for why
/// a one-zone act still gets a coin. Both faces delegate to
/// <c>ModelDb.Act&lt;Glory&gt;()</c>, so their seven act events are the same
/// LIST and not merely the same length -- which is what keeps the run's
/// `UpFront` shuffle, and every roll downstream of it, identical whichever way
/// the act-3 coin falls.
///
/// R273 sec.3 records why Sumeru sits here rather than on the Hive: it is the
/// strongest nation in both zones and can take only one, and its ritual
/// casters and devotees clear nine of Glory's twelve exclusive slots against
/// five on the Hive. That is a curation fact about the face's future content,
/// not about this file, which is the same twenty-odd delegations as its three
/// siblings.
/// </summary>
public sealed class Sumeru : ActModel
{
    /// <summary>The zone this one dresses, shared with <see cref="Fontaine"/>.</summary>
    private static Glory Base => ModelDb.Act<Glory>();

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<AncientEventModel> AllAncients => Base.AllAncients;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        Base.GetUnlockedAncients(state);

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <inheritdoc cref="Fontaine.GetMapPointTypes"/>
    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) => Base.GetMapPointTypes(mapRng);

    /// <summary>Glory's thirteen (`Glory.cs:44`); `protected`, so not
    /// reachable to delegate.</summary>
    protected override int BaseNumberOfRooms => 13;

    /// <summary>Glory's two (`Glory.cs:42`).</summary>
    protected override int NumberOfWeakEncounters => 2;

    /// <summary>Glory's is empty (`Glory.cs:104`), so this one is too.</summary>
    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
    }

    /// <summary>Glory's index (`Glory.cs:46`).</summary>
    public override int Index => 2;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsDefault => true;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsUnlocked(UnlockState unlockState) => true;

    /// <summary>Glory's `1D1E2F` (`Glory.cs:60`).</summary>
    public override Color MapTraveledColor => new Color("1D1E2F");

    /// <summary>Glory's `60717C` (`Glory.cs:62`).</summary>
    public override Color MapUntraveledColor => new Color("60717C");

    /// <summary>Glory's `819A97` (`Glory.cs:64`).</summary>
    public override Color MapBgColor => new Color("819A97");

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
