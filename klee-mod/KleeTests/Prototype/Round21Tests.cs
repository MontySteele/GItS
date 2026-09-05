using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND TWENTY-ONE -- the Furina round-15 and Kokomi round-21 act-one runs of
/// 2026-09-06 (`review/active/furina-reframe-round-15-2026-09-06.md`,
/// `review/active/kokomi-overhaul-round-21-2026-09-06.md`) and the rows they
/// left behind on the C# side.
///
/// WHAT THIS FILE HOLDS. Three of the four rows here are about a NUMBER, and a
/// number in this mod needs a live `CombatState` -- the README's headless
/// boundary -- so what a pin can read is which method a call site calls and
/// what that call passes. That is <see cref="Round19Tests"/>' arrangement and
/// the reason for it, unchanged: the behavioural claim is pinned for real in
/// tier0, where the same rule is one function, and the STRUCTURAL claim is
/// pinned here so the two engines cannot drift apart quietly.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class Round21Tests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>A tip's printed body, keys dropped.
    /// <see cref="Round19Tests"/>' helper, verbatim.</summary>
    private static string Printed(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method, All)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    // ==================================================================
    // `EB-588` -- a performance is not an Attack, so Weak does not move it
    // ==================================================================
    //
    // THE FIND (Furina r15 lane 2 (c) 4). Weak cut a member performance from 6
    // to 4 twice, while the Salon paragraph on the same screen says "a
    // performance is not an Attack and not a hit: Vulnerable moves it" and
    // names no Weak. The row's D default is that the text stands.
    //
    // THE TEXT WAS RIGHT AND THE MIRROR WAS THE DEFECT. The hit already
    // reached `CreatureCmd.Damage` as `ValueProp.Unpowered` with `dealer:
    // null`; what was still running was `SimDamagePipeline.DealerMods`, one
    // stage above it, which is where the Weak came from. `powered: false` is
    // the engines' one flag for exactly that stage.

    [Fact]
    public void A_performance_asks_the_funnel_for_an_unpowered_hit()
    {
        // STRUCTURAL, and read off the SOURCE because an argument's VALUE is
        // invisible to `Il` -- `Round19Tests` reads `ElementalHit`'s own call
        // the same way for the carry-out.
        var source = Source("Powers/SalonPowers.cs").Replace("\r\n", "\n");

        Assert.Contains(
            "landed = await ElementalHit.Deal(\n"
          + "                    choiceContext, target, Elements.Element.Hydro,\n"
          + "                    amount, owner, powered: false);",
            source);

        // And it is still the elemental funnel and never the Attack door,
        // which is the OTHER half of "not a card being played" and the half
        // `EB-548` pinned.
        Assert.Contains(Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
                        c => c == "ElementalHit.Deal");
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
            c => c.StartsWith("DamageCmd.", StringComparison.Ordinal));
    }

    [Fact]
    public void The_flag_that_drops_the_weak_is_the_one_that_drops_strength()
    {
        // ONE FLAG AND NOT TWO, which is `ElementalHit.Deal`'s own written
        // rule and worth a pin because "skip the Weak but keep the Strength"
        // is the obvious wrong fix: it would need a second parameter meaning
        // half of `Unpowered`, and two flags for one pipeline stage is what
        // that doc refuses. Read off `DealerMods`, which is the one stage
        // `powered` gates.
        var pipeline = Source("Powers/SimDamagePipeline.cs");
        var mods = MethodBody(pipeline, @"public\s+static\s+decimal\s+DealerMods\s*\(");

        Assert.Contains("StrengthPower", mods);
        Assert.Contains("WeakPower", mods);
    }

    // ==================================================================
    // `EB-587` -- the Evoke is a performance and pays like one
    // ==================================================================
    //
    // THE FIND (Furina r15 lane 1 (c) 1). At 0 Encore three performances
    // printed and landed dry at three-quarters while the Evoke on the same
    // turn delivered its full 14 -- the one act that also costs a member was
    // the one act the economy did not price. The tip's explanation for that
    // ("the card's Encore price pays for it", `F7` (1)) is FALSE on Curtain
    // Rises, which Evokes by deploying onto a full stage and prints no Encore
    // price at all.

    [Fact]
    public void An_evoke_pays_the_upkeep_through_the_performance_s_own_reads()
    {
        // ONE QUESTION, ONE OWNER. "Can this act afford the upkeep" is
        // `PerformancePays`, and the Evoke asks IT rather than spelling the
        // comparison a second time -- the same discipline that keeps a member
        // performing to one implementation.
        var bow = Il.Calls(Il.Method("SalonMemberPower", "Bow"));

        Assert.Contains("SalonMemberPower.PerformancePays", bow);
        Assert.Contains("FurinaResources.SpendEncore", bow);
        Assert.Contains("SalonMemberPower.Dry", bow);
    }

    [Fact]
    public void The_dry_cut_has_one_site_and_both_acts_read_it()
    {
        // A performance and an Evoke take the SAME cut, so the arithmetic is
        // one method rather than two casts that agree today. `TickValue` is
        // the performance's reader and `Bow` is the Evoke's.
        Assert.Contains(Il.Calls(Il.Method("SalonMemberPower", "TickValue")),
                        c => c == "SalonMemberPower.Dry");

        var source = Source("Powers/SalonPowers.cs").Replace("\r\n", "\n");
        Assert.Contains(
            "    private static int Dry(int amount, bool paid) =>\n"
          + "        paid ? amount : (int)(amount * "
          + "SalonConstants.DryDamageMultiplier);",
            source);
    }

    [Fact]
    public void The_evoke_word_prints_the_price_and_not_the_old_promise()
    {
        // The numerals are INTERPOLATED from the constants they quote
        // (`EB-89`), so the IL literals hold the prose either side of them --
        // the same fold-out `test_understudy_blindplay`'s glossary table
        // already makes for this word.
        var word = Printed(typeof(ArmKeywordTips), "ForEvoke");

        Assert.Contains("It spends ", word);
        Assert.Contains(" [gold]Encore[/gold], or Evokes at 3/4.", word);
        // The retired sentence, by name: it was false on Curtain Rises.
        Assert.DoesNotContain("price pays", word);
    }

    // ==================================================================
    // `EB-591` -- Courtroom Drama's clause order is on its face
    // ==================================================================
    //
    // THE FIND (Furina r15 lane 2 (c) 3). "Courtroom Drama's Vulnerable boosts
    // the hit that triggered it. 50 -> 19 from one 1-cost card. Nothing
    // printed suggests the debuff lands early enough to amplify its own
    // trigger."
    //
    // THE ENGINE IS NOT WHAT MOVED. That phase is RULED and pinned in BOTH
    // engines -- `tier0/tests/test_reaction_phase_parity.py`'s
    // "courtroom-drama-vulnerable-is-multiplicative" row, EB-19/M1 -- and the
    // pin exists because the mod once landed it a hook LATE and paid two
    // different numbers for one reaction depending on whether a bomb or a card
    // caused it. So the face moved to the engines, not the reverse.

    [Fact]
    public void The_face_says_the_vulnerable_moves_the_hit_that_applied_it()
    {
        var card = Source("Cards/Furina/Generated/CourtroomDrama.cs");
        var power = Source("Powers/CurtainCallPowers.cs");

        foreach (var surface in new[] { card, power })
        {
            Assert.Contains("[gold]Vulnerable[/gold] moves that hit.",
                            surface);
        }
    }

    [Fact]
    public void The_card_and_its_badge_are_the_same_sentence()
    {
        // TWO SURFACES, ONE RULE. The generated face comes from
        // `gen_klee_cards.POWER_DESCRIPTIONS` and the badge is hand-written,
        // so nothing but a pin holds them together -- and a player meets the
        // badge for the rest of the run after meeting the card once.
        var card = Source("Cards/Furina/Generated/CourtroomDrama.cs");
        var power = Source("Powers/CurtainCallPowers.cs");

        foreach (var clause in new[]
                 {
                     "Your first [gold]Elemental Reaction[/gold] each turn ",
                     "[gold]Vulnerable[/gold] and ",
                     "[gold]Weak[/gold] ",
                     "to its target. The [gold]Vulnerable[/gold] moves that "
                   + "hit.",
                 })
        {
            Assert.Contains(clause, card);
            Assert.Contains(clause, power);
        }
    }

    // ==================================================================
    // `EB-592` -- a card hit is still a hit
    // ==================================================================
    //
    // THE FIND (Furina r15 lane 2 (c) 1). "Skittish 6 never fired. B was at
    // 12, took the 13-damage Chevreuse and died... On the same turn, a dry
    // 4-damage performance took A from 25 to exactly 21." Round 14 on
    // `0.2.2753+proto` had seen the same power fire on card hits, so the
    // reading was that a card hit had stopped counting between the builds.
    //
    // IT HAD NOT. The diff over `klee-mod/KleeCode` across that range touches
    // tips, the R260 opening arrival, the Evoke's log row and the Spotlight
    // window line -- and not one line of the door a Companion Attack goes
    // through. Both of the seat's own observations are rules that were already
    // there: a KILLING hit grants Block to nobody (the base game's own IsDead
    // guard at the funnel), and a performance is not a hit (`EB-548`).

    [Fact]
    public void A_companion_attack_still_goes_through_the_powered_door()
    {
        // The card the seat was holding, read off its own emitted `OnPlay`:
        // `DamageCmd.Attack(...).FromCard(...)` is a POWERED hit with a
        // dealer and a card source, which is what a when-hit power answers --
        // the exact opposite of the unpowered door a performance, a carry-out
        // and a Bomb take.
        var card = Source(
            "Cards/Generated/ChevreuseInterdictionFire.cs")
            .Replace("\r\n", "\n");

        Assert.Contains("await DamageCmd.Attack(DynamicVars.CalculatedDamage)\n"
                      + "            .FromCard(this, cardPlay)", card);
        Assert.DoesNotContain("ElementalHit.Deal", card);
    }

    [Fact]
    public void And_the_performance_beside_it_still_does_not()
    {
        // The pair the seat compared, in one place: same fight, same bodies,
        // two doors. `EB-548`'s rule, re-read here because `EB-592` is the
        // question of whether it had widened to swallow card hits too.
        Assert.Contains(Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
                        c => c == "ElementalHit.Deal");
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
            c => c.StartsWith("DamageCmd.", StringComparison.Ordinal));
    }

    // ------------------------------------------------------------ helpers --

    /// <summary>The body of a method matched by <paramref name="signature"/>,
    /// braces balanced. `tier0/tests/test_reaction_phase_parity.py`'s
    /// `method_body`, in C#.</summary>
    private static string MethodBody(string source, string signature)
    {
        var match = System.Text.RegularExpressions.Regex.Match(
            source, signature);
        Assert.True(match.Success, signature);
        var start = source.IndexOf('{', match.Index);
        var depth = 0;
        for (var i = start; i < source.Length; i++)
        {
            if (source[i] == '{') depth++;
            else if (source[i] == '}' && --depth == 0)
            {
                return source[start..(i + 1)];
            }
        }

        throw new InvalidOperationException($"unbalanced braces: {signature}");
    }

    /// <summary>A source file under `klee-mod/KleeCode`.
    /// <see cref="Round19Tests"/>' helper, verbatim.</summary>
    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
