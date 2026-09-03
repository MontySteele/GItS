using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
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
/// THE INAZUMA COMPANION OVERHAUL -- ITS FIFTEEN POWERS AND ITS ONE HELPER
/// (QUARANTINED, R213 B).
///
/// The approved workshop <c>companion-workshop-inazuma-2026-09-01.md</c> sec.3
/// (approved 2026-09-01 at its four default picks, its sec.9; a Paper artefact
/// on another branch and not in this tree) rewrites Inazuma's Universal
/// companion pool: fifteen shipped rows re-authored and nine characters with no
/// row today given one. Its sec.2 nation shape is "Inazuma reads the HP bar",
/// and eight of the twenty-four rows do.
///
/// SAME FLAG AS MONDSTADT, deliberately: <c>CompanionOverhaul.Enabled</c> means
/// "the companion pool is the approved workshops' pool", and a second property
/// would let a build offer one nation's rewrites beside the other's shipped
/// rows -- a state no document describes and no seat would be asked to grade.
///
/// WHAT THIS FILE REUSES rather than builds, which is most of it. Every hook
/// below was built for Mondstadt's second wave and is spent again here without
/// a line of new plumbing:
///
///   * THE END-OF-TURN VOLLEY, driven by <see cref="CompanionOverhaulTurnEnd"/>
///     in one fixed order (Gorou's Juuga, Sayu's Daruma, Shinobu's ring, Yae's
///     Sakura, Ayaka's Soumetsu, Ayato's clock, Chiori's Tamoto, and three
///     clocks that fire nothing).
///   * THE START-OF-TURN PAYOUT, each power on its own
///     <c>AfterPlayerTurnStart</c> broadcast, on the argument the Mondstadt
///     three already make and which extends: the four are COMMUTATIVE. One
///     clamps its own Block mark, one draws, one grants a rider and one deals
///     UNELEMENTED damage -- so none reads a value another writes and none can
///     change which reactions the others see.
///   * THE BLOCK-ABSORPTION TRIGGER (Diona's paws) answers Thoma's Blazing
///     Barrier as well, from <see cref="CompanionOverhaulIncomingHit"/>.
///   * THE NEXT-ATTACK ELEMENT OVERRIDE (Bennett, Razor, Varka) answers Sara's
///     Crowfeather Cover and Ayato's Kyouka, through the one funnel
///     <see cref="CompanionOverhaulRiders"/> owns.
///   * THE REACTION EVENT counts Swirls for Heizou at the same one call site.
///   * <c>AfterCardPlayed</c> answers Thoma's Crimson Ooyoroi.
///   * A POWER HOSTED ON A CHOSEN BODY (Barbara, Eula) hosts Yoimiya's mark.
///
/// WHAT IS GENUINELY NEW, and there are two. A PER-PLAY DAMAGE TOTAL
/// (<see cref="CompanionOverhaulLedger.DamageDealtThisPlay"/>), because Gorou's
/// "Block equal to half the damage dealt" reads a number no card can compute
/// for itself; and A HIT THAT IGNORES BLOCK (Chiori's Tamoto), which is one
/// optional flag on <see cref="ElementalHit.Deal"/>.
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

/// <summary>
/// Gorou, General's War Banner: "Gain 2 Dexterity for 2 turns."
///
/// THE DEXTERITY IS REAL AND THE CARD GRANTS IT. The row applies
/// <c>DexterityPower</c> 2 and then applies this, which is a CLOCK: Amount is
/// turns remaining, and when it runs out it takes its own two stacks back. A
/// private "+2 Block per gain" modifier was the alternative and was refused --
/// the card says Dexterity, and Dexterity is a thing this engine already has,
/// so a second one wearing the same word is how the two stop meaning the same.
///
/// "FOR 2 TURNS" IS THIS TURN AND THE NEXT, the reading
/// <see cref="LightningFangPower"/> already gives the identical sentence. The
/// workshop's own gloss says "applies this turn too, so three turns of Block"
/// -- the first half is true under this reading and the arithmetic in the
/// second half is not; the PRINTED text is what is built (the workshop's sec.3
/// preamble: "printed text only"), and the discrepancy is disclosed rather
/// than resolved by moving a number nobody ruled.
///
/// IT TAKES BACK ITS OWN TWO, not the stack: a banner that expires while a
/// second one stands leaves that one's Dexterity alone.
/// </summary>
public sealed class WarBannerPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "General's War Banner"),
        ("description",
            "You have [blue]" + CompanionOverhaulLaw.WarBannerDexterity
          + "[/blue] more [gold]Dexterity[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Tick(PlayerChoiceContext choiceContext)
    {
        if (Amount > 1)
        {
            await PowerCmd.TickDownDuration(this);
            return;
        }
        await PowerCmd.Remove(this);
        var dex = Owner.Powers.OfType<DexterityPower>().FirstOrDefault();
        if (dex == null) return;
        if (dex.Amount <= CompanionOverhaulLaw.WarBannerDexterity)
        {
            await PowerCmd.Remove(dex);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, dex, -CompanionOverhaulLaw.WarBannerDexterity,
            applier: Owner, cardSource: null, silent: true);
    }
}

/// <summary>
/// Gorou, Juuga: Forward Unto Victory: "For 3 turns, at the end of your turn
/// deal 6 Geo damage to a random enemy." Amount is TURNS REMAINING.
///
/// <see cref="GlacialWaltzPower"/>'s shape, character for character, with a
/// different element and a different number -- a separate class rather than a
/// retune for the arm's standing reason: a flag-off build has to keep meaning
/// what it printed.
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

// ---------------------------------------------------------------------------
// SAYU
// ---------------------------------------------------------------------------

/// <summary>
/// Sayu, Muji-Muji Daruma: "for 2 turns, at the end of your turn, if you are
/// above 70% HP deal 6 damage to a random enemy; otherwise gain 6 Block."
///
/// THE BAR IS READ WHEN THE DARUMA ACTS, not when it was summoned. "If you are"
/// is present tense, and the whole point of the nation's shape is that the
/// split follows the fight.
///
/// THE DAMAGE CARRIES NO ELEMENT, because the card names none --
/// <see cref="SolarIsotomaBloomPower"/> made the same call for the same reason.
/// </summary>
public sealed class MujiMujiDarumaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Muji-Muji Daruma"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.DarumaDamage}[/blue] damage to a random "
          + "enemy if you are above 70% HP, otherwise gain "
          + $"[blue]{CompanionOverhaulLaw.DarumaBlock}[/blue] [gold]Block[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        if (InazumaCompanion.AbovePercent(Owner, 70))
        {
            var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
            if (target != null)
            {
                await InazumaCompanion.DealUnelemented(
                    choiceContext, target,
                    CompanionOverhaulLaw.DarumaDamage, Owner);
            }
        }
        else
        {
            // NC-11: power-sourced Block stays raw.
            await CreatureCmd.GainBlock(
                Owner, CompanionOverhaulLaw.DarumaBlock,
                ValueProp.Unpowered, null, fast: true);
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Sayu, Naptime: "Gain 4 Block. At the start of your next turn, draw 2 if you
/// played no Attacks this turn."
///
/// THE CONDITION IS ABOUT THE TURN THE CARD WAS PLAYED, so it is answered at
/// the END of that turn: an Attack played this turn deletes the promise, and
/// anything still standing at the next turn's start has already earned its
/// draw. Answering it at the start of the next turn instead would have meant
/// reading a counter the turn boundary has already cleared.
///
/// Amount is CARDS, so two Naptimes draw four, and the promise is popped WHOLE
/// -- it is kept once, not ticked.
///
/// ITS OWN BROADCAST on both ends. The draw is commutative with the other three
/// start-of-turn readers, and the fizzle is a REMOVAL, which has no position to
/// defend -- the same argument the Mondstadt wave's own removals make.
/// </summary>
public sealed class NaptimePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Naptime"),
        ("description",
            "If you play no Attacks this turn, draw [blue]{Amount}[/blue] "
          + "card{Amount:plural:|s} at the start of your next turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        var cards = (int)Amount;
        await PowerCmd.Remove(this);
        if (cards > 0) await CardPileCmd.Draw(choiceContext, cards, player);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (CompanionOverhaulLedger.For(Owner).AttacksPlayedThisTurn <= 0) return;
        await PowerCmd.Remove(this);
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
            "Marks your [gold]Block[/gold]. When it absorbs damage, gain "
          + $"[blue]{CompanionOverhaulLaw.BlazingBarrierBlock}[/blue] "
          + "[gold]Block[/gold], marked too."),
        ("smartDescription",
            "[blue]{Left}[/blue] [gold]Block[/gold] left. When it absorbs "
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

/// <summary>
/// Thoma, Crimson Ooyoroi: "For 2 turns, whenever you play an Attack, deal 5
/// Pyro damage to a random enemy and gain 3 Block."
///
/// <c>AfterCardPlayed</c>, so the rider answers the board the Attack left
/// behind and a killing Attack's rider finds one fewer body. ONE volley per
/// play and not per stack -- Amount is TURNS REMAINING, the arm's standing rule
/// for a timed power, so a second Ooyoroi lengthens the window.
///
/// NOT gated on a first-in-series check: a replayed Attack is an Attack played
/// again, which is the index rule the sim's own `_finish_play` loop takes.
/// </summary>
public sealed class CrimsonOoyoroiPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crimson Ooyoroi"),
        ("description",
            "Whenever you play an Attack, deal "
          + $"[blue]{CompanionOverhaulLaw.OoyoroiDamage}[/blue] [gold]Pyro[/gold] "
          + "damage to a random enemy and gain "
          + $"[blue]{CompanionOverhaulLaw.OoyoroiBlock}[/blue] [gold]Block[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (cardPlay.Card?.Type != CardType.Attack) return;
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target != null)
        {
            await ElementalHit.Deal(
                choiceContext, target, Element.Pyro,
                CompanionOverhaulLaw.OoyoroiDamage, Owner);
        }
        await CreatureCmd.GainBlock(
            Owner, CompanionOverhaulLaw.OoyoroiBlock,
            ValueProp.Unpowered, null, fast: true);
    }
}

// ---------------------------------------------------------------------------
// KUJOU SARA
// ---------------------------------------------------------------------------

/// <summary>
/// Kujou Sara, Crowfeather Cover: "Your next Attack this turn deals 4 more and
/// applies Electro."
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
            "Your next Attack this turn deals [blue]{Amount}[/blue] additional "
          + "damage and applies [gold]Electro[/gold]."),
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

/// <summary>
/// Kujou Sara, Tengu Stormcall: "Next turn, your Attacks deal 5 more damage."
///
/// A PROMISE, NOT A RIDER. It pays into the SHIPPED
/// <see cref="AttackUpThisTurnPower"/> at the start of the turn it names, which
/// is already summed by every damage path and already cleared at the end of the
/// player's turn -- so "next turn" needs no clock of its own and the rider
/// cannot outlive the turn it was promised for. Amount is COPIES: two
/// stormcalls promise ten.
/// </summary>
public sealed class TenguStormcallPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tengu Stormcall"),
        ("description",
            "Next turn, your Attacks deal [blue]"
          + CompanionOverhaulLaw.StormcallBonus
          + "[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        var copies = (int)Amount;
        await PowerCmd.Remove(this);
        if (copies <= 0) return;
        await PowerCmd.Apply<AttackUpThisTurnPower>(
            choiceContext, Owner,
            CompanionOverhaulLaw.StormcallBonus * copies,
            applier: Owner, cardSource: null);
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
            "At the end of your turn, each [gold]Sakura[/gold] deals "
          + $"[blue]{CompanionOverhaulLaw.SakuraDamage}[/blue] [gold]Electro[/gold] "
          + "damage to a random enemy, plus "
          + $"[blue]{CompanionOverhaulLaw.SakuraBonus}[/blue] "
          + "after the first. [blue]{Amount}[/blue] out."),
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
// YOIMIYA
// ---------------------------------------------------------------------------

/// <summary>
/// Yoimiya, Aurous Blaze: "Mark an enemy for 2 turns. Whenever it takes damage
/// from a card that is not an Attack, deal 6 Pyro damage to ALL enemies."
///
/// HOSTED ON THE ENEMY, which is what "mark an enemy" means when a power holds
/// no target: the body holds the mark. Barbara's Melody Loop and Eula's
/// Lightfall Sword are the two rows that established the seam, and this is the
/// third; a body that dies takes the mark with it.
///
/// "FROM A CARD THAT IS NOT AN ATTACK" IS <c>cardSource</c>, and the test has
/// to be three-way rather than two: a Skill's damage line and an Attack's both
/// arrive as powered card damage, and a bomb, a volley or a Shatter arrives
/// with NO card at all. So the mark fires when a card is present AND its type
/// is not Attack -- which also means the blast it fires cannot re-trigger any
/// mark, its own included, because a power-sourced hit names no card.
///
/// Amount is TURNS REMAINING, so re-marking a body extends the window rather
/// than doubling the blast.
/// </summary>
public sealed class AurousBlazePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Aurous Blaze"),
        ("description",
            "Whenever this enemy takes damage from a non-Attack card, deal "
          + $"[blue]{CompanionOverhaulLaw.AurousBlazeDamage}[/blue] [gold]Pyro[/gold] "
          + "damage to ALL enemies. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != Owner) return;
        if (cardSource == null || cardSource.Type == CardType.Attack) return;
        if (result.UnblockedDamage <= 0) return;
        var applier = Applier ?? dealer;
        if (applier == null) return;
        var board = CombatState?.HittableEnemies.ToList();
        if (board == null) return;
        foreach (var enemy in board)
        {
            if (enemy.IsDead) continue;
            await ElementalHit.Deal(
                choiceContext, enemy, Element.Pyro,
                CompanionOverhaulLaw.AurousBlazeDamage, applier);
        }
    }

    /// <summary>The clock, run down by the arm's ordered end-of-turn walk.
    /// A removal, so it defends no position in that sequence -- it is there
    /// because the walk already visits the board for Eula's blade.</summary>
    internal async Task Tick() => await PowerCmd.TickDownDuration(this);
}

// ---------------------------------------------------------------------------
// KAMISATO AYAKA AND AYATO
// ---------------------------------------------------------------------------

/// <summary>
/// Kamisato Ayaka, Soumetsu: "For 2 turns, at the end of your turn deal 8 Cryo
/// damage to ALL enemies. After 2 turns, deal 16 Cryo damage to ALL
/// enemies."
///
/// FIRE, TICK, AND FIRE AGAIN AT ZERO -- both on the same turn when the clock
/// runs out, because "then" is what happens after the two turns and the second
/// turn's own 8 is one of them.
/// </summary>
public sealed class SoumetsuPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Soumetsu"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.SoumetsuDamage}[/blue] [gold]Cryo[/gold] "
          + "damage to ALL enemies, then "
          + $"[blue]{CompanionOverhaulLaw.SoumetsuFinale}[/blue] when it ends. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
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

/// <summary>
/// Kamisato Ayato, Kyouka: "For 2 turns, your Attacks apply Hydro and deal 4
/// more damage. When it ends, deal 12 Hydro damage to a random enemy."
///
/// <see cref="LightningFangPower"/>'s two halves plus an expiry payoff. Amount
/// is TURNS REMAINING, so the damage it pays is the CONSTANT rather than the
/// stack -- a second copy makes the window longer, not the hits bigger, which
/// is the arm's standing rule for a timed power. The element half is read
/// through <see cref="CompanionOverhaulRiders"/>.
/// </summary>
public sealed class KyoukaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kyouka"),
        ("description",
            "Your Attacks apply [gold]Hydro[/gold] and deal "
          + $"[blue]{CompanionOverhaulLaw.KyoukaDamage}[/blue] additional damage. "
          + $"When it ends, deal [blue]{CompanionOverhaulLaw.KyoukaFinale}[/blue] "
          + "[gold]Hydro[/gold] damage to a random enemy. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return CompanionOverhaulLaw.KyoukaDamage;
    }

    internal async Task Tick(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        if (Amount > 1)
        {
            await PowerCmd.TickDownDuration(this);
            return;
        }
        await PowerCmd.Remove(this);
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target == null) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro,
            CompanionOverhaulLaw.KyoukaFinale, Owner);
    }
}

// ---------------------------------------------------------------------------
// KIRARA AND CHIORI
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

/// <summary>
/// Chiori, Fluttering Hasode: "Summon Tamoto: for 3 turns, at the end of your
/// turn deal 6 Geo damage to a random enemy, ignoring Block."
///
/// THE DOLL THAT CUTS ARMOUR. "Ignoring Block" is one optional flag on
/// <see cref="ElementalHit.Deal"/> -- <c>ValueProp.Unblockable</c> beside the
/// <c>Unpowered</c> every power-sourced hit already carries. Everything else
/// about the hit is unchanged: it still reacts, it still counts as a hit, and
/// it is still capped by Intangible, because unblockable is not uncappable
/// (R128).
/// </summary>
public sealed class TamotoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tamoto"),
        ("description",
            "At the end of your turn, deal "
          + $"[blue]{CompanionOverhaulLaw.TamotoDamage}[/blue] [gold]Geo[/gold] "
          + "damage to a random enemy, ignoring [gold]Block[/gold]. "
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
                CompanionOverhaulLaw.TamotoDamage, Owner, ignoreBlock: true);
        }
        await PowerCmd.TickDownDuration(this);
    }
}
