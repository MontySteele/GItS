using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// TAMAKUSHI CASKET -- the Kokomi overhaul's starting relic.
///
/// THE RE-FOUNDING (2026-10-12) REWROTE IT, and kept its name and art
/// (<c>review/active/kokomi-design-pass-2026-10-11.md</c> pick 3, ruled; card
/// paper sec.1 rule 1): "At the start of your turn, if a Plan is waiting,
/// gain 3 Block." The count it kept since the Casket pass (2026-09-28) and the
/// Open the Casket token it dealt are gone with the Casket. About 9 Block in a
/// three-turn act-1 fight, against Burning Blood's 6 HP; with no 0-cost Plan
/// left, the Plan it asks for costs Energy, so the condition is a real price.
///
/// START OF TURN, NOT END (2026-10-12, [USER]: "For Kokomi - let's have her
/// starter relic apply block at the beginning of the turn rather than the
/// end."). THE HOOK IS <c>AfterBlockCleared</c>, the base game's
/// <c>BlockNextTurnPower</c>'s: <c>CombatManager.StartTurn</c> clears Block,
/// broadcasts <c>AfterBlockCleared</c> for each creature starting its turn,
/// and only then runs <c>SetupPlayerTurn</c> (energy, the draw,
/// <c>AfterPlayerTurnStart</c>), where <c>ProtoBakeKuragePower</c> carries
/// the waiting Plans out and clears the queue
/// (<c>tier0/tests/test_reaction_phase_parity.TURN_START_BROADCAST_ORDER</c>).
/// So the Block survives the clear, and the queue it reads
/// (<see cref="KokomiPlan.PlansHeld"/>) is still last turn's Plans. Block
/// stays raw, the base relic's <c>ValueProp.Unpowered</c>. Sim twin:
/// <c>kokomi_plan.casket_block</c>, right after the turn's Block clear.
///
/// THE WHOLE FILE IS QUARANTINED, for the reason it always was:
/// <c>tools/lint_unique_names.py</c> reads relic names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c>, so it sits here under
/// <c>#if PROTOTYPE_CARDS</c> rather than under <c>Powers/Prototype/</c>.
///
/// IT KEEPS THE COMPANION REWARD SLOT, which the Commander draws from.
///
/// NOT SEALED: <see cref="WatatsumiCasket"/>, the Touch of Orobas upgrade, IS
/// a Tamakushi Casket with more Block, so every
/// <c>GetRelic&lt;TamakushiCasket&gt;</c> (the game's is an <c>is T</c> test)
/// finds either relic.
/// </summary>
public class TamakushiCasket : CustomRelicModel
{
    public TamakushiCasket() : base(autoAdd: false)
    {
    }

    /// <summary>Touch of Orobas: the Watatsumi Casket (2026-09-30).</summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<WatatsumiCasket>().ToMutable();

    /// <summary>The Block at the start of her turn while a Plan is waiting.
    /// The Tamakushi Casket <see cref="KokomiOverhaulLaw.CasketBlock"/>;
    /// <see cref="WatatsumiCasket"/> more.</summary>
    public virtual int Block => KokomiOverhaulLaw.CasketBlock;

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Tamakushi Casket"),
        ("description", Face(KokomiOverhaulLaw.CasketBlock)),
    };

    /// <summary>The face, one sentence, the number the only difference
    /// between the Casket and its upgrade.</summary>
    internal static string Face(int block) =>
        "At the start of your turn, if a [gold]Plan[/gold] is waiting, gain "
      + "[blue]" + block + "[/blue] [gold]Block[/gold]. A "
      // Kokomi pre-run fixes (2026-10-12): two seats wrote Block Plans for
      // the hit coming this turn. `ProtoBakeKuragePower.AfterPlayerTurnStart`
      // carries Plans out after her turn-start Block clear.
      + "[gold]Plan[/gold]'s own [gold]Block[/gold] comes at the start of "
      + "your next turn.";

    /// <summary>
    /// Rule 1's jellyfish, made true by the relic too.
    /// <c>KokomiRules.InstallAll</c> already summons it from the same hook
    /// because rule 1 is a KIT rule; both calls are idempotent.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        if (!KokomiOverhaul.LiveFor(Owner?.Creature)) return;
        await BakeKuragePet.Summon(Owner);
    }

    /// <summary>"At the start of your turn, if a Plan is waiting, gain 3
    /// Block." Her own Block clear only, and only while the Bake-Kurage still
    /// holds last turn's Plans (they are carried out later this turn, in
    /// <c>AfterPlayerTurnStart</c>).</summary>
    public override async Task AfterBlockCleared(Creature creature)
    {
        var kokomi = Owner?.Creature;
        if (kokomi == null || creature != kokomi) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (!Pays(KokomiPlan.PlansHeld(kokomi))) return;
        Flash();
        await CreatureCmd.GainBlock(kokomi, Block, ValueProp.Unpowered, null);
    }

    /// <summary>Does a queue this deep pay? Any Plan waiting. PURE.</summary>
    public static bool Pays(int plansWaiting) => plansWaiting > 0;

    /// <summary>
    /// The relic's own name, for any line that names it. A second spelling of
    /// the title above on purpose: `tools/lint_unique_names.py` reads the
    /// literal inside the <c>("title", "...")</c> tuple.
    /// </summary>
    internal const string SourceName = "Tamakushi Casket";

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Kokomi);

    /// <summary>
    /// Her fourth companion reward option, kept from the Pearl of Wisdom
    /// unchanged -- see this class's header for why.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
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
    /// commissioned when a slice is ACCEPTED, not before.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}

/// <summary>
/// WATATSUMI CASKET -- the Tamakushi Casket upgraded, Touch of Orobas's
/// hand-over (main-session design, 2026-09-30, from [USER]'s co-op playtest:
/// "Varka and Kokomi need Ancient relics for Orobas"). Since the re-founding
/// (2026-10-12) it is the same sentence at 5 Block (the smallest change that
/// keeps it an upgrade of a 3-Block relic; it started combat with 3 in the
/// Casket before). It IS a Tamakushi Casket (see its header), so the hook and
/// the companion reward slot are the base's, and the only difference is
/// <see cref="Block"/>.
///
/// ANCIENT, NEVER STARTER (see <c>ExplosiveFrags</c>). ICON: the Tamakushi
/// Casket's own fallback chain, as Pearl of Insight reuses the Pearl's.
/// NOT IN THE SIM: tier05 has no Orobas row for the prototype arm.
/// </summary>
public sealed class WatatsumiCasket : TamakushiCasket
{
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Watatsumi Casket"),
        ("description", Face(WatatsumiBlock)),
    };

    /// <summary>The Block at the start of her turn while a Plan is waiting.
    /// </summary>
    public const int WatatsumiBlock = 5;

    public override int Block => WatatsumiBlock;

    /// <summary>Already the upgrade: nothing further for Orobas.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;
}
