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
/// NATLAN -- the Hive, dressed (R273 pick 1 at its default, layout 1).
///
/// A SIBLING, NOT A FORK, on exactly <see cref="Mondstadt"/>'s terms: every
/// mechanical member delegates to <c>ModelDb.Act&lt;Hive&gt;()</c>, so the
/// twenty encounters, the ten act events, the three Ancients and the boss
/// discovery order are the base zone's OWN object references and cannot drift
/// from it. What changes is `Id.Entry` -- `NATLAN` -- and the title, the map
/// palette and the asset paths the engine derives from it.
///
/// ONE ZONE, TWO FACES, AND THAT IS THE DIFFERENCE FROM ACT 1. The base game
/// ships two zones at index 0 (Overgrowth and Underdocks), so act 1's pair
/// replaced a pair. It ships exactly ONE at index 1, the Hive, so BOTH faces
/// of act 2 are siblings of the SAME base act and the Hive is replaced by the
/// two of them together (`review/ruled/teyvat-nation-mapping-2026-09-14.md`
/// sec.1; `Patches/ModelDbActsPatch` is where that is written). The coin act 2
/// rolls is therefore one this arm CREATES rather than one it rides -- a
/// one-candidate bucket becomes a two-candidate bucket -- and
/// `ActModel.GetRandomList` still makes exactly one `rng.NextItem` draw at
/// index 1 either way (`ActModel.cs:551-578`, confirmed against the installed
/// 0.111.0 decompile), so the draw COUNT on the run's rng is unchanged and no
/// later roll moves.
///
/// NO REPLICATED BODY AND NO DRIFT RISK. `Hive.ApplyActDiscoveryOrderModifications`
/// is EMPTY (`Acts/Hive.cs:112-114`), unlike Overgrowth's, so this class
/// copies nothing at all -- the honest copy <see cref="Mondstadt"/> carries
/// has no counterpart here.
/// </summary>
public sealed class Natlan : ActModel
{
    /// <summary>The zone this one dresses, and the zone <see cref="Inazuma"/>
    /// dresses too. One property, read by every delegation below.</summary>
    private static Hive Base => ModelDb.Act<Hive>();

    // ==================================================================
    // MECHANICS -- every one of these is the base zone's own object.
    // ==================================================================

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <inheritdoc cref="Mondstadt.AllEvents"/>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="Mondstadt.AllAncients"/>
    public override IEnumerable<AncientEventModel> AllAncients =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Natlan, Base.AllAncients);

    /// <summary>
    /// The base zone's own unlocked pool, dressed. `Dress` is downstream of
    /// the filter, so every epoch gate the base act applies still applies --
    /// the Hive removes Orobas behind `OrobasEpoch`, and a face act hides
    /// Xbalanque / the Sacred Sakura on exactly the same save.
    /// </summary>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        TeyvatGeneratedAncients.Dress(TeyvatFrame.Natlan, Base.GetUnlockedAncients(state));

    /// <inheritdoc cref="Mondstadt.GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <summary>
    /// The Hive's map shape, asked of the base instance with the caller's map
    /// rng. `Hive.GetMapPointTypes` makes a `NextGaussianInt` draw and then a
    /// `StandardRandomUnknownCount` draw (`Hive.cs:121-126`); delegating is how
    /// you copy two rng draws without writing them down twice.
    /// </summary>
    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) => Base.GetMapPointTypes(mapRng);

    /// <summary>The Hive's fourteen (`Hive.cs:48`). `protected abstract`, so
    /// not reachable to delegate -- one of exactly two numbers in this
    /// file.</summary>
    protected override int BaseNumberOfRooms => 14;

    /// <summary>The Hive's two (`Hive.cs:46`), for the same reason.</summary>
    protected override int NumberOfWeakEncounters => 2;

    /// <summary>The Hive's is empty (`Hive.cs:112`), so this one is too and
    /// nothing here can drift from it.</summary>
    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
    }

    // ==================================================================
    // IDENTITY AND DRESSING.
    // ==================================================================

    /// <summary>The Hive's index (`Hive.cs:50`). Both faces of act 2 stand
    /// here, and nothing else does once the patch has run.</summary>
    public override int Index => 1;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsDefault => true;

    /// <inheritdoc cref="Mondstadt.IsDefault"/>
    public override bool IsUnlocked(UnlockState unlockState) => true;

    /// <summary>The Hive's `27221C` (`Hive.cs:64`). Copied, not delegated:
    /// `MapTraveledColor` is `abstract` and must be answered here.</summary>
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
