using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using BaseLib.Extensions;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Powers;

/// <summary>
/// A PERFORMER'S BODY. Three of these, one per member of the cast, and the
/// only thing that differs between them is the name and the sprite.
///
/// A PET, AND THE ENGINE ALREADY HAS PETS -- the decompile read written out in
/// full on <c>BakeKurageMonster</c>, which this class is a second consumer of
/// rather than a second discovery. <c>PlayerCmd.AddPet&lt;T&gt;(Player)</c>
/// spawns one on the player's side, it lives in <c>CombatState._allies</c> for
/// the fight, and ENEMIES CANNOT TARGET IT BY CONSTRUCTION:
/// <c>MonsterModel.PerformMove</c> is handed <c>combatState.PlayerCreatures</c>,
/// which is <c>Creatures.Where(c =&gt; c.IsPlayer)</c>, and a pet has no
/// <c>Player</c>. Nothing here maintains that. It is what being a pet MEANS,
/// and it is exactly what brief sec.3 rule 6 needs: "enemies keep targeting
/// Furina; the redirect is in her damage pipeline".
///
/// WITH A VISIBLE BAR, which is the one place this differs from the jellyfish.
/// The Bake-Kurage is <c>CustomPetModel(visibleHp: false)</c> on a 9999 pool
/// because it must not die; a performer's bar IS its Fanfare (rule 1), so the
/// flag is true and <c>BaseLib.CustomPetModel.IsHealthBarVisible</c> returns
/// it. HP must be at least 1 for a live creature, so the ledger never writes a
/// 0: a performer at 0 has LEFT, and <see cref="FurinaStagePets"/> removes the
/// body in the same reconcile.
///
/// THE ART IS OWED AND THE FALLBACK IS OSTY, deliberately and on the
/// jellyfish's own terms. Art is commissioned when a slice is ACCEPTED, not
/// before; a performer scene wants a <c>pck-src</c> pass and a
/// <c>build_pck</c>, which is refused from a worktree. So
/// <see cref="CustomVisualPath"/> asks the pack for this performer's scene and
/// falls through to the base game's Osty rig while the pack has none -- the
/// same null-answering <c>KleePck.Path</c> funnel every asset in this mod
/// goes through, and the same pre-repack failure mode the jellyfish already
/// documents. Three identical rigs is sec.8's "Three Ostys" failure mode
/// LITERALLY on screen, so this is a build-order fact worth reading twice: the
/// arm is not eyes-on ready until the three scenes exist.
/// </summary>
public abstract class StagePerformerMonster : CustomPetModel, ILocalizationProvider
{
    protected StagePerformerMonster() : base(visibleHp: true)
    {
    }

    /// <summary>Which member of the cast this body is.</summary>
    public abstract StagePerformer Performer { get; }

    /// <summary>The display name, and the one the strip and the log print.
    /// </summary>
    public abstract string DisplayName { get; }

    /// <summary>
    /// The bar's floor and ceiling as the ENGINE sees them. Both 1 because the
    /// real bar is written by <c>CreatureCmd.SetMaxAndCurrentHp</c> the moment
    /// the body is fielded: a performer arrives at 1 (rule 3) or at the
    /// relic's 3 (rule 2) or at a rotation's inherited pool, and none of those
    /// is a property of the MODEL. The engine's own pets do the same thing in
    /// the opposite direction (Byrdpip is 9999/9999 because it must never
    /// die).
    /// </summary>
    public override int MinInitialHp => 1;

    public override int MaxInitialHp => 1;

    /// <summary>This performer's scene inside the pack, or null while the pack
    /// has none. STATIC, so the scene-conversion registration can ask for the
    /// path without first building a model to ask.</summary>
    internal static string? ModVisualsPathFor(StagePerformer who) =>
        KleePck.Path($"furina/model/{who.ToString().ToLowerInvariant()}.tscn");

    /// <inheritdoc cref="StagePerformerMonster"/>
    public override string? CustomVisualPath =>
        ModVisualsPathFor(Performer)
        ?? SceneHelper.GetScenePath("creature_visuals/osty");

    public List<(string, string)>? Localization => new()
    {
        ("name", DisplayName),
        ("title", DisplayName),
    };
}

/// <summary>Gentilhomme Usher. Acts for Block, bows for Block (rules 9, 10).
/// </summary>
public sealed class UsherMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Usher;

    public override string DisplayName => "Gentilhomme Usher";
}

/// <summary>Surintendante Chevalmarin. The Guest Cast plan's performer: her
/// act and her bow both put Hydro on the board (brief sec.5.3).</summary>
public sealed class ChevalmarinMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Chevalmarin;

    public override string DisplayName => "Surintendante Chevalmarin";
}

/// <summary>Mademoiselle Crabaletta. The damage act and the damage bow.
/// </summary>
public sealed class CrabalettaMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Crabaletta;

    public override string DisplayName => "Mademoiselle Crabaletta";
}

/// <summary>
/// THE BODIES, RECONCILED AGAINST THE LEDGER. One entry point,
/// <see cref="Sync"/>, called after every change to the stage.
///
/// WHY A RECONCILE AND NOT A COMMAND PER RULE. Six rules move the stage --
/// summon, rotate, raise, spend, absorb, regen -- and each of them can add a
/// body, remove one, or move a bar, in combinations (a rotation removes AND
/// adds in one call). Six sites each doing their own spawn and despawn is six
/// chances to leave a body on a stage the ledger says is empty, and that
/// desync is invisible on screen until an attack lands on nothing. So the
/// ledger moves first, always, and this walks the difference.
///
/// IT IS THE MIRROR AND NEVER THE SOURCE. Nothing here decides a number:
/// every HP it writes is a <see cref="StageSeat.Fanfare"/> the ledger already
/// holds. See <c>FurinaStageLedger</c>'s header for why that direction is safe
/// -- no enemy can reach a pet, so no HP moves behind the ledger's back.
/// </summary>
public static class FurinaStagePets
{
    /// <summary>Which performers' scenes have been handed to BaseLib's
    /// conversion registry. PER PERFORMER and not one bool: the three carry
    /// three different scenes, and a single latch would register whichever
    /// arrived first and leave the other two as the engine's error
    /// creature.</summary>
    private static readonly HashSet<StagePerformer> _visualsRegistered = new();

    /// <summary>Is this creature one of HER performers? The type test is the
    /// whole test, for <c>BakeKuragePet.Is</c>'s reason: nothing else spawns
    /// one, and asking for the model rather than for <c>IsPet</c> keeps a
    /// relic's or a companion's pet out of the stage.</summary>
    public static bool Is(Creature? creature) =>
        creature?.Monster is StagePerformerMonster;

    /// <summary>Every body currently standing on THIS seat's stage, in the
    /// engine's own pet order.</summary>
    public static IEnumerable<Creature> BodiesOf(Creature? furina) =>
        furina?.Player?.PlayerCombatState?.Pets.Where(Is)
        ?? Enumerable.Empty<Creature>();

    /// <summary>
    /// Field the missing bodies, remove the departed ones, and push every
    /// seat's bar onto the body wearing it.
    ///
    /// ORDER MATTERS ONCE: departures BEFORE arrivals. A rotation on a full
    /// stage leaves three seats and one dead reference, and the engine's own
    /// placement pass (see <see cref="FurinaStagePlacement"/>) re-lays a
    /// player's pets out on every ADD -- so removing first means the new
    /// body's arrival lays out the three that are actually standing there
    /// rather than four.
    /// </summary>
    public static async Task Sync(Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        if (furina!.Player is not { } player) return;
        var ledger = FurinaStageLedger.For(furina);

        var kept = ledger.Seats
            .Select(s => s.Pet)
            .Where(p => p != null)
            .ToHashSet();
        foreach (var stray in BodiesOf(furina).ToList())
        {
            if (kept.Contains(stray)) continue;
            await Retire(stray);
        }

        foreach (var seat in ledger.Seats.ToList())
        {
            if (seat.Pet == null || seat.Pet.IsDead)
            {
                seat.Pet = await Field(player, seat.Who);
            }
            if (seat.Pet == null) continue;
            await CreatureCmd.SetMaxAndCurrentHp(seat.Pet, seat.Fanfare);
        }

        FurinaStagePlacement.Reflow(furina);
    }

    /// <summary>
    /// The BARS ONLY -- no arrival, no departure, no re-flow.
    ///
    /// A SECOND ENTRY POINT AND NOT A FLAG, because the two are different
    /// events and one of them is far the commoner: a Raise or a regen moves a
    /// number on a body already standing where it belongs, and running the
    /// full reconcile for it would walk the pet list, ask the room for its
    /// nodes and re-lay out a line that has not changed -- every turn, and on
    /// every Raise. Nothing here can add or remove a body, which is the
    /// property that makes it safe on those two hot paths.
    /// </summary>
    public static void SyncBars(Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        foreach (var seat in FurinaStageLedger.For(furina!).Seats)
        {
            if (seat.Pet == null || seat.Pet.IsDead) continue;
            // Fire-and-forget is deliberate HERE and nowhere else: this call
            // adds no creature and removes none, so nothing later in the frame
            // can read a half-built board. Every arrival and departure goes
            // through the awaited `Sync` above.
            _ = CreatureCmd.SetMaxAndCurrentHp(seat.Pet, seat.Fanfare);
        }
    }

    /// <summary>
    /// One body onto the board.
    ///
    /// THE MODEL IS INJECTED ON FIRST USE rather than registered at boot, for
    /// <c>BakeKuragePet.Summon</c>'s reason word for word:
    /// <c>AbstractModel</c>'s constructor does not add to <c>ModelDb</c>, and
    /// <c>ModelDb.Inject</c> is the door the engine documents for mods. It is
    /// itself guarded by <c>Contains</c>, so calling it per summon costs one
    /// dictionary lookup and cannot double-register.
    /// </summary>
    private static async Task<Creature?> Field(Player player, StagePerformer who)
    {
        try
        {
            var type = ModelFor(who);
            if (!ModelDb.Contains(type)) ModelDb.Inject(type);
            EnsureVisualsConverted(who);
            return who switch
            {
                StagePerformer.Usher =>
                    await PlayerCmd.AddPet<UsherMonster>(player),
                StagePerformer.Chevalmarin =>
                    await PlayerCmd.AddPet<ChevalmarinMonster>(player),
                _ => await PlayerCmd.AddPet<CrabalettaMonster>(player),
            };
        }
        catch (Exception e)
        {
            // A body that cannot be fielded must not take the fight down with
            // it: the RULES are the ledger's and they are already correct, so
            // the worst case here is a stage that is invisible rather than a
            // stage that is wrong. Loud in godot.log, which is where the
            // triage of every mod defect in this repo starts.
            Log.Warn($"[{KleeMod.ModId}] stage: could not field {who}: {e}");
            return null;
        }
    }

    /// <summary>
    /// A body off the board.
    ///
    /// KILL AND NOT ESCAPE, and it is the pet list that decides:
    /// <c>PlayerCombatState.AddPetInternal</c> subscribes <c>OnPetDied</c>, so
    /// DEATH is what takes a pet out of <c>Pets</c>. <c>CreatureCmd.Escape</c>
    /// removes the node and the combat entry and leaves the pet in that list,
    /// which would leave <see cref="BodiesOf"/> counting a performer that is
    /// not on the stage.
    /// </summary>
    private static async Task Retire(Creature pet)
    {
        if (pet.IsDead) return;
        await CreatureCmd.Kill(pet, force: true);
    }

    internal static Type ModelFor(StagePerformer who) => who switch
    {
        StagePerformer.Usher => typeof(UsherMonster),
        StagePerformer.Chevalmarin => typeof(ChevalmarinMonster),
        _ => typeof(CrabalettaMonster),
    };

    /// <summary>Teach BaseLib that this performer's scene is an
    /// <c>NCreatureVisuals</c>. The whole argument -- why the library's own
    /// automatic pass cannot cover an INJECTED model, and why the Osty
    /// fallback must NOT be registered -- is written out on
    /// <c>BakeKuragePet.EnsureVisualsConverted</c>; this is the same door for
    /// three more scenes.</summary>
    private static void EnsureVisualsConverted(StagePerformer who)
    {
        if (_visualsRegistered.Contains(who)) return;
        if (StagePerformerMonster.ModVisualsPathFor(who) is not { } scene) return;
        _visualsRegistered.Add(who);
        scene.RegisterSceneForConversion<NCreatureVisuals>();
    }
}
