using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// Klee's real starting relic (spec C1.4/C2.3, klee-character-design.md §23):
/// +1 Spark per Bomb detonation. This is the talent-relic — her weapon slot is
/// folded into it per design principles §118 — and it is what makes the
/// demolition deck feed the Spark economy: bombs pop, sparks bank, the third
/// spark makes the next real Attack free.
///
/// Subscribes to BombPower's detonation bus by interface, once per bomb — a
/// 3-bomb pop banks 3 Sparks (sim parity: the grant is inside the per-bomb
/// loop in tier0/engine/effects.py).
///
/// autoAdd: false for the same reason as the cards (DECISIONS finding 14):
/// BaseLib's auto-registration demands a [Pool] attribute, and this relic is
/// not pool content — it exists only as StartingRelics[0]. ModelDb still
/// registers the type itself, which is all StartingRelics needs.
/// </summary>
public sealed class PoundingSurprise : CustomRelicModel, IBombDetonationListener
#if PROTOTYPE_CARDS
    // QUARANTINED. Under the Klee overhaul the relic IS the Spark rule (the
    // ruled brief sec.8), so it listens to the arm's explosion bus as well as
    // to the shipped detonation bus. The seam is inside the switch, so a
    // release build neither compiles the interface nor references it.
    , Powers.IProtoExplosionListener
#endif
{
    public PoundingSurprise()
        : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>
    /// G-C3. Touch of Orobas asks this; without it BaseLib's
    /// StarterUpgradePatches prefix falls through to vanilla's hardcoded
    /// dictionary, which does not know us and returns the no-effect Circlet --
    /// so the act-2 "upgrade your starter" reward silently DELETED Klee's
    /// talent relic. See Relics/UpgradedStarterRelics.cs for the full trace.
    /// </summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<ExplosiveFrags>().ToMutable();

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pounding Surprise"),
        ("description",
#if KLEE_OVERHAUL
            // The arm's cards say "Set off" for the action and "goes off"
            // for the event; the relic uses the event word there.
            "Whenever a [gold]Bomb[/gold] goes off, gain 1 [gold]Spark[/gold]. "
#else
            "Whenever a [gold]Bomb[/gold] detonates, gain 1 [gold]Spark[/gold]. "
#endif
          + CompanionSlot.RewardSlotDescription),
    };

    /// <summary>
    /// FALLBACK ICON. RelicModel's icon-path getters are virtual, so the pck
    /// texture wires in directly below; the Burning Blood slug remains for
    /// when the pack is absent, and for the OUTLINE atlas entry, which we
    /// ship no asset for yet. There is no in-run collision because this relic
    /// exists precisely to REPLACE Burning Blood in Klee's starting slot.
    /// </summary>
    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.BigIconPath;

    /// <summary>
    /// The companion reward slot (tier05 roll_rewards, standard mode): one
    /// companion appended to the FIGHT card reward's options.
    ///
    /// Hosted here because the starter relic is the one model guaranteed
    /// present for the whole of every Klee run, and relics are this hook's
    /// intended listeners (AbstractModel doc: Orrery, Tiny Mailbox).
    ///
    /// CORRECTION OF RECORD (playtest 2026-07-21). This first shipped as
    /// TryModifyRewards + SpecialCardReward, which put the companion in its
    /// own reward row -- so the player could take a card AND the companion.
    /// That is not the law: tier05 roll_rewards returns ONE offers list,
    /// REWARD_CARD_OFFERS cards with the companion appended, and the draft
    /// policy picks one from it. TryModifyCardRewardOptions is the hook that
    /// mirrors that exactly -- it appends to the card reward's own option
    /// list, so the companion is a genuine 4th choice competing with the
    /// three cards. Fired from CardFactory.CreateForReward after the cards
    /// are rolled.
    ///
    /// Source == Encounter is the "post-fight reward" gate (the enum's own
    /// doc); Shop and Other (events, relic-granted picks) get no companion,
    /// matching roll_rewards being the post-fight function. BossEncounter
    /// odds identify the end-of-act reward and force this fourth slot to the
    /// Rare companion tier.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter) return false;
        if (player.Character is not Klee) return false;

        var companionRarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, companionRarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target, int damage)
    {
        // Own bombs only: in co-op another player's detonations are theirs.
        if (applier?.Player != Owner) return;

        Flash();
        await SparkPower.Gain(choiceContext, Owner.Creature, 1, cardSource: null,
            source: "relic:pounding_surprise/detonation");
    }

#if PROTOTYPE_CARDS
    /// <summary>
    /// THE OVERHAUL'S RULE 4, and the whole of what this relic does under that
    /// arm: one Spark per EXPLOSION.
    ///
    /// It is the same body as the shipped hook above, pointed at the arm's own
    /// bus, because it is the same rule -- the brief simply makes it the only
    /// Spark source there is ("Under this flag Sparks come ONLY from
    /// explosions"). The relic's OTHER hook, the companion reward slot, is not
    /// gated off: it is not a Spark rule and not a Bomb rule, and the slice's
    /// React loop draws its appliers from that very slot (sec.4, "Appliers come
    /// from the Mondstadt Universals already in her pool"). Turning it off
    /// would delete a loop the slice is trying to test.
    ///
    /// The flag guard means a dev build running the SPARKS arm is untouched by
    /// this: no proto Bomb exists there, so the bus never rings, but the guard
    /// says so rather than relying on it.
    /// </summary>
    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (!Powers.KleeOverhaul.Enabled) return;
        if (applier.Player != Owner) return;    // co-op: your explosions only

        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature,
            Powers.KleeOverhaulLaw.SparkPerExplosion,
            cardSource: null, source: "relic:pounding_surprise/explosion");
    }
#endif
}
