using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using KleeMod.Relics;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Abyss;

/// <summary>
/// THE SPIRAL ABYSS MODE (<c>review/active/spiral-abyss-pools-2026-10-12.md</c>
/// sec.4): a run modifier, saved with the run. It holds the Blessings and
/// Shadows taken so far and applies them through combat hooks.
///
/// GATED BY PRESENCE. A modifier receives hooks only in a run that carries it,
/// so a normal run never reaches a line below. The two places this mode
/// touches shared code -- the Ancient's choice page and the reaction count on
/// the shield -- both start by asking whether the run carries this modifier
/// (or the body wears the shield), and do nothing otherwise.
///
/// REGISTERED by BaseLib's <see cref="CustomModifierModel"/> (BaseLib 3.4.7
/// has it): Good alignment, so it is a tickbox on the Custom screen. Daily
/// runs and the Custom screen's Randomize never roll it
/// (<see cref="AbyssModifierListPatches"/>).
/// </summary>
public sealed class SpiralAbyss : CustomModifierModel, ILocalizationProvider
{
    public override ModifierAlignment Alignment => ModifierAlignment.Good;

    /// <summary>The Custom screen's tickbox icon (the official Spiral Abyss
    /// emblem). <c>ModifierModel.Icon</c> falls back to the missing-icon
    /// square when this does not resolve.</summary>
    protected override string IconPath => KleePck.Path(AbyssMenu.IconFile) ?? base.IconPath;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Spiral Abyss"),
        ("description",
            "Before each act's Ancient, take one of three Blessings. The enemies "
          + "take one of the two Shadows you pass. Some last the whole run; "
          + "others end with the act."),
    };

    private AbyssRecord? _record;

    /// <summary>What the run has taken. Lazily built, because the canonical
    /// instance and a MemberwiseClone must never share one.</summary>
    public AbyssRecord Record => _record ??= new AbyssRecord();

    // ---- The save: three parallel int[] (see AbyssRecord). ---------------

    [SavedProperty]
    public int[] SpiralAbyssActs
    {
        get => Record.ActsArray();
        set => Record.LoadActs(value);
    }

    [SavedProperty]
    public int[] SpiralAbyssBlessings
    {
        get => Record.BlessingsArray();
        set => Record.LoadBlessings(value);
    }

    [SavedProperty]
    public int[] SpiralAbyssShadows
    {
        get => Record.ShadowsArray();
        set => Record.LoadShadows(value);
    }

    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        var copy = new AbyssRecord();
        if (_record != null)
        {
            copy.LoadActs(_record.ActsArray());
            copy.LoadBlessings(_record.BlessingsArray());
            copy.LoadShadows(_record.ShadowsArray());
        }
        _record = copy;
        _moonCounts = new Dictionary<Player, int>();
        _heraldDone = new HashSet<Creature>();
        _riptide = new AbyssTurnLedger<Creature>();
        _elementalMark = new AbyssTurnLedger<Creature>();
    }

    /// <summary>A NEW run starts with nothing taken. The Custom screen keeps
    /// its tickbox's instance between runs, so a second Abyss run from the
    /// same screen could otherwise inherit the first one's record.</summary>
    protected override void AfterRunCreated(RunState runState)
    {
        Record.Clear();
    }

    /// <summary>The run's Abyss modifier, or null in every other run.</summary>
    public static SpiralAbyss? In(IRunState? runState) =>
        runState?.Modifiers.OfType<SpiralAbyss>().FirstOrDefault();

    /// <summary>Is Blessing <paramref name="b"/> in force now? A Whole run
    /// Blessing is once taken; a This act one only in the act it was taken in
    /// (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>, pick 1 (a)). Nothing
    /// new is saved: the record already keeps each pick's act, so a run
    /// continued mid-act keeps the act's entries and one continued after the
    /// act has ended has lost them.</summary>
    public bool Has(AbyssBlessing b) =>
        AbyssDurations.Of(b) == AbyssDuration.WholeRun ? Record.Has(b) : Record.HasInForce(b, CurrentAct);

    public bool Has(AbyssShadow s) =>
        AbyssDurations.Of(s) == AbyssDuration.WholeRun ? Record.Has(s) : Record.HasInForce(s, CurrentAct);

    /// <summary>The headless suite's act: a modifier the harness builds has
    /// no run. Null in every game.</summary>
    public int? ActForTests;

    private int CurrentAct => ActForTests ?? RunState.CurrentActIndex;

    /// <summary>The act Blessing <paramref name="b"/> was taken in: the act
    /// its numbers come from (<c>review/active/abyss-act-scaling-2026-10-18.md</c>).
    /// An entry taken early keeps its number.</summary>
    public int ActOf(AbyssBlessing b) => Record.ActTaken(b);

    public int ActOf(AbyssShadow s) => Record.ActTaken(s);

    /// <summary>The Shadows on the enemies now, in the order applied.</summary>
    public IReadOnlyList<AbyssShadow> ShadowsNow => Record.ShadowsInForce(CurrentAct);

    /// <summary>
    /// THE ACT ENDS (the game's act-change hook, which runs once the next act
    /// is entered, never on a reload): every This act entry of the act just
    /// left drops off. The effects stop by themselves (<see cref="Has(AbyssBlessing)"/>
    /// reads the act); this brings each player's display relics into line:
    /// an expired Blessing's relic goes, the Abyss Shadows list is redrawn.
    /// The enemy badges need nothing: they are put on per combat from the
    /// Shadows in force.
    /// </summary>
    public override async Task AfterActEntered()
    {
        foreach (var player in RunState.Players)
        {
            await AbyssDisplay.GrantTo(player, Record, CurrentAct);
        }
    }

    /// <summary>The run's Abyss, found from a creature in it (the reaction
    /// seams have a creature, not a run).</summary>
    internal static SpiralAbyss? Of(Creature? creature) =>
        In(creature?.Player?.RunState ?? creature?.CombatState?.RunState);

    /// <summary>Overflow's factor on a reaction's own damage: 2 for a
    /// reaction a player dealt while Overflow is in force, else 1. Called
    /// from <c>CompanionOverhaulReactions.DamageMultiplier</c>, the one seam
    /// every reaction's damage passes.</summary>
    public static decimal OverflowFactor(Creature? dealer)
    {
        if (dealer == null || dealer.Player == null) return 1m;
        var abyss = Of(dealer);
        if (abyss == null || !abyss.Has(AbyssBlessing.Overflow)) return 1m;
        return AbyssRules.OverflowFactor(dealerIsPlayer: true);
    }

    /// <summary>Wavering Moon: "Whenever you trigger an Elemental Reaction,
    /// deal 3 damage to ALL enemies." Called from
    /// <c>ReactionEffects.Resolve</c>, the single site a reaction resolves.
    /// The damage is element-less, so it reacts with nothing and cannot loop.</summary>
    public static async Task NoteReaction(PlayerChoiceContext choiceContext, Creature target, Creature? dealer)
    {
        if (!AbyssRules.WaveringMoonFires(dealer?.Player != null)) return;
        var abyss = Of(dealer);
        if (abyss == null || !abyss.Has(AbyssBlessing.WaveringMoon)) return;
        if (dealer!.IsDead || dealer.CombatState == null) return;
        var enemies = dealer.CombatState.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        await CreatureCmd.Damage(
            choiceContext, enemies, AbyssNumbers.WaveringMoonDamage(abyss.ActOf(AbyssBlessing.WaveringMoon)),
            ValueProp.Unpowered, dealer);
    }

    // ---- Per-combat scratch, never saved: a combat restarts on reload. ----

    private Dictionary<Player, int> _moonCounts = new();
    private HashSet<Creature> _heraldDone = new();
    // Riptide's and Elemental Mark's "first time each turn" ledgers. Lazily
    // built, so a modifier the headless suite builds uninitialized has them.
    private AbyssTurnLedger<Creature>? _riptide;
    private AbyssTurnLedger<Creature>? _elementalMark;
    private AbyssTurnLedger<Creature> RiptideLedger => _riptide ??= new AbyssTurnLedger<Creature>();
    private AbyssTurnLedger<Creature> ElementalMarkLedger => _elementalMark ??= new AbyssTurnLedger<Creature>();

    private static PlayerChoiceContext NoChoice() => new ThrowingPlayerChoiceContext();

    public override async Task BeforeCombatStart()
    {
        _moonCounts.Clear();
        _heraldDone.Clear();
        RiptideLedger.Clear();
        ElementalMarkLedger.Clear();

        if (Has(AbyssBlessing.Crystallize))
        {
            foreach (var player in RunState.Players)
            {
                var creature = player.Creature;
                if (creature == null || creature.IsDead) continue;
                await CreatureCmd.GainBlock(
                    creature, AbyssNumbers.CrystallizeBlock(ActOf(AbyssBlessing.Crystallize)),
                    ValueProp.Unpowered, null);
            }
        }
    }

    // ---- Shadows that arrive with the room ------------------------------

    public override async Task AfterRoomEntered(AbstractRoom room)
    {
        // Display only: each player's Abyss relics print the numbers of the
        // act each entry was taken in. A reloaded relic comes back with the
        // act 1 text, so every room puts the right one back.
        foreach (var player in RunState.Players) AbyssDisplay.RefreshTexts(player, Record, CurrentAct);

        if (room is not CombatRoom combatRoom) return;
        var enemies = combatRoom.CombatState.Enemies.Where(e => e.IsAlive).ToList();
        var isElite = combatRoom.RoomType == RoomType.Elite;
        var isBoss = combatRoom.RoomType == RoomType.Boss;

        // The badges first (display only, AbyssDisplay): one per Shadow in
        // force on every enemy that starts the fight. A This act Shadow of an
        // earlier act is not in force, so it wears no badge; an elite-only or
        // elite-and-boss Shadow wears none outside its rooms (BadgesFor).
        var inForce = AbyssRules.BadgesFor(ShadowsNow, isElite, isBoss);
        foreach (var enemy in enemies) AbyssDisplay.ShowShadows(enemy, inForce, Record, CurrentAct);
        // The player-side Shadows (Withering, Sheer Cold) badge each player
        // instead, where base powers show; ShadowsToShow picks the side.
        foreach (var player in RunState.Players)
        {
            if (player.Creature is { IsDead: false } body) AbyssDisplay.ShowShadows(body, inForce, Record, CurrentAct);
        }

        // The combat-start powers, where the base game's Oddly Smooth Stone
        // and Philosopher's Stone put theirs.
        if (Has(AbyssShadow.Frenzy) && enemies.Count > 0)
        {
            await PowerCmd.Apply<StrengthPower>(
                NoChoice(), enemies, AbyssNumbers.FrenzyStrength(ActOf(AbyssShadow.Frenzy)), null, null);
        }

        if (Has(AbyssShadow.ThornyGround) && enemies.Count > 0)
        {
            await PowerCmd.Apply<ThornsPower>(
                NoChoice(), enemies, AbyssNumbers.ThornyGroundThorns(ActOf(AbyssShadow.ThornyGround)), null, null);
        }

        var players = RunState.Players
            .Select(p => p.Creature).Where(c => c is { IsDead: false }).Select(c => c!).ToList();
        if (players.Count > 0)
        {
            if (Has(AbyssBlessing.BattleRhythm))
            {
                var rhythmAct = ActOf(AbyssBlessing.BattleRhythm);
                await PowerCmd.Apply<StrengthPower>(
                    NoChoice(), players, AbyssNumbers.BattleRhythmStrength(rhythmAct), null, null);
                await PowerCmd.Apply<DexterityPower>(
                    NoChoice(), players, AbyssNumbers.BattleRhythmDexterity(rhythmAct), null, null);
            }

            if (Has(AbyssShadow.Withering))
            {
                await PowerCmd.Apply<WeakPower>(
                    NoChoice(), players, AbyssNumbers.WitheringWeak, null, null);
            }
        }

        if (Has(AbyssShadow.Herald))
        {
            foreach (var enemy in enemies) await HeraldBuff(enemy);
        }

        if (Has(AbyssShadow.FatuiSkirmishers) && AbyssRules.FatuiRoom(isElite, isBoss))
        {
            await PowerCmd.Apply<PlatingPower>(
                NoChoice(), enemies, AbyssNumbers.FatuiPlating(ActOf(AbyssShadow.FatuiSkirmishers)), null, null);
        }

        if (Has(AbyssShadow.MageShield) && AbyssRules.MageShieldRoom(isElite))
        {
            var element = AbyssElements.ForAct(CurrentAct);
            foreach (var enemy in enemies)
            {
                await AbyssShieldPower.Apply(NoChoice(), enemy, element);
            }
        }
    }

    public override async Task AfterCreatureAddedToCombat(Creature creature)
    {
        // Abyss Herald: "Enemies have 15% more HP" -- a body summoned later is
        // an enemy too. The two elite-entry Shadows are about entering combat,
        // so a summon does not take them.
        if (creature.Side != CombatSide.Enemy) return;
        // A summoned enemy wears the badges too (display only). The
        // combat-start Shadows (Frenzy, Thorny Ground, Bulwark) are about
        // starting the combat, so a summon does not take them.
        AbyssDisplay.ShowShadows(creature, AbyssRules.BadgesFor(ShadowsNow, isElite: false, isBoss: false), Record, CurrentAct);
        if (Has(AbyssShadow.Herald)) await HeraldBuff(creature);
    }

    private async Task HeraldBuff(Creature enemy)
    {
        if (!_heraldDone.Add(enemy)) return;
        var bonus = AbyssRules.HeraldBonus(enemy.MaxHp);
        if (bonus <= 0) return;
        await CreatureCmd.SetMaxHp(enemy, enemy.MaxHp + bonus);
        await CreatureCmd.SetCurrentHp(enemy, enemy.CurrentHp + bonus);
    }

    // ---- Turn boundaries -------------------------------------------------

    public override async Task AfterSideTurnStart(
        CombatSide side, IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side == CombatSide.Player)
        {
            // Bulwark (2026-10-17; the user: "Bulwark looks pretty weak"):
            // each enemy gains Block at the start of every player turn, so
            // it soaks each turn's damage. It was 6 Block once, at combat
            // start, which cleared at the enemies' first turn. 4 / 6 / 8 by
            // the act it was taken in (2026-10-18).
            if (Has(AbyssShadow.Bulwark))
            {
                var block = AbyssNumbers.BulwarkBlock(ActOf(AbyssShadow.Bulwark));
                foreach (var enemy in combatState.Enemies.Where(e => e.IsAlive).ToList())
                {
                    await CreatureCmd.GainBlock(enemy, block, ValueProp.Unpowered, null);
                }
            }
            if (!Has(AbyssBlessing.Resonance)) return;
            foreach (var creature in participants)
            {
                var player = creature.Player;
                if (player?.PlayerCombatState == null) continue;
                if (!AbyssRules.ResonanceApplies(player.PlayerCombatState.TurnNumber)) continue;
                await PlayerCmd.GainEnergy(AbyssNumbers.ResonanceEnergy, player);
            }
            return;
        }

        if (side != CombatSide.Enemy) return;

        if (Has(AbyssBlessing.LeyLine))
        {
            var element = AbyssElements.ForAct(CurrentAct);
            foreach (var enemy in combatState.Enemies.ToList())
            {
                if (!AbyssRules.LeyLineApplies(
                        enemy.Side == CombatSide.Enemy, enemy.IsAlive,
                        AuraCmd.Find(enemy) != null))
                {
                    continue;
                }
                await AuraCmd.Apply(NoChoice(), enemy, element, null, null);
            }
        }

        if (Has(AbyssShadow.Clock) && AbyssRules.ClockApplies(combatState.RoundNumber))
        {
            var alive = combatState.Enemies.Where(e => e.IsAlive).ToList();
            await PowerCmd.Apply<StrengthPower>(
                NoChoice(), alive, AbyssNumbers.ClockStrength(ActOf(AbyssShadow.Clock)), null, null);
        }
    }

    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        // Abyssal Moon counts "in a turn": each player's count starts again
        // when their turn does.
        if (side == CombatSide.Player)
        {
            foreach (var creature in participants)
            {
                if (creature.Player != null) _moonCounts.Remove(creature.Player);
            }
        }
        return Task.CompletedTask;
    }

    /// <summary>Sheer Cold, in the LATE end-of-turn broadcast: strictly after
    /// every end-of-turn effect that can grant Block (Plating, the turn-end
    /// volleys) and after <c>KleeElementalHooks</c> resets the Grass Ring's
    /// HP-loss window in <c>AfterSideTurnEnd</c>, so the 3 HP lands in the
    /// new window every time rather than in whichever one the listener order
    /// happened to pick.</summary>
    public override async Task AfterSideTurnEndLate(
        PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !Has(AbyssShadow.SheerCold)) return;
        foreach (var creature in participants.ToList())
        {
            if (!AbyssRules.SheerColdApplies(creature.Player != null, creature.IsAlive, creature.Block))
            {
                continue;
            }
            await CreatureCmd.Damage(
                choiceContext, creature, AbyssNumbers.SheerColdHpLoss(ActOf(AbyssShadow.SheerCold)),
                ValueProp.Unblockable | ValueProp.Unpowered, null, null, null);
        }
    }

    // ---- Card plays ------------------------------------------------------

    /// <summary>
    /// First Strike: "Your first Attack each combat is played twice."
    ///
    /// SETTLED FROM THE DECOMPILE (sts2.dll, 2026-10-12), because two seats
    /// reported it never doubling. <c>CardModel.OnPlayWrapper</c> calls
    /// <c>GeneratePlayCount</c> -- which runs this hook -- BEFORE its play loop,
    /// and the loop is what appends <c>CombatHistory.CardPlayStarted</c> for
    /// each play (CardModel.cs ~1887 then ~1929). So the play being sized is
    /// never in the history yet, and an empty history means "this is the
    /// first". The history is cleared at every combat's end
    /// (<c>CombatManager.EndCombatInternal</c>), so the count is per combat,
    /// and it is filtered to the card's owner, so in co-op each player's first
    /// Attack doubles. Echo Form counts the same history the same way.
    /// What the seats saw is not this hook: in the first four fights of the
    /// lane 2 godot log Varka's Fury is never his first Attack, and the page's
    /// turn log printed a doubled card as one row with nothing saying it
    /// played twice (it now does: <c>ResolutionLedger</c>'s play count).
    /// </summary>
    public override int ModifyCardPlayCount(CardModel card, Creature? target, int playCount)
    {
        if (!Has(AbyssBlessing.FirstStrike)) return playCount;
        var owner = card.Owner;
        if (owner == null) return playCount;
        var attackAlready = AbyssRules.AttackAlreadyStarted(
            CombatManager.Instance.History.CardPlaysStarted.Select(e =>
                (e.CardPlay.Player, e.CardPlay.IsFirstInSeries,
                 e.CardPlay.Card.Type == CardType.Attack)),
            owner);
        return playCount + AbyssRules.FirstStrikeExtraPlays(card.Type == CardType.Attack, attackAlready);
    }

    /// <summary>The receipt the base game's Throwing Axe gives for the same
    /// effect: the owner's First Strike relic flashes when it doubles a card.
    /// Display only; the game calls this only on a model that changed the
    /// count, and First Strike is the only thing here that does.</summary>
    public override Task AfterModifyingCardPlayCount(CardModel card)
    {
        var relic = card.Owner?.Relics.OfType<AbyssFirstStrikeRelic>().FirstOrDefault();
        relic?.Flash();
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!cardPlay.IsFirstInSeries) return;
        var player = cardPlay.Player;
        var creature = player?.Creature;
        if (creature == null || creature.IsDead || creature.CombatState == null) return;

        if (Has(AbyssBlessing.AbyssalMoon))
        {
            var count = (_moonCounts.TryGetValue(player!, out var c) ? c : 0) + 1;
            _moonCounts[player!] = count;
            if (AbyssRules.AbyssalMoonFires(count))
            {
                await CreatureCmd.Damage(
                    choiceContext, creature.CombatState.HittableEnemies.ToList(),
                    AbyssNumbers.AbyssalMoonDamage(ActOf(AbyssBlessing.AbyssalMoon)), ValueProp.Unpowered, creature);
            }
        }

        if (Has(AbyssBlessing.ElementalBurst)
            && AbyssRules.ElementalBurstFires(cardPlay.Card.Type == CardType.Power, cardPlay.IsFirstInSeries)
            && !creature.IsDead)
        {
            await CreatureCmd.Damage(
                choiceContext, creature.CombatState.HittableEnemies.ToList(),
                AbyssNumbers.ElementalBurstDamage(ActOf(AbyssBlessing.ElementalBurst)), ValueProp.Unpowered, creature);
        }
    }

    public override decimal ModifyHandDraw(Player player, decimal count)
    {
        if (!Has(AbyssBlessing.Resonance) || player.PlayerCombatState == null) return count;
        return AbyssRules.ResonanceApplies(player.PlayerCombatState.TurnNumber)
            ? count + AbyssNumbers.ResonanceDraw
            : count;
    }

    // ---- Damage ------------------------------------------------------------

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer == null) return 0m;
        var delta = 0m;
        if (Has(AbyssBlessing.LeyLine))
        {
            delta += AbyssRules.LeyLineDamageDelta(
                dealer.Side == CombatSide.Enemy, AuraCmd.Find(dealer) != null,
                props.IsPoweredAttack(), amount);
        }
        if (Has(AbyssBlessing.VigorOfTheAbyss))
        {
            delta += AbyssRules.VigorDamageDelta(
                dealer.Player != null, props.IsPoweredAttack(), dealer.CurrentHp, dealer.MaxHp,
                ActOf(AbyssBlessing.VigorOfTheAbyss));
        }
        return delta;
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (!Has(AbyssShadow.ElementalMark) && !Has(AbyssShadow.Riptide)) return;
        if (!AbyssRules.EnemyAttackLanded(
                target.Player != null, dealer?.Side == CombatSide.Enemy,
                props.IsPoweredAttack(), result.UnblockedDamage))
        {
            return;
        }

        var round = target.CombatState?.RoundNumber ?? 0;

        // Elemental Mark (2026-10-18): the first landed hit each turn, per
        // player, so a multi-hit attack adds one Burn, not one per hit.
        if (Has(AbyssShadow.ElementalMark) && !target.IsDead && TakeElementalMark(target, round))
        {
            await CardPileCmd.AddToCombatAndPreview<Burn>(target, PileType.Discard, 1, null);
        }

        // Riptide (2026-10-18): per enemy, its first landed hit each turn,
        // up to the cap of the act it was taken in, per combat.
        if (Has(AbyssShadow.Riptide) && dealer is { IsAlive: true } && TakeRiptide(dealer, round))
        {
            await PowerCmd.Apply<StrengthPower>(
                choiceContext, dealer, AbyssNumbers.RiptideStrength, dealer, null);
        }
    }

    /// <summary>Riptide's decision and its count, together: does this
    /// enemy's landed hit in round <paramref name="round"/> feed it? Counts
    /// it if so. Public so the headless suite drives the real ledger.</summary>
    public bool TakeRiptide(Creature dealer, int round)
    {
        if (!AbyssRules.RiptideFeeds(
                RiptideLedger.CountedThisTurn(dealer, round), RiptideLedger.CountThisCombat(dealer),
                AbyssNumbers.RiptideCap(ActOf(AbyssShadow.Riptide))))
        {
            return false;
        }
        RiptideLedger.Count(dealer, round);
        return true;
    }

    /// <summary>Elemental Mark's decision and its count, on
    /// <see cref="TakeRiptide"/>'s terms, per player.</summary>
    public bool TakeElementalMark(Creature player, int round)
    {
        if (!AbyssRules.ElementalMarkFires(ElementalMarkLedger.CountedThisTurn(player, round))) return false;
        ElementalMarkLedger.Count(player, round);
        return true;
    }

    public override async Task AfterDeath(
        PlayerChoiceContext choiceContext, Creature creature, bool wasRemovalPrevented,
        float deathAnimLength)
    {
        if (!Has(AbyssShadow.Rally) || wasRemovalPrevented) return;
        if (creature.Side != CombatSide.Enemy || creature.CombatState == null) return;
        var others = creature.CombatState.Enemies
            .Where(e => e != creature && e.IsAlive).ToList();
        if (others.Count == 0) return;
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, others, AbyssNumbers.RallyStrength(ActOf(AbyssShadow.Rally)), null, null);
    }

    public override async Task AfterCombatVictory(CombatRoom room)
    {
        // Moonlit Rest (whole run) and Moonlit Spring (this act) stack, each
        // at the number of the act it was taken in.
        var heal = AbyssRules.CombatEndHeal(
            Has(AbyssBlessing.MoonlitRest) ? ActOf(AbyssBlessing.MoonlitRest) : null,
            Has(AbyssBlessing.MoonlitSpring) ? ActOf(AbyssBlessing.MoonlitSpring) : null);
        if (heal <= 0) return;
        foreach (var player in RunState.Players)
        {
            var creature = player.Creature;
            if (creature == null || creature.IsDead) continue;
            await CreatureCmd.Heal(creature, heal);
        }
    }
}
