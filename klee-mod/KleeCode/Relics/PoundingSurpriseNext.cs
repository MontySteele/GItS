using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// THE TEMPO RELIC, A STAGING TEST AND NOT A STARTER CHANGE (the Klee scaling
/// pass, klee-next 2026-10-05, `review/active/klee-scaling-pass-2026-10-05.md`
/// sec.4 D; pick 5 stays [USER]'s). A copy of <see cref="PoundingSurprise"/>
/// -- the Spark per explosion, the companion reward slot, the Touch of Orobas
/// upgrade -- that ALSO does: "At the start of each combat, place a Bomb 6 on
/// a random enemy."
///
/// GRANT-ONLY. A member of <c>KleeRelicPool</c> (a poolless relic throws at
/// <c>RelicModel.Pool</c>) and NOT in <c>ArmRelicPools.KleeArmPool</c>, so no
/// reward, shop or event offers it; Starter rarity besides. The only door is
/// embark's <c>--relic KLEEMOD-POUNDING_SURPRISE_NEXT</c>.
///
/// IT REPLACES POUNDING SURPRISE: <see cref="AfterObtained"/> removes the
/// original, so she never holds both (two would pay two Sparks an explosion).
///
/// THE TIMING, read off the 0.111.0 decompile (<c>CombatManager
/// .StartCombatInternal</c>): <c>Hook.BeforeCombatStart</c> runs once, after
/// every creature is in and BEFORE the first <c>StartTurn</c>, whose
/// <c>Hook.BeforeSideTurnStart</c> on the player side is where
/// <c>ProtoBombPower</c> grows (rule 1, +4) -- on turn 1 as on every turn. So
/// the Bomb placed here is 6 when it lands and 10 when she first acts, which
/// is the paper's "Turn 1 then holds a real choice: Ka-pow! it now, or cook
/// it." The hook carries no <c>PlayerChoiceContext</c>, and a placement asks
/// for no choice, so it runs under a <c>ThrowingPlayerChoiceContext</c>, the
/// Furina Stage's arrangement for the same shape.
/// </summary>
public sealed class PoundingSurpriseNext : CustomRelicModel,
    IBombDetonationListener, IProtoExplosionListener
{
    /// <summary>The Bomb it places at the start of each combat.</summary>
    public const int OpeningBomb = 6;

    public PoundingSurpriseNext() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<ExplosiveFrags>().ToMutable();

    public override List<(string, string)>? Localization => new()
    {
        // A title of its own: the repo's names are unique
        // (`tools/lint_unique_names.py`), and she never holds both.
        ("title", "Pounding Surprise II"),
        ("description",
            "Whenever a [gold]Bomb[/gold] goes off, gain [blue]"
          + KleeOverhaulLaw.SparkPerExplosion + "[/blue] [gold]Spark[/gold]. "
          + "At the start of each combat, place a [gold]Bomb[/gold] [blue]"
          + OpeningBomb + "[/blue] on a random enemy."),
    };

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.BigIconPath;

    /// <summary>Granted: the original leaves, so this one REPLACES it.</summary>
    public override async Task AfterObtained()
    {
        await base.AfterObtained();
        foreach (var original in Owner.Relics.OfType<PoundingSurprise>().ToList())
        {
            await RelicCmd.Remove(original);
        }
    }

    /// <summary>The start-of-combat Bomb (see the class note for the timing).</summary>
    public override async Task BeforeCombatStart()
    {
        var klee = Owner?.Creature;
        if (klee == null || klee.IsDead || klee.CombatState == null) return;
        Flash();
        await ProtoBombPower.PlaceOnRandom(new ThrowingPlayerChoiceContext(),
                                           klee, OpeningBomb, isMine: false,
                                           payloadMineAll: 0, cardSource: null);
    }

    // ---- Pounding Surprise's own two rules, unchanged ---------------------

    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Klee);

    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
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
        if (applier?.Player != Owner) return;
        Flash();
        await SparkPower.Gain(choiceContext, Owner.Creature, 1, cardSource: null,
            source: "relic:pounding_surprise_next/detonation");
    }

    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (applier.Player != Owner) return;
        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature, KleeOverhaulLaw.SparkPerExplosion,
            cardSource: null, source: "relic:pounding_surprise_next/explosion");
    }
}
