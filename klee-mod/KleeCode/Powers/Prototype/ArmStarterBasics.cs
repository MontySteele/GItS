using HarmonyLib;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// `EB-351`. THE THIRD SEAM: which pair of basics is this character's, when a
/// base-game effect asks the CHARACTER instead of reading the deck.
///
/// WHAT WENT WRONG. A blind seat on `0.2.2301+proto` opened fight 1 of a Klee
/// overhaul run holding **Duck and Cover**, with **Kaboom!** in the same
/// twelve-card deck -- two SHIPPED Klee cards, in an arm whose whole premise is
/// that no shipped row means what it prints any more
/// (`review/qa/klee-round-8-2026-09-03/opus-act1.md`, the Identity block and
/// fight 1's opening hand). The arm's own two seams were both intact: the deck
/// `KleeOverhaulRoster.StartingDeck` states is exactly ten ids and none of them
/// is shipped, and `KleeCardPool.FilterThroughEpochs` returns the slice.
///
/// THE CAUSE, read off the 0.111.0 decompile rather than guessed. The seat took
/// **Large Capsule** at Neow -- "Obtain 2 random Relics. Add an additional
/// Strike and Defend to your Deck" -- and the base game resolves those two
/// words like this:
///
///   private static CardModel GetStrikeForCharacter(CharacterModel character)
///       => character.CardPool.AllCards.First(
///              c =&gt; c.Rarity == CardRarity.Basic
///                   &amp;&amp; c.Tags.Contains(CardTag.Strike));
///
/// `AllCards`, not `GetUnlockedCards`. `CardPoolModel.AllCards` is the pool's
/// whole declared membership and `FilterThroughEpochs` is never applied to it,
/// so the arm's pool replacement is not in that path at all -- and
/// `KleeCardPool.GenerateAllCards` still lists `Kaboom` (Basic, `CardTag.Strike`)
/// and `DuckAndCover` (Basic, `CardTag.Defend`) first, because it MUST: a card
/// missing from `AllCards` has no `CardModel.Pool` and throws "You monster!" the
/// moment it is drawn, which is the reason that list is deliberately untouched
/// by the arm. So the relic handed a Klee overhaul run exactly the two shipped
/// basics the arm had just replaced, and the deck went from ten cards to twelve.
///
/// NOT A REGRESSION FROM ANY MERGE. The knowledge was already in the tree --
/// `KleeSelfCheck`'s rule R11 quotes that very predicate, because an unguarded
/// `First()` over a pool with no Basic Strike is a THROW inside an Ancient
/// event's option handler (playtest 2026-07-23, Furina's first relic). What
/// nobody joined up was that Klee's pool satisfies R11 with the SHIPPED pair, so
/// under the arm the relic does not throw -- it succeeds, wrongly, in silence.
/// Round 7b's seats never saw it because their Neow pick was Hefty Tablet; the
/// defect needs Large Capsule in the run, which is an Ancient-rarity relic and
/// therefore a Neow or Ancient-event offer.
///
/// LARGE CAPSULE IS THE ONLY DOOR, and that is a sweep of the decompile rather
/// than a hope: `CardPoolModel.AllCards` has exactly two consumers in the whole
/// assembly -- `PreloadManager` (asset paths, grants nothing) and these two
/// methods. Everything else that reaches into a character's pool -- the
/// merchant, `CardFactory`, Discovery, Metamorphosis, Stoke, Jackpot, the
/// Crystal Sphere, Dusty Tome -- goes through `GetUnlockedCards`, which IS
/// `FilterThroughEpochs`, which the arm already owns.
///
/// WHY A PATCH AND NOT AN `AllCards` OVERRIDE. `AllCards` is virtual, so the
/// arm could have returned a list with the shipped basics removed or the base
/// pair prepended. Both are wrong for the same reason and it is not taste:
/// `CardModel.Pool` resolves an id by scanning `ModelDb.AllCardPools` for the
/// pool whose `AllCardIds` contains it. Removing the shipped basics takes their
/// `Pool` with them (the "You monster!" throw above); prepending
/// `StrikeIronclad` would put an id in TWO pools and let an Ironclad player's
/// own Strike resolve to Klee's pool -- her frame, her energy orb -- depending
/// on registration order. The narrow patch moves one relic's answer for one
/// character while an arm is on, and nothing else.
///
/// WHY IT IS A PREFIX. A postfix would have to let the original `First()` run,
/// and `First()` is the throw R11 exists to prevent. Refusing the original is
/// also the shape BaseLib already uses one relic over, on
/// `TouchOfOrobas.GetUpgradedStarterRelic` (quoted in
/// <c>Relics/UpgradedStarterRelics.cs</c>).
///
/// FLAG OFF, NOTHING MOVES. With both arms off <see cref="StrikeFor"/> and
/// <see cref="DefendFor"/> return null before they touch `ModelDb`, the prefix
/// returns true, and the base game answers exactly as it did -- Kaboom! and Duck
/// and Cover for Klee, her shipped basics, which is correct off the arm. A
/// release build compiles none of this: the file is under `Powers/Prototype/**`,
/// which `KleeCode.csproj` removes without `-p:PrototypeCards=true`.
///
/// FURINA IS ABSENT ON PURPOSE. The reframe arm does not replace her starter,
/// so her shipped `SoloistsSolicitation` / `StagePresence` are still the honest
/// answer and the base game already gives it.
/// </summary>
internal static class ArmStarterBasics
{
    /// <summary>
    /// The Basic Strike a base-game effect should be handed for this character,
    /// or <c>null</c> when no overhaul arm owns them and the base game's own
    /// answer stands.
    ///
    /// SCOPED ON THE IDENTITY INTERFACES, not on the concrete classes. That is
    /// what `tools/lint_prototype_patch_scope.py` accepts, and its reason is
    /// this file's problem exactly: ONE `PROTOTYPE_CARDS` switch compiles every
    /// arm, so a prototype patch with no character test runs on every seat at a
    /// co-op table (`EB-194`, `EB-221`). It is also the honest predicate --
    /// <c>IKleeCharacter</c> is the arm's own identity gate everywhere else in
    /// the mod.
    /// </summary>
    internal static CardModel? StrikeFor(CharacterModel character)
    {
        if (character is IKleeCharacter && KleeOverhaul.Enabled)
        {
            return KleeOverhaulRoster.StarterStrike();
        }

        if (character is IKokomiCharacter && KokomiOverhaul.Enabled)
        {
            return KokomiOverhaulRoster.StarterStrike();
        }

        return null;
    }

    /// <summary>The Defend twin of <see cref="StrikeFor"/>.</summary>
    internal static CardModel? DefendFor(CharacterModel character)
    {
        if (character is IKleeCharacter && KleeOverhaul.Enabled)
        {
            return KleeOverhaulRoster.StarterDefend();
        }

        if (character is IKokomiCharacter && KokomiOverhaul.Enabled)
        {
            return KokomiOverhaulRoster.StarterDefend();
        }

        return null;
    }
}

/// <summary>
/// Large Capsule's "an additional Strike", under an overhaul arm.
///
/// NOT ON <c>KleePatchBootstrap.SoftlockGuards</c>, and the distinction is the
/// list's own: that list is for patches whose absence LOSES THE RUN to a black
/// screen. This one's absence costs a prototype ROUND -- the arm quietly plays
/// two shipped cards and the round grades a deck nobody designed -- which is
/// worse to read and better to survive. The boot report still names it if the
/// lookup ever dies, which is the signal that matters here.
/// </summary>
[HarmonyPatch(typeof(LargeCapsule), "GetStrikeForCharacter")]
internal static class LargeCapsule_ArmStarterStrike_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(CharacterModel character, ref CardModel __result)
    {
        var replacement = ArmStarterBasics.StrikeFor(character);
        if (replacement == null)
        {
            return true;
        }

        __result = replacement;
        return false;
    }
}

/// <summary>Large Capsule's "and Defend", on exactly the terms above.</summary>
[HarmonyPatch(typeof(LargeCapsule), "GetDefendForCharacter")]
internal static class LargeCapsule_ArmStarterDefend_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(CharacterModel character, ref CardModel __result)
    {
        var replacement = ArmStarterBasics.DefendFor(character);
        if (replacement == null)
        {
            return true;
        }

        __result = replacement;
        return false;
    }
}
