using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
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

namespace KleeMod.Relics;

/// <summary>
/// TAMAKUSHI CASKET -- the Kokomi overhaul's starting relic.
///
/// THE CASKET PASS (2026-09-28) REWROTE IT. It used to answer every debuff she
/// applied with a 2 Hydro hit (`CasketStrike`); that trigger is gone. It now
/// COUNTS: each Plan the Bake-Kurage carries out adds 1 to the Casket, and the
/// Open the Casket token it deals into her opening hand turns the count into
/// Strength. [USER], 2026-09-28, on why this and not a Vigor-style relic:
/// Vigor "devolves into 'solve for lethal, press the I Win button'"; the
/// design is "an artifact that grants / tracks an alternative energy that
/// builds by 1 for every Plan played, and adds one 0-cost Retain / Exhaust card
/// that converts that energy into Strength." Counting is "when it's carried
/// out"; "the casket keeps counting" after it is opened; and no card SPENDS
/// the count: "We don't need this to be the equivalent to Regent's stars or
/// Klee's sparks. This should feel like a distinct effect."
///
/// THE TOKEN PAYS MORE THAN ONCE (2026-10-01, the four-kit review, Kokomi
/// pick 1): Open the Casket costs 1 and has no Exhaust, so it cycles with the
/// deck. [USER]: "if it's repeatable, it should probably cost energy, though,
/// to make this a real choice and not just button mashing when it comes up?"
/// This relic still deals ONE copy, on turn one; nothing here assumed the
/// Exhaust.
///
/// THE COUNT LIVES ON THE ARM'S LEDGER, NOT ON THIS INSTANCE
/// (<see cref="KokomiOverhaulLedger.CasketCount"/>): per combat by
/// construction (a new combat's ledger starts at 0), readable by a card's
/// calculated var with no relic lookup, and one number for every reader --
/// the cards, the counter below and the blind page. This relic is where the
/// carry-out ADDS (<see cref="NoteCarriedOut"/>) and where the count is SHOWN.
///
/// THE COUNTER ON THE ICON, the base game's idiom (`Kunai`, `Pen Nib`):
/// <see cref="ShowCounter"/> in combat and <see cref="DisplayAmount"/> the
/// count, redrawn by <see cref="Refresh"/> whenever anything moves it. The
/// bridge carries a relic's counter as `counter` whenever the icon draws one
/// (`McpMod.StateBuilder`), so the blind page prints "Tamakushi Casket (N)"
/// with no new wire field.
///
/// THE WHOLE FILE IS QUARANTINED, for the reason it always was:
/// <c>tools/lint_unique_names.py</c> reads relic names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c>, so it sits here under
/// <c>#if PROTOTYPE_CARDS</c> rather than under <c>Powers/Prototype/</c>.
///
/// IT KEEPS THE COMPANION REWARD SLOT, which is not a Charge rule and which the
/// Commander loop draws its whole army from.
///
/// NOT SEALED: <see cref="WatatsumiCasket"/>, the Touch of Orobas upgrade, IS
/// a Tamakushi Casket with an opening count, so every
/// <c>GetRelic&lt;TamakushiCasket&gt;</c> (the game's is an <c>is T</c> test)
/// -- the carry-out add, the counter, the token -- finds either relic. The
/// cards never look for the relic at all: Shell Guard, Driftglass, Depths'
/// Judgment, What the Tokoyo Took, Open the Casket, Kurage Swarm and Grand
/// Design read the ledger's count.
/// </summary>
public class TamakushiCasket : CustomRelicModel
{
    public TamakushiCasket() : base(autoAdd: false)
    {
    }

    /// <summary>Touch of Orobas: the Watatsumi Casket (2026-09-30).</summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<WatatsumiCasket>().ToMutable();

    /// <summary>What the Casket holds when a combat starts. The Tamakushi
    /// Casket 0; <see cref="WatatsumiCasket"/> 3.</summary>
    public virtual int OpeningCount => 0;

    /// <summary>The combat this relic last seeded, so a second call in one
    /// combat seeds nothing.</summary>
    private object? _seededCombat;

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>
    /// The face, inside the 120-character relic ceiling -- which is why the
    /// ruled "Each Plan the Bake-Kurage carries out" prints as "Each Plan it
    /// carries out" (127 characters otherwise). The two keyword tips
    /// (<see cref="ArmKeywordTips.ForCasket"/>,
    /// <see cref="ArmKeywordTips.ForOpenTheCasket"/>) carry the rest.
    /// </summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Tamakushi Casket"),
        ("description",
            "Start each combat with the [gold]Bake-Kurage[/gold] and "
          + "[gold]Open the Casket[/gold] in hand. Each [gold]Plan[/gold] it "
          + "carries out adds " + KokomiOverhaulLaw.CasketPerPlan
          + " to the Casket."),
    };

    /// <summary>The token's card, on the relic's own hover -- the base game's
    /// shape for a relic that deals a card (`RadiantPearl`).</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<OpenTheCasket>();

    /// <summary>
    /// The count on the icon, in combat only (Kunai's rule): out of combat
    /// there is no count to show.
    /// </summary>
    public override bool ShowCounter =>
        Owner?.Creature?.CombatState != null
        && KokomiOverhaul.LiveFor(Owner.Creature);

    public override int DisplayAmount =>
        Owner?.Creature is { CombatState: not null } kokomi
            ? KokomiOverhaulLedger.For(kokomi).CasketCount
            : 0;

    /// <summary>
    /// The relic's first clause, made true by the relic itself.
    /// <c>KokomiRules.InstallAll</c> already summons the jellyfish from the
    /// same hook because rule 1 is a KIT rule; both calls are idempotent.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        if (!KokomiOverhaul.LiveFor(Owner?.Creature)) return;
        SeedOpeningCount(Owner!.Creature);
        await BakeKuragePet.Summon(Owner);
        Refresh(Owner!.Creature);
    }

    /// <summary>
    /// "... and Open the Casket in hand": dealt before the first hand draw,
    /// the site and the command `RadiantPearl` uses for its Luminesce, so the
    /// token is in hand beside the opening draw rather than instead of a card
    /// of it.
    /// </summary>
    public override async Task BeforeHandDraw(
        Player player, PlayerChoiceContext choiceContext,
        ICombatState combatState)
    {
        if (player != Owner) return;
        if (!KokomiOverhaul.LiveFor(Owner?.Creature)) return;
        if (Owner!.PlayerCombatState?.TurnNumber != 1) return;
        var token = Owner.Creature.CombatState!.CreateCard<OpenTheCasket>(Owner);
        await CardPileCmd.AddGeneratedCardsToCombat(
            new List<CardModel> { token }, PileType.Hand, Owner);
    }

    /// <summary>
    /// "Each Plan the Bake-Kurage carries out adds 1 to the Casket."
    /// Called by <c>KokomiPlan.ResolveEntry</c> -- the one place a Plan is
    /// carried out -- once per CARRY-OUT, so a Plan carried out twice (Second
    /// Wave, Nereid's Ascension) adds twice, and morning, Dusk and Change of
    /// Plans all count. A Kokomi not holding the relic adds nothing: it is the
    /// relic's sentence. Sim twin: <c>kokomi_plan.note_casket_carry_out</c>.
    /// </summary>
    public static void NoteCarriedOut(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Player?.GetRelic<TamakushiCasket>() == null) return;
        KokomiOverhaulLedger.For(kokomi).AddToCasket(
            KokomiOverhaulLaw.CasketPerPlan);
        Refresh(kokomi);
    }

    /// <summary>
    /// The opening count onto this combat's ledger: the Watatsumi Casket's
    /// "starts each combat with 3". Nothing for the Tamakushi Casket (0), and
    /// once per combat per relic.
    /// </summary>
    public static void SeedOpeningCount(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var relic = kokomi!.Player?.GetRelic<TamakushiCasket>();
        if (relic == null || relic.OpeningCount <= 0) return;
        var combat = (object?)kokomi.CombatState;
        if (combat != null && ReferenceEquals(relic._seededCombat, combat)) return;
        relic._seededCombat = combat;
        KokomiOverhaulLedger.For(kokomi).AddToCasket(relic.OpeningCount);
        Refresh(kokomi);
    }

    /// <summary>Redraw the counter after anything moved the count.</summary>
    public static void Refresh(Creature? kokomi)
    {
        var relic = kokomi?.Player?.GetRelic<TamakushiCasket>();
        relic?.InvokeDisplayAmountChanged();
    }

    /// <summary>
    /// The relic's own name, for any line that names it. A second spelling of
    /// the title above on purpose: `tools/lint_unique_names.py` reads the
    /// literal inside the <c>("title", "...")</c> tuple.
    /// `KurageBeatTests` pins the two together.
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
/// "Varka and Kokomi need Ancient relics for Orobas"). Identical to the
/// Tamakushi Casket in every way, except the Casket starts each combat with
/// 3. It IS a Tamakushi Casket (see its header), so the carry-out add, the
/// counter, the Open the Casket token and the companion reward slot are the
/// base's, and the only difference is <see cref="OpeningCount"/>.
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
        ("description",
            "Start each combat with the [gold]Bake-Kurage[/gold], "
          + "[gold]Open the Casket[/gold] in hand and [blue]"
          + WatatsumiOpeningCount + "[/blue] in the Casket. Each "
          + "[gold]Plan[/gold] it carries out adds "
          + KokomiOverhaulLaw.CasketPerPlan + "."),
    };

    /// <summary>The Casket's count at the start of every combat.</summary>
    public const int WatatsumiOpeningCount = 3;

    public override int OpeningCount => WatatsumiOpeningCount;

    /// <summary>Already the upgrade: nothing further for Orobas.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;
}
