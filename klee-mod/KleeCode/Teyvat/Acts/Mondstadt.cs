using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod.Teyvat.Acts;

/// <summary>
/// MONDSTADT -- Overgrowth, dressed (spike item 4.1).
///
/// A SIBLING, NOT A FORK. Every mechanical member of this class is a
/// DELEGATION to <c>ModelDb.Act&lt;Overgrowth&gt;()</c>, which means the encounter
/// table, the event pool, the Ancient pool, the boss discovery order, the room
/// count and the map point counts are not copies of Overgrowth's -- they are
/// Overgrowth's, the same object references, resolved through the same
/// `ModelDb` singletons. A number cannot drift between the two zones because
/// there is only one set of numbers.
///
/// WHAT ACTUALLY CHANGES is `Id.Entry`: `MONDSTADT` instead of `OVERGROWTH`.
/// From that one string the engine derives the act title (`acts` loc table,
/// key `MONDSTADT.title`) and -- but for the alias below -- every asset path.
/// `TeyvatFrame.AssetAlias` sends the asset paths back to Overgrowth's for the
/// spike, because `Rooms/BackgroundAssets`'s constructor throws rather than
/// falls back on a missing directory and this spike commissions no art.
///
/// THE MAP COLOURS ARE COPIED AND NOT DELEGATED, and that is the one place
/// this file states a value of its own. `MapTraveledColor` and its two
/// siblings are `abstract` on `ActModel`, so they must be answered here; they
/// are answered with Overgrowth's exact hex strings, so the map screen is
/// pixel-identical. They are the obvious first thing a real dressing changes.
///
/// TWO THINGS THIS CLASS DELIBERATELY DOES NOT DO. It does not declare an
/// `Index` of its own choosing -- it declares Overgrowth's, 0, because the
/// coin the base game already flips is the coin this design rides. And it does
/// not appear in `ModelDb.Acts` by itself: `Patches/ModelDbActsPatch` is what
/// publishes it, and that patch stands down entirely when the arm is off.
/// </summary>
public sealed class Mondstadt : ActModel
{
    /// <summary>The zone this one dresses. One property, read by every
    /// delegation below, so the pairing is stated once.</summary>
    private static Overgrowth Base => ModelDb.Act<Overgrowth>();

    // ==================================================================
    // MECHANICS -- every one of these is the base zone's own object.
    // ==================================================================

    /// <summary>
    /// The identical <see cref="EncounterModel"/> instances Overgrowth
    /// returns. `AllEncounters` on the base act caches
    /// `GenerateAllEncounters()` once, so this returns that one cached
    /// sequence rather than re-running the generator -- which is what makes
    /// `Mondstadt.AllEncounters` REFERENCE-EQUAL to `Overgrowth.AllEncounters`
    /// and not merely equal element by element. `TeyvatFrameTests` pins the
    /// reference equality, because element equality would still permit a
    /// future edit to fork the list.
    /// </summary>
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => Base.AllEncounters;

    /// <summary>
    /// Overgrowth's thirteen act-exclusive events, unchanged and in order.
    ///
    /// EQUAL COUNTS ARE A HARD RULE, not a preference (the read's sec.6):
    /// `ActModel.GenerateRooms` shuffles `AllEvents.Concat(AllSharedEvents)`
    /// with `UnstableShuffle(rng)` on the run's `UpFront` rng at run start,
    /// so a pool of a different LENGTH consumes a different number of draws
    /// and moves every later roll on that rng -- bosses, Ancients, encounter
    /// order. Returning the base zone's own list makes the counts equal by
    /// identity rather than by arithmetic.
    ///
    /// SO THE CONVERTED EVENT IS NOT IN HERE. Spike item 4.2's Springvale
    /// Cheese Cellar reaches the map by SUBSTITUTION at pull time
    /// (`Patches/PullNextEventPatch`), which is downstream of the shuffle and
    /// therefore costs no rng draw at all. See that file for the argument.
    /// </summary>
    public override IEnumerable<EventModel> AllEvents => Base.AllEvents;

    /// <inheritdoc cref="AllEvents"/>
    public override IEnumerable<AncientEventModel> AllAncients => Base.AllAncients;

    /// <inheritdoc cref="AllEvents"/>
    public override IEnumerable<AncientEventModel> GetUnlockedAncients(UnlockState state) =>
        Base.GetUnlockedAncients(state);

    /// <inheritdoc cref="GenerateAllEncounters"/>
    public override IEnumerable<EncounterModel> BossDiscoveryOrder => Base.BossDiscoveryOrder;

    /// <summary>
    /// Overgrowth's own map shape, asked of the base instance with the map rng
    /// the caller passed. The read's warning was "copy the source act's
    /// numbers verbatim, or the map changes"; delegating is how you copy a
    /// number without writing it down twice.
    /// </summary>
    public override MapPointTypeCounts GetMapPointTypes(Rng mapRng) => Base.GetMapPointTypes(mapRng);

    /// <summary>
    /// Overgrowth's fifteen. `BaseNumberOfRooms` is `protected abstract`, so
    /// it cannot be delegated -- a protected member of a sealed sibling is not
    /// reachable from here -- and the literal is stated with the base zone's
    /// line number beside it. One of exactly three numbers in this file.
    /// (`MegaCrit.Sts2.Core.Models.Acts/Overgrowth.cs:47`.)
    /// </summary>
    protected override int BaseNumberOfRooms => 15;

    /// <summary>Overgrowth's three (`Overgrowth.cs:45`), for the same
    /// reason: `protected`, so not reachable to delegate.</summary>
    protected override int NumberOfWeakEncounters => 3;

    /// <summary>
    /// Overgrowth's first-run ordering, REPLICATED rather than delegated, and
    /// this is the one honest copy in the arm.
    ///
    /// `ApplyActDiscoveryOrderModifications` is `protected abstract` and
    /// writes into `_rooms`, which is THIS instance's room set -- so calling
    /// Overgrowth's copy would order Overgrowth's rooms and leave ours
    /// untouched. The body below is Overgrowth's, statement for statement
    /// (`Overgrowth.cs:110-127`); every type it names is a base-game model and
    /// `RoomSet.SwapToOrCreateAtIndex` is the game's own public static.
    ///
    /// IT IS A DRIFT RISK AND IS NAMED AS ONE. If MegaCrit changes
    /// Overgrowth's first-run order in a patch, this copy does not follow, and
    /// nothing in the build would say so. A real dressing wants that pinned;
    /// a spike records it. Note it only fires on a save with zero completed
    /// runs, so no seat and no calibration read can reach it.
    /// </summary>
    protected override void ApplyActDiscoveryOrderModifications(UnlockState unlockState)
    {
        if (unlockState.NumberOfRuns != 0)
        {
            return;
        }

        RoomSet.SwapToOrCreateAtIndex<EncounterModel, NibbitsWeak>(_rooms.normalEncounters, 0);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, SlimesWeak>(_rooms.normalEncounters, 1);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, ShrinkerBeetleWeak>(_rooms.normalEncounters, 2);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, InkletsNormal>(_rooms.normalEncounters, 3);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, MawlerNormal>(_rooms.normalEncounters, 4);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, RubyRaidersNormal>(_rooms.normalEncounters, 5);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, NibbitsNormal>(_rooms.normalEncounters, 6);
        RoomSet.SwapToOrCreateAtIndex<EventModel, ByrdonisNest>(_rooms.events, 0);
        RoomSet.SwapToOrCreateAtIndex<EventModel, SapphireSeed>(_rooms.events, 1);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, ByrdonisElite>(_rooms.eliteEncounters, 0);
        RoomSet.SwapToOrCreateAtIndex<EncounterModel, PhrogParasiteElite>(_rooms.eliteEncounters, 1);
    }

    // ==================================================================
    // IDENTITY AND DRESSING.
    // ==================================================================

    /// <summary>Overgrowth's index. The whole design rests on this line: two
    /// acts at one index is a state the base game is already in (Overgrowth
    /// and Underdocks both answer 0), so the roll needs no mod-side coin.
    /// </summary>
    public override int Index => 0;

    /// <summary>
    /// TRUE, and deliberately so, where a naive dressing would say false.
    ///
    /// `ActModel.GetRandomList` FORCES a non-default, unlocked, undiscovered
    /// act on a single-player run outside test mode, bypassing the roll
    /// entirely (`ActModel.cs:563`). A dressing marked non-default would
    /// therefore appear on the first run after it ships whatever the coin
    /// said, and any later reading of coin fairness would be measuring that
    /// branch instead. Marking both faces default keeps the pair a genuine
    /// coin from the first run.
    ///
    /// It also means the dressing needs no epoch: `IsUnlocked` is
    /// unconditional below, matching Overgrowth's.
    /// </summary>
    public override bool IsDefault => true;

    /// <inheritdoc cref="IsDefault"/>
    public override bool IsUnlocked(UnlockState unlockState) => true;

    /// <summary>
    /// Overgrowth's `28231D` (`Overgrowth.cs:65`). Copied, not delegated,
    /// because `MapTraveledColor` is `abstract` and must be answered here --
    /// and stated rather than aliased because the map palette is the first
    /// thing a real Mondstadt changes, so this is where that edit lands.
    /// </summary>
    public override Color MapTraveledColor => new Color("28231D");

    /// <summary>Overgrowth's `877256` (`Overgrowth.cs:67`).</summary>
    public override Color MapUntraveledColor => new Color("877256");

    /// <summary>Overgrowth's `A78A67` (`Overgrowth.cs:69`).</summary>
    public override Color MapBgColor => new Color("A78A67");

    /// <summary>
    /// Overgrowth's two FMOD events and their banks, unchanged.
    ///
    /// SPIKE ITEM 4.4 DOES NOT LIVE HERE. Naming a non-existent FMOD event
    /// would be the cheapest possible duck, but it would also be a silent
    /// failure mode: `NRunMusicController.LoadActBank` refuses a bank it
    /// cannot verify and the act would run in silence whether or not a
    /// replacement track existed. The music arm is a patch on
    /// `NRunMusicController` instead (`Teyvat/TeyvatMusic.cs`), which can
    /// check for the track FIRST and do nothing at all when there is none.
    /// </summary>
    public override string[] BgMusicOptions => Base.BgMusicOptions;

    /// <inheritdoc cref="BgMusicOptions"/>
    public override string[] MusicBankPaths => Base.MusicBankPaths;

    /// <inheritdoc cref="BgMusicOptions"/>
    public override string AmbientSfx => Base.AmbientSfx;

    /// <summary>Overgrowth's chest rig, its two skins and its sfx. The read
    /// costed this at zero and it is: three delegations.</summary>
    public override string ChestSpineResourcePath => Base.ChestSpineResourcePath;

    /// <inheritdoc cref="ChestSpineResourcePath"/>
    public override string ChestSpineSkinNameNormal => Base.ChestSpineSkinNameNormal;

    /// <inheritdoc cref="ChestSpineResourcePath"/>
    public override string ChestSpineSkinNameStroke => Base.ChestSpineSkinNameStroke;

    /// <inheritdoc cref="ChestSpineResourcePath"/>
    public override string ChestOpenSfx => Base.ChestOpenSfx;
}
