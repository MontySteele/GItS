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
/// INAZUMA -- the Hive's second face (R273 pick 1 at its default, layout 1),
/// and <see cref="Natlan"/>'s twin in every mechanical respect.
///
/// THE TWO FACES OF ACT 2 DRESS THE SAME ZONE. Read <see cref="Natlan"/> for
/// why that is the shape and what it costs; the only thing that distinguishes
/// this class from that one is `Id.Entry`, and everything the engine derives
/// from it. Both delegate to <c>ModelDb.Act&lt;Hive&gt;()</c>, so their event
/// pools are not merely the same LENGTH -- which is the hard rule, because
/// `ActModel.GenerateRooms` shuffles the pool on the run's `UpFront` rng and a
/// different length moves every later roll -- they are the same LIST.
///
/// The map palette is the Hive's own hex, verbatim, exactly as act 1's
/// dressings carry Overgrowth's and Underdocks'. It is the first thing a real
/// dressing changes and this is where that edit lands.
/// </summary>
public sealed class Inazuma : ActModel
{
    /// <summary>The zone this one dresses, shared with <see cref="Natlan"/>.</summary>
    private static Hive Base => ModelDb.Act<Hive>();

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="Mondstadt.AllAncients"/>
    public override IEnumerable<AncientEventModel> AllAncients =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Inazuma, Base.AllAncients);

    /// <summary>
    /// The base zone's own unlocked pool, dressed. `Dress` is downstream of
    /// the filter, so every epoch gate the base act applies still applies --
    /// the Hive removes Orobas behind `OrobasEpoch`, and a face act hides
    /// Xbalanque / the Sacred Sakura on exactly the same save.
    /// </summary>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Inazuma, Base.GetUnlockedAncients(state));

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <inheritdoc cref="Natlan.GetMapPointTypes"/>
    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) => Base.GetMapPointTypes(mapRng);

    /// <summary>The Hive's fourteen (`Hive.cs:48`); `protected`, so not
    /// reachable to delegate.</summary>
    protected override int BaseNumberOfRooms => 14;

    /// <summary>The Hive's two (`Hive.cs:46`).</summary>
    protected override int NumberOfWeakEncounters => 2;

    /// <summary>The Hive's is empty (`Hive.cs:112`), so this one is too.</summary>
    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
    }

    /// <summary>The Hive's index (`Hive.cs:50`).</summary>
    public override int Index => 1;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsDefault => true;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsUnlocked(UnlockState unlockState) => true;

    /// <summary>The Hive's `27221C` (`Hive.cs:64`).</summary>
    public override Color MapTraveledColor => new Color("27221C");

    /// <summary>The Hive's `6E7750` (`Hive.cs:66`).</summary>
    public override Color MapUntraveledColor => new Color("6E7750");

    /// <summary>The Hive's `9B9562` (`Hive.cs:68`).</summary>
    public override Color MapBgColor => new Color("9B9562");

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
