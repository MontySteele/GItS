using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Abyss;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// NUMBERS BY ACT, AND THE SNOWBALLS BOUNDED
/// (<c>review/active/abyss-act-scaling-2026-10-18.md</c>, v2, ruled
/// 2026-10-18: "Makes sense! ... let's do both.").
///
/// Every entry the paper gives three numbers prints, and uses, the number of
/// the act it was taken in; an entry taken early keeps its number. Riptide is
/// once per turn per enemy with a cap per combat, Elemental Mark once per turn,
/// and Abyss Mage Shield is 6 hits deep with the counter element removing 3.
/// The texts are pinned word for word, one row per act.
/// </summary>
public class AbyssActScalingTests
{
    private static SpiralAbyss NewModifier(int act)
    {
        var abyss = (SpiralAbyss)RuntimeHelpers.GetUninitializedObject(typeof(SpiralAbyss));
        abyss.ActForTests = act;
        return abyss;
    }

    // ---- The texts, one row per act ------------------------------------------

    [Theory]
    [InlineData(AbyssBlessing.AbyssalMoon, 0, "Every third card you play in a turn deals 4 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.AbyssalMoon, 1, "Every third card you play in a turn deals 5 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.AbyssalMoon, 2, "Every third card you play in a turn deals 6 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.MoonlitRest, 0, "Heal 2 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.MoonlitRest, 1, "Heal 3 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.MoonlitRest, 2, "Heal 5 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.ElementalBurst, 0, "Whenever you play a Power, deal 6 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.ElementalBurst, 1, "Whenever you play a Power, deal 9 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.ElementalBurst, 2, "Whenever you play a Power, deal 12 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.Crystallize, 0, "Start each combat with 8 Block.")]
    [InlineData(AbyssBlessing.Crystallize, 1, "Start each combat with 12 Block.")]
    [InlineData(AbyssBlessing.Crystallize, 2, "Start each combat with 16 Block.")]
    [InlineData(AbyssBlessing.FatefulFortune, 0, "Gain 12 Max HP.")]
    [InlineData(AbyssBlessing.FatefulFortune, 1, "Gain 16 Max HP.")]
    [InlineData(AbyssBlessing.FatefulFortune, 2, "Gain 20 Max HP.")]
    [InlineData(AbyssBlessing.VigorOfTheAbyss, 0, "This act, while you are above half HP, your Attacks deal 3 additional damage.")]
    [InlineData(AbyssBlessing.VigorOfTheAbyss, 1, "This act, while you are above half HP, your Attacks deal 4 additional damage.")]
    [InlineData(AbyssBlessing.VigorOfTheAbyss, 2, "This act, while you are above half HP, your Attacks deal 5 additional damage.")]
    [InlineData(AbyssBlessing.MoonlitSpring, 0, "This act, heal 5 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.MoonlitSpring, 1, "This act, heal 5 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.MoonlitSpring, 2, "This act, heal 5 HP at the end of each combat.")]
    [InlineData(AbyssBlessing.BattleRhythm, 0, "This act, start each combat with 1 Strength and 1 Dexterity.")]
    [InlineData(AbyssBlessing.BattleRhythm, 1, "This act, start each combat with 2 Strength and 2 Dexterity.")]
    [InlineData(AbyssBlessing.BattleRhythm, 2, "This act, start each combat with 2 Strength and 2 Dexterity.")]
    [InlineData(AbyssBlessing.WaveringMoon, 0, "Whenever you trigger an Elemental Reaction, deal 3 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.WaveringMoon, 1, "Whenever you trigger an Elemental Reaction, deal 4 damage to ALL enemies.")]
    [InlineData(AbyssBlessing.WaveringMoon, 2, "Whenever you trigger an Elemental Reaction, deal 5 damage to ALL enemies.")]
    public void A_Blessings_text_prints_its_acts_number(AbyssBlessing b, int act, string text) =>
        Assert.Equal(text, AbyssText.Text(b, act));

    [Theory]
    [InlineData(AbyssShadow.Bulwark, 0, "This act, at the start of your turn, each enemy gains 4 Block.")]
    [InlineData(AbyssShadow.Bulwark, 1, "This act, at the start of your turn, each enemy gains 6 Block.")]
    [InlineData(AbyssShadow.Bulwark, 2, "This act, at the start of your turn, each enemy gains 8 Block.")]
    [InlineData(AbyssShadow.Frenzy, 0, "This act, enemies start each combat with 2 Strength.")]
    [InlineData(AbyssShadow.Frenzy, 1, "This act, enemies start each combat with 3 Strength.")]
    [InlineData(AbyssShadow.Frenzy, 2, "This act, enemies start each combat with 4 Strength.")]
    [InlineData(AbyssShadow.ThornyGround, 0, "This act, enemies start each combat with 2 Thorns.")]
    [InlineData(AbyssShadow.ThornyGround, 1, "This act, enemies start each combat with 2 Thorns.")]
    [InlineData(AbyssShadow.ThornyGround, 2, "This act, enemies start each combat with 3 Thorns.")]
    [InlineData(AbyssShadow.Riptide, 0, "This act, the first time each turn an enemy's attack deals you unblocked damage, it gains 1 Strength, up to 3 times per combat.")]
    [InlineData(AbyssShadow.Riptide, 1, "This act, the first time each turn an enemy's attack deals you unblocked damage, it gains 1 Strength, up to 4 times per combat.")]
    [InlineData(AbyssShadow.Riptide, 2, "This act, the first time each turn an enemy's attack deals you unblocked damage, it gains 1 Strength, up to 5 times per combat.")]
    [InlineData(AbyssShadow.ElementalMark, 0, "The first time each turn an enemy attack deals you unblocked damage, add a Burn to your discard pile.")]
    [InlineData(AbyssShadow.ElementalMark, 1, "The first time each turn an enemy attack deals you unblocked damage, add a Burn to your discard pile.")]
    [InlineData(AbyssShadow.ElementalMark, 2, "The first time each turn an enemy attack deals you unblocked damage, add a Burn to your discard pile.")]
    [InlineData(AbyssShadow.MageShield, 0, "Elites enter combat with a shield of this act's element, 6 hits deep, that stops all damage. A hit removes 1. A reaction or a counter-element hit removes 3.")]
    [InlineData(AbyssShadow.MageShield, 1, "Elites enter combat with a shield of this act's element, 6 hits deep, that stops all damage. A hit removes 1. A reaction or a counter-element hit removes 3.")]
    [InlineData(AbyssShadow.MageShield, 2, "Elites enter combat with a shield of this act's element, 6 hits deep, that stops all damage. A hit removes 1. A reaction or a counter-element hit removes 3.")]
    [InlineData(AbyssShadow.Clock, 0, "From turn 5, every enemy gains 2 Strength at the start of its turn.")]
    [InlineData(AbyssShadow.Clock, 1, "From turn 5, every enemy gains 2 Strength at the start of its turn.")]
    [InlineData(AbyssShadow.Clock, 2, "From turn 5, every enemy gains 3 Strength at the start of its turn.")]
    [InlineData(AbyssShadow.Rally, 0, "When an enemy dies, every other enemy gains 2 Strength.")]
    [InlineData(AbyssShadow.Rally, 1, "When an enemy dies, every other enemy gains 3 Strength.")]
    [InlineData(AbyssShadow.Rally, 2, "When an enemy dies, every other enemy gains 3 Strength.")]
    [InlineData(AbyssShadow.SheerCold, 0, "If you end your turn with no Block, lose 3 HP.")]
    [InlineData(AbyssShadow.SheerCold, 1, "If you end your turn with no Block, lose 4 HP.")]
    [InlineData(AbyssShadow.SheerCold, 2, "If you end your turn with no Block, lose 5 HP.")]
    [InlineData(AbyssShadow.FatuiSkirmishers, 0, "Elites and bosses enter combat with 3 Plated Armor.")]
    [InlineData(AbyssShadow.FatuiSkirmishers, 1, "Elites and bosses enter combat with 4 Plated Armor.")]
    [InlineData(AbyssShadow.FatuiSkirmishers, 2, "Elites and bosses enter combat with 6 Plated Armor.")]
    public void A_Shadows_text_prints_its_acts_number(AbyssShadow s, int act, string text) =>
        Assert.Equal(text, AbyssText.Text(s, act));

    /// <summary>The entries with no number by act read the same in every act,
    /// word for word what they were.</summary>
    [Theory]
    [InlineData(AbyssBlessing.LeyLine, "Each enemy turn, every enemy without an aura takes this act's element. An enemy wearing an aura deals 1 less damage.")]
    [InlineData(AbyssBlessing.FirstStrike, "Your first Attack each combat is played twice.")]
    [InlineData(AbyssBlessing.Resonance, "On turn 1 of each combat, gain 1 Energy and draw 1 card.")]
    [InlineData(AbyssBlessing.Overflow, "This act, Elemental Reactions deal double damage.")]
    [InlineData(AbyssBlessing.StarfellDraft, "Card rewards show 1 additional card.")]
    public void An_unscaled_Blessing_reads_the_same_in_every_act(AbyssBlessing b, string text)
    {
        for (var act = 0; act < 4; act++) Assert.Equal(text, AbyssText.Text(b, act));
    }

    [Theory]
    [InlineData(AbyssShadow.Herald, "Enemies have 15% more HP.")]
    [InlineData(AbyssShadow.Withering, "You start each combat with 1 Weak.")]
    public void An_unscaled_Shadow_reads_the_same_in_every_act(AbyssShadow s, string text)
    {
        for (var act = 0; act < 4; act++) Assert.Equal(text, AbyssText.Text(s, act));
    }

    [Fact]
    public void An_act_past_the_third_takes_the_last_row_and_an_unplaced_entry_the_first()
    {
        Assert.Equal(AbyssText.Text(AbyssShadow.Bulwark, 2), AbyssText.Text(AbyssShadow.Bulwark, 3));
        Assert.Equal(8, AbyssNumbers.BulwarkBlock(5));
        Assert.Equal(4, AbyssNumbers.BulwarkBlock(-1));
        Assert.Equal(0, AbyssNumbers.Row(-1));
        Assert.Equal(2, AbyssNumbers.Row(7));
    }

    // ---- The number is the act it was TAKEN in --------------------------------

    [Fact]
    public void An_entry_taken_in_act_1_keeps_its_act_1_number_in_act_3()
    {
        var abyss = NewModifier(act: 0);
        abyss.Record.Record(0, AbyssBlessing.Crystallize, AbyssShadow.Clock);
        abyss.Record.Record(1, AbyssBlessing.WaveringMoon, AbyssShadow.Rally);
        abyss.ActForTests = 2;

        Assert.True(abyss.Has(AbyssBlessing.Crystallize));
        Assert.True(abyss.Has(AbyssShadow.Clock));
        Assert.Equal(0, abyss.ActOf(AbyssBlessing.Crystallize));
        Assert.Equal(0, abyss.ActOf(AbyssShadow.Clock));
        Assert.Equal(1, abyss.ActOf(AbyssShadow.Rally));
        Assert.Equal(8, AbyssNumbers.CrystallizeBlock(abyss.ActOf(AbyssBlessing.Crystallize)));
        Assert.Equal(2, AbyssNumbers.ClockStrength(abyss.ActOf(AbyssShadow.Clock)));
        Assert.Equal(3, AbyssNumbers.RallyStrength(abyss.ActOf(AbyssShadow.Rally)));
        Assert.Equal(-1, abyss.ActOf(AbyssBlessing.LeyLine));   // never taken

        // The act 3 page's strip prints each entry at the act it was taken in.
        var offer = new AbyssOffer(2, new[] { new AbyssOption(AbyssBlessing.FatefulFortune, AbyssShadow.Bulwark) }, 0);
        var content = AbyssOverlayContent.For(offer, abyss.Record);
        Assert.Equal("Start each combat with 8 Block.", content.BlessingsTaken[0].Text);
        Assert.Equal("From turn 5, every enemy gains 2 Strength at the start of its turn.",
                     content.ShadowsInForce[0].Text);
        Assert.Equal("When an enemy dies, every other enemy gains 3 Strength.", content.ShadowsInForce[1].Text);
        // ...while the act 3 card prints act 3's.
        Assert.Equal("Gain 20 Max HP.", content.Cards[0].BlessingText);
        Assert.Equal("This act, at the start of your turn, each enemy gains 8 Block.", content.Cards[0].ShadowText);
    }

    [Fact]
    public void Vigor_taken_in_act_2_adds_4_through_the_real_hook()
    {
        var abyss = NewModifier(act: 1);
        var seat = Seat.Klee(maxHp: 80);
        abyss.Record.Record(1, AbyssBlessing.VigorOfTheAbyss, AbyssShadow.Clock);
        Assert.Equal(4m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move, seat.Creature, null, null));
    }

    [Fact]
    public void The_save_is_unchanged_three_int_arrays()
    {
        var saved = typeof(SpiralAbyss).GetProperties()
            .Where(p => p.GetCustomAttributes(typeof(MegaCrit.Sts2.Core.Saves.Runs.SavedPropertyAttribute), true).Any())
            .Select(p => p.Name).OrderBy(n => n).ToArray();
        Assert.Equal(new[] { "SpiralAbyssActs", "SpiralAbyssBlessings", "SpiralAbyssShadows" }, saved);
    }

    [Fact]
    public void The_choice_page_has_one_option_row_per_act()
    {
        var rows = AbyssChoicePage.LocRows();
        for (var act = 0; act < AbyssNumbers.ActRows; act++)
        {
            Assert.Equal(
                AbyssText.Text(AbyssBlessing.MoonlitRest, act)
                + "\n[red]If you pass this, the enemies may take its Shadow:[/red] [gold]Bulwark[/gold]. "
                + AbyssText.Text(AbyssShadow.Bulwark, act),
                rows[AbyssChoicePage.OptionDescriptionKey(AbyssBlessing.MoonlitRest, AbyssShadow.Bulwark, act)]);
        }
        // An act past the third reads the last row.
        Assert.Equal(AbyssChoicePage.OptionDescriptionKey(AbyssBlessing.MoonlitRest, AbyssShadow.Bulwark, 2),
                     AbyssChoicePage.OptionDescriptionKey(AbyssBlessing.MoonlitRest, AbyssShadow.Bulwark, 3));
        // STRUCTURAL: Fateful Fortune's Max HP is the pick's act.
        Assert.Contains("AbyssNumbers.FatefulFortuneMaxHp",
            Il.Calls(typeof(AbyssChoicePage).GetMethod("OnChosen", HeadlessGame.All)!));
    }

    // ---- Riptide: once per turn per enemy, and a cap --------------------------

    [Fact]
    public void Riptide_feeds_once_per_turn_per_enemy_up_to_its_acts_cap()
    {
        var abyss = NewModifier(act: 0);
        abyss.Record.Record(0, AbyssBlessing.FirstStrike, AbyssShadow.Riptide);
        var enemyA = Seat.Klee().Creature;
        var enemyB = Seat.Varka().Creature;

        // Round 1: a multi-hit attack lands three times; one feeds it.
        Assert.True(abyss.TakeRiptide(enemyA, 1));
        Assert.False(abyss.TakeRiptide(enemyA, 1));
        Assert.False(abyss.TakeRiptide(enemyA, 1));
        // Per enemy: the other enemy's first hit this turn feeds it.
        Assert.True(abyss.TakeRiptide(enemyB, 1));

        // Rounds 2 and 3 feed A again; act 1's cap is 3, so round 4 does not.
        Assert.True(abyss.TakeRiptide(enemyA, 2));
        Assert.True(abyss.TakeRiptide(enemyA, 3));
        Assert.False(abyss.TakeRiptide(enemyA, 4));
        Assert.False(abyss.TakeRiptide(enemyA, 5));
        // B has its own count.
        Assert.True(abyss.TakeRiptide(enemyB, 4));
    }

    [Fact]
    public void Riptide_taken_in_act_3_caps_at_5()
    {
        var abyss = NewModifier(act: 2);
        abyss.Record.Record(2, AbyssBlessing.FirstStrike, AbyssShadow.Riptide);
        var enemy = Seat.Klee().Creature;
        var fed = Enumerable.Range(1, 9).Count(round => abyss.TakeRiptide(enemy, round));
        Assert.Equal(5, fed);
        Assert.Equal(new[] { 3, 4, 5 }, AbyssNumbers.RiptideCapByAct);
    }

    [Fact]
    public void Riptide_rule_and_ledger()
    {
        Assert.True(AbyssRules.RiptideFeeds(enemyAlreadyFedThisTurn: false, gainsThisCombat: 2, cap: 3));
        Assert.False(AbyssRules.RiptideFeeds(enemyAlreadyFedThisTurn: true, gainsThisCombat: 0, cap: 3));
        Assert.False(AbyssRules.RiptideFeeds(false, gainsThisCombat: 3, cap: 3));

        var ledger = new AbyssTurnLedger<string>();
        Assert.False(ledger.CountedThisTurn("a", 1));
        ledger.Count("a", 1);
        Assert.True(ledger.CountedThisTurn("a", 1));
        Assert.False(ledger.CountedThisTurn("a", 2));
        Assert.Equal(1, ledger.CountThisCombat("a"));
        ledger.Clear();   // a new combat
        Assert.Equal(0, ledger.CountThisCombat("a"));
        Assert.False(ledger.CountedThisTurn("a", 1));

        // STRUCTURAL: the damage hook asks the ledgers, and combat start
        // clears them.
        var hook = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterDamageReceived))!);
        Assert.Contains("SpiralAbyss.TakeRiptide", hook);
        Assert.Contains("SpiralAbyss.TakeElementalMark", hook);
        var start = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.BeforeCombatStart))!);
        Assert.Contains("AbyssTurnLedger`1.Clear", start);
    }

    // ---- Elemental Mark: once per turn ----------------------------------------

    [Fact]
    public void Elemental_Mark_adds_one_Burn_per_turn_per_player()
    {
        var abyss = NewModifier(act: 0);
        abyss.Record.Record(0, AbyssBlessing.FirstStrike, AbyssShadow.ElementalMark);
        var klee = Seat.Klee().Creature;
        var varka = Seat.Varka().Creature;

        // A three-hit attack in round 1: one Burn.
        Assert.True(abyss.TakeElementalMark(klee, 1));
        Assert.False(abyss.TakeElementalMark(klee, 1));
        Assert.False(abyss.TakeElementalMark(klee, 1));
        // The co-op partner is marked on their own.
        Assert.True(abyss.TakeElementalMark(varka, 1));
        // No cap: every turn may mark again.
        for (var round = 2; round < 12; round++) Assert.True(abyss.TakeElementalMark(klee, round));

        Assert.True(AbyssRules.ElementalMarkFires(playerAlreadyMarkedThisTurn: false));
        Assert.False(AbyssRules.ElementalMarkFires(playerAlreadyMarkedThisTurn: true));
    }
}
