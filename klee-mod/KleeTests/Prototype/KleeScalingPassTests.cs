using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE SCALING PASS (staging branch `klee-next`, 2026-10-05,
/// `review/active/klee-scaling-pass-2026-10-05.md` sec.4): A Klee's Secret
/// Base, B the grant-only Witch's Homework II, C Boom Badge, D the tempo
/// relic. Pure reads where the rule is pure; structural (IL) pins where the
/// rule runs through <c>PowerCmd.Apply</c>, outside the headless boundary
/// (README).
/// </summary>

public sealed class KleeScalingPassTests
{
    // ==== A. Klee's Secret Base ==============================================

    [Fact]
    public void Secret_base_reads_three_four_upgraded_and_places_nothing_itself()
    {
        var card = new ProtoKoSecretBase();
        Assert.Equal("Your [gold]Bombs[/gold] are placed {PowerAmount:diff()} bigger.",
                     Face(card));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(3m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(4m, Upgraded<ProtoKoSecretBase>().DynamicVars["PowerAmount"].BaseValue);
        // The old turn-start Bomb is gone: no override, no sequencer seat.
        Assert.NotEqual(typeof(SecretBasePower),
                        typeof(SecretBasePower).GetMethod("AfterPlayerTurnStart")!.DeclaringType);
        Assert.DoesNotContain("SecretBasePower",
            string.Join(" ", Il.Calls(Il.Method("KleeExpansion", "RunTurnStartPlacements"))));
    }

    [Fact]
    public void Secret_base_stacks_by_adding_and_joins_the_charm_in_the_placement_bonus()
    {
        var klee = Seat.Klee();
        Assert.Equal(0, SecretBasePower.BonusFor(klee.Creature));
        Assert.Equal(0, SecretBasePower.BonusFor(null));
        klee.WithPower<SecretBasePower>(3);
        Assert.Equal(3, SecretBasePower.BonusFor(klee.Creature));
        // A Counter: a second copy adds to the one instance (the game's
        // stacking); two instances, if ever, still sum.
        klee.WithPower<SecretBasePower>(4);
        Assert.Equal(7, SecretBasePower.BonusFor(klee.Creature));
        Assert.Equal(7, ProtoBombPower.PlacementBonus(klee.Creature));
        Give<DodocoCharm>(klee);
        Assert.Equal(8, ProtoBombPower.PlacementBonus(klee.Creature));
    }

    [Fact]
    public void Place_pays_secret_base_on_every_placement_and_never_on_a_move()
    {
        var place = Il.Calls(Il.Method("ProtoBombPower", "Place"));
        Assert.Contains("SecretBasePower.BonusFor", place);
        Assert.Contains("DodocoCharm.BonusFor", place);
        // The MOVES pass `relocated: true`: a jump and a merge.
        foreach (var move in new[] { "JumpCharges", "MergeAllTo" })
        {
            Assert.All(PlaceFlags("ProtoBombPower", move), f => Assert.True(f, move));
        }
        Assert.All(PlaceFlags("AlicesMasterpiecePower", "Remain"), f => Assert.True(f));
        // Every PLACEMENT passes false: the card verbs, Jumpy Dumpty's payload
        // Mines (inside Explode), All of My Treasures!'s copies, a charge
        // landing on a dead target.
        foreach (var placement in new[] { "PlaceOnAll", "PlaceOnRandom",
                     "PlaceCopyOfLargest", "Explode", "PlaceOrJump" })
        {
            Assert.All(PlaceFlags("ProtoBombPower", placement), f => Assert.False(f, placement));
        }
    }

    [Fact]
    public void Every_other_placer_goes_through_the_one_door()
    {
        // Return to Sender, Little Hexenzirkel, Aftershock, Party Poppers,
        // Finders Keepers, Dodoco, the relics: each reaches Place (directly or
        // through PlaceOnRandom / PlaceOnAll), which is where the bonus is paid.
        var doors = new[] { "ProtoBombPower.Place", "ProtoBombPower.PlaceOnRandom",
                            "ProtoBombPower.PlaceOnAll" };
        foreach (var (type, method) in new[]
                 {
                     ("AftershockPower", "AfterChargeExploded"),
                     ("PartyPoppersPower", "AfterCardPlayed"),
                     ("KleeExpansion", "RunTurnStartPlacements"),
                     ("PoundingSurpriseNext", "BeforeCombatStart"),
                 })
        {
            Assert.Contains(Il.Calls(Il.Method(type, method)), c => doors.Contains(c));
        }
    }

    [Fact]
    public void A_bomb_face_previews_the_placed_size_as_accuracy_does_a_shiv()
    {
        var klee = Seat.Klee().WithPower<SecretBasePower>(3);
        var pop = Owned(new ProtoKoPop(), klee);
        var size = pop.DynamicVars["BombSize"];
        Assert.IsType<BombSizeVar>(size);
        Assert.Equal(8m, Preview(size, pop, hooks: true));
        // The play still hands the BASE to Place, which adds the bonus once.
        Assert.Equal(5, size.IntValue);
        // Off the hand (no global hooks) the face prints its own number.
        Assert.Equal(5m, Preview(size, pop, hooks: false));
        // A canonical copy (reward, compendium) prints its base.
        var canonical = new ProtoKoPop();
        Assert.Equal(5m, Preview(canonical.DynamicVars["BombSize"], canonical, hooks: true));

        // Jumpy Dumpty's payload Mine is a placement too, and its face says so.
        var jumpy = Owned(new ProtoKoJumpyDumpty(), klee);
        Assert.Equal(11m, Preview(jumpy.DynamicVars["BombSize"], jumpy, hooks: true));
        Assert.Equal(6m, Preview(jumpy.DynamicVars["PayloadMine"], jumpy, hooks: true));
        Assert.Contains("ProtoBombPower.Place", Il.Calls(Il.Method("ProtoKoPop", "OnPlay")));
    }

    // ==== C. Boom Badge =======================================================

    [Fact]
    public void Boom_badge_retains_and_does_not_stack()
    {
        var card = new ProtoKoBoomBadge();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.EndsWith("deal double damage. Does not stack.", Face(card));
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(1, Upgraded<ProtoKoBoomBadge>().PrintedSparkPrice);
        Assert.Equal(1, BoomBadgePower.FactorFor(0));
        Assert.Equal(2, BoomBadgePower.FactorFor(1));
        Assert.Equal(2, BoomBadgePower.FactorFor(2));
        Assert.Equal(2, BoomBadgePower.FactorFor(9));
    }

    // ==== B. Witch's Homework II ==============================================

    [Fact]
    public void Homework_prints_its_face_and_is_offered_nowhere()
    {
        var card = new ProtoKoWitchsHomeworkNext();
        Assert.Equal(
            "Place a [gold]Bomb[/gold] {BombSize:diff()}. When it goes off, this "
          + "card's [gold]Bomb[/gold] is {IfUpgraded:show:3|2} larger for the rest "
          + "of the run.", Face(card));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(6m, card.DynamicVars["BombSize"].BaseValue);
        Assert.IsType<BombSizeVar>(card.DynamicVars["BombSize"]);
        Assert.Equal(2, ((IHomeworkCard)card).HomeworkStep);
        Assert.Equal(3, ((IHomeworkCard)Upgraded<ProtoKoWitchsHomeworkNext>()).HomeworkStep);
        Assert.Contains("KleeScalingPass.PlaceHomework",
                        Il.Calls(Il.Method("ProtoKoWitchsHomeworkNext", "OnPlay")));
        // Grant-only: not in her offer roster (the pool's Witch's Homework is).
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        Assert.DoesNotContain(slice, c => c.Contains("ProtoKoWitchsHomeworkNext"));
        Assert.Contains(slice, c => c.Contains("ProtoKoOneMoreCharge"));
    }

    [Fact]
    public void Homework_growth_is_a_saved_property_that_writes_the_face()
    {
        var prop = typeof(ProtoKoWitchsHomeworkNext).GetProperty("HomeworkGrowth")!;
        Assert.NotNull(prop.GetCustomAttribute<SavedPropertyAttribute>());

        // A save load writes the property; the face follows.
        var loaded = Mutable(new ProtoKoWitchsHomeworkNext());
        ((IHomeworkCard)loaded).HomeworkGrowth = 4;
        Assert.Equal(10m, loaded.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(10, loaded.DynamicVars["BombSize"].IntValue);
    }

    [Fact]
    public void Homework_grows_the_combat_copy_and_its_deck_card_like_genetic_algorithm()
    {
        var deck = Mutable(new ProtoKoWitchsHomeworkNext());
        var combat = Mutable(new ProtoKoWitchsHomeworkNext());
        combat.DeckVersion = deck;

        KleeScalingPass.Grow(combat, 2);
        Assert.Equal(2, ((IHomeworkCard)deck).HomeworkGrowth);
        Assert.Equal(2, ((IHomeworkCard)combat).HomeworkGrowth);
        Assert.Equal(8m, deck.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(8m, combat.DynamicVars["BombSize"].BaseValue);

        // A card with no deck version (made in combat) grows only itself.
        var made = Mutable(new ProtoKoWitchsHomeworkNext());
        KleeScalingPass.Grow(made, 3);
        Assert.Equal(9m, made.DynamicVars["BombSize"].BaseValue);
    }

    [Fact]
    public void Homework_grows_at_most_once_a_combat_whatever_replays_it()
    {
        KleeOverhaulLedger.ResetAll();
        var klee = Seat.Klee();
        var deck = Mutable(new ProtoKoWitchsHomeworkNext());
        var first = Mutable(new ProtoKoWitchsHomeworkNext());
        first.DeckVersion = deck;
        // A replay is the same combat card; a second copy of the same deck
        // card shares the key.
        var second = Mutable(new ProtoKoWitchsHomeworkNext());
        second.DeckVersion = deck;

        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(second));
        Assert.Equal(2, ((IHomeworkCard)deck).HomeworkGrowth);

        // An unmarked charge (a copy from All of My Treasures!) grows nothing.
        var other = Mutable(new ProtoKoWitchsHomeworkNext());
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature,
            new ProtoBombPower.ProtoCharge(20, false, 0));
        Assert.Equal(0, ((IHomeworkCard)other).HomeworkGrowth);

        // The next combat (a fresh ledger) grows it again.
        KleeOverhaulLedger.ResetAll();
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        Assert.Equal(4, ((IHomeworkCard)deck).HomeworkGrowth);
        KleeOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_mark_survives_a_jump_and_a_merge_and_a_copy_never_has_it()
    {
        // Explode is where it is read.
        Assert.Contains("KleeScalingPass.AfterHomeworkWentOff",
                        Il.Calls(Il.Method("ProtoBombPower", "Explode")));
        // A jump hands the charge's mark to its landing.
        Assert.Contains("ProtoCharge.get_Homework",
                        Il.Calls(Il.Method("ProtoBombPower", "JumpCharges")));
        // A merge carries every mark it swallowed.
        Assert.Contains("KleeScalingPass.MergeMarks",
                        Il.Calls(Il.Method("ProtoBombPower", "MergeAllTo")));
        // A copy reads the size and nothing else.
        foreach (var copy in new[] { "PlaceCopyOfLargest", "PlaceCopyOfLargestOnAll" })
        {
            Assert.DoesNotContain("ProtoCharge.get_Homework",
                                  Il.Calls(Il.Method("ProtoBombPower", copy)));
        }

        var a = Mutable(new ProtoKoWitchsHomeworkNext());
        var b = Mutable(new ProtoKoWitchsHomeworkNext());
        Assert.Null(KleeScalingPass.MergeMarks(null, null));
        Assert.Equal(new CardModel[] { a }, KleeScalingPass.MergeMarks(null, new CardModel[] { a }));
        Assert.Equal(new CardModel[] { a, b },
                     KleeScalingPass.MergeMarks(new CardModel[] { a }, new CardModel[] { b, a }));
    }

    [Fact]
    public void Two_merged_homework_bombs_grow_both_cards()
    {
        KleeOverhaulLedger.ResetAll();
        var klee = Seat.Klee();
        var a = Mutable(new ProtoKoWitchsHomeworkNext());
        var b = Mutable(Upgraded<ProtoKoWitchsHomeworkNext>());
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature,
            new ProtoBombPower.ProtoCharge(20, false, 0, new CardModel[] { a, b }));
        Assert.Equal(2, ((IHomeworkCard)a).HomeworkGrowth);
        Assert.Equal(3, ((IHomeworkCard)b).HomeworkGrowth);
        KleeOverhaulLedger.ResetAll();
    }

    // ==== D. The tempo relic ==================================================

    [Fact]
    public void The_tempo_relic_is_pounding_surprise_plus_a_bomb_six_at_combat_start()
    {
        var relic = (PoundingSurpriseNext)RuntimeHelpers
            .GetUninitializedObject(typeof(PoundingSurpriseNext));
        Assert.Equal(RelicRarity.Starter, relic.Rarity);
        Assert.EndsWith(
            "At the start of each combat, place a [gold]Bomb[/gold] [blue]6[/blue] "
          + "on a random enemy.", RelicFace(relic));
        Assert.StartsWith("Whenever a [gold]Bomb[/gold] goes off, gain [blue]1[/blue] "
                        + "[gold]Spark[/gold].", RelicFace(relic));
        Assert.Equal(6, PoundingSurpriseNext.OpeningBomb);
        Assert.IsAssignableFrom<IProtoExplosionListener>(relic);

        // Placed at BeforeCombatStart, which runs before the first StartTurn;
        // turn 1's BeforeSideTurnStart grows it by rule 1 before she acts.
        Assert.Contains("ProtoBombPower.PlaceOnRandom",
                        Il.Calls(Il.Method("PoundingSurpriseNext", "BeforeCombatStart")));
        Assert.Contains("ProtoBombPower.GrowBy",
                        Il.Calls(Il.Method("ProtoBombPower", "BeforeSideTurnStart")));
        Assert.Equal(10, PoundingSurpriseNext.OpeningBomb + KleeOverhaulLaw.BombGrowth);

        // It replaces the original when granted, and Orobas upgrades it the same way.
        Assert.Contains("RelicCmd.Remove",
                        Il.Calls(Il.Method("PoundingSurpriseNext", "AfterObtained")));
        Assert.Contains("ModelDb.Relic",
                        string.Join(" ", Il.Calls(Il.Method("PoundingSurpriseNext",
                                                            "GetUpgradeReplacement"))));
    }

    [Fact]
    public void The_tempo_relic_is_a_pool_member_and_offered_nowhere()
    {
        Assert.DoesNotContain(typeof(PoundingSurpriseNext), ArmRelicPools.KleeArmPool);
        Assert.Contains("ModelDb.Relic<PoundingSurpriseNext>",
                        Il.CallSequence(Il.Method("KleeRelicPool", "GenerateAllRelics")));
    }

    // ==== helpers =============================================================

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static string RelicFace(RelicModel relic) =>
        ((ILocalizationProvider)relic).Localization!.Single(r => r.Item1 == "description").Item2;

    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    private static T Owned<T>(T card, Seat owner) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", owner.Player);
        return card;
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static decimal Preview(DynamicVar var, CardModel card, bool hooks)
    {
        var.UpdateCardPreview(card, CardPreviewMode.Normal, null, runGlobalHooks: hooks);
        return var.PreviewValue;
    }

    private static ProtoBombPower.ProtoCharge Marked(CardModel card) =>
        new(10, false, 0, new[] { card });

    private static T Give<T>(Seat seat) where T : RelicModel
    {
        var relic = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        Seat.Set(relic, "IsMutable", true);
        Seat.Set(relic, "Owner", seat.Player);
        ((List<RelicModel>)typeof(MegaCrit.Sts2.Core.Entities.Players.Player)
            .GetField("_relics", HeadlessGame.All)!.GetValue(seat.Player)!).Add(relic);
        return relic;
    }

    /// <summary>The `relocated` flag each `Place` call in a method passes,
    /// read off the IL: the argument pushed last before the call
    /// (`relocated` is <c>Place</c>'s final parameter).</summary>
    private static List<bool> PlaceFlags(string type, string method)
    {
        var bodies = (IEnumerable<MethodBase>)typeof(Il)
            .GetMethod("Bodies", HeadlessGame.All)!
            .Invoke(null, new object[] { Il.Method(type, method) })!;
        var flags = new List<bool>();
        foreach (var body in bodies)
        {
            var il = body.GetMethodBody()?.GetILAsByteArray();
            if (il == null) continue;
            for (var i = 1; i + 5 <= il.Length; i++)
            {
                if (il[i] != 0x28) continue;
                MethodBase? target;
                try
                {
                    target = body.Module.ResolveMethod(BitConverter.ToInt32(il, i + 1));
                }
                catch
                {
                    continue;
                }
                if (target?.Name != "Place" || target.DeclaringType != typeof(ProtoBombPower))
                {
                    continue;
                }
                Assert.True(il[i - 1] == 0x16 || il[i - 1] == 0x17,
                            $"{method}: the argument before Place is 0x{il[i - 1]:X2}");
                flags.Add(il[i - 1] == 0x17);
            }
        }
        Assert.NotEmpty(flags);
        return flags;
    }
}
