using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Powers;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 16, and it is round 15's list one debuff and one keyword further on:
/// a rule stated in words narrower than the rule, found by a seat that ran the
/// experiment and read the wrong sentence off the screen afterwards.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round16Tests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    /// <summary>
    /// The literal text one tip attach prints, read off the compiled method --
    /// `Round15Tests`' own reader, and its note applies here unchanged:
    /// enumerating a tip is not reachable headless because every yielded
    /// `HoverTip` formats its title through `LocManager.Instance`, null until
    /// the game boots.
    /// </summary>
    private static string Printed(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method, All)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    // ==================================================================
    // `EB-481` -- "Receive 50% more damage from Attacks", and a Skill that
    //             took the 1.5x
    // ==================================================================
    //
    // THE FIND (Kokomi r16 (c) 2), and it is `EB-469`'s twin one debuff over:
    // the status line says "from Attacks", the glossary said "every hit", and
    // `Kurage's Oath` -- printed `cost 1, skill` -- took the 1.5x. So the
    // glossary was right and the pair still disagreed, which is a player
    // sequencing badly off whichever of the two it read.
    //
    // THE ENGINE IS NOT WHAT IS WRONG, the same finding as the twin's.
    // `VulnerablePower` is the TARGET's own power and its
    // `ModifyDamageMultiplicative` asks `props.IsPoweredAttack()` -- a
    // property of the HIT -- while the generator emits `ValueProp.Move` for
    // every `op: damage` clause whatever `type:` the row declares.

    [Fact]
    public void A_skills_damage_clause_is_read_by_vulnerable_as_an_attack_hit()
    {
        // THE CARD IS A SKILL, and it is the exact card the seat watched take
        // the 1.5x -- the same one `EB-469` watched lose 25%.
        var oath = new ProtoKkKuragesOath();
        Assert.Equal(CardType.Skill, oath.Type);

        var vars = ((IEnumerable<DynamicVar>)typeof(ProtoKkKuragesOath)
            .GetProperty("CanonicalVars", All)!.GetValue(oath)!).ToList();
        var damage = vars.OfType<DamageVar>().Single();
        Assert.Equal(ValueProp.Move, damage.Props);
        Assert.True(damage.Props.IsPoweredAttack());

        // AND THE GAME'S OWN POWER AGREES, run for real rather than reasoned
        // about. `VulnerablePower` sits on the creature TAKING the hit and
        // guards on `target == Owner`, which is the shape `AuraPower` was
        // written against; the card is never handed to it at all.
        var wearer = Seat.Kokomi(30).WithPower<VulnerablePower>(1);
        var attacker = Seat.Kokomi();
        var vulnerable =
            wearer.Creature.Powers.OfType<VulnerablePower>().Single();

        Assert.Equal(1.5m, vulnerable.ModifyDamageMultiplicative(
            wearer.Creature, 0m, damage.Props, attacker.Creature, null, null));

        // 3 x 1.5 = 4.5, and the seat read the whole 1.5x off the body.
        Assert.Equal(3m, damage.BaseValue);
    }

    [Fact]
    public void The_vulnerable_tip_names_the_case_the_status_line_leaves_open()
    {
        var body = Printed(typeof(BaseKeywordTips), "ForVulnerable");

        Assert.Equal(
            "The wearer takes 50% more damage from every hit it takes, a "
          + "Skill's damage too. One stack falls off at the end of each of "
          + "its turns.", body);
        // The tip a player hovers is inside the in-game box either way, and
        // it is exactly its twin's length.
        Assert.True(body.Length <= 135, body.Length.ToString());
        Assert.Equal(Printed(typeof(BaseKeywordTips), "ForWeak").Length,
                     body.Length);
    }

    // ==================================================================
    // `EB-490` -- the tax nobody was paying, and the two clauses that
    //             pointed opposite ways
    // ==================================================================
    //
    // THE FIND (Klee r16 (c)). The Gardener's "first time it is hit each turn,
    // it gains 6 Block" never triggered on a Set off -- which is most of why
    // Klee beats that elite -- and nothing printed says so. The seat "planned
    // two turns around a tax it was not paying" and learned the rule by
    // autopsy from a 26-HP body dying to 30 points of Bomb.
    //
    // WHY THE WORDS AND NOT THE RULE. `EB-443` put both halves on the tip:
    // "Block stops them" and "no Attack trigger fires". They are each true and
    // together they point opposite ways for a reader who does not already know
    // Skittish is an ON-HIT power -- the first says a Bomb interacts with what
    // the enemy has, the second says a Bomb sets nothing off, and "Attack
    // trigger" reads as something on the player's own side of the board.

    private static string SetOffTip() =>
        Printed(typeof(ArmKeywordTips), "ForSetOff");

    [Fact]
    public void The_set_off_tip_names_the_powers_on_the_enemys_status_bar()
    {
        Assert.Contains("no when-hit power fires", SetOffTip());
        Assert.DoesNotContain("Attack trigger", SetOffTip());
        // The Block clause is untouched: the pair was the problem, not either
        // half, and dropping one would put `EB-443`'s finding back.
        Assert.Contains("[gold]Block[/gold] stops them", SetOffTip());
    }

    [Fact]
    public void Renaming_the_class_cost_the_ceiling_nothing()
    {
        // "Attack trigger" and "when-hit power" are the same fourteen
        // characters, so `EB-443`'s 132-of-135 reading stands as published.
        var rendered = SetOffTip()
            .Replace("[gold]", string.Empty).Replace("[/gold]", string.Empty);
        Assert.Equal(132, rendered.Length);
    }

    [Fact]
    public void A_set_off_hands_the_hit_no_attacker_so_skittish_cannot_fire()
    {
        // THE BEHAVIOURAL HALF, and it is STRUCTURAL for `EB-343`'s reason:
        // an explosion needs a live `CombatState` (the README's headless
        // boundary), so what a test can read is which method the call site
        // calls and what that method's one damage call passes.
        //
        // The explosion asks the funnel for the dealer-free door...
        var explode = typeof(ProtoBombPower)
            .GetMethod("Explode", All)!;
        Assert.Contains(Il.Calls(explode),
                        c => c == "ElementalHit.DealWithoutDealerMods");

        // ...and that door's `powered: false` path reaches `CreatureCmd.Damage`
        // as an UNPOWERED hit with NO DEALER. A power keyed on being hit by an
        // Attack therefore has neither an attacker nor a powered hit to answer,
        // which is the whole of why Skittish stays unfired. Read off the source
        // because an argument's VALUE is invisible to `Il`.
        var source = Source("Powers/ElementalHit.cs");
        Assert.Contains(
            "await CreatureCmd.Damage(\n"
          + "            choiceContext, target, landed,\n"
          + "            ignoreBlock ? ValueProp.Unpowered | "
          + "ValueProp.Unblockable\n"
          + "                        : ValueProp.Unpowered,\n"
          + "            dealer: null, cardSource: null, cardPlay: null);",
            source.Replace("\r\n", "\n"));
        Assert.Contains(
            "ignoreBlock: false, powered: false);",
            source.Replace("\r\n", "\n"));
    }

    // ==================================================================
    // `EB-485` -- a per-combat purchase priced as a permanent one
    // ==================================================================
    //
    // THE FIND (Furina r10 (c) 1). "It does nothing once your Companion cards
    // are lit" reads as permanent. The lighting is a POWER: it dies with the
    // fight and the 2 Encore is paid again every combat. The seat weighed the
    // Spotlight as bought once and met Chevreuse printing 7 again in fight 2.
    //
    // BOTH SURFACES, because they are read at different moments: the relic
    // once at the top of a run, and the card on the turn the Encore is being
    // spent. THE ARM'S RELIC FACE IS READ AS SOURCE, not off the type -- the
    // gate compiles this suite with `PrototypeCards` alone, so the
    // `FURINA_REFRAME` branch is not in the binary. `Round12Tests` reads the
    // same file the same way for the same reason.

    private static string SpotlightDurationTip() =>
        Printed(typeof(FurinaRiderTips), "ForSpotlightDuration");

    [Fact]
    public void The_relic_line_says_how_long_the_lighting_lasts()
    {
        var relic = Source("Relics/EtherealSpotlightRelic.cs")
            .Replace("\r\n", "\n");

        Assert.Contains(
            "\"Each turn, add an [gold]Ethereal Spotlight[/gold] to your \"\n"
          + "          + \"[gold]Hand[/gold]. It does nothing once your \"\n"
          + "          + \"[gold]Companion[/gold] cards are lit for this "
          + "combat.\"", relic);

        // Inside the 120-character relic ceiling, and at the SAME length the
        // sentence it replaces had: "Each turn" is what paid for the duration.
        const string rendered =
            "Each turn, add an Ethereal Spotlight to your Hand. It does "
          + "nothing once your Companion cards are lit for this combat.";
        Assert.Equal(117, rendered.Length);
    }

    [Fact]
    public void The_card_that_pays_the_encore_carries_the_same_sentence()
    {
        // The attach, on the card and under the arm's own compile gate.
        var card = Source("Cards/Furina/SpotlightCards.cs").Replace("\r\n", "\n");
        Assert.Contains("#if PROTOTYPE_CARDS && FURINA_REFRAME", card);
        Assert.Contains(
            "FurinaRiderTips.ForSpotlightDuration(base.ExtraHoverTips, this)",
            card);

        // And the sentence itself, off the compiled method -- that one is not
        // inside an `#if`, because a tip class is compiled whole and the call
        // site is what the arm gates.
        var body = SpotlightDurationTip();
        Assert.Contains("lasts this combat", body);
        Assert.Contains("Every fight starts unlit", body);
        Assert.True(
            body.Replace("[gold]", string.Empty)
                .Replace("[/gold]", string.Empty).Length <= 135,
            body.Length.ToString());
    }

    [Fact]
    public void The_new_tip_title_is_registered_and_not_a_raw_key()
    {
        // The trap this repo has fallen into twice: a `KLEEMOD-` key with no
        // `.title` row renders AS THE KEY on a live screen, and the pck's
        // `card_keywords.json` carries none of these -- `KleeMod.cs` is their
        // only source (`EB-329`'s note on `CompanionKey`).
        Assert.Equal("KLEEMOD-SPOTLIGHT_LASTS",
                     FurinaRiderTips.SpotlightLastsKey);
        Assert.Contains(
            "[Cards.FurinaRiderTips.SpotlightLastsKey + \".title\"]",
            Source("KleeMod.cs"));
    }

    // ==================================================================
    // `EB-488` -- a reward screen with no glossary for the word on the card
    // ==================================================================
    //
    // THE FIND (Furina r10 (c) 5). `Grand Salon` -- "Salon Member numbers are
    // 1 higher" -- was the run's FIRST card reward, and the seat passed on it
    // partly because it could not price it. The Salon tip had appeared exactly
    // once all run, on `Salon Debut` in fight 1.
    //
    // WHY: the three member paragraphs attach from the EFFECT (which member
    // does this row deploy), which is right for them and wrong for the RULES
    // paragraph -- a face that names the word and deploys nobody is exactly
    // the face whose reader has never met it. So the rules tip attaches from
    // the PRINTED WORD, the way the Companion tip already reaches a reward.

    [Fact]
    public void A_face_that_names_a_salon_member_and_deploys_none_defines_it()
    {
        // The card the finding is about, and it fields nobody at all: its one
        // effect is a Power that raises everyone else's numbers.
        var grandSalon = Source("Cards/Furina/Generated/GrandSalon.cs");
        Assert.Contains("[gold]Salon Member[/gold] numbers are", grandSalon);
        Assert.Contains(
            "SalonMemberTips.ForSalonRules(base.ExtraHoverTips, this)",
            grandSalon);
    }

    [Fact]
    public void Every_furina_face_printing_the_word_carries_the_definition()
    {
        // THE DENOMINATOR, and the reason the attach is DERIVED rather than
        // applied by hand: eight of her shipped faces print the word, only one
        // of them was the seat's, and a row that prints it tomorrow carries
        // the definition because it printed it.
        foreach (var cls in new[] { "GrandSalon", "CastingCall",
                                    "FortissimoGuard", "PitOrchestra",
                                    "TempoChange", "WatersEmbrace",
                                    "ManyWatersMelody", "MatineePerformance" })
        {
            var src = Source("Cards/Furina/Generated/" + cls + ".cs");
            Assert.Contains("[gold]Salon Member", src);
            Assert.Contains("SalonMemberTips.ForSalonRules(", src);
        }
    }

    [Fact]
    public void A_deploy_card_is_left_with_the_one_copy_it_already_had()
    {
        // Two copies of one definition on one face is what the game's own tip
        // de-duplication would then be picking between, so a row that DEPLOYS
        // keeps `ForCard`'s paragraph and takes no second attach.
        foreach (var cls in new[] { "SalonDebut", "EndlessWaltz" })
        {
            var src = Source("Cards/Furina/Generated/" + cls + ".cs");
            Assert.Contains("SalonMemberTips.ForCard(", src);
            Assert.DoesNotContain("SalonMemberTips.ForSalonRules(", src);
        }
    }

    /// <summary>A mod source file, read whole -- `Round12Tests.Printed`'s
    /// idiom and its reason: a stale copy beside the dll is exactly the drift
    /// a text pin exists to catch.</summary>
    private static string Source(string relativePath)
    {
        var relative = System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar));
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

        throw new System.IO.FileNotFoundException(
            "no " + relative + " above " + AppContext.BaseDirectory);
    }
}
