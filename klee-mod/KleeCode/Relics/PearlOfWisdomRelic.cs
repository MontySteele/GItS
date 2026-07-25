using System.Collections.Generic;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Relics;

/// <summary>
/// Kokomi's starter talent: every card rotated off the line becomes Charge.
///
/// NAMING, on the record (R55). [USER] picked "Pearl of Wisdom" over the
/// drafted "Everlasting Moonglow". "Tamakushi Casket" moved to the
/// Garment/Bake-Kurage link where canon actually puts it -- it is her first
/// ascension passive, not her talent -- while the sim's internal hook id
/// stays `tamakushi_casket` so the rename is display-only and no measurement
/// is invalidated by it.
///
/// THE RELIC HAS NO HOOK OF ITS OWN. The accrual lives in
/// <see cref="Powers.KokomiResourceHooks.AfterCardExhausted"/>, gated on
/// character identity rather than on holding this relic. That is the sim's
/// shape (the funnel is universal for her and never written as card text),
/// and it matters for the playtest: a player who somehow loses the relic must
/// not lose the character. The relic is the FICTION of the rule and the place
/// the tooltip lives; it is not the mechanism.
/// </summary>
public sealed class PearlOfWisdomRelic : CustomRelicModel
{
    public PearlOfWisdomRelic() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pearl of Wisdom"),
        ("description",
            "Whenever a card is [gold]Exhausted[/gold], gain "
          + $"{Powers.KokomiConstants.ChargePerExhaust} [gold]Charge[/gold] "
          + $"and {Powers.KokomiConstants.BurstPerExhaust} Burst Energy."),
    };

    /// <summary>
    /// FALLBACK ICON while her art pass is outstanding -- the Pounding
    /// Surprise / Ethereal Spotlight arrangement. Kokomi borrows the Silent
    /// relic pool, so a slug that belongs to a real Silent relic CAN co-occur
    /// with it in one run; that is exactly why the packed path below matters.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}
