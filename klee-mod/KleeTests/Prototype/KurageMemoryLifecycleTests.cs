using System.Runtime.CompilerServices;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-196 -- THE MEMORY'S LIFETIME, and the reason a live Kokomi's queue was
/// always empty.
///
/// THE FINDING (review/ruled/kokomi-kurage-memory-2026-08-29.md sec.13.6,
/// Gate B). On the 0.2.1441+proto build the strip printed and the base-kit
/// facts were true on the wire, but across two whole fights the queue never
/// held an entry: Gorou Exhausted (the bank moved, so the funnel ran), the
/// starter Muster transformed a card, and both left `memory empty`.
///
/// THE CAUSE, and it is not in either entry rule. `KurageMemory.ResetForCombat`
/// was called from <c>KokomiResourceHooks.Subscribe</c>, on the reading that
/// the subscription delegate is handed a fresh combat ONCE per fight. It is
/// not. <c>CombatState.IterateHookListeners</c> is an ITERATOR that walks
/// <c>ModHelper.IterateAllCombatStateSubscribers(combatState)</c>, which
/// re-invokes every mod's subscription delegate, and the combat enumerates its
/// hook listeners on EVERY hook broadcast. So the delegate -- and the clear
/// inside it -- ran between every pair of hooks in the fight, and an entry
/// filed by one hook was gone before the next one could read it.
///
/// The queue was the visible half. <c>PlayedAnything</c> and
/// <c>LastCardType</c> live in the same reset, which is why the strip also
/// said "you have played no card this turn" on turns where cards had been
/// played: the pulse key was wiped by the same line.
///
/// THE FIX, and why it is two things. The clear moved to
/// <c>BeforeCombatStart</c>, which the game raises ONCE per combat (it is
/// already where the base kit's jellyfish is installed, and Gate B proved that
/// hook fires); and <see cref="KurageMemory.ResetForCombat"/> keeps an
/// identity guard, so being handed the SAME combat again is a re-enumeration
/// and not a new fight. Either alone would fix the observed bug; both together
/// mean neither a re-enumeration nor a reused CombatState instance can lose or
/// keep a memory it should not.
/// </summary>
public class KurageMemoryLifecycleTests
{
    private static CombatState Fight() =>
        (CombatState)RuntimeHelpers.GetUninitializedObject(typeof(CombatState));

    /// <summary>A played, Exhausting starter Companion: the exact card the
    /// live gate played first.</summary>
    private static GorouInuzakaCharge Gorou(Seat seat)
    {
        var card = new GorouInuzakaCharge();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>A 1-cost kit Skill: what a starter Muster eats.</summary>
    private static CoralGuard Sacrifice(Seat seat)
    {
        var card = new CoralGuard();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    // --- both entry rules, played rather than pinned ----------------------

    [Fact]
    public void An_exhausting_companion_enters_the_memory()
    {
        // RULE 2. The class doc of KurageMemoryPinTests said this was outside
        // the boundary; it is not -- a Seat carries a real Creature, which is
        // everything `Enrol` reads.
        KurageMemory.ResetForCombat(Fight());
        var kokomi = Seat.Kokomi().WithCombatState();

        KurageMemory.NoteExhaust(Gorou(kokomi));

        var queue = KurageMemory.Queue(kokomi.Player);
        Assert.Single(queue);
        Assert.Equal("exhaust", queue[0].Rule);
        Assert.Equal(0, queue[0].Price);   // 0-cost: free, because it is
    }

    [Fact]
    public void The_card_sacrificed_to_a_muster_enters_the_memory()
    {
        // RULE 1, priced at 3x the SACRIFICE's own face.
        KurageMemory.ResetForCombat(Fight());
        var kokomi = Seat.Kokomi().WithCombatState();

        KurageMemory.NoteMuster(kokomi.Player, Sacrifice(kokomi));

        var queue = KurageMemory.Queue(kokomi.Player);
        Assert.Single(queue);
        Assert.Equal("muster", queue[0].Rule);
        Assert.Equal(3, queue[0].Price);
    }

    // --- THE BITE ---------------------------------------------------------

    [Fact]
    public void The_memory_survives_the_subscriber_list_being_re_enumerated()
    {
        // THE DEFECT, reproduced: the game hands the SAME CombatState to the
        // subscription delegate again on the next hook broadcast, and before
        // EB-196 that wiped the queue. One Muster and one Exhaust are filed
        // here because the live gate played exactly those two and lost both.
        var fight = Fight();
        KurageMemory.ResetForCombat(fight);
        var kokomi = Seat.Kokomi().WithCombatState();

        KurageMemory.NoteMuster(kokomi.Player, Sacrifice(kokomi));
        KurageMemory.NoteExhaust(Gorou(kokomi));
        Assert.Equal(2, KurageMemory.Queue(kokomi.Player).Count);

        // What the very next hook broadcast does.
        KurageMemory.ResetForCombat(fight);

        Assert.Equal(2, KurageMemory.Queue(kokomi.Player).Count);
    }

    [Fact]
    public void The_pulse_key_survives_the_same_re_enumeration()
    {
        // The other half of the same line, and the strip's second wrong
        // sentence: `PlayedAnything` is cleared by the same reset, so the
        // forecast read "you have played no card this turn" after cards had
        // been played.
        var fight = Fight();
        KurageMemory.ResetForCombat(fight);
        var kokomi = Seat.Kokomi().WithCombatState();
        KurageMemory.NoteExhaust(Gorou(kokomi));

        KurageMemory.ResetForCombat(fight);

        Assert.False((bool)KurageMemory.Snapshot(kokomi.Player)["empty"]);
    }

    [Fact]
    public void A_different_fight_still_starts_with_an_empty_memory()
    {
        // The guard is identity, not "never clear": a new CombatState is a new
        // fight and the memory is per fight.
        KurageMemory.ResetForCombat(Fight());
        var kokomi = Seat.Kokomi().WithCombatState();
        KurageMemory.NoteExhaust(Gorou(kokomi));
        Assert.Single(KurageMemory.Queue(kokomi.Player));

        KurageMemory.ResetForCombat(Fight());

        Assert.Empty(KurageMemory.Queue(kokomi.Player));
    }

    // --- STRUCTURAL: where the clear lives, and why it had to move ---------

    [Fact]
    public void The_fight_start_hook_is_what_clears_the_memory()
    {
        // The identity guard alone would still be at the mercy of the game
        // reusing a CombatState instance between fights. The clear belongs on
        // the hook the game raises once per combat -- the same one that
        // installs the base kit's jellyfish, which Gate B proved fires.
        var calls = Il.Calls(Il.Method("KokomiResourceHooks", "BeforeCombatStart"));

        Assert.Contains("KurageMemory.ClearForNewCombat", calls);
        Assert.Contains("KurageMemory.InstallAll", calls);
    }

    [Fact]
    public void The_subscription_delegate_no_longer_clears_anything()
    {
        // It is called on every hook broadcast, so nothing destructive may
        // live in it. It may only stash the combat the base-kit install needs.
        var calls = Il.Calls(Il.Method("KokomiResourceHooks", "Subscribe"));

        Assert.DoesNotContain("KurageMemory.ResetForCombat", calls);
        Assert.DoesNotContain("KurageMemory.ClearForNewCombat", calls);
        Assert.Contains("KurageMemory.NoteCombat", calls);
    }

    [Fact]
    public void The_game_re_enumerates_the_subscribers_on_every_hook_broadcast()
    {
        // WHY, read off the game rather than asserted: the combat's hook
        // listener walk is an iterator over ModHelper's subscriber walk, which
        // re-invokes each mod's delegate. This is the fact the old placement
        // got wrong, and it is the game's, so it is pinned here rather than
        // trusted to a comment.
        var iterate = typeof(CombatState)
            .GetMethod("IterateHookListeners", HeadlessGame.All)!;

        Assert.Contains("ModHelper.IterateAllCombatStateSubscribers",
                        Il.Calls(iterate));
    }
}
