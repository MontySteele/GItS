using System;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA ROUND 9, the rows filed against words the board did not carry: a
/// rule a seat could only find by running the experiment twice, and a half of
/// a card that went missing in silence.
/// </summary>
public class FurinaRoundNineTests
{
    /// <summary>Turn the reframe's MANUAL leg on for one test and put every
    /// flag back after it -- `FurinaReframeRoundSevenTests.Arm` verbatim, and
    /// for its reason: the six flags are process-global statics.</summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
            FurinaReframe.EvokeEnabled = false;
            FurinaReframe.MeterEnabled = false;
            FurinaReframe.SpotlightEnabled = false;
            FurinaReframe.BurstEnabled = false;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
            FurinaReframe.BurstEnabled = _burst;
        }
    }

    // ==================================================================
    // `EB-475` -- three words that gated decisions and defined nothing
    // ==================================================================
    //
    // THE FIND (Furina r9 (c) 2). "'If you moved the Spotlight this turn'
    // gates Director's Cut and Take It From the Top, and nothing ever defines
    // what moving the Spotlight is... I passed on both cards purely because I
    // could not tell whether I could turn the condition on." "'Guest Stars'
    // appears inside Blocking Notes' scaling clause" undefined. And "'Take
    // Your Bow -- The leftmost member of your Salon takes their bow' was
    // offered as a card reward with no keyword, no number, and no glossary
    // line... I declined a 0-cost card because I could not read it."
    //
    // TWO ARE DERIVED FROM THE PRINTED FACE (`gen_klee_cards`
    // `prints_spotlight_move` / `prints_takes_bow`), so a row that prints
    // either phrase carries the definition because it printed it. The third
    // is not on any face -- it is in `CompanionBody`'s own clause -- so it
    // rides the tip that prints the word.

    /// <summary>The tip bodies a card yields, off the compiled attach: the
    /// same reason `Round15Tests.Printed` reads `ldstr` rather than
    /// enumerating -- a `HoverTip` title formats through `LocManager`, null
    /// headless.</summary>
    private static string Attached(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method,
            System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.NonPublic
            | System.Reflection.BindingFlags.Static)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    [Fact]
    public void Every_face_gating_on_the_spotlight_move_carries_its_definition()
    {
        foreach (var card in new[] { "CurtainCue", "DirectorsCut",
                                     "TakeItFromTheTop" })
        {
            var tips = Il.Calls(Il.Method(card, "get_ExtraHoverTips"));
            Assert.Contains(tips,
                c => c.Contains("FurinaRiderTips.ForSpotlightMove"));
        }

        // AND IT ANSWERS THE QUESTION THE SEAT ASKED: what turns it on.
        var body = Attached(typeof(FurinaRiderTips), "SpotlightMoveBody");
        Assert.Contains("Playing [gold]Ethereal Spotlight[/gold] moves it", body);
        Assert.Contains("clears at the start of your turn", body);
    }

    [Fact]
    public void Take_your_bow_carries_the_definition_of_its_verb()
    {
        Assert.Contains(Il.Calls(Il.Method("TakeYourBow", "get_ExtraHoverTips")),
                        c => c.Contains("FurinaRiderTips.ForBow"));

        var body = Attached(typeof(FurinaRiderTips), "BowBody");
        Assert.Contains("leaves the stage and fires its payoff", body);
        // The three payoffs are interpolated from the constants that pay them,
        // so the sentence cannot quote a retired number (`EB-89`).
        Assert.Contains("Crabaletta deals ", body);
        Assert.Contains("the Usher gains ", body);
        Assert.Contains("Chevalmarin applies Hydro to ALL enemies", body);
    }

    [Fact]
    public void The_tip_that_prints_guest_star_defines_it()
    {
        // The word is printed by `CompanionBody`, not by a card face, so the
        // attach is that tip -- and the two ride together or neither does.
        var body = Attached(typeof(FurinaRiderTips), "ForCard");
        Assert.Contains("A [gold]Companion[/gold] card created into your hand "
                      + "during a fight rather than drafted into your deck.",
                        body);
        Assert.Contains("Guest Stars",
                        Attached(typeof(FurinaRiderTips), "CompanionBody"));
    }

    // ==================================================================
    // `EB-477` -- the half of a Companion card that goes missing in silence
    // ==================================================================
    //
    // THE FIND (Furina r9 (b); r8 (c) two rounds earlier). Under the arm a
    // Companion card you play performs the front member -- and with an EMPTY
    // stage it performs nobody, silently. The r9 seat lost two turns to it,
    // one of them the elite's turn 1; round 8 waited two fights to learn the
    // same thing. There is no board surface that could have said so either:
    // the stage badge IS the Salon power, and an empty stage has no badge.
    //
    // SO THE CARD SAYS IT, live, the way Ethereal Spotlight prints its
    // refusal -- and off the OWNER rather than off the sheet, because Furina
    // holds shared Companions and Guest Stars as readily as her own rows.

    [Fact]
    public void Every_companion_row_carries_the_performance_line()
    {
        // The attach is the generator's and it is by `is_companion`, so it
        // reaches a Guest Star, one of Furina's own rows, and a shared
        // Companion emitted from another character's sheet.
        foreach (var card in new[] { "GuestNeuvilletteTears", "SayuNaptime",
                                     "DionaIcyPaws" })
        {
            Assert.Contains(Il.Calls(Il.Method(card, "get_ExtraHoverTips")),
                            c => c.Contains("ForCompanionPerform"));
        }
    }

    [Fact]
    public void An_empty_stage_prints_the_refusal_and_a_manned_one_does_not()
    {
        var body = Attached(typeof(FurinaRiderTips), "ForCompanionPerform");

        Assert.Contains("No member on stage: performs nobody.", body);
        Assert.Contains("Playing this performs ", body);

        // AND THE GATE IS THE ARM'S: the sentence describes a rule the
        // shipped kit does not have (its members act on their own turn), so
        // the tip asks `ManualLiveFor` before it says anything at all.
        Assert.Contains(
            Il.Calls(Il.Method("FurinaRiderTips", "ForCompanionPerform")),
            c => c.Contains("ManualLiveFor"));
    }

    // ==================================================================
    // `EB-476` -- is a performance an Attack? Two experiments, two answers
    // ==================================================================
    //
    // THE FIND (Furina r9 (c) 3). "A member performance is an Attack for
    // Vulnerable but not for Frozen. Vulnerable 2 turned Crabaletta's 6 into
    // 9... but a Frozen enemy survived two performances without Shattering."
    // The seat ran the experiment twice and could not name the class the
    // performance belongs to.
    //
    // BOTH OBSERVATIONS ARE ONE RULE, `EB-343`'s. A performance goes out
    // through `ElementalHit.Deal`, which reaches `CreatureCmd.Damage` as
    // `ValueProp.Unpowered` with no dealer and no card source. Every gate that
    // asks `IsPoweredAttack()` refuses it -- the Shatter, an enemy's on-Attack
    // trigger -- and `SimDamagePipeline.TargetMods`, which reads the target's
    // Vulnerable, asks nothing of the kind. The arm's Salon paragraph now says
    // it in one sentence.

    [Fact]
    public async Task A_frozen_enemy_keeps_frozen_through_a_performance()
    {
        // THE PROPS A PERFORMANCE CARRIES, handed to the Shatter's own hook:
        // `ElementalHit.Deal` passes `ValueProp.Unpowered`, `dealer: null` and
        // `cardSource: null`, and `FrozenPower.AfterDamageReceived` refuses on
        // the first two of its three guards. Run rather than reasoned about --
        // the refusal returns before any command, which is exactly why it is
        // reachable headless while a real Shatter is not.
        var enemy = Seat.Klee(30).WithPower<FrozenPower>(1);
        var frozen = enemy.Creature.Powers.OfType<FrozenPower>().Single();

        await frozen.AfterDamageReceived(
            null!, enemy.Creature, default!, ValueProp.Unpowered, null, null);

        Assert.Single(enemy.Creature.Powers.OfType<FrozenPower>());

        // AND THE GATE IS THE REASON, not the harness: the same hook reads
        // `IsPoweredAttack`, which `ValueProp.Unpowered` fails.
        Assert.Contains(
            Il.Calls(Il.Method("FrozenPower", "AfterDamageReceived")),
            c => c.Contains("IsPoweredAttack"));
    }

    [Fact]
    public void A_performance_goes_out_through_the_unpowered_elemental_funnel()
    {
        // `PerformMember` is the ONE implementation of a member acting, and
        // the funnel it uses is what decides both halves of the sentence.
        Assert.Contains(
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
            c => c.Contains("ElementalHit.Deal"));

        // The Vulnerable half: `Deal` runs the target's modifiers, and
        // `TargetMods` reads `VulnerablePower` with no powered-attack gate.
        Assert.Contains(
            Il.Calls(Il.Method("ElementalHit", "Deal")),
            c => c.Contains("SimDamagePipeline.TargetMods"));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SimDamagePipeline", "TargetMods")),
            c => c.Contains("IsPoweredAttack"));
    }

    [Fact]
    public void The_arms_salon_paragraph_names_the_class_a_performance_is_in()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        var rules = SalonMemberTips.SalonRulesBody(seat.Creature);

        // `EB-548` renamed the second half and added the word "hit": the
        // rule is about being HIT, and "on-Attack triggers" named it from the
        // player's own side of the board (`Round19Tests` holds that row).
        Assert.Contains(
            "A performance is not an [gold]Attack[/gold] and not a hit: "
          + "[gold]Vulnerable[/gold] moves it, but no [gold]Shatter[/gold] "
          + "and no when-hit power fires.", rules);
    }

    [Fact]
    public void The_shipped_paragraph_takes_no_such_sentence()
    {
        // The shipped kit's members act on their own turn and its paragraph
        // has never described what a performance IS, so the clause has nowhere
        // to go there -- `FurinaReframeRoundSevenTests`' own split, one
        // sentence over.
        using var _ = new Arm(master: false);
        var seat = Seat.Furina().WithCombatState();

        Assert.DoesNotContain(
            "not an [gold]Attack[/gold]",
            SalonMemberTips.SalonRulesBody(seat.Creature));
    }
}
