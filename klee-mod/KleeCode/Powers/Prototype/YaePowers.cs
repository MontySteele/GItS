using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
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
        // The kind and the Annotation are numbers (YaeSakuraKind,
        // YaeAnnotation) read by the game's own `cond:` formatter, the shape
        // SHRINK_POWER's shipped row uses. No placeholder sits inside a
        // branch.
        ("smartDescription",
            "{Kind:cond:==1?Foxfire Sakura|==2?Kitsune Sakura|Sakura}, "
          + "Level {Level}, planted at {Planted}. "
          + "{Kind:cond:==1?Hits ALL enemies for |==2?You gain |Strikes a random enemy for }"
          + "{Strike}{Kind:cond:==2? [gold]Block[/gold].| [gold]Electro[/gold] damage.}"
          + $"{{Ann:cond:==1? [gold]Red Ink[/gold]: +{YaeLaw.RedInkAmount}.|==3? [gold]Deadline Extension[/gold]: no wither.|==4? [gold]Fox Fire[/gold]: +{YaeLaw.FoxFireDamage} to a random enemy.|}}"
          + " Turns left: {Turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Level", 1m), new("Turns", 3m), new("Strike", 3m),
        new("Ann", 0m), new("Kind", 0m), new("Planted", 1m),
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
        DynamicVars["Ann"].BaseValue = (int)sakura.Annotation;
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
/// 3). <see cref="YaeShrine.PlantLevel"/> reads the amount.</summary>
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
