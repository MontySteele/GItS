using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE VERBS: every rule in brief sec.3 that has to touch the engine, sited so
/// that each of them has exactly ONE implementation.
///
/// THE SPLIT THIS CLASS EXISTS FOR. <c>FurinaStageLedger</c> holds the
/// arithmetic and can be asked a question with no combat, no scene tree and no
/// <c>PlayerChoiceContext</c>; this holds the consequences, which need all
/// three. Every method here is the same two steps in the same order:
///
///   1. move the LEDGER, which is where the rule lives;
///   2. pay out whatever that move earned, then reconcile the bodies
///      (<c>FurinaStagePets.Sync</c>).
///
/// Written the other way round -- pay out, then record -- a bow that killed
/// the last enemy would fire off a stage the ledger had not yet emptied.
///
/// EVERY ENTRY IS ARM-GATED AND SEAT-GATED at its own door, through
/// <see cref="FurinaStage.LiveFor"/>. Not one of them is reachable from a
/// shipped file except behind <c>#if PROTOTYPE_CARDS</c>, and with the flag
/// off each is one early return.
/// </summary>
public static class FurinaStageRules
{
    /// <summary>
    /// RULE 2, the relic's opening: Usher takes the FRONT seat at
    /// <see cref="FurinaStageLaw.OpeningFanfare"/>. Idempotent on a stage that
    /// already has somebody standing on it, which is what lets the relic and a
    /// future kit install both make the sentence true for one list check.
    /// </summary>
    public static async Task Open(Creature? furina, StagePerformer who)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        if (FurinaStageLedger.For(furina!).OpenWith(who) == null) return;
        await FurinaStagePets.Sync(furina);
    }

    /// <summary>
    /// RULE 3, a summon. The rotation's leaver takes NO BOW (sec.10 default
    /// 5), so this pays nothing out: it moves the ledger and reconciles the
    /// bodies, and the newcomer's act arrives on its own at the end of the
    /// turn because it is standing there when the acts fire.
    /// </summary>
    public static async Task<StageSummon?> Summon(
        Creature? furina, StagePerformer who)
    {
        if (!FurinaStage.LiveFor(furina)) return null;
        var result = FurinaStageLedger.For(furina!).Summon(who);
        await FurinaStagePets.Sync(furina);
        return result;
    }

    /// <summary>
    /// RULE 3's other half, "a random performer not on stage" -- Salon Debut's
    /// roll (sec.10 default 2).
    ///
    /// THE POOL IS THE CAST MINUS THE STAGE, and on a stage carrying all three
    /// it is empty: the card then rolls over the whole cast, because a summon
    /// onto a full stage is a ROTATION and rotating in a duplicate is a legal
    /// board (rule 3 says nothing against it, and the shipped sheet's
    /// <i>Grand Gala</i> deploys one member twice).
    ///
    /// THE RNG IS THE RUN'S <c>CombatTargets</c> stream, which is the one
    /// every other roll in this mod draws from, so a seeded run is
    /// reproducible.
    /// </summary>
    public static StagePerformer Roll(Creature furina)
    {
        var ledger = FurinaStageLedger.For(furina);
        var onStage = ledger.Company.ToHashSet();
        var pool = All.Where(p => !onStage.Contains(p)).ToList();
        if (pool.Count == 0) pool = All.ToList();
        var rng = furina.Player?.RunState.Rng.CombatTargets;
        return rng == null ? pool[0] : rng.NextItem(pool);
    }

    /// <summary>The cast, in the order the brief's sec.2 table lists it.
    /// </summary>
    public static IReadOnlyList<StagePerformer> All { get; } = new[]
    {
        StagePerformer.Usher,
        StagePerformer.Chevalmarin,
        StagePerformer.Crabaletta,
    };

    /// <summary>
    /// RULE 5, a Raise: "Raise N Fanfare on the back performer" -- the
    /// back-most, which is the lead when it is alone. Returns what it raised,
    /// 0 on an empty stage.
    /// </summary>
    public static async Task<int> Raise(Creature? furina, int amount)
    {
        if (!FurinaStage.LiveFor(furina)) return 0;
        var raised = FurinaStageLedger.For(furina!).Raise(amount);
        if (raised > 0) await FurinaStagePets.Sync(furina);
        return raised;
    }

    /// <summary>
    /// RULE 8, a Spend rider paying out of the lead, and RULE 9's bow when
    /// that empties it.
    ///
    /// THE RETURN IS THE RIDER'S QUESTION, not the payment: a card asks "did
    /// my rider fire" and gets <see cref="StageSpend.Fired"/>, which is true
    /// whenever anybody was on the stage however little they could pay, and
    /// false only on an empty one. A card that priced its rider off
    /// <see cref="StageSpend.Paid"/> would be reintroducing the shortfall rule
    /// sec.10 default 4 removed.
    /// </summary>
    public static async Task<StageSpend> Spend(
        PlayerChoiceContext choiceContext, Creature? furina, int amount)
    {
        if (!FurinaStage.LiveFor(furina)) return new StageSpend(false, 0, null);
        var result = FurinaStageLedger.For(furina!).Spend(amount);
        if (result.Exit is { } exit) await Bow(choiceContext, furina!, exit);
        await FurinaStagePets.Sync(furina);
        return result;
    }

    /// <summary>
    /// RULE 9, the curtain call. ONE implementation, and it takes the exit
    /// rather than the performer so that the "no bow" cases cannot reach it by
    /// accident: <see cref="StageExit.Bows"/> is the ledger's own read of rule
    /// 7, and a departure that did not earn a bow returns here without paying.
    /// </summary>
    public static async Task Bow(
        PlayerChoiceContext choiceContext, Creature furina, StageExit exit)
    {
        if (!exit.Bows) return;
        switch (exit.Who)
        {
            case StagePerformer.Usher:
                await CreatureCmd.GainBlock(
                    furina, FurinaStageLaw.UsherBowBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case StagePerformer.Chevalmarin:
                foreach (var enemy in Enemies(furina))
                {
                    await ElementalHit.ApplyOnly(
                        choiceContext, enemy, Elements.Element.Hydro, furina);
                }
                break;
            case StagePerformer.Crabaletta:
                if (Pick(furina) is { } target)
                {
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.CrabalettaBowDamage, furina,
                        powered: false);
                }
                break;
        }
    }

    /// <summary>
    /// RULE 10, the acts, at the end of Furina's turn: FLAT, from ANY seat,
    /// and reading no bar.
    ///
    /// FLAT IS THE RULE AND NOT A SIMPLIFICATION. Sec.3 rule 10 ends "scaling
    /// on Fanfare lives in payoff cards (sec.5.2), never in the performer" --
    /// which is the whole separation between the Salon plan and the Ovation
    /// plan. An act that read its own bar would make every Refill a damage
    /// card and delete sec.5.2's card slot.
    ///
    /// FRONT TO BACK, because that is the order the strip draws and the order
    /// a player reads. It matters on exactly one board: three acts that each
    /// could be lethal resolve in a stated order rather than an arbitrary one.
    ///
    /// `powered: false` on the two damage acts, which is
    /// <c>SalonMemberPower.PerformMember</c>'s ruling one arm over (`EB-588`):
    /// a performance is not the player's Attack, so her Strength and her Weak
    /// do not enter it. The target's Vulnerable and the board's reaction still
    /// do -- that is what makes the hit real.
    /// </summary>
    public static async Task PerformActs(
        PlayerChoiceContext choiceContext, Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        var ledger = FurinaStageLedger.For(furina!);
        foreach (var seat in ledger.Seats.ToList())
        {
            if (furina!.IsDead) return;
            switch (seat.Who)
            {
                case StagePerformer.Usher:
                    await CreatureCmd.GainBlock(
                        furina, FurinaStageLaw.UsherActBlock,
                        ValueProp.Unpowered, null, fast: true);
                    break;
                case StagePerformer.Chevalmarin:
                    foreach (var enemy in Enemies(furina))
                    {
                        await ElementalHit.Deal(
                            choiceContext, enemy, Elements.Element.Hydro,
                            FurinaStageLaw.ChevalmarinActDamage, furina,
                            powered: false);
                    }
                    break;
                case StagePerformer.Crabaletta:
                    if (Pick(furina) is { } target)
                    {
                        await ElementalHit.Deal(
                            choiceContext, target, Elements.Element.Hydro,
                            FurinaStageLaw.CrabalettaActDamage, furina,
                            powered: false);
                    }
                    break;
            }
        }
    }

    /// <summary>
    /// RULE 4, the lead's regen, at the start of Furina's turn from her SECOND
    /// turn on. The turn number is the seat's own
    /// (<c>PlayerCombatState.TurnNumber</c>), which is per-player, so a co-op
    /// partner's turn cannot pay hers.
    /// </summary>
    public static async Task Regen(Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        var turn = furina!.Player?.PlayerCombatState?.TurnNumber ?? 0;
        if (FurinaStageLedger.For(furina).Regen(turn) <= 0) return;
        await FurinaStagePets.Sync(furina);
    }

    /// <summary>
    /// RULE 6's FLUSH. <see cref="FurinaStageLedger.Absorb"/> runs
    /// synchronously inside <c>ModifyHpLostBeforeOsty</c> because the engine
    /// wants a number back there; this is what pays for it a hook later, in
    /// <c>AfterDamageReceived</c> -- the same deferral
    /// <c>FurinaResources.FlushFanfareDeltaBlock</c> already makes for the
    /// shipped kit's Block, and per damage instance, so the board is settled
    /// before the NEXT hit of the same flurry.
    ///
    /// NOTHING IS PAID OUT, only reconciled: a lead emptied by a hit takes no
    /// bow (rule 7, first clause).
    /// </summary>
    public static async Task Flush(Creature? furina) =>
        await FurinaStagePets.Sync(furina);

    private static IEnumerable<Creature> Enemies(Creature furina) =>
        furina.CombatState?.HittableEnemies.ToList()
        ?? Enumerable.Empty<Creature>();

    /// <summary>A random hittable enemy off the run's own combat stream, or
    /// null on an empty board.</summary>
    private static Creature? Pick(Creature furina)
    {
        var targets = Enemies(furina).ToList();
        if (targets.Count == 0) return null;
        var rng = furina.Player?.RunState.Rng.CombatTargets;
        return rng == null ? targets[0] : rng.NextItem(targets);
    }
}
