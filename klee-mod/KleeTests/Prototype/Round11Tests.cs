using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 11 -- `EB-417`, the enemy badge that titled a Mine `Bomb`.
///
/// THE FIND. The r11 blind Opus seat played the whole of act 1 off Jumpy
/// Dumpty's Mine line and had to learn the rule from the CARD, because the
/// badge on the enemy wearing the Mine led with the wrong word:
///
///     "the enemy badge calls a Mine `Bomb 4` in the title and only discloses
///     it is a Mine in the body text ('Bombs here: 1, including 1 Mine').
///     Since the whole Mine trick is timing, the badge should lead with it."
///
/// The seat is right about the stakes rather than only the wording: its two
/// best plays of the run were both "leave the enemy on exactly Mine-lethal HP,
/// because a Mine goes off before the hit lands", and that is a read taken off
/// the badge under an enemy, in the moment, with no card in front of the
/// player at all.
///
/// WHAT MOVED, AND WHAT DELIBERATELY DID NOT. Only the TITLE. Rule 6's
/// sentence was already on the mined faces (`EB-260`) and stays exactly where
/// it was, on both branches of the title -- so a mixed pile keeps `Bomb`,
/// keeps its fuse mark ("including {Mines} Mines") and keeps the timing clause
/// beside it. All of them or none is the honest test for a badge that is ONE
/// name over one number.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round11Tests
{
    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    [Fact]
    public void The_badge_carries_both_names()
    {
        // Loc is registered once at boot and a pile changes every turn, so the
        // second name has to EXIST before the live choice can be made -- the
        // same bargain `SmartDescriptionLocKey` makes for the face.
        var pile = ProtoBombs.Place(Seat.Klee(30).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4));
        Assert.Equal("Bomb", Row(pile, "title"));
        Assert.Equal("Mine", Row(pile, "titleMine"));
    }

    [Fact]
    public void A_pile_that_is_all_mines_is_titled_a_mine()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(3, IsMine: true),
            new ProtoBombs.Charge(4, IsMine: true));

        Assert.Equal(2, pile.MineCount);
        Assert.True(pile.TitledAsMine);
    }

    [Fact]
    public void A_pile_holding_one_plain_bomb_is_still_titled_a_bomb()
    {
        // The denominator, and the rule itself: one badge over two kinds of
        // charge may not promise a timing rule that half of it does not have.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(8),
            new ProtoBombs.Charge(4, IsMine: true));

        Assert.Equal(1, pile.MineCount);
        Assert.False(pile.TitledAsMine);
        // ...and the Mine is disclosed where it always was, with rule 6's
        // clause beside it: the title switch is not what carries the timing.
        var face = Row(pile, "smartDescriptionMines");
        Assert.Contains("including [blue]{Mines}[/blue]", face);
        Assert.Contains("before the hit lands", face);
    }

    [Fact]
    public void A_pile_with_no_charges_left_is_a_bomb_again()
    {
        // A canonical (compendium) copy has no charges, and an emptied pile is
        // the same shape: `MineCount == _charges.Count` is true vacuously at
        // zero, so the guard leads with `MineCount > 0`.
        var pile = ProtoBombs.Place(Seat.Klee(30).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4, IsMine: true));
        pile.TakeAll();

        Assert.Equal(0, pile.MineCount);
        Assert.False(pile.TitledAsMine);
    }
}
