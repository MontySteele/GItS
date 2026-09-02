using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using BaseLib.Patches.Content;
using BaseLib.Patches.Features;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;

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
/// THE ART IS A PLACEHOLDER, named as one (slice sec.7: "Art for the pet beyond
/// a placeholder" is out of scope). <see cref="CustomVisualPath"/> borrows
/// Osty's creature-visuals scene, which is the base game's own pet rig and
/// carries every animation state <c>MonsterModel.GenerateAnimator</c> asks for
/// (<c>idle_loop</c>, <c>cast</c>, <c>attack</c>, <c>hurt</c>, <c>die</c>). A
/// missing scene would fall back to the engine's error creature rather than
/// throw, so the failure mode of getting this wrong is visible, not fatal.
/// </summary>
public sealed class BakeKurageMonster : CustomPetModel, ILocalizationProvider
{
    public BakeKurageMonster() : base(visibleHp: false)
    {
    }

    public override int MinInitialHp => 9999;

    public override int MaxInitialHp => 9999;

    /// <summary>Placeholder art: the base game's own pet rig. See the class
    /// header.</summary>
    public override string? CustomVisualPath =>
        SceneHelper.GetScenePath("creature_visuals/osty");

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
        await PlayerCmd.AddPet<BakeKurageMonster>(player);
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
