using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Combat.History.Entries;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Kokomi's CharacterModel, her identity gate: in co-op the other
/// seat is not hers, and every rule of her kit asks this first.
/// </summary>
public interface IKokomiCharacter
{
}

/// <summary>
/// Kokomi's identity and card predicates. Her shipped meters (the Charge bank,
/// her Burst meter and the Ceremonial Garment grant) went with the shipped
/// kits (legacy cleanup stage 5).
/// </summary>
public static class KokomiResources
{
    public static bool IsKokomi(Creature? creature) =>
        creature?.Player?.Character is IKokomiCharacter;

    /// <summary>
    /// ROTATION LAW ([USER] ruling 2026-08-23; LAW "Character identity —
    /// Kokomi"). "Whenever one of YOUR cards is Exhausted" reads literally: a
    /// Status or a Curse is never one of her cards. This one predicate is the
    /// law's whole surface in the mod -- the Muster candidate filter, every
    /// generated chosen-Exhaust selector, and the Charge/Burst funnel all ask
    /// it -- so the three cannot drift apart. Sim twin: Card.is_junk
    /// (tier0/engine/state.py), used at the same three seams.
    ///
    /// The retired behaviour was kickoff v1 §2.1's "statuses/curses count
    /// too (accepted quirk)": a Dazed in hand was free curse removal that
    /// also paid Charge when the recruit rotated out, which made her uniquely
    /// status-resistant for nothing. A card that IS allowed to eat junk says
    /// so on its face with an explicit filter (Dodge Roll's shape) -- that is
    /// the design space this vacates, at Uncommon/Rare.
    /// </summary>
    public static bool IsJunk(CardModel card) =>
        card.Rarity == CardRarity.Status || card.Rarity == CardRarity.Curse;

    /// <summary>
    /// The selector predicate for every Kokomi verb that picks one of HER
    /// cards: not junk.
    /// </summary>
    public static bool OwnCard(CardModel card) => !IsJunk(card);

    /// <summary>
    /// Cards this SEAT has discarded this turn -- the scaling term behind
    /// `what_the_tokoyo_took` (EB-122, from EB-69's fill).
    ///
    /// TRANSCRIBED, not re-derived. The expression is the base game's own
    /// MementoMori multiplier verbatim (sts2.dll v0.107.1,
    /// MegaCrit.Sts2.Core.Models.Cards.MementoMori.CanonicalVars), and the sim
    /// names that same card as the source of its `discards_this_turn` token
    /// (tier0/engine/effects.py `_formula_count`). Two consequences fall out
    /// of reading the HISTORY rather than a counter, and both are the sim's
    /// too rather than choices made here: the end-of-turn hand flush does not
    /// go through CardCmd.Discard and so does not count, and the owner filter
    /// makes the tally PER SEAT -- a co-op partner's discards are not this
    /// card's bonus.
    ///
    /// Static and null-tolerant because CalculatedVar previews call it with no
    /// target, and outside a combat there is no history to read.
    /// </summary>
    public static int DiscardsThisTurn(CardModel? card)
    {
        if (card == null) return 0;
        var combatState = card.CombatState;
        if (combatState == null) return 0;
        var history = CombatManager.Instance?.History;
        if (history == null) return 0;

        // A loop rather than MementoMori's `.Count(lambda)`: the predicate is
        // the whole meaning of this method, and in a closure it is invisible
        // to the structural pin that guards it (KleeTests reads a method's own
        // call set and cannot follow a compiler-generated display class). The
        // two clauses are byte-for-byte the base game's; only the spelling of
        // the iteration differs, and this one also allocates nothing on a
        // preview, which runs on every hover.
        var count = 0;
        foreach (var entry in history.Entries)
        {
            if (entry is not CardDiscardedEntry discarded) continue;
            if (!discarded.HappenedThisTurn(combatState)) continue;
            if (discarded.Card.Owner != card.Owner) continue;
            count++;
        }

        return count;
    }
}

/// <summary>
/// Her combat-scoped engine hooks: the Kokomi overhaul's stash, the
/// Bake-Kurage install before the first turn, and its turn-start belt.
/// </summary>
public sealed class KokomiResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static KokomiResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KokomiResourceHooks>(
            ModelDb.GetId<KokomiResourceHooks>());
        // STASH ONLY: this delegate runs on every hook broadcast
        // (`EB-196`: CombatState.IterateHookListeners -> ModHelper's
        // subscriber walk -> this delegate), so it holds no per-fight work.
        // That is BeforeCombatStart's, below.
        KokomiRules.NoteCombat(combatState);
        yield return _instance;
    }

    /// <summary>
    /// Rule 1's jellyfish is not summoned by a card, so somebody has to put it
    /// on the field before the first turn opens. The install also CAPTURES HER
    /// ENTRY HP, the ceiling on every Mend in the fight. The game raises this
    /// hook ONCE per combat, after every creature is in.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        await KokomiRules.InstallAll();
    }

    /// <summary>
    /// The BELT to BeforeCombatStart's braces: idempotent, and here so that a
    /// combat whose setup order ever changes still opens with a jellyfish. The
    /// Plans resolve on the marker power's own override
    /// (<c>ProtoBakeKuragePower.AfterPlayerTurnStart</c>).
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (KokomiOverhaul.LiveFor(player.Creature))
        {
            await KokomiRules.Install(player.Creature);
        }
    }
}
