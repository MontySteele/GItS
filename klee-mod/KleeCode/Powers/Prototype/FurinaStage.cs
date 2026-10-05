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
///      when it cannot be paid. It cannot take her below half the HP she
///      started this combat with (the line). HP lost to a Drain is drained.
///   2. REPAY N: regain up to N of her drained HP, never more.
///   3. FANFARE: one number on Furina, no cap, no fade. +1 for every HP she
///      loses (a Drain, a hit past Block, anything) and +1 for every HP she
///      Repays. Spend N and the spend-all cards pay it.
///   4. SALON SOLITAIRE, her starting relic: "At the end of your turn, Repay
///      2." (Upgraded: 3.)
///   5. GUEST STARS: three seats, guests only. A guest acts at the end of her
///      turn; a fourth makes the oldest leave, acting once more as it goes; a
///      second copy of one on stage makes it act and stay.
///   6. THE CURTAIN CALL: when the combat ends, all drained HP returns.
///
/// THIS CLASS IS THE VERB SURFACE the generated cards, the powers, the relics
/// and the potions call. The order of things is
/// <see cref="StageDirector"/>'s, the numbers <see cref="FurinaStageLedger"/>'s,
/// and the game half <see cref="GameStageBoard"/>'s.
/// </summary>
public static class FurinaStage
{
    /// <summary>Is the kit live for THIS creature? In co-op the other seat is
    /// not hers: her cards do nothing on anyone else, and never throw.
    /// </summary>
    public static bool LiveFor(Creature? creature) =>
        FurinaResources.IsFurina(creature);

    /// <summary>The seven guests' sheet names (the slice's four, and the
    /// pool to 39's three).</summary>
    public static readonly string[] Guests =
    {
        "charlotte", "wriothesley", "lynette", "clorinde",
        "lyney", "sigewinne", "chevreuse",
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
        _ => StagePerformer.Charlotte,
    };

    /// <summary>A guest to its sheet name.</summary>
    public static string Name(StagePerformer who) =>
        who.ToString().ToLowerInvariant();

    // ---- reading the kit ---------------------------------------------------

    public static IReadOnlyList<StageSeat> Of(Creature? owner) =>
        owner == null || !LiveFor(owner)
            ? System.Array.Empty<StageSeat>()
            : FurinaStageLedger.For(owner).Seats;

    /// <summary>Is any guest on stage?</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    /// <summary>Her Fanfare.</summary>
    public static int FanfareOf(Creature? owner) =>
        LiveFor(owner) ? FurinaStageLedger.For(owner!).Fanfare : 0;

    /// <summary>Her drained HP, not yet repaid.</summary>
    public static int DrainedOf(Creature? owner) =>
        LiveFor(owner) ? FurinaStageLedger.For(owner!).Drained : 0;

    /// <summary>The lowest HP a Drain may take her to (rule 1).</summary>
    public static int LineOf(Creature? owner) =>
        LiveFor(owner) ? FurinaStageLedger.For(owner!).Line : 0;

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

    /// <summary>What her powers make of the rules, read live.</summary>
    public static StageMods ModsOf(Creature owner)
    {
        int Sum<T>() where T : PowerModel =>
            (int)owner.Powers.OfType<T>().Sum(p => p.Amount);
        return new StageMods
        {
            Revelry = Sum<UniversalRevelryPower>(),
            SalonsEncore = Sum<SalonsEncorePower>(),
            EndlessWaltz = owner.Powers.OfType<EndlessWaltzPower>().Count(),
            Thunderous = Sum<ThunderousApplausePower>(),
            OusiaSurge = Sum<OusiaSurgePower>(),
            FiveCenturyAct = owner.Powers.OfType<FiveCenturyActPower>().Count(),
            CriticsDarling = Sum<CriticsDarlingPower>(),
            Bis = owner.Powers.OfType<BisPower>().Count(),
        };
    }

    // ---- the gates ----------------------------------------------------------

    /// <summary>Is a Spend N offered? Only when her Fanfare holds it.
    /// </summary>
    public static bool CanSpend(Creature? owner, int amount) =>
        LiveFor(owner) && FurinaStageLedger.For(owner!).CanSpend(amount);

    /// <summary>Rule 1: is a Drain N offered? Only when it would not take her
    /// below the line.</summary>
    public static bool CanDrain(Creature? owner, int amount) =>
        LiveFor(owner)
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
    }

    // ---- the verbs the cards call -------------------------------------------

    /// <summary>Gain Fanfare (a relic, a potion, an Ancient).</summary>
    public static Task<int> Gain(PlayerChoiceContext choiceContext,
                                 Creature? owner, int amount,
                                 string source = "")
    {
        if (!LiveFor(owner) || amount <= 0) return Task.FromResult(0);
        var gained = FurinaStageLedger.For(owner!).Gain(amount, source);
        RefreshBadges(owner);
        return Task.FromResult(gained);
    }

    /// <summary>A Spend N. Center of Attention's free Spend takes nothing
    /// (and moves nothing, so it is no Spend). Returns what was paid.
    /// </summary>
    public static async Task<int> Spend(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        if (CenterOfAttentionPower.TryClaim(owner!))
        {
            RefreshBadges(owner);
            return 0;
        }
        var paid = await Director(choiceContext, owner!).Spend(amount);
        RefreshBadges(owner);
        return paid;
    }

    /// <summary>"Spend all your Fanfare." Returns what was spent.</summary>
    public static async Task<int> SpendAll(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var spent = await Director(choiceContext, owner!).SpendAll();
        RefreshBadges(owner);
        return spent;
    }

    /// <summary>Rule 1: Drain N. Nothing on anyone but Furina, and nothing
    /// past the line.</summary>
    public static async Task<bool> Drain(PlayerChoiceContext choiceContext,
                                         Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return false;
        var drained = await Director(choiceContext, owner!).Drain(amount);
        RefreshBadges(owner);
        return drained;
    }

    /// <summary>Rule 2: Repay N. Returns HP repaid.</summary>
    public static async Task<int> Repay(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        var back = await Director(choiceContext, owner!).Repay(amount);
        RefreshBadges(owner);
        return back;
    }

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public static async Task<int> RepayAll(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var back = await Director(choiceContext, owner!).RepayAll();
        RefreshBadges(owner);
        return back;
    }

    /// <summary>"Gain N Energy next turn" (`stage_energy_next`, Interval Bell
    /// and Salon's Tab): the game's <c>EnergyNextTurnPower</c>.</summary>
    public static async Task EnergyNextTurn(PlayerChoiceContext choiceContext,
                                            Creature? owner, int amount)
    {
        if (!LiveFor(owner) || amount <= 0) return;
        await PowerCmd.Apply<EnergyNextTurnPower>(
            choiceContext, owner!, amount, applier: owner, cardSource: null);
    }

    /// <summary>A Guest Star card (`stage_guest`): summon the guest. The
    /// trailing amount is the sheet's arrival Fanfare, 0 on every row of the
    /// slice.</summary>
    public static async Task GuestStar(PlayerChoiceContext choiceContext,
                                       Creature? owner, string member,
                                       int fanfare = 0)
    {
        if (!LiveFor(owner)) return;
        var director = Director(choiceContext, owner!);
        await director.SummonGuest(Parse(member));
        if (fanfare > 0) director.Gain(fanfare, "Guest Star");
        await Done(owner);
    }

    // ---- the clocks ---------------------------------------------------------

    /// <summary>The combat opens: the entry HP the line is read from, and the
    /// badge. Idempotent.</summary>
    public static async Task OpenCombat(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).Open((int)owner!.CurrentHp);
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
        await FountainRepays(choiceContext, furina);
        RefreshBadges(furina);
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
                                 FurinaStageLaw.FountainTurns);
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
    /// Solitaire's 2, The Curtain Never Falls' 3.</summary>
    public static int SingerOf(Creature? owner)
    {
        if (!LiveFor(owner) || owner!.Player is not { } player) return 0;
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

    /// <summary>THE CURTAIN CALL (sec.16): at the combat's end every drained
    /// HP returns, and the HP carries into the run.</summary>
    public static async Task CurtainCall(Creature? owner)
    {
        if (!LiveFor(owner) || owner!.IsDead) return;
        await Director(new ThrowingPlayerChoiceContext(), owner).CurtainCall();
        RefreshBadges(owner);
    }

    /// <summary>A card play opens: a fresh per-play spend record.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).BeginPlay();
    }

    /// <summary>A card play closes: its spend record closes with it, so a
    /// spend-all face reads her Fanfare again.</summary>
    public static void EndPlay(Creature? owner)
    {
        if (LiveFor(owner)) FurinaStageLedger.For(owner!).EndPlay();
    }

    /// <summary>Rule 3: HP lost to anything but a Drain prints Fanfare.
    /// </summary>
    public static void NoteHpLost(Creature? owner, int amount)
    {
        if (!LiveFor(owner) || amount <= 0) return;
        var ledger = FurinaStageLedger.For(owner!);
        if (ledger.Draining) return;
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
        ledger.Gain(hpLost, "Lynette");
        RefreshBadges(owner);
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
    /// order. Null for anyone but Furina. PURE.</summary>
    public static StageForecast? Forecast(Creature? owner)
    {
        if (!LiveFor(owner)) return null;
        return Forecast(FurinaStageLedger.For(owner!));
    }

    /// <summary>The forecast against a given stage (the pins').</summary>
    public static StageForecast Forecast(FurinaStageLedger ledger) =>
        new(ledger.Seats.Select(CueOf).ToList());

    private static StageForecastCue CueOf(StageSeat seat) => seat.Who switch
    {
        StagePerformer.Charlotte => new(seat.Who, seat.Key, StageCueKind.Repay,
            FurinaStageLaw.CharlotteActRepay, "", ""),
        StagePerformer.Wriothesley => new(seat.Who, seat.Key,
            StageCueKind.Damage, FurinaStageLaw.WriothesleyActDamage, "Cryo",
            StageForecastCue.Random),
        StagePerformer.Lynette => new(seat.Who, seat.Key, StageCueKind.Damage,
            FurinaStageLaw.LynetteActDamage, "Anemo", StageForecastCue.Aura),
        StagePerformer.Lyney => new(seat.Who, seat.Key, StageCueKind.Damage,
            FurinaStageLaw.LyneyActDamage, "Pyro", StageForecastCue.All),
        StagePerformer.Sigewinne => new(seat.Who, seat.Key,
            StageCueKind.Repay, FurinaStageLaw.SigewinneActRepay, "", ""),
        StagePerformer.Chevreuse => new(seat.Who, seat.Key,
            StageCueKind.Damage, FurinaStageLaw.ChevreuseActDamage, "",
            StageForecastCue.Random),
        _ => new(seat.Who, seat.Key, StageCueKind.Damage,
            FurinaStageLaw.ClorindeActDamage, "Electro",
            StageForecastCue.Random),
    };
}

/// <summary>What a guest's act is, as its cue draws it.</summary>
public enum StageCueKind
{
    /// <summary>Every damage act.</summary>
    Damage,

    /// <summary>Charlotte: Repay.</summary>
    Repay,
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
        await Hit(target, amount, element);
    }

    public async Task PowerHit(string source, StageTarget target, int amount)
    {
        if (amount <= 0) return;
        await Hit(target, amount, Element.None);
    }

    public async Task Block(int amount)
    {
        if (amount <= 0 || _owner.IsDead) return;
        await CreatureCmd.GainBlock(_owner, amount, ValueProp.Unpowered, null,
                                    fast: true);
    }

    public async Task Vulnerable(StageTarget target, int amount)
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
            await PowerCmd.Apply<VulnerablePower>(
                _context, enemy, amount, applier: _owner, cardSource: null);
        }
    }

    private async Task Hit(StageTarget target, int amount, Element element)
    {
        var enemies = FurinaStage.Enemies(_owner).ToList();
        if (enemies.Count == 0) return;
        if (target == StageTarget.All)
        {
            foreach (var enemy in enemies)
            {
                if (Over) return;
                await One(enemy, amount, element);
            }
            return;
        }
        var pool = enemies;
        if (target == StageTarget.Aura)
        {
            pool = enemies.Where(e => AuraCmd.Find(e) != null).ToList();
        }
        if (FurinaStage.RandomOf(_owner, pool) is { } body)
        {
            await One(body, amount, element);
        }
    }

    private Task<int> One(Creature enemy, int amount, Element element) =>
        element == Element.None
            ? ElementalHit.DealUnelemented(_context, enemy, amount, _owner,
                                           powered: false)
            : ElementalHit.Deal(_context, enemy, element, amount, _owner,
                                powered: false);

    public async Task Draw(int amount)
    {
        if (amount <= 0 || _owner.Player is not { } player) return;
        await CardPileCmd.Draw(_context, amount, player);
    }

    public Task Lunge(StageSeat? seat) =>
        Vfx.StagePerformerBeat.Act(seat?.Pet);

    public async Task Sync()
    {
        await FurinaStagePets.Sync(_owner);
        FurinaStage.RefreshBadges(_owner);
    }
}

/// <summary>THE CAST: the slice's four Guest Stars and the pool to 39's
/// three. A guest is a pet body with no bar; every rule about it is the
/// ledger's.</summary>
public enum StagePerformer
{
    Charlotte,
    Wriothesley,
    Lynette,
    Clorinde,
    Lyney,
    Sigewinne,
    Chevreuse,
}
