using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// WHAT ONE SAKURA STRIKE DOES (shrine r2, ruled 2026-10-14, in
/// <c>review/active/yae-design-axes-2026-10-14.md</c>): the persistent Rite
/// is gone. Every end-of-turn strike, Last Bloom, Editor-in-Chief and
/// Kitsune Pounce strike as Thunder; a typed Tenko ("Tenko (Warding)")
/// strikes every Sakura once as its kind. Sim twin:
/// <c>yae_shrine.TENKO_KINDS</c>.
/// </summary>
public enum YaeTenkoKind
{
    Thunder = 0,
    Warding = 1,
    Wildfire = 2,
    Offering = 3,
}

/// <summary>The end an "Edit your newest / oldest Sakura" counts from, or
/// "Edit every Sakura".</summary>
public enum YaeSakuraEnd
{
    Newest = 0,
    Oldest = 1,
    Every = 2,
}

/// <summary>One Sesshou Sakura: its Level, the strikes it has left, its
/// place in planting order (the ledger's clock), and the one Annotation it
/// may carry (Red Ink, Fox Fire or Deadline Extension; ruled
/// 2026-10-14).</summary>
public sealed class YaeSakura
{
    public int Level { get; internal set; }

    public int TurnsLeft { get; internal set; }

    public int Seq { get; internal set; }

    public YaeAnnotation Annotation { get; internal set; }
}

/// <summary>
/// YAE'S SHRINE, ONE FIGHT'S WORTH (paper sec.2, "Sakura"). PURE -- no
/// command runs here -- so the headless suite pins every reading by value;
/// <see cref="YaeShrine"/> is the door that strikes and pays the powers.
///
/// PER COMBAT, keyed on the creature and rolled to the combat the way
/// <see cref="VarkaOathLedger"/> is: a new <c>CombatState</c> forgets every
/// Sakura ("fight one opens with an empty shrine"). Sim twin:
/// <c>yae_shrine.YaeLedger</c>.
/// </summary>
public sealed class YaeShrineLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, YaeShrineLedger> _byYae = new();
    private static readonly object Gate = new();

    /// <summary>This creature's shrine for this combat, created on first ask.
    /// </summary>
    public static YaeShrineLedger For(Creature creature)
    {
        lock (Gate)
        {
            var combat = (object?)creature.CombatState;
            if (!ReferenceEquals(_combat, combat))
            {
                _combat = combat;
                _byYae.Clear();
            }
            if (!_byYae.TryGetValue(creature, out var ledger))
            {
                ledger = new YaeShrineLedger();
                _byYae[creature] = ledger;
            }
            return ledger;
        }
    }

    /// <summary>Test seam: forget every ledger. The mod never calls it.
    /// </summary>
    public static void ResetAll()
    {
        lock (Gate)
        {
            _combat = null;
            _byYae.Clear();
        }
    }

    private readonly List<YaeSakura> _sakura = new();

    /// <summary>The Sakura standing, oldest first.</summary>
    public IReadOnlyList<YaeSakura> Standing => _sakura;

    /// <summary>How many stand now ("standing counts Sakura now").</summary>
    public int Count => _sakura.Count;

    /// <summary>The planting clock.</summary>
    public int Seq { get; private set; }

    /// <summary>This turn's aimed enemy (Foxfire Lure), or null.</summary>
    public Creature? Lure { get; set; }

    /// <summary>Strikes made this combat (telemetry, the seat page).</summary>
    public int Strikes { get; private set; }

    /// <summary>Edits made this combat.</summary>
    public int Edits { get; private set; }

    /// <summary>Offering: cards she draws at the start of her next turn.
    /// </summary>
    public int PendingDraw { get; internal set; }

    /// <summary>Withers since her last turn start (Fallen Petals pays them
    /// then: a Sakura withers at her turn's end, when Energy is lost).
    /// </summary>
    public int PendingWithers { get; internal set; }

    /// <summary>
    /// PLANT ONE (shrine r2, ruled 2026-10-14): a new Sakura at
    /// <paramref name="plantLevel"/> with <see cref="YaeLaw.SakuraTurns"/>
    /// strikes left; the others are NOT levelled. With three standing, the
    /// OLDEST instead refreshes (<see cref="YaeLaw.SakuraTurns"/> again) and
    /// gains 1 Level, and none is added. Levels have no cap. Returns whether
    /// one was added.
    /// </summary>
    public bool Plant(int plantLevel) => Plant(plantLevel, null);

    /// <summary>Plant one, the new Sakura starting at <paramref name="startLevel"/>
    /// where a card says so (Grafted Branch), raised as every plant is by
    /// Fox's Mooncall (its bonus is <paramref name="plantLevel"/> over
    /// <see cref="YaeLaw.PlantLevel"/>); never below the plant Level.
    /// <paramref name="inherited"/>: the Annotation the new Sakura carries
    /// from the card that planted it (Red Ink on a card that only plants,
    /// ruled 2026-10-14, <see cref="YaeAnnotationReach"/>); none is added
    /// when three stand, so nothing inherits then.
    /// </summary>
    public bool Plant(int plantLevel, int? startLevel,
                      YaeAnnotation inherited = YaeAnnotation.None)
    {
        if (startLevel is { } at)
            plantLevel = Math.Max(plantLevel, at + plantLevel - YaeLaw.PlantLevel);
        if (_sakura.Count >= YaeLaw.SakuraCap)
        {
            var oldest = _sakura[0];
            oldest.TurnsLeft = YaeLaw.SakuraTurns;
            oldest.Level++;
            return false;
        }
        Seq++;
        _sakura.Add(new YaeSakura
        {
            Level = plantLevel,
            TurnsLeft = YaeLaw.SakuraTurns,
            Seq = Seq,
            Annotation = HasSakuraReading(inherited) ? inherited : YaeAnnotation.None,
        });
        return true;
    }

    /// <summary>Tenko's second half: "every timer is set back to 3".</summary>
    public void Refresh()
    {
        foreach (var s in _sakura) s.TurnsLeft = YaeLaw.SakuraTurns;
    }

    /// <summary>"Each Sakura lasts 1 more turn": +n strikes on every timer.
    /// </summary>
    public void Extend(int n)
    {
        foreach (var s in _sakura) s.TurnsLeft += n;
    }

    /// <summary>"Each Sakura gains a Level": +n each, no cap.</summary>
    public void LevelUp(int n)
    {
        foreach (var s in _sakura) s.Level += n;
    }

    /// <summary>After the end-of-turn strikes every timer ticks. A Deadline
    /// Extension Sakura's timer does not tick, so it never withers. Returns
    /// the Sakura whose timers ran out, oldest first, STILL STANDING: each
    /// blooms (Last Bloom), then <see cref="Wither"/> removes it.</summary>
    public IReadOnlyList<YaeSakura> Tick()
    {
        foreach (var s in _sakura)
        {
            if (s.Annotation != YaeAnnotation.DeadlineExtension) s.TurnsLeft--;
        }
        return _sakura.Where(s => s.TurnsLeft <= 0).ToList();
    }

    /// <summary>One Sakura withers: it leaves, and Fallen Petals banks it.
    /// </summary>
    public void Wither(YaeSakura sakura)
    {
        if (_sakura.Remove(sakura)) PendingWithers++;
    }

    /// <summary>Tick, then wither the run-out ones without their bloom (the
    /// pure read; the door blooms each first). Returns how many withered.
    /// </summary>
    public int TickAndWither()
    {
        var withered = Tick();
        foreach (var s in withered) Wither(s);
        return withered.Count;
    }

    /// <summary>"Edit your newest / oldest Sakura" (<paramref name="n"/>
    /// from that end) or "Edit every Sakura" (<see cref="YaeSakuraEnd.Every"/>):
    /// the Annotation replaces any each carried. Returns how many were
    /// Edited.</summary>
    public int EditSakura(YaeSakuraEnd end, int n, YaeAnnotation annotation)
    {
        if (!YaeShrineLedger.HasSakuraReading(annotation)) return 0;
        var ordered = end == YaeSakuraEnd.Oldest
            ? _sakura.ToList()
            : Enumerable.Reverse(_sakura).ToList();
        var edited = 0;
        if (end == YaeSakuraEnd.Every) n = ordered.Count;
        foreach (var s in ordered.Take(Math.Max(0, n)))
        {
            s.Annotation = annotation;
            edited++;
        }
        return edited;
    }

    /// <summary>Offering's cards and the withers, taken at her turn start.
    /// </summary>
    internal (int Draw, int Withers) TakePending()
    {
        var owed = (PendingDraw, PendingWithers);
        PendingDraw = 0;
        PendingWithers = 0;
        return owed;
    }

    /// <summary>The three Annotations a Sakura can carry.</summary>
    public static bool HasSakuraReading(YaeAnnotation annotation) =>
        annotation is YaeAnnotation.RedInk or YaeAnnotation.FoxFire
            or YaeAnnotation.DeadlineExtension;

    /// <summary>Editor-in-Chief's Sakura: the highest Level, the oldest on a
    /// tie. Null with none standing.</summary>
    public YaeSakura? Highest() =>
        _sakura.OrderByDescending(s => s.Level).ThenBy(s => s.Seq).FirstOrDefault();

    internal void NoteStrike() => Strikes++;

    internal void NoteEdit() => Edits++;

    /// <summary>
    /// A Thunder strike's printed amount (sec.2): 2 + its Level, and Edict
    /// of Cleansing's on an enemy it applies to. The enemy's Vulnerable and
    /// Block apply later, in the hit. PURE.
    /// </summary>
    public static int StrikeDamage(int level, bool reacts, int edict) =>
        StrikeSize(YaeTenkoKind.Thunder, level, YaeAnnotation.None)
        + (reacts ? edict : 0);

    /// <summary>
    /// ONE STRIKE'S SIZE AS A TENKO KIND (shrine r2), before Edict: Thunder
    /// and Warding 2 + Level, Wildfire Level, Offering 1 card. A Red Ink
    /// Sakura's 3 adds to all but Offering (Claude, 2026-10-14). Sakura Grove
    /// and Mikage Thunder raise Levels, so no global bonus sizes a strike.
    /// PURE.
    /// </summary>
    public static int StrikeSize(YaeTenkoKind rite, int level, YaeAnnotation annotation)
    {
        var size = rite switch
        {
            YaeTenkoKind.Offering => YaeLaw.OfferingPerStrike,
            YaeTenkoKind.Wildfire => level,
            _ => YaeLaw.SakuraBase + level,
        };
        if (annotation == YaeAnnotation.RedInk && rite != YaeTenkoKind.Offering)
            size += YaeLaw.RedInkAmount;
        return size;
    }

    /// <summary>Edict of Cleansing's read: the enemy is Weak, or wears an
    /// aura an Electro strike reacts with. PURE.</summary>
    public static bool EdictApplies(bool weak, bool reacts) => weak || reacts;
}

/// <summary>
/// THE SHRINE'S DOOR: plants, strikes, Tenko, the turn's two moments and the
/// badge. Every method is a no-op for a creature that is not Yae (Varka's
/// <c>VarkaOath.Live</c> gate). Sim twin: the shrine half of
/// <c>tier0/engine/yae_shrine.py</c>.
/// </summary>
public static class YaeShrine
{
    public static bool Live(Creature? creature) => YaePrototype.IsYae(creature);

    /// <summary>The Sakura standing beside <paramref name="yae"/> (0 for
    /// anyone else).</summary>
    public static int Count(Creature? yae) =>
        yae == null || !Live(yae) ? 0 : YaeShrineLedger.For(yae).Count;

    /// <summary>The Level a Sakura is planted at: 1, plus 1 for each Fox's
    /// Mooncall (Yae review r1: "planted 1 Level higher", per copy).</summary>
    public static int PlantLevel(Creature yae) =>
        YaeLaw.PlantLevel + yae.GetPowerAmount<FoxsMooncallPower>();

    /// <summary>Do Pyro, Hydro or Cryo sit on this enemy, so an Electro strike
    /// reacts (Edict of Cleansing's read)?</summary>
    public static bool Reacts(Creature? target)
    {
        var aura = target == null ? null : AuraCmd.Find(target);
        return aura != null && aura.Element is Element.Pyro or Element.Hydro or Element.Cryo;
    }

    /// <summary>Plant <paramref name="n"/> Sakura, one at a time (with three
    /// standing, each further plant refreshes and levels the then-oldest).
    /// <paramref name="startLevel"/>: Grafted Branch.
    /// <paramref name="inherited"/>: the planting card's Red Ink, given to
    /// each NEW Sakura this plants, not to an oldest it refreshes
    /// (<see cref="YaeAnnotationReach.Inherited"/>).
    /// </summary>
    public static async Task Plant(PlayerChoiceContext choiceContext,
                                   Creature? yae, int n, int? startLevel = null,
                                   YaeAnnotation inherited = YaeAnnotation.None)
    {
        if (yae == null || !Live(yae) || n <= 0) return;
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < n; i++)
        {
            ledger.Plant(PlantLevel(yae), startLevel, inherited);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Is this enemy Weak (Edict's and Kitsune Pounce's read)?
    /// </summary>
    public static bool IsWeak(Creature? target) =>
        target != null && target.Powers.OfType<WeakPower>().Any(p => p.Amount > 0);

    /// <summary>The size of <paramref name="sakura"/>'s strike as
    /// <paramref name="rite"/> (Thunder by default), before Edict.
    /// </summary>
    public static int Size(Creature yae, YaeSakura sakura,
                           YaeTenkoKind rite = YaeTenkoKind.Thunder) =>
        YaeShrineLedger.StrikeSize(rite, sakura.Level, sakura.Annotation);

    /// <summary>The enemy a single-target strike lands on: the card's aim
    /// (Kitsune Pounce), else this turn's Lure while it lives, else one
    /// random living enemy off the combat target stream.</summary>
    private static Creature? Aim(Creature yae, Creature? aim = null)
    {
        if (aim is { IsAlive: true }) return aim;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Lure is { IsAlive: true } lured) return lured;
        var living = yae.CombatState?.HittableEnemies.Where(e => e.IsAlive).ToList();
        if (living == null || living.Count == 0) return null;
        var rng = yae.Player?.RunState.Rng.CombatTargets;
        return rng == null ? living[0] : rng.NextItem(living);
    }

    /// <summary>One damage strike's hit: Electro, a PET'S HIT (her Strength
    /// and Weak do not apply; the enemy's Vulnerable and Block do), reacting
    /// with whatever aura it lands on, credited to Yae; Edict on top.
    /// </summary>
    private static async Task Hit(PlayerChoiceContext choiceContext, Creature yae,
                                  Creature target, int size)
    {
        var damage = size + (YaeShrineLedger.EdictApplies(IsWeak(target), Reacts(target))
            ? yae.GetPowerAmount<EdictOfCleansingPower>() : 0);
        if (damage <= 0) return;
        await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, Element.Electro, damage, yae);
    }

    /// <summary>
    /// ONE SAKURA'S STRIKE AS <paramref name="rite"/> (shrine r2; Thunder
    /// unless a typed Tenko says otherwise): Thunder hits one enemy (the aim,
    /// the Lure, else random); Warding gives her Block (unpowered); Wildfire
    /// hits ALL; Offering banks a card for her next turn. Then the Sakura's
    /// own Fox Fire.
    /// </summary>
    public static async Task Strike(PlayerChoiceContext choiceContext,
                                    Creature yae, YaeSakura sakura,
                                    Creature? aim = null,
                                    YaeTenkoKind rite = YaeTenkoKind.Thunder)
    {
        if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) return;
        var ledger = YaeShrineLedger.For(yae);
        var size = Size(yae, sakura, rite);
        ledger.NoteStrike();
        switch (rite)
        {
            case YaeTenkoKind.Thunder:
                if (Aim(yae, aim) is { } target) await Hit(choiceContext, yae, target, size);
                break;
            case YaeTenkoKind.Warding:
                if (size > 0) await CreatureCmd.GainBlock(yae, size, ValueProp.Unpowered, null);
                break;
            case YaeTenkoKind.Wildfire:
                foreach (var enemy in yae.CombatState!.HittableEnemies.Where(e => e.IsAlive).ToList())
                {
                    await Hit(choiceContext, yae, enemy, size);
                }
                break;
            case YaeTenkoKind.Offering:
                ledger.PendingDraw += size;
                break;
        }
        if (sakura.Annotation == YaeAnnotation.FoxFire)
        {
            await FoxFire(choiceContext, yae);
        }
    }

    /// <summary>Every Sakura strikes as <paramref name="rite"/>, oldest
    /// first, while an enemy lives.</summary>
    public static async Task StrikeAll(PlayerChoiceContext choiceContext,
                                       Creature yae,
                                       YaeTenkoKind rite = YaeTenkoKind.Thunder)
    {
        foreach (var sakura in YaeShrineLedger.For(yae).Standing.ToList())
        {
            if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) break;
            await Strike(choiceContext, yae, sakura, null, rite);
        }
    }

    /// <summary>
    /// TENKO (shrine r2, ruled 2026-10-14): every Sakura strikes now, oldest
    /// first, as <paramref name="kind"/>: plain Tenko as Thunder, "Tenko
    /// (Warding)" as Block, "Tenko (Wildfire)" its Level to ALL, "Tenko
    /// (Offering)" a card next turn. Then every timer is set back to 3
    /// ([USER], 2026-10-14: "make Tenko keep resetting the duration").
    /// Tenko with no Sakura does nothing.
    /// </summary>
    public static async Task Tenko(PlayerChoiceContext choiceContext, Creature? yae,
                                   YaeTenkoKind kind = YaeTenkoKind.Thunder)
    {
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return;
        await StrikeAll(choiceContext, yae, kind);
        ledger.Refresh();
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Fox Fire's play rider: 4 Electro to a random enemy, a pet's
    /// hit. Not aimed by the Lure (the Lure aims the Sakura).</summary>
    public static async Task FoxFire(PlayerChoiceContext choiceContext, Creature? owner)
    {
        if (owner?.CombatState == null) return;
        var living = owner.CombatState.HittableEnemies.Where(e => e.IsAlive).ToList();
        if (living.Count == 0) return;
        var rng = owner.Player?.RunState.Rng.CombatTargets;
        var target = rng == null ? living[0] : rng.NextItem(living);
        await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, Element.Electro, YaeLaw.FoxFireDamage, owner);
    }

    /// <summary>
    /// Her turn start, after the draw (<c>KleeElementalHooks.AfterPlayerTurnStart</c>,
    /// the sim's <c>yae_shrine.turn_start</c> site): the Lure expires, then
    /// Yakan Offering plants, then Sakura Grove levels every Sakura (shrine
    /// r2).
    /// </summary>
    public static async Task TurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        var yae = player.Creature;
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        ledger.Lure = null;
        await FoxfireLurePower.ClearAll(yae);
        // Offering's cards and Fallen Petals' Energy (and draw), owed since
        // the end of her last turn.
        var (draw, withers) = ledger.TakePending();
        var petals = yae.GetPowerAmount<FallenPetalsPower>();
        var petalsPlus = yae.GetPowerAmount<FallenPetalsPlusPower>();
        var energy = withers * (petals + petalsPlus);
        draw += withers * petalsPlus;
        if (energy > 0)
        {
            await PlayerCmd.GainEnergy(energy, player);
        }
        if (draw > 0)
        {
            await CardPileCmd.Draw(choiceContext, draw, player);
        }
        var offering = yae.GetPowerAmount<YakanOfferingPower>();
        if (offering > 0)
        {
            yae.Powers.OfType<YakanOfferingPower>().FirstOrDefault()?.Pulse();
            await Plant(choiceContext, yae, offering);
        }
        var grove = yae.GetPowerAmount<SakuraGrovePower>();
        if (grove > 0 && ledger.Count > 0)
        {
            yae.Powers.OfType<SakuraGrovePower>().FirstOrDefault()?.Pulse();
            ledger.LevelUp(grove);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// Her turn end (<c>KleeElementalHooks.BeforeSideTurnEnd</c>, the sim's
    /// <c>yae_shrine.turn_end</c> site): the strikes, then every timer ticks.
    /// LAST BLOOM (Yae review r1, pick 1 (a), ruled 2026-10-14): each Sakura
    /// whose timer ran out, oldest first, strikes once more as Thunder (a
    /// normal strike), THEN withers -- so Fallen Petals banks it after the
    /// bloom.
    /// </summary>
    public static async Task TurnEnd(PlayerChoiceContext choiceContext, Creature yae)
    {
        if (!Live(yae)) return;
        await StrikeAll(choiceContext, yae);
        await TickAndBloom(choiceContext, yae);
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>The timers tick; each run-out Sakura blooms, then withers.
    /// </summary>
    public static async Task TickAndBloom(PlayerChoiceContext choiceContext, Creature yae)
    {
        var ledger = YaeShrineLedger.For(yae);
        foreach (var sakura in ledger.Tick())
        {
            await Strike(choiceContext, yae, sakura);
            ledger.Wither(sakura);
        }
    }

    /// <summary>
    /// After an Annotated card's own effects and its Annotation's:
    /// Serialization (shrine r2, "Whenever you play an Annotated card, gain 3
    /// Block"), then Editor-in-Chief, "a Sakura strikes (the highest
    /// Level)", once per stack.
    /// </summary>
    public static async Task AfterCardPlayed(PlayerChoiceContext choiceContext,
                                             CardPlay cardPlay)
    {
        var yae = cardPlay.Card?.Owner?.Creature;
        if (yae == null || !Live(yae)) return;
        if (!YaeEditing.IsAnnotated(cardPlay.Card)) return;
        await SerializationPower.Pay(yae, 1);
        var stacks = yae.GetPowerAmount<EditorInChiefPower>();
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < stacks; i++)
        {
            if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) return;
            var sakura = ledger.Highest();
            if (sakura == null) return;
            await Strike(choiceContext, yae, sakura);
        }
    }

    /// <summary>Kitsune Pounce: "If the enemy is Weak, a Sakura strikes it"
    /// -- the highest Level, as Thunder, aimed at it.</summary>
    public static async Task StrikeIfWeak(PlayerChoiceContext choiceContext,
                                          Creature? yae, Creature? target)
    {
        if (yae == null || !Live(yae)) return;
        if (target is not { IsAlive: true } || !IsWeak(target)) return;
        var sakura = YaeShrineLedger.For(yae).Highest();
        if (sakura == null) return;
        await Strike(choiceContext, yae, sakura, target);
    }
}

/// <summary>
/// THE LIVE TENKO CLAUSE (shrine r2, 2026-10-14; it replaces review r1's
/// "Rite: X (your Sakura: ...)" line). A Tenko card's face carries
/// <c>{InCombat:{YaeTenko}|}</c>: right after "Tenko" on a plain Tenko,
/// inside the brackets on a typed one. In combat it says what the Tenko would
/// do now, summed over the Sakura standing: "Tenko (12 damage)", "Tenko
/// (Warding: 12 Block)"; with none standing "Tenko (no Sakura)", "Tenko
/// (Warding, no Sakura)". Empty off a combat, on a canonical card, and for
/// anyone but a live Yae. The Tenko's own job only: before Edict and Fox
/// Fire. Display only. Sim twin: <c>yae_shrine.tenko_line</c>.
/// </summary>
public static class YaeShrineFace
{
    /// <summary>The description token a Tenko clause rides on.</summary>
    public const string TenkoToken = "YaeTenko";

    /// <summary>A plain Tenko's clause with no Sakura standing.</summary>
    public const string NoSakura = " (no Sakura)";

    /// <summary>A typed Tenko's clause with no Sakura standing, inside its
    /// brackets.</summary>
    public const string NoSakuraTyped = ", no Sakura";

    /// <summary>A Tenko card's live clause.</summary>
    public static string TenkoLine(CardModel? card,
                                   YaeTenkoKind kind = YaeTenkoKind.Thunder) =>
        Owner(card) is { } yae ? TenkoWords(kind, Total(yae, kind)) : "";

    /// <summary>What every Sakura standing beside <paramref name="yae"/>
    /// would strike for as <paramref name="kind"/>, summed.</summary>
    public static int Total(Creature yae, YaeTenkoKind kind) =>
        YaeShrineLedger.For(yae).Standing.Sum(s => YaeShrine.Size(yae, s, kind));

    /// <summary>The same sum off the numbers alone. PURE.</summary>
    public static int Total(IEnumerable<YaeSakura> standing, YaeTenkoKind kind) =>
        standing.Sum(s => YaeShrineLedger.StrikeSize(kind, s.Level, s.Annotation));

    /// <summary>The clause for a total: " (12 damage)" or ": 12 Block"; at
    /// 0, which is no Sakura standing, the "no Sakura" words. PURE.</summary>
    public static string TenkoWords(YaeTenkoKind kind, int total)
    {
        var typed = kind != YaeTenkoKind.Thunder;
        if (total <= 0) return typed ? NoSakuraTyped : NoSakura;
        var what = Amount(kind, total.ToString(System.Globalization.CultureInfo.InvariantCulture));
        return typed ? $": {what}" : $" ({what})";
    }

    /// <summary>What a Tenko of <paramref name="kind"/> does, for a number
    /// written as <paramref name="n"/>: "5 damage", "5 Block", "5 to ALL",
    /// "draw 5". PURE.</summary>
    public static string Amount(YaeTenkoKind kind, string n) => kind switch
    {
        YaeTenkoKind.Warding => $"{n} Block",
        YaeTenkoKind.Wildfire => $"{n} to ALL",
        YaeTenkoKind.Offering => $"draw {n}",
        _ => $"{n} damage",
    };

    private static Creature? Owner(CardModel? card)
    {
        Creature? owner;
        try
        {
            owner = global::KleeMod.Cards.TipOwner.CreatureOf(card);
        }
        catch (Exception)
        {
            return null;
        }
        return owner?.CombatState != null && YaeShrine.Live(owner) ? owner : null;
    }
}

/// <summary>
/// YAE'S CARD VERBS (the sheet's `yae` op): one method per `kind`, each
/// called as <c>await YaeCards.Kind(choiceContext, this, cardPlay)</c> by the
/// generated card, reading its own numbers off the card's `Ym*` vars. Sim
/// twins: <c>yae_shrine.op_yae</c>'s kinds.
/// </summary>
public static class YaeCards
{
    /// <summary>A card's `Ym*` number. A row's count of 1 and base of 0
    /// carry no var (`gen_klee_cards.YAE_FIELD_DEFAULTS`), so a missing
    /// YmAmount reads 1 and a missing YmBase or YmPer reads 0.</summary>
    private static int Var(CardModel card, string name) =>
        card.DynamicVars.TryGetValue(name, out var v) ? (int)v.BaseValue
            : name == "YmAmount" ? 1 : 0;

    /// <summary>"Plant a Sakura" / "Plant 2 Sakura". Red Ink on a card that
    /// only plants passes to each Sakura planted (ruled 2026-10-14).</summary>
    public static Task Plant(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, Var(card, "YmAmount"),
                        null, YaeAnnotationReach.Inherited(card));

    /// <summary>"Tenko." (Thunder).</summary>
    public static Task Tenko(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        YaeShrine.Tenko(choiceContext, card.Owner?.Creature);

    /// <summary>"Tenko (Warding)", "Tenko (Wildfire)", "Tenko (Offering)"
    /// (shrine r2: they replace "Rite: X").</summary>
    public static Task Tenko(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay, YaeTenkoKind kind) =>
        YaeShrine.Tenko(choiceContext, card.Owner?.Creature, kind);

    /// <summary>Shrine Offering: "Each Sakura lasts 1 more turn."</summary>
    public static async Task Extend(PlayerChoiceContext choiceContext,
                                    CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).Extend(Var(card, "YmAmount"));
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Rooted Shrine, Mikage Thunder: "Each Sakura gains a Level"
    /// (YmAmount Levels; no cap).</summary>
    public static async Task LevelUp(PlayerChoiceContext choiceContext,
                                     CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).LevelUp(Var(card, "YmAmount"));
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>"Edit a card in your hand: &lt;Annotation&gt;" (amount
    /// times).</summary>
    public static Task Edit(PlayerChoiceContext choiceContext, CardModel card,
                            CardPlay cardPlay, YaeAnnotation annotation) =>
        YaeEditing.Edit(choiceContext, card, annotation, Var(card, "YmAmount"));

    /// <summary>Reborn as Guuji Yae.</summary>
    public static Task EditAll(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay, YaeAnnotation annotation) =>
        YaeEditing.EditAll(choiceContext, card, annotation);

    /// <summary>The Seven Glamours.</summary>
    public static Task Publish(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        YaeEditing.PublishFromHand(choiceContext, card);

    /// <summary>Foxfire Lure: "This turn, your Sakura strike it."</summary>
    public static async Task Lure(PlayerChoiceContext choiceContext,
                                  CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        if (cardPlay.Target is not { IsAlive: true } target) return;
        YaeShrineLedger.For(yae).Lure = target;
        await FoxfireLurePower.Mark(choiceContext, yae, target);
    }

    /// <summary>Thunderbolt Tithe: base + per for each Sakura standing, one
    /// powered Electro hit of the card.</summary>
    public static Task DamagePerSakura(PlayerChoiceContext choiceContext,
                                       CardModel card, CardPlay cardPlay) =>
        CardHit(choiceContext, card, cardPlay,
                Var(card, "YmBase") + Var(card, "YmPer") * YaeShrine.Count(card.Owner?.Creature));

    /// <summary>Shrine Maiden's Guard: base + per for each Sakura standing,
    /// the card's own Block.</summary>
    public static Task BlockPerSakura(PlayerChoiceContext choiceContext,
                                      CardModel card, CardPlay cardPlay) =>
        CardBlock(card, cardPlay,
                  Var(card, "YmBase") + Var(card, "YmPer") * YaeShrine.Count(card.Owner?.Creature));

    /// <summary>Bestseller: base + per for each Annotated card in hand, the
    /// card itself counted when Annotated.</summary>
    public static Task DamagePerAnnotated(PlayerChoiceContext choiceContext,
                                          CardModel card, CardPlay cardPlay) =>
        CardHit(choiceContext, card, cardPlay,
                Var(card, "YmBase") + Var(card, "YmPer") * YaeEditing.AnnotatedInHand(card));

    /// <summary>Print Run: base + per for each Annotated card in hand.
    /// </summary>
    public static Task BlockPerAnnotated(PlayerChoiceContext choiceContext,
                                         CardModel card, CardPlay cardPlay) =>
        CardBlock(card, cardPlay,
                  Var(card, "YmBase") + Var(card, "YmPer") * YaeEditing.AnnotatedInHand(card));

    /// <summary>Kitsune Flash: base, and amount more if this card is
    /// Annotated.</summary>
    public static Task AnnotatedStrike(PlayerChoiceContext choiceContext,
                                       CardModel card, CardPlay cardPlay) =>
        CardHit(choiceContext, card, cardPlay,
                Var(card, "YmBase")
                + (YaeEditing.IsAnnotated(card) ? Var(card, "YmAmount") : 0));

    /// <summary>"Edit your newest / oldest Sakura: X" (YmAmount from that
    /// end; Fox Fire Draft's upgrade takes the newest three, every Sakura),
    /// "Edit every Sakura: X".</summary>
    public static async Task EditSakura(PlayerChoiceContext choiceContext, CardModel card,
                                        CardPlay cardPlay, YaeSakuraEnd end,
                                        YaeAnnotation annotation)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).EditSakura(end, Var(card, "YmAmount"), annotation);
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Grafted Branch: "Plant a Sakura. It starts at Level 2 [3]."
    /// </summary>
    public static Task PlantLevel(PlayerChoiceContext choiceContext, CardModel card,
                                  CardPlay cardPlay) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, 1, Var(card, "YmAmount"),
                        YaeAnnotationReach.Inherited(card));

    /// <summary>Kitsune Pounce's rider.</summary>
    public static Task StrikeIfWeak(PlayerChoiceContext choiceContext, CardModel card,
                                    CardPlay cardPlay) =>
        YaeShrine.StrikeIfWeak(choiceContext, card.Owner?.Creature, cardPlay.Target);

    /// <summary>The `fox_fire` kind (Fox Fire's rider as a verb).</summary>
    public static Task FoxFire(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        YaeShrine.FoxFire(choiceContext, card.Owner?.Creature);

    /// <summary>
    /// ONE POWERED HIT OF THE CARD, carrying Electro (the sim's reading:
    /// "`damage_per_sakura` and `damage_per_annotated` are ONE powered hit of
    /// the card (Strength counts, flat Attack riders ride it) carrying
    /// Electro"). Red Ink rides it through the engine's enchant door.
    /// </summary>
    private static async Task CardHit(PlayerChoiceContext choiceContext,
                                      CardModel card, CardPlay cardPlay,
                                      int damage)
    {
        if (cardPlay.Target is not { IsAlive: true } target || damage <= 0) return;
        using (HitElement.Carry(card, Element.Electro))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .Targeting(target)
                .WithElementHitFx(Element.Electro)
                .Execute(choiceContext);
        }
    }

    /// <summary>The card's own Block (Dexterity, Frail and Red Ink read it).
    /// </summary>
    private static async Task CardBlock(CardModel card, CardPlay cardPlay, int amount)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || amount <= 0) return;
        await CreatureCmd.GainBlock(owner, amount, ValueProp.Move, cardPlay);
    }
}
