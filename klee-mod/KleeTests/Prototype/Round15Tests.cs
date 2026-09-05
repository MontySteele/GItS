using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 15, the rows the seats filed against a face that was true and
/// unreadable -- a rule stated in words narrower than the rule.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round15Tests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    /// <summary>One localization row off a card or power instance.</summary>
    private static string Row(object model, string key)
    {
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

    /// <summary>
    /// The literal text one tip attach prints, read off the compiled method.
    ///
    /// ENUMERATING THE TIP IS NOT REACHABLE HEADLESS: every yielded
    /// <c>HoverTip</c> formats a <c>LocString</c> title through
    /// <c>LocManager.Instance</c>, null until the game boots
    /// (<see cref="ArmKeywordTipTests"/>' own note, and the README's headless
    /// boundary). Adjacent string constants are folded by the compiler, so a
    /// body written as a concatenation is one `ldstr` per sentence and reading
    /// them back needs no ordering.
    /// </summary>
    private static string Printed(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method, All)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    // ==================================================================
    // `EB-469` -- "Attacks deal 25% less" and a Skill that lost its damage
    // ==================================================================
    //
    // THE FIND (Kokomi r15 (c) 2). "Weak reduces a card printed as a `skill`,
    // and the two Weak texts disagree about that. The keyword box says 'Weak
    // -- The wearer deals 25% less damage'; my own status line says 'Weak 1
    // (debuff) -- **Attacks** deal 25% less damage for 1 turn.' Kurage's Oath
    // is printed `cost 1, skill` and its face changed from 'Deal 3 damage to
    // ALL enemies' to 'Deal 2 damage to ALL enemies' while I wore Weak... the
    // status line told me skills were safe and the card told me they were
    // not."
    //
    // WHAT THE ENGINE DOES, WHICH IS WHAT THE ROW ASKS FIRST. Weak is a
    // property of the HIT, never of the card: `WeakPower` returns its 0.75
    // only for a hit whose `ValueProp` answers `IsPoweredAttack()`, and the
    // generator emits `new DamageVar(..., ValueProp.Move)` for every `op:
    // damage` clause on every row whatever `type:` that row declares. A Skill
    // that deals damage is therefore Weakened exactly like an Attack, and
    // "Attacks" in the game's own sentence means attack HITS.
    //
    // SO NOTHING IN THE ENGINE MOVES and the words do: `BaseKeywordTips.
    // ForWeak` and `blindplay_notes.BASE_KEYWORDS["Weak"]` -- pinned to each
    // other by `test_the_base_keyword_glossary_is_the_mods_own_tooltip_text`
    // -- now name the case the status line leaves ambiguous.

    [Fact]
    public void A_skills_damage_clause_is_a_powered_attack_and_weak_reads_it()
    {
        // THE CARD IS A SKILL. Not incidentally: this is the exact card the
        // seat watched go 3 -> 2, and its type is what it read as protection.
        var oath = new ProtoKkKuragesOath();
        Assert.Equal(CardType.Skill, oath.Type);

        // AND ITS DAMAGE CLAUSE IS A POWERED ATTACK. `CanonicalVars` is
        // protected, so it is read the way every other pin in this suite reads
        // it, and the `Props` on the emitted `DamageVar` is what the hook sees.
        var vars = ((IEnumerable<DynamicVar>)typeof(ProtoKkKuragesOath)
            .GetProperty("CanonicalVars", All)!.GetValue(oath)!).ToList();
        var damage = vars.OfType<DamageVar>().Single();

        Assert.Equal(ValueProp.Move, damage.Props);
        Assert.True(damage.Props.IsPoweredAttack());

        // AND THE GAME'S OWN POWER AGREES, run for real rather than reasoned
        // about: 0.75 off a `ValueProp.Move` hit, which is the only question
        // `WeakPower` asks -- it is never handed the card at all.
        var wearer = Seat.Kokomi().WithPower<WeakPower>(1);
        var enemy = Seat.Kokomi(30).Creature;
        var weak = wearer.Creature.Powers.OfType<WeakPower>().Single();

        Assert.Equal(0.75m, weak.ModifyDamageMultiplicative(
            enemy, 0m, damage.Props, wearer.Creature, null, null));

        // 3 x 0.75 = 2.25, truncated by the printer to the 2 the seat read.
        Assert.Equal(3m, damage.BaseValue);
        Assert.Equal(2, new DynamicVar("x", damage.BaseValue * 0.75m).IntValue);
    }

    // ==================================================================
    // `EB-468` -- a promise advertised for a full turn after it was dead
    // ==================================================================
    //
    // THE FIND (Kokomi r15 (c) 4). Sayu -- Naptime played after a Strike put
    // "Naptime 4 -- if you play no Attacks this turn, draw 4" on the bar for a
    // full turn and paid nothing; the condition had already failed when the
    // card was played. "A Glam replay stacked it 2 to 4 rather than firing
    // twice" was the same seat's second half, and unprinted.
    //
    // THE RULE DOES NOT MOVE. The grant stands and the end-of-turn removal
    // stands -- a play that granted nothing would leave nothing on screen at
    // all, and the badge is what the player reads. What moves is the badge:
    // while an Attack has already been played it prints the missed form, and
    // the promise carries the stacking clause either way.

    /// <summary>A Naptime badge on a live seat, with an id to key its faces
    /// off. `ProtoBombsHarness`' shape, inline: the harness there exists
    /// because a Bomb pile needs charges seeded, and this power needs nothing
    /// but an owner and a stack.</summary>
    private static (Seat Seat, NaptimePower Power) Napping(int amount = 2)
    {
        var seat = Seat.Kokomi().WithCombatState().WithPower<NaptimePower>(amount);
        var power = seat.Creature.Powers.OfType<NaptimePower>().Single();
        Seat.Force(power, "Id", new ModelId("POWER", "NAPTIME_TEST"));
        return (seat, power);
    }

    [Fact]
    public void Naptime_prints_the_missed_form_once_an_attack_has_been_played()
    {
        var (seat, power) = Napping();
        var key = typeof(NaptimePower).GetProperty(
            "SmartDescriptionLocKey", All)!;

        // NOTHING PLAYED YET: the promise is live and the badge says so.
        Assert.EndsWith(".smartDescription", (string)key.GetValue(power)!);

        // ONE ATTACK, and the same badge now says the turn is spent. The
        // ledger is the mod's own counter, the one `AfterSideTurnEnd` reads to
        // decide whether to remove the power at all.
        CompanionOverhaulLedger.For(seat.Creature).NoteAttack();

        Assert.EndsWith(".smartDescriptionMissed",
                        (string)key.GetValue(power)!);

        var rows = power.Localization!;
        Assert.Equal(
            "Missed this turn: an [gold]Attack[/gold] has been played, so "
          + "this draws nothing and leaves at the end of the turn.",
            rows.Single(r => r.Item1 == "smartDescriptionMissed").Item2);
    }

    [Fact]
    public void The_naptime_face_says_that_copies_add_up()
    {
        var (_, power) = Napping();
        var rows = power.Localization!;

        // Both the compendium row and the live one, because a replay is met
        // in hand as often as on the bar.
        foreach (var key in new[] { "description", "smartDescription" })
        {
            Assert.EndsWith("Copies add up.",
                            rows.Single(r => r.Item1 == key).Item2);
        }
    }

    [Fact]
    public void A_replayed_naptime_reads_four_because_the_counter_adds()
    {
        // `PowerStackType.Counter` is what makes a second grant a bigger draw
        // rather than a second draw -- which is the arithmetic the seat saw
        // (2 -> 4) and the clause above now prints.
        var (_, power) = Napping(4);

        Assert.Equal(PowerStackType.Counter, power.StackType);
        Assert.Equal(4m, power.Amount);
    }

    // ==================================================================
    // `EB-471` -- which side of the growth tick a Mine goes off on
    // ==================================================================
    //
    // THE FIND (Klee r15 run 2 (c) 3). "A Mine fires at its base size on the
    // enemy's turn, before the growth tick, and nothing printed says which
    // side of the tick it lands on: Jumpy Dumpty's Mine 3 paid 3, not 7, and I
    // reverse-engineered it from HP." It changes whether the rider is worth
    // the card.
    //
    // THE ROW'S FIRST OPTION IS FALSE HERE and cannot be printed: "Mines do
    // not grow" is contradicted by `ProtoBombPower.GrowBy`, which walks EVERY
    // charge on the pile, and a Mine is a charge -- a Mine that lives to the
    // next turn start really is 7. What is true is the TIMING, and the badge
    // is where it goes: growth at the start of your turn, the Mine off before
    // the enemy's hit, so the number standing now is the number it pays.
    //
    // ON THE MINE FACE AND NOT ON `Bombs`, which is at 125 of its 125-char
    // ceiling (its own note says so, and `lint_text_conventions` bites); the
    // Mine faces already carry `_BOMB_FACE_REASON`'s exception.

    [Fact]
    public void The_mine_badge_says_when_the_growth_it_is_about_happens()
    {
        var mines = (string)typeof(ProtoBombPower)
            .GetField("BombsWithMines", All)!.GetValue(null)!;
        var plain = (string)typeof(ProtoBombPower)
            .GetField("Bombs", All)!.GetValue(null)!;

        Assert.EndsWith("growing at your turn's start.", mines);
        // The no-Mine face is untouched: it has no room and no Mine to be
        // about. `KleeOverhaulRoundFourTests` pins its wording.
        Assert.EndsWith("growing each turn.", plain);
    }

    [Fact]
    public void A_mine_is_a_charge_and_the_growth_walk_does_not_skip_it()
    {
        // The reason the row's other sentence could not be printed, asserted
        // rather than asserted about: place a Mine, grow the pile, and the
        // Mine is bigger.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(3, IsMine: true));

        Assert.Equal(3, pile.TotalSize);
        pile.GrowBy(KleeOverhaulLaw.BombGrowth);
        Assert.Equal(3 + KleeOverhaulLaw.BombGrowth, pile.TotalSize);
        Assert.Equal(1, pile.MineCount);
    }

    [Fact]
    public void The_weak_tip_names_the_case_the_status_line_leaves_open()
    {
        var body = Printed(typeof(BaseKeywordTips), "ForWeak");

        Assert.Equal(
            "The wearer deals 25% less damage with every hit it lands, a "
          + "Skill's damage too. One stack falls off at the end of each of "
          + "its turns.", body);
        // The tip a player hovers is inside the in-game box either way.
        Assert.True(body.Length <= 135, body.Length.ToString());
    }
}
