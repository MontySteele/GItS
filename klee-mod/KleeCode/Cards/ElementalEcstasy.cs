using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: uncommon skill, cost 2, refresh all elemental auras, draw 1 card
/// per aura. Hand-written (R23). Port of tier0 _op_refresh_all_auras +
/// _op_draw's per_aura formula: count first, refresh each, draw the count.
///
/// Skills carry no element (sheet header), so playing this never applies or
/// consumes anything -- it only resets durations, which is why it reads the
/// aura powers directly instead of going through a damage pipeline.
/// </summary>
public sealed class ElementalEcstasy : CustomCardModel
{
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("elemental_ecstasy");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Elemental Ecstasy"),
        ("description",
            "Refresh all elemental auras. Draw 1 card for each aura."),
    };

    // autoAdd: false -- KleeCardPool declares pool membership itself (see Kaboom).
    public ElementalEcstasy()
        : base(2, CardType.Skill, CardRarity.Uncommon, TargetType.Self, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // HittableEnemies is the verified live-enemy accessor the generated
        // random-target cards use; the sim iterates living_enemies.
        var refreshed = 0;
        foreach (var enemy in CombatState!.HittableEnemies.ToList())
        {
            var aura = AuraCmd.Find(enemy);
            if (aura == null) continue;
            refreshed++;
            await AuraCmd.Refresh(choiceContext, aura, Owner.Creature, this);
        }

        if (refreshed > 0)
        {
            await CardPileCmd.Draw(choiceContext, refreshed, Owner);
        }
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: cost -1 (2 -> 1, uncommon cost slot).
        EnergyCost.UpgradeBy(-1);
    }
}
