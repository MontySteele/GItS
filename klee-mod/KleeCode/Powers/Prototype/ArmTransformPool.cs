using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// A TRANSFORM OF THE ARM'S BORROWED BASICS OFFERS THE ARM'S POOL (the Klee
/// full run on lane 1, 2026-09-26).
///
/// THE FIND. "Pandora's Box and Kill with Fire turned my cards into Ironclad
/// cards (Stoke, Rage, Pillage, Burning Pact and so on)." Under an overhaul arm
/// the starter's Strike and Defend are Ironclad's own
/// (<see cref="ArmStarterBasics"/>: <c>StrikeIronclad</c> and
/// <c>DefendIronclad</c>), and the base game picks a transform's replacement
/// from the ORIGINAL CARD's pool, not the character's:
///
///   GetDefaultTransformationOptions(original, isInCombat)
///       =&gt; pool = original.Pool  (Colorless for Quest/Event/Ancient/Token)
///          GetFilteredTransformationOptions(original,
///              pool.GetUnlockedCards(owner.UnlockState, ...), isInCombat)
///
/// (0.111.0 decompile, <c>CardFactory</c>). So a borrowed basic's pool is
/// Ironclad's and every transform of one hands her an Ironclad card. Pandora's
/// Box (<c>CreateRandomCardForTransform</c>) and Symbiote's Kill with Fire
/// (<c>CardCmd.TransformToRandom</c>) both reach this one method, and so does
/// the transform preview (<c>NTransformPreview</c>).
///
/// THE FIX IS THE SAME CALL WITH HER POOL. For a borrowed basic of a character
/// whose arm is on, the prefix answers the base game's own filter
/// (<c>GetFilteredTransformationOptions</c>, the private step it would have
/// run) over the CHARACTER's unlocked cards -- which under the arm is the
/// arm's pool, `FilterThroughEpochs` being the arm's seam. Every other card,
/// every other character and every run with the arms off takes the base
/// method untouched.
///
/// NOT A <see cref="ArmStarterBasics"/> SWEPT SITE, and that is why this is a
/// class of its own: that list is the unguarded `First()` lookups that THROW
/// or answer wrongly when asked for "the Strike"; this one asks which card a
/// Strike becomes. It reads the same seam to know what "borrowed basic" means.
/// </summary>
public static class ArmTransformPool
{
    /// <summary>The base game's private filter, resolved once. Null after a
    /// Steam move that renamed it, and then the prefix stands aside.</summary>
    public static readonly MethodInfo? FilterMethod =
        AccessTools.Method(typeof(CardFactory), "GetFilteredTransformationOptions");

    /// <summary>
    /// The transform options for <paramref name="original"/>, or null where
    /// the base game's own answer stands. <c>IsMutable</c> first: a canonical
    /// card's <c>Owner</c> asserts.
    /// </summary>
    public static IEnumerable<CardModel>? OptionsFor(
        CardModel original, bool isInCombat)
    {
        if (!original.IsMutable) return null;
        var owner = original.Owner;
        if (owner == null) return null;
        var character = owner.Character;
        if (!(character is IKleeCharacter || character is IKokomiCharacter))
        {
            return null;
        }
        if (!IsBorrowedBasic(original, character)) return null;
        if (FilterMethod == null) return null;

        var pool = character.CardPool.GetUnlockedCards(
            owner.UnlockState, original.RunState.CardMultiplayerConstraint);
        return FilterMethod.Invoke(
            null, new object[] { original, pool, isInCombat }) as CardModel[];
    }

    /// <summary>Is <paramref name="card"/> one of the basics an arm borrowed
    /// for this character -- the pair <see cref="ArmStarterBasics"/> names?
    /// False for every character no arm owns.</summary>
    public static bool IsBorrowedBasic(CardModel card, CharacterModel character)
    {
        var strike = ArmStarterBasics.StrikeFor(character);
        var defend = ArmStarterBasics.DefendFor(character);
        return (strike != null && card.Id == strike.Id)
            || (defend != null && card.Id == defend.Id);
    }
}

/// <summary>
/// The patch <see cref="ArmTransformPool"/> is about. A PREFIX, because the
/// base method's answer is a different pool rather than a filtered one; it
/// returns true (the base game runs) for everything the seam does not claim.
/// Harmony binds the arguments by NAME, and a pin reads the names off the
/// shipped method.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.GetDefaultTransformationOptions))]
internal static class CardFactory_ArmTransformPool_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(CardModel original, bool isInCombat,
                               ref IEnumerable<CardModel> __result)
    {
        var options = ArmTransformPool.OptionsFor(original, isInCombat);
        if (options == null)
        {
            return true;
        }

        __result = options;
        return false;
    }
}
