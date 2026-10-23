using System.Collections.Generic;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Abyss;

/// <summary>
/// THE SHADOW BADGES (2026-10-12): in an Abyss combat every enemy wears one
/// badge per Shadow in force, whose tooltip is the Shadow's text. DISPLAY
/// ONLY: the Shadow's effect is the <see cref="SpiralAbyss"/> modifier's hook,
/// and this power overrides no hook, so it changes nothing by being there.
///
/// PUT ON QUIETLY. <see cref="AbyssDisplay.ShowShadows"/> attaches it with
/// <c>PowerModel.ApplyInternal</c> rather than <c>PowerCmd.Apply</c>, so no
/// power-applied hook, no Artifact check and no combat-history row sees it: a
/// listener that reacts to an enemy gaining a power never meets a badge.
///
/// <see cref="PowerStackType.Single"/>: the amount is hidden and always 1.
/// </summary>
public abstract class AbyssShadowPower : PowerModel, ILocalizationProvider
{
    public abstract AbyssShadow Shadow { get; }

    /// <summary>The pck-relative icon, a literal per subclass so
    /// <c>validate.ps1</c> S12 can see it (read by <c>KleePowerIcons</c>).</summary>
    public abstract string IconFile { get; }

    /// <summary>The badge's text, in a <see cref="StringVar"/> so it can
    /// print the number of the act the Shadow was taken in
    /// (<c>review/active/abyss-act-scaling-2026-10-18.md</c>). The plain
    /// description is the act 1 text, for a badge no combat has set.</summary>
    public const string TextVar = "Text";

    public List<(string, string)>? Localization => new()
    {
        ("title", AbyssText.NameEnglish(Shadow)),
        ("description", AbyssText.English(Shadow, AbyssText.NoAct)),
        ("smartDescription", "{" + TextVar + "}"),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new StringVar(TextVar, AbyssText.Text(Shadow, AbyssText.NoAct)),
    };

    /// <summary>The text this badge prints now.</summary>
    public string ShownText => DynamicVars[TextVar] is StringVar text ? text.StringValue : "";

    /// <summary>Print the text for act <paramref name="act"/>, the act the
    /// Shadow was taken in. Display only. <paramref name="elementAct"/> is
    /// the act being played, whose element Abyss Mage Shield names.</summary>
    public void ShowAct(int act, int? elementAct = null)
    {
        if (DynamicVars[TextVar] is StringVar text) text.StringValue = AbyssText.Text(Shadow, act, elementAct);
    }

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

public sealed class AbyssClockShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Clock;
    public override string IconFile => "abyss/powers/shadow_clock.png";
}

public sealed class AbyssMageShieldShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.MageShield;
    public override string IconFile => "abyss/powers/shadow_mage_shield.png";
}

public sealed class AbyssSheerColdShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.SheerCold;
    public override string IconFile => "abyss/powers/shadow_sheer_cold.png";
}

public sealed class AbyssElementalMarkShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.ElementalMark;
    public override string IconFile => "abyss/powers/shadow_elemental_mark.png";
}

public sealed class AbyssHeraldShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Herald;
    public override string IconFile => "abyss/powers/shadow_herald.png";
}

public sealed class AbyssRallyShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Rally;
    public override string IconFile => "abyss/powers/shadow_rally.png";
}

public sealed class AbyssRiptideShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Riptide;
    public override string IconFile => "abyss/powers/shadow_riptide.png";
}

public sealed class AbyssFatuiSkirmishersShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.FatuiSkirmishers;
    public override string IconFile => "abyss/powers/shadow_fatui_skirmishers.png";
}

public sealed class AbyssThornyGroundShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.ThornyGround;
    public override string IconFile => "abyss/powers/shadow_thorny_ground.png";
}

public sealed class AbyssBulwarkShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Bulwark;
    public override string IconFile => "abyss/powers/shadow_bulwark.png";
}

public sealed class AbyssFrenzyShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Frenzy;
    public override string IconFile => "abyss/powers/shadow_frenzy.png";
}

public sealed class AbyssWitheringShadowPower : AbyssShadowPower
{
    public override AbyssShadow Shadow => AbyssShadow.Withering;
    public override string IconFile => "abyss/powers/shadow_withering.png";
}
