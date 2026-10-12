using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE KOKOMI RE-FOUNDING (2026-10-12): Plans and Ethereal, the Casket gone.
/// Direction <c>review/active/kokomi-design-pass-2026-10-11.md</c> (all five
/// picks (a)); cards <c>review/active/kokomi-card-paper-2026-10-12.md</c>
/// (ruled 2026-10-12). The now-line verbs of the new and changed rows, one
/// awaited call per `kind:` of the `kokomi` op
/// (<c>tools/gen_klee_cards.KOKOMI_KINDS</c>). Sim twin:
/// <c>tier0/engine/kokomi_plan.kind</c>.
/// </summary>
public static partial class KokomiCards
{
    /// <summary>The two jellyfish cards (card paper sec.1 rule 4).</summary>
    public enum Jellyfish
    {
        Sting,
        Ward,
    }

    /// <summary>
    /// Add <paramref name="amount"/> Stings or Wards to her hand: generated,
    /// Ethereal and Exhausting (their own rows print both keywords), upgraded
    /// where the caller says so. A full hand sends the rest to the discard
    /// pile, the base game's rule for a generated card. Returns how many were
    /// made. Sim twin: <c>kokomi_plan.add_jellyfish</c>.
    /// </summary>
    public static async Task<int> AddJellyfish(
        Player? owner, Jellyfish kind, int amount, bool upgraded)
    {
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null || amount <= 0) return 0;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return 0;
        var made = 0;
        for (var i = 0; i < amount; i++)
        {
            CardModel card = kind == Jellyfish.Sting
                ? combat.CreateCard<ProtoKkSting>(owner)
                : combat.CreateCard<ProtoKkWard>(owner);
            if (upgraded) card.UpgradeInternal();
            await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand,
                                                        owner);
            made++;
        }
        return made;
    }

    /// <summary>Shoal Call: "Add 2 [upgraded] Stings to your hand."</summary>
    public static Task ShoalCall(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddJellyfish(card.Owner, Jellyfish.Sting, Amount(card),
                     card.IsUpgraded);

    /// <summary>Jellyfish Drift, Kurage Barrage: "Add a Sting to your hand."
    /// The Sting is never upgraded by the card's own upgrade.</summary>
    public static Task AddSting(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddJellyfish(card.Owner, Jellyfish.Sting, 1, false);

    /// <summary>Bubble Ward, Watatsumi Drill: "Add a Ward to your hand."
    /// </summary>
    public static Task AddWard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddJellyfish(card.Owner, Jellyfish.Ward, 1, false);

    /// <summary>A face that names a Sting previews one (Blade Dance's shape);
    /// Shoal Call's upgraded face previews the upgraded Sting.</summary>
    public static IEnumerable<IHoverTip> WithStingPreview(
        IEnumerable<IHoverTip> tips, CardModel card, bool upgradedWithCard)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKkSting>(
            upgradedWithCard && card.IsUpgraded);
    }

    /// <summary>A face that names a Ward previews one.</summary>
    public static IEnumerable<IHoverTip> WithWardPreview(
        IEnumerable<IHoverTip> tips)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKkWard>(false);
    }

    /// <summary>
    /// Orders from the Shrine, Watatsumi Muster: "Add N random Common Inazuma
    /// Companion cards to your hand. They are Ethereal." Distinct cards off
    /// <see cref="KokomiCompanionPlan.Generated"/>, the run's companion
    /// roster (Klee's Tag Along door, <c>TakeRandom</c> on
    /// <c>Rng.CombatCardGeneration</c>); each is Ethereal and Exhausts (paper
    /// sec.1 rule 5), and arrives upgraded on the upgraded card.
    /// </summary>
    public static Task AddCompanions(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddCompanionCards(card, Amount(card));

    /// <summary>Orders from the Shrine: "Add a random Common Inazuma
    /// Companion card to your hand." One of <see cref="AddCompanions"/>.
    /// </summary>
    public static Task AddCompanion(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddCompanionCards(card, 1);

    private static async Task AddCompanionCards(CardModel card, int amount)
    {
        var owner = card.Owner;
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var made = KokomiCompanionPlan.Generated(owner, CardRarity.Common)
            .TakeRandom(amount, owner.RunState.Rng.CombatCardGeneration)
            .Select(c => combat.CreateCard(c, owner))
            .Where(c => c != null)
            .Cast<CardModel>()
            .ToList();
        foreach (var companion in made)
        {
            if (card.IsUpgraded) companion.UpgradeInternal();
            await CardPileCmd.AddGeneratedCardToCombat(
                KokomiCompanionPlan.Generate(companion), PileType.Hand,
                owner);
        }
    }

    /// <summary>
    /// Call the Generals: "Choose 1 of 3 random Rare Inazuma Companion cards.
    /// Add it to your hand. It is Ethereal." Klee's Tag Along screen
    /// (<c>CardSelectCmd.FromChooseACardScreen</c>, skippable, the base
    /// game's discovery), without the cost-0 rider.
    /// </summary>
    public static async Task CallTheGenerals(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var offered = KokomiCompanionPlan.Generated(owner, CardRarity.Rare)
            .TakeRandom(KokomiCompanionPlan.GeneralsOffered,
                        owner.RunState.Rng.CombatCardGeneration)
            .Select(c => combat.CreateCard(c, owner))
            .Where(c => c != null)
            .Cast<CardModel>()
            .ToList();
        if (offered.Count == 0) return;
        var pick = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, offered, owner, canSkip: true);
        if (pick == null) return;
        await CardPileCmd.AddGeneratedCardToCombat(
            KokomiCompanionPlan.Generate(pick), PileType.Hand, owner);
    }

    /// <summary>
    /// Reserves: "Put a card from your Exhaust Pile into your hand. It is
    /// Ethereal." Moon's Reflection's screen over the Exhaust Pile; an empty
    /// pile is a no-op. The card keeps every keyword it had and gains
    /// Ethereal.
    /// </summary>
    public static async Task Reserves(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner == null || !KokomiOverhaul.LiveFor(owner.Creature)) return;
        var pile = CardPile.Get(PileType.Exhaust, owner);
        if (pile == null || pile.Cards.Count == 0) return;
        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(
                new LocString("cards", KokomiRefounding.ReservesPromptKey),
                1))).FirstOrDefault();
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
        pick.AddKeyword(CardKeyword.Ethereal);
    }

    /// <summary>
    /// Grand Design (the re-founding's card under the old name): "Write up to
    /// 3 cards from your hand as Plans. They cost 0." Each chosen card is
    /// written exactly as if she had played it on the Bake-Kurage, for 0
    /// Energy (<see cref="KokomiRefounding.WriteFree"/>). Only a card that can
    /// be written is offered: one with a Plan line, or a Companion card.
    /// </summary>
    public static async Task GrandDesign(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner == null || !KokomiOverhaul.LiveFor(owner.Creature)) return;
        var picked = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(
                new LocString("cards", KokomiRefounding.GrandDesignPromptKey),
                0, Amount(card)),
            KokomiRefounding.CanBeWritten, card)).ToList();
        foreach (var chosen in picked)
        {
            await KokomiRefounding.WriteFree(choiceContext, chosen);
        }
    }

    /// <summary>Evening Watch (Dusk retired, 2026-10-12): "Gain 4 Block for
    /// each enemy intending to attack." Counted when it is played; the card's
    /// own Block, so Dexterity and Frail read it.</summary>
    public static async Task BlockPerAttacker(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) return;
        var attackers = KokomiRefounding.EnemiesIntendingAttack(kokomi);
        if (attackers <= 0) return;
        await CreatureCmd.GainBlock(kokomi, Amount(card) * attackers,
                                    ValueProp.Move, cardPlay);
    }

    /// <summary>Brace for the Tide (Dusk retired, 2026-10-12): "Double your
    /// Block." The base game's Entrench.</summary>
    public static async Task DoubleBlock(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) return;
        var standing = (int)kokomi.Block;
        if (standing <= 0) return;
        await CreatureCmd.GainBlock(kokomi, standing, ValueProp.Unpowered,
                                    cardPlay);
    }

    /// <summary>Tidecleanse (no Plan line since 2026-10-12): "Exhaust up to
    /// 2 statuses or curses in your hand." The Plan line's body, now.</summary>
    public static async Task ExhaustStatuses(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner == null || !KokomiOverhaul.LiveFor(owner.Creature)) return;
        await KokomiStatusBatch.ExhaustStatuses(choiceContext, owner,
                                                Amount(card), card);
    }
}

/// <summary>
/// A Companion card that can be written as a Plan (design pass pick 4 (a)):
/// every generated Companion row. <see cref="PrintedTargetType"/> is the
/// target the card prints, before <see cref="KokomiCompanionPlan.TargetFor"/>
/// lets it reach the Bake-Kurage on Kokomi.
/// </summary>
public interface IWritableCompanion
{
    TargetType PrintedTargetType { get; }
}

/// <summary>
/// COMPANIONS AS PLANS (design pass pick 4 (a), ruled 2026-10-12): "Any
/// Companion card can be written as a Plan. It is carried out next turn at
/// its printed rate, and the Bake-Kurage applies Hydro to its target first,
/// so each written Companion reacts with that Hydro and never with the
/// Companion before it."
///
/// WRITTEN like any Plan card: played on the Bake-Kurage, it is paid for and
/// goes where a played card goes (a generated one Exhausts); its Plan is ONE
/// clause holding the card (<see cref="KokomiPlan.Kind.PlayCompanion"/>).
/// CARRIED OUT as Crystal Collapse's copy is: a clone, played free and
/// Exhausted, so the deck is not a card short for having written it -- the
/// card itself is not played twice. Its Hydro lands FIRST, on its target: the
/// front enemy for a Companion that aims at an enemy (a Plan's target rule),
/// and the front enemy too for one that does not (paper sec.1 rule 5), so a
/// Companion that hits reacts with it and one that only buffs or blocks
/// carries the Hydro alone. Sim twin: <c>kokomi_plan.carry_out_companion</c>.
/// </summary>
public static class KokomiCompanionPlan
{
    /// <summary>Call the Generals' "1 of 3".</summary>
    public const int GeneralsOffered = 3;

    /// <summary>The nation her generators draw from.</summary>
    public const string Nation = "inazuma";

    /// <summary>
    /// The card's target on THIS owner: on Kokomi it also accepts the
    /// Bake-Kurage (an aimed Companion becomes "an enemy or the
    /// Bake-Kurage", any other "you or the Bake-Kurage", her own cards'
    /// spellings); everyone else sees the printed target. A canonical copy has
    /// no owner (its getter throws), so it prints its own.
    /// </summary>
    public static TargetType TargetFor(CardModel card, TargetType printed)
    {
        if (!OnKokomi(card)) return printed;
        if (printed == TargetType.AnyEnemy) return KokomiTargets.PetOrEnemy;
        if (printed == TargetType.AnyAlly) return KokomiTargets.PetOrAlly;
        return KokomiTargets.PetOrSelf;
    }

    /// <summary>Is this card held by Kokomi, so it can be written as a Plan?
    /// <see cref="TargetFor"/>'s test, and the Companion Plan tip's
    /// (<c>ArmKeywordTips.ForCompanionPlan</c>). A canonical copy has no owner
    /// (its getter throws), so it answers false.</summary>
    public static bool OnKokomi(CardModel card)
    {
        if (!card.IsMutable) return false;
        Creature? owner;
        try
        {
            owner = card.Owner?.Creature;
        }
        catch (System.Exception)
        {
            return false;
        }
        return KokomiOverhaul.LiveFor(owner);
    }

    /// <summary>Write a played Companion as a Plan: one clause holding the
    /// card itself.</summary>
    public static Task Write(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        KokomiPlan.Schedule(choiceContext, card.Owner?.Creature, card,
            new[]
            {
                new KokomiPlan.Planned(KokomiPlan.Kind.PlayCompanion, 0,
                                       KokomiPlan.Aim.FrontEnemy, card),
            });

    /// <summary>Does the Companion aim at an enemy as printed?</summary>
    public static bool AimsAtAnEnemy(CardModel? card) =>
        card is IWritableCompanion { PrintedTargetType: TargetType.AnyEnemy };

    /// <summary>
    /// The carry-out: the Bake-Kurage applies Hydro to the target, then a
    /// free clone of the Companion is played at it (an aimed one) or with no
    /// chosen target (any other), and Exhausts. No front enemy left: no Hydro,
    /// and an aimed Companion finds no target and is not played.
    /// </summary>
    public static async Task CarryOut(
        PlayerChoiceContext choiceContext, Creature kokomi, CardModel? card)
    {
        if (card == null || kokomi.CombatState is not { } combat) return;
        var front = KokomiPlan.FrontEnemy(kokomi);
        if (front != null)
        {
            await ElementalHit.ApplyOnly(choiceContext, front, Element.Hydro,
                                         kokomi);
        }
        var copy = combat.CloneCard(card);
        copy.ExhaustOnNextPlay = true;
        await CardCmd.AutoPlay(choiceContext, copy,
                               AimsAtAnEnemy(card) ? front : null);
    }

    /// <summary>
    /// The Companions her generators may make for <paramref name="owner"/>:
    /// the run's companion roster (<see cref="CompanionPool.All"/>, the door
    /// the reward slot and Klee's Tag Along read), Inazuma's, of
    /// <paramref name="rarity"/>, less any Personal that is someone else's.
    /// Gorou's four are her own cards since the re-founding and are not in the
    /// roster. Sorted by id so the roll is reproducible. PURE.
    /// </summary>
    public static List<CardModel> Generated(Player owner, CardRarity rarity) =>
        CompanionPool.All
            .Where(card => card.Rarity == rarity)
            .Where(card => (card as ICompanionCard)?.Nation == Nation)
            .Where(card => CompanionPool.IsOfferable(card, owner))
            .OrderBy(card => card.Id.ToString())
            .ToList();

    /// <summary>A generated Companion is Ethereal and Exhausts when played
    /// or carried out (paper sec.1 rule 5).</summary>
    public static CardModel Generate(CardModel card)
    {
        card.AddKeyword(CardKeyword.Ethereal);
        card.AddKeyword(CardKeyword.Exhaust);
        return card;
    }
}

/// <summary>
/// THE RE-FOUNDING'S RULE SEAMS: the two moments its payoffs read -- a Plan
/// WRITTEN (<see cref="OnWritten"/>, from <c>KokomiPlan.Schedule</c>) and a
/// Plan CARRIED OUT (<see cref="OnCarriedOut"/>, from
/// <c>KokomiPlan.ResolveEntry</c>) -- and Grand Design's free write.
/// </summary>
public static class KokomiRefounding
{
    /// <summary>Reserves' Exhaust Pile screen, merged into the `cards`
    /// table by <c>KleeMod.InjectLocStrings</c>.</summary>
    public const string ReservesPromptKey =
        "KLEEMOD-KOKOMI_RESERVES.selectionScreenPrompt";

    public const string ReservesPromptText =
        "Choose a card to put into your hand.";

    /// <summary>Grand Design's hand screen.</summary>
    public const string GrandDesignPromptKey =
        "KLEEMOD-KOKOMI_GRAND_DESIGN.selectionScreenPrompt";

    public const string GrandDesignPromptText =
        "Choose up to 3 cards to write as Plans.";

    /// <summary>How many enemies are telegraphing an attack right now, by
    /// the arm's one definition (<c>CurtainCallHooks.IntendsAttack</c>).</summary>
    public static int EnemiesIntendingAttack(Creature kokomi) =>
        kokomi.CombatState?.HittableEnemies
            .Where(e => !e.IsDead)
            .Count(CurtainCallHooks.IntendsAttack) ?? 0;

    /// <summary>Can this card be written as a Plan? A Plan line, or a
    /// Companion card. PURE.</summary>
    public static bool CanBeWritten(CardModel? card) =>
        card is IPlannedCard { PlanClauses.Count: > 0 }
        || card is IWritableCompanion;

    /// <summary>Is this card Ethereal right now (its own keyword, or one it
    /// was given)?</summary>
    public static bool IsEthereal(CardModel? card) =>
        card != null && card.Keywords.Contains(CardKeyword.Ethereal);

    /// <summary>Is this one of the two jellyfish cards?</summary>
    public static bool IsJellyfish(CardModel? card) =>
        card is ProtoKkSting or ProtoKkWard;

    private static readonly HashSet<CardModel> _freeWrites = new();

    /// <summary>Is this play Grand Design's free write? Read by
    /// <see cref="KokomiPlan.PlayedOnPet"/>, which otherwise refuses an
    /// auto-play.</summary>
    public static bool IsFreeWrite(CardModel? card) =>
        card != null && _freeWrites.Contains(card);

    /// <summary>
    /// Grand Design's write: the card is played on the Bake-Kurage for free
    /// through the game's own free-play door (<c>CardCmd.AutoPlay</c>, aimed
    /// at the jellyfish), so it leaves her hand and goes where a played card
    /// goes, and its own Plan branch writes it -- the same path a drag onto
    /// the jellyfish takes. No jellyfish, nothing.
    /// </summary>
    public static async Task WriteFree(PlayerChoiceContext choiceContext,
                                       CardModel card)
    {
        var kokomi = card.Owner?.Creature;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var pet = BakeKuragePet.Of(kokomi);
        if (pet == null) return;
        _freeWrites.Add(card);
        try
        {
            await CardCmd.AutoPlay(choiceContext, card, pet);
        }
        finally
        {
            _freeWrites.Remove(card);
        }
    }

    /// <summary>
    /// A Plan was just written; <paramref name="written"/> is the card that
    /// wrote it. Watchful Shoal pays Block for an Ethereal card, Watatsumi
    /// Resistance a Sting for a Companion card. Sim twin:
    /// <c>kokomi_plan.note_written</c>.
    /// </summary>
    public static async Task OnWritten(PlayerChoiceContext choiceContext,
                                       Creature? kokomi, CardModel? written)
    {
        if (kokomi == null || written == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (IsEthereal(written))
        {
            var block = (int)kokomi.Powers.OfType<WatchfulShoalPower>()
                .Sum(p => p.Amount);
            if (block > 0)
            {
                // NC-11: power-sourced Block stays raw.
                await CreatureCmd.GainBlock(kokomi, block,
                                            ValueProp.Unpowered, null);
            }
        }
        if (CompanionHexerei.CountsAsCompanion(written))
        {
            var stings = (int)kokomi.Powers.OfType<WatatsumiResistancePower>()
                .Sum(p => p.Amount);
            if (stings > 0)
            {
                await KokomiCards.AddJellyfish(kokomi.Player,
                    KokomiCards.Jellyfish.Sting, stings, upgraded: false);
            }
        }
    }

    /// <summary>
    /// A Plan was just carried out; <paramref name="card"/> is the card that
    /// wrote it. Coordinated Tide hits the front enemy for an Ethereal card;
    /// Endless Shoal adds a copy of a Sting or Ward to her hand. Once per
    /// carry-out, either line. Sim twin: <c>kokomi_plan.note_carried_out</c>.
    /// </summary>
    public static async Task OnCarriedOut(PlayerChoiceContext choiceContext,
                                          Creature kokomi, CardModel? card)
    {
        if (card == null || !KokomiOverhaul.LiveFor(kokomi)) return;
        if (IsEthereal(card))
        {
            var hit = (int)kokomi.Powers.OfType<CoordinatedTidePower>()
                .Sum(p => p.Amount);
            var front = KokomiPlan.FrontEnemy(kokomi);
            if (hit > 0 && front != null)
            {
                await ElementalHit.Deal(choiceContext, front, Element.Hydro,
                                        hit, kokomi, powered: false);
            }
        }
        if (IsJellyfish(card) && kokomi.CombatState is { } combat
            && kokomi.Player is { } player)
        {
            var copies = (int)kokomi.Powers.OfType<EndlessShoalPower>()
                .Sum(p => p.Amount);
            for (var i = 0; i < copies; i++)
            {
                var copy = combat.CloneCard(card);
                await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand,
                                                            player);
            }
        }
    }

    /// <summary>Gorou, General's War Banner's Plan line: "Gain 3 Strength
    /// this turn." The base game's Flex shape (a positive
    /// <c>TemporaryStrengthPower</c>).</summary>
    public static Task StrengthThisTurn(PlayerChoiceContext choiceContext,
                                        Creature kokomi, int amount) =>
        amount <= 0
            ? Task.CompletedTask
            : PowerCmd.Apply<WarBannerPlanPower>(
                choiceContext, kokomi, amount, applier: kokomi,
                cardSource: null);

    /// <summary>Grand Strategist: "Whenever a Plan causes an Elemental
    /// Reaction, deal 5 damage to ALL enemies." Called from the one place the
    /// mod resolves a reaction (<c>CompanionOverhaulReactions.Note</c>); a
    /// reaction inside a carry-out's window is the Plan's.</summary>
    public static async Task OnReaction(PlayerChoiceContext choiceContext,
                                        Creature? dealer)
    {
        if (dealer == null || !KokomiOverhaul.LiveFor(dealer)) return;
        if (!KokomiPlan.IsCarryingOut(dealer.Player)) return;
        var amount = (int)dealer.Powers.OfType<GrandStrategistPower>()
            .Sum(p => p.Amount);
        if (amount <= 0 || dealer.CombatState is not { } combat) return;
        foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                    .ToList())
        {
            await ElementalHit.DealUnelemented(choiceContext, enemy, amount,
                                               dealer, powered: false);
        }
    }
}

/// <summary>Gorou, General's War Banner, its Plan line: "Gain 3 Strength this
/// turn." Flex's shape: Strength now, taken back at the end of the turn. Sim
/// twin: <c>temp_strength</c>.</summary>
public sealed class WarBannerPlanPower : TemporaryStrengthPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "General's War Banner"),
        ("description",
            "Gain [blue]{Amount}[/blue] [gold]Strength[/gold] this turn."),
    };

    public override AbstractModel OriginModel =>
        ModelDb.Card<ProtoMiGorouWarBanner>();
}

/// <summary>Sangonomiya's Orders: "At the start of your turn, add a random
/// Common Inazuma Companion card to your hand. It is Ethereal." Copies add
/// one each. Sim twin: <c>kokomi_plan.turn_start_generators</c>.</summary>
public sealed class SangonomiyasOrdersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sangonomiya's Orders"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] random "
          + "Common Inazuma [gold]Companion[/gold] "
          + "{Amount:plural:card|cards} to your hand. "
          + "{Amount:plural:It is|They are} [gold]Ethereal[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    // STAGED into the start-of-turn tail (AfterPlayerTurnStartLate), so the
    // card lands after the Bake-Kurage's morning Plans in every order -- the
    // sim's `kokomi_plan.turn_start_generators`, after `resolve_all`.
    public override async Task AfterPlayerTurnStartLate(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner || Amount <= 0) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        var combat = Owner.CombatState;
        if (combat == null) return;
        var made = KokomiCompanionPlan.Generated(player, CardRarity.Common)
            .TakeRandom((int)Amount, player.RunState.Rng.CombatCardGeneration)
            .Select(c => combat.CreateCard(c, player))
            .Where(c => c != null)
            .Cast<CardModel>()
            .ToList();
        foreach (var companion in made)
        {
            await CardPileCmd.AddGeneratedCardToCombat(
                KokomiCompanionPlan.Generate(companion), PileType.Hand,
                player);
        }
    }
}

/// <summary>Kurage Bloom: "At the start of your turn, add a Sting to your
/// hand." Copies add one each. Sim twin:
/// <c>kokomi_plan.turn_start_generators</c>.</summary>
public sealed class KurageBloomPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Bloom"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Sting[/gold]|[gold]Stings[/gold]} to your "
          + "hand."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    // STAGED into the start-of-turn tail (AfterPlayerTurnStartLate), so the
    // card lands after the Bake-Kurage's morning Plans in every order -- the
    // sim's `kokomi_plan.turn_start_generators`, after `resolve_all`.
    public override async Task AfterPlayerTurnStartLate(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner || Amount <= 0) return;
        await KokomiCards.AddJellyfish(player, KokomiCards.Jellyfish.Sting,
                                       (int)Amount, upgraded: false);
    }
}

/// <summary>Watchful Shoal: "Whenever you write an Ethereal card as a Plan,
/// gain 3 Block." Paid from <see cref="KokomiRefounding.OnWritten"/>.
/// </summary>
public sealed class WatchfulShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watchful Shoal"),
        ("description",
            "Whenever you write an [gold]Ethereal[/gold] card as a "
          + "[gold]Plan[/gold], gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Coordinated Tide: "Whenever the Bake-Kurage carries out an
/// Ethereal card, deal 4 Hydro damage to the front enemy." Paid from
/// <see cref="KokomiRefounding.OnCarriedOut"/>; unpowered Hydro, Tidal
/// Riposte's hit.</summary>
public sealed class CoordinatedTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Coordinated Tide"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out an "
          + "[gold]Ethereal[/gold] card, deal [blue]{Amount}[/blue] "
          + "[gold]Hydro[/gold] damage to the front enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Grand Strategist: "Whenever a Plan causes an Elemental Reaction,
/// deal 5 damage to ALL enemies." Paid from
/// <see cref="KokomiRefounding.OnReaction"/>.</summary>
public sealed class GrandStrategistPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Strategist"),
        ("description",
            "Whenever a [gold]Plan[/gold] causes an [gold]Elemental "
          + "Reaction[/gold], deal [blue]{Amount}[/blue] damage to ALL "
          + "enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Endless Shoal: "Whenever the Bake-Kurage carries out a Sting or
/// Ward, add a copy of it to your hand." Paid from
/// <see cref="KokomiRefounding.OnCarriedOut"/>; copies add one each.
/// </summary>
public sealed class EndlessShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Endless Shoal"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Sting[/gold] or [gold]Ward[/gold], add a copy of it to "
          + "your hand."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Dawn Tide: "At the start of your turn, the Bake-Kurage applies Hydro to
/// ALL enemies." Called from <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c>
/// AFTER the morning's Plans (<see cref="Signal"/>), so the Hydro stands for
/// her turn. The aura is applied inside the morning window, so this turn
/// start's tick spares it, as a Plan's is. Sim twin:
/// <c>kokomi_plan.dawn_tide</c>.
/// </summary>
public sealed class DawnTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Dawn Tide"),
        ("description",
            "At the start of your turn, the [gold]Bake-Kurage[/gold] applies "
          + "[gold]Hydro[/gold] to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static async Task Signal(PlayerChoiceContext choiceContext,
                                    Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (!kokomi!.Powers.OfType<DawnTidePower>().Any()) return;
        var combat = kokomi.CombatState;
        if (combat == null) return;
        AuraPower.MorningWindow++;
        try
        {
            foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                        .ToList())
            {
                await ElementalHit.ApplyOnly(choiceContext, enemy,
                                             Element.Hydro, kokomi);
            }
        }
        finally
        {
            AuraPower.MorningWindow--;
        }
    }
}
