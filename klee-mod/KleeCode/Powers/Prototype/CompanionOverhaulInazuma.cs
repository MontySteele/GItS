using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE INAZUMA COMPANION OVERHAUL -- ITS POWERS AND ITS ONE HELPER
/// (R213 B).
///
/// The approved workshop <c>companion-workshop-inazuma-2026-09-01.md</c> sec.3
/// rewrote Inazuma's Universal companion pool; the Inazuma pool rework
/// (<c>review/active/inazuma-companions-2026-10-18.md</c>, 2026-10-18) took
/// it to 34 cards (8 / 16 / 10): three cut, seven rebuilt, sixteen new, and
/// eight Powers, two cards a character. Its powers are at the foot of this
/// file.
///
/// WHAT THIS FILE REUSES rather than builds, which is most of it. Every hook
/// below was built for Mondstadt's second wave and is spent again here without
/// a line of new plumbing:
///
///   * THE END-OF-TURN VOLLEY, driven by <see cref="CompanionOverhaulTurnEnd"/>
///     in one fixed order (Gorou's Juuga, Shinobu's ring, Yae's Sakura,
///     Ayaka's Soumetsu).
///   * THE START-OF-TURN PAYOUT, each power on its own
///     <c>AfterPlayerTurnStart</c> broadcast: Thoma's Block mark clamps and
///     Kirara's parcel deals UNELEMENTED damage.
///   * THE BLOCK-ABSORPTION TRIGGER (Diona's paws) answers Thoma's Blazing
///     Barrier as well, from <see cref="CompanionOverhaulIncomingHit"/>.
///   * THE NEXT-ATTACK ELEMENT OVERRIDE (Bennett, Razor, Varka) answers Sara's
///     Crowfeather Cover and the Electro rider, through the one funnel
///     <see cref="CompanionOverhaulRiders"/> owns.
///   * THE REACTION EVENT counts Swirls for Chihayaburu at the same one call
///     site.
///
/// WHAT IS GENUINELY NEW: A PER-PLAY DAMAGE TOTAL
/// (<see cref="CompanionOverhaulLedger.DamageDealtThisPlay"/>), because Gorou's
/// "Block equal to half the damage dealt" reads a number no card can compute
/// for itself.
///
/// PURITY IS LOAD-BEARING, as it is next door: nothing in this file mutates
/// from a modifier hook. Every consumption is in <c>AfterPlayerTurnStart</c>,
/// <c>AfterCardPlayed</c>, <c>AfterSideTurnEnd</c>, <c>AfterDamageReceived</c>
/// or <c>BeforeDamageReceived</c>.
/// </summary>
internal static class InazumaCompanion
{
    /// <summary>
    /// Gorou, Inuzaka All-Round Defense: "Gain Block equal to half the damage
    /// dealt." The emitted body calls this after its own damage line.
    ///
    /// HALF OF WHAT LANDED ON HP, rounded down. The printed 8 is not what the
    /// hit was worth once Strength, Weak, an amplifier and the target's Block
    /// have had their say, so the ledger's running total is the honest number
    /// and the card's face cannot be one. Sim twin:
    /// `effects._op_block_half_damage`, reading
    /// `state.mi_damage_dealt_this_card`.
    ///
    /// THE PRINTED-BLOCK FUNNEL, not raw: this is a card's own Block line, so
    /// Frail bites it exactly as it bites a printed <c>block</c> op. (The arm's
    /// POWERS grant raw Block -- NC-11 -- and that difference is between a card
    /// and a power, not between this and its neighbour.)
    /// </summary>
    internal static async Task BlockHalfDamage(
        PlayerChoiceContext choiceContext, Creature owner, CardPlay cardPlay)
    {
        var half = CompanionOverhaulLedger.For(owner).DamageDealtThisPlay / 2;
        if (half <= 0) return;
        await CreatureCmd.GainBlock(
            owner, new BlockVar(half, ValueProp.Move), cardPlay);
    }

    /// <summary>
    /// One unelemented, power-sourced hit -- <see cref="SolarIsotomaBloomPower"/>'s
    /// own two lines, factored out because three Inazuma powers make it (Sayu's
    /// Daruma, Kirara's parcel, and the tick that ends Ayaka's Soumetsu is not
    /// one of them -- it names Cryo). The sim's twin is
    /// `deal_damage_to_enemy(..., element=None, source="companion")`.
    /// </summary>
    internal static async Task DealUnelemented(
        PlayerChoiceContext choiceContext, Creature target, int amount,
        Creature applier)
    {
        var dealt = SimDamagePipeline.DealerMods(applier, amount);
        // The seat this card-less hit is credited to, as on
        // `ElementalHit.DealUnelemented` (Sacred Sakura's Favor reads it).
        using var credit = Diagnostics.DamageCredit.OpenIfNone(
            applier, Diagnostics.DamageCredit.Power);
        await CreatureCmd.Damage(
            choiceContext, target,
            (int)SimDamagePipeline.TargetMods(target, dealt),
            ValueProp.Unpowered, dealer: null, cardSource: null,
            cardPlay: null);
    }

    /// <summary>The nation's shape, as one predicate: is this creature above
    /// <paramref name="pct"/>% HP? CROSS-MULTIPLIED rather than divided, which
    /// is the rule the sheet's own `hp_pct_above_N` predicate keeps -- so a
    /// power reading the bar and a card reading it cannot round the one HP
    /// value a player notices in different directions.</summary>
    internal static bool AbovePercent(Creature creature, int pct) =>
        creature.CurrentHp * 100m > creature.MaxHp * pct;
}

// ---------------------------------------------------------------------------
// GOROU
// ---------------------------------------------------------------------------

// (General's War Banner's Dexterity clock, `WarBannerPower`, left with the
// Kokomi level pass, 2026-10-12: the card gains Block and plans Strength.)

/// <summary>
/// Gorou, Juuga: Forward Unto Victory: "For 3 turns, at the end of your turn
/// deal 6 Geo damage to a random enemy." Amount is TURNS REMAINING.
///
/// <see cref="GlacialWaltzPower"/>'s shape, character for character, with a
/// different element and a different number, as a separate class.
/// </summary>
public sealed class JuugaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Juuga: Forward Unto Victory"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.JuugaDamage}[/blue] [gold]Geo[/gold] "
          + "damage to a random enemy. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target != null)
        {
            await ElementalHit.Deal(
                choiceContext, target, Element.Geo,
                CompanionOverhaulLaw.JuugaDamage, Owner);
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Gorou, Juuga's Plan line (the Kokomi re-founding, 2026-10-12, card paper
/// sec.3): "For 3 turns, at the end of your turn gain 6 Block." Amount is
/// TURNS REMAINING; <see cref="JuugaPower"/>'s shape with Block for the hit,
/// walked beside it at the end of her turn. Power-sourced Block stays raw
/// (NC-11). Sim twin: <c>mi_juuga_guard</c>.
/// </summary>
public sealed class JuugaGuardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Juuga: Forward Unto Victory"),
        ("description",
            "At the end of your turn, gain "
          + $"[blue]{CompanionOverhaulLaw.JuugaGuardBlock}[/blue] "
          + "[gold]Block[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Guard(PlayerChoiceContext choiceContext)
    {
        await CreatureCmd.GainBlock(Owner, CompanionOverhaulLaw.JuugaGuardBlock,
                                    ValueProp.Unpowered, null);
        await PowerCmd.TickDownDuration(this);
    }
}

// ---------------------------------------------------------------------------
// KUKI SHINOBU
// ---------------------------------------------------------------------------

/// <summary>
/// Kuki Shinobu, Sanctifying Ring: "For 3 turns, at the end of your turn deal 5
/// Electro damage to ALL enemies and gain 5 Block." (The "Lose 3 HP" is the
/// card's own first line, a plain self-damage row, and is not here.)
///
/// THE BLOCK IS PAID WHETHER OR NOT THE RING FOUND A BODY: the printed sentence
/// joins its two clauses with a bare "and", which is the reading
/// <see cref="DandelionBreezePower"/> already took for the same construction.
/// </summary>
public sealed class SanctifyingRingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sanctifying Ring"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.SanctifyingRingDamage}[/blue] "
          + "[gold]Electro[/gold] damage to ALL enemies and gain "
          + $"[blue]{CompanionOverhaulLaw.SanctifyingRingBlock}[/blue] [gold]Block[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        var board = CombatState?.HittableEnemies.ToList();
        if (board != null)
        {
            foreach (var enemy in board)
            {
                if (enemy.IsDead) continue;
                await ElementalHit.Deal(
                    choiceContext, enemy, Element.Electro,
                    CompanionOverhaulLaw.SanctifyingRingDamage, Owner);
            }
        }
        await CreatureCmd.GainBlock(
            Owner, CompanionOverhaulLaw.SanctifyingRingBlock,
            ValueProp.Unpowered, null, fast: true);
        await PowerCmd.TickDownDuration(this);
    }
}

// ---------------------------------------------------------------------------
// THOMA
// ---------------------------------------------------------------------------

/// <summary>
/// Thoma, Blazing Barrier: "Gain 6 Block. Whenever this Block absorbs damage,
/// gain 3 Block."
///
/// <see cref="IcyPawsPower"/>'s construction, exactly: the engine has ONE Block
/// pool, so "this Block" is a MARK on it, a hit that spends Block spends the
/// mark with it, and marked-Block-eaten-FIRST is the conservative reading of a
/// question a single pool cannot answer (R212's one-way rule). The only
/// difference is the payout -- Block instead of an aura on the attacker.
///
/// `EB-353`. THE BLOCK THE RIDER PAYS IS MARKED TOO, and that is what makes
/// the rider fire ONCE PER ABSORPTION rather than once per barrier. The card
/// says "WHENEVER this Block absorbs damage", and a three-hit attack is three
/// absorptions; with the payout unmarked the mark was spent whole by the first
/// hit and the barrier paid exactly once, for any attack, forever. The blind
/// act-2 seat measured it three times and got the same 9 every time -- 18
/// incoming / 9 taken, 9 incoming / 0 taken, 21 incoming / 12 taken -- and
/// wrote "Thoma is a 9-Block card that prints 6 and implies more"
/// (`klee round 8, opus-act2.md`, finding 4). Per absorption the same 7x3
/// absorbs 6 + 3 + 3 = 12.
///
/// IT IS NOT A SHIELD THAT THICKENS FOR THE FIGHT, which is what the old note
/// here feared. The mark carries no Block of its own: it is bounded by the
/// pool through <see cref="BlockMark.Left"/>, and the pool is cleared at the
/// player's turn start, where <see cref="BlockMark.ClearIfSpent"/> removes a
/// mark with nothing behind it. So the barrier lives exactly one enemy turn
/// per play, which is the card's own price.
///
/// `EB-337`. THE LINE USED TO LIE, AND THIS IS THE ROW THE SEAT FILED IT ON.
/// The blind seat carried "Blazing Barrier 6 -- 6 Block left" through two
/// rounds with `Block` at 0 and took a 15 in full
/// (`klee round 7b, opus-act2.md`, section (c)): the mark
/// is a mark on the Block pool, the pool is cleared at the turn tick, and the
/// printed number was the raw stack. The printed number and the badge are now
/// <see cref="BlockMark.Left"/> -- read LIVE, so they are what
/// <see cref="Thicken"/> was always going to pay on -- and a mark with nothing
/// behind it leaves at the start of the turn, which is what the sim's
/// `inazuma_overhaul_turn_start` has always done. <see cref="BlockMark"/>
/// carries the whole argument; Diona's paws are the same construction and took
/// the same fix.
/// </summary>
public sealed class BlazingBarrierPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Blazing Barrier"),
        // THE STATIC (compendium) ROW CARRIES NO VAR TOKEN -- `EB-353`.
        // `PowerModel.HoverTips` takes the smart branch only when
        // `HasSmartDescription && IsMutable`, and `DynamicVars.AddTo` is
        // called on THAT branch alone; the static branch binds the game's own
        // three dumb variables and nothing else. So `{Left}` written here was
        // never bound, and the seat read the placeholder itself off the buff
        // list: "Blazing Barrier 6 (buff) -- {Left} Block left."
        // (`klee round 8, opus-act2.md`). The same split, for the same
        // reason, as `SalonPowers`' `{Slots}`.
        ("description",
            "Marks your [gold]Block[/gold]. Whenever it absorbs damage, gain "
          + $"[blue]{CompanionOverhaulLaw.BlazingBarrierBlock}[/blue] "
          + "[gold]Block[/gold], marked too."),
        ("smartDescription",
            "[blue]{Left}[/blue] [gold]Block[/gold] left. Whenever it absorbs "
          + $"damage, gain [blue]{CompanionOverhaulLaw.BlazingBarrierBlock}[/blue] "
          + "[gold]Block[/gold], marked too."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BlockMarkVar() };

    /// <summary>`EB-337`: the badge is the number the face prints.</summary>
    public override int DisplayAmount => BlockMark.Left(this);

    /// <summary>`EB-337`, the housekeeping half, and the twin of the sim's
    /// `inazuma_overhaul_turn_start` clamp. This file's own header already
    /// promised the behaviour ("One clamps its own Block mark"); the hook was
    /// missing.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await BlockMark.ClearIfSpent(this);
    }

    /// <summary>The hit is about to be absorbed. Same arithmetic as the paws,
    /// off the same standing Block, so a board carrying both spends both marks
    /// against the same absorption -- and `EB-353` means the paws' arithmetic
    /// is now literally the same call, with the barrier's payout as its one
    /// argument. <see cref="BlockMark.Absorb"/> owns it; this owns the
    /// commands, which is the split the paws' own note already made.</summary>
    internal async Task Thicken(PlayerChoiceContext choiceContext,
                                decimal amount)
    {
        var left = BlockMark.Absorb(
            (int)Amount, (int)Owner.Block, (int)amount,
            CompanionOverhaulLaw.BlazingBarrierBlock);
        if (left == null) return;
        await CreatureCmd.GainBlock(
            Owner, CompanionOverhaulLaw.BlazingBarrierBlock,
            ValueProp.Unpowered, null, fast: true);
        // Never zero: the payout is marked, so the mark always survives its
        // own absorption and leaves at the turn tick instead of here.
        await PowerCmd.ModifyAmount(
            choiceContext, this, left.Value - (int)Amount,
            applier: Owner, cardSource: null, silent: true);
    }
}

// ---------------------------------------------------------------------------
// KUJOU SARA
// ---------------------------------------------------------------------------

/// <summary>
/// Kujou Sara, Crowfeather Cover: "Your next Attack card this turn deals 4
/// additional damage and is Electro, not its own element."
///
/// <see cref="PassionOverloadPower"/> with a different element, and a separate
/// type for that reason alone: the element half is read through
/// <see cref="CompanionOverhaulRiders"/>, which asks WHICH power is standing.
/// </summary>
public sealed class CrowfeatherCoverPower
    : NextAttackRiderPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crowfeather Cover"),
        ("description",
            "Your next Attack card this turn deals [blue]{Amount}[/blue] "
          + "additional damage and is [gold]Electro[/gold], not its own "
          + "element."),
    };

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

// ---------------------------------------------------------------------------
// YAE MIKO
// ---------------------------------------------------------------------------

/// <summary>
/// Yae Miko, Sesshou Sakura: "Place a Sakura: at the end of your turn it deals
/// 4 Electro damage plus your Strength to a random enemy. Each Sakura you place
/// while one is out deals 3 more. Up to 3."
///
/// AMOUNT IS SAKURA, and the power is PERMANENT: the card places a totem, not a
/// timer.
///
/// "EACH SAKURA YOU PLACE WHILE ONE IS OUT DEALS 3 MORE" is read as a statement
/// about the SAKURA BEING PLACED, which is what its subject says: the first one
/// out deals 4 and every later one deals 7, whether one or two were already
/// standing. So three Sakura are volleys of 4, 7 and 7, fired in placement
/// order, each at its own random target because each Sakura is its own totem.
/// The alternative reading -- every placement raising every Sakura, which the
/// workshop's italic gloss ("totems that level up together") suggests -- is not
/// what the printed sentence says, and the printed sentence is what is built.
///
/// "PLUS YOUR STRENGTH" IS PRINTED, NOT IMPLEMENTED: every power-sourced hit in
/// this arm already runs the dealer's modifiers (<c>SimDamagePipeline</c> here,
/// `powers.modify_damage_dealt` in the sim), so the clause describes what the
/// volley was always going to do. It is on the face because the workshop put it
/// there.
///
/// "UP TO 3" IS READ AT THE FIRE, not at the placement: a fourth Sakura can be
/// placed and simply never fires. That is the conservative direction and it
/// needs no stack cap in either engine.
/// </summary>
public sealed class SesshouSakuraPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sesshou Sakura"),
        ("description",
            // THE 2026-09-25 TEXT PASS. "Plus 3 after the first" read as a
            // bonus that might stack Sakura by Sakura; `FireVolley` below
            // pays the first one the base and every later one base PLUS the
            // bonus, flat, so the face prints that second number outright.
            "At the end of your turn, your [blue]{Amount}[/blue] "
          + "[gold]Sakura[/gold] each deal "
          + $"[blue]{CompanionOverhaulLaw.SakuraDamage}[/blue] [gold]Electro[/gold] "
          + "damage to a random enemy, or "
          + $"[blue]{CompanionOverhaulLaw.SakuraDamage + CompanionOverhaulLaw.SakuraBonus}[/blue] "
          + "after the first."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        var sakura = System.Math.Min((int)Amount, CompanionOverhaulLaw.SakuraCap);
        for (var i = 0; i < sakura; i++)
        {
            var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
            if (target == null) break;
            var damage = CompanionOverhaulLaw.SakuraDamage
                       + (i > 0 ? CompanionOverhaulLaw.SakuraBonus : 0);
            await ElementalHit.Deal(
                choiceContext, target, Element.Electro, damage, Owner);
        }
        // NO tick-down. A Sakura is a totem, not a timer.
    }
}

// ---------------------------------------------------------------------------
// KAMISATO AYAKA
// ---------------------------------------------------------------------------

/// <summary>
/// Kamisato Ayaka, Soumetsu: "At the end of each of your next 2 turns, deal 8
/// Cryo damage to ALL enemies. On the last of them, deal 16 more."
///
/// FIRE, TICK, AND FIRE AGAIN AT ZERO -- both on the same turn when the clock
/// runs out, because the last turn's own 8 is one of the two and the finale
/// lands beside it. So the last turn pays 24.
///
/// `EB-698`. THE TEXT IS THE FIX AND THE NUMBERS ARE UNTOUCHED. Both surfaces
/// used to say "after 2 turns, deal 16", which reads as a third event after
/// the clock and says nothing about which of the turns in front of you pays
/// which number; three plays and the seat never knew what was about to land
/// (Kokomi r30 lane 1). The card and this badge now say the same sentence: 8
/// on every one of them, 16 more on the last. The badge carries the live count
/// on top, because `{Amount}` is TURNS REMAINING and is one of the three dumb
/// variables `PowerModel.GetDumbHoverTip` binds on the static row.
/// </summary>
public sealed class SoumetsuPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Soumetsu"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.SoumetsuDamage}[/blue] [gold]Cryo[/gold] "
          + "damage to ALL enemies. [blue]{Amount}[/blue] "
          + "{Amount:plural:turn|turns} left. The last deals "
          + $"[blue]{CompanionOverhaulLaw.SoumetsuFinale}[/blue] additional "
          + "damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        await Sweep(choiceContext, CompanionOverhaulLaw.SoumetsuDamage);
        if (Amount > 1)
        {
            await PowerCmd.TickDownDuration(this);
            return;
        }
        await PowerCmd.Remove(this);
        await Sweep(choiceContext, CompanionOverhaulLaw.SoumetsuFinale);
    }

    private async Task Sweep(PlayerChoiceContext choiceContext, int damage)
    {
        var board = CombatState?.HittableEnemies.ToList();
        if (board == null) return;
        foreach (var enemy in board)
        {
            if (enemy.IsDead) continue;
            await ElementalHit.Deal(
                choiceContext, enemy, Element.Cryo, damage, Owner);
        }
    }
}

// ---------------------------------------------------------------------------
// KIRARA
// ---------------------------------------------------------------------------

/// <summary>
/// Kirara, Surprise Dispatch: "Gain 8 Block. Next turn, deal 10 damage to a
/// random enemy." (The Block is the card's own line.)
///
/// The parcel that goes off later: POPPED WHOLE at the start of the next turn,
/// Amount being COPIES. The damage carries NO element, because the card names
/// none -- and Kirara is the one companion in this pool whose own element the
/// engine does not have, so <c>CompanionElement</c> is <c>Element.None</c> on
/// her card too.
/// </summary>
public sealed class SurpriseDispatchPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Surprise Dispatch"),
        ("description",
            "Next turn, deal [blue]"
          + CompanionOverhaulLaw.SurpriseDispatchDamage
          + "[/blue] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        var copies = (int)Amount;
        await PowerCmd.Remove(this);
        for (var i = 0; i < copies; i++)
        {
            var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
            if (target == null) break;
            await InazumaCompanion.DealUnelemented(
                choiceContext, target,
                CompanionOverhaulLaw.SurpriseDispatchDamage, Owner);
        }
    }
}

// ---------------------------------------------------------------------------
// THE INAZUMA POOL REWORK (2026-10-18)
// ---------------------------------------------------------------------------
// review/active/inazuma-companions-2026-10-18.md; [USER]: "Ok, agreed on all
// defaults for both the PR and inazuma companions". Seven powers: Thoma's
// rebuilt Ooyoroi, the Electro rider Sara's Stormcall and Raiden's Baleful
// Omen share, and the five Rare Powers. Each one's sim twin is named on it.

/// <summary>
/// The Inazuma rework's card-side helper: Chiori's Fluttering Hasode, "This
/// ignores Block." The base game's <c>AttackCommand</c> carries its props in
/// <c>DamageProps</c> with a private setter and offers only <c>Unpowered()</c>,
/// so the emitted body adds <see cref="ValueProp.Unblockable"/> here. The hit
/// stays a powered card Attack (Strength, Weak and Vulnerable still apply) and
/// is still capped by Intangible. Sim twin:
/// `deal_damage_to_enemy(ignore_block=True)`, from `_op_damage`.
/// </summary>
public static class InazumaAttackExtensions
{
    private static readonly System.Reflection.PropertyInfo? DamagePropsProperty =
        typeof(AttackCommand).GetProperty(nameof(AttackCommand.DamageProps));

    public static AttackCommand IgnoringBlock(this AttackCommand command)
    {
        DamagePropsProperty?.SetValue(
            command, command.DamageProps | ValueProp.Unblockable);
        return command;
    }
}

/// <summary>
/// Thoma, Crimson Ooyoroi (rebuilt as a Power, 2026-10-18): "At the start of
/// your turn, keep up to 6 [9] of your Block." <see cref="WatatsumisGracePower"/>'s
/// construction, the base game's Sturdy Clamp shape: the Block clear is
/// prevented, then everything above the stack is lost. Amount IS the cap, so
/// copies add. Barricade (or Grace) worn first keeps its own rule: the first
/// preventer wins, as in the base game. Sim twin: `effects.ooyoroi_keeps`,
/// read at the block clear beside `kokomi_plan.grace_keeps`.
/// </summary>
public sealed class CrimsonOoyoroiPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crimson Ooyoroi"),
        ("description",
            "At the start of your turn, keep up to [blue]{Amount}[/blue] of "
          + "your [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool ShouldClearBlock(Creature creature) =>
        creature != Owner;

    public override async Task AfterPreventingBlockClear(
        AbstractModel preventer, Creature creature)
    {
        if (this != preventer || creature != Owner) return;
        var over = (int)creature.Block - (int)Amount;
        if (over > 0)
        {
            await CreatureCmd.LoseBlock(new BlockingPlayerChoiceContext(),
                                        creature, over, null);
        }
    }
}

/// <summary>
/// Kujou Sara, Tengu Stormcall (2026-10-18; Baleful Omen shared it until cut, 2026-10-19):
/// "Your next Attack this turn applies Electro." <see cref="CrowfeatherCoverPower"/>
/// without the damage half: a one-shot element rider, spent by the next
/// Attack card (<see cref="NextAttackRiderPower"/>) and removed at the end of
/// the turn. The element is read through <see cref="CompanionOverhaulRiders"/>
/// at Crowfeather's tier. Sim twin: `mi_next_electro` in
/// `effects.companion_overhaul_card_start`.
/// </summary>
public sealed class NextAttackElectroPower
    : NextAttackRiderPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Electro Rider"),
        ("description",
            "Your next Attack this turn applies [gold]Electro[/gold]."
          + CardTypeClause),
    };

    public override PowerStackType StackType => PowerStackType.Single;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Raiden Shogun, Plane of Euthymia (Rare Power, 2 [1]): "At the end of your
/// turn, Retain your Hand." The base game's Runic Pyramid as a Power: the
/// end-of-turn flush is refused for its owner (<c>ShouldFlush</c>, the hook
/// <c>RunicPyramid</c> and <c>RetainHandPower</c> override). Ethereal cards
/// still Exhaust, because that is not the flush. Sim twin: `mi_euthymia` in
/// `refpowers.retain_at_flush`.
/// </summary>
public sealed class PlaneOfEuthymiaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Plane of Euthymia"),
        ("description",
            "At the end of your turn, Retain your [gold]Hand[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    public override bool ShouldFlush(Player player) =>
        player != Owner.Player;
}

/// <summary>
/// Itto, Royal Descent: Behold, Itto the Evil! (Rare Power, 2): "Whenever an
/// enemy's attack deals you no damage, deal 6 [9] Geo damage to it."
///
/// PER ENEMY ATTACK, NOT PER HIT, <see cref="TidalRipostePower"/>'s read:
/// <c>AfterAttack</c> fires once for the enemy's whole <c>AttackCommand</c>,
/// and it pays when at least one hit reached her and none of them cost HP
/// (Block took it, or it dealt 0). A multi-hit attack pays once. Amount IS
/// the damage, so copies add. The hit is the arm's power-sourced Geo hit
/// (<see cref="ElementalHit.Deal"/>), so it reacts. Sim twin:
/// `effects.royal_descent`, called once per enemy attack beside Tidal
/// Riposte.
/// </summary>
public sealed class RoyalDescentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Royal Descent"),
        ("description",
            "Whenever an enemy's attack deals you no damage, deal "
          + "[blue]{Amount}[/blue] [gold]Geo[/gold] damage to it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The rule, readable without a combat: one attack's hits on
    /// her, as unblocked HP damage. No damage is "at least one hit, and none
    /// got through".</summary>
    public static bool DealtNoDamage(IEnumerable<int> unblocked)
    {
        var any = false;
        foreach (var hit in unblocked)
        {
            if (hit > 0) return false;
            any = true;
        }
        return any;
    }

    public override async Task AfterAttack(
        PlayerChoiceContext choiceContext, AttackCommand command)
    {
        if (Owner == null || Owner.IsDead || Amount <= 0) return;
        if (command.Attacker is not { IsEnemy: true } attacker) return;
        if (!command.DamageProps.IsPoweredAttack()) return;
        var me = Owner;
        var hits = command.Results
            .SelectMany(r => r)
            .Where(r => r.Receiver == me)
            .Select(r => r.UnblockedDamage);
        if (!DealtNoDamage(hits)) return;
        if (attacker.IsDead) return;
        Flash();
        await ElementalHit.Deal(
            choiceContext, attacker, Element.Geo, (int)Amount, me);
    }
}

/// <summary>
/// Yoimiya, Niwabi Fire-Dance (Rare Power, 2 [1]): "The first Attack you
/// play each turn is played twice." The base game's replay surface
/// (<c>ModifyCardPlayCount</c>, Echo Form's and Burst's), on the shape
/// <see cref="FirstAttackTwicePower"/> (Pincer) takes for one turn.
///
/// "THE FIRST" IS THE ARM'S ATTACK LEDGER
/// (<see cref="CompanionOverhaulLedger.AttacksPlayedThisTurn"/>, written after
/// each Attack play): an Attack played while it reads 0 is played twice, so a
/// Niwabi played after this turn's first Attack waits for next turn. A card
/// planned on the Bake-Kurage is not doubled (Pincer's rule: it resolves none
/// of its face), though the write is an Attack play to the ledger. The stack
/// is a marker: a second copy doubles nothing further. Sim twin:
/// `effects.niwabi_replays`.
/// </summary>
public sealed class NiwabiFireDancePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Niwabi Fire-Dance"),
        ("description",
            "The first Attack you play each turn is played twice."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (card.Type != CardType.Attack) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (BakeKuragePet.Is(target)) return playCount;
        int played;
        try
        {
            played = CompanionOverhaulLedger.For(Owner).AttacksPlayedThisTurn;
        }
        catch (System.Exception)
        {
            return playCount;
        }
        return played > 0 ? playCount : playCount + 1;
    }

    public override Task AfterModifyingCardPlayCount(CardModel card)
    {
        Flash();
        return Task.CompletedTask;
    }
}

/// <summary>
/// Kaedehara Kazuha, Chihayaburu (Rare Power, 1 [0]): "Whenever you Swirl,
/// draw 1 card." Read at the one site the mod resolves a reaction
/// (<see cref="CompanionOverhaulReactions.Note"/>), on a Swirl the owner
/// dealt: one draw per Swirl, so a Swirl of ALL enemies draws one for each
/// enemy it Swirled. Amount is cards, so copies add. Sim twin: `mi_chihayaburu`
/// in `effects.companion_overhaul_reaction`.
/// </summary>
public sealed class ChihayaburuPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Chihayaburu"),
        ("description",
            "Whenever you [gold]Swirl[/gold], draw [blue]{Amount}[/blue] "
          + "card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal static async Task OnSwirl(
        PlayerChoiceContext choiceContext, Creature dealer)
    {
        var player = dealer.Player;
        if (player == null) return;
        var cards = dealer.Powers.OfType<ChihayaburuPower>()
            .Sum(p => (int)p.Amount);
        if (cards <= 0) return;
        foreach (var power in dealer.Powers.OfType<ChihayaburuPower>())
        {
            power.Flash();
        }
        await CardPileCmd.Draw(choiceContext, cards, player);
    }
}

/// <summary>
/// Wanderer, Hanega: Song of the Wind (Rare Power, 1 [0]; the review's
/// amended text, 2026-10-18): "At the start of your turn, gain 1 Energy.
/// Cards give you 3 less Block." The Energy is the base game's
/// <c>EnergyNextTurnPower</c> hook (<c>AfterEnergyReset</c>), every turn. The
/// Block is Dexterity's own filter turned down (<c>ModifyBlockAdditive</c> on
/// powered card Block only, <c>IsPoweredCardOrMonsterMoveBlock</c> with a card
/// source), so relic and power Block are untouched, and the game's
/// <c>Hook.ModifyBlock</c> floors the total at 0. Amount is copies, and both
/// halves stack with it (the review, 2026-10-18): each copy gives 1 Energy
/// and 3 less Block, so two give 2 Energy and 6 less. The badge prints the
/// live total (<see cref="HanegaBlockLossVar"/>). Sim twins:
/// `effects.hanega_energy` and `powers.modify_block_gained`.
/// </summary>
public sealed class HanegaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Hanega: Song of the Wind"),
        // The static (compendium) row binds only the game's dumb vars, so
        // it prints the one-copy 3; the badge prints the stacked total
        // (`BlazingBarrierPower`'s split).
        ("description",
            "At the start of your turn, gain {Amount:energyIcons()}. Cards "
          + $"give you [blue]{CompanionOverhaulLaw.HanegaBlockLoss}[/blue] "
          + "less [gold]Block[/gold]."),
        ("smartDescription",
            "At the start of your turn, gain {Amount:energyIcons()}. Cards "
          + "give you [blue]{" + HanegaBlockLossVar.Token + "}[/blue] "
          + "less [gold]Block[/gold]."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new HanegaBlockLossVar() };

    /// <summary>The Block cards give you less, all copies: 3 per copy.</summary>
    public static int BlockLoss(int copies) =>
        CompanionOverhaulLaw.HanegaBlockLoss * System.Math.Max(0, copies);

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterEnergyReset(Player player)
    {
        if (player != Owner.Player || Amount <= 0) return;
        await PlayerCmd.GainEnergy((int)Amount, player);
    }

    public override decimal ModifyBlockAdditive(
        Creature target, decimal block, ValueProp props,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (cardSource == null || target != Owner) return 0m;
        if (cardSource.Owner?.Creature != Owner) return 0m;
        if (!props.IsPoweredCardOrMonsterMoveBlock()) return 0m;
        return -BlockLoss((int)Amount);
    }
}

/// <summary>Hanega's badge number, "{BlockLoss}": 3 per copy, read live off
/// the power (<see cref="BlockMarkVar"/>'s shape).</summary>
internal sealed class HanegaBlockLossVar : DynamicVar
{
    internal const string Token = "BlockLoss";

    internal HanegaBlockLossVar()
        : base(Token, CompanionOverhaulLaw.HanegaBlockLoss)
    {
    }

    private int Live => _owner is PowerModel power
        ? HanegaPower.BlockLoss((int)power.Amount)
        : (int)BaseValue;

    protected override decimal GetBaseValueForIConvertible() => Live;

    public override string ToString() =>
        Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
}

/// <summary>
/// Raiden Shogun, Musou no Hitotachi's "ALL enemies and you lose 3 Strength
/// this turn" (2026-10-19, Baleful Omen's power renamed with its card cut):
/// <see cref="ProtoKoCoverYourEarsPower"/>'s shape, the base game's
/// <c>PiercingWailPower</c>, on every enemy and on the player. Emitted by the
/// codegen's <c>lose_strength</c> with <c>this_turn: true</c>
/// (<c>{CardClass}Power</c>). Sim twin: <c>temp_strength_down</c>.
/// </summary>
public sealed class ProtoMiRaidenMusouNoHitotachiPower : TemporaryStrengthPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Musou no Hitotachi"),
        ("description",
            "Lose [blue]{Amount}[/blue] [gold]Strength[/gold] this turn."),
    };

    public override AbstractModel OriginModel =>
        ModelDb.Card<global::KleeMod.Cards.Prototype.Generated.ProtoMiRaidenMusouNoHitotachi>();

    protected override bool IsPositive => false;
}

/// <summary>
/// Musou no Hitotachi's "plus 2 for each card in your Hand" (2026-10-19): the
/// hand as it stands, the card itself left out, so the preview in hand and
/// the hit in play read the same number. Sim twin: the
/// <c>other_cards_in_hand</c> runtime count.
/// </summary>
public static class InazumaHand
{
    public static int OtherCardsInHand(CardModel card)
    {
        var owner = card.Owner;
        if (owner == null) return 0;
        return PileType.Hand.GetPile(owner).Cards.Count(c => !ReferenceEquals(c, card));
    }
}

// ---------------------------------------------------------------------------
// GROWING THE POOL TO 34 (ruled 2026-10-18)
// ---------------------------------------------------------------------------
// review/active/inazuma-companions-2026-10-18.md, "Growing the pool to 34";
// [USER]: "Agreed on (a)! And also on growing the pool". Two Rare Powers.

/// <summary>
/// Chiori, Hiyoku: Twin Blades (Rare Power, 1; the review's text,
/// 2026-10-18): "Your Attacks that hit more than once hit one additional
/// time." Upgraded, it is Innate.
///
/// A MULTI-HIT ATTACK IS ONE WHOSE PRINTED HIT COUNT IS 2 OR MORE: the
/// <c>WithHitCount</c> the card's own <c>AttackCommand</c> was built with
/// (its private <c>_hitCount</c>, read before <c>Hook.ModifyAttackHitCount</c>
/// has its say), so a single-hit Attack played twice by Niwabi is not one.
/// The extra hit is the base game's own hit-count hook
/// (<c>ModifyAttackHitCount</c>), the surface Niwabi's replay sits beside: a
/// pure read, one more hit per stack. A Plan line's multi-hit (Pearl Current,
/// Kyouka Fuushi) is no <c>AttackCommand</c>, so it takes its extra hit in
/// <see cref="KokomiPlan"/>'s <c>Hit</c> through <see cref="PlanExtraHits"/>.
/// Sim twin: `mi_twin_blades` in `effects._op_damage` (an Attack with `times`
/// of 2 or more) and `kokomi_plan._hit`.
/// </summary>
public sealed class TwinBladesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Hiyoku: Twin Blades"),
        ("description",
            "Your Attacks that hit more than once hit [blue]{Amount}[/blue] "
          + "additional {Amount:plural:time|times}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    private static readonly System.Reflection.FieldInfo? HitCountField =
        typeof(AttackCommand).GetField(
            "_hitCount",
            System.Reflection.BindingFlags.NonPublic
            | System.Reflection.BindingFlags.Instance);

    /// <summary>The hit count an <c>AttackCommand</c> was printed with, or 1
    /// where it cannot be read.</summary>
    public static int PrintedHits(AttackCommand command) =>
        HitCountField?.GetValue(command) is int hits ? hits : 1;

    /// <summary>The rule, readable without a combat.</summary>
    public static bool IsMultiHitAttack(CardModel? card, int hits) =>
        card is { Type: CardType.Attack } && hits >= 2;

    public override int ModifyAttackHitCount(AttackCommand attack, int hitCount)
    {
        if (Owner == null || attack.Attacker != Owner || Amount <= 0) return hitCount;
        if (!IsMultiHitAttack(attack.ModelSource as CardModel, PrintedHits(attack)))
        {
            return hitCount;
        }
        return hitCount + (int)Amount;
    }

    /// <summary>A planned hit's extra hits: an Attack's Plan line of 2 or
    /// more hits takes one per stack of the owner's Twin Blades, else 0.</summary>
    public static int PlanExtraHits(Creature? owner, CardModel? source, int times)
    {
        if (owner == null || !IsMultiHitAttack(source, times)) return 0;
        return owner.Powers.OfType<TwinBladesPower>().Sum(p => (int)p.Amount);
    }
}

/// <summary>
/// Yae Miko, Sacred Sakura's Favor (Rare Power, 2 [1]): "Damage you deal at
/// the end of your turn is increased by 50%." Offered to Yae too (the review,
/// 2026-10-18); her Sesshou Sakura stays hidden from her.
///
/// "AT THE END OF YOUR TURN" IS THE GAME'S OWN END-OF-TURN PHASE, read off
/// the turn state and not off a list of actors (<see cref="InEndOfTurn"/>):
/// <c>CombatManager.EndPlayerTurnPhaseOneInternal</c> sets the player's
/// <c>PlayerTurnPhase.End</c> after the AutoPostPlay phase and before
/// <c>BeforeSideTurnEnd</c>, and it stays End through the hand flush and
/// <c>AfterSideTurnEnd</c> until the side switches to the enemy. So every
/// end-of-turn power, pet, summon, orb or guest that acts in that window is
/// in it (the companion walk, Furina's guests, Yae's Sakura strikes, a
/// base-game power such as Combust), and Lisa's Lightning Rose, which fires
/// at the start of the turn, is not.
///
/// "DAMAGE YOU DEAL" IS A HIT ON AN ENEMY THAT IS THIS PLAYER'S: the dealer
/// is the owner or the owner's pet, or, for the mod's power-sourced doors
/// that pass no dealer, the damage credit scope those doors open names this
/// seat (<see cref="Diagnostics.DamageCredit.Current"/>). One multiplicative
/// hook on the engine's own damage call, so every door is covered once. A
/// marker: a second copy adds nothing. Sim twin:
/// `effects.sacred_sakuras_favor_mult`, read in `deal_damage_to_enemy` while
/// `state.turn_end_window` is open.
/// </summary>
public sealed class SacredSakurasFavorPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sacred Sakura's Favor"),
        ("description",
            "Damage you deal at the end of your turn is increased by "
          + "[blue]50%[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>Is it <paramref name="creature"/>'s player's end-of-turn
    /// phase? PURE.</summary>
    public static bool InEndOfTurn(Creature? creature)
    {
        var player = creature?.Player ?? creature?.PetOwner;
        if (player?.PlayerCombatState?.Phase != PlayerTurnPhase.End) return false;
        return creature!.CombatState?.CurrentSide == CombatSide.Player;
    }

    /// <summary>Is this hit the owner's? The dealer's seat, else the open
    /// damage credit's seat. PURE.</summary>
    public static bool IsOwners(Creature owner, Creature? dealer)
    {
        var seat = Diagnostics.DamageCredit.OwnerOf(dealer)
                   ?? Diagnostics.DamageCredit.Current?.Owner;
        return seat != null && seat == owner.Player;
    }

    /// <summary>The rule, as one multiplier. PURE.</summary>
    public static decimal Multiplier(Creature owner, Creature? target,
                                     Creature? dealer)
    {
        if (target == null || target.Side == owner.Side) return 1m;
        if (!InEndOfTurn(owner) || !IsOwners(owner, dealer)) return 1m;
        return CompanionOverhaulLaw.SacredSakuraMult;
    }

    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (Owner == null) return 1m;
        return Multiplier(Owner, target, dealer);
    }
}
