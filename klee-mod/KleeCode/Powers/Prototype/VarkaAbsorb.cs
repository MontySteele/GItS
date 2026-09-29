using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards
{
    /// <summary>
    /// VARKA'S ABSORB KEYWORD, on the card: an Attack carrying this marker
    /// takes a fresh aura off the enemy it hits and gives its Wind
    /// (<see cref="Powers.VarkaAbsorb"/>). Emitted by the codegen from a row
    /// tagged <c>absorb</c>; no members, because the question it answers is
    /// only "does this card Absorb".
    /// </summary>
    public interface IAbsorbCard
    {
    }
}

namespace KleeMod.Powers
{
    /// <summary>What an Absorb does to the one hit it is asked about.</summary>
    public enum AbsorbOutcome
    {
        /// <summary>Not an Absorb: the aura's ordinary lifecycle runs.</summary>
        None = 0,
        /// <summary>The aura comes off the enemy and its Wind is gained. No
        /// spread, no flat 2, no reaction.</summary>
        Absorb,
        /// <summary>He already holds that Wind, so the hit Swirls the aura
        /// instead, whatever element the card carries (sec.10.1).</summary>
        SwirlInstead,
    }

    /// <summary>
    /// ABSORB (sec.10.1): "on a fresh aura, takes the aura off that enemy and
    /// gives you its Wind. No spread, no flat 2. If you already hold that
    /// Wind, the hit Swirls instead. With no fresh aura, only the card's
    /// damage." And Boreas's Fang reads the same rule: "Once each turn, the
    /// first non-Anemo Attack that hits a fresh aura Absorbs it."
    ///
    /// THE DECISION IS ONE PURE FUNCTION, <see cref="Decide(Element, bool,
    /// bool, bool, bool)"/>, and the aura's two sites ask it: the damage
    /// multiplier (so a hit that will be absorbed previews no amplifier) and
    /// the lifecycle (which carries it out). A hit landing needs a live combat,
    /// outside the headless boundary, so the pins read the decision value by
    /// value and the call graph to prove both sites take it.
    /// </summary>
    public static class VarkaAbsorb
    {
        /// <summary>
        /// THE RULE, on primitives. <paramref name="auraElement"/> is the
        /// aura the hit meets and <paramref name="spent"/> whether it has
        /// already paid a trigger; <paramref name="absorbCard"/> whether the
        /// card prints Absorb, <paramref name="fangReady"/> whether the Fang
        /// may take this hit (an unused Fang and a non-Anemo Attack), and
        /// <paramref name="holdsWind"/> whether the dealer already holds that
        /// element's Wind. PURE.
        /// </summary>
        public static AbsorbOutcome Decide(
            Element auraElement, bool spent, bool absorbCard, bool fangReady,
            bool holdsWind)
        {
            if (!VarkaPrototype.Enabled) return AbsorbOutcome.None;
            if (spent || !VarkaWinds.IsWindElement(auraElement))
            {
                return AbsorbOutcome.None;
            }
            if (!absorbCard && !fangReady) return AbsorbOutcome.None;
            return holdsWind ? AbsorbOutcome.SwirlInstead : AbsorbOutcome.Absorb;
        }

        /// <summary>The rule for one aura, one dealer and one card. PURE.
        /// </summary>
        public static AbsorbOutcome Decide(
            AuraPower aura, Creature? dealer, CardModel? cardSource)
        {
            if (!VarkaPrototype.Enabled || dealer?.Player == null
                || cardSource == null)
            {
                return AbsorbOutcome.None;
            }
            var absorbCard = cardSource is IAbsorbCard;
            var fang = !absorbCard && FangTakes(dealer, cardSource);
            return Decide(aura.Element, aura.Spent, absorbCard, fang,
                          VarkaWinds.Holds(dealer, aura.Element));
        }

        /// <summary>
        /// Would Boreas's Fang take this hit? The dealer holds the relic, it
        /// has not fired this turn, and the card is an Attack whose hit is
        /// not Anemo ("the first non-Anemo Attack"). An Attack on an enemy
        /// with no fresh aura never reaches this, so it does not use the Fang
        /// up. PURE.
        /// </summary>
        public static bool FangTakes(Creature? dealer, CardModel? card)
        {
            if (card is not { Type: CardType.Attack }) return false;
            if (IsFangAttackElement(AuraCmd.ElementOfPlay(card, dealer)))
            {
                var fang = dealer?.Player?.GetRelic<Relics.BoreasFang>();
                return fang is { UsedThisTurn: false };
            }
            return false;
        }

        /// <summary>The Fang's element test on its own: anything but Anemo,
        /// no element included (a base Strike). PURE.</summary>
        public static bool IsFangAttackElement(Element hit) =>
            hit != Element.Anemo;

        /// <summary>
        /// The Fang's once-a-turn latch. Marked when the Fang made the call
        /// on a hit, Absorb or Swirl alike: "the first non-Anemo Attack that
        /// hits a fresh aura" is used up by that hit either way.
        /// </summary>
        internal static void NoteFang(Creature? dealer, CardModel? cardSource)
        {
            if (cardSource is IAbsorbCard) return;
            var fang = dealer?.Player?.GetRelic<Relics.BoreasFang>();
            fang?.Use();
        }

        /// <summary>
        /// THE ABSORB ITSELF: the aura comes off the enemy, the dealer gains
        /// its Wind, and every Boreas Unbound he holds pays. Nothing reacts,
        /// nothing spreads and no flat 2 is dealt; the card's own damage has
        /// already landed.
        /// </summary>
        internal static async Task Take(
            PlayerChoiceContext choiceContext, AuraPower aura, Creature dealer,
            CardModel? cardSource)
        {
            NoteFang(dealer, cardSource);
            var element = aura.Element;
            var target = aura.Owner;
            await PowerCmd.Remove(aura);
            await VarkaWinds.Gain(choiceContext, dealer, element, cardSource);
            foreach (var unbound in dealer.Powers.OfType<BoreasUnboundPower>()
                         .ToList())
            {
                await unbound.OnAbsorb(choiceContext);
            }
            Log.Info($"[{KleeMod.ModId}] VARKA Absorb: {element} off "
                   + $"{target?.Name}.");
        }
    }
}
