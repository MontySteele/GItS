using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Prototype;

// ======================================================================
// FURINA, THE STAGE (v2): THE PERFORMER PICKER'S FACES, and Lyney's Trick.
//
// "Cue a performer", "Move a performer to the front" and "A performer Bows
// and leaves" are the PLAYER'S choice (sec.8: "The chosen Cue is part of the
// design, not an option ... If clicking a performer is awkward, the C# uses a
// small selection panel"). A card's own target is the enemy it hits (Encore!
// deals damage AND Cues), so the performer is picked on a small panel after
// the play: one face per seat, front to back, left to right
// (<see cref="FurinaStage.ChooseSeat"/>). A face is a card only because the
// panel takes cards; it is never played and never offered, but it is a POOL
// MEMBER (`FurinaOffPoolCards`), because a card in no pool throws inside the
// screen (`EB-150`).
// ======================================================================

/// <summary>One performer's face on the picker: its name and its act.
/// </summary>
public abstract class StageSeatOption : ModalOptionCard
{
    protected StageSeatOption() : base(CardType.Skill)
    {
    }

    /// <summary>Which performer this face names.</summary>
    public abstract StagePerformer Performer { get; }

    /// <summary>The seat this face stands for on the screen that made it
    /// (front = 0). Set by the picker; never read off a canonical copy.
    /// </summary>
    public int SeatIndex { get; internal set; } = -1;

    /// <summary>The performer's card art: its Guest Star card's, or the
    /// trio's own shipped portraits.</summary>
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait(PortraitKey(Performer));

    internal static string PortraitKey(StagePerformer who) => who switch
    {
        StagePerformer.Usher => "proto_fs_leading_lady",
        StagePerformer.Chevalmarin => "surintendante_chevalmarin",
        StagePerformer.Crabaletta => "mademoiselle_crabaletta",
        _ => "proto_fs_guest_star_" + FurinaStage.Name(who),
    };

    /// <summary>The face's text: the performer's act, in its badge's words.
    /// </summary>
    protected List<(string, string)> Face => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description", StagePerformerBadge.ActText(Performer)),
    };
}

public sealed class UsherSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Usher;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevalmarinSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevalmarin;
    public List<(string, string)>? Localization => Face;
}

public sealed class CrabalettaSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Crabaletta;
    public List<(string, string)>? Localization => Face;
}

public sealed class NeuvilletteSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;
    public List<(string, string)>? Localization => Face;
}

public sealed class ClorindeSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Clorinde;
    public List<(string, string)>? Localization => Face;
}

public sealed class NaviaSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Navia;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevreuseSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;
    public List<(string, string)>? Localization => Face;
}

public sealed class WriothesleySeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;
    public List<(string, string)>? Localization => Face;
}

public sealed class SigewinneSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;
    public List<(string, string)>? Localization => Face;
}

public sealed class CharlotteSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Charlotte;
    public List<(string, string)>? Localization => Face;
}

public sealed class LynetteSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lynette;
    public List<(string, string)>? Localization => Face;
}

public sealed class LyneySeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lyney;
    public List<(string, string)>? Localization => Face;
}

public sealed class EscoffierSeatOption : StageSeatOption, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Escoffier;
    public List<(string, string)>? Localization => Face;
}

/// <summary>
/// LYNEY'S TRICK (sec.2 as sec.8 amends it): "Deal 4 Pyro damage. Retain.
/// Exhaust." A token his act adds to her hand; Retain because his act comes
/// after the hand is played, so without it the Trick would be discarded
/// unused. A member of her pool so its <c>Pool</c> lookup resolves, never
/// offered (`FurinaOffPoolCards`).
/// </summary>
public sealed class StageTrick : CustomCardModel, ILocalizationProvider, IElementalCard,
                                 ICharacterCard
{
    public string CharacterId => "furina";

    public Element Element => Element.Pyro;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_fs_guest_star_lyney");

    public List<(string, string)>? Localization => new()
    {
        ("title", "Trick"),
        ("description",
            "Deal {Damage:diff()} [gold]Pyro[/gold] damage."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain, CardKeyword.Exhaust,
                KleeKeywords.AppliesPyro };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(FurinaStageLaw.TrickDamage, ValueProp.Move),
        };

    public StageTrick()
        : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Target == null) return;
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .WithElementHitFx(this)
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
    }
}
