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
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>One Sesshou Sakura: its Level, the strikes it has left, and its
/// place in planting order (the ledger's clock).</summary>
public sealed class YaeSakura
{
    public int Level { get; internal set; }

    public int TurnsLeft { get; internal set; }

    public int Seq { get; internal set; }
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

    /// <summary>
    /// PLANT ONE (pick 1 (a), ruled): every standing Sakura gains a Level (to
    /// <paramref name="levelCap"/>), then a new one is added at
    /// <paramref name="plantLevel"/> with <see cref="YaeLaw.SakuraTurns"/>
    /// strikes left -- unless three stand, in which case the three are
    /// levelled and none is added. Returns whether one was added.
    /// </summary>
    public bool Plant(int plantLevel, int levelCap)
    {
        foreach (var s in _sakura)
        {
            s.Level = Math.Min(levelCap, s.Level + 1);
        }
        if (_sakura.Count >= YaeLaw.SakuraCap) return false;
        Seq++;
        _sakura.Add(new YaeSakura
        {
            Level = plantLevel,
            TurnsLeft = YaeLaw.SakuraTurns,
            Seq = Seq,
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

    /// <summary>"Each Sakura gains a Level": +n each, capped.</summary>
    public void LevelUp(int n, int levelCap)
    {
        foreach (var s in _sakura) s.Level = Math.Min(levelCap, s.Level + n);
    }

    /// <summary>After the end-of-turn strikes every timer ticks; a Sakura at
    /// 0 withers. Returns how many withered.</summary>
    public int TickAndWither()
    {
        foreach (var s in _sakura) s.TurnsLeft--;
        return _sakura.RemoveAll(s => s.TurnsLeft <= 0);
    }

    /// <summary>Editor-in-Chief's Sakura: the highest Level, the oldest on a
    /// tie. Null with none standing.</summary>
    public YaeSakura? Highest() =>
        _sakura.OrderByDescending(s => s.Level).ThenBy(s => s.Seq).FirstOrDefault();

    internal void NoteStrike() => Strikes++;

    internal void NoteEdit() => Edits++;

    /// <summary>
    /// One strike's printed amount (sec.2): 2 + its Level, Sakura Grove's
    /// bonus, and Edict of Cleansing's on an enemy whose aura the strike will
    /// react with. The enemy's Vulnerable and Block apply later, in the hit.
    /// PURE.
    /// </summary>
    public static int StrikeDamage(int level, int grove, bool reacts, int edict) =>
        YaeLaw.SakuraBase + level + grove + (reacts ? edict : 0);
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

    /// <summary>The Level a Sakura is planted at: 1, or 2 under Fox's
    /// Mooncall.</summary>
    public static int PlantLevel(Creature yae) =>
        yae.HasPower<FoxsMooncallPower>() ? YaeLaw.MooncallPlantLevel : YaeLaw.PlantLevel;

    /// <summary>The Level a Sakura can reach: 3, or 4 under Fox's Mooncall.
    /// </summary>
    public static int LevelCap(Creature yae) =>
        yae.HasPower<FoxsMooncallPower>() ? YaeLaw.MooncallLevelCap : YaeLaw.LevelCap;

    /// <summary>Do Pyro, Hydro or Cryo sit on this enemy, so an Electro strike
    /// reacts (Edict of Cleansing's read)?</summary>
    public static bool Reacts(Creature? target)
    {
        var aura = target == null ? null : AuraCmd.Find(target);
        return aura != null && aura.Element is Element.Pyro or Element.Hydro or Element.Cryo;
    }

    /// <summary>Plant <paramref name="n"/> Sakura, one at a time (each levels
    /// the ones standing).</summary>
    public static async Task Plant(PlayerChoiceContext choiceContext,
                                   Creature? yae, int n)
    {
        if (yae == null || !Live(yae) || n <= 0) return;
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < n; i++)
        {
            ledger.Plant(PlantLevel(yae), LevelCap(yae));
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>The enemy a strike lands on: this turn's Lure while it
    /// lives, else one random living enemy off the combat target stream.
    /// </summary>
    private static Creature? Aim(Creature yae)
    {
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Lure is { IsAlive: true } lured) return lured;
        var living = yae.CombatState?.HittableEnemies.Where(e => e.IsAlive).ToList();
        if (living == null || living.Count == 0) return null;
        var rng = yae.Player?.RunState.Rng.CombatTargets;
        return rng == null ? living[0] : rng.NextItem(living);
    }

    /// <summary>
    /// One Sakura's strike: 2 + its Level Electro on one enemy, a PET'S HIT
    /// (her Strength and Weak do not apply; the enemy's Vulnerable and Block
    /// do), reacting with whatever aura it lands on, credited to Yae. Sakura
    /// Channeling pays after.
    /// </summary>
    public static async Task Strike(PlayerChoiceContext choiceContext,
                                    Creature yae, YaeSakura sakura)
    {
        var target = Aim(yae);
        if (target == null) return;
        var damage = YaeShrineLedger.StrikeDamage(
            sakura.Level, yae.GetPowerAmount<SakuraGrovePower>(),
            Reacts(target), yae.GetPowerAmount<EdictOfCleansingPower>());
        YaeShrineLedger.For(yae).NoteStrike();
        await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, Element.Electro, damage, yae);
        await SakuraChannelingPower.Pay(yae);
    }

    /// <summary>Every Sakura strikes, oldest first, while an enemy lives.
    /// </summary>
    public static async Task StrikeAll(PlayerChoiceContext choiceContext,
                                       Creature yae)
    {
        foreach (var sakura in YaeShrineLedger.For(yae).Standing.ToList())
        {
            if (yae.CombatState?.HittableEnemies.Any(e => e.IsAlive) != true) break;
            await Strike(choiceContext, yae, sakura);
        }
    }

    /// <summary>
    /// TENKO: "every Sakura strikes now (the same strikes, oldest first),
    /// then every timer is set back to 3. Tenko with no Sakura does nothing.
    /// Tenko keeps the board."
    /// </summary>
    public static async Task Tenko(PlayerChoiceContext choiceContext, Creature? yae)
    {
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        if (ledger.Count == 0) return;
        await StrikeAll(choiceContext, yae);
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
    /// Yakan Offering plants.
    /// </summary>
    public static async Task TurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        var yae = player.Creature;
        if (yae == null || !Live(yae)) return;
        var ledger = YaeShrineLedger.For(yae);
        ledger.Lure = null;
        await FoxfireLurePower.ClearAll(yae);
        var offering = yae.GetPowerAmount<YakanOfferingPower>();
        if (offering > 0)
        {
            yae.Powers.OfType<YakanOfferingPower>().FirstOrDefault()?.Pulse();
            await Plant(choiceContext, yae, offering);
        }
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// Her turn end (<c>KleeElementalHooks.BeforeSideTurnEnd</c>, the sim's
    /// <c>yae_shrine.turn_end</c> site): the strikes, then every timer ticks
    /// and the withered leave.
    /// </summary>
    public static async Task TurnEnd(PlayerChoiceContext choiceContext, Creature yae)
    {
        if (!Live(yae)) return;
        await StrikeAll(choiceContext, yae);
        YaeShrineLedger.For(yae).TickAndWither();
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>
    /// Editor-in-Chief, after the card's own effects and its Annotation's:
    /// "Whenever you play an Annotated card, a Sakura strikes (the highest
    /// Level)", once per stack.
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
            await Strike(choiceContext, yae, sakura);
        }
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

    /// <summary>"Plant a Sakura" / "Plant 2 Sakura".</summary>
    public static Task Plant(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        YaeShrine.Plant(choiceContext, card.Owner?.Creature, Var(card, "YmAmount"));

    /// <summary>"Tenko."</summary>
    public static Task Tenko(PlayerChoiceContext choiceContext, CardModel card,
                             CardPlay cardPlay) =>
        YaeShrine.Tenko(choiceContext, card.Owner?.Creature);

    /// <summary>Shrine Offering: "Each Sakura lasts 1 more turn."</summary>
    public static async Task Extend(PlayerChoiceContext choiceContext,
                                    CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).Extend(Var(card, "YmAmount"));
        await SakuraBadge.Sync(choiceContext, yae);
    }

    /// <summary>Rooted Shrine: "Each Sakura gains a Level."</summary>
    public static async Task LevelUp(PlayerChoiceContext choiceContext,
                                     CardModel card, CardPlay cardPlay)
    {
        var yae = card.Owner?.Creature;
        if (yae == null || !YaeShrine.Live(yae)) return;
        YaeShrineLedger.For(yae).LevelUp(Var(card, "YmAmount"), YaeShrine.LevelCap(yae));
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
