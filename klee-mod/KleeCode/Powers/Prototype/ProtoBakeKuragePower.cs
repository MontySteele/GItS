using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// THE OVERHAUL'S BAKE-KURAGE MARKER (draft 6 rules 1 and 2).
///
/// WHAT THIS IS NOT ANY MORE. Under draft 2 this power WAS the jellyfish: it
/// held the Tide, it was the badge, and the creature did not exist. Draft 6
/// makes the Bake-Kurage a real pet on the field
/// (<see cref="BakeKuragePet"/>), and the Tide is cut by the ruled brief's
/// sec.6 by name -- so what is left here is one job and it is a real one.
///
/// IT HOSTS THE PLAN QUEUE'S RESOLUTION, and it hosts it for a reason the Klee
/// arm could not use: <c>KleeOverhaulLedger</c>'s header explains that under
/// its rule 7 there is no power guaranteed to be on Klee, so its turn boundary
/// had to roll on a round stamp. Here rule 1 GUARANTEES this power is on her
/// for every turn of every combat, so the turn-start hook the Plans need can
/// hang off it honestly.
///
/// WHY NOT ON THE PET. The pet is a creature and a creature can be removed --
/// and a torn-down host would take the drain with it, silently, on the one turn
/// the player was counting on. The queue is per PLAYER
/// (<see cref="KokomiPlan"/>), so its resolution belongs on the player too. The
/// pet is where a Plan is SENT and where the strip is drawn; it is not the
/// bookkeeping.
///
/// THE AMOUNT IS A PRESENCE MARKER pinned at 1: a
/// <see cref="PowerStackType.Counter"/> at zero stacks is a power the game may
/// tear down, and rule 1 says the jellyfish is on the field for the WHOLE
/// combat.
/// </summary>
public sealed class ProtoBakeKuragePower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for any model implementing this
    /// interface, so the loc lives here and cannot drift from the id.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bake-Kurage"),
        ("description",
            "The jellyfish is on the field for the whole combat and enemies "
          + "cannot touch it. Play a card with a [gold]Plan[/gold] line on it "
          + "and the jellyfish carries that line out at the start of your next "
          + "turn."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: the badge shows a number, not a countdown.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// RULE 2's resolution point: the Plans she wrote last turn happen at the
    /// START of this one.
    ///
    /// <c>AfterPlayerTurnStart</c>, AND NOT THE PRE-DRAW HOOK THE SLICE'S sec.2
    /// PROSE ASKS FOR -- a reading, recorded here because the pool's own cards
    /// are what settle it against the wording, and draft 6 did not change that
    /// arithmetic.
    ///
    /// The game's turn-start order is fixed and written down
    /// (<c>tier0/tests/test_reaction_phase_parity.TURN_START_BROADCAST_ORDER</c>,
    /// read off the decompile): <c>BeforeSideTurnStart</c>, BLOCK CLEAR,
    /// <c>AfterBlockCleared</c>, ENERGY RESET, HAND DRAW,
    /// <c>AfterPlayerTurnStart</c>. There is NO broadcast between the energy
    /// reset and the draw. So a Plan resolved "before draw" resolves before the
    /// block clear and the energy reset too, and Read the Field's "Plan: Gain 8
    /// Block", Coral Bulwark's, Cleansing Wave's and Battle Plan's "Plan: Gain
    /// 2 Energy" would all be wiped by the turn setup that follows them -- five
    /// of the sixteen Plan rows, silently doing nothing.
    ///
    /// What the later hook costs is one turn's card ORDER: a Plan-drawn card
    /// (Stolen Chapter, Battle Plan) arrives after the turn's hand rather than
    /// before it. Nothing in the slice reads that difference, and it is the
    /// only clause of "before you draw" that any card can tell apart.
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        await KokomiPlan.ResolveAll(choiceContext, Owner);
    }
}

/// <summary>
/// THE ARM'S RULES, in one place: the jellyfish's install, <b>Mend</b>, and the
/// one damage formula a card does not print as a literal.
///
/// EVERY CARD REACHES A RULE THROUGH EXACTLY ONE CALL HERE, which is the same
/// discipline <c>ProtoBombPower</c>'s static face keeps and for the same
/// reason: the rules live in one file, so a card cannot express a VARIANT of a
/// rule by being generated differently, and the entry-HP cap cannot be
/// forgotten at one call site out of four.
///
/// DRAFT 2's VERBS ARE GONE, not switched off: Tide, Surge, Exert, the pulse,
/// the Garment, Strength-to-Tide, Orders and Tactics are cut by the ruled
/// brief's sec.6 by name. A method left standing for a retired rule is a call
/// site waiting to reappear.
/// </summary>
public static class KokomiRules
{
    /// <summary>This creature's Bake-Kurage marker, or null.</summary>
    public static ProtoBakeKuragePower? Marker(Creature? kokomi) =>
        kokomi?.Powers.OfType<ProtoBakeKuragePower>().FirstOrDefault();

    /// <summary>
    /// RULE 1's install. Idempotent, and called from two places for the reason
    /// the Kurage's memory installs from two: the combat-start hook is the
    /// braces and the turn-start one is the belt, so a combat whose setup order
    /// ever moves still opens with a jellyfish rather than silently without
    /// one.
    ///
    /// THE PET IS SUMMONED HERE TOO, so the marker and the creature have one
    /// lifetime and one entry point. A fight that had one without the other
    /// would be a fight in which either the Plans do not resolve or there is
    /// nothing to aim them at, and neither failure says so on screen.
    /// </summary>
    public static async Task Install(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        await BakeKuragePet.Summon(kokomi!.Player);
        if (Marker(kokomi) != null) return;
        await PowerCmd.Apply<ProtoBakeKuragePower>(
            new ThrowingPlayerChoiceContext(), kokomi, 1,
            applier: kokomi, cardSource: null, silent: true);
    }

    private static ICombatState? _combat;

    /// <summary>
    /// STASH ONLY, and it is the arrangement <c>KurageMemory.NoteCombat</c>
    /// already has for the same reason: <c>KokomiResourceHooks.Subscribe</c> is
    /// the one place the mod is handed a <c>CombatState</c>, but the game
    /// re-enumerates its hook listeners on EVERY hook broadcast, so that
    /// delegate is not a per-fight seam. The per-fight work is
    /// <see cref="InstallAll"/>'s, called from <c>BeforeCombatStart</c>.
    /// </summary>
    public static void NoteCombat(ICombatState? combat) => _combat = combat;

    /// <summary>The combat this arm last saw. Read by the HUD teardown,
    /// which is handed no state of its own -- the same accessor
    /// <c>KurageMemory.Combat</c> exists for.</summary>
    public static ICombatState? Combat => _combat;

    /// <summary>Every seat in this combat opens with a jellyfish and a captured
    /// entry HP. Twin of <c>KurageMemory.InstallAll</c>, called from the same
    /// hook and for the same reason.</summary>
    public static async Task InstallAll()
    {
        var combat = _combat;
        if (combat == null) return;
        foreach (var player in combat.Players)
        {
            var creature = player.Creature;
            if (creature == null) continue;
            // ENTRY HP FIRST, AND FOR EVERY SEAT EITHER ARM REACHES. The Mend
            // cap is the HP the fighter WALKED IN WITH (brief sec.14), and this
            // hook runs before the first turn opens, so this is the only moment
            // in the fight at which that number is simply their current HP.
            //
            // THE COMPANION ARM NEEDS IT TOO, and that is the whole reason this
            // is not inside the Kokomi guard: Mizuki's Anraku Secret Spring
            // Therapy is a UNIVERSAL that prints Mend, so a Klee holding it must
            // have a ceiling captured at the same moment hers is.
            if (MendIsLive(creature))
            {
                KokomiOverhaulLedger.OpenCombat(creature);
            }
            if (!KokomiOverhaul.LiveFor(creature)) continue;
            await Install(creature);
        }
    }

    // ---- the one formula a card does not print ----------------------------

    /// <summary>
    /// Sango Isshin's "a quarter of your Max HP", rounded DOWN.
    ///
    /// ONE function, and it is public for the Furina legibility lesson: a
    /// preview and an effect that compute separately will eventually disagree,
    /// and the player believes the preview. Both the now-line and the planned
    /// all-enemies half read this, so they cannot round differently.
    /// </summary>
    public static int QuarterOfMaxHp(Creature? kokomi) =>
        kokomi == null ? 0 : (int)kokomi.MaxHp / 4;

    /// <summary>Sango Isshin's now-line: the quarter, at the enemy she aimed
    /// at, Hydro through the shared pipeline so Strength, the aura and the
    /// reaction all behave as they do on any Attack of hers.</summary>
    public static async Task QuarterMaxHp(
        PlayerChoiceContext choiceContext, Creature? kokomi, Creature? target)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var amount = QuarterOfMaxHp(kokomi);
        if (amount <= 0 || target == null || target.IsDead) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro, amount, kokomi);
    }

    /// <summary>The same, at every living enemy. Snapshotted before the first
    /// hit, so an enemy the volley kills does not change who is in it.</summary>
    public static async Task QuarterMaxHpAll(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var amount = QuarterOfMaxHp(kokomi);
        var combat = kokomi!.CombatState;
        if (amount <= 0 || combat == null) return;
        foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                    .ToList())
        {
            if (enemy.IsDead) continue;
            await ElementalHit.Deal(
                choiceContext, enemy, Element.Hydro, amount, kokomi);
        }
    }

    // ---- the Mend rule ----------------------------------------------------

    /// <summary>
    /// Is MEND live for this creature? The keyword belongs to the Kokomi arm
    /// and its rule is that arm's, but the CARDS that print it are not all
    /// hers: the approved Inazuma companion workshop makes Mizuki's Anraku
    /// Secret Spring Therapy a UNIVERSAL, and "the one true heal in the pool"
    /// has to be the same keyword with the same bound in whoever's hands it
    /// lands -- Klee's and Furina's included.
    ///
    /// SO THE GATE WIDENED AND THE RULE DID NOT. <see cref="Mend"/> below is
    /// still the one place "never above the HP you entered the fight with" is
    /// written, and no second Mend was authored for the companion pool.
    ///
    /// A CREATURE WITH NO PLAYER IS NEVER MENDED. An enemy has no entry HP in
    /// this ledger and no card of theirs prints the keyword, so the guard is
    /// what keeps a widened gate from becoming an open one.
    /// </summary>
    internal static bool MendIsLive(Creature? creature) =>
        KokomiOverhaul.LiveFor(creature)
        || (CompanionOverhaul.Enabled && creature?.Player != null);

    /// <summary>
    /// MEND: heal, never above entry HP. Returns the HP that actually landed.
    ///
    /// ONE FUNCTION, and every Mend in the arm goes through it -- two Rares, a
    /// planned clause and a companion Universal -- because "never above entry
    /// HP" is the rule that makes the whole healing bound work (brief sec.2,
    /// LAW's card-sheet rules) and a second implementation of it is how the
    /// bound would eventually come off one of them.
    /// </summary>
    public static async Task<int> Mend(
        PlayerChoiceContext choiceContext, Creature? kokomi, int amount)
    {
        if (!MendIsLive(kokomi) || amount <= 0) return 0;

        var entry = KokomiOverhaulLedger.For(kokomi!).EntryHp;
        var room = entry - (int)kokomi!.CurrentHp;
        var landed = room > 0 ? System.Math.Min(amount, room) : 0;

        if (landed > 0)
        {
            await CreatureCmd.Heal(kokomi, landed);
        }

        return landed;
    }
}
