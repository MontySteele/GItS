using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;

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
    /// companion offered on every FIGHT reward screen, riding
    /// SpecialCardReward (the native take-or-skip single-card reward).
    /// Hosted here because the starter relic is the one model guaranteed
    /// present for the whole of every Klee run and relics are the hook's
    /// intended listeners (AbstractModel doc: Orrery, Tiny Mailbox).
    /// room is CombatRoom = end-of-encounter rewards only; null room
    /// (relic pickups, events) and non-combat rooms get no slot.
    /// </summary>
    public override bool TryModifyRewards(
        Player player, List<Reward> rewards, AbstractRoom? room)
    {
        if (room is not CombatRoom) return false;
        if (player.Character is not Klee) return false;

        var offer = CompanionSlot.Roll(player);
        if (offer == null) return false;
        rewards.Add(new SpecialCardReward(offer, player));
        return true;
    }

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target, int damage)
    {
        // Own bombs only: in co-op another player's detonations are theirs.
        if (applier?.Player != Owner) return;

        Flash();
        await SparkPower.Gain(choiceContext, Owner.Creature, 1, cardSource: null);
    }
}
