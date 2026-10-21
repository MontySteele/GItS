using System;
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
            // Kurage Lantern (Kokomi's own relics, 2026-10-15): one made
            // while she holds it is not Ethereal.
            Relics.KurageLantern.Steady(owner.Creature, card);
            await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand,
                                                        owner);
            made++;
            // Kokomi round 3 A-list (2026-10-13): a full hand sent it to the
            // discard pile; the page says so ("1 Sting to the discard pile
            // (hand full)") rather than the seat reading it as lost.
            if (card.Pile?.Type == PileType.Discard)
            {
                var title = card.Title
                            ?? (kind == Jellyfish.Sting ? "Sting" : "Ward");
                // Seat page backlog (2026-10-18): made inside a carry-out,
                // the line goes on that Plan's row; it printed after the
                // whole morning.
                if (!KokomiPlan.NoteDiscardedInBeat(owner.Creature, title))
                {
                    ResolutionLedger.NoteToDiscard(title);
                }
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

    /// <summary>The `shoal_call` kind: "Add N Stings to your hand." Plain
    /// Stings. Shoal Call's verb until the Kokomi taste audit (2026-10-21),
    /// which has it Plan them (<see cref="PlanStings"/>); Brine Spray's
    /// branch keeps this one.</summary>
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

    /// <summary>Crystal Collapse previews the Companion it copies (Kokomi
    /// wording pass, 2026-10-14): the card a waiting Plan caught, or, in
    /// hand, the card it would catch now. Nothing to preview, no box. A
    /// read on every hover, so it never throws.</summary>
    public static IEnumerable<IHoverTip> WithCopiedCompanionPreview(
        IEnumerable<IHoverTip> tips, CardModel card)
    {
        foreach (var tip in tips) yield return tip;
        var held = KokomiRefounding.CompanionToCopy(card);
        if (held != null) yield return HoverTipFactory.FromCard(held);
    }

    /// <summary>A face that names a Ward previews one; the upgraded one
    /// where the upgraded card hands over an upgraded Ward (Kurage Canopy,
    /// the Kokomi upgrade pass, 2026-10-19).</summary>
    public static IEnumerable<IHoverTip> WithWardPreview(
        IEnumerable<IHoverTip> tips, bool upgraded = false)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKkWard>(upgraded);
    }

    /// <summary>A face that names Sea Glass previews it, as Compact previews
    /// Fuel (the Kokomi upgrade pass, 2026-10-19): Sea Glass+ on the card
    /// whose Plan makes it.</summary>
    public static IEnumerable<IHoverTip> WithSeaGlassPreview(
        IEnumerable<IHoverTip> tips, bool upgraded)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<global::KleeMod.Cards.Prototype.SeaGlass>(upgraded);
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
        // Kokomi review r9 (2026-10-15, item 2): "It costs 0 this turn."
        var made = KokomiCompanionPlan.Generate(pick);
        made.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(made, PileType.Hand, owner);
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
    /// Energy (<see cref="KokomiRefounding.WriteFree"/>). Offered: a card with
    /// a Plan line, and since 2026-10-18 a Basic card without one ("Basic
    /// cards included"), which is planned to be played as itself
    /// (<see cref="KokomiRefounding.WriteAsItself"/>). The Kokomi finish pass
    /// (2026-10-19, sec.7 change 2): "Plan up to 3 [4] cards from your Hand.
    /// They cost 0. Draw 1 card for each. Exhaust." -- 1 card per card
    /// actually planned, drawn after all of them are written.
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
            KokomiRefounding.GrandDesignTakes, card)).ToList();
        var planned = 0;
        foreach (var chosen in picked)
        {
            var wrote = KokomiRefounding.CanBeWritten(chosen)
                ? await KokomiRefounding.WriteFree(choiceContext, chosen)
                : await KokomiRefounding.WriteAsItself(choiceContext, chosen);
            if (wrote) planned++;
        }
        if (planned > 0)
            await CardPileCmd.Draw(choiceContext, planned, owner);
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
        var done = await KokomiStatusBatch.ExhaustStatuses(
            choiceContext, owner, Amount(card), card) ?? 0;
        // Kokomi review r9 (2026-10-15, item 1): "Draw 1 card for each."
        if (done > 0)
            await CardPileCmd.Draw(choiceContext, done, owner);
    }
}

/// <summary>
/// KOKOMI'S COMPANION GENERATORS: Call the Generals, Sangonomiya's Orders and
/// their kin make Inazuma Companions. The re-founding's general rule that
/// "any Companion card can be written as a Plan" (design pass pick 4 (a),
/// 2026-10-12) lived here too and is gone (Kokomi review r9 pick 1 (a),
/// 2026-10-15; [USER]: "let's get rid of Companions as Plans unless we make a
/// card that specifically has a Plan line."): a Companion is planned only
/// through a Plan line it prints (Gorou's), on the Plan path every Plan card
/// takes, and the Bake-Kurage refuses any other.
/// </summary>
public static class KokomiCompanionPlan
{
    /// <summary>Call the Generals' "1 of 3".</summary>
    public const int GeneralsOffered = 3;

    /// <summary>The nation her generators draw from.</summary>
    public const string Nation = "inazuma";

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
        "Choose up to {Amount} cards to plan.";

    /// <summary>How many enemies are telegraphing an attack right now, by
    /// the arm's one definition (<c>CurtainCallHooks.IntendsAttack</c>).</summary>
    public static int EnemiesIntendingAttack(Creature kokomi) =>
        kokomi.CombatState?.HittableEnemies
            .Where(e => !e.IsDead)
            .Count(CurtainCallHooks.IntendsAttack) ?? 0;

    /// <summary>Can this card be written as a Plan? Only a card that prints a
    /// Plan line, a Companion included (Gorou's): Kokomi review r9 pick 1
    /// (a), 2026-10-15, dropped "any Companion card". PURE.</summary>
    public static bool CanBeWritten(CardModel? card) =>
        card is IPlannedCard { PlanClauses.Count: > 0 };

    /// <summary>GRAND DESIGN TAKES BASICS (2026-10-18, review/active/
    /// open-design-items-2026-10-18.md; [USER]: "Ok, agreed on all defaults
    /// for both the PR and inazuma companions"): a Basic Attack or Skill with
    /// no Plan line -- her Strike and Defend. Only Grand Design reads this;
    /// the Bake-Kurage still refuses such a card. PURE. Sim twin:
    /// <c>kokomi_plan.plans_as_itself</c>.</summary>
    public static bool PlansAsItself(CardModel? card) =>
        card is { Rarity: CardRarity.Basic,
                  Type: CardType.Attack or CardType.Skill }
        && !CanBeWritten(card);

    /// <summary>What Grand Design's hand screen offers: a card that can be
    /// written, or a Basic it plans as itself. PURE. Sim twin:
    /// <c>kokomi_plan.grand_design_takes</c>.</summary>
    public static bool GrandDesignTakes(CardModel? card) =>
        CanBeWritten(card) || PlansAsItself(card);

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
    /// <see cref="GrandDesignTakes"/>. A card whose read throws counts as
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

    /// <summary>Crystal Collapse's gate (Kokomi wording pass, 2026-10-14,
    /// [USER]: "Yep, please proceed"): has a Companion been played this
    /// combat? With none, its Plan was written and carried out as nothing,
    /// so the card is unplayable until one has. A canonical copy, a card
    /// with no owner and a throw all answer true (fails open,
    /// <see cref="AnyToPlan"/>'s rule). Sim twin:
    /// <c>kokomi_plan.refuses_for_no_plan</c>.</summary>
    public static bool AnyCompanionPlayed(CardModel card)
    {
        try
        {
            if (!card.IsMutable) return true;
            var kokomi = card.Owner?.Creature;
            if (kokomi?.CombatState == null) return true;
            return CompanionPlayed(KokomiOverhaulLedger.Peek(kokomi));
        }
        catch (System.Exception e)
        {
            WarnOnce(ref _warnedCompanion,
                     $"Crystal Collapse read of the ledger threw: {e}");
            return true;
        }
    }

    /// <summary><see cref="AnyCompanionPlayed"/>'s read, PURE: a ledger
    /// that holds a last Companion. No ledger yet is none played.</summary>
    public static bool CompanionPlayed(KokomiOverhaulLedger? ledger) =>
        ledger?.LastCompanionPlayed != null;

    /// <summary>The Companion Crystal Collapse copies, for its hover: the
    /// card a waiting Plan of THIS card caught when it was written, else the
    /// last Companion played this combat (what writing it now would catch).
    /// Null outside combat or with none. Never throws.</summary>
    public static CardModel? CompanionToCopy(CardModel card)
    {
        try
        {
            var owner = card.Owner;
            var kokomi = owner?.Creature;
            if (kokomi?.CombatState == null) return null;
            foreach (var entry in KokomiPlan.Showing(owner))
            {
                if (!ReferenceEquals(entry.Source, card)) continue;
                foreach (var clause in entry.Clauses)
                {
                    if (clause.Kind == KokomiPlan.Kind.PlayCopyOfCompanion)
                        return clause.Card;
                }
            }
            return KokomiOverhaulLedger.Peek(kokomi)?.LastCompanionPlayed;
        }
        catch (System.Exception)
        {
            return null;
        }
    }

    private static bool _warnedCompanion;
    private static bool _warnedHand;
    private static bool _warnedCard;
    private static bool _warnedExhaust;

    private static bool CanBeWrittenSafely(CardModel card)
    {
        try
        {
            return GrandDesignTakes(card);
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

    /// <summary>Co-op state divergence (2026-10-17): a free write the last
    /// fight left suspended owes this fight nothing. Called from
    /// <see cref="KokomiPlan.ResetFight"/>.</summary>
    internal static void ResetFight() => _freeWrites.Clear();

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
    public static async Task<bool> WriteFree(PlayerChoiceContext choiceContext,
                                             CardModel card)
    {
        var kokomi = card.Owner?.Creature;
        if (!KokomiOverhaul.LiveFor(kokomi)) return false;
        var pet = BakeKuragePet.Of(kokomi);
        if (pet == null) return false;
        _freeWrites.Add(card);
        try
        {
            await CardCmd.AutoPlay(choiceContext, card, pet);
        }
        finally
        {
            _freeWrites.Remove(card);
        }
        return true;
    }

    /// <summary>
    /// GRAND DESIGN TAKES BASICS (2026-10-18): a Basic card with no Plan line,
    /// planned. It goes from her hand to the Discard Pile, where a played
    /// card goes (moved, not played: no card-played hook sees it now), and a
    /// one-clause Plan is written under it, <see cref="KokomiPlan.Kind.PlayAsItself"/>,
    /// which plays a free copy of it at the carry-out. It is an ordinary Plan
    /// in every count (Chain lines, Endless Shoal, Battle Formation, Nereid's
    /// Ascension's double), and it has one line, so it cannot be flipped. No
    /// jellyfish, nothing (<see cref="WriteFree"/>'s rule). Sim twin:
    /// <c>kokomi_plan.write_as_itself</c>.
    /// </summary>
    public static async Task<bool> WriteAsItself(PlayerChoiceContext choiceContext,
                                                 CardModel card)
    {
        var kokomi = card.Owner?.Creature;
        if (!KokomiOverhaul.LiveFor(kokomi)) return false;
        if (BakeKuragePet.Of(kokomi) == null) return false;
        if (!PlansAsItself(card)) return false;
        await CardPileCmd.Add(card, PileType.Discard, CardPilePosition.Top);
        await KokomiPlan.Schedule(choiceContext, kokomi, card,
            new[]
            {
                new KokomiPlan.Planned(KokomiPlan.Kind.PlayAsItself, 1,
                                       KokomiPlan.Aim.FrontEnemy, card),
            });
        return true;
    }

    /// <summary>
    /// A Plan was just carried out; <paramref name="card"/> is the card that
    /// wrote it and <paramref name="line"/> the card whose line it was (they
    /// differ for Moon's Reflection). Endless Shoal (the jellyfish build,
    /// 2026-10-12; Kokomi card paper v2, 2026-10-18, sec.2 change 5):
    /// "Whenever the Bake-Kurage carries out a Plan that is not a Sting or
    /// Ward, add a Sting to your Hand." Either line; once per CARRY-OUT, so a
    /// Plan carried out twice (Nereid's Ascension, Second Wave) gives two
    /// Stings, and copies add one each. A planned Sting no longer replaces
    /// itself. (Coordinated Tide's hit is inside the carry-out,
    /// <see cref="CoordinatedTide"/>.) Sim twin:
    /// <c>kokomi_plan.note_carried_out</c>.
    /// </summary>
    public static async Task OnCarriedOut(PlayerChoiceContext choiceContext,
                                          Creature kokomi, CardModel? card,
                                          CardModel? line = null)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var stings = IsJellyfish(line ?? card)
            ? 0
            : (int)kokomi.Powers.OfType<EndlessShoalPower>().Sum(p => p.Amount);
        if (stings > 0)
        {
            await KokomiCards.AddJellyfish(kokomi.Player,
                KokomiCards.Jellyfish.Sting, stings, upgraded: false);
        }
        // (Battle Formation left this tail in the Kokomi finish pass,
        // 2026-10-19: it reads the morning's count once, at the start of
        // her turn, `BattleFormationPower.Signal`.)
        // KOKOMI REVIEW R6 (2026-10-14, pick 2 (b)): Following Current's hit.
        await FollowingCurrentPower.OnCarriedOut(choiceContext, kokomi);
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
    ///     a Plan's alone).
    /// (Coordinated Tide's and Jellyfish Current's Stings, which read the
    /// hit's own card through <paramref name="cardSource"/> or
    /// <see cref="CreditHits"/>, left with their dead power classes in the
    /// icon declutter, 2026-10-19: no row applied either.) Sim twin:
    /// <c>kokomi_plan.note_reaction</c>.
    /// </summary>
    public static async Task OnReaction(PlayerChoiceContext choiceContext,
                                        Creature? dealer,
                                        CardModel? cardSource = null)
    {
        if (dealer == null || !KokomiOverhaul.LiveFor(dealer)) return;
        KokomiOverhaulLedger.For(dealer).NoteReaction();
        // Ocean-Hued Clam (Kokomi's own relics, 2026-10-15): Mend 1.
        await Relics.KokomiArmRelics.OnReaction(choiceContext, dealer);
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
/// one each. The Kokomi upgrade pass (2026-10-19): one power for both
/// versions (<see cref="UpgradeTwinPower"/>), each upgraded copy's
/// Companion arriving upgraded (the face keeps its one sentence: a count of
/// each would pass the power ceiling, Kurage Canopy's reason). Sim twin:
/// <c>kokomi_plan.turn_start_generators</c>.</summary>
public sealed class SangonomiyasOrdersPower : UpgradeTwinPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sangonomiya's Orders"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] random "
          + "Common Inazuma "
          + "{Amount:plural:[gold]Companion[/gold]|[gold]Companions[/gold]} "
          + "to your [gold]Hand[/gold]. "
          + "{Amount:plural:It costs|They cost} 0 and "
          + "{Amount:plural:is|are} [gold]Ethereal[/gold]."),
    };

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
        foreach (var (count, upgraded) in Batches())
        {
            var made = KokomiCompanionPlan.Generated(player, CardRarity.Common)
                .TakeRandom(count, player.RunState.Rng.CombatCardGeneration)
                .Select(c => combat.CreateCard(c, player))
                .Where(c => c != null)
                .Cast<CardModel>()
                .ToList();
            foreach (var companion in made)
            {
                if (upgraded && companion.IsUpgradable && !companion.IsUpgraded)
                {
                    companion.UpgradeInternal();
                }
                // Kokomi review r9 (2026-10-15, item 3): "It costs 0."
                var free = KokomiCompanionPlan.Generate(companion);
                free.EnergyCost.SetThisTurn(0);
                await CardPileCmd.AddGeneratedCardToCombat(
                    free, PileType.Hand, player);
            }
        }
    }
}

/// <summary>Kurage Bloom. THE KOKOMI TASTE AUDIT (2026-10-21, review/active/
/// kokomi-taste-audit-2026-10-21.md, pick 1 (a)): "At the end of your turn,
/// Plan a Sting." (was "At the start of your turn, add a Sting to your
/// Hand", Infinite Blades). Copies Plan one each, so the Sting is carried
/// out the next morning. Paid from <see cref="KokomiTasteAudit.TurnEnd"/>,
/// before Watatsumi's Grace counts the Plans waiting. Sim twin:
/// <c>kokomi_plan.turn_end</c>.</summary>
public sealed class KurageBloomPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Bloom"),
        ("description",
            "At the end of your turn, [gold]Plan[/gold] [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Sting[/gold]|[gold]Stings[/gold]}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>A badge that names a Sting previews one.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiCards.WithStingPreview(System.Array.Empty<IHoverTip>());
}

/// <summary>
/// Watchful Shoal (Kokomi round-3 changes, 2026-10-12): "Your Stings deal 4
/// additional damage." The base game's Accuracy, on the Stings. (Its Ward
/// half went with the Ward's Block, 2026-10-18.)
///
/// TWO PLACES A STING NUMBER IS MADE, and this reaches both:
/// a Sting's NOW-LINE, played or carried out by a flip, goes through the
/// engine's hook (<see cref="ModifyDamageAdditive"/>), which is also what
/// folds the face; its PLAN LINE is an unpowered planned hit the hook never
/// sees, so its bonus is folded at writing with her Strength
/// (<see cref="KokomiPlan.Hers"/> asks <see cref="StingBonus"/>), and the
/// face's <c>PlanDamageVar</c> previews the same call. Sim twin:
/// <c>kokomi_plan.watchful_shoal_bonus</c>.
/// </summary>
public sealed class WatchfulShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watchful Shoal"),
        ("description",
            "Your [gold]Stings[/gold] deal [blue]{Amount}[/blue] additional "
          + "damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Kokomi review r5 (2026-10-14, A9): the badge defines the
    /// card it names, as the card's face does (<see
    /// cref="KokomiCards.WithStingPreview"/>), so "Stings" is defined where a
    /// seat reads it.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiCards.WithStingPreview(System.Array.Empty<IHoverTip>());

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

/// <summary>
/// Battle Formation (the pool overhaul, 2026-10-13; the Kokomi finish pass,
/// 2026-10-19, review/active/kokomi-cards-2026-10-18.md sec.7 change 1, ruled
/// (a)): "At the start of your turn, if 2 or more of your Plans were carried
/// out, gain 1 Energy [and draw 1 card]. Stings and Wards don't count."
/// Read ONCE, at the start of her turn, right after the morning's Plans
/// (<see cref="Signal"/>, from <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c>
/// after <c>KokomiPlan.ResolveAll</c>), off the ledger's
/// <see cref="KokomiOverhaulLedger.ChainPlansThisTurn"/> -- the morning's
/// carry-outs less the Sting and Ward Plans; a doubled carry-out counts
/// twice. One power for both versions (<see cref="UpgradeTwinPower"/>): every
/// copy adds 1 Energy, each copy an upgraded card installed adds
/// <see cref="Draw"/> card. Sim twin: <c>kokomi_plan.battle_formation</c>.
/// </summary>
public sealed class BattleFormationPower : UpgradeTwinPower, ILocalizationProvider
{
    /// <summary>The cards each upgraded copy draws.</summary>
    public const int Draw = 1;

    /// <summary>The Plans, not Stings or Wards, it waits for.</summary>
    public const int Threshold = 2;

    /// <summary>The badge prints the plain card's sentence only. A face that
    /// also counts the upgraded copies' cards (Prima Donna's
    /// <c>{Upgraded:cond:...}</c>) runs past the 125 power ceiling
    /// (<c>tools/lint_text_conventions.py</c>), so the draw is on the card.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Battle Formation"),
        ("description",
            $"At the start of your turn, if {Threshold} or more of your "
          + "[gold]Plans[/gold] were carried out, gain "
          + "{Amount:energyIcons()}. Stings and Wards don't count."),
    };

    /// <summary>Does this morning's count pay? PURE over its inputs.</summary>
    public static bool Pays(int plansCarriedOut) =>
        plansCarriedOut >= Threshold;

    /// <summary>What the copies pay when the count pays: (Energy, cards).
    /// PURE.</summary>
    public static (int Energy, int Cards) Payout(int copies, int upgradedCopies) =>
        (Math.Max(0, copies), Math.Max(0, upgradedCopies) * Draw);

    public static async Task Signal(PlayerChoiceContext choiceContext,
                                    Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Player is not { } player) return;
        var powers = kokomi.Powers.OfType<BattleFormationPower>().ToList();
        var copies = (int)powers.Sum(p => p.Amount);
        if (copies <= 0) return;
        var ledger = KokomiOverhaulLedger.For(kokomi);
        if (!Pays(ledger.ChainPlansThisTurn)) return;
        var (energy, cards) = Payout(copies, powers.Sum(p => p.UpgradedCopies));
        if (energy > 0) await PlayerCmd.GainEnergy(energy, player);
        if (cards > 0) await CardPileCmd.Draw(choiceContext, cards, player);
    }
}

/// <summary>Undercurrent Snare's Plan line (the pool overhaul, 2026-10-13):
/// "Each enemy that intends to attack loses 4 Strength this turn." The base
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
/// Bake-Kurage carries out a Plan that is not a Sting or Ward, add a Sting to
/// your hand" (the clause since the Kokomi card paper v2, 2026-10-18). Paid from
/// <see cref="KokomiRefounding.OnCarriedOut"/>, once per carry-out; copies
/// add one each.</summary>
public sealed class EndlessShoalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Endless Shoal"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold] that is not a [gold]Sting[/gold] or "
          + "[gold]Ward[/gold], add [blue]{Amount}[/blue] "
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
        AuraPower.OpenMorning(kokomi);
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
            AuraPower.CloseMorning(kokomi);
        }
    }
}

/// <summary>
/// KOKOMI REVIEW R6 (2026-10-14, pick 2 (b)): the two Hydro sources built for
/// the act-2 boss's damage bar, beside the Bake-Kurage's own Plan hits. One
/// hit each: Hydro, dealt by her through the Bake-Kurage (a Plan hit's terms,
/// <c>powered: false</c>, so her Strength and Weak do not move it and the
/// target's Vulnerable and Block do), at <see cref="KokomiPlan.FrontEnemy"/>.
/// Credited to the Bake-Kurage in telemetry, under the Power's name. Sim
/// twin: <c>kokomi_plan.kurage_hit</c>.
/// </summary>
public static class KurageHydroSources
{
    /// <summary>Returns the body hit and what landed (before its Block;
    /// <c>ElementalHit.Deal</c>'s figure), or (null, 0) when nothing was hit.</summary>
    public static async Task<(Creature? Target, int Landed)> Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, int amount,
        string cause, bool morning)
    {
        if (amount <= 0) return (null, 0);
        var target = KokomiPlan.FrontEnemy(kokomi);
        if (target == null || target.IsDead) return (null, 0);
        using var credit = Diagnostics.DamageCredit.Open(
            kokomi, Diagnostics.DamageCredit.Pet, "Bake-Kurage",
            cause: cause, card: cause);
        if (morning) AuraPower.OpenMorning(kokomi);
        try
        {
            var landed = await ElementalHit.Deal(choiceContext, target, Element.Hydro,
                                                 amount, kokomi, powered: false);
            return (target, landed);
        }
        finally
        {
            if (morning) AuraPower.CloseMorning(kokomi);
        }
    }
}

/// <summary>Kurage Vanguard (Kokomi review r6, 2026-10-14): "At the start of
/// your turn, the Bake-Kurage deals 4 [6] Hydro damage to the front enemy."
/// Called from <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c> after the
/// morning's Plans and before Dawn Tide; copies stack into one hit. Sim
/// twin: <c>kokomi_plan.kurage_vanguard</c>.
///
/// KOKOMI BOSS RAMP (2026-10-21, [USER]: "Got it, let's try that"): a ramp,
/// "It deals 2 more each turn." The Amount IS the next hit, so the badge
/// shows it: 4, 6, 8 ... [6, 8, 10 ...]. After each trigger the power grows
/// by <see cref="Growth"/>. A second copy adds its base to the next hit; the
/// growth stays 2 a turn whatever the copies.</summary>
public sealed class KurageVanguardPower : PowerModel, ILocalizationProvider
{
    /// <summary>"It deals 2 more each turn." Sim twin:
    /// <c>C.KOKOMI_KURAGE_VANGUARD_GROWTH</c>.</summary>
    public const int Growth = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Vanguard"),
        ("description",
            "At the start of your turn, the [gold]Bake-Kurage[/gold] deals "
          + "[blue]{Amount}[/blue] [gold]Hydro[/gold] damage. It deals 2 "
          + "more each turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The hit after <paramref name="triggers"/> earlier triggers of
    /// a power that started at <paramref name="baseAmount"/>. PURE.</summary>
    public static int HitAfter(int baseAmount, int triggers) =>
        baseAmount + Growth * triggers;

    public static async Task Signal(PlayerChoiceContext choiceContext,
                                    Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var powers = kokomi!.Powers.OfType<KurageVanguardPower>().ToList();
        if (powers.Count == 0) return;
        var amount = (int)powers.Sum(p => p.Amount);
        await KurageHydroSources.Hit(choiceContext, kokomi, amount,
                                     "Kurage Vanguard", morning: true);
        // The ramp: the next hit is 2 more. One host grows, so copies that
        // stacked into one instance (Counter) grow once.
        await PowerCmd.ModifyAmount(choiceContext, powers[0], Growth,
                                    applier: kokomi, cardSource: null,
                                    silent: true);
    }
}

/// <summary>Following Current (Kokomi review r6, 2026-10-14): "Whenever a
/// Plan is carried out, the Bake-Kurage deals 3 [4] Hydro damage to the front
/// enemy." Once per carry-out, after the Plan's own clauses, either line
/// (<see cref="KokomiRefounding.OnCarriedOut"/>); copies stack into one hit.
/// Sim twin: <c>kokomi_plan.following_current</c>.</summary>
public sealed class FollowingCurrentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Following Current"),
        ("description",
            "Whenever a [gold]Plan[/gold] is carried out, the "
          + "[gold]Bake-Kurage[/gold] deals [blue]{Amount}[/blue] "
          + "[gold]Hydro[/gold] damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static async Task OnCarriedOut(PlayerChoiceContext choiceContext,
                                          Creature kokomi)
    {
        var amount = (int)kokomi.Powers.OfType<FollowingCurrentPower>()
            .Sum(p => p.Amount);
        var (target, landed) = await KurageHydroSources.Hit(
            choiceContext, kokomi, amount, "Following Current",
            morning: KokomiPlan.InMorning(kokomi));
        // Kokomi v3 seats (2026-10-18): the page printed no line for this
        // hit, so seats thought it never fired. It goes on the carry-out's
        // own row ("Following Current: 3 Hydro to Louse").
        KokomiPlan.NoteAfter(kokomi, "Following Current", landed, target);
    }
}
