using System;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using FurinaGen = KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME'S STARTER SEAM -- BOTH of her kit slots, and no other.
///
/// R254, ROUND 4 PICK 1 (2026-09-04) put a Fanfare reader on the first.
/// [USER], ruling <c>review/ruled/furina-reframe-round-4-2026-09-04.md</c>
/// sec.6: "maybe a reader in the starter deck? I still want to leave it at
/// just 2 'good' cards, but they can be stronger." So her two kit starters
/// stay two and ONE of them reads Fanfare -- <i>Aria of Recompense</i>, under
/// the arm only: "Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more."
///
/// THE BAR IS 3, NOT THE RIDERS' 6 (round 6 sec.4, 2026-09-04, a D default).
/// It was built at 6 -- the bar the four rider copies carry -- and three seat
/// runs played the card at Fanfare 3 with the 6 line never paying once,
/// because Aria is played BEFORE the stage performs and 3 is the Fanfare the
/// records show on an Aria turn. Both numbers are still lifted rather than
/// picked (the 5 is Aria's own printed Encore, the 3 is read off those runs),
/// so no number here was decided on this side of the wire; the four OFFERED
/// rider copies keep their own bars (6/6/8/10).
///
/// <c>EB-416</c> WIRED THE SECOND. The packet's sec.5 ruled that the starter
/// deploy NAMES its member, and slice 2 built the row that says so --
/// <c>ProtoFrSalonDebutNamed</c>, "Deploy Mademoiselle Crabaletta" -- with a
/// generated class, a pool entry and pins, and put it in NO starter in either
/// engine. The arm went on dealing the shipped Salon Début and its RANDOM
/// member, which under the manual leg decides for the player which member
/// their first Companion play makes perform. The row does not move; what is
/// new is that the seam hands it out.
///
/// WHAT IS PINNED, and it is what the sim pins as well
/// (<c>tier0/tests/test_furina_reframe_starter.py</c>): each kit slot is
/// swapped at one seam and each seam names both cards, Aria's copy pays 5
/// below the bar and 10 at it, and the named Début prints the member the
/// shipped card rolls for.
///
/// THE FIRST IS STRUCTURAL AND THE SECOND IS REAL, and the split is forced
/// rather than chosen. <c>Furina.StartingDeck</c> resolves every slot through
/// <c>ModelDb.Card&lt;T&gt;</c>, which throws until the game boots, so what
/// the deck HOLDS can only be read off the emitted calls -- the same seam
/// <c>KurageMemoryPinTests.The_starter_swap_happens_at_exactly_one_seam</c>
/// reads one character over. What the card DOES needs no model table at all,
/// so it is played.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype row's arithmetic,
/// not a number about a game.
/// </summary>
public class FurinaReframeStarterTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;

        internal Arm(bool master) { FurinaReframe.Enabled = master; }

        public void Dispose() { FurinaReframe.Enabled = _enabled; }
    }

    // ==================================================================
    // 1. WHICH CARD THE RUN IS DEALT -- one seam, both sides of the flag.
    // ==================================================================

    [Theory]
    [InlineData("StarterAria", "AriaOfRecompense")]
    [InlineData("StarterSalonDebut", "SalonDebut")]
    public void Each_kit_slot_is_swapped_at_exactly_one_seam(
        string seam, string shipped)
    {
        // ONE SEAM PER SLOT, so the mod and the sim cannot disagree about what
        // she opens with -- `loader._starter_ids` is the sim's, and these are
        // its twins. The authored deck reaching the seam at all is what makes
        // there be only one: if a second site ever swapped a starter card, the
        // getter would still be the only place this list is built.
        var getter = Il.CallSequence(Il.Method("Furina", "get_StartingDeck"));

        Assert.Contains("FurinaReframeRoster." + seam, getter);
        // And the slot is no longer filled unconditionally: a getter that still
        // named the shipped card directly would deal it under the arm too.
        Assert.DoesNotContain("ModelDb.Card<" + shipped + ">", getter);
    }

    [Theory]
    [InlineData("StarterAria", "ProtoFrAriaOfRecompense", "AriaOfRecompense")]
    [InlineData("StarterSalonDebut", "ProtoFrSalonDebutNamed", "SalonDebut")]
    public void A_seam_names_the_copy_and_the_shipped_card(
        string seam, string copy, string shipped)
    {
        // BOTH BRANCHES, read off the seam itself. With the arm off it is the
        // shipped card byte for byte -- the acceptance condition on the flag --
        // and with it on it is the copy. A seam that named only one of them
        // would be a swap that cannot be turned off, or one that never happens.
        var calls = Il.CallSequence(Il.Method("FurinaReframeRoster", seam));

        Assert.Contains("ModelDb.Card<" + copy + ">", calls);
        Assert.Contains("ModelDb.Card<" + shipped + ">", calls);
        Assert.Contains("FurinaReframe.get_Enabled", calls);
    }

    [Fact]
    public void The_swap_is_one_card_for_one_card()
    {
        // What keeps this a substitution rather than a starter rework: the deck
        // the getter builds is still TEN slots -- eight `ModelDb.Card<T>` sites
        // plus the two kit seams. Counted off the ORDERED read, which keeps the
        // three Soloist copies distinct; the set-valued `Calls` would fold them
        // and could not see a slot go missing.
        var getter = Il.CallSequence(Il.Method("Furina", "get_StartingDeck"));
        var slots = 0;
        foreach (var call in getter)
        {
            if (call.StartsWith("ModelDb.Card<", StringComparison.Ordinal)
                || call == "FurinaReframeRoster.StarterAria"
                || call == "FurinaReframeRoster.StarterSalonDebut")
            {
                slots++;
            }
        }

        Assert.Equal(10, slots);
        // The filler is untouched: the arm owns her two KIT slots and no other.
        Assert.Contains("ModelDb.Card<RegalBearing>", getter);
        Assert.Contains("ModelDb.Card<AnInvitation>", getter);
    }

    // ==================================================================
    // 2. WHAT THE COPY PAYS. The bar is 3; 2 is one under it.
    // ==================================================================

    [Theory]
    [InlineData(2, 5)]     // one under the bar: the shipped line alone
    [InlineData(3, 10)]    // at the bar: the shipped line and the reader
    public void The_copy_pays_the_reader_only_at_the_bar(int fanfare, int paid)
    {
        // REAL: the row's own `OnPlay`, on a seat whose meter is set to the
        // amount under test. `ReadableFanfare` is what the generated body
        // asks, and it is the clamped read -- so a seat with a debt gets the
        // base line and nothing more, which is the behaviour every other
        // Fanfare reader in this kit already has.
        using var _ = new Arm(master: true);
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(seat.Creature, fanfare);
        Assert.Equal(fanfare, FurinaResources.Fanfare(seat.Creature));

        Play(Held<ProtoFrAriaOfRecompense>(seat));

        Assert.Equal(paid, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_upgrade_gains_three_more_and_is_not_innate()
    {
        // `EB-550` (round 13, a D default). The upgrade WAS Innate, and Innate
        // is what defeated the reader it rides on: an Innate card is in the
        // opening hand, and on turn one Fanfare is always 0 because nothing has
        // performed yet, so the "at least 3 Fanfare" half was structurally dead
        // every fight across two lanes. The upgrade keeps its +3 Encore, which
        // is the half a player can spend, and drops the keyword.
        var card = new ProtoFrAriaOfRecompense();
        var upgraded = Upgraded<ProtoFrAriaOfRecompense>();

        Assert.DoesNotContain(CardKeyword.Innate, card.Keywords);
        Assert.DoesNotContain(CardKeyword.Innate, upgraded.Keywords);
    }

    [Theory]
    [InlineData(2, 8)]     // one under the bar: the upgraded shipped line
    [InlineData(3, 16)]    // at the bar: both lines at the upgraded number
    public void The_upgraded_copy_pays_three_more_on_each_line(int fanfare,
                                                              int paid)
    {
        // The other half of `EB-550`: what the upgrade still buys. 5 -> 8 on
        // the line every play pays, and the reader's line moves with it, so the
        // card that can now be drawn after a performance is worth drawing.
        using var _ = new Arm(master: true);
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(seat.Creature, fanfare);

        var card = Upgraded<ProtoFrAriaOfRecompense>();
        Seat.Set(card, "Owner", seat.Player);
        Play(card);

        Assert.Equal(paid, FurinaResources.Encore(seat.Creature));
    }

    // ==================================================================
    // 3. WHAT THE NAMED DEBUT DEPLOYS (`EB-416`).
    // ==================================================================

    [Fact]
    public void The_named_debut_names_its_member_and_the_shipped_one_rolls()
    {
        // THE DIFFERENCE THE PACKET'S sec.5 RULED, read where the player reads
        // it. Both rows resolve through the same `SalonMemberPower.Deploy`; the
        // copy passes `SalonMember.Crabaletta` where the shipped card passes
        // `null` and lets the deploy roll. That argument is an `ldc` and no IL
        // read can see it, so the FACE is what is pinned -- and the face is the
        // half that matters under the manual leg, where the front member is the
        // one a Companion play makes perform.
        Assert.Contains("Crabaletta", Face(new ProtoFrSalonDebutNamed()));
        Assert.DoesNotContain("random", Face(new ProtoFrSalonDebutNamed()));

        Assert.Contains("random", Face(new FurinaGen.SalonDebut()));
        Assert.DoesNotContain("Crabaletta", Face(new FurinaGen.SalonDebut()));
    }

    [Fact]
    public void Both_debuts_deploy_through_the_one_shared_verb()
    {
        // A COPY, NOT A SECOND RULE. The arm's row reaches the stage through
        // the same `Deploy` the shipped card uses -- so the deploy-performs
        // and full-stage-Evoke legs of the manual arm apply to it without
        // anything being wired twice.
        var copy = Il.Calls(Il.Method("ProtoFrSalonDebutNamed", "OnPlay"));
        var shipped = Il.Calls(Il.Method("SalonDebut", "OnPlay"));

        Assert.Contains("SalonMemberPower.Deploy", copy);
        Assert.Contains("SalonMemberPower.Deploy", shipped);
    }

    [Fact]
    public void The_shipped_card_never_reads_the_meter()
    {
        // The R130 veto stands where it was ruled ([USER], 2026-08-07: the
        // starter gets no payoff). R254 moves a PROTOTYPE arm rather than
        // reversing it, so the shipped row still gains 5 off a full meter --
        // and its body does not ask the meter at all.
        var calls = Il.Calls(Il.Method("AriaOfRecompense", "OnPlay"));

        Assert.Contains("FurinaResources.GainEncore", calls);
        Assert.DoesNotContain("FurinaResources.ReadableFanfare", calls);
    }

    [Fact]
    public void The_copy_reads_the_meter_through_the_clamped_reader()
    {
        // ONE READER FOR THE WHOLE KIT. `ReadableFanfare` clamps at zero, so a
        // seat carrying a Fanfare debt (Track C.2 leaves one on purpose) gets
        // the base line and nothing worse -- the same door every other Fanfare
        // gate in this mod goes through. A row that read the raw field would
        // be a second rule about the same meter.
        var calls = Il.Calls(Il.Method("ProtoFrAriaOfRecompense", "OnPlay"));

        Assert.Contains("FurinaResources.ReadableFanfare", calls);
        Assert.Contains("FurinaResources.GainEncore", calls);
    }

    // ==================================================================
    // Fixtures.
    // ==================================================================

    /// <summary>Upgrade a card the way the campfire does. Lifted from
    /// <c>HexereiReaderTests.Upgraded</c>, for its reason: `UpgradeInternal`
    /// raises the level, calls the card's own `OnUpgrade` and finalizes each
    /// DynamicVar's preview, so a keyword the upgrade adds is on the card
    /// afterwards exactly as a player would find it.</summary>
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    /// <summary>The printed description, which is what the player reads.
    /// Lifted from <c>KleeOverhaulRoundThreeTests.Face</c>.</summary>
    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>A card in a seat's hand: mutable, owned, and therefore
    /// playable. `IsMutable` first -- Owner's setter calls AssertMutable.
    /// Lifted from <c>FurinaReframeSliceTwoTests.Held</c>.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The row's own `OnPlay`, awaited.
    ///
    /// Reflective because the method is `protected`: a generated card's play
    /// body is not public API, and the alternative -- restating the two
    /// `GainEncore` calls here -- would assert this file's arithmetic rather
    /// than the card's. Neither parameter is touched by this row, so both are
    /// passed as their defaults.</summary>
    private static void Play(CardModel card)
    {
        var play = card.GetType()
            .GetMethod("OnPlay", HeadlessGame.All)!;
        var task = (Task)play.Invoke(card, new object?[] { null, null })!;
        task.GetAwaiter().GetResult();
    }
}
