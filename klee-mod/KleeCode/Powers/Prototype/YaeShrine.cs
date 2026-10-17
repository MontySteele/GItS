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
/// and the Annotations it carries (Red Ink, Fox Fire, Deadline Extension).
/// THE POOL TO 78, pick 2 (a) (ruled 2026-10-15,
/// <c>review/active/yae-pool-to-78-2026-10-15.md</c>): distinct Annotations
/// COEXIST on a Sakura; a second copy of one it has does nothing; they
/// survive a Tenko refresh and a same-kind refresh and go when the Sakura
/// withers or is replaced. Sim twin: <c>yae_shrine.Sakura.annotations</c>.
/// </summary>
public sealed class YaeSakura
{
    public YaeSakuraKind Kind { get; internal set; }

    public int Level { get; internal set; }

    public int PlantedLevel { get; internal set; }

    public int TurnsLeft { get; internal set; }

    public int Seq { get; internal set; }

    private readonly List<YaeAnnotation> _annotations = new();

    /// <summary>The distinct Annotations it carries, in the order written.
    /// </summary>
    public IReadOnlyList<YaeAnnotation> Annotations => _annotations;

    /// <summary>Does it carry <paramref name="annotation"/>?</summary>
    public bool Has(YaeAnnotation annotation) => _annotations.Contains(annotation);

    /// <summary>Write one Annotation. False when it changes nothing: one the
    /// Sakura already carries (no second +3), or one with no Sakura reading.
    /// A write that changes nothing is not an Edit.</summary>
    internal bool Add(YaeAnnotation annotation)
    {
        if (!YaeShrineLedger.HasSakuraReading(annotation) || Has(annotation)) return false;
        _annotations.Add(annotation);
        return true;
    }
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

    /// <summary>The seat page's per-Sakura read (<see cref="YaeShrine.Snapshot"/>):
    /// one row per Sakura, oldest first, <c>slot</c> matching its badge
    /// ("Sakura 1" is the oldest) and <c>annotations</c> naming each
    /// Annotation it carries in the order written. The badge sentence lists
    /// them in a fixed order; this keeps the order they were applied.
    /// Primitives only.</summary>
    public List<object?> SakuraRows() =>
        _sakura.Select((s, i) => (object?)new Dictionary<string, object?>
        {
            ["slot"] = i + 1,
            ["annotations"] = s.Annotations
                .Select(a => (object?)YaeAnnotationText.Name(a)).ToList(),
        }).ToList();

    /// <summary>The planting clock.</summary>
    public int Seq { get; private set; }

    /// <summary>This turn's aimed enemy (Foxfire Lure), or null.</summary>
    public Creature? Lure { get; set; }

    /// <summary>Actions made this combat (telemetry, the seat page).</summary>
    public int Strikes { get; private set; }

    /// <summary>Editorial Priority (the pool to 78): has the first Annotated
    /// card this turn been played? Cleared at her turn start.</summary>
    public bool PriorityUsed { get; set; }

    /// <summary>Cards Edited this combat: each card in hand an Edit,
    /// Reborn as Guuji Yae or Inked Branches+ Annotated, and each Sakura an
    /// "Edit your ... Sakura" card Annotated (Inked Branches counts every
    /// one). A Publish is not an Edit. Bestseller counts it
    /// (Yae review r5, pick 1 (a), ruled 2026-10-15). Per combat, as the
    /// whole ledger is: never saved, a new combat starts it at 0.</summary>
    public int Edits { get; private set; }

    /// <summary>Cards Edited THIS TURN, counted as <see cref="Edits"/> is
    /// (the refill: Publisher's Deadline's "Costs 1 less if you Edited a
    /// card this turn"). Cleared at her turn start
    /// (<see cref="YaeShrine.TurnStart"/>). Sim twin:
    /// <c>yae_shrine.YaeLedger.edits_this_turn</c>.</summary>
    public int EditsThisTurn { get; internal set; }

    /// <summary>HUNTING GAZE (the refill): the last enemy hit by one of her
    /// Attack cards this combat, or null (<see cref="YaeShrine.NoteAttacked"/>).
    /// Kept whether or not she has the power, so a Gaze played late still
    /// knows whom she attacked. Sim twin: <c>yae_shrine.YaeLedger.last_attacked</c>.
    /// </summary>
    public Creature? LastAttacked { get; set; }

    /// <summary>
    /// PLANT ONE: a new Sakura of <paramref name="kind"/> at
    /// <paramref name="plantLevel"/> with <see cref="YaeLaw.SakuraTurns"/>
    /// actions left; the others are NOT levelled. Returns whether a Sakura
    /// was added (a full-shrine plant of the oldest's kind adds none).
    /// </summary>
    public bool Plant(int plantLevel) => Plant(plantLevel, null);

    /// <summary>
    /// Plant one, starting at <paramref name="startLevel"/> where a card
    /// says so (Guardian of Narukami), raised as every plant is by Fox's Mooncall
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
                                YaeSakuraKind kind = YaeSakuraKind.Thunder,
                                int extraTurns = 0)
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
                // the refreshed Sakura, as it would to a new one; the pool to
                // 78, pick 2 (a): beside what it already carries.
                oldest.Add(inherited);
                LastPlanted = oldest;
                return false;
            }
            _sakura.RemoveAt(0);          // another kind: it withers
        }
        Seq++;
        var planted = new YaeSakura
        {
            Kind = kind,
            Level = plantLevel,
            PlantedLevel = plantLevel,
            // "and lasts 1 more turn" (Grafted Branch's, cut 2026-10-16).
            TurnsLeft = YaeLaw.SakuraTurns + Math.Max(0, extraTurns),
            Seq = Seq,
        };
        planted.Add(inherited);
        _sakura.Add(planted);
        LastPlanted = planted;
        return true;
    }

    /// <summary>The Sakura the last plant made or, into a full shrine of its
    /// kind, refreshed: the "it" of "Plant a Foxfire Sakura at Level 3. Edit
    /// it: Deadline Extension." (Yakan Evocation: Sesshou Sakura, the Yae
    /// pass 2026-10-16). Null before any plant this combat.</summary>
    public YaeSakura? LastPlanted { get; private set; }

    /// <summary>"Edit it": one Annotation on <paramref name="sakura"/>, if it
    /// still stands. Counted as an Edit only when it changes something.
    /// </summary>
    public bool EditOne(YaeSakura? sakura, YaeAnnotation annotation)
    {
        if (sakura == null || !_sakura.Contains(sakura)) return false;
        if (!sakura.Add(annotation)) return false;
        NoteEdit();
        return true;
    }

    /// <summary>Would a plant of <paramref name="kind"/> into a shrine of
    /// <paramref name="cap"/> REPLACE (wither) the oldest? A full shrine
    /// whose oldest is another kind. PURE.</summary>
    public bool WouldReplace(int cap, YaeSakuraKind kind) =>
        _sakura.Count >= cap && _sakura.Count > 0 && _sakura[0].Kind != kind;

    /// <summary>Genre Shift: the kinds with none standing, in kind order
    /// (Sakura, Foxfire Sakura, Kitsune Sakura). PURE.</summary>
    public IReadOnlyList<YaeSakuraKind> MissingKinds() =>
        new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune }
            .Where(k => _sakura.All(s => s.Kind != k)).ToList();

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

    /// <summary>EVERGREEN CHARM (the Yae pass, 2026-10-16): "Your oldest
    /// Sakura lasts 2 more turns" (Kitsune's Blessing's reading), +n on the
    /// oldest's timer. Whether one stood. Sim twin: the `extend_oldest`
    /// kind.</summary>
    public bool ExtendOldest(int n)
    {
        if (_sakura.Count == 0) return false;
        _sakura[0].TurnsLeft += Math.Max(0, n);
        return true;
    }

    /// <summary>"Each Sakura gains a Level": +n each, no cap; with
    /// <paramref name="kind"/>, that kind only (Kitsune Veil).</summary>
    public void LevelUp(int n, YaeSakuraKind? kind = null)
    {
        foreach (var s in _sakura.Where(s => kind == null || s.Kind == kind)) s.Level += n;
    }

    /// <summary>After the end-of-turn actions every timer ticks. A Deadline
    /// Extension Sakura's timer does not tick, and under Eternity (the pool
    /// to 78, <paramref name="eternal"/>) none does: "Your Sakura no longer
    /// wither when their turns run out." Returns the Sakura whose timers ran
    /// out, oldest first, STILL STANDING: each blooms (Last Bloom), then
    /// <see cref="Wither"/> removes it.</summary>
    public IReadOnlyList<YaeSakura> Tick(bool eternal = false)
    {
        if (eternal) return Array.Empty<YaeSakura>();
        foreach (var s in _sakura)
        {
            if (!s.Has(YaeAnnotation.DeadlineExtension)) s.TurnsLeft--;
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
    /// from that end) or "Edit every Sakura". THE POOL TO 78, pick 2 (a): the
    /// Annotation joins what each carries; on one that already carries it,
    /// it changes nothing, and AN EDIT THAT CHANGES NOTHING IS NOT AN EDIT
    /// (Bestseller and Serialization never see it). Returns how
    /// many were Edited.</summary>
    public int EditSakura(YaeSakuraEnd end, int n, YaeAnnotation annotation)
    {
        if (!HasSakuraReading(annotation)) return 0;
        var ordered = end == YaeSakuraEnd.Oldest
            ? _sakura.ToList()
            : Enumerable.Reverse(_sakura).ToList();
        var edited = 0;
        if (end == YaeSakuraEnd.Every) n = ordered.Count;
        foreach (var s in ordered.Take(Math.Max(0, n)))
        {
            if (s.Add(annotation)) edited++;
        }
        Edits += edited;
        EditsThisTurn += edited;
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

    internal void NoteEdit()
    {
        Edits++;
        EditsThisTurn++;
    }

    /// <summary>Dawn Prayer (the refill): "Your newest Sakura gains 2 [3]
    /// Levels." Whether one stood.</summary>
    public bool LevelNewest(int n)
    {
        if (_sakura.Count == 0) return false;
        _sakura[_sakura.Count - 1].Level += n;
        return true;
    }

    /// <summary>Kitsune's Blessing (the refill): "Your highest-Level Sakura
    /// gains 3 [4] Levels and lasts 2 more turns." Any kind; on a tie, the
    /// OLDEST (<see cref="Highest"/>, Editor-in-Chief's reading). The Sakura
    /// blessed, or null with none.</summary>
    public YaeSakura? Bless(int n, int lasts)
    {
        var s = Highest();
        if (s == null) return null;
        s.Level += n;
        s.TurnsLeft += Math.Max(0, lasts);
        return s;
    }

    /// <summary>Sesshou Fang (the refill): does any Sakura, any kind, stand
    /// at <paramref name="level"/> or higher? PURE.</summary>
    public bool AnyAtLevel(int level) => _sakura.Any(s => s.Level >= level);

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
    /// a Red Ink Sakura's 3 adds to any kind, once. PURE.
    /// </summary>
    public static int ActSize(YaeSakuraKind kind, int level,
                              IEnumerable<YaeAnnotation> annotations) =>
        KindBase(kind) + level
        + (annotations.Contains(YaeAnnotation.RedInk) ? YaeLaw.RedInkAmount : 0);

    /// <summary>The same, for a Sakura carrying one Annotation (or none).
    /// PURE.</summary>
    public static int ActSize(YaeSakuraKind kind, int level, YaeAnnotation annotation) =>
        ActSize(kind, level, new[] { annotation });

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

    /// <summary>The cards <paramref name="yae"/> Edited this combat (0 for
    /// anyone else): what Bestseller counts.</summary>
    public static int Edits(Creature? yae) =>
        yae == null || !Live(yae) ? 0 : YaeShrineLedger.For(yae).Edits;

    /// <summary>The cards <paramref name="yae"/> Edited this turn (0 for
    /// anyone else): Publisher's Deadline's discount (the refill).</summary>
    public static int EditsThisTurn(Creature? yae) =>
        yae == null || !Live(yae) ? 0 : YaeShrineLedger.For(yae).EditsThisTurn;

    /// <summary>
    /// HUNTING GAZE's memory (the refill): a hit of one of her own Attack
    /// cards (a powered attack whose source is an Attack she owns) on
    /// another creature makes that creature the last she attacked. A
    /// Sakura's or Fox Fire's hit (a pet's, with no card) is not her
    /// attack. <c>KleeElementalHooks.AfterDamageGiven</c> calls it for every
    /// hit; a no-op for anyone not Yae. Sim twin:
    /// <c>yae_shrine.note_attacked</c>.
    /// </summary>
    public static void NoteAttacked(Creature? dealer, Creature? receiver,
                                    ValueProp props, CardModel? cardSource)
    {
        if (dealer == null || receiver == null || ReferenceEquals(receiver, dealer)) return;
        if (!Live(dealer)) return;
        if (cardSource is not { Type: CardType.Attack } || cardSource.Owner?.Creature != dealer) return;
        if (!props.IsPoweredAttack()) return;
        YaeShrineLedger.For(dealer).LastAttacked = receiver;
    }

    /// <summary>
    /// The seat page's read (the bridge's <c>gits/GitsYaeShrine.cs</c>, by
    /// reflection; <c>understudy/blindplay_board.yae_shrine</c>): the cards
    /// she Edited this combat, the count Bestseller reads, and
    /// each Sakura's Annotations in the order applied (<c>sakura</c>). EMPTY
    /// for anyone not Yae and outside a fight (a ledger is asked for only
    /// inside one, so a map-screen poll never resets it), except that a
    /// Meditations of a Yako which found nothing to Publish after this fight
    /// adds <c>nothing_to_publish</c> (Yae review r6, item 3). Primitives
    /// only.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        if (player?.Relics.OfType<global::KleeMod.Relics.MeditationsOfAYako>()
                .Any(r => r.NothingToPublish) == true)
            snapshot["nothing_to_publish"] = true;
        var yae = player?.Creature;
        if (yae == null || !Live(yae) || yae.CombatState == null) return snapshot;
        snapshot["live"] = true;
        snapshot["edits_this_combat"] = Edits(yae);
        // The pool to 78, pick 2 (a): a Sakura carries several Annotations,
        // and the page lists them in the order applied (the badge sentence
        // keeps its fixed-order flags, which an older page still reads).
        snapshot["sakura"] = YaeShrineLedger.For(yae).SakuraRows();
        return snapshot;
    }

    /// <summary>The Level a Sakura is planted at: 1, plus 1 for each Fox's
    /// Mooncall.</summary>
    public static int PlantLevel(Creature yae) =>
        YaeLaw.PlantLevel + yae.GetPowerAmount<FoxsMooncallPower>();

    /// <summary>How many Sakura may stand beside <paramref name="yae"/>: 3,
    /// plus Sakura Channeling's amount. Sim twin: <c>yae_shrine.sakura_cap</c>.
    /// </summary>
    public static int MaxSakura(Creature yae) =>
        YaeLaw.SakuraCap + yae.GetPowerAmount<SakuraChannelingPower>()
        // Fox Ofuda (the Yae pass, 2026-10-16): "You can have 1 more Sakura",
        // Sakura Channeling's words, and it stacks with Channeling.
        + Relics.FoxOfuda.Extra(yae);

    /// <summary>Torii Ward's "If your shrine is full": as many stand as may
    /// (<see cref="MaxSakura"/>). False for anyone not Yae.</summary>
    public static bool Full(Creature? yae) =>
        yae != null && Live(yae) && YaeShrineLedger.For(yae).Count >= MaxSakura(yae);

    /// <summary>Disarming Smile's "for each enemy that is Weak": the living
    /// enemies wearing Weak. Sim twin: the `weak_enemies` count.</summary>
    public static int WeakEnemies(Creature? yae) =>
        yae?.CombatState?.HittableEnemies.Count(e => e.IsAlive && IsWeak(e)) ?? 0;

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
    /// <paramref name="startLevel"/>: Guardian of Narukami.
    /// <paramref name="inherited"/>: the planting card's Red Ink, given to
    /// each NEW Sakura this plants.
    /// </summary>
    public static async Task Plant(PlayerChoiceContext choiceContext,
                                   Creature? yae, int n, int? startLevel = null,
                                   YaeAnnotation inherited = YaeAnnotation.None,
                                   YaeSakuraKind kind = YaeSakuraKind.Thunder,
                                   int lasts = 0)
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
            var replaced = ledger.WouldReplace(cap, kind);
            ledger.Plant(PlantLevel(yae), startLevel, inherited, cap, kind, lasts);
            // A replaced oldest withered (the pool to 78: Scattered
            // Blossoms reads every wither).
            if (replaced) await Withered(choiceContext, yae, 1);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// SCATTERED BLOSSOMS (the pool to 78): "Whenever a Sakura withers,
    /// draw 1 card." Paid once per Sakura that withered, per stack: a timer
    /// run out, Fallen Petals, Replanting, Daisesshou, a full-shrine plant
    /// that replaced the oldest. Sim twin: <c>yae_shrine._withered</c>.
    /// </summary>
    public static async Task Withered(PlayerChoiceContext choiceContext, Creature yae, int n)
    {
        var per = yae.GetPowerAmount<EnlightenedBlessingPower>();
        if (per <= 0 || n <= 0 || yae.Player is not { } player) return;
        yae.Powers.OfType<EnlightenedBlessingPower>().FirstOrDefault()?.Pulse();
        await CardPileCmd.Draw(choiceContext, per * n, player);
    }

    /// <summary>Is this enemy Weak (Edict's and Kitsune Pounce's read)?
    /// </summary>
    public static bool IsWeak(Creature? target) =>
        target != null && target.Powers.OfType<WeakPower>().Any(p => p.Amount > 0);

    /// <summary>The size of <paramref name="sakura"/>'s action, before Edict.
    /// </summary>
    public static int Size(Creature yae, YaeSakura sakura) =>
        YaeShrineLedger.ActSize(sakura.Kind, sakura.Level, sakura.Annotations)
        // Electroculus (the Yae pass, 2026-10-16): "Your Sakura's strikes deal
        // 1 more damage", added to the strike's size before Edict and Fox
        // Fire; a Foxfire's hit on ALL counts, a Kitsune's Block does not.
        + (YaeShrineLedger.DealsDamage(sakura.Kind) ? Relics.Electroculus.Bonus(yae) : 0);

    /// <summary>The enemy a single-target strike lands on: the card's aim
    /// (Kitsune Pounce), else this turn's Lure while it lives, else (with
    /// Hunting Gaze, the refill) the last enemy her Attack cards hit while it
    /// lives, else one random living enemy off the combat target stream.
    /// Copies of Hunting Gaze do not stack: one aim either way.</summary>
    private static Creature? Aim(Creature yae, Creature? aim = null)
    {
        if (aim is { IsAlive: true }) return aim;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Lure is { IsAlive: true } lured) return lured;
        if (yae.GetPowerAmount<HuntingGazePower>() > 0
            && ledger.LastAttacked is { IsAlive: true } prey)
        {
            yae.Powers.OfType<HuntingGazePower>().FirstOrDefault()?.Pulse();
            return prey;
        }
        var living = yae.CombatState?.HittableEnemies.Where(e => e.IsAlive).ToList();
        if (living == null || living.Count == 0) return null;
        var rng = yae.Player?.RunState.Rng.CombatTargets;
        return rng == null ? living[0] : rng.NextItem(living);
    }

    /// <summary>One damage action's hit: Electro, a PET'S HIT (her Strength
    /// and Weak do not apply; the enemy's Vulnerable and Block do), reacting
    /// with whatever aura it lands on, credited to Yae; Edict on top.
    /// STELLAR CONDUCT (the pool to 78): "Whenever a Sakura's strike
    /// triggers an Elemental Reaction, it strikes again", once per stack,
    /// the same strike at the same enemy; a strike again never strikes
    /// again (and the reaction spent the aura it read).
    /// </summary>
    private static async Task Hit(PlayerChoiceContext choiceContext, Creature yae,
                                  Creature target, int size, bool again = false)
    {
        var damage = size + (YaeShrineLedger.EdictApplies(IsWeak(target), Reacts(target))
            ? yae.GetPowerAmount<EdictOfCleansingPower>() : 0);
        if (damage <= 0) return;
        var before = ReactionEffects.TotalResolved;
        await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, Element.Electro, damage, yae);
        if (again || ReactionEffects.TotalResolved <= before) return;
        var stellar = yae.GetPowerAmount<StellarConductPower>();
        if (stellar > 0) yae.Powers.OfType<StellarConductPower>().FirstOrDefault()?.Pulse();
        for (var i = 0; i < stellar; i++)
        {
            if (!target.IsAlive) return;
            await Hit(choiceContext, yae, target, size, again: true);
        }
    }

    /// <summary>
    /// ONE SAKURA ACTS AS ITS KIND (review r3, ruled 2026-10-14): a Sakura
    /// strikes one enemy (the aim, the Lure, else random) for 2 + its Level;
    /// a Foxfire Sakura hits ALL enemies for 1 + its Level; a Kitsune Sakura
    /// gives her 2 + its Level Block (unpowered). Red Ink adds 3 to any of
    /// them. Then the Sakura's own Fox Fire, once.
    /// THE POOL TO 78 (revised after GPT's review): a strike AIMED at a
    /// chosen enemy (<paramref name="aim"/>: Falling Blossom, Narukami Judgment,
    /// Saiguu's Lesson, Fox's Verdict, Kitsune Pounce) is one hit on that
    /// enemy, a Foxfire Sakura's included; only its own act (turn end, Last
    /// Bloom, Tenko, a full-shrine plant) hits ALL.
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
                if (aim is { IsAlive: true } aimed)
                {
                    await Hit(choiceContext, yae, aimed, size);
                    break;
                }
                foreach (var enemy in yae.CombatState!.HittableEnemies.Where(e => e.IsAlive).ToList())
                {
                    await Hit(choiceContext, yae, enemy, size);
                }
                break;
            default:
                if (Aim(yae, aim) is { } target) await Hit(choiceContext, yae, target, size);
                break;
        }
        if (sakura.Has(YaeAnnotation.FoxFire))
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
        // Kagura Bell (the Yae pass, 2026-10-16): "Whenever you Tenko, each
        // Sakura gains a Level", after the Tenko's strikes.
        Relics.KaguraBell.Ring(yae);
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// AFTER <paramref name="n"/> EDITS (every Edit's one door: a hand Edit,
    /// Reborn as Guuji Yae, an "Edit your ... Sakura" card, Yakan Evocation:
    /// Sesshou Sakura and Saiguu's Inkstone): Serialization pays per Edit
    /// (Yae review r6, item 1), and Proofreader's Glasses (the Yae pass,
    /// 2026-10-16) draws on the turn's first. Counted already
    /// (<see cref="YaeShrineLedger.EditsThisTurn"/>).
    /// </summary>
    public static async Task AfterEdits(PlayerChoiceContext choiceContext,
                                        Creature? yae, int n)
    {
        if (yae == null || n <= 0) return;
        await SerializationPower.Pay(yae, n);
        if (Live(yae) && YaeShrineLedger.For(yae).EditsThisTurn == n)
            await Relics.ProofreadersGlasses.FirstEdit(choiceContext, yae);
    }

    /// <summary>
    /// FALLEN PETALS (review r3, sec.4): "Your oldest Sakura withers (it acts
    /// once, its Last Bloom)." Deadline Extension does not stop it (an
    /// active wither, not a timer). Whether one did.
    /// FALLING BLOSSOM (the refill): "its Last Bloom strikes this enemy",
    /// <paramref name="aim"/>, one hit whatever the kind (a Foxfire's
    /// included), as every aimed strike is; a dead aim falls back to the
    /// plain act.
    /// </summary>
    public static async Task<bool> WitherOldest(PlayerChoiceContext choiceContext,
                                                Creature? yae, Creature? aim = null)
    {
        if (yae == null || !Live(yae)) return false;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return false;
        var oldest = ledger.Standing[0];
        await Act(choiceContext, yae, oldest, aim);
        var withered = ledger.Wither(oldest);
        if (withered) await Withered(choiceContext, yae, 1);
        await SakuraBadge.Sync(choiceContext, yae);
        return withered;
    }

    /// <summary>HIDE BEHIND THE SHRINE (the refill): "Your newest Sakura
    /// withers", its Last Bloom as every wither's (it acts as its kind:
    /// a Kitsune's Block, a Foxfire's hit on ALL). Whether one did.</summary>
    public static async Task<bool> WitherNewest(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return false;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return false;
        var newest = ledger.Standing[ledger.Count - 1];
        await Act(choiceContext, yae, newest);
        var withered = ledger.Wither(newest);
        if (withered) await Withered(choiceContext, yae, 1);
        await SakuraBadge.Sync(choiceContext, yae);
        return withered;
    }

    /// <summary>
    /// FORBIDDEN ART: DAISESSHOU (the pool to 78): "Every Sakura withers."
    /// Each acts once as it withers (its Last Bloom), oldest first, Deadline
    /// Extension or not. Returns how many withered.
    /// </summary>
    public static async Task<int> WitherAll(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return 0;
        var ledger = YaeShrineLedger.For(yae);
        var n = 0;
        foreach (var sakura in ledger.Standing.ToList())
        {
            await Act(choiceContext, yae, sakura);
            if (ledger.Wither(sakura)) n++;
        }
        await Withered(choiceContext, yae, n);
        await SakuraBadge.Sync(choiceContext, yae);
        return n;
    }

    /// <summary>
    /// REPLANTING (the pool to 78): "Your oldest Sakura withers. Plant one of
    /// its kind, 1 [2] Level higher." The oldest withers as Fallen Petals'
    /// does (its Last Bloom, its Annotations go); the new one of its kind
    /// starts at its Level plus <paramref name="higher"/>, and Fox's
    /// Mooncall still adds, as on every plant. Nothing standing: nothing.
    /// </summary>
    public static async Task Replant(PlayerChoiceContext choiceContext, Creature? yae,
                                     int higher, YaeAnnotation inherited = YaeAnnotation.None)
    {
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return;
        var oldest = ledger.Standing[0];
        var kind = oldest.Kind;
        var level = oldest.Level;
        if (!await WitherOldest(choiceContext, yae)) return;
        await Plant(choiceContext, yae, 1, level + higher, inherited, kind);
    }

    /// <summary>Genre Shift (the pool to 78): "Plant one of each kind of
    /// Sakura you do not have", the kinds missing when it is played, in kind
    /// order.</summary>
    public static async Task PlantMissing(PlayerChoiceContext choiceContext, Creature? yae,
                                          YaeAnnotation inherited = YaeAnnotation.None)
    {
        if (yae == null || !Live(yae)) return;
        foreach (var kind in YaeShrineLedger.For(yae).MissingKinds())
        {
            await Plant(choiceContext, yae, 1, null, inherited, kind);
        }
    }

    /// <summary>Narukami Bloom (the pool to 78): "Plant Sakura until your
    /// shrine is full." A full shrine plants none.</summary>
    public static Task PlantUntilFull(PlayerChoiceContext choiceContext, Creature? yae,
                                      YaeAnnotation inherited = YaeAnnotation.None)
    {
        if (yae == null || !Live(yae)) return Task.CompletedTask;
        var room = MaxSakura(yae) - YaeShrineLedger.For(yae).Count;
        return Plant(choiceContext, yae, room, null, inherited);
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
        ledger.PriorityUsed = false;
        ledger.EditsThisTurn = 0;
        await FoxfireLurePower.ClearAll(yae);
        // Saiguu's Inkstone (the Yae pass, 2026-10-16): "At the start of your
        // turn, Edit a random card in your hand: Red Ink", after the draw and
        // after the turn's Edit count is cleared, so it is the turn's first.
        await Relics.SaiguusInkstone.Edit(choiceContext, player);
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
        // The Shrine's Sacred Shade (the pool to 78): "At the end of your
        // turn, gain 2 [3] Block for each Sakura", the Sakura standing as the
        // turn ends, before they act. Unpowered (the Powers' door).
        var shade = yae.GetPowerAmount<SacredShadePower>();
        var standing = YaeShrineLedger.For(yae).Count;
        if (shade > 0 && standing > 0)
        {
            yae.Powers.OfType<SacredShadePower>().FirstOrDefault()?.Pulse();
            await CreatureCmd.GainBlock(yae, shade * standing, ValueProp.Unpowered, null);
        }
        await ActAll(choiceContext, yae);
        await TickAndBloom(choiceContext, yae);
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>The timers tick; each run-out Sakura blooms, then withers.
    /// </summary>
    public static async Task TickAndBloom(PlayerChoiceContext choiceContext, Creature yae)
    {
        var ledger = YaeShrineLedger.For(yae);
        var n = 0;
        foreach (var sakura in ledger.Tick(yae.GetPowerAmount<EternityPower>() > 0))
        {
            await Act(choiceContext, yae, sakura);
            if (ledger.Wither(sakura)) n++;
        }
        await Withered(choiceContext, yae, n);
    }

    /// <summary>
    /// After an Annotated card's own effects and its Annotations':
    /// Editor-in-Chief, "a Sakura strikes": the highest-Level Sakura
    /// acts as its kind, once per stack (review r3, the builder's reading).
    /// </summary>
    public static async Task AfterCardPlayed(PlayerChoiceContext choiceContext,
                                             CardPlay cardPlay)
    {
        var yae = cardPlay.Card?.Owner?.Creature;
        if (yae == null || !Live(yae)) return;
        if (!YaeEditing.IsAnnotated(cardPlay.Card)) return;
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
        if (target is not { IsAlive: true } || !IsWeak(target)) return;
        await StrikeTarget(choiceContext, yae, target);
    }

    /// <summary>"A Sakura strikes it" (Saiguu's Lesson, Kitsune Pounce; the
    /// pool to 78): the highest-Level Sakura that strikes (a Sakura or a
    /// Foxfire Sakura), one hit on <paramref name="target"/>.</summary>
    public static async Task StrikeTarget(PlayerChoiceContext choiceContext,
                                          Creature? yae, Creature? target)
    {
        if (yae == null || !Live(yae)) return;
        if (target is not { IsAlive: true }) return;
        var sakura = YaeShrineLedger.For(yae).Highest(damageOnly: true);
        if (sakura == null) return;
        await Act(choiceContext, yae, sakura, target);
    }

    /// <summary>Narukami Judgment (the pool to 78): "Each striking Sakura
    /// strikes it", oldest first, one hit each, while it lives.</summary>
    public static async Task StrikeAllAt(PlayerChoiceContext choiceContext,
                                         Creature? yae, Creature? target)
    {
        if (yae == null || !Live(yae)) return;
        foreach (var sakura in YaeShrineLedger.For(yae).Standing
                     .Where(s => YaeShrineLedger.DealsDamage(s.Kind)).ToList())
        {
            if (target is not { IsAlive: true }) return;
            await Act(choiceContext, yae, sakura, target);
        }
    }

    /// <summary>Fox's Verdict (the pool to 78): "Each striking Sakura
    /// strikes each enemy that is Weak": oldest Sakura first, one hit on
    /// each Weak enemy, never a sweep per enemy.</summary>
    public static async Task Verdict(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return;
        foreach (var sakura in YaeShrineLedger.For(yae).Standing
                     .Where(s => YaeShrineLedger.DealsDamage(s.Kind)).ToList())
        {
            var weak = yae.CombatState?.HittableEnemies
                .Where(e => e.IsAlive && IsWeak(e)).ToList();
            if (weak == null || weak.Count == 0) return;
            foreach (var enemy in weak)
            {
                if (!enemy.IsAlive) continue;
                await Act(choiceContext, yae, sakura, enemy);
            }
        }
    }

    /// <summary>Kitsune's Shelter (the pool to 78): "Each Kitsune Sakura
    /// acts", oldest first.</summary>
    public static async Task KitsuneAct(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return;
        foreach (var sakura in YaeShrineLedger.For(yae).Standing
                     .Where(s => s.Kind == YaeSakuraKind.Kitsune).ToList())
        {
            await Act(choiceContext, yae, sakura);
        }
    }

    /// <summary>
    /// SAIGUU'S LESSON (the pool to 78): "Whenever you apply Weak to an
    /// enemy, a Sakura strikes it", once per stack, per enemy Weak landed on
    /// (<see cref="SaiguusLessonPower"/>). Sim twin:
    /// <c>yae_shrine.on_weak_applied</c>.
    /// </summary>
    public static async Task OnWeakApplied(PlayerChoiceContext choiceContext,
                                           Creature yae, Creature target, int stacks)
    {
        for (var i = 0; i < stacks; i++)
        {
            if (!target.IsAlive) return;
            await StrikeTarget(choiceContext, yae, target);
        }
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
            ? TenkoWords(Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Thunder)
                         + Bonus(yae, YaeSakuraKind.Thunder),
                         Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Foxfire)
                         + Bonus(yae, YaeSakuraKind.Foxfire),
                         Total(YaeShrineLedger.For(yae).Standing, YaeSakuraKind.Kitsune))
            : "";

    /// <summary>Electroculus's +1 on each Sakura of a damage kind.</summary>
    private static int Bonus(Creature yae, YaeSakuraKind kind) =>
        Relics.Electroculus.Bonus(yae)
        * YaeShrineLedger.For(yae).Standing.Count(s => s.Kind == kind);

    /// <summary>What every Sakura of <paramref name="kind"/> would do,
    /// summed, off the numbers alone. PURE.</summary>
    public static int Total(IEnumerable<YaeSakura> standing, YaeSakuraKind kind) =>
        standing.Where(s => s.Kind == kind)
            .Sum(s => YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotations));

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

    /// <summary>Evergreen Charm (the Yae pass, 2026-10-16): "Your oldest
    /// Sakura lasts 2 more turns" (YmAmount).</summary>
    public static async Task ExtendOldest(PlayerChoiceContext choiceContext,
                                          CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        if (YaeShrineLedger.For(yae).ExtendOldest(Var(card, "YmAmount")))
            await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// YAKAN EVOCATION: SESSHOU SAKURA (the Yae pass, 2026-10-16, the
    /// Archaic Tooth's): "Plant a Foxfire Sakura at Level 3 (YmAmount). Edit
    /// it: Deadline Extension." The plant is every plant: into a full shrine
    /// whose oldest is a Foxfire Sakura it refreshes and Levels that one, and
    /// "it" is the Sakura refreshed. The Edit counts only when it changes
    /// something (a second Deadline Extension does not).
    /// </summary>
    public static async Task SesshouSakura(PlayerChoiceContext choiceContext,
                                           CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        await YaeShrine.Plant(choiceContext, yae, 1, Var(card, "YmAmount"),
                              YaeAnnotationReach.Inherited(card), YaeSakuraKind.Foxfire);
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.EditOne(ledger.LastPlanted, YaeAnnotation.DeadlineExtension))
        {
            await YaeShrine.AfterEdits(choiceContext, yae, 1);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Kitsune Veil (the pool to 78): "Each Kitsune Sakura gains 2
    /// [2] Levels" (YmAmount).</summary>
    public static async Task LevelKitsune(PlayerChoiceContext choiceContext,
                                          CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).LevelUp(Var(card, "YmAmount"), YaeSakuraKind.Kitsune);
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Narukami Ray, Mikage Thunder: "Each Sakura gains a Level"
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

    /// <summary>Base + per for each card you Edited this combat, one powered
    /// Electro hit (<see cref="YaeShrineLedger.Edits"/>). No row since
    /// Bestseller took the calculated rail (2026-10-15).</summary>
    public static Task DamagePerEdit(PlayerChoiceContext choiceContext,
                                     CardModel card, CardPlay cardPlay) =>
        CardHit(choiceContext, card, cardPlay,
                Var(card, "YmBase") + Var(card, "YmPer") * YaeShrine.Edits(card.Owner?.Creature));

    /// <summary>Base + per for each card you Edited this combat, the card's
    /// own Block (no row since Print Run, cut 2026-10-16, took the calculated rail,
    /// 2026-10-15).
    /// </summary>
    public static Task BlockPerEdit(PlayerChoiceContext choiceContext,
                                    CardModel card, CardPlay cardPlay) =>
        CardBlock(card, cardPlay,
                  Var(card, "YmBase") + Var(card, "YmPer") * YaeShrine.Edits(card.Owner?.Creature));

    /// <summary>(No row since Kitsune Flash was cut, 2026-10-16.) Base, and amount more if this card is
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
                                        bool handIfUpgraded = false)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        // Yae review r5, item 2: Inked Branches+ with neither a Sakura nor a
        // hand card to Edit says "Nothing to Edit" once, not a bubble from
        // each half. One that Edited a Sakura says nothing about the hand.
        var hand = handIfUpgraded && card.IsUpgraded;
        var edited = YaeShrineLedger.For(yae).EditSakura(end, Var(card, "YmAmount"), annotation);
        await YaeShrine.AfterEdits(choiceContext, yae, edited);
        if (edited == 0 && !hand)
            YaeEditing.SayNothing(yae, YaeEditing.NoSakuraToEditKey);
        await SakuraBadge.Sync(choiceContext, yae);
        if (hand)
            await YaeEditing.Edit(choiceContext, card, annotation, 1,
                                  sayNothing: edited == 0);
    }

    /// <summary>(Grafted Branch's, cut 2026-10-16:) "Plant a Sakura. It starts at Level 3 [4]
    /// and lasts 1 more turn." (<paramref name="lasts"/>, the pool to 78);
    /// Guardian of Narukami's Kitsune Sakura "starts at Level 3"
    /// (<paramref name="kind"/>).</summary>
    public static Task PlantLevel(PlayerChoiceContext choiceContext, CardModel card,
                                  CardPlay cardPlay,
                                  YaeSakuraKind kind = YaeSakuraKind.Thunder,
                                  int lasts = 0) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, 1, Var(card, "YmAmount"),
                        YaeAnnotationReach.Inherited(card), kind, lasts);

    // ---- The pool to 78 (review/active/yae-pool-to-78-2026-10-15.md) ------

    /// <summary>"A Sakura strikes it." (No row since Sacred Spark was cut,
    /// 2026-10-16.)</summary>
    public static Task StrikeTarget(PlayerChoiceContext choiceContext, CardModel card,
                                    CardPlay cardPlay) =>
        YaeShrine.StrikeTarget(choiceContext, card.Owner?.Creature, cardPlay.Target);

    /// <summary>Narukami Judgment: "Each striking Sakura strikes it."</summary>
    public static Task StrikeAllAt(PlayerChoiceContext choiceContext, CardModel card,
                                   CardPlay cardPlay) =>
        YaeShrine.StrikeAllAt(choiceContext, card.Owner?.Creature, cardPlay.Target);

    /// <summary>Kitsune's Shelter: "Each Kitsune Sakura acts."</summary>
    public static Task KitsuneAct(PlayerChoiceContext choiceContext, CardModel card,
                                  CardPlay cardPlay) =>
        YaeShrine.KitsuneAct(choiceContext, card.Owner?.Creature);

    /// <summary>Fox's Verdict: "Each striking Sakura strikes each enemy that
    /// is Weak."</summary>
    public static Task Verdict(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        YaeShrine.Verdict(choiceContext, card.Owner?.Creature);

    /// <summary>Hold the Presses: "Retain your hand this turn", the base
    /// game's Equilibrium rider (<c>RetainHandPower</c>, 1 turn).</summary>
    public static async Task RetainHand(PlayerChoiceContext choiceContext, CardModel card,
                                        CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null) return;
        await PowerCmd.Apply<RetainHandPower>(choiceContext, owner, 1m, owner, card);
    }

    /// <summary>Replanting: "Your oldest Sakura withers. Plant one of its
    /// kind, 1 [2] Level higher." (YmAmount).</summary>
    public static Task Replant(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        YaeShrine.Replant(choiceContext, card.Owner?.Creature, Var(card, "YmAmount"),
                          YaeAnnotationReach.Inherited(card));

    /// <summary>Genre Shift: "Plant one of each kind of Sakura you do not
    /// have."</summary>
    public static Task PlantMissing(PlayerChoiceContext choiceContext, CardModel card,
                                    CardPlay cardPlay) =>
        YaeShrine.PlantMissing(choiceContext, card.Owner?.Creature,
                               YaeAnnotationReach.Inherited(card));

    /// <summary>Narukami Bloom: "Plant Sakura until your shrine is full."
    /// </summary>
    public static Task PlantUntilFull(PlayerChoiceContext choiceContext, CardModel card,
                                      CardPlay cardPlay) =>
        YaeShrine.PlantUntilFull(choiceContext, card.Owner?.Creature,
                                 YaeAnnotationReach.Inherited(card));

    /// <summary>Forbidden Art: Daisesshou: "Every Sakura withers. Deal 9
    /// [12] Electro damage to ALL enemies for each one." ONE powered hit of
    /// the card on every enemy, YmPer times the Sakura that withered; none
    /// withered, no hit.</summary>
    public static async Task Daisesshou(PlayerChoiceContext choiceContext, CardModel card,
                                        CardPlay cardPlay)
    {
        var n = await YaeShrine.WitherAll(choiceContext, card.Owner?.Creature);
        await CardHitAll(choiceContext, card, cardPlay, Var(card, "YmPer") * n);
    }

    /// <summary>Offertory Box: "Gain [E] for each Sakura." (its upgrade's
    /// draw is the row's `add:`).</summary>
    public static async Task EnergyPerSakura(PlayerChoiceContext choiceContext, CardModel card,
                                             CardPlay cardPlay)
    {
        var owner = card.Owner;
        var n = YaeShrine.Count(owner?.Creature);
        if (owner == null || n <= 0) return;
        await PlayerCmd.GainEnergy(n, owner);
    }

    /// <summary>Afterword: "Put every Annotated card from your Discard Pile
    /// into your Hand."</summary>
    public static Task Afterword(PlayerChoiceContext choiceContext, CardModel card,
                                 CardPlay cardPlay) =>
        card.Owner is { } owner ? YaeEditing.RecallAllAnnotated(owner) : Task.CompletedTask;

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

    // ---- The refill (review/active/yae-refill-2026-10-16.md) --------------

    /// <summary>Kitsune Barrage: "Deal 4 [5] Electro damage twice. If you
    /// have 3 or more Sakura, deal it 3 times." The shrine is read when it
    /// is played; one powered attack of the card with that many hits.
    /// </summary>
    public static Task Barrage(PlayerChoiceContext choiceContext, CardModel card,
                               CardPlay cardPlay) =>
        CardHit(choiceContext, card, cardPlay, Var(card, "YmAmount"),
                YaeLaw.BarrageHitCount(YaeShrine.Count(card.Owner?.Creature)));

    /// <summary>Sesshou Fang: "Deal 6 [8] Electro damage. If a Sakura is
    /// Level 3 or higher, deal 6 [8] more." One hit, the shrine read when it
    /// is played.</summary>
    public static Task LevelStrike(PlayerChoiceContext choiceContext, CardModel card,
                                   CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        var high = yae != null && YaeShrine.Live(yae)
                   && YaeShrineLedger.For(yae).AnyAtLevel(YaeLaw.FangLevel);
        return CardHit(choiceContext, card, cardPlay,
                       Var(card, "YmBase") + (high ? Var(card, "YmAmount") : 0));
    }

    /// <summary>Falling Blossom: "Your oldest Sakura withers; its Last Bloom
    /// strikes this enemy."</summary>
    public static async Task WitherOldestAt(PlayerChoiceContext choiceContext, CardModel card,
                                            CardPlay cardPlay) =>
        await YaeShrine.WitherOldest(choiceContext, card.Owner?.Creature, cardPlay.Target);

    /// <summary>Hide Behind the Shrine: "Your newest Sakura withers; if one
    /// did, gain 5 more [Block]", the card's own Block (YmAmount).</summary>
    public static async Task WitherNewestBlock(PlayerChoiceContext choiceContext, CardModel card,
                                               CardPlay cardPlay)
    {
        if (!await YaeShrine.WitherNewest(choiceContext, card.Owner?.Creature)) return;
        await CardBlock(card, cardPlay, Var(card, "YmAmount"));
    }

    /// <summary>The discard chooser's prompt for Rewrite (merged into the
    /// `cards` table by <c>KleeMod.InjectLocStrings</c>).</summary>
    public const string RewritePromptKey = "KLEEMOD-YAE_REWRITE.selectionScreenPrompt";

    public const string RewritePromptText = "Choose up to {Amount} cards to discard.";

    /// <summary>Rewrite: "Discard up to 2 [3] cards, then draw that many.
    /// Edit a card in your hand: Red Ink." The base game's Gambler's Brew
    /// chooser (zero to YmAmount cards, confirmed by hand), then the Edit,
    /// which can reach a card just drawn.</summary>
    public static async Task Rewrite(PlayerChoiceContext choiceContext, CardModel card,
                                     CardPlay cardPlay, YaeAnnotation annotation)
    {
        var owner = card.Owner;
        if (owner == null) return;
        var n = Var(card, "YmAmount");
        var hand = PileType.Hand.GetPile(owner).Cards.Count(c => !ReferenceEquals(c, card));
        if (n > 0 && hand > 0)
        {
            var picked = (await CardSelectCmd.FromHandForDiscard(
                choiceContext, owner,
                new CardSelectorPrefs(new LocString("cards", RewritePromptKey), 0, n)
                {
                    RequireManualConfirmation = true,
                },
                null, card)).Take(n).ToList();
            if (picked.Count > 0)
            {
                await CardCmd.DiscardAndDraw(choiceContext, picked, picked.Count);
            }
        }
        await YaeEditing.Edit(choiceContext, card, annotation, 1);
    }

    /// <summary>Dawn Prayer: "Your newest Sakura gains 2 [3] Levels."
    /// </summary>
    public static async Task LevelNewest(PlayerChoiceContext choiceContext, CardModel card,
                                         CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        if (YaeShrineLedger.For(yae).LevelNewest(Var(card, "YmAmount")))
            await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Kitsune's Blessing: "Your highest-Level Sakura gains 3 [4]
    /// Levels and lasts 2 more turns" (<paramref name="lasts"/>).</summary>
    public static async Task BlessHighest(PlayerChoiceContext choiceContext, CardModel card,
                                          CardPlay cardPlay, int lasts = 0)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        if (YaeShrineLedger.For(yae).Bless(Var(card, "YmAmount"), lasts) != null)
            await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// ONE POWERED ATTACK OF THE CARD, carrying Electro, of
    /// <paramref name="hits"/> hits (Kitsune Barrage's two or three). Red
    /// Ink rides it through the engine's enchant door.
    /// </summary>
    private static async Task CardHit(PlayerChoiceContext choiceContext,
                                      CardModel card, CardPlay cardPlay,
                                      int damage, int hits = 1)
    {
        if (cardPlay.Target is not { IsAlive: true } target || damage <= 0 || hits <= 0) return;
        using (HitElement.Carry(card, Element.Electro))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .Targeting(target)
                .WithHitCount(hits)
                .WithElementHitFx(Element.Electro)
                .Execute(choiceContext);
        }
    }

    /// <summary>ONE POWERED HIT OF THE CARD ON EVERY ENEMY, carrying
    /// Electro (Daisesshou).</summary>
    private static async Task CardHitAll(PlayerChoiceContext choiceContext,
                                         CardModel card, CardPlay cardPlay, int damage)
    {
        var combat = card.Owner?.Creature?.CombatState;
        if (combat == null || damage <= 0) return;
        if (!combat.HittableEnemies.Any(e => e.IsAlive)) return;
        using (HitElement.Carry(card, Element.Electro))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .TargetingAllOpponents(combat)
                .WithElementHitFx(Element.Electro)
                .SpawningHitVfxOnEachCreature()
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
