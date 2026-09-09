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

    // `EB-719` RETIRED THIS PIN WITH ITS WORD. `EB-587` put the Evoke's price
    // on `ArmKeywordTips.ForEvoke`, and the word left the mod with the
    // reframe's eleven `proto_fr_` rows under R213 B's deletion rule -- a
    // tooltip for a rule no row prints is a definition of a mechanic that is
    // not there. The PRICE it was about is `SalonPowers`' own and is pinned by
    // `The_dry_cut_has_one_site_and_both_acts_read_it` directly above.

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

    // ==================================================================
    // `EB-580` -- a card's enchantment folds into its Plan line
    // ==================================================================
    //
    // THE FIND (Kokomi r21 lane 2 (c) 3). A Sharp 2 raised Riptide's now-line
    // from 9 to 11 and left its Plan line printing 13, so the pair read as a
    // fact about the card: the Plan premium had shrunk and the now-line was
    // the better half. It "silently reversed the right play on my best card".
    // Ruled at the r21 packet's D default -- a card's own enchantment applies
    // to BOTH its lines, since both are the card's.
    //
    // STRUCTURAL, for this file's standing reason: an `EnchantmentModel` is a
    // live model on a live card and the headless suite has neither, so what a
    // pin reads is that ONE method asks the base game's two calls and that
    // both the number WRITTEN and the number PRINTED go through it. The
    // arithmetic itself is pinned for real in tier0
    // (`test_eb580_an_enchantment_folds_into_the_plan_line.py`).

    [Fact]
    public void The_fold_asks_the_base_game_s_own_two_terms()
    {
        var folded = Il.Calls(Il.Method("KokomiPlan", "Enchanted"));

        Assert.Contains("EnchantmentModel.EnchantDamageAdditive", folded);
        Assert.Contains("EnchantmentModel.EnchantDamageMultiplicative", folded);
        // `ValueProp.Move` and not the planned hit's `Unpowered`, which is the
        // one argument in that method: measured on the shipped assembly,
        // `Corrupted` answers x1.5 to `Move` and x1 to `Unpowered`, so the
        // hit's own prop would have dropped every multiplier.
        var source = Source("Powers/Prototype/KokomiPlan.cs")
            .Replace("\r\n", "\n");
        Assert.Contains(
            "        var folded = amount\n"
          + "                   + enchantment.EnchantDamageAdditive("
          + "amount, ValueProp.Move);",
            source);
    }

    [Fact]
    public void The_number_written_and_the_number_printed_take_the_same_fold()
    {
        // ONE CALL, TWO READERS -- `EB-265`'s rule, and the whole of why the
        // r21 find was legible as a defect at all: a face that folds and a
        // queue that does not is two numbers for one line.
        //
        // `EB-599` PUT HER STRENGTH ON THE SAME CALL, so the shared reader is
        // now `Hers` and the enchantment fold is what it opens with. Both
        // sites still reach `Enchanted`, through one method rather than two.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Hers")),
                        c => c == "KokomiPlan.Enchanted");
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Schedule")),
                        c => c == "KokomiPlan.Hers");
        Assert.Contains(
            Il.Calls(Il.Method("PlanDamageVar", "UpdateCardPreview")),
            c => c == "KokomiPlan.Hers");
    }

    // ==================================================================
    // `EB-589` -- the previewed reaction, folded into a number
    // ==================================================================
    //
    // THE FIND (Furina r15 lane 2 (c) 2). Chevreuse printed 7, 10 and 10 and
    // delivered 11, 15 and 22: "the Spotlight and Weak and Passion Overload
    // are all folded into the number on the face; the previewed 1.5x Vaporize
    // never is. The face is right about four modifiers and silent about the
    // biggest one."
    //
    // AND THE FACE CANNOT FOLD IT, which is why the repair is on the PREVIEW.
    // The amplifier and the target's Vulnerable are per-BODY terms and a card
    // in hand has no target -- so the four modifiers the face does carry are
    // exactly the four that are facts about the player. The reaction preview
    // already walks the board and knows which body raised it, which makes it
    // the one surface that can answer.

    [Fact]
    public void The_reaction_preview_folds_through_EB_559_s_own_reader()
    {
        var folded = Il.Calls(Il.Method("KleeCardTooltips", "AmplifiedBody"));

        // ONE READER, NOT A SECOND COPY: `ResolveOnTarget` is
        // `ElementalHit.Deal`'s own target-mods, truncation and per-hit cap,
        // and it is what `ProtoBombPower.PredictedSetOffDamage` asks for the
        // same question about a pile (`EB-559`).
        Assert.Contains("SimDamagePipeline.ResolveOnTarget", folded);
        Assert.Contains("ReactionTable.AmplifierMultiplier", folded);
        Assert.Contains("KleeCardTooltips.PrintedDamage", folded);

        // PURE, because it is read on every state poll: no command, no
        // counter. `ProtoBombPower.PendingReactionMultiplier`'s rule, and this
        // is the same claim about the same kind of surface.
        Assert.DoesNotContain(folded,
                              c => c.StartsWith("Cmd.", StringComparison.Ordinal)
                                || c.Contains("Cmd."));
    }

    [Fact]
    public void And_the_preview_substitutes_the_body_rather_than_a_new_row()
    {
        // The substitution mechanism is `EB-338`'s and the two title keys are
        // its two: Vaporize and Melt are the only reactions that amplify
        // (`ReactionTable.AmplifierMultiplier`), and they are exactly the pair
        // `NoHitTitleKey` already names -- so an amplified body always has a
        // registered title row to print under.
        var forCard = Il.Calls(Il.Method("KleeCardTooltips", "ForCard"));

        Assert.Contains("KleeCardTooltips.AmplifiedBody", forCard);
        Assert.Contains("KleeCardTooltips.NoHitTitleKey", forCard);

        var table = Source("Elements/ReactionTable.cs");
        var amp = MethodBody(
            table, @"public\s+static\s+decimal\s+AmplifierMultiplier\s*\(\s*Reaction");
        Assert.Contains("Reaction.Vaporize", amp);
        Assert.Contains("Reaction.Melt", amp);
        Assert.Contains("_ => 1m", amp);
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
