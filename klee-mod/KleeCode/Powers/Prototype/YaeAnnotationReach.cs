using System.Linq;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// A CARD WHOSE OWN PLAY PLANTS A SAKURA, AS A TYPE. The codegen puts this on
/// every row with a `yae` plant / plant_level op (Yakan Evocation, Twin
/// Sakura, Grafted Branch) and nothing else implements it: a marker with no
/// members, read by <see cref="YaeAnnotationReach.Plants"/>. Sim twin:
/// <c>yae_shrine.plants_sakura</c>, off the same ops.
/// </summary>
public interface ISakuraPlanterCard
{
}

/// <summary>
/// A card whose `yae` kind gives its own Block (block_per_sakura,
/// block_per_annotated: Print Run). It declares no BlockVar, so the game's
/// <c>GainsBlock</c> is false (Nimble is unchanged), but Red Ink rides that
/// Block: <see cref="YaeAnnotationReach.GivesBlock"/> reads this marker too.
/// Codegen-emitted; sim twin <c>yae_shrine.gives_block</c>.
/// </summary>
public interface IYaeBlockCard
{
}

/// <summary>
/// WHERE AN ANNOTATION DOES SOMETHING (ruled 2026-10-14,
/// <c>review/active/yae-design-axes-2026-10-14.md</c>). [USER]: "Hmm, let's
/// do both. Make the Sakura work, but also try to block dead edits when we
/// can."
///
/// 1. INHERITANCE (Red Ink only): Red Ink on a card that plants a Sakura
///    passes to every Sakura that play plants (a full-shrine plant that only
///    levels plants nothing), and the card's own damage and Block still take
///    the +3. Widened 2026-10-14 (main session, after a GPT design review):
///    it once passed only off a card that "only plants", so Twin Sakura+,
///    which gains Block, lost the Sakura bonus on upgrade.
/// 2. THE DEAD-EDIT FILTER: an Edit's chooser, Reborn as Guuji Yae and the
///    after-elite Publish offer skip a card the Annotation would do nothing
///    on. Red Ink needs a card that deals damage, gives Block or plants;
///    Reprint (2026-10-14) needs a card that can be played (no Unplayable).
///    Every other Annotation does something on any card.
///
/// The card facts are the engine's own, never the text: an Attack, or a
/// card declaring a damage var, deals damage (the Sharp door, widened so a
/// Skill that hits stays editable: the fail-open side); <c>GainsBlock</c>
/// (Nimble's door) gives Block; <see cref="ISakuraPlanterCard"/> plants.
/// Sim twin: <c>yae_shrine.affects</c> / <c>yae_shrine.inherits</c>.
/// </summary>
public static class YaeAnnotationReach
{
    /// <summary>Does the card deal damage? An Attack, or any card declaring
    /// a damage var.</summary>
    public static bool DealsDamage(CardModel card) =>
        card.Type == CardType.Attack
        || card.DynamicVars.Values.Any(v => v is DamageVar or CalculatedDamageVar);

    /// <summary>Does the card give Block? The game's own answer, or a
    /// <see cref="IYaeBlockCard"/>.</summary>
    public static bool GivesBlock(CardModel card) =>
        card.GainsBlock || card is IYaeBlockCard;

    /// <summary>Does the card's own play plant a Sakura?</summary>
    public static bool Plants(CardModel card) => card is ISakuraPlanterCard;

    /// <summary>Would <paramref name="annotation"/> do anything on a card
    /// with these facts? PURE.</summary>
    public static bool Affects(YaeAnnotation annotation, bool damage, bool block,
                               bool plants, bool playable = true) =>
        annotation == YaeAnnotation.Reprint
            ? playable
            : annotation != YaeAnnotation.RedInk || damage || block || plants;

    /// <summary>Can the card be played at all? An Unplayable card never is,
    /// so Reprint on it is dead.</summary>
    public static bool Playable(CardModel card) =>
        !card.Keywords.Contains(CardKeyword.Unplayable);

    /// <summary>Does <paramref name="annotation"/> on a card with these
    /// facts pass to the Sakura it plants? Red Ink on any planting card; its
    /// own damage and Block do not stop it (2026-10-14). PURE.</summary>
    public static bool Inherits(YaeAnnotation annotation, bool damage, bool block,
                                bool plants) =>
        annotation == YaeAnnotation.RedInk && plants;

    /// <summary>Would <paramref name="annotation"/> do anything on
    /// <paramref name="card"/>?</summary>
    public static bool Affects(CardModel card, YaeAnnotation annotation) =>
        annotation == YaeAnnotation.Reprint
            ? Playable(card)
            : annotation != YaeAnnotation.RedInk
              || Affects(annotation, DealsDamage(card), GivesBlock(card), Plants(card));

    /// <summary>The Annotation the Sakura this card plants inherit: Red Ink
    /// when any layer of the card carries it and it plants, else none. Once
    /// (+3), however many Red Ink layers (review r3, the builder's reading:
    /// a Sakura carries one Annotation).</summary>
    public static YaeAnnotation Inherited(CardModel card) =>
        YaeEditing.Count(card, YaeAnnotation.RedInk) > 0
        && Inherits(YaeAnnotation.RedInk, DealsDamage(card), GivesBlock(card), Plants(card))
            ? YaeAnnotation.RedInk : YaeAnnotation.None;
}
