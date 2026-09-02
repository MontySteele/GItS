using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using BaseLib.Extensions;
using BaseLib.Patches.Content;
using BaseLib.Patches.Features;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Powers;

/// <summary>
/// DRAFT 6's RULE 1: <b>the Bake-Kurage is a pet on her side of the field for
/// the whole combat, and enemies cannot touch it. It is where a Plan is sent.</b>
///
/// A PET, AND THE ENGINE ALREADY HAS PETS. The 2026-09-02 decompile read
/// (brief sec.7) is what settled the shape: <c>Creature.PetOwner</c> /
/// <c>Creature.IsPet</c> exist, <c>PlayerCmd.AddPet&lt;T&gt;(Player)</c> spawns
/// one on the player's side, and the pet lives in <c>CombatState._allies</c>
/// for the whole fight. The Necrobinder's Osty is one; the relic pets Byrdpip
/// and Pael's Legion are two more.
///
/// UNTARGETABLE BY ENEMIES IS FREE, BY CONSTRUCTION -- not a flag, and there is
/// no flag to set. <c>MonsterModel.PerformMove</c> hands a move
/// <c>combatState.PlayerCreatures</c>, and <c>PlayerCreatures</c> is
/// <c>Creatures.Where(c => c.IsPlayer)</c>. A pet has no <c>Player</c>, so it
/// is never in an enemy's target list. Nothing here maintains that; it is what
/// being a pet MEANS.
///
/// NO HP BAR: <c>CustomPetModel(visibleHp: false)</c> plus the 9999-HP pool the
/// base library's own pets use (<c>Byrdpip</c> and <c>PaelsLegion</c> are both
/// <c>MinInitialHp =&gt; 9999; MaxInitialHp =&gt; 9999;
/// IsHealthBarVisible =&gt; false</c>). HP must be at least 1 and a dead pet is
/// removed, so a huge pool is how the game spells "this one does not die".
///
/// ITS PLACEMENT IS THE ENGINE'S, NOT BESPOKE CODE, and that is a finding
/// rather than a shortcut: <c>NCombatRoom.PositionPlayersAndPets</c> has an
/// Osty-specific branch (gated on <c>Character is Necrobinder</c>) and a
/// GENERIC one under it that lays every other pet out beside its owner --
/// which is the branch Byrdpip takes and the one this takes. The slice's sec.5
/// expected to write placement code; the engine did not need it.
///
/// IT WEARS THE MOD'S OWN JELLYFISH, not Osty's rig. <see cref="CustomVisualPath"/>
/// borrowed <c>creature_visuals/osty</c> while the pet was first built; it now points
/// at <see cref="ModVisualsResource"/>, a convention combat scene wrapped around the
/// SAME sprite the shipped <c>KurageSummonPower</c> already draws in the end-of-turn
/// docket -- <c>kokomi/summon/bake_kurage.png</c>, cut from the Bake-Kurage summon art
/// by <c>tools/cut_kurage_summon.py</c>. One producer, one silhouette, two consumers.
///
/// WHY A SCENE AND NOT A <c>CreateCustomVisuals</c> OVERRIDE: <c>MonsterModel.CreateVisuals</c>
/// is <c>PreloadManager.Cache.GetScene(VisualsPath).Instantiate&lt;NCreatureVisuals&gt;()</c>,
/// and BaseLib's <c>VisualsPath</c> prefix feeds it <c>CustomVisualPath</c>. The engine
/// wants a path. The scene is the SMALLEST <c>NCreatureVisualsFactory</c> accepts:
/// <c>%Visuals</c> is the one mandatory node (<c>NCreatureVisuals._Ready</c> hard-fetches
/// it and throws without it), and the factory GENERATES <c>%CenterPos</c>,
/// <c>IntentPos</c> and <c>%FormVfx</c> off <c>Bounds</c>. So the scene ships
/// <c>Visuals/Rig/Body</c>, a <c>Bounds</c> box and the animation pair, and lets the
/// library build the three markers it knows how to build.
///
/// <c>Bounds</c> IS THE PLACEMENT, which is why it is authored and not defaulted.
/// <c>NCombatRoom.PositionPlayersAndPets</c>'s generic branch puts a pet at
/// <c>-targetX + 20 - Bounds.Size.X * 0.5</c>, <c>player.Y + 10</c>: the box's WIDTH is
/// the only dial it reads, and the factory's default box is Klee-sized 240x280.
/// 120x160 is cut to the 64x128 sprite, so the jellyfish sits beside Kokomi rather than
/// a character-width step away, and floats 16px clear of the ground line.
///
/// STATIC ART PLUS THE SCENE'S OWN IDLE -- motion, not new art. The docket sprite does
/// not move; here <c>Visuals/Rig</c> carries a 3s bob and sway, and the
/// attack / hurt / death states <see cref="KleeMod.Vfx.CreatureAnimationRouter"/>
/// travels to. That is the same four-state scene contract Klee's and Furina's combat
/// scenes carry, driven by the same router, with no code anywhere that knows this
/// creature exists. No Spine rig is involved, so <c>MonsterModel.GenerateAnimator</c> is
/// never reached: <c>NCreature</c> builds <c>_spineAnimator</c> only when
/// <c>Visuals.HasSpineAnimation</c>, and <c>SetAnimationTrigger</c> is a no-op without it.
///
/// THE FALLBACK IS STILL OSTY, and deliberately. <c>KleePck.Path</c> returns null while
/// the pack is absent or stale; a null <c>CustomVisualPath</c> sends
/// <c>MonsterModel.VisualsPath</c> to an id-derived scene that does not exist, which is
/// the engine's error creature. Falling through to Osty's rig keeps the pre-repack
/// failure mode exactly what it was before this change.
/// </summary>
public sealed class BakeKurageMonster : CustomPetModel, ILocalizationProvider
{
    /// <summary>The mod's jellyfish creature scene, inside the pack.</summary>
    internal const string ModVisualsResource = "kokomi/model/bake_kurage.tscn";

    public BakeKurageMonster() : base(visibleHp: false)
    {
    }

    public override int MinInitialHp => 9999;

    public override int MaxInitialHp => 9999;

    /// <summary>
    /// The mod's own scene when the pack carries it, else null. Also what
    /// <see cref="BakeKuragePet.Summon"/> registers for node conversion -- the
    /// Osty fallback must NOT be registered, since it is already an
    /// <c>NCreatureVisuals</c> and the base game owns that path.
    /// </summary>
    internal static string? ModVisualsPath => KleePck.Path(ModVisualsResource);

    /// <summary>The mod's jellyfish; Osty's rig only while the pack is stale.
    /// See the class header.</summary>
    public override string? CustomVisualPath =>
        ModVisualsPath ?? SceneHelper.GetScenePath("creature_visuals/osty");

    public List<(string, string)>? Localization => new()
    {
        ("name", "Bake-Kurage"),
        ("title", "Bake-Kurage"),
    };
}

/// <summary>
/// The jellyfish's lifecycle: one spawn per combat, and one way to find it.
/// </summary>
public static class BakeKuragePet
{
    /// <summary>
    /// Is this creature HER jellyfish? Asked by the generated cards' play
    /// branch through <c>KokomiPlan.PlayedOnPet</c>, and by the relic.
    ///
    /// THE TYPE TEST IS THE WHOLE TEST. A creature carrying this monster model
    /// is a pet by construction -- nothing else spawns one -- and asking for
    /// the model rather than for `IsPet` keeps a future second pet (a
    /// companion's, a relic's) from swallowing a Plan.
    /// </summary>
    public static bool Is(Creature? creature) =>
        creature?.Monster is BakeKurageMonster;

    /// <summary>This seat's jellyfish, or null.</summary>
    public static Creature? Of(Creature? kokomi) =>
        kokomi?.Player?.PlayerCombatState?.Pets.FirstOrDefault(Is);

    /// <summary>
    /// RULE 1's install: the jellyfish is out from the start of every combat.
    ///
    /// IDEMPOTENT, and called from the combat-start hook only. The model is
    /// INJECTED on first use rather than registered at boot because
    /// <c>AbstractModel</c>'s constructor does not add to <c>ModelDb</c> --
    /// <c>ModelDb.Inject</c> is the door the engine documents for mods, and it
    /// is itself guarded by <c>Contains</c>, so calling it every combat costs
    /// one dictionary lookup and cannot double-register.
    /// </summary>
    public static async Task Summon(Player? player)
    {
        if (player == null) return;
        if (!KokomiOverhaul.LiveFor(player.Creature)) return;
        if (Of(player.Creature) != null) return;
        if (!ModelDb.Contains(typeof(BakeKurageMonster)))
        {
            ModelDb.Inject(typeof(BakeKurageMonster));
        }
        EnsureVisualsConverted();
        await PlayerCmd.AddPet<BakeKurageMonster>(player);
        LogHitboxProbe(player);
    }

    /// <summary>
    /// `EB-296`'s probe: one line per combat, kept in the build on purpose.
    ///
    /// The wire supplies its target explicitly, so no scenario and no seat can
    /// ever see a hitbox defect -- the whole class of "the card resolves but
    /// you cannot AIM it" is invisible to every automated arm this repo has.
    /// This prints the numbers that decide it, for the pet and for one enemy
    /// beside it as the control: whether the hitbox node exists, its size and
    /// global position (which come from the visuals scene's <c>Bounds</c> box
    /// through <c>NCreature.UpdateBounds</c>), and the two flags
    /// <c>NCreature.ToggleIsInteractable</c> writes -- <c>MouseFilter</c>,
    /// which decides the drag, and <c>FocusMode</c>, which decides the D-pad.
    /// A future report of "it will not take my drop" is then one grep of
    /// godot.log rather than a session.
    /// </summary>
    private static void LogHitboxProbe(Player player)
    {
        try
        {
            var room = NCombatRoom.Instance;
            if (room == null) return;

            var pet = room.GetCreatureNode(Of(player.Creature));
            var enemy = room.CreatureNodes.FirstOrDefault(
                n => n?.Entity?.IsEnemy == true);
            Log.Info($"[{KleeMod.ModId}] EB-296 hitbox probe: "
                   + $"pet[{Describe(pet)}] enemy[{Describe(enemy)}]");
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] EB-296 hitbox probe failed: {e}");
        }
    }

    private static string Describe(NCreature? node)
    {
        if (node == null) return "no node";
        var hitbox = node.Hitbox;
        var who = node.Entity?.Monster?.GetType().Name ?? "?";
        if (hitbox == null) return $"{who} no hitbox";
        return $"{who} {hitbox.GetType().Name} size={hitbox.Size} "
             + $"pos={hitbox.GlobalPosition} mouse={hitbox.MouseFilter} "
             + $"focus={hitbox.FocusMode} interactable={node.IsInteractable}";
    }

    private static bool _visualsRegistered;

    /// <summary>
    /// Teach BaseLib that the pet's scene is an <c>NCreatureVisuals</c>.
    ///
    /// WITHOUT THIS THE JELLYFISH IS THE ERROR CREATURE, and silently:
    /// <c>MonsterModel.CreateVisuals</c> does
    /// <c>GetScene(path).Instantiate&lt;NCreatureVisuals&gt;()</c> against a
    /// script-less <c>Node2D</c> scene (pck-src rule: no scripts in pck scenes),
    /// which is an invalid cast that <c>CreateVisuals</c>'s own catch turns into the
    /// fallback creature. BaseLib's <c>SceneConversionPatch</c> is what makes the cast
    /// succeed, and it only converts scenes REGISTERED with <c>NodeFactory</c>.
    ///
    /// THE LIBRARY'S OWN AUTOMATIC PASS CANNOT COVER US, which is why this is here and
    /// not free like it is for Klee: <c>PostModInitPatch.RegisterSceneConversions</c>
    /// runs on <c>ModelDb.Preload</c> and calls
    /// <c>ModelDb.GetById(...) as ISceneConversions</c> -- a null-conditional on a model
    /// that is not in <c>ModelDb</c> yet. This model is INJECTED at first combat (see
    /// <see cref="Summon"/>), so at that pass it is not there and the registration is a
    /// no-op. Registering here, one call before the pet exists, is the same door
    /// (<c>CustomMonsterModel.RegisterSceneConversions</c> is this one line) opened at a
    /// moment the model is real.
    ///
    /// Guarded by a bool rather than left to run per combat only because the registry
    /// logs a line on every write; the write itself is an idempotent dictionary
    /// assignment. The Osty fallback is deliberately NOT registered -- it is a
    /// base-game scene that already instantiates as <c>NCreatureVisuals</c>.
    /// </summary>
    private static void EnsureVisualsConverted()
    {
        if (_visualsRegistered) return;
        if (BakeKurageMonster.ModVisualsPath is not { } scene) return;
        _visualsRegistered = true;
        scene.RegisterSceneForConversion<NCreatureVisuals>();
    }
}

/// <summary>
/// THE THREE TARGET SPELLINGS a Plan card can declare, and only one of them is
/// new.
///
/// The base library already ships <c>CustomTargetType.Pet</c> ("your live pet")
/// and <c>CustomTargetType.PetOrSelf</c>, with the whole vanilla gate chain
/// prefixed for them -- <c>IsValidTargetPatch</c> and
/// <c>CanPlayTargetingPatch</c> on <c>CardModel</c>,
/// <c>TargetSelectionPatch</c> on <c>NMouseCardPlay</c>,
/// <c>AllowedToTargetCreaturePatch</c> on <c>NTargetManager</c>, and the
/// controller and reticle patches. So drag-to-target, playability and the
/// multiplayer action all work unmodified for those two.
///
/// WHAT DRAFT 6 NEEDED THAT DID NOT EXIST is the middle case: an Attack (or a
/// Skill that debuffs) whose now-line aims at an enemy and whose Plan line goes
/// to the jellyfish -- Slack Water, Feint, Exposed Flank, Sango Isshin, Rally.
/// <see cref="PetOrEnemy"/> is that one, minted through the same
/// <c>[CustomEnum]</c> seam the library mints its own with and registered on
/// the same <c>ModelDb.Init</c> postfix, so it rides every patch above without
/// one line of new UI code.
///
/// A POSTFIX, NOT A PREFIX. The value is GENERATED by BaseLib's own
/// <c>ModelDb.Init</c> PREFIX (<c>GenEnumValues</c> scans every mod type for
/// <c>[CustomEnum]</c> fields and assigns), so the predicate can only be
/// registered afterwards -- registering against an unassigned field would key
/// the table on <c>TargetType.None</c>.
/// </summary>
public static class KokomiTargets
{
    /// <summary>"An enemy or the Bake-Kurage."</summary>
    [CustomEnum(null)]
    public static TargetType PetOrEnemy;

    /// <summary>"The Bake-Kurage." The base library's own; named here so a
    /// generated card names ONE class for all three spellings.</summary>
    public static TargetType PetOnly => CustomTargetType.Pet;

    /// <summary>"You or the Bake-Kurage." The base library's own.</summary>
    public static TargetType PetOrSelf => CustomTargetType.PetOrSelf;

    /// <summary>
    /// The predicate. Deliberately the UNION of the library's two rather than a
    /// re-derivation: an enemy is anything alive on the other side, and the pet
    /// half is <c>CustomTargetType.Pet</c>'s own clause word for word.
    /// </summary>
    public static void Register()
    {
        if (CustomTargetType.IsCustomSingleTargetType(PetOrEnemy)) return;
        CustomTargetType.RegisterSingleTargetType(
            PetOrEnemy,
            (Creature target, Player player) =>
                (target.IsAlive && target.IsEnemy)
                || (target.IsAlive && target.IsPet && target.PetOwner == player));
    }
}

/// <summary>
/// Registers <see cref="KokomiTargets.PetOrEnemy"/>'s predicate, in the same
/// postfix slot BaseLib registers its own thirteen in. Applied through
/// <c>KleePatchBootstrap</c> like every other patch class in this mod, so a
/// rename that breaks it is named at boot rather than silently dropped.
/// </summary>
// lint: no-seat: model-registry setup, not combat. It runs once at
// `ModelDb.Init`, before any run exists, and its whole body registers one
// TargetType predicate -- there is no creature to scope to and no seat to
// resolve, which is exactly what the exemption is for.
[HarmonyPatch(typeof(ModelDb), "Init")]
internal static class KokomiTargetTypeInitPatch
{
    [HarmonyPostfix]
    public static void Postfix() => KokomiTargets.Register();
}
