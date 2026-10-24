using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE SALON'S TAB (2026-10-05,
/// <c>review/active/furina-research-proposal-2026-10-05.md</c> sec.2, sec.16
/// and sec.17; the sim twin is <c>tier0/engine/furina_tide.py</c>, run for
/// her arm by <c>tier0/engine/furina_stage.py</c>).
///
/// THE RULES:
///
///   1. DRAIN N: lose N HP for the bigger effect -- a mode on a two-mode card
///      (the Spend chooser), or a fixed price on a card that cannot be played
///      when it cannot be paid. The line is the HP she started this combat
///      with, minus 1/4 of her Max HP (2026-10-09); a Drain may go past it,
///      but never to 0 HP.
///      HP lost to a Drain is drained, in two parts: above the line and
///      past it.
///   2. REPAY N: regain up to N of her drained HP, never more; the
///      past-line part first. The Repay floor (2026-10-09): some Repays pay
///      Block, Vigor or damage for the part of N they could not return.
///   3. FANFARE: one number on Furina, no cap, no fade. +1 for every HP she
///      loses (a Drain, a hit past Block, anything) and +1 for every HP she
///      Repays. Spend N and the spend-all cards pay it.
///   4. SALON SOLITAIRE, her starting relic: "At the end of your turn, Repay
///      1." (Upgraded: 2. <see cref="FurinaStageLaw.SingerRepay"/>.)
///   5. GUEST STARS (the pool to 75's rule,
///      <c>review/ruled/furina-pool-growth-2026-10-09.md</c> sec.3): three
///      seats, guests only. A Guest Star exhausts when played and has no
///      effect on summon; a guest has a line while on stage and acts at the
///      end of her turn, oldest first. A fourth makes the oldest leave, and
///      a guest that leaves (evicted, or sent off by Final Bow) sends its
///      card to the discard pile. A second copy of one on stage moves it to
///      the newest seat and acts once (2026-10-11).
///   6. THE CURTAIN CALL: when the combat ends, the HP drained above the
///      line returns; the HP drained past it stays lost (A Five-Century Act
///      returns it too).
///
/// THIS CLASS IS THE VERB SURFACE the generated cards, the powers, the relics
/// and the potions call. The order of things is
/// <see cref="StageDirector"/>'s, the numbers <see cref="FurinaStageLedger"/>'s,
/// and the game half <see cref="GameStageBoard"/>'s.
/// </summary>
public static class FurinaStage
{
    /// <summary>
    /// Is the Stage UP for THIS creature: its clocks run (the guests' acts,
    /// the turn's counts, the curtain call), HP lost prints Fanfare, and its
    /// gauges may draw? Furina's is up from the start of every combat;
    /// anyone else's from their first Stage verb or Furina card this combat
    /// (<see cref="Ensure"/>; the off-character fix, 2026-10-18). This is
    /// the base game's Orbs and Osty shape: the Defect's first Channel
    /// grants a slot to a character with none, and Osty is summoned if
    /// absent. In co-op each seat's Stage is its own.
    /// </summary>
    public static bool LiveFor(Creature? creature) =>
        FurinaResources.IsFurina(creature)
        || (creature?.Player != null && FurinaStageLedger.HasOpened(creature));

    /// <summary>Does this creature have a Stage to READ? Any player's: a
    /// card's face, price and gate read the same for whoever holds it (an
    /// Ironclad with no Stage up reads a fresh one: 0 Fanfare, nothing
    /// drained). Reading never brings the Stage up.</summary>
    public static bool Holds(Creature? creature) => creature?.Player != null;

    /// <summary>
    /// A Stage verb or a Furina card brings this player's Stage up, once a
    /// combat (the off-character fix, 2026-10-18: card verbs work for
    /// whichever player plays the card). The ledger's entry HP is what it
    /// captured on its first ask. False for no player, so a verb does
    /// nothing and never throws.
    /// </summary>
    public static bool Ensure(Creature? owner)
    {
        if (!Holds(owner)) return false;
        var ledger = FurinaStageLedger.For(owner!);
        if (!ledger.Opened) ledger.Open(ledger.EntryHp, ledger.EntryMaxHp);
        return true;
    }

    /// <summary>Her roster id, the one her cards carry.</summary>
    public const string CharacterId = "furina";

    /// <summary>Is this one of Furina's cards (her pool, her Guest Stars, her
    /// Ancients)? Playing one brings the player's Stage up, so her Powers
    /// and her readers are live on anyone who plays them. PURE.</summary>
    public static bool IsFurinaCard(CardModel? card) =>
        card is global::KleeMod.Cards.ICharacterCard { CharacterId: CharacterId };

    /// <summary>A card play opens: one of hers brings its player's Stage up
    /// before its effects (<see cref="Ensure"/>).</summary>
    public static void StartOnPlay(CardModel? card)
    {
        if (!IsFurinaCard(card)) return;
        Creature? owner;
        try
        {
            owner = card!.Owner?.Creature;
        }
        catch (System.Exception)
        {
            return;
        }
        Ensure(owner);
    }

    /// <summary>The eleven guests' sheet names (the slice's four, the pool to
    /// 39's three and the pool to 75's four).</summary>
    public static readonly string[] Guests =
    {
        "charlotte", "wriothesley", "lynette", "clorinde",
        "lyney", "sigewinne", "chevreuse",
        "freminet", "navia", "neuvillette", "escoffier",
    };

    /// <summary>A sheet name to a guest (an unknown name reads as Charlotte:
    /// the codegen refuses one at emit).</summary>
    public static StagePerformer Parse(string member) => member switch
    {
        "wriothesley" => StagePerformer.Wriothesley,
        "lynette" => StagePerformer.Lynette,
        "clorinde" => StagePerformer.Clorinde,
        "lyney" => StagePerformer.Lyney,
        "sigewinne" => StagePerformer.Sigewinne,
        "chevreuse" => StagePerformer.Chevreuse,
        "freminet" => StagePerformer.Freminet,
        "navia" => StagePerformer.Navia,
        "neuvillette" => StagePerformer.Neuvillette,
        "escoffier" => StagePerformer.Escoffier,
        _ => StagePerformer.Charlotte,
    };

    /// <summary>A guest to its sheet name.</summary>
    public static string Name(StagePerformer who) =>
        who.ToString().ToLowerInvariant();

    // ---- reading the kit ---------------------------------------------------

    public static IReadOnlyList<StageSeat> Of(Creature? owner) =>
        owner == null || !Holds(owner)
            ? System.Array.Empty<StageSeat>()
            : FurinaStageLedger.For(owner).Seats;

    /// <summary>Is any guest on stage?</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    /// <summary>Her Fanfare.</summary>
    public static int FanfareOf(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).Fanfare : 0;

    /// <summary>Her drained HP, not yet repaid.</summary>
    public static int DrainedOf(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).Drained : 0;

    /// <summary>High Stakes' count: HP she has drained this combat, gross
    /// (no Repay lowers it; the Spend round 2, 2026-10-10).</summary>
    public static int DrainedThisCombatOf(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).DrainedThisCombat : 0;

    /// <summary>Her Drain line (rule 1): her HP now minus the Drain buffer
    /// she has left (2026-10-11); HP drained past it does not return at the
    /// curtain call.</summary>
    public static int LineOf(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).Line : 0;

    /// <summary>`stage_spent`: what THIS play's spend-all took.</summary>
    public static int Spent(CardModel? card) =>
        card?.Owner?.Creature is { } owner && Holds(owner)
            ? FurinaStageLedger.For(owner).SpentThisPlay : 0;

    /// <summary>`stage_spent` for a "Spend up to <paramref name="cap"/>" as
    /// a face prints it: during the play, what it counted; before it, what
    /// it would count now (the cap under Center of Attention's free Spend,
    /// else the cap or all she holds plus Navia's free points). One
    /// expression, so preview and resolution agree.</summary>
    /// Extended Run (furina-next paper 2, 2026-10-16) adds to the card's
    /// printed cap, as the play's Spend does.
    public static int SpentOrUpTo(CardModel? card, int cap)
    {
        var owner = card?.Owner?.Creature;
        return SpentOrUpToCap(card, Holds(owner)
            ? FurinaStageLedger.For(owner!).CardUpToCap(cap) : cap);
    }

    /// <summary>`SpentOrUpTo` over a cap no power raises (Spend half).
    /// </summary>
    private static int SpentOrUpToCap(CardModel? card, int cap)
    {
        var spent = Spent(card);
        if (spent > 0) return spent;
        var owner = card?.Owner?.Creature;
        if (!Holds(owner)) return 0;
        return CenterOfAttentionPower.Covers(owner)
            ? cap
            : FurinaStageLedger.For(owner!).UpToOf(cap);
    }

    /// <summary>`stage_spent` for "Spend half your Fanfare" (Standing
    /// Ovation, 2026-10-11) as a face prints it: during the play, what it
    /// counted; before it, what a "Spend up to" half the bank (rounded down)
    /// would count now.</summary>
    public static int SpentOrHalf(CardModel? card) =>
        SpentOrUpToCap(card, FanfareOf(card?.Owner?.Creature) / 2);

    /// <summary>`stage_spent_fours`: this play's "Spend up to X" in fours,
    /// rounded down ("Draw 1 for every 4 spent", "hit once more for every
    /// 4").</summary>
    public static int SpentFours(CardModel? card) =>
        Spent(card) / FurinaStageLaw.SpendUpToEvery;

    /// <summary>`stage_spent_threes` (the diversity pass, 2026-10-11): this
    /// play's spend-all in threes, rounded down -- Bravura's hits ("Deal 7
    /// Hydro damage for every 3 spent").</summary>
    public static int SpentThrees(CardModel? card) =>
        Spent(card) / FurinaStageLaw.BravuraSpentPer;

    /// <summary>`stage_fanfare_fours` (the Spend outlet paper, 2026-10-12):
    /// her Fanfare in fours, rounded down -- Packed House's "plus 1 for every 4
    /// Fanfare you have" (read, never spent).</summary>
    public static int FanfareFours(Creature? owner) =>
        FanfareOf(owner) / FurinaStageLaw.PackedHouseFanfarePer;

    /// <summary>`stage_spent` as a face prints it: before the play, the
    /// Fanfare a spend-all is about to take; during it, what it took. One
    /// expression, so preview and resolution agree.</summary>
    public static int SpentOrFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : FanfareOf(card?.Owner?.Creature);
    }

    /// <summary>What her powers make of the rules, read live.</summary>
    public static StageMods ModsOf(Creature owner)
    {
        int Sum<T>() where T : PowerModel =>
            (int)owner.Powers.OfType<T>().Sum(p => p.Amount);
        int Upgraded<T>() where T : UpgradeTwinPower =>
            owner.Powers.OfType<T>().Sum(p => p.UpgradedCopies);
        // Her relics (Furina's card pass, 2026-10-15), counted off the
        // player; none headless.
        // Relic effects are Furina's own (the off-character fix,
        // 2026-10-18): her Stage on anyone else counts none.
        var hers = FurinaResources.IsFurina(owner);
        int Held<T>() where T : RelicModel =>
            hers ? owner.Player?.Relics.OfType<T>().Count() ?? 0 : 0;
        var seasonPass = Held<Relics.EpicleseSeasonPass>();
        return new StageMods
        {
            Capacity = (owner.Powers.OfType<EnsembleCastPower>().Any()
                ? FurinaStageLaw.EnsembleSeats : FurinaStageLaw.Seats)
              + seasonPass * FurinaStageLaw.SeasonPassSeats,
            SeasonPass = seasonPass,
            FontaineTeardrop = Held<Relics.FontaineTeardrop>(),
            ClaquesLedger = Held<Relics.ClaquesLedger>(),
            BouquetOfRoses = Held<Relics.BouquetOfRoses>(),
            GrandEntrance = Sum<GrandEntrancePower>(),
            Showstopper = Sum<ShowstopperPower>(),
            // The upgrade census (2026-10-23): one badge for both versions;
            // an upgraded card's copy Spends 3, gains 2 more Block, deals 1
            // more.
            ShowstopperUpgraded = Upgraded<ShowstopperPower>(),
            Crescendo = Sum<CrescendoPower>(),
            // One badge for both versions (the icon declutter, 2026-10-19):
            // every copy is Energy, an upgraded card's copy is also a card.
            PrimaDonna = Sum<PrimaDonnaPower>(),
            PrimaDonnaDraw = owner.Powers.OfType<PrimaDonnaPower>()
                .Sum(p => p.UpgradedCopies),
            StandingRoomOnly = Sum<StandingRoomOnlyPower>(),
            Revelry = Sum<UniversalRevelryPower>(),
            Thunderous = Sum<ThunderousApplausePower>(),
            FiveCenturyAct = owner.Powers.OfType<FiveCenturyActPower>().Count(),
            CriticsDarling = Sum<CriticsDarlingPower>(),
            CriticsDarlingUpgraded = Upgraded<CriticsDarlingPower>(),
            ExtendedRun = Sum<ExtendedRunPower>(),
            Masquerade = Sum<TheMasqueradePower>(),
            MasqueradeUpgraded = Upgraded<TheMasqueradePower>(),
            FullHouse = Sum<FullHousePower>(),
        };
    }

    // ---- the gates ----------------------------------------------------------

    /// <summary>Is a Spend N offered? Only when her Fanfare holds it.
    /// </summary>
    public static bool CanSpend(Creature? owner, int amount) =>
        Holds(owner) && FurinaStageLedger.For(owner!).CanSpend(amount);

    /// <summary>Rule 1: is a Drain N offered? Only when it would not take her
    /// to 0 HP or below (2026-10-09: never refused for the line).</summary>
    public static bool CanDrain(Creature? owner, int amount) =>
        Holds(owner)
        && FurinaStageLedger.For(owner!).CanDrain(amount,
                                                  (int)owner!.CurrentHp);

    // ---- the director ----------------------------------------------------

    /// <summary>The rules over this Furina's kit and the live board.</summary>
    public static StageDirector Director(PlayerChoiceContext choiceContext,
                                         Creature owner) =>
        new(FurinaStageLedger.For(owner),
            new GameStageBoard(choiceContext, owner));

    private static async Task Done(Creature? owner)
    {
        if (owner == null) return;
        await FurinaStagePets.Sync(owner);
        RefreshBadges(owner);
        await ShowBadge(owner);
    }

    // ---- the verbs the cards call -------------------------------------------

    /// <summary>Gain Fanfare (a relic, a potion, an Ancient).</summary>
    public static async Task<int> Gain(PlayerChoiceContext choiceContext,
                                       Creature? owner, int amount,
                                       string source = "")
    {
        if (amount <= 0 || !Ensure(owner)) return 0;
        var gained = FurinaStageLedger.For(owner!).Gain(amount, source);
        RefreshBadges(owner);
        await ShowBadge(owner);
        return gained;
    }

    /// <summary>A Spend N. Center of Attention's free Spend takes nothing
    /// (and moves nothing, so it is no Spend). Returns what was paid.
    /// </summary>
    public static async Task<int> Spend(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (!Ensure(owner)) return 0;
        if (CenterOfAttentionPower.TryClaim(owner!))
        {
            RefreshBadges(owner);
            return 0;
        }
        var paid = await Director(choiceContext, owner!).Spend(amount);
        RefreshBadges(owner);
        return paid;
    }

    /// <summary>"Spend up to X" (the Spend paper, 2026-10-10): spends X or
    /// all she holds, never fails, and is a Spend when at least 1 counts.
    /// Center of Attention's free Spend counts the full X and takes nothing
    /// (and, like its free Spend N, is no Spend). Returns what counts as
    /// spent, which the card's payoff reads as `stage_spent`. The verb an
    /// Attack or Skill calls: Extended Run (furina-next paper 2, 2026-10-16)
    /// adds to its whole printed cap, once
    /// (<see cref="FurinaStageLedger.CardUpToCap"/>).</summary>
    public static Task<int> SpendUpTo(PlayerChoiceContext choiceContext,
                                      Creature? owner, int cap) =>
        Ensure(owner)
            ? SpendUpToCap(choiceContext, owner,
                           FurinaStageLedger.For(owner!).CardUpToCap(cap))
            : Task.FromResult(0);

    /// <summary>A "Spend up to" over a cap no power raises.</summary>
    private static async Task<int> SpendUpToCap(
        PlayerChoiceContext choiceContext, Creature? owner, int cap)
    {
        if (!LiveFor(owner)) return 0;
        if (cap > 0 && CenterOfAttentionPower.TryClaim(owner!))
        {
            var free = FurinaStageLedger.For(owner!).SpendUpToFree(cap);
            RefreshBadges(owner);
            return free;
        }
        var spent = await Director(choiceContext, owner!).SpendUpTo(cap);
        RefreshBadges(owner);
        return spent;
    }

    /// <summary>"Spend half your Fanfare" (Standing Ovation, 2026-10-11): a
    /// "Spend up to" half the bank, rounded down, so 0 or 1 held spends
    /// nothing. It Spends no printed number, so Extended Run does not
    /// raise it. Returns what counts as spent.</summary>
    public static Task<int> SpendHalf(PlayerChoiceContext choiceContext,
                                      Creature? owner) =>
        SpendUpToCap(choiceContext, owner, FanfareOf(owner) / 2);

    /// <summary>"Spend all your Fanfare." Returns what was spent.</summary>
    public static async Task<int> SpendAll(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!Ensure(owner)) return 0;
        var spent = await Director(choiceContext, owner!).SpendAll();
        RefreshBadges(owner);
        return spent;
    }

    /// <summary>Rule 1: Drain N, on whichever player plays it, and nothing
    /// that would take them to 0 HP.</summary>
    public static async Task<bool> Drain(PlayerChoiceContext choiceContext,
                                         Creature? owner, int amount)
    {
        if (!Ensure(owner)) return false;
        var drained = await Director(choiceContext, owner!).Drain(amount);
        RefreshBadges(owner);
        await ShowBadge(owner);
        return drained;
    }

    /// <summary>Rule 2: Repay N, a card's. The part of N it could not
    /// return is paid as Block (furina-next paper 3, 2026-10-16: "Any HP a
    /// Repay cannot return becomes Block"); a card whose floor is its own
    /// damage (Cleansing Torrent) passes <see cref="StageFloor.None"/>.
    /// Either way the leftover is recorded for the play
    /// (<see cref="FurinaStageLedger.RepayLeftThisPlay"/>, the damage
    /// card's floor). Returns HP repaid.</summary>
    public static async Task<int> Repay(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount,
                                        StageFloor floor = StageFloor.Block)
    {
        if (!Ensure(owner)) return 0;
        var director = Director(choiceContext, owner!);
        var back = await director.RepayFloor(amount, floor);
        director.Stage.NoteRepayLeft(amount, back);
        RefreshBadges(owner);
        await ShowBadge(owner);
        return back;
    }

    /// <summary>The Repay floor's damage (Surging Waters, Hydro Lance,
    /// Cleansing Torrent: "plus 1 for any HP it could not Repay"): during the
    /// play, after its Repay, what that Repay could not return; before the
    /// play, what a Repay of <paramref name="amount"/> would leave now. One
    /// expression, so preview and resolution agree.</summary>
    public static int RepayLeftOrRoom(CardModel? card, int amount)
    {
        if (card?.Owner?.Creature is not { } owner || !Holds(owner))
        {
            return 0;
        }
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.RepayedThisPlay) return ledger.RepayLeftThisPlay;
        return System.Math.Max(0,
            amount - FurinaStageFacePreview.Room(owner, amount));
    }

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public static async Task<int> RepayAll(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!Ensure(owner)) return 0;
        var back = await Director(choiceContext, owner!).RepayAll();
        RefreshBadges(owner);
        await ShowBadge(owner);
        return back;
    }

    /// <summary>Bottled Encore: "Each guest acts twice."</summary>
    public static async Task ActEachTwice(PlayerChoiceContext choiceContext,
                                          Creature? owner)
    {
        if (!Ensure(owner)) return;
        await Director(choiceContext, owner!).ActEachTwice();
        await Done(owner);
    }

    /// <summary>"Gain N Energy next turn" (`stage_energy_next`, Interval Bell
    /// and Salon's Tab): the game's <c>EnergyNextTurnPower</c>.</summary>
    public static async Task EnergyNextTurn(PlayerChoiceContext choiceContext,
                                            Creature? owner, int amount)
    {
        if (amount <= 0 || !Ensure(owner)) return;
        await PowerCmd.Apply<EnergyNextTurnPower>(
            choiceContext, owner!, amount, applier: owner, cardSource: null);
    }

    /// <summary>A Guest Star card (`stage_guest`, the pool to 75's sec.3):
    /// summon the guest, with no effect on summon. The amount is the sheet's
    /// arrival Fanfare, 0 on every row. <paramref name="card"/> is the Guest
    /// Star played: it exhausts, its seat holds it until the guest leaves,
    /// and an upgraded one raises the guest's line or act. Grand Entrance
    /// Repays after.</summary>
    public static async Task GuestStar(PlayerChoiceContext choiceContext,
                                       Creature? owner, string member,
                                       int fanfare = 0,
                                       CardModel? card = null)
    {
        if (!Ensure(owner)) return;
        var director = Director(choiceContext, owner!);
        await director.SummonGuest(Parse(member), card?.IsUpgraded ?? false,
                                   card);
        if (fanfare > 0) director.Gain(fanfare, "Guest Star");
        var entrance = director.Stage.Mods.GrandEntrance;
        if (entrance > 0)
        {
            using (director.Stage.CausedBy(StageDirector.GrandEntranceTitle))
            {
                // "Repay 4." with the rule's Block floor (paper 3).
                await director.RepayFloor(entrance, StageFloor.Block);
            }
        }
        await Done(owner);
    }

    // ---- the pool to 75's guest verbs (FurinaCards' kinds call these) ------

    /// <summary>Encore!: "Your oldest guest acts."</summary>
    public static async Task ActOldest(PlayerChoiceContext choiceContext,
                                       Creature? owner)
    {
        if (!Ensure(owner)) return;
        await Director(choiceContext, owner!).ActOldest();
        await Done(owner);
    }

    /// <summary>Tutti!: "Each guest acts."</summary>
    public static async Task ActAll(PlayerChoiceContext choiceContext,
                                    Creature? owner)
    {
        if (!Ensure(owner)) return;
        await Director(choiceContext, owner!).ActAll();
        await Done(owner);
    }

    /// <summary>Bring the House Down (the upgrade census, 2026-10-23):
    /// "Spend 5 for each guest on stage: each guest acts twice." With no
    /// guest on stage, or a bank short of the price, nothing happens
    /// (Showstopper's "Spend 5: ..."). A card's Spend N, so Center of
    /// Attention's free Spend pays it. Sim twin:
    /// <c>furina_tide.house_down</c>.</summary>
    public static async Task HouseDown(PlayerChoiceContext choiceContext,
                                       Creature? owner)
    {
        if (!Ensure(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        if (ledger.IsEmpty) return;
        var price = HouseDownPrice(ledger.Seats.Count);
        var director = Director(choiceContext, owner!);
        if (CenterOfAttentionPower.TryClaim(owner!))
        {
            RefreshBadges(owner);
        }
        else
        {
            if (!ledger.CanSpend(price)) return;
            if (await director.Spend(price) <= 0) return;
        }
        await director.ActEachTwice();
        await Done(owner);
    }

    /// <summary>Bring the House Down's price: 5 for each guest on stage.
    /// PURE.</summary>
    public static int HouseDownPrice(int guests) =>
        System.Math.Max(0, guests) * FurinaStageLaw.HouseDownSpendPerGuest;

    /// <summary>Final Bow: "Choose a guest. It acts twice, then leaves."
    /// [3 times]. One guest is taken without a screen; with more, the player
    /// picks off a grid of their Guest Star cards.</summary>
    public static async Task FinalBow(PlayerChoiceContext choiceContext,
                                      Creature? owner, int times)
    {
        if (!Ensure(owner) || owner!.Player is not { } player) return;
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.IsEmpty) return;
        var index = 0;
        if (ledger.Seats.Count > 1)
        {
            index = await FurinaCards.ChooseSeat(choiceContext, player, ledger);
        }
        await Director(choiceContext, owner).FinalBow(index, times);
        await Done(owner);
    }

    /// <summary>Ensemble Cast (the diversity pass, 2026-10-11): "Summon a
    /// random guest." One of the eleven not on stage, off the combat's
    /// target stream, unupgraded and holding no card (none comes back when
    /// it leaves). Not a Guest Star played, so Grand Entrance stays quiet.
    /// With all eleven on stage, nothing. Sim twin:
    /// <c>furina_tide.summon_random</c>.</summary>
    public static async Task SummonRandom(PlayerChoiceContext choiceContext,
                                          Creature? owner)
    {
        if (!Ensure(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        var absent = System.Enum.GetValues<StagePerformer>()
            .Where(who => ledger.SeatOf(who) == null).ToList();
        if (absent.Count == 0) return;
        var rng = owner!.Player?.RunState?.Rng?.CombatTargets;
        var pick = rng == null ? absent[0] : rng.NextItem(absent);
        await Director(choiceContext, owner).SummonGuest(pick);
        await Done(owner);
    }

    /// <summary>Undercurrent's count: Drains made this combat.</summary>
    public static int DrainsThisCombat(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).DrainsThisCombat : 0;

    /// <summary>Rising Tide's count: Repays that returned HP this turn.
    /// </summary>
    public static int RepaysThisTurn(Creature? owner) =>
        Holds(owner) ? FurinaStageLedger.For(owner!).RepaysThisTurn : 0;

    /// <summary>Endless Waltz (furina-next paper 3, 2026-10-16): "Repay 2.
    /// Deal X damage, plus Y for each time you Repaid this turn." Its own
    /// Repay counts only when it returns HP. During the play, after that
    /// Repay, the count as it stands; before the play, the count plus 1 if
    /// a Repay of <paramref name="amount"/> would return HP now. One
    /// expression, so preview and resolution agree.</summary>
    public static int RepaysThisTurnWith(CardModel? card, int amount)
    {
        if (card?.Owner?.Creature is not { } owner || !Holds(owner))
        {
            return 0;
        }
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.RepayedThisPlay) return ledger.RepaysThisTurn;
        return ledger.RepaysThisTurn
             + (FurinaStageFacePreview.Room(owner, amount) > 0 ? 1 : 0);
    }

    /// <summary>Grand Absolution's "that much": HP THIS play's Repays
    /// returned.</summary>
    public static int RepaidThisPlay(CardModel? card) =>
        card?.Owner?.Creature is { } owner && Holds(owner)
            ? FurinaStageLedger.For(owner).RepaidThisPlay : 0;

    /// <summary>Grand Absolution's face before the play: the HP a Repay of
    /// everything would return now; during it, what it returned.</summary>
    public static int RepaidOrDrained(CardModel? card)
    {
        var repaid = RepaidThisPlay(card);
        if (repaid > 0) return repaid;
        return card?.Owner?.Creature is { } owner && Holds(owner)
            ? FurinaStageFacePreview.Room(owner, DrainedOf(owner)) : 0;
    }

    /// <summary>Against the Tide (2026-10-12): "If you Drained this turn":
    /// 1 or more HP drained this turn by any Drain, her cards' or a guest's
    /// act. Mirrors <c>furina_stage.drained_this_turn</c>.</summary>
    public static bool DrainedThisTurn(Creature? owner) =>
        Holds(owner) && FurinaStageLedger.For(owner!).DrainedThisTurn > 0;

    /// <summary>Clean Slate: "If you have no drained HP left".</summary>
    public static bool NoneDrained(Creature? owner) =>
        Holds(owner) && DrainedOf(owner) <= 0;

    /// <summary>Neuvillette's line: "Your Hydro damage deals 2 more." [3]
    /// The bonus a hit of <paramref name="element"/> from
    /// <paramref name="dealer"/> takes. PURE.</summary>
    public static int HydroBonus(Creature? dealer, Element element)
    {
        if (element != Element.Hydro || !LiveFor(dealer)) return 0;
        var seat = FurinaStageLedger.For(dealer!).SeatOf(
            StagePerformer.Neuvillette);
        if (seat == null) return 0;
        return seat.Upgraded ? FurinaStageLaw.NeuvilletteHydroBonusUpgraded
                             : FurinaStageLaw.NeuvilletteHydroBonus;
    }

    /// <summary>Star Turn: "Costs 1 less for every 6 Fanfare you have."
    /// </summary>
    public static int StarTurnDiscount(Creature? owner) =>
        FanfareOf(owner) / FurinaStageLaw.StarTurnFanfarePer;

    // ---- the clocks ---------------------------------------------------------

    /// <summary>The combat opens: the entry HP and Max HP the line is read
    /// from, and the badge. Idempotent.</summary>
    public static async Task OpenCombat(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).Open((int)owner!.CurrentHp,
                                           (int)owner!.MaxHp);
        await InstallBadge(owner);
        RefreshBadges(owner);
    }

    /// <summary>The top of her turn, before the draw: the flow counts and the
    /// once-a-turn latches reset.</summary>
    public static void OpenTurn(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).OpenTurn();
        RefreshBadges(owner);
    }

    public const string AllTheWorldsAStageTitle = "All the World's a Stage";
    public const string SalonSolitaireTitle = "Salon Solitaire";

    /// <summary>After her draw: Grand Theater Program's Fanfare.</summary>
    public static async Task TurnStart(PlayerChoiceContext choiceContext,
                                       Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var furina = owner!;
        var program = Relics.FurinaStageRelics
            .Count<Relics.GrandTheaterProgram>(furina)
            * Relics.GrandTheaterProgram.Fanfare;
        if (program > 0)
        {
            Relics.FurinaStageRelics.Flash<Relics.GrandTheaterProgram>(furina);
            using (FurinaStageLedger.For(furina).CausedBy("Grand Theater Program"))
            {
                await Gain(choiceContext, furina, program, "Grand Theater Program");
            }
        }
        CrescendoGains(choiceContext, furina);
        await ReginaDrains(choiceContext, furina);
        await FountainRepays(choiceContext, furina);
        await PrimaDonnaEnergy(choiceContext, furina);
        RefreshBadges(furina);
    }

    /// <summary>Crescendo (furina-next, 2026-10-16): "At the start of your
    /// turn, gain 2 [3] Fanfare, then 2 [3] more each turn after", counted
    /// from the turn it was played. Beside Grand Theater Program, the other
    /// turn-start Fanfare.</summary>
    private static void CrescendoGains(PlayerChoiceContext choiceContext,
                                       Creature furina)
    {
        using (FurinaStageLedger.For(furina).CausedBy(StageDirector.CrescendoTitle))
        {
            Director(choiceContext, furina).Crescendo();
        }
    }

    /// <summary>Regina of All Waters: "At the start of your turn, Drain 3,
    /// never past your line. If you do, gain 1 Strength." First of her
    /// turn-start Powers, so the Repays after it have room.</summary>
    private static async Task ReginaDrains(PlayerChoiceContext choiceContext,
                                           Creature furina)
    {
        var copies = (int)furina.Powers.OfType<ReginaOfAllWatersPower>()
            .Sum(p => p.Amount);
        if (copies <= 0) return;
        using (FurinaStageLedger.For(furina).CausedBy(StageDirector.ReginaTitle))
        {
            await Director(choiceContext, furina).Regina(copies);
        }
    }

    /// <summary>Prima Donna (furina-next, 2026-10-16): "At the start of your
    /// turn, if you Spent last turn, gain 1 Energy [and draw 1 card]." Last
    /// of her turn-start Powers. Copies add.</summary>
    private static async Task PrimaDonnaEnergy(
        PlayerChoiceContext choiceContext, Creature furina)
    {
        await Director(choiceContext, furina).PrimaDonna();
    }

    /// <summary>Fountain of Lucine: what the power took in since the last
    /// turn start is scheduled for three turns, then this turn's Repays are
    /// made, and the badge leaves once nothing is owed.</summary>
    private static async Task FountainRepays(PlayerChoiceContext choiceContext,
                                             Creature furina)
    {
        var power = furina.Powers.OfType<FountainOfLucinePower>().FirstOrDefault();
        if (power == null) return;
        var ledger = FurinaStageLedger.For(furina);
        var applied = (int)power.Amount;
        if (applied > ledger.FountainSeen)
        {
            ledger.ScheduleRepay(applied - ledger.FountainSeen,
                                 turns: 1);   // ruled 2026-10-13: the next turn only
            ledger.FountainSeen = applied;
        }
        using (ledger.CausedBy(FountainOfLucinePower.Title))
        {
            await Director(choiceContext, furina).TurnStartRepays();
        }
        if (!ledger.OwesRepays)
        {
            ledger.FountainSeen = 0;
            await PowerCmd.Remove(power);
        }
        else
        {
            power.Refresh();
        }
    }

    /// <summary>Rule 4: the Singer's Repay at the end of her turn -- Salon
    /// Solitaire's 1, The Curtain Never Falls' 2.</summary>
    public static int SingerOf(Creature? owner)
    {
        // Salon Solitaire is her starter: hers alone.
        if (!FurinaResources.IsFurina(owner) || owner!.Player is not { } player)
        {
            return 0;
        }
        return player.Relics.OfType<Relics.SalonSolitaire>().Count()
                   * FurinaStageLaw.SingerRepay
               + player.Relics.OfType<Relics.CurtainNeverFalls>().Count()
                   * FurinaStageLaw.SingerRepayUpgraded;
    }

    /// <summary>The end of her turn: the guests act front to back, then the
    /// Singer Repays.</summary>
    public static async Task EndOfTurnActs(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var singer = SingerOf(owner);
        if (singer > 0 && owner!.Player is { } player)
        {
            foreach (var relic in player.Relics
                         .Where(r => r is Relics.SalonSolitaire
                                     or Relics.CurtainNeverFalls))
            {
                relic.Flash();
            }
        }
        var director = Director(choiceContext, owner!);
        using (FurinaStageLedger.For(owner!).CausedBy(SalonSolitaireTitle))
        {
            await director.EndOfTurn(singer);
        }
        await Done(owner);
    }

    /// <summary>THE CURTAIN CALL (sec.16; the Drain line rule, 2026-10-09):
    /// at the combat's end the HP drained above the line returns (past it
    /// too, with A Five-Century Act), and the HP carries into the run.
    /// </summary>
    public static async Task CurtainCall(Creature? owner)
    {
        if (!LiveFor(owner) || owner!.IsDead) return;
        var parts = await Director(new ThrowingPlayerChoiceContext(), owner)
            .CurtainCallParts();
        // 2026-10-05: the seat page says it on the next screen ("Drained N HP
        // returned"); seats could not tell the drained HP came back. The
        // Spend round (2026-10-10): and what did NOT come back, the HP
        // drained past the line ("6 past your line lost"), or under A
        // Five-Century Act how much of the return was past it.
        if (parts.Back > 0 || parts.Lost > 0)
        {
            ResolutionLedger.NoteEvent(ResolutionLedger.HpReturned,
                                       string.Empty, owner, string.Empty,
                                       parts.Back, lost: parts.Lost,
                                       past: parts.PastBack);
        }
        RefreshBadges(owner);
    }

    /// <summary>A card play opens: a fresh per-play spend record.</summary>
    public static void BeginPlay(Creature? owner, string card = "")
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).BeginPlay(card);
    }

    /// <summary>A card play closes: its spend record closes with it, so a
    /// spend-all face reads her Fanfare again.</summary>
    public static void EndPlay(Creature? owner)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).EndPlay();
    }

    /// <summary>Rule 3: HP lost to anything but a Drain prints Fanfare (and
    /// counts for Neuvillette's act).</summary>
    public static void NoteHpLost(Creature? owner, int amount)
    {
        if (!LiveFor(owner) || amount <= 0) return;
        var ledger = FurinaStageLedger.For(owner!);
        if (ledger.Draining) return;
        ledger.NoteHpLost(amount);
        ledger.Gain(amount, "HP lost");
        RefreshBadges(owner);
    }

    /// <summary>Lynette's line: the first HP an enemy takes each turn pays
    /// its Fanfare again.</summary>
    public static void NoteEnemyHit(Creature? owner, int hpLost)
    {
        if (!LiveFor(owner) || hpLost <= 0) return;
        var ledger = FurinaStageLedger.For(owner!);
        if (!ledger.OnStage(StagePerformer.Lynette)
            || ledger.LynetteFiredThisTurn)
        {
            return;
        }
        ledger.LynetteFiredThisTurn = true;
        var gained = ledger.Gain(hpLost, "Lynette");
        ledger.NoteLine(StagePerformer.Lynette, gained);
        Vfx.StagePerformerBeat.Line(ledger.SeatOf(StagePerformer.Lynette)?.Pet);
        RefreshBadges(owner);
    }

    // ---- the badge ----------------------------------------------------------

    /// <summary>Her Fanfare badge (<see cref="FanfarePower"/>), installed at
    /// combat open and asked again every turn start. Idempotent.</summary>
    public static async Task InstallBadge(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        // Anyone else's badge goes up on their first Fanfare, as the base
        // game's Star counter does, and never off a combat.
        if (!FurinaResources.IsFurina(owner)
            && (owner!.CombatState == null || FanfareOf(owner) <= 0))
        {
            return;
        }
        if (owner!.Powers.OfType<FanfarePower>().Any()) return;
        await PowerCmd.Apply<FanfarePower>(
            new ThrowingPlayerChoiceContext(), owner, 1,
            applier: owner, cardSource: null, silent: true);
    }

    /// <summary>Anyone else's Fanfare badge, after a move that can gain
    /// Fanfare (<see cref="InstallBadge"/>). Furina's is up already.</summary>
    internal static Task ShowBadge(Creature? owner) =>
        FurinaResources.IsFurina(owner) ? Task.CompletedTask
                                        : InstallBadge(owner);

    /// <summary>Redraw the Fanfare badge, the Fanfare gauge, the Drained
    /// counter and the cues.</summary>
    public static void RefreshBadges(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        foreach (var badge in owner!.Powers.OfType<FanfarePower>().ToList())
        {
            badge.Refresh();
        }
        Vfx.FanfareCounter.Refresh(owner);
        Vfx.DrainedCounter.Refresh(owner);
        // Her HP legibility pass (2026-10-19): the returning HP on her bar.
        Vfx.FurinaReturningHpBar.Refresh(owner);
        Vfx.FurinaStageCues.Refresh(owner);
    }

    // ---- the board's helpers ------------------------------------------------

    internal static bool CombatOver() =>
        MegaCrit.Sts2.Core.Combat.CombatManager.Instance.IsOverOrEnding;

    internal static IEnumerable<Creature> Enemies(Creature owner) =>
        owner.CombatState?.HittableEnemies.ToList()
        ?? Enumerable.Empty<Creature>();

    /// <summary>A random one of <paramref name="pool"/>, off the combat's
    /// target stream.</summary>
    public static Creature? RandomOf(Creature owner, IReadOnlyList<Creature> pool)
    {
        if (pool.Count == 0) return null;
        var rng = owner.Player?.RunState?.Rng?.CombatTargets;
        return rng == null ? pool[0] : rng.NextItem(pool);
    }

    // ---- the forecast (what the end of this turn will do) ------------------

    /// <summary>The end of this turn, forecast: each guest's act in seat
    /// order. Null for anyone whose Stage is not up. PURE.</summary>
    public static StageForecast? Forecast(Creature? owner)
    {
        if (!LiveFor(owner)) return null;
        return Forecast(FurinaStageLedger.For(owner!));
    }

    /// <summary>The forecast against a given stage (the pins'). Navia Spends
    /// half and Freminet a quarter of what is left when they act, oldest
    /// first (the Spend paper, 2026-10-10), so the bank is walked in seat
    /// order.</summary>
    public static StageForecast Forecast(FurinaStageLedger ledger)
    {
        var bank = ledger.Fanfare;
        var free = ledger.NaviaDiscount;      // the turn's first Spend only
        var cues = new List<StageForecastCue>(ledger.Seats.Count);
        foreach (var seat in ledger.Seats)
        {
            var half = 0;
            if (seat.Who is StagePerformer.Navia or StagePerformer.Freminet)
            {
                half = bank / (seat.Who == StagePerformer.Navia
                    ? FurinaStageLaw.NaviaSpendDivisor
                    : FurinaStageLaw.FreminetSpendDivisor);
                if (half > 0)
                {
                    bank -= half - System.Math.Min(half, free);
                    free = 0;
                }
            }
            cues.Add(CueOf(ledger, seat, half));
        }
        return new(cues);
    }

    private static StageForecastCue CueOf(FurinaStageLedger ledger,
                                          StageSeat seat, int half)
    {
        var n = StageDirector.ActAmount(seat.Who, seat.Upgraded);
        return seat.Who switch
        {
            StagePerformer.Charlotte => new(seat.Who, seat.Key,
                StageCueKind.Repay, n, "", ""),
            StagePerformer.Wriothesley => new(seat.Who, seat.Key,
                StageCueKind.Damage, n, "Cryo", StageForecastCue.Random),
            StagePerformer.Lynette => new(seat.Who, seat.Key,
                StageCueKind.Damage, n, "Anemo", StageForecastCue.Aura),
            StagePerformer.Lyney => new(seat.Who, seat.Key,
                StageCueKind.Damage, n, "Pyro", StageForecastCue.All),
            StagePerformer.Sigewinne => new(seat.Who, seat.Key,
                StageCueKind.Repay, n, "", ""),
            StagePerformer.Chevreuse => new(seat.Who, seat.Key,
                StageCueKind.Damage, n, "", StageForecastCue.Random),
            StagePerformer.Freminet => new(seat.Who, seat.Key,
                StageCueKind.Block, n + half, "", ""),
            StagePerformer.Navia => new(seat.Who, seat.Key,
                StageCueKind.Damage,
                half * FurinaStageLaw.NaviaActMultiplier, "Geo", StageForecastCue.Random),
            StagePerformer.Neuvillette => new(seat.Who, seat.Key,
                StageCueKind.Damage, ledger.HpLostSinceLastTurn, "Hydro",
                StageForecastCue.All),
            StagePerformer.Escoffier => new(seat.Who, seat.Key,
                StageCueKind.Damage, n, "Cryo", StageForecastCue.All),
            _ => new(seat.Who, seat.Key, StageCueKind.Damage, n, "Electro",
                StageForecastCue.Random),
        };
    }
}

/// <summary>
/// A SPEND CARD, AS A TYPE (the Furina whole-run round 2, 2026-10-10). The
/// codegen puts this on every row whose own play pays Fanfare -- a
/// <c>stage_spend</c>, <c>stage_spend_all</c>, <c>stage_spend_up_to</c> or
/// <c>stage_spend_half</c> anywhere in its body, modes included -- and nothing else implements it.
/// A Power that Spends later (Showstopper) or reacts to a Spend is not one.
/// A marker with no members, like <c>ISetOffCard</c>: telemetry counts the
/// Spend cards in her hand as each turn opens.
/// </summary>
public interface IStageSpendCard
{
}

/// <summary>What a guest's act is, as its cue draws it.</summary>
public enum StageCueKind
{
    /// <summary>Every damage act.</summary>
    Damage,

    /// <summary>Charlotte: Repay.</summary>
    Repay,

    /// <summary>Freminet: Block (the Spend paper, 2026-10-10).</summary>
    Block,
}

/// <summary>ONE GUEST'S CUE: what it will do at the end of this turn.
/// </summary>
public readonly record struct StageForecastCue(
    StagePerformer Who, int Key, StageCueKind Kind, int Amount,
    string Element, string Target)
{
    public const string All = "all";
    public const string Random = "random";
    public const string Aura = "random_aura";
}

/// <summary>The whole forecast: one cue per guest in seat order.</summary>
public sealed record StageForecast(IReadOnlyList<StageForecastCue> Cues);

/// <summary>
/// THE BOARD HALF, IN THE GAME: every Drain's, Repay's, act's and line's
/// command, on the live combat. Guest acts and Power hits are unpowered (her
/// Strength and Weak stay out of them); a guest's act carries its element
/// through <see cref="ElementalHit.Deal"/>, so it applies its aura and
/// reacts.
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

    public int Hp => (int)_owner.CurrentHp;

    public int MaxHp => (int)_owner.MaxHp;

    /// <summary>A Drain: an unblockable, unpowered HP loss on herself, the
    /// base game's own self-damage shape (Offering's). What landed is
    /// measured, so a relic that softens HP loss is honoured.</summary>
    public async Task<int> LoseHp(int amount)
    {
        if (amount <= 0) return 0;
        var before = (int)_owner.CurrentHp;
        await CreatureCmd.Damage(
            _context, _owner, amount,
            ValueProp.Unblockable | ValueProp.Unpowered, dealer: null,
            cardSource: null, cardPlay: null);
        return System.Math.Max(0, before - (int)_owner.CurrentHp);
    }

    public async Task<int> Heal(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return 0;
        var before = (int)_owner.CurrentHp;
        await CreatureCmd.Heal(_owner, amount);
        return System.Math.Max(0, (int)_owner.CurrentHp - before);
    }

    public async Task Damage(StagePerformer who, StageTarget target,
                             int amount, Element element)
    {
        if (amount <= 0) return;
        using var credit = Diagnostics.DamageCredit.Open(
            _owner, Diagnostics.DamageCredit.Pet, who.ToString());
        await Hit(target, amount, element, who);
    }

    public async Task PowerHit(string source, StageTarget target, int amount)
    {
        if (amount <= 0) return;
        // The play telemetry credits the Power by name ("(Thunderous
        // Applause)", the Spend round 2, 2026-10-10), not the shared
        // "(power)" bucket; it replaces a card's or an act's scope, since the
        // Power is what deals it.
        using var credit = Diagnostics.DamageCredit.Open(
            _owner, Diagnostics.DamageCredit.Power, source);
        await Hit(target, amount, Element.None);
    }

    public async Task Block(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return;
        await CreatureCmd.GainBlock(_owner, amount, ValueProp.Unpowered, null,
                                    fast: true);
    }

    public async Task Vigor(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return;
        await PowerCmd.Apply<VigorPower>(
            _context, _owner, amount, applier: _owner, cardSource: null);
    }

    public Task Vulnerable(StageTarget target, int amount) =>
        Debuff<VulnerablePower>(target, amount);

    public Task Weak(StageTarget target, int amount) =>
        Debuff<WeakPower>(target, amount);

    private async Task Debuff<T>(StageTarget target, int amount)
        where T : PowerModel
    {
        if (amount <= 0) return;
        var enemies = FurinaStage.Enemies(_owner).ToList();
        var targets = target == StageTarget.All
            ? enemies
            : FurinaStage.RandomOf(_owner, enemies) is { } one
                ? new List<Creature> { one }
                : new List<Creature>();
        foreach (var enemy in targets)
        {
            if (Over) return;
            await PowerCmd.Apply<T>(
                _context, enemy, amount, applier: _owner, cardSource: null);
        }
    }

    public async Task Strength(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return;
        await PowerCmd.Apply<StrengthPower>(
            _context, _owner, amount, applier: _owner, cardSource: null);
    }

    public Task LineCue(StageSeat? seat)
    {
        Vfx.StagePerformerBeat.Line(seat?.Pet);
        // The guest effects (2026-10-16): Navia's discount, Chevreuse's line.
        Vfx.FurinaGuestFx.OnLine(seat);
        return Task.CompletedTask;
    }

    /// <summary>The pool to 75 (sec.3): a guest that leaves sends its Guest
    /// Star cards from the exhaust pile to the discard pile. A card no longer
    /// exhausted (another effect moved it) is left where it is.</summary>
    public async Task ReturnCards(StageSeat seat)
    {
        var exhaust = _owner.Player is { } player
            ? CardPile.Get(PileType.Exhaust, player) : null;
        foreach (var card in seat.Cards.ToList())
        {
            if (exhaust == null || !exhaust.Cards.Contains(card)) continue;
            await CardPileCmd.Add(card, PileType.Discard);
        }
        seat.Cards.Clear();
    }

    /// <summary><paramref name="who"/> is the guest whose act this is
    /// (null for a Power's hit): its effect plays on each enemy it lands on
    /// (the guest effects, 2026-10-16).</summary>
    private async Task Hit(StageTarget target, int amount, Element element,
                           StagePerformer? who = null)
    {
        var enemies = FurinaStage.Enemies(_owner).ToList();
        if (enemies.Count == 0) return;
        if (target == StageTarget.All)
        {
            foreach (var enemy in enemies)
            {
                if (Over) return;
                await One(enemy, amount, element, who);
            }
            return;
        }
        var pool = enemies;
        if (target == StageTarget.Aura)
        {
            // "an enemy, aura first" (the diversity pass,
            // 2026-10-11): with no aura on any enemy, any enemy.
            var aura = enemies.Where(e => AuraCmd.Find(e) != null).ToList();
            if (aura.Count > 0) pool = aura;
        }
        if (FurinaStage.RandomOf(_owner, pool) is { } body)
        {
            await One(body, amount, element, who);
        }
    }

    private Task<int> One(Creature enemy, int amount, Element element,
                          StagePerformer? who)
    {
        if (who is { } guest) Vfx.FurinaGuestFx.OnHit(guest, enemy);
        return element == Element.None
            ? ElementalHit.DealUnelemented(_context, enemy, amount, _owner,
                                           powered: false)
            : ElementalHit.Deal(_context, enemy, element, amount, _owner,
                                powered: false);
    }

    public async Task Draw(int amount)
    {
        if (amount <= 0 || _owner.Player is not { } player) return;
        await CardPileCmd.Draw(_context, amount, player);
    }

    /// <summary>The act's lunge, then (the guest effects, 2026-10-16) the
    /// effect of a guest whose act lands on Furina: Charlotte's flash,
    /// Sigewinne's bubbles, Freminet's plate. Not awaited past the lunge.
    /// </summary>
    public async Task Lunge(StageSeat? seat)
    {
        await Vfx.StagePerformerBeat.Act(seat?.Pet);
        Vfx.FurinaGuestFx.OnAct(_owner, seat);
    }

    /// <summary>Her model art, phase B (2026-10-13): the Spend, Drain or
    /// Repay effect on her body, fire-and-forget.</summary>
    public void Effect(StageEffect effect) =>
        Vfx.FurinaStageFx.Play(_owner, effect);

    public async Task Sync()
    {
        await FurinaStagePets.Sync(_owner);
        FurinaStage.RefreshBadges(_owner);
    }

    public async Task Energy(int amount)
    {
        if (amount <= 0 || _owner.IsDead || _owner.Player is not { } player) return;
        await PlayerCmd.GainEnergy(amount, player);
    }

    public void FlashRelic(System.Type relic)
    {
        if (_owner.Player is not { } player) return;
        foreach (var held in player.Relics.Where(r => r.GetType() == relic))
        {
            held.Flash();
        }
    }
}

/// <summary>THE CAST: the slice's four Guest Stars, the pool to 39's three
/// and the pool to 75's four. A guest is a pet body with no bar; every rule
/// about it is the ledger's.</summary>
public enum StagePerformer
{
    Charlotte,
    Wriothesley,
    Lynette,
    Clorinde,
    Lyney,
    Sigewinne,
    Chevreuse,
    Freminet,
    Navia,
    Neuvillette,
    Escoffier,
}
