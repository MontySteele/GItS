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
/// THE MONDSTADT COMPANION OVERHAUL, SECOND WAVE -- THE HOOKS (QUARANTINED,
/// R213 B).
///
/// The first pass shipped twenty-one of the approved workshop's thirty-four
/// Universals and left THIRTEEN out, each one because its printed text wanted
/// an engine hook that existed in NEITHER engine. These are those hooks and the
/// thirteen powers that ride them. Sim twin:
/// <c>tier0/engine/effects.py</c>'s `companion_overhaul_*` block, which names
/// the same five call sites.
///
/// WHAT WAS REUSED RATHER THAN BUILT, said once at the top because it is the
/// most important thing in the file:
///
///   * THE PRE-ENEMY-ATTACK TRAP is <c>PowerModel.BeforeDamageReceived</c>, the
///     hook Klee's Mine already answers an enemy attack with
///     (<see cref="ProtoBombPower"/>, rule 6). Dahlia's Shower and Amber's
///     Baron Bunny sit on the PLAYER instead of on the enemy and read the same
///     broadcast from the other side, exactly as <c>CompanionPowers</c> does.
///     No second "an enemy is about to attack" concept was minted -- and the
///     intent-based predicate that already exists
///     (<see cref="CurtainCallHooks.EnemyIntendsAttack"/>) was refused for the
///     Mine's own reason: an intent can be answered and then not happen.
///   * THE INCOMING-DAMAGE REDUCTION is <c>ModifyDamageAdditive</c> returning a
///     negative, which is <see cref="PreventExhaustWardPower"/>'s shape.
///   * THE OUTGOING DAMAGE RIDERS are <c>ModifyDamageAdditive</c> with the
///     shipped <see cref="NextAttackUpPower"/> guard triple.
///   * THE COST DISCOUNT is <c>TryModifyEnergyCostInCombat</c>, which is
///     <see cref="SpotlightDiscountPower"/>'s shape.
///   * THE REACTION EVENT is a call from the ONE place the mod resolves a
///     reaction (<c>ReactionEffects.Resolve</c>), not a new bus.
///
/// WHAT IS GENUINELY NEW, and there are four: a per-instance Block-absorption
/// read (<see cref="IcyPawsPower"/>), an element OVERRIDE on an Attack
/// (<see cref="CompanionOverhaulRiders"/> -- the element used to be read
/// straight off the card at two sites and is now read through one helper), an
/// Attacks-played-this-turn counter
/// (<see cref="CompanionOverhaulLedger"/>), and a Swirl that remembers its
/// element (<see cref="SwirlChargePower"/>).
///
/// PURITY IS LOAD-BEARING HERE. <c>ModifyDamageAdditive</c>,
/// <c>ModifyDamageMultiplicative</c> and <c>TryModifyEnergyCostInCombat</c> are
/// called SPECULATIVELY by previews and tooltips, and a mutation inside one
/// desynced co-op once already (the Vigil's own note,
/// <c>KuragePowers.cs</c>). Every modifier in this file is a pure read; every
/// consumption is in <c>BeforeCardPlayed</c> / <c>AfterCardPlayed</c> /
/// <c>BeforeDamageReceived</c>.
/// </summary>
public sealed class CompanionOverhaulLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, CompanionOverhaulLedger> _byOwner = new();

    /// <summary>
    /// This creature's ledger for this combat, rolled to this round and created
    /// on first ask. Shape lifted from <see cref="KleeOverhaulLedger"/>, for its
    /// reasons: the turn ROLLS ON READ off the combat's round number rather
    /// than on a hook, so the counter needs no power to be present and no
    /// broadcast to fire, and the whole table is dropped when the combat
    /// instance changes so it cannot leak across a run.
    ///
    /// NOT <c>CurtainCallHooks.AttacksPlayed</c>, which counts the same thing:
    /// that map is cleared from <c>FurinaResourceHooks.BeforeSideTurnStart</c>
    /// and therefore only ever for Furina, so a Klee key would accumulate for
    /// the whole fight. That is the defect its own <c>Purge</c> comment records
    /// against <c>CompanionPlays</c>, met a second time; a roll-on-read ledger
    /// cannot have it.
    /// </summary>
    public static CompanionOverhaulLedger For(Creature owner)
    {
        var combat = (object?)owner.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byOwner.Clear();
        }
        if (!_byOwner.TryGetValue(owner, out var ledger))
        {
            ledger = new CompanionOverhaulLedger();
            _byOwner[owner] = ledger;
        }
        ledger.RollTo(owner.CombatState?.RoundNumber ?? 0);
        return ledger;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byOwner.Clear();
    }

    /// <summary>
    /// Attacks this creature has FINISHED playing this turn.
    ///
    /// COUNTED AFTER THE CARD RESOLVES, which is the sim's own timing
    /// (`refpowers.after_card_played`, run after `effects.resolve_card`). So a
    /// card asking "is this the third Attack you played this turn" reads this
    /// number PLUS ONE -- itself -- and both engines spell the question that
    /// way. Per PLAY rather than per series: a doubled Attack is two plays, the
    /// index rule the sim's Juggling already uses.
    /// </summary>
    public int AttacksPlayedThisTurn { get; private set; }

    /// <summary>
    /// SWIRLS resolved for this creature this turn -- the count Heizou's
    /// Heartstopper Strike prints (the Inazuma companion overhaul). Written at
    /// the ONE place the mod resolves a reaction
    /// (<see cref="CompanionOverhaulReactions.Note"/>), which is the site the
    /// sim counts it at too, so neither engine grows a second definition of
    /// "a Swirl happened".
    /// </summary>
    public int SwirlsThisTurn { get; private set; }

    /// <summary>
    /// Damage this creature's CURRENT CARD PLAY has put on enemy HP -- the
    /// total Gorou's Inuzaka All-Round Defense halves. Opened by the emitted
    /// body of any card that reads it and totalled by
    /// <see cref="CompanionOverhaulPlayWatcher"/>, so a card that never asks
    /// pays nothing for the machinery.
    ///
    /// HP, not the swing: it is the conservative reading of "the damage dealt"
    /// (R212's one-way rule -- the doubt pays LESS Block), and it is the number
    /// <c>DamageResult.UnblockedDamage</c> already hands over without a second
    /// definition. Sim twin: `state.mi_damage_dealt_this_card`.
    /// </summary>
    public int DamageDealtThisPlay { get; private set; }

    private int _round = -1;

    /// <summary>One Attack finished. The one write site.</summary>
    public void NoteAttack() => AttacksPlayedThisTurn++;

    /// <summary>
    /// The element the LAST Swirl this turn consumed, or <c>Element.None</c>.
    /// KLEE'S COVEN reads it: Prune's Hexhunter Chime hands "the swirled
    /// element" to the next Bomb set off, and the Chime is armed AFTER the
    /// Swirl its own card makes -- so the latch cannot live on the power the
    /// way Varka's does (<see cref="SwirlChargePower"/>) and lives on the
    /// turn-scoped ledger instead. Sim twin: `state.cvn_swirl_element`,
    /// cleared on the same turn boundary as the count above.
    /// </summary>
    public Element LastSwirlElement { get; private set; } = Element.None;

    /// <summary>One Swirl resolved, consuming <paramref name="element"/>. The
    /// one write site for the count and the latch, so the two cannot disagree
    /// about which Swirl was the last one.</summary>
    public void NoteSwirl(Element element = Element.None)
    {
        SwirlsThisTurn++;
        LastSwirlElement = element;
    }

    /// <summary>A card play begins: the play-scoped total starts clean.
    /// `KokomiOverhaulLedger.BeginPlay`'s shape, and emitted the same way --
    /// at the top of the body of any card that reads it.</summary>
    public void BeginPlay() => DamageDealtThisPlay = 0;

    /// <summary>Damage that reached an enemy's HP during the current play.
    /// The one write site.</summary>
    public void NoteDamage(int hp)
    {
        if (hp > 0) DamageDealtThisPlay += hp;
    }

    /// <summary>Roll the per-turn counter to <paramref name="round"/>. Public
    /// to the pins so a turn boundary can be exercised without a combat.</summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        AttacksPlayedThisTurn = 0;
        SwirlsThisTurn = 0;
        // The coven's latch is turn-scoped like the count it rides beside.
        LastSwirlElement = Element.None;
        // Per PLAY rather than per turn, but zeroed here as well as at the top
        // of a play: a turn boundary is a play boundary too, and a total left
        // standing across one is a number nothing would ever clear.
        DamageDealtThisPlay = 0;
        _round = round;
    }
}

/// <summary>
/// WHICH ELEMENT AN ATTACK APPLIES, once, for the whole mod.
///
/// Before this arm the answer was read straight off the card at two sites --
/// <c>AuraPower.ElementOf</c> and
/// <c>KleeElementalHooks.BeforeDamageReceived</c> -- as
/// <c>cardSource is IElementalCard</c>. Three rewritten companions print an
/// element on the ATTACK rather than on themselves (Bennett's "your next Attack
/// ... applies Pyro", Razor's "for 2 turns, your Attacks apply Electro",
/// Varka's "your next Attack deals 6 more damage of the swirled element"), so
/// the answer now depends on the DEALER as well as the card. Both sites route
/// through here so they cannot drift: an application site and a reaction site
/// that disagreed about a card's element would apply one aura and react with
/// another.
///
/// PURE, because both callers are reached from preview paths.
///
/// WITH NO OVERHAUL POWER STANDING THIS IS THE OLD EXPRESSION, character for
/// character -- which is what makes a release build byte-identical. It also
/// cannot be reached at all in one: the whole file is <c>Compile Remove</c>d.
/// </summary>
public static class CompanionOverhaulRiders
{
    /// <summary>
    /// The element <paramref name="cardSource"/> applies when
    /// <paramref name="dealer"/> plays it.
    ///
    /// THE ORDER IS LAW and is the sim's `companion_overhaul_card_start` order:
    /// the blanket rider first, the two one-shots after, LAST WINS. A one-shot
    /// the player has just bought and is spending on THIS Attack is the more
    /// specific claim than a two-turn blanket, and Varka's is last of the two
    /// because its element is the one the board produced a moment ago.
    ///
    /// AN OVERRIDE BEATS `Element.None` TOO. "Your next Attack applies Pyro" is
    /// a statement about the Attack, not a modifier to one the Attack was
    /// already making, so a card printing no element applies Pyro under it.
    /// </summary>
    public static Element ElementFor(CardModel? cardSource, Creature? dealer)
    {
        // `EB-307`. The card-level read used to be written out here; it moved
        // to <see cref="CatalystCadence.PrintedElement"/> when R242 put the
        // BASE GAME's Strike and Defend in both overhaul starters. A base card
        // is sealed and can never be an `IElementalCard`, so "what does this
        // apply?" has to be able to fall back on WHOSE hand it came from. The
        // riders below still win over it, which is the order they already had
        // over a printed element and the order the sim reads them in.
        var printed = CatalystCadence.PrintedElement(cardSource, dealer);
        if (dealer == null || cardSource is not { Type: CardType.Attack })
        {
            return printed;
        }
        var over = Element.None;
        // BLANKET RIDERS FIRST, in nation order, then the ONE-SHOTS, then
        // Varka's banked Swirl last of all. The Inazuma arm adds one of each --
        // Ayato's Kyouka ("for 2 turns, your Attacks apply Hydro") and Sara's
        // Crowfeather Cover ("your next Attack ... applies Electro") -- and
        // they join the sequence at their own tier rather than at the end,
        // which is what keeps "last wins" meaning the most specific claim
        // rather than the most recently written class. Sim twin:
        // `effects.companion_overhaul_card_start`, same order.
        if (dealer.Powers.OfType<LightningFangPower>().Any()) over = Element.Electro;
        if (dealer.Powers.OfType<KyoukaPower>().Any()) over = Element.Hydro;
        if (dealer.Powers.OfType<PassionOverloadPower>().Any()) over = Element.Pyro;
        if (dealer.Powers.OfType<CrowfeatherCoverPower>().Any()) over = Element.Electro;
        var charge = dealer.Powers.OfType<SwirlChargePower>().FirstOrDefault();
        if (charge != null && charge.SwirledElement != Element.None)
        {
            over = charge.SwirledElement;
        }
        return over == Element.None ? printed : over;
    }
}

/// <summary>
/// THE ARM'S REACTION READERS, called from the ONE place the mod resolves a
/// reaction (<c>ReactionEffects.Resolve</c>). Sim twin:
/// `effects.companion_overhaul_reaction`, called from `reactions._react` at the
/// site that already counts a reaction, so both engines answer "a reaction
/// happened" the same way and neither grows a second definition.
///
/// A CALL, NOT A BUS. <see cref="IProtoExplosionListener"/> exists because the
/// Klee overhaul has THREE independent listeners for one explosion; this arm
/// has two readers and one owner, and an interface fanned over every power for
/// two consumers would be machinery bought for one slice.
/// </summary>
public static class CompanionOverhaulReactions
{
    /// <summary>
    /// A reaction has just resolved. <paramref name="consumedAura"/> is the
    /// element that was standing and is the only surviving handle on it -- the
    /// aura power is removed before this runs, exactly as the sim clears
    /// `enemy.aura` before `_react`.
    /// </summary>
    internal static async Task Note(
        PlayerChoiceContext choiceContext, Reaction reaction,
        Creature target, Creature? dealer, Element consumedAura)
    {
        if (reaction == Reaction.None || dealer == null) return;

        // Dahlia, Favonian Favor: "Whenever a reaction happens this turn, gain
        // 3 Block." The stack IS the 3, so a second copy pays twice. ANY
        // reaction counts; the card names none.
        foreach (var favor in dealer.Powers.OfType<FavonianFavorPower>().ToList())
        {
            // NC-11: power-sourced Block stays raw.
            await CreatureCmd.GainBlock(
                dealer, favor.Amount, ValueProp.Unpowered, null, fast: true);
        }

        // KLEE'S HEXEREI FAMILY, the third, fourth and fifth readers of this
        // event (QUARANTINED, R236 sec.3): Albedo's Tectonic Tide on ANY
        // reaction, Sucrose's Mollis Favonius on a DAMAGING one, Fischl's
        // Sinful Hex on an ELECTRO one -- which is derived from the reaction
        // and the consumed aura rather than passed, so nothing here widened
        // for the slice. `KleeMod.Powers.CompanionHexerei` argues all three.
        await CompanionHexerei.OnReaction(
            choiceContext, reaction, target, dealer, consumedAura);

        if (reaction != Reaction.Swirl) return;

        // THE INAZUMA ARM'S Swirl WINDOW, counted here and nowhere else:
        // Heizou's Heartstopper Strike prints "deals 4 more for each Swirl this
        // turn", and this is the one site the mod resolves a reaction, so the
        // count and Varka's latch below it read the same event.
        // KLEE'S COVEN rides the same write: Prune's Chime needs the ELEMENT
        // this Swirl consumed, and this is the one site the mod has it.
        CompanionOverhaulLedger.For(dealer).NoteSwirl(consumedAura);

        // Varka, Sturm und Drang: "Whenever a Swirl happens, your next Attack
        // deals 6 more damage OF THE SWIRLED ELEMENT."
        var stacks = dealer.Powers.OfType<SturmUndDrangPower>().Sum(p => (int)p.Amount);
        if (stacks <= 0) return;
        var charge = await PowerCmd.Apply<SwirlChargePower>(
            choiceContext, dealer, stacks, applier: dealer, cardSource: null);
        // LAST WINS: two Swirls of different elements before one Attack bank
        // twice (the stack adds) and the Attack carries the LATEST element,
        // which is what "the swirled element" names on a card that has just
        // watched one happen. The sim latches the same way
        // (`Player.mc_swirl_element`).
        if (charge is SwirlChargePower swirl) swirl.Remember(consumedAura);
    }

    /// <summary>
    /// Durin's WHITE form: "enemies take 50% more damage from reactions", as a
    /// multiplier on the REACTION'S OWN damage. 1 with no White standing, which
    /// is what leaves the shipped reaction pipeline byte-identical.
    ///
    /// Stacks are COPIES and each is another 50 percentage points, ADDED rather
    /// than compounded: two Durins are +100%, not +125%. Sim twin:
    /// `effects.companion_overhaul_reaction_mult`.
    /// </summary>
    public static decimal DamageMultiplier(Creature? dealer)
    {
        if (dealer == null) return 1m;
        var stacks = dealer.Powers.OfType<BinaryFormWhitePower>()
            .Sum(p => (int)p.Amount);
        if (stacks <= 0) return 1m;
        return 1m + (CompanionOverhaulLaw.BinaryWhiteReactionMult - 1m) * stacks;
    }
}

// ---------------------------------------------------------------------------
// THE THIRTEEN POWERS
// ---------------------------------------------------------------------------

/// <summary>
/// `EB-337`. THE TWO BLOCK MARKS PRINT WHAT IS ACTUALLY LEFT.
///
/// WHAT THE SEAT SAW (`klee round 7b, opus-act2.md`,
/// section (c)). Thoma's Blazing Barrier sat on the status strip reading
/// "Blazing Barrier 6 -- 6 Block left" while `Block` read 0, and the Bowlbug's
/// 15 went through in full. Nothing was miscounted: the mark is a mark on the
/// Block pool, the pool had been CLEARED at the turn tick, and the mark's
/// printed number was the raw stack -- one Block pool printed twice, once
/// honestly and once from a stack nothing had lowered.
///
/// THE SIM ALREADY DID THIS AND THE MOD DID NOT. `effects.
/// companion_overhaul_turn_start` clamps `mc_icy_paws` to `p.block` and deletes
/// it at zero, and `inazuma_overhaul_turn_start` does the same for
/// `mi_blazing_barrier`; the C# file's own header even claims the behaviour
/// ("One clamps its own Block mark"). Neither power had the hook.
///
/// TWO HALVES, and the first one is the fix. The PRINTED number is read LIVE
/// through <see cref="BlockMarkVar"/>, so it can never be a stale copy of a
/// pool that has moved -- exactly what <see cref="IcyPawsPower.Bite"/> and
/// <c>BlazingBarrierPower.Thicken</c> have always computed for themselves
/// (`min(Amount, Owner.Block)`), now said out loud. The second is housekeeping
/// and mirrors the sim exactly: at the start of the player's turn a mark with
/// no Block behind it is REMOVED, so a spent barrier leaves the strip instead
/// of sitting there reading 0.
///
/// WHY LIVE AND NOT ONLY THE CLAMP. The clamp shares
/// <c>AfterPlayerTurnStart</c> with two powers that GRANT Block
/// (<see cref="SignatureMixPower"/>, <see cref="RevelationPower"/>) and the
/// game guarantees no order between listeners, so a clamp alone would print a
/// number that depended on iteration order. A live read is right in every
/// order, and it is what the rider was always going to pay on.
/// </summary>
internal static class BlockMark
{
    /// <summary>How much of this mark is still backed by standing Block.
    ///
    /// A CANONICAL (compendium) copy has no owner and <c>Owner</c>'s getter
    /// asserts mutability, so it answers the raw stack -- which is what the
    /// face printed before this row and is 0 on a compendium entry either way.
    /// </summary>
    internal static int Left(PowerModel power) =>
        !power.IsMutable
            ? power.Amount
            : System.Math.Min(power.Amount, power.Owner.Block);

    /// <summary>
    /// ONE ABSORPTION, SPENT AGAINST THIS MARK -- `EB-353`. Returns the mark's
    /// new amount, or <c>null</c> when this hit does not touch the mark at all
    /// (nothing marked is standing, or nothing was absorbed) and the rider
    /// must not fire.
    ///
    /// PURE, and that is the point: <c>BlazingBarrierPower.Thicken</c> and
    /// <see cref="IcyPawsPower.Bite"/> both need a live combat to spend their
    /// commands, so the arithmetic is the only half a headless pin can read.
    /// Both call this, so the two marks cannot drift apart again.
    ///
    /// <paramref name="payout"/> IS WHAT MAKES A RIDER FIRE PER ABSORPTION.
    /// Marked-Block-eaten-FIRST means an absorption spends the mark by what it
    /// absorbed; a rider that pays BLOCK puts that Block back under the SAME
    /// mark, because it is the same "this Block" the card is talking about, so
    /// the next hit of a multi-hit attack is another absorption of it. The
    /// paws pass 0 -- their payout is an aura on the attacker, not Block --
    /// which is exactly the marked-first spend they always had, down to and
    /// including the 0 that means "gone".
    /// </summary>
    internal static int? Absorb(int mark, int standing, int incoming,
                                int payout)
    {
        var marked = System.Math.Min(mark, standing);
        var absorbed = System.Math.Min(standing, incoming);
        if (marked <= 0 || absorbed <= 0) return null;
        return System.Math.Max(marked - absorbed, 0) + payout;
    }

    /// <summary>The start-of-turn housekeeping, shared by both marks: a mark
    /// with nothing behind it is gone. Written as a CLAMP rather than as a
    /// clear beside the block reset so it stays correct under Barricade, which
    /// suppresses the reset -- the sim's own words for the same line.</summary>
    internal static async Task ClearIfSpent(PowerModel power)
    {
        if (!power.IsMutable) return;
        if (Left(power) > 0) return;
        await PowerCmd.Remove(power);
    }
}

/// <summary>
/// `EB-337`. <c>{Left}</c>, READ LIVE -- the live half of <see cref="BlockMark"/>.
///
/// A plain <see cref="DynamicVar"/> is a stored number written when something
/// remembers to write it, and the Block pool moves without either mark being
/// told: the turn tick clears it and any hit spends it. So the var asks the
/// power at FORMAT time instead, the same construction and for the same reason
/// as <c>ProtoBombPower.SetOffDamageVar</c> -- the game hands the var itself to
/// SmartFormat and formats it through <c>ToString()</c>, converting through
/// <c>IConvertible</c> only for the numeric formatters, so both are overridden
/// and both answer the same number.
/// </summary>
internal sealed class BlockMarkVar : DynamicVar
{
    internal const string Token = "Left";

    internal BlockMarkVar() : base(Token, 0m)
    {
    }

    private int Live =>
        _owner is PowerModel power ? BlockMark.Left(power) : (int)BaseValue;

    protected override decimal GetBaseValueForIConvertible() => Live;

    public override string ToString() =>
        Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
}

/// <summary>
/// Diona, Icy Paws: "Gain 6 Block. When this Block absorbs damage, apply Cryo
/// to the attacker."
///
/// AMOUNT IS A MARK ON THE BLOCK POOL, not a duration and not a copy count.
/// The engine has ONE Block pool, so "this Block" cannot be a separate pile:
/// the power records how much of the standing Block the card put there, and a
/// hit that spends Block spends the mark with it. That is the marked-Block-eaten
/// -FIRST reading, and it is the conservative one (R212's one-way rule): the
/// paws bite on fewer hits than marked-last would, and a single pool cannot say
/// which coin was spent.
///
/// FIRED BY <see cref="CompanionOverhaulIncomingHit"/>, not by a broadcast of
/// its own -- see that class for why the three incoming readers share one
/// listener.
///
/// `EB-337`: the printed number and the badge are <see cref="BlockMark.Left"/>,
/// not the raw stack. See <see cref="BlockMark"/> for the whole argument; the
/// defect was found on Thoma's twin and both marks are the one construction.
/// </summary>
public sealed class IcyPawsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Icy Paws"),
        // THE STATIC (compendium) ROW CARRIES NO VAR TOKEN -- `EB-353`, found
        // on Thoma's twin and fixed on both because both are the one
        // construction. `PowerModel.HoverTips` calls `DynamicVars.AddTo` on
        // the SMART branch alone (`HasSmartDescription && IsMutable`); the
        // static branch binds the game's own three dumb variables and nothing
        // else, so `{Left}` written here was never bound and the placeholder
        // itself reached the screen.
        ("description",
            "Marks your [gold]Block[/gold]. When it absorbs damage, apply "
          + "[gold]Cryo[/gold] to the attacker."),
        ("smartDescription",
            "[blue]{Left}[/blue] [gold]Block[/gold] left. When it absorbs "
          + "damage, apply [gold]Cryo[/gold] to the attacker."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BlockMarkVar() };

    /// <summary>The badge is the same number the face prints (`EB-337`), for
    /// <c>EB-270</c>'s reason one power over: two numbers on one mark is one
    /// number too many, and the survivor is the one the rider pays on.</summary>
    public override int DisplayAmount => BlockMark.Left(this);

    /// <summary>`EB-337`, the housekeeping half. The sim's
    /// `companion_overhaul_turn_start` deletes a mark with no Block behind it
    /// and this is the same moment: <c>AfterPlayerTurnStart</c> runs after the
    /// block clear (`KleeOverhaulOpening`'s own note establishes it).</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await BlockMark.ClearIfSpent(this);
    }

    /// <summary>The hit is about to be absorbed. Returns nothing: the caller
    /// owns the order, and this owns the arithmetic.</summary>
    internal async Task Bite(PlayerChoiceContext choiceContext,
                             Creature attacker, decimal amount)
    {
        // Block is NOT yet spent at BeforeDamageReceived (the Vigil's own note
        // in KuragePowers.cs establishes it), so `Owner.Block` here is the
        // standing Block and `min(Block, amount)` is exactly what will be
        // absorbed -- the sim's `blocked = min(player.block, dmg)`.
        // `EB-353`: the spend is `BlockMark.Absorb` now, with a payout of 0 --
        // the paws pay an aura and no Block, so there is nothing to put back
        // under the mark and the arithmetic is the marked-first spend it
        // always was.
        var left = BlockMark.Absorb((int)Amount, (int)Owner.Block,
                                    (int)amount, payout: 0);
        if (left == null) return;
        if (!attacker.IsDead)
        {
            await ElementalHit.ApplyOnly(
                choiceContext, attacker, Element.Cryo, Owner);
        }
        if (left.Value > 0)
        {
            await PowerCmd.ModifyAmount(
                choiceContext, this, left.Value - (int)Amount,
                applier: Owner, cardSource: null, silent: true);
        }
        else
        {
            await PowerCmd.Remove(this);
        }
    }
}

/// <summary>
/// Barbara, Melody Loop: "For 3 turns, at the start of your turn apply Hydro to
/// target enemy."
///
/// HOSTED ON THE ENEMY, which is what makes "target enemy" answerable at all: a
/// power holds no target, so the target holds the power. The workshop's own
/// gloss is "a persistent applier on a chosen body", and a body that dies takes
/// the loop with it -- the literal reading, and the one that needs no
/// machinery. <c>Applier</c> is the player who played the card, which is how
/// the loop knows whose turn start it answers.
///
/// Amount is TURNS REMAINING. Its own <c>AfterPlayerTurnStart</c> broadcast
/// rather than a listener, on the argument the three shipped start-of-turn
/// powers already make and which extends: it touches ONLY its own host, and the
/// other three grant the player Block or Strength or apply Vulnerable, so
/// nothing any of the four does can change what another sees. Two Melody Loops
/// are on two different enemies and are independent by construction.
/// </summary>
public sealed class MelodyLoopPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Melody Loop"),
        ("description",
            "At the start of your turn, apply [gold]Hydro[/gold] to this "
          + "enemy. Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Applier == null || player.Creature != Applier) return;
        await ElementalHit.ApplyOnly(
            choiceContext, Owner, Element.Hydro, Applier);
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// The base of the three riders that speak about YOUR NEXT ATTACK and are spent
/// by it -- Bennett's Passion Overload, Varka's banked Swirl charge, and Mika's
/// cost discount.
///
/// THE LATCH IS WHY THIS CLASS EXISTS, and the shipped
/// <see cref="NextAttackUpPower"/> did not need it. That power is applied by a
/// SKILL, so an Attack that consumes it can never be the Attack that made it;
/// Mika's Starfrost Swirl IS an Attack that applies its own rider, so
/// "remove myself after any Attack" would have eaten the discount the card just
/// printed. So the amount standing BEFORE the play is latched in
/// <c>BeforeCardPlayed</c> and only that much is spent in
/// <c>AfterCardPlayed</c> -- anything the play itself added survives. The sim
/// reaches the same answer from the other side by consuming at the head of the
/// card's resolution, before its effects run.
///
/// <c>CardPlay</c> identity is the latch key, the idiom
/// <see cref="SparkAttackCostPower"/> documents: a stale reference on a clone
/// can never equal a live <c>CardPlay</c>, so the worst case is a no-op.
/// </summary>
public abstract class NextAttackRiderPower : PowerModel
{
    /// <summary>
    /// `EB-540`. THE CLAUSE EVERY RIDER OWES, spelled once on the class that
    /// owns the rule.
    ///
    /// THE FIND (Kokomi r19 lane 2). "Ambush is a `skill` whose entire text is
    /// 'Deal 5 damage.' Bennett buffs 'your next Attack', so Bennett's buff sat
    /// unspent on my bar while Ambush hit. The card types are internally
    /// consistent, but the faces give a blind reader no warning that a damage
    /// card can fail to be an Attack." The seat played the buff and the Skill
    /// in the same turn and read the result off its own status bar.
    ///
    /// THE RULE IS THIS CLASS'S: <see cref="BeforeCardPlayed"/> refuses on
    /// <c>cardPlay.Card?.Type != CardType.Attack</c> and every subclass's
    /// <c>ModifyDamageAdditive</c> asks the same of <c>cardSource</c>. So the
    /// sentence belongs here rather than on a kit's keyword: it is true of
    /// every rider, on every character, and of no other buff in the mod.
    ///
    /// AND IT SAYS WHAT IS TRUE AND NOT MORE. "A Skill's damage is not an
    /// Attack" is the reading the row proposed, and it is too wide by one
    /// surface: `EB-469`/`EB-481` measured the opposite half -- a Skill's
    /// damage clause is emitted as `ValueProp.Move`, so Weak DOES cut it and
    /// Vulnerable DOES raise it, and the base game's own Weak line says
    /// "Attacks" about exactly that. What is narrow and true is the card TYPE:
    /// a rider reads the card, and a Skill is not one.
    /// </summary>
    ///
    /// FORTY-SIX CHARACTERS, and it is four faces' worth of ceiling: the
    /// longest of them (`CrowfeatherCoverPower`) runs to 119 of 125 with this
    /// on it, so no rider takes an exception for a sentence every rider owes.
    /// "Never a Skill" rather than "never a Skill's damage" is what paid for
    /// that, and it loses nothing: the rule is about the card's TYPE and a
    /// Skill that deals no damage was never spending the buff either.
    protected const string CardTypeClause =
        " Only an Attack card spends it, never a Skill.";

    private CardPlay? _spendingOn;
    private int _spending;

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        _spendingOn = null;
        _spending = 0;
        if (cardPlay.Card?.Type != CardType.Attack) return Task.CompletedTask;
        if (cardPlay.Card?.Owner?.Creature != Owner) return Task.CompletedTask;
        _spendingOn = cardPlay;
        _spending = (int)Amount;
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!ReferenceEquals(_spendingOn, cardPlay)) return;
        _spendingOn = null;
        var spent = _spending;
        _spending = 0;
        if (spent <= 0) return;
        if (Amount <= spent)
        {
            await PowerCmd.Remove(this);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, this, -spent,
            applier: Owner, cardSource: null, silent: true);
    }
}

/// <summary>
/// Bennett, Passion Overload: "Your next Attack this turn deals 4 more and
/// applies Pyro."
///
/// A SECOND CLASS RATHER THAN A RETUNE of the shipped
/// <see cref="NextAttackUpPower"/> of the same name, on the arm's standing
/// rule: a flag-off build has to keep meaning what it printed, and the shipped
/// power carries no element clause at all.
///
/// The element half is read through <see cref="CompanionOverhaulRiders"/>; only
/// the damage half is here. "THIS TURN" is the removal in
/// <c>AfterSideTurnEnd</c> -- the shipped
/// <see cref="AttackUpThisTurnPower"/>'s own shape, and order-independent,
/// which is why it keeps its own broadcast.
/// </summary>
public sealed class PassionOverloadPower : NextAttackRiderPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Passion Overload"),
        ("description",
            "Your next Attack this turn deals [blue]{Amount}[/blue] additional "
          + "damage and applies [gold]Pyro[/gold]." + CardTypeClause),
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
/// Varka's banked charge: "your next Attack deals 6 more damage of the swirled
/// element." Applied by <see cref="CompanionOverhaulReactions"/> on every
/// Swirl, never by a card.
///
/// IT REMEMBERS AN ELEMENT, which no power in this mod did before. A plain enum
/// field is safe where a <c>Creature</c> reference would not be: it is a value
/// type, so <c>MutableClone</c>'s shallow copy carries it correctly and
/// <c>DeepCloneFields</c> has nothing to do.
/// </summary>
public sealed class SwirlChargePower : NextAttackRiderPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sturm und Drang"),
        ("description",
            "Your next Attack deals [blue]{Amount}[/blue] additional damage of "
          + "the last [gold]Swirl[/gold]ed element." + CardTypeClause),
    };

    /// <summary>The element the latest Swirl carried. LAST WINS.</summary>
    public Element SwirledElement { get; private set; } = Element.None;

    public void Remember(Element element) => SwirledElement = element;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount;
    }
}

/// <summary>
/// Mika, Starfrost Swirl: "Your next Attack costs 1 less."
///
/// NO TURN LIMIT, because the card prints none -- it is spent by the next
/// Attack whenever that is. <c>TryModifyEnergyCostInCombat</c> is the hook, and
/// it is PURE: the consumption is the rider latch, so the cost query may be
/// asked as often as the screen likes.
/// </summary>
public sealed class StarfrostDiscountPower : NextAttackRiderPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Starfrost Swirl"),
        ("description", "Your next Attack costs [blue]{Amount}[/blue] less."
                      + CardTypeClause),
    };

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        // THROUGH `SparkCost.OwnerCreatureOf`, NOT `card.Owner`, and that is
        // EB-94 met from the other side: `CardModel.Owner`'s getter asserts
        // mutability and THROWS on the canonical models the compendium hands
        // out, and a cost query is asked of those. The safe accessor returns
        // null for a card nobody holds, which is the right answer anyway --
        // a card with no owner has no rider to discount it.
        if (SparkCost.OwnerCreatureOf(card) != Owner) return false;
        if (card.Type != CardType.Attack || originalCost <= 0m) return false;
        modifiedCost = System.Math.Max(0m, originalCost - Amount);
        return modifiedCost != originalCost;
    }
}

/// <summary>
/// Razor, Lightning Fang: "For 2 turns, your Attacks apply Electro and deal 3
/// more."
///
/// Amount is TURNS REMAINING, so the damage it pays is the constant rather than
/// the stack -- a second copy makes the window longer, not the hits bigger,
/// which is the arm's standing rule for a timed power. The element half is read
/// through <see cref="CompanionOverhaulRiders"/>.
/// </summary>
public sealed class LightningFangPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lightning Fang"),
        ("description",
            "Your Attacks apply [gold]Electro[/gold] and deal "
          + $"[blue]{CompanionOverhaulLaw.LightningFangDamage}[/blue] additional damage. "
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
        return CompanionOverhaulLaw.LightningFangDamage;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Varka, Sturm und Drang: "Whenever a Swirl happens, your next Attack deals 6
/// more damage of the swirled element." PERMANENT; Amount is the damage each
/// copy banks, so two copies bank twice per Swirl.
///
/// The power itself does nothing on a hook: it is read by
/// <see cref="CompanionOverhaulReactions"/>, which is the one place the mod
/// knows a Swirl happened AND what it swirled.
/// </summary>
public sealed class SturmUndDrangPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sturm und Drang"),
        ("description",
            "Whenever a [gold]Swirl[/gold] happens, your next Attack deals "
          + "[blue]{Amount}[/blue] additional damage of the swirled element."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Dahlia, Favonian Favor: "Gain 7 Block. Whenever a reaction happens this
/// turn, gain 3 Block." (The 7 is on the card.)
///
/// Amount is the Block PER REACTION, so a second copy pays twice. "This turn"
/// is the removal in <c>AfterSideTurnEnd</c>, the shipped
/// <see cref="AttackUpThisTurnPower"/>'s shape.
/// </summary>
public sealed class FavonianFavorPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Favonian Favor"),
        ("description",
            "Whenever an [gold]Elemental Reaction[/gold] happens this turn, "
          + "gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Durin, Binary Form / WHITE: "enemies take 50% more damage from reactions."
///
/// The power stores nothing and hooks nothing: the multiplier is computed in
/// ONE place (<see cref="CompanionOverhaulReactions.DamageMultiplier"/>) and
/// spent at the two sites a reaction deals damage, so this power's whole job is
/// to be present and countable -- the same argument
/// <see cref="ExplosivesWorkshopGrowthPower"/> makes for growth.
/// </summary>
public sealed class BinaryFormWhitePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Binary Form: White"),
        ("description",
            "Enemies take 50% more damage from [gold]Elemental Reactions[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Durin, Binary Form / DARK: "your Pyro Attacks that react deal 8 more."
///
/// ALL THREE CLAUSES ARE READ IN THE ADDITIVE PHASE, which is where they can be
/// read purely. "Pyro" is the element the play ACTUALLY applies
/// (<see cref="CompanionOverhaulRiders"/>), so Bennett's and Varka's overrides
/// are honoured. "Attack" is the card type. "That react" is a FORECAST off the
/// standing aura -- <c>ReactionTable.Lookup</c> against the aura the target is
/// carrying right now, which is exactly the read
/// <see cref="AuraPower.ModifyDamageMultiplicative"/> already makes one phase
/// later, and it is available because the aura is not consumed until
/// <c>AfterDamageReceived</c>.
///
/// The forecast is what lets the 8 land BEFORE the amplifier, in the same
/// additive phase Strength lands in, which is where the sim puts it too.
/// </summary>
public sealed class BinaryFormDarkPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Binary Form: Dark"),
        ("description",
            "Your [gold]Pyro[/gold] Attacks that react deal "
          + "[blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (CompanionOverhaulRiders.ElementFor(cardSource, dealer) != Element.Pyro)
        {
            return 0m;
        }
        var aura = AuraCmd.Find(target);
        if (aura == null) return 0m;
        return ReactionTable.Lookup(aura.Element, Element.Pyro) == Reaction.None
            ? 0m : Amount;
    }
}

/// <summary>
/// Dahlia, Sacramental Shower: "Place a Shower: the next time an enemy attacks
/// you, deal 9 Hydro damage to it first."
///
/// Amount is the number of SHOWERS placed, and one hit spends one -- "the next
/// time an enemy attacks you" is one attack, so two copies answer two attacks
/// and never one attack twice. Fired by
/// <see cref="CompanionOverhaulIncomingHit"/>.
/// </summary>
public sealed class SacramentalShowerPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sacramental Shower"),
        // THE STATIC (compendium) ROW CARRIES NO VAR TOKEN -- `EB-353`'s
        // finding, one class over: `PowerModel.HoverTips` calls
        // `DynamicVars.AddTo` on the SMART branch alone, so a token written
        // here would reach the screen as a placeholder.
        ("description",
            "The next time an enemy attacks you, deal "
          + $"[blue]{CompanionOverhaulLaw.ShowerDamage}[/blue] [gold]Hydro[/gold] "
          + "damage to it first."),
        // `EB-438`. THE STORED NUMBER, FOLDED THE WAY THE CARD FACES ARE.
        //
        // The r6 act-1 seat read this badge and lost the arithmetic on it:
        // "the buff line printed `Sacramental Shower 1 -- The next time an
        // enemy attacks you, deal 9 Hydro damage to it first`, and when it
        // fired the ship went 38 to 32, i.e. 6. I was carrying Weak 2. Card
        // text on this kit folds Weak into the printed number reliably and
        // well; the STORED-BUFF text does not. If you are going to fold
        // modifiers into printed numbers -- and you should, it's very good --
        // the buff readouts have to do it too, or the one place that doesn't
        // becomes the place you get killed."
        //
        // The fold is not a new arithmetic: <see cref="Spring"/> deals through
        // `ElementalHit.Deal` with `powered: true`, whose first step is
        // `SimDamagePipeline.DealerMods` -- Strength, then Weak's three
        // quarters. <see cref="ShowerVar"/> asks that same call at FORMAT
        // time, so the badge and the hit cannot drift.
        ("smartDescription",
            "The next time an enemy attacks you, deal "
          + $"[blue]{{{ShowerVar.Token}}}[/blue] [gold]Hydro[/gold] "
          + "damage to it first."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new ShowerVar() };

    internal async Task Spring(PlayerChoiceContext choiceContext,
                               Creature attacker)
    {
        await SpendOne(choiceContext);
        await ElementalHit.Deal(
            choiceContext, attacker, Element.Hydro,
            CompanionOverhaulLaw.ShowerDamage, Owner);
    }

    private async Task SpendOne(PlayerChoiceContext choiceContext)
    {
        if (Amount <= 1)
        {
            await PowerCmd.Remove(this);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, this, -1, applier: Owner, cardSource: null,
            silent: true);
    }
}

/// <summary>
/// `EB-438`. <c>{Shower}</c>, READ LIVE.
///
/// A plain <see cref="DynamicVar"/> is a stored number written when something
/// remembers to write it, and the terms that move this one belong to KOKOMI
/// and move between the placing and the springing: the Shower is placed on one
/// turn and answers an attack on the next, with a Weak applied in between.
/// So the var asks the pipeline at FORMAT time, the construction
/// <see cref="BlockMarkVar"/> and <c>ProtoBombPower.SetOffDamageVar</c> both
/// use -- the game hands the var itself to SmartFormat and formats it through
/// <c>ToString()</c>, converting through <c>IConvertible</c> only for the
/// numeric formatters, so both are overridden and both answer one number.
///
/// THE DEALER'S TERMS AND NOT THE TARGET'S, because the target is not known
/// until the attack lands: `Spring` hits whichever enemy attacked. What a
/// badge can promise is the half that is already decided, which is exactly
/// the half the seat was reading Weak off.
/// </summary>
internal sealed class ShowerVar : DynamicVar
{
    internal const string Token = "Shower";

    internal ShowerVar() : base(Token, CompanionOverhaulLaw.ShowerDamage)
    {
    }

    private int Live =>
        _owner is PowerModel { Owner: not null } power
            ? (int)SimDamagePipeline.DealerMods(power.Owner, BaseValue)
            : (int)BaseValue;

    protected override decimal GetBaseValueForIConvertible() => Live;

    public override string ToString() =>
        Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
}

/// <summary>
/// Amber, Explosive Puppet: "Place Baron Bunny: the next time an enemy attacks
/// you, take 3 less and deal 8 Pyro damage to all enemies."
///
/// THE TWO HALVES SIT ON DIFFERENT HOOKS AND THAT IS FORCED. "Take 3 less" has
/// to change the damage number, and the only hook that can is
/// <c>ModifyDamageAdditive</c>, which the engine calls SPECULATIVELY for the
/// intent preview and which therefore may not mutate anything. So the reduction
/// is a pure read of a standing decoy and the CONSUMPTION plus the volley
/// happen in <see cref="CompanionOverhaulIncomingHit"/>, one phase later, on
/// the number this modifier already reduced. The sim, which previews no
/// incoming damage, does both in one place and says so.
///
/// Amount is the number of decoys; one hit spends one.
/// </summary>
public sealed class BaronBunnyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Baron Bunny"),
        ("description",
            "The next time an enemy attacks you, take "
          + $"[blue]{CompanionOverhaulLaw.BaronBunnyReduction}[/blue] less damage and deal "
          + $"[blue]{CompanionOverhaulLaw.BaronBunnyDamage}[/blue] [gold]Pyro[/gold] "
          + "damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        // PURE. One decoy reduces one hit; the reduction floors at the hit's
        // own size rather than healing.
        if (target != Owner || amount <= 0m) return 0m;
        if (dealer == null || dealer.Player != null) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        return -System.Math.Min(amount, CompanionOverhaulLaw.BaronBunnyReduction);
    }

    internal async Task Explode(PlayerChoiceContext choiceContext)
    {
        if (Amount <= 1)
        {
            await PowerCmd.Remove(this);
        }
        else
        {
            await PowerCmd.ModifyAmount(
                choiceContext, this, -1, applier: Owner, cardSource: null,
                silent: true);
        }
        var combat = Owner.CombatState;
        if (combat == null) return;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            await ElementalHit.Deal(
                choiceContext, enemy, Element.Pyro,
                CompanionOverhaulLaw.BaronBunnyDamage, Owner);
        }
    }
}

/// <summary>
/// Eula, Glacial Illumination: "Place a Lightfall Sword on target: for 2 turns
/// it counts your Attacks; then it deals 8 plus 5 per Attack counted."
///
/// HOSTED ON THE ENEMY, like Barbara's loop and for the same reason -- the card
/// says "on target", so the target carries it. Amount is TURNS REMAINING and
/// <see cref="Counted"/> is the tally; the tally is a plain int rather than a
/// second power, because a counter inside another power is not a power and
/// should not appear as one.
///
/// TICK, THEN FIRE AT ZERO, which is the opposite order from the arm's volleys
/// and is what the printed sentence says: it counts for two turns and THEN it
/// deals. THE BLADE'S DAMAGE CARRIES NO ELEMENT, because the card's text names
/// none -- the same call <see cref="SolarIsotomaBloomPower"/> made.
/// </summary>
public sealed class LightfallSwordPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lightfall Sword"),
        ("description",
            "Counts its owner's Attacks. When it falls, deals "
          + $"[blue]{CompanionOverhaulLaw.LightfallBase}[/blue] damage plus "
          + $"[blue]{CompanionOverhaulLaw.LightfallPerAttack}[/blue] per "
          + "Attack counted. Falls in [blue]{Amount}[/blue] "
          + "{Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Attacks the blade has counted.</summary>
    public int Counted { get; private set; }

    /// <summary>One Attack landed on the ledger.</summary>
    public void Note() => Counted++;

    internal async Task Tick(PlayerChoiceContext choiceContext)
    {
        if (Amount > 1)
        {
            await PowerCmd.TickDownDuration(this);
            return;
        }
        var damage = CompanionOverhaulLaw.LightfallBase
                   + CompanionOverhaulLaw.LightfallPerAttack * Counted;
        var host = Owner;
        await PowerCmd.Remove(this);
        var dealt = SimDamagePipeline.DealerMods(Applier, damage);
        await CreatureCmd.Damage(
            choiceContext, host,
            (int)SimDamagePipeline.TargetMods(host, dealt),
            ValueProp.Unpowered, dealer: null, cardSource: null,
            cardPlay: null);
    }
}

// ---------------------------------------------------------------------------
// THE TWO LISTENERS
// ---------------------------------------------------------------------------

/// <summary>
/// THE ARM'S INCOMING-HIT ORDER, made explicit -- EB-19/races-c applied a third
/// time. Three of the second wave's powers answer an enemy's hit, two of them
/// put an element on the board and can kill the attacker, so a deck holding two
/// would have had its reactions decided by listener iteration order. ONE tenant
/// drives all three, in the sim's sequence:
///
///     SacramentalShowerPower   (9 Hydro at the attacker, before its hit)
///     BaronBunnyPower          (the volley; its -3 is already in `amount`)
///     IcyPawsPower             (Cryo at the attacker, off the Block absorbed)
///
/// THE SHOWER IS FIRST, in sheet order, and the paws are LAST because they read
/// the absorption the other two have already re-priced.
///
/// <c>BeforeDamageReceived</c>, the hook Klee's Mine uses, for the Mine's own
/// stated reasons: it fires before the hit lands, before Block is spent, and it
/// carries a <c>PlayerChoiceContext</c> -- and it is fanned to every model in
/// the combat, so a listener that is on nobody sees it. The guards are the
/// Mine's, read from the other side: the VICTIM is a player and the DEALER is
/// not, and the hit is a powered attack.
/// </summary>
public sealed class CompanionOverhaulIncomingHit : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static CompanionOverhaulIncomingHit? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<CompanionOverhaulIncomingHit>(
            ModelDb.GetId<CompanionOverhaulIncomingHit>());
        yield return _instance;
    }

    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target.Player == null) return;          // a player is being hit
        if (dealer == null || dealer.Player != null) return;   // by an enemy
        if (!props.IsPoweredAttack()) return;

        foreach (var shower in target.Powers.OfType<SacramentalShowerPower>().ToList())
        {
            await shower.Spring(choiceContext, dealer);
        }
        foreach (var bunny in target.Powers.OfType<BaronBunnyPower>().ToList())
        {
            await bunny.Explode(choiceContext);
        }
        foreach (var paws in target.Powers.OfType<IcyPawsPower>().ToList())
        {
            await paws.Bite(choiceContext, dealer, amount);
        }
        // THE INAZUMA ARM'S ONE INCOMING READER, LAST. Thoma's Blazing Barrier
        // is the paws' construction with a Block payout instead of an aura, and
        // it goes after them for the reason they go after the two traps: it
        // reads the absorption everything above it has already re-priced. It
        // cannot change what the paws saw either -- both read `Owner.Block`,
        // which no reader in this list moves.
        foreach (var barrier in target.Powers.OfType<BlazingBarrierPower>().ToList())
        {
            await barrier.Thicken(choiceContext, amount);
        }
    }
}

/// <summary>
/// THE ARM'S CARD-PLAY WATCHER: the two things that have to be counted on every
/// Attack whether or not any power of this arm is on the player.
///
///   * <see cref="CompanionOverhaulLedger"/>'s Attacks-played-this-turn, noted
///     AFTER the card resolves so it mirrors the sim's
///     `refpowers.after_card_played`.
///   * Eula's blades, noted BEFORE the card resolves so it mirrors the sim's
///     tally at the head of `companion_overhaul_card_start` -- and so an Attack
///     that kills the blade's host is not counted by a blade that will never
///     pay out.
///
/// A LISTENER RATHER THAN A POWER, because both facts have to be true for a
/// player carrying none of this arm's powers: Razor's card asks the ledger the
/// turn it is drawn, and Eula's blade lives on the ENEMY, so there is nothing
/// on the player to hang either off.
/// </summary>
public sealed class CompanionOverhaulPlayWatcher : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static CompanionOverhaulPlayWatcher? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<CompanionOverhaulPlayWatcher>(
            ModelDb.GetId<CompanionOverhaulPlayWatcher>());
        yield return _instance;
    }

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null || cardPlay.Card?.Type != CardType.Attack)
        {
            return Task.CompletedTask;
        }
        var combat = owner.CombatState;
        if (combat == null) return Task.CompletedTask;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            foreach (var blade in enemy.Powers.OfType<LightfallSwordPower>().ToList())
            {
                // Only the blades this player planted: in co-op the other
                // seat's Attacks are not on this ledger (R205's rule, met
                // again).
                if (blade.Applier == owner) blade.Note();
            }
        }
        return Task.CompletedTask;
    }

    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null || cardPlay.Card?.Type != CardType.Attack)
        {
            return Task.CompletedTask;
        }
        CompanionOverhaulLedger.For(owner).NoteAttack();
        return Task.CompletedTask;
    }

    /// <summary>
    /// THE INAZUMA ARM'S PER-PLAY DAMAGE TOTAL, for Gorou's "Block equal to
    /// half the damage dealt". Totalled here rather than on a power because
    /// the card that reads it carries none: it is an Attack that banks its own
    /// hit, and there is nothing on the player to hang the count off.
    ///
    /// CARD-SOURCED AND OWNED, which is what the sentence names and what keeps
    /// the two engines counting the same thing: the sim adds `hp_dmg` for
    /// `source in ("card", "attack")`, and this arm's own power-sourced hits go
    /// through <c>ElementalHit.Deal</c>, which passes no dealer and no card
    /// source, so neither engine counts them.
    /// </summary>
    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer == null || dealer.Player == null) return Task.CompletedTask;
        if (cardSource == null || ReferenceEquals(target, dealer))
        {
            return Task.CompletedTask;
        }
        CompanionOverhaulLedger.For(dealer)
            .NoteDamage((int)result.UnblockedDamage);
        return Task.CompletedTask;
    }
}
