using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
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
    public void Tinder_Toss_no_longer_rolls_a_target_at_all()
    {
        // `EB-749` (R271 sec.5.3) ENDED the random-target complaint on this
        // row rather than re-wording it: the card took Fireworks Show's slot
        // and aims at everything, so there is no roll for a face to name.
        // (Rapid Fire, which kept the repeated-Set-off line, was cut by the
        // Klee status package, 2026-10-01.)
        var face = Face<ProtoKoTinderToss>();
        Assert.Equal(
            "[gold]Set off[/gold] ALL enemies. Deal {Damage:diff()} [gold]Pyro[/gold] damage "
          + "to ALL enemies.", face);
        Assert.DoesNotContain("random", face);
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
        // nothing printed." `EB-755` (R276) made the words unambiguous for two
        // Bombs placed in one turn.
        // Text pass 2026-09-25: "oldest first", the tip's one order clause.
        Assert.Contains("oldest first", SetOffTip());
    }

    [Fact]
    public void The_pile_is_still_the_subject_of_the_sentence()
    {
        // `EB-287`'s claim -- a pile goes off TOGETHER -- was carried by this
        // tip's old "Every Bomb on the target". It is carried by the new
        // subject instead, and the round-four pin reads it there.
        Assert.Contains("Every [gold]Bomb[/gold] on the enemy goes off",
                        SetOffTip());
    }

    // ---- EB-392: three words on one screen, now one (R276) ---------------

    // `EB-723` RETIRED THE SECOND HALF OF THIS PAIR. It asserted that
    // `ArmKeywordTips.ForDeploy` was at its ceiling and so could not have
    // carried the aim clause -- and the `Deploy` word left the mod with the
    // reframe's eleven `proto_fr_` rows under R213 B's deletion rule, so the
    // pin has no subject. The clause it was about is still where it went, and
    // the test above is what holds it there.

    // ---- EB-437: two nouns that read as one ------------------------------

    /// <summary>A mod source file, read whole. Walked up from the test binary
    /// rather than copied at build time, which is `KurageMemoryPinTests`'
    /// idiom and its reason: a stale copy beside the dll is exactly the drift
    /// a text pin exists to catch.</summary>
    private static string Printed(string relativePath)
    {
        var relative = System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar));
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                // COMMENTS STRIPPED, which `lint_text_conventions` does for
                // the same reason: a comment quoting the seat's own words is
                // not a surface a player reads, and this pin is about what
                // ships.
                return System.Text.RegularExpressions.Regex.Replace(
                    System.IO.File.ReadAllText(candidate),
                    @"^\s*//.*$", string.Empty,
                    System.Text.RegularExpressions.RegexOptions.Multiline);
            }
            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(
            "no " + relative + " above " + System.AppContext.BaseDirectory);
    }

    // ---- EB-438: a printed number is the delivered number ---------------

    [Fact]
    public void The_stored_shower_prints_the_number_it_will_deal()
    {
        // "The buff line printed `Sacramental Shower 1 -- ... deal 9 Hydro
        // damage to it first`, and when it fired the ship went 38 to 32, i.e.
        // 6. I was carrying Weak 2... the stored-buff text does not [fold]."
        //
        // `Spring` deals through `ElementalHit.Deal` with `powered: true`,
        // whose first step is `SimDamagePipeline.DealerMods`, so the badge
        // asks that same call.
        var src = Printed("Powers/Prototype/CompanionOverhaulHooks.cs");

        Assert.Contains("(\"smartDescription\",", src);
        Assert.Contains("SimDamagePipeline.DealerMods(power.Owner, BaseValue)",
                        src);
        // The static compendium row keeps its literal: `PowerModel.HoverTips`
        // binds vars on the SMART branch alone, and a token on the other one
        // reaches the screen as a placeholder (`EB-353`).
        Assert.Contains(
            "$\"[blue]{CompanionOverhaulLaw.ShowerDamage}[/blue]", src);
    }
    // ==================================================================
    // `EB-526` -- "Spotlight every Companion card" and the card made after
    // ==================================================================
    //
    // THE READ (Furina r12 lane 2). "Charlotte arrived printing 6 damage and
    // Shinobu printing 6 block while `Guest Cast 1` was up. Every Companion
    // that was in my deck when I played it showed its lit number immediately."
    //
    // SIX IS THE LIT NUMBER. Both rows are printed 4 on their sheets
    // (`charlotte_freezing_point` deals 4, `shinobu_grass_ring_bond` gains 4)
    // and Guest Cast is x1.5, so 4 -> 6 on each. The seat compared the two
    // against a base of 6 and read the lit face as the unlit one.
    //
    // AND THE PREDICATE HAS NO MEMBERSHIP IN IT, which is why a card made
    // after the lighting cannot be missed: `IsSpotlighted` asks the OWNER's
    // live mode and the card's CLASS, and reads no list of cards that were
    // present when the mode was set. A generated Companion is `ICompanionCard`
    // and carries its owner (`GuestStarGenerator` hands `source.Owner` to
    // `CreateCard`), so it answers the same question the same way.

}
