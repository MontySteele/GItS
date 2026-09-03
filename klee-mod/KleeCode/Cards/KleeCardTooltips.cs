using System.Collections.Generic;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Shared card affordances for Bomb rules and board-aware reaction previews.
/// ExtraHoverTips is evaluated when the card is inspected, so the reaction
/// list follows the enemies' current auras without patching card UI nodes.
/// For random/all-enemy cards it intentionally lists every distinct reaction
/// currently available; choosing a particular target remains the player's
/// decision.
/// </summary>
public static class KleeCardTooltips
{
    /// <summary>The hover-tip title table, same one the rider tips use.</summary>
    private const string Table = "card_keywords";

    /// <summary>Loc key for the Burst Energy keyword's title row. The BODY is
    /// built live below, the Muster/Charge bargain: it quotes constants and
    /// reads the owner's meter, so a repricing cannot leave a row lying.
    /// </summary>
    public const string BurstKey = "KLEEMOD-BURST";

    /// <summary>
    /// The [gold]Burst Energy[/gold] KEYWORD, roster-wide.
    ///
    /// THE GAP. Burst is the oldest meter in the mod and no face ever said
    /// what it is: thirty-eight faces across three characters and the
    /// companion pool print the word, and the only surface that ever
    /// explained it was <see cref="BurstMeterPower"/>, a status badge retired
    /// in 2026-07-23 playtest feedback. The blind seat on run B6 reported it
    /// from the player's side -- Burst "accumulated alongside that plan,
    /// although I never saw how to spend it". This is the Charge keyword's
    /// twin, one meter over.
    ///
    /// IT LIVES HERE, NOT IN KokomiRiderTips, BECAUSE THE METER IS
    /// ROSTER-WIDE. Klee, Furina and Kokomi each own a Burst resource, and
    /// the companion cards that print the word are held by whoever mustered
    /// or drafted them. This is the shared attach point; the tip states the
    /// SHARED rules and reads the owner's own numbers for the rest.
    ///
    /// WHAT IS SHARED AND WHAT IS NOT. Shared, verbatim from the code: the
    /// skill-tag grant (BurstConstants.PerSkillTag, mirrored by
    /// FurinaResourceConstants.BurstPerSkillTag and read for Kokomi at
    /// KokomiExhaustHooks), the reaction grant (ReactionEffects.Resolve pays
    /// every character the same 5), the grant-at-full rule (Klee/Furina/
    /// KokomiKitGrant carry the same four rules) and the drain-the-whole-meter
    /// cast (each DrainOnPlay sets Amount = 0). NOT shared: the meter's SIZE
    /// (40 / 70 / 20) and each character's extra income -- Kokomi's exhaust
    /// accrual, Furina's Salon ticks and Encore spend, Klee's detonation
    /// splash. So the size is read live from the owner rather than printed as
    /// a numeral, and the extra income is left to the faces and powers that
    /// grant it, which print their own lines.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBurst(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, BurstKey + ".title"), BurstBody(card));
    }

    /// <summary>
    /// The shared rules, plus the owner's own meter when there is one to read.
    /// Out of combat (deck view, reward screen) the rules stand alone rather
    /// than printing a misleading 0 -- the FurinaRiderTips rule.
    /// </summary>
    private static string BurstBody(CardModel card)
    {
        var meter = MeterOf(TipOwner.CreatureOf(card));
        // The rates are quoted from the OWNER's constants where an owner can
        // be read, and from the shared pair otherwise. All three characters
        // sit at 5/5 today and each per-character constant is documented as
        // mirroring the same tier0 value -- but "documented as mirroring" is
        // not "cannot diverge", and this tip must not be the place a
        // divergence first tells a player something false.
        var perSkillTag = meter?.PerSkillTag ?? BurstConstants.PerSkillTag;
        var perReaction = meter?.PerReaction ?? BurstConstants.PerReaction;
        var rule =
            $"[gold]Burst Energy[/gold]: your character's meter, empty at the "
          + $"start of each combat. Playing a card with [gold]Elemental "
          + $"Skill[/gold] grants {perSkillTag} and every Elemental Reaction "
          + $"grants {perReaction}; some cards, powers and relics grant more. "
          + "The moment the meter is FULL your character's Burst card is put "
          + "into your hand, and casting it spends the WHOLE meter -- energy "
          + "past full is lost at the cast, not at the gain.";
        if (meter == null || card.CombatState == null) return rule;
        return $"{rule} You hold {meter.Amount} of {meter.Max} "
             + "[gold]Burst Energy[/gold].";
    }

    /// <summary>One character's Burst meter, or null for an owner that has
    /// none (no owner at all, or a card being inspected outside a run). The
    /// three branches are the same three the overhead gauge dispatches on
    /// (Vfx.GaugeBridge.Specs) and read through the same accessors, so the
    /// tip and the gauge cannot disagree about the number.</summary>
    private sealed record BurstMeter(
        int Amount, int Max, int PerSkillTag, int PerReaction);

    private static BurstMeter? MeterOf(Creature? owner)
    {
        if (owner == null) return null;
        if (KokomiResources.IsKokomi(owner))
        {
            return new BurstMeter(
                KokomiResources.GetBurst(owner), KokomiConstants.BurstMax,
                BurstConstants.PerSkillTag, KokomiConstants.BurstPerReaction);
        }

        if (FurinaResources.IsFurina(owner))
        {
            return new BurstMeter(
                FurinaResources.Burst(owner),
                FurinaResourceConstants.BurstMax,
                FurinaResourceConstants.BurstPerSkillTag,
                FurinaResourceConstants.BurstPerReaction);
        }

        if (owner.Player?.Character is Klee)
        {
            return new BurstMeter(
                KleeBurstResource.AmountFor(owner), BurstConstants.KleeMax,
                BurstConstants.PerSkillTag, BurstConstants.PerReaction);
        }

        return null;
    }

    /// <summary>
    /// <paramref name="appliesWithoutHit"/> is `EB-338`. See
    /// <see cref="NoHitBody"/> for what it changes and
    /// <c>gen_klee_cards.emit</c> for how it is derived (never remembered).
    /// </summary>
    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        Element trigger = Element.None,
        bool includesBombRules = false,
        bool includesConfiscatedRules = false,
        bool appliesWithoutHit = false)
    {
        foreach (var tip in inherited) yield return tip;

        if (includesBombRules)
        {
            yield return HoverTipFactory.FromKeyword(KleeKeywords.Bomb);
        }

        if (includesConfiscatedRules)
        {
            yield return HoverTipFactory.FromKeyword(KleeKeywords.Confiscated);
        }

        if (trigger == Element.None || card.CombatState == null) yield break;

        var seen = new HashSet<Reaction>();
        foreach (var enemy in card.CombatState.HittableEnemies)
        {
            var aura = AuraCmd.Find(enemy);
            if (aura == null) continue;

            var reaction = ReactionTable.Lookup(aura.Element, trigger);
            if (reaction == Reaction.None || !seen.Add(reaction)) continue;

            // `EB-366`. THE PREVIEW READS THE FREEZE'S OWN PREDICATE, and it
            // used to read HALF of it. The substitution is per-CREATURE inside
            // a boss room -- `boss room AND not a Minion` -- and this line
            // asked only the room, so a MINION standing beside a boss previewed
            // "Bosses cannot be Frozen ... 2 Vulnerable instead" and then froze,
            // which is exactly what the freeze branch does for it. Two
            // statements of one rule is one statement too many, so the reader
            // is now `ReactionEffects.FrozenBossVulnWillApply` -- the read-only
            // twin that the damage pipeline already asks one phase early -- and
            // there is no second copy left to drift.
            var keyword = reaction == Reaction.Frozen
                && ReactionEffects.FrozenBossVulnWillApply(enemy)
                    ? KleeKeywords.FrozenBossPreview
                    : KleeKeywords.ReactionPreview(reaction);
            if (keyword == MegaCrit.Sts2.Core.Entities.Cards.CardKeyword.None)
            {
                continue;
            }

            // `EB-338`. The keyword's own TITLE ROW, so a reader still finds
            // the reaction by name, with the body the card can actually keep.
            var substitute = appliesWithoutHit ? NoHitBody(reaction) : null;
            yield return substitute == null
                ? HoverTipFactory.FromKeyword(keyword)
                : new HoverTip(
                    new LocString(Table, NoHitTitleKey(reaction) + ".title"),
                    substitute);
        }
    }

    /// <summary>
    /// `EB-338`. The two preview keywords a no-hit card substitutes the BODY
    /// of, named by their loc key.
    ///
    /// THE KEY RATHER THAN THE KEYWORD, and the reason is the boundary: the
    /// game's own `CardKeyword.GetTitle()` lives on an INTERNAL extension
    /// class, so a mod cannot ask a keyword for its title row. These are the
    /// keys `KleeMod.InjectLocStrings` registers, one const apiece so the two
    /// spellings cannot drift -- pinned against the compiled registration by
    /// `ReactionPreviewNoHitTests`, the same `Il.Strings` read
    /// `KeywordTitleRowTests` uses for every other title row.
    /// </summary>
    public const string VaporizePreviewKey = "KLEEMOD-VAPORIZE_PREVIEW";

    /// <summary>Melt's half of <see cref="VaporizePreviewKey"/>.</summary>
    public const string MeltPreviewKey = "KLEEMOD-MELT_PREVIEW";

    private static string NoHitTitleKey(Reaction reaction) =>
        reaction == Reaction.Vaporize ? VaporizePreviewKey : MeltPreviewKey;

    /// <summary>
    /// `EB-338`. THE PREVIEW ON A CARD WITH NO HIT.
    ///
    /// WHAT THE SEAT SAW (`klee round 7b, opus-act2b.md`,
    /// finding 4). Barbara's stand-in -- "Gain 6 Block. Apply Hydro", and not a
    /// point of damage on it -- carried *"Reaction preview: Vaporize -- The
    /// triggering hit deals 1.5x damage and consumes the aura"* over a Pyro
    /// aura. The reaction fired and the aura went; the enemy stayed on 23/41.
    /// A line advertising a damage bonus delivered a pure loss, and nothing
    /// told the seat apart from the previews on Ka-pow! and Charlotte, which
    /// are worth having.
    ///
    /// THE RULE DOES NOT MOVE, only the words: an APPLICATION reacts, which is
    /// what the Applies-X keyword has always said, and consuming the aura is
    /// the reaction happening rather than a bug. So the preview says the one
    /// thing it was not saying.
    ///
    /// THE SHAPE IS THE BOSS SUBSTITUTION'S, which the same seat called
    /// excellent on the same card: *"Bosses cannot be Frozen. Hydro plus Cryo
    /// is consumed and applies 2 Vulnerable instead."* It names the case, names
    /// what is still consumed, and names what is paid instead.
    ///
    /// ONLY THE TWO MULTIPLIERS ARE SUBSTITUTED, because only they promise a
    /// number that a card with no hit cannot pay. Overload's splash,
    /// Superconduct's Vulnerable, Electro-Charged's dot, Frozen, Swirl and
    /// Crystallize all land in full off an application, so their rows are
    /// already true and are left exactly as they are.
    ///
    /// THE MULTIPLIERS STAY LITERALS, the same decision the loc rows in
    /// `KleeMod.cs` write down: they are floats, and interpolating a float
    /// renders it under the host's culture, so a comma locale would print
    /// "1,5x".
    /// </summary>
    public static string? NoHitBody(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize =>
            "This card deals no damage. Pyro plus Hydro is still consumed, "
          + "and there is no hit here for the 1.5x to multiply.",
        Reaction.Melt =>
            "This card deals no damage. Pyro plus Cryo is still consumed, "
          + "and there is no hit here for the 1.75x to multiply.",
        _ => null,
    };
}
