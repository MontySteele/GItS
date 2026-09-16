using System;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-495`, the C# half of the kit-verb / base-game-trigger matrix
/// (`docs/current/atlas/kit-verbs-vs-base-triggers.md`). This class pins the
/// cells AS THEY ARE TODAY, against the real `klee.dll` and the real
/// `sts2.dll`, so a cell that moves fails here rather than being discovered
/// by play a month later -- which is how every cell in that matrix was
/// discovered in the first place.
///
/// TWO SIDES, AND THE POINT IS THE JOIN.
///
///   * THE TRIGGER SIDE reads the BASE GAME's own bodies. A trigger's answer
///     is not a fact about the mod at all: it is `props.IsPoweredAttack()`
///     inside `EnvenomPower`, `result.UnblockedDamage` inside `EmotionChip`,
///     `cardPlay.Card.Type` inside `ArtOfWar`. The mod cannot pin those by
///     calling them -- they need a live combat -- but the IL of a decompiled
///     method is readable, and `Harness.Il` already reads it. A game patch
///     that re-gates one of these fails the pin, which is exactly the event
///     the matrix would otherwise go stale on silently.
///
///   * THE VERB SIDE reads the MOD's bodies: which damage door each kit verb
///     goes through, and -- the load-bearing negative -- that the door it goes
///     through can never reach an `AttackCommand`.
///
/// WHY THE NEGATIVE IS THE IMPORTANT ASSERTION. Twenty of the matrix's
/// twenty-four verb rows read `none` under "you attack", "you deal damage"
/// and "damage modifiers", and all twenty read that way because of ONE line:
/// `ElementalHit.Deal` hands `CreatureCmd.Damage` a finished number with
/// `ValueProp.Unpowered`, `dealer: null` and `cardSource: null`. Somebody
/// routing that through `DamageCmd.Attack` for the hit animation would flip
/// sixty cells in one edit and nothing else in the repo would notice.
///
/// THE HEADLESS BOUNDARY (README): nothing here resolves an act, deals a hit
/// or builds a `CombatState`. Every assertion is a call-graph read.
///
/// The prototype arm's verbs -- the overhaul Bomb, the Mine, the Plan, the
/// Stage -- are in `Prototype/KitVerbBaseTriggerProtoPinTests.cs`, because
/// their types are not compiled without `-p:PrototypeCards=true`. The sim
/// column and the `powered:`/`element:` ARGUMENT values, which no IL read can
/// see, are pinned in `tier0/tests/test_eb495_kit_verb_triggers.py`.
/// </summary>
public class KitVerbBaseTriggerPinTests
{
    /// <summary>One base-game method, by simple type name, off the real
    /// `sts2.dll`. Deliberately reflective rather than `typeof(...)`: naming
    /// these types in source would make this file stop COMPILING when the
    /// game renames one, and a compile error says far less than a named
    /// assertion failure about which trigger moved.</summary>
    private static MethodBase Base(string typeName, string methodName)
    {
        var asm = typeof(MegaCrit.Sts2.Core.ValueProps.ValueProp).Assembly;
        var type = asm.GetTypes().FirstOrDefault(t => t.Name == typeName)
            ?? throw new InvalidOperationException(
                $"no type named {typeName} in sts2.dll -- the game moved it");
        return type.GetMethod(methodName, HeadlessGame.All)
            ?? throw new InvalidOperationException(
                $"{typeName} has no {methodName} -- the trigger moved");
    }

    // ================================================================
    // THE TRIGGER SIDE -- the matrix's eight columns, read off sts2.dll
    // ================================================================

    [Theory]
    // T2, "whenever you play an Attack": the predicate is the CARD's type.
    [InlineData("ArtOfWar", "AfterCardPlayed")]
    [InlineData("RippleBasin", "AfterCardPlayed")]
    [InlineData("PenNib", "BeforeCardPlayed")]
    public void A_play_an_Attack_trigger_reads_the_cards_type(
        string type, string method)
    {
        // `cardPlay.Card.Type` compiles to the two getters; the comparison
        // against `CardType.Attack` is an ldc, not a call, so the getters are
        // what an IL read can see. Both must be present: a trigger that
        // stopped reading `Card` would be reading something else's type.
        var calls = Il.Calls(Base(type, method));

        Assert.Contains("CardPlay.get_Card", calls);
        Assert.Contains("CardModel.get_Type", calls);
    }

    [Theory]
    // T1, "whenever you play a card": no type filter at all. The negative is
    // the assertion -- these are the relics a kit verb ALSO never reaches,
    // and they never reach it for a different reason (no card play), so if
    // one of them grew a type filter the matrix's T1 column would split.
    [InlineData("Pocketwatch")]
    [InlineData("BrilliantScarf")]
    [InlineData("VelvetChoker")]
    public void An_any_card_played_trigger_reads_no_card_type(string type)
    {
        Assert.DoesNotContain("CardModel.get_Type", Il.Calls(
            Base(type, "AfterCardPlayed")));
    }

    [Theory]
    // T3/T4/T6/T7: the predicate is `IsPoweredAttack()`, i.e. the damage
    // instance's ValueProp -- `Move` and not `Unpowered`. THIS IS THE ONE
    // PREDICATE THAT DECIDES MOST OF THE MATRIX, and every one of these
    // readers is a trigger no kit verb can ever wake.
    [InlineData("VigorPower", "BeforeAttack")]              // T3
    [InlineData("GigantificationPower", "BeforeAttack")]    // T3
    [InlineData("PainfulStabsPower", "AfterAttack")]        // T3
    [InlineData("SuckPower", "AfterAttack")]                // T3
    [InlineData("EnvenomPower", "AfterDamageGiven")]        // T4
    [InlineData("PaperCutsPower", "AfterDamageGiven")]      // T4
    [InlineData("ReaperFormPower", "AfterDamageGiven")]     // T4
    [InlineData("ThornsPower", "BeforeDamageReceived")]     // T6
    [InlineData("FlameBarrierPower", "AfterDamageReceived")]// T6
    [InlineData("CurlUpPower", "AfterDamageReceived")]      // T6
    [InlineData("SlowPower", "ModifyDamageMultiplicative")] // T7
    public void A_powered_attack_trigger_reads_IsPoweredAttack(
        string type, string method)
    {
        Assert.Contains("ValuePropExtensions.IsPoweredAttack",
                        Il.Calls(Base(type, method)));
    }

    [Fact]
    public void Skittish_is_the_loose_one_and_reads_Move_without_powered()
    {
        // MATRIX T3, and the reason DISAGREEMENT D1 exists. `SkittishPower`
        // does NOT ask `IsPoweredAttack()`: it asks for `ValueProp.Move` and
        // a `CardModel` source, so a SKILL that deals damage wakes it. The
        // sim gates the same power on `source == "attack"`, which is the
        // card's declared type, and therefore does not.
        //
        // `HasFlag` is the call that survives to IL; the `Move` literal is an
        // ldc. Asserting the absence of `IsPoweredAttack` is what actually
        // names the difference from the eleven readers above.
        var calls = Il.Calls(Base("SkittishPower", "AfterAttack"));

        Assert.Contains("Enum.HasFlag", calls);
        Assert.DoesNotContain("ValuePropExtensions.IsPoweredAttack", calls);
    }

    [Theory]
    // T5, "when it takes unblocked damage": NO attack filter, only the
    // amount. This is the one column where a kit verb IS seen, so the
    // absence of `IsPoweredAttack` here is the cell.
    [InlineData("EmotionChip")]
    [InlineData("LavaLamp")]
    [InlineData("BeatingRemnant")]
    public void An_unblocked_damage_trigger_reads_only_the_amount(string type)
    {
        var calls = Il.Calls(Base(type, "AfterDamageReceived"));

        Assert.Contains("DamageResult.get_UnblockedDamage", calls);
        Assert.DoesNotContain("ValuePropExtensions.IsPoweredAttack", calls);
    }

    [Fact]
    public void The_debuff_trigger_reads_the_powers_type_and_a_card_source()
    {
        // MATRIX T8 and DISAGREEMENT D7. `UnsettlingLamp` doubles a debuff
        // only when one was applied BY A CARD -- `cardSource == null` is its
        // third early return -- and a kit verb's debuff carries
        // `cardSource: null`, so the relic never sees one. `GetTypeForAmount`
        // is what makes "a debuff" mean a debuff.
        Assert.Contains("PowerModel.GetTypeForAmount",
                        Il.Calls(Base("UnsettlingLamp",
                                      "BeforePowerAmountChanged")));

        // Artifact is the counter-example that proves the column has two
        // shapes: it gates on the same `GetTypeForAmount` and on NO card
        // source, so it DOES block a verb's debuff.
        Assert.Contains("PowerModel.GetTypeForAmount",
                        Il.Calls(Base("ArtifactPower",
                                      "TryModifyPowerAmountReceived")));
    }

    [Fact]
    public void Only_an_AttackCommand_can_reach_the_attack_hooks()
    {
        // THE STRUCTURAL FACT UNDERNEATH THE WHOLE T3 COLUMN. `Hook.
        // BeforeAttack` and `Hook.AfterAttack` are broadcast from
        // `AttackCommand` and `AttackContext` and from nowhere else, so
        // damage that never builds one is invisible to every T3 reader
        // whatever its props. Read here rather than asserted in prose,
        // because it is the premise twenty matrix rows rest on.
        var execute = Il.Calls(Base("AttackCommand", "Execute"));

        Assert.Contains("Hook.BeforeAttack", execute);
        Assert.Contains("Hook.AfterAttack", execute);

        // And the funnel every kit verb DOES reach broadcasts the other
        // three, which is why T5 is the one column that answers.
        //
        // EVERY OVERLOAD, unioned, because `CreatureCmd.Damage` is a family
        // of six and the thin ones forward to the fat one. The claim is about
        // the FAMILY -- "no way into this funnel is an attack" -- so naming
        // one signature would be both ambiguous to reflection and weaker than
        // the thing being asserted.
        var asm = typeof(MegaCrit.Sts2.Core.ValueProps.ValueProp).Assembly;
        var damage = asm.GetTypes().First(t => t.Name == "CreatureCmd")
            .GetMethods(HeadlessGame.All)
            .Where(m => m.Name == "Damage")
            .SelectMany(Il.Calls)
            .ToList();

        Assert.Contains("Hook.AfterDamageGiven", damage);
        Assert.Contains("Hook.AfterDamageReceived", damage);
        Assert.DoesNotContain("Hook.BeforeAttack", damage);
        Assert.DoesNotContain("Hook.AfterAttack", damage);
    }

    // ================================================================
    // THE VERB SIDE -- the mod's one door, and the shipped verbs
    // ================================================================

    [Fact]
    public void The_one_door_ends_in_CreatureCmd_Damage_and_never_an_attack()
    {
        // `ElementalHit.Deal` IS the matrix's C# column for twenty of its
        // twenty-four rows. The positive says it reaches the raw damage
        // funnel; the negative says it can never build an AttackCommand, and
        // the negative is the one that would otherwise rot.
        var deal = Il.Calls(Il.Method("ElementalHit", "Deal"));

        Assert.Contains("CreatureCmd.Damage", deal);
        Assert.DoesNotContain("DamageCmd.Attack", deal);
        Assert.DoesNotContain("AttackCommand.Execute", deal);

        // The mod's own pipeline is what replaces the base game's, which is
        // why dropping the game's attack machinery costs the kit nothing.
        Assert.Contains("SimDamagePipeline.TargetMods", deal);
    }

    [Fact]
    public void The_named_door_for_a_bomb_is_the_same_door_unpowered()
    {
        // `EB-343` (R248) spelled "a Bomb carries the target's modifiers
        // only" as a METHOD rather than an argument precisely so a headless
        // pin could read it. This is that pin's matrix half: the door exists
        // and goes through `Deal`, so the Bomb's cell is `Deal`'s cell.
        Assert.Contains("ElementalHit.Deal",
                        Il.Calls(Il.Method("ElementalHit",
                                           "DealWithoutDealerMods")));
    }

    [Theory]
    // MATRIX V4, V12, V13 -- the SHIPPED verbs. Each reaches the one door
    // and none of them reaches `DamageCmd`, which is the whole of their row:
    // damage-only under T5 and `none` everywhere else. V11, the Casket, is
    // the Kokomi arm's relic and is pinned with the other quarantined verbs.
    [InlineData("BombPower", "ResolvePayload")]        // V4  detonation
    [InlineData("SalonMemberPower", "PerformMember")]  // V12 performance
    [InlineData("SalonMemberPower", "Bow")]            // V13 bow / Evoke
    public void A_shipped_kit_verb_goes_through_the_one_door(
        string type, string method)
    {
        var calls = Il.Calls(Il.Method(type, method));

        Assert.Contains("ElementalHit.Deal", calls);
        Assert.DoesNotContain("DamageCmd.Attack", calls);
    }

    [Fact]
    public void A_kit_verbs_debuff_carries_no_card_source()
    {
        // MATRIX T8 for the verb rows, the mod side of DISAGREEMENT D7.
        // The reaction layer is where a verb's debuff is minted, and it mints
        // it with whatever `cardSource` it was handed -- which, coming
        // through `ElementalHit.Deal`, is null. Pinned as a call-graph fact:
        // `ReactionEffects.Resolve` applies powers and never looks a card up
        // for itself.
        var resolve = Il.Calls(Il.Method("ReactionEffects", "Resolve"));

        Assert.Contains("PowerCmd.Apply", resolve);
        Assert.DoesNotContain("CardModel.get_Type", resolve);
    }

    [Fact]
    public void The_shipped_bomb_detonates_only_on_an_Attack_cards_hit()
    {
        // MATRIX V1/V2 vs the shipped Bomb: `BombPower.AfterDamageReceived`
        // asks BOTH questions -- a powered hit AND `cardSource.Type ==
        // CardType.Attack` -- so unlike Skittish it agrees with the sim's
        // `source == "attack"`. That agreement is a cell and is pinned here.
        var calls = Il.Calls(Il.Method("BombPower", "AfterDamageReceived"));

        Assert.Contains("ValuePropExtensions.IsPoweredAttack", calls);
        Assert.Contains("CardModel.get_Type", calls);
        Assert.Contains("DamageResult.get_UnblockedDamage", calls);
    }

    [Fact]
    public void Shatter_asks_the_same_two_questions_the_sim_asks()
    {
        // MATRIX V21, the other cell where the engines agree through
        // different machinery.
        var calls = Il.Calls(Il.Method("FrozenPower", "AfterDamageReceived"));

        Assert.Contains("ValuePropExtensions.IsPoweredAttack", calls);
        Assert.Contains("CardModel.get_Type", calls);
    }
}
