using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CO-OP SET (review/records/coop-set-2026-09-25.md): nine
/// multiplayer-only cards, three per character.
///
/// THE SIM SEATS ONE PLAYER, so this is the only engine the co-op rules are
/// tested in (`tier0/engine/coop.py` says so on the other side, and
/// `tier0/tests/test_coop_set.py` pins that the sim loads the rows and never
/// deals them).
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KleePlaytest20260924Tests"/>' terms. The cards' own declarations,
/// the single-player filter, the "each other player" walk, the hit record, the
/// Guest of Honor redirect (a synchronous hook over the real Stage ledger) and
/// the Mine's pre-emption of it are run for real. Anything that awaits a
/// command -- a Set off, a Block gain, a draw, a Bow -- needs a live combat,
/// so its ORDER and its DOORS are pinned off the compiled methods and say so.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class CoopSetTests
{
    private static ValueProp Attack => ValueProp.Move;

    // ---- the nine cards, as the spec prints them -------------------------

    public static IEnumerable<object[]> Nine => new[]
    {
        Row<ProtoKoPassTheMatch>(0, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoKoHideHere>(1, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoKoKnightsOfFavonius>(2, CardType.Power, CardRarity.Rare),
        Row<ProtoFsGuestOfHonor>(1, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoFsShareTheSpotlight>(1, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoFsPeopleOfFontaine>(1, CardType.Power, CardRarity.Rare),
        Row<ProtoKkJointOrders>(1, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoKkCoordinatedStrike>(1, CardType.Attack, CardRarity.Uncommon),
        Row<ProtoKkSangonomiyasCounsel>(2, CardType.Power, CardRarity.Rare),
    };

    private static object[] Row<T>(int cost, CardType type, CardRarity rarity)
        where T : CardModel, new() =>
        new object[] { typeof(T), cost, type, rarity };

    [Theory]
    [MemberData(nameof(Nine))]
    public void Every_card_is_multiplayer_only_at_the_printed_cost_type_and_rarity(
        Type cardType, int cost, CardType type, CardRarity rarity)
    {
        var card = (CardModel)Activator.CreateInstance(cardType)!;
        Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                     card.MultiplayerConstraint);
        Assert.Equal(cost, card.EnergyCost.Canonical);
        Assert.Equal(type, card.Type);
        Assert.Equal(rarity, card.Rarity);
    }

    [Fact]
    public void Another_player_is_the_base_games_ally_target()
    {
        // Lift and Believe In You's `TargetType.AnyAlly`: a living player who
        // is not you. "Each other player" takes no target.
        Assert.Equal(TargetType.AnyAlly, new ProtoKoPassTheMatch().TargetType);
        Assert.Equal(TargetType.AnyAlly, new ProtoKoHideHere().TargetType);
        Assert.Equal(TargetType.AnyAlly, new ProtoFsGuestOfHonor().TargetType);
        Assert.Equal(TargetType.AnyAlly,
                     new ProtoFsShareTheSpotlight().TargetType);
        Assert.Equal(TargetType.Self, new ProtoKoKnightsOfFavonius().TargetType);
        Assert.Equal(TargetType.Self, new ProtoFsPeopleOfFontaine().TargetType);
        Assert.Equal(TargetType.Self,
                     new ProtoKkSangonomiyasCounsel().TargetType);
    }

    [Fact]
    public void The_faces_are_the_designs_words()
    {
        Assert.Equal(
            "Choose another player. This turn, their next Attack [gold]Sets off[/gold] "
            + "your [gold]Bombs[/gold] on each enemy it hits. Draw {Cards:diff()} "
            + "card{Cards:plural:|s}.",
            Face(new ProtoKoPassTheMatch()));
        Assert.Equal(
            "Until your next turn, hits on another player land on "
            + "their [gold]Block[/gold], then your [gold]front performer[/gold]'s "
            + "[gold]Fanfare[/gold], then them.",
            Face(new ProtoFsGuestOfHonor()));
        Assert.Equal(
            "Another player gains {Block:diff()} [gold]Block[/gold]. "
            + "[gold]Plan[/gold]: They draw 2 cards.",
            Face(new ProtoKkJointOrders()));
    }

    // ---- the single-player guard -----------------------------------------

    [Fact]
    public void A_single_player_run_is_never_offered_one()
    {
        // REAL, through the base game's own filter: `GetUnlockedCards` with a
        // one-player run's constraint (`IRunState.CardMultiplayerConstraint`
        // is SingleplayerOnly at one player) drops every MultiplayerOnly card
        // and keeps every other one; a co-op run keeps them.
        var pool = (CoopProbePool)RuntimeHelpers.GetUninitializedObject(
            typeof(CoopProbePool));
        var solo = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.SingleplayerOnly).ToList();
        Assert.Single(solo);
        Assert.IsType<ProtoKoCarefulNow>(solo[0]);

        var coop = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.MultiplayerOnly).ToList();
        Assert.Equal(10, coop.Count);
    }

    /// <summary>A pool of the nine and one standard card, through the base
    /// game's own <c>CardPoolModel.GetUnlockedCards</c>.</summary>
    private sealed class CoopProbePool : CardPoolModel
    {
        public override string Title => "probe";
        public override string EnergyColorName => "probe";
        public override string CardFrameMaterialPath => "probe";
        public override Godot.Color DeckEntryCardColor => default;
        public override bool IsColorless => true;

        protected override CardModel[] GenerateAllCards() => new CardModel[]
        {
            new ProtoKoCarefulNow(),
            new ProtoKoPassTheMatch(), new ProtoKoHideHere(),
            new ProtoKoKnightsOfFavonius(), new ProtoFsGuestOfHonor(),
            new ProtoFsShareTheSpotlight(), new ProtoFsPeopleOfFontaine(),
            new ProtoKkJointOrders(), new ProtoKkCoordinatedStrike(),
            new ProtoKkSangonomiyasCounsel(),
        };
    }

    [Fact]
    public void Each_arm_offers_its_tier_through_its_one_pool_door_outside_the_slice()
    {
        // STRUCTURAL: the offer seams need ModelDb. The tier is its OWN list
        // (so the slice's count and its pins do not move) and the pool door
        // concatenates it.
        Assert.Contains("KleeOverhaulRoster.MultiplayerSlice",
            Il.Calls(Il.Method("KleeOverhaulRoster", "OfferablePool")));
        Assert.Contains("KokomiOverhaulRoster.MultiplayerSlice",
            Il.Calls(Il.Method("KokomiOverhaulRoster", "OfferablePool")));
        Assert.Contains("FurinaStageRoster.MultiplayerRows",
            Il.Calls(Il.Method("FurinaStageRoster", "SwapOfferedRows")));
        Assert.DoesNotContain(
            Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice")),
            c => c.Contains("PassTheMatch") || c.Contains("HideHere")
                 || c.Contains("KnightsOfFavonius"));
    }

    // ---- "each other player" ----------------------------------------------

    [Fact]
    public void Each_other_player_is_every_living_player_but_you()
    {
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var kokomi = Seat.Kokomi();
        var enemy = Enemy();
        Table(new[] { klee.Creature, furina.Creature, kokomi.Creature }, enemy);

        var others = CoopSet.OtherPlayers(klee.Creature);
        Assert.Equal(new[] { furina.Creature, kokomi.Creature }, others);

        Seat.Set(kokomi.Creature, "CurrentHp", 0);
        Assert.Equal(new[] { furina.Creature },
                     CoopSet.OtherPlayers(klee.Creature));
        Assert.Empty(CoopSet.OtherPlayers(null));
    }

    [Fact]
    public void A_one_seat_fight_has_no_other_player()
    {
        var klee = Seat.Klee();
        Table(new[] { klee.Creature }, Enemy());
        Assert.Empty(CoopSet.OtherPlayers(klee.Creature));
        Assert.Null(CoopSet.PlanAlly(klee.Creature));
    }

    // ---- which enemies an Attack hit ---------------------------------------

    [Fact]
    public void The_hit_record_names_each_enemy_the_watched_attack_hit_once()
    {
        var attack = new ProtoKkCoordinatedStrike();
        var other = new ProtoKkCoordinatedStrike();
        var a = Enemy();
        var b = Enemy();
        var ally = Seat.Furina().Creature;

        var record = new CoopSet.HitRecord();
        record.Note(a, attack);                  // not watching yet
        record.Begin(attack);
        record.Note(b, attack);
        record.Note(a, attack);
        record.Note(b, attack);                  // twice is once
        record.Note(a, other);                   // another card's hit
        record.Note(a, null);                    // a Bomb, a Mine, an act
        record.Note(ally, attack);               // not an enemy
        Assert.Equal(new[] { b, a }, record.Take());
        Assert.Empty(record.Hit);
        Assert.True(record.Watching(attack));
        record.End();
        Assert.False(record.Watching(attack));
    }

    [Fact]
    public void Another_players_attack_is_an_attack_card_whose_owner_is_not_you()
    {
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var attack = Owned(new ProtoKkCoordinatedStrike(), furina);
        var skill = Owned(new ProtoKoHideHere(), furina);
        var hers = Owned(new ProtoKkCoordinatedStrike(), klee);

        Assert.True(CoopSet.IsAnotherPlayersAttack(Play(attack, furina), klee.Creature));
        Assert.False(CoopSet.IsAnotherPlayersAttack(Play(skill, furina), klee.Creature));
        Assert.False(CoopSet.IsAnotherPlayersAttack(Play(hers, klee), klee.Creature));
    }

    // ---- Klee ------------------------------------------------------------------

    [Fact]
    public void An_allys_set_off_is_hers_and_not_a_set_off_card()
    {
        // STRUCTURAL (an explosion needs a live combat). The Bombs are set off
        // through the raw `SetOff` with KLEE as the applier, so her pile, her
        // Sparks, jumps and Mine readers pay; and none of the card-facing
        // entry points is taken, so Once More!'s note and Boom Badge's
        // doubling never see the ally's card.
        var calls = Il.Calls(Il.Method("CoopSet", "SetOffOn"));
        Assert.Contains("ProtoBombPower.SetOff", calls);
        Assert.Contains("ProtoBombPower.SweepJumps", calls);
        Assert.DoesNotContain("ProtoBombPower.SetOffAimed", calls);
        Assert.DoesNotContain("BoomBadgePower.Spend", calls);
        Assert.DoesNotContain(calls, c => c.Contains("NoteSetOffCardPlayed"));

        // After the Attack's hits resolve: the record is TAKEN in
        // AfterCardPlayed and handed to the Set off.
        foreach (var power in new[] { "PassTheMatchPower", "KnightsOfFavoniusPower" })
        {
            var after = Il.CallSequence(Il.Method(power, "AfterCardPlayed")).ToList();
            Assert.True(after.IndexOf("HitRecord.Take") < after.IndexOf("CoopSet.SetOffOn"),
                        power);
            Assert.Contains("HitRecord.Note",
                Il.Calls(Il.Method(power, "AfterDamageReceived")));
        }
        Assert.Contains("CoopSet.IsAnotherPlayersAttack",
            Il.Calls(Il.Method("KnightsOfFavoniusPower", "BeforeCardPlayed")));
    }

    [Fact]
    public void Pass_the_match_goes_on_the_ally_placed_by_klee_and_ends_with_the_turn()
    {
        var play = Il.Calls(Il.Method("ProtoKoPassTheMatch", "OnPlay"));
        Assert.Contains(play, c => c.StartsWith("PowerCmd.Apply"));
        Assert.Contains(play, c => c.StartsWith("CardPileCmd.Draw"));
        Assert.Contains("PowerCmd.Remove",
            Il.Calls(Il.Method("PassTheMatchPower", "AfterSideTurnEnd")));
        var power = (PassTheMatchPower)RuntimeHelpers.GetUninitializedObject(
            typeof(PassTheMatchPower));
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Powers.PowerInstanceType.InstancedPerApplier,
                     power.InstanceType);
    }

    [Fact]
    public void Hide_here_pays_her_largest_bomb_capped_to_the_aimed_player()
    {
        var klee = Seat.Klee();
        var a = Enemy();
        var b = Enemy();
        ProtoBombs.Board(klee.Creature, a, b);
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(5),
                         new ProtoBombs.Charge(9));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(14));

        // Board-wide largest, capped; nothing removed.
        Assert.Equal(12, ProtoBombPower.LargestBombBlock(klee.Creature, 12));
        Assert.Equal(14, ProtoBombPower.LargestBombBlock(klee.Creature, 16));
        Assert.Equal(3, a.Powers.OfType<ProtoBombPower>().Sum(p => p.Amount)
                        + b.Powers.OfType<ProtoBombPower>().Sum(p => p.Amount));

        // The card hands the aimed player and the play to the rule, and the
        // smith moves the printed cap.
        var play = Il.Calls(Il.Method("ProtoKoHideHere", "OnPlay"));
        Assert.Contains("ProtoBombPower.BlockAllyForLargestBomb", play);
        Assert.Contains("{BombCap:diff()}", Face(new ProtoKoHideHere()));
    }

    [Fact]
    public async System.Threading.Tasks.Task Hide_here_with_nobody_to_give_it_to_pays_nothing()
    {
        var klee = Seat.Klee();
        var a = Enemy();
        ProtoBombs.Board(klee.Creature, a);
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(9));
        Assert.Equal(0, await ProtoBombPower.BlockAllyForLargestBomb(
            null!, klee.Creature, 12, ally: null, cardPlay: null));
    }

    // ---- Furina ----------------------------------------------------------------

    [Fact]
    public void Guest_of_honor_sends_what_is_left_after_their_block_to_the_lead()
    {
        using var _ = new StageArm();
        var (furina, stage) = Stage((StagePerformer.Usher, 5),
                                    (StagePerformer.Crabaletta, 3));
        var ally = Seat.Klee();
        var enemy = Enemy();
        var guest = Guest(ally, furina);

        // 8 past the ally's Block: the lead takes 5 and leaves WITHOUT a Bow
        // (a hit), the back performer steps forward, and 3 reaches the ally.
        Assert.Equal(3m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 8m, Attack, enemy, cardSource: null));
        Assert.Single(stage.Seats);
        Assert.Equal(StagePerformer.Crabaletta, stage.Lead!.Who);
        Assert.Equal(3, stage.Lead.Fanfare);

        // A smaller hit stops at the lead.
        Assert.Equal(0m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 2m, Attack, enemy, cardSource: null));
        Assert.Equal(1, stage.Lead!.Fanfare);
    }

    [Fact]
    public void Guest_of_honor_is_attacks_on_the_guest_only()
    {
        using var _ = new StageArm();
        var (furina, stage) = Stage((StagePerformer.Usher, 5));
        var ally = Seat.Klee();
        var enemy = Enemy();
        var guest = Guest(ally, furina);

        // Not the guest, not an attack, or unblockable: untouched.
        Assert.Equal(8m, guest.ModifyHpLostBeforeOsty(
            furina.Creature, 8m, Attack, enemy, null));
        Assert.Equal(8m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 8m, ValueProp.Unpowered, enemy, null));
        Assert.Equal(8m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 8m, Attack | ValueProp.Unblockable, enemy, null));
        Assert.Equal(5, stage.Lead!.Fanfare);

        // With the Stage off nothing is redirected.
        FurinaStage.Enabled = false;
        Assert.Equal(8m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 8m, Attack, enemy, null));
    }

    [Fact]
    public void A_lethal_mine_still_fires_first_and_the_lead_pays_nothing()
    {
        // The Mine answers in BeforeDamageReceived, before Block, on ANY
        // player (PR #658); a lethal one notes the pre-empted hit, and the
        // redirect then takes nothing off the lead for a hit that never
        // happened. A Mine that does not kill leaves the hit to land here.
        using var _ = new StageArm();
        var (furina, stage) = Stage((StagePerformer.Usher, 5));
        var ally = Seat.Klee();
        var enemy = Enemy();
        var guest = Guest(ally, furina);
        var klee = Seat.Klee();
        Assert.True(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, ally.Creature, enemy, Attack));

        ProtoBombPower.Preempted.Clear();
        try
        {
            Seat.Set(enemy, "CurrentHp", 0);
            ProtoBombPower.Preempted.Note(ally.Creature, enemy);
            Assert.Equal(0m, guest.ModifyHpLostBeforeOsty(
                ally.Creature, 8m, Attack, enemy, null));
            Assert.Equal(5, stage.Lead!.Fanfare);
        }
        finally
        {
            ProtoBombPower.Preempted.Clear();
        }
    }

    [Fact]
    public void A_rapt_audience_fires_on_a_hit_the_guest_took()
    {
        using var _ = new StageArm();
        var (furina, stage) = Stage((StagePerformer.Usher, 9),
                                    (StagePerformer.Crabaletta, 1));
        furina.WithPower<RaptAudiencePower>(50);
        var ally = Seat.Klee();
        var guest = Guest(ally, furina);

        Assert.Equal(0m, guest.ModifyHpLostBeforeOsty(
            ally.Creature, 4m, Attack, Enemy(), null));
        Assert.Equal(5, stage.Lead!.Fanfare);
        Assert.Equal(3, stage.Back!.Fanfare);    // 1 + half of 4
    }

    [Fact]
    public void Guest_of_honor_flushes_her_stage_and_leaves_at_the_next_turn()
    {
        Assert.Contains("FurinaStage.Flush",
            Il.Calls(Il.Method("GuestOfHonorPower", "AfterDamageReceived")));
        Assert.Contains("PowerCmd.Remove",
            Il.Calls(Il.Method("GuestOfHonorPower", "BeforeSideTurnStart")));
        Assert.Contains("PowerCmd.Remove",
            Il.Calls(Il.Method("GuestOfHonorPower", "AfterDeath")));
    }

    [Fact]
    public void Share_the_spotlight_gives_the_whole_bar_as_block_then_bows()
    {
        // STRUCTURAL: an exact emptying of the back bar, the Block to the
        // aimed player FIRST (the face's order), then a real Bow.
        var seq = Il.CallSequence(Il.Method("FurinaStage", "ShareTheSpotlight")).ToList();
        var spend = seq.IndexOf("FurinaStageLedger.SpendAllOfBack");
        var block = seq.FindIndex(c => c.StartsWith("CreatureCmd.GainBlock"));
        var bow = seq.IndexOf("FurinaStage.Bow");
        Assert.True(spend >= 0 && spend < block && block < bow);
    }

    [Fact]
    public void The_ledger_empties_the_back_bar_exactly_and_owes_a_bow()
    {
        using var _ = new StageArm();
        var (furina, stage) = Stage((StagePerformer.Usher, 4),
                                    (StagePerformer.Chevalmarin, 6));
        var result = stage.SpendAllOfBack();
        Assert.True(result.Fired);
        Assert.Equal(6, result.Paid);
        Assert.True(result.Exit!.Value.Bows);
        Assert.Single(stage.Seats);

        stage.Clear();
        Assert.False(stage.SpendAllOfBack().Fired);   // empty stage: nothing
    }

    [Fact]
    public void The_people_of_fontaine_raise_on_another_players_attack()
    {
        var calls = Il.Calls(Il.Method("PeopleOfFontainePower", "AfterCardPlayed"));
        Assert.Contains("CoopSet.IsAnotherPlayersAttack", calls);
        Assert.Contains("FurinaStage.Raise", calls);
        Assert.Contains("{PowerAmount:diff()}", Face(new ProtoFsPeopleOfFontaine()));
    }

    // ---- Kokomi ------------------------------------------------------------------

    [Fact]
    public void Joint_orders_remembers_its_player_and_a_dead_one_draws_nothing()
    {
        var kokomi = Seat.Kokomi();
        var furina = Seat.Furina();
        Table(new[] { kokomi.Creature, furina.Creature }, Enemy());
        Seat.Set(furina.Creature, "CombatId", (uint?)7u);

        // Two seats: "they" is the one other player, chosen by nobody.
        Assert.Same(furina.Creature, CoopSet.PlanAlly(kokomi.Creature));

        var clause = new KokomiPlan.Planned(
            KokomiPlan.Kind.AllyDraw, 2, KokomiPlan.Aim.Self,
            Targets: new List<string> { furina.Creature.CombatId.ToString()! });
        Assert.Same(furina.Creature, CoopSet.PlanAllyFor(kokomi.Creature, clause));

        Seat.Set(furina.Creature, "CurrentHp", 0);
        Assert.Null(CoopSet.PlanAllyFor(kokomi.Creature, clause));
        Assert.Null(CoopSet.PlanAllyFor(kokomi.Creature,
            clause with { Targets = new List<string>() }));
    }

    [Fact]
    public void Joint_orders_is_the_ally_or_the_jellyfish()
    {
        var card = new ProtoKkJointOrders();
        Assert.Contains(card.PlanClauses, c => c.Kind == KokomiPlan.Kind.AllyDraw
                                               && c.Amount == 2);
        var play = Il.Calls(Il.Method("ProtoKkJointOrders", "OnPlay"));
        Assert.Contains("KokomiPlan.PlayedOnPet", play);
        Assert.Contains("KokomiPlan.Schedule", play);
        Assert.Contains(play, c => c.StartsWith("CreatureCmd.GainBlock"));
        // The player is captured when the Plan is WRITTEN.
        Assert.Contains("CoopSet.PlanAlly",
            Il.Calls(Il.Method("KokomiPlan", "Schedule")));
    }

    [Fact]
    public void The_carry_outs_reach_the_other_players()
    {
        var resolve = Il.Calls(Il.Method("KokomiPlan", "ResolveOne"));
        Assert.Contains("CoopSet.PlanAllyFor", resolve);
        Assert.Contains("CardPileCmd.DrawWithoutBlockingOnOtherPlayers", resolve);
        Assert.Contains("CoopSet.OtherPlayers", resolve);

        var strike = new ProtoKkCoordinatedStrike();
        Assert.Contains(strike.PlanClauses,
            c => c.Kind == KokomiPlan.Kind.OthersAttackDamageThisTurn
                 && c.Amount == 3);
    }

    [Fact]
    public void Sangonomiyas_counsel_pays_each_other_player_on_every_plan()
    {
        var calls = Il.Calls(Il.Method("SangonomiyasCounselPower", "OnPlanResolved"));
        Assert.Contains("CoopSet.OtherPlayers", calls);
        Assert.Contains(calls, c => c.StartsWith("CreatureCmd.GainBlock"));
        Assert.DoesNotContain(calls, c => c.Contains("ClaimOncePerTurn"));
        Assert.True(typeof(IKokomiPlanListener).IsAssignableFrom(
            typeof(SangonomiyasCounselPower)));
    }

    // ---- helpers ---------------------------------------------------------------

    private sealed class StageArm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal StageArm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    /// <summary>A Guest of Honor on <paramref name="ally"/>, placed by
    /// <paramref name="furina"/>: the power's two backing fields, the way the
    /// harness seeds every power it cannot apply.</summary>
    private static GuestOfHonorPower Guest(Seat ally, Seat furina)
    {
        var power = (GuestOfHonorPower)RuntimeHelpers.GetUninitializedObject(
            typeof(GuestOfHonorPower));
        SetField(power, "_owner", ally.Creature);
        SetField(power, "_applier", furina.Creature);
        SetField(power, "_amount", 1);
        Seat.Set(power, "IsMutable", true);
        return power;
    }

    /// <summary>A creature on the ENEMY side. The harness's seats are players,
    /// and the co-op reads ask <c>IsEnemy</c>.</summary>
    private static Creature Enemy()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", CombatSide.Enemy);
        return body;
    }

    /// <summary>A real CombatState with these players on the player side and
    /// the enemies on the other, every creature pointed back at it.</summary>
    private static CombatState Table(Creature[] players, params Creature[] enemies)
    {
        var combat = ProtoBombs.Board(players[0], enemies);
        var allies = (List<Creature>)typeof(CombatState)
            .GetField("_allies", HeadlessGame.All)!.GetValue(combat)!;
        allies.AddRange(players);
        foreach (var p in players) p.CombatState = combat;
        return combat;
    }

    private static T Owned<T>(T card, Seat owner) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", owner.Player);
        return card;
    }

    private static CardPlay Play(CardModel card, Seat by) => new()
    {
        Card = card,
        Player = by.Player,
        Target = null,
        ResultPile = PileType.Discard,
        Resources = default,
        IsAutoPlay = false,
        PlayIndex = 0,
        PlayCount = 1,
    };

    private static void SetField(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }
        throw new InvalidOperationException($"{field} is gone");
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;
}
