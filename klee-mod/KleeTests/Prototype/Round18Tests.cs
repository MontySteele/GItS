using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND EIGHTEEN -- the two seats' act-one runs on the same relic
/// (`review/active/klee-overhaul-round-18-2026-09-05.md`), and the five rows
/// they left behind.
///
/// `EB-516`, the two ADJUSTMENTS the doctrine read ruled FOLLOWS on: Grounded's
/// condition becomes "if you have a Bomb on the field", and a random Set off
/// draws from the enemies carrying one.
///
/// `EB-512` to `EB-515`, the four DEFECTS: Stoke the Fuse billed and did not
/// charge, Frail skipped a companion's Block, the stacked-Bomb headline hid its
/// hit count, and a killing Electro hit into a Pyro aura fired no Overloaded.
///
/// WHAT IS REAL AND WHAT IS STRUCTURAL, per file convention (README, "the
/// headless boundary"). Real: every DECISION these rows take -- who Grounded
/// pays, which bodies a random Set off may roll, whether a spend that moved
/// nothing reports itself as paid, and which props the two Block surfaces
/// carry. Structural, and labelled at the site: the rolls, the payouts and the
/// reaction itself, all of which need a live `CombatState`.
/// </summary>
public class Round18Tests
{
    private const BindingFlags All = HeadlessGame.All;

    // ==================================================================
    // `EB-516` (1) -- Grounded reads the board
    // ==================================================================

    [Fact]
    public void Grounded_pays_while_a_bomb_is_cooking_and_not_on_an_empty_field()
    {
        // REAL. `AnyPlacedBy` is the whole of the new condition and it is a
        // pure read off the board, so the three pins the row names are all
        // reachable: an empty field pays nothing, a Mine alone pays, and a
        // Bomb still cooking pays whatever went off before it.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature),
                     "an empty field is not a Bomb on the field");

        // A MINE ALONE PAYS: a Mine is a Bomb (`EB-373`).
        var pile = ProtoBombs.Place(enemy, klee.Creature,
                                    new ProtoBombs.Charge(4, IsMine: true));
        Assert.True(ProtoBombPower.AnyPlacedBy(klee.Creature));

        // ONE WENT OFF AND ANOTHER IS STILL COOKING -- the reading the old
        // explosion counter could not express, and the r18 ledgers' common
        // case: something goes off on most turns because Mines fire on the
        // enemy's beat.
        pile.TakeAll();
        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature));
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(7));
        Assert.True(ProtoBombPower.AnyPlacedBy(klee.Creature));
    }

    [Fact]
    public void Groundeds_face_prints_the_condition_it_now_runs()
    {
        // The Power badge and the card row say the same thing, which is the
        // half of `EB-516` a player can see.
        var badge = new GroundedPower().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("if you have a [gold]Bomb[/gold] on the field", badge);
        Assert.DoesNotContain("went off last turn", badge);

        var card = new ProtoKoGrounded().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("if you have a [gold]Bomb[/gold] on the field", card);
        Assert.DoesNotContain("went off last turn", card);
    }

    // ==================================================================
    // `EB-516` (2) -- a random Set off prefers a bombed enemy
    // ==================================================================

    [Fact]
    public void A_random_set_off_draws_only_from_the_bombed_bodies()
    {
        // REAL, and it is the whole rule: `BombedFirst` is the bag the roll
        // draws from, extracted for exactly this reason (the roll around it
        // needs a live combat). A two-enemy board with one Bomb can only
        // produce the bombed body, however the die falls.
        var klee = Seat.Klee();
        var bombed = Seat.Klee(60).Creature;
        var bare = Seat.Klee(60).Creature;
        ProtoBombs.Board(klee.Creature, bombed, bare);
        ProtoBombs.Place(bombed, klee.Creature, new ProtoBombs.Charge(4));

        var bag = ProtoBombPower.BombedFirst(new[] { bombed, bare },
                                             klee.Creature);
        Assert.Equal(new[] { bombed }, bag);
    }

    [Fact]
    public void A_bomb_less_board_is_uniform_and_a_mine_counts()
    {
        // The fallback is EVERY living enemy and not an empty bag: the card
        // still resolves on a board holding none of hers, which is what keeps
        // "Set off a random enemy and deal 4, twice" a legal play. And a Mine
        // puts its body in the bag, for `EB-373`'s reason.
        var klee = Seat.Klee();
        var a = Seat.Klee(60).Creature;
        var b = Seat.Klee(60).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        Assert.Equal(new[] { a, b },
                     ProtoBombPower.BombedFirst(new[] { a, b }, klee.Creature));

        ProtoBombs.Place(b, klee.Creature,
                         new ProtoBombs.Charge(4, IsMine: true));
        Assert.Equal(new[] { b },
                     ProtoBombPower.BombedFirst(new[] { a, b }, klee.Creature));
    }

    [Fact]
    public void Another_placers_pile_does_not_put_a_body_in_the_bag()
    {
        // R205-scoped, like every other read of the pile: a second Klee's
        // Bomb is not hers to cash, so it cannot aim her card.
        var klee = Seat.Klee();
        var other = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var bare = Seat.Klee(60).Creature;
        ProtoBombs.Board(klee.Creature, enemy, bare);
        ProtoBombs.Place(enemy, other.Creature, new ProtoBombs.Charge(9));

        Assert.Equal(new[] { enemy, bare },
                     ProtoBombPower.BombedFirst(new[] { enemy, bare },
                                                klee.Creature));
    }

    [Fact]
    public void The_roll_draws_from_the_bag_and_re_reads_it_per_hit()
    {
        // STRUCTURAL: the roll needs a live combat and its RNG. What is read
        // is that `SetOffRandom` asks `BombedFirst` at all, and that it does so
        // INSIDE the per-hit loop -- the bag is re-read like the wider one was,
        // so a body whose last charge this hit spent is out of it next roll.
        var loop = Il.CallSequence(
            Il.Method("ProtoBombPower", "SetOffRandom")).ToList();

        Assert.Contains("ProtoBombPower.BombedFirst", loop);
        var bagAt = loop.FindIndex(c => c == "ProtoBombPower.BombedFirst");
        var rollAt = loop.FindIndex(c => c.Contains("NextItem"));
        Assert.True(bagAt >= 0, "the roll asks for the bag");
        Assert.True(rollAt > bagAt,
                    "the bag is built before the die is thrown");
        // And INSIDE the loop, beside the living read it narrows: both are
        // taken per hit, so the bag cannot outlive the board it describes.
        Assert.Contains("ICombatState.get_HittableEnemies", loop);
    }

    // ==================================================================
    // `EB-512` -- a spend that moved nothing is not a payment
    // ==================================================================

    [Fact]
    public void A_spend_that_did_not_move_the_bank_is_not_reported_as_paid()
    {
        // REAL, and it reproduces the r18 screen exactly. `PowerCmd.ModifyAmount`
        // returns having touched nothing on two of its own guards -- the combat
        // is ending, or the power's owner has no combat state -- and the second
        // is what a seat with no `CombatState` here stands in for. Before
        // `EB-512` this returned TRUE with the bank whole, which is precisely
        // "the effect billed me and the counter did not".
        var klee = Seat.Klee().WithPower<SparkPower>(2);

        Assert.True(SparkPower.CanSpend(klee.Creature, 2));
        Assert.Equal(2, SparkPower.SparksAtPlay(klee.Creature));

        var paid = SparkPower
            .Spend(null!, klee.Creature, 2, null).GetAwaiter().GetResult();

        Assert.False(paid, "the bank did not move, so nothing was paid");
        Assert.Equal(2, SparkPower.SparksAtPlay(klee.Creature));
    }

    [Fact]
    public void A_short_bank_still_refuses_through_the_gates_own_predicate()
    {
        // The older refusal is untouched: `EB-512` added a second answer, it
        // did not move the first one.
        var klee = Seat.Klee().WithPower<SparkPower>(1);

        Assert.False(SparkPower
            .Spend(null!, klee.Creature, 3, null).GetAwaiter().GetResult());
        Assert.Equal(1, SparkPower.SparksAtPlay(klee.Creature));
    }

    [Fact]
    public void Stoke_the_fuse_abandons_its_payout_when_the_price_fails()
    {
        // STRUCTURAL: an `OnPlay` body needs a live combat. What is read is
        // the SHAPE the codegen now emits for the X price -- the bank is
        // captured, the spend is GUARDED, and the payout is behind the guard.
        // The gate in front of the card is a printed price of ONE while the
        // spend asks for the whole bank, so the two ask different questions
        // and a failed spend is not one the gate could have refused.
        var play = Il.CallSequence(
            Il.Method("ProtoKoStokeTheFuse", "OnPlay")).ToList();

        var read = play.FindIndex(c => c.Contains("SparkPower.SparksAtPlay"));
        var spend = play.FindIndex(c => c.Contains("SparkPower.Spend"));
        var grow = play.FindIndex(
            c => c.Contains("ProtoBombPower.GrowLargestPerSpark"));

        Assert.True(read < spend, "the bank is read before it is emptied");
        Assert.True(spend < grow, "the price is paid before the payout");

        // The guard itself: the emitted body branches on the spend's answer,
        // which is what the old `await ...;` could not do.
        var il = Il.Method("ProtoKoStokeTheFuse", "OnPlay");
        Assert.Contains("SparkPower.Spend", Il.Calls(il));
        Assert.Contains(
            "if (!await SparkPower.Spend(choiceContext, Owner.Creature, "
            + "sparksSpent, this)) return;",
            System.IO.File.ReadAllText(
                System.IO.Path.Combine(Repo(), "klee-mod", "KleeCode", "Cards",
                                       "Prototype", "Generated",
                                       "ProtoKoStokeTheFuse.cs")));
    }

    // ==================================================================
    // `EB-513` -- a companion's printed Block takes the card's Frail fold
    // ==================================================================

    [Theory]
    [InlineData("ShakenNotPurredPower")]
    [InlineData("IGotYourBackPower")]
    [InlineData("FrontRowSeatPower")]
    public void A_companion_pays_its_block_through_the_cards_own_fold(string power)
    {
        // STRUCTURAL for the hit -- `CreatureCmd.GainBlock` needs a live
        // combat -- and it is the one value that decides the rule:
        // `FrailPower.ModifyBlockMultiplicative` folds exactly when the props
        // carry `Move` and not `Unpowered`, so the props ARE the fold. Read
        // out of the compiled body rather than asserted about behaviour.
        var pay = typeof(ShakenNotPurredPower).Assembly
            .GetTypes().First(t => t.Name == power)
            .GetMethod("Pay", All)!;

        Assert.Contains("CreatureCmd.GainBlock", Il.Calls(pay));
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(
            Repo(), "klee-mod", "KleeCode", "Powers", "Prototype",
            "CompanionStandIns.cs"));
        Assert.DoesNotContain(
            "await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, "
            + "null,", source);
    }

    [Fact]
    public void A_companions_printed_bonus_block_folds_on_its_face_too()
    {
        // REAL. The face's number is `{PowerAmount:diff()}`, which renders the
        // var's `PreviewValue`; only a `BlockVar` writes one, by running
        // `Hook.ModifyBlock` in `UpdateCardPreview`. A bare `DynamicVar` -- what
        // the row emitted until `EB-513` -- has an empty override, which is why
        // Diona printed 5 under Frail and delivered 5.
        //
        // ONE FOLD: `IntValue` is `(int)BaseValue`, so the Apply still hands the
        // power the PRINTED number and the fold happens once, on the way out.
        foreach (var card in new CardModelUnderTest[]
                 {
                     new(new ProtoMcDionaShakenNotPurred()),
                     new(new ProtoMcNoelleIGotYourBack()),
                     new(new ProtoMcBarbaraFrontRowSeat()),
                 })
        {
            var amount = card.Var("PowerAmount");
            var block = Assert.IsType<BlockVar>(amount);
            Assert.Equal(ValueProp.Move, block.Props);
            Assert.True(block.IntValue > 0);
        }
    }

    // ==================================================================
    // `EB-514` -- the stacked-Bomb headline names its hit count
    // ==================================================================

    [Fact]
    public void A_stacks_headline_names_its_hit_count_and_its_sparks()
    {
        // REAL as a row read, which is how every badge face is pinned here.
        // The seat's complaint was about the FIRST sentence: the total is a
        // sum over the charges, so `deals 7` read as one hit and one Spark on
        // a pile that was two of each.
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4),
                                    new ProtoBombs.Charge(3));
        var rows = pile.Localization!;

        foreach (var key in new[] { "smartDescription", "smartDescriptionMines" })
        {
            var face = rows.First(r => r.Item1 == key).Item2;
            Assert.Contains("Pyro damage, in [blue]{Count}[/blue] "
                            + "hit{Count:plural:|s} for as many "
                            + "[gold]Sparks[/gold].", face);
            // The queue stays where `EB-450` put it: the sizes are a different
            // fact from the count, and the headline is where the plan is made.
            Assert.Contains("Bombs here: [blue]{Charges}[/blue]", face);
        }
    }

    [Fact]
    public void The_hit_count_is_the_live_charge_list_and_not_the_stack()
    {
        // `EB-289`'s var, unchanged: a Mine that has already self-popped is
        // off the list and out of the count, and the stack cannot be lowered
        // by the pure takes.
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4, IsMine: true),
                                    new ProtoBombs.Charge(3));
        Sync(pile);
        Assert.Equal(2, pile.DynamicVars["Count"].IntValue);

        pile.TakeMines();
        Sync(pile);
        Assert.Equal(1, pile.DynamicVars["Count"].IntValue);
    }

    // ==================================================================
    // `EB-515` -- a killing hit still fires its reaction
    // ==================================================================

    [Fact]
    public void The_aura_resolves_its_reaction_on_a_killing_hit_too()
    {
        // STRUCTURAL, and the boundary is the base game's: `CreatureCmd.Damage`
        // guards its whole `Hook.AfterDamageReceived` broadcast on the hit NOT
        // having killed, so the site the aura has always hung off never runs on
        // a kill. `Hook.AfterDamageGiven` is raised from the same method, over
        // the same listener set, ABOVE that guard -- so the killing case is
        // served there, and the two sites are exclusive by construction.
        var given = typeof(AuraPower).GetMethod("AfterDamageGiven", All)!;
        var received = typeof(AuraPower).GetMethod("AfterDamageReceived", All)!;

        Assert.Contains("AuraPower.ResolveLifecycle", Il.Calls(given));
        Assert.Contains("AuraPower.ResolveLifecycle", Il.Calls(received));

        // The guard is the exact complement of the base game's, so no aura is
        // consumed twice: this site acts only when the hit killed.
        var calls = Il.Calls(given);
        Assert.Contains("DamageResult.get_WasTargetKilled", calls);
        Assert.Contains("Creature.get_IsDead", calls);
    }

    [Fact]
    public void The_reaction_is_resolved_in_one_place_for_both_sites()
    {
        // ONE BODY, TWO DOORS: the consume, the refresh and
        // `ReactionEffects.Resolve` all live in `ResolveLifecycle`, so a
        // killing hit and an ordinary one cannot resolve two different rules.
        var lifecycle = typeof(AuraPower)
            .GetMethod("ResolveLifecycle", All)!;
        var calls = Il.Calls(lifecycle);

        Assert.Contains("ReactionEffects.Resolve", calls);
        Assert.Contains("PowerCmd.Remove", calls);
        Assert.DoesNotContain("ReactionEffects.Resolve",
                              Il.Calls(typeof(AuraPower)
                                  .GetMethod("AfterDamageGiven", All)!));
    }

    // ---- helpers ---------------------------------------------------------

    /// <summary>`SyncDisplay` is private and is what every mutator calls; the
    /// pins above are about the number it writes, not about who calls it.
    /// </summary>
    private static void Sync(ProtoBombPower pile) =>
        typeof(ProtoBombPower).GetMethod("SyncDisplay", All)!
            .Invoke(pile, System.Array.Empty<object>());

    private static string Repo()
    {
        var dir = new System.IO.DirectoryInfo(
            System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(dir.FullName, "klee-mod")))
        {
            dir = dir.Parent;
        }
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    /// <summary>A generated card, with its canonical vars materialised the way
    /// the game materialises them at construction.</summary>
    private readonly struct CardModelUnderTest
    {
        private readonly CardModel _card;

        public CardModelUnderTest(
            CardModel card) => _card = card;

        public DynamicVar Var(string name) => _card.DynamicVars[name];
    }
}
