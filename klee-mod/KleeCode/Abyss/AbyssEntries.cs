using System;
using System.Collections.Generic;
using KleeMod.Elements;

namespace KleeMod.Abyss;

/// <summary>
/// THE SPIRAL ABYSS MODE's Blessings: the first eight
/// (<c>review/active/spiral-abyss-pools-2026-10-12.md</c> sec.2) and round
/// two's six (<c>review/active/abyss-pools-2-2026-10-12.md</c>). The numeric
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
    // Round 2 (review/active/abyss-pools-2-2026-10-12.md): four This act,
    // two Whole run.
    Overflow = 9,
    VigorOfTheAbyss = 10,
    MoonlitSpring = 11,
    BattleRhythm = 12,
    WaveringMoon = 13,
    StarfellDraft = 14,
}

/// <summary>The Shadows: the first paper's eight (sec.3) and round two's
/// four, numbered for the save on the same terms as
/// <see cref="AbyssBlessing"/>.</summary>
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
    // Round 2: three This act, one Whole run.
    ThornyGround = 9,
    Bulwark = 10,
    Frenzy = 11,
    Withering = 12,
}

/// <summary>
/// HOW LONG AN ENTRY LASTS (<c>review/active/abyss-pools-2-2026-10-12.md</c>,
/// pick 1 (a)). Genshin's two layers: the Blessing of the Abyssal Moon lasts
/// the whole cycle, a Ley Line Disorder one floor -- here, one act. A This act
/// entry is in force only in the act it was taken in (the record keeps each
/// pick's act, so nothing new is saved) and drops off when the act ends.
/// </summary>
public enum AbyssDuration
{
    WholeRun = 0,
    ThisAct = 1,
}

public static class AbyssDurations
{
    public static AbyssDuration Of(AbyssBlessing b) => b switch
    {
        AbyssBlessing.Overflow or AbyssBlessing.VigorOfTheAbyss
            or AbyssBlessing.MoonlitSpring or AbyssBlessing.BattleRhythm => AbyssDuration.ThisAct,
        _ => AbyssDuration.WholeRun,
    };

    public static AbyssDuration Of(AbyssShadow s) => s switch
    {
        AbyssShadow.ThornyGround or AbyssShadow.Bulwark
            or AbyssShadow.Frenzy or AbyssShadow.Riptide => AbyssDuration.ThisAct,
        _ => AbyssDuration.WholeRun,
    };

    /// <summary>The card tag and the strip's label.</summary>
    public static string Tag(AbyssDuration d) => d == AbyssDuration.ThisAct ? "This act" : "Whole run";

    /// <summary>Is an entry taken in act <paramref name="takenInAct"/> in
    /// force in act <paramref name="currentAct"/>? Whole run: from its act on.
    /// This act: in its act only.</summary>
    public static bool InForce(AbyssDuration d, int takenInAct, int currentAct) =>
        d == AbyssDuration.WholeRun ? takenInAct <= currentAct : takenInAct == currentAct;
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
    public const int OverflowMultiplier = 2;
    public const int VigorDamage = 3;
    public const int MoonlitSpringHeal = 8;
    public const int BattleRhythmStrength = 1;
    public const int BattleRhythmDexterity = 1;
    public const int WaveringMoonDamage = 3;
    public const int StarfellDraftExtraCards = 1;

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
    public const int ThornyGroundThorns = 2;
    public const int BulwarkBlock = 6;
    public const int FrenzyStrength = 2;
    public const int WitheringWeak = 1;
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
        AbyssBlessing.Overflow => "Overflow",
        AbyssBlessing.VigorOfTheAbyss => "Vigor of the Abyss",
        AbyssBlessing.MoonlitSpring => "Moonlit Spring",
        AbyssBlessing.BattleRhythm => "Battle Rhythm",
        AbyssBlessing.WaveringMoon => "Wavering Moon",
        AbyssBlessing.StarfellDraft => "Starfell Draft",
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
        AbyssBlessing.Overflow => "This act, Elemental Reactions deal double damage.",
        AbyssBlessing.VigorOfTheAbyss =>
            $"This act, while you are above half HP, your Attacks deal {AbyssNumbers.VigorDamage} additional damage.",
        AbyssBlessing.MoonlitSpring =>
            $"This act, heal {AbyssNumbers.MoonlitSpringHeal} HP at the end of each combat.",
        AbyssBlessing.BattleRhythm =>
            $"This act, start each combat with {AbyssNumbers.BattleRhythmStrength} Strength and {AbyssNumbers.BattleRhythmDexterity} Dexterity.",
        AbyssBlessing.WaveringMoon =>
            $"Whenever you trigger an Elemental Reaction, deal {AbyssNumbers.WaveringMoonDamage} damage to ALL enemies.",
        AbyssBlessing.StarfellDraft =>
            $"Card rewards show {AbyssNumbers.StarfellDraftExtraCards} additional card.",
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
        AbyssShadow.ThornyGround => "Thorny Ground",
        AbyssShadow.Bulwark => "Bulwark",
        AbyssShadow.Frenzy => "Frenzy",
        AbyssShadow.Withering => "Withering",
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
        // This act from round 2 (pick 1 (a)), so its text says so.
        AbyssShadow.Riptide =>
            "This act, whenever an enemy attack deals you unblocked damage, that enemy gains "
          + $"{AbyssNumbers.RiptideStrength} Strength.",
        AbyssShadow.FatuiSkirmishers =>
            $"Elites and bosses enter combat with {AbyssNumbers.FatuiPlating} Plated Armor.",
        AbyssShadow.ThornyGround =>
            $"This act, enemies start each combat with {AbyssNumbers.ThornyGroundThorns} Thorns.",
        AbyssShadow.Bulwark =>
            $"This act, enemies start each combat with {AbyssNumbers.BulwarkBlock} Block.",
        // [USER], 2026-10-12: "Why the extra words? Just give enemies 2 Strength."
        AbyssShadow.Frenzy =>
            $"This act, enemies start each combat with {AbyssNumbers.FrenzyStrength} Strength.",
        AbyssShadow.Withering => $"You start each combat with {AbyssNumbers.WitheringWeak} Weak.",
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
