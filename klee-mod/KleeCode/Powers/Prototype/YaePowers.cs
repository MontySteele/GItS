using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ---------------------------------------------------------------------------
//  THE SHRINE'S BADGES: one per Sakura standing, oldest first.
// ---------------------------------------------------------------------------

/// <summary>
/// ONE SAKURA ON HER STATUS BAR (the paper's display: "two numbers per
/// Sakura on the display (Level and turns left)"). The icon's number is the
/// Sakura's LEVEL; the tooltip names its KIND (review r3), the Level and the
/// Level it was planted at (so the rest is what plants, Grove and the cards
/// added since), what its action does now, the Annotation it carries and
/// the turns it has left, and the seat page reads them off that sentence.
/// Badge 1 is the oldest, the one that acts first and withers first. A view
/// of <see cref="YaeShrineLedger"/>, kept in step by <see cref="SakuraBadge.Sync"/>.
/// </summary>
public abstract class SakuraBadgePower : PowerModel, ILocalizationProvider
{
    /// <summary>0 for the oldest Sakura.</summary>
    public abstract int Slot { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", $"Sakura {Slot + 1}"),
        ("description",
            "A [gold]Sakura[/gold] beside you. It acts at the end of your "
          + "turn."),
        // The kind is a number (YaeSakuraKind) read by the game's own
        // `cond:` formatter, the shape SHRINK_POWER's shipped row uses; the
        // pool to 78 (pick 2 (a)) lets Annotations coexist, so each is its
        // own 0/1 flag, in Red Ink, Deadline Extension, Fox Fire order. No
        // placeholder sits inside a branch.
        ("smartDescription",
            "{Kind:cond:==1?Foxfire Sakura|==2?Kitsune Sakura|Sakura}, "
          + "Level {Level}, planted at {Planted}. "
          + "{Kind:cond:==1?Hits ALL enemies for |==2?You gain |Strikes a random enemy for }"
          + "{Strike}{Kind:cond:==2? [gold]Block[/gold].| [gold]Electro[/gold] damage.}"
          + $"{{RedInk:cond:==1? [gold]Red Ink[/gold]: +{YaeLaw.RedInkAmount}.|}}"
          + "{Deadline:cond:==1? [gold]Deadline Extension[/gold]: no wither.|}"
          + $"{{FoxFire:cond:==1? [gold]Fox Fire[/gold]: +{YaeLaw.FoxFireDamage} to a random enemy.|}}"
          + " Turns left: {Turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Level", 1m), new("Turns", 3m), new("Strike", 3m),
        new("RedInk", 0m), new("Deadline", 0m), new("FoxFire", 0m),
        new("Kind", 0m), new("Planted", 1m),
    };

    private YaeSakura? Mine()
    {
        if (!IsMutable || Owner == null) return null;
        var standing = YaeShrineLedger.For(Owner).Standing;
        return Slot < standing.Count ? standing[Slot] : null;
    }

    /// <summary>The Sakura's Level.</summary>
    public override int DisplayAmount => Mine()?.Level ?? Amount;

    /// <summary>Copy the ledger into the tooltip and redraw the icon.</summary>
    internal void Refresh()
    {
        var sakura = Mine();
        if (sakura == null || Owner == null) return;
        DynamicVars["Level"].BaseValue = sakura.Level;
        DynamicVars["Turns"].BaseValue = sakura.TurnsLeft;
        DynamicVars["Strike"].BaseValue = YaeShrine.Size(Owner, sakura);
        DynamicVars["RedInk"].BaseValue = sakura.Has(YaeAnnotation.RedInk) ? 1 : 0;
        DynamicVars["Deadline"].BaseValue = sakura.Has(YaeAnnotation.DeadlineExtension) ? 1 : 0;
        DynamicVars["FoxFire"].BaseValue = sakura.Has(YaeAnnotation.FoxFire) ? 1 : 0;
        DynamicVars["Kind"].BaseValue = (int)sakura.Kind;
        DynamicVars["Planted"].BaseValue = sakura.PlantedLevel;
        InvokeDisplayAmountChanged();
    }
}

public sealed class SakuraFirstPower : SakuraBadgePower
{
    public override int Slot => 0;
}

public sealed class SakuraSecondPower : SakuraBadgePower
{
    public override int Slot => 1;
}

public sealed class SakuraThirdPower : SakuraBadgePower
{
    public override int Slot => 2;
}

// Sakura Channeling (2026-10-14): "You can have 2 more Sakura", per copy,
// so the shrine can hold 5, 7, 9 ... One badge per slot up to nine (three
// copies); a tenth Sakura still stands and strikes, it shows no badge.

public sealed class SakuraFourthPower : SakuraBadgePower
{
    public override int Slot => 3;
}

public sealed class SakuraFifthPower : SakuraBadgePower
{
    public override int Slot => 4;
}

public sealed class SakuraSixthPower : SakuraBadgePower
{
    public override int Slot => 5;
}

public sealed class SakuraSeventhPower : SakuraBadgePower
{
    public override int Slot => 6;
}

public sealed class SakuraEighthPower : SakuraBadgePower
{
    public override int Slot => 7;
}

public sealed class SakuraNinthPower : SakuraBadgePower
{
    public override int Slot => 8;
}

/// <summary>Keeps one badge per standing Sakura.</summary>
public static class SakuraBadge
{
    /// <summary>The badges <paramref name="count"/> Sakura want, oldest
    /// first. PURE.</summary>
    public static IReadOnlyList<System.Type> Wanted(int count) =>
        Slots.Take(System.Math.Max(0, System.Math.Min(Slots.Length, count)))
            .ToList();

    /// <summary>Every badge, oldest Sakura first (nine: three Sakura
    /// Channelings' worth).</summary>
    public static readonly System.Type[] Slots =
    {
        typeof(SakuraFirstPower), typeof(SakuraSecondPower), typeof(SakuraThirdPower),
        typeof(SakuraFourthPower), typeof(SakuraFifthPower), typeof(SakuraSixthPower),
        typeof(SakuraSeventhPower), typeof(SakuraEighthPower), typeof(SakuraNinthPower),
    };

    /// <summary>Add or remove badges to match the ledger, then refresh them.
    /// Headless (no combat) it does nothing. (The Rite badge left with the
    /// Rite, shrine r2, 2026-10-14.)</summary>
    public static async Task Sync(PlayerChoiceContext choiceContext, Creature yae)
    {
        if (yae.CombatState == null || !YaeShrine.Live(yae)) return;
        var wanted = Wanted(YaeShrineLedger.For(yae).Count);
        foreach (var stale in yae.Powers.OfType<SakuraBadgePower>()
                     .Where(b => !wanted.Contains(b.GetType())).ToList())
        {
            await PowerCmd.Remove(stale);
        }
        foreach (var type in wanted)
        {
            if (yae.Powers.Any(p => p.GetType() == type)) continue;
            await Apply(choiceContext, yae, type);
        }
        foreach (var badge in yae.Powers.OfType<SakuraBadgePower>())
        {
            badge.Refresh();
        }
    }

    private static Task Apply(PlayerChoiceContext choiceContext, Creature yae, System.Type type)
    {
        if (type == typeof(SakuraFirstPower))
            return PowerCmd.Apply<SakuraFirstPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraSecondPower))
            return PowerCmd.Apply<SakuraSecondPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraThirdPower))
            return PowerCmd.Apply<SakuraThirdPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraFourthPower))
            return PowerCmd.Apply<SakuraFourthPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraFifthPower))
            return PowerCmd.Apply<SakuraFifthPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraSixthPower))
            return PowerCmd.Apply<SakuraSixthPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraSeventhPower))
            return PowerCmd.Apply<SakuraSeventhPower>(choiceContext, yae, 1, yae, null, silent: true);
        if (type == typeof(SakuraEighthPower))
            return PowerCmd.Apply<SakuraEighthPower>(choiceContext, yae, 1, yae, null, silent: true);
        return PowerCmd.Apply<SakuraNinthPower>(choiceContext, yae, 1, yae, null, silent: true);
    }
}

/// <summary>Foxfire Lure's mark on the enemy her Sakura strike this turn.
/// Display only: the ledger's <see cref="YaeShrineLedger.Lure"/> is the rule.
/// Cleared at her next turn start.</summary>
public sealed class FoxfireLurePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Foxfire Lure"),
        ("description",
            "This turn, Yae's striking [gold]Sakura[/gold] strike this enemy."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>Move the mark onto <paramref name="target"/>.</summary>
    internal static async Task Mark(PlayerChoiceContext choiceContext,
                                    Creature yae, Creature target)
    {
        await ClearAll(yae);
        await PowerCmd.Apply<FoxfireLurePower>(choiceContext, target, 1, yae, null);
    }

    /// <summary>Take every mark off the board.</summary>
    internal static async Task ClearAll(Creature yae)
    {
        var enemies = yae.CombatState?.Enemies.ToList();
        if (enemies == null) return;
        foreach (var enemy in enemies)
        {
            foreach (var mark in enemy.Powers.OfType<FoxfireLurePower>().ToList())
            {
                await PowerCmd.Remove(mark);
            }
        }
    }
}

// ---------------------------------------------------------------------------
//  HER CARDS' POWERS (`apply_power`, target self). Sim twins by name in
//  tier0/engine/yae_shrine.py.
// ---------------------------------------------------------------------------

/// <summary>Sakura Grove (shrine r2, ruled 2026-10-14): "At the start of
/// your turn, each Sakura gains a Level." Paid by
/// <see cref="YaeShrine.TurnStart"/>, one Level per stack.</summary>
public sealed class SakuraGrovePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Grove"),
        ("description",
            "At the start of your turn, each [gold]Sakura[/gold] gains "
          + "[blue]{Amount}[/blue] Level."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>Edict of Cleansing: "Your Sakura strikes deal 3 [5] more to an
/// enemy that is Weak or has a Pyro, Hydro or Cryo aura." Damage strikes
/// only.</summary>
public sealed class EdictOfCleansingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Edict of Cleansing"),
        ("description",
            "Your [gold]Sakura[/gold] strikes deal [blue]{Amount}[/blue] "
          + "additional damage to an enemy that is [gold]Weak[/gold] or has a "
          + "[gold]Pyro[/gold], [gold]Hydro[/gold] or [gold]Cryo[/gold] aura."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Serialization (Yae review r6, item 1): "Whenever you Edit a
/// card, gain 3 [4] Block." (was: whenever you play an Annotated card).
/// Paid on the same events the per-combat Edit count records
/// (<see cref="YaeShrineLedger.Edits"/>): each card in hand an Edit or
/// Reborn Annotates, each Sakura an "Edit your ... Sakura" card Annotates.
/// A Publish is not an Edit. Unpowered (the sim's `_block`, the Powers'
/// door).</summary>
public sealed class SerializationPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Serialization"),
        ("description",
            "Whenever you [gold]Edit[/gold] a card, gain "
          + "[blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Pay <paramref name="edits"/> Edits' Block.</summary>
    internal static async Task Pay(Creature yae, int edits)
    {
        var per = yae.GetPowerAmount<SerializationPower>();
        if (per <= 0 || edits <= 0) return;
        yae.Powers.OfType<SerializationPower>().FirstOrDefault()?.Flash();
        await CreatureCmd.GainBlock(yae, per * edits, ValueProp.Unpowered, null);
    }
}

/// <summary>Fox's Mooncall (Yae review r1, pick 2, ruled 2026-10-14): "Your
/// Sakura are planted 1 Level higher", per copy (two copies plant at Level
/// 3); the pool to 78: an Uncommon at 1 whose upgrade plants 2 Levels
/// higher (amount 2). <see cref="YaeShrine.PlantLevel"/> reads the amount.
/// </summary>
public sealed class FoxsMooncallPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fox's Mooncall"),
        ("description",
            "Your [gold]Sakura[/gold] are planted [blue]{Amount}[/blue] Level "
          + "higher."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Yakan Offering: "At the start of your turn, plant a Sakura."
/// Paid by <see cref="YaeShrine.TurnStart"/>, one plant per stack.</summary>
public sealed class YakanOfferingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Yakan Offering"),
        ("description",
            "At the start of your turn, plant [blue]{Amount}[/blue] "
          + "[gold]Sakura[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>Sakura Channeling, the Rare that bends the 3-Sakura limit
/// (designed by the main session 2026-10-14: [USER] judged Yae "generally
/// underpowered right now"): "You can have 2 more Sakura". Its amount, 2 per
/// copy, is read by <see cref="YaeShrine.MaxSakura"/> for this combat; the
/// full-shrine plant fires at that cap.</summary>
public sealed class SakuraChannelingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Channeling"),
        ("description",
            "You can have [blue]{Amount}[/blue] more [gold]Sakura[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Serial Novel (review r3, sec.3, ruled 2026-10-14): "At the
/// start of your turn, put a random Annotated card from your Discard Pile
/// into your hand." One card per stack, paid by
/// <see cref="YaeShrine.TurnStart"/> after the draw.</summary>
public sealed class SerialNovelPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Serial Novel"),
        ("description",
            "At the start of your turn, put [blue]{Amount}[/blue] random "
          + "[gold]Annotated[/gold] card from your [gold]Discard Pile[/gold] "
          + "into your [gold]Hand[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>Editor-in-Chief: "Whenever you play an Annotated card, a Sakura
/// strikes." Paid by <see cref="YaeShrine.AfterCardPlayed"/>, one strike per
/// stack.</summary>
public sealed class EditorInChiefPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Editor-in-Chief"),
        ("description",
            "Whenever you play an [gold]Annotated[/gold] card, a "
          + "[gold]Sakura[/gold] strikes."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

// ---------------------------------------------------------------------------
//  THE POOL TO 78 (review/active/yae-pool-to-78-2026-10-15.md, ruled
//  2026-10-15, all picks (a)). Sim twins by name in
//  tier0/engine/yae_shrine.py.
// ---------------------------------------------------------------------------

/// <summary>Scattered Blossoms: "Whenever a Sakura withers, draw 1 card."
/// Paid by <see cref="YaeShrine.Withered"/>, one card per stack per Sakura
/// that withered.</summary>
public sealed class EnlightenedBlessingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Scattered Blossoms"),
        ("description",
            "Whenever a [gold]Sakura[/gold] withers, draw [blue]{Amount}[/blue] "
          + "{Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>Saiguu's Lesson: "Whenever you apply Weak to an enemy, a Sakura
/// strikes it." Each copy strikes once per enemy the Weak lands on
/// (<see cref="YaeShrine.OnWeakApplied"/>): the highest-Level Sakura that
/// strikes, one hit on that enemy.</summary>
public sealed class SaiguusLessonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Saiguu's Lesson"),
        ("description",
            "Whenever you apply [gold]Weak[/gold] to an enemy, a "
          + "[gold]Sakura[/gold] strikes it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does this change pay? Weak, gained, on a living enemy, put
    /// there by <paramref name="owner"/>. PURE.</summary>
    public static bool Pays(PowerModel? power, decimal amount,
                            Creature? applier, Creature? owner) =>
        power is MegaCrit.Sts2.Core.Models.Powers.WeakPower
        && amount > 0m
        && owner != null && applier == owner
        && power.Owner is { IsEnemy: true, IsDead: false };

    public override async Task AfterPowerAmountChanged(
        PlayerChoiceContext choiceContext, PowerModel power, decimal amount,
        Creature? applier, CardModel? cardSource)
    {
        if (Owner == null || Amount <= 0 || !Pays(power, amount, applier, Owner)) return;
        if (!YaeShrine.Live(Owner)) return;
        Flash();
        await YaeShrine.OnWeakApplied(choiceContext, Owner, power.Owner!, Amount);
    }
}

/// <summary>The Shrine's Sacred Shade: "At the end of your turn, gain 2 [3]
/// Block for each Sakura." Paid by <see cref="YaeShrine.TurnEnd"/>, before
/// the Sakura act.</summary>
public sealed class SacredShadePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Shrine's Sacred Shade"),
        ("description",
            "At the end of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold] for each [gold]Sakura[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>
/// Editorial Priority: "The first Annotated card you play each turn costs
/// 0." The base game's FreeSkillPower shape: the cost hook answers 0 for an
/// Annotated card in hand (or being played) while this turn's first has not
/// been played, and the first Annotated card played spends it
/// (<see cref="YaeShrineLedger.PriorityUsed"/>, cleared at her turn start).
/// One free card a turn however many copies.
/// </summary>
public sealed class EditorialPriorityPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Editorial Priority"),
        ("description",
            "The first [gold]Annotated[/gold] card you play each turn costs 0."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does the power free this card now? PURE over its facts.
    /// </summary>
    public static bool Frees(bool annotated, bool inHandOrPlay, bool used) =>
        annotated && inHandOrPlay && !used;

    private bool Used => Owner != null && YaeShrineLedger.For(Owner).PriorityUsed;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (Owner == null || card.Owner?.Creature != Owner) return false;
        var pile = card.Pile?.Type;
        if (!Frees(YaeEditing.IsAnnotated(card),
                   pile == PileType.Hand || pile == PileType.Play, Used))
        {
            return false;
        }
        modifiedCost = 0m;
        return true;
    }

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (Owner == null || cardPlay.Card?.Owner?.Creature != Owner) return Task.CompletedTask;
        if (!YaeEditing.IsAnnotated(cardPlay.Card)) return Task.CompletedTask;
        var ledger = YaeShrineLedger.For(Owner);
        if (!ledger.PriorityUsed)
        {
            ledger.PriorityUsed = true;
            Flash();
        }
        return Task.CompletedTask;
    }
}

/// <summary>Stellar Conduct (the proposal's parked nod, any reaction):
/// "Whenever a Sakura's strike triggers an Elemental Reaction, it strikes
/// again." Paid inside the Sakura's hit (<c>YaeShrine.Hit</c>), once per
/// stack; a strike again never strikes again.</summary>
public sealed class StellarConductPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stellar Conduct"),
        ("description",
            "Whenever a [gold]Sakura[/gold]'s strike triggers an "
          + "[gold]Elemental Reaction[/gold], it strikes again."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal void Pulse() => Flash();
}

/// <summary>Hunting Gaze (the refill,
/// <c>review/active/yae-refill-2026-10-16.md</c>): "Your Sakura strike the
/// last enemy you attacked, while it lives." Read where a strike would pick
/// a random enemy (<c>YaeShrine.Aim</c>): an aimed strike, the Lure and a
/// Foxfire Sakura's hit on ALL are unchanged; with no living target it
/// falls back to random. Copies do not stack.</summary>
public sealed class HuntingGazePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Hunting Gaze"),
        ("description",
            "Your [gold]Sakura[/gold] strike the last enemy you attacked, "
          + "while it lives."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    internal void Pulse() => Flash();
}

/// <summary>Eternity: "Your Sakura no longer wither when their turns run
/// out." While she has it no timer ticks (<see cref="YaeShrineLedger.Tick"/>);
/// a Sakura still withers to Fallen Petals, Replanting, Daisesshou or a
/// full-shrine plant of another kind.</summary>
public sealed class EternityPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Eternity"),
        ("description",
            "Your [gold]Sakura[/gold] no longer wither when their turns run "
          + "out."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Yae Publishing House (the Yae pass, 2026-10-16, her Dusty Tome
/// Ancient): "Your Edits write their Annotation twice." Read by
/// <see cref="YaeEditing.WriteTimes"/> at each Edit of a card: the temporary
/// slot holds two layers, which add up. On a Sakura twice is once (its
/// Annotations are distinct), so Deadline Extension twice is once. Copies do
/// not stack.</summary>
public sealed class YaePublishingHousePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Yae Publishing House"),
        ("description",
            "Your [gold]Edits[/gold] write their Annotation twice."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}
