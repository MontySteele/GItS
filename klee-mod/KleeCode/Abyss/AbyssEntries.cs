using System;
using System.Collections.Generic;
using KleeMod.Elements;

namespace KleeMod.Abyss;

/// <summary>
/// THE SPIRAL ABYSS MODE's eight Blessings
/// (<c>review/active/spiral-abyss-pools-2026-10-12.md</c> sec.2). The numeric
/// values are what the run save stores, so they never move: a new entry takes
/// a new number.
/// </summary>
public enum AbyssBlessing
{
    None = 0,
    LeyLine = 1,
    AbyssalMoon = 2,
    MoonlitRest = 3,
    FirstStrike = 4,
    ElementalBurst = 5,
    Resonance = 6,
    Crystallize = 7,
    FatefulFortune = 8,
}

/// <summary>The paper's eight Shadows (sec.3), numbered for the save on the
/// same terms as <see cref="AbyssBlessing"/>.</summary>
public enum AbyssShadow
{
    None = 0,
    Clock = 1,
    MageShield = 2,
    SheerCold = 3,
    ElementalMark = 4,
    Herald = 5,
    Rally = 6,
    Riptide = 7,
    FatuiSkirmishers = 8,
}

/// <summary>Every number the paper prints, in one place. First guesses,
/// tuned by play (paper sec.1).</summary>
public static class AbyssNumbers
{
    public const int LeyLineDamageReduction = 1;
    public const int AbyssalMoonEvery = 3;
    public const int AbyssalMoonDamage = 4;
    public const int MoonlitRestHeal = 4;
    public const int ElementalBurstDamage = 6;
    public const int ResonanceEnergy = 1;
    public const int ResonanceDraw = 1;
    public const int ResonanceTurn = 1;
    public const int CrystallizeBlock = 8;
    public const int FatefulFortuneMaxHp = 12;

    public const int ClockFromRound = 5;
    public const int ClockStrength = 2;
    public const int MageShieldHits = 8;
    public const int MageShieldPerHit = 1;
    public const int MageShieldPerReaction = 3;
    public const int SheerColdHpLoss = 3;
    public const decimal HeraldHpBonus = 0.15m;
    public const int RallyStrength = 2;
    public const int RiptideStrength = 1;
    public const int FatuiPlating = 3;
}

/// <summary>The player-facing names and texts, word for word the paper's.</summary>
public static class AbyssText
{
    public static string Name(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine => "The Ley Line",
        AbyssBlessing.AbyssalMoon => "Abyssal Moon",
        AbyssBlessing.MoonlitRest => "Moonlit Rest",
        AbyssBlessing.FirstStrike => "First Strike",
        AbyssBlessing.ElementalBurst => "Elemental Burst",
        AbyssBlessing.Resonance => "Resonance",
        // Shown as Jade Shield (seat round, 2026-10-12): "Crystallize" is a
        // reaction's name, and the page glossed the reaction under it. The
        // member name and its save number 7 stay.
        AbyssBlessing.Crystallize => "Jade Shield",
        AbyssBlessing.FatefulFortune => "Fateful Fortune",
        _ => throw new ArgumentOutOfRangeException(nameof(b)),
    };

    public static string Text(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine =>
            "Each enemy turn, every enemy without an aura takes this act's element. "
          + $"An enemy wearing an aura deals {AbyssNumbers.LeyLineDamageReduction} less damage.",
        AbyssBlessing.AbyssalMoon =>
            $"Every third card you play in a turn deals {AbyssNumbers.AbyssalMoonDamage} damage to ALL enemies.",
        AbyssBlessing.MoonlitRest => $"Heal {AbyssNumbers.MoonlitRestHeal} HP at the end of each combat.",
        AbyssBlessing.FirstStrike => "Your first Attack each combat is played twice.",
        AbyssBlessing.ElementalBurst =>
            $"Whenever you play a Power, deal {AbyssNumbers.ElementalBurstDamage} damage to ALL enemies.",
        AbyssBlessing.Resonance =>
            $"On turn {AbyssNumbers.ResonanceTurn} of each combat, gain {AbyssNumbers.ResonanceEnergy} Energy and draw {AbyssNumbers.ResonanceDraw} card.",
        AbyssBlessing.Crystallize => $"Start each combat with {AbyssNumbers.CrystallizeBlock} Block.",
        AbyssBlessing.FatefulFortune => $"Gain {AbyssNumbers.FatefulFortuneMaxHp} Max HP.",
        _ => throw new ArgumentOutOfRangeException(nameof(b)),
    };

    public static string Name(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock => "The Clock",
        AbyssShadow.MageShield => "Abyss Mage Shield",
        AbyssShadow.SheerCold => "Sheer Cold",
        AbyssShadow.ElementalMark => "Elemental Mark",
        AbyssShadow.Herald => "Abyss Herald",
        AbyssShadow.Rally => "Rally",
        AbyssShadow.Riptide => "Riptide",
        AbyssShadow.FatuiSkirmishers => "Fatui Skirmishers",
        _ => throw new ArgumentOutOfRangeException(nameof(s)),
    };

    public static string Text(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock =>
            $"From turn {AbyssNumbers.ClockFromRound}, every enemy gains {AbyssNumbers.ClockStrength} Strength at the start of its turn.",
        AbyssShadow.MageShield =>
            $"Elites enter combat with a shield of this act's element, {AbyssNumbers.MageShieldHits} hits deep, "
          + $"that stops all damage. Each hit removes {AbyssNumbers.MageShieldPerHit}, a reaction removes {AbyssNumbers.MageShieldPerReaction}, and "
          + "the counter element breaks it.",
        AbyssShadow.SheerCold => $"If you end your turn with no Block, lose {AbyssNumbers.SheerColdHpLoss} HP.",
        AbyssShadow.ElementalMark =>
            "Whenever an enemy attack deals you unblocked damage, add a Burn to "
          + "your discard pile.",
        AbyssShadow.Herald => $"Enemies have {(int)(AbyssNumbers.HeraldHpBonus * 100)}% more HP.",
        AbyssShadow.Rally => $"When an enemy dies, every other enemy gains {AbyssNumbers.RallyStrength} Strength.",
        AbyssShadow.Riptide =>
            "Whenever an enemy attack deals you unblocked damage, that enemy gains "
          + $"{AbyssNumbers.RiptideStrength} Strength.",
        AbyssShadow.FatuiSkirmishers =>
            $"Elites and bosses enter combat with {AbyssNumbers.FatuiPlating} Plated Armor.",
        _ => throw new ArgumentOutOfRangeException(nameof(s)),
    };
}

/// <summary>
/// "THIS ACT'S ELEMENT" (The Ley Line, Abyss Mage Shield). The mod has no
/// act-to-element mapping to inherit: the Teyvat frame's act-1 nations are
/// Mondstadt and Liyue, Anemo and Geo, and neither leaves an aura. So the
/// table is the build's own: act 1 Hydro, act 2 Pyro, act 3 Electro -- three
/// aura elements, three Abyss Mage colours. An act past the table takes the
/// last row.
///
/// THE COUNTER ELEMENT is Genshin's shield weakness: a Hydro shield breaks to
/// Cryo, Pyro to Hydro, Electro to Cryo (the Shadowlord's Electro shield is
/// weakest to Cryo, <c>docs/current/dossiers/bosses/dossiers.md</c>), Cryo to
/// Pyro.
/// </summary>
public static class AbyssElements
{
    private static readonly Element[] ByAct = { Element.Hydro, Element.Pyro, Element.Electro };

    public static Element ForAct(int actIndex) =>
        ByAct[Math.Clamp(actIndex, 0, ByAct.Length - 1)];

    public static Element CounterOf(Element shield) => shield switch
    {
        Element.Hydro => Element.Cryo,
        Element.Pyro => Element.Hydro,
        Element.Electro => Element.Cryo,
        Element.Cryo => Element.Pyro,
        _ => Element.None,
    };

    public static IReadOnlyList<Element> Table => ByAct;
}
