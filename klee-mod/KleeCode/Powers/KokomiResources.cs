using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Combat.History.Entries;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Kokomi's CharacterModel. Same reason Furina has one: a generated
/// Kokomi card acquired by another character must not silently grant them her
/// Charge engine.
/// </summary>
public interface IKokomiCharacter
{
}

/// <summary>
/// TRANSCRIPTION SURFACE. Every number here is copied verbatim from the sim;
/// none is re-derived C#-side.
///
/// THE CHECKLIST IS NOW A GATE. This table used to live in the PR body and be
/// kept by discipline -- which meant a sim-side retune that nobody mirrored
/// produced a green build playing to numbers no simulation ever endorsed.
/// tools/lint_constant_parity.py compares every row below against tier0 by
/// value, and fails on any C# constant that is neither mirrored nor declared
/// unmirrored with a reason. Adding a constant here without touching that
/// table is a build failure, on purpose.
///
/// | C# constant         | sim source                               |
/// |---------------------|------------------------------------------|
/// | ChargePerExhaust    | constants.py CHARGE_PER_EXHAUST = 1       |
/// | BurstPerExhaust     | constants.py KOKOMI_BURST_PER_EXHAUST=2   |
/// | BurstPerReaction    | constants.py BURST_PER_REACTION = 5       |
/// | KurageDuration      | constants.py KURAGE_DURATION = 1          |
/// | KuragePulseBase     | constants.py KURAGE_PULSE_BASE = 4        |
/// | KuragePulsePerChg   | constants.py KURAGE_PULSE_PER_CHARGE = 3  |
/// | KuragePulseBlock    | constants.py KURAGE_PULSE_BLOCK = 0       |
/// | GarmentAttackBlock  | constants.py GARMENT_ATTACK_BLOCK = 2     |
/// | GarmentTurns        | constants.py CEREMONIAL_GARMENT_TURNS = 3 |
/// | GarmentChargeDivisor| constants.py GARMENT_CHARGE_DIVISOR = 2   |
/// | ConscriptCostDelta  | constants.py CONSCRIPT_COST_DELTA = -1    |
/// | BurstMax            | characters/kokomi.yaml burst_max: 20      |
/// </summary>
public static class KokomiConstants
{
    public const int ChargePerExhaust = 1;
    public const int BurstPerExhaust = 2;

    /// <summary>
    /// tier0 BURST_PER_REACTION = 5, and tier0 BURST_PER_SKILL_TAG = 5 is
    /// <see cref="BurstConstants.PerSkillTag"/>. Both sim gates are
    /// `if p.burst_max` -- UNIVERSAL to anyone carrying a meter, not
    /// Klee-scoped -- so she is paid on the same lines Klee and Furina are.
    /// Aliased here rather than reaching for Klee's constant at her call
    /// sites, so her economy reads in one place.
    /// </summary>
    public const int BurstPerReaction = 5;
    public const int KurageDuration = 1;
    public const int KuragePulseBase = 4;

    /// <summary>
    /// A MULTIPLIER, not a divisor -- the pulse gains this much per POINT of
    /// Charge. [USER]-ratified over the assistant's objection (Necrobinder
    /// precedent, R56): unbounded starting-deck scaling is what the designers
    /// actually ship. The standing caveat is that Osty's HP can drop while
    /// Charge only climbs, so act 3 is the cell to watch; sim-side that is
    /// now a report column (tier05/kurage_telemetry.py, R57 P2).
    ///
    /// R73 (Neap Tide v2.1, 2026-07-26): 4 -> 2, then 2 -> 3 when E1 graded
    /// P6 and the sprint's pre-committed weak-side fallback fired.
    ///
    /// The act-3 caveat above is exactly what came due: at x4 the pulse
    /// out-read the Rare that was supposed to cap the hierarchy. But x2
    /// overshot -- against same-world roster anchors her BEST plan cleared
    /// act 1 at 57.2% against a roster floor of 57.5%, and her best full-run
    /// win rate sat under the reference Ironclad's. Weak everywhere is not
    /// the design target, so x3 is the landed value.
    ///
    /// Cutting the SLOPE and leaving the accrual side alone is deliberate
    /// (§5 knob order): the bank fills at the same rate, it just buys less.
    /// "Before Sun and Moon" is the only sanctioned way back up, and it is a
    /// draft cost.
    /// </summary>
    public const int KuragePulsePerCharge = 3;

    /// <summary>
    /// Zero since the v0.4b starter rework: the pulse is damage now, not
    /// mending. The mending half is DRAFTED, via Kurage's Oath. Kept as a
    /// named constant rather than inlined so restoring the baseline stays a
    /// one-constant change on both sides of the bridge.
    /// </summary>
    public const int KuragePulseBlock = 0;

    public const int GarmentAttackBlock = 2;
    public const int GarmentTurns = 3;

    /// <summary>
    /// tier0 GARMENT_CHARGE_DIVISOR = 2. While the Garment holds, her attacks
    /// gain +1 damage per this much Charge -- the "scaled down per hit" read
    /// (kickoff §2.2, Shape B). Was 4 until the v0.3 charge-curve pass found
    /// the meter reading ~4x under the Regent-common benchmark: at /4 a node-4
    /// bank of 8 paid +2 per attack, which is decoration rather than a scaling
    /// identity. Do not re-derive it here -- constants.py is LAW.
    /// </summary>
    public const int GarmentChargeDivisor = 2;
    public const int ConscriptCostDelta = -1;
    public const int BurstMax = 20;
}

/// <summary>
/// Kokomi's Charge: her scaling bank.
///
/// READ, NEVER SPENT -- this is the whole shape of the character, and it is
/// why <see cref="Spend{T}"/> below is a no-op rather than an oversight.
/// Nothing in her kit consumes Charge; cards READ it (the Kurage pulse, the
/// Garment's attack rider) and the bank keeps climbing. That is deliberate
/// asymmetry against Furina, who pays her Encore back out.
///
/// It is modelled as a BaseLib CustomResource for the gauge: BaseLib scans the
/// assembly and registers every concrete subclass itself, so this class is
/// DEFINED and never registered by hand (the ModelDb lesson). Per-combat
/// instances are created lazily and zeroed by PrepForCombat, matching the
/// sim's per-fight reset.
/// </summary>
public sealed class ChargeResource : BasicCustomResource
{
    public ChargeResource() : base("KLEEMOD_CHARGE")
    {
    }

    /// <summary>
    /// No card has a Charge cost, so there is no shared cost modification to
    /// apply. False keeps cost-reduction effects from pretending otherwise.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>
    /// NO SHIPPED CARD SPENDS CHARGE, and this override is still the "never
    /// spent" contract for every route the GAME can take on its own: a
    /// canonical resource cost, a cost modifier, anything that reaches a
    /// CustomResource generically. It returns true without decrementing, so
    /// none of them can quietly drain a bank every scaling number on her
    /// sheet was measured against (R80).
    ///
    /// The reopened question (R213 E1) does NOT come through here. A
    /// prototype row prints an explicit `spend_charge` op, and that op
    /// resolves through <see cref="KokomiResources.SpendCharge"/> -- one
    /// named door, greppable, quarantined, and deleted with the slice's rows
    /// if the slice is rejected. Sim twin: tier0/engine/resources.py
    /// `spend_charge`, which likewise nothing shipped calls.
    /// </summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }
}

/// <summary>
/// Static accessors for Kokomi's bank. Mirrors KleeBurstResource's shape --
/// one private Find() that gates on character identity, everything else on
/// top of it -- so the two meters stay easy to compare and instrument.
/// </summary>
public static class KokomiResources
{
    public static bool IsKokomi(Creature? creature) =>
        creature?.Player?.Character is IKokomiCharacter;

    /// <summary>
    /// ROTATION LAW ([USER] ruling 2026-08-23; LAW "Character identity —
    /// Kokomi"). "Whenever one of YOUR cards is Exhausted" reads literally: a
    /// Status or a Curse is never one of her cards. This one predicate is the
    /// law's whole surface in the mod -- the Muster candidate filter, every
    /// generated chosen-Exhaust selector, and the Charge/Burst funnel all ask
    /// it -- so the three cannot drift apart. Sim twin: Card.is_junk
    /// (tier0/engine/state.py), used at the same three seams.
    ///
    /// The retired behaviour was kickoff v1 §2.1's "statuses/curses count
    /// too (accepted quirk)": a Dazed in hand was free curse removal that
    /// also paid Charge when the recruit rotated out, which made her uniquely
    /// status-resistant for nothing. A card that IS allowed to eat junk says
    /// so on its face with an explicit filter (Dodge Roll's shape) -- that is
    /// the design space this vacates, at Uncommon/Rare.
    /// </summary>
    public static bool IsJunk(CardModel card) =>
        card.Rarity == CardRarity.Status || card.Rarity == CardRarity.Curse;

    /// <summary>
    /// The selector predicate for every Kokomi verb that picks one of HER
    /// cards to rotate out: kit-exempt (the v1.9 invariant every discard and
    /// exhaust pool already rides) AND not junk.
    /// </summary>
    public static bool OwnCard(CardModel card) =>
        KitGrant.NotKitCard(card) && !IsJunk(card);

    private static ChargeResource? Find(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner?.Character is not IKokomiCharacter) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<ChargeResource>.Get(combatState);
    }

    /// <summary>Current bank, 0 for non-Kokomi owners. The display surfaces
    /// and the pulse arithmetic both read this, so they cannot drift.</summary>
    public static int GetCharge(Creature? creature) => Find(creature)?.Amount ?? 0;

    /// <summary>
    /// Grants Charge. Gated on identity inside Find() rather than at each call
    /// site: the sim accrues at a single chokepoint
    /// (refpowers.after_card_exhausted) and card-side gain_charge lines are
    /// premiums on top, so both paths land here.
    /// </summary>
    public static void GainCharge(Creature? creature, int amount)
    {
        if (amount <= 0) return;
        var resource = Find(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature!);
        // EB-53/N1: Charge IS the Bake-Kurage pulse's variable, so the docket's
        // pulse number moves on every gain. Same funnel and the same reason as
        // the gauge above -- a display may not go stale behind a mutation.
        Vfx.TurnEndPreviewBridge.Refresh(creature);
    }

    /// <summary>
    /// QUARANTINED SUPPORT (R213 E1). Whether the bank could pay this price.
    ///
    /// The Charge cost LINE: a generated card printing a top-level
    /// `spend_charge` overrides IsPlayable with this call, which is how the
    /// price is shown before the energy is committed rather than failing
    /// silently. Sim twin: tier0/engine/combat.py `charge_cost` reached
    /// through `card_playable`.
    /// </summary>
    public static bool CanSpendCharge(Creature? creature, int amount) =>
        amount > 0 && GetCharge(creature) >= amount;

    /// <summary>
    /// QUARANTINED SUPPORT (R213 E1). Spend Charge as a COST. ALL OR
    /// NOTHING -- returns whether the bank paid, and mutates nothing when it
    /// did not. Sim twin: tier0/engine/resources.py `spend_charge`.
    ///
    /// NO OVERDRAW, and that is her LAW rather than a taste call: the
    /// shortfall-drains-HP grammar is Furina's Encore alone, and "no
    /// self-damage anywhere in her kit or personal pool" forbids the shape
    /// here outright. A partial spend would also leave the caller believing
    /// it was paid, which is the failure SparkPower.Spend was given the same
    /// rule to avoid.
    ///
    /// THE RETURN VALUE IS LOAD-BEARING and the generator checks it. The
    /// IsPlayable gate covers a top-level price, but a price inside a
    /// `choose_one` mode has no gate to sit on -- the choose-a-card screen
    /// offers every mode whatever the bank holds -- so the emitted statement
    /// is `if (!await SpendCharge(...)) return;` and the play is abandoned
    /// where the price failed.
    ///
    /// The direct ModifyAmount, rather than the resource's own Spend: that
    /// override is deliberately inert (see ChargeResource), so routing
    /// through it would return true and move nothing.
    /// </summary>
    public static Task<bool> SpendCharge(
        PlayerChoiceContext choiceContext, Creature? creature, int amount,
        CardModel? cardSource)
    {
        if (!CanSpendCharge(creature, amount)) return Task.FromResult(false);
        var resource = Find(creature);
        if (resource == null) return Task.FromResult(false);
        resource.ModifyAmount(-amount);
        Vfx.GaugeBridge.Refresh(creature!);
        // The pulse reads the bank, so a spend moves the end-of-turn preview
        // for exactly the reason a gain does. Same funnel, same rule: a
        // display may not go stale behind a mutation.
        Vfx.TurnEndPreviewBridge.Refresh(creature);
        return Task.FromResult(true);
    }

    /// <summary>
    /// Cards currently in the exhaust pile. The scaling term behind her
    /// exhaust-pile finishers (pearl_barrage, depths_judgment): the pile IS
    /// the record of everything she has rotated off the line, so a card that
    /// reads it is reading her whole game so far.
    ///
    /// Static and null-tolerant because CalculatedVar previews call it with
    /// no target while nothing is hovered.
    /// </summary>
    public static int ExhaustPileCount(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner == null) return 0;
        return CardPile.Get(PileType.Exhaust, owner)?.Cards.Count ?? 0;
    }

    /// <summary>
    /// Cards this SEAT has discarded this turn -- the scaling term behind
    /// `what_the_tokoyo_took` (EB-122, from EB-69's fill).
    ///
    /// TRANSCRIBED, not re-derived. The expression is the base game's own
    /// MementoMori multiplier verbatim (sts2.dll v0.107.1,
    /// MegaCrit.Sts2.Core.Models.Cards.MementoMori.CanonicalVars), and the sim
    /// names that same card as the source of its `discards_this_turn` token
    /// (tier0/engine/effects.py `_formula_count`). Two consequences fall out
    /// of reading the HISTORY rather than a counter, and both are the sim's
    /// too rather than choices made here: the end-of-turn hand flush does not
    /// go through CardCmd.Discard and so does not count, and the owner filter
    /// makes the tally PER SEAT -- a co-op partner's discards are not this
    /// card's bonus.
    ///
    /// Static and null-tolerant because CalculatedVar previews call it with no
    /// target, and outside a combat there is no history to read.
    /// </summary>
    public static int DiscardsThisTurn(CardModel? card)
    {
        if (card == null) return 0;
        var combatState = card.CombatState;
        if (combatState == null) return 0;
        var history = CombatManager.Instance?.History;
        if (history == null) return 0;

        // A loop rather than MementoMori's `.Count(lambda)`: the predicate is
        // the whole meaning of this method, and in a closure it is invisible
        // to the structural pin that guards it (KleeTests reads a method's own
        // call set and cannot follow a compiler-generated display class). The
        // two clauses are byte-for-byte the base game's; only the spelling of
        // the iteration differs, and this one also allocates nothing on a
        // preview, which runs on every hover.
        var count = 0;
        foreach (var entry in history.Entries)
        {
            if (entry is not CardDiscardedEntry discarded) continue;
            if (!discarded.HappenedThisTurn(combatState)) continue;
            if (discarded.Card.Owner != card.Owner) continue;
            count++;
        }

        return count;
    }

    /// <summary>
    /// QUARANTINED SUPPORT (R213 B). Cards this SEAT has Exhausted since its
    /// own turn started -- the third counting basis, and the one [USER]
    /// expected Pearl Barrage to have (R215 C: "I thought it was tracking how
    /// many cards had been exhausted that whole turn").
    ///
    /// NOTHING SHIPPED READS THIS. It serves the `exhausts_this_turn`
    /// amount_formula count, which lives only on the quarantined prototype
    /// surface. The tally is maintained even in a release build -- one integer
    /// per seat, which no shipped card can see -- because a counter that only
    /// exists under a compile flag is a counter whose maintenance is never
    /// exercised.
    ///
    /// A COUNTER RATHER THAN A HISTORY READ, which is the opposite choice from
    /// DiscardsThisTurn above, and the reason is evidence rather than taste:
    /// that method transcribes MementoMori's own CanonicalVars out of the
    /// decompile, and there is no decompiled first-party card scaling off a
    /// per-turn EXHAUST count to transcribe. Naming a history entry type that
    /// has not been read off sts2.dll would be exactly the guess the
    /// generator's UNPARSEABLE discipline exists to refuse. The after-exhaust
    /// hook below is already the universal exhaust funnel this file owns -- it
    /// is where the Charge and Burst accrual is paid -- so the count is taken
    /// there. (The hook's own name is deliberately not spelled in this
    /// comment: tier0/tests/test_starter_relic_upgrades.py anchors on its
    /// FIRST occurrence in the file to read the funnel's summary, and a
    /// mention up here would move the anchor onto prose.)
    ///
    /// NO JUNK FILTER, deliberately, and it is the one place the rotation law
    /// does not reach: this counts CARDS THAT LEFT, not income earned. The sim
    /// twin (`CombatState.exhausts_this_turn`) is incremented at the pile
    /// append with no filter either, and the two must agree or the falsifier
    /// reads a different card from the one the seat plays.
    ///
    /// Per SEAT, keyed on the Player, because co-op runs two of them and a
    /// partner's rotation is not this card's bonus -- the same rule
    /// DiscardsThisTurn gets from its owner filter.
    /// </summary>
    public static int ExhaustsThisTurn(Player? owner)
    {
        if (owner == null) return 0;
        return ExhaustsByPlayer.TryGetValue(owner, out var count) ? count : 0;
    }

    private static readonly Dictionary<Player, int> ExhaustsByPlayer = new();

    /// <summary>One card reached the exhaust pile. Called from the funnel.</summary>
    internal static void NoteExhaustThisTurn(Player? owner)
    {
        if (owner == null) return;
        ExhaustsByPlayer[owner] =
            (ExhaustsByPlayer.TryGetValue(owner, out var n) ? n : 0) + 1;
    }

    /// <summary>
    /// The window closes and reopens at PLAYER TURN START, which is where the
    /// sim closes it too (`refpowers.reset_turn_counters`). Clearing the whole
    /// map rather than one seat's entry also drops Players from finished
    /// combats, so the dictionary cannot grow across a run.
    /// </summary>
    internal static void ResetExhaustsThisTurn()
    {
        ExhaustsByPlayer.Clear();
    }

    internal static KokomiBurstResource? FindBurst(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner?.Character is not IKokomiCharacter) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<KokomiBurstResource>.Get(combatState);
    }

    /// <summary>Current Burst meter, 0 for non-Kokomi owners.</summary>
    public static int GetBurst(Creature? creature) => FindBurst(creature)?.Amount ?? 0;

    /// <summary>
    /// The single Burst gain funnel. Every source lands here -- the exhaust
    /// funnel, the skill-tag bonus, reactions -- so the gauge cannot go stale
    /// behind a gain and so the economy stays one place to instrument.
    /// Accrual is UNCAPPED past the max (the sim never clamps; the grant check
    /// is `>=` and casting resets to 0 -- overflow is lost at cast, not gain).
    /// </summary>
    public static void GainBurst(Creature? creature, int amount)
    {
        if (amount <= 0) return;
        var resource = FindBurst(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature!);
    }
}

/// <summary>
/// The two engine-level rules that are NOT card text.
///
/// 1. The exhaust funnel. Every owned-card exhaust pays Charge and Burst
///    energy. In the sim this is the relic hook (`tamakushi_casket`, shipped
///    as "Pearl of Wisdom"), and it is universal -- it is deliberately not
///    written on any card face, because "exhaust pays" is the character, not a
///    card's rider. FeelNoPainPower / DarkEmbracePower are the first-party
///    precedent for this hook.
///
/// 2. LAW 3, Flawless Strategy. Kokomi CANNOT gain Strength; incoming Strength
///    converts to Charge instead. The conversion sits at
///    TryModifyPowerAmountReceived, which is the chokepoint EVERY source flows
///    through -- cards, companion buffs, enemy-applied. Doing it per-card
///    would leave the other two sources granting real Strength, which is
///    exactly the hole the sim closes at its own apply_power chokepoint.
/// </summary>
public sealed class KokomiResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static KokomiResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KokomiResourceHooks>(
            ModelDb.GetId<KokomiResourceHooks>());
#if PROTOTYPE_CARDS
        // QUARANTINED (Powers/Prototype/KurageMemory.cs). The memory is PER
        // FIGHT, which the sim gets free because CombatState is rebuilt by
        // run_fight; this hook model is a singleton and has to be told. This
        // is the one place the mod is handed a fresh combat.
        KurageMemory.ResetForCombat(combatState);
#endif
        yield return _instance;
    }

#if PROTOTYPE_CARDS
    /// <summary>
    /// QUARANTINED, v4 BASE KIT (sec.12.6 item 1). The jellyfish is installed
    /// HERE rather than by a card, because under the base kit nothing summons
    /// it. Mirror of the sim's `combat.run_fight`, which installs beside the
    /// per-combat Charge reset for the same reason: the two have one lifetime.
    ///
    /// THIS HOOK AND NOT `AfterCreatureAddedToCombat`, which was the first
    /// choice and is wrong: the game raises that one from
    /// `CreatureCmd.AddToCombat`, i.e. for creatures SPAWNED into a live
    /// combat, while the seats are seeded by the combat's own setup loop and
    /// never pass through it. `CombatManager` raises THIS hook after every
    /// creature is in and immediately before `StartTurn`, which is exactly
    /// "before the first turn opens".
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        await KurageMemory.InstallAll();
    }
#endif

    public override Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        // CardModel.Owner is the Player; PowerModel.Owner is the Creature.
        // The two differ, and mixing them is a silent type error the compiler
        // happens to catch here only because the helpers take Creature.
        // ABOVE BOTH GUARDS BELOW, and that is the whole difference between
        // this tally and the accrual under it: the quarantined
        // `exhausts_this_turn` count counts CARDS THAT LEFT, so it takes no
        // view on who owns them or whether they were junk. Sim twin:
        // `CombatState.exhausts_this_turn`, incremented at the pile append.
#if PROTOTYPE_CARDS
        // QUARANTINED (Powers/Prototype/KurageMemory.cs). ABOVE EVEN THAT
        // TALLY: a memory copy's removal "is not an Exhaust EVENT at all", so
        // NOTHING hanging off this funnel pays out for a card that was never
        // burned -- not Charge, not Burst, not the per-turn count, not a
        // relic's damage_per_exhaust. In practice the copy never reaches here
        // (KurageMemory.Fire clears its Exhaust keyword before the play and
        // lifts it out of its pile after); this is the belt to that braces.
        if (KurageMemory.IsCopy(card))
        {
            return Task.CompletedTask;
        }
#endif
        KokomiResources.NoteExhaustThisTurn(card.Owner);

        var owner = card.Owner?.Creature;
        if (!KokomiResources.IsKokomi(owner)) return Task.CompletedTask;

        // ROTATION LAW ([USER] 2026-08-23): "one of YOUR cards" is literal.
        // A Status or a Curse pays nothing here whichever route exhausted it
        // -- Ethereal, a played Dazed, the ward's random draw-pile pick. Both
        // halves of the accrual (Charge AND the Burst particle) read the same
        // way. Sim twin: refpowers.after_card_exhausted's `not card.is_junk`.
        if (KokomiResources.IsJunk(card)) return Task.CompletedTask;

        // EPOCH 2 / D1 (audit sec.1.1). This granted the BASE 1/2 unconditionally
        // and never looked at the relic, while PearlOfInsightRelic declared
        // ChargePerExhaust = 2 / BurstPerExhaust = 4 -- constants read by
        // nothing except the relic's own description string. Kokomi's upgraded
        // starter was a NO-OP WITH A LYING TOOLTIP: it promised doubled
        // per-exhaust accrual, printed those numbers on the relic panel, and
        // changed nothing. The red-pen record (Part 1 item 6, "shipped as
        // doubled per-exhaust") described a game that was never built.
        //
        // The relic is the source of truth for its own numbers, so they are
        // READ off it rather than restated here -- restating them is how the
        // description and the funnel came to disagree in the first place.
        // QUARANTINED FUEL NOTE (v3, sec.11.6 PICK A): the fuel is THIS funnel,
        // unnarrowed -- her own cards AND original Companions, at 1 per
        // Exhaust. v3 retires v2's Companion carve-out, so there is nothing to
        // add here: the shipped line already is v3's rule.
        KokomiResources.GainCharge(owner, ExhaustCharge(owner));
        KokomiResources.GainBurst(owner, ExhaustBurst(owner));
#if PROTOTYPE_CARDS
        // RULE 2 -- ENTRY ON EXHAUST. OUTSIDE the relic gate above,
        // deliberately: the memory belongs to the jellyfish, not to the
        // Tamakushi Casket, and a Kokomi who has lost the relic should still
        // remember what she burned even while she cannot afford to replay it.
        KurageMemory.NoteExhaust(card);
#endif
        return Task.CompletedTask;
    }

    /// <summary>
    /// Does this creature's player hold the upgraded starter?
    ///
    /// A relic query rather than a power or a per-combat resource, matching
    /// SpotlightSystem.BothModes: the relic is RUN state and survives combats,
    /// so a per-combat mirror would need re-seeding at every fight start and
    /// its failure mode would be silent.
    /// </summary>
    private static bool HasPearlOfInsight(Creature? owner) =>
        owner?.Player?.Relics.Any(relic => relic is Relics.PearlOfInsightRelic)
        ?? false;

    internal static int ExhaustCharge(Creature? owner) =>
        HasPearlOfInsight(owner)
            ? Relics.PearlOfInsightRelic.ChargePerExhaust
            : KokomiConstants.ChargePerExhaust;

    internal static int ExhaustBurst(Creature? owner) =>
        HasPearlOfInsight(owner)
            ? Relics.PearlOfInsightRelic.BurstPerExhaust
            : KokomiConstants.BurstPerExhaust;

    /// <summary>
    /// Sim order (combat.py play_card): the requires-full drain FIRST, then
    /// the skill-tag bonus, both once per play rather than once per replay.
    /// The game fires card hooks once per replay in a series, so IsFirstInSeries
    /// is what reproduces "once per play_card call" -- an unguarded hook would
    /// double-grant where the sim grants once.
    ///
    /// The skill-tag half is UNIVERSAL in the sim (`if p.burst_max`, not
    /// `if klee`), and she has burst_max 20, so her skill-tagged cards pay the
    /// same 5 Klee's do. Missing this made her meter fill from exhausts alone,
    /// which is roughly half the sim's rate -- the Burst would have felt
    /// unreachable in play and correct in the model.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
#if PROTOTYPE_CARDS
        // QUARANTINED: the memory's per-card TARGET RECORD, written at the
        // bind. This is the earliest site carrying a resolved Target and it is
        // strictly before the result-pile move that exhausts, which is what
        // makes "a card that enters the memory after a play carries the body it
        // hit" true. Sim twin: the record in effects.resolve_card. Outside the
        // IsFirstInSeries guard on purpose -- a replay in a series aims at the
        // same body, and the last write is the one that counts.
        KurageMemory.NoteBind(cardPlay);
#endif
        if (!cardPlay.IsFirstInSeries) return Task.CompletedTask;
        KokomiBurstResource.DrainOnPlay(cardPlay.Card);
        var owner = cardPlay.Card.Owner?.Creature;
        if (cardPlay.Card is ISkillTagCard && KokomiResources.IsKokomi(owner))
        {
            KokomiResources.GainBurst(owner, BurstConstants.PerSkillTag);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Grant check sites, the sim's three grant_charged_kit calls: after the
    /// turn-start draw, after every card played, and at turn end before the
    /// flush. Her income arrives at all three -- exhausts and skill tags land
    /// inside plays, the Kurage's pulse reactions land in the turn-end
    /// broadcast, and an Ancient's turn-start drip lands at the top.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
#if PROTOTYPE_CARDS
        // QUARANTINED: THE PULSE KEY. Sim twin: effects.note_kurage_play, at
        // the one site both a manual play and an auto-play pass through.
        KurageMemory.NotePlay(cardPlay);
#endif
        await KokomiKitGrant.GrantIfCharged(choiceContext, cardPlay.Card.Owner);
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        // The quarantined per-turn exhaust window closes and reopens here,
        // which is where the sim closes it (refpowers.reset_turn_counters).
        // Ethereal cards burn at BeforeSideTurnEnd and so belong to the turn
        // that just ended -- resetting at the next turn's start, rather than
        // at the old turn's end, is what keeps them there.
        KokomiResources.ResetExhaustsThisTurn();
#if PROTOTYPE_CARDS
        // QUARANTINED: THE FIRE, at the start of her turn -- [USER], sec.11.1,
        // "At the start of Kokomi's turn, if she can afford the front Memory,
        // spend its Charge cost and play it." OpenTurn first: it clears the
        // once-per-turn latch and the pulse key, the way combat._player_turn
        // clears kurage_fired_this_turn and kurage_last_card_type.
        //
        // KURAGE_FIRE_TIMING's "turn_end" alternative is implemented in the sim
        // so the arm can be swept; the mod mirrors the DEFAULT only, and a
        // sweep of that constant is a C# edit rather than a flag flip. Named
        // here rather than left to be discovered.
        KurageMemory.OpenTurn(player);
        if (KokomiResources.IsKokomi(player.Creature))
        {
            // v4 BASE KIT, the BELT to AfterCreatureAddedToCombat's braces
            // (sec.12.6 item 1). Idempotent by construction, and here so that a
            // combat whose setup order ever changes still opens with the
            // jellyfish rather than silently without one -- the failure mode
            // otherwise is a fight that quietly never pulses and never fires.
            await KurageMemory.Install(player.Creature);
            await KurageMemory.Fire(choiceContext, player);
        }
#endif
        await KokomiKitGrant.GrantIfCharged(choiceContext, player);
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants)
        {
            if (creature.Player is { } player && KokomiResources.IsKokomi(creature))
            {
                await KokomiKitGrant.GrantIfCharged(choiceContext, player);
            }
        }
    }

    /// <summary>
    /// LAW 3. Returning true with modifiedAmount 0 refuses the Strength and
    /// pays Charge instead. The refusal is silent on purpose: her fiction is
    /// that she does not get stronger, she gets better positioned.
    ///
    /// All THREE Strength powers are caught, not just the plain one. Temporary
    /// and Possess variants are separate models, and letting either through
    /// would leave a legal route to Strength on a character whose sheet is
    /// designed around not having one -- the same hole the sim closes at its
    /// apply_power chokepoint.
    /// </summary>
    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (!KokomiResources.IsKokomi(target)) return false;
        if (canonicalPower is not (MegaCrit.Sts2.Core.Models.Powers.StrengthPower
                                   or MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower
                                   or MegaCrit.Sts2.Core.Models.Powers.PossessStrengthPower))
        {
            return false;
        }
        if (amount <= 0) return false;      // Strength LOSS still lands

        KokomiResources.GainCharge(target, (int)amount);
        modifiedAmount = 0;
        return true;
    }
}

/// <summary>
/// "At the start of your turn, gain Amount Charge." The engine behind her
/// Ancient card (see Cards/Kokomi/PrincessOfWatatsumi.cs).
///
/// This is the ONE place in the mod where Charge accrues without a card
/// leaving the deck, and that is the point of an Ancient: it is the only
/// door out of her central bargain. It is also why the number is small --
/// the pulse reads the bank at KuragePulsePerCharge, so a drip compounds
/// against a multiplier rather than adding to a total.
/// </summary>
public sealed class ChargePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Princess of Watatsumi"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Charge[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// STAGED INTO BeforeSideTurnStart, NOT AfterPlayerTurnStart (EB-2's
    /// twin). The sim sources both Ancient income ticks ABOVE the per-turn
    /// group and above the Salon upkeep -- `effects.player_turn_start_triggers`
    /// reads `charge_per_turn` before `salon_tick`, pinned by
    /// tier0/tests/test_eb30m_ancients.py::
    /// test_ancient_income_is_sourced_above_the_salon_upkeep. Every consumer
    /// of that income (KokomiResourceHooks' kit-grant check, the Salon upkeep,
    /// the other per-turn mints) is an AfterPlayerTurnStart tenant, and
    /// same-broadcast co-tenants have no guaranteed relative order -- so the
    /// income is staged one broadcast EARLIER, where the ordering is the
    /// engine's rather than an assumption. BeforeSideTurnStart is the only
    /// turn-start broadcast that precedes AfterPlayerTurnStart's whole
    /// dependency fan (see TURN_START_BROADCAST_ORDER in
    /// tier0/tests/test_reaction_phase_parity.py).
    ///
    /// PRE-DRAW AND PRE-BLOCK-CLEAR, and that is inert here: this power only
    /// moves a meter. It reads no hand, no deck, no energy and grants no
    /// Block, which is the same argument the sim's own comment at the
    /// insertion point makes for the divergence in the other direction.
    /// </summary>
    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return Task.CompletedTask;
        if (Owner?.Player == null) return Task.CompletedTask;
        KokomiResources.GainCharge(Owner, (int)Amount);
        return Task.CompletedTask;
    }
}

/// <summary>
/// Kokomi's Burst meter. Separate class from Klee's and Furina's because the
/// ceiling is hers (kokomi.yaml burst_max: 20) and because BaseLib keys
/// per-combat instances by resource type.
///
/// The three guards below are NOT boilerplate -- each one closes an exposure
/// the other two meters paid for in a playtest, and a meter that ships
/// without them is a meter that can be cast off empty or cast twice.
/// </summary>
public sealed class KokomiBurstResource : BasicCustomResource
{
    public KokomiBurstResource() : base("KLEEMOD_KOKOMI_BURST")
    {
    }

    /// <summary>
    /// The meter is not an energy cost and must not be discounted like one.
    /// BaseLib forwards SetToFreeThisTurn / SetToFreeThisCombat onto every
    /// custom-resource cost unless the resource opts out here. A "this card is
    /// free" effect landing on the kit card would zero the meter cost -- see
    /// <see cref="DrainOnPlay"/> for why that is catastrophic rather than
    /// merely generous.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>
    /// The cast gate is `requires: burst_energy_full` (tier0 card_playable):
    /// it reads the CANONICAL 20, never a discounted number. BaseLib's default
    /// CanAfford compares against the cost AFTER modifiers, and custom costs
    /// run through Hook.ModifyEnergyCostInCombat -- the hook cost reducers
    /// use. Without this override any cost reducer in range makes the Burst
    /// castable on an empty meter.
    /// </summary>
    public override bool CanAfford(CardModel card, int cost)
    {
        var canonical = CustomResources<KokomiBurstResource>.CanonicalCost(card);
        return canonical < 0 ? base.CanAfford(card, cost) : Amount >= canonical;
    }

    /// <summary>
    /// DELIBERATE NO-OP; the drain lives in <see cref="DrainOnPlay"/>, called
    /// from <see cref="KokomiResourceHooks.BeforeCardPlayed"/>. Same idiom and
    /// the same reason as Klee's -- see KleeBurstResource.DrainOnPlay for the
    /// infinite-Burst bug this shape exists to prevent (CardCmd.AutoPlay skips
    /// SpendResources entirely, so a drain riding the cost machinery is not
    /// called on every play path).
    /// </summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }

    /// <summary>
    /// Sim law, verbatim (combat.py play_card): `p.burst_energy = 0` on a
    /// requires-full play. Overflow past the max is lost at CAST, never
    /// clamped at gain, so this zeroes rather than subtracting.
    ///
    /// Gated on the card CARRYING a burst cost rather than on the concrete
    /// card type, which keeps it correct for any future kit card of hers.
    /// </summary>
    public static void DrainOnPlay(CardModel card)
    {
        if (CustomResources<KokomiBurstResource>.Cost(card) == null) return;
        var owner = card.Owner;
        if (owner == null) return;
        var resource = KokomiResources.FindBurst(owner.Creature);
        if (resource == null) return;
        resource.Amount = 0;
        Vfx.GaugeBridge.Refresh(owner.Creature);
    }
}

/// <summary>
/// Kokomi's kit-grant, port of tier0 grant_charged_kit (combat.py v1.9).
/// Same four rules Klee's and Furina's carry, and for the same reasons:
///   - grant only at a FULL meter (`>=`, because accrual is uncapped);
///   - never a duplicate: a copy already in hand blocks the grant;
///   - a full hand DEFERS, never drops -- the meter stays full so the next
///     check re-offers it. The hand-size test has to live HERE, before the
///     add, because the game's full-hand behaviour for
///     AddGeneratedCardToCombat is redirect-to-discard, and a kit card in a
///     pile recirculates the Burst as loot;
///   - the granted copy is fresh each time (the cast copy leaves combat).
/// </summary>
public static class KokomiKitGrant
{
    public static async Task GrantIfCharged(
        PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Character is not IKokomiCharacter) return;
        var playerCombatState = owner.PlayerCombatState;
        var combatState = owner.Creature.CombatState;
        if (playerCombatState == null || combatState == null) return;

        // Rules read the RESOURCE, never a display surface.
        var resource =
            CustomResources<KokomiBurstResource>.Get(playerCombatState);
        if (resource.Amount < KokomiConstants.BurstMax) return;

        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null
            || hand.Cards.Any(card => card is Cards.Kokomi.CeremonialGarment)
            || hand.Cards.Count >= CardPile.MaxCardsInHand)
        {
            return;
        }

        var burst = combatState.CreateCard<Cards.Kokomi.CeremonialGarment>(owner);
        await CardPileCmd.AddGeneratedCardToCombat(burst, PileType.Hand, owner);
    }
}
