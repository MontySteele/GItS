using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;

namespace KleeMod.Powers;

/// <summary>
/// The verbs that belong to no rule -- Rally's discount, the cleanse, the
/// Casket's verbs. Kept out of <see cref="KokomiRules"/> because that file is
/// the RULES and these are cards. The one shared EVENT that used to live here
/// ("she applied a debuff to an enemy") left with its last reader, The Clouds
/// Like Waves Rippling (expansion batch one, 2026-09-29).
/// </summary>
public static class KokomiOverhaulKit
{
    /// <summary>
    /// Rally: "The next Companion card you play this turn costs 1 less."
    ///
    /// ONE STACK, ALWAYS. The grant is a switch, not a counter -- two Rallies
    /// in one turn do not make the next Companion cost two less, because the
    /// card says "costs 1 less" and not "costs 1 less per Rally" -- so this
    /// applies at 1 whether or not the power is already there, and
    /// <see cref="NextCompanionDiscountPower"/> removes itself on the play that
    /// spends it.
    /// </summary>
    public static async Task NextCompanionDiscount(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<NextCompanionDiscountPower>().Any()) return;
        await PowerCmd.Apply<NextCompanionDiscountPower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: cardSource);
    }

    /// <summary>
    /// Battle Plan's carry-out (`EB-655`, `EB-668`): "the next Attack you play
    /// face-up this turn deals 4 additional damage."
    ///
    /// ONE STACK, ALWAYS, on <see cref="NextCompanionDiscount"/>'s terms and
    /// for its reason: the face says "deals 4 additional damage" and not "per Plan",
    /// so a morning that carries out two Battle Plans buffs one Attack.
    /// <see cref="NextAttackDamagePower"/> removes itself on the face-up
    /// Attack that spends it, and at the end of the turn either way.
    /// </summary>
    public static async Task NextAttackDamage(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<NextAttackDamagePower>().Any()) return;
        await PowerCmd.Apply<NextAttackDamagePower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: cardSource);
    }

    /// <summary>
    /// PINCER's carry-out (R276): "This turn, your first Attack is played
    /// twice." ONE STACK, ALWAYS -- "your first Attack" is one Attack however
    /// many Pincers are carried out.
    /// </summary>
    public static async Task FirstAttackTwice(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<FirstAttackTwicePower>().Any()) return;
        await PowerCmd.Apply<FirstAttackTwicePower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: null);
    }

    /// <summary>
    /// STOLEN CHAPTER's carry-out (R276): "This turn, the first card you play
    /// costs 0." ONE STACK, ALWAYS, for the same reason.
    /// </summary>
    public static async Task FirstCardFree(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<FirstCardFreePower>().Any()) return;
        await PowerCmd.Apply<FirstCardFreePower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: null);
    }

    /// <summary>
    /// CHAIN OF COMMAND's carry-out (Kokomi core pass): "the first Companion
    /// card you play costs 0." ONE STACK, ALWAYS, Stolen Chapter's reason.
    /// </summary>
    public static async Task FirstCompanionFree(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<FirstCompanionFreePower>().Any()) return;
        await PowerCmd.Apply<FirstCompanionFreePower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: null);
    }

    /// <summary>
    /// TIDE WALL's read (R276): the total damage <paramref name="enemy"/>'s
    /// current intent would deal <paramref name="kokomi"/>, every hit counted
    /// -- the game's own <c>AttackIntent.GetTotalDamage</c>, which is the
    /// number the intent badge shows (its Strength and Weak, her Vulnerable).
    /// 0 for no enemy, a sleeping one or a non-attack intent. A state read
    /// must never throw, so a failing intent reads 0. Sim twin:
    /// <c>kokomi_plan.front_intent_damage</c>.
    /// </summary>
    public static int IntendedDamage(Creature? enemy, Creature? kokomi)
    {
        if (enemy == null || kokomi == null) return 0;
        if (!CurtainCallHooks.IntendsAttack(enemy)) return 0;
        try
        {
            var targets = new[] { kokomi };
            return enemy.Monster?.NextMove?.Intents
                .OfType<AttackIntent>()
                .Sum(intent => intent.GetTotalDamage(targets, enemy)) ?? 0;
        }
        catch (System.Exception)
        {
            return 0;
        }
    }

    /// <summary>
    /// Cleansing Wave: "Remove a debuff from yourself."
    ///
    /// A READING, recorded because the card says "a debuff" and not "the worst
    /// one": the FIRST debuff on her power list goes, which is the oldest one
    /// still standing, and the card gives the player no choice. A selection
    /// screen would be a different card, and picking "the largest" would be a
    /// rule nothing printed. The alternative is one line away if play says so.
    ///
    /// AN AURA IS NOT A DEBUFF and cannot be cleansed by this: the mod's
    /// <c>AuraPower</c> is <c>PowerType.Buff</c> (decompile-checked; the base
    /// game's own aura reads as a debuff only through its per-amount helper),
    /// and it lives on enemies anyway.
    /// </summary>
    public static async Task RemoveOneDebuff(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var debuff = kokomi!.Powers
            .FirstOrDefault(p => p.Type == PowerType.Debuff);
        if (debuff == null) return;
        await PowerCmd.Remove(debuff);
    }

    // ---- THE CASKET PASS (2026-09-28) ----------------------------------
    //
    // The Tamakushi Casket's count and the four verbs that touch it. The count
    // is <see cref="KokomiOverhaulLedger.CasketCount"/>; the relic adds 1 per
    // carry-out (<see cref="Relics.TamakushiCasket.NoteCarriedOut"/>). Every
    // verb below redraws the relic's counter. Sim twins: the `casket` block
    // in `tier0/engine/kokomi_plan.py`.

    /// <summary>
    /// "The Casket gains N" -- Pearl Diver's Plan and Moon Signal. Unlike the
    /// relic's own +1 it asks for no relic: the card says the Casket gains,
    /// and the count is the arm's.
    /// </summary>
    public static void GainCasket(Creature? kokomi, int amount)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || amount <= 0) return;
        KokomiOverhaulLedger.For(kokomi!).AddToCasket(amount);
        Relics.TamakushiCasket.Refresh(kokomi);
    }

    /// <summary>What the Tokoyo Took: "Double the Casket's count." A Task
    /// so the emitted <c>OnPlay</c> awaits it like every other verb.</summary>
    public static Task DoubleCasket(Creature? kokomi)
    {
        if (KokomiOverhaul.LiveFor(kokomi))
        {
            KokomiOverhaulLedger.For(kokomi!).DoubleCasket();
            Relics.TamakushiCasket.Refresh(kokomi);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Open the Casket: "Gain Strength equal to the Casket's count, then empty
    /// it." At <see cref="KokomiOverhaulLaw.CasketStrengthPerPoint"/> per
    /// point. An empty Casket grants nothing (and applies no zero-stack
    /// power). The relic keeps counting from 0.
    /// </summary>
    public static async Task OpenCasket(
        PlayerChoiceContext choiceContext, Creature? kokomi,
        CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var points = KokomiOverhaulLedger.For(kokomi!).EmptyCasket();
        Relics.TamakushiCasket.Refresh(kokomi);
        var strength = points * KokomiOverhaulLaw.CasketStrengthPerPoint;
        if (strength <= 0) return;
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, kokomi!, strength, applier: kokomi,
            cardSource: cardSource);
    }

    /// <summary>
    /// What the Tokoyo Returns: "Put Open the Casket from your Exhaust Pile
    /// into your Hand." The FIRST one there; none there, nothing happens.
    /// <c>CardPileCmd.Add</c> to the hand is the door Second Thoughts' return
    /// takes (<see cref="KokomiPlan.CancelLast"/>).
    /// </summary>
    public static async Task FetchOpenCasket(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;
        var exhaust = CardPile.Get(PileType.Exhaust, player);
        var token = exhaust?.Cards.OfType<Cards.Prototype.OpenTheCasket>()
            .FirstOrDefault();
        if (token == null) return;
        await CardPileCmd.Add(token, PileType.Hand, CardPilePosition.Top);
    }

    /// <summary>
    /// Undertow's "if the enemy has a debuff". The definition is the ENGINE'S
    /// OWN -- <c>PowerType.Debuff</c> -- rather than a list of names this file
    /// would have to keep current as the arm, the companions and the base game
    /// each add one.
    /// </summary>
    public static bool HasDebuff(Creature? creature) =>
        creature != null && creature.Powers.Any(p => p.Type == PowerType.Debuff);

    /// <summary>
    /// Well Laid's "for each debuff on the enemy" (R276 pick 1): DISTINCT
    /// debuffs, not stacks -- Weak 2 is one -- by <see cref="HasDebuff"/>'s own
    /// definition. Null-safe because the calculated var's preview hands it a
    /// null target whenever nothing is hovered. Sim twin:
    /// <c>kokomi_plan.debuff_count</c>.
    /// </summary>
    public static int DebuffCount(Creature? creature) =>
        creature == null
            ? 0
            : creature.Powers.Count(p => p.Type == PowerType.Debuff);

    // The re-entrancy latch the Casket's debuff strike needed (a Hydro
    // strike into a Cryo aura Freezes, and Frozen is a debuff she applied)
    // left with the strike in the Casket pass (2026-09-28).
}
