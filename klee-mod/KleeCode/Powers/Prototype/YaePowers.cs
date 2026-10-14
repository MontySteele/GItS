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
/// says the Level, what it does under the shrine's Rite and for how much,
/// the Annotation it carries (ruled 2026-10-14) and the strikes it has
/// left, and the seat page reads them off that sentence. Badge 1 is the oldest, the one
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
          + "strikes under the shrine's [gold]Rite[/gold]."),
        // The Rite and the Annotation are numbers (YaeRite, YaeAnnotation)
        // read by the game's own `cond:` formatter, the shape SHRINK_POWER's
        // shipped row uses.
        ("smartDescription",
            "Level {Level}. At the end of your turn it "
          + "{Rite:cond:==1?gives you|==2?strikes ALL enemies for|==3?draws you|strikes a random enemy for}"
          + " {Strike}"
          + "{Rite:cond:==1? [gold]Block[/gold]|==3? more card next turn| [gold]Electro[/gold] damage}"
          + "."
          + $"{{Ann:cond:==1? [gold]Red Ink[/gold] makes its strike {YaeLaw.RedInkAmount} bigger (not in Offering).|==3? [gold]Deadline Extension[/gold] keeps it from withering.|==4? [gold]Fox Fire[/gold] adds {YaeLaw.FoxFireDamage} [gold]Electro[/gold] damage to a random enemy.|}}"
          + " Strikes left: {Turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Level", 1m), new("Turns", 3m), new("Strike", 3m),
        new("Rite", 0m), new("Ann", 0m),
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
        DynamicVars["Rite"].BaseValue = (int)YaeShrineLedger.For(Owner).Rite;
        DynamicVars["Ann"].BaseValue = (int)sakura.Annotation;
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

    /// <summary>The Rite badge the shrine's Rite wants. PURE.</summary>
    public static System.Type RiteBadge(YaeRite rite) => rite switch
    {
        YaeRite.Warding => typeof(WardingRitePower),
        YaeRite.Wildfire => typeof(WildfireRitePower),
        YaeRite.Offering => typeof(OfferingRitePower),
        _ => typeof(ThunderRitePower),
    };

    /// <summary>Add or remove badges to match the ledger, then refresh them.
    /// The shrine's Rite shows as one badge beside them. Headless (no
    /// combat) it does nothing.</summary>
    public static async Task Sync(PlayerChoiceContext choiceContext, Creature yae)
    {
        if (yae.CombatState == null || !YaeShrine.Live(yae)) return;
        var riteType = RiteBadge(YaeShrineLedger.For(yae).Rite);
        foreach (var stale in yae.Powers.OfType<YaeRiteBadgePower>()
                     .Where(b => b.GetType() != riteType).ToList())
        {
            await PowerCmd.Remove(stale);
        }
        if (!yae.Powers.Any(p => p.GetType() == riteType))
        {
            if (riteType == typeof(WardingRitePower))
                await PowerCmd.Apply<WardingRitePower>(choiceContext, yae, 1, yae, null, silent: true);
            else if (riteType == typeof(WildfireRitePower))
                await PowerCmd.Apply<WildfireRitePower>(choiceContext, yae, 1, yae, null, silent: true);
            else if (riteType == typeof(OfferingRitePower))
                await PowerCmd.Apply<OfferingRitePower>(choiceContext, yae, 1, yae, null, silent: true);
            else
                await PowerCmd.Apply<ThunderRitePower>(choiceContext, yae, 1, yae, null, silent: true);
        }
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
        foreach (var badge in yae.Powers.OfType<YaeRiteBadgePower>())
        {
            badge.Refresh();
        }
    }
}

/// <summary>
/// THE SHRINE'S RITE ON HER STATUS BAR (ruled 2026-10-14): one badge, the
/// current Rite's, titled "Rite: X"; <see cref="SakuraBadge.Sync"/> swaps
/// it. Display only: <see cref="YaeShrineLedger.Rite"/> is the rule.
/// </summary>
public abstract class YaeRiteBadgePower : PowerModel, ILocalizationProvider
{
    public abstract YaeRite Rite { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", "Rite: " + Rite),
        ("description", YaeRiteText.Rule(Rite)),
        // Yae review r1 (Claude, 2026-10-14): with a Sakura standing, the
        // badge adds what they would do now under this Rite, the sum the
        // "Rite: X" cards print (`YaeShrineFace`).
        ("smartDescription", YaeRiteText.Rule(Rite)),
        (LiveKey, YaeRiteText.Rule(Rite) + YaeRiteText.Now(Rite)),
    };

    /// <summary>The smart face read while a Sakura stands.</summary>
    public const string LiveKey = "smartDescriptionLive";

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Total", 0m),
    };

    /// <summary>The live face while the total is above 0 (a Sakura stands).
    /// </summary>
    protected override string SmartDescriptionLocKey =>
        Id.Entry + "." + (DynamicVars["Total"].BaseValue > 0 ? LiveKey : "smartDescription");

    /// <summary>Copy the shrine's total under this Rite into the tooltip.
    /// </summary>
    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        DynamicVars["Total"].BaseValue = YaeShrineFace.Total(Owner, Rite);
        InvokeDisplayAmountChanged();
    }
}

public sealed class ThunderRitePower : YaeRiteBadgePower
{
    public override YaeRite Rite => YaeRite.Thunder;
}

public sealed class WardingRitePower : YaeRiteBadgePower
{
    public override YaeRite Rite => YaeRite.Warding;
}

public sealed class WildfireRitePower : YaeRiteBadgePower
{
    public override YaeRite Rite => YaeRite.Wildfire;
}

public sealed class OfferingRitePower : YaeRiteBadgePower
{
    public override YaeRite Rite => YaeRite.Offering;
}

/// <summary>What each Rite makes a strike do, one sentence (the badges).
/// </summary>
public static class YaeRiteText
{
    /// <summary>The badge's live sentence, the cards' clause as a sentence:
    /// " Your Sakura now: {Total} Block." (Yae review r1, 2026-10-14).
    /// </summary>
    public static string Now(YaeRite rite) =>
        " Your Sakura now: " + YaeShrineFace.RiteAmount(rite, "{Total}") + ".";

    public static string Rule(YaeRite rite) => rite switch
    {
        YaeRite.Warding =>
            $"Each [gold]Sakura[/gold] strike gives you {YaeLaw.SakuraBase} plus "
          + "its Level [gold]Block[/gold].",
        YaeRite.Wildfire =>
            "Each [gold]Sakura[/gold] strike deals its Level "
          + "[gold]Electro[/gold] damage to ALL enemies.",
        YaeRite.Offering =>
            $"Each [gold]Sakura[/gold] strike draws you {YaeLaw.OfferingPerStrike} "
          + "more card at the start of your next turn.",
        _ =>
            $"Each [gold]Sakura[/gold] strike deals {YaeLaw.SakuraBase} plus its "
          + "Level [gold]Electro[/gold] damage to a random enemy.",
    };
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

/// <summary>Sakura Grove: "Your Sakura strike for 2 [3] more in Thunder,
/// Warding and Wildfire."</summary>
public sealed class SakuraGrovePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Grove"),
        ("description",
            "Your [gold]Sakura[/gold] strikes are [blue]{Amount}[/blue] bigger "
          + "in Thunder, Warding and Wildfire."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
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

/// <summary>Sakura Channeling (design axes sec.4, the bend): "Your Sakura
/// also strike as Thunder, whatever the Rite." A marker
/// <see cref="YaeShrine.Strike"/> reads.</summary>
public sealed class SakuraChannelingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sakura Channeling"),
        ("description",
            "Your [gold]Sakura[/gold] also strike as Thunder, whatever the "
          + "[gold]Rite[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Mikage Thunder (batch two): "For the rest of this combat, your
/// Sakura strike for 1 more." Stacks per play; sized as Sakura Grove is
/// (not in Offering).</summary>
public sealed class MikageThunderPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Mikage Thunder"),
        ("description",
            "Your [gold]Sakura[/gold] strikes are [blue]{Amount}[/blue] bigger "
          + "in Thunder, Warding and Wildfire."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Fallen Petals (batch two): "Whenever a Sakura withers, gain 1
/// Energy", paid at the start of her next turn by
/// <see cref="YaeShrine.TurnStart"/> (a Sakura withers at her turn's end).
/// </summary>
public sealed class FallenPetalsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fallen Petals"),
        ("description",
            "Whenever a [gold]Sakura[/gold] withers, gain "
          + "{Amount:energyIcons()} on your next turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Fallen Petals, upgraded: "and draw 1 card".</summary>
public sealed class FallenPetalsPlusPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fallen Petals+"),
        ("description",
            "Whenever a [gold]Sakura[/gold] withers, gain "
          + "{Amount:energyIcons()} and draw [blue]{Amount}[/blue] card on your "
          + "next turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
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
