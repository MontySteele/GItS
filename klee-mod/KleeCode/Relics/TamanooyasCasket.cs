#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
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
/// TAMANOOYA'S CASKET -- the Kokomi overhaul's starting relic, and RULE 4
/// (the ruled brief sec.4 rule 4, sec.8; slice one sec.3).
///
/// "The jellyfish is out from the start of combat; at the end of each turn she
/// did not Surge, it Mends her 2, up to 8 per combat."
///
/// THE WHOLE FILE IS QUARANTINED. It sits in <c>Relics/</c> rather than under
/// <c>Powers/Prototype/</c>, which the csproj Compile-Removes, for one reason:
/// <c>tools/lint_unique_names.py</c> reads relic display names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c> and nowhere else, and R69 put relic
/// names in the same namespace as card names. A prototype relic hidden from
/// that lint could mint a name a shipped card already owns. So the QUARANTINE
/// is the <c>#if PROTOTYPE_CARDS</c> wrapping the entire file -- a release
/// build compiles no part of it and there is no type for anything to grant --
/// and the name still reaches the lint, because the lint reads text.
///
/// THE RELIC CARRIES BOTH NUMBERS, and the brief says so twice ("The relic
/// carries both numbers", "Both numbers live on the relic"). They are read
/// through <see cref="PulseMend"/> and <see cref="PulseBudget"/>, which are the
/// only two places the pulse's size and ceiling are decided, so Song of Pearls
/// and The Clouds Like Waves move the pulse by being present rather than by
/// each carrying a copy of the rule.
///
/// IT REPLACES THE PEARL OF WISDOM, and that is not a preference: the Pearl IS
/// the exhaust funnel ("Whenever a card is Exhausted, gain Charge and Burst
/// Energy"), which is the first thing the brief's sec.4 retires. A run holding
/// both would print a rule the arm has turned off.
///
/// IT KEEPS THE COMPANION REWARD SLOT. That hook is not a Charge rule and not a
/// pulse rule, and the slice's Commander loop draws its whole army from that
/// very slot ("Companions come from the Inazuma Universals already in the
/// pool"); dropping it would delete one of the three loops the slice exists to
/// test. Same reasoning, one arm over, as <c>PoundingSurprise</c>'s.
/// </summary>
public sealed class TamanooyasCasket : CustomRelicModel
{
    public TamanooyasCasket() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Tamanooya's Casket"),
        ("description",
            "The [gold]Bake-Kurage[/gold] is on the field from the start of "
          + "every combat. At the end of each turn you did not "
          + "[gold]Surge[/gold], it [gold]Mends[/gold] you "
          + KokomiOverhaulLaw.PulseMend + ", up to "
          + KokomiOverhaulLaw.PulseBudget + " per combat. "
          + CompanionSlot.RewardSlotDescription),
    };

    /// <summary>
    /// THE PULSE'S SIZE, right now, for this Kokomi. ONE function, and it is
    /// public for the Furina legibility lesson: a preview and an effect that
    /// compute separately will eventually disagree, and the player believes the
    /// preview.
    ///
    /// TWO CARDS MOVE IT AND THE COMPOSITION IS <c>MAX</c>, which is a READING
    /// and is recorded as one. Song of Pearls prints "the pulse Mends 3" and
    /// The Clouds Like Waves prints "while you are under half HP, the pulse
    /// Mends 4"; both are flat statements about the same number, and with both
    /// out and her under half there is no printed order between them. The
    /// larger is taken because each card's face is then still true -- under 4
    /// the Clouds card would be a lie, and under 3 Song of Pearls would be one.
    /// Adding them was never on offer: neither card says "more".
    /// </summary>
    public static int PulseMend(Creature? kokomi)
    {
        if (kokomi == null) return KokomiOverhaulLaw.PulseMend;
        var mend = kokomi.Powers.OfType<SongOfPearlsPower>().Any()
            ? KokomiOverhaulLaw.SongOfPearlsMend
            : KokomiOverhaulLaw.PulseMend;
        var clouds = kokomi.Powers.OfType<CloudsLikeWavesPower>()
            .FirstOrDefault();
        if (clouds != null && CloudsLikeWavesPower.UnderHalf(kokomi))
        {
            mend = System.Math.Max(mend, clouds.Amount);
        }
        return mend;
    }

    /// <summary>
    /// THE PER-COMBAT CEILING, right now. Only Song of Pearls moves it, and it
    /// REPLACES rather than adds ("its budget IS 12").
    /// </summary>
    public static int PulseBudget(Creature? kokomi) =>
        kokomi != null && kokomi.Powers.OfType<SongOfPearlsPower>().Any()
            ? KokomiOverhaulLaw.SongOfPearlsBudget
            : KokomiOverhaulLaw.PulseBudget;

    /// <summary>What is left of this combat's budget. The slice's UI list asks
    /// for exactly this number, on this relic.</summary>
    public static int BudgetRemaining(Creature? kokomi) =>
        kokomi == null
            ? 0
            : System.Math.Max(
                0, PulseBudget(kokomi)
                   - KokomiOverhaulLedger.For(kokomi).PulseSpent);

    /// <summary>
    /// RULE 4. At the END of her turn, if she did not Surge, the jellyfish
    /// Mends her -- bounded three ways, and every one of them is printed
    /// somewhere: by the pulse's own size, by her entry HP (inside
    /// <see cref="KokomiTide.Mend"/>, which is the only place that cap lives)
    /// and by what is left of the per-combat budget.
    ///
    /// <c>BeforeSideTurnEnd</c> is the hook, matching <c>EndOfTurnSetOffPower</c>
    /// one arm over: it is the end-of-turn hook carrying a
    /// <c>PlayerChoiceContext</c>, which a Mend needs because Sango Isshin can
    /// turn one into a hit.
    ///
    /// THE BUDGET IS SPENT IN HP THAT LANDED, not in pulses fired, and the
    /// brief's own arithmetic is what settles it: script A's turn-1 pulse
    /// "would Mend 2, but she is at 80, so nothing", and after three effective
    /// pulses "the pulse paid 6 of its 8". A pulse at full HP therefore costs
    /// nothing, and -- a consequence, reported rather than hidden -- neither
    /// does the damage Sango Isshin makes out of the excess.
    /// </summary>
    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        var kokomi = Owner?.Creature;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;

        var ledger = KokomiOverhaulLedger.For(kokomi!);
        if (ledger.SurgedThisTurn) return;                  // she cashed instead

        var room = PulseBudget(kokomi) - ledger.PulseSpent;
        if (room <= 0) return;

        var amount = System.Math.Min(PulseMend(kokomi), room);
        var landed = await KokomiTide.Mend(choiceContext, kokomi, amount);
        if (landed > 0)
        {
            Flash();
            ledger.NotePulse(landed);
        }
    }

    /// <summary>
    /// Her fourth companion reward option, kept from the Pearl of Wisdom
    /// unchanged -- see this class's header for why it is not gated off with
    /// the rest of the shipped kit.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Kokomi)
        {
            return false;
        }
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
    /// commissioned when a slice is ACCEPTED, not before -- the same rule the
    /// Klee overhaul's power icons follow.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}
#endif
