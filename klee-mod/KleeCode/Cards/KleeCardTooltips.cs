using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
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

#if PROTOTYPE_CARDS
    /// <summary>`EB-389`. Titles the line a card grows while a rider is
    /// overriding the element it prints.
    ///
    /// INSIDE THE SWITCH, and `KeywordTitleRowTests` is why: that rule finds
    /// every `KLEEMOD-` key in the assembly by reflection and demands a
    /// registered `.title` row for it, because a key with no row renders AS
    /// the key (0.2-589, 0.2-634). The row it needs is registered beside the
    /// arm's other title rows, which are themselves behind this switch -- and
    /// an override can only exist under the arm anyway, since the rider file
    /// is <c>Compile Remove</c>d in a release build.</summary>
    public const string OverriddenElementKey = "KLEEMOD-ELEMENT_OVERRIDDEN";
#endif

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
    /// unchanged in a release build, where the whole rider file is
    /// <c>Compile Remove</c>d and no override can exist.
    /// </summary>
    public static Element AppliedElement(CardModel card, Element printed)
    {
#if PROTOTYPE_CARDS
        // `EB-94`'s door, and it is not optional here: `CardModel.Owner`'s
        // getter asserts mutability, so asking it on a CANONICAL model -- the
        // compendium, a reward shelf -- throws out of the whole `HoverTips`
        // getter and the card loses every tip it had. `TipOwner` answers null
        // there, which is also the right answer: a card nobody holds is under
        // nobody's riders and prints what it prints.
        var over = CompanionOverhaulRiders.ElementFor(
            card, TipOwner.CreatureOf(card));
        if (over != Element.None) return over;
#endif
        return printed;
    }

    /// <summary>`EB-389`'s second half: the card says WHICH element, in words,
    /// because a gem swapped under a reader who has already read the face is
    /// the same silence one step quieter.</summary>
    public static string OverriddenElementBody(Element applied) =>
        $"While the buff stands, this card's hit applies "
      + $"[gold]{applied}[/gold] instead of the element it prints.";

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
#if PROTOTYPE_CARDS
        // `EB-449`. A RETIRED METER EXPLAINS NOTHING.
        //
        // R251 retired Furina's Burst under the reframe, and this paragraph
        // went on describing it: what the meter is, that a Burst card enters
        // the hand the moment it fills, and that "energy past full is lost at
        // the cast". The r7 seat met all three on High Tide at a floor-9
        // reward with no Burst meter anywhere on the screen -- three rules
        // about a resource the arm does not have, printed on the one surface
        // a reader consults before drafting.
        //
        // `FurinaResources.StageRetiresTheShippedMeters` IS THE GATE, the
        // same one that file asks before granting, spending or displaying the
        // meter. Asking it here makes "she has no Burst meter under the arm"
        // one decision rather than four, and keeps this branch owner-scoped:
        // in co-op the other seat may be Klee, whose meter is live, and whose
        // card must keep the paragraph.
        //
        // NOT THE `Elemental Skill` KEYWORD, which is loc registered once at
        // boot and cannot be owner-branched. Its own retirement is
        // `EB-200`'s, which rides `EB-199`; this is the tip the seat read.
        if (FurinaResources.StageRetiresTheShippedMeters(
                TipOwner.CreatureOf(card)))
        {
            yield break;
        }
#endif
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
#if PROTOTYPE_CARDS
        if (applied != trigger && applied != Element.None)
        {
            yield return new HoverTip(
                new LocString(Table, OverriddenElementKey + ".title"),
                OverriddenElementBody(applied));
        }
#endif
        trigger = applied;

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
            //
            // `EB-589`: and where the card HITS and the reaction AMPLIFIES,
            // the body carries the folded number instead. Same substitution
            // mechanism, same two title keys -- Vaporize and Melt are the two
            // amplifying reactions and are exactly the pair `NoHitTitleKey`
            // already names.
            var substitute = appliesWithoutHit
                ? NoHitBody(reaction)
                : AmplifiedBody(card, reaction, enemy, aura.Element);
            yield return substitute == null
                ? HoverTipFactory.FromKeyword(keyword)
                : new HoverTip(
                    new LocString(Table, NoHitTitleKey(reaction) + ".title"),
                    substitute);
        }
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
        // Vulnerable twice. Asked by TYPE NAME rather than by type, because
        // the class lives under `Cards/Prototype/` and a release build
        // Compile-Removes it -- there it simply never matches.
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
            return $"The [gold]Set off[/gold] takes the {aura} aura first, so "
                 + $"the {mult:0.##}x is the [gold]Bomb[/gold]'s. This card's "
                 + $"own {printed} lands {own}." + UnblockedRaiserClause(dealer);
        }
        var landed = TargetAlreadyFolded(card)
            ? Capped(enemy, (int)(printed * mult))
            : SimDamagePipeline.ResolveOnTarget(enemy, printed, mult);
        return $"The triggering hit deals {mult:0.##}x damage and consumes "
             + $"the aura. Into that {aura} aura this card's {printed} lands "
             + $"{landed}." + UnblockedRaiserClause(dealer);
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
    private static string UnblockedRaiserClause(Creature? dealer) =>
        dealer?.Player?.Relics.Any(relic => relic is TheBoot) == true
            ? " [gold]The Boot[/gold] raises an unblocked hit after Block, so "
            + "it is not in that number."
            : "";

    /// <summary>
    /// `EB-733`. Does this card's printed face put <b>Set off</b> before its
    /// own damage?
    ///
    /// READ OFF THE ROW THE MOD AUTHORED, which is the one place a card's
    /// clause ORDER is written down in a form this class can ask: the play
    /// body is a compiled method, and the localized string is a table lookup a
    /// non-English host would answer differently. <c>Localization</c> is
    /// <c>CustomCardModel</c>'s own English source row -- the same one the
    /// emitter writes and `lint_text_conventions` measures.
    ///
    /// FALSE FOR EVERY CARD THAT IS NOT ONE OF OURS, and false for a row whose
    /// Set off comes AFTER its damage: there the card's own hit does meet the
    /// aura and the amplified body is right as it stands.
    ///
    /// TWO OPENINGS SINCE THE 2026-09-24 PLAYTEST: the bare "Set off." and
    /// Pocket Match's "Set off only your largest Bomb on the enemy." Both put
    /// one aimed explosion ahead of the card's own hit, so the first charge
    /// takes the aura either way.
    /// </summary>
    public static bool SetsOffFirst(CardModel card)
    {
        if (card is not CustomCardModel custom) return false;
        var rows = custom.Localization;
        if (rows == null) return false;
        foreach (var row in rows)
        {
            if (row.Item1 != "description" || row.Item2 == null) continue;
            return row.Item2.StartsWith("[gold]Set off[/gold].",
                                        System.StringComparison.Ordinal)
                || row.Item2.StartsWith("[gold]Set off[/gold] only your largest ",
                                        System.StringComparison.Ordinal);
        }
        return false;
    }

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
        foreach (var name in new[] { "CalculatedDamage", "Damage" })
        {
            if (card.DynamicVars.TryGetValue(name, out var dynamicVar))
            {
                var preview = (int)dynamicVar.PreviewValue;
                return preview > 0 ? preview : dynamicVar.IntValue;
            }
        }

        return 0;
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
    /// BY NAME AND NOT BY TYPE, which is a build fact rather than a
    /// preference: that class sits under <c>Powers/Prototype/</c> and
    /// <c>KleeCode.csproj</c> Compile-Removes the directory from a release
    /// build, so a <c>typeof</c> here would not compile there. In a release
    /// build no var can carry the name and the answer is false, which is also
    /// the truth about that build.
    /// </summary>
    private static bool TargetAlreadyFolded(CardModel card) =>
        card.DynamicVars.TryGetValue("CalculatedDamage", out var calculated)
        && calculated.GetType().Name == "FrontFoldedDamageVar";

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
