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

    private int _round = -1;

    /// <summary>A new round clears the turn's Knight count.</summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        _round = round;
        KnightsThisTurn = 0;
    }

    // ---- reads ------------------------------------------------------------

    /// <summary>His Oath of <paramref name="element"/> (0 for any element
    /// that keeps none).</summary>
    public int Oath(Element element) =>
        _oath.TryGetValue(element, out var n) ? n : 0;

    /// <summary>The one count his cards read: the current element's.</summary>
    public int CurrentOath => Oath(Current);

    /// <summary>How many elements he has any Oath in (Tailwind Guard).</summary>
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
        Current = element;
        return true;
    }

    /// <summary>A Knight was played (or replayed) this turn.</summary>
    public void NoteKnight() => KnightsThisTurn++;

    /// <summary>A Swirl he made, on <paramref name="swirled"/>.</summary>
    public void NoteSwirl(Creature swirled)
    {
        SwirlsMade++;
        if (_scopeDepth > 0) _swirledThisPlay.Add(swirled);
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

    /// <summary>Four Winds' Accord's first half: the total split evenly among
    /// the four, rounding down. The +1 of each is four gains, which
    /// <see cref="VarkaOath"/> pays.</summary>
    public void Split()
    {
        var each = Total / Elements.Count;
        foreach (var e in Elements) _oath[e] = each;
    }

    // ---- the per-play credit scope ----------------------------------------

    private int _scopeDepth;
    /// <summary>Per open scope, innermost last: is it an OPEN-OATH play (a
    /// card of his that is not a Knight), and which card. Baron Bunny's
    /// scope and a Knight's play are not.</summary>
    private readonly List<(bool Open, object? Card)> _plays = new();
    private readonly HashSet<(bool Swirl, Element Element)> _credited = new();
    private readonly List<Creature> _swirledThisPlay = new();

    /// <summary>Is a card play (or a scoped event) open?</summary>
    public bool Scoped => _scopeDepth > 0;

    /// <summary>While positive, an application credits nothing (Four Winds'
    /// Ascension's elemental hit).</summary>
    public int SuppressApply { get; set; }

    /// <summary>A play opens: its credits start empty. <paramref name="open"/>
    /// marks a play of his own non-Knight card (<paramref name="card"/>),
    /// whose applications set his current element.</summary>
    public void OpenScope(bool open = false, object? card = null)
    {
        if (_scopeDepth++ == 0)
        {
            _credited.Clear();
            _swirledThisPlay.Clear();
            _plays.Clear();
        }
        _plays.Add((open, card));
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
        if (_scopeDepth == 0) return true;
        return _credited.Add((swirl, element));
    }

    /// <summary>The enemies this play has Swirled, in order (Storm Surge).
    /// </summary>
    public IReadOnlyList<Creature> SwirledThisPlay => _swirledThisPlay;
}

/// <summary>
/// VARKA'S OATH RULES (sec.3, sec.4), the one door that moves the ledger and
/// pays for it. Every Knight play, every application and every Swirl of his
/// passes here once:
///
///   * <see cref="BeginPlay"/> / <see cref="EndPlay"/> bracket each card play
///     (<c>KleeElementalHooks</c>), and a Knight sets his current element
///     before its effects resolve (Favonian Standard, Boreas Unbound).
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
    /// <summary>Is this creature Varka with the arm live?</summary>
    public static bool Live(Creature? creature) => VarkaPrototype.LiveFor(creature);

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

    public static int KnightsPlayedThisTurn(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).KnightsThisTurn : 0;

    public static int SwirlsMadeBy(Creature? creature) =>
        creature != null && Live(creature)
            ? VarkaOathLedger.For(creature).SwirlsMade : 0;

    /// <summary>The element a Knight card sets, or None for any other card.
    /// PURE.</summary>
    public static Element KnightElement(CardModel? card) =>
        VarkaRules.IsKnight(card) && card is ICompanionCard companion
            ? companion.CompanionElement : Element.None;

    // ---- the play bracket -------------------------------------------------

    /// <summary>
    /// A card play opens (every replay too). Opens his credit scope (an
    /// open-Oath one for any card that is not a Knight, <see
    /// cref="VarkaOathLedger.OpenOathSwitches"/>), and if
    /// the card is a Knight sets his current element BEFORE its effects:
    /// Favonian Standard pays when the Knight's element was already current,
    /// Boreas Unbound when it changes (sec.6).
    /// </summary>
    public static async Task BeginPlay(CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (!Live(owner)) return;
        var ledger = VarkaOathLedger.For(owner!);
        ledger.OpenScope(open: !VarkaRules.IsKnight(card), card: card);
        var element = KnightElement(card);
        if (element == Element.None) return;
        ledger.NoteKnight();
        await SetCurrent(new ThrowingPlayerChoiceContext(), owner!, element,
                         knight: true);
    }

    /// <summary>A card play ends.</summary>
    public static void EndPlay(CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (!Live(owner)) return;
        VarkaOathLedger.For(owner!).CloseScope();
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
    /// Make <paramref name="element"/> his current element. A Knight whose
    /// element was already current pays Favonian Standard; a change pays
    /// Boreas Unbound. The badge follows.
    /// </summary>
    public static async Task SetCurrent(
        PlayerChoiceContext choiceContext, Creature varka, Element element,
        bool knight)
    {
        if (!Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
        if (knight && element == ledger.Current)
        {
            foreach (var standard in varka.Powers.OfType<FavonianStandardPower>().ToList())
            {
                await CreatureCmd.GainBlock(varka, standard.Amount,
                    ValueProp.Unpowered, null, fast: true);
            }
        }
        if (ledger.SetCurrent(element))
        {
            foreach (var unbound in varka.Powers.OfType<BoreasUnboundPower>().ToList())
            {
                await unbound.OnElementChanged();
            }
        }
        await OathBadge.Sync(choiceContext, varka);
    }

    // ---- gains --------------------------------------------------------------

    /// <summary>
    /// Every Oath gain: add it, pay Dawn Wind's March when it is the current
    /// element's, and let Boreas's Fang add Four Winds' Ascension the first
    /// time each combat (sec.4). One call is one gain event.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature varka, Element element,
        int n)
    {
        if (!Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
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
        if (!ledger.FangFired && varka.Player is { } player
            && Relics.BoreasFang.HeldBy(player) is { } fang)
        {
            ledger.FangFired = true;
            await fang.AddAscension(player);
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
    /// when the hit names one.
    /// </summary>
    public static async Task NoteApplication(
        PlayerChoiceContext choiceContext, Creature? applier, Element element,
        CardModel? cardSource = null)
    {
        if (applier == null || !Live(applier) || !element.LeavesAura()) return;
        var ledger = VarkaOathLedger.For(applier);
        if (ledger.OpenOathSwitches(element, cardSource))
        {
            await SetCurrent(choiceContext, applier, element, knight: false);
        }
        if (!ledger.TryCredit(swirl: false, element)) return;
        await Gain(choiceContext, applier, element, 1);
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
        ledger.NoteSwirl(target);
        if (ledger.TryCredit(swirl: true, swirled))
        {
            await Gain(choiceContext, dealer, swirled, 1);
        }
        var current = ledger.Current;
        switch (current)
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
                foreach (var enemy in dealer.CombatState?.HittableEnemies.ToList()
                                      ?? new List<Creature>())
                {
                    if (!enemy.IsAlive) continue;
                    await ElementalHit.DealUnelemented(
                        choiceContext, enemy, VarkaLaw.SwirlElectroDamageAll,
                        dealer, powered: false);
                }
                break;
        }
        if (current != Element.None)
        {
            Log.Info($"[{KleeMod.ModId}] VARKA Swirl on {target.Name}: "
                   + $"{swirled} Oath, paid {current}.");
        }
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
    /// Sworn Brotherhood, then Oath of the Knights (which reads the count
    /// after Sworn Brotherhood's gain). Called from
    /// <c>KleeElementalHooks.AfterPlayerTurnStart</c>.
    /// </summary>
    public static async Task TurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        var varka = player.Creature;
        if (!Live(varka)) return;
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
        foreach (var oath in varka.Powers.OfType<OathOfTheKnightsPower>().ToList())
        {
            var block = CurrentOath(varka) * oath.Amount;
            if (block <= 0) continue;
            await CreatureCmd.GainBlock(varka, block, ValueProp.Unpowered, null,
                                        fast: true);
        }
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

    /// <summary>Knightly Guard: "gain 1 Oath of your current element".
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
    /// Four Winds' Ascension's second hit: "Then deal 3 [4] damage for each
    /// Oath of your current element, as that element." The Oath is read after
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
                .WithHitFx("vfx/vfx_attack_slash")
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

    /// <summary>Wall of Gales: "Swirl every fresh aura." The fresh bodies are
    /// taken when it is played and each takes its own damage-less Anemo hit,
    /// shielded from an earlier Swirl's spread as Gale Sweep's are.</summary>
    public static Task SwirlFreshAuras(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        VarkaRules.SwirlFreshAuras(choiceContext, card.Owner?.Creature);

    /// <summary>Eula: "Gain 1 Cryo Oath for each enemy with a Cryo aura",
    /// fresh or spent, read after her hit. One gain.</summary>
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
    /// current element. Gain Block equal to its Oath." A grid of the elements
    /// he holds Oath in; not a Knight, so Favonian Standard passes it by and
    /// Boreas Unbound sees the change.
    /// </summary>
    public static async Task ChangeOfGuard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        var ledger = VarkaOathLedger.For(owner);
        var held = VarkaOathLedger.Elements.Where(e => ledger.Oath(e) > 0).ToList();
        if (held.Count == 0) return;
        var element = held.Count == 1
            ? held[0]
            : await VarkaRules.ChooseElement(choiceContext, card.Owner, held);
        if (element == Element.None) return;
        await VarkaOath.SetCurrent(choiceContext, owner, element, knight: false);
        var block = ledger.Oath(element);
        if (block > 0)
        {
            await CreatureCmd.GainBlock(owner, block, ValueProp.Unpowered, null,
                                        fast: true);
        }
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

    /// <summary>Four Winds' Accord: "Split your total Oath evenly among the
    /// four elements, rounding down, then gain 1 of each."</summary>
    public static async Task Accord(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner?.Creature;
        if (owner == null || !VarkaOath.Live(owner)) return;
        VarkaOathLedger.For(owner).Split();
        foreach (var element in VarkaOathLedger.Elements)
        {
            await VarkaOath.Gain(choiceContext, owner, element, 1);
        }
        await OathBadge.Sync(choiceContext, owner);
    }

    /// <summary>Unfurled Banner: "Put Four Winds' Ascension from your discard
    /// pile into your hand. It costs 0 this turn." Nothing if none is there.
    /// </summary>
    public static async Task UnfurledBanner(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var player = card.Owner;
        if (player == null) return;
        var ascension = PileType.Discard.GetPile(player).Cards
            .OfType<ProtoVkFourWindsAscension>().FirstOrDefault();
        if (ascension == null) return;
        await CardPileCmd.Add(ascension, PileType.Hand);
        ascension.EnergyCost.SetThisTurn(0);
    }
}
