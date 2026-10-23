using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The four Fontaine 5-star Rares (R64, 2026-07-25). Sim is LAW: each of these
/// mirrors a tier0 power by name, and the amounts live on the card, not here,
/// so there is nothing for the constant-parity lint to drift on.
/// </summary>

/// <summary>
/// Navia, Cannon Fire Support (the Fontaine pool rework, 2026-10-19,
/// <c>review/active/fontaine-companions-2026-10-19.md</c>): "At the start of
/// your turn, deal 5 [7] Geo damage to ALL enemies." It gained Block after a
/// reaction until the rework (the lowest Rare take, 3%).
///
/// Amount IS the damage, so copies add. Each hit is the arm's power-sourced
/// elemental hit (<see cref="ElementalHit.Deal"/>), so on an aura it is a
/// Crystallize and pays that reaction's Block, as the paper says. Every
/// living hittable enemy, in board order, read once before the volley. Sim
/// twin: the `cannon_fire_support` read in
/// `effects.player_turn_start_triggers`, beside Neuvillette's.
/// </summary>
public sealed class CannonFireSupportPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Cannon Fire Support"),
        ("description",
            "At the start of your turn, deal [blue]{Amount}[/blue] "
          + "[gold]Geo[/gold] damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner || Amount <= 0) return;
        var enemies = Owner.CombatState?.HittableEnemies
            .Where(e => e.IsAlive).ToList();
        if (enemies == null || enemies.Count == 0) return;
        Flash();
        foreach (var enemy in enemies)
        {
            if (!enemy.IsAlive) continue;
            await ElementalHit.Deal(
                choiceContext, enemy, Elements.Element.Geo, Amount, Owner);
        }
    }
}

/// <summary>
/// Clorinde, Night Vigil: your Attacks against enemies holding an aura deal
/// +Amount.
///
/// DELIBERATE MIRROR of <c>SolarIsotomaPower</c> (retired): same trigger ("my
/// attack lands on an aura'd enemy"), opposite currency -- Albedo pays Block,
/// Clorinde pays damage. Recorded here and on the sheet so the pairing reads
/// as design rather than as one being a copy of the other.
///
/// Read in ModifyDamageAdditive, which runs before the hit resolves and so
/// before the aura it keys on is consumed -- the identical ordering constraint
/// Solar Isotoma has, for the identical reason.
/// </summary>
public sealed class NightVigilPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Night Vigil"),
        ("description",
            "Your Attacks against enemies with an aura deal "
          + "[blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner || target == null) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (AuraCmd.Find(target) == null) return 0m;
        return Amount;
    }
}

/// <summary>
/// Neuvillette, Heir to the Ancient Sea's Authority: at the start of your
/// turn, apply Hydro to a random enemy; auras you apply last Amount extra
/// turns.
///
/// The duration half has no hook of its own -- AuraCmd.Duration reads it at
/// the one place aura duration is decided, which is why that helper exists.
///
/// CO-OP NOTES PICK 4 ([USER], 2026-10-02, "Agreed on Neuvillette's a)"):
/// the card was a 5-star Rare that did nothing by itself, so it now applies
/// Hydro each turn as well, a free reaction partner for any kit. That
/// reverses the old "authority over water, not more water" line, which kept
/// it off Hydro for the mass-Frozen watchlist; the ruling is the newer fact.
/// Amount counts copies (the upgrade is a cost cut), so each copy hits
/// once.
///
/// 2026-10-11 COMPANION PASS: the Hydro became "deal 5 Hydro damage to a
/// random enemy" (<see cref="CompanionConstants.AncientSeaDamage"/>), a
/// powered hit through <see cref="ElementalHit.Deal"/>, so the damage lays
/// the Hydro and reacts and credits as any companion hit does. Sim twin: the
/// `ancient_sea_authority` read in `effects.player_turn_start_triggers`.
/// </summary>
public sealed class AncientSeaAuthorityPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Heir to the Ancient Sea's Authority"),
        ("description",
            "At the start of your turn, deal "
          + $"[blue]{CompanionConstants.AncientSeaDamage}[/blue] "
          + "[gold]Hydro[/gold] damage to a random "
          + "enemy. Auras you apply last [blue]{Amount}[/blue] "
          + "additional {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await HitHydro(choiceContext, player);
    }

    /// <summary>The turn's Hydro hit: one random hittable enemy per copy.
    /// </summary>
    internal async Task HitHydro(PlayerChoiceContext choiceContext, Player player)
    {
        for (var i = 0; i < Amount; i++)
        {
            var enemies = Owner.CombatState?.HittableEnemies
                .Where(e => e.IsAlive).ToList();
            if (enemies == null || enemies.Count == 0) return;
            var target = player.RunState.Rng.CombatTargets.NextItem(enemies);
            if (target == null) return;
            Flash();
            await ElementalHit.Deal(
                choiceContext, target, Elements.Element.Hydro,
                CompanionConstants.AncientSeaDamage, Owner);
        }
    }

    /// <summary>Extra aura turns this creature grants, 0 if none.</summary>
    public static int ExtraTurnsFrom(Creature? applier) =>
        applier?.Powers.OfType<AncientSeaAuthorityPower>()
            .FirstOrDefault()?.Amount ?? 0;
}

/// <summary>
/// Arlecchino, Masque of the Red Death (2026-10-11 Companion pass): "At the
/// start of your turn, lose 1 HP and gain 1 Strength." Amount is Strength per
/// turn -- a ratchet, like Nicole's celestial_gift -- and the HP is a flat
/// <see cref="CompanionConstants.MasqueHpLoss"/> that does not scale with it.
/// The HP first, as printed: the base game's self-damage shape (Offering's,
/// unblockable and unpowered). The Bond of Life Block clause, and the
/// end-of-turn payment that carried it, left in the same pass.
///
/// Strength is granted through the ordinary power path, which is what makes
/// Kokomi's LAW 3 chokepoint convert it to Charge for her without a
/// special case anywhere. Sim twin: the `masque_red_death` read in
/// `effects.player_turn_start_triggers`.
/// </summary>
public sealed class MasqueRedDeathPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Masque of the Red Death"),
        ("description",
            "At the start of your turn, lose "
          + $"[blue]{CompanionConstants.MasqueHpLoss}[/blue] HP and gain "
          + "[blue]{Amount}[/blue] [gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        Flash();
        await CreatureCmd.Damage(
            choiceContext, Owner, CompanionConstants.MasqueHpLoss,
            ValueProp.Unblockable | ValueProp.Unpowered, dealer: null,
            cardSource: null, cardPlay: null);
        if (!Owner.IsAlive) return;
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, Owner, Amount, applier: Owner, cardSource: null);
    }
}
