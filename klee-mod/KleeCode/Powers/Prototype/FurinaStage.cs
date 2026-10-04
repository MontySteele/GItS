using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards.Prototype;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>Marker: a card that summons a Salon member as its own effect (a
/// TOP-LEVEL <c>stage_summon</c>), which Escoffier's line makes free once a
/// turn. Stamped by the codegen off the row.</summary>
public interface IStageSalonSummonCard
{
}

/// <summary>Marker: a card that Cues a performer (a <c>stage_cue</c>), which
/// Lyney's line makes free once a turn. Stamped by the codegen off the row.
/// </summary>
public interface IStageCueCard
{
}

/// <summary>
/// FURINA, THE STAGE (v2, the re-founding,
/// <c>review/active/furina-refounding-2026-10-03.md</c>; the sim's reference
/// is <c>tier0/engine/furina_v2.py</c>).
///
/// THE RULES, in the paper's order (sec.1 as sec.8 amends it, sec.10's
/// sheet):
///
///   1. Three seats; performers have no bars and take no hits. At the end of
///      her turn they act front to back. Combat opens with Usher on stage.
///   2. The Salon trio carries the numbers; a Guest Star bends a rule while on
///      stage and/or has a utility act. One of each guest; a second copy Bows
///      it and it keeps its seat.
///   3. A performer that leaves acts once more, FREE, then gives 1 Fanfare.
///   4. Overflow: a summon onto a full stage Bows the front-most Salon member;
///      a Salon summon onto a stage of guests is a walk-on; a guest onto a
///      stage of guests Bows the front guest.
///   5. Fanfare is ONE number on Furina, with no cap and no fade. Cards Spend
///      it; stars pay for their acts or skip; a payment is not a Spend.
///   6. Rehearsal: +1 per stack to every damage and Block act.
///   7. Cue: the chosen performer acts now (a star pays).
///
/// THIS CLASS IS THE VERB SURFACE the generated cards, the powers, the relics
/// and the potions call. The order of acts and Bows is
/// <see cref="StageDirector"/>'s, the numbers <see cref="FurinaStageLedger"/>'s,
/// and the game half <see cref="GameStageBoard"/>'s.
/// </summary>
public static partial class FurinaStage
{
    /// <summary>Is the stage live for THIS creature? In co-op the other seat
    /// is not hers and grows no stage.</summary>
    public static bool LiveFor(Creature? creature) =>
        FurinaResources.IsFurina(creature);

    /// <summary>The trio, in the brief's order (the sheet speaks strings).
    /// </summary>
    public static readonly string[] Performers =
        { "usher", "chevalmarin", "crabaletta" };

    /// <summary>The ten guests' sheet names.</summary>
    public static readonly string[] Guests =
    {
        "neuvillette", "clorinde", "navia", "chevreuse", "wriothesley",
        "sigewinne", "charlotte", "lynette", "lyney", "escoffier",
    };

    /// <summary>A sheet name to a performer (an unknown name reads as Usher:
    /// the codegen refuses one at emit).</summary>
    public static StagePerformer Parse(string member) => member switch
    {
        "chevalmarin" => StagePerformer.Chevalmarin,
        "crabaletta" => StagePerformer.Crabaletta,
        "neuvillette" => StagePerformer.Neuvillette,
        "clorinde" => StagePerformer.Clorinde,
        "navia" => StagePerformer.Navia,
        "chevreuse" => StagePerformer.Chevreuse,
        "wriothesley" => StagePerformer.Wriothesley,
        "sigewinne" => StagePerformer.Sigewinne,
        "charlotte" => StagePerformer.Charlotte,
        "lynette" => StagePerformer.Lynette,
        "lyney" => StagePerformer.Lyney,
        "escoffier" => StagePerformer.Escoffier,
        _ => StagePerformer.Usher,
    };

    /// <summary>A performer to its sheet name.</summary>
    public static string Name(StagePerformer who) =>
        who.ToString().ToLowerInvariant();

    /// <summary>Is this performer a Guest Star? Every one after the trio.
    /// </summary>
    public static bool IsGuest(StagePerformer who) =>
        who >= StagePerformer.Neuvillette;

    /// <summary>Is this guest a star (it pays for its act)?</summary>
    public static bool IsStar(StagePerformer who) =>
        who is StagePerformer.Neuvillette or StagePerformer.Clorinde
            or StagePerformer.Lyney or StagePerformer.Escoffier
            or StagePerformer.Navia;

    // ---- reading the stage ---------------------------------------------

    public static IReadOnlyList<StageSeat> Of(Creature? owner) =>
        owner == null || !LiveFor(owner)
            ? System.Array.Empty<StageSeat>()
            : FurinaStageLedger.For(owner).Seats;

    public static StageSeat? Lead(Creature? owner) =>
        Of(owner).FirstOrDefault();

    /// <summary>Is anybody on stage? (`stage_occupied`.)</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    /// <summary>How many performers are on stage (`stage_count`).</summary>
    public static int Count(CardModel? card) => Of(card?.Owner?.Creature).Count;

    /// <summary>Her Fanfare.</summary>
    public static int FanfareOf(Creature? owner) =>
        LiveFor(owner) ? FurinaStageLedger.For(owner!).Fanfare : 0;

    /// <summary>`fanfare_gained`: Fanfare gained this turn (Ousia Surge).
    /// </summary>
    public static int GainedThisTurn(CardModel? card) =>
        card?.Owner?.Creature is { } owner && LiveFor(owner)
            ? FurinaStageLedger.For(owner).GainedThisTurn : 0;

    /// <summary>`fanfare_spent`: Fanfare her cards' Spends took this turn
    /// (Pneuma Refrain, Bring the House Down). A star's payment is not a
    /// Spend.</summary>
    public static int SpentThisTurn(CardModel? card) =>
        card?.Owner?.Creature is { } owner && LiveFor(owner)
            ? FurinaStageLedger.For(owner).SpentThisTurn : 0;

    /// <summary>`stage_spent`: what THIS play's spend-all took.</summary>
    public static int Spent(CardModel? card) =>
        card?.Owner?.Creature is { } owner && LiveFor(owner)
            ? FurinaStageLedger.For(owner).SpentThisPlay : 0;

    /// <summary>`stage_spent` as a face prints it: before the play, the
    /// Fanfare a spend-all is about to take; during it, what it took. One
    /// expression, so preview and resolution agree.</summary>
    public static int SpentOrFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : FanfareOf(card?.Owner?.Creature);
    }

    /// <summary>`stage_bows`: every Bow this combat (Da Capo).</summary>
    public static int Bows(CardModel? card) =>
        card?.Owner?.Creature is { } owner && LiveFor(owner)
            ? FurinaStageLedger.For(owner).BowsThisCombat : 0;

    /// <summary>Opening Number: the cards she finished playing this turn.
    /// </summary>
    public static int CardsPlayedThisTurn(Creature? owner) =>
        LiveFor(owner) ? FurinaStageLedger.For(owner!).CardsPlayedThisTurn : 0;

    /// <summary>How many seats her stage has: four under Sold Out.</summary>
    public static int CapacityOf(Creature? owner) =>
        owner != null && owner.Powers.OfType<SoldOutPower>().Any()
            ? FurinaStageLaw.SoldOutSeats
            : FurinaStageLaw.Seats;

    /// <summary>The Last Act: her seats with nobody in them.</summary>
    public static int EmptySeats(Creature? owner) =>
        !LiveFor(owner) ? 0
            : System.Math.Max(0, FurinaStageLedger.For(owner!).Capacity
                                 - Of(owner).Count);

    /// <summary>What her powers and relics make of the rules, read live.
    /// </summary>
    public static StageMods ModsOf(Creature owner)
    {
        int Sum<T>() where T : PowerModel =>
            (int)owner.Powers.OfType<T>().Sum(p => p.Amount);
        return new StageMods
        {
            Rehearsal = Sum<RehearsalPower>(),
            Capacity = CapacityOf(owner),
            BowDraw = Sum<ThunderousApplausePower>(),
            BowActs = Relics.CurtainCallBouquet.ActsFor(owner),
            BowBlock = Relics.StagehandsGloves.BlockFor(owner),
            FiveCentury = owner.Powers.OfType<FiveCenturyActPower>().Any(),
            CriticsDarling = Sum<CriticsDarlingPower>(),
            StarBilling = Sum<StarBillingPower>(),
            StarTurn = Sum<StarTurnPower>(),
            FullHouse = Sum<FullHousePower>(),
            SpendDiscount = Relics.FurinaStageRelics.Count<Relics.PalaisLedger>(owner)
                            * Relics.PalaisLedger.Discount,
        };
    }

    // ---- Spend (rule 5) --------------------------------------------------

    /// <summary>The price a chosen Spend N mode asks: N less Palais Ledger's
    /// discount, floored at 0. The gate and the payment read it alike.
    /// </summary>
    public static int PriceOf(Creature owner, int amount)
    {
        var off = Relics.FurinaStageRelics.Count<Relics.PalaisLedger>(owner)
                  * Relics.PalaisLedger.Discount;
        return System.Math.Max(0, amount - off);
    }

    /// <summary>Is a Spend N mode offered? Only when her Fanfare holds the
    /// price.</summary>
    public static bool CanSpend(Creature? owner, int amount) =>
        LiveFor(owner)
        && FurinaStageLedger.For(owner!).CanSpend(PriceOf(owner!, amount));

    /// <summary>The guests the end-of-turn sweep would leave unable to pay
    /// after this Spend (the chooser's warning).</summary>
    public static IReadOnlyList<StagePerformer> StrandedBySpend(
        Creature? owner, int amount)
    {
        if (!CanSpend(owner, amount) || CenterOfAttentionPower.Covers(owner))
        {
            return System.Array.Empty<StagePerformer>();
        }
        var ledger = FurinaStageLedger.For(owner!);
        var before = ForecastSweep(ledger, ledger.Fanfare);
        var after = ForecastSweep(ledger,
                                  ledger.Fanfare - PriceOf(owner!, amount));
        return after.Where(cue => cue.Skips)
            .Select(cue => cue.Who)
            .Where(who => !before.Any(b => b.Who == who && b.Skips))
            .Distinct()
            .ToList();
    }

    // ---- the director ----------------------------------------------------

    /// <summary>The rules over this Furina's stage and the live board.
    /// </summary>
    public static StageDirector Director(PlayerChoiceContext choiceContext,
                                         Creature owner) =>
        new(FurinaStageLedger.For(owner),
            new GameStageBoard(choiceContext, owner));

    private static async Task Done(Creature? owner)
    {
        if (owner == null) return;
        await FurinaStagePets.Sync(owner);
        RefreshBadges(owner);
    }

    // ---- the verbs the cards call ------------------------------------------

    /// <summary>Gain Fanfare (`stage_raise`).</summary>
    public static async Task<int> Gain(PlayerChoiceContext choiceContext,
                                       Creature? owner, int amount,
                                       string source = "")
    {
        if (!LiveFor(owner) || amount <= 0) return 0;
        var gained = await Director(choiceContext, owner!).Gain(amount, source);
        RefreshBadges(owner);
        return gained;
    }

    /// <summary>A Spend N mode's payment. Center of Attention's free Spend
    /// takes nothing (and moves nothing, so it is no Spend). Returns what was
    /// paid.</summary>
    public static async Task<int> Spend(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        if (CenterOfAttentionPower.TryClaim(owner!))
        {
            RefreshBadges(owner);
            return 0;
        }
        var paid = await Director(choiceContext, owner!)
            .Spend(PriceOf(owner!, amount));
        RefreshBadges(owner);
        return paid;
    }

    /// <summary>"Spend all your Fanfare" (`stage_spend_all`): Bravura, Let
    /// the People Rejoice. Returns what was spent.</summary>
    public static async Task<int> SpendAll(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var spent = await Director(choiceContext, owner!).SpendAll();
        RefreshBadges(owner);
        return spent;
    }

    /// <summary>A Salon summon (`stage_summon`): a named member, or
    /// <c>"random"</c> (uniform over the trio).</summary>
    public static async Task Summon(PlayerChoiceContext choiceContext,
                                    Creature? owner, string member)
    {
        if (!LiveFor(owner)) return;
        var who = member == "random" ? RollTrio(owner!) : Parse(member);
        if (member == "random")
        {
            ResolutionLedger.NoteSummon(Name(who),
                                        FurinaStageLedger.DisplayName(who));
        }
        await Director(choiceContext, owner!).SummonSalon(who);
        await Done(owner);
    }

    /// <summary>A Guest Star card (`stage_guest`): summon the guest, then
    /// gain <paramref name="fanfare"/>.</summary>
    public static async Task GuestStar(PlayerChoiceContext choiceContext,
                                       Creature? owner, string member,
                                       int fanfare = 0)
    {
        if (!LiveFor(owner)) return;
        var guestBook = Relics.GuestBook.BonusFor(owner!);
        await Director(choiceContext, owner!)
            .SummonGuest(Parse(member), fanfare, guestBook);
        await Done(owner);
    }

    /// <summary>"Cue a performer" (`stage_cue`): the player picks the
    /// performer (<see cref="ChooseSeat"/>), which acts now.</summary>
    public static async Task Cue(PlayerChoiceContext choiceContext,
                                 Player? player, int times = 1)
    {
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var index = await ChooseSeat(choiceContext, player!, SeatPick.Cue);
        await Director(choiceContext, owner!).Cue(index, times);
        await Done(owner);
    }

    /// <summary>Revolving Stage: Cue the FRONT performer.</summary>
    public static async Task CueFront(PlayerChoiceContext choiceContext,
                                      Creature? owner)
    {
        if (!Occupied(owner)) return;
        await Director(choiceContext, owner!).Cue(0);
        await Done(owner);
    }

    /// <summary>Step Forward: a chosen performer moves to the front.</summary>
    public static async Task StepForward(PlayerChoiceContext choiceContext,
                                         Player? player)
    {
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var index = await ChooseSeat(choiceContext, player!, SeatPick.Front);
        await Director(choiceContext, owner!).StepForward(index);
        await Done(owner);
    }

    /// <summary>Final Bow, Intermission: a chosen performer Bows and leaves.
    /// </summary>
    public static async Task FinalBow(PlayerChoiceContext choiceContext,
                                      Player? player)
    {
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var index = await ChooseSeat(choiceContext, player!, SeatPick.Bow);
        await Director(choiceContext, owner!).FinalBow(index);
        await Done(owner);
    }

    /// <summary>Tutti! (every performer acts), Endless Waltz
    /// (<paramref name="guestsOnly"/>: each guest acts), Encore Elixir
    /// (<paramref name="times"/> 2).</summary>
    public static async Task PerformAll(PlayerChoiceContext choiceContext,
                                        Creature? owner, bool guestsOnly = false,
                                        int times = 1)
    {
        if (!LiveFor(owner)) return;
        await Director(choiceContext, owner!).PerformAll(guestsOnly, times);
        await Done(owner);
    }

    /// <summary>Grand Finale: every performer Bows without leaving.</summary>
    public static async Task GrandFinale(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        if (!LiveFor(owner)) return;
        await Director(choiceContext, owner!).BowAll();
        await Done(owner);
    }

    /// <summary>Let the People Rejoice's "Your performers Bow and return":
    /// the same Bows, each keeping its seat.</summary>
    public static Task CurtainCall(PlayerChoiceContext choiceContext,
                                   Creature? owner) =>
        GrandFinale(choiceContext, owner);

    /// <summary>Oratrice's Verdict: this turn every random pick a performer
    /// makes is <paramref name="target"/>, while it lives.</summary>
    public static void SetVerdict(Creature? owner, Creature? target)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).VerdictTarget = target;
        RefreshBadges(owner);
    }

    /// <summary>Dual Nature: Ousia or Pneuma for this turn, once.</summary>
    public static async Task DualNature(PlayerChoiceContext choiceContext,
                                        Player? player)
    {
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var pneuma = await ArkheAlignmentPower.Ask(choiceContext, player!);
        await ArkheAlignmentPower.Choose(choiceContext, owner!, pneuma, 1);
        RefreshBadges(owner);
    }

    /// <summary>
    /// <i>Casting Agent</i>: "Choose 1 of 3 random Guest Star cards and add
    /// it to your hand. It costs 0 this turn [and is upgraded]." Three
    /// different cards off the shared <c>CombatTargets</c> stream; a full hand
    /// takes nothing.
    /// </summary>
    public static async Task CastingAgent(PlayerChoiceContext choiceContext,
                                          CardModel card)
    {
        var player = card.Owner;
        var owner = player?.Creature;
        if (!LiveFor(owner)) return;
        var combat = owner!.CombatState;
        if (combat == null || player == null) return;
        if (CardPile.Get(PileType.Hand, player) is { } hand
            && hand.Cards.Count >= KokomiPoolCompletion.MaxHandSize)
        {
            return;
        }
        var remaining = FurinaStageRoster.GuestStarCards().ToList();
        var rng = player.RunState?.Rng?.CombatTargets;
        var options = new List<CardModel>();
        while (options.Count < FurinaStageLaw.CastingAgentOffer
               && remaining.Count > 0)
        {
            var pick = rng != null ? rng.NextItem(remaining) : remaining[0];
            if (pick == null) break;
            remaining.Remove(pick);
            options.Add(combat.CreateCard(pick, player));
        }
        if (options.Count == 0) return;
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, player, canSkip: false);
        if (selected == null) return;
        if (card.IsUpgraded && !selected.IsUpgraded) selected.UpgradeInternal();
        selected.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(selected, PileType.Hand,
                                                    player);
    }

    /// <summary>
    /// THE CO-OP SET, <i>Share the Spotlight</i>: "Spend all your Fanfare.
    /// Another player gains 2 Block per point." The Spend first (Clorinde's
    /// line answers it), then the ally's Block, the card's own
    /// (<c>ValueProp.Move</c>). Returns what was spent.
    /// </summary>
    public static async Task<int> ShareTheSpotlight(
        PlayerChoiceContext choiceContext, Creature? owner, Creature? ally,
        int perPoint, CardPlay? cardPlay)
    {
        if (!LiveFor(owner)) return 0;
        var spent = await Director(choiceContext, owner!).SpendAll();
        if (ally is { IsAlive: true } && spent > 0 && perPoint > 0)
        {
            await CreatureCmd.GainBlock(
                ally, spent * perPoint, ValueProp.Move, cardPlay);
        }
        RefreshBadges(owner);
        return spent;
    }

    /// <summary>
    /// THE CO-OP SET, <i>Raise a Toast</i>'s Spend 4 mode: "another player
    /// gains 4 temporary Strength" (6 upgraded). The base game's Coordinate
    /// shape (<see cref="RaiseAToastPower"/>). Returns what was given.
    /// </summary>
    public static async Task<int> RaiseAToast(
        PlayerChoiceContext choiceContext, Creature? owner, Creature? ally,
        int amount, CardModel? cardSource)
    {
        if (!LiveFor(owner) || amount <= 0 || ally is not { IsAlive: true })
        {
            return 0;
        }
        await PowerCmd.Apply<RaiseAToastPower>(
            choiceContext, ally, amount, applier: owner, cardSource: cardSource);
        return amount;
    }

    /// <summary>Tide of Applause, called from <c>ReactionEffects.Resolve</c>
    /// with the reaction's dealer: each copy's amount, gained.</summary>
    internal static async Task OnReaction(PlayerChoiceContext choiceContext,
                                          Creature? dealer)
    {
        if (!LiveFor(dealer)) return;
        var amount = (int)dealer!.Powers.OfType<TideOfApplausePower>()
            .Sum(p => p.Amount);
        if (amount <= 0) return;
        using (FurinaStageLedger.For(dealer).CausedBy(TideOfApplauseTitle))
        {
            await Gain(choiceContext, dealer, amount, TideOfApplauseTitle);
        }
    }

    // ---- the performer picker (rule 7: the player chooses) ----------------

    /// <summary>What the picker is choosing a performer for.</summary>
    public enum SeatPick
    {
        Cue,
        Front,
        Bow,
    }

    public const string CuePromptKey =
        "KLEEMOD-STAGE_PICK_CUE.selectionScreenPrompt";

    public const string CuePromptText = "Choose a performer to Cue.";

    public const string FrontPromptKey =
        "KLEEMOD-STAGE_PICK_FRONT.selectionScreenPrompt";

    public const string FrontPromptText =
        "Choose a performer to move to the front.";

    public const string BowPromptKey =
        "KLEEMOD-STAGE_PICK_BOW.selectionScreenPrompt";

    public const string BowPromptText =
        "Choose a performer to Bow and leave.";

    /// <summary>Test seam: a headless pin answers the picker with a seat
    /// index. Null in the game.</summary>
    public static System.Func<IReadOnlyList<StageSeat>, SeatPick, int?>?
        PickOverride { get; set; }

    /// <summary>
    /// THE PERFORMER PICKER (sec.8: "The chosen Cue is part of the design ...
    /// If clicking a performer is awkward, the C# uses a small selection
    /// panel"). A card's own target is the enemy it hits, so the performer is
    /// picked on a panel: one face per seat, front to back, left to right,
    /// each naming the performer and its act (<see cref="StageSeatOption"/>).
    /// The game's grid screen (Treasure Map's), which takes any count and
    /// syncs co-op by index. No question with one performer, and none on an
    /// empty stage (null).
    /// </summary>
    public static async Task<int?> ChooseSeat(PlayerChoiceContext choiceContext,
                                              Player player, SeatPick pick)
    {
        var owner = player.Creature;
        var seats = Of(owner);
        if (seats.Count == 0) return null;
        if (PickOverride is { } scripted) return scripted(seats, pick);
        if (seats.Count == 1) return 0;
        var combat = owner?.CombatState;
        if (combat == null) return 0;
        var options = new List<CardModel>();
        for (var i = 0; i < seats.Count; i++)
        {
            if (combat.CreateCard(OptionFor(seats[i].Who), player)
                is not StageSeatOption face)
            {
                continue;
            }
            face.SeatIndex = i;
            options.Add(face);
        }
        if (options.Count == 0) return 0;
        var key = pick switch
        {
            SeatPick.Front => FrontPromptKey,
            SeatPick.Bow => BowPromptKey,
            _ => CuePromptKey,
        };
        var chosen = (await CardSelectCmd.FromSimpleGrid(
            choiceContext, options, player,
            new CardSelectorPrefs(new LocString("cards", key), 1)))
            .FirstOrDefault();
        return chosen is StageSeatOption picked && picked.SeatIndex >= 0
            ? picked.SeatIndex : 0;
    }

    /// <summary>The canonical picker face for a performer.</summary>
    public static CardModel OptionFor(StagePerformer who) => who switch
    {
        StagePerformer.Chevalmarin => ModelDb.Card<ChevalmarinSeatOption>(),
        StagePerformer.Crabaletta => ModelDb.Card<CrabalettaSeatOption>(),
        StagePerformer.Neuvillette => ModelDb.Card<NeuvilletteSeatOption>(),
        StagePerformer.Clorinde => ModelDb.Card<ClorindeSeatOption>(),
        StagePerformer.Navia => ModelDb.Card<NaviaSeatOption>(),
        StagePerformer.Chevreuse => ModelDb.Card<ChevreuseSeatOption>(),
        StagePerformer.Wriothesley => ModelDb.Card<WriothesleySeatOption>(),
        StagePerformer.Sigewinne => ModelDb.Card<SigewinneSeatOption>(),
        StagePerformer.Charlotte => ModelDb.Card<CharlotteSeatOption>(),
        StagePerformer.Lynette => ModelDb.Card<LynetteSeatOption>(),
        StagePerformer.Lyney => ModelDb.Card<LyneySeatOption>(),
        StagePerformer.Escoffier => ModelDb.Card<EscoffierSeatOption>(),
        _ => ModelDb.Card<UsherSeatOption>(),
    };

    /// <summary>Every picker face, for the pool membership
    /// (<c>FurinaOffPoolCards</c>).</summary>
    public static IEnumerable<CardModel> AllOptions() =>
        System.Enum.GetValues<StagePerformer>().Select(OptionFor);

    // ---- the clocks ---------------------------------------------------------

    /// <summary>Rule 1: Salon Solitaire (and The Curtain Never Falls) open the
    /// combat with Usher on stage. Idempotent.</summary>
    public static async Task OpenCombat(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        await InstallBadge(owner);
        if (!FurinaStageLedger.For(owner!).Open()) return;
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageCues.CurtainUp(owner);
        RefreshBadges(owner);
    }

    /// <summary>The top of her turn, before the draw: the flow counts and the
    /// once-a-turn latches reset (sec.8).</summary>
    public static void OpenTurn(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).OpenTurn();
        RefreshBadges(owner);
    }

    public const string SeasonTicketsTitle = "Season Tickets";
    public const string RevolvingStageTitle = "Revolving Stage";
    public const string TideOfApplauseTitle = "Tide of Applause";
    public const string PremiereSeasonTitle = "Premiere Season";
    public const string AllTheWorldsAStageTitle = "All the World's a Stage";

    /// <summary>
    /// After her draw: Charlotte's extra card, then the turn-start powers --
    /// One-Woman Show, Premiere Season's Rehearsal, Grand Theater Program's
    /// and Season Tickets' Fanfare, Regina's Hydro, and Revolving Stage's Cue
    /// last -- the sim arm's order (`furina_stage.turn_start`).
    /// </summary>
    public static async Task TurnStart(PlayerChoiceContext choiceContext,
                                       Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var furina = owner!;
        var ledger = FurinaStageLedger.For(furina);
        if (ledger.OnStage(StagePerformer.Charlotte)
            && furina.Player is { } drawer)
        {
            await CardPileCmd.Draw(choiceContext, FurinaStageLaw.CharlotteExtra,
                                   drawer);
        }
        var show = (int)furina.Powers.OfType<OneWomanShowPower>()
            .Sum(p => p.Amount);
        if (show > 0 && !Occupied(furina) && furina.Player is { } player)
        {
            await PlayerCmd.GainEnergy(show, player);
            await CardPileCmd.Draw(choiceContext, 2 * show, player);
        }
        var premiere = (int)furina.Powers.OfType<PremiereSeasonPower>()
            .Sum(p => p.Amount);
        if (premiere > 0)
        {
            await PowerCmd.Apply<RehearsalPower>(choiceContext, furina,
                                                 premiere, applier: furina,
                                                 cardSource: null);
        }
        var program = Relics.FurinaStageRelics
            .Count<Relics.GrandTheaterProgram>(furina)
            * Relics.GrandTheaterProgram.Fanfare;
        if (program > 0)
        {
            Relics.FurinaStageRelics.Flash<Relics.GrandTheaterProgram>(furina);
            using (ledger.CausedBy("Grand Theater Program"))
            {
                await Gain(choiceContext, furina, program, "Grand Theater Program");
            }
        }
        var tickets = (int)furina.Powers.OfType<SeasonTicketsPower>()
            .Sum(p => p.Amount);
        if (tickets > 0)
        {
            using (ledger.CausedBy(SeasonTicketsTitle))
            {
                await Gain(choiceContext, furina, tickets, SeasonTicketsTitle);
            }
        }
        if (furina.Powers.OfType<ReginaOfAllWatersPower>().Any())
        {
            foreach (var enemy in Enemies(furina).ToList())
            {
                if (furina.IsDead || CombatOver()) break;
                await ElementalHit.ApplyOnly(choiceContext, enemy,
                                             Element.Hydro, furina);
            }
        }
        var turns = (int)furina.Powers.OfType<RevolvingStagePower>()
            .Sum(p => p.Amount);
        using (ledger.CausedBy(RevolvingStageTitle))
        {
            for (var i = 0; i < turns; i++)
            {
                if (furina.IsDead || CombatOver()) break;
                await CueFront(choiceContext, furina);
            }
        }
        RefreshBadges(furina);
    }

    /// <summary>Rule 1: the end of her turn. Every performer acts, front to
    /// back; then this turn's Ousia and Verdict are spent.</summary>
    public static async Task EndOfTurnActs(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return;
        await Director(choiceContext, owner!).EndOfTurn();
        FurinaStageLedger.For(owner!).CloseTurn();
        await Done(owner);
    }

    /// <summary>A card play opens: a fresh per-play spend record.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).BeginPlay();
    }

    /// <summary>A card play closed: the counts Opening Number, Escoffier's
    /// and Lyney's lines read.</summary>
    public static void NoteCardPlayed(Creature? owner, CardModel? card)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        ledger.CardsPlayedThisTurn++;
        if (card is IStageSalonSummonCard) ledger.SalonSummonCardsThisTurn++;
        if (card is IStageCueCard) ledger.CueCardsThisTurn++;
        RefreshBadges(owner);
    }

    /// <summary>Escoffier's and Lyney's lines: is this card free to play now?
    /// PURE.</summary>
    public static bool PlaysFree(Creature? owner, CardModel card)
    {
        if (!LiveFor(owner)) return false;
        var ledger = FurinaStageLedger.For(owner!);
        if (card is IStageSalonSummonCard
            && ledger.OnStage(StagePerformer.Escoffier)
            && ledger.SalonSummonCardsThisTurn == 0)
        {
            return true;
        }
        return card is IStageCueCard
               && ledger.OnStage(StagePerformer.Lyney)
               && ledger.CueCardsThisTurn == 0;
    }

    /// <summary>Sigewinne's reading: Furina lost HP.</summary>
    public static void NoteHpLoss(Creature? owner)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).NoteHpLoss();
    }

    /// <summary>Wriothesley's reading: her Block stopped this much.</summary>
    public static void NoteBlocked(Creature? owner, int blocked)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).NoteBlocked(blocked);
    }

    /// <summary>Neuvillette's line on her CARDS: "Your Hydro damage deals 2
    /// more", per hit, while he is on stage. (His own act adds it in the
    /// director.) PURE.</summary>
    public static int HydroBonus(Creature? dealer, CardModel? cardSource)
    {
        if (cardSource == null || !LiveFor(dealer)) return 0;
        if (!FurinaStageLedger.For(dealer!).OnStage(StagePerformer.Neuvillette))
        {
            return 0;
        }
        return CatalystCadence.PrintedElement(cardSource, dealer) == Element.Hydro
            ? FurinaStageLaw.NeuvilletteHydroBonus : 0;
    }

    // ---- the badge ----------------------------------------------------------

    /// <summary>Her Fanfare badge (<see cref="FanfarePower"/>), installed at
    /// combat open and asked again every turn start. Idempotent.</summary>
    public static async Task InstallBadge(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        if (owner!.Powers.OfType<FanfarePower>().Any()) return;
        await PowerCmd.Apply<FanfarePower>(
            new ThrowingPlayerChoiceContext(), owner, 1,
            applier: owner, cardSource: null, silent: true);
    }

    /// <summary>Redraw the Fanfare badge's numbers, the Fanfare gauge
    /// (<see cref="Vfx.FanfareCounter"/>) and the cues.</summary>
    public static void RefreshBadges(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        foreach (var badge in owner!.Powers.OfType<FanfarePower>().ToList())
        {
            badge.Refresh();
        }
        Vfx.FanfareCounter.Refresh(owner);
        Vfx.FurinaStageCues.Refresh(owner);
    }

    // ---- the board's helpers ------------------------------------------------

    internal static bool CombatOver() =>
        MegaCrit.Sts2.Core.Combat.CombatManager.Instance.IsOverOrEnding;

    internal static IEnumerable<Creature> Enemies(Creature owner) =>
        owner.CombatState?.HittableEnemies.ToList()
        ?? Enumerable.Empty<Creature>();

    /// <summary>A uniform roll over the trio (they can be cloned).</summary>
    private static StagePerformer RollTrio(Creature owner)
    {
        var trio = Performers.Select(Parse).ToList();
        var roll = owner.Player?.RunState.Rng.CombatTargets;
        return roll != null ? roll.NextItem(trio) : trio[0];
    }

    /// <summary>Who an act that "hits a random enemy" hits: Oratrice's
    /// Verdict's enemy this turn while it lives and is in
    /// <paramref name="pool"/>, else a random one.</summary>
    public static Creature? ActTarget(Creature owner, IReadOnlyList<Creature> pool)
    {
        if (pool.Count == 0) return null;
        var verdict = FurinaStageLedger.For(owner).VerdictTarget;
        if (verdict is { IsAlive: true } && pool.Contains(verdict)) return verdict;
        var rng = owner.Player?.RunState?.Rng?.CombatTargets;
        return rng == null ? pool[0] : rng.NextItem(pool);
    }

    // ---- the forecast (what the end of this turn will do) ------------------

    /// <summary>The end of this turn, forecast off the ledger's numbers:
    /// each performer's act, in seat order, with what it costs and whether a
    /// star will skip, her Fanfare after the sweep and the Block it gives.
    /// Null with the arm off. PURE.</summary>
    public static StageForecast? Forecast(Creature? owner)
    {
        if (!LiveFor(owner)) return null;
        var ledger = FurinaStageLedger.For(owner!);
        var run = new ForecastRun(ledger, ledger.Fanfare);
        var cues = run.Sweep();
        return new StageForecast(cues, run.Fanfare, run.Block);
    }

    /// <summary>The forecast against a given stage (the pins').</summary>
    public static StageForecast Forecast(FurinaStageLedger ledger)
    {
        var run = new ForecastRun(ledger, ledger.Fanfare);
        var cues = run.Sweep();
        return new StageForecast(cues, run.Fanfare, run.Block);
    }

    private static IReadOnlyList<StageForecastCue> ForecastSweep(
        FurinaStageLedger ledger, int fanfare) =>
        new ForecastRun(ledger, fanfare).Sweep();

    private sealed class ForecastRun
    {
        private readonly FurinaStageLedger _stage;
        private bool _chevreuse;

        internal int Fanfare;
        internal int Block;

        internal ForecastRun(FurinaStageLedger stage, int fanfare)
        {
            _stage = stage;
            Fanfare = fanfare;
            _chevreuse = stage.ChevreuseActedThisTurn;
        }

        internal IReadOnlyList<StageForecastCue> Sweep()
        {
            var times = 1 + (_stage.IsFull ? _stage.Mods.FullHouse : 0);
            var cues = new List<StageForecastCue>();
            foreach (var seat in _stage.Seats)
            {
                StageForecastCue? first = null;
                var landed = 0;
                for (var i = 0; i < times; i++)
                {
                    var cue = Act(seat);
                    first ??= cue;
                    if (!cue.Skips) landed++;
                }
                cues.Add(first!.Value with
                {
                    Times = landed,
                    Skips = landed == 0,
                });
            }
            return cues;
        }

        private StageForecastCue Act(StageSeat seat)
        {
            var who = seat.Who;
            var price = FurinaStageLaw.PriceOf(who);
            var r = _stage.Rehearsal;
            var mult = System.Math.Max(1, _stage.ActDamageMultiplier);
            int Dmg(int printed) => (printed + r) * mult;
            StageForecastCue Cue(StageCueKind kind, int amount,
                                 string element = "", string target = "") =>
                new(who, seat.Key, kind, amount, element, target, 1, price,
                    false);
            var skip = Cue(StageForecast.KindOf(who), 0) with { Skips = true };
            if (who == StagePerformer.Chevreuse)
            {
                if (_chevreuse || Fanfare < price) return skip;
                _chevreuse = true;
                Fanfare -= price;
                return Cue(StageCueKind.Energy, FurinaStageLaw.ActChevreuseEnergy);
            }
            if (price > 0)
            {
                if (Fanfare < price) return skip;
                Fanfare -= price;
            }
            switch (who)
            {
                case StagePerformer.Usher:
                {
                    var block = FurinaStageLaw.ActUsherBlock + r;
                    Block += block;
                    return Cue(StageCueKind.Block, block);
                }
                case StagePerformer.Chevalmarin:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.ActChevalmarinDamage), "",
                               StageForecastCue.All);
                case StagePerformer.Crabaletta:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.ActCrabalettaDamage), "",
                               StageForecastCue.Random);
                case StagePerformer.Neuvillette:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.ActNeuvilletteDamage)
                               + FurinaStageLaw.NeuvilletteHydroBonus,
                               "Hydro", StageForecastCue.All);
                case StagePerformer.Clorinde:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.ActClorindeDamage), "Electro",
                               StageForecastCue.Random);
                case StagePerformer.Lyney:
                    return Cue(StageCueKind.Card, 1);
                case StagePerformer.Escoffier:
                    foreach (var salon in _stage.Seats
                                 .Where(s => !IsGuest(s.Who)).ToList())
                    {
                        Act(salon);
                    }
                    return Cue(StageCueKind.Ensemble, 0);
                case StagePerformer.Navia:
                {
                    var printed = FurinaStageLaw.NaviaPerSpent
                                  * _stage.SpentThisTurn;
                    return Cue(StageCueKind.Damage,
                               printed > 0 ? Dmg(printed) : 0, "Geo",
                               StageForecastCue.Random);
                }
                case StagePerformer.Charlotte:
                    Fanfare += FurinaStageLaw.ActCharlotteGain;
                    return Cue(StageCueKind.Fanfare,
                               FurinaStageLaw.ActCharlotteGain);
                case StagePerformer.Lynette:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.ActLynetteDamage), "Anemo",
                               StageForecastCue.Aura);
                case StagePerformer.Sigewinne:
                {
                    var block = FurinaStageLaw.SigewinneBlock(
                        _stage.HpLossesSince(who)) + r;
                    Block += block;
                    return Cue(StageCueKind.Block, block);
                }
                case StagePerformer.Wriothesley:
                    return Cue(StageCueKind.Damage,
                               Dmg(FurinaStageLaw.WriothesleyDamage(
                                   _stage.BlockedSince(who))), "Cryo",
                               StageForecastCue.Random);
                default:
                    return Cue(StageCueKind.Damage, 0);
            }
        }
    }
}

/// <summary>What a performer's act is, as its cue draws it.</summary>
public enum StageCueKind
{
    /// <summary>Usher, Sigewinne: Block for Furina.</summary>
    Block,

    /// <summary>Every damage act.</summary>
    Damage,

    /// <summary>Chevreuse: Energy next turn.</summary>
    Energy,

    /// <summary>Charlotte: Fanfare for Furina.</summary>
    Fanfare,

    /// <summary>Lyney: a Trick into her hand.</summary>
    Card,

    /// <summary>Escoffier: the Salon members act.</summary>
    Ensemble,
}

/// <summary>
/// ONE PERFORMER'S CUE: what it will do at the end of this turn.
/// <see cref="Amount"/> is one act's number; <see cref="Times"/> how many of
/// its acts land; <see cref="Price"/> what each costs; <see cref="Skips"/> a
/// star (or Chevreuse) that cannot pay and does nothing.
/// </summary>
public readonly record struct StageForecastCue(
    StagePerformer Who, int Key, StageCueKind Kind, int Amount,
    string Element, string Target, int Times, int Price, bool Skips)
{
    public const string All = "all";
    public const string Random = "random";
    public const string Aura = "random_aura";
}

/// <summary>The whole forecast: one cue per performer in seat order, her
/// Fanfare after the sweep, and the Block the acts give.</summary>
public sealed record StageForecast(
    IReadOnlyList<StageForecastCue> Cues, int FanfareAfter, int Block)
{
    /// <summary>The kind of act a performer has.</summary>
    public static StageCueKind KindOf(StagePerformer who) => who switch
    {
        StagePerformer.Usher or StagePerformer.Sigewinne => StageCueKind.Block,
        StagePerformer.Chevreuse => StageCueKind.Energy,
        StagePerformer.Charlotte => StageCueKind.Fanfare,
        StagePerformer.Lyney => StageCueKind.Card,
        StagePerformer.Escoffier => StageCueKind.Ensemble,
        _ => StageCueKind.Damage,
    };
}

/// <summary>
/// THE BOARD HALF, IN THE GAME: every act's and line's command, on the live
/// combat. Acts are unpowered (her Strength and Weak stay out of them,
/// `EB-495` D3); a guest's act carries its element through
/// <see cref="ElementalHit.Deal"/>, so it applies its aura and reacts; the
/// trio's acts carry none.
/// </summary>
public sealed class GameStageBoard : IStageBoard
{
    private readonly PlayerChoiceContext _context;
    private readonly Creature _owner;

    public GameStageBoard(PlayerChoiceContext context, Creature owner)
    {
        _context = context;
        _owner = owner;
    }

    public bool Over => _owner.IsDead || FurinaStage.CombatOver();

    public async Task Block(StagePerformer who, int amount)
    {
        if (amount <= 0) return;
        await CreatureCmd.GainBlock(_owner, amount, ValueProp.Unpowered, null,
                                    fast: true);
    }

    public async Task Damage(StagePerformer who, StageTarget target,
                             int amount, Element element)
    {
        if (amount <= 0) return;
        using var credit = Diagnostics.DamageCredit.Open(
            _owner, Diagnostics.DamageCredit.Pet, who.ToString());
        var enemies = FurinaStage.Enemies(_owner).ToList();
        if (enemies.Count == 0) return;
        if (target == StageTarget.All)
        {
            foreach (var enemy in enemies)
            {
                if (Over) return;
                await Hit(enemy, amount, element);
            }
            return;
        }
        var pool = enemies;
        if (target == StageTarget.Aura)
        {
            var wearing = enemies.Where(e => AuraCmd.Find(e) != null).ToList();
            if (wearing.Count > 0) pool = wearing;
        }
        if (FurinaStage.ActTarget(_owner, pool) is { } body)
        {
            await Hit(body, amount, element);
        }
    }

    private Task<int> Hit(Creature enemy, int amount, Element element) =>
        element == Element.None
            ? ElementalHit.DealUnelemented(_context, enemy, amount, _owner,
                                           powered: false)
            : ElementalHit.Deal(_context, enemy, element, amount, _owner,
                                powered: false);

    public async Task AddTrick()
    {
        if (_owner.Player is not { } player || _owner.CombatState is not { } combat)
        {
            return;
        }
        var trick = combat.CreateCard(ModelDb.Card<StageTrick>(), player);
        if (trick == null) return;
        var full = CardPile.Get(PileType.Hand, player) is { } hand
                   && hand.Cards.Count >= KokomiPoolCompletion.MaxHandSize;
        await CardPileCmd.AddGeneratedCardToCombat(
            trick, full ? PileType.Discard : PileType.Hand, player);
    }

    public async Task EnergyNextTurn(int amount)
    {
        if (amount <= 0) return;
        await PowerCmd.Apply<EnergyNextTurnPower>(
            _context, _owner, amount, applier: _owner, cardSource: null);
    }

    public async Task Draw(int amount)
    {
        if (amount <= 0 || _owner.Player is not { } player) return;
        await CardPileCmd.Draw(_context, amount, player);
    }

    public async Task ClorindeLine(int amount)
    {
        var enemies = FurinaStage.Enemies(_owner).ToList();
        if (FurinaStage.ActTarget(_owner, enemies) is not { } body) return;
        using var credit = Diagnostics.DamageCredit.Open(
            _owner, Diagnostics.DamageCredit.Pet,
            StagePerformer.Clorinde.ToString());
        await ElementalHit.Deal(_context, body, Element.Electro, amount, _owner,
                                powered: false);
    }

    public async Task CriticsHit(int amount)
    {
        var enemies = FurinaStage.Enemies(_owner).ToList();
        if (enemies.Count == 0 || amount <= 0) return;
        var rng = _owner.Player?.RunState?.Rng?.CombatTargets;
        var body = rng == null ? enemies[0] : rng.NextItem(enemies);
        if (body == null) return;
        await ElementalHit.DealUnelemented(_context, body, amount, _owner,
                                           powered: false);
    }

    public async Task GlovesBlock(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return;
        Relics.FurinaStageRelics.Flash<Relics.StagehandsGloves>(_owner);
        await CreatureCmd.GainBlock(_owner, amount, ValueProp.Unpowered, null,
                                    fast: true);
        RelicAnswerLog.NoteGain("Stagehand's Gloves", amount, "Block");
    }

    public Task Lunge(StageSeat? seat) =>
        Vfx.StagePerformerBeat.Act(seat?.Pet);

    public async Task Sync()
    {
        await FurinaStagePets.Sync(_owner);
        Vfx.FanfareCounter.Refresh(_owner);
        Vfx.FurinaStageCues.Refresh(_owner);
    }
}

/// <summary>
/// THE CAST: the Salon trio, then the ten Guest Stars. A performer is a pet
/// body with no bar; every rule about it is the ledger's.
/// </summary>
public enum StagePerformer
{
    Usher,
    Chevalmarin,
    Crabaletta,

    // The Guest Stars (everything after the trio is a guest: `IsGuest`).
    Neuvillette,
    Clorinde,
    Navia,
    Chevreuse,
    Wriothesley,
    Sigewinne,
    Charlotte,
    Lynette,
    Lyney,
    Escoffier,
}
