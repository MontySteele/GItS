using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 11 RUN 2 AND ROUND 12 -- the random Set off's two faces (`EB-431`).
///
/// THE FIND. `Set off each enemy hit` was read as a promise the card kept and
/// it is not one. Across three plays into a four-body elite the two
/// random-target rows set off NOTHING: "Rapid Fire's four 3-damage hits landed
/// as two on Gardener (1) and two on Gardener (2) -- neither of them the one
/// carrying the bomb... `Set off each enemy hit` did nothing at all", and one
/// turn later "Tinder Toss's two hits went to Gardener (1) and Gardener (4).
/// Again neither was the bombed body." The seat's verdict was the card, not the
/// wording: "Its printed selling point cannot be aimed."
///
/// WHAT THE FACES SAY NOW, and it is the C# rule verbatim.
/// <see cref="KleeMod.Powers.ProtoBombPower.SetOffRandom"/> rolls ONCE PER HIT
/// and sets off the enemy that roll picked -- "the roll happens once per hit
/// and each rolled enemy's Bombs go off before that hit lands". So the face
/// leads with the roll and hangs the Set off on the body it picked, which is
/// the shortest sentence that is true of the loop; both rows read alike
/// because both rows are the same call.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round12Tests
{
    /// <summary>A generated card's printed face, off an instance allocated
    /// uninitialised: these `Localization` getters are pure string builders
    /// (<c>DefenceShelfTests</c>' idiom, and the headless boundary's
    /// reason).</summary>
    private static string Face<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == "description").Item2;
    }

    [Fact]
    public void Rapid_Fires_face_hangs_the_set_off_on_the_enemy_it_rolled()
    {
        var face = Face<ProtoKoRapidFire>();
        Assert.Equal(
            "[gold]Set off[/gold] a random enemy and deal {Damage:diff()} "
          + "damage to it, 4 times.", face);
        // The clause the seat priced two turns off is gone: nothing on the
        // face promises a Set off that reaches a body the roll did not pick.
        Assert.DoesNotContain("each enemy hit", face);
    }

    [Fact]
    public void Tinder_Toss_reads_the_same_way_because_it_is_the_same_call()
    {
        var face = Face<ProtoKoTinderToss>();
        Assert.Equal(
            "[gold]Set off[/gold] a random enemy and deal {Damage:diff()} "
          + "damage to it, twice.", face);
    }

    [Fact]
    public void Both_faces_name_the_roll_before_the_set_off()
    {
        // THE ORDER IN THE SENTENCE IS THE ORDER IN THE LOOP. `SetOffRandom`
        // picks the target, then sets that target off, then deals the hit --
        // so "a random enemy" has to be inside the Set off's own clause and
        // not a separate sentence after it, which is how the old faces let a
        // reader believe the two halves aimed at different things.
        foreach (var face in new[] { Face<ProtoKoRapidFire>(),
                                     Face<ProtoKoTinderToss>() })
        {
            Assert.StartsWith("[gold]Set off[/gold] a random enemy and deal ",
                              face);
        }
    }

    // ---- EB-432: the order inside the pile -------------------------------

    /// <summary>The `Set off` tip's body, joined out of the method's own
    /// string literals -- `ArmKeywordTipTests`' idiom, and the headless
    /// boundary's reason: a `LocString` cannot be resolved without a booted
    /// game.</summary>
    private static string SetOffTip() =>
        string.Concat(Il.Strings(typeof(ArmKeywordTips)
            .GetMethod("ForSetOff", HeadlessGame.All)!));

    [Fact]
    public void The_set_off_tip_states_the_placement_order()
    {
        // `SetOff` walks the charges `AddCharge` appended, in the order it
        // appended them ("Charges in placement order"). The r11 run-2 seat
        // could get that only by arithmetic: "Bombs go off in placement
        // order, and the first one is the one that eats the Melt -- a rule
        // nothing printed."
        Assert.Contains("oldest first", SetOffTip());
    }

    [Fact]
    public void The_set_off_tip_says_which_charge_meets_the_aura()
    {
        // Every reaction consumes the aura, so the charge that meets it is
        // the one the walk reaches first. Stated as the aura and not as "only
        // the first reacts", which a Swirl makes false: that reaction
        // re-applies what it consumed to every living enemy, the target
        // included.
        Assert.Contains("the first takes the aura", SetOffTip());
        Assert.DoesNotContain("only the first reacts", SetOffTip());
    }

    [Fact]
    public void The_pile_is_still_the_subject_of_the_sentence()
    {
        // `EB-287`'s claim -- a pile goes off TOGETHER -- was carried by this
        // tip's old "Every Bomb on the target". It is carried by the new
        // subject instead, and the round-four pin reads it there.
        Assert.Contains("The target's [gold]Bombs[/gold] go off first",
                        SetOffTip());
    }

    // ---- EB-443: what Block and a when-hit Attack effect do to a Bomb -----

    [Fact]
    public void The_set_off_tip_says_block_absorbs_the_hit()
    {
        // `ElementalHit.DealWithoutDealerMods` passes `ignoreBlock: false`,
        // so the explosion pays Block like anything else. The r12 run-2 seat
        // concluded the opposite from a true observation: "Set off ignores
        // enemy Block... Two 11-point bombs both landed at full value into
        // Skittish 6." There was no Block, because Skittish never fired.
        Assert.Contains("[gold]Block[/gold] stops them", SetOffTip());
    }

    [Fact]
    public void The_set_off_tip_says_no_attack_trigger_fires()
    {
        // The hit reaches `CreatureCmd.Damage` as `ValueProp.Unpowered` with
        // `dealer: null`, so nothing an enemy keys on being hit by an Attack
        // can answer it. "Not an Attack" on the Bomb tip left that to
        // inference and the seat's inference went the other way.
        Assert.Contains("no Attack trigger ", SetOffTip());
        Assert.Contains("fires", SetOffTip());
    }

    [Fact]
    public void The_size_clause_is_what_paid_for_them()
    {
        // A keyword tip is read in HAND, where there is no pile to quote, so
        // the arithmetic stays on the badge -- `EB-343`'s own split between
        // the two surfaces, and the trade the Mine tip already makes.
        Assert.DoesNotContain("for its size", SetOffTip());
        Assert.Contains("each a Pyro hit.", SetOffTip());
    }

    // ---- EB-436: a Mine does not blunt the hit ---------------------------

    private static string MineTip() =>
        string.Concat(Il.Strings(typeof(ArmKeywordTips)
            .GetMethod("ForMine", HeadlessGame.All)!));

    [Fact]
    public void The_mine_tip_says_the_hit_still_lands()
    {
        // THE OLD SENTENCE WAS TRUE AND SAID NOTHING ABOUT THE HIT. "Goes off
        // when its enemy attacks you, before the hit lands" reads as
        // mitigation, and the r12 act-1 seat played a turn on that read:
        // three Mines left armed against an elite, five went off, "every hit
        // landed in full, 36 to 18 HP".
        Assert.Contains("which lands in full unless the Mine kills", MineTip());
        Assert.DoesNotContain("before the hit lands", MineTip());
    }

    [Fact]
    public void The_mine_tip_still_names_both_folded_terms()
    {
        // "Read the badge:" is what paid for the new clause; the clause it
        // introduced is untouched, so R248's rule survives whole.
        Assert.Contains("Only their ", MineTip());
        Assert.Contains("[gold]Vulnerable[/gold] and a cap move it.", MineTip());
        Assert.DoesNotContain("Read the badge", MineTip());
    }

    [Fact]
    public void The_badge_carries_the_same_sentence()
    {
        // ONE CLAUSE, TWO SURFACES -- the arrangement `MineClause` has had
        // since `EB-260`, and the reason that row was filed: the tooltip
        // carried rule 6 and the smart face did not.
        var pile = ProtoBombs.Place(Seat.Klee(30).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4, IsMine: true));
        var rows = pile.Localization!;
        foreach (var key in new[] { "description", "smartDescriptionMines" })
        {
            Assert.Contains(
                "goes off before this enemy's hit, which lands in full "
              + "unless the Mine kills.",
                rows.First(r => r.Item1 == key).Item2);
        }
    }

    // ---- EB-392: three words on one screen -------------------------------

    private static string HexereiTip() =>
        string.Concat(Il.Strings(typeof(ArmKeywordTips)
            .GetMethod("ForHexerei", HeadlessGame.All)!));

    [Fact]
    public void The_hexerei_tip_gives_a_test_a_player_can_run()
    {
        // "From the witches' circle" was doing silent work: the r12 run-2
        // seat "could not tell from any card face whether MY Companion
        // qualified" and found out by counting Bombs on an enemy badge. Every
        // member prints the word now, so the definition can point at it.
        Assert.Contains("card that prints the word", HexereiTip());
        Assert.DoesNotContain("witches' circle", HexereiTip());
    }

    [Fact]
    public void The_hexerei_tip_names_the_other_word_on_the_screen()
    {
        // The seat met three: "there is apparently a distinction between
        // `Companion`, `Hexerei`, and `Klee's own Companion`, and none of the
        // three cards involved prints which one it is." `Klee's own` is the
        // Spark rider's exact phrase, so the two meet under one spelling --
        // and the relation is stated as the OVERLAP it is, five rows carrying
        // both marks and thirteen carrying one.
        Assert.Contains("Some are Klee's own, some are not", HexereiTip());
        // ONE SPELLING FOR THE OTHER WORD: the Spark rider says "Klee's own"
        // too, so a player who has met that rider recognises the set this
        // sentence is pointing at rather than meeting a fourth phrase.
        Assert.Contains("Klee's own", string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForCovenSpark", HeadlessGame.All)!)));
    }

    // ---- EB-425: a deploy deals damage and takes no target ---------------

    [Fact]
    public void The_salon_rules_say_the_member_picks_its_own_enemy()
    {
        // THE REFUSAL WAS THE FIRST PLACE THE SEAT LEARNED IT. r5 run 1: "the
        // first thing I tried was `play 'Salon Debut' on 'Corpse Slug (1)'`
        // and it was refused... a card that deals damage but takes no target
        // is not something the face warns you about. The Salon picked slug 2
        // on its own. I never got to choose a member's target all round."
        //
        // It is a rule about every PERFORMANCE -- `PerformMember` draws the
        // body from `Rng.CombatTargets` and is the only implementation of a
        // member acting -- so it is on the paragraph every Salon card carries
        // rather than on one card's face.
        var body = string.Concat(Il.Strings(typeof(SalonMemberTips)
            .GetMethod("SalonRulesBody",
                       HeadlessGame.All,
                       new[] { typeof(Creature) })!));

        Assert.Contains("A performing member picks its own enemy.", body);
    }

    [Fact]
    public void The_deploy_word_could_not_have_carried_it()
    {
        // Said rather than assumed: the keyword is at its ceiling with
        // `EB-368`'s three rules, which is why the clause went to the
        // paragraph behind the word.
        var deploy = string.Concat(Il.Strings(typeof(ArmKeywordTips)
            .GetMethod("ForDeploy", HeadlessGame.All)!));
        var rendered = deploy.Replace("KLEEMOD-ARM_DEPLOY", string.Empty)
            .Replace("[gold]", string.Empty).Replace("[/gold]", string.Empty);

        Assert.True(rendered.Length > 130, rendered.Length.ToString());
        Assert.DoesNotContain("picks its own", deploy);
    }
}
