using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// VARKA'S OATH, ONE FIGHT'S WORTH (<c>review/active/varka-paper-kit-2026-09-28.md</c>
/// sec.3): the four Oath counts, his current element, and the per-play
/// bookkeeping the credit rule needs. PURE -- no command runs here -- so the
/// headless suite can pin every rule by value; <see cref="VarkaOath"/> is the
/// door that mutates it and pays the powers.
///
/// PER COMBAT, keyed on the creature and rolled to the combat the way
/// <c>KokomiOverhaulLedger</c> is: a new <c>CombatState</c> forgets
/// everything, which is "all four reset at the end of the fight". Sim twin:
/// the Varka ledger in <c>tier0/engine/varka_oath.py</c>.
/// </summary>
public sealed class VarkaOathLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, VarkaOathLedger> _byVarka = new();
    private static readonly object Gate = new();

    /// <summary>The four elements an Oath is kept in, in the order every
    /// surface lists them (sec.3: "Pyro, Hydro, Electro, Cryo").</summary>
    public static readonly IReadOnlyList<Element> Elements = new[]
    {
        Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo,
    };

    /// <summary>This creature's ledger for this combat, created on first ask
    /// and rolled to this round.</summary>
    public static VarkaOathLedger For(Creature creature)
    {
        lock (Gate)
        {
            var combat = (object?)creature.CombatState;
            if (!ReferenceEquals(_combat, combat))
            {
                _combat = combat;
                _byVarka.Clear();
            }
            if (!_byVarka.TryGetValue(creature, out var ledger))
            {
                ledger = new VarkaOathLedger();
                _byVarka[creature] = ledger;
            }
            ledger.RollTo(creature.CombatState?.RoundNumber ?? 0);
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
            _byVarka.Clear();
        }
    }

    private readonly Dictionary<Element, int> _oath = Elements.ToDictionary(e => e, _ => 0);

    /// <summary>His current element: the last Knight's, the last Oath element
    /// one of his other cards applied (the open Oath, 2026-09-30), or what
    /// Change of Guard chose. <see cref="Element.None"/> before the first.
    /// </summary>
    public Element Current { get; private set; } = Element.None;

    /// <summary>Has Boreas's Fang added Four Winds' Ascension this fight?
    /// </summary>
    public bool FangFired { get; set; }

    /// <summary>Every Swirl he has made this fight. Only DIFFS are read
    /// ("If it Swirls" snapshots it at the top of a play).</summary>
    public int SwirlsMade { get; private set; }

    /// <summary>Knights played this turn, replays included.</summary>
    public int KnightsThisTurn { get; private set; }

    /// <summary>Knights played this fight, replays included (the expansion's
    /// Charge of the Knights). Noelle counts.</summary>
    public int KnightsThisCombat { get; private set; }

    /// <summary>Swirls he made this turn (Eye of Stormterror).</summary>
    public int SwirlsThisTurn { get; private set; }

    /// <summary>While positive, a Swirl he makes pays twice (Crosscurrent).
    /// </summary>
    public int PaysTwice { get; set; }

    private int _round = -1;
    private int _changedRound = -1;
    private int _staticFieldRound = -1;
    private int _leftRound = -1;

    /// <summary>ELEMENT IDENTITIES sec.7 (2026-10-01): the element that
    /// stopped being current, the last time one did (<see cref="SetCurrent"/>),
    /// for the badge to flag on that turn.</summary>
    public Element LeftElement { get; private set; } = Element.None;

    /// <summary>Did an element stop being current this turn? Its count is
    /// <see cref="LeftElement"/>'s.</summary>
    public bool LeftThisTurn =>
        LeftElement != Element.None && _leftRound >= 0 && _leftRound == _round;

    /// <summary>Did his current element change this turn (Shifting Gale)?
    /// None to an element counts, as it does for Boreas Unbound.</summary>
    public bool ChangedThisTurn => _changedRound >= 0 && _changedRound == _round;

    /// <summary>Static Field: is this the turn's first Electro he applied?
    /// Marks the turn as spent when it is. Returns true once per turn.</summary>
    public bool TakeStaticField()
    {
        if (_staticFieldRound == _round) return false;
        _staticFieldRound = _round;
        return true;
    }

    /// <summary>Cards he played this turn, replays included (the rebalance's
    /// Rippling Guard reads the others; the playing card counts itself).
    /// </summary>
    public int PlaysThisTurn { get; private set; }

    /// <summary>A card play opened (<see cref="VarkaOath.BeginPlay"/>).
    /// </summary>
    public void NotePlay() => PlaysThisTurn++;

    private readonly List<int[]> _echoBlock = new();

    /// <summary>Whisper of Water (the rebalance, sec.3): <paramref
    /// name="block"/> at the start of each of his next
    /// <paramref name="turns"/> turns.</summary>
    public void AddEchoBlock(int block, int turns)
    {
        if (block > 0 && turns > 0) _echoBlock.Add(new[] { block, turns });
    }

    /// <summary>The echo Block due this turn start, each entry spending a
    /// turn. Returns the total.</summary>
    public int TakeEchoBlock()
    {
        var total = 0;
        foreach (var echo in _echoBlock)
        {
            total += echo[0];
            echo[1]--;
        }
        _echoBlock.RemoveAll(e => e[1] <= 0);
        return total;
    }

    /// <summary>The echo Block still owed, for a test.</summary>
    public int EchoEntries => _echoBlock.Count;

    /// <summary>A new round clears the turn's Knight, Swirl and play counts.
    /// </summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        _round = round;
        KnightsThisTurn = 0;
        SwirlsThisTurn = 0;
        PlaysThisTurn = 0;
    }

    // ---- reads ------------------------------------------------------------

    /// <summary>His Oath of <paramref name="element"/> (0 for any element
    /// that keeps none).</summary>
    public int Oath(Element element) =>
        _oath.TryGetValue(element, out var n) ? n : 0;

    /// <summary>The one count his cards read: the current element's, or all
    /// four together on a turn he drank the Elixir of the Four Winds.
    /// </summary>
    public int CurrentOath => AllFourThisTurn ? Total : Oath(Current);

    private int _allFourRound = -1;

    /// <summary>Elixir of the Four Winds: "This turn, your cards read your
    /// total Oath across all four elements." Read off the round the ledger
    /// is rolled to, so the next round ends it.</summary>
    public bool AllFourThisTurn => _allFourRound >= 0 && _allFourRound == _round;

    /// <summary>The Elixir is drunk: this round reads all four.</summary>
    public void ReadAllFourThisTurn() => _allFourRound = _round;

    /// <summary>How many elements he has any Oath in (the
    /// <c>oath_elements</c> count; Tailwind Guard's, cut by the combo pass).
    /// </summary>
    public int ElementsWithOath => Elements.Count(e => Oath(e) > 0);

    /// <summary>All four together.</summary>
    public int Total => Elements.Sum(Oath);

    // ---- writes (VarkaOath calls these; each is pure) ---------------------

    /// <summary>Add <paramref name="n"/> Oath of an Oath element. Returns
    /// whether anything was added.</summary>
    public bool Add(Element element, int n)
    {
        if (n <= 0 || !_oath.ContainsKey(element)) return false;
        _oath[element] += n;
        return true;
    }

    /// <summary>Make <paramref name="element"/> current. Returns whether the
    /// current element CHANGED (none to Pyro is a change; Pyro to Pyro is
    /// not).</summary>
    public bool SetCurrent(Element element)
    {
        if (!_oath.ContainsKey(element) || element == Current) return false;
        if (Current != Element.None)
        {
            LeftElement = Current;
            _leftRound = _round;
        }
        Current = element;
        _changedRound = _round;
        return true;
    }

    /// <summary>A Knight was played (or replayed) this turn.</summary>
    public void NoteKnight()
    {
        KnightsThisTurn++;
        KnightsThisCombat++;
    }

    /// <summary>A Swirl he made, on <paramref name="swirled"/>, of a
    /// <paramref name="element"/> aura.</summary>
    public void NoteSwirl(Creature swirled, Element element = Element.None)
    {
        SwirlsMade++;
        SwirlsThisTurn++;
        if (_scopeDepth > 0)
        {
            _swirledThisPlay.Add(swirled);
            if (element != Element.None) _swirledElementsThisPlay.Add(element);
        }
    }

    /// <summary>Banner of the West Wind: every point of
    /// <paramref name="from"/> moves to <paramref name="to"/>. Not a gain.
    /// Returns how many moved.</summary>
    public int MoveOath(Element from, Element to)
    {
        if (from == to || !_oath.ContainsKey(from) || !_oath.ContainsKey(to))
        {
            return 0;
        }
        var moved = _oath[from];
        _oath[from] = 0;
        _oath[to] += moved;
        return moved;
    }

    /// <summary>Rally to the Banner: every point moves to the current
    /// element. Nothing without one.</summary>
    public void Rally()
    {
        if (Current == Element.None) return;
        var total = Total;
        foreach (var e in Elements) _oath[e] = 0;
        _oath[Current] = total;
    }

    // ---- the per-play credit scope ----------------------------------------

    private int _scopeDepth;
    /// <summary>Per open scope, innermost last: is it an OPEN-OATH play (a
    /// card of his that is not a Knight), and which card. Baron Bunny's
    /// scope and a Knight's play are not.</summary>
    private readonly List<(bool Open, object? Card)> _plays = new();
    private readonly HashSet<(bool Swirl, Element Element)> _credited = new();
    private readonly List<Creature> _swirledThisPlay = new();
    private readonly List<Element> _swirledElementsThisPlay = new();

    /// <summary>Is a card play (or a scoped event) open?</summary>
    public bool Scoped => _scopeDepth > 0;

    /// <summary>While positive, an application credits nothing (Four Winds'
    /// Ascension's elemental hit).</summary>
    public int SuppressApply { get; set; }

    /// <summary>While positive, a Swirl credits nothing either: a relic's or
    /// a potion's Swirls (the expansion paper, sec.4: "Relic and potion
    /// applications gain no Oath"). The payout still pays.</summary>
    public int SuppressSwirl { get; set; }

    /// <summary>A play opens: its credits start empty. <paramref name="open"/>
    /// marks a play of his own non-Knight card (<paramref name="card"/>),
    /// whose applications set his current element.</summary>
    public void OpenScope(bool open = false, object? card = null)
    {
        if (_scopeDepth++ == 0)
        {
            _credited.Clear();
            _swirledThisPlay.Clear();
            _swirledElementsThisPlay.Clear();
            _plays.Clear();
            _gainClauses.Clear();
            FangInThisPlay = null;
            _bannerPaid = false;
        }
        _plays.Add((open, card));
    }

    private bool _bannerPaid;

    /// <summary>Unwavering Banner (the combo pass, 2026-10-04): "Whenever
    /// another card would [change your current element], gain 1 Oath of your
    /// current element instead." Once per play, however many switches the
    /// card would have made (Tempest of the Four Winds would make three).
    /// Returns true the first time a play asks.</summary>
    public bool TakeBannerPay()
    {
        if (_bannerPaid) return false;
        _bannerPaid = true;
        return true;
    }

    /// <summary>A play ends.</summary>
    public void CloseScope()
    {
        if (_scopeDepth > 0) _scopeDepth--;
        if (_plays.Count > 0) _plays.RemoveAt(_plays.Count - 1);
    }

    /// <summary>
    /// THE OPEN OATH ([USER], 2026-09-30): "Any card that applies an element
    /// other than Anemo counts for Oath effects". Does an application of
    /// <paramref name="element"/> make it his current element? Only inside a
    /// play of his own non-Knight card (a Knight set it at the top of its
    /// play), only for the four Oath elements, never inside a hit that
    /// credits nothing (Four Winds' Ascension's), and, when the hit names a
    /// card, only when it is the card being played. Baron Bunny's burst,
    /// relics, potions and powers outside a play are not plays. PURE.
    /// </summary>
    public bool OpenOathSwitches(Element element, object? cardSource = null)
    {
        if (_plays.Count == 0 || !_oath.ContainsKey(element)) return false;
        if (SuppressApply > 0) return false;
        var (open, card) = _plays[^1];
        if (!open) return false;
        return cardSource == null || ReferenceEquals(cardSource, card);
    }

    /// <summary>
    /// THE CREDIT RULE (sec.3): "counted per card, not per enemy". Within one
    /// open scope, the first application of an element credits 1 and the
    /// first Swirl of an element credits 1, the two separately; every later
    /// one credits nothing. Outside any scope each event credits.
    /// </summary>
    public bool TryCredit(bool swirl, Element element)
    {
        if (!_oath.ContainsKey(element)) return false;
        if (!swirl && SuppressApply > 0) return false;
        if (swirl && SuppressSwirl > 0) return false;
        if (_scopeDepth == 0) return true;
        return _credited.Add((swirl, element));
    }

    /// <summary>The enemies this play has Swirled, in order (Storm Surge).
    /// </summary>
    public IReadOnlyList<Creature> SwirledThisPlay => _swirledThisPlay;

    /// <summary>The elements this play has Swirled, in order (Downburst).
    /// </summary>
    public IReadOnlyList<Element> SwirledElementsThisPlay =>
        _swirledElementsThisPlay;

    // ---- where each gain came from (the rebalance round, 2026-10-03) ------

    private readonly List<string> _gainClauses = new();

    /// <summary>The open play's gains, in order, as
    /// <see cref="VarkaOath.GainClause"/> prints them, and the name of the
    /// relic one of them made add Four Winds' Ascension (Boreas's Fang, or
    /// Wolf's Gravestone after Orobas), or null.</summary>
    public IReadOnlyList<string> GainClauses => _gainClauses;
    public string? FangInThisPlay { get; private set; }

    /// <summary>File one gain's clause against the open play.</summary>
    public void NoteGainClause(string clause) => _gainClauses.Add(clause);

    /// <summary>The Fang (by its printed name) fired inside the open play.
    /// </summary>
    public void NoteFangInPlay(string relic) => FangInThisPlay = relic;

    /// <summary>Hand back and forget the outermost play's gains.</summary>
    public (List<string> Clauses, string? Fang) TakeGainClauses()
    {
        var taken = (new List<string>(_gainClauses), FangInThisPlay);
        _gainClauses.Clear();
        FangInThisPlay = null;
        return taken;
    }
}

/// <summary>Where one Oath gain came from: an element his card applied, a
/// Swirl it made, or anything else (a card's own text, a power, a relic).
/// </summary>
public enum OathSource
{
    Other,
    Applied,
    Swirl,
}

/// <summary>
/// VARKA'S OATH RULES (sec.3, sec.4), the one door that moves the ledger and
/// pays for it. Every Knight play, every application and every Swirl of his
/// passes here once:
///
///   * <see cref="BeginPlay"/> / <see cref="EndPlay"/> bracket each card play
///     (<c>KleeElementalHooks</c>), and a Knight sets his current element
///     before its effects resolve (Boreas Unbound).
///   * <see cref="NoteApplication"/> is called where a hit or an application
///     of an aura element lands on an enemy (<c>KleeElementalHooks.BeforeDamageReceived</c>,
///     <c>ElementalHit.Deal</c> / <c>ApplyOnly</c>); a Swirl's spread never
///     passes it.
///   * <see cref="OnSwirl"/> is called from <c>ReactionEffects.Resolve</c>,
///     the single site every reaction passes: the credit, then his current
///     element's payout.
///   * <see cref="Gain"/> is every gain: Dawn Wind's March and Boreas's Fang.
/// </summary>
public static class VarkaOath
{
    /// <summary>Is this creature Varka?</summary>
    public static bool Live(Creature? creature) => VarkaPrototype.IsVarka(creature);

    // ---- reads (PURE; the generated readers and the badge take these) -----

    public static Element Current(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).Current : Element.None;

    public static bool HasCurrent(Creature? creature) =>
        Current(creature) != Element.None;

    public static int Count(Creature? creature, Element element) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).Oath(element) : 0;

    public static int CurrentOath(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).CurrentOath : 0;

    public static int ElementsWithOath(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).ElementsWithOath : 0;

    /// <summary>Half his total Oath, rounded down (the
    /// <c>half_total_oath</c> count; Gale Mantle's, cut by the combo pass).
    /// </summary>
    public static int HalfTotalOath(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).Total / 2 : 0;

    public static int KnightsPlayedThisTurn(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).KnightsThisTurn : 0;

    public static int SwirlsMadeBy(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).SwirlsMade : 0;

    // ---- the expansion's reads (2026-10-01) ---------------------------------

    /// <summary>Charge of the Knights: Knights played this fight.</summary>
    public static int KnightsInCombat(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).KnightsThisCombat : 0;

    /// <summary>Shifting Gale: did his current element change this turn?
    /// </summary>
    public static bool ElementChangedThisTurn(Creature? creature) =>
        creature != null && Live(creature)
        && VarkaOathLedger.For(creature).ChangedThisTurn;

    /// <summary>Hittable enemies wearing an aura (the
    /// <c>enemies_with_aura</c> count; West Wind Shield's, cut by the combo
    /// pass).</summary>
    public static int EnemiesWithAura(Creature? creature) =>
        creature?.CombatState == null || !Live(creature) ? 0
            : creature.CombatState.HittableEnemies.Count(
                e => AuraCmd.Find(e) != null);

    /// <summary>The element a Knight card sets, or None for any other card.
    /// PURE.</summary>
    public static Element KnightElement(CardModel? card) =>
        VarkaRules.IsKnight(card) && card is ICompanionCard companion
            ? companion.CompanionElement : Element.None;

    /// <summary>Is <paramref name="element"/> one an Oath is kept in? Geo
    /// (Noelle: Steadfast Maid) is not. PURE.</summary>
    public static bool IsOathElement(Element element) =>
        VarkaOathLedger.Elements.Contains(element);

    // ---- the play bracket -------------------------------------------------

    /// <summary>
    /// A card play opens (every replay too). Opens his credit scope (an
    /// open-Oath one for any card that is not a Knight, <see
    /// cref="VarkaOathLedger.OpenOathSwitches"/>), and if
    /// the card is a Knight sets his current element BEFORE its effects:
    /// Boreas Unbound pays when it changes (sec.6).
    /// </summary>
    public static async Task BeginPlay(CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (!Live(owner)) return;
        var ledger = VarkaOathLedger.For(owner!);
        ledger.OpenScope(open: !VarkaRules.IsKnight(card), card: card);
        ledger.NotePlay();
        if (!VarkaRules.IsKnight(card)) return;
        ledger.NoteKnight();
        // Noelle (the expansion) is a Geo Knight: a Knight for every
        // Knight-played read, but Geo keeps no Oath, so she sets nothing.
        var element = KnightElement(card);
        if (!IsOathElement(element)) return;
        await SetCurrent(new ThrowingPlayerChoiceContext(), owner!, element,
                         knight: true);
    }

    /// <summary>A card play ends: the scope closes, then the expansion's
    /// after-play Power, Wolfpack on Four Winds' Ascension. Every replay is
    /// a play. (Assembly at the Cathedral left this site with co-op notes
    /// pick 2: it pays at <see cref="NoteApplication"/> now.)</summary>
    public static async Task EndPlay(
        PlayerChoiceContext choiceContext, CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (!Live(owner)) return;
        var ledger = VarkaOathLedger.For(owner!);
        ledger.CloseScope();
        // The rebalance round (2026-10-03): the play's Oath gains, said over
        // his head once the card has resolved, naming the card.
        if (!ledger.Scoped)
        {
            var (clauses, fang) = ledger.TakeGainClauses();
            var line = GainLine(Safe(() => card.Title?.ToString()), clauses, fang);
            if (line.Length > 0) global::KleeMod.Vfx.KurageBeat.Say(owner, line);
        }
        if (card is ProtoVkFourWindsAscension)
        {
            foreach (var wolves in owner!.Powers.OfType<WolfpackPower>().ToList())
            {
                await wolves.OnAscensionPlayed(card);
            }
        }
    }

    /// <summary>An event outside a card play that must credit as one
    /// (Baron Bunny's burst). Dispose closes it.</summary>
    public static IDisposable Scope(Creature creature)
    {
        if (!Live(creature)) return new Closer(null);
        var ledger = VarkaOathLedger.For(creature);
        ledger.OpenScope();
        return new Closer(ledger.CloseScope);
    }

    /// <summary>While open, an application credits nothing: Four Winds'
    /// Ascension's elemental hit (sec.4: "gains no Oath").</summary>
    public static IDisposable NoApplyCredit(Creature creature)
    {
        if (!Live(creature)) return new Closer(null);
        var ledger = VarkaOathLedger.For(creature);
        ledger.SuppressApply++;
        return new Closer(() => ledger.SuppressApply--);
    }

    /// <summary>While open, neither an application nor a Swirl credits Oath,
    /// and no application switches his element: a relic's or a potion's
    /// (Dandelion Seeds, Bottled Gale).</summary>
    public static IDisposable NoCredit(Creature creature)
    {
        if (!Live(creature)) return new Closer(null);
        var ledger = VarkaOathLedger.For(creature);
        ledger.SuppressApply++;
        ledger.SuppressSwirl++;
        return new Closer(() =>
        {
            ledger.SuppressApply--;
            ledger.SuppressSwirl--;
        });
    }

    private sealed class Closer : IDisposable
    {
        private Action? _close;
        public Closer(Action? close) => _close = close;
        public void Dispose()
        {
            _close?.Invoke();
            _close = null;
        }
    }

    // ---- the current element ----------------------------------------------

    /// <summary>
    /// Make <paramref name="element"/> his current element. A change pays
    /// Boreas Unbound, Cycle of Seasons and Windborne Resolve. The badge
    /// follows. (<paramref name="knight"/> paid Favonian Standard, retired by
    /// the Varka defence paper; kept for its callers.)
    /// </summary>
    public static async Task SetCurrent(
        PlayerChoiceContext choiceContext, Creature varka, Element element,
        bool knight)
    {
        if (!Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
        var was = ledger.Current;
        if (ledger.SetCurrent(element))
        {
            // His relics (the expansion paper, sec.4): Banner of the West Wind
            // carries the old element's Oath over first, then Windblume
            // Garland's Block.
            await Relics.VarkaArmRelics.OnElementChanged(varka, was, element);
            foreach (var unbound in varka.Powers.OfType<BoreasUnboundPower>().ToList())
            {
                await unbound.OnElementChanged();
            }
            // Cycle of Seasons (the AoE trim): damage to a random enemy.
            foreach (var cycle in varka.Powers.OfType<CycleOfSeasonsPower>().ToList())
            {
                await cycle.OnElementChanged(choiceContext);
            }
            // Windborne Resolve (Varka defence): its Block twin.
            foreach (var resolve in varka.Powers.OfType<WindborneResolvePower>().ToList())
            {
                await resolve.OnElementChanged();
            }
        }
        await OathBadge.Sync(choiceContext, varka);
    }

    /// <summary>
    /// A card of his that is NOT a Knight says "<paramref name="element"/>
    /// becomes your current element" (Stoke the Flames, 2026-10-05). The same
    /// fork the open Oath's switch takes in <see cref="NoteApplication"/>:
    /// under Unwavering Banner the Banner holds it (<see cref="BannerHolds"/>),
    /// otherwise it is made current. Sim twin: <c>varka_oath.card_makes_current</c>.
    /// </summary>
    public static async Task CardMakesCurrent(
        PlayerChoiceContext choiceContext, Creature varka, Element element)
    {
        if (!Live(varka) || !IsOathElement(element)) return;
        if (varka.HasPower<UnwaveringBannerPower>())
        {
            await BannerHolds(choiceContext, varka, element);
            return;
        }
        await SetCurrent(choiceContext, varka, element, knight: false);
    }

    // ---- gains --------------------------------------------------------------

    /// <summary>
    /// Every Oath gain: add it, pay Dawn Wind's March when it is the current
    /// element's, and let Boreas's Fang add Four Winds' Ascension the first
    /// time each combat (sec.4). One call is one gain event.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature varka, Element element,
        int n, OathSource source = OathSource.Other)
    {
        if (!Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
        // Oath Unto Death (the expansion): "Whenever you gain Oath of your
        // current element, gain 1 more." Inside this one gain event.
        if (element == ledger.Current && n > 0)
        {
            n += varka.Powers.OfType<OathUntoDeathPower>().Sum(p => p.Amount);
        }
        if (!ledger.Add(element, n)) return;
        if (element == ledger.Current)
        {
            foreach (var march in varka.Powers.OfType<DawnWindsMarchPower>().ToList())
            {
                await CreatureCmd.GainBlock(varka, march.Amount,
                    ValueProp.Unpowered, null, fast: true);
            }
        }
        await OathBadge.Sync(choiceContext, varka);
        // The rebalance round (2026-10-03): every gain names its source. The
        // badge flashes; the play's line is said at its end (EndPlay); a gain
        // outside a play is said now; and the seat page's resolution row
        // files it under the card.
        foreach (var badge in varka.Powers.OfType<OathBadgePower>().ToList())
        {
            badge.Pulse();
        }
        var clause = GainClause(element, n, source);
        ResolutionLedger.NoteOath(element.ToString(), n, SourceWord(source));
        if (ledger.Scoped) ledger.NoteGainClause(clause);
        else global::KleeMod.Vfx.KurageBeat.Say(varka, clause);
        if (!ledger.FangFired && varka.Player is { } player
            && Relics.BoreasFang.HeldBy(player) is { } fang)
        {
            ledger.FangFired = true;
            ResolutionLedger.NoteFangAscension(fang.RelicName);
            if (ledger.Scoped) ledger.NoteFangInPlay(fang.RelicName);
            await fang.AddAscension(player);
        }
    }

    /// <summary>The source as the seat page and the line print it: "applied",
    /// "Swirl", or "" for anything else. PURE.</summary>
    public static string SourceWord(OathSource source) => source switch
    {
        OathSource.Applied => "applied",
        OathSource.Swirl => "Swirl",
        _ => "",
    };

    /// <summary>One gain, as said over his head: "+1 Pyro Oath (Swirl)".
    /// PURE.</summary>
    public static string GainClause(Element element, int n, OathSource source)
    {
        var word = SourceWord(source);
        return $"+{n} {element} Oath" + (word.Length > 0 ? $" ({word})" : "");
    }

    /// <summary>A play's gains in one line: "Amber: Precise Shot — +1 Pyro
    /// Oath (applied)", and the card <paramref name="fang"/> (the relic held:
    /// Boreas's Fang, or Wolf's Gravestone after Orobas) added when one of
    /// them made it. Empty when the play gained nothing. PURE.</summary>
    public static string GainLine(string? card, IReadOnlyList<string> clauses,
                                  string? fang)
    {
        if (clauses.Count == 0) return string.Empty;
        var line = string.Join(", ", clauses);
        if (!string.IsNullOrEmpty(card)) line = $"{card} — {line}";
        if (!string.IsNullOrEmpty(fang)) line += $". {fang}: Four Winds' Ascension";
        return line;
    }

    private static string Safe(Func<string?> read)
    {
        try
        {
            return read() ?? string.Empty;
        }
        catch (Exception)
        {
            return string.Empty;
        }
    }

    /// <summary>
    /// An element of <paramref name="element"/> landed on an enemy from
    /// <paramref name="applier"/>: a hit that sticks, refreshes or reacts, or
    /// a damage-less application. Credits 1 Oath once per play (sec.3).
    /// Inside a play of his own non-Knight card the element first becomes his
    /// current element (the open Oath, 2026-09-30), so the gain is the current
    /// element's and Dawn Wind's March pays, as a Knight's does; the last
    /// one applied wins. <paramref name="cardSource"/> is the hit's card,
    /// when the hit names one. <paramref name="target"/> is the enemy it
    /// landed on (Wildfire Oath pays it).
    /// </summary>
    public static async Task NoteApplication(
        PlayerChoiceContext choiceContext, Creature? applier, Element element,
        CardModel? cardSource = null, Creature? target = null)
    {
        if (applier == null || !Live(applier) || !element.LeavesAura()) return;
        var ledger = VarkaOathLedger.For(applier);
        // Static Field (the expansion): the turn's first Electro he applies
        // draws, whether or not it credits.
        if (element == Element.Electro
            && applier.Powers.OfType<StaticFieldPower>().ToList() is { Count: > 0 } fields
            && ledger.TakeStaticField())
        {
            foreach (var field in fields) await field.Draw(choiceContext);
        }
        // Unwavering Banner (reworded by the combo pass, 2026-10-04): only
        // Knights move it, so the open Oath's switch is off, and the card
        // gains 1 Oath of the current element instead (once per play).
        if (ledger.OpenOathSwitches(element, cardSource))
        {
            if (applier.HasPower<UnwaveringBannerPower>())
            {
                await BannerHolds(choiceContext, applier, element);
            }
            else
            {
                await SetCurrent(choiceContext, applier, element, knight: false);
            }
        }
        if (ledger.TryCredit(swirl: false, element))
        {
            await Gain(choiceContext, applier, element, 1, OathSource.Applied);
        }
        // Wildfire Oath (Varka Wildfire Oath and Short Circuit, 2026-10-03):
        // "Whenever you apply Pyro to an enemy, deal damage equal to your
        // Pyro Oath to it" -- after the credit above, so the Oath this
        // application just raised counts. Element-less, so its hit never
        // comes back through here. Sim twin: `varka_oath.note_hit`.
        if (element == Element.Pyro && target != null)
        {
            foreach (var wildfire in applier.Powers
                         .OfType<WildfireOathPower>().ToList())
            {
                await wildfire.OnPyroApplied(choiceContext, target);
            }
        }
        // Assembly at the Cathedral (co-op notes pick 2, 2026-10-02):
        // "Whenever you apply an element", whether or not it credits. Its
        // hit is element-less, so it never comes back through here.
        foreach (var assembly in applier.Powers
                     .OfType<AssemblyAtTheCathedralPower>().ToList())
        {
            await assembly.OnElementApplied(choiceContext);
        }
    }

    /// <summary>
    /// UNWAVERING BANNER'S PAYOUT (the combo pass, 2026-10-04): a card of his
    /// that is not a Knight would make <paramref name="element"/> his current
    /// element, and the Banner holds it. When that would have been a change
    /// (another element is current), gain 1 Oath of the current element,
    /// once per play. With no current element there is nothing to gain.
    /// Sim twin: <c>varka_oath.banner_holds</c>.
    /// </summary>
    public static async Task BannerHolds(
        PlayerChoiceContext choiceContext, Creature varka, Element element)
    {
        if (!Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
        var current = ledger.Current;
        if (current == Element.None || element == current) return;
        if (!ledger.TakeBannerPay()) return;
        foreach (var banner in varka.Powers.OfType<UnwaveringBannerPower>().ToList())
        {
            banner.Pulse();
        }
        // "gain 1 Oath" -- the printed 1, as Vow of the Blade's.
        await Gain(choiceContext, varka, current, 1);
    }

    // ---- the Swirl ------------------------------------------------------------

    /// <summary>
    /// A SWIRL <paramref name="dealer"/> MADE of a <paramref name="swirled"/>
    /// aura on <paramref name="target"/>: count it, credit its element once
    /// per play, then pay his current element's one effect (sec.3). A dealer
    /// who is not a live Varka pays nothing.
    /// </summary>
    internal static async Task OnSwirl(
        PlayerChoiceContext choiceContext, Creature target, Creature? dealer,
        Element swirled)
    {
        if (dealer == null || !Live(dealer)) return;
        var ledger = VarkaOathLedger.For(dealer);
        ledger.NoteSwirl(target, swirled);
        if (ledger.TryCredit(swirl: true, swirled))
        {
            await Gain(choiceContext, dealer, swirled, 1, OathSource.Swirl);
        }
        var current = ledger.Current;
        // Stormterror's Scale: "Your Swirls pay twice." The expansion:
        // Crosscurrent's Swirl pays twice too (the two multiply); Twin Gales
        // pays the element Swirled as well, once, when it is not the current
        // one.
        var twin = dealer.HasPower<TwinGalesPower>();
        var times = Relics.StormterrorsScale.TakePayouts(dealer)
                    * (ledger.PaysTwice > 0 ? 2 : 1);
        for (var pay = 0; pay < times; pay++)
        {
            await Pay(choiceContext, target, dealer, current);
            if (twin && IsOathElement(swirled) && swirled != current)
            {
                await Pay(choiceContext, target, dealer, swirled);
            }
        }
        // Twin Gales (the Varka payoff round, 2026-10-10): the seat page says
        // what each Swirl paid. Numbers held; this is a line, not a rule.
        if (twin)
        {
            var paid = TwinGalesPaid(current, swirled, times);
            if (paid.Length > 0)
            {
                ResolutionLedger.NoteEvent(ResolutionLedger.SwirlPaid,
                    swirled.ToString(), target, paid);
            }
        }
        // Eye Wall: Block per Swirl this turn. Eye of Stormterror: the first
        // three Swirls each turn draw.
        foreach (var wall in dealer.Powers.OfType<EyeWallPower>().ToList())
        {
            await CreatureCmd.GainBlock(dealer, wall.Amount,
                ValueProp.Unpowered, null, fast: true);
        }
        if (ledger.SwirlsThisTurn <= VarkaLaw.EyeOfStormterrorSwirls)
        {
            foreach (var eye in dealer.Powers.OfType<EyeOfStormterrorPower>().ToList())
            {
                await eye.Draw(choiceContext);
            }
        }
        if (current != Element.None)
        {
            Log.Info($"[{KleeMod.ModId}] VARKA Swirl on {target.Name}: "
                   + $"{swirled} Oath, paid {current}.");
        }
    }

    /// <summary>One element's Swirl payout in words, with
    /// <see cref="VarkaLaw"/>'s numbers: "Pyro (3 damage)". Empty for an
    /// element that pays nothing. PURE.</summary>
    public static string PayoutWords(Element element) => element switch
    {
        Element.Pyro => $"Pyro ({VarkaLaw.SwirlPyroDamage} damage)",
        Element.Hydro => $"Hydro ({VarkaLaw.SwirlHydroBlock} Block)",
        Element.Cryo => $"Cryo ({VarkaLaw.SwirlCryoVulnerable} Vulnerable)",
        Element.Electro =>
            $"Electro ({VarkaLaw.SwirlElectroDamageAll} damage to ALL)",
        _ => string.Empty,
    };

    /// <summary>What one Swirl paid under Twin Gales, as the seat page prints
    /// it: the current element's payout, and the Swirled element's when it is
    /// another Oath element, joined by "and", with " x2" when the Swirl paid
    /// <paramref name="times"/> over (Stormterror's Scale, Crosscurrent).
    /// Empty when nothing paid. PURE.</summary>
    public static string TwinGalesPaid(Element current, Element swirled,
                                       int times)
    {
        if (times <= 0) return string.Empty;
        var parts = new List<string>();
        var first = PayoutWords(current);
        if (first.Length > 0) parts.Add(first);
        if (IsOathElement(swirled) && swirled != current)
        {
            parts.Add(PayoutWords(swirled));
        }
        if (parts.Count == 0) return string.Empty;
        var line = string.Join(" and ", parts);
        return times > 1 ? $"{line}, x{times}" : line;
    }

    /// <summary>
    /// ONE SWIRL PAYOUT of <paramref name="element"/> (sec.3). (Wildfire Oath
    /// widened Pyro's until element identities; Absolute Zero widened Cryo's
    /// until the rebalance, 2026-10-03, made it a debuff payoff,
    /// <see cref="AbsoluteZeroPower"/>.)
    /// </summary>
    private static async Task Pay(
        PlayerChoiceContext choiceContext, Creature target, Creature dealer,
        Element element)
    {
        var enemies = dealer.CombatState?.HittableEnemies.ToList()
                      ?? new List<Creature>();
        switch (element)
        {
            case Element.Pyro:
                if (target.IsAlive)
                {
                    await ElementalHit.DealUnelemented(
                        choiceContext, target, VarkaLaw.SwirlPyroDamage, dealer,
                        powered: false);
                }
                break;
            case Element.Hydro:
                await CreatureCmd.GainBlock(dealer, VarkaLaw.SwirlHydroBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case Element.Cryo:
                if (target.IsAlive)
                {
                    await PowerCmd.Apply<VulnerablePower>(
                        choiceContext, target, VarkaLaw.SwirlCryoVulnerable,
                        applier: dealer, cardSource: null);
                }
                break;
            case Element.Electro:
                foreach (var enemy in enemies)
                {
                    if (!enemy.IsAlive) continue;
                    await ElementalHit.DealUnelemented(
                        choiceContext, enemy, VarkaLaw.SwirlElectroDamageAll,
                        dealer, powered: false);
                }
                break;
        }
    }

    /// <summary>
    /// ELEMENT IDENTITIES sec.7: would playing <paramref name="card"/> now
    /// make <paramref name="element"/> his current element? Only for a live
    /// Varka owner, only when another element (or none) is current, and, for
    /// any card but a Knight, only without Unwavering Banner (the open Oath's
    /// switch). The element is the card's own (codegen's
    /// <c>varka_switch_element</c>). PURE apart from the reads.
    /// </summary>
    public static bool WouldSwitchTo(CardModel? card, Element element)
    {
        Creature? owner;
        try
        {
            owner = card?.Owner?.Creature;
        }
        catch (Exception)
        {
            // A canonical (compendium) copy asserts on Owner.
            return false;
        }
        if (owner?.CombatState == null || !Live(owner)) return false;
        if (!IsOathElement(element)) return false;
        if (Current(owner) == element) return false;
        return VarkaRules.IsKnight(card)
            || !owner.HasPower<UnwaveringBannerPower>();
    }

    /// <summary>The payout sentence for <paramref name="element"/>, the one
    /// the badge and the current-element tip print. PURE.</summary>
    public static string PayoutSentence(Element element) => element switch
    {
        Element.Pyro => $"Your Swirls deal {VarkaLaw.SwirlPyroDamage} damage "
                      + "to that enemy.",
        Element.Hydro => $"Your Swirls give you {VarkaLaw.SwirlHydroBlock} "
                       + "[gold]Block[/gold].",
        Element.Cryo => $"Your Swirls apply {VarkaLaw.SwirlCryoVulnerable} "
                      + "[gold]Vulnerable[/gold] to that enemy.",
        Element.Electro => $"Your Swirls deal {VarkaLaw.SwirlElectroDamageAll} "
                         + "damage to ALL enemies.",
        _ => "",
    };

    // ---- the turn start (after the draw) -----------------------------------

    /// <summary>
    /// His start-of-turn powers, in a fixed order: Baron Bunny's burst, then
    /// Sworn Brotherhood, then The Order Answers. (Oath of the Knights, which
    /// paid after Sworn Brotherhood, left with its card in the combo pass.)
    /// Called from <c>KleeElementalHooks.AfterPlayerTurnStart</c>.
    /// </summary>
    public static async Task TurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        var varka = player.Creature;
        if (!Live(varka)) return;
        // Whisper of Water (the rebalance, sec.3): "and at the start of your
        // next 2 turns". Unpowered, as BlockNextTurnPower's payout is.
        var echo = VarkaOathLedger.For(varka).TakeEchoBlock();
        if (echo > 0)
        {
            await CreatureCmd.GainBlock(varka, echo, ValueProp.Unpowered, null,
                                        fast: true);
        }
        // Weathervane (the expansion), first: Sworn Brotherhood below then
        // gains the element it chose. Since the combo pass (2026-10-04)
        // "Only Knights can change your current element", so Unwavering
        // Banner stops it; it is not a card, so it gains nothing instead.
        if (varka.HasPower<WeathervanePower>()
            && !varka.HasPower<UnwaveringBannerPower>())
        {
            await Weathervane(choiceContext, player);
        }
        foreach (var bunny in varka.Powers.OfType<VarkaBaronBunnyPower>().ToList())
        {
            await bunny.Fire(choiceContext);
        }
        foreach (var sworn in varka.Powers.OfType<SwornBrotherhoodPower>().ToList())
        {
            foreach (var element in VarkaOathLedger.Elements)
            {
                await Gain(choiceContext, varka, element, sworn.Amount);
            }
        }
        // Power cost sweep, 2026-09-30: the base card, current element only.
        foreach (var sworn in varka.Powers.OfType<SwornBrotherhoodCurrentPower>().ToList())
        {
            var element = Current(varka);
            if (element == Element.None) continue;
            await Gain(choiceContext, varka, element, sworn.Amount);
        }
        // The Order Answers (the expansion), last: a random pool Knight at
        // its own cost, one per stack.
        foreach (var order in varka.Powers.OfType<TheOrderAnswersPower>().ToList())
        {
            for (var i = 0; i < order.Amount; i++)
            {
                await VarkaRules.AddRandomKnight(player, free: false);
            }
        }
    }

    /// <summary>
    /// Weathervane: "At the start of your turn, you may choose an element you
    /// have Oath in; it becomes your current element." A grid of the
    /// elements he holds Oath in, cancelable (the "may"); nothing to ask when
    /// he holds none, or holds only the current one.
    /// </summary>
    private static async Task Weathervane(
        PlayerChoiceContext choiceContext, Player player)
    {
        var varka = player.Creature;
        var ledger = VarkaOathLedger.For(varka);
        var held = VarkaOathLedger.Elements.Where(e => ledger.Oath(e) > 0).ToList();
        if (held.Count == 0 || (held.Count == 1 && held[0] == ledger.Current))
        {
            return;
        }
        var element = await VarkaRules.ChooseElement(
            choiceContext, player, held, optional: true);
        if (element == Element.None) return;
        await SetCurrent(choiceContext, varka, element, knight: false);
    }
}

/// <summary>
/// VARKA'S CARD VERBS (the sheet's `varka` op): one method per `kind`, each
/// called as <c>await VarkaCards.Kind(choiceContext, this, cardPlay)</c> by
/// the generated card, reading its own numbers off the card's `Vk*` vars.
/// Sim twins: the `varka` op kinds in <c>tier0/engine/varka_oath.py</c>.
/// </summary>
public static class VarkaCards
{
    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    /// <summary>Favonius Drill: "Apply your current element to an enemy."
    /// </summary>
    public static async Task ApplyCurrentElement(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (element == Element.None || cardPlay.Target is not { IsAlive: true } target)
        {
            return;
        }
        await ElementalHit.ApplyOnly(choiceContext, target, element, owner);
    }

    /// <summary>Vow of the Blade: "Gain 1 Oath of your current element".
    /// </summary>
    public static async Task GainCurrentOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (owner == null || element == Element.None) return;
        await VarkaOath.Gain(choiceContext, owner, element, 1);
    }

    /// <summary>
    /// Four Winds' Ascension's second hit: "Then deal 3 damage for each Oath
    /// of your current element, as that element." (The upgrade cuts the cost,
    /// not this number.) The Oath is read after
    /// the Anemo hit, and this hit credits no Oath (sec.4).
    /// </summary>
    public static Task AscensionHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        CurrentElementHit(choiceContext, card, cardPlay, 0m,
                          Var(card, "VkPer"), credit: false);

    /// <summary>Northwind Avatar's second hit: "Then deal 10 [14], plus 2 for
    /// each Oath, as your current element." It credits like any card.</summary>
    public static Task AvatarHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        CurrentElementHit(choiceContext, card, cardPlay, Var(card, "VkBase"),
                          Var(card, "VkPer"), credit: true);

    /// <summary>The shared shape: one powered hit on the card's target,
    /// carrying his current element (<see cref="HitElement.Carry"/>, the
    /// scope Knights' Muster's hit took). Nothing without a current element,
    /// or at 0 damage.</summary>
    public static int CurrentElementDamage(decimal baseDamage, decimal per,
                                           int oath) =>
        (int)(baseDamage + per * oath);

    private static async Task CurrentElementHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay,
        decimal baseDamage, decimal per, bool credit)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (owner == null || element == Element.None) return;
        if (cardPlay.Target is not { IsAlive: true } target) return;
        var damage = CurrentElementDamage(baseDamage, per,
                                          VarkaOath.CurrentOath(owner));
        if (damage <= 0) return;
        using (HitElement.Carry(card, element))
        using (credit ? null : VarkaOath.NoApplyCredit(owner))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .Targeting(target)
                .WithElementHitFx(element)
                .Execute(choiceContext);
        }
    }

    /// <summary>Storm Surge: "Each enemy it Swirls takes 5 more." Element-less
    /// (so it cannot Swirl again), his Strength counting.</summary>
    public static async Task SwirledTakeMore(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        var amount = Var(card, "VkAmount");
        foreach (var enemy in VarkaOathLedger.For(owner).SwirledThisPlay
                     .Distinct().ToList())
        {
            if (!enemy.IsAlive) continue;
            await ElementalHit.DealUnelemented(choiceContext, enemy, amount,
                                               owner);
        }
    }

    /// <summary>Downburst (2026-10-04): "If it Swirls, gain 2 Oath of the
    /// element Swirled." One gain per element Swirled, on top of the Swirl's
    /// own credit, through <see cref="VarkaOath.Gain"/> so Oath Unto Death,
    /// Dawn Wind's March and Boreas's Fang see it.</summary>
    public static async Task SwirledOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        var gains = SwirledOathGains(
            VarkaOathLedger.For(owner).SwirledElementsThisPlay,
            (int)Var(card, "VkAmount"));
        foreach (var (element, n) in gains)
        {
            await VarkaOath.Gain(choiceContext, owner, element, n,
                                 OathSource.Swirl);
        }
    }

    /// <summary>Downburst's gains: <paramref name="amount"/> of each Oath
    /// element the play Swirled, once per element, in order. Empty when it
    /// Swirled nothing. PURE.</summary>
    public static List<(Element Element, int Amount)> SwirledOathGains(
        IReadOnlyList<Element> swirled, int amount) =>
        amount <= 0
            ? new List<(Element, int)>()
            : swirled.Where(VarkaOath.IsOathElement).Distinct()
                .Select(e => (e, amount)).ToList();

    /// <summary>Wall of Gales: "Swirl every aura." The aura'd bodies are
    /// taken when it is played and each takes its own damage-less Anemo hit,
    /// shielded from an earlier Swirl's spread as Gale Sweep's are.</summary>
    public static Task SwirlFreshAuras(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        VarkaRules.SwirlFreshAuras(choiceContext, card.Owner?.Creature);

    /// <summary>Eula: "Gain 1 Cryo Oath for each enemy with a Cryo aura",
    /// read after her hit. One gain.</summary>
    public static async Task OathPerCryoEnemy(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var combat = owner?.CombatState;
        if (owner == null || combat == null) return;
        var n = combat.HittableEnemies.Count(
            e => AuraCmd.Find(e) is { Element: Element.Cryo });
        await VarkaOath.Gain(choiceContext, owner, Element.Cryo, n);
    }

    /// <summary>
    /// Change of Guard: "Choose an element you have Oath in. It becomes your
    /// current element. Draw 1 card." A grid of the elements he holds Oath
    /// in; not a Knight; Boreas Unbound
    /// sees the change. The draw is the sheet's own op, after this one, so it
    /// draws with no Oath too. (The open-Oath round, 2026-10-01: the Block
    /// went, the card went to 0 with no Exhaust.)
    /// </summary>
    public static async Task ChangeOfGuard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        var ledger = VarkaOathLedger.For(owner);
        var held = VarkaOathLedger.Elements.Where(e => ledger.Oath(e) > 0).ToList();
        if (held.Count == 0) return;
        // Unwavering Banner (the combo pass, 2026-10-04): only Knights change
        // it. No grid: the Banner holds, and pays 1 Oath of the current
        // element when another element could have been chosen.
        if (owner.HasPower<UnwaveringBannerPower>())
        {
            var other = held.FirstOrDefault(e => e != ledger.Current);
            if (other != Element.None)
            {
                await VarkaOath.BannerHolds(choiceContext, owner, other);
            }
            return;
        }
        var element = held.Count == 1
            ? held[0]
            : await VarkaRules.ChooseElement(choiceContext, card.Owner, held);
        if (element == Element.None) return;
        await VarkaOath.SetCurrent(choiceContext, owner, element, knight: false);
    }

    /// <summary>Rally to the Banner: "Move all your Oath to your current
    /// element." Not a gain.</summary>
    public static async Task Rally(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        VarkaOathLedger.For(owner).Rally();
        await OathBadge.Sync(choiceContext, owner);
    }

    // ---- the expansion (2026-10-01) ------------------------------------------

    /// <summary>One powered hit of <paramref name="card"/> on
    /// <paramref name="target"/> carrying <paramref name="element"/>, through
    /// the card's own DamageCmd (Strength and the card's riders count), the
    /// shape <c>CurrentElementHit</c> takes. It credits like any hit of his.
    /// </summary>
    private static async Task ElementHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay,
        Creature? target, decimal damage, Element element)
    {
        if (target is not { IsAlive: true } || damage <= 0) return;
        using (HitElement.Carry(card, element))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .Targeting(target)
                .WithElementHitFx(element)
                .Execute(choiceContext);
        }
    }

    /// <summary>Pathfinder's Mark: "Apply your current element to an enemy
    /// (a random one of the four if you have none). [ALL enemies]" One
    /// element for every target; the upgraded card reads its own
    /// <c>IsUpgraded</c> (the row's <c>varka_upgraded</c>).</summary>
    public static async Task PathfindersMark(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var player = card.Owner;
        if (owner == null || player == null || !VarkaOath.Live(owner)) return;
        var element = VarkaOath.Current(owner);
        if (element == Element.None)
        {
            element = player.RunState.Rng.CombatTargets.NextItem(
                VarkaOathLedger.Elements.ToList());
        }
        var targets = card.IsUpgraded
            ? owner.CombatState?.HittableEnemies.ToList() ?? new List<Creature>()
            : cardPlay.Target is { } one ? new List<Creature> { one }
            : new List<Creature>();
        foreach (var target in targets)
        {
            if (!target.IsAlive) continue;
            await ElementalHit.ApplyOnly(choiceContext, target, element, owner);
        }
    }

    /// <summary>Cavalry Charge: "Deal 7 [10] damage as your current
    /// element." Without one, his plain Anemo hit.</summary>
    public static Task CurrentElementStrike(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var element = VarkaOath.Current(card.Owner?.Creature);
        return ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                          Var(card, "VkBase"),
                          element == Element.None ? Element.Anemo : element);
    }

    /// <summary>Blazing Charge: "Deal 5 [7] Pyro damage, plus 2 for each
    /// Pyro Oath." Its own element's Oath, read before the hit.</summary>
    public static Task BlazingCharge(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   CurrentElementDamage(Var(card, "VkBase"), Var(card, "VkPer"),
                       VarkaOath.Count(card.Owner?.Creature, Element.Pyro)),
                   Element.Pyro);

    /// <summary>Glacial Edict's stacks: 1, plus 1 for every
    /// <paramref name="per"/> Cryo Oath. PURE.</summary>
    public static int GlacialEdictStacks(int cryoOath, int per) =>
        1 + (per <= 0 ? 0 : cryoOath / per);

    /// <summary>Glacial Edict: "and 1 Weak and 1 Vulnerable, plus 1 of each
    /// for every 3 [2] Cryo Oath", read after the row's own Cryo landed.
    /// </summary>
    public static async Task GlacialEdict(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || cardPlay.Target is not { IsAlive: true } target) return;
        var n = GlacialEdictStacks(VarkaOath.Count(owner, Element.Cryo),
                                   (int)Var(card, "VkAmount"));
        await PowerCmd.Apply<WeakPower>(choiceContext, target, n,
                                        applier: owner, cardSource: card);
        await PowerCmd.Apply<VulnerablePower>(choiceContext, target, n,
                                              applier: owner, cardSource: card);
    }

    /// <summary>Thundering Verdict (element identities sec.3, an X cost):
    /// "Deal 6 [8] Electro damage to ALL enemies X times, plus 1 for each
    /// Electro Oath each time." X is the Energy spent (Whirlwind's
    /// <c>ResolveEnergyXValue</c>); the Electro Oath is read once, before the
    /// hits.</summary>
    public static async Task ThunderingVerdict(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner?.CombatState == null) return;
        var x = card.ResolveEnergyXValue();
        // The face's per-hit number reads the same sum (VkHit).
        var damage = VarkaHitDamageVar.PerHit(card, Element.Electro);
        for (var i = 0; i < x; i++)
        {
            foreach (var enemy in owner.CombatState.HittableEnemies.ToList())
            {
                await ElementHit(choiceContext, card, cardPlay, enemy, damage,
                                 Element.Electro);
            }
        }
    }

    /// <summary>Charged Lunge (element identities sec.3): "Deal 6 [9]
    /// Electro damage." The draw is the row's own op.</summary>
    public static Task ElectroStrike(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   Var(card, "VkBase"), Element.Electro);

    /// <summary>Chain Lightning (element identities sec.3): "Deal 8 [11]
    /// Electro damage to ALL enemies." Its discount is the card's own cost
    /// hook.</summary>
    public static async Task ElectroAll(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner?.CombatState == null) return;
        foreach (var enemy in owner.CombatState.HittableEnemies.ToList())
        {
            await ElementHit(choiceContext, card, cardPlay, enemy,
                             Var(card, "VkBase"), Element.Electro);
        }
    }

    /// <summary>
    /// Violet Storm (element identities sec.3, raised at the ruling): "Discard
    /// your hand. Deal 8 [11] Electro damage to a random enemy for each card
    /// discarded." Storm of Steel's discard, the whole hand in one
    /// <c>CardCmd.Discard</c>; then one hit per card, each at a random
    /// living enemy (<c>Rng.CombatTargets</c>).
    /// </summary>
    public static async Task VioletStorm(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var player = card.Owner;
        var combat = player?.Creature?.CombatState;
        if (player == null || combat == null) return;
        var hand = PileType.Hand.GetPile(player).Cards.ToList();
        var discarded = hand.Count;
        if (discarded > 0) await CardCmd.Discard(choiceContext, hand);
        for (var i = 0; i < discarded; i++)
        {
            var living = combat.HittableEnemies.Where(e => e.IsAlive).ToList();
            if (living.Count == 0) break;
            var target = player.RunState.Rng.CombatTargets.NextItem(living);
            await ElementHit(choiceContext, card, cardPlay, target,
                             Var(card, "VkBase"), Element.Electro);
        }
    }

    /// <summary>Razor: Awakening's hit on one enemy: the base, plus the
    /// bonus when it already wore Electro. PURE.</summary>
    public static int AwakeningDamage(decimal baseDamage, decimal bonus,
                                      bool hadElectro) =>
        (int)(baseDamage + (hadElectro ? bonus : 0m));

    /// <summary>Razor: Awakening (the AoE trim, sec.4): "Deal 4 [6] Electro
    /// damage to an enemy. If it already has Electro, deal 3 more." Whether it
    /// wore Electro is read before the hit.</summary>
    public static async Task Awakening(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (cardPlay.Target is not { IsAlive: true } target) return;
        var had = AuraCmd.Find(target) is { Element: Element.Electro };
        await ElementHit(choiceContext, card, cardPlay, target,
            AwakeningDamage(Var(card, "VkBase"), Var(card, "VkAmount"), had),
            Element.Electro);
    }

    // ---- THE REBALANCE (2026-10-03, review/active/varka-rebalance-2026-10-03.md
    // secs.3-4). Sim twins: varka_oath._rebalance_kind.

    /// <summary>Kindled Edge: "Deal 7 [10] Pyro damage. If it sets off an
    /// Elemental Reaction, deal 7 [10] more." The more is a second hit on the
    /// same enemy with no element (a second application is not printed).
    /// The reaction is read off the target's aura: it wore one Pyro reacts
    /// with, and the hit consumed it.</summary>
    public static async Task KindledEdge(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || cardPlay.Target is not { IsAlive: true } target) return;
        var amount = Var(card, "VkBase");
        var before = ReactionEffects.TotalResolved;
        await ElementHit(choiceContext, card, cardPlay, target, amount,
                         Element.Pyro);
        if (ReactionEffects.TotalResolved > before && target.IsAlive)
        {
            await DamageCmd.Attack(amount)
                .FromCard(card, cardPlay)
                .Targeting(target)
                .Execute(choiceContext);
        }
    }

    /// <summary>Storm Battery: "Deal 2 [3] Electro damage to ALL enemies for
    /// each other card in your hand." The card has left the hand when it
    /// resolves, so the hand is the others.</summary>
    public static async Task StormBattery(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var player = card.Owner;
        var combat = player?.Creature?.CombatState;
        if (player == null || combat == null) return;
        var others = PileType.Hand.GetPile(player).Cards.Count(c => c != card);
        var damage = Var(card, "VkPer") * others;
        if (damage <= 0) return;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            await ElementHit(choiceContext, card, cardPlay, enemy, damage,
                             Element.Electro);
        }
    }

    /// <summary>Frost Ward (the forced-Amber round, 2026-10-10): "Gain 3 [4]
    /// Block. For each enemy with an aura, apply 1 Weak and gain 3 [4] additional
    /// Block." The enemies wearing an aura when it is played; one Block gain
    /// of VkAmount x (1 + those enemies), so Dexterity counts once.
    /// Sim twin: <c>varka_oath</c>'s <c>frost_ward</c> kind.</summary>
    /// <summary>Frost Ward's Block: the floor plus as much again per enemy
    /// with an aura. PURE.</summary>
    public static int FrostWardBlock(int amount, int marked) =>
        amount * (1 + System.Math.Max(0, marked));

    public static async Task FrostWard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner?.CombatState == null) return;
        var marked = owner.CombatState.HittableEnemies
            .Where(e => e.IsAlive && AuraCmd.Find(e) != null).ToList();
        foreach (var enemy in marked)
        {
            await PowerCmd.Apply<WeakPower>(choiceContext, enemy, 1,
                                            applier: owner, cardSource: card);
        }
        await GainCardBlock(owner, FrostWardBlock((int)Var(card, "VkAmount"),
                                                  marked.Count), cardPlay);
    }

    /// <summary>Barbara: Gleeful Songs: "Apply Hydro to ALL enemies. Gain
    /// 4 [6] Block, plus 3 [4] for each enemy it reacts on."</summary>
    public static async Task GleefulSongs(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner?.CombatState == null) return;
        var reacted = 0;
        foreach (var enemy in owner.CombatState.HittableEnemies.ToList())
        {
            var before = ReactionEffects.TotalResolved;
            await ElementalHit.ApplyOnly(choiceContext, enemy, Element.Hydro,
                                         owner);
            if (ReactionEffects.TotalResolved > before) reacted++;
        }
        await GainCardBlock(owner,
            Var(card, "VkBase") + Var(card, "VkPer") * reacted, cardPlay);
    }

    /// <summary>Rippling Guard: "Gain 3 Block, plus 2 [3] for each other card
    /// you played this turn." The ledger counts this play too.</summary>
    public static async Task RipplingGuard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        var others = System.Math.Max(
            0, VarkaOathLedger.For(owner).PlaysThisTurn - 1);
        await GainCardBlock(owner,
            Var(card, "VkBase") + Var(card, "VkPer") * others, cardPlay);
    }

    /// <summary>Whisper of Water's "and at the start of your next 2 turns":
    /// the ledger pays it at <see cref="VarkaOath.TurnStart"/>.</summary>
    public static Task EchoBlock(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner != null && VarkaOath.Live(owner))
        {
            VarkaOathLedger.For(owner).AddEchoBlock(
                (int)Var(card, "VkAmount"), VarkaLaw.EchoBlockTurns);
        }
        return Task.CompletedTask;
    }

    /// <summary>A card's printed Block, powered (Dexterity, Frail).</summary>
    private static async Task GainCardBlock(
        Creature owner, decimal amount, CardPlay cardPlay)
    {
        if (amount <= 0) return;
        await CreatureCmd.GainBlock(owner, amount, ValueProp.Move, cardPlay);
    }

    /// <summary>Lisa: Pulsating Witch: "Draw 1 card for each enemy."
    /// </summary>
    public static async Task DrawPerEnemy(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var player = card.Owner;
        var n = player?.Creature?.CombatState?.HittableEnemies.Count(e => e.IsAlive) ?? 0;
        if (player == null || n <= 0) return;
        await CardPileCmd.Draw(choiceContext, n, player);
    }

    /// <summary>Barbara: Wellspring Hymn: "Remove your Weak, Frail and
    /// Vulnerable."</summary>
    public static async Task Cleanse(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null) return;
        foreach (var power in owner.Powers
                     .Where(p => p is WeakPower or FrailPower or VulnerablePower)
                     .ToList())
        {
            await PowerCmd.Remove(power);
        }
    }

    /// <summary>Crosscurrent: "Swirl an enemy's aura. This Swirl pays
    /// twice." A damage-less Anemo hit, Jean's, inside the ledger's
    /// pays-twice window.</summary>
    public static async Task Crosscurrent(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || cardPlay.Target is not { } target) return;
        var ledger = VarkaOath.Live(owner) ? VarkaOathLedger.For(owner) : null;
        if (ledger != null) ledger.PaysTwice++;
        try
        {
            await ElementalHit.ApplyOnly(choiceContext, target, Element.Anemo,
                                         owner);
        }
        finally
        {
            if (ledger != null) ledger.PaysTwice--;
        }
    }

    /// <summary>Grand Master's Verdict: "Double your current element's
    /// Oath." One gain of what he holds.</summary>
    public static async Task DoubleCurrentOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (owner == null || element == Element.None) return;
        var held = VarkaOath.Count(owner, element);
        if (held <= 0) return;
        await VarkaOath.Gain(choiceContext, owner, element, held);
    }

    /// <summary>Tempest of the Four Winds' order: Pyro, Hydro, Cryo,
    /// Electro (the last applied wins the open Oath).</summary>
    public static readonly IReadOnlyList<Element> TempestOrder = new[]
    {
        Element.Pyro, Element.Hydro, Element.Cryo, Element.Electro,
    };

    /// <summary>Tempest of the Four Winds: "Deal 4 [5] damage four times, as
    /// Pyro, Hydro, Cryo and Electro." Each hit credits its own element.
    /// </summary>
    public static async Task Tempest(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        foreach (var element in TempestOrder)
        {
            await ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                             Var(card, "VkBase"), element);
        }
    }

    // ---- THE COMBO PASS (2026-10-04, review/active/varka-combo-pass-2026-10-04.md
    // secs.3-4). Sim twins: varka_oath._combo_kind.

    /// <summary>Stoke the Flames: "Pyro becomes your current element. Gain
    /// 2 [3] Pyro Oath." After the row's own Exhaust, the switch, then one
    /// gain (the Varka payoff round, 2026-10-10: switch first, so Dawn Wind's
    /// March, Oath Unto Death and every current-element gain listener see the
    /// gain as the current element's). The switch is a non-Knight card's, so
    /// Unwavering Banner holds it (<see cref="VarkaOath.CardMakesCurrent"/>).
    /// Ember Cleave's gain is this kind too, so it switches first as well.
    /// </summary>
    public static async Task GainPyroOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        await VarkaOath.CardMakesCurrent(choiceContext, owner, Element.Pyro);
        await VarkaOath.Gain(choiceContext, owner, Element.Pyro,
                             (int)Var(card, "VkAmount"));
    }

    /// <summary>Ember Cleave: "Deal 9 [12] Pyro damage." The Exhaust is the
    /// row's own op, after this one.</summary>
    public static Task PyroStrike(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   Var(card, "VkBase"), Element.Pyro);

    /// <summary>Weak plus Vulnerable on <paramref name="enemy"/>, in stacks
    /// (Shatter's count). 0 for none. PURE apart from the reads.</summary>
    public static int WeakAndVulnerable(Creature? enemy) =>
        enemy == null ? 0
            : (int)(enemy.Powers.OfType<WeakPower>().FirstOrDefault()?.Amount ?? 0)
              + (int)(enemy.Powers.OfType<VulnerablePower>().FirstOrDefault()?.Amount ?? 0);

    /// <summary>Shatter's hit before the damage hooks: the base, plus
    /// <paramref name="per"/> for each stack. PURE.</summary>
    public static int ShatterDamage(decimal baseDamage, decimal per,
                                    int stacks) =>
        (int)(baseDamage + per * System.Math.Max(0, stacks));

    /// <summary>Shatter: "Deal 5 [7] Cryo damage, plus 2 [3] for each Weak and
    /// Vulnerable on the enemy." The stacks are read before the hit (its
    /// Cryo may react and its hooks may move them).</summary>
    public static async Task Shatter(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (cardPlay.Target is not { IsAlive: true } target) return;
        var damage = ShatterDamage(Var(card, "VkBase"), Var(card, "VkPer"),
                                   WeakAndVulnerable(target));
        await ElementHit(choiceContext, card, cardPlay, target, damage,
                         Element.Cryo);
    }

    /// <summary>Deep Freeze: "Double its Weak and Vulnerable." After the
    /// row's own Cryo; each doubling is an application of what it holds
    /// (Suffocating Deep's shape), so Absolute Zero sees it.</summary>
    public static async Task DeepFreeze(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || cardPlay.Target is not { IsAlive: true } target)
        {
            return;
        }
        var weak = (int)(target.Powers.OfType<WeakPower>()
                             .FirstOrDefault()?.Amount ?? 0);
        if (weak > 0)
        {
            await PowerCmd.Apply<WeakPower>(choiceContext, target, weak,
                                            applier: owner, cardSource: card);
        }
        if (!target.IsAlive) return;
        var vulnerable = (int)(target.Powers.OfType<VulnerablePower>()
                                   .FirstOrDefault()?.Amount ?? 0);
        if (vulnerable > 0)
        {
            await PowerCmd.Apply<VulnerablePower>(
                choiceContext, target, vulnerable, applier: owner,
                cardSource: card);
        }
    }
}

/// <summary>
/// SHATTER'S PRINTED NUMBER (the combo pass, 2026-10-04: "show the computed
/// damage in combat the way other Varka formula cards do"). Display only:
/// <c>VkBase</c> plus <c>VkPer</c> for each Weak and Vulnerable on the body
/// the face previews against (the aimed enemy, else the front one, as
/// <see cref="FrontFoldedDamageVar"/> picks), folded through the game's
/// damage hooks with Cryo carried. The play reads the card's own vars
/// (<see cref="VarkaCards.Shatter"/>). Emitted by codegen for the kinds in
/// <c>VARKA_TARGET_PREVIEW_KINDS</c>.
/// </summary>
public sealed class VarkaShatterDamageVar : DamageVar
{
    /// <summary>The face's token, Thundering Verdict's.</summary>
    public const string Token = "VkHit";

    public VarkaShatterDamageVar()
        : base(Token, 0m, ValueProp.Move)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!runGlobalHooks || !card.IsMutable)
        {
            BaseValue = VarkaCards.ShatterDamage(
                card.DynamicVars["VkBase"].BaseValue,
                card.DynamicVars["VkPer"].BaseValue, 0);
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        BaseValue = VarkaCards.ShatterDamage(
            card.DynamicVars["VkBase"].BaseValue,
            card.DynamicVars["VkPer"].BaseValue,
            VarkaCards.WeakAndVulnerable(body));
        using (HitElement.Carry(card, Element.Cryo))
        {
            base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        }
    }
}

/// <summary>
/// THE PER-HIT NUMBER OF A VARKA KIND THAT READS AN ELEMENT'S OATH (the
/// element identities round, 2026-10-01: "Thundering Verdict prints no per-hit
/// number"; X=4 landed 27 a hit where the seat had seen 10 earlier). Display
/// only, the base game's Whirlwind shape: the face prints what one hit deals,
/// <c>VkBase</c> plus <c>VkPer</c> for each Oath of
/// <see cref="OathElement"/>, folded through the game's damage hooks
/// (Strength, Weak) with the hit's element carried, as
/// <see cref="VarkaCards.ThunderingVerdict"/> deals it. Nothing reads it in
/// play; the play reads the card's own <c>VkBase</c> and <c>VkPer</c>.
/// Emitted by codegen for the kinds in <c>VARKA_HIT_PREVIEW_KINDS</c>.
/// </summary>
public sealed class VarkaHitDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "VkHit";

    /// <summary>The element whose Oath the hit adds, and that it carries.
    /// </summary>
    public Element OathElement { get; }

    public VarkaHitDamageVar(Element oathElement)
        : base(Token, 0m, ValueProp.Move)
    {
        OathElement = oathElement;
    }

    /// <summary>One hit's printed number before the hooks: VkBase plus VkPer
    /// for each Oath of the element (none off a card nobody holds). PURE.
    /// </summary>
    public static int PerHit(CardModel card, Element element)
    {
        var owner = card.IsMutable ? card.Owner?.Creature : null;
        return VarkaCards.CurrentElementDamage(
            card.DynamicVars["VkBase"].BaseValue,
            card.DynamicVars["VkPer"].BaseValue,
            VarkaOath.Count(owner, element));
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        BaseValue = PerHit(card, OathElement);
        if (!runGlobalHooks || !card.IsMutable)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        using (HitElement.Carry(card, OathElement))
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
        }
    }
}
