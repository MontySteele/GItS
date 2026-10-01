using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// VARKA'S KNIGHTS AND HIS TWO GRIDS (the Oath rework, sec.6): what a Knight
/// is, Knights' Roll Call's add (<c>gen_klee_cards</c>'s <c>add_knight</c>),
/// Change of Guard's element pick, and the fresh-aura sweeps (Gale Sweep's
/// <c>only_if: fresh_aura</c> rider and Wall of Gales).
///
/// A KNIGHT is any Companion card whose personal pool is his: the nine pool
/// Knights and the four starter-only ones (sec.5, sec.6). Playing one sets
/// his current element (<see cref="VarkaOath.BeginPlay"/>); Grand Master's
/// Order repeats one.
///
/// A CHOICE OF MORE THAN THREE IS A GRID. The choose-a-card screen throws on
/// more than three cards (<c>CardSelectCmd.FromChooseACardScreen</c>, 0.111.0
/// decompile), so both picks are <c>CardSelectCmd.FromSimpleGrid</c>, the
/// screen Treasure Map's discard pick opens and the bridge answers. Co-op
/// synced by index, as the game syncs every grid.
/// </summary>
public static class VarkaRules
{
    private const string Table = "cards";

    /// <summary>Knights' Roll Call+'s prompt. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, its only source.</summary>
    public const string KnightPromptKey =
        "KLEEMOD-CHOOSE_KNIGHT.selectionScreenPrompt";

    public const string KnightPromptText = "Choose a Knight.";

    /// <summary>Change of Guard's prompt, on the same terms.</summary>
    public const string ElementPromptKey =
        "KLEEMOD-CHOOSE_ELEMENT.selectionScreenPrompt";

    public const string ElementPromptText = "Choose your current element.";

    /// <summary>Is this a Knight card: a Companion card in his personal
    /// pool? PURE.</summary>
    public static bool IsKnight(CardModel? card) =>
        card is ICompanionCard { PersonalPool: VarkaPrototype.CharacterId };

    /// <summary>The POOL Knights Knights' Roll Call draws from (sec.6),
    /// canonical, in pool order: nine, and thirteen since the expansion
    /// (2026-10-01), Noelle among them. The starter-only four are not.
    /// </summary>
    public static IReadOnlyList<CardModel> PoolKnights() => new CardModel[]
    {
        ModelDb.Card<ProtoVkAmberBaronBunny>(),
        ModelDb.Card<ProtoVkBarbaraShowBegin>(),
        ModelDb.Card<ProtoVkLisaVioletArc>(),
        ModelDb.Card<ProtoVkKaeyaFrostgnaw>(),
        ModelDb.Card<ProtoVkRazorClawAndThunder>(),
        ModelDb.Card<ProtoVkMikaStarfrostSwirl>(),
        ModelDb.Card<ProtoVkDilucSearingOnslaught>(),
        ModelDb.Card<ProtoVkEulaIcetideVortex>(),
        ModelDb.Card<ProtoVkBarbaraWhisperOfWater>(),
        // THE EXPANSION (2026-10-01).
        ModelDb.Card<ProtoVkAmberSharpshooter>(),
        ModelDb.Card<ProtoVkBarbaraWellspringHymn>(),
        ModelDb.Card<ProtoVkLisaPulsatingWitch>(),
        ModelDb.Card<ProtoVkNoelleSteadfastMaid>(),
    };

    /// <summary>The four starter-only Knights, one of which joins each run's
    /// starter (sec.5), in <see cref="VarkaOathLedger.Elements"/>' order.
    /// </summary>
    public static IReadOnlyList<CardModel> StarterKnights() => new CardModel[]
    {
        ModelDb.Card<ProtoVkAmberFieryRain>(),
        ModelDb.Card<ProtoVkBarbaraMelodyLoop>(),
        ModelDb.Card<ProtoVkLisaLightningRose>(),
        ModelDb.Card<ProtoVkKaeyaGlacialWaltz>(),
    };

    /// <summary>Is this one of the four starter-only Knights? PURE.</summary>
    public static bool IsStarterKnight(CardModel? card) =>
        card is ProtoVkAmberFieryRain or ProtoVkBarbaraMelodyLoop
            or ProtoVkLisaLightningRose or ProtoVkKaeyaGlacialWaltz;

    /// <summary>
    /// Knights' Roll Call: "Add a random Knight to your hand. It costs 0 this
    /// turn." Upgraded, the player picks it (<paramref name="choose"/>, the
    /// card's own <c>IsUpgraded</c>) on a grid of the Knight cards themselves.
    /// </summary>
    public static async Task AddKnight(
        PlayerChoiceContext choiceContext, Player? owner, bool choose)
    {
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;

        CardModel? card;
        if (choose)
        {
            var options = PoolKnights()
                .Select(c => combat.CreateCard(c, owner))
                .Where(c => c != null)
                .Cast<CardModel>()
                .ToList();
            card = (await CardSelectCmd.FromSimpleGrid(
                choiceContext, options, owner,
                new CardSelectorPrefs(new LocString(Table, KnightPromptKey), 1)))
                .FirstOrDefault();
        }
        else
        {
            var canonical = owner.RunState.Rng.CombatTargets.NextItem(
                PoolKnights().ToList());
            card = canonical == null ? null : combat.CreateCard(canonical, owner);
        }
        if (card == null) return;
        card.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, owner);
    }

    /// <summary>
    /// The Order Answers: "add a random Knight to your hand", a pool Knight
    /// at its own cost (<paramref name="free"/> false), off the same roll
    /// Knights' Roll Call takes.
    /// </summary>
    public static async Task AddRandomKnight(Player? owner, bool free)
    {
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        var canonical = owner.RunState.Rng.CombatTargets.NextItem(
            PoolKnights().ToList());
        var card = canonical == null ? null : combat.CreateCard(canonical, owner);
        if (card == null) return;
        if (free) card.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, owner);
    }

    /// <summary>
    /// DOWNBURST (the expansion, pick 3a): "If it Swirls, the copies it
    /// spreads arrive fresh." The card itself is the marker; read where the
    /// Swirl's spread lands a copy (<c>ReactionEffects.SwirlPays</c>). PURE.
    /// </summary>
    public static bool SpreadArrivesFresh(CardModel? cardSource) =>
        VarkaPrototype.Enabled && cardSource is ProtoVkDownburst;

    /// <summary>
    /// Change of Guard's pick: the elements he holds Oath in, as option faces
    /// on a grid (<see cref="Cards.Prototype.VarkaModalOptions"/>). Returns
    /// the element, or <see cref="Element.None"/> when nothing came back.
    /// <paramref name="optional"/> (Weathervane's "you may") lets the player
    /// close the grid without a pick.
    /// </summary>
    public static async Task<Element> ChooseElement(
        PlayerChoiceContext choiceContext, Player? owner,
        IReadOnlyList<Element> elements, bool optional = false)
    {
        if (owner?.Creature?.CombatState == null) return Element.None;
        var options = elements
            .Select(e => Cards.Prototype.VarkaModalOptions.FaceFor(e, owner))
            .Where(c => c != null)
            .Cast<CardModel>()
            .ToList();
        var picked = (await CardSelectCmd.FromSimpleGrid(
            choiceContext, options, owner,
            new CardSelectorPrefs(new LocString(Table, ElementPromptKey), 1)
            {
                Cancelable = optional,
            }))
            .FirstOrDefault();
        return picked is Cards.Prototype.ElementOption face
            ? face.OptionElement : Element.None;
    }

    // ---- Gale Sweep -------------------------------------------------------

    /// <summary>The bodies a running Gale Sweep has still to hit. A Swirl's
    /// spread passes them by (<see cref="SpreadShielded"/>), so "a spread
    /// from an earlier Swirl in the sweep does not cancel a later one".
    /// </summary>
    private static readonly HashSet<Creature> SweepPending = new();

    private static readonly object Gate = new();

    /// <summary>Does a Swirl's spread pass this body by, because a Gale
    /// Sweep still owes it its own hit? PURE.</summary>
    public static bool SpreadShielded(Creature? body)
    {
        if (body == null) return false;
        lock (Gate) return SweepPending.Contains(body);
    }

    /// <summary>The bodies a Gale Sweep played now would hit: every hittable
    /// enemy wearing a FRESH aura, in enemy order. PURE.</summary>
    public static List<Creature> FreshAuraBodies(IEnumerable<Creature> enemies) =>
        enemies.Where(e => AuraCmd.Find(e) is { Spent: false }).ToList();

    /// <summary>
    /// Gale Sweep (sec.6): "Deal 3 [5] Anemo to every enemy that has a fresh
    /// aura." (Snapshot when played; each Swirls.) The bodies are
    /// taken when it is played, and each takes its own hit from the card, in
    /// enemy order, so each Anemo hit Swirls its own aura through the shared
    /// rule. While the sweep runs, a body it has not reached yet keeps its
    /// aura against the earlier Swirls' spread.
    /// </summary>
    public static async Task HitFreshAuras(
        PlayerChoiceContext choiceContext, Creature? owner, CardModel card,
        CardPlay cardPlay, decimal damage)
    {
        var combat = owner?.CombatState;
        if (combat == null) return;
        var bodies = FreshAuraBodies(combat.HittableEnemies);
        lock (Gate) SweepPending.UnionWith(bodies);
        try
        {
            foreach (var body in bodies)
            {
                lock (Gate) SweepPending.Remove(body);
                if (!body.IsAlive) continue;
                await DamageCmd.Attack(damage)
                    .FromCard(card, cardPlay)
                    .Targeting(body)
                    .WithHitFx("vfx/vfx_attack_slash")
                    .Execute(choiceContext);
            }
        }
        finally
        {
            lock (Gate) SweepPending.ExceptWith(bodies);
        }
    }

    /// <summary>
    /// Wall of Gales (sec.6): "Swirl every fresh aura." The bodies wearing a
    /// fresh aura are taken when it is played; each takes its own damage-less
    /// Anemo hit (<see cref="ElementalHit.ApplyOnly"/>, the shared rule), and
    /// a body not reached yet keeps its aura against the earlier Swirls'
    /// spread, as Gale Sweep's do.
    /// </summary>
    public static async Task SwirlFreshAuras(
        PlayerChoiceContext choiceContext, Creature? owner)
    {
        var combat = owner?.CombatState;
        if (combat == null) return;
        var bodies = FreshAuraBodies(combat.HittableEnemies);
        lock (Gate) SweepPending.UnionWith(bodies);
        try
        {
            foreach (var body in bodies)
            {
                lock (Gate) SweepPending.Remove(body);
                if (!body.IsAlive) continue;
                await ElementalHit.ApplyOnly(
                    choiceContext, body, Element.Anemo, owner);
            }
        }
        finally
        {
            lock (Gate) SweepPending.ExceptWith(bodies);
        }
    }
}
