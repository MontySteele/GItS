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
/// NO BAR (the re-founding, 2026-10-04: "performers with no bars"). The
/// Bake-Kurage's shape exactly: <c>CustomPetModel(visibleHp: false)</c>, and
/// nothing in the arm ever writes a performer's HP. A pet must have at least
/// 1 HP to be alive, so the model's pool is 1; enemies cannot target a pet,
/// so nothing can take it.
///
/// EACH WEARS ITS OWN SILHOUETTE, and the three scenes are authored rather
/// than borrowed: <c>klee-mod/pck-src/furina/model/{usher,chevalmarin,
/// crabaletta}.tscn</c>, cut from the Kurage's minimal
/// <c>NCreatureVisualsFactory</c> scene -- <c>%Visuals/Rig/Body</c>, a
/// <c>Bounds</c> box, and the four-state animation pair the shared
/// <see cref="KleeMod.Vfx.CreatureAnimationRouter"/> travels to. They point at
/// the Salon strip's own member sprites
/// (<c>res://furina/salon/member_*.png</c>), which the pack already carries:
/// ONE PRODUCER PER OUT-PATH (art_lint L11) is why the art is reused where it
/// stands rather than copied to a second path. The eight guests' scenes
/// (<c>guest_*.tscn</c>) are the same scene re-proportioned: people, not
/// creatures, cut at 224 px (80% of Furina's 280) from each guest's in-game
/// model render where it keys cleanly and from the Wish render otherwise, by
/// <c>tools/cut_guest_bodies.py</c>, which writes the scenes from one
/// template.
///
/// THEY STAND, WHERE THE JELLYFISH FLOATS, and that is the one number that is
/// theirs rather than inherited. A <c>Sprite2D</c> centres on its origin, so a
/// 144-tall performer whose feet are on the ground line has its Rig at -72;
/// the Kurage's is -80 under a 128-tall sprite, which floats it 16px clear --
/// right for a jellyfish and wrong for a person on a stage. The idle bob is a
/// third of the jellyfish's and the sway a half, for the same reason.
///
/// <c>Bounds</c> IS THE PLACEMENT DIAL and is cut to each sprite's real width
/// (121 / 129 / 120): <see cref="FurinaStagePlacement"/> packs the line out
/// from Furina's hitbox edge by each body's OWN box, so a box wider than the
/// art would space the line by a margin nobody can see.
///
/// THE FALLBACK IS STILL OSTY and stays, on the jellyfish's own terms:
/// <see cref="CustomVisualPath"/> asks the pack for this performer's scene and
/// falls through to the base game's rig when the pack has none -- the same
/// null-answering <c>KleePck.Path</c> funnel every asset in this mod goes
/// through. It is a PRE-REPACK failure mode now rather than the standing
/// state, and it is worth keeping named: three identical rigs is sec.8's
/// "Three Ostys" literally on screen, so a build whose pck predates these
/// scenes reads as that failure rather than as the design.
/// </summary>
public abstract class StagePerformerMonster : CustomPetModel, ILocalizationProvider
{
    protected StagePerformerMonster() : base(visibleHp: false)
    {
    }

    /// <summary>Which member of the cast this body is.</summary>
    public abstract StagePerformer Performer { get; }

    /// <summary>The display name, and the one the strip and the log print.
    /// </summary>
    public abstract string DisplayName { get; }

    /// <summary>One HP, never written: performers have no bars.</summary>
    public override int MinInitialHp => 1;

    public override int MaxInitialHp => 1;

    /// <summary>This performer's scene inside the pack, or null while the pack
    /// has none. STATIC, so the scene-conversion registration can ask for the
    /// path without first building a model to ask.</summary>
    internal static string? ModVisualsPathFor(StagePerformer who) => who switch
    {
        // One LITERAL path per guest, not one interpolated one: the deploy's
        // S12 check reads every `KleePck.Path("...")` literal and refuses a
        // reference it cannot find in the staged pack. Each guest's body is
        // cut by tools/cut_guest_bodies.py (224 px, 80% of Furina).
        StagePerformer.Charlotte => KleePck.Path("furina/model/guest_charlotte.tscn"),
        StagePerformer.Wriothesley => KleePck.Path("furina/model/guest_wriothesley.tscn"),
        StagePerformer.Lynette => KleePck.Path("furina/model/guest_lynette.tscn"),
        StagePerformer.Clorinde => KleePck.Path("furina/model/guest_clorinde.tscn"),
        StagePerformer.Lyney => KleePck.Path("furina/model/guest_lyney.tscn"),
        StagePerformer.Sigewinne => KleePck.Path("furina/model/guest_sigewinne.tscn"),
        StagePerformer.Chevreuse => KleePck.Path("furina/model/guest_chevreuse.tscn"),
        // The pool to 75 (2026-10-09): three of its four guests were cut by
        // the supporting pool's art pass and stand in their own scenes;
        // Freminet has none yet and stands as the Osty fallback.
        StagePerformer.Navia => KleePck.Path("furina/model/guest_navia.tscn"),
        StagePerformer.Neuvillette => KleePck.Path("furina/model/guest_neuvillette.tscn"),
        StagePerformer.Escoffier => KleePck.Path("furina/model/guest_escoffier.tscn"),
        _ => null,
    };

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

// ---- THE FOUR GUESTS of the Salon's Tab slice (2026-10-05). The name is the
// ledger's (`FurinaStageLedger.DisplayName`).

public sealed class CharlotteMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Charlotte;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class WriothesleyMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class LynetteMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Lynette;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class ClorindeMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Clorinde;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

// ---- THE POOL TO 39's three guests (2026-10-05).

public sealed class LyneyMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Lyney;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class SigewinneMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class ChevreuseMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

// ---- THE POOL TO 75's four guests (2026-10-09,
// review/active/furina-pool-growth-2026-10-09.md sec.5). Navia, Neuvillette
// and Escoffier wear the scenes the supporting pool's art pass cut; Freminet
// has none yet (`ModVisualsPathFor` answers null) and stands as the Osty
// fallback until one is cut.

public sealed class FreminetMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Freminet;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class NaviaMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Navia;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class NeuvilletteMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

public sealed class EscoffierMonster : StagePerformerMonster
{
    public override StagePerformer Performer => StagePerformer.Escoffier;

    public override string DisplayName =>
        FurinaStageLedger.DisplayName(Performer);
}

/// <summary>
/// THE BODIES, RECONCILED AGAINST THE LEDGER. One entry point,
/// <see cref="Sync"/>, called after every change to the stage.
///
/// WHY A RECONCILE AND NOT A COMMAND PER RULE. Summons, evictions, Bows,
/// returns and moves each add or remove a body, in combinations. So the
/// ledger moves first, always, and this walks the difference.
///
/// IT IS THE MIRROR AND NEVER THE SOURCE: nothing here decides a rule.
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
    /// Field the missing bodies and remove the departed ones.
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
                seat.Pet = await Field(player, seat.Who, seat.Upgraded);
            }
            else if (seat.Upgraded)
            {
                // The pool to 75: an upgraded duplicate moved a standing
                // guest; its badge now says the upgraded line and act.
                await StagePerformerBadge.Repin(seat.Pet, seat.Who, true);
            }
        }

        FurinaStagePlacement.Reflow(furina);
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
    private static async Task<Creature?> Field(Player player, StagePerformer who,
                                               bool upgraded = false)
    {
        try
        {
            var type = ModelFor(who);
            if (!ModelDb.Contains(type)) ModelDb.Inject(type);
            EnsureVisualsConverted(who);
            Creature pet = who switch
            {
                StagePerformer.Wriothesley =>
                    await PlayerCmd.AddPet<WriothesleyMonster>(player),
                StagePerformer.Lynette =>
                    await PlayerCmd.AddPet<LynetteMonster>(player),
                StagePerformer.Clorinde =>
                    await PlayerCmd.AddPet<ClorindeMonster>(player),
                StagePerformer.Lyney =>
                    await PlayerCmd.AddPet<LyneyMonster>(player),
                StagePerformer.Sigewinne =>
                    await PlayerCmd.AddPet<SigewinneMonster>(player),
                StagePerformer.Chevreuse =>
                    await PlayerCmd.AddPet<ChevreuseMonster>(player),
                StagePerformer.Freminet =>
                    await PlayerCmd.AddPet<FreminetMonster>(player),
                StagePerformer.Navia =>
                    await PlayerCmd.AddPet<NaviaMonster>(player),
                StagePerformer.Neuvillette =>
                    await PlayerCmd.AddPet<NeuvilletteMonster>(player),
                StagePerformer.Escoffier =>
                    await PlayerCmd.AddPet<EscoffierMonster>(player),
                _ => await PlayerCmd.AddPet<CharlotteMonster>(player),
            };
            // 2026-09-25: the body SAYS WHAT IT DOES. Hovering a creature
            // shows its powers' tips, and the base game gives Osty a quiet
            // badge the same way (`OstyCmd.Summon`, `DieForYouPower`); a
            // first-time player could not tell what any performer did.
            await StagePerformerBadge.Pin(pet, who, upgraded);
            return pet;
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
        StagePerformer.Wriothesley => typeof(WriothesleyMonster),
        StagePerformer.Lynette => typeof(LynetteMonster),
        StagePerformer.Clorinde => typeof(ClorindeMonster),
        StagePerformer.Lyney => typeof(LyneyMonster),
        StagePerformer.Sigewinne => typeof(SigewinneMonster),
        StagePerformer.Chevreuse => typeof(ChevreuseMonster),
        StagePerformer.Freminet => typeof(FreminetMonster),
        StagePerformer.Navia => typeof(NaviaMonster),
        StagePerformer.Neuvillette => typeof(NeuvilletteMonster),
        StagePerformer.Escoffier => typeof(EscoffierMonster),
        _ => typeof(CharlotteMonster),
    };

    /// <summary>Teach BaseLib that this performer's scene is an
    /// <c>NCreatureVisuals</c>. The whole argument -- why the library's own
    /// automatic pass cannot cover an INJECTED model, and why the Osty
    /// fallback must NOT be registered -- is written out on
    /// <c>BakeKuragePet.EnsureVisualsConverted</c>; this is the same door for
    /// the eleven performer scenes.</summary>
    private static void EnsureVisualsConverted(StagePerformer who)
    {
        if (_visualsRegistered.Contains(who)) return;
        if (StagePerformerMonster.ModVisualsPathFor(who) is not { } scene) return;
        _visualsRegistered.Add(who);
        scene.RegisterSceneForConversion<NCreatureVisuals>();
    }
}
