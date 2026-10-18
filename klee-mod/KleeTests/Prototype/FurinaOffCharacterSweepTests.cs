using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S CARDS ON ANYONE (the off-character fix, 2026-10-18), on the base
/// game's Orbs and Osty precedent: the first Channel grants a Defect slot to a
/// character with none, and Osty is summoned if absent. Her cards reach other
/// characters through Kaleidoscope, Prismatic Gem, Sea Glass, Splash and a
/// co-op partner's Imitation Learning. Before this fix, every Stage verb
/// returned early unless the player WAS Furina: a Guest Star cost 1 Energy and
/// did nothing, and seven Drain-priced cards could never be played.
///
/// Every card of her kit (her pool, her Guest Stars, her Ancients) is swept
/// here as if an IRONCLAD held it: its face reads the same as on her, its
/// gate answers the same at every Fanfare bank and HP, and no identity test
/// sits on its play closure except the named by-design sites. The verbs
/// themselves bring the player's own Stage up (<see cref="FurinaStage.Ensure"/>).
/// </summary>
public class FurinaOffCharacterSweepTests
{
    internal static IReadOnlyList<Type> KitCards() =>
        OffCharacterSweep.Cards("ProtoFs",
            typeof(global::KleeMod.Cards.Furina.CenterOfAttention),
            typeof(global::KleeMod.Cards.Furina.AllTheWorldsAStage));

    // The interface only: the byte scan (Il.TypesTested's caveat) reads a
    // `leave` operand in FurinaStagePets.Field as a cast to the Furina class.
    private static readonly Type[] Identity = { typeof(IFurinaCharacter) };

    private static readonly MethodBase IsFurina =
        typeof(FurinaResources).GetMethod(nameof(FurinaResources.IsFurina))!;

    private static Seat Ironclad(int hp = 80) => Seat.Of(new Ironclad(), hp);

    private static Seat Furina(int hp = 80) => Seat.Furina(hp);

    /// <summary>The seven cards whose fixed price is a Drain.</summary>
    private static readonly string[] DrainPriced =
    {
        nameof(ProtoFsAllIn), nameof(ProtoFsEbbAndFlow),
        nameof(ProtoFsGrandDeluge), nameof(ProtoFsMademoiselleCrabaletta),
        nameof(ProtoFsOusiaPledge), nameof(ProtoFsRiptideLunge),
        nameof(ProtoFsUndercurrent),
    };

    [Fact]
    public void The_sweep_covers_the_whole_kit()
    {
        var kit = KitCards().Select(t => t.Name).ToList();
        Assert.True(kit.Count >= 80, $"only {kit.Count} kit cards found");
        Assert.Contains(nameof(ProtoFsGuestStarCharlotte), kit);
        Assert.Contains(nameof(ProtoFsAllIn), kit);
        Assert.Contains("AllTheWorldsAStage", kit);
    }

    // --- the play: no Furina identity on any card's closure ---------------

    /// <summary>The sites that MAY ask "is this Furina", and why each is
    /// hers by design rather than a card reading Furina-only state.</summary>
    private static readonly Dictionary<string, string> ByDesign = new()
    {
        ["FurinaResources.IsFurina"] = "the identity predicate itself",
        // Her Stage is up from the start of every combat; anyone else's
        // from their first Stage verb or Furina card (Ensure). The verbs do
        // not ask it: see Every_stage_verb_brings_the_players_stage_up.
        ["FurinaStage.LiveFor"] = "the always-up half: her Stage from turn one",
        // Her relics are hers: their effects count on her Stage only.
        ["FurinaStage.ModsOf"] = "relic effects: her relics count on her only",
        ["FurinaStage.SingerOf"] = "her starter relic, Salon Solitaire",
        ["FurinaStageRelics.Count"] = "relic effects: her relics count on her only",
        // The Fanfare badge is up from turn one on her; anyone else's goes
        // up on their first Fanfare, as the base game's Star counter does.
        ["FurinaStage.InstallBadge"] = "display: her badge from turn one",
        ["FurinaStage.ShowBadge"] = "display: anyone else's badge on first gain",
        ["FanfareCounter.AppliesTo"] = "display: her gauge is always shown",
        // Random Companions come from the OWNER's personal pool (Klee's
        // sweep allows the same two).
        ["CompanionPool.CharacterId"] = "companion personal pool of the owner",
        ["CompanionPool.HomeNation"] = "companion nation of the owner",
        ["DrainedCounter.AppliesTo"] = "display: her counter is always shown",
    };

    [Fact]
    public void No_kit_card_reads_furina_identity_when_played()
    {
        var findings = OffCharacterSweep.Unexpected(KitCards(), Identity, IsFurina, ByDesign);
        Assert.True(findings.Count == 0,
            "Furina identity read on a kit card's closure:\n  "
            + string.Join("\n  ", findings));
    }

    [Fact]
    public void The_closure_walk_bites()
    {
        var hits = OffCharacterSweep.IdentityReads(typeof(ProtoFsAllIn), Identity, IsFurina)
            .Select(h => h.Site).ToList();
        Assert.Contains("FurinaStage.LiveFor", hits);
        Assert.Contains("FurinaResources.IsFurina", hits);
    }

    /// <summary>The verbs a card calls, each of which must bring the
    /// player's Stage up rather than ask who the player is.</summary>
    private static readonly string[] Verbs =
    {
        nameof(FurinaStage.Gain), nameof(FurinaStage.Spend),
        nameof(FurinaStage.SpendUpTo), nameof(FurinaStage.SpendAll),
        nameof(FurinaStage.Drain), nameof(FurinaStage.Repay),
        nameof(FurinaStage.RepayAll), nameof(FurinaStage.ActEachTwice),
        nameof(FurinaStage.EnergyNextTurn), nameof(FurinaStage.GuestStar),
        nameof(FurinaStage.ActOldest), nameof(FurinaStage.ActAll),
        nameof(FurinaStage.FinalBow), nameof(FurinaStage.SummonRandom),
    };

    [Fact]
    public void Every_stage_verb_brings_the_players_stage_up()
    {
        foreach (var verb in Verbs)
        {
            var calls = Il.Calls(typeof(FurinaStage).GetMethod(verb)!);
            Assert.True(calls.Contains("FurinaStage.Ensure"),
                        $"FurinaStage.{verb} does not bring the Stage up");
            Assert.False(calls.Contains("FurinaStage.LiveFor"),
                         $"FurinaStage.{verb} asks whose Stage it is");
        }
        // SpendHalf rides SpendUpToCap, which SpendUpTo calls after Ensure.
        Assert.Contains("FurinaStage.SpendUpToCap",
                        Il.Calls(typeof(FurinaStage).GetMethod(nameof(FurinaStage.SpendHalf))!));
        // A Furina card brings its player's Stage up as it is played.
        Assert.Contains("FurinaStage.StartOnPlay",
                        Il.Calls(Il.Method("FurinaStageHooks", "BeforeCardPlayed")));
    }

    [Fact]
    public void Every_kit_card_is_one_of_hers()
    {
        // StartOnPlay reads the card's roster id: a kit card without it
        // would not bring the Stage up and its Powers would sit blank.
        foreach (var type in KitCards())
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.True(FurinaStage.IsFurinaCard(card), $"{type.Name} is not a Furina card");
        }
        Assert.False(FurinaStage.IsFurinaCard(new ProtoKoKapow()));
    }

    // --- the face: every variable resolves, and reads the same ------------

    [Fact]
    public void Every_face_resolves_and_reads_the_same_on_an_ironclad()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            var problems = OffCharacterSweep.FaceProblems(
                KitCards(), () => Ironclad(), () => Furina());
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    // --- the price: any owner's Fanfare and HP pay it ---------------------

    private static Seat Banked(Seat seat, int fanfare)
    {
        if (fanfare > 0) FurinaStageLedger.For(seat.Creature).Gain(fanfare);
        return seat;
    }

    [Fact]
    public void Every_playability_gate_answers_the_same_for_an_ironclad()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            var problems = new List<string>();
            var gated = 0;
            foreach (var type in KitCards())
            {
                if (!OffCharacterSweep.Gated(type)) continue;
                gated++;
                foreach (var hp in new[] { 80, 6, 2 })
                {
                    foreach (var bank in new[] { 0, 1, 4, 10, 20 })
                    {
                        var off = OffCharacterSweep.Ask(OffCharacterSweep.HeldBy(
                            type, Banked(Ironclad(hp), bank)));
                        var on = OffCharacterSweep.Ask(OffCharacterSweep.HeldBy(
                            type, Banked(Furina(hp), bank)));
                        if (off != on)
                        {
                            problems.Add($"{type.Name} at {hp} HP, {bank} Fanfare: Furina {on}, Ironclad {off}");
                        }
                    }
                }
            }
            Assert.True(gated >= DrainPriced.Length, $"only {gated} gated kit cards found");
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    [Fact]
    public void The_seven_drain_priced_cards_are_playable_off_furina()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            foreach (var name in DrainPriced)
            {
                var type = OffCharacterSweep.Mod.GetType(
                    "KleeMod.Cards.Prototype.Generated." + name)!;
                Assert.Contains("FurinaStage.CanDrain", Il.Calls(Il.Method(name, "get_IsPlayable")));
                Assert.Equal("True", OffCharacterSweep.Ask(
                    OffCharacterSweep.HeldBy(type, Ironclad())));
                // Never to 0 HP, on anyone.
                Assert.Equal("False", OffCharacterSweep.Ask(
                    OffCharacterSweep.HeldBy(type, Ironclad(1))));
            }
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    [Theory]
    [InlineData(44)]
    [InlineData(55)]
    public void Ousia_pledge_drains_3_in_a_yae_deck(int hp)
    {
        // Yae round 7, lane 1: Ousia Pledge+ in a Yae deck was refused "it
        // would take you to 0 HP" at 44 to 55 HP with Drain 3. Fixed by the
        // off-character fix (2026-10-18); this pins it.
        FurinaStageLedger.ResetAll();
        try
        {
            var card = OffCharacterSweep.HeldBy(typeof(ProtoFsOusiaPledge), Seat.Yae(hp));
            Assert.Equal("True", OffCharacterSweep.Ask(card));
            Assert.Null(((ProtoFsOusiaPledge)card).UnplayableReason);
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    // --- the Stage itself: anyone's, from first use, and their own --------

    [Fact]
    public void An_ironclads_stage_comes_up_on_first_use_and_is_its_own()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            var context = new ThrowingPlayerChoiceContext();
            var ironclad = Ironclad().WithCombatState().Creature;
            var partner = Ironclad().WithCombatState().Creature;

            // Reading never brings it up: a fresh Stage, as on Furina.
            Assert.False(FurinaStage.LiveFor(ironclad));
            Assert.Equal(0, FurinaStage.FanfareOf(ironclad));
            Assert.Equal(FurinaStage.LineOf(Furina().Creature),
                         FurinaStage.LineOf(ironclad));

            // A verb does: the Fanfare lands on the Ironclad's own Stage.
            Assert.Equal(4, StageKit.Run(FurinaStage.Gain(context, ironclad, 4)));
            Assert.True(FurinaStage.LiveFor(ironclad));
            Assert.Equal(4, FurinaStage.FanfareOf(ironclad));
            Assert.True(FurinaStage.CanSpend(ironclad, 4));
            Assert.False(FurinaStage.LiveFor(partner));
            Assert.Equal(0, FurinaStage.FanfareOf(partner));

            // So does playing one of her cards (Ensure, from the play hook).
            var held = OffCharacterSweep.HeldBy(typeof(ProtoFsGuestStarCharlotte),
                                                Ironclad().WithCombatState());
            var owner = held.Owner!.Creature;
            Assert.False(FurinaStage.LiveFor(owner));
            FurinaStage.StartOnPlay(held);
            Assert.True(FurinaStage.LiveFor(owner));
            // Anyone else's card does not.
            var klee = OffCharacterSweep.HeldBy(typeof(ProtoKoKapow),
                                                Ironclad().WithCombatState());
            FurinaStage.StartOnPlay(klee);
            Assert.False(FurinaStage.LiveFor(klee.Owner!.Creature));
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    [Fact]
    public void Her_relics_and_her_singer_stay_hers()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            // An Ironclad holding Salon Solitaire, Stage up, Repays nothing at
            // the end of the turn: the starter relic is Furina's.
            var seat = Ironclad().WithCombatState()
                .WithRelic<global::KleeMod.Relics.SalonSolitaire>();
            FurinaStage.Ensure(seat.Creature);
            Assert.True(FurinaStage.LiveFor(seat.Creature));
            Assert.Equal(0, FurinaStage.SingerOf(seat.Creature));
            Assert.Equal(FurinaStageLaw.SingerRepay, FurinaStage.SingerOf(
                Furina().WithRelic<global::KleeMod.Relics.SalonSolitaire>().Creature));
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    [Fact]
    public void Her_gauges_show_from_turn_one_on_her_and_from_first_gain_on_anyone()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            Assert.True(global::KleeMod.Vfx.FanfareCounter.ShowsFor(Furina().Creature));
            Assert.True(global::KleeMod.Vfx.DrainedCounter.ShowsFor(Furina().Creature));

            var ironclad = Ironclad().WithCombatState().Creature;
            Assert.False(global::KleeMod.Vfx.FanfareCounter.ShowsFor(ironclad));
            FurinaStage.Ensure(ironclad);
            // Up, but nothing gained yet: still no gauge.
            Assert.False(global::KleeMod.Vfx.FanfareCounter.ShowsFor(ironclad));
            Assert.False(global::KleeMod.Vfx.DrainedCounter.ShowsFor(ironclad));
            FurinaStageLedger.For(ironclad).Gain(2);
            Assert.True(global::KleeMod.Vfx.FanfareCounter.ShowsFor(ironclad));
            Assert.False(global::KleeMod.Vfx.DrainedCounter.ShowsFor(ironclad));
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }
}
