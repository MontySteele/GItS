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
/// WARD AND CASKET (2026-10-18, [USER]: "Modify the starting relic... 'gain
/// 2 block for each Plan or Companion Card played.'", then "if we allow for
/// Sting and Ward to count, is that a real problem? I'm wondering if we scale
/// that around allowing 0-cost cards to trigger it (possibly bringing it down
/// to 1 per card played)."), worded since 2026-10-20: "Whenever you Plan a
/// card or play a Companion, gain 1 Block." It replaces the start-of-turn Block for a waiting Plan (the
/// re-founding's, 2026-10-12; git keeps its reasoning).
///
/// KOKOMI BOSS RAMP (2026-10-21, [USER]: "Got it, let's try that"): 2 Block
/// a counted play (was 1), the Watatsumi Casket 3 (was 2). Balance suite 2
/// had her act 1 HP loss at 1.88x base once face-up Plan cards stopped
/// paying. What counts is unchanged.
///
/// WHAT COUNTS (2026-10-20, [USER] on paying for planning, not for any Plan
/// card: "2 was definitely the intent, and we should figure out a different
/// Block solution if needed"): a card PLANNED this play, written onto the
/// Bake-Kurage (<see cref="KokomiPlan.PlayedOnPet"/> and
/// <see cref="KokomiRefounding.CanBeWritten"/>), or a Companion
/// (<see cref="ICompanionCard"/>) played face-up or planned. A Plan card
/// played face-up pays nothing. Once a play however many of the two it is.
/// A Plan carried out later is the jellyfish's play, not hers
/// (<see cref="KokomiPlan.IsCarryingOut"/>). Treatise keeps its own test.
/// Block stays raw, the base relic's <c>ValueProp.Unpowered</c>. Sim twin:
/// <c>kokomi_plan.casket_block</c>, after each play.
///
/// IT SITS IN <c>Relics/</c>, not <c>Powers/Prototype/</c>:
/// <c>tools/lint_unique_names.py</c> reads relic names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c>.
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

    /// <summary>The Block each counted play pays:
    /// <see cref="KokomiOverhaulLaw.CasketBlock"/>; the
    /// <see cref="WatatsumiCasket"/>'s is larger.</summary>
    public virtual int Block => KokomiOverhaulLaw.CasketBlock;

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Tamakushi Casket"),
        ("description", Face(KokomiOverhaulLaw.CasketBlock)),
    };

    /// <summary>The face, one sentence, shared with the Watatsumi Casket.
    /// </summary>
    internal static string Face(int block) =>
        "Whenever you [gold]Plan[/gold] a card or play a Companion, gain "
      + "[blue]" + block + "[/blue] [gold]Block[/gold].";

    /// <summary>
    /// Rule 1's jellyfish, made true by the relic too.
    /// <c>KokomiRules.InstallAll</c> already summons it from the same hook
    /// because rule 1 is a KIT rule; both calls are idempotent.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        if (!KokomiOverhaul.IsHers(Owner?.Creature)) return;
        await BakeKuragePet.Summon(Owner);
    }

    /// <summary>Does this card pay, planned or not? A Companion always; a
    /// Plan card (Stings and Wards included) only when
    /// <paramref name="planned"/>. PURE.</summary>
    public static bool CountsCard(CardModel? card, bool planned) =>
        card is ICompanionCard
        || (planned && KokomiRefounding.CanBeWritten(card));

    /// <summary>Does this play pay? Hers, a card planned this play
    /// (<see cref="KokomiPlan.PlayedOnPet"/>) or a Companion, and not a
    /// carry-out. PURE on the play.</summary>
    public static bool Counts(CardPlay cardPlay, Creature? kokomi) =>
        kokomi != null
        && KokomiOverhaul.IsHers(kokomi)
        && cardPlay.Card.Owner?.Creature == kokomi
        && CountsCard(cardPlay.Card, KokomiPlan.PlayedOnPet(cardPlay))
        && !KokomiPlan.IsCarryingOut(kokomi.Player);

    /// <summary>"Whenever you Plan a card or play a Companion, gain 2
    /// Block." Once a play, however many of the two the card is.</summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var kokomi = Owner?.Creature;
        if (kokomi == null || cardPlay.Player != Owner) return;
        if (!Counts(cardPlay, kokomi)) return;
        var block = Block;
        if (block <= 0) return;
        Flash();
        // Seat page backlog (2026-10-19): "could not tell from the screen
        // whether it fired". The page prints it under "Since last page".
        ResolutionLedger.NoteRelic(RelicName, BlockNote(block));
        await CreatureCmd.GainBlock(kokomi, block, ValueProp.Unpowered, null,
                                    fast: true);
    }

    /// <summary>
    /// THE KOKOMI TASTE AUDIT (2026-10-21): a generated Sting Planned by a
    /// card or a Power ("Plan a Sting": Shoal Call, Kurage Bloom, Flotsam
    /// Surge's Plan) pays as a Sting she Planned herself does, once per
    /// Sting, through the relic she holds -- inside a carry-out too, where the
    /// carried-out card itself pays nothing. No relic, nothing. Sim twin:
    /// <c>kokomi_plan.casket_block_planned</c>.
    /// </summary>
    public static async Task PayForPlanned(Creature? kokomi, CardModel? card)
    {
        if (kokomi?.Player is not { } player) return;
        if (!KokomiOverhaul.IsHers(kokomi)) return;
        if (!CountsCard(card, planned: true)) return;
        var relic = player.Relics.OfType<TamakushiCasket>().FirstOrDefault();
        if (relic == null) return;
        var block = relic.Block;
        if (block <= 0) return;
        relic.Flash();
        ResolutionLedger.NoteRelic(relic.RelicName, BlockNote(block));
        await CreatureCmd.GainBlock(kokomi, block, ValueProp.Unpowered, null,
                                    fast: true);
    }

    /// <summary>The page's words for one payout: "gained 2 Block". PURE.
    /// </summary>
    public static string BlockNote(int block) => $"gained {block} Block";

    /// <summary>The printed title the page names it by.</summary>
    public virtual string RelicName => SourceName;

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
        var offer = CompanionSlot.Roll(player, creationOptions);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>
    /// FALLBACK ICON, borrowed from the relic whose slot this takes. Art is
    /// commissioned when a slice is ACCEPTED, not before.
    /// </summary>
    protected override string IconBaseName => "ring_of_the_snake";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}

/// <summary>
/// WATATSUMI CASKET -- the Tamakushi Casket upgraded, Touch of Orobas's
/// hand-over (main-session design, 2026-09-30, from [USER]'s co-op playtest:
/// "Varka and Kokomi need Ancient relics for Orobas"). Since Ward and Casket
/// (2026-10-18), worded since 2026-10-20: "Whenever you Plan a card or play
/// a Companion, gain 2 Block." (3 since the Kokomi boss ramp, 2026-10-21.)
/// It IS a Tamakushi Casket (see its header), so the
/// hook and the companion reward slot are the base's, and the only
/// difference is <see cref="Block"/>.
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

    /// <summary>The Block each counted play pays.</summary>
    public const int WatatsumiBlock = 3;

    public override int Block => WatatsumiBlock;

    /// <summary>The printed title the page names it by.</summary>
    public override string RelicName => "Watatsumi Casket";

    /// <summary>Already the upgrade: nothing further for Orobas.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;
}
