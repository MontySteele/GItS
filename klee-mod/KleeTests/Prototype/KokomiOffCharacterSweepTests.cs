#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI'S CARDS ON ANYONE (the off-character fix, 2026-10-18), on the base
/// game's Osty and Orbs precedent: Osty is summoned if absent, and a gauge
/// appears on first gain. Her cards reach other characters through
/// Kaleidoscope, Prismatic Gem, Sea Glass, Splash and a co-op partner, and a
/// Companion card can print a Plan line for anyone. Before this fix her kit
/// was hers alone: no Bake-Kurage off Kokomi, so a Plan line could never be
/// written, a Plan-only card was greyed, and a Sting maker made nothing.
///
/// THE RULE. A player's Kokomi kit (the flag, the Bake-Kurage, the marker
/// that carries the Plans out) comes up the first time a card with a Plan
/// line reaches their hand or they play one of her cards
/// (<see cref="KokomiRules.BringUp"/>), and stays for the combat. The Plan
/// strip and its peek view appear on their first Plan written
/// (<see cref="KokomiOverhaul.StripShowsFor"/>). Her relics and her
/// telemetry record stay hers (<see cref="KokomiOverhaul.IsHers"/>).
///
/// WHAT IS REAL HERE: the gates on real seats and real generated cards, the
/// flip on a real queue, the target predicates on a real pet. WHAT IS
/// STRUCTURAL: the summon, the marker and the morning's carry-out, which need
/// a live combat (the headless boundary), are pinned by their call graphs.
/// </summary>
public class KokomiOffCharacterSweepTests
{
    internal static IReadOnlyList<Type> KitCards() =>
        OffCharacterSweep.Cards("ProtoKk",
            typeof(global::KleeMod.Cards.Kokomi.DivineStrategy),
            typeof(global::KleeMod.Cards.Kokomi.PrincessOfWatatsumi));

    private static readonly Type[] Identity = { typeof(IKokomiCharacter) };

    private static readonly MethodBase IsKokomi =
        typeof(KokomiResources).GetMethod(nameof(KokomiResources.IsKokomi))!;

    private static Seat Ironclad(int hp = 80) => Seat.Of(new Ironclad(), hp);

    private static Seat Kokomi(int hp = 70) => Seat.Kokomi(hp);

    private static void Clean()
    {
        KokomiOverhaulLedger.ResetAll();
        KokomiPlan.ResetAll();
    }

    [Fact]
    public void The_sweep_covers_the_whole_kit()
    {
        var kit = KitCards().Select(t => t.Name).ToList();
        Assert.True(kit.Count >= 80, $"only {kit.Count} kit cards found");
        Assert.Contains(nameof(ProtoKkFeint), kit);
        Assert.Contains(nameof(ProtoKkSting), kit);
        Assert.Contains(nameof(ProtoKkWard), kit);
        Assert.Contains(nameof(ProtoKkMasterstroke), kit);
        Assert.Contains("PrincessOfWatatsumi", kit);
    }

    [Fact]
    public void Every_kit_card_brings_the_kit_up_when_played()
    {
        foreach (var type in KitCards())
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.True(KokomiOverhaul.BringsUpOnPlay(card), $"{type.Name} would not bring her kit up");
        }
        // Anyone else's card does not, unless it prints a Plan line.
        Assert.False(KokomiOverhaul.BringsUpOnPlay(new ProtoKoKapow()));
        Assert.False(KokomiOverhaul.BringsUpOnPlay(new ProtoFsAllIn()));
        Assert.True(KokomiOverhaul.BringsUpOnPlay(new ProtoMiGorouWarBanner()));
    }

    [Fact]
    public void A_plan_line_is_an_IPlannedCard_and_every_one_aims_at_the_kurage()
    {
        // HasPlanLine is the type test; every card that passes it must be a
        // Kokomi-target card, or the jellyfish would come up for a card that
        // cannot be aimed at it.
        var planned = OffCharacterSweep.Mod.GetTypes()
            .Where(t => typeof(IPlannedCard).IsAssignableFrom(t)
                        && typeof(CardModel).IsAssignableFrom(t) && !t.IsAbstract)
            .ToList();
        Assert.True(planned.Count >= 40, $"only {planned.Count} Plan cards");
        Assert.Contains(planned, t => t.Name.StartsWith("ProtoMi", StringComparison.Ordinal));
        WithDistinctSpellings(() =>
        {
            var spellings = new[]
            {
                KokomiTargets.PetOrEnemy, KokomiTargets.PetOrAlly,
                KokomiTargets.KurageOnly, KokomiTargets.KurageOrSelf,
            };
            foreach (var type in planned)
            {
                var card = (CardModel)Activator.CreateInstance(type)!;
                Assert.True(spellings.Contains(card.TargetType),
                            $"{type.Name} prints a Plan line but aims at no Kurage spelling");
            }
        });
    }

    // --- the play: no Kokomi identity on any card's closure ---------------

    /// <summary>The sites that MAY ask "is this Kokomi", and why each is
    /// hers by design rather than a card reading Kokomi-only state.</summary>
    private static readonly Dictionary<string, string> ByDesign = new()
    {
        ["KokomiResources.IsKokomi"] = "the identity predicate itself",
        // Her kit is up from the start of every combat; anyone else's from
        // their first Plan card in hand or Kokomi card played (BringUp).
        ["KokomiOverhaul.LiveFor"] = "the always-up half: her kit from turn one",
        // Her relics are hers: their effects count on her only.
        ["KokomiOverhaul.IsHers"] = "relic effects: her relics count on her only",
        // The strip is hers from turn one; anyone else's on first Plan.
        ["KokomiOverhaul.StripShowsFor"] = "display: her strip from turn one",
        // Random Companions come from the OWNER's personal pool (Klee's
        // and Furina's sweeps allow the same two).
        ["CompanionPool.CharacterId"] = "companion personal pool of the owner",
        ["CompanionPool.HomeNation"] = "companion nation of the owner",
    };

    [Fact]
    public void No_kit_card_reads_kokomi_identity_when_played()
    {
        var findings = OffCharacterSweep.Unexpected(KitCards(), Identity, IsKokomi, ByDesign);
        Assert.True(findings.Count == 0,
            "Kokomi identity read on a kit card's closure:\n  "
            + string.Join("\n  ", findings));
    }

    [Fact]
    public void The_closure_walk_bites()
    {
        var hits = OffCharacterSweep.IdentityReads(typeof(ProtoKkFeint), Identity, IsKokomi)
            .Select(h => h.Site).ToList();
        Assert.Contains("KokomiOverhaul.LiveFor", hits);
        Assert.Contains("KokomiResources.IsKokomi", hits);
    }

    // --- the face and the gate --------------------------------------------

    [Fact]
    public void Every_face_resolves_and_reads_the_same_on_an_ironclad()
    {
        Clean();
        try
        {
            var problems = OffCharacterSweep.FaceProblems(
                KitCards(), () => Ironclad(), () => Kokomi());
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            Clean();
        }
    }

    [Fact]
    public void Every_playability_gate_answers_the_same_for_an_ironclad()
    {
        Clean();
        try
        {
            var problems = new List<string>();
            foreach (var type in KitCards().Where(OffCharacterSweep.Gated))
            {
                foreach (var hp in new[] { 70, 6, 1 })
                {
                    var off = OffCharacterSweep.Ask(OffCharacterSweep.HeldBy(type, Ironclad(hp)));
                    var on = OffCharacterSweep.Ask(OffCharacterSweep.HeldBy(type, Kokomi(hp)));
                    if (off != on) problems.Add($"{type.Name} at {hp} HP: Kokomi {on}, Ironclad {off}");
                }
            }
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            Clean();
        }
    }

    // --- the kit: anyone's, from first need, and their own -----------------

    [Fact]
    public void An_ironclads_kit_comes_up_on_start_and_is_its_own()
    {
        Clean();
        try
        {
            var kokomi = Kokomi().WithCombatState().Creature;
            var ironclad = Ironclad().WithCombatState().Creature;
            var partner = Ironclad().WithCombatState().Creature;

            // Hers from turn one, as before; nobody else's.
            Assert.True(KokomiOverhaul.LiveFor(kokomi));
            Assert.False(KokomiOverhaul.LiveFor(ironclad));
            // Reading never brings it up, and creates no ledger.
            Assert.False(KokomiOverhaulLedger.HasStarted(ironclad));
            Assert.Null(KokomiOverhaulLedger.Peek(ironclad));

            Assert.True(KokomiOverhaul.Start(ironclad));
            Assert.True(KokomiOverhaul.LiveFor(ironclad));
            // Co-op: the partner's kit is still down.
            Assert.False(KokomiOverhaul.LiveFor(partner));
            // Kokomi herself never needs the flag.
            Assert.False(KokomiOverhaulLedger.HasStarted(kokomi));
            // Not hers: her relics and telemetry still ask IsHers.
            Assert.True(KokomiOverhaul.IsHers(kokomi));
            Assert.False(KokomiOverhaul.IsHers(ironclad));
            // A creature with no player has no kit.
            Assert.False(KokomiOverhaul.Start(null));

            // A new combat is a new ledger: the kit is down again.
            KokomiOverhaulLedger.ResetAll();
            Assert.False(KokomiOverhaul.LiveFor(ironclad));
        }
        finally
        {
            Clean();
        }
    }

    [Theory]
    [InlineData("ironclad")]
    [InlineData("klee")]
    [InlineData("yae")]
    public void A_plan_card_reaching_the_hand_brings_the_kurage_and_nothing_else_does(string who)
    {
        Clean();
        try
        {
            var seat = who switch
            {
                "klee" => Seat.Klee(),
                "yae" => Seat.Yae(),
                _ => Ironclad(),
            };
            seat.WithCombatState();
            var feint = OffCharacterSweep.HeldBy(typeof(ProtoKkFeint), seat);
            var sting = OffCharacterSweep.HeldBy(typeof(ProtoKkSting), seat);
            var gorou = OffCharacterSweep.HeldBy(typeof(ProtoMiGorouWarBanner), seat);
            var shoalCall = OffCharacterSweep.HeldBy(typeof(ProtoKkShoalCall), seat);
            var kapow = OffCharacterSweep.HeldBy(typeof(ProtoKoKapow), seat);

            // In the hand: a Plan line brings it, from her pool, a Sting or a
            // Companion. Anywhere else, or no Plan line: nothing.
            Assert.True(Arrives(feint, PileType.Hand));
            Assert.True(Arrives(sting, PileType.Hand));
            Assert.True(Arrives(gorou, PileType.Hand));
            Assert.False(Arrives(feint, PileType.Draw));
            Assert.False(Arrives(feint, PileType.Discard));
            Assert.False(Arrives(shoalCall, PileType.Hand));
            Assert.False(Arrives(kapow, PileType.Hand));

            // Played: any card of hers, or a Plan line; never anyone else's.
            Assert.True(OnPlay(feint));
            Assert.True(OnPlay(shoalCall));
            Assert.True(OnPlay(gorou));
            Assert.False(OnPlay(kapow));

            // Once up, nothing brings it up again (BringUp is idempotent too).
            KokomiOverhaul.Start(seat.Creature);
            Assert.False(Arrives(feint, PileType.Hand));
            Assert.False(OnPlay(shoalCall));
        }
        finally
        {
            Clean();
        }
    }

    [Fact]
    public void On_kokomi_neither_hook_does_anything()
    {
        Clean();
        try
        {
            var seat = Kokomi().WithCombatState();
            var feint = OffCharacterSweep.HeldBy(typeof(ProtoKkFeint), seat);
            Assert.False(Arrives(feint, PileType.Hand));
            Assert.False(OnPlay(feint));
            Assert.False(KokomiOverhaulLedger.HasStarted(seat.Creature));
        }
        finally
        {
            Clean();
        }
    }

    [Fact]
    public void The_two_hooks_bring_the_kit_up_and_bring_up_installs_the_kurage()
    {
        var play = Il.Calls(Il.Method("KokomiResourceHooks", "BeforeCardPlayed"));
        Assert.Contains("KokomiRules.BringsUpOnPlay", play);
        Assert.Contains("KokomiRules.BringUp", play);

        var pile = Il.Calls(Il.Method("KokomiResourceHooks", "AfterCardChangedPiles"));
        Assert.Contains("KokomiRules.BringsUpOnArrival", pile);
        Assert.Contains("KokomiRules.BringUp", pile);

        var bringUp = Il.Calls(Il.Method("KokomiRules", "BringUp"));
        Assert.Contains("KokomiOverhaul.Start", bringUp);
        Assert.Contains("KokomiRules.Install", bringUp);

        // Install summons the pet and applies the marker, behind the kit
        // gate (which Start has just opened), not her identity.
        var install = Il.Calls(Il.Method("KokomiRules", "Install"));
        Assert.Contains("BakeKuragePet.Summon", install);
        Assert.Contains("KokomiOverhaul.LiveFor", install);
        var summon = Il.Calls(Il.Method("BakeKuragePet", "Summon"));
        Assert.Contains("KokomiOverhaul.LiveFor", summon);
        Assert.DoesNotContain("KokomiResources.IsKokomi", summon);
    }

    // --- the Bake-Kurage: a play option for anyone whose kit is up ---------

    [Fact]
    public void An_ironclads_kurage_takes_its_own_plan_cards_and_no_one_elses()
    {
        WithDistinctSpellings(() =>
        {
            Clean();
            try
            {
                var ironclad = Ironclad().WithCombatState();
                var masterstroke = Owned(new ProtoKkMasterstroke(), ironclad);
                // No jellyfish: the Plan-only card is greyed, as before.
                Assert.True(PlanOnlyUnplayable(masterstroke));

                KokomiOverhaul.Start(ironclad.Creature);
                var kurage = Kurage(ironclad);
                // The jellyfish is out: the Plan-only card plays, and every
                // spelling's pet half takes this player's own jellyfish.
                Assert.False(PlanOnlyUnplayable(masterstroke));
                Assert.True(Pred("CanTargetPetOrEnemy")(kurage, ironclad.Player));
                Assert.True(Pred("CanTargetKurageOnly")(kurage, ironclad.Player));
                Assert.True(Pred("CanTargetKurageOrSelf")(kurage, ironclad.Player));
                Assert.True(Pred("CanTargetPetOrAlly")(kurage, ironclad.Player));

                // A co-op partner's cards cannot reach it.
                var partner = Seat.Klee().WithCombatState();
                Assert.False(Pred("CanTargetPetOrEnemy")(kurage, partner.Player));
                Assert.False(Pred("CanTargetKurageOnly")(kurage, partner.Player));
                Assert.True(PlanOnlyUnplayable(Owned(new ProtoKkMasterstroke(), partner)));
            }
            finally
            {
                Clean();
            }
        });
    }

    [Fact]
    public void A_play_on_the_kurage_writes_a_plan_whoever_plays_it()
    {
        // The write is the card's own OnPlay branch: aimed at a Bake-Kurage,
        // Schedule. Neither asks whose jellyfish beyond the kit gate.
        var feint = Il.Calls(Il.Method(nameof(ProtoKkFeint), "OnPlay"));
        Assert.Contains("KokomiPlan.PlayedOnPet", feint);
        Assert.Contains("KokomiPlan.Schedule", feint);
        var onPet = Il.Calls(Il.Method("KokomiPlan", "PlayedOnPet"));
        Assert.Contains("BakeKuragePet.Is", onPet);
        Assert.DoesNotContain("KokomiResources.IsKokomi", onPet);
        var schedule = Il.Calls(Il.Method("KokomiPlan", "Schedule"));
        Assert.Contains("KokomiOverhaul.LiveFor", schedule);
        Assert.DoesNotContain("KokomiOverhaul.IsHers", schedule);
        Assert.Contains("KokomiOverhaulLedger.NotePlanWritten", schedule);
        // The auto-play roll keeps an auto-played Attack off anyone's
        // jellyfish, not only hers.
        var roll = Il.Calls(Il.Method("AutoPlayNeverAimsAtThePetPatch", "Prefix"));
        Assert.Contains("KokomiOverhaul.LiveFor", roll);
        Assert.DoesNotContain("KokomiResources.IsKokomi", roll);
    }

    // --- the morning: next turn, after the draw, in order -----------------

    [Fact]
    public void Plans_are_carried_out_at_the_turn_start_after_the_draw_for_anyone()
    {
        // ProtoBakeKuragePower.AfterPlayerTurnStart: after the block clear,
        // the energy reset and the hand draw, so a planned Block lasts the
        // turn it lands on. Gated on the kit, not on her identity.
        var morning = Il.Calls(Il.Method(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart"));
        Assert.Contains("KokomiPlan.ResolveAll", morning);
        Assert.Contains("KokomiOverhaul.LiveFor", morning);
        Assert.DoesNotContain("KokomiOverhaul.IsHers", morning);
        Assert.Null(typeof(ProtoBakeKuragePower).GetMethod("BeforeSideTurnStart",
            HeadlessGame.All | BindingFlags.DeclaredOnly));
        var resolve = Il.Calls(Il.Method("KokomiPlan", "ResolveAll"));
        Assert.Contains("KokomiOverhaul.LiveFor", resolve);
        Assert.DoesNotContain("KokomiResources.IsKokomi", resolve);
    }

    [Fact]
    public void An_ironclad_flips_its_own_waiting_plan()
    {
        Clean();
        try
        {
            var ironclad = Ironclad().WithCombatState();
            var player = ironclad.Player;
            Seat.Force(player.PlayerCombatState!, "Phase", PlayerTurnPhase.Play);
            var queue = new List<KokomiPlan.Entry>
            {
                new(OffCharacterSweep.HeldBy(typeof(ProtoKkMasterstroke), ironclad), OneHit),
                new(OffCharacterSweep.HeldBy(typeof(ProtoKkKuragesOath), ironclad), OneHit),
            };
            Plant(player, queue);

            // Kit down: no Bake-Kurage, no flip.
            Assert.False(KokomiPlan.Flip(player, 1));
            Assert.Equal("there is no Bake-Kurage here", KokomiPlan.RequestFlip(player, 1));

            KokomiOverhaul.Start(ironclad.Creature);
            Assert.False(KokomiPlan.Flip(player, 0));     // Plan-only
            Assert.True(KokomiPlan.Flip(player, 1));
            Assert.True(KokomiPlan.Pending(player)[1].Now);
            Assert.True(KokomiPlan.Flip(player, 1));      // and back
            Assert.False(KokomiPlan.Pending(player)[1].Now);
            // In order: the writing order is the queue order.
            Assert.Equal(nameof(ProtoKkMasterstroke), KokomiPlan.Pending(player)[0].Source!.GetType().Name);
        }
        finally
        {
            Clean();
        }
    }

    // --- the strip and the peek view: on first Plan, not before ------------

    [Fact]
    public void The_strip_shows_from_turn_one_on_her_and_from_the_first_plan_on_anyone()
    {
        Clean();
        try
        {
            Assert.True(KokomiOverhaul.StripShowsFor(Kokomi().Creature));

            var ironclad = Ironclad().WithCombatState().Creature;
            var partner = Ironclad().WithCombatState().Creature;
            Assert.False(KokomiOverhaul.StripShowsFor(ironclad));
            KokomiOverhaul.Start(ironclad);
            // Up (the jellyfish is out), but nothing written yet: no strip.
            Assert.False(KokomiOverhaul.StripShowsFor(ironclad));
            KokomiOverhaulLedger.For(ironclad).NotePlanWritten();
            Assert.True(KokomiOverhaul.StripShowsFor(ironclad));
            Assert.False(KokomiOverhaul.StripShowsFor(partner));
        }
        finally
        {
            Clean();
        }
    }

    [Fact]
    public void The_strip_and_the_view_ask_the_kit_not_her_identity()
    {
        var live = Il.Calls(Il.Method("KokomiPlanStrip", "Live"));
        Assert.Contains("KokomiOverhaul.StripShowsFor", live);
        Assert.Contains("KokomiOverhaul.LiveFor",
                        Il.Calls(Il.Method("KokomiPlanStrip", "DiscardAll")));
        Assert.Contains("KokomiOverhaul.LiveFor", Il.Calls(Il.Method("KokomiPlanView", "Owns")));
        Assert.DoesNotContain("KokomiResources.IsKokomi",
                              Il.Calls(Il.Method("KokomiPlanView", "Owns")));
        Assert.DoesNotContain("KokomiResources.IsKokomi",
                              Il.Calls(Il.Method("KokomiPlanView", "OnChoiceBegun")));
    }

    // --- what stays hers ----------------------------------------------------

    [Fact]
    public void Her_relics_and_her_telemetry_stay_hers()
    {
        foreach (var (type, method) in new[]
                 {
                     ("TamakushiCasket", "BeforeCombatStart"),
                     ("TamakushiCasket", "AfterBlockCleared"),
                     ("KokomiArmRelics", "FirstTurnOf"),
                     ("ResistanceArmband", "Counts"),
                 })
        {
            var calls = Il.Calls(Il.Method(type, method));
            Assert.True(calls.Contains("KokomiOverhaul.IsHers"), $"{type}.{method} does not ask IsHers");
            Assert.False(calls.Contains("KokomiOverhaul.LiveFor"), $"{type}.{method} asks the kit gate");
        }

        Clean();
        try
        {
            // A Kurage Lantern held by an Ironclad whose kit is up counts 0.
            var ironclad = Ironclad().WithCombatState().WithRelic<global::KleeMod.Relics.KurageLantern>();
            KokomiOverhaul.Start(ironclad.Creature);
            var held = typeof(global::KleeMod.Relics.KokomiArmRelics)
                .GetMethod("Held", HeadlessGame.All)!
                .MakeGenericMethod(typeof(global::KleeMod.Relics.KurageLantern));
            Assert.Equal(0, (int)held.Invoke(null, new object?[] { ironclad.Creature })!);
            var kokomi = Kokomi().WithCombatState().WithRelic<global::KleeMod.Relics.KurageLantern>();
            Assert.Equal(1, (int)held.Invoke(null, new object?[] { kokomi.Creature })!);
        }
        finally
        {
            Clean();
        }
    }

    // --- helpers ----------------------------------------------------------

    private static readonly IReadOnlyList<KokomiPlan.Planned> OneHit = new[]
    {
        new KokomiPlan.Planned(KokomiPlan.Kind.Damage, 6, KokomiPlan.Aim.FrontEnemy),
    };

    private static bool Arrives(CardModel card, PileType pile) =>
        (bool)Il.Method("KokomiRules", "BringsUpOnArrival")
            .Invoke(null, new object?[] { card, pile })!;

    private static bool OnPlay(CardModel card) =>
        (bool)Il.Method("KokomiRules", "BringsUpOnPlay")
            .Invoke(null, new object?[] { card })!;

    private static void Plant(Player player, List<KokomiPlan.Entry> queue)
    {
        var plan = typeof(KokomiPlan);
        plan.GetField("_combat", HeadlessGame.All)!.SetValue(null, player.Creature.CombatState);
        var queues = (Dictionary<Player, List<KokomiPlan.Entry>>)plan
            .GetField("_queues", HeadlessGame.All)!.GetValue(null)!;
        queues[player] = queue;
    }

    private static Creature Kurage(Seat owner)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        var pet = (Creature)ctor.Invoke(new object?[] { null, 10, 10 });
        Seat.Force(pet, "Monster", RuntimeHelpers.GetUninitializedObject(typeof(BakeKurageMonster)));
        pet.PetOwner = owner.Player;
        ((List<Creature>)typeof(PlayerCombatState)
            .GetField("_pets", HeadlessGame.All)!
            .GetValue(owner.Player.PlayerCombatState!)!).Add(pet);
        return pet;
    }

    private static Func<Creature, Player, bool> Pred(string name)
    {
        var method = Il.Method("KokomiTargets", name);
        return (c, p) => (bool)method.Invoke(null, new object[] { c, p })!;
    }

    private static bool PlanOnlyUnplayable(CardModel card) =>
        (bool)Il.Method("PlanOnlyNeedsTheKuragePatch", "Unplayable")
            .Invoke(null, new object?[] { card })!;

    private static CardModel Owned(CardModel card, Seat seat)
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    /// <summary><see cref="KokomiOffCharacterTargetTests"/>' own: distinct
    /// values for the four spellings for one test (cards read the value at
    /// construction, so build them inside), then the host's values back.</summary>
    private static void WithDistinctSpellings(Action body)
    {
        var saved = (KokomiTargets.PetOrEnemy, KokomiTargets.PetOrAlly,
                     KokomiTargets.KurageOnly, KokomiTargets.KurageOrSelf);
        try
        {
            KokomiTargets.PetOrEnemy = (TargetType)9001;
            KokomiTargets.PetOrAlly = (TargetType)9002;
            KokomiTargets.KurageOnly = (TargetType)9003;
            KokomiTargets.KurageOrSelf = (TargetType)9004;
            body();
        }
        finally
        {
            (KokomiTargets.PetOrEnemy, KokomiTargets.PetOrAlly,
             KokomiTargets.KurageOnly, KokomiTargets.KurageOrSelf) = saved;
        }
    }
}
