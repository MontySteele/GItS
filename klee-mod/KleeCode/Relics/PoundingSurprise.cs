using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

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
{
    public PoundingSurprise()
        : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pounding Surprise"),
        ("description",
            "Whenever a [gold]Bomb[/gold] detonates, gain 1 [gold]Spark[/gold]."),
    };

    /// <summary>
    /// PLACEHOLDER ICON. Relic icons are `.tres` atlas entries resolved
    /// through ResourceLoader, so finding 18's `.pck` gate applies to
    /// relic_atlas exactly as it does to power_atlas — the fetched
    /// pounding_surprise.png cannot be wired until the pack lands. Borrowing
    /// Burning Blood's slug (a known-good atlas entry) instead of shipping the
    /// "Nope" placeholder; there is no in-run collision because this relic
    /// exists precisely to REPLACE Burning Blood in Klee's starting slot.
    /// </summary>
    protected override string IconBaseName => "burning_blood";

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target, int damage)
    {
        // Own bombs only: in co-op another player's detonations are theirs.
        if (applier?.Player != Owner) return;

        Flash();
        await SparkPower.Gain(choiceContext, Owner.Creature, 1, cardSource: null);
    }
}
