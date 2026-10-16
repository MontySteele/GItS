using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// SALON SOLITAIRE -- Furina's starting relic (the Salon's Tab, 2026-10-05,
/// proposal sec.2 rule 4 and sec.16): "At the end of your turn, Repay 1."
/// (2026-10-09 playtest trim: was Repay 2, upgraded 3.)
/// This is the Singer of Many Waters: she pays the Salon's loan back, one HP
/// a turn, and every HP repaid is a point of Fanfare. Upgraded (Touch of
/// Orobas) it is The Curtain Never Falls, which Repays 2.
///
/// THE REPAY IS THE KIT'S, AT THE END OF HER TURN AFTER THE GUESTS ACT
/// (<see cref="FurinaStage.EndOfTurnActs"/>, which reads
/// <see cref="FurinaStage.SingerOf"/>): one ordering for the guests and the
/// Singer, the sim's (`furina_tide.end_of_turn`). The relic states the rule
/// and carries the companion slot.
///
/// THE WHOLE FILE lives under <c>Relics/</c> for <c>TamakushiCasket</c>'s
/// reason: <c>tools/lint_unique_names.py</c> reads relic display names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c> and nowhere else.
/// </summary>
public sealed class SalonSolitaire : CustomRelicModel
{
    public SalonSolitaire() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>Touch of Orobas: The Curtain Never Falls, rebuilt for the
    /// Stage (the relics-and-potions paper, 2026-09-27) -- the Ethereal
    /// Spotlight's upgrade, now this starter's.</summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<CurtainNeverFalls>().ToMutable();

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Salon Solitaire"),
        ("description",
            "At the end of your turn, [gold]Repay[/gold] [blue]"
          + FurinaStageLaw.SingerRepay + "[/blue]."),
    };

    /// <summary>The combat opens: the entry Max HP the Drain buffer is read
    /// from (2026-10-11; the entry HP is still recorded for the page).
    /// Idempotent.</summary>
    public override async Task BeforeCombatStart()
    {
        var furina = Owner?.Creature;
        if (!FurinaStage.LiveFor(furina)) return;
        await FurinaStage.OpenCombat(furina);
    }

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Furina);

    /// <summary>
    /// Furina's companion reward slot, carried over from the Ethereal
    /// Spotlight this relic replaces. The starter relic is where every roster
    /// character's fourth reward choice lives, and the Stage kept companions
    /// ("Companion cards stay the shared action pool", brief sec.2). The slot
    /// was left off when the relic was written, so a Stage Furina drafted no
    /// companions at all; [USER]'s co-op run caught it (2026-09-27).
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>
    /// THE ICON is her talent's own, "Talent Salon Solitaire.png"
    /// (art/plan.tsv relic_salon_solitaire). Until 2026-10-16 this pointed
    /// at ethereal_spotlight.png, the Spotlight item picture of the relic
    /// whose slot this took, so the select screen showed a spotlight.
    ///
    /// IconBaseName names only the OUTLINE atlas sprite the base RelicModel
    /// still derives from it (<c>PackedIconOutlinePath</c>); it must be a
    /// sprite the base atlas holds, or the game draws its "NO PE"
    /// placeholder behind the icon. "snake_ring" was not one (2026-10-16).
    /// </summary>
    protected override string IconBaseName => "ring_of_the_snake";

    public override string PackedIconPath =>
        KleePck.Path("furina/relics/salon_solitaire.png")
        ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("furina/relics/salon_solitaire.png")
        ?? base.BigIconPath;
}
