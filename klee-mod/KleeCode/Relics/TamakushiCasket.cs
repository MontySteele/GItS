#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// TAMAKUSHI CASKET -- the Kokomi overhaul's starting relic (ruled brief draft
/// 6 sec.4 pick 3; slice draft 6 sec.3).
///
/// "The Bake-Kurage is out from the start of every combat. Whenever you apply a
/// debuff to an enemy, it strikes that enemy for 2 Hydro damage."
///
/// IT REPLACES TAMANOOYA'S CASKET, which is a rename and a rewrite in one: the
/// old spelling was wrong (the Watatsumi treasure is the Tamakushi), and the
/// old body was the pulse -- "at the end of each turn you did not Surge it
/// Mends you 2, up to 8 per combat" -- which the ruled brief's sec.6 cuts along
/// with the Surge it was priced against. It also replaces the Pearl of Wisdom
/// under the arm, because the Pearl IS the exhaust-for-Charge funnel the brief
/// retires; a run holding it would print a rule the arm has turned off.
///
/// IT IS LIVE FROM TURN ONE, which is the whole argument for pick 3's default:
/// Slack Water applies Weak on the first turn of the first fight, so the
/// jellyfish strikes before the player has read anything. The pool's status
/// lines feed it on purpose (slice sec.4) -- Slack Water, Exposed Flank, War
/// Council, Vanguard, Sea-Salt Prayer, Rally and the Banner all make it strike
/// -- and so do REACTIONS, since Superconduct, Overloaded and Frozen each apply
/// a debuff.
///
/// THE JELLYFISH IS THE DEALER, and that is a reading rather than a detail: the
/// slice says "it strikes that enemy for 2", so the applier handed to the
/// shared elemental pipeline is the PET. A pet carries no Strength, so the 2 is
/// a flat 2 -- which is what makes this the relic's number and not a scaling
/// engine attached to every debuff she applies. (Draft 6 gives her Strength
/// back; routing this through her would have quietly made the Casket the best
/// Strength payoff in the pool.) The hit is otherwise REAL: Block, Vulnerable,
/// the aura and the reaction all apply, because it goes through the same
/// <see cref="ElementalHit"/> funnel every other non-attack hit in this mod
/// does.
///
/// THE WHOLE FILE IS QUARANTINED. It sits in <c>Relics/</c> rather than under
/// <c>Powers/Prototype/</c>, which the csproj Compile-Removes, for one reason:
/// <c>tools/lint_unique_names.py</c> reads relic display names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c> and nowhere else, and R69 put relic
/// names in the same namespace as card names. A prototype relic hidden from
/// that lint could mint a name a shipped card already owns. So the QUARANTINE
/// is the <c>#if PROTOTYPE_CARDS</c> wrapping the entire file, and the name
/// still reaches the lint, because the lint reads text.
///
/// IT KEEPS THE COMPANION REWARD SLOT. That hook is not a pulse rule and not a
/// Charge rule, and the slice's Commander loop draws its whole army from that
/// very slot; dropping it would delete one of the three loops the slice exists
/// to test. Same reasoning, one arm over, as <c>PoundingSurprise</c>'s.
/// </summary>
public sealed class TamakushiCasket : CustomRelicModel
{
    public TamakushiCasket() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Tamakushi Casket"),
        ("description",
            "The [gold]Bake-Kurage[/gold] is out from the start of every "
          + "combat. Whenever you apply a debuff to an enemy, it strikes that "
          + "enemy for " + KokomiOverhaulLaw.CasketStrike + " Hydro damage. "
          + CompanionSlot.RewardSlotDescription),
    };

    /// <summary>
    /// The relic's first sentence, made true by the relic itself.
    ///
    /// REDUNDANT WITH THE KIT'S OWN INSTALL, deliberately.
    /// <c>KokomiRules.InstallAll</c> already summons the jellyfish from the
    /// same hook because rule 1 is a KIT rule and holds whether or not she is
    /// still carrying this -- but the relic prints the sentence, so the relic
    /// makes it true too. Both calls are idempotent
    /// (<see cref="BakeKuragePet.Summon"/> returns early if the pet is out), so
    /// the belt costs one lookup.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        if (!KokomiOverhaul.LiveFor(Owner?.Creature)) return;
        await BakeKuragePet.Summon(Owner);
    }

    /// <summary>
    /// The strike. <c>AfterPowerAmountChanged</c> is the hook because it is the
    /// one the game raises on BOTH <c>PowerCmd</c> paths and fans to every
    /// model in the combat, so nothing that puts a debuff on an enemy can slip
    /// past it -- a card, a Plan, a companion or a reaction.
    ///
    /// WHAT COUNTS AS APPLYING A DEBUFF IS NOT DECIDED HERE.
    /// <see cref="KokomiOverhaulKit.IsHerDebuffOnEnemy"/> is the one predicate,
    /// shared with The Clouds Like Waves Rippling, so the relic and the card
    /// cannot come to disagree about the event they both answer.
    ///
    /// THE LATCH IS NOT PARANOIA: a Hydro strike into a Cryo aura Freezes, and
    /// Frozen is a debuff she applied to an enemy. Without
    /// <see cref="KokomiOverhaulKit.Answer"/> the relic would answer its own
    /// answer until the stack ran out.
    /// </summary>
    public override async Task AfterPowerAmountChanged(
        PlayerChoiceContext choiceContext, PowerModel power, decimal amount,
        Creature? applier, CardModel? cardSource)
    {
        var kokomi = Owner?.Creature;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (!KokomiOverhaulKit.IsHerDebuffOnEnemy(power, amount, applier, kokomi))
        {
            return;
        }
        var target = power.Owner;
        if (target == null) return;
        await KokomiOverhaulKit.Answer(async () =>
        {
            Flash();
            await Strike(choiceContext, kokomi!, target);
        });
    }

    /// <summary>The jellyfish's hit, in one place so a pin and the relic read
    /// the same arithmetic. The pet is the dealer; with no pet on the board she
    /// is, which is the honest degradation rather than a silent no-op.</summary>
    public static async Task Strike(
        PlayerChoiceContext choiceContext, Creature kokomi, Creature target)
    {
        if (target.IsDead) return;
        var dealer = BakeKuragePet.Of(kokomi) ?? kokomi;
        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro,
            KokomiOverhaulLaw.CasketStrike, dealer);
    }

    /// <summary>
    /// Her fourth companion reward option, kept from the Pearl of Wisdom
    /// unchanged -- see this class's header for why it is not gated off with
    /// the rest of the shipped kit.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Kokomi)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds
                     == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>
    /// FALLBACK ICON, borrowed from the relic whose slot this takes. Art is
    /// commissioned when a slice is ACCEPTED, not before -- the same rule the
    /// Klee overhaul's power icons follow.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}
#endif
