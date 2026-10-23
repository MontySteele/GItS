using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
// `EB-752`: `TheBoot`, the relic whose rule runs after Block.
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Cards;

/// <summary>
/// Shared card affordances for Bomb rules and board-aware reaction previews.
/// ExtraHoverTips is evaluated when the card is inspected, so the reaction
/// list follows the enemies' current auras without patching card UI nodes.
/// For random/all-enemy cards it intentionally lists every distinct reaction
/// currently available; choosing a particular target remains the player's
/// decision.
///
/// THE TOOLTIP TRIM (2026-10-14): that board-wide list is now the blind
/// seat's (<see cref="TipAudience.Seat"/>). A player sees one preview, for the
/// enemy the card is aimed at, while aiming (<see cref="ReactionAim"/>).
/// </summary>
public static class KleeCardTooltips
{
    /// <summary>The hover-tip title table, same one the rider tips use.</summary>
    private const string Table = "card_keywords";

    /// <summary>`EB-389`. Titles the line a card grows while a rider is
    /// overriding the element it prints.
    ///
    /// A REGISTERED ROW, and `KeywordTitleRowTests` is why: that rule finds
    /// every `KLEEMOD-` key in the assembly by reflection and demands a
    /// registered `.title` row for it, because a key with no row renders AS
    /// the key (0.2-589, 0.2-634). The row it needs is registered beside the
    /// arm's other title rows.</summary>
    public const string OverriddenElementKey = "KLEEMOD-ELEMENT_OVERRIDDEN";


    /// <summary>
    /// `EB-389`. THE ELEMENT THIS CARD'S HIT WILL ACTUALLY APPLY.
    ///
    /// THE FIND (Furina r2 run 2 act 2, finding 1). With Razor's Lightning Fang
    /// up, High Tide ("[Hydro]", Applies Hydro) and Chevreuse ("[Pyro]") both
    /// applied Electro and the faces never changed; without it the same
    /// sequence Vaporized as printed. The seat lost a planned Overloaded to it.
    ///
    /// <c>CompanionOverhaulRiders.ElementFor</c> IS THE ONE EXPRESSION, already
    /// shared by the application site and the reaction site so the two cannot
    /// disagree; this makes the FACE a third reader of it rather than a fourth
    /// copy. It is pure and preview-safe, which is what its own header promises
    /// and what a hover path needs. Sim twin:
    /// `effects.companion_overhaul_card_start`.
    ///
    /// <paramref name="printed"/> is codegen's static answer and is returned
    /// unchanged when no override stands.
    /// </summary>
    public static Element AppliedElement(CardModel card, Element printed)
    {
        // `EB-94`'s door, and it is not optional here: `CardModel.Owner`'s
        // getter asserts mutability, so asking it on a CANONICAL model -- the
        // compendium, a reward shelf -- throws out of the whole `HoverTips`
        // getter and the card loses every tip it had. `TipOwner` answers null
        // there, which is also the right answer: a card nobody holds is under
        // nobody's riders and prints what it prints.
        var over = CompanionOverhaulRiders.ElementFor(
            card, TipOwner.CreatureOf(card));
        if (over != Element.None) return over;
        return printed;
    }

    /// <summary>`EB-389`'s second half: the card says WHICH element, in words,
    /// because a gem swapped under a reader who has already read the face is
    /// the same silence one step quieter.</summary>
    public static string OverriddenElementBody(Element applied) =>
        CodeText.Format(OverriddenElementRow, CodeText.Vars(("Element", ElementWords.Name(applied))));

    /// <summary>
    /// <paramref name="appliesWithoutHit"/> is `EB-338`. See
    /// <see cref="NoHitBody"/> for what it changes and
    /// <c>gen_klee_cards.emit</c> for how it is derived (never remembered).
    /// </summary>
    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        Element trigger = Element.None,
        bool includesConfiscatedRules = false,
        bool appliesWithoutHit = false,
        bool includesDazedCard = false,
        bool elementOnlyOnSpend = false)
    {
        foreach (var tip in inherited) yield return tip;

        if (includesConfiscatedRules)
        {
            yield return HoverTipFactory.FromKeyword(KleeKeywords.Confiscated);
        }

        // THE KLEE STATUS PACKAGE (2026-10-01): a card that shuffles in the
        // base game's Dazed previews it, the way a Shiv maker previews a Shiv.
        if (includesDazedCard)
        {
            yield return HoverTipFactory.FromCard<MegaCrit.Sts2.Core.Models.Cards.Dazed>(false);
        }

        // `EB-389`. THE ELEMENT A RIDER IS ABOUT TO APPLY, not the one the face
        // prints. `trigger` is codegen's STATIC answer -- the card's printed
        // element -- and an override rider makes it wrong for as long as it
        // stands: with Razor's Lightning Fang up, High Tide ("[Hydro]") and
        // Chevreuse ("[Pyro]") both applied Electro and neither face moved
        // (Furina r2 run 2 act 2). It cost a planned Overloaded, because the
        // previews below were computed against the printed element too.
        //
        // ONE READ, TWO USES: the preview is computed against the element that
        // will actually land, and where that differs from the print the card
        // says so in words.
        var applied = AppliedElement(card, trigger);
        if (applied != trigger && applied != Element.None)
        {
            yield return new HoverTip(
                new LocString(Table, OverriddenElementKey + ".title"),
                OverriddenElementBody(applied));
        }
        trigger = applied;

        if (trigger == Element.None || card.CombatState == null) yield break;

        // THE TOOLTIP TRIM (2026-10-14), pick 2 (a). A player sees a preview
        // only for the enemy the card is being aimed at, raised by
        // `ReactionAim` while it is dragged onto that enemy, and none while
        // the card is only hovered in hand. A blind seat (`TipAudience.Seat`)
        // reads every matching aura's preview, as before the trim.
        var aimed = ReactionAim.TargetFor(card);
        if (aimed == null && !TipAudience.Seat) yield break;

        var previews = new List<IHoverTip>();
        // Co-op seat (2026-10-16): Kaeya's Frozen preview missed an Artifact
        // that ate the freeze. A Frozen an Artifact will block is its own row,
        // so a plain Frozen on another enemy cannot hide it.
        var seen = new HashSet<(Reaction, bool, Element)>();
        var printedTrigger = trigger;
        var hittable = card.CombatState.HittableEnemies;
        var several = hittable.Count() > 1;
        foreach (var enemy in PreviewOrder(card, hittable))
        {
            if (aimed != null && !ReferenceEquals(enemy, aimed)) continue;
            var aura = AuraCmd.Find(enemy);
            if (aura == null) continue;
            trigger = printedTrigger;

            var reaction = ReactionTable.Lookup(aura.Element, trigger);
            // Kit display pass (2026-10-18), the Varka combo round's item 4:
            // an Artifact also eats Overloaded's Weak, Superconduct's
            // Vulnerable and Electro-Charged's Poison, so those rows say so.
            var blocked = ReactionEffects.ArtifactWillBlock(reaction, enemy);
            // Swirl legibility (2026-10-19): a Swirl preview names the element
            // it spreads, so one per aura element, not one per reaction.
            var spread = reaction == Reaction.Swirl ? aura.Element : Element.None;
            if (reaction == Reaction.None || !seen.Add((reaction, blocked, spread)))
            {
                continue;
            }

            // SWIRL LEGIBILITY (2026-10-19): the Swirl preview says what this
            // Swirl does here -- the element it spreads, the damage, and for
            // Varka the Oath it credits and what his Fang pays -- instead of
            // the generic rule.
            if (reaction == Reaction.Swirl)
            {
                previews.Add(new HoverTip(
                    new LocString(Table, PreviewKey(reaction, false) + ".title"),
                    SpendOnlyIf(elementOnlyOnSpend, SwirlBody(card, aura.Element, several))));
                continue;
            }

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
            //
            // `EB-589`: and where the card HITS and the reaction AMPLIFIES,
            // the body carries the folded number instead. Same substitution
            // mechanism, same two title keys -- Vaporize and Melt are the two
            // amplifying reactions and are exactly the pair `NoHitTitleKey`
            // already names.
            var substitute = appliesWithoutHit
                ? NoHitBody(reaction)
                : AmplifiedBody(card, reaction, enemy, aura.Element);
            // 2026-10-01 (a Varka seat): Kaeya's Cryo on a Hydro Cubex
            // Construct promised Frozen, and its Artifact ate the freeze.
            // The preview asks the Artifact alone: the log's detail also
            // reads a mark one hit scopes, and a mark left by the last hit
            // hid the warning (co-op seat, 2026-10-16).
            if (blocked && reaction != Reaction.Frozen)
            {
                var debuffKey = PreviewKey(reaction, false);
                previews.Add(new HoverTip(
                    new LocString(Table, debuffKey + ".title"),
                    SpendOnlyIf(elementOnlyOnSpend, CodeText.Format(WithArtifactRow, CodeText.Vars(
                        ("Body", new LocString(Table, debuffKey + ".description")
                            .GetFormattedText()),
                        ("Artifact", DebuffArtifactSentence(
                            ReactionEffects.ArtifactBlockedDebuff(reaction)!,
                            several ? enemy.Name : null)))))));
                continue;
            }
            if (blocked)
            {
                var boss = ReactionEffects.FrozenBossVulnWillApply(enemy);
                previews.Add(new HoverTip(
                    new LocString(Table, (boss ? FrozenBossPreviewKey
                                               : FrozenPreviewKey) + ".title"),
                    SpendOnlyIf(elementOnlyOnSpend, FrozenArtifactBody(boss,
                              several ? enemy.Name : null))));
                continue;
            }
            // 2026-10-04 (Furina v2 seat round): Tidal Flourish previewed
            // "Frozen" over a Cryo aura while its plain mode applies no Hydro
            // at all -- only the Spend mode does. Where the element lands only
            // behind a Spend, the preview names that condition first.
            if (elementOnlyOnSpend)
            {
                var key = PreviewKey(reaction,
                    keyword == KleeKeywords.FrozenBossPreview);
                previews.Add(new HoverTip(
                    new LocString(Table, (substitute == null
                        ? key : NoHitTitleKey(reaction)) + ".title"),
                    SpendOnly(substitute
                        ?? new LocString(Table, key + ".description")
                            .GetFormattedText())));
            }
            else
            {
                previews.Add(substitute == null
                    ? HoverTipFactory.FromKeyword(keyword)
                    : new HoverTip(
                        new LocString(Table, NoHitTitleKey(reaction) + ".title"),
                        substitute));
            }
            // Text pass 2026-09-25: the Electro-Charged preview names Poison
            // and no longer spells out how it ticks, so Poison's own tip
            // rides beside it. A hover tip cannot nest, so this is the attach.
            if (reaction == Reaction.ElectroCharged)
            {
                previews.Add(HoverTipFactory.FromPower<MegaCrit.Sts2.Core.Models.Powers.PoisonPower>());
            }
        }

        if (aimed != null)
        {
            ReactionAim.Collect(previews);
            yield break;
        }
        foreach (var preview in previews) yield return preview;
    }


    /// <summary>
    /// `EB-589`. THE PREVIEWED REACTION, FOLDED INTO A NUMBER -- `EB-559`'s
    /// repair one surface over, and it reuses that row's reader rather than
    /// deriving a second one.
    ///
    /// THE FIND (Furina r15 lane 2 (c) 2). Chevreuse printed 7, 10 and 10 and
    /// delivered 11, 15 and 22: "the Spotlight and Weak and Passion Overload
    /// are all folded into the number on the face; the previewed 1.5x Vaporize
    /// never is. The face is right about four modifiers and silent about the
    /// biggest one."
    ///
    /// WHY THE FACE CANNOT DO IT AND THIS CAN, which is the whole shape of the
    /// row. The amplifier and the target's Vulnerable are per-BODY terms, and
    /// a card in hand has no target -- <c>CalculatedDamageVar</c>'s preview is
    /// handed one only while the card is dragged over an enemy, so the four
    /// modifiers it does fold are exactly the four that are facts about the
    /// PLAYER. This tip is the surface that already walks the board: it is
    /// raised only while a matching aura is out, and it knows which body
    /// raised it.
    ///
    /// <c>SimDamagePipeline.ResolveOnTarget</c> AND NOT A SECOND COPY of the
    /// arithmetic: it is `ElementalHit.Deal`'s own target-mods, one truncation
    /// and per-hit cap, and it is what `ProtoBombPower.PredictedSetOffDamage`
    /// asks for the same question about a pile. So a face that disagrees with
    /// the board is a red test rather than a number a seat stops trusting.
    ///
    /// THE FIRST BODY CARRYING THE AURA, because the loop above dedupes by
    /// REACTION rather than by enemy: two Hydro bodies wearing different
    /// Vulnerable would land different numbers and the preview names one. That
    /// is the same trade `PredictedSetOffDamage` makes about the pile it walks,
    /// and the alternative -- a row per body -- is the wall of tips this class
    /// exists to keep off a card.
    ///
    /// PURE. It is read on every state poll, so it touches no command and
    /// rolls no counter: <c>ReactionTable.AmplifierMultiplier</c>,
    /// <c>ResolveOnTarget</c> and a var read are all reads.
    ///
    /// NULL WHERE THERE IS NOTHING TO FOLD -- no amplifier on this reaction --
    /// and the keyword's own body prints exactly as it always has.
    ///
    /// `EB-614`: EXCEPT WHERE THE CARD HAS NO HIT, WHICH IS NOT THE SAME
    /// SILENCE. A zero-damage card that DECLARES the element takes this branch
    /// rather than <see cref="NoHitBody"/>'s -- `appliesWithoutHit` is set off
    /// the declaration and not off the number -- so "no damage number on this
    /// card" fell back to a keyword row promising "the triggering hit deals
    /// 1.5x damage". Such a card fires the reaction, strips the aura and pays
    /// nothing, and the seat that used it on purpose derived that from the
    /// board (Klee r8 run 2 act 2, and again in r10 run 2 act 2). That is
    /// `EB-338`'s finding arriving through the other door, so it takes
    /// `EB-338`'s answer -- the same sentence, out of the same method, because
    /// two wordings of one rule is how a screen contradicts itself.
    /// </summary>
    private static string? AmplifiedBody(
        CardModel card, Reaction reaction, Creature enemy, Element aura)
    {
        var dealer = TipOwner.CreatureOf(card);
        var mult = ReactionTable.AmplifierMultiplier(reaction, dealer);
        if (mult == 1m) return null;
        var printed = PrintedDamage(card);
        if (printed <= 0) return NoHitBody(reaction);

        // `EB-602`: THE TARGET'S TERMS ONLY WHERE THE FACE HAS NOT ALREADY
        // FOLDED THEM. `FrontFoldedDamageVar` (the arm's proto rows) writes
        // them into `PreviewValue` itself, and `PrintedDamage` now reads that
        // number, so asking `ResolveOnTarget` for them again would multiply a
        // Vulnerable twice. Asked by TYPE NAME rather than by type, a
        // leftover from when the class was not compiled in every build.
        // `EB-733`. A CARD THAT SETS OFF FIRST DOES NOT GET ITS OWN AMPLIFIER.
        //
        // THE FIND (Klee r26 lane 1, (c) 5). Pocket Match's *Reaction preview:
        // Melt* said "this card's 7 lands 12" into a Cryo aura, and it landed
        // 7: the Set off in the card's own first sentence had eaten the aura a
        // beat earlier, so the reaction was the BOMB's and the card's own hit
        // met a bare body. "It reads as a contradiction until you work out the
        // ordering." `EB-387`'s family -- and the Set off tip one class over
        // already states the rule ("the first takes the aura"), which is what
        // made the number beside it a contradiction rather than a gap.
        //
        // THE REACTION IS STILL PREVIEWED, because one still happens: the
        // title row is true and only the body's arithmetic was false. So the
        // body names the ORDER, whose multiplier it is, and the number that
        // actually lands -- this card's own hit with no amplifier on it, the
        // target's terms and the per-hit cap read exactly as below.
        //
        // THE FACE IS THE TEST, which is the row's own wording ("a card whose
        // first sentence is Set off"): what decides this is whether the Set
        // off resolves before the card's own damage, and the printed order is
        // where that is written down.
        if (SetsOffFirst(card))
        {
            var own = TargetAlreadyFolded(card)
                ? Capped(enemy, printed)
                : SimDamagePipeline.ResolveOnTarget(enemy, printed, 1m);
            return WithBoot(SetOffFirstBody(aura, mult, printed, own), Boot(dealer));
        }
        // THE FACE MAY ALREADY CARRY THE AMPLIFIER (the Varka element
        // identities round, 2026-10-01). Amber: Sharpshooter's face read 18
        // into a Hydro aura, this tip said "this card's 18 lands 27", and 18
        // landed: `FrontFoldedDamageVar` previews against the front enemy
        // with the game's hooks, and that body's own aura hook
        // (`AuraPower.ModifyDamageMultiplicative`) had already put the 1.5x
        // into the 18. Where the face folded THIS body, its number is the
        // landed one and only the cap is left to apply.
        if (TargetAlreadyFolded(card) && ReferenceEquals(FaceBody(card), enemy))
        {
            return WithBoot(FoldedHereBody(mult, printed, aura, Capped(enemy, printed)),
                            Boot(dealer));
        }
        // THE FACE FOLDED A DIFFERENT BODY (Kokomi seats, 2026-10-14). Two
        // seats read "Reaction preview: Vaporize ... lands 31" on a Chevreuse
        // whose hit into a Hydro Ovicopter dealt 21. The face had folded the
        // FRONT enemy's terms -- its Vaporize included, 14 x 1.5 = 21 -- and
        // this line multiplied that 21 by 1.5 again for another Hydro body.
        // So the face body's terms come OUT of the printed number before this
        // body's go in (`LandedOffFoldedFace`).
        var landed = TargetAlreadyFolded(card)
            ? LandedOffFoldedFace(
                printed,
                FaceBody(card) is { } face ? BodyTerms(face, card, dealer) : 1m,
                BodyTerms(enemy, card, dealer),
                SimDamagePipeline.TargetCap(enemy))
            : SimDamagePipeline.ResolveOnTarget(enemy, printed, mult);
        return WithBoot(FoldedElsewhereBody(mult, aura, printed, landed), Boot(dealer));
    }

    // ---- THE RIDERS' ROWS (the localization census, 2026-10-23, step 2).
    // Every rider this class builds is a row in `card_keywords` under the
    // preview's own key, read through `CodeText`: the multiplier and the
    // numbers are vars, an element's name its own row (`ElementWords`), an
    // enemy's name the game's; where two sentences join, the join is a row.

    internal static readonly CodeRow OverriddenElementRow = new(Table, OverriddenElementKey + ".description",
        "While the buff stands, this card's hit applies [gold]{Element}[/gold] instead of the "
      + "element it prints.");
    private static readonly string PreviewRowKey = "KLEEMOD-REACTION_PREVIEW";
    internal static readonly CodeRow SetOffFirstRow = new(Table, PreviewRowKey + ".amplified_set_off_first",
        "The [gold]Set off[/gold] takes the {Aura} aura first, so the {Mult}x is the "
      + "[gold]Bomb[/gold]'s. This card's own {Printed} lands {Landed}.");
    internal static readonly CodeRow FoldedHereRow = new(Table, PreviewRowKey + ".amplified_folded_here",
        "The triggering hit deals {Mult}x damage and consumes the aura. The {Printed} on this "
      + "card already counts it: into that {Aura} aura it lands {Landed}.");
    internal static readonly CodeRow FoldedElsewhereRow = new(Table, PreviewRowKey + ".amplified_folded_elsewhere",
        "The triggering hit deals {Mult}x damage and consumes the aura. Into that {Aura} aura "
      + "this card's {Printed} lands {Landed}.");
    public static readonly CodeRow BootRow = new(Table, PreviewRowKey + ".boot",
        "[gold]The Boot[/gold] raises an unblocked hit after Block, so it is not in that number.");
    internal static readonly CodeRow WithBootRow = new(Table, PreviewRowKey + ".with_boot", "{Body} {Boot}");
    internal static readonly CodeRow WithArtifactRow = new(Table, PreviewRowKey + ".with_artifact",
        "{Body} {Artifact}");
    internal static readonly CodeRow DebuffArtifactRow = new(Table, PreviewRowKey + ".artifact",
        "But its [gold]Artifact[/gold] blocks the [gold]{Debuff}[/gold].");
    internal static readonly CodeRow DebuffArtifactNamedRow = new(Table, PreviewRowKey + ".artifact_named",
        "But {Enemy}'s [gold]Artifact[/gold] blocks the [gold]{Debuff}[/gold].");
    internal static readonly CodeRow SpendOnlyRow = new(Table, PreviewRowKey + ".only_if_spend",
        "Only if you [gold]Spend[/gold]: {Body}");
    internal static readonly CodeRow FrozenArtifactRow = new(Table, FrozenPreviewKey + ".description_artifact",
        "[gold]Hydro[/gold] meets [gold]Cryo[/gold] and the aura is used up, but its "
      + "[gold]Artifact[/gold] blocks the Frozen.");
    internal static readonly CodeRow FrozenArtifactNamedRow = new(Table,
        FrozenPreviewKey + ".description_artifact_named",
        "[gold]Hydro[/gold] meets [gold]Cryo[/gold] and the aura is used up, but {Enemy}'s "
      + "[gold]Artifact[/gold] blocks the Frozen.");
    internal static readonly CodeRow FrozenBossArtifactRow = new(Table,
        FrozenBossPreviewKey + ".description_artifact",
        "[gold]Hydro[/gold] meets [gold]Cryo[/gold] and the aura is used up, but its "
      + "[gold]Artifact[/gold] blocks the [gold]Vulnerable[/gold].");
    internal static readonly CodeRow FrozenBossArtifactNamedRow = new(Table,
        FrozenBossPreviewKey + ".description_artifact_named",
        "[gold]Hydro[/gold] meets [gold]Cryo[/gold] and the aura is used up, but {Enemy}'s "
      + "[gold]Artifact[/gold] blocks the [gold]Vulnerable[/gold].");
    internal static readonly CodeRow VaporizeNoHitRow = new(Table, VaporizePreviewKey + ".description_no_hit",
        "This card deals no damage. Pyro plus Hydro is still consumed, and there is no hit here "
      + "for the {Mult}x to multiply.");
    internal static readonly CodeRow MeltNoHitRow = new(Table, MeltPreviewKey + ".description_no_hit",
        "This card deals no damage. Pyro plus Cryo is still consumed, and there is no hit here "
      + "for the {Mult}x to multiply.");
    private static readonly string SwirlKey = "KLEEMOD-SWIRL_PREVIEW";
    internal static readonly CodeRow SwirlSpreadsRow = new(Table, SwirlKey + ".description_spreads",
        "Spreads [gold]{Element}[/gold] to the other enemies and deals [blue]{Damage}[/blue] damage "
      + "to ALL enemies.");
    internal static readonly CodeRow SwirlRemovesRow = new(Table, SwirlKey + ".description_removes",
        "Removes the [gold]{Element}[/gold] aura and deals [blue]{Damage}[/blue] damage to ALL "
      + "enemies.");
    internal static readonly CodeRow SwirlOathRow = new(Table, SwirlKey + ".description_oath",
        "{Body} +1 [gold]{Oath}[/gold] Oath.");
    internal static readonly CodeRow SwirlOathPaysRow = new(Table, SwirlKey + ".description_oath_pays",
        "{Body} +1 [gold]{Oath}[/gold] Oath; {Pays}.");
    internal static readonly CodeRow SwirlPaysRow = new(Table, SwirlKey + ".description_pays",
        "{Body} {Pays}.");

    /// <summary>The debuff words an Artifact blocks, each its own row
    /// (<see cref="ReactionEffects.ArtifactBlockedDebuff"/>'s English).</summary>
    internal static CodeRow DebuffWordRow(string debuff) =>
        new(Table, PreviewRowKey + ".debuff_" + debuff.ToUpperInvariant(), debuff);

    private static readonly string[] Debuffs = { "Weak", "Vulnerable", "Poison" };

    /// <summary>Every rider's row (<see cref="CodeText.Sources"/>).</summary>
    public static IEnumerable<CodeRow> TextRows() =>
        new[]
        {
            OverriddenElementRow, SetOffFirstRow, FoldedHereRow, FoldedElsewhereRow, BootRow,
            WithBootRow, WithArtifactRow, DebuffArtifactRow, DebuffArtifactNamedRow, SpendOnlyRow,
            FrozenArtifactRow, FrozenArtifactNamedRow, FrozenBossArtifactRow, FrozenBossArtifactNamedRow,
            VaporizeNoHitRow, MeltNoHitRow, SwirlSpreadsRow, SwirlRemovesRow, SwirlOathRow,
            SwirlOathPaysRow, SwirlPaysRow,
        }.Concat(Debuffs.Select(DebuffWordRow));

    /// <summary>A multiplier as the riders print it: two places at most, as
    /// the old <c>0.##</c> did.</summary>
    private static decimal Mult(decimal mult) =>
        CodeText.Num(decimal.Round(mult, 2, System.MidpointRounding.AwayFromZero));

    private static IReadOnlyDictionary<string, object> AmpVars(
        Element aura, decimal mult, int printed, int landed) =>
        CodeText.Vars(("Aura", ElementWords.Name(aura)), ("Mult", Mult(mult)),
                      ("Printed", printed), ("Landed", landed));

    /// <summary>A card that sets off first: the Bomb's multiplier, this
    /// card's own number.</summary>
    public static string SetOffFirstBody(Element aura, decimal mult, int printed, int own) =>
        CodeText.Format(SetOffFirstRow, AmpVars(aura, mult, printed, own));

    /// <summary>The face already folded this body's amplifier.</summary>
    public static string FoldedHereBody(decimal mult, int printed, Element aura, int landed) =>
        CodeText.Format(FoldedHereRow, AmpVars(aura, mult, printed, landed));

    /// <summary>The face folded another body, or none.</summary>
    public static string FoldedElsewhereBody(decimal mult, Element aura, int printed, int landed) =>
        CodeText.Format(FoldedElsewhereRow, AmpVars(aura, mult, printed, landed));

    /// <summary>The body, and The Boot's sentence after it when
    /// <paramref name="boot"/>.</summary>
    public static string WithBoot(string body, bool boot) =>
        boot ? CodeText.Format(WithBootRow, CodeText.Vars(("Body", body), ("Boot", CodeText.Format(BootRow))))
             : body;

    /// <summary>Only if you Spend: the body.</summary>
    public static string SpendOnly(string body) =>
        CodeText.Format(SpendOnlyRow, CodeText.Vars(("Body", body)));

    private static string SpendOnlyIf(bool onlyOnSpend, string body) =>
        onlyOnSpend ? SpendOnly(body) : body;

    /// <summary>
    /// The order the reaction loop visits bodies in: where the face folded a
    /// body, THAT body first, so a reaction it shares with another body is
    /// previewed off the body the printed number already describes. Board
    /// order otherwise. PURE.
    /// </summary>
    private static IEnumerable<Creature> PreviewOrder(
        CardModel card, IEnumerable<Creature> hittable)
    {
        var list = hittable.ToList();
        var face = TargetAlreadyFolded(card) ? FaceBody(card) : null;
        if (face == null || !list.Remove(face)) return list;
        list.Insert(0, face);
        return list;
    }

    /// <summary>
    /// The target-side multiplier a powered hit from this card meets on
    /// <paramref name="body"/>: the product of that body's own
    /// <c>ModifyDamageMultiplicative</c> answers -- its aura's amplifier
    /// (<c>AuraPower</c>) and its Vulnerable -- the same hooks the face's
    /// preview folded. PURE: those hooks run on every preview.
    /// </summary>
    private static decimal BodyTerms(Creature body, CardModel card, Creature? dealer)
    {
        var terms = 1m;
        foreach (var power in body.Powers)
        {
            terms *= power.ModifyDamageMultiplicative(
                body, 1m, MegaCrit.Sts2.Core.ValueProps.ValueProp.Move,
                dealer, card, null);
        }
        return terms;
    }

    /// <summary>
    /// What a folded face's <paramref name="printed"/> lands on another body:
    /// the face body's target terms (<paramref name="faceTerms"/>) divided
    /// back out, this body's (<paramref name="bodyTerms"/>) multiplied in,
    /// one truncation, then this body's <paramref name="cap"/>. The Kokomi
    /// seats' case (2026-10-14): a 21 folded off a Hydro front enemy, into a
    /// second Hydro body, is 21 -- not 31. Rounded to six places before the
    /// truncation so a divide-then-multiply never lands a hair under an
    /// integer. Public so a headless test can pin the arithmetic.
    /// </summary>
    public static int LandedOffFoldedFace(
        int printed, decimal faceTerms, decimal bodyTerms, decimal cap)
    {
        if (faceTerms <= 0m) faceTerms = 1m;
        var landed = (int)decimal.Round(printed / faceTerms * bodyTerms, 6);
        return landed > cap ? (int)cap : landed;
    }

    /// <summary>
    /// The body a <c>FrontFoldedDamageVar</c> face folds its number against
    /// while it sits in the hand with no aim: the front enemy, or none on a
    /// Furina Stage board (<c>FoldedPreview.Body</c> with no target). PURE.
    /// </summary>
    private static Creature? FaceBody(CardModel card)
    {
        var owner = TipOwner.CreatureOf(card);
        return FurinaStage.LiveFor(owner) ? null : KokomiPlan.FrontEnemy(owner);
    }

    /// <summary>
    /// `EB-752`. THE ONE TERM THIS NUMBER CANNOT CARRY, named beside it.
    ///
    /// THE FIND (Klee r27, lanes 2 and cook, fight 2 each). "Ka-pow! printed
    /// Deal 4 while The Boot made it 5", and on a Weak turn the printed
    /// numbers under-counted in the direction that makes a seat UNDER-play.
    ///
    /// WHY NO FACE AND NO FOLD CAN HOLD IT, which is `EB-328`'s finding and
    /// the reason the row was re-scoped: The Boot is a
    /// <c>ModifyHpLostAfterOstyLate</c> hook. It runs AFTER the target's Block
    /// has been taken out of the hit, so it is not a damage modifier at all --
    /// it is an HP-loss modifier, and every arithmetic on this tip (and every
    /// <c>CalculatedDamageVar</c> on every face) stops one phase earlier. A
    /// number here that included it would be wrong on every blocked hit.
    ///
    /// THIS TIP IS THE SURFACE THAT CAN SAY IT, for <see cref="AmplifiedBody"/>'s
    /// own reason: it is the one place in this class that prints a LANDED
    /// number, and a landed number is exactly what a reader will compare with
    /// the bar afterwards. The blind page's twin is
    /// `blindplay_render._unblocked_raise_clause`, and it says the same thing
    /// in the same place -- after the number, with the condition attached.
    ///
    /// NO ARITHMETIC, DELIBERATELY. The page can do it because the relic's own
    /// printed sentence rides the feed with its numbers in it; here the relic
    /// is a held model and its rule is a localized row, so the honest thing is
    /// to name it and say WHERE it runs. "" for a player not holding it, which
    /// is every board the clause would be noise on.
    /// </summary>
    private static bool Boot(Creature? dealer) =>
        dealer?.Player?.Relics.Any(relic => relic is TheBoot) == true;

    /// <summary>
    /// `EB-733`. Does this card's printed face put <b>Set off</b> before its
    /// own damage?
    ///
    /// A DATA FLAG, NOT A TEXT READ (localization route b, 2026-10-19): the
    /// card generator stamps <see cref="ISetsOffFirstCard"/> on a row whose
    /// face opens with an aimed Set off, so nothing at runtime reads English
    /// to decide behaviour. False for every card that is not one of ours, and
    /// false for a row whose Set off comes AFTER its damage: there the card's
    /// own hit does meet the aura and the amplified body is right as it
    /// stands.
    /// </summary>
    public static bool SetsOffFirst(CardModel card) => card is ISetsOffFirstCard;

    /// <summary>
    /// `EB-589`. The number this card's face is printing right now, or 0 where
    /// it prints none.
    ///
    /// TWO NAMES AND NOT A TYPE TEST: a generated Attack carries
    /// <c>CalculatedDamage</c> (base, extra and the Spotlight multiplier
    /// composed) and a hand-written one carries <c>Damage</c>, and
    /// <c>TryGetValue</c> is the game's own way of asking which.
    ///
    /// `EB-602`: <c>PreviewValue</c> AND NOT <c>IntValue</c>, and this is the
    /// row. <c>IntValue</c> is the var's stored BASE -- MEASURED on the
    /// shipped assembly: setting <c>PreviewValue</c> to 10 on a var built at
    /// 7 leaves <c>IntValue</c> answering 7 -- while <c>PreviewValue</c> is
    /// the number <c>{Var:diff()}</c> renders, which is what "the number this
    /// card's face is printing" means. A lit Chevreuse showed the difference:
    /// the face read 10 off a base of 7, this tip named Vaporize off the 7,
    /// and 15 landed (Furina r16 lane 1 (c) 3). The Spotlight, her Weak and
    /// Passion Overload all live in that gap, and the tip's own claim is that
    /// it folds the same number the face does.
    ///
    /// THE BASE IS THE FALLBACK, for the read where no preview has run: a var
    /// that has never been previewed answers 0, and 0 is not a face.
    /// </summary>
    private static int PrintedDamage(CardModel card)
    {
        var dynamicVar = PrintedVar(card);
        if (dynamicVar == null) return 0;
        var preview = (int)dynamicVar.PreviewValue;
        return preview > 0 ? preview : dynamicVar.IntValue;
    }

    /// <summary>
    /// The var <see cref="PrintedDamage"/> reads: <c>CalculatedDamage</c>,
    /// else <c>Damage</c>, else -- Kokomi Balance suite 4 (2026-10-21) -- the
    /// live arm of a two-armed face whose only hit is the
    /// <c>PlainDamage</c> / <c>BranchDamage</c> pair. Press the Advantage
    /// ("Deal 8. If a Plan is waiting, deal 13 instead.") has no other damage
    /// var, so this tip printed "This card deals no damage" over a card that
    /// dealt 13. The card says which arm is live
    /// (<see cref="IBranchDamageFace"/>); without it, the plain arm.
    /// Null for a card with no hit.
    /// </summary>
    public static DynamicVar? PrintedVar(CardModel card)
    {
        foreach (var name in new[] { "CalculatedDamage", "Damage" })
        {
            if (card.DynamicVars.TryGetValue(name, out var dynamicVar))
            {
                return dynamicVar;
            }
        }
        if (BranchLive(card)
            && card.DynamicVars.TryGetValue("BranchDamage", out var branch))
        {
            return branch;
        }
        return card.DynamicVars.TryGetValue("PlainDamage", out var plain)
            ? plain : null;
    }

    /// <summary><see cref="IBranchDamageFace.BranchDamageLive"/>, false for
    /// any other card and on a throw (a card with no owner). Display only.
    /// </summary>
    private static bool BranchLive(CardModel card)
    {
        try
        {
            return card is IBranchDamageFace { BranchDamageLive: true };
        }
        catch (System.Exception)
        {
            return false;
        }
    }

    /// <summary>
    /// `EB-602`. Has this face already folded the target's own terms into the
    /// number <see cref="PrintedDamage"/> just read?
    ///
    /// ONE TYPE DOES, and it is `EB-522`'s: <c>FrontFoldedDamageVar</c> writes
    /// <see cref="SimDamagePipeline.TargetMods"/> into its own
    /// <c>PreviewValue</c>, because a Kokomi face read off a blind page has no
    /// drag target to be handed one. Every other var stops at the dealer's
    /// hooks, which is why this tip exists at all.
    ///
    /// BY NAME AND NOT BY TYPE, a leftover from when that class (under
    /// <c>Powers/Prototype/</c>) was not compiled in every build.
    ///
    /// Kokomi Balance suite 4 (2026-10-21): and the pair's own
    /// <c>FoldedDamageVar</c> (and its <c>PlanCarriedDamageVar</c> headline),
    /// which fold the same body the same way (<c>FoldedPreview.Body</c>), so
    /// Press the Advantage's 13 into a Vulnerable body is not multiplied by
    /// the Vulnerable twice.
    /// </summary>
    private static bool TargetAlreadyFolded(CardModel card) =>
        PrintedVar(card)?.GetType().Name is "FrontFoldedDamageVar"
            or "FoldedDamageVar" or "PlanCarriedDamageVar";

    /// <summary>
    /// `EB-602`. <see cref="SimDamagePipeline.ResolveOnTarget"/>'s last step
    /// on its own -- the per-hit cap the target imposes -- for the one branch
    /// whose number has already been through that method's other two.
    /// </summary>
    private static int Capped(Creature enemy, int landed)
    {
        var cap = SimDamagePipeline.TargetCap(enemy);
        return landed > cap ? (int)cap : landed;
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

    /// <summary>Frozen's two preview keys, for the Artifact body below.</summary>
    public const string FrozenPreviewKey = "KLEEMOD-FROZEN_PREVIEW";
    public const string FrozenBossPreviewKey = "KLEEMOD-FROZEN_BOSS_PREVIEW";

    /// <summary>2026-10-01: the Frozen preview over a target whose Artifact
    /// will negate what the reaction applies. The aura is still used up.
    /// With several enemies, <paramref name="who"/> names the one.
    /// </summary>
    public static string FrozenArtifactBody(bool boss, string? who = null) =>
        string.IsNullOrEmpty(who)
            ? CodeText.Format(boss ? FrozenBossArtifactRow : FrozenArtifactRow)
            : CodeText.Format(boss ? FrozenBossArtifactNamedRow : FrozenArtifactNamedRow,
                              CodeText.Vars(("Enemy", who)));

    /// <summary>Kit display pass (2026-10-18): the sentence a debuffing
    /// reaction's preview ends with when the target's Artifact will negate
    /// the debuff. The reaction still happens and the aura is still used up.
    /// With several enemies, <paramref name="who"/> names the one.</summary>
    public static string DebuffArtifactSentence(string debuff, string? who = null) =>
        string.IsNullOrEmpty(who)
            ? CodeText.Format(DebuffArtifactRow, CodeText.Vars(("Debuff", CodeText.Format(DebuffWordRow(debuff)))))
            : CodeText.Format(DebuffArtifactNamedRow, CodeText.Vars(
                ("Enemy", who), ("Debuff", CodeText.Format(DebuffWordRow(debuff)))));

    /// <summary>2026-10-04: the condition a Spend-gated element's
    /// reaction preview opens with.</summary>

    /// <summary>The loc key of a reaction's preview keyword, the keys
    /// `KleeMod.InjectLocStrings` registers.</summary>
    public static string PreviewKey(Reaction reaction, bool frozenBoss) =>
        reaction switch
        {
            Reaction.Vaporize => VaporizePreviewKey,
            Reaction.Melt => MeltPreviewKey,
            Reaction.Overload => "KLEEMOD-OVERLOAD_PREVIEW",
            Reaction.Superconduct => "KLEEMOD-SUPERCONDUCT_PREVIEW",
            Reaction.ElectroCharged => "KLEEMOD-ELECTRO_CHARGED_PREVIEW",
            Reaction.Frozen => frozenBoss ? FrozenBossPreviewKey
                                          : FrozenPreviewKey,
            Reaction.Swirl => "KLEEMOD-SWIRL_PREVIEW",
            Reaction.Crystallize => "KLEEMOD-CRYSTALLIZE_PREVIEW",
            _ => "",
        };

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
        Reaction.Vaporize => CodeText.Format(VaporizeNoHitRow,
            CodeText.Vars(("Mult", Mult(ReactionConstants.VaporizeMult)))),
        Reaction.Melt => CodeText.Format(MeltNoHitRow,
            CodeText.Vars(("Mult", Mult(ReactionConstants.MeltMult)))),
        _ => null,
    };

    /// <summary>
    /// SWIRL LEGIBILITY (2026-10-19). The Swirl preview's body for this card
    /// against a <paramref name="aura"/> aura: the spread and the flat damage
    /// (<c>ReactionEffects.SwirlPays</c>, Durin's White folded in as there),
    /// then, for a live Varka, the Oath the Swirl credits and what his Fang
    /// pays (<see cref="VarkaOath.SwirlPaysNow"/>). Display only.
    /// </summary>
    private static string SwirlBody(CardModel card, Element aura, bool others)
    {
        var dealer = TipOwner.CreatureOf(card);
        var damage = (int)(ReactionConstants.SwirlDamage
                           * CompanionOverhaulReactions.DamageMultiplier(dealer));
        var varka = dealer != null && VarkaOath.Live(dealer);
        return SwirlPreviewBody(
            aura, others, damage,
            varka && VarkaOath.IsOathElement(aura) ? aura : Element.None,
            varka ? VarkaOath.SwirlPaysNow(dealer, card) : "");
    }

    /// <summary>
    /// The Swirl preview's words, at most two sentences: "Spreads Cryo to the
    /// other enemies and deals 2 damage to ALL enemies." (with one enemy,
    /// "Removes the Cryo aura and ..."), then Varka's "+1 Cryo Oath; Swirl
    /// pays Hydro: 3 Block." where <paramref name="oath"/> or
    /// <paramref name="pays"/> says so. PURE.
    /// </summary>
    public static string SwirlPreviewBody(Element aura, bool others, int damage,
                                          Element oath, string pays)
    {
        var body = CodeText.Format(others ? SwirlSpreadsRow : SwirlRemovesRow, CodeText.Vars(
            ("Element", ElementWords.Name(aura)), ("Damage", damage)));
        var vars = CodeText.Vars(("Body", body), ("Oath", ElementWords.Name(oath)), ("Pays", pays));
        var paid = !string.IsNullOrEmpty(pays);
        return oath != Element.None
            ? CodeText.Format(paid ? SwirlOathPaysRow : SwirlOathRow, vars)
            : paid ? CodeText.Format(SwirlPaysRow, vars) : body;
    }
}

/// <summary>
/// `EB-733`. A MARKER: this card's face opens with an aimed <b>Set off</b>
/// ("Set off the enemy.", the bare "Set off.", or Pocket Match's "Set off
/// only your largest Bomb on the enemy."), so the Set off takes the aura
/// before the card's own hit (<see cref="KleeCardTooltips.SetsOffFirst"/>).
/// Stamped by <c>tools/gen_klee_cards.py</c> (<c>sets_off_first</c>); declared
/// here, outside Powers/Prototype, because the tooltip reading it ships in
/// every build.
/// </summary>
public interface ISetsOffFirstCard
{
}

/// <summary>
/// Kokomi Balance suite 4 (2026-10-21). A card whose one printed hit is a
/// two-armed pair -- "Deal {PlainDamage}. If ..., deal {BranchDamage}
/// instead." -- says which arm lands if it is played now, so the reaction
/// preview (<see cref="KleeCardTooltips"/>) folds that number rather than
/// finding none. Emitted by <c>tools/gen_klee_cards.py</c>
/// (<c>branch_damage_face</c>) only where the condition is a board fact a
/// preview can read before the play; declared here because the tooltip
/// reading it ships in every build.
/// </summary>
public interface IBranchDamageFace
{
    /// <summary><c>BranchDamage</c> lands when true, <c>PlainDamage</c>
    /// otherwise.</summary>
    bool BranchDamageLive { get; }
}
