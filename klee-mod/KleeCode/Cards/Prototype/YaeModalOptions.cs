using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// Reborn as Guuji Yae's five Annotation faces ("Choose an Annotation"),
/// carried the way <see cref="VarkaModalOptions"/> carries Change of Guard's
/// four, so the Yae pool puts them in <c>AllCardIds</c> and the grid can draw
/// them (EB-150).
/// </summary>
public static class YaeModalOptions
{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {
        ModelDb.Card<AnnotationOptionRedInk>(),
        ModelDb.Card<AnnotationOptionFootnote>(),
        ModelDb.Card<AnnotationOptionDeadline>(),
        ModelDb.Card<AnnotationOptionFoxFire>(),
        ModelDb.Card<AnnotationOptionSakuraSeal>(),
    };

    /// <summary>The five, in the Edit tip's order.</summary>
    public static readonly IReadOnlyList<YaeAnnotation> Order = new[]
    {
        YaeAnnotation.RedInk, YaeAnnotation.Footnote,
        YaeAnnotation.DeadlineExtension, YaeAnnotation.FoxFire,
        YaeAnnotation.SakuraSeal,
    };

    /// <summary>The face for <paramref name="annotation"/>, made for
    /// <paramref name="owner"/>.</summary>
    public static CardModel? FaceFor(YaeAnnotation annotation, Player owner) => annotation switch
    {
        YaeAnnotation.RedInk => ModalChoice.CreateOption<AnnotationOptionRedInk>(owner),
        YaeAnnotation.Footnote => ModalChoice.CreateOption<AnnotationOptionFootnote>(owner),
        YaeAnnotation.DeadlineExtension => ModalChoice.CreateOption<AnnotationOptionDeadline>(owner),
        YaeAnnotation.FoxFire => ModalChoice.CreateOption<AnnotationOptionFoxFire>(owner),
        YaeAnnotation.SakuraSeal => ModalChoice.CreateOption<AnnotationOptionSakuraSeal>(owner),
        _ => null,
    };

    /// <summary>The player's pick of the five, or
    /// <see cref="YaeAnnotation.None"/> with no combat to draw the grid in.
    /// </summary>
    public static async Task<YaeAnnotation> Choose(
        PlayerChoiceContext choiceContext, Player owner)
    {
        if (owner.Creature?.CombatState == null) return YaeAnnotation.None;
        var options = Order.Select(a => FaceFor(a, owner))
            .Where(c => c != null).Cast<CardModel>().ToList();
        var picked = (await CardSelectCmd.FromSimpleGrid(
            choiceContext, options, owner,
            new CardSelectorPrefs(new LocString("cards", YaeEditing.AnnotationPromptKey), 1)))
            .FirstOrDefault();
        return picked is AnnotationOption face ? face.OptionAnnotation : YaeAnnotation.None;
    }
}

/// <summary>The Annotation a Reborn face stands for.</summary>
public interface AnnotationOption
{
    YaeAnnotation OptionAnnotation { get; }
}

/// <summary>The faces' one wording: the Annotation's name and rule, off the
/// enchantment so the two cannot disagree. Placeholder art: Proofread's.
/// </summary>
internal static class AnnotationFace
{
    internal static List<(string, string)> For(YaeAnnotation annotation) => new()
    {
        ("title", YaeAnnotationText.NameEnglish(annotation)),
        ("description", YaeAnnotationText.RuleEnglish(annotation)),
    };
}

public sealed class AnnotationOptionRedInk : ModalOptionCard, AnnotationOption
{
    public YaeAnnotation OptionAnnotation => YaeAnnotation.RedInk;

    public override Texture2D? CustomPortrait => RosterArt.CardPortrait("proto_ym_proofread");

    public override List<(string, string)>? Localization => AnnotationFace.For(OptionAnnotation);
}

public sealed class AnnotationOptionFootnote : ModalOptionCard, AnnotationOption
{
    public YaeAnnotation OptionAnnotation => YaeAnnotation.Footnote;

    public override Texture2D? CustomPortrait => RosterArt.CardPortrait("proto_ym_footnote");

    public override List<(string, string)>? Localization => AnnotationFace.For(OptionAnnotation);
}

public sealed class AnnotationOptionDeadline : ModalOptionCard, AnnotationOption
{
    public YaeAnnotation OptionAnnotation => YaeAnnotation.DeadlineExtension;

    // The dedupe (2026-10-16) cut Deadline and took Cliffhanger's art; the
    // Yae block and Edit pass (2026-10-19) made Cliffhanger Kitsune Lantern,
    // which keeps the art and no longer prints the Annotation.
    public override Texture2D? CustomPortrait => RosterArt.CardPortrait("proto_ym_cliffhanger");

    public override List<(string, string)>? Localization => AnnotationFace.For(OptionAnnotation);
}

public sealed class AnnotationOptionFoxFire : ModalOptionCard, AnnotationOption
{
    public YaeAnnotation OptionAnnotation => YaeAnnotation.FoxFire;

    public override Texture2D? CustomPortrait => RosterArt.CardPortrait("proto_ym_fox_fire_draft");

    public override List<(string, string)>? Localization => AnnotationFace.For(OptionAnnotation);
}

public sealed class AnnotationOptionSakuraSeal : ModalOptionCard, AnnotationOption
{
    public YaeAnnotation OptionAnnotation => YaeAnnotation.SakuraSeal;

    public override Texture2D? CustomPortrait => RosterArt.CardPortrait("proto_ym_sakura_seal");

    public override List<(string, string)>? Localization => AnnotationFace.For(OptionAnnotation);
}
