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
/// Sakura's LEVEL, the number the player raises by planting; the tooltip
/// says the Level, what it strikes for and the strikes it has left, and the
/// seat page reads both off that sentence. Badge 1 is the oldest, the one
/// that strikes first and withers first. A view of
/// <see cref="YaeShrineLedger"/>, kept in step by <see cref="SakuraBadge.Sync"/>.
/// </summary>
public abstract class SakuraBadgePower : PowerModel, ILocalizationProvider
{
    /// <summary>0 for the oldest Sakura.</summary>
    public abstract int Slot { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", $"Sakura {Slot + 1}"),
        ("description",
            "A [gold]Sakura[/gold] beside you. At the end of your turn it "
          + "strikes a random enemy for [gold]Electro[/gold] damage."),
        ("smartDescription",
            "Level {Level}. At the end of your turn it strikes a random enemy "
          + "for {Strike} [gold]Electro[/gold] damage. Strikes left: {Turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Level", 1m), new("Turns", 3m), new("Strike", 3m),
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
        DynamicVars["Strike"].BaseValue = YaeShrineLedger.StrikeDamage(
            sakura.Level, Owner.GetPowerAmount<SakuraGrovePower>(), false, 0);
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

/// <summary>Keeps one badge per standing Sakura.</summary>
public static class SakuraBadge
{
    /// <summary>The badges <paramref name="count"/> Sakura want, oldest
    /// first. PURE.</summary>
    public static IReadOnlyList<System.Type> Wanted(int count) =>
        new[] { typeof(SakuraFirstPower), typeof(SakuraSecondPower), typeof(SakuraThirdPower) }
            .Take(System.Math.Max(0, System.Math.Min(YaeLaw.SakuraCap, count)))
            .ToList();

    /// <summary>Add or remove badges to match the ledger, then refresh them.
    /// Headless (no combat) it does nothing.</summary>
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
            if (type == typeof(SakuraFirstPower))
                await PowerCmd.Apply<SakuraFirstPower>(choiceContext, yae, 1, yae, null, silent: true);
            else if (type == typeof(SakuraSecondPower))
                await PowerCmd.Apply<SakuraSecondPower>(choiceContext, yae, 1, yae, null, silent: true);
            else
                await PowerCmd.Apply<SakuraThirdPower>(choiceContext, yae, 1, yae, null, silent: true);
        }
        foreach (var badge in yae.Powers.OfType<SakuraBadgePower>())
        {
            badge.Refresh();
        }
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
            "This turn, Yae's [gold]Sakura[/gold] strike this enemy."),
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

/// <summary>Sakura Grove: "Your Sakura strike for 1 [2] more."</summary>
public sealed class SakuraGrovePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Grove"),
        ("description",
            "Your [gold]Sakura[/gold] strikes deal [blue]{Amount}[/blue] additional "
          + "damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Edict of Cleansing: "Your Sakura strikes deal 4 [6] more to an
/// enemy with a Pyro, Hydro or Cryo aura."</summary>
public sealed class EdictOfCleansingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Edict of Cleansing"),
        ("description",
            "Your [gold]Sakura[/gold] strikes deal [blue]{Amount}[/blue] "
          + "additional damage to an enemy with a [gold]Pyro[/gold], [gold]Hydro[/gold] or "
          + "[gold]Cryo[/gold] aura."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Serialization: "Whenever you Edit a card, gain 3 [4] Block."
/// Unpowered (the sim's `_block`, the Powers' door).</summary>
public sealed class SerializationPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Serialization"),
        ("description",
            "Whenever you [gold]Edit[/gold] a card, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]."),
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

/// <summary>Fox's Mooncall: "Your Sakura are planted at Level 2 and can reach
/// Level 4." A marker <see cref="YaeShrine.PlantLevel"/> and
/// <see cref="YaeShrine.LevelCap"/> read.</summary>
public sealed class FoxsMooncallPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fox's Mooncall"),
        ("description",
            $"Your [gold]Sakura[/gold] are planted at Level {YaeLaw.MooncallPlantLevel} "
          + $"and can reach Level {YaeLaw.MooncallLevelCap}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
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

/// <summary>Sakura Channeling: "Whenever a Sakura strikes, gain 2 [3]
/// Block." Unpowered.</summary>
public sealed class SakuraChannelingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Channeling"),
        ("description",
            "Whenever a [gold]Sakura[/gold] strikes, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal static async Task Pay(Creature yae)
    {
        var amount = yae.GetPowerAmount<SakuraChannelingPower>();
        if (amount <= 0) return;
        await CreatureCmd.GainBlock(yae, amount, ValueProp.Unpowered, null);
    }
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
