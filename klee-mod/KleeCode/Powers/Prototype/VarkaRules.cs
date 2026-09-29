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
/// VARKA'S CARD VERBS, one awaited call each from the generated rows
/// (<c>gen_klee_cards</c>: <c>knight_aura</c>, <c>add_knight</c> and the
/// <c>only_if: fresh_aura</c> damage rider) and from the hand-written
/// Knights' Muster.
///
/// THE KNIGHTS are his four personal-pool Companions (sec.4, sec.10.1:
/// "Knights are Varka's personal-pool companions, all Skills"): Amber
/// (Pyro), Barbara (Hydro), Lisa (Electro) and Kaeya (Cryo). A Knight CARD is
/// any Companion card whose personal pool is his, which is those four and
/// Knights' Muster ("a companion card", sec.4); Grand Master's Order repeats
/// either.
///
/// "CHOOSE A KNIGHT" IS A GRID. Four Knights do not fit the choose-a-card
/// screen, which throws on more than three cards
/// (<c>CardSelectCmd.FromChooseACardScreen</c>, 0.111.0 decompile), so the
/// choice is <c>CardSelectCmd.FromSimpleGrid</c> over four option faces, the
/// screen Treasure Map's discard pick already opens and the bridge already
/// answers. Co-op synced by index, as the game syncs every grid.
/// </summary>
public static class VarkaRules
{
    private const string Table = "cards";

    /// <summary>The grid's prompt, keyed on the verb. Merged into the `cards`
    /// table by <c>KleeMod.InjectLocStrings</c>, its only source.</summary>
    public const string KnightPromptKey =
        "KLEEMOD-CHOOSE_KNIGHT.selectionScreenPrompt";

    public const string KnightPromptText = "Choose a Knight.";

    /// <summary>The four Knights' elements, in the order their option faces
    /// and cards are listed everywhere.</summary>
    public static readonly IReadOnlyList<Element> KnightElements = new[]
    {
        Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo,
    };

    /// <summary>Is this a Knight card: a Companion card in his personal
    /// pool? PURE.</summary>
    public static bool IsKnight(CardModel? card) =>
        card is ICompanionCard { PersonalPool: VarkaPrototype.CharacterId };

    /// <summary>The four Knight cards, canonical, in
    /// <see cref="KnightElements"/>' order.</summary>
    public static IReadOnlyList<CardModel> KnightCards() => new CardModel[]
    {
        ModelDb.Card<ProtoVkAmberBaronBunny>(),
        ModelDb.Card<ProtoVkBarbaraShowBegin>(),
        ModelDb.Card<ProtoVkLisaVioletArc>(),
        ModelDb.Card<ProtoVkKaeyaFrostgnaw>(),
    };

    /// <summary>
    /// Ask the player which Knight: four option faces on a grid. Returns the
    /// Knight's element, or <see cref="Element.None"/> when there is no
    /// board to ask on or nothing came back.
    /// </summary>
    public static async Task<Element> ChooseKnight(
        PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Creature?.CombatState == null) return Element.None;
        var options = new List<CardModel>
        {
            ModalChoice.CreateOption<KnightOptionAmber>(owner),
            ModalChoice.CreateOption<KnightOptionBarbara>(owner),
            ModalChoice.CreateOption<KnightOptionLisa>(owner),
            ModalChoice.CreateOption<KnightOptionKaeya>(owner),
        };
        var picked = (await CardSelectCmd.FromSimpleGrid(
            choiceContext, options, owner,
            new CardSelectorPrefs(new LocString(Table, KnightPromptKey), 1)))
            .FirstOrDefault();
        return ElementOfOption(options, picked);
    }

    /// <summary>The element of the option face picked, by position. PURE.
    /// </summary>
    public static Element ElementOfOption(
        IReadOnlyList<CardModel> options, CardModel? picked)
    {
        if (picked == null) return Element.None;
        for (var i = 0; i < options.Count && i < KnightElements.Count; i++)
        {
            if (ReferenceEquals(options[i], picked)) return KnightElements[i];
        }
        return Element.None;
    }

    /// <summary>
    /// Favonius Drill: "Choose a Knight: apply their element to the enemy."
    /// The element lands through <see cref="ElementalHit.ApplyOnly"/>, the
    /// door every damage-less application takes, so on a standing aura it
    /// reacts as any Knight's paint would.
    /// </summary>
    public static async Task KnightAura(
        PlayerChoiceContext choiceContext, Player? owner, Creature target)
    {
        var element = await ChooseKnight(choiceContext, owner);
        if (element == Element.None || !target.IsAlive) return;
        await ElementalHit.ApplyOnly(
            choiceContext, target, element, owner!.Creature);
    }

    /// <summary>
    /// Knights' Roll Call: "Add a random Knight to your hand. It costs 0 this
    /// turn." Upgraded, the player picks it (<paramref name="choose"/>, the
    /// card's own <c>IsUpgraded</c>). The pick shows the four Knight cards
    /// themselves, since the card is what arrives.
    /// </summary>
    public static async Task AddKnight(
        PlayerChoiceContext choiceContext, Player? owner, bool choose)
    {
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;

        CardModel? card;
        if (choose)
        {
            var options = KnightCards()
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
                KnightCards().ToList());
            card = canonical == null ? null : combat.CreateCard(canonical, owner);
        }
        if (card == null) return;
        card.EnergyCost.SetThisTurn(0);
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, owner);
    }

    // ---- Gale Sweep -------------------------------------------------------

    /// <summary>The bodies a running Gale Sweep has still to hit. A Swirl's
    /// spread passes them by (<see cref="SpreadShielded"/>), so "a spread
    /// from an earlier Swirl in the sweep does not cancel a later one"
    /// (sec.9.6).</summary>
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
    /// Gale Sweep (sec.10.3; sec.9.6): "Deal 3 Anemo to every enemy that has
    /// a fresh aura. (Snapshot when played; each Swirls.)" The bodies are
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
}
