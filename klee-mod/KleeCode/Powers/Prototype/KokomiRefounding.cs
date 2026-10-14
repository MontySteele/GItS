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
/// Direction <c>review/ruled/kokomi-design-pass-2026-10-11.md</c> (all five
/// picks (a)); cards <c>review/ruled/kokomi-card-paper-2026-10-12.md</c>
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
            // Kokomi round 3 A-list (2026-10-13): a full hand sent it to the
            // discard pile; the page says so ("1 Sting to the discard pile
            // (hand full)") rather than the seat reading it as lost.
            if (card.Pile?.Type == PileType.Discard)
            {
                ResolutionLedger.NoteToDiscard(
                    card.Title ?? (kind == Jellyfish.Sting ? "Sting" : "Ward"));
            }
        }
        // The jellyfish build (2026-10-12): Stings made this fight, for
        // telemetry (the paper's first check line).
        if (kind == Jellyfish.Sting && made > 0)
        {
            KokomiOverhaulLedger.For(owner.Creature!).NoteStingsMade(made);
        }
        return made;
    }

    /// <summary>Shoal Call (the jellyfish build, 2026-10-12, the base game's
    /// Blade Dance): "Add 3 [4] Stings to your hand." Plain Stings on both
    /// faces; the upgrade adds one.</summary>
    public static Task ShoalCall(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddJellyfish(card.Owner, Jellyfish.Sting, Amount(card), false);

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

    /// <summary>A face that names a Sting previews one (Blade Dance's
    /// shape). Every Sting handed over is a plain one since the jellyfish
    /// build (2026-10-12).</summary>
    public static IEnumerable<IHoverTip> WithStingPreview(
        IEnumerable<IHoverTip> tips)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKkSting>(false);
    }

    /// <summary>A face that names a Ward previews one.</summary>
    public static IEnumerable<IHoverTip> WithWardPreview(
        IEnumerable<IHoverTip> tips)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKkWard>(false);
    }

    /// <summary>
    /// Watatsumi Muster: "Add N random Common Inazuma
    /// Companion cards to your hand. They are Ethereal." Distinct cards off
    /// <see cref="KokomiCompanionPlan.Generated"/>, the run's companion
    /// roster (Klee's Tag Along door, <c>TakeRandom</c> on
    /// <c>Rng.CombatCardGeneration</c>); each is Ethereal and Exhausts (paper
    /// sec.1 rule 5), and arrives upgraded on the upgraded card.
    /// </summary>
    public static Task AddCompanions(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        AddCompanionCards(card, Amount(card));

    /// <summary>
    /// Orders from the Shrine (the Kokomi level pass, 2026-10-12): "Choose 1
    /// of 3 random Common Inazuma Companions to add into your Hand. It is
    /// Ethereal." Call the Generals' screen at Common, without its cost-0
    /// rider; the card's upgrade is its cost, so the pick arrives as it is.
    /// </summary>
    public static async Task ChooseCommonCompanion(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var offered = KokomiCompanionPlan.Generated(owner, CardRarity.Common)
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
    /// Add it to your hand. It is Ethereal. It costs 0 this turn." Klee's Tag
    /// Along screen (<c>CardSelectCmd.FromChooseACardScreen</c>, skippable,
    /// the base game's discovery) with its cost-0 rider since Kokomi round 2
    /// (2026-10-12): the Rare Inazuma Companions cost 2 or 3, so a 1-Energy
    /// card handed over a card she could not play that turn.
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
        var made = KokomiCompanionPlan.Generate(pick);
        made.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(made, PileType.Hand, owner);
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
        "Choose a card to put into your [gold]Hand[/gold].";

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

    /// <summary>Grand Design's gate (Kokomi review 2026-10-13): does her
    /// hand hold a card, other than <paramref name="card"/> itself, that can
    /// be planned? A canonical copy has no owner and answers false. Must
    /// never throw: <c>IsPlayable</c> is read on every state poll. Sim twin:
    /// <c>kokomi_plan.refuses_for_no_plan</c>.
    ///
    /// FAILS OPEN (Kokomi round 2, 2026-10-13). Lane 3's Grand Design+ said
    /// "no card in your hand can be planned" on most turns of a deck about
    /// two-thirds Plan cards and Companions, while this predicate matches the
    /// Bake-Kurage's drop target for every card in the assembly, upgraded or
    /// not (<c>KokomiRoundTwoFixesTests</c>). The one path that could refuse a
    /// good hand was the catch: any throw while reading the hand answered
    /// "nothing to plan". A throw now answers "playable" (a Grand Design that
    /// finds nothing picks nothing, which is the lesser defect), a throwing
    /// card counts alone as unplannable, and the first throw of each kind is
    /// written to godot.log so the next round names it.</summary>
    public static bool AnyToPlan(CardModel card)
    {
        try
        {
            if (!card.IsMutable) return false;
            var owner = card.Owner;
            if (owner == null) return false;
            return AnyOtherToPlan(PileType.Hand.GetPile(owner).Cards, card);
        }
        catch (System.Exception e)
        {
            WarnOnce(ref _warnedHand, $"reading the hand threw: {e}");
            return true;
        }
    }

    /// <summary>The hand read behind <see cref="AnyToPlan"/>, PURE: any card
    /// in <paramref name="hand"/> but <paramref name="self"/> that
    /// <see cref="CanBeWritten"/>. A card whose read throws counts as
    /// unplannable on its own rather than ending the read.</summary>
    public static bool AnyOtherToPlan(IEnumerable<CardModel> hand,
                                      CardModel? self) =>
        hand.ToList().Any(other => !ReferenceEquals(other, self)
                                   && CanBeWrittenSafely(other));

    /// <summary>Kokomi round 4 (2026-10-13): does the owner's Exhaust Pile
    /// hold a card? Moon's Reflection is unplayable while it does not, rather
    /// than spending its cost and exhausting on nothing (lane 1 F17). A
    /// canonical copy has no owner and answers true, and a throw answers true
    /// (fails open, <see cref="AnyToPlan"/>'s rule). Sim twin:
    /// <c>kokomi_plan.refuses_for_no_plan</c>.</summary>
    public static bool AnyExhausted(CardModel card)
    {
        try
        {
            if (!card.IsMutable) return true;
            var owner = card.Owner;
            if (owner == null) return true;
            return PileType.Exhaust.GetPile(owner).Cards.Count > 0;
        }
        catch (System.Exception e)
        {
            WarnOnce(ref _warnedExhaust,
                     $"Moon's Reflection read of the Exhaust Pile threw: {e}");
            return true;
        }
    }

    private static bool _warnedHand;
    private static bool _warnedCard;
    private static bool _warnedExhaust;

    private static bool CanBeWrittenSafely(CardModel card)
    {
        try
        {
            return CanBeWritten(card);
        }
        catch (System.Exception e)
        {
            WarnOnce(ref _warnedCard,
                     $"reading {card.GetType().Name} threw: {e}");
            return false;
        }
    }

    private static void WarnOnce(ref bool warned, string message)
    {
        if (warned) return;
        warned = true;
        try
        {
            MegaCrit.Sts2.Core.Logging.Log.Warn(
                $"[{KleeMod.ModId}] Grand Design gate: {message}");
        }
        catch (System.Exception)
        {
            // Headless (no logger): the answer above stands.
        }
    }

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
    /// wrote it. Watatsumi Resistance pays a Sting for a Companion card
    /// (Watchful Shoal left this bus in the Kokomi round-3 changes,
    /// 2026-10-12). Sim twin:
    /// <c>kokomi_plan.note_written</c>.
    /// </summary>
    public static async Task OnWritten(PlayerChoiceContext choiceContext,
                                       Creature? kokomi, CardModel? written)
    {
        if (kokomi == null || written == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
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
    /// wrote it. Endless Shoal (the jellyfish build, 2026-10-12): "Whenever
    /// the Bake-Kurage carries out a Plan, add a Sting to your hand." Any
    /// Plan, either line; once per CARRY-OUT, so a Plan carried out twice
    /// (Nereid's Ascension, Second Wave) gives two Stings, and copies add one
    /// each. (Coordinated Tide's hit is inside the carry-out,
    /// <see cref="CoordinatedTide"/>.) Sim twin:
    /// <c>kokomi_plan.note_carried_out</c>.
    /// </summary>
    public static async Task OnCarriedOut(PlayerChoiceContext choiceContext,
                                          Creature kokomi, CardModel? card)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var stings = (int)kokomi.Powers.OfType<EndlessShoalPower>()
            .Sum(p => p.Amount);
        if (stings > 0)
        {
            await KokomiCards.AddJellyfish(kokomi.Player,
                KokomiCards.Jellyfish.Sting, stings, upgraded: false);
        }
        // THE POOL OVERHAUL (2026-10-13): Battle Formation, when the third
        // Plan of the turn finishes.
        await BattleFormationPower.OnCarriedOut(choiceContext, kokomi);
    }

    /// <summary>Gorou, General's War Banner's Plan line: "Gain 1 Strength."
    /// Permanent since the Kokomi level pass (2026-10-12), her own slow
    /// Strength line. Sim twin: `kokomi_plan`'s `GAIN_STRENGTH`.</summary>
    public static Task GainStrength(PlayerChoiceContext choiceContext,
                                    Creature kokomi, int amount) =>
        amount <= 0
            ? Task.CompletedTask
            : PowerCmd.Apply<StrengthPower>(
                choiceContext, kokomi, amount, applier: kokomi,
                cardSource: null);

    /// <summary>
    /// THE POOL OVERHAUL (2026-10-13): an Elemental Reaction she triggered.
    /// Called from the one place the mod resolves a reaction
    /// (<c>CompanionOverhaulReactions.Note</c>), whose dealer is her for her
    /// cards, her Companions and the Bake-Kurage's Plans alike (a Plan's hit
    /// passes her as the applier, `EB-334`).
    ///   * All Streams Flow to the Sea's per-combat count
    ///     (<see cref="KokomiOverhaulLedger.ReactionsThisCombat"/>);
    ///   * Grand Strategist: "Whenever you trigger an Elemental Reaction,
    ///     deal 4 damage to ALL enemies" -- any reaction credited to her (was
    ///     a Plan's alone);
    ///   * Coordinated Tide: a Companion card's own hit reacted, played or
    ///     carried out as a Plan -- add a Sting;
    ///   * Jellyfish Current: a Sting's own hit reacted -- add a Sting.
    /// "Its own hit" is <paramref name="cardSource"/>, the card the game's
    /// damage carried, or, for a Plan line's hit (which goes out through
    /// <c>ElementalHit.Deal</c> with no card), the card that wrote the Plan
    /// (<see cref="CreditHits"/>, opened by <c>KokomiPlan.Hit</c>). The
    /// Bake-Kurage's Hydro before a written Companion credits no card.
    /// JELLYFISH CURRENT IS BOUNDED: each reaction consumes the aura it
    /// reacted with (the thin-deck loop rule's known set). Sim twin:
    /// <c>kokomi_plan.note_reaction</c>.
    /// </summary>
    public static async Task OnReaction(PlayerChoiceContext choiceContext,
                                        Creature? dealer,
                                        CardModel? cardSource = null)
    {
        if (dealer == null || !KokomiOverhaul.LiveFor(dealer)) return;
        KokomiOverhaulLedger.For(dealer).NoteReaction();
        var amount = (int)dealer.Powers.OfType<GrandStrategistPower>()
            .Sum(p => p.Amount);
        if (amount > 0 && dealer.CombatState is { } combat)
        {
            foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                        .ToList())
            {
                await ElementalHit.DealUnelemented(choiceContext, enemy,
                                                   amount, dealer,
                                                   powered: false);
            }
        }
        var card = cardSource ?? _creditedHit;
        if (card == null) return;
        var tide = (int)dealer.Powers.OfType<CoordinatedTidePower>()
            .Sum(p => p.Amount);
        if (tide > 0 && IsCompanionHit(card))
        {
            await KokomiCards.AddJellyfish(dealer.Player,
                KokomiCards.Jellyfish.Sting, tide, upgraded: false);
        }
        var current = (int)dealer.Powers.OfType<JellyfishCurrentPower>()
            .Sum(p => p.Amount);
        if (current > 0 && card is ProtoKkSting)
        {
            await KokomiCards.AddJellyfish(dealer.Player,
                KokomiCards.Jellyfish.Sting, current, upgraded: false);
        }
    }

    /// <summary>Coordinated Tide's "a Companion": the arm's one definition
    /// (<see cref="CompanionHexerei.CountsAsCompanion"/>, the sim's
    /// <c>companion_hexerei.counts_as_companion</c>). PURE.</summary>
    public static bool IsCompanionHit(CardModel? card)
    {
        if (card == null) return false;
        if (card is ICompanionCard) return true;
        // Alice's Introduction Magic reads the owner, which a canonical copy
        // has none of (its getter asserts): such a card is not a Companion.
        try
        {
            return card.IsMutable && CompanionHexerei.CountsAsCompanion(card);
        }
        catch (System.Exception)
        {
            return false;
        }
    }

    private static CardModel? _creditedHit;

    /// <summary>The card a Plan line's hit is credited to right now, or
    /// null. Read by <see cref="OnReaction"/>.</summary>
    public static CardModel? CreditedHit => _creditedHit;

    /// <summary>
    /// THE POOL OVERHAUL (2026-10-13): credit the hits inside this scope to
    /// <paramref name="card"/> -- a Plan line's hit is the writing card's own
    /// hit. Opened by <c>KokomiPlan.Hit</c> around its
    /// <c>ElementalHit.Deal</c> calls, which carry no card; the previous
    /// credit comes back on dispose, so a scope opened inside another (a
    /// Grand Strategist volley inside a Plan's reaction) cannot leak.
    /// </summary>
    public static HitCredit CreditHits(CardModel? card) => new(card);

    /// <summary><see cref="CreditHits"/>' scope.</summary>
    public readonly struct HitCredit : System.IDisposable
    {
        private readonly CardModel? _was;

        internal HitCredit(CardModel? card)
        {
            _was = _creditedHit;
            _creditedHit = card;
        }

        public void Dispose() => _creditedHit = _was;
    }
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
          + "Common Inazuma "
          + "{Amount:plural:[gold]Companion[/gold]|[gold]Companions[/gold]} "
          + "to your [gold]Hand[/gold]. "
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
          + "[gold]Hand[/gold]."),
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

/// <summary>
/// Watchful Shoal (Kokomi round-3 changes, 2026-10-12): "Your Stings deal 3
/// additional damage. Your Wards gain 3 additional Block." The base game's
/// Accuracy, on the jellyfish.
///
/// THREE PLACES A JELLYFISH NUMBER IS MADE, and this reaches each:
/// a Sting's or Ward's NOW-LINE, played or carried out by a flip, goes
/// through the engine's hooks (<see cref="ModifyDamageAdditive"/>,
/// <see cref="ModifyBlockAdditive"/>), which is also what folds the face; a
/// Sting's PLAN LINE is an unpowered planned hit the hooks never see, so its
/// bonus is folded at writing with her Strength
/// (<see cref="KokomiPlan.Hers"/> asks <see cref="StingBonus"/>), and the
/// face's <c>PlanDamageVar</c> previews the same call. A Ward's Plan line
/// gains no Block. Sim twin: <c>kokomi_plan.watchful_shoal_bonus</c>.
/// </summary>
public sealed class WatchfulShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watchful Shoal"),
        ("description",
            "Your [gold]Stings[/gold] deal [blue]{Amount}[/blue] additional "
          + "damage. Your [gold]Wards[/gold] gain [blue]{Amount}[/blue] "
          + "additional [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The Plan-line bonus a Sting written now carries: the stack
    /// on <paramref name="kokomi"/>, 0 for any other card.</summary>
    public static int StingBonus(Creature? kokomi, CardModel? card)
    {
        if (kokomi == null || card is not ProtoKkSting) return 0;
        return (int)kokomi.Powers.OfType<WatchfulShoalPower>()
            .Sum(p => p.Amount);
    }

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (Owner == null || dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        return cardSource is ProtoKkSting ? Amount : 0m;
    }

    public override decimal ModifyBlockAdditive(
        Creature target, decimal block, ValueProp props,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (Owner == null || target != Owner) return 0m;
        return cardSource is ProtoKkWard ? Amount : 0m;
    }
}

/// <summary>Coordinated Tide (the pool overhaul, 2026-10-13, the bridge):
/// "Whenever a Companion triggers an Elemental Reaction, add a Sting to your
/// Hand." A Companion card's own hit, played or carried out as a Plan; copies
/// add one each. Paid from <see cref="KokomiRefounding.OnReaction"/>. (Was
/// a hit whenever the Bake-Kurage carried out an Ethereal card.)</summary>
public sealed class CoordinatedTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Coordinated Tide"),
        ("description",
            "Whenever a [gold]Companion[/gold] triggers an [gold]Elemental "
          + "Reaction[/gold], add [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Sting[/gold]|[gold]Stings[/gold]} to your "
          + "[gold]Hand[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Grand Strategist (the pool overhaul, 2026-10-13): "Whenever you
/// trigger an Elemental Reaction, deal 4 damage to ALL enemies." Any
/// reaction credited to her. Paid from
/// <see cref="KokomiRefounding.OnReaction"/>.</summary>
public sealed class GrandStrategistPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Strategist"),
        ("description",
            "Whenever you trigger an [gold]Elemental Reaction[/gold], deal "
          + "[blue]{Amount}[/blue] damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Jellyfish Current (the pool overhaul, 2026-10-13): "Whenever a
/// Sting triggers an Elemental Reaction, add a Sting to your Hand." A Sting's
/// own hit -- played, flipped or carried out as its Plan line. Bounded: each
/// reaction consumes the aura it reacted with. Copies add one each. Paid
/// from <see cref="KokomiRefounding.OnReaction"/>. Sim twin:
/// <c>kokomi_plan.note_reaction</c>.</summary>
public sealed class JellyfishCurrentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Jellyfish Current"),
        ("description",
            "Whenever a [gold]Sting[/gold] triggers an [gold]Elemental "
          + "Reaction[/gold], add [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Sting[/gold]|[gold]Stings[/gold]} to your "
          + "[gold]Hand[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Battle Formation (the pool overhaul, 2026-10-13): "Whenever 3 or more
/// Plans are carried out in one turn, gain 1 Energy and draw 2 cards." Fires
/// ONCE a turn, when the third carry-out of the turn finishes
/// (<see cref="KokomiRefounding.OnCarriedOut"/>, the tail of
/// <c>KokomiPlan.ResolveEntry</c>), on the ledger's once-per-turn latch.
/// The stack is the Energy (a second copy adds 1, the face's
/// <c>{Amount:energyIcons()}</c>); the draw is 2 however many. Sim twin:
/// <c>kokomi_plan.battle_formation</c>.
/// </summary>
public sealed class BattleFormationPower : PowerModel, ILocalizationProvider
{
    public const string ClaimKey = "kk_battle_formation";

    /// <summary>The cards drawn per copy.</summary>
    public const int Draw = 2;

    /// <summary>The Plans carried out in one turn it waits for.</summary>
    public const int Threshold = 3;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Battle Formation"),
        ("description",
            $"Whenever {Threshold} or more [gold]Plans[/gold] are carried "
          + "out in one turn, gain {Amount:energyIcons()} and draw "
          + $"{Draw} cards."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does this turn's count pay? PURE over its inputs.</summary>
    public static bool Pays(int carriedOutThisTurn) =>
        carriedOutThisTurn >= Threshold;

    public static async Task OnCarriedOut(PlayerChoiceContext choiceContext,
                                          Creature kokomi)
    {
        var copies = (int)kokomi.Powers.OfType<BattleFormationPower>()
            .Sum(p => p.Amount);
        if (copies <= 0 || kokomi.Player is not { } player) return;
        var ledger = KokomiOverhaulLedger.For(kokomi);
        if (!Pays(ledger.PlansCarriedOutThisTurn)) return;
        if (!ledger.Claim(ClaimKey)) return;
        await PlayerCmd.GainEnergy(copies, player);
        await CardPileCmd.Draw(choiceContext, Draw, player);
    }
}

/// <summary>Undercurrent Snare's Plan line (the pool overhaul, 2026-10-13):
/// "Each enemy that intends to attack loses 3 Strength this turn." The base
/// game's temporary Strength loss, returned at the end of the turn, Cover
/// Your Ears!'s shape. Sim twin: <c>temp_strength_down</c>.</summary>
public sealed class UndercurrentSnarePower : TemporaryStrengthPower,
                                             ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Undercurrent Snare"),
        ("description",
            "Lose [blue]{Amount}[/blue] [gold]Strength[/gold] this turn."),
    };

    public override AbstractModel OriginModel =>
        ModelDb.Card<ProtoKkUndercurrentSnare>();

    protected override bool IsPositive => false;
}

/// <summary>Endless Shoal (the jellyfish build, 2026-10-12): "Whenever the
/// Bake-Kurage carries out a Plan, add a Sting to your hand." Paid from
/// <see cref="KokomiRefounding.OnCarriedOut"/>, once per carry-out; copies
/// add one each.</summary>
public sealed class EndlessShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Endless Shoal"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], add [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Sting[/gold]|[gold]Stings[/gold]} to your "
          + "[gold]Hand[/gold]."),
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
