using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE LATER-ACT SEAT ROUNDS OF 2026-09-26 -- the mod-side half of the
/// screen/outcome defects five blind seats and one full run reported
/// (`review/qa/seats-2026-09-26/`, gitignored). The page-side half is in
/// `tier0/tests/test_understudy_blindplay.py`.
///
/// WHAT A PIN HERE CAN AND CANNOT SAY: a hit, a placement and a transform all
/// run through commands that need a live combat or a booted `ModelDb`
/// (KleeTests README, "The headless boundary"). So every decision that can be
/// taken purely is RUN, and the rest is read off the call graph and labelled
/// STRUCTURAL.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeSeatDefects20260926Tests
{
    private static readonly BindingFlags All = HeadlessGame.All;

    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();

    // ==================================================================
    // 1. Sizzle+ printed "18 additional" and landed 10
    // ==================================================================

    [Fact]
    public void An_additional_leg_after_the_cards_own_hit_previews_without_a_reaction()
    {
        // The act-3 lane-3 seat: Sizzle+ into a Cryo-wearing, Vulnerable
        // enemy printed 18 (7 x 1.5 x 1.75 Melt) and the extra hit landed 10,
        // because the card's own Pyro Set off and hit had used the aura up.
        foreach (var card in new CardModel[]
                 { new ProtoKoSizzle(), new ProtoMiShinobuThundergrust() })
        {
            var branch = Assert.IsType<FoldedDamageVar>(
                Vars(card).Single(v => v.Name == "BranchDamage"));
            Assert.True(branch.FollowsHit, card.GetType().Name);
        }

        // A two-armed face's branch IS the hit (Press the Advantage: "... If
        // a Plan is waiting, deal 10 instead"; Feint until the Casket pass
        // re-keyed it, 2026-09-28), so it keeps the fold it had.
        var press = Assert.IsType<FoldedDamageVar>(
            Vars(new ProtoKkPressTheAdvantage())
                .Single(v => v.Name == "BranchDamage"));
        Assert.False(press.FollowsHit);
    }

    [Fact]
    public void The_reaction_fold_is_off_only_inside_the_preview_scope()
    {
        Assert.False(AuraPower.ReactionFoldSuppressed);
        using (AuraPower.PreviewWithoutReaction())
        {
            Assert.True(AuraPower.ReactionFoldSuppressed);
            var inner = AuraPower.PreviewWithoutReaction();
            inner.Dispose();
            inner.Dispose();                 // a second close is a no-op
            Assert.True(AuraPower.ReactionFoldSuppressed);
        }
        Assert.False(AuraPower.ReactionFoldSuppressed);

        // STRUCTURAL: the term reads the scope, and the var opens it.
        var term = typeof(AuraPower).GetMethod(
            "ModifyDamageMultiplicative", All)!;
        Assert.Contains("AuraPower.get_ReactionFoldSuppressed", Il.Calls(term));
        var preview = typeof(FoldedDamageVar).GetMethod(
            "UpdateCardPreview", All)!;
        Assert.Contains("AuraPower.PreviewWithoutReaction", Il.Calls(preview));
    }

    // ==================================================================
    // 2. Big Badda Boom paid the target's Vulnerable twice
    // ==================================================================

    [Fact]
    public void The_echo_base_takes_each_explosions_vulnerable_back_out()
    {
        // The lane-2 full run's Terror Eel, Vulnerable: "BBB read 12, 7, 18,
        // 28" -- the Bombs landed 12 and 7, and the echo was 19 x 1.5.
        KleeOverhaulLedger.ResetAll();
        var ledger = new KleeOverhaulLedger();
        ledger.RollTo(1);
        ledger.BeginPlay();
        ledger.NoteExplosion(reacted: false, damageDealt: 12, vulnerablePaid: true);
        ledger.NoteExplosion(reacted: false, damageDealt: 7, vulnerablePaid: true);

        Assert.Equal(19, ledger.DamageSetOffThisPlay);
        // What the echo lands once the game applies the Vulnerable ONCE.
        Assert.Equal(19, (int)(ledger.SetOffEchoBaseThisPlay * 1.5m));

        // A body that was not Vulnerable pays the whole number, as before.
        ledger.BeginPlay();
        ledger.NoteExplosion(reacted: false, damageDealt: 6);
        Assert.Equal(6m, ledger.SetOffEchoBaseThisPlay);

        // And a new play starts empty.
        ledger.BeginPlay();
        Assert.Equal(0m, ledger.SetOffEchoBaseThisPlay);
    }

    [Fact]
    public void The_rounding_never_loses_a_point_the_bombs_dealt()
    {
        for (var dealt = 1; dealt <= 400; dealt++)
        {
            var once = KleeOverhaulLedger.EchoBase(dealt, vulnerablePaid: true);
            Assert.Equal(dealt, (int)(once * 1.5m));
        }
        // Summed, too: a pile of many small charges.
        var sum = Enumerable.Range(1, 60)
            .Sum(d => KleeOverhaulLedger.EchoBase(d, vulnerablePaid: true));
        Assert.Equal(Enumerable.Range(1, 60).Sum(), (int)(sum * 1.5m));
    }

    [Fact]
    public void The_echo_hits_for_the_echo_base_and_the_explosion_says_what_it_paid()
    {
        // STRUCTURAL: both are inside async command bodies.
        var echo = typeof(ProtoBombPower).GetMethod("DealSetOffTotal", All)!;
        Assert.Contains("KleeOverhaulLedger.get_SetOffEchoBaseThisPlay",
                        Il.Calls(echo));
        Assert.DoesNotContain("KleeOverhaulLedger.get_DamageSetOffThisPlay",
                              Il.Calls(echo));

        var explode = typeof(ProtoBombPower).GetMethod("Explode", All)!;
        var calls = Il.CallSequence(explode).ToList();
        var hit = calls.IndexOf("ElementalHit.DealWithoutDealerMods");
        var reads = calls.Select((c, i) => (c, i))
            .Where(p => p.c == "ProtoBombPower.HasVulnerable")
            .Select(p => p.i).ToList();
        // Read on both sides of the hit, and before Explosive Frags lays one
        // this hit did not pay.
        Assert.Contains(reads, i => i < hit);
        Assert.Contains(reads, i => i > hit);
        var frags = calls.IndexOf("MineFragsPower.OnMineWentOff");
        Assert.True(reads.Max() < frags);
    }

    // ==================================================================
    // 3. Coven Errand demanded a target in its ALL case
    // ==================================================================

    [Fact]
    public void Coven_errand_always_aims_since_the_aoe_trim()
    {
        // AoE trim (2026-10-03): Coven Errand places ONE Bomb on an enemy
        // either way, so it no longer answers AllEnemies while its predicate
        // holds -- the override is gone and the card always aims.
        Assert.Null(typeof(ProtoKoCovenErrand).GetProperty(
            "TargetType", All | BindingFlags.DeclaredOnly));
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoCovenErrand().TargetType);

        // Team Effort widens its Set off too, but its HIT still lands on the
        // aimed enemy, so it keeps its target.
        Assert.Null(typeof(ProtoKoTeamEffort).GetProperty(
            "TargetType", All | BindingFlags.DeclaredOnly));
    }

    // ==================================================================
    // 6. Sit Tight's status read "Sit Tight 4" on a turn it could not pay
    // ==================================================================

    [Fact]
    public void Sit_tight_says_so_once_a_bomb_of_hers_has_gone_off()
    {
        Assert.Equal("X.smartDescription", SitTightPower.FaceKey("X", pays: true));
        Assert.Equal("X." + SitTightPower.SpentKey,
                     SitTightPower.FaceKey("X", pays: false));

        var rows = ((ILocalizationProvider)System.Runtime.CompilerServices
                .RuntimeHelpers.GetUninitializedObject(typeof(SitTightPower)))
            .Localization!;
        Assert.Contains(rows, r => r.Item1 == SitTightPower.SpentKey);
        // The paying face has NO smart row, so it falls back to the plain one.
        Assert.DoesNotContain(rows, r => r.Item1 == "smartDescription");

        // RUN, on a seat: the face follows the ledger.
        KleeOverhaulLedger.ResetAll();
        var seat = Seat.Klee().WithPower<SitTightPower>(4);
        var power = seat.Creature.Powers.OfType<SitTightPower>().Single();
        Seat.Force(power, "Id", new ModelId("POWER", "KLEE_SIT_TIGHT_TEST"));
        var key = typeof(SitTightPower).GetProperty(
            "SmartDescriptionLocKey", All)!;
        Assert.EndsWith(".smartDescription", (string)key.GetValue(power)!);
        KleeOverhaulLedger.For(seat.Creature).NoteExplosion(false, 5);
        Assert.EndsWith("." + SitTightPower.SpentKey,
                        (string)key.GetValue(power)!);
        KleeOverhaulLedger.ResetAll();
    }

    // ==================================================================
    // 9. The Bomb a card places on the body its own hit just killed
    // ==================================================================

    [Fact]
    public void A_charge_placed_on_a_body_that_is_gone_jumps()
    {
        // The lane-1 full run: "Bang Bang!+ killed the Egg. The `Place a
        // Bomb 6` part never showed up on the board." RUN: the test Place
        // takes.
        var klee = Seat.Klee().Creature;
        var alive = Seat.Klee(30).Creature;
        var dead = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee, alive, dead);
        Seat.Set(dead, "CurrentHp", 0);
        Assert.False(ProtoBombPower.LandsOnNobody(alive));
        Assert.True(ProtoBombPower.LandsOnNobody(dead));
        // Torn out of the combat entirely.
        Assert.True(ProtoBombPower.LandsOnNobody(Seat.Klee(30).Creature));

        // STRUCTURAL: the refusal hands the charge to rule 3.
        var place = typeof(ProtoBombPower).GetMethod("Place", All)!;
        var calls = Il.Calls(place);
        Assert.Contains("ProtoBombPower.LandsOnNobody", calls);
        Assert.Contains("ProtoBombPower.JumpCharges", calls);
    }

    // ==================================================================
    // 8. A transform of her borrowed basics offered Ironclad's pool
    // ==================================================================

    [Fact]
    public void The_transform_patch_targets_the_method_the_base_game_declares()
    {
        // REAL: Harmony binds a prefix's arguments by NAME.
        var method = AccessTools.DeclaredMethod(
            typeof(CardFactory), "GetDefaultTransformationOptions");
        Assert.NotNull(method);
        Assert.True(method!.IsStatic);
        Assert.Equal(new[] { "original", "isInCombat" },
                     method.GetParameters().Select(p => p.Name));

        var patch = typeof(ArmTransformPool).Assembly.GetTypes()
            .Single(t => t.Name == "CardFactory_ArmTransformPool_Patch");
        Assert.Contains(patch.GetCustomAttributes(inherit: true)
                            .OfType<HarmonyPatch>().Select(a => a.info),
                        i => i.declaringType == typeof(CardFactory)
                             && i.methodName == "GetDefaultTransformationOptions");
        var prefix = patch.GetMethod("Prefix", All)!;
        Assert.Equal(typeof(bool), prefix.ReturnType);
        Assert.Equal(new[] { "original", "isInCombat", "__result" },
                     prefix.GetParameters().Select(p => p.Name));
        Assert.Contains("ArmTransformPool.OptionsFor", Il.Calls(prefix));

        // The base game's own filter, which the prefix runs over her pool.
        var filter = ArmTransformPool.FilterMethod;
        Assert.NotNull(filter);
        Assert.Equal(new[] { typeof(CardModel), typeof(IEnumerable<CardModel>),
                             typeof(bool) },
                     filter!.GetParameters().Select(p => p.ParameterType));
        Assert.Contains("CardPoolModel.GetUnlockedCards",
                        Il.Calls(Il.Method("ArmTransformPool", "OptionsFor")));
    }

    [Fact]
    public void Varka_s_borrowed_basics_transform_into_his_own_pool()
    {
        // 2026-09-30 co-op playtest: Morphic Grove and Astrolabe turned his
        // Silent Strikes and Defends into Silent cards. The seam's character
        // test now names him: OptionsFor carries an `isinst IVarkaCharacter`.
        var method = (MethodInfo)Il.Method("ArmTransformPool", "OptionsFor");
        var il = method.GetMethodBody()!.GetILAsByteArray()!;
        var tested = new List<Type>();
        for (var i = 0; i + 4 < il.Length; i++)
        {
            if (il[i] != 0x75) continue;              // isinst <token>
            var token = BitConverter.ToInt32(il, i + 1);
            try { tested.Add(method.Module.ResolveType(token)); }
            catch (ArgumentException) { }
        }
        Assert.Contains(typeof(IVarkaCharacter), tested);
        Assert.Contains(typeof(IKokomiCharacter), tested);
    }
}
