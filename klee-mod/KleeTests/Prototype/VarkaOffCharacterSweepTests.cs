using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA'S CARDS ON ANYONE (the off-character fix, 2026-10-18), on the base
/// game's Orbs precedent: the Defect's first Channel grants a slot to a
/// character with none. His cards reach other characters through
/// Kaleidoscope, Prismatic Gem, Sea Glass, Splash and a co-op partner's
/// Imitation Learning. Before this fix the Oath was kept only for Varka: his
/// cards played at their base numbers anywhere else, a Knight set no
/// element, and his Oath Powers were blank.
///
/// Every card of his kit (his pool, his Knights, his Ancients) is swept here
/// as if an IRONCLAD held it: its face reads the same as on him, and no
/// identity test sits on its play closure except the named by-design sites.
/// The first Varka card a player plays starts that player's own Oath
/// (<see cref="VarkaOath.Start"/>, from <see cref="VarkaOath.BeginPlay"/>).
/// </summary>
public class VarkaOffCharacterSweepTests
{
    internal static IReadOnlyList<Type> KitCards() =>
        OffCharacterSweep.Cards("ProtoVk",
            typeof(global::KleeMod.Cards.Varka.AllFourWinds),
            typeof(global::KleeMod.Cards.Varka.DandelionGale));

    private static readonly Type[] Identity = { typeof(IVarkaCharacter) };

    private static readonly MethodBase IsVarka =
        typeof(VarkaPrototype).GetMethod(nameof(VarkaPrototype.IsVarka))!;

    private static Seat Ironclad() => Seat.Of(new Ironclad());

    [Fact]
    public void The_sweep_covers_the_whole_kit()
    {
        var kit = KitCards().Select(t => t.Name).ToList();
        Assert.True(kit.Count >= 85, $"only {kit.Count} kit cards found");
        Assert.Contains(nameof(ProtoVkAmberBaronBunny), kit);
        Assert.Contains(nameof(ProtoVkWindwardFlank), kit);
        Assert.Contains("AllFourWinds", kit);
    }

    [Fact]
    public void Every_kit_card_is_one_of_his()
    {
        // BeginPlay starts the Oath off the card's roster id or its Knight
        // pool: a kit card with neither would leave its Powers blank.
        foreach (var type in KitCards())
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.True(VarkaOath.IsVarkaCard(card), $"{type.Name} is not a Varka card");
        }
        Assert.False(VarkaOath.IsVarkaCard(new ProtoKoKapow()));
    }

    // --- the play: no Varka identity on any card's closure ----------------

    /// <summary>The sites that MAY ask "is this Varka", and why each is his
    /// by design rather than a card reading Varka-only state.</summary>
    private static readonly Dictionary<string, string> ByDesign = new()
    {
        ["VarkaPrototype.IsVarka"] = "the identity predicate itself",
        // His Oath is kept from the start of every combat; anyone else's
        // from the first Varka card they play (Start, from BeginPlay).
        ["VarkaOath.Live"] = "the always-kept half: his Oath from turn one",
        // His relics are his: Banner of the West Wind, Windblume Garland and
        // the rest count on him only.
        ["VarkaArmRelics.Held"] = "relic effects: his relics count on him only",
        ["VarkaArmRelics.FirstTurnOf"] = "relic effects: his relics count on him only",
        // Boreas's Fang is his starter relic: its Knight slot and its turn
        // hooks are his.
        ["BoreasFang.OffersCompanionTo"] = "his starter relic, Boreas's Fang",
        // The dial is always shown for him; anyone else's appears on their
        // first Oath or current element.
        ["VarkaOathDial.AppliesTo"] = "display: his dial is always shown",
        // Random Companions come from the OWNER's personal pool.
        ["CompanionPool.CharacterId"] = "companion personal pool of the owner",
        ["CompanionPool.HomeNation"] = "companion nation of the owner",
    };

    [Fact]
    public void No_kit_card_reads_varka_identity_when_played()
    {
        var findings = OffCharacterSweep.Unexpected(KitCards(), Identity, IsVarka, ByDesign);
        Assert.True(findings.Count == 0,
            "Varka identity read on a kit card's closure:\n  "
            + string.Join("\n  ", findings));
    }

    [Fact]
    public void The_closure_walk_bites()
    {
        var hits = OffCharacterSweep.IdentityReads(typeof(ProtoVkAmberBaronBunny), Identity, IsVarka)
            .Select(h => h.Site).ToList();
        Assert.Contains("VarkaOath.Live", hits);
        Assert.Contains("VarkaPrototype.IsVarka", hits);
    }

    // --- the face: every variable reads the same --------------------------

    [Fact]
    public void Every_face_reads_the_same_on_an_ironclad()
    {
        VarkaOathLedger.ResetAll();
        try
        {
            var problems = OffCharacterSweep.FaceProblems(
                KitCards(), Ironclad, () => Seat.Varka());
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            VarkaOathLedger.ResetAll();
        }
    }

    [Fact]
    public void No_kit_card_has_a_gate_of_its_own()
    {
        // Varka's prices are Energy only, so every card is playable on anyone
        // who can pay it. A card that grows its own gate needs the sweep's
        // gate comparison (Furina's has one).
        var gated = KitCards().Where(OffCharacterSweep.Gated).Select(t => t.Name).ToList();
        Assert.True(gated.Count == 0, "gated: " + string.Join(", ", gated));
    }

    // --- the Oath itself: anyone's, from first use, and their own ---------

    [Fact]
    public void A_knight_starts_an_ironclads_oath_and_sets_its_element()
    {
        VarkaOathLedger.ResetAll();
        try
        {
            var knight = OffCharacterSweep.HeldBy(typeof(ProtoVkAmberBaronBunny),
                                                  Ironclad().WithCombatState());
            var ironclad = knight.Owner!.Creature;
            Assert.False(VarkaOath.Live(ironclad));

            StageKit.Run(VarkaOath.BeginPlay(knight));
            Assert.True(VarkaOath.Live(ironclad));
            Assert.Equal(Element.Pyro, VarkaOath.Current(ironclad));
            Assert.Equal(1, VarkaOath.KnightsPlayedThisTurn(ironclad));

            // An element the Ironclad applies inside the play credits Oath.
            StageKit.Run(VarkaOath.NoteApplication(
                new ThrowingPlayerChoiceContext(), ironclad, Element.Pyro));
            Assert.Equal(1, VarkaOath.Count(ironclad, Element.Pyro));
            Assert.Equal(1, VarkaOath.CurrentOath(ironclad));

            // A partner's Oath is their own.
            var partner = Ironclad().WithCombatState().Creature;
            Assert.False(VarkaOath.Live(partner));
            Assert.Equal(0, VarkaOath.Count(partner, Element.Pyro));
        }
        finally
        {
            VarkaOathLedger.ResetAll();
        }
    }

    [Fact]
    public void Anyone_elses_card_starts_no_oath()
    {
        VarkaOathLedger.ResetAll();
        try
        {
            var kapow = OffCharacterSweep.HeldBy(typeof(ProtoKoKapow),
                                                 Ironclad().WithCombatState());
            var ironclad = kapow.Owner!.Creature;
            StageKit.Run(VarkaOath.BeginPlay(kapow));
            Assert.False(VarkaOath.Live(ironclad));
            StageKit.Run(VarkaOath.NoteApplication(
                new ThrowingPlayerChoiceContext(), ironclad, Element.Pyro));
            Assert.Equal(0, VarkaOath.Count(ironclad, Element.Pyro));
        }
        finally
        {
            VarkaOathLedger.ResetAll();
        }
    }

    [Fact]
    public void The_dial_shows_from_turn_one_on_him_and_from_first_oath_on_anyone()
    {
        VarkaOathLedger.ResetAll();
        try
        {
            Assert.True(global::KleeMod.Vfx.VarkaOathDial.ShowsFor(Seat.Varka().Creature));
            var ironclad = Ironclad().WithCombatState().Creature;
            Assert.False(global::KleeMod.Vfx.VarkaOathDial.ShowsFor(ironclad));
            VarkaOath.Start(ironclad);
            Assert.False(global::KleeMod.Vfx.VarkaOathDial.ShowsFor(ironclad));
            VarkaOathLedger.For(ironclad).Add(Element.Cryo, 2);
            Assert.True(global::KleeMod.Vfx.VarkaOathDial.ShowsFor(ironclad));
        }
        finally
        {
            VarkaOathLedger.ResetAll();
        }
    }
}
