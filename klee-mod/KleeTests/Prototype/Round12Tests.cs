using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
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
}
