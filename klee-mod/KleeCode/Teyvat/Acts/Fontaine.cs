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
/// FONTAINE -- Glory, dressed (R273 pick 2 at its default, layout 1).
///
/// A SIBLING, NOT A FORK, on <see cref="Mondstadt"/>'s terms and with
/// <see cref="Natlan"/>'s shape: Glory is the base game's ONE zone at index 2,
/// so both faces of act 3 dress it and Glory itself is replaced by the pair
/// (`review/ruled/teyvat-nation-mapping-2026-09-14.md` sec.1). Every
/// mechanical member delegates to <c>ModelDb.Act&lt;Glory&gt;()</c>: the
/// eighteen encounters, the seven act events, the three Ancients and the boss
/// discovery order are Glory's own object references.
///
/// GLORY'S ANCIENTS HAVE NO EPOCH GATE, unlike the Hive's.
/// `Glory.GetUnlockedAncients` is `AllAncients.ToList()` and nothing else
/// (`Acts/Glory.cs:99-102`); delegating carries that too, so a dressed act 3
/// offers the same three on every save.
///
/// NO REPLICATED BODY. `Glory.ApplyActDiscoveryOrderModifications` is EMPTY
/// (`Glory.cs:104-106`), so this class copies no statement of Glory's and
/// carries no drift risk with it.
/// </summary>
public sealed class Fontaine : ActModel
{
    /// <summary>The zone this one dresses, shared with <see cref="Sumeru"/>.</summary>
    private static Glory Base => ModelDb.Act<Glory>();

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="Mondstadt.AllAncients"/>
    public override IEnumerable<AncientEventModel> AllAncients =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Fontaine, Base.AllAncients);

    /// <summary>
    /// The base zone's own unlocked pool, dressed. `Dress` is downstream of
    /// the filter, so every epoch gate the base act applies still applies --
    /// the Hive removes Orobas behind `OrobasEpoch`, and a face act hides
    /// Xbalanque / the Sacred Sakura on exactly the same save.
    /// </summary>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Fontaine, Base.GetUnlockedAncients(state));

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <summary>
    /// Glory's map shape, asked of the base instance. `Glory.GetMapPointTypes`
    /// makes a `NextInt(5, 7)` draw and then a `StandardRandomUnknownCount`
    /// draw (`Glory.cs:108-113`) -- two draws, delegated rather than restated.
    /// </summary>
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

    /// <summary>Glory's index (`Glory.cs:46`). Both faces of act 3 stand
    /// here.</summary>
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
