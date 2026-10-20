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

    /// <summary>Has this creature's Oath started this combat
    /// (<see cref="VarkaOath.Start"/>)? A pure read: it creates nothing.
    /// </summary>
    public static bool HasStarted(Creature creature)
    {
        lock (Gate)
        {
            if (!ReferenceEquals(_combat, (object?)creature.CombatState)) return false;
            return _byVarka.TryGetValue(creature, out var ledger) && ledger.Started;
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

    /// <summary>Is the Oath kept for this creature this combat? Varka's is
    /// always; anyone else's from the first Varka card they play (the
    /// off-character fix, 2026-10-18).</summary>
    public bool Started { get; set; }

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

    /// <summary>A new round clears the turn's Knight and Swirl counts.
    /// </summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        _round = round;
        KnightsThisTurn = 0;
        SwirlsThisTurn = 0;
    }

    // ---- reads ------------------------------------------------------------

    /// <summary>His Oath of <paramref name="element"/> (0 for any element
    /// that keeps none).</summary>
    public int Oath(Element element) =>
        _oath.TryGetValue(element, out var n) ? n : 0;

    /// <summary>The one count his cards read: the current element's, or all
    /// four together on a turn he drank the Elixir of the Four Winds, or for
    /// the rest of a fight he played All Four Winds in.
    /// </summary>
    public int CurrentOath => ReadsAllFour ? Total : Oath(Current);

    /// <summary>Do his cards read all four Oaths together now: the Elixir's
    /// turn, or All Four Winds' combat?</summary>
    public bool ReadsAllFour => AllFourThisTurn || AllFourThisCombat;

    /// <summary>All Four Winds (his Ancient, the Varka review, ruled
    /// 2026-10-12): "Your cards read your Oath of every element together."
    /// The Elixir's effect for the whole combat; a new combat's ledger starts
    /// without it.</summary>
    public bool AllFourThisCombat { get; private set; }

    /// <summary>All Four Winds is played.</summary>
    public void ReadAllFourThisCombat() => AllFourThisCombat = true;

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
/// THE OATH DIAL'S PREVIEW (2026-10-14). The codegen puts this on every row
/// whose play makes an element Varka's current one (<c>gen_klee_cards
/// .varka_switch_element</c>, the element its "(Makes Pyro current)" line and
/// its switch tip are emitted with), and nothing else implements it. Whether
/// the play WOULD switch now is still <see cref="VarkaOath.WouldSwitchTo"/>'s
/// question. Display only.
/// </summary>
public interface IVarkaSwitchCard
{
    /// <summary>The element this card makes current.</summary>
    Element VarkaSwitchElement { get; }
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
    /// <summary>
    /// Is the Oath kept for THIS creature: it gains Oath from the elements it
    /// applies and the Swirls it makes, a Knight sets its current element,
    /// and the Oath Powers pay? Varka's is from the start of every combat;
    /// anyone else's from the first Varka card they play this combat
    /// (<see cref="Start"/>; the off-character fix, 2026-10-18), the base
    /// game's Orbs shape (the first Channel grants a slot to a character
    /// with none). In co-op each seat's Oath is its own.
    /// </summary>
    public static bool Live(Creature? creature) =>
        VarkaPrototype.IsVarka(creature)
        || (creature?.Player != null && VarkaOathLedger.HasStarted(creature));

    /// <summary>Is this one of Varka's cards: his pool, his Knights, his
    /// Ancients? PURE.</summary>
    public static bool IsVarkaCard(CardModel? card) =>
        card is ICharacterCard { CharacterId: VarkaPrototype.CharacterId }
        || VarkaRules.IsKnight(card);

    /// <summary>Start this player's Oath, once a combat: a Varka card is
    /// being played. False for no player.</summary>
    public static bool Start(Creature? creature)
    {
        if (creature?.Player == null) return false;
        VarkaOathLedger.For(creature).Started = true;
        return true;
    }

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

    /// <summary>Tempest Charge's discount: Swirls he made this turn (the
    /// ledger rolls the count to 0 each round). Sim twin: the ledger's
    /// <c>swirls_this_turn</c>, read by <c>combat.card_cost</c>.</summary>
    public static int SwirlsThisTurn(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).SwirlsThisTurn : 0;

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
        creature?.CombatState == null || creature.Player == null ? 0
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
        // One of his cards starts its player's Oath first, whoever that
        // player is (the off-character fix, 2026-10-18).
        if (!Live(owner) && (!IsVarkaCard(card) || !Start(owner))) return;
        var ledger = VarkaOathLedger.For(owner!);
        ledger.OpenScope(open: !VarkaRules.IsKnight(card), card: card);
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
    /// element's, and let Wolf's Gravestone add Four Winds' Ascension the
    /// first time each combat (sec.4; the plain Fang no longer does since
    /// Starter (a), 2026-10-13). One call is one gain event.
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
        // Starter (a), 2026-10-13: only Wolf's Gravestone still adds it;
        // the Fang's Ascension is in his deck.
        if (!ledger.FangFired && varka.Player is { } player
            && Relics.BoreasFang.HeldBy(player) is { AddsAscension: true } fang)
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
        var paid = 0;
        foreach (var banner in varka.Powers.OfType<UnwaveringBannerPower>().ToList())
        {
            banner.Pulse();
            paid += banner.OathPaid;
        }
        // "gain 1 [2] Oath" -- 1 per plain copy, 2 per upgraded copy (the
        // power upgrade pass, 2026-10-19), once per play.
        await Gain(choiceContext, varka, current, System.Math.Max(1, paid));
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
        // Converging Winds (round 3, pick 1): first, as the sim pays it.
        await ConvergingWindsPower.OnSwirl(choiceContext, target, dealer);
        var ledger = VarkaOathLedger.For(dealer);
        ledger.NoteSwirl(target, swirled);
        if (ledger.TryCredit(swirl: true, swirled))
        {
            await Gain(choiceContext, dealer, swirled, 1, OathSource.Swirl);
        }
        // Starter (a), 2026-10-13 ([USER]: "it's basically a second starter
        // relic untied to his actual relic"): the current element's payout is
        // Boreas's Fang's ("Your Swirls also pay your current element"). With
        // no Fang held, nothing current is paid.
        var current = Relics.BoreasFang.PaysSwirls(dealer.Player)
            ? ledger.Current : Element.None;
        // Stormterror's Scale: "Your Swirls pay twice." The expansion:
        // Crosscurrent's Swirl pays twice too (the two multiply); Twin Gales
        // pays the element Swirled as well. Varka round 5 (2026-10-13,
        // varka-next): when that is the current element it pays again, so a
        // matched element pays twice (the Fang's payout, then Twin Gales').
        var twin = dealer.HasPower<TwinGalesPower>();
        var times = Relics.StormterrorsScale.TakePayouts(dealer)
                    * (ledger.PaysTwice > 0 ? 2 : 1);
        for (var pay = 0; pay < times; pay++)
        {
            await Pay(choiceContext, target, dealer, current, fang: true);
            if (twin && IsOathElement(swirled))
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
        // The power upgrade pass (2026-10-19): the upgraded copies also draw
        // on the 4th (`EyeOfStormterrorPower.DrawsFor`).
        foreach (var eye in dealer.Powers.OfType<EyeOfStormterrorPower>().ToList())
        {
            await eye.Draw(choiceContext, ledger.SwirlsThisTurn);
        }
        // West Wind's Blessing (Varka's co-op five, 2026-10-13): the first
        // Swirl each turn gives each other player energy.
        await WestWindsBlessingPower.OnSwirl(choiceContext, dealer);
        if (current != Element.None)
        {
            Log.Info($"[{KleeMod.ModId}] VARKA Swirl on {target.Name}: "
                   + $"{swirled} Oath, paid {current}.");
        }
    }

    /// <summary>One element's Swirl payout in words, with
    /// <see cref="VarkaLaw"/>'s numbers: "Pyro (3 damage)". Empty for an
    /// element that pays nothing. PURE.</summary>
    public static string PayoutWords(Element element)
    {
        var effect = PayoutEffect(element);
        return effect.Length > 0 ? $"{element} ({effect})" : string.Empty;
    }

    /// <summary>What one Swirl payout of <paramref name="element"/> does, in
    /// <see cref="VarkaLaw"/>'s numbers: "3 Block". Empty for an element that
    /// pays nothing. <see cref="PayoutWords"/>' and the Swirl line's one
    /// source. PURE.</summary>
    public static string PayoutEffect(Element element) => element switch
    {
        Element.Pyro => $"{VarkaLaw.SwirlPyroDamage} damage",
        Element.Hydro => $"{VarkaLaw.SwirlHydroBlock} Block",
        Element.Cryo => $"{VarkaLaw.SwirlCryoVulnerable} Vulnerable",
        Element.Electro => $"{VarkaLaw.SwirlElectroDamageAll} damage to ALL",
        _ => string.Empty,
    };

    /// <summary>
    /// SWIRL LEGIBILITY (2026-10-19): what his Swirl pays, in words, "Swirl
    /// pays Hydro: 3 Block", with ", twice" or ", 3 times" when it pays over
    /// (<paramref name="times"/>: Stormterror's Scale, Crosscurrent's own
    /// Swirl). Empty with no current element or nothing paid. The card
    /// face's line and the Swirl preview's clause. PURE.
    /// </summary>
    public static string SwirlPays(Element current, int times)
    {
        var effect = PayoutEffect(current);
        if (effect.Length == 0 || times <= 0) return string.Empty;
        var over = times switch
        {
            1 => "",
            2 => ", twice",
            _ => $", {times} times",
        };
        return $"Swirl pays {current}: {effect}{over}";
    }

    /// <summary>
    /// What a Swirl <paramref name="card"/> makes for <paramref name="varka"/>
    /// pays right now, as <see cref="SwirlPays"/> words, or empty: no live
    /// Oath, no Boreas's Fang (the payout is the Fang's), or no current
    /// element. Times are Stormterror's Scale's copies, doubled on
    /// Crosscurrent ("This Swirl pays twice"). Display only: it reads the
    /// ledger and the relics and runs nothing. Twin Gales' extra payout
    /// depends on the aura Swirled and is that card's own words.
    /// </summary>
    public static string SwirlPaysNow(Creature? varka, CardModel? card)
    {
        if (varka == null || !Live(varka)) return string.Empty;
        if (!Relics.BoreasFang.PaysSwirls(varka.Player)) return string.Empty;
        var times = Relics.StormterrorsScale.PayoutsFor(varka)
                    * (card is ProtoVkCrosscurrent ? 2 : 1);
        return SwirlPays(VarkaOathLedger.For(varka).Current, times);
    }

    /// <summary>What one Swirl paid under Twin Gales, as the seat page prints
    /// it: the current element's payout, and the Swirled element's when it is
    /// another Oath element, joined by "and"; " twice" when the two are the
    /// same element (Varka round 5, 2026-10-13: a matched element pays
    /// twice); with " x2" when the Swirl paid <paramref name="times"/> over
    /// (Stormterror's Scale, Crosscurrent). Empty when nothing paid.
    /// PURE.</summary>
    public static string TwinGalesPaid(Element current, Element swirled,
                                       int times)
    {
        if (times <= 0) return string.Empty;
        var parts = new List<string>();
        var first = PayoutWords(current);
        if (IsOathElement(swirled) && swirled == current && first.Length > 0)
        {
            parts.Add(first + " twice");
        }
        else
        {
            if (first.Length > 0) parts.Add(first);
            if (IsOathElement(swirled)) parts.Add(PayoutWords(swirled));
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
    /// <paramref name="fang"/> (2026-10-19, Varka Fang pick 2a): this is
    /// Boreas's Fang's current-element payout, not Twin Gales' Swirled one,
    /// so the run telemetry tags it (`fang_*` fields,
    /// <see cref="Diagnostics.PlayTelemetry"/>). Measurement only: the tag
    /// changes no number and no argument.
    /// </summary>
    private static async Task Pay(
        PlayerChoiceContext choiceContext, Creature target, Creature dealer,
        Element element, bool fang = false)
    {
        using var tag = fang && element != Element.None
            ? Diagnostics.DamageCredit.OpenFang(element.ToString())
            : default;
        if (fang && element != Element.None)
        {
            Diagnostics.PlayTelemetry.FangPaid(dealer, element.ToString());
        }
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
            {
                var blockBefore = fang ? (int)dealer.Block : 0;
                await CreatureCmd.GainBlock(dealer, VarkaLaw.SwirlHydroBlock,
                    ValueProp.Unpowered, null, fast: true);
                if (fang)
                {
                    Diagnostics.PlayTelemetry.FangBlockGained(
                        dealer, (int)dealer.Block - blockBefore);
                }
                break;
            }
            case Element.Cryo:
                if (target.IsAlive)
                {
                    var vulnBefore = fang
                        ? Diagnostics.ReactionTally.Stacks<VulnerablePower>(target)
                        : 0;
                    await PowerCmd.Apply<VulnerablePower>(
                        choiceContext, target, VarkaLaw.SwirlCryoVulnerable,
                        applier: dealer, cardSource: null);
                    if (fang)
                    {
                        Diagnostics.PlayTelemetry.FangVulnerableApplied(
                            dealer, target, vulnBefore,
                            Diagnostics.ReactionTally.Stacks<VulnerablePower>(target));
                    }
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
        // A Varka card would start its player's Oath as it is played.
        if (owner?.CombatState == null
            || (!Live(owner) && (owner.Player == null || !IsVarkaCard(card))))
        {
            return false;
        }
        if (!IsOathElement(element)) return false;
        if (Current(owner) == element) return false;
        return VarkaRules.IsKnight(card)
            || !owner.HasPower<UnwaveringBannerPower>();
    }

    /// <summary>
    /// THE SWITCH PREVIEW (the Varka review, 2026-10-12, sec.5): "Any card of
    /// his that would change the current element will show '(Makes Pyro
    /// current)' in combat, the same in-combat preview Kokomi's Plans use."
    /// The generated card ends its face in <c>{InCombat:{VarkaSwitch}|}</c>
    /// and fills the token from here: the line on its own row while playing
    /// the card would change his current element to
    /// <paramref name="element"/> (<see cref="WouldSwitchTo"/>, the hover
    /// tip's question), else empty.
    ///
    /// Varka round 5 (2026-10-13, "What to change" 1): the line also says
    /// what the switch costs, "(Makes Cryo current: 2 Oath)": the Oath he
    /// holds in <paramref name="element"/> when it becomes current
    /// (<see cref="OathOnSwitch"/>), so Kaeya, Barbara and Short Circuit no
    /// longer lower Four Winds' Ascension silently. Display only.
    /// </summary>
    public static string SwitchLine(CardModel? card, Element element) =>
        WouldSwitchTo(card, element)
            ? SwitchWords(element, OathOnSwitch(card!.Owner!.Creature, element))
            : "";

    /// <summary>The Oath he holds in <paramref name="element"/> the moment it
    /// becomes current: its own count, plus the old element's when Banner of
    /// the West Wind carries it over (<see cref="SetCurrent"/> pays the
    /// Banner at the switch). The play's own gain is not in it; that prints
    /// on the play's Oath line as it always has.</summary>
    public static int OathOnSwitch(Creature? varka, Element element)
    {
        if (varka == null || !Live(varka)) return 0;
        var current = Current(varka);
        var banner = current != element && IsOathElement(current)
            && Relics.VarkaArmRelics.Held<Relics.BannerOfTheWestWind>(varka) > 0;
        return SwitchOath(Count(varka, element),
                          banner ? Count(varka, current) : 0);
    }

    /// <summary>The count the line prints: the new element's Oath plus what
    /// the Banner carries over. PURE.</summary>
    public static int SwitchOath(int newElementOath, int carried) =>
        Math.Max(0, newElementOath) + Math.Max(0, carried);

    /// <summary>The line itself, a line break then "(Makes Pyro current:
    /// 3 Oath)". PURE.</summary>
    public static string SwitchWords(Element element, int oath) =>
        $"\n(Makes {element} current: {oath} Oath)";

    /// <summary>
    /// THE SWIRL LINE (Varka round 5, 2026-10-13, "What to change" 1: "Swirl
    /// cards whose target has lost its aura read 'No aura'"). A reaction that
    /// used up an aura left a later Swirl card with nothing to Swirl, and the
    /// hand did not say so. A Swirl card of his ends its face in
    /// <c>{InCombat:{VarkaSwirl}|}</c> and the line reads "(No aura to
    /// Swirl)" while the enemy it is aimed at has no aura
    /// (<see cref="DescribedTarget"/>), or, not aimed, while no enemy has
    /// one. Empty otherwise, off a combat and for anyone who is not a player.
    /// Display only.
    /// </summary>
    public static string SwirlLine(CardModel? card)
    {
        if (card is not { IsMutable: true }) return "";
        Creature? owner;
        try
        {
            owner = card.Owner?.Creature;
        }
        catch (Exception)
        {
            return "";
        }
        if (owner?.CombatState == null || owner.Player == null) return "";
        var target = DescribedTarget.For(card);
        var aura = target != null
            ? AuraCmd.Find(target) != null
            : owner.CombatState.HittableEnemies
                .Any(e => AuraCmd.Find(e) != null);
        return SwirlWords(aura, SwirlPaysNow(owner, card));
    }

    /// <summary>The words: "(no aura: no Swirl)" when there is no aura, else
    /// empty. PURE.</summary>
    public static string SwirlWords(bool aura) => aura ? "" : NoAuraToSwirl;

    /// <summary>
    /// SWIRL LEGIBILITY (2026-10-19): with an aura to Swirl the line names
    /// what the Swirl pays, "(Swirl pays Hydro: 3 Block)"
    /// (<see cref="SwirlPaysNow"/>); with none it reads "(no aura: no
    /// Swirl)" as before. Empty with an aura and nothing paid. PURE.
    /// </summary>
    public static string SwirlWords(bool aura, string pays) =>
        !aura ? NoAuraToSwirl : pays.Length > 0 ? $"\n({pays})" : "";

    /// <summary><see cref="SwirlWords"/>' line.</summary>
    public const string NoAuraToSwirl = "\n(no aura: no Swirl)";

    /// <summary>
    /// WILDFIRE OATH'S PREVIEW (BACKLOG: "Wildfire Oath's damage has no
    /// preview on the card that applies Pyro; a seat mis-added a lethal by
    /// 1"). A card of his that applies Pyro ends its face in
    /// <c>{InCombat:{VarkaWildfire}|}</c>, the switch line's seam, and the
    /// line prints what each Pyro application of the play deals while
    /// <see cref="WildfireOathPower"/> is up: his Pyro Oath after this play's
    /// own credit of 1 (<see cref="NoteApplication"/> pays Wildfire after the
    /// credit), plus Oath Unto Death's extra when Pyro is or becomes his
    /// current element, times the stacks. Empty otherwise.
    /// </summary>
    public static string WildfireLine(CardModel? card)
    {
        if (card is not { IsMutable: true }) return "";
        Creature? owner;
        try
        {
            owner = card.Owner?.Creature;
        }
        catch (System.Exception)
        {
            return "";
        }
        if (owner?.CombatState == null || !Live(owner)) return "";
        var fires = owner.Powers.OfType<WildfireOathPower>().ToList();
        var stacks = fires.Sum(p => (int)p.Amount);
        var upgraded = fires.Sum(p => p.UpgradedCopies);
        if (stacks <= 0) return "";
        var gain = 1;
        if (Current(owner) == Element.Pyro || WouldSwitchTo(card, Element.Pyro))
        {
            gain += owner.Powers.OfType<OathUntoDeathPower>()
                .Sum(p => (int)p.Amount);
        }
        return WildfireWords(WildfireOathPower.DamageFor(
            Count(owner, Element.Pyro) + gain, stacks, upgraded));
    }

    /// <summary>The line itself, "(Wildfire Oath deals 5)", or empty for 0.
    /// PURE.</summary>
    public static string WildfireWords(int damage) =>
        damage > 0 ? $"\n(Wildfire Oath deals {damage})" : "";

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
        // Power cost sweep, 2026-09-30: the base card, current element only.
        foreach (var sworn in varka.Powers.OfType<SwornBrotherhoodCurrentPower>().ToList())
        {
            var element = Current(varka);
            if (element == Element.None) continue;
            await Gain(choiceContext, varka, element, sworn.Amount);
        }
        // The Order Answers (the expansion), last: one choice of 3 random
        // pool Knights per stack, the pick added upgraded at its own cost
        // (Varka co-op fixes, 2026-10-11).
        foreach (var order in varka.Powers.OfType<TheOrderAnswersPower>().ToList())
        {
            for (var i = 0; i < order.Amount; i++)
            {
                await VarkaRules.ChooseUpgradedKnight(choiceContext, player);
            }
        }
        // The Oath dial: a new turn can end the Elixir's read-all-four.
        // Display only.
        global::KleeMod.Vfx.VarkaOathDial.Refresh(varka);
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
        // Weathervane, upgraded (the power upgrade pass, 2026-10-19): "Gain 1
        // Oath of it", per upgraded copy, only when an element was chosen.
        // Sim twin: `varka_oath._weathervane`.
        var oath = varka.Powers.OfType<WeathervanePower>().Sum(w => w.OathGained);
        if (oath > 0) await Gain(choiceContext, varka, element, oath);
    }
}

/// <summary>
/// VARKA'S CARD VERBS (the sheet's `varka` op): one method per `kind`, each
/// called as <c>await VarkaCards.Kind(choiceContext, this, cardPlay)</c> by
/// the generated card, reading its own numbers off the card's `Vk*` vars.
/// Sim twins: the `varka` op kinds in <c>tier0/engine/varka_oath.py</c>.
/// </summary>
public static partial class VarkaCards
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

    /// <summary>Vow of the Blade: "Gain 2 Oath of your current element"
    /// (Varka co-op fixes, 2026-10-11). The number is the card's optional
    /// <c>VkAmount</c>; a row that prints none gains 1.</summary>
    public static async Task GainCurrentOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (owner == null || element == Element.None) return;
        await VarkaOath.Gain(choiceContext, owner, element,
                             CurrentOathAmount(card));
    }

    /// <summary>How much Oath <see cref="GainCurrentOath"/> pays: the card's
    /// <c>VkAmount</c>, or 1 when it prints none. PURE.</summary>
    public static int CurrentOathAmount(CardModel card) =>
        card.DynamicVars.TryGetValue("VkAmount", out var amount)
            ? (int)amount.BaseValue : 1;

    /// <summary>
    /// Four Winds' Ascension's second hit: "Then deal 3 damage per Oath
    /// of your current element, as that element." (The upgrade cuts the cost,
    /// not this number.) The Oath is read after
    /// the Anemo hit, and this hit credits no Oath (sec.4).
    /// </summary>
    public static Task AscensionHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        CurrentElementHit(choiceContext, card, cardPlay, 0m,
                          Var(card, "VkPer"), credit: false);

    /// <summary>
    /// Dandelion Gale's second hit (the Archaic Tooth redesign, 2026-10-13):
    /// the Ascension's, "to each" enemy. One hit on ALL enemies carrying his
    /// current element, read after the Anemo hit, crediting no Oath. Nothing
    /// without a current element, or at 0 damage.
    /// </summary>
    public static async Task GaleHit(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        if (owner == null || element == Element.None) return;
        if (card.CombatState is not { } combat) return;
        var damage = CurrentElementDamage(0m, Var(card, "VkPer"),
                                          VarkaOath.CurrentOath(owner));
        if (damage <= 0) return;
        using (HitElement.Carry(card, element))
        using (VarkaOath.NoApplyCredit(owner))
        {
            await DamageCmd.Attack(damage)
                .FromCard(card, cardPlay)
                .TargetingAllOpponents(combat)
                .WithElementHitFx(element)
                .SpawningHitVfxOnEachCreature()
                .Execute(choiceContext);
        }
    }

    /// <summary>Northwind Avatar's second hit: "Then deal 8 [12], plus 2 per
    /// Oath, as your current element." It credits like any card.</summary>
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

    /// <summary>Downburst (Varka pool audit, 2026-10-13): "If it Swirls,
    /// gain 2 Oath of each element." One gain per Oath element, on top of the
    /// Swirl's own credit, through <see cref="VarkaOath.Gain"/> so Oath Unto
    /// Death, Dawn Wind's March and Boreas's Fang see it.</summary>
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

    /// <summary>Downburst's gains: <paramref name="amount"/> of each of the
    /// four Oath elements (Pyro, Hydro, Cryo, Electro, the printed order) when
    /// the play Swirled any Oath element. Empty when it Swirled nothing.
    /// PURE.</summary>
    public static List<(Element Element, int Amount)> SwirledOathGains(
        IReadOnlyList<Element> swirled, int amount) =>
        amount <= 0 || !swirled.Any(VarkaOath.IsOathElement)
            ? new List<(Element, int)>()
            : new[] { Element.Pyro, Element.Hydro, Element.Cryo,
                      Element.Electro }
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

    /// <summary>Blazing Charge: "Deal 8 [11] Pyro damage, plus 1 for each
    /// Pyro Oath." (Varka pool audit, 2026-10-13: was plus 2.) Its own
    /// element's Oath, read before the hit.</summary>
    public static Task BlazingCharge(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   CurrentElementDamage(Var(card, "VkBase"), Var(card, "VkPer"),
                       VarkaOath.Count(card.Owner?.Creature, Element.Pyro)),
                   Element.Pyro);

    /// <summary>Tidal Bulwark's hit before the damage hooks: his Block, plus
    /// <paramref name="per"/> for each Hydro Oath. PURE.</summary>
    public static int TidalBulwarkDamage(int block, decimal per,
                                         int hydroOath) =>
        System.Math.Max(0, block) + (int)(per * System.Math.Max(0, hydroOath));

    /// <summary>Tidal Bulwark (Varka text pass, 2026-10-13, [USER]: "Instead
    /// of saying "Apply hydro", it should say "Deal hydro damage"", ruled
    /// (a)): "Deal Hydro damage equal to your Block, plus 2 [3] for each Hydro
    /// Oath." No Block of its own; one Hydro hit, so it reacts with an aura
    /// already there and credits the Hydro Oath like any Hydro hit. The Block
    /// and the Oath are read before the hit (its own credit comes after).
    /// Sim twin: <c>varka_oath</c>'s <c>tidal_bulwark</c> kind.
    ///
    /// AT 0 IT STILL SWINGS (in-game check 2026-10-16,
    /// <c>varka/02-attack-hydro-*</c>: at 0 Block and no Hydro Oath the card
    /// played no motion at all). <see cref="ElementHit"/> skips a hit of 0,
    /// as the sim's <c>_card_hit</c> does, so no attack command ran and
    /// nothing lunged. The rule stays (no hit, no Hydro, no credit); only the
    /// swing is played, through the same trigger and delay an attack command
    /// uses (<see cref="SwingsWithoutAHit"/>).</summary>
    public static Task TidalBulwark(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var damage = TidalBulwarkDamage(owner == null ? 0 : (int)owner.Block,
            Var(card, "VkPer"), VarkaOath.Count(owner, Element.Hydro));
        if (SwingsWithoutAHit(damage, cardPlay.Target?.IsAlive == true))
        {
            return SwingOnly(card);
        }
        return ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   damage, Element.Hydro);
    }

    /// <summary>An Attack whose one hit is 0 still plays its swing when it
    /// was aimed at a living enemy. PURE.</summary>
    public static bool SwingsWithoutAHit(decimal damage, bool targetAlive) =>
        damage <= 0 && targetAlive;

    /// <summary>The attack command's own lunge, with no hit after it: the
    /// "Attack" trigger at the character's AttackAnimDelay.</summary>
    private static Task SwingOnly(CardModel card)
    {
        var owner = card.Owner;
        if (owner?.Creature is not { IsDead: false } creature)
        {
            return Task.CompletedTask;
        }
        return CreatureCmd.TriggerAnim(creature, "Attack",
            owner.Character.AttackAnimDelay);
    }

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

    /// <summary>Chain Lightning (Varka pool audit, 2026-10-13): "Deal 8 [11]
    /// Electro damage to ALL enemies. Discard 2 cards." Costs 0; the discard
    /// is the row's own chosen-discard op after this hit.</summary>
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
    /// Violet Storm (Varka last pass, 2026-10-12): "Deal 6 [8] Electro
    /// damage to a random enemy for each other card in your Hand." No
    /// discard (it threw away a held Ascension); Storm Battery's count, one
    /// hit per other card, each at a random living enemy
    /// (<c>Rng.CombatTargets</c>).
    /// </summary>
    public static async Task VioletStorm(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var player = card.Owner;
        var combat = player?.Creature?.CombatState;
        if (player == null || combat == null) return;
        var others = PileType.Hand.GetPile(player).Cards.Count(c => c != card);
        for (var i = 0; i < others; i++)
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

    /// <summary>Kindled Edge: "Deal 7 [10] Pyro damage. If it triggers an
    /// Elemental Reaction, deal 5 [7] additional damage." (Varka pool audit,
    /// 2026-10-13: the bonus is its own <c>VkAmount</c>, was the base hit's.)
    /// The more is a second hit on the same enemy with no element (a second
    /// application is not printed).
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
            await DamageCmd.Attack(Var(card, "VkAmount"))
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

    /// <summary>Frost Ward's Block (Varka round 3, 2026-10-10): the floor
    /// plus the per-aura step for each enemy with an aura. PURE.</summary>
    public static int FrostWardBlock(int floor, int per, int marked) =>
        floor + per * System.Math.Max(0, marked);

    /// <summary>Frost Ward (Varka round 3, 2026-10-10): "Gain 5 [6] Block.
    /// For each enemy with an aura, apply 1 Weak and gain 3 [4] additional
    /// Block." The enemies wearing an aura when it is played; one Block gain
    /// of VkBase + VkPer x those enemies, so Dexterity counts once.
    /// Sim twin: <c>varka_oath</c>'s <c>frost_ward</c> kind.</summary>

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
        await GainCardBlock(owner, FrostWardBlock((int)Var(card, "VkBase"),
                                                  (int)Var(card, "VkPer"),
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

    /// <summary>Tempest of the Four Winds: "Deal 6 [8] damage four times, as
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
    /// 2 [3] Pyro Oath." The switch, then one
    /// gain (the Varka payoff round, 2026-10-10: switch first, so Dawn Wind's
    /// March, Oath Unto Death and every current-element gain listener see the
    /// gain as the current element's). The switch is a non-Knight card's, so
    /// Unwavering Banner holds it (<see cref="VarkaOath.CardMakesCurrent"/>).
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

    /// <summary>Ember Cleave: "Deal 7 [9] Pyro damage."</summary>
    public static Task PyroStrike(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        ElementHit(choiceContext, card, cardPlay, cardPlay.Target,
                   Var(card, "VkBase"), Element.Pyro);

    /// <summary>Ashen Oath (the Pyro pass, 2026-10-11): "Gain 2 Pyro Oath."
    /// A gain that switches nothing (Stoke's <see cref="GainPyroOath"/>
    /// switches first). Sim twin: the `pyro_oath` kind.</summary>
    public static async Task PyroOath(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        await VarkaOath.Gain(choiceContext, owner, Element.Pyro,
                             (int)Var(card, "VkAmount"));
    }

    /// <summary>Ember Cleave (Pyro paper 2, 2026-10-12): "Gain 2 [3]
    /// Strength this turn." The base game's Setup Strike: a
    /// <see cref="TemporaryStrengthPower"/> named for its card
    /// (<see cref="EmberCleavePower"/>). Sim twin: the `temp_strength` kind,
    /// the shared `temp_strength` power.</summary>
    public static async Task TemporaryStrength(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var amount = (int)Var(card, "VkAmount");
        if (owner == null || amount <= 0) return;
        await PowerCmd.Apply<EmberCleavePower>(
            choiceContext, owner, amount, applier: owner, cardSource: card);
    }

    /// <summary>Stoke the Flames (Pyro paper 2, 2026-10-12): "Your next Pyro
    /// Attack this turn deals 5 [7] additional damage."
    /// <see cref="StokeTheFlamesPower"/>. Sim twin: the `next_pyro_attack`
    /// kind.</summary>
    public static async Task NextPyroAttack(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        var amount = (int)Var(card, "VkBase");
        if (owner == null || amount <= 0) return;
        await PowerCmd.Apply<StokeTheFlamesPower>(
            choiceContext, owner, amount, applier: owner, cardSource: card);
    }

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
/// TIDAL BULWARK'S LIVE TOTAL (Varka text pass, 2026-10-13). Display only,
/// Shatter's shape: the face's <c>{VkHit}</c> is his Block plus <c>VkPer</c>
/// for each Hydro Oath, folded through the game's damage hooks against the
/// body <see cref="FrontFoldedDamageVar"/> picks with Hydro carried, as
/// <see cref="VarkaCards.TidalBulwark"/> deals it. Emitted by codegen for the
/// kinds in <c>VARKA_TARGET_PREVIEW_KINDS</c>.
/// </summary>
public sealed class VarkaTidalBulwarkDamageVar : DamageVar
{
    /// <summary>The face's token, Shatter's.</summary>
    public const string Token = "VkHit";

    public VarkaTidalBulwarkDamageVar()
        : base(Token, 0m, ValueProp.Move)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!runGlobalHooks || !card.IsMutable)
        {
            BaseValue = 0m;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        BaseValue = VarkaCards.TidalBulwarkDamage(
            owner == null ? 0 : (int)owner.Block,
            card.DynamicVars["VkPer"].BaseValue,
            VarkaOath.Count(owner, Element.Hydro));
        if (BaseValue <= 0)
        {
            // The play deals nothing here, so no Strength is folded onto it.
            PreviewValue = 0m;
            return;
        }
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        using (HitElement.Carry(card, Element.Hydro))
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

/// <summary>
/// THE SECOND HIT'S LIVE TOTAL ON FOUR WINDS' ASCENSION AND NORTHWIND AVATAR
/// (text pass 2026-10-13, [USER]: "Currently the second line doesn't actually
/// say how much it's going to hit for"). Display only, Shatter's shape: the
/// face's <c>{VkHit}</c> is <c>VkBase</c> (0 on a card that prints none) plus
/// <c>VkPer</c> for each Oath of his current element, folded through the
/// game's damage hooks against the body <see cref="FrontFoldedDamageVar"/>
/// picks (the aimed enemy, else the front one) with the current element
/// carried, as <see cref="VarkaCards.AscensionHit"/> and
/// <see cref="VarkaCards.AvatarHit"/> deal it. With no current element, or a
/// total of 0, the play deals nothing and the face prints 0. Emitted by
/// codegen for the kinds in <c>VARKA_CURRENT_HIT_PREVIEW_KINDS</c>.
/// </summary>
public sealed class VarkaCurrentElementHitVar : DamageVar
{
    /// <summary>The face's token, Thundering Verdict's and Shatter's.</summary>
    public const string Token = "VkHit";

    public VarkaCurrentElementHitVar()
        : base(Token, 0m, ValueProp.Move)
    {
    }

    /// <summary>The second hit before the hooks, as
    /// <c>VarkaCards.CurrentElementHit</c> computes it: 0 with no current
    /// element (the play skips the hit). PURE.</summary>
    public static int Raw(decimal baseDamage, decimal per, Element current,
                          int oath) =>
        current == Element.None
            ? 0
            : Math.Max(0, VarkaCards.CurrentElementDamage(baseDamage, per, oath));

    private static decimal BaseOf(CardModel card) =>
        card.DynamicVars.TryGetValue("VkBase", out var v) ? v.BaseValue : 0m;

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!runGlobalHooks || !card.IsMutable)
        {
            BaseValue = VarkaCards.CurrentElementDamage(
                BaseOf(card), card.DynamicVars["VkPer"].BaseValue, 0);
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        var element = VarkaOath.Current(owner);
        BaseValue = Raw(BaseOf(card), card.DynamicVars["VkPer"].BaseValue,
                        element, VarkaOath.CurrentOath(owner));
        if (BaseValue <= 0)
        {
            // The play deals nothing here, so no Strength is folded onto it.
            PreviewValue = 0m;
            return;
        }
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        using (HitElement.Carry(card, element))
        {
            base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        }
    }
}

/// <summary>
/// KINDLED EDGE'S "ADDITIONAL" HIT, FOLDED (Varka text pass, 2026-10-13, the
/// damage-preview census). Display only: the face's second number is the
/// card's <c>VkAmount</c> since the Varka pool audit (2026-10-13; was
/// <c>VkBase</c>), read live so the upgrade moves it,
/// folded the way <see cref="FoldedDamageVar"/> folds a follow-up leg: the
/// body's Vulnerable and his Strength, no reaction (the first hit consumed
/// the aura) and no element (<see cref="VarkaCards.KindledEdge"/>'s second
/// hit carries none). Emitted by codegen for <c>VARKA_FOLLOW_UP_KINDS</c>.
/// </summary>
public sealed class VarkaFollowUpDamageVar : DamageVar
{
    /// <summary>The var whose number the follow-up repeats.</summary>
    public string Source { get; }

    public VarkaFollowUpDamageVar(string name, string source)
        : base(name, 0m, ValueProp.Move)
    {
        Source = source;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        BaseValue = card.DynamicVars[Source].BaseValue;
        using var reaction = AuraPower.PreviewWithoutReaction();
        if (!runGlobalHooks || !card.IsMutable)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
    }
}

/// <summary>
/// A BONUS INSIDE ONE HIT, FOLDED (Varka text pass, 2026-10-13: Razor:
/// Awakening's "If it already has Electro, deal 3 additional damage").
/// Display only. The bonus rides the same hit as <c>VkBase</c>
/// (<see cref="VarkaCards.AwakeningDamage"/>), so his Strength counts once and
/// the body's Weak and Vulnerable multiply the sum: the printed bonus is the
/// folded hit with it less the folded hit without it, so the two printed
/// numbers add up to what the hit deals. Out of combat, the sheet number.
/// Emitted by codegen for <c>VARKA_BONUS_FOLD_KINDS</c>; the play reads the
/// var's <c>BaseValue</c>, which this never leaves changed.
/// </summary>
public sealed class VarkaBonusDamageVar : DamageVar
{
    /// <summary>The hit's own number, which the bonus is added to.</summary>
    public string Source { get; }

    /// <summary>The element the hit carries.</summary>
    public Element Carries { get; }

    public VarkaBonusDamageVar(string name, decimal amount, string source,
                               Element carries)
        : base(name, amount, ValueProp.Move)
    {
        Source = source;
        Carries = carries;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!runGlobalHooks || !card.IsMutable)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        var bonus = BaseValue;
        var hit = card.DynamicVars[Source].BaseValue;
        try
        {
            using (HitElement.Carry(card, Carries))
            {
                BaseValue = hit + bonus;
                base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
                var with = PreviewValue;
                BaseValue = hit;
                base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
                var without = PreviewValue;
                PreviewValue = Math.Max(0m, with - without);
            }
        }
        finally
        {
            BaseValue = bonus;
        }
    }
}

/// <summary>
/// STORM BATTERY'S LIVE TOTAL (Varka text pass, 2026-10-13). Display only:
/// the face's <c>{VkHit}</c> is <c>VkPer</c> for each other card in his Hand,
/// folded through the game's damage hooks with Electro carried, as
/// <see cref="VarkaCards.StormBattery"/> deals it to each enemy. An
/// all-enemies face, so the body is the game's own
/// (<see cref="FoldedPreview.Body"/>). Emitted by codegen for
/// <c>VARKA_TARGET_PREVIEW_KINDS</c>.
/// </summary>
public sealed class VarkaStormBatteryDamageVar : DamageVar
{
    /// <summary>The face's token, Shatter's.</summary>
    public const string Token = "VkHit";

    public VarkaStormBatteryDamageVar()
        : base(Token, 0m, ValueProp.Move)
    {
    }

    /// <summary>The other cards in the owner's Hand (the card leaves the Hand
    /// when it resolves, so the play's count is the same).</summary>
    public static int OthersInHand(CardModel card) =>
        card.IsMutable && card.Owner is { } player
            ? PileType.Hand.GetPile(player).Cards.Count(c => c != card)
            : 0;

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!runGlobalHooks || !card.IsMutable)
        {
            BaseValue = 0m;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var owner = card.Owner?.Creature;
        BaseValue = card.DynamicVars["VkPer"].BaseValue * OthersInHand(card);
        if (BaseValue <= 0)
        {
            PreviewValue = 0m;
            return;
        }
        var body = FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
        using (HitElement.Carry(card, Element.Electro))
        {
            base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        }
    }
}
