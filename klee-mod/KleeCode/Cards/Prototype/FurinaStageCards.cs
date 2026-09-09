using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// THE STAGE'S THREE STARTER KIT CARDS, hand-written, and that is a build
/// ORDER rather than a design position.
///
/// The batch-one faces are being authored as `proto_fs_` rows on the sheet
/// (`docs/prototype-surface.yaml`, the `stage-sim` branch), and the codegen is
/// what will ship them: a hand-written row is one the sheet cannot see, one
/// the sim cannot read and one the deletion rule (R213 B) has no grip on. But
/// the MACHINERY has to be exercisable before the sheet lands -- the
/// acceptance scenario needs a summon, a Spend and a Raise it can actually
/// play -- so these three are the starter of brief sec.7, written by hand
/// under the switch, and they are replaced by their generated twins when the
/// sheet arrives.
///
/// THE THREE ARE THE THREE SEC.7 NAMES, at the numbers sec.7 plays them at:
/// <i>Salon Début</i> (summon a random performer not on stage),
/// <i>Curtain Rise</i> (Deal 7. Spend 3: deal 13 instead) and <i>Standing
/// Ovation</i> (Raise 5 Fanfare on the back performer). One Energy each, which
/// is what makes sec.7's turn-one lines add up to three cards on three Energy.
///
/// OFF-POOL, like every other quarantined row: in <c>FurinaOffPoolCards</c> so
/// <c>CardModel.Pool</c> resolves when one is drawn, out of
/// <c>GetUnlockedCards</c> so no reward roll can offer one. They reach a deck
/// through <c>FurinaStageRoster.StartingDeck</c> and through a scenario's
/// <c>give:</c>, and by no other door.
/// </summary>
internal static class FurinaStageCardArt
{
    /// <summary>The portraits are BORROWED from the shipped Salon rows whose
    /// verbs these three take over. Art is commissioned when a slice is
    /// ACCEPTED (the rule the overhaul power icons and Salon Solitaire both
    /// follow), and <c>RosterArt.CardPortrait</c> answers null on a miss, so a
    /// borrowed name degrades to the frame rather than to a crash.</summary>
    internal const string Debut = "salon_debut";

    internal const string CurtainRise = "curtain_rises";

    internal const string StandingOvation = "an_invitation";
}

/// <summary>
/// SALON DÉBUT -- "Summon a random performer that is not on stage."
///
/// THE ROLL IS THE DEFAULT sec.10 discloses (default 2, a D): the three named
/// summons are Commons in the pool, and the starter's one is the random one,
/// so a starting deck cannot choose its cast. <c>FurinaStageRules.Roll</c>
/// owns the pool ("the cast minus the stage", and the whole cast when all
/// three are up, because a summon onto a full stage is a ROTATION).
///
/// NO NUMBER ON THE FACE, deliberately: the bar it arrives at is
/// <see cref="FurinaStageLaw.SummonFanfare"/> on an open stage and the
/// LEAVER'S bar on a full one (rule 3), and a face printing "1" would be
/// false on exactly the board where rotation is the play. The Summon tip
/// carries both clauses.
/// </summary>
public sealed class StageSalonDebut : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait(FurinaStageCardArt.Debut);

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Salon Début"),
        ("description",
            "[gold]Summon[/gold] a random performer that is not on stage."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForSummon(
            ArmKeywordTips.ForFanfare(base.ExtraHoverTips, this), this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public StageSalonDebut()
        : base(1, CardType.Skill, CardRarity.Common, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var furina = Owner?.Creature;
        if (furina == null) return;
        await FurinaStageRules.Summon(furina, FurinaStageRules.Roll(furina));
    }

    /// <summary>The upgrade summons at a bigger bar rather than summoning
    /// twice: a second body is a rotation on a full stage, and an upgrade that
    /// rotated the cast for you is a downgrade on the board the card is best
    /// on. The Raise rides the same funnel Standing Ovation does, so the
    /// newcomer's seat decides where it lands.</summary>
    protected override void OnUpgrade()
    {
    }
}

/// <summary>
/// CURTAIN RISE -- "Deal 7. Spend 3: deal 13 instead."
///
/// THE WHOLE CONTESTED MECHANIC ON ONE CARD (brief sec.4). Its rider fires
/// whenever ANYBODY is on stage, however little they can pay: a 1-bar lead
/// pays its 1, the card still deals 13, and the lead leaves with a bow
/// (sec.10 default 4). On an EMPTY stage the rider cannot fire at all and the
/// card is a 7.
///
/// PREVIEW TRUTH, WHICH IS THE ONE THING THIS CARD CANNOT GET WRONG. The house
/// rule is <c>klee-mod-runtime.md</c> sec.3: a preview reads the resolution's
/// own accessor, never its own arithmetic. So the bonus lives in
/// <see cref="ModifyDamageAdditive"/> -- the Strength/Vigor idiom
/// <c>FlameDance</c> uses -- and the number the player sees on the card in
/// hand is the number that lands, because the same override feeds the preview
/// and the hit. The PREDICATE is the ledger's own "is anybody on stage",
/// which is the same question <c>FurinaStageLedger.Spend</c> answers with
/// <see cref="StageSpend.Fired"/>: the preview and the resolution cannot come
/// to disagree about whether the rider fires, because they ask one object.
/// </summary>
public sealed class StageCurtainRise : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait(FurinaStageCardArt.CurtainRise);

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Curtain Rise"),
        ("description",
            "Deal {Damage:diff()} damage. [gold]Spend[/gold] "
          + "{SpendCost}: deal {ExtraDamage} more."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForBow(
            ArmKeywordTips.ForLead(
                ArmKeywordTips.ForSpend(base.ExtraHoverTips, this), this),
            this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(7m, ValueProp.Move),
            new ExtraDamageVar(6m),
            new DynamicVar("SpendCost", 3m),
        };

    public StageCurtainRise()
        : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy,
               autoAdd: false)
    {
    }

    /// <summary>The rider, as a damage modifier so the face cannot lie. It is
    /// the CARD's own hit only (<c>cardSource != this</c> returns nothing),
    /// which is what keeps it off every other Attack in the deck.</summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (cardSource != this) return 0m;
        var furina = SparkCost.OwnerCreatureOf(this) ?? dealer;
        if (!FurinaStage.LiveFor(furina)) return 0m;
        return FurinaStageLedger.For(furina!).IsEmpty
            ? 0m
            : DynamicVars.ExtraDamage.BaseValue;
    }

    /// <summary>
    /// THE HIT FIRST, THE PAYMENT SECOND, and the order is the rule rather
    /// than a preference.
    ///
    /// The bonus is not added here at all: it rides
    /// <see cref="ModifyDamageAdditive"/>, which the damage pipeline asks
    /// during <c>DamageCmd.Attack</c> -- the same override the card's own
    /// preview asked a moment earlier, which is what makes the printed number
    /// and the delivered number one number. Its predicate is "is anybody on
    /// stage", and the Spend below can make that false, so a payment that ran
    /// FIRST would silently turn the 13 the player was reading into a 7.
    ///
    /// The bow therefore lands after the hit, which is also where it belongs:
    /// Crabaletta's 8 finishes what the card started rather than racing it,
    /// and Usher's 4 Block arrives before the enemy answers.
    /// </summary>
    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var furina = Owner?.Creature;
        if (furina == null || cardPlay.Target == null) return;
        var fired = FurinaStage.LiveFor(furina)
                    && !FurinaStageLedger.For(furina).IsEmpty;
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
        if (fired)
        {
            await FurinaStageRules.Spend(
                choiceContext, furina, DynamicVars["SpendCost"].IntValue);
        }
    }

    protected override void OnUpgrade()
    {
        // The upgrade moves the PAID number and leaves the base and the price
        // alone: the card's question is whether to spend, and an upgrade that
        // moved the base would answer it.
        DynamicVars.ExtraDamage.UpgradeValueBy(3m);
    }
}

/// <summary>
/// STANDING OVATION -- "Raise 5 Fanfare on the back performer."
///
/// THE BACK AND NOT THE LEAD (rule 5), which is the lever sec.8's second
/// failure mode names: a Refill that landed on the lead would be Block by
/// another name, topping up the buffer that is currently eating the hits. It
/// lands at the back, where it is a RESERVE that only becomes the buffer after
/// a rotation or a departure -- which is sec.5.1's "wants a Spend card on the
/// last turn" in the other direction.
///
/// WITH ONE PERFORMER ON STAGE THE BACK IS THE LEAD, and the face says
/// nothing about that because it is not an exception: the back-most performer
/// of one performer is that performer. The tip says it.
/// </summary>
public sealed class StageStandingOvation : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait(FurinaStageCardArt.StandingOvation);

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Standing Ovation"),
        ("description",
            "[gold]Raise[/gold] {Amount:diff()} [gold]Fanfare[/gold] on the "
          + "back performer."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForBackPerformer(
            ArmKeywordTips.ForRaise(
                ArmKeywordTips.ForFanfare(base.ExtraHoverTips, this), this),
            this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("Amount", FurinaStageLaw.RefillAmount),
        };

    public StageStandingOvation()
        : base(1, CardType.Skill, CardRarity.Common, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await FurinaStageRules.Raise(
            Owner?.Creature, DynamicVars["Amount"].IntValue);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["Amount"].UpgradeValueBy(2m);
    }
}
