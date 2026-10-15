using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
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

/// <summary>
/// THE SAKURA KINDS (review r3, ruled 2026-10-14,
/// <c>review/active/yae-review-r3-2026-10-14.md</c> sec.1). Set when a
/// Sakura is planted. A Sakura (Thunder, the default) strikes an enemy for
/// 2 + its Level; a Foxfire Sakura hits ALL enemies for 1 + its Level; a
/// Kitsune Sakura, the decoy, gives Yae 2 + its Level Block ("Yae does not
/// shield. A fox illusion draws the blow."). Sim twin:
/// <c>yae_shrine.SAKURA_KINDS</c>.
/// </summary>
public enum YaeSakuraKind
{
    Thunder = 0,
    Foxfire = 1,
    Kitsune = 2,
}

/// <summary>The end an "Edit your newest / oldest Sakura" counts from, or
/// "Edit every Sakura".</summary>
public enum YaeSakuraEnd
{
    Newest = 0,
    Oldest = 1,
    Every = 2,
}

/// <summary>One Sesshou Sakura: its kind, its Level (and the Level it was
/// planted at, so the display can say where the rest came from), the
/// actions it has left, its place in planting order (the ledger's clock),
/// and the one Annotation it may carry (Red Ink, Fox Fire or Deadline
/// Extension).</summary>
public sealed class YaeSakura
{
    public YaeSakuraKind Kind { get; internal set; }

    public int Level { get; internal set; }

    public int PlantedLevel { get; internal set; }

    public int TurnsLeft { get; internal set; }

    public int Seq { get; internal set; }

    public YaeAnnotation Annotation { get; internal set; }

    /// <summary>Yae review r4, item 4: a Deadline Extension Edit that keeps
    /// the Sakura's Red Ink leaves the +3 on it.</summary>
    public bool KeepsRedInk { get; internal set; }
}

/// <summary>
/// YAE'S SHRINE, ONE FIGHT'S WORTH (paper sec.2, "Sakura"). PURE -- no
/// command runs here -- so the headless suite pins every reading by value;
/// <see cref="YaeShrine"/> is the door that acts and pays the powers.
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

    /// <summary>Actions made this combat (telemetry, the seat page).</summary>
    public int Strikes { get; private set; }

    /// <summary>Edits made this combat.</summary>
    public int Edits { get; private set; }

    /// <summary>
    /// PLANT ONE: a new Sakura of <paramref name="kind"/> at
    /// <paramref name="plantLevel"/> with <see cref="YaeLaw.SakuraTurns"/>
    /// actions left; the others are NOT levelled. Returns whether a Sakura
    /// was added (a full-shrine plant of the oldest's kind adds none).
    /// </summary>
    public bool Plant(int plantLevel) => Plant(plantLevel, null);

    /// <summary>
    /// Plant one, starting at <paramref name="startLevel"/> where a card
    /// says so (Grafted Branch), raised as every plant is by Fox's Mooncall
    /// (its bonus is <paramref name="plantLevel"/> over
    /// <see cref="YaeLaw.PlantLevel"/>); never below the plant Level.
    /// <paramref name="inherited"/>: the Annotation each NEW Sakura carries
    /// from the card that planted it (Red Ink, <see cref="YaeAnnotationReach"/>).
    /// <paramref name="cap"/>: how many may stand (<see cref="YaeShrine.MaxSakura"/>).
    ///
    /// FULL SHRINE (review r3, amended after GPT's review; the door has
    /// already made the oldest act): the SAME KIND as the oldest refreshes it
    /// (to at least <see cref="YaeLaw.SakuraTurns"/>) and gives it a Level,
    /// and none is added; ANOTHER KIND withers the oldest and the new Sakura
    /// takes its place, as the newest, at its printed Level.
    /// </summary>
    public bool Plant(int plantLevel, int? startLevel,
                                YaeAnnotation inherited = YaeAnnotation.None,
                                int cap = YaeLaw.SakuraCap,
                                YaeSakuraKind kind = YaeSakuraKind.Thunder)
    {
        if (startLevel is { } at)
            plantLevel = Math.Max(plantLevel, at + plantLevel - YaeLaw.PlantLevel);
        if (_sakura.Count >= cap && _sakura.Count > 0)
        {
            var oldest = _sakura[0];
            if (oldest.Kind == kind)
            {
                oldest.TurnsLeft = Math.Max(oldest.TurnsLeft, YaeLaw.SakuraTurns);
                oldest.Level++;
                // Yae review r4, item 2: the planting card's Red Ink goes to
                // the refreshed Sakura, as it would to a new one.
                if (HasSakuraReading(inherited))
                {
                    oldest.Annotation = inherited;
                    oldest.KeepsRedInk = false;
                }
                return false;
            }
            _sakura.RemoveAt(0);          // another kind: it withers
        }
        Seq++;
        _sakura.Add(new YaeSakura
        {
            Kind = kind,
            Level = plantLevel,
            PlantedLevel = plantLevel,
            TurnsLeft = YaeLaw.SakuraTurns,
            Seq = Seq,
            Annotation = HasSakuraReading(inherited) ? inherited : YaeAnnotation.None,
        });
        return true;
    }

    /// <summary>Tenko's second half: every timer is refreshed to at least
    /// 3, never shortened.</summary>
    public void Refresh()
    {
        foreach (var s in _sakura) s.TurnsLeft = Math.Max(s.TurnsLeft, YaeLaw.SakuraTurns);
    }

    /// <summary>"Each Sakura lasts 1 more turn": +n on every timer.</summary>
    public void Extend(int n)
    {
        foreach (var s in _sakura) s.TurnsLeft += n;
    }

    /// <summary>"Each Sakura gains a Level": +n each, no cap.</summary>
    public void LevelUp(int n)
    {
        foreach (var s in _sakura) s.Level += n;
    }

    /// <summary>After the end-of-turn actions every timer ticks. A Deadline
    /// Extension Sakura's timer does not tick. Returns the Sakura whose
    /// timers ran out, oldest first, STILL STANDING: each blooms (Last
    /// Bloom), then <see cref="Wither"/> removes it.</summary>
    public IReadOnlyList<YaeSakura> Tick()
    {
        foreach (var s in _sakura)
        {
            if (s.Annotation != YaeAnnotation.DeadlineExtension) s.TurnsLeft--;
        }
        return _sakura.Where(s => s.TurnsLeft <= 0).ToList();
    }

    /// <summary>One Sakura withers: it leaves. Whether it stood.</summary>
    public bool Wither(YaeSakura sakura) => _sakura.Remove(sakura);

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
    /// from that end) or "Edit every Sakura": the Annotation replaces any
    /// each carried. Returns how many were Edited.</summary>
    public int EditSakura(YaeSakuraEnd end, int n, YaeAnnotation annotation,
                          bool keepRedInk = false)
    {
        if (!HasSakuraReading(annotation)) return 0;
        var ordered = end == YaeSakuraEnd.Oldest
            ? _sakura.ToList()
            : Enumerable.Reverse(_sakura).ToList();
        var edited = 0;
        if (end == YaeSakuraEnd.Every) n = ordered.Count;
        foreach (var s in ordered.Take(Math.Max(0, n)))
        {
            var hadRed = s.Annotation == YaeAnnotation.RedInk || s.KeepsRedInk;
            s.Annotation = annotation;
            s.KeepsRedInk = keepRedInk && hadRed && annotation != YaeAnnotation.RedInk;
            edited++;
        }
        return edited;
    }

    /// <summary>The three Annotations a Sakura can carry.</summary>
    public static bool HasSakuraReading(YaeAnnotation annotation) =>
        annotation is YaeAnnotation.RedInk or YaeAnnotation.FoxFire
            or YaeAnnotation.DeadlineExtension;

    /// <summary>The highest-Level Sakura, the oldest on a tie; with
    /// <paramref name="damageOnly"/>, a Sakura or Foxfire Sakura only
    /// (Kitsune Pounce's "strikes it"). Null with none.</summary>
    public YaeSakura? Highest(bool damageOnly = false) =>
        _sakura.Where(s => !damageOnly || DealsDamage(s.Kind))
            .OrderByDescending(s => s.Level).ThenBy(s => s.Seq).FirstOrDefault();

    internal void NoteStrike() => Strikes++;

    internal void NoteEdit() => Edits++;

    /// <summary>Does this kind deal damage (Edict, the Lure)? PURE.</summary>
    public static bool DealsDamage(YaeSakuraKind kind) => kind != YaeSakuraKind.Kitsune;

    /// <summary>What a kind adds to its Level: Thunder 2, Foxfire 1,
    /// Kitsune 2 (<see cref="YaeLaw"/>). PURE.</summary>
    public static int KindBase(YaeSakuraKind kind) => kind switch
    {
        YaeSakuraKind.Foxfire => YaeLaw.FoxfireBase,
        YaeSakuraKind.Kitsune => YaeLaw.KitsuneBase,
        _ => YaeLaw.SakuraBase,
    };

    /// <summary>
    /// ONE ACTION'S SIZE (review r3), before Edict: damage for a Sakura,
    /// each enemy's damage for a Foxfire Sakura, Block for a Kitsune Sakura;
    /// a Red Ink Sakura's 3 adds to any kind. PURE.
    /// </summary>
    public static int ActSize(YaeSakuraKind kind, int level, YaeAnnotation annotation,
                              bool keptRedInk = false) =>
        KindBase(kind) + level
        + (annotation == YaeAnnotation.RedInk || keptRedInk ? YaeLaw.RedInkAmount : 0);

    /// <summary>A Sakura (Thunder) strike's printed amount at an enemy:
    /// 2 + its Level, and Edict of Cleansing's when it applies. PURE.
    /// </summary>
    public static int StrikeDamage(int level, bool reacts, int edict) =>
        ActSize(YaeSakuraKind.Thunder, level, YaeAnnotation.None)
        + (reacts ? edict : 0);

    /// <summary>Edict of Cleansing's read: the enemy is Weak, or wears an
    /// aura an Electro strike reacts with. PURE.</summary>
    public static bool EdictApplies(bool weak, bool reacts) => weak || reacts;
}

/// <summary>
/// THE SHRINE'S DOOR: plants, actions, Tenko, the turn's two moments and the
/// badges. Every method is a no-op for a creature that is not Yae (Varka's
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
    /// Mooncall.</summary>
    public static int PlantLevel(Creature yae) =>
        YaeLaw.PlantLevel + yae.GetPowerAmount<FoxsMooncallPower>();

    /// <summary>How many Sakura may stand beside <paramref name="yae"/>: 3,
    /// plus Sakura Channeling's amount. Sim twin: <c>yae_shrine.sakura_cap</c>.
    /// </summary>
    public static int MaxSakura(Creature yae) =>
        YaeLaw.SakuraCap + yae.GetPowerAmount<SakuraChannelingPower>();

    /// <summary>Do Pyro, Hydro or Cryo sit on this enemy, so an Electro strike
    /// reacts (Edict of Cleansing's read)?</summary>
    public static bool Reacts(Creature? target)
    {
        var aura = target == null ? null : AuraCmd.Find(target);
        return aura != null && aura.Element is Element.Pyro or Element.Hydro or Element.Cryo;
    }

    /// <summary>
    /// Plant <paramref name="n"/> Sakura of <paramref name="kind"/>, one at a
    /// time. With the shrine full (<see cref="MaxSakura"/>), each further
    /// plant makes the then-oldest ACT first, exactly as its Last Bloom
    /// would; then the ledger levels it (same kind) or withers it and
    /// plants the new one in its place (another kind; review r3).
    /// <paramref name="startLevel"/>: Grafted Branch.
    /// <paramref name="inherited"/>: the planting card's Red Ink, given to
    /// each NEW Sakura this plants.
    /// </summary>
    public static async Task Plant(PlayerChoiceContext choiceContext,
                                   Creature? yae, int n, int? startLevel = null,
                                   YaeAnnotation inherited = YaeAnnotation.None,
                                   YaeSakuraKind kind = YaeSakuraKind.Thunder)
    {
        if (yae == null || !Live(yae) || n <= 0) return;
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < n; i++)
        {
            var cap = MaxSakura(yae);
            if (ledger.Count >= cap && ledger.Count > 0)
            {
                await Act(choiceContext, yae, ledger.Standing[0]);
            }
            ledger.Plant(PlantLevel(yae), startLevel, inherited, cap, kind);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Is this enemy Weak (Edict's and Kitsune Pounce's read)?
    /// </summary>
    public static bool IsWeak(Creature? target) =>
        target != null && target.Powers.OfType<WeakPower>().Any(p => p.Amount > 0);

    /// <summary>The size of <paramref name="sakura"/>'s action, before Edict.
    /// </summary>
    public static int Size(Creature yae, YaeSakura sakura) =>
        YaeShrineLedger.ActSize(sakura.Kind, sakura.Level, sakura.Annotation, sakura.KeepsRedInk);

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

    /// <summary>One damage action's hit: Electro, a PET'S HIT (her Strength
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
    /// ONE SAKURA ACTS AS ITS KIND (review r3, ruled 2026-10-14): a Sakura
    /// strikes one enemy (the aim, the Lure, else random) for 2 + its Level;
    /// a Foxfire Sakura hits ALL enemies for 1 + its Level; a Kitsune Sakura
    /// gives her 2 + its Level Block (unpowered). Red Ink adds 3 to any of
    /// them. Then the Sakura's own Fox Fire, once.
    /// </summary>
    public static async Task Act(PlayerChoiceContext choiceContext,
                                 Creature yae, YaeSakura sakura,
                                 Creature? aim = null)
    {
        if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) return;
        var ledger = YaeShrineLedger.For(yae);
        ledger.NoteStrike();
        var size = Size(yae, sakura);
        switch (sakura.Kind)
        {
            case YaeSakuraKind.Kitsune:
                if (size > 0) await CreatureCmd.GainBlock(yae, size, ValueProp.Unpowered, null);
                break;
            case YaeSakuraKind.Foxfire:
                foreach (var enemy in yae.CombatState!.HittableEnemies.Where(e => e.IsAlive).ToList())
                {
                    await Hit(choiceContext, yae, enemy, size);
                }
                break;
            default:
                if (Aim(yae, aim) is { } target) await Hit(choiceContext, yae, target, size);
                break;
        }
        if (sakura.Annotation == YaeAnnotation.FoxFire)
        {
            await FoxFire(choiceContext, yae);
        }
    }

    /// <summary>Every Sakura acts, oldest first, while an enemy lives.
    /// </summary>
    public static async Task ActAll(PlayerChoiceContext choiceContext, Creature yae)
    {
        foreach (var sakura in YaeShrineLedger.For(yae).Standing.ToList())
        {
            if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) break;
            await Act(choiceContext, yae, sakura);
        }
    }

    /// <summary>
    /// TENKO (review r3, ruled 2026-10-14): one plain rule again. "Every
    /// Sakura acts now. Refresh them to at least 3 turns." The mix of kinds
    /// planted decides whether it is damage, AoE or Block. Tenko with no
    /// Sakura does nothing.
    /// </summary>
    public static async Task Tenko(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return;
        await ActAll(choiceContext, yae);
        ledger.Refresh();
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// FALLEN PETALS (review r3, sec.4): "Your oldest Sakura withers (it acts
    /// once, its Last Bloom)." Deadline Extension does not stop it (an
    /// active wither, not a timer). Whether one did.
    /// </summary>
    public static async Task<bool> WitherOldest(PlayerChoiceContext choiceContext,
                                                Creature? yae)
    {
        if (yae == null || !Live(yae)) return false;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return false;
        var oldest = ledger.Standing[0];
        await Act(choiceContext, yae, oldest);
        var withered = ledger.Wither(oldest);
        await SakuraBadge.Sync(choiceContext, yae);
        return withered;
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
    /// Serial Novel brings back an Annotated card per stack, then Yakan
    /// Offering plants, then Sakura Grove levels every Sakura.
    /// </summary>
    public static async Task TurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        var yae = player.Creature;
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        ledger.Lure = null;
        await FoxfireLurePower.ClearAll(yae);
        var serial = yae.GetPowerAmount<SerialNovelPower>();
        if (serial > 0)
        {
            yae.Powers.OfType<SerialNovelPower>().FirstOrDefault()?.Pulse();
            await YaeEditing.RecallRandomAnnotated(player, serial);
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
    /// <c>yae_shrine.turn_end</c> site): every Sakura acts, then every timer
    /// ticks. LAST BLOOM: each Sakura whose timer ran out, oldest first, acts
    /// once more, THEN withers.
    /// </summary>
    public static async Task TurnEnd(PlayerChoiceContext choiceContext, Creature yae)
    {
        if (!Live(yae)) return;
        await ActAll(choiceContext, yae);
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
            await Act(choiceContext, yae, sakura);
            ledger.Wither(sakura);
        }
    }

    /// <summary>
    /// After an Annotated card's own effects and its Annotations':
    /// Serialization ("Whenever you play an Annotated card, gain 3 Block"),
    /// then Editor-in-Chief, "a Sakura strikes": the highest-Level Sakura
    /// acts as its kind, once per stack (review r3, the builder's reading).
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
            await Act(choiceContext, yae, sakura);
        }
    }

    /// <summary>Kitsune Pounce: "If the enemy is Weak, a Sakura strikes it"
    /// -- the highest-Level Sakura that deals damage (a Sakura or a Foxfire
    /// Sakura), aimed at it (review r3, the builder's reading).</summary>
    public static async Task StrikeIfWeak(PlayerChoiceContext choiceContext,
                                          Creature? yae, Creature? target)
    {
        if (yae == null || !Live(yae)) return;
        if (target is not { IsAlive: true } || !IsWeak(target)) return;
        var sakura = YaeShrineLedger.For(yae).Highest(damageOnly: true);
        if (sakura == null) return;
        await Act(choiceContext, yae, sakura, target);
    }
}

/// <summary>
/// THE LIVE TENKO CLAUSE. A Tenko card's face carries
/// <c>{InCombat:{YaeTenko}|}</c> right after "Tenko". In combat it says
/// what the Tenko would do now, summed by kind over the Sakura standing
/// (review r3): "Tenko (8 damage, 4 to each enemy, 5 Block)", a kind with
/// none standing left out; with none at all "Tenko (no Sakura)". Empty off
/// a combat, on a canonical card, and for anyone but a live Yae. The
/// Tenko's own job only: before Edict and Fox Fire. Display only. Sim twin:
/// <c>yae_shrine.tenko_line</c>.
/// </summary>
public static class YaeShrineFace
{
    /// <summary>The description token a Tenko clause rides on.</summary>
    public const string TenkoToken = "YaeTenko";

    /// <summary>The clause with no Sakura standing.</summary>
    public const string NoSakura = " (no Sakura)";

    /// <summary>A Tenko card's live clause.</summary>
    public static string TenkoLine(CardModel? card) =>
        Owner(card) is { } yae
            ? TenkoWords(Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Thunder),
                         Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Foxfire),
                         Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Kitsune))
            : "";

    /// <summary>What every Sakura of <paramref name="kind"/> would do,
    /// summed, off the numbers alone. PURE.</summary>
    public static int Total(IEnumerable<YaeSakura> standing, YaeSakuraKind kind) =>
        standing.Where(s => s.Kind == kind)
            .Sum(s => YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotation, s.KeepsRedInk));

    /// <summary>The clause for each kind's sum, in kind order, zeros left
    /// out: " (8 damage, 4 to each enemy, 5 Block)"; all zero is the "no
    /// Sakura" words. PURE.</summary>
    public static string TenkoWords(int damage, int toEach = 0, int block = 0)
    {
        var parts = new List<string>();
        if (damage > 0) parts.Add(Amount(YaeSakuraKind.Thunder, N(damage)));
        if (toEach > 0) parts.Add(Amount(YaeSakuraKind.Foxfire, N(toEach)));
        if (block > 0) parts.Add(Amount(YaeSakuraKind.Kitsune, N(block)));
        return parts.Count == 0 ? NoSakura : $" ({string.Join(", ", parts)})";
    }

    private static string N(int n) =>
        n.ToString(System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>What a kind's action does, for a number written as
    /// <paramref name="n"/>: "5 damage", "5 to each enemy", "5 Block". PURE.
    /// </summary>
    public static string Amount(YaeSakuraKind kind, string n) => kind switch
    {
        YaeSakuraKind.Kitsune => $"{n} Block",
        YaeSakuraKind.Foxfire => $"{n} to each enemy",
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
    /// plants passes to each Sakura planted.</summary>
    public static Task Plant(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        Plant(choiceContext, card, cardPlay, YaeSakuraKind.Thunder);

    /// <summary>"Plant a Foxfire Sakura", "Plant a Kitsune Sakura" (review
    /// r3: the kind is the row's `as:`).</summary>
    public static Task Plant(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay, YaeSakuraKind kind) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, Var(card, "YmAmount"),
                        null, YaeAnnotationReach.Inherited(card), kind);

    /// <summary>"Tenko." (review r3: one plain rule).</summary>
    public static Task Tenko(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        YaeShrine.Tenko(choiceContext, card.Owner?.Creature);

    /// <summary>"Each Sakura lasts 1 more turn."</summary>
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

    /// <summary>Base + per for each Sakura standing, the card's own Block.
    /// </summary>
    public static Task BlockPerSakura(PlayerChoiceContext choiceContext,
                                      CardModel card, CardPlay cardPlay) =>
        CardBlock(card, cardPlay,
                  Var(card, "YmBase") + Var(card, "YmPer") * YaeShrine.Count(card.Owner?.Creature));

    /// <summary>Bestseller: base + per for each Annotated card in hand, the
    /// card itself counted when Annotated (any layer, a Published one
    /// included).</summary>
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

    /// <summary>"Edit your newest / oldest Sakura: X", "Edit every Sakura:
    /// X". <paramref name="handIfUpgraded"/> (Inked Branches+, Yae review
    /// r4, pick 1 (a)): the upgraded card also Edits a card in your hand
    /// with it, read off <c>IsUpgraded</c> (`yae_upgraded`).</summary>
    public static async Task EditSakura(PlayerChoiceContext choiceContext, CardModel card,
                                        CardPlay cardPlay, YaeSakuraEnd end,
                                        YaeAnnotation annotation,
                                        bool keepRedInk = false,
                                        bool handIfUpgraded = false)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        // Yae review r5, item 2: Inked Branches+ with neither a Sakura nor a
        // hand card to Edit says "Nothing to Edit" once, not a bubble from
        // each half. One that Edited a Sakura says nothing about the hand.
        var hand = handIfUpgraded && card.IsUpgraded;
        var edited = YaeShrineLedger.For(yae).EditSakura(end, Var(card, "YmAmount"), annotation, keepRedInk);
        if (edited == 0 && !hand)
            YaeEditing.SayNothing(yae, YaeEditing.NoSakuraToEditKey);
        await SakuraBadge.Sync(choiceContext, yae);
        if (hand)
            await YaeEditing.Edit(choiceContext, card, annotation, 1,
                                  sayNothing: edited == 0);
    }

    /// <summary>Grafted Branch: "Plant a Sakura. It starts at Level 2 [3]."
    /// </summary>
    public static Task PlantLevel(PlayerChoiceContext choiceContext, CardModel card,
                                  CardPlay cardPlay) =>
        PlantLevel(choiceContext, card, cardPlay, YaeSakuraKind.Thunder);

    /// <summary>The same, of a named kind (no row prints one yet).</summary>
    public static Task PlantLevel(PlayerChoiceContext choiceContext, CardModel card,
                                  CardPlay cardPlay, YaeSakuraKind kind) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, 1, Var(card, "YmAmount"),
                        YaeAnnotationReach.Inherited(card), kind);

    /// <summary>Kitsune Pounce's rider.</summary>
    public static Task StrikeIfWeak(PlayerChoiceContext choiceContext, CardModel card,
                                    CardPlay cardPlay) =>
        YaeShrine.StrikeIfWeak(choiceContext, card.Owner?.Creature, cardPlay.Target);

    /// <summary>The `fox_fire` kind (Fox Fire's rider as a verb).</summary>
    public static Task FoxFire(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        YaeShrine.FoxFire(choiceContext, card.Owner?.Creature);

    /// <summary>
    /// FALLEN PETALS (review r3, sec.4): "Your oldest Sakura withers (it acts
    /// once, its Last Bloom). If one did, gain 1 Energy [and draw 1 card]."
    /// The upgrade's draw is read off <c>IsUpgraded</c> (`yae_upgraded`).
    /// </summary>
    public static async Task FallenPetals(PlayerChoiceContext choiceContext,
                                          CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner?.Creature == null) return;
        if (!await YaeShrine.WitherOldest(choiceContext, owner.Creature)) return;
        await PlayerCmd.GainEnergy(1, owner);
        if (card.IsUpgraded)
        {
            await CardPileCmd.Draw(choiceContext, 1, owner);
        }
    }

    /// <summary>Second Printing (review r3, sec.3): "Put an Annotated card
    /// from your Discard Pile into your hand. [It costs 0 this turn.]"
    /// </summary>
    public static Task SecondPrinting(PlayerChoiceContext choiceContext,
                                      CardModel card, CardPlay cardPlay) =>
        YaeEditing.SecondPrinting(choiceContext, card, card.IsUpgraded);

    /// <summary>Author's Copy (review r3, sec.3): "Add a copy of an Annotated
    /// card in your hand (not an Author's Copy) to your hand. It keeps its
    /// Annotations."</summary>
    public static Task AuthorsCopy(PlayerChoiceContext choiceContext,
                                   CardModel card, CardPlay cardPlay) =>
        YaeEditing.AuthorsCopy(choiceContext, card);

    /// <summary>
    /// ONE POWERED HIT OF THE CARD, carrying Electro. Red Ink rides it
    /// through the engine's enchant door.
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
