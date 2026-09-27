#if PROTOTYPE_CARDS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// KLEE'S OWN RELICS, the Klee arm's pool
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>, ruled
/// 2026-09-27 at the defaults). The base game's shape: one Common, two
/// Uncommons, three Rares and one Shop relic beside the starter. Under the arm
/// they and the starter and the Ancient are her whole relic pool, and the
/// Silent borrow goes (<see cref="KleeRelicPool"/>).
///
/// QUARANTINED for Salon Solitaire's reason: the whole file is inside
/// <c>#if PROTOTYPE_CARDS</c> and lives under <c>Relics/</c>, so the relic
/// names stay in <c>tools/lint_unique_names.py</c>'s namespace. Every effect
/// early-returns with the arm off, so a relic granted by hand to an arm-off
/// Klee does nothing it does not print.
/// </summary>
public static class KleeArmRelics
{
    /// <summary>The seven, in the paper's table order. The pool reads this
    /// list and nothing else.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(DodocoCharm), typeof(CloverCharm), typeof(FreshCatch),
        typeof(AlicesGuidebook), typeof(FireworksStand), typeof(AlicesTeapot),
        typeof(DodocoArmy),
    };

    /// <summary>How many copies of <typeparamref name="T"/> this Klee holds,
    /// with the arm on; 0 otherwise.</summary>
    internal static int Held<T>(Creature? klee) where T : RelicModel =>
        KleeOverhaul.Enabled && klee?.Player is { } player
            ? player.Relics.OfType<T>().Count()
            : 0;

    internal static string Icon(string slug) => "klee/relics/" + slug + ".png";
}

/// <summary>Common. "Whenever you place a Bomb, it is 1 bigger." Paid at
/// <see cref="ProtoBombPower.Place"/>, the one door every placement takes; a
/// jump, a merge and a split move a Bomb and are not paid.</summary>
public sealed class DodocoCharm : CustomRelicModel
{
    public const int Bonus = 1;

    public DodocoCharm() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Dodoco Charm"),
        ("description",
            "Whenever you place a [gold]Bomb[/gold], it is [blue]" + Bonus
          + "[/blue] bigger."),
    };

    /// <summary>The size a placement by <paramref name="applier"/> gains.
    /// Copies add.</summary>
    public static int BonusFor(Creature? applier) =>
        Bonus * KleeArmRelics.Held<DodocoCharm>(applier);

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("dodoco_charm")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("dodoco_charm")) ?? base.BigIconPath;
}

/// <summary>Uncommon. "Whenever one of your Mines goes off, gain 3 Block."
/// Called from <c>ProtoBombPower.Explode</c>'s Mine branch, whatever set the
/// Mine off, so a Mine answering an attack blocks part of that attack.</summary>
public sealed class CloverCharm : CustomRelicModel
{
    public const int Block = 3;

    public CloverCharm() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Clover Charm"),
        ("description",
            "Whenever one of your [gold]Mines[/gold] goes off, gain [blue]"
          + Block + "[/blue] [gold]Block[/gold]."),
    };

    /// <summary>The Block one Mine going off pays its placer: 3 a copy.
    /// </summary>
    public static int BlockFor(Creature? applier) =>
        Block * KleeArmRelics.Held<CloverCharm>(applier);

    public static async Task AfterMineWentOff(Creature applier)
    {
        var block = BlockFor(applier);
        if (block <= 0 || applier.IsDead) return;
        foreach (var relic in applier.Player!.Relics.OfType<CloverCharm>())
        {
            relic.Flash();
        }
        await CreatureCmd.GainBlock(applier, block, ValueProp.Unpowered, null,
                                    fast: true);
    }

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("clover_charm")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("clover_charm")) ?? base.BigIconPath;
}

/// <summary>Uncommon. "At the start of each combat, apply Hydro to a random
/// enemy." One free aura a fight for the React plan, through the shared
/// element funnel, on her first turn.</summary>
public sealed class FreshCatch : CustomRelicModel
{
    public FreshCatch() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Fresh Catch"),
        ("description",
            "At the start of each combat, apply [gold]Hydro[/gold] to a random "
          + "enemy."),
    };

    /// <summary>The turn-one gate, shared with <see cref="DodocoArmy"/>: her
    /// own first turn, with the arm on.</summary>
    public static bool FirstTurnOf(RelicModel relic, Player player) =>
        KleeOverhaul.Enabled && player == relic.Owner
        && player.PlayerCombatState?.TurnNumber == 1
        && player.Creature is { IsDead: false };

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!FirstTurnOf(this, player)) return;
        var combat = player.Creature.CombatState;
        if (combat == null) return;
        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (target == null) return;
        Flash();
        await ElementalHit.ApplyOnly(choiceContext, target, Element.Hydro,
                                     player.Creature);
    }

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("fresh_catch")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("fresh_catch")) ?? base.BigIconPath;
}

/// <summary>Rare. "At the start of your turn, your largest Bomb grows 3
/// more." Late in the turn start, after rule 1's growth and the turn-start
/// placements, so "largest" is read off the board the turn opened on. From
/// her second turn: on the first there is no growth for it to add to.</summary>
public sealed class AlicesGuidebook : CustomRelicModel
{
    public const int Growth = 3;

    public AlicesGuidebook() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Guidebook"),
        ("description",
            "At the start of your turn, your largest [gold]Bomb[/gold] grows "
          + "[blue]" + Growth + "[/blue] more."),
    };

    public override Task AfterPlayerTurnStartLate(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!KleeOverhaul.Enabled || player != Owner) return Task.CompletedTask;
        if ((player.PlayerCombatState?.TurnNumber ?? 0) < 2) return Task.CompletedTask;
        if (player.Creature is not { IsDead: false } klee) return Task.CompletedTask;
        if (ProtoBombPower.GrowLargest(klee, Growth) > 0) Flash();
        return Task.CompletedTask;
    }

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("alices_guidebook")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("alices_guidebook")) ?? base.BigIconPath;
}

/// <summary>Rare. "Whenever one card sets off 3 or more Bombs, gain 1
/// energy." Counts her explosions between the card's own before- and
/// after-play hooks, off the arm's explosion bus, and pays once per card.
/// </summary>
public sealed class FireworksStand : CustomRelicModel, IProtoExplosionListener
{
    public const int Threshold = 3;
    public const int Energy = 1;

    private bool _inPlay;
    private int _setOffThisPlay;

    public FireworksStand() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Fireworks Stand"),
        ("description",
            "Whenever one card sets off [blue]" + Threshold + "[/blue] or more "
          + "[gold]Bombs[/gold], gain [blue]" + Energy + "[/blue] "
          + "[gold]Energy[/gold]."),
    };

    /// <summary>Explosions counted for the card being played. Read by the
    /// tests.</summary>
    public int SetOffThisPlay => _setOffThisPlay;

    private bool IsMine(CardPlay cardPlay) =>
        KleeOverhaul.Enabled && cardPlay.Card?.Owner == Owner;

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (!IsMine(cardPlay)) return Task.CompletedTask;
        _inPlay = true;
        _setOffThisPlay = 0;
        return Task.CompletedTask;
    }

    public Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (_inPlay && applier.Player == Owner) _setOffThisPlay++;
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!IsMine(cardPlay) || !_inPlay) return;
        _inPlay = false;
        var count = _setOffThisPlay;
        _setOffThisPlay = 0;
        if (!Pays(count)) return;
        Flash();
        await PlayerCmd.GainEnergy(Energy, Owner);
    }

    /// <summary>The rule: one card, three or more.</summary>
    public static bool Pays(int setOffByOneCard) => setOffByOneCard >= Threshold;

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("fireworks_stand")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("fireworks_stand")) ?? base.BigIconPath;
}

/// <summary>Rare. "The first Bomb you set off each turn reacts as if its enemy
/// had Hydro." React without a companion. Taken at
/// <c>ProtoBombPower.Explode</c>, on the players' turn only (a Mine answering
/// an attack is not one she set off), once a turn on the arm's ledger; the hit
/// goes through <c>ElementalHit.DealAsIfAura</c>, which consumes nothing real.
/// </summary>
public sealed class AlicesTeapot : CustomRelicModel
{
    public AlicesTeapot() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Teapot"),
        ("description",
            "The first [gold]Bomb[/gold] you set off each turn reacts as if its "
          + "enemy had [gold]Hydro[/gold]."),
    };

    /// <summary>Would the next Bomb <paramref name="applier"/> sets off take
    /// the Teapot? The badge's read, which spends nothing: held, the arm on,
    /// the players' turn, and this turn's Teapot unspent. <c>TakeFor</c>'s
    /// gate less the element, which the badge prices as Pyro.</summary>
    public static bool Pending(Creature? applier) =>
        applier != null
        && KleeArmRelics.Held<AlicesTeapot>(applier) > 0
        && applier.CombatState?.CurrentSide == CombatSide.Player
        && !KleeOverhaulLedger.For(applier).TeapotSpent;

    /// <summary>Does THIS explosion take the Teapot? Spends the turn's latch
    /// when it does. False with no Teapot, on the enemies' turn, and for an
    /// element Hydro does not react with.</summary>
    public static bool TakeFor(Creature applier, Element element)
    {
        if (KleeArmRelics.Held<AlicesTeapot>(applier) == 0) return false;
        if (applier.CombatState?.CurrentSide != CombatSide.Player) return false;
        if (ReactionTable.Lookup(Element.Hydro, element) == Reaction.None)
        {
            return false;
        }
        if (!KleeOverhaulLedger.For(applier).TakeTeapot()) return false;
        foreach (var relic in applier.Player!.Relics.OfType<AlicesTeapot>())
        {
            relic.Flash();
        }
        return true;
    }

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("alices_teapot")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("alices_teapot")) ?? base.BigIconPath;
}

/// <summary>Shop. "At the start of each combat, place a Mine 2 on ALL
/// enemies." On her first turn, through the arm's own placer, so a Dodoco
/// Charm makes them Mine 3.</summary>
public sealed class DodocoArmy : CustomRelicModel
{
    public const int MineSize = 2;

    public DodocoArmy() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Dodoco Army"),
        ("description",
            "At the start of each combat, place a [gold]Mine[/gold] [blue]"
          + MineSize + "[/blue] on ALL enemies."),
    };

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!FreshCatch.FirstTurnOf(this, player)) return;
        Flash();
        await ProtoBombPower.PlaceOnAll(choiceContext, player.Creature, MineSize,
                                        isMine: true, payloadMineAll: 0,
                                        cardSource: null);
    }

    protected override string IconBaseName => "burning_blood";
    public override string PackedIconPath =>
        KleePck.Path(KleeArmRelics.Icon("dodoco_army")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(KleeArmRelics.Icon("dodoco_army")) ?? base.BigIconPath;
}
#endif
