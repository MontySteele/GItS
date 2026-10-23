using System;
using System.Collections.Generic;
using KleeMod.Elements;

namespace KleeMod.Abyss;

/// <summary>
/// THE SPIRAL ABYSS MODE's Blessings: the first eight
/// (<c>review/active/spiral-abyss-pools-2026-10-12.md</c> sec.2) and round
/// two's six (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>). The numeric
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
    // Round 2 (review/ruled/abyss-pools-2-2026-10-12.md): four This act,
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
/// HOW LONG AN ENTRY LASTS (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>,
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
/// tuned by play (paper sec.1).
///
/// NUMBERS BY ACT (<c>review/active/abyss-act-scaling-2026-10-18.md</c>, ruled
/// 2026-10-18): an entry the paper gives three numbers carries a table of
/// three, one per act (act 1 is index 0; an act past the third takes the
/// last). The number an entry uses -- in its text and in its effect -- is the
/// one for the act it was TAKEN in (<see cref="AbyssRecord.ActTaken(AbyssBlessing)"/>),
/// so an entry taken early keeps its number and nothing grows by itself.
/// The run save is unchanged: it already keeps each pick's act.</summary>
public static class AbyssNumbers
{
    /// <summary>The number of rows in every by-act table.</summary>
    public const int ActRows = 3;

    /// <summary>The row of a by-act table for act index <paramref name="act"/>:
    /// clamped, so an act past the third takes the last row and an act the
    /// record cannot place (-1) takes the first.</summary>
    public static int Row(int act) => Math.Clamp(act, 0, ActRows - 1);

    private static int At(IReadOnlyList<int> table, int act) => table[Row(act)];

    public const int LeyLineDamageReduction = 1;
    public const int AbyssalMoonEvery = 3;
    public static IReadOnlyList<int> AbyssalMoonDamageByAct { get; } = new[] { 4, 5, 6 };
    public static int AbyssalMoonDamage(int act) => At(AbyssalMoonDamageByAct, act);
    public static IReadOnlyList<int> MoonlitRestHealByAct { get; } = new[] { 2, 3, 5 };
    public static int MoonlitRestHeal(int act) => At(MoonlitRestHealByAct, act);
    public static IReadOnlyList<int> ElementalBurstDamageByAct { get; } = new[] { 6, 9, 12 };
    public static int ElementalBurstDamage(int act) => At(ElementalBurstDamageByAct, act);
    public const int ResonanceEnergy = 1;
    public const int ResonanceDraw = 1;
    public const int ResonanceTurn = 1;
    public static IReadOnlyList<int> CrystallizeBlockByAct { get; } = new[] { 8, 12, 16 };
    public static int CrystallizeBlock(int act) => At(CrystallizeBlockByAct, act);
    public static IReadOnlyList<int> FatefulFortuneMaxHpByAct { get; } = new[] { 12, 16, 20 };
    public static int FatefulFortuneMaxHp(int act) => At(FatefulFortuneMaxHpByAct, act);
    public const int OverflowMultiplier = 2;
    public static IReadOnlyList<int> VigorDamageByAct { get; } = new[] { 3, 4, 5 };
    public static int VigorDamage(int act) => At(VigorDamageByAct, act);
    public static IReadOnlyList<int> MoonlitSpringHealByAct { get; } = new[] { 5, 5, 5 };
    public static int MoonlitSpringHeal(int act) => At(MoonlitSpringHealByAct, act);
    public static IReadOnlyList<int> BattleRhythmStrengthByAct { get; } = new[] { 1, 2, 2 };
    public static int BattleRhythmStrength(int act) => At(BattleRhythmStrengthByAct, act);
    public static IReadOnlyList<int> BattleRhythmDexterityByAct { get; } = new[] { 1, 2, 2 };
    public static int BattleRhythmDexterity(int act) => At(BattleRhythmDexterityByAct, act);
    public static IReadOnlyList<int> WaveringMoonDamageByAct { get; } = new[] { 3, 4, 5 };
    public static int WaveringMoonDamage(int act) => At(WaveringMoonDamageByAct, act);

    public const int ClockFromRound = 5;
    public static IReadOnlyList<int> ClockStrengthByAct { get; } = new[] { 2, 2, 3 };
    public static int ClockStrength(int act) => At(ClockStrengthByAct, act);
    /// <summary>Abyss Mage Shield (2026-10-18): 6 hits deep; a hit removes
    /// <see cref="MageShieldPerHit"/>, and a reaction or a counter-element hit
    /// removes <see cref="MageShieldPerReaction"/>.</summary>
    public const int MageShieldHits = 6;
    public const int MageShieldPerHit = 1;
    public const int MageShieldPerReaction = 3;
    public static IReadOnlyList<int> SheerColdHpLossByAct { get; } = new[] { 3, 4, 5 };
    public static int SheerColdHpLoss(int act) => At(SheerColdHpLossByAct, act);
    public const decimal HeraldHpBonus = 0.15m;
    public static IReadOnlyList<int> RallyStrengthByAct { get; } = new[] { 2, 3, 3 };
    public static int RallyStrength(int act) => At(RallyStrengthByAct, act);
    public const int RiptideStrength = 1;
    /// <summary>Riptide's bound (2026-10-18): at most this many Strength
    /// gains per enemy per combat.</summary>
    public static IReadOnlyList<int> RiptideCapByAct { get; } = new[] { 3, 4, 5 };
    public static int RiptideCap(int act) => At(RiptideCapByAct, act);
    public static IReadOnlyList<int> FatuiPlatingByAct { get; } = new[] { 3, 4, 6 };
    public static int FatuiPlating(int act) => At(FatuiPlatingByAct, act);
    public static IReadOnlyList<int> ThornyGroundThornsByAct { get; } = new[] { 2, 2, 3 };
    public static int ThornyGroundThorns(int act) => At(ThornyGroundThornsByAct, act);
    public static IReadOnlyList<int> BulwarkBlockByAct { get; } = new[] { 4, 6, 8 };
    public static int BulwarkBlock(int act) => At(BulwarkBlockByAct, act);
    public static IReadOnlyList<int> FrenzyStrengthByAct { get; } = new[] { 2, 3, 4 };
    public static int FrenzyStrength(int act) => At(FrenzyStrengthByAct, act);
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

    /// <summary>The act index a text is read for when no act is known (the
    /// compendium, a relic before its run sets it): the numbers take act 1's
    /// row (<see cref="AbyssNumbers.Row"/>) and "this act's element" lists
    /// all three.</summary>
    public const int NoAct = -1;

    /// <summary>
    /// THE ELEMENT, NAMED ([USER], 2026-10-22: "For the Spiral Abyss Blessing
    /// 'The Ley Line' - what's this act's element?"). The element of act
    /// <paramref name="elementAct"/> (<see cref="AbyssElements.ForAct"/>),
    /// golded; with no act known, the three acts' elements in one line.
    /// </summary>
    public static string ActElement(int elementAct) =>
        elementAct < 0
            ? "this act's element"
            : $"[gold]{AbyssElements.ForAct(elementAct)}[/gold]";

    /// <summary>"[gold]Hydro[/gold] in act 1, [gold]Pyro[/gold] in act 2,
    /// [gold]Electro[/gold] in act 3." from <see cref="AbyssElements.Table"/>.</summary>
    public static string ElementsByAct()
    {
        var parts = new List<string>();
        for (var i = 0; i < AbyssElements.Table.Count; i++)
        {
            parts.Add($"[gold]{AbyssElements.Table[i]}[/gold] in act {i + 1}");
        }
        return string.Join(", ", parts) + ".";
    }

    /// <summary>A Blessing's text for one act: the numbers are the ones for
    /// <paramref name="act"/>, the act it is offered or was taken in
    /// (<see cref="AbyssNumbers"/>), so the text prints one number.
    /// <paramref name="elementAct"/> is the act whose element The Ley Line
    /// names: the act being played, which for a Blessing held since an
    /// earlier act is not the act it was taken in (its effect reads
    /// <c>SpiralAbyss.CurrentAct</c>). Left out, it is <paramref name="act"/>;
    /// <see cref="NoAct"/> names all three.</summary>
    public static string Text(AbyssBlessing b, int act, int? elementAct = null) => b switch
    {
        AbyssBlessing.LeyLine => (elementAct ?? act) < 0
            ? "Each enemy turn, every enemy without an aura takes this act's element. "
              + $"An enemy wearing an aura deals {AbyssNumbers.LeyLineDamageReduction} less damage. "
              + "The element is " + ElementsByAct()
            : $"Each enemy turn, every enemy without an aura takes {ActElement(elementAct ?? act)}. "
              + $"An enemy wearing an aura deals {AbyssNumbers.LeyLineDamageReduction} less damage.",
        AbyssBlessing.AbyssalMoon =>
            $"Every third card you play in a turn deals {AbyssNumbers.AbyssalMoonDamage(act)} damage to ALL enemies.",
        AbyssBlessing.MoonlitRest => $"Heal {AbyssNumbers.MoonlitRestHeal(act)} HP at the end of each combat.",
        AbyssBlessing.FirstStrike => "Your first Attack each combat is played twice.",
        AbyssBlessing.ElementalBurst =>
            $"Whenever you play a Power, deal {AbyssNumbers.ElementalBurstDamage(act)} damage to ALL enemies.",
        AbyssBlessing.Resonance =>
            $"On turn {AbyssNumbers.ResonanceTurn} of each combat, gain {AbyssNumbers.ResonanceEnergy} Energy and draw {AbyssNumbers.ResonanceDraw} card.",
        AbyssBlessing.Crystallize => $"Start each combat with {AbyssNumbers.CrystallizeBlock(act)} Block.",
        AbyssBlessing.FatefulFortune => $"Gain {AbyssNumbers.FatefulFortuneMaxHp(act)} Max HP.",
        AbyssBlessing.Overflow => "This act, Elemental Reactions deal double damage.",
        AbyssBlessing.VigorOfTheAbyss =>
            $"This act, while you are above half HP, your Attacks deal {AbyssNumbers.VigorDamage(act)} additional damage.",
        AbyssBlessing.MoonlitSpring =>
            $"This act, heal {AbyssNumbers.MoonlitSpringHeal(act)} HP at the end of each combat.",
        AbyssBlessing.BattleRhythm =>
            $"This act, start each combat with {AbyssNumbers.BattleRhythmStrength(act)} Strength and {AbyssNumbers.BattleRhythmDexterity(act)} Dexterity.",
        AbyssBlessing.WaveringMoon =>
            $"Whenever you trigger an Elemental Reaction, deal {AbyssNumbers.WaveringMoonDamage(act)} damage to ALL enemies.",
        AbyssBlessing.StarfellDraft =>
            // A word, not a tunable: "1 additional card" is the Blessing.
            // (Kept off AbyssNumbers so the prose lint does not pair every
            // card's "1 card" with it.)
            "Card rewards show 1 additional card.",
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

    /// <summary>A Shadow's text for one act, on <see cref="Text(AbyssBlessing, int, int?)"/>'s
    /// terms: <paramref name="elementAct"/> is the act whose element Abyss
    /// Mage Shield names.</summary>
    public static string Text(AbyssShadow s, int act, int? elementAct = null) => s switch
    {
        AbyssShadow.Clock =>
            $"From turn {AbyssNumbers.ClockFromRound}, every enemy gains {AbyssNumbers.ClockStrength(act)} Strength at the start of its turn.",
        // 2026-10-18 (review/active/abyss-act-scaling-2026-10-18.md): 6 hits,
        // and the counter element removes 3 rather than breaking it.
        AbyssShadow.MageShield => (elementAct ?? act) < 0
            ? $"Elites enter combat with a shield of this act's element, {AbyssNumbers.MageShieldHits} hits deep, "
              + $"that stops all damage. A hit removes {AbyssNumbers.MageShieldPerHit}. "
              + $"A reaction or a counter-element hit removes {AbyssNumbers.MageShieldPerReaction}. "
              + "Shields are " + ElementsByAct()
            : $"Elites enter combat with a shield of {ActElement(elementAct ?? act)}, {AbyssNumbers.MageShieldHits} hits deep, "
              + $"that stops all damage. A hit removes {AbyssNumbers.MageShieldPerHit}. "
              + $"A reaction or a [gold]{AbyssElements.CounterOf(AbyssElements.ForAct(elementAct ?? act))}[/gold] hit "
              + $"removes {AbyssNumbers.MageShieldPerReaction}.",
        AbyssShadow.SheerCold => $"If you end your turn with no Block, lose {AbyssNumbers.SheerColdHpLoss(act)} HP.",
        // 2026-10-18: once per turn, so a multi-hit attack adds one Burn.
        AbyssShadow.ElementalMark =>
            "The first time each turn an enemy attack deals you unblocked damage, add a Burn into "
          + "your Discard Pile.",
        AbyssShadow.Herald => $"Enemies have {(int)(AbyssNumbers.HeraldHpBonus * 100)}% more HP.",
        AbyssShadow.Rally => $"Whenever an enemy dies, every other enemy gains {AbyssNumbers.RallyStrength(act)} Strength.",
        // This act from round 2 (pick 1 (a)), so its text says so. Bounded
        // 2026-10-18: once per turn per enemy, and a cap per combat.
        AbyssShadow.Riptide =>
            "This act, the first time each turn an enemy's attack deals you unblocked damage, it gains "
          + $"{AbyssNumbers.RiptideStrength} Strength, up to {AbyssNumbers.RiptideCap(act)} times each combat.",
        // 2026-10-18 ([USER]: pick (a)): base Plating scales in co-op (x3 for two
        // players, PlatingPower.GetScaledAmountForMultiplayer), so the text says so.
        AbyssShadow.FatuiSkirmishers =>
            $"Elites and bosses enter combat with {AbyssNumbers.FatuiPlating(act)} Plated Armor, more in co-op.",
        AbyssShadow.ThornyGround =>
            $"This act, enemies start each combat with {AbyssNumbers.ThornyGroundThorns(act)} Thorns.",
        AbyssShadow.Bulwark =>
            $"This act, at the start of your turn, each enemy gains {AbyssNumbers.BulwarkBlock(act)} Block.",
        // [USER], 2026-10-12: "Why the extra words? Just give enemies 2 Strength."
        AbyssShadow.Frenzy =>
            $"This act, enemies start each combat with {AbyssNumbers.FrenzyStrength(act)} Strength.",
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
