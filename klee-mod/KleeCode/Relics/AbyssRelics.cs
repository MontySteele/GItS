using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Abyss;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace KleeMod.Relics;

/// <summary>
/// THE SPIRAL ABYSS'S DISPLAY RELICS (2026-10-12): what an Abyss run has taken,
/// shown in the relic bar. DISPLAY ONLY -- every effect stays in the
/// <see cref="SpiralAbyss"/> modifier's hooks, so these override no hook at all
/// and nothing can fire twice. <c>SpiralAbyssDisplayTests</c> holds every
/// override here to a display-only allowlist.
///
/// NEVER OFFERED, NEVER TRADED. Each is a member of the base game's
/// <c>DeprecatedRelicPool</c> (registered in <see cref="AbyssDisplay.RegisterPool"/>;
/// a poolless relic throws at <c>RelicModel.Pool</c>) and of no other pool.
/// Rewards and shops draw from <c>SharedRelicPool</c> plus the character's own
/// pool and only at Common/Uncommon/Rare/Shop (<c>RelicGrabBag.Populate</c>);
/// these are <see cref="RelicRarity.None"/>, the rarity the base game gives its
/// two never-rolled relics (Circlet, DeprecatedRelic), which also keeps them out
/// of the compendium's rarity shelves. <c>RelicModel.IsTradable</c> is what the
/// base game's only relic-taking events read (Ranwid, the Relic Trader), and
/// it is false for a relic that reports an upon-pickup effect -- the game's own
/// "this cannot be handed back" flag -- so these report one.
/// </summary>
public abstract class AbyssDisplayRelic : CustomRelicModel
{
    protected AbyssDisplayRelic() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.None;

    /// <summary>Makes <c>IsTradable</c> false (see the class note). The relic
    /// has no pickup effect of its own: the Blessing's effect, Fateful
    /// Fortune's Max HP included, is the modifier's.</summary>
    public override bool HasUponPickupEffect => true;

    public override bool IsAllowedInShops => false;

    public override bool IsAllowed(IRunState runState) => false;

    public override bool ShouldFlashOnPlayer => false;

    /// <summary>The pck-relative icon, a literal per subclass so
    /// <c>validate.ps1</c> S12 can see it.</summary>
    protected abstract string IconFile { get; }

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath => KleePck.Path(IconFile) ?? base.PackedIconPath;

    protected override string BigIconPath => KleePck.Path(IconFile) ?? base.BigIconPath;
}

/// <summary>One per Blessing: the Blessing's name and its text, word for word
/// <see cref="AbyssText"/>'s.</summary>
public abstract class AbyssBlessingRelic : AbyssDisplayRelic
{
    public abstract AbyssBlessing Blessing { get; }

    protected abstract string Title { get; }

    public override List<(string, string)>? Localization => new()
    {
        ("title", Title),
        ("description", AbyssText.Text(Blessing)),
    };
}

public sealed class AbyssLeyLineRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.LeyLine;
    protected override string Title => "The Ley Line";
    protected override string IconFile => "abyss/relics/ley_line.png";
}

public sealed class AbyssAbyssalMoonRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.AbyssalMoon;
    protected override string Title => "Abyssal Moon";
    protected override string IconFile => "abyss/relics/abyssal_moon.png";
}

public sealed class AbyssMoonlitRestRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.MoonlitRest;
    protected override string Title => "Moonlit Rest";
    protected override string IconFile => "abyss/relics/moonlit_rest.png";
}

public sealed class AbyssFirstStrikeRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.FirstStrike;
    protected override string Title => "First Strike";
    protected override string IconFile => "abyss/relics/first_strike.png";
}

public sealed class AbyssElementalBurstRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.ElementalBurst;
    protected override string Title => "Elemental Burst";
    protected override string IconFile => "abyss/relics/elemental_burst.png";
}

public sealed class AbyssResonanceRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.Resonance;
    protected override string Title => "Resonance";
    protected override string IconFile => "abyss/relics/resonance.png";
}

public sealed class AbyssCrystallizeRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.Crystallize;
    // Jade Shield, not Crystallize (a reaction's name). The class name is
    // the model id a saved run holds, and the icon is the same shield, so
    // both stay.
    protected override string Title => "Jade Shield";
    protected override string IconFile => "abyss/relics/crystallize.png";
}

public sealed class AbyssFatefulFortuneRelic : AbyssBlessingRelic
{
    public override AbyssBlessing Blessing => AbyssBlessing.FatefulFortune;
    protected override string Title => "Fateful Fortune";
    protected override string IconFile => "abyss/relics/fateful_fortune.png";
}

/// <summary>
/// "ABYSS SHADOWS": one relic on every player, granted with the run's first
/// Shadow, whose text lists the Shadows in force. The list is a
/// <see cref="StringVar"/> -- the base game's own way to put run state in a
/// relic's text (Archaic Tooth) -- fed from a saved copy of the record's
/// Shadows, so a reload prints the same list without asking the run.
/// </summary>
public sealed class AbyssShadowsRelic : AbyssDisplayRelic
{
    public const string ShadowsVar = "Shadows";

    private int[] _shadows = Array.Empty<int>();

    protected override string IconFile => "abyss/relics/abyss_shadows.png";

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Abyss Shadows"),
        ("description", "The enemies carry these Shadows:\n{" + ShadowsVar + "}"),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new StringVar(ShadowsVar, AbyssDisplay.ShadowsText(Array.Empty<AbyssShadow>())),
    };

    /// <summary>The Shadows this relic lists, as the record stores them. Saved
    /// with the relic; the setter refreshes the printed list.</summary>
    [SavedProperty]
    public int[] SpiralAbyssShadowsShown
    {
        get => _shadows ?? Array.Empty<int>();
        set
        {
            _shadows = value ?? Array.Empty<int>();
            if (IsMutable) RefreshText();
        }
    }

    public IReadOnlyList<AbyssShadow> Shadows => SpiralAbyssShadowsShown.Select(s => (AbyssShadow)s).ToList();

    public void SetShadows(IEnumerable<AbyssShadow> shadows) =>
        SpiralAbyssShadowsShown = shadows.Where(s => s != AbyssShadow.None).Select(s => (int)s).ToArray();

    private void RefreshText()
    {
        if (DynamicVars[ShadowsVar] is StringVar text)
        {
            text.StringValue = AbyssDisplay.ShadowsText(Shadows);
        }
    }
}
