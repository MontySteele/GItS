using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// KOKOMI'S OWN RELICS (<c>review/active/kokomi-relics-potions-2026-10-15.md</c>,
/// kit census pick 1 (a), ruled 2026-10-15). The base game's shape, Klee's and
/// Varka's: one Common, two Uncommons, three Rares and one Shop relic beside
/// the Tamakushi Casket. They, the Casket and the Watatsumi Casket are her
/// whole relic offer; the Silent borrow leaves the offer (census pick 2).
///
/// UNDER <c>Relics/</c>, so the
/// titles stay in <c>tools/lint_unique_names.py</c>'s namespace. Every effect
/// asks <see cref="KokomiOverhaul.IsHers"/>, so a relic held by anyone else
/// does nothing. No relic writes or carries out a Plan by itself (brief rule
/// 4, "Nothing happens by itself").
///
/// NO SIM TWIN: tier0's Kokomi twin models the Casket and no other relic, as
/// Varka's and Klee's own relics have none until Balance.
/// </summary>
public static class KokomiArmRelics
{
    /// <summary>The seven, in the paper's table order. The pool reads this
    /// list and nothing else.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(SangoPearl), typeof(ResistanceArmband), typeof(ElectroSigil),
        typeof(EverlastingMoonglow), typeof(OceanHuedClam),
        typeof(KurageLantern), typeof(ResistanceMusterRoll),
    };

    /// <summary>How many copies of <typeparamref name="T"/> this Kokomi
    /// holds; 0 for anyone else.</summary>
    internal static int Held<T>(Creature? kokomi) where T : RelicModel =>
        KokomiOverhaul.IsHers(kokomi) && kokomi!.Player is { } player
            ? player.Relics.OfType<T>().Count()
            : 0;

    /// <summary>Flash every copy of <typeparamref name="T"/> she holds.
    /// </summary>
    internal static void FlashAll<T>(Creature kokomi) where T : RelicModel
    {
        foreach (var relic in kokomi.Player?.Relics.OfType<T>().ToList()
                              ?? new List<T>())
        {
            relic.Flash();
        }
    }

    /// <summary>The turn-one gate Fresh Catch uses: her own first turn.
    /// </summary>
    public static bool FirstTurnOf(RelicModel relic, Player player) =>
        player == relic.Owner
        && KokomiOverhaul.IsHers(player.Creature)
        && player.PlayerCombatState?.TurnNumber == 1
        && player.Creature is { IsDead: false };

    internal static string Icon(string slug) => "kokomi/relics/" + slug + ".png";

    /// <summary>
    /// A Plan was just carried out (<c>KokomiPlan.ResolveEntry</c>, the one
    /// place a Plan is carried out: the morning, Change of Plans and Bottled
    /// Tide). Everlasting Moonglow's hook.
    /// </summary>
    internal static Task AfterPlanCarriedOut(
        Creature kokomi, CardModel? card) =>
        EverlastingMoonglow.Return(kokomi, card);

    /// <summary>A reaction she triggered
    /// (<c>KokomiRefounding.OnReaction</c>, from the one reaction funnel).
    /// Ocean-Hued Clam's hook.</summary>
    internal static Task OnReaction(
        PlayerChoiceContext choiceContext, Creature kokomi) =>
        OceanHuedClam.Mend(choiceContext, kokomi);
}

/// <summary>A relic of hers: Burning Blood until the art pass puts her own
/// file in the pack (Varka's relics' fallback chain).</summary>
public abstract class KokomiArmRelic : CustomRelicModel
{
    protected KokomiArmRelic() : base(autoAdd: false) { }

    /// <summary><c>kokomi/relics/&lt;slug&gt;.png</c>.</summary>
    protected abstract string Slug { get; }

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path(KokomiArmRelics.Icon(Slug)) ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path(KokomiArmRelics.Icon(Slug)) ?? base.BigIconPath;
}

/// <summary>Common. "The first card you plan each combat costs 0." Planning
/// is writing a card onto the Bake-Kurage (<see cref="KokomiPlan.PlayedOnPet"/>);
/// the cost cannot be changed at the moment the target is chosen, so the
/// Energy paid is refunded right after the play (the paper's accepted
/// reading). Once per combat, on the combat ledger's latch; a card played
/// normally costs its usual amount and the Pearl waits. The first card
/// planned spends it even when it cost nothing (Grand Design's free write).
/// </summary>
public sealed class SangoPearl : KokomiArmRelic
{
    /// <summary>The latch key on the combat ledger.</summary>
    public const string Latch = "SangoPearl";

    protected override string Slug => "sango_pearl";

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Sango Pearl"),
        ("description",
            "The first card you plan each combat costs [blue]0[/blue]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForPlanOnly(Array.Empty<IHoverTip>(), null!);

    /// <summary>Does this play spend the Pearl? Hers, written on the
    /// Bake-Kurage, the first of the combat. Claims the latch. </summary>
    public static bool Claims(CardPlay cardPlay, Creature? kokomi) =>
        KokomiArmRelics.Held<SangoPearl>(kokomi) > 0
        && cardPlay.Card.Owner?.Creature == kokomi
        && KokomiPlan.PlayedOnPet(cardPlay)
        && KokomiOverhaulLedger.For(kokomi!).ClaimOncePerCombat(Latch);

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var kokomi = Owner?.Creature;
        if (kokomi == null || cardPlay.Player != Owner) return;
        // One refund however many copies she holds: the first copy claims.
        if (Owner.Relics.OfType<SangoPearl>().FirstOrDefault() != this) return;
        if (!Claims(cardPlay, kokomi)) return;
        var paid = cardPlay.Resources.EnergySpent;
        Flash();
        // Seat page backlog (2026-10-19): the page says the discount is spent.
        ResolutionLedger.NoteRelic(PageName, SpentNote((int)paid));
        if (paid > 0) await PlayerCmd.GainEnergy(paid, Owner);
    }

    /// <summary>The printed title the page names it by.</summary>
    public const string PageName = "Sango Pearl";

    /// <summary>The page's words: "refunded 2 Energy, used this combat",
    /// or "used this combat" for a write that cost nothing. PURE.</summary>
    public static string SpentNote(int refunded) =>
        refunded > 0 ? $"refunded {refunded} Energy, used this combat"
                     : "used this combat";
}

/// <summary>Uncommon. "The first time each turn you play a Companion, gain 4
/// Block." (The paper's word order, house-ordered by text-conventions rule
/// 5.) Her Companion count's definition (<see cref="ICompanionCard"/>,
/// <c>ProtoBakeKuragePower.AfterCardPlayed</c>): played from her hand,
/// face-up or written on the Bake-Kurage. A carry-out is the jellyfish's
/// play, not hers, and does not count. Copies add.</summary>
public sealed class ResistanceArmband : KokomiArmRelic
{
    public const int Block = 4;

    public const string Latch = "ResistanceArmband";

    protected override string Slug => "resistance_armband";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Resistance Armband"),
        ("description",
            "The first time each turn you play a [gold]Companion[/gold], gain "
          + "[blue]" + Block + "[/blue] [gold]Block[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCompanion(Array.Empty<IHoverTip>(), null!);

    /// <summary>Is this play one that counts? A Companion of hers, not a
    /// carry-out. PURE on the play.</summary>
    public static bool Counts(CardPlay cardPlay, Creature? kokomi) =>
        KokomiOverhaul.IsHers(kokomi)
        && cardPlay.Card is ICompanionCard
        && cardPlay.Card.Owner?.Creature == kokomi
        && !KokomiPlan.IsCarryingOut(kokomi!.Player);

    /// <summary>The Block the turn's first Companion pays: 4 a copy.
    /// </summary>
    public static int BlockFor(Creature? kokomi) =>
        Block * KokomiArmRelics.Held<ResistanceArmband>(kokomi);

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var kokomi = Owner?.Creature;
        if (kokomi == null || cardPlay.Player != Owner) return;
        if (Owner.Relics.OfType<ResistanceArmband>().FirstOrDefault() != this) return;
        if (!Counts(cardPlay, kokomi)) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(kokomi, Latch)) return;
        var block = BlockFor(kokomi);
        if (block <= 0) return;
        KokomiArmRelics.FlashAll<ResistanceArmband>(kokomi);
        await CreatureCmd.GainBlock(kokomi, block, ValueProp.Unpowered, null,
                                    fast: true);
    }
}

/// <summary>Uncommon. "At the start of each combat, apply Electro to ALL
/// enemies." Fresh Catch's door and hook (her first turn, after the draw),
/// over every living enemy. Her first Hydro hit on each makes
/// Electro-Charged.</summary>
public sealed class ElectroSigil : KokomiArmRelic
{
    protected override string Slug => "electro_sigil";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Electro Sigil"),
        ("description",
            "At the start of each combat, apply [gold]Electro[/gold] to ALL "
          + "enemies."),
    };

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!KokomiArmRelics.FirstTurnOf(this, player)) return;
        var combat = player.Creature.CombatState;
        if (combat == null) return;
        var enemies = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (enemies.Count == 0) return;
        Flash();
        foreach (var enemy in enemies)
        {
            if (enemy.IsDead) continue;
            await ElementalHit.ApplyOnly(choiceContext, enemy, Element.Electro,
                                         player.Creature);
        }
    }
}

/// <summary>Rare. "After your first Plan each turn is carried out, return it
/// to your Hand unless it Exhausts." "First" is the first carry-out of the
/// turn, the morning's front Plan or Change of Plans' if it comes first, on
/// the ledger's once-per-turn latch; a Plan carried out twice returns once.
/// "It" is the card a cancel would give back (<c>Entry.Returns</c>), found
/// in her Draw or Discard Pile; one exhausted (a Sting, a Ward, a generated
/// Companion) or already in hand stays where it is.</summary>
public sealed class EverlastingMoonglow : KokomiArmRelic
{
    public const string Latch = "EverlastingMoonglow";

    protected override string Slug => "everlasting_moonglow";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Everlasting Moonglow"),
        ("description",
            "After your first [gold]Plan[/gold] each turn is carried out, "
          + "return it to your [gold]Hand[/gold] unless it [gold]Exhausts[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForPlanOnly(Array.Empty<IHoverTip>(), null!);

    /// <summary>Is <paramref name="card"/> where a return can reach it: her
    /// Draw or Discard Pile, never the Exhaust Pile or her hand. PURE.
    /// </summary>
    public static bool Returnable(CardModel? card) =>
        card?.Pile?.Type is PileType.Draw or PileType.Discard;

    /// <summary>The hook (<see cref="KokomiArmRelics.AfterPlanCarriedOut"/>).
    /// The turn's first carry-out spends the latch whether or not its card
    /// can come back.</summary>
    internal static async Task Return(Creature kokomi, CardModel? card)
    {
        if (KokomiArmRelics.Held<EverlastingMoonglow>(kokomi) <= 0) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(kokomi, Latch)) return;
        if (!Returnable(card) || card!.Owner?.Creature != kokomi) return;
        KokomiArmRelics.FlashAll<EverlastingMoonglow>(kokomi);
        // Seat page backlog (2026-10-19): a full hand sends the card to the
        // Discard Pile (the base game's rule), and the page says which.
        string name;
        try { name = card.Title?.ToString() ?? string.Empty; }
        catch (Exception) { name = string.Empty; }
        var full = kokomi.Player is { } player
                   && PileType.Hand.GetPile(player).Cards.Count
                      >= CardPile.MaxCardsInHand;
        ResolutionLedger.NoteRelic(PageName, ReturnNote(name, full));
        await CardPileCmd.Add(card, PileType.Hand);
    }

    /// <summary>The printed title the page names it by.</summary>
    public const string PageName = "Everlasting Moonglow";

    /// <summary>The page's words: "returned Ward to your hand", or, at a
    /// full hand, "your hand was full, so Ward went to your Discard Pile".
    /// PURE.</summary>
    public static string ReturnNote(string card, bool handFull)
    {
        var what = card.Length > 0 ? card : "the card";
        return handFull
            ? $"your hand was full, so {what} went to your Discard Pile"
            : $"returned {what} to your hand";
    }
}

/// <summary>Rare. "Whenever you trigger an Elemental Reaction, Mend 1."
/// Every named reaction she triggers, Plans and Stings included, from the one
/// reaction funnel (<c>KokomiRefounding.OnReaction</c>). Mend's own ceiling
/// applies (<see cref="KokomiRules.Mend"/>). Copies add.</summary>
public sealed class OceanHuedClam : KokomiArmRelic
{
    public const int MendAmount = 1;

    protected override string Slug => "ocean_hued_clam";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ocean-Hued Clam"),
        ("description",
            "Whenever you trigger an [gold]Elemental Reaction[/gold], "
          + "[gold]Mend[/gold] [blue]" + MendAmount + "[/blue]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForMend(
            ArmKeywordTips.ForElementalReaction(Array.Empty<IHoverTip>(), null!),
            null!);

    /// <summary>The Mend one reaction asks for: 1 a copy.</summary>
    public static int MendFor(Creature? kokomi) =>
        MendAmount * KokomiArmRelics.Held<OceanHuedClam>(kokomi);

    internal static async Task Mend(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        var amount = MendFor(kokomi);
        if (amount <= 0) return;
        KokomiArmRelics.FlashAll<OceanHuedClam>(kokomi);
        var landed = await KokomiRules.Mend(choiceContext, kokomi, amount);
        // Seat page backlog (2026-10-19): the Mend had no page line.
        ResolutionLedger.NoteRelic(PageName, MendNote(amount, landed));
    }

    /// <summary>The printed title the page names it by.</summary>
    public const string PageName = "Ocean-Hued Clam";

    /// <summary>The page's words: "Mend 1, healed 1 HP", or "Mend 1, healed
    /// 0 HP (Mend stops at your HP when the fight began)". PURE.</summary>
    public static string MendNote(int amount, int landed) =>
        $"Mend {amount}, healed {landed} HP"
        + (landed < amount && landed <= 0
            ? " (Mend stops at your HP when the fight began)" : "");
}

/// <summary>Rare. "Your Stings and Wards are not Ethereal." Read where every
/// Sting and Ward is made (<see cref="KokomiCards.AddJellyfish"/>): one made
/// while she holds it loses Ethereal and keeps Exhaust, so it still Exhausts
/// when played or carried out. One made before she took it keeps
/// Ethereal.</summary>
public sealed class KurageLantern : KokomiArmRelic
{
    protected override string Slug => "kurage_lantern";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Lantern"),
        ("description",
            "Your [gold]Stings[/gold] and [gold]Wards[/gold] are not "
          + "[gold]Ethereal[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiCards.WithWardPreview(
            KokomiCards.WithStingPreview(Array.Empty<IHoverTip>()));

    /// <summary>Does a Sting or Ward made for <paramref name="kokomi"/> now
    /// lose Ethereal?</summary>
    public static bool Holds(Creature? kokomi) =>
        KokomiArmRelics.Held<KurageLantern>(kokomi) > 0;

    /// <summary>The make-time edit (<see cref="KokomiCards.AddJellyfish"/>).
    /// </summary>
    public static void Steady(Creature? kokomi, CardModel card)
    {
        if (!Holds(kokomi)) return;
        card.RemoveKeyword(CardKeyword.Ethereal);
    }
}

/// <summary>Shop. "At the start of each combat, choose 1 of 3 random Inazuma
/// Companions to add to your Hand. It costs 0 this turn." Call the Generals'
/// screen (skippable, the base game's discovery) over her generators' roster
/// (<see cref="KokomiCompanionPlan.Generated"/>) at every rarity, on her
/// first turn after the draw so the cost holds (Favonius Duty Roster's hook).
/// The face names no Ethereal, so the pick arrives as it is printed.</summary>
public sealed class ResistanceMusterRoll : KokomiArmRelic
{
    protected override string Slug => "resistance_muster_roll";

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Resistance Muster Roll"),
        ("description",
            "At the start of each combat, choose 1 of "
          + KokomiCompanionPlan.GeneralsOffered + " random Inazuma "
          + "[gold]Companions[/gold] to add into your [gold]Hand[/gold]. It "
          + "costs 0 this turn."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCompanion(Array.Empty<IHoverTip>(), null!);

    /// <summary>The roster it rolls from: her Inazuma Companions at Common,
    /// Uncommon and Rare. PURE over the run's roster.</summary>
    public static List<CardModel> Roster(Player owner) =>
        new[] { CardRarity.Common, CardRarity.Uncommon, CardRarity.Rare }
            .SelectMany(r => KokomiCompanionPlan.Generated(owner, r))
            .ToList();

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!KokomiArmRelics.FirstTurnOf(this, player)) return;
        var combat = player.Creature.CombatState;
        if (combat == null) return;
        var offered = Roster(player)
            .TakeRandom(KokomiCompanionPlan.GeneralsOffered,
                        player.RunState.Rng.CombatCardGeneration)
            .Select(c => combat.CreateCard(c, player))
            .Where(c => c != null)
            .Cast<CardModel>()
            .ToList();
        if (offered.Count == 0) return;
        Flash();
        var pick = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, offered, player, canSkip: true);
        if (pick == null) return;
        pick.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(pick, PileType.Hand, player);
    }
}
