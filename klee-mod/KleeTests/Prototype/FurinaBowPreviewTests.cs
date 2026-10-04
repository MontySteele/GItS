using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Models;
using Xunit;
using static KleeMod.Powers.StagePerformer;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// WHO A SUMMON WILL BOW, ON THE CARD (2026-10-04, the Furina v2 seat round:
/// three summons onto a full stage Bowed Usher off without the player
/// noticing). A summon card's in-combat line names who will Bow; these pins
/// hold that the line names EXACTLY the performers the summon then Bows, in
/// order, for every overflow case -- the preview is planned off the same
/// rule (<see cref="StageDirector.SalonRoom"/>,
/// <see cref="StageDirector.GuestRoom"/>) and then the summon is run for real
/// on the same stage.
/// </summary>
public class FurinaBowPreviewTests
{
    private static StageSummonStep S(StagePerformer? who) =>
        StageSummonStep.Salon(who);

    private static StageSummonStep G(StagePerformer who) =>
        StageSummonStep.GuestStar(who);

    private static readonly StageSummonStep[] Gala =
        { S(Usher), S(Chevalmarin), S(Crabaletta) };

    public static TheoryData<string, StagePerformer[], StageSummonStep[], string>
        Overflow() => new()
    {
        // A Salon summon onto a full stage: the front-most Salon member.
        { "salon, all Salon", new[] { Usher, Chevalmarin, Crabaletta },
          new[] { S(Crabaletta) }, "\n(Usher will Bow)" },
        { "salon, guest in front", new[] { Neuvillette, Chevalmarin, Usher },
          new[] { S(Usher) }, "\n(Chevalmarin will Bow)" },
        { "salon, Salon at the back", new[] { Neuvillette, Clorinde, Usher },
          new[] { S(Chevalmarin) }, "\n(Usher will Bow)" },
        // A Salon summon onto a stage of guests: the walk-on.
        { "salon, walk-on", new[] { Navia, Clorinde, Charlotte },
          new[] { S(Usher) }, "\n(Walk-on: acts once and Bows)" },
        // A Guest Star onto a full stage: the front-most Salon member, else
        // the front guest.
        { "guest, mixed stage", new[] { Navia, Usher, Clorinde },
          new[] { G(Charlotte) }, "\n(Usher will Bow)" },
        { "guest, three guests", new[] { Navia, Clorinde, Charlotte },
          new[] { G(Neuvillette) }, "\n(Navia will Bow)" },
        // A repeat copy: the guest already on stage Bows and stays.
        { "guest, repeat", new[] { Usher, Clorinde },
          new[] { G(Clorinde) }, "\n(Clorinde will Bow and stay)" },
        { "guest, repeat on a full stage",
          new[] { Usher, Clorinde, Navia },
          new[] { G(Navia) }, "\n(Navia will Bow and stay)" },
        // Gala Premiere: everyone it pushes off, in order -- each newcomer
        // takes the back seat, so a later summon may Bow an earlier one.
        { "gala, full Salon", new[] { Usher, Chevalmarin, Crabaletta }, Gala,
          "\n(Usher, Chevalmarin and Crabaletta will Bow)" },
        { "gala, guests keep their seats", new[] { Clorinde, Usher, Navia },
          Gala, "\n(Usher, Usher and Chevalmarin will Bow)" },
        { "gala, fills then overflows", new[] { Clorinde }, Gala,
          "\n(Usher will Bow)" },
        { "gala, three guests", new[] { Navia, Clorinde, Charlotte }, Gala,
          "\n(Walk-on: each acts once and Bows)" },
        // Room to spare: no line at all.
        { "salon, free seat", new[] { Usher }, new[] { S(Crabaletta) }, "" },
        { "guest, free seat", new[] { Usher, Navia }, new[] { G(Clorinde) },
          "" },
    };

    [Theory]
    [MemberData(nameof(Overflow))]
    public void The_preview_names_exactly_who_the_summon_bows(
        string name, StagePerformer[] stage, StageSummonStep[] steps,
        string line)
    {
        var kit = StageKit.Of(stage);
        var plan = StageDirector.PlanSummons(kit.Stage, steps);
        Assert.Equal(line, FurinaStageBowPreview.For(kit.Stage, steps));

        foreach (var step in steps)
        {
            if (step.Guest) StageKit.Run(kit.Director.SummonGuest(step.Who!.Value, 0));
            else StageKit.Run(kit.Director.SummonSalon(step.Who!.Value));
        }
        var bowed = kit.Stage.Beats
            .Where(b => b.Event == FurinaStageLedger.BowEvent)
            .Select(b => (StagePerformer?)b.Who)
            .ToList();
        Assert.True(plan.Select(b => b.Who).SequenceEqual(bowed),
                    $"{name}: planned [{string.Join(", ", plan.Select(b => b.Who))}]"
                    + $" but Bowed [{string.Join(", ", bowed)}]");
    }

    [Fact]
    public void The_plan_kind_matches_what_the_summon_reports()
    {
        foreach (var (stage, step) in new (StagePerformer[], StageSummonStep)[]
                 {
                     (new[] { Usher, Chevalmarin, Crabaletta }, S(Usher)),
                     (new[] { Navia, Clorinde, Charlotte }, S(Usher)),
                     (new[] { Navia, Clorinde, Charlotte }, G(Lyney)),
                     (new[] { Navia, Clorinde }, G(Clorinde)),
                 })
        {
            var kit = StageKit.Of(stage);
            var planned = StageDirector.PlanSummons(kit.Stage, new[] { step })
                .Single().Kind;
            var result = step.Guest
                ? StageKit.Run(kit.Director.SummonGuest(step.Who!.Value, 0))
                : StageKit.Run(kit.Director.SummonSalon(step.Who!.Value));
            Assert.Equal(result, planned);
        }
    }

    [Theory]
    [InlineData(Usher)]
    [InlineData(Chevalmarin)]
    [InlineData(Crabaletta)]
    public void A_random_summon_names_the_performer_whatever_it_rolls(
        StagePerformer rolled)
    {
        // Take the Stage: the member is rolled at play, but who makes room
        // is not -- the front-most Salon member.
        var kit = StageKit.Of(Neuvillette, Chevalmarin, Usher);
        var random = new[] { S(null) };
        Assert.Equal("\n(Chevalmarin will Bow)",
                     FurinaStageBowPreview.For(kit.Stage, random));
        StageKit.Run(kit.Director.SummonSalon(rolled));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent, Chevalmarin));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent));
    }

    [Fact]
    public void A_random_walk_on_names_nobody()
    {
        var kit = StageKit.Of(Navia, Clorinde, Charlotte);
        Assert.Equal("\n(Walk-on: acts once and Bows)",
                     FurinaStageBowPreview.For(kit.Stage, new[] { S(null) }));
    }

    [Fact]
    public void Sold_out_seats_four_so_a_fourth_summon_bows_nobody()
    {
        var kit = StageKit.With(new StageMods { Capacity = 4 }, 0,
                                Usher, Chevalmarin, Crabaletta);
        Assert.Equal("", FurinaStageBowPreview.For(kit.Stage,
                                                   new[] { S(Usher) }));
        StageKit.Run(kit.Director.SummonSalon(Usher));
        Assert.Equal(0, kit.Beats(FurinaStageLedger.BowEvent));
    }

    // ---- the faces ---------------------------------------------------------

    public static TheoryData<string> SummonCards() => new()
    {
        nameof(ProtoFsSalonDebut), nameof(ProtoFsLeadingLady),
        nameof(ProtoFsSurintendanteChevalmarin),
        nameof(ProtoFsMademoiselleCrabaletta), nameof(ProtoFsGalaPremiere),
        nameof(ProtoFsGuestStarNeuvillette), nameof(ProtoFsGuestStarClorinde),
        nameof(ProtoFsGuestStarNavia), nameof(ProtoFsGuestStarChevreuse),
        nameof(ProtoFsGuestStarWriothesley), nameof(ProtoFsGuestStarSigewinne),
        nameof(ProtoFsGuestStarCharlotte), nameof(ProtoFsGuestStarLynette),
        nameof(ProtoFsGuestStarLyney), nameof(ProtoFsGuestStarEscoffier),
    };

    private static BaseLib.Abstracts.CustomCardModel Card(string type) =>
        (BaseLib.Abstracts.CustomCardModel)System.Activator.CreateInstance(
            typeof(ProtoFsGalaPremiere).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + type)!)!;

    [Theory]
    [MemberData(nameof(SummonCards))]
    public void Every_summon_card_face_carries_the_bow_line(string type)
    {
        var card = Card(type);
        var face = card.Localization!.Single(r => r.Item1 == "description").Item2;
        Assert.EndsWith("{InCombat:{" + FurinaStageBowPreview.Token + "}|}",
                        face);
        // Off a combat (a canonical card has no owner) the line is empty.
        Assert.Equal("", FurinaStageBowPreview.Salon(card, "usher"));
    }

    [Fact]
    public void Improvised_number_carries_no_bow_line()
    {
        // It summons only when no one is on stage, so nobody can Bow.
        var face = new ProtoFsImprovisedNumber().Localization!
            .Single(r => r.Item1 == "description").Item2;
        Assert.DoesNotContain(FurinaStageBowPreview.Token, face);
    }
}
