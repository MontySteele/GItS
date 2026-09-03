using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-338`: THE REACTION PREVIEW ON A CARD WITH NO HIT.
///
/// WHAT THE SEAT SAW (`klee round 7b, opus-act2b.md`,
/// finding 4). Barbara's stand-in -- "Gain 6 Block. Apply Hydro" -- carried
/// *"Reaction preview: Vaporize -- The triggering hit deals 1.5x damage and
/// consumes the aura"* over a Pyro aura. The reaction fired and the aura went;
/// the enemy stayed on 23/41. The line advertised an upside and delivered a
/// loss.
///
/// THE RULE DID NOT MOVE, only the words: an application reacts. So this file
/// pins the WORDS, which is what the row asked for.
///
/// WHY THE BODY AND NOT THE TIP. Every `HoverTip` constructor formats its
/// `LocString` through `LocManager.Instance`, which is null headlessly -- the
/// README's fourth boundary -- so a tip set cannot be enumerated end to end.
/// The bodies are plain strings and are asserted directly, exactly as
/// `ArmKeywordTipTests` asserts every other tip body in the mod. The codegen
/// half -- which cards carry the flag -- is pinned in
/// `tier0/tests/test_roster_codegen.py`, where the sheet is.
/// </summary>
public class ReactionPreviewNoHitTests
{
    [Fact]
    public void Only_the_two_amplifiers_are_substituted()
    {
        // The other six reactions land in FULL off an application: Overload's
        // splash, Superconduct's Vulnerable, Electro-Charged's dot, Frozen,
        // Swirl's copy and Crystallize's Block are all paid whether or not the
        // card hit anything. Their printed rows are already true, so the
        // substitution must leave them alone -- and `null` is how
        // `KleeCardTooltips.ForCard` is told to keep the keyword's own tip.
        Assert.NotNull(KleeCardTooltips.NoHitBody(Reaction.Vaporize));
        Assert.NotNull(KleeCardTooltips.NoHitBody(Reaction.Melt));

        foreach (var reaction in Enum.GetValues<Reaction>())
        {
            if (reaction is Reaction.Vaporize or Reaction.Melt) continue;
            Assert.Null(KleeCardTooltips.NoHitBody(reaction));
        }
    }

    [Fact]
    public void The_substituted_body_names_the_case_the_consumption_and_the_loss()
    {
        // The shape is the boss substitution's, which the same seat called
        // excellent on the same card: name the case, name what is still
        // consumed, name what is paid instead. Here what is paid instead is
        // nothing, and saying so is the whole row.
        var vaporize = KleeCardTooltips.NoHitBody(Reaction.Vaporize)!;

        Assert.Contains("deals no damage", vaporize);
        Assert.Contains("still consumed", vaporize);
        Assert.Contains("no hit", vaporize);
        // The number the old line promised, named as the thing that has
        // nothing to multiply rather than dropped.
        Assert.Contains("1.5x", vaporize);
        Assert.Contains("1.75x", KleeCardTooltips.NoHitBody(Reaction.Melt)!);
    }

    [Fact]
    public void The_substituted_body_does_not_promise_a_multiplied_hit()
    {
        // The exact sentence that was wrong, gone from both. The shipped rows
        // in `KleeMod.InjectLocStrings` still carry it -- they are right about
        // a card that hits -- so this is a claim about the SUBSTITUTE only.
        foreach (var reaction in new[] { Reaction.Vaporize, Reaction.Melt })
        {
            var body = KleeCardTooltips.NoHitBody(reaction)!;
            Assert.DoesNotContain("The triggering hit deals", body);
        }
    }

    [Fact]
    public void The_two_title_keys_are_rows_the_mod_actually_registers()
    {
        // The substitute keeps the keyword's own TITLE so a reader still finds
        // the reaction by name -- and it has to name that row by key, because
        // the game's `CardKeyword.GetTitle()` is on an INTERNAL extension class
        // a mod cannot call. So the two consts are checked against the compiled
        // registration, the same `Il.Strings` read `KeywordTitleRowTests` uses
        // for every other title row: a typo here would render a raw key on a
        // card face, which is the defect `EB-155` exists for.
        var registered = Registered();

        Assert.Contains(KleeCardTooltips.VaporizePreviewKey + ".title",
                        registered);
        Assert.Contains(KleeCardTooltips.MeltPreviewKey + ".title", registered);
    }

    // ==================================================================
    // `EB-366`. THE FROZEN PREVIEW AND THE FREEZE ASKED DIFFERENT QUESTIONS.
    // ==================================================================

    [Fact]
    public void The_frozen_preview_reads_the_freezes_own_predicate()
    {
        // WHAT THE SEAT SAW (Furina reframe round 1, the Elite fight, round 5):
        // Freminet's Cryo onto a Hydro aura previewed *"Bosses cannot be
        // Frozen ... applies 2 Vulnerable instead"* on Byrdonis -- and Byrdonis
        // froze.
        //
        // The substitution is per-CREATURE inside a boss room: `RoomType.Boss`
        // AND no `MinionPower`, which is the only per-creature "secondary
        // enemy" fact the assembly carries (NC-7). The preview asked only the
        // room half, so a MINION beside a boss previewed the fallback and then
        // froze -- exactly as the freeze branch says it should.
        //
        // STRUCTURAL, and it has to be: the predicate reads
        // `Creature.CombatState.Encounter.RoomType`, and building an encounter
        // is outside the headless boundary (README). What is pinned is that
        // there is now ONE statement of the rule rather than two -- the preview
        // calls the freeze's own read-only twin and no longer reads a RoomType
        // of its own to compare.
        var calls = Il.Calls(Il.Method("KleeCardTooltips", "ForCard"));

        Assert.Contains("ReactionEffects.FrozenBossVulnWillApply", calls);
        Assert.DoesNotContain("EncounterModel.get_RoomType", calls);
    }

    [Fact]
    public void The_freeze_branch_still_owns_the_only_copy_of_the_rule()
    {
        // The other half of the same claim: the predicate the preview now reads
        // is the one the RESOLUTION acts on, so the two cannot drift.
        var resolve = Il.Calls(Il.Method("ReactionEffects", "Resolve"));

        Assert.Contains("ReactionEffects.FrozenBossVulnWillApply", resolve);
    }

    private static IReadOnlyCollection<string> Registered()
        => Il.Strings(typeof(global::KleeMod.KleeMod)
                          .GetMethod("InjectLocStrings", HeadlessGame.All)!);
}
