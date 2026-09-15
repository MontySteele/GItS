using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// ABYSSAL BATHS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/AbyssalBaths.cs` and cross-checked
/// against the frozen harvest (Immerse, Linger, Exit Baths, Abstain).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three vars (2 Max HP, 3
/// unblockable unpowered damage, 10 heal), the same gain-then-damage order in
/// `OnImmerse`, the same `+1` to the damage var after every soak, the same
/// clamp of the Linger counter at nine, and the same death-warning page
/// substituted for the numbered one when the next soak would kill.
///
/// LINGER AND EXIT BATHS LIVE ON `pages.ALL`, AND THAT IS WHY THIS EVENT WAS
/// PARKED. The INITIAL page offers two options; the face writes four lines,
/// because the wiki lists the pool's later two beside them. Both now pair
/// with full-suffix keys -- `pages.ALL.options.LINGER` and
/// `pages.ALL.options.EXIT_BATHS` -- in the mirror ledger's `options` list, so
/// the lines that were already written land on the options they describe.
///
/// THE NINE LINGER PAGES ARE WRITTEN OUT, NOT BUILT, for
/// <see cref="SlipperyBridgeMirror"/>'s reason: the base event interpolates
/// `$"ABYSSAL_BATHS.pages.LINGER{LingerCount}.description"`, which leaves the
/// index a stub and would leave this mirror carrying the fragment `LINGER`.
/// </summary>
public abstract class AbyssalBathsMirror : TeyvatEventMirror
{
    /// <summary>The nine numbered soak pages, one literal each. The counter is
    /// clamped at nine, so a tenth soak re-reads the ninth page -- the base
    /// event's own behaviour, and the reason there is no tenth row.</summary>
    private string[] LingerPages => new[]
    {
        "LINGER1.description",
        "LINGER2.description",
        "LINGER3.description",
        "LINGER4.description",
        "LINGER5.description",
        "LINGER6.description",
        "LINGER7.description",
        "LINGER8.description",
        "LINGER9.description",
    };

    private int _lingerCount;

    private int LingerCount
    {
        get => _lingerCount;
        set
        {
            AssertMutable();
            _lingerCount = value;
        }
    }

    /// <summary>`AbyssalBaths.cs:29-34`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new MaxHpVar(2m),
            new DamageVar(3m, ValueProp.Unblockable | ValueProp.Unpowered),
            new HealVar(10m),
        };

    /// <summary>Two options, in the base event's order, under its names. The
    /// damage annotation is the NET of the soak -- the damage taken less the
    /// Max HP gained -- which is what makes the warning honest.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Immerse, InitialOptionKey("IMMERSE"))
                .ThatDoesDamage((decimal)DynamicVars.Damage.IntValue - DynamicVars.MaxHp.BaseValue),
            new EventOption(this, Abstain, InitialOptionKey("ABSTAIN")),
        };

    /// <summary>`Immerse`: the first soak, then the pool's own two
    /// options.</summary>
    private async Task Immerse()
    {
        await OnImmerse();
        SetEventState(L10NLookup(PageKey("IMMERSE.description")), PoolOptions(
            (decimal)DynamicVars.Damage.IntValue - DynamicVars.MaxHp.BaseValue));
    }

    /// <summary>`Abstain`: the heal, and the end of it.</summary>
    private async Task Abstain()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars.Heal.IntValue);
        SetEventFinished(L10NLookup(PageKey("ABSTAIN.description")));
    }

    /// <summary>
    /// `Linger`: count, soak, and then either the death warning or the
    /// numbered page -- with the same two options underneath either way, so
    /// the only thing the warning changes is what the player is reading.
    /// </summary>
    private async Task Linger()
    {
        LingerCount++;
        if (LingerCount > 9)
        {
            LingerCount = 9;
        }

        await OnImmerse();
        decimal damage = (decimal)DynamicVars.Damage.IntValue - DynamicVars.MaxHp.BaseValue;
        if (WillKillPlayer(damage))
        {
            SetEventState(L10NLookup(PageKey("DEATH_WARNING.description")), PoolOptions(damage));
            return;
        }

        SetEventState(L10NLookup(PageKey(LingerPages[LingerCount - 1])), PoolOptions(damage));
    }

    /// <summary>The two options every page in the pool carries, under the
    /// base event's `pages.ALL` keys.</summary>
    private IReadOnlyList<EventOption> PoolOptions(decimal damage) =>
        new List<EventOption>
        {
            new EventOption(this, Linger, PageKey("ALL.options.LINGER")).ThatDoesDamage(damage),
            new EventOption(this, ExitBaths, PageKey("ALL.options.EXIT_BATHS")),
        };

    /// <summary>The base event's test: CURRENT hp, and `&lt;=` rather than
    /// `&lt;`.</summary>
    private bool WillKillPlayer(decimal damage) =>
        (decimal)Owner.Creature.CurrentHp <= damage;

    /// <summary>`ExitBaths`: its own page, and nothing paid for it.</summary>
    private Task ExitBaths()
    {
        SetEventFinished(L10NLookup(PageKey("EXIT_BATHS.description")));
        return Task.CompletedTask;
    }

    /// <summary>One soak: the Max HP first, then the damage, then the price of
    /// the next one. The order is the base event's and it is load-bearing --
    /// the gain is what keeps the first soaks survivable.</summary>
    private async Task OnImmerse()
    {
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars.MaxHp.BaseValue);
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), Owner.Creature,
            DynamicVars.Damage, null, null, null);
        DynamicVars.Damage.BaseValue += 1m;
    }
}
