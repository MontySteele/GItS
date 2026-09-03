using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// `EB-351`, extended by `EB-352`. THE THIRD SEAM: which pair of basics is this
/// character's, when a base-game effect asks the CHARACTER instead of reading
/// the deck. `EB-351` built it for Large Capsule, which asks and gets the wrong
/// answer; `EB-352` added Fasten, which asks and gets a throw.
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
/// LARGE CAPSULE IS THE ONLY `AllCards` DOOR, and that is a sweep of the
/// decompile rather than a hope: `CardPoolModel.AllCards` has exactly two
/// consumers in the whole assembly -- `PreloadManager` (asset paths, grants
/// nothing) and these two methods. Everything else that reaches into a
/// character's pool -- the merchant, `CardFactory`, Discovery, Metamorphosis,
/// Stoke, Jackpot, the Crystal Sphere, Dusty Tome -- goes through
/// `GetUnlockedCards`, which IS `FilterThroughEpochs`, which the arm already
/// owns.
///
/// `EB-352`: THE SECOND DOOR, AND OWNING `GetUnlockedCards` WAS NOT ENOUGH.
/// `EB-351` closed on that last sentence, and it is true of every consumer that
/// OFFERS from the pool -- they all take what the arm hands them. It is not
/// true of the one consumer that does not offer but ASKS THE POOL A QUESTION:
///
///   protected override IEnumerable&lt;IHoverTip&gt; ExtraHoverTips  // Fasten
///       =&gt; ... Owner.Character.CardPool
///              .GetUnlockedCards(Owner.UnlockState, ...)
///              .First(c =&gt; c.Tags.Contains(CardTag.Defend)) ...
///
/// Fasten is an Uncommon Power in `ColorlessCardPool` -- Defend-tagged cards
/// gain extra Block (`FastenPower.ModifyBlockAdditive`) -- and it renders its
/// second hover tip as a picture of the reader's OWN Defend, which is what that
/// lookup is for. It reaches a modded seat the way any Colorless card does: the
/// merchant's colorless slots, Toolbox, Orange Dough, a Colorless Potion.
///
/// Owning `FilterThroughEpochs` is exactly what breaks it: the arm's pool is
/// the prototype rows and nothing else, not one of which carries
/// `CardTag.Defend` (the base Defends live in the STARTER, and putting one in
/// the offer pool would make it drawable as a reward, which is not the fix). So
/// the `First()` finds nothing and throws -- and unlike Large Capsule's silent
/// wrong answer this one is a hard `InvalidOperationException` the moment the
/// card is SHOWN: a shop shelf, a reward screen, a hand. `KleeSelfCheck`'s R11
/// cannot see it either, for the mirror of R11's `AllCards` blind spot -- R11
/// reads the SHIPPED pool, where Duck and Cover satisfies the predicate.
///
/// THE SWEEP THAT SAYS THESE THREE ARE ALL OF THEM. Over the whole 0.111.0
/// assembly, every unguarded `First`/`Single`/`Last` taking a `CardModel`
/// predicate is one of exactly three call sites: `Fasten.ExtraHoverTips`,
/// `LargeCapsule.GetStrikeForCharacter`, `LargeCapsule.GetDefendForCharacter`.
/// Everything else keyed on `CardTag.Strike` / `CardTag.Defend` either reads
/// the DECK rather than the pool (`Tezcatara`, `Amalgamator`, `NeowsTalisman`,
/// `LeafyPoultice`, `NutritiousSoup`, `SoldiersStew`, `PerfectedStrike`) or
/// asks a single card about itself (`StrikeDummy`, `FakeStrikeDummy`,
/// `GhostSeed`, `Spiral`, `Goopy`, `HellraiserPower`, `FastenPower`), and both
/// of those are safe by construction: an arm run's deck DOES hold four base
/// Defends, and a per-card test cannot be empty. The list is a pin --
/// `ArmStarterBasicsTests.The_swept_pool_lookups_are_the_three_this_seam_covers`
/// -- so a fourth site after a Steam move is an addition somebody has to write.
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
/// FLAG OFF, NOTHING MOVES. With both arms off <see cref="StrikeFor"/>,
/// <see cref="DefendFor"/> and <see cref="DefendTipsFor"/> return null before
/// they touch `ModelDb`, every prefix returns true, and the base game answers
/// exactly as it did -- Kaboom! and Duck and Cover for Klee, her shipped
/// basics, and Fasten's tip a picture of Duck and Cover, which is correct off
/// the arm. A release build compiles none of this: the file is under
/// `Powers/Prototype/**`, which `KleeCode.csproj` removes without
/// `-p:PrototypeCards=true`.
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

    /// <summary>
    /// `EB-352`. Fasten's two hover tips, under an overhaul arm, or
    /// <c>null</c> when no arm owns this character and the base game's own
    /// getter stands.
    ///
    /// THE SAME ANSWER AS <see cref="DefendFor"/>, NOT A SECOND ONE. This
    /// exists only to spell the tip PAIR, because the site being replaced is a
    /// whole property getter rather than a one-card helper -- the Defend it
    /// names still comes from the one seam, so the relic and the tip cannot
    /// disagree about which Defend is hers.
    ///
    /// WHY THE PAIR IS REBUILT RATHER THAN REPAIRED. The throwing `First()` is
    /// INLINE in `Fasten.ExtraHoverTips`; there is no inner method to answer,
    /// so a prefix has to produce the whole list. It is a two-element list and
    /// both elements are the base game's own factory calls in the base game's
    /// own order -- <c>Static(Block)</c> then <c>FromCard(theDefend)</c> -- and
    /// a pin reads the shipped getter's IL to say those two are still what it
    /// builds (`ArmStarterBasicsTests`). If MegaCrit adds a third tip, that pin
    /// bites rather than the arm quietly dropping it.
    ///
    /// TAKES THE CHARACTER, NOT THE CARD, so the flag-off pin can ask it the
    /// same way it asks the other two -- with a character and no live run. The
    /// card-shaped part (is it mutable, has it an owner) belongs to the patch,
    /// because that is the base game's own guard and it is where the base
    /// game's own fallback lives.
    /// </summary>
    internal static IEnumerable<IHoverTip>? DefendTipsFor(CharacterModel character)
    {
        var defend = DefendFor(character);
        if (defend == null)
        {
            return null;
        }

        return new IHoverTip[]
        {
            HoverTipFactory.Static(StaticHoverTip.Block),
            HoverTipFactory.FromCard(defend),
        };
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

/// <summary>
/// `EB-352`. Fasten's "a picture of your Defend" hover tip, under an overhaul
/// arm, where asking the arm's pool for a `CardTag.Defend` card throws.
///
/// THIS ONE *IS* A SOFTLOCK-CLASS FAILURE, and that is the difference from the
/// two patches above. Large Capsule's absence costs a prototype round -- the
/// arm quietly plays two shipped cards. This one's absence throws
/// `InvalidOperationException` out of a property getter that the card RENDERER
/// calls, so the screen holding the card never finishes drawing: a shop shelf
/// with Fasten on it, the reward screen that rolled it, or the hand it was
/// drawn into. It is still not on `KleePatchBootstrap.SoftlockGuards`, because
/// that list is read by an operator deciding whether to playtest a build at
/// all, and this failure needs a Colorless card the run may never see -- but
/// the boot report names the class either way, which is the signal that
/// matters.
///
/// THE GUARD IS THE BASE GAME'S OWN, in the base game's order.
/// `CardModel.Owner` calls `AssertMutable()` and THROWS on a canonical model,
/// so `IsMutable` is tested FIRST and the `||` short-circuit that stops `Owner`
/// being read is load-bearing, not style. When either test fails we return true
/// and the base getter takes its own `cardModel == null` arm, which hands back
/// `ModelDb.Card&lt;DefendIronclad&gt;()` -- the right answer for a card with no
/// reader (the card library, a canonical model), and unchanged from the shipped
/// game.
/// </summary>
[HarmonyPatch(typeof(Fasten), "ExtraHoverTips", MethodType.Getter)]
internal static class Fasten_ArmDefendTip_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(Fasten __instance, ref IEnumerable<IHoverTip> __result)
    {
        if (!__instance.IsMutable || __instance.Owner == null)
        {
            return true;
        }

        var replacement = ArmStarterBasics.DefendTipsFor(__instance.Owner.Character);
        if (replacement == null)
        {
            return true;
        }

        __result = replacement;
        return false;
    }
}
