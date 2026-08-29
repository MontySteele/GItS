using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Bake-Kurage on the field.
///
/// Stacks ARE turns remaining (the OzSummonPower grammar). Re-summoning
/// REFRESHES rather than adds -- a second jellyfish is not a bigger jellyfish
/// -- which is why <see cref="KurageSummon.Field"/> below sets the duration to
/// max(current, turns) instead of applying stacks.
///
/// The pulse reads Charge and never spends it. Sim order is HIT, then Block,
/// then tick down; the manual TickDownDuration after the volley preserves it,
/// same as Oz.
/// </summary>
public sealed class KurageSummonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bake-Kurage"),
        ("description",
            "At the end of your turn, the jellyfish deals "
          + $"{KokomiConstants.KuragePulseBase} plus "
          + $"{KokomiConstants.KuragePulsePerCharge} per [gold]Charge[/gold] "
          + "damage and applies [gold]Hydro[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// The number the pulse will deal right now. Public so the card face and
    /// the hover tip read the SAME arithmetic the hit uses -- the Furina
    /// legibility lesson (preview and effect must not be able to drift).
    /// </summary>
    public static int PulseDamage(Creature? owner) =>
        KokomiConstants.KuragePulseBase
        + PulseMultiplier(owner) * KokomiResources.GetCharge(owner);

    /// <summary>
    /// The bank read, INCLUDING every copy of Before Sun and Moon (R73/G2).
    ///
    /// Mirrors tier0 `player_turn_end_triggers`:
    ///     multiplier = KURAGE_PULSE_PER_CHARGE + powers["kurage_amp"]
    ///
    /// Stacking is [USER]-ratified (G2) over a ban on the effect class, so
    /// the sum here is the ruling and not an accident of PowerStackType.
    /// It sits behind PulseDamage rather than at the call site so the card
    /// face, the hover tip and the hit cannot disagree -- the Furina
    /// legibility lesson, which is why PulseDamage was made public at all.
    /// </summary>
    public static int PulseMultiplier(Creature? owner) =>
        KokomiConstants.KuragePulsePerCharge
        + (owner?.Powers.OfType<KurageAmpPower>().FirstOrDefault()?.Amount ?? 0);

    /// <summary>
    /// NOT A BROADCAST OVERRIDE ANY MORE. This method is a tenant of BOTH
    /// filed end-of-turn races and TurnEndSequencer settles both at once:
    ///
    /// EB-19/races-c -- the HYDRO leg of the three volleys, fired LAST
    /// (tier0 order Pyro -> Electro -> Hydro).
    /// EB-19/races-a -- its Block grant lands strictly AFTER
    /// MasqueRedDeathPower.PayBondOfLife, because the sim pays the Bond at the
    /// top of `effects.player_turn_end_triggers` and only then reaches
    /// `kurage_summon`.
    /// </summary>
    public async Task FirePulse(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;

        var damage = PulseDamage(Owner);

        var candidates = CombatState.HittableEnemies.ToList();
        if (candidates.Count > 0)
        {
            var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target != null)
            {
                await ElementalHit.Deal(
                    choiceContext, target, Element.Hydro, damage, Owner);
            }
        }

        // Block lands whether or not an enemy was standing: under the R52
        // healing law her mending is Block, and a pulse into an empty board
        // still mends. Baseline is 0 since the starter rework; the drafted
        // half rides the same line so restoring the baseline is one constant.
        var block = KokomiConstants.KuragePulseBlock
                    + KurageWardPower.WardAmount(Owner);
        if (block > 0)
        {
            // NC-11 (R116, Errata Batch 2 item 4): power-sourced block is
            // RAW. Unpowered, not Move, so neither Frail nor Dexterity sees
            // it -- tier0 writes `p.block +=` here, deliberately bypassing
            // `powers.modify_block_gained` (the funnel exemption documented
            // at powers.py:75-81, ruled canonical).
            await CreatureCmd.GainBlock(Owner, block, ValueProp.Unpowered, null);
        }

        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>Fielding and refreshing the jellyfish.</summary>
public static class KurageSummon
{
    /// <summary>
    /// REFRESH, NEVER STACK. tier0 _op_summon_kurage:
    /// powers["kurage_summon"] = max(existing, turns).
    /// </summary>
    public static async Task Field(
        PlayerChoiceContext choiceContext, Creature owner, int turns,
        CardModel? source)
    {
        var existing = owner.Powers
            .FirstOrDefault(p => p is KurageSummonPower);
        if (existing != null)
        {
            var have = (int)existing.Amount;
            if (turns > have)
            {
                await PowerCmd.ModifyAmount(
                    choiceContext, existing, turns - have, owner, source, false);
            }
            return;
        }

        // SOFTLOCK FIX 2026-07-26. This used to call the NON-generic
        // PowerCmd.Apply and hand it ModelDb.Power<KurageSummonPower>() --
        // the CANONICAL prototype, which is immutable. That overload's second
        // statement is `power.AssertMutable()`, which throws
        // CanonicalModelException on a canonical model. The generic Apply<T>
        // is the one that does the missing step:
        //
        //     PowerModel powerModel = ModelDb.Power<T>();
        //     PowerModel power = FindExistingInstanceForStacking(...);
        //     if (power == null)
        //     {
        //         power = powerModel.ToMutable();   // <-- this
        //         await Apply(choiceContext, power, target, ...);
        //     }
        //
        // The early return above means this line is reached ONLY when no
        // jellyfish is fielded, so it threw on every FIRST Bake-Kurage of a
        // combat. An exception inside an awaited action leaves the action
        // queue unfinished, which surfaces as a SOFTLOCK rather than a crash
        // -- the game simply stops advancing, with nothing in the log that
        // names a card.
        //
        // Using the generic overload rather than adding .ToMutable() here is
        // deliberate: it is the idiom every other PowerCmd.Apply call in this
        // assembly already uses, so the fix removes an oddity instead of
        // adding a second correct-but-unusual spelling. The stacking branch
        // inside it is unreachable from here (the early return owns that
        // case), so refresh-never-stack is unaffected.
        await PowerCmd.Apply<KurageSummonPower>(
            choiceContext, owner, turns, owner, source, false);
    }
}

/// <summary>
/// Kurage's Oath -- the jellyfish's canon second job, drafted rather than
/// baseline.
///
/// COUPLING, on the record (playtest sprint P1): this power pays out once per
/// PULSE, so its real value is (ward x pulses per play). It owns only the
/// first factor -- the second is KurageDuration and the bake_kurage upgrade.
/// The 12 was measured at duration 1. Raising the duration reprices this card
/// without editing it; the sim pins that (see
/// test_oath_ward_is_pinned_to_the_pulse_frequency_it_was_measured_at) and it
/// carries a [USER] "maybe too strong" flag as the first knob back.
/// </summary>
public sealed class KurageWardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage's Oath"),
        ("description",
            "Each [gold]Bake-Kurage[/gold] pulse also grants {Amount} Block."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int WardAmount(Creature? owner)
    {
        if (owner == null) return 0;
        var power = owner.Powers.FirstOrDefault(p => p is KurageWardPower);
        return power == null ? 0 : (int)power.Amount;
    }
}

/// <summary>
/// "Before Sun and Moon" (R73, Neap Tide v2.1). +1 to the Bake-Kurage pulse
/// MULTIPLIER, and it stacks.
///
/// SHARED SCHEMA NOTE (sprint exit criterion). The sim models this as an
/// ordinary integer power, `powers["kurage_amp"]`, summed straight into the
/// multiplier; here it is a Counter PowerModel whose Amount is summed the
/// same way by <see cref="KurageSummonPower.PulseMultiplier"/>. The two
/// representations differ -- a dict entry against a power instance -- but the
/// ARITHMETIC is identical and neither side caps. That matters because
/// PowerStackType is the kind of thing a later reader "fixes": switching this
/// to Single would silently implement the stacking BAN that [USER] considered
/// and rejected at G2, and it would do so without touching a number anyone
/// would think to re-measure. tier0's
/// test_before_sun_and_moon_raises_the_multiplier_and_stacks is the sim-side
/// pin. `klee-mod/KleeTests` (EB-105) could hold the C#-side one -- summing
/// Amounts is pure arithmetic, well inside its headless boundary -- but no
/// test claims it yet, so until one does this comment is the C#-side pin.
///
/// It multiplies an uncapped, never-spent bank (R80), so it is the steepest
/// term on her sheet: every other scaling card adds a term, this moves a
/// coefficient. C4 reports stack counts with no threshold (R14).
///
/// KNOWN LEGIBILITY GAP, flagged not hidden: KurageSummonPower's own
/// description prints the BASE multiplier, because Localization is resolved
/// on the canonical model and has no owner to read an amp off. So a player
/// holding two copies sees the Bake-Kurage text quote the unamped number
/// while the hit uses the amped one. The hit and the tip are still in sync
/// (both route through PulseDamage); it is the static face text that lags.
/// Closing it needs the DynamicVar treatment the Furina legibility sprint
/// gave her riders, which is a bigger change than this ruling authorises.
/// </summary>
public sealed class KurageAmpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Before Sun and Moon"),
        ("description",
            "Each [gold]Bake-Kurage[/gold] pulse reads your "
          + "[gold]Charge[/gold] for {Amount} more damage per point."),
    };

    public override PowerType Type => PowerType.Buff;

    // Counter, NOT Single. See the stacking note above -- this is a ruling.
    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// The Ceremonial Garment: her Burst's state (kit card
/// <see cref="Cards.Kokomi.CeremonialGarment"/>; Nereid's Ascension enters it
/// too).
///
/// TWO riders, and the damage one is the whole point of the Burst. While the
/// state holds:
///   - her ATTACKS read the Charge bank, +1 damage per
///     <see cref="KokomiConstants.GarmentChargeDivisor"/> Charge, per hit;
///   - her attacks ALSO grant Block (the Charlotte precedent; in canon the
///     burst's attacks damage AND restore the party).
///
/// The read is a READ: nothing here decrements the bank, and if it ever
/// starts to, every scaling number on her sheet was measured against a bank
/// that only grows and is silently wrong.
///
/// Both riders are applied from outside the card faces -- the damage one here
/// in ModifyDamageAdditive, the Block one in
/// <see cref="KokomiGarmentHooks"/> -- because they must catch every attack
/// she plays, drafted and generated alike, and no card face can know that.
///
/// THE CASKET LINK IS INERT AND SHIPS ANYWAY. Casting the Burst refreshes a
/// fielded Bake-Kurage (Tamakushi Casket, her A1). At KurageDuration 1 a
/// fielded jellyfish is always at exactly 1, so refresh-to-full is a no-op
/// unless the Burst goes off the same turn the Kurage was played. Parity means
/// parity: the sim carries the same dead link, [USER] confirmed shipping it
/// rather than holding the build, and the Burst rework inherits it with the
/// playtest's evidence attached.
/// </summary>
public sealed class CeremonialGarmentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Your Attacks deal 1 more damage per "
          + $"{KokomiConstants.GarmentChargeDivisor} [gold]Charge[/gold] and "
          + $"grant {KokomiConstants.GarmentAttackBlock} Block. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static bool IsUp(Creature? owner) =>
        owner != null && owner.Powers.Any(p => p is CeremonialGarmentPower);

    /// <summary>
    /// The bonus her attacks are carrying RIGHT NOW. Public so card faces and
    /// hover tips read the same arithmetic the hit uses -- the Furina
    /// legibility lesson: a preview and an effect that compute separately will
    /// eventually disagree, and the player believes the preview.
    /// </summary>
    public static int ChargeBonus(Creature? owner) =>
        IsUp(owner)
            ? KokomiResources.GetCharge(owner) / KokomiConstants.GarmentChargeDivisor
            : 0;

    /// <summary>
    /// tier0 flat_attack_bonus: `bonus += p.charge // GARMENT_CHARGE_DIVISOR`,
    /// folded in flat BEFORE Strength and Vulnerable, and applied PER TARGET
    /// (the sim adds current_attack_bonus inside its per-target damage
    /// computation, so an AoE attack pays it to each enemy). Additive is
    /// exactly that phase, which is why this is not a multiplier hook.
    ///
    /// Stacking is irrelevant by construction: the power's Amount is TURNS
    /// REMAINING, not a magnitude, so re-casting the Burst extends the window
    /// and never doubles the read.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return KokomiResources.GetCharge(Owner) / KokomiConstants.GarmentChargeDivisor;
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
/// The Garment's attack rider, and the Casket link. Separate from
/// <see cref="KokomiResourceHooks"/> so the Burst's behaviour reads in one
/// place when the rework lands.
/// </summary>
public sealed class KokomiGarmentHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static KokomiGarmentHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KokomiGarmentHooks>(
            ModelDb.GetId<KokomiGarmentHooks>());
        yield return _instance;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card.Owner?.Creature;
        if (!KokomiResources.IsKokomi(owner)) return;
        if (cardPlay.Card.Type != CardType.Attack) return;
        if (!CeremonialGarmentPower.IsUp(owner)) return;

        // NC-11 (R116, Errata Batch 2 item 4): the rider is POWER-sourced,
        // not card-printed -- the Attack is only its trigger -- so it is
        // Unpowered and exempt from Frail and Dexterity, matching tier0's
        // raw `p.block +=` (effects.py, `ceremonial_garment`).
        await CreatureCmd.GainBlock(
            owner!, KokomiConstants.GarmentAttackBlock, ValueProp.Unpowered,
            cardPlay);
    }
}

/// <summary>
/// Vigil of the Deep -- the prevention ward (kickoff §2.4).
///
/// The first time each turn an attack would land unblocked damage, prevent up
/// to Amount of it and Exhaust a random card from the draw pile. Prevention is
/// priced in FUTURE DRAWS, not HP: R52's healing law says her HP bar never
/// moves, the incoming does.
///
/// The exhaust routes through the ordinary funnel, so being attacked feeds
/// Charge -- getting hit fuels the finisher, which is the stability identity
/// expressed as a mechanic rather than as flavour.
///
/// IT CAN RUN OUT, and that is the design. If draw and discard are both empty
/// the ward cannot pay and does not proc: the deck really is her second HP bar.
/// A version that prevents for free would be a different, much safer card.
/// </summary>
public sealed class PreventExhaustWardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Vigil of the Deep"),
        ("description",
            "The first time you would take unblocked attack damage each turn, "
          + "prevent up to {Amount} of it and [gold]Exhaust[/gold] a random "
          + "card from your draw pile."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Reset with the other per-turn windows, matching the sim's
    /// `prevention_used_this_turn`.</summary>
    private bool _usedThisTurn;

    /// <summary>
    /// UNBLOCKED residual of the hit currently resolving -- what is left
    /// after Block and before the ward -- captured in
    /// <see cref="BeforeDamageReceived"/>. Not the raw incoming: the sim
    /// wards only the residual (combat.py, `dmg - blocked`), so a fully
    /// blocked hit must leave this at zero and cost the ward nothing.
    ///
    /// This field exists because <see cref="ModifyDamageAdditive"/> is NOT a
    /// real-hit hook. The engine also calls it to answer damage PREVIEWS --
    /// the Beetle Swarm ruling in DECISIONS puts it exactly: previews are
    /// "questions about the current board rather than about a cast in
    /// progress". Previews are local UI, so they run a different number of
    /// times on each co-op peer.
    ///
    /// The 2026-07-27 co-op playtest is what that costs. This power used to
    /// set its per-turn latch AND arm its exhaust from inside the modifier,
    /// so a preview on one peer burned the latch the other peer still had.
    /// The peers then disagreed about whether the ward had fired, and -- the
    /// fatal part -- one of them took a roll off the shared
    /// Rng.CombatTargets stream that the other did not. That poisons every
    /// later roll in the run, so the host's checksum tripped at the next
    /// boundary and it disconnected the client (StateDivergence).
    ///
    /// So: the modifier is PURE, and every mutation lives in the
    /// Before/After hooks, which only ever run on hits that really happened.
    /// </summary>
    private decimal _unblockedThisHit;

    /// <summary>
    /// What the ward actually reads: the hit as it stands AFTER Block, which
    /// is the sim's `dmg - blocked` (combat.py, the enemy-attack branch).
    /// Block is not yet spent at either hook that calls this, so both the
    /// modifier and the Before hook see the same standing Block and can
    /// never disagree about whether the ward is owed a proc.
    /// </summary>
    private decimal UnblockedPortion(decimal amount) =>
        System.Math.Max(0m, amount - Owner.Block);

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature == Owner) _usedThisTurn = false;
        return Task.CompletedTask;
    }

    /// <summary>
    /// Fuel is draw + discard, because an empty draw pile reshuffles the
    /// discard back in before the ward gives up (tier0
    /// prevent_damage_exhaust). Kept in one place so the modifier's answer
    /// and the exhaust's decision can never drift apart.
    /// </summary>
    private bool HasFuel()
    {
        if (Owner.Player == null) return false;
        var draw = CardPile.Get(PileType.Draw, Owner.Player);
        var discard = CardPile.Get(PileType.Discard, Owner.Player);
        return (draw?.Cards.Count ?? 0) + (discard?.Cards.Count ?? 0) > 0;
    }

    public override Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        // Real hits only. Capturing here rather than in the modifier is what
        // lets AfterDamageReceived tell a hit apart from a preview without
        // the modifier having to remember anything.
        //
        // The ward is an ATTACK ward on both sides of the bridge: the sim
        // reaches it only from the enemy attack branch, and both printed
        // descriptions say "attack damage".
        _unblockedThisHit = target == Owner && props.IsPoweredAttack()
            ? UnblockedPortion(amount)
            : 0m;
        return Task.CompletedTask;
    }

    /// <summary>
    /// PURE -- mutating anything here desyncs co-op (see _unblockedThisHit).
    /// Returning the same reduction for a preview and for the real hit is
    /// the correct answer to both questions: the preview asks what this hit
    /// would do, and what it would do is the reduced number.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature target, decimal amount, ValueProp props, Creature dealer,
        CardModel cardSource, CardPlay? cardPlay)
    {
        if (target != Owner || _usedThisTurn || amount <= 0) return 0m;
        if (!props.IsPoweredAttack()) return 0m;   // attacks only, per the text
        if (!HasFuel()) return 0m;       // defenceless: the deck is spent
        // The ward sits AFTER Block, before HP (sim: prevent_damage_exhaust
        // is handed `dmg - blocked`). This hook runs BEFORE the engine
        // spends Block, so the residual has to be computed here rather than
        // read off the hit -- subtracting from the raw amount would ward
        // damage Block was already going to eat.
        //
        // Reducing by min(residual, Amount) leaves `amount` still at or above
        // the standing Block whenever the residual is positive, so the engine
        // consumes exactly the Block the sim consumes. HP and Block both land
        // on the sim's numbers on a partially blocked hit.
        var unblocked = UnblockedPortion(amount);
        if (unblocked <= 0m) return 0m;
        return -System.Math.Min(unblocked, Amount);
    }

    /// <summary>
    /// The fuel is paid AFTER the hit resolves. Exhausting inside the damage
    /// modifier would mutate piles mid-calculation, which is the class of bug
    /// that produces "the number changed while I was reading it".
    ///
    /// The per-turn latch is set HERE, not in the modifier, so it can only
    /// ever be burned by a hit that really landed.
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature dealer, CardModel cardSource)
    {
        var unblocked = _unblockedThisHit;
        _unblockedThisHit = 0m;

        // The same predicate the modifier just answered with. Because the
        // modifier mutates nothing, it is still true here on a hit the ward
        // actually reduced -- and false on every hit it declined.
        //
        // `unblocked`, never the raw hit: the sim returns 0 without latching
        // or exhausting when the residual is <= 0 (effects.py
        // prevent_damage_exhaust). A hit Block ate completely deals nothing,
        // so it may not cost a card out of the draw pile.
        if (target != Owner || _usedThisTurn || unblocked <= 0) return;
        if (Owner.Player == null) return;

        // tier0 order: reshuffle FIRST, and only then decide the ward is out
        // of fuel. ShuffleIfNecessary is the funnel every other draw-pile
        // read in the game goes through.
        var drawPile = CardPile.Get(PileType.Draw, Owner.Player);
        if (drawPile == null || drawPile.Cards.Count == 0)
        {
            await CardPileCmd.ShuffleIfNecessary(choiceContext, Owner.Player);
            drawPile = CardPile.Get(PileType.Draw, Owner.Player);
        }
        if (drawPile == null || drawPile.Cards.Count == 0) return;

        _usedThisTurn = true;
        var victim = Owner.Player.RunState.Rng.CombatTargets
            .NextItem(drawPile.Cards.ToList());
        if (victim != null)
        {
            await CardCmd.Exhaust(choiceContext, victim);
        }
    }

    /// <summary>
    /// The card whose application is in flight, captured from the ONE hook
    /// that carries it. <see cref="TryModifyPowerAmountReceived"/> is handed
    /// the applier CREATURE and no card (decompiled
    /// PowerCmd.Apply/ModifyAmount: Hook.ModifyPowerAmountReceived takes no
    /// cardSource), and the composition rule is a property of the ROW, not of
    /// the power -- so the row's identity has to arrive some other way.
    /// Hook.BeforePowerAmountChanged is awaited immediately before the modify
    /// hooks on BOTH application paths and does carry it.
    ///
    /// Set on every application, including to null, so it can never go stale:
    /// a non-card source (relic, potion, enemy) clears it and takes the
    /// default read.
    /// </summary>
    private CardModel? _applyingCard;

    /// <summary>
    /// The title of the card that last applied this ward, so the power tooltip
    /// names the card the player actually played. Before this, the class hard-
    /// coded the Rare's title in its <see cref="Localization"/>, so a second
    /// card applying the same power displayed "Vigil of the Deep" in the power
    /// bar -- a live defect the moment the ward stopped being Rare-only
    /// (EB-26 §7.1).
    ///
    /// Stored as the LocString rather than the card, so nothing here holds a
    /// combat card alive past its pile, and the fallback stays the registered
    /// loc entry for an application with no card behind it.
    /// </summary>
    private LocString? _sourceTitle;

    public override LocString Title => _sourceTitle ?? base.Title;

    public override Task BeforePowerAmountChanged(
        PowerModel power, decimal amount, Creature target, Creature? applier,
        CardModel? cardSource)
    {
        if (power is PreventExhaustWardPower && target == Owner)
        {
            _applyingCard = cardSource;
            if (amount > 0 && cardSource != null)
            {
                _sourceTitle = cardSource.TitleLocString;
            }
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// The FIRST application creates this instance, and a model that is not in
    /// the combat yet does not receive
    /// <see cref="BeforePowerAmountChanged"/> -- so the title of the card that
    /// opened the ward is captured here instead. Same value, the other path.
    /// </summary>
    public override Task BeforeApplied(
        Creature target, decimal amount, Creature? applier,
        CardModel? cardSource)
    {
        if (target == Owner && amount > 0 && cardSource != null)
        {
            _sourceTitle = cardSource.TitleLocString;
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// How two applications of the ward compose. Clamped on the RESULTING
    /// COUNTER rather than on the delta, following
    /// <see cref="SalonMemberPower"/>.
    ///
    /// TWO modes, exactly mirroring the sim's `apply_power`
    /// (tier0/engine/powers.py) and picked by the applying ROW, which is why
    /// <see cref="_applyingCard"/> exists:
    ///
    /// 1. DEFAULT (no sheet field) -- the cap bounds the running total:
    ///    min(Amount + amount, cap). Every row of this power that does not ask
    ///    otherwise uses the SINGLE-APPLICATION encoding, max_stacks EQUALS the
    ///    applied amount and the upgrade moves both together (6/6 -> 8/8, see
    ///    kokomi-upgrades.yaml and tier0's
    ///    test_vigil_upgrade_moves_the_cap_with_the_amount). Under that
    ///    encoding min(Amount + amount, amount) is just `amount`, so the ward
    ///    SETS rather than adds: a second copy re-asserts the magnitude instead
    ///    of doubling it. The magnitude is the knob, not the copy count.
    ///    Deriving the cap from the application rather than hard-coding 6 is
    ///    what keeps the upgraded copy at its printed 8.
    ///
    /// 2. FLOOR-NOT-CLAMP (<see cref="INeverReducingApplier"/>, sheet
    ///    `never_reduces: true`; EB-26 D2 ruled 2026-08-10 option (d)) -- the
    ///    application raises the stack toward the CARD'S OWN cap and never
    ///    lowers a higher standing stack:
    ///    max(Amount, min(Amount + amount, card cap)). This is what lets a
    ///    lesser uncommon ward top a Rare ward up without a card ever being a
    ///    downgrade to play. Without it, `vigil_of_the_deep+` (8) followed by
    ///    the lesser ward (3) left 3.
    /// </summary>
    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not PreventExhaustWardPower || target != Owner)
        {
            return false;
        }
        if (amount <= 0) return false;      // removal still lands in full
        if (_applyingCard is INeverReducingApplier floorApplier)
        {
            var raised = System.Math.Max(
                Amount,
                System.Math.Min(Amount + amount, floorApplier.NeverReducingCap));
            modifiedAmount = raised - Amount;
        }
        else
        {
            modifiedAmount = amount - Amount;
        }
        return modifiedAmount != amount;
    }
}
