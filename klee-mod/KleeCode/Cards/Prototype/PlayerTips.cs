using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// EVERY ARM TIP BODY A PLAYER READS, AS KEYED ROWS (the localization census,
/// 2026-10-23, step 1; [USER]: "I do want to have localization support").
/// Each body is a <see cref="CodeRow"/> in <c>card_keywords</c>, keyed
/// <c>&lt;tip key&gt;.description</c> (a variant
/// <c>&lt;tip key&gt;.description_&lt;variant&gt;</c>), merged into the
/// English table by <see cref="CodeText"/> and read through the game's
/// <c>LocString</c>, so a translation replaces it row by row. The numbers are
/// vars read off the laws they quote (<see cref="Vars"/>, `EB-89`).
///
/// THE TOOLTIP TRIM (2026-10-14, review/active/tooltip-trim-2026-10-14.md
/// sec.3, all three picks at (a)). [USER], during the 2026-10-14 Furina run:
/// "her cards still make a million words of tooltips come up ... I think it's
/// worth trying to figure out how to make this cleaner / simpler so the
/// tooltips aren't half the screen."
///
/// THE HOUSE RULE: at most 3 boxes on a card's static hover, about 90
/// characters a box, in base-game style (what the word does, in one
/// sentence). `tools/lint_hover_tips.py` holds every generated card to it.
///
/// THE SEAT KEEPS EVERY WORD. Where a blind seat reads a longer sentence than
/// the player, that sentence stays an English literal in
/// <see cref="ArmKeywordTips"/> (<c>With(inherited, key, seatBody)</c>), read
/// only while <see cref="TipAudience.Seat"/> is true; seat text is not
/// translated. Where the two read the same words, the row here is both
/// (<c>With(inherited, key)</c>). A rider only the seat's chain carries
/// (Big Badda Boom's total, Pass the Match, Final Bow and the rest) has no
/// row: it is seat text. Which boxes a card raises for each reader is
/// codegen's (`gen_klee_cards.player_tip_layers`), and
/// `tools/lint_hover_tips.py` fails a player chain that raises a tip with no
/// row here.
/// </summary>
internal static class PlayerTips
{
    /// <summary>The table every tip body lives in, beside its title.</summary>
    internal const string Table = "card_keywords";

    // The variant leaves (`<key>.description_<variant>`).
    internal const string OpeningBank = "opening_bank";
    internal const string OwnLine = "own_line";
    internal const string Yae = "yae";

    /// <summary>The merged Guest Star box, the paper's sentence. Declared
    /// before <see cref="Bodies"/>, which reads it at type init.</summary>
    internal static readonly string GuestStarBody =
        "Joins at the back and acts at the end of your turn. If the stage "
      + "is full, it pushes out the oldest.";

    /// <summary>The law constants the bodies quote, by var name.</summary>
    internal static readonly IReadOnlyDictionary<string, object> Vars = CodeText.Vars(
        ("BombGrowth", KleeOverhaulLaw.BombGrowth),
        ("OpeningSpark", KleeOverhaulLaw.OpeningSpark),
        ("SwirlDamage", Elements.ReactionConstants.SwirlDamage),
        ("SakuraBase", YaeLaw.SakuraBase),
        ("SakuraPerLevel", YaeLaw.SakuraPerLevel),
        ("SakuraTurns", YaeLaw.SakuraTurns),
        ("FoxfireBase", YaeLaw.FoxfireBase),
        ("KitsuneBase", YaeLaw.KitsuneBase));

    /// <summary>Player bodies by tip key, row <c>&lt;key&gt;.description</c>.
    /// A key with no row prints its seat wording to both readers.</summary>
    internal static readonly Dictionary<string, string> Bodies = new()
    {
        // ---- Klee. Bomb and Set off kept, one sentence each; the jump and
        // the other enemies' Bombs are the seat's.
        [ArmKeywordTips.BombKey] =
            "Deals its size in [gold]Pyro[/gold] damage when "
          + "[gold]Set off[/gold], and grows {BombGrowth} each turn.",
        [ArmKeywordTips.SetOffKey] =
            "Every [gold]Bomb[/gold] on the enemy goes off, oldest first.",
        // The Spark tip, the player's way: the price, and (`.description_
        // opening_bank`, below) the opening bank; "no cap" and "gone after
        // combat" are the seat's.
        [ArmKeywordTips.SparkKey] =
            "Some cards cost [gold]Sparks[/gold] instead of Energy.",
        [ArmKeywordTips.MineKey] =
            "A [gold]Bomb[/gold] that also goes off when its enemy attacks you.",
        [ArmKeywordTips.OzKey] =
            "Fischl's raven. While you hold Oz, at Your Side, he hits with "
          + "[gold]Electro[/gold] each turn.",
        // `EB-575`: the no-Bomb rider, the card that is nothing but Bomb work
        // (`.description_own_line`, below, for one with a line of its own).
        [ArmKeywordTips.EmptyFieldKey] =
            "No [gold]Bomb[/gold] on the field: this card does nothing.",

        // ---- Kokomi. The keyword tip's opening and timing (2026-10-18),
        // inside this box's 100: its "; Block lasts that turn" and flip
        // sentence are the seat's.
        [ArmKeywordTips.PlanKey] =
            "Play it on the [gold]Bake-Kurage[/gold] instead. After enemies "
          + "act and you draw, Plans happen in order.",
        [ArmKeywordTips.PlanOnlyKey] =
            "Play the card on the [gold]Bake-Kurage[/gold]. It happens next "
          + "turn.",
        [ArmKeywordTips.PlanNoLineKey] =
            "This card has no Plan line, so it cannot be played on the "
          + "[gold]Bake-Kurage[/gold].",
        [ArmKeywordTips.PlanElementKey] =
            "The [gold]Bake-Kurage[/gold] carries out this [gold]Plan[/gold] "
          + "as a [gold]Hydro[/gold] hit: it applies [gold]Hydro[/gold].",
        [ArmKeywordTips.MendKey] =
            "[gold]Mend N[/gold]: heal N HP, but never above the HP you had "
          + "at the start of this combat.",

        // ---- Shared element words.
        [ArmKeywordTips.SwirlKey] =
            "[gold]Anemo[/gold] meets an aura: deal {SwirlDamage} unblockable "
          + "damage to ALL enemies and spread that element.",
        [ArmKeywordTips.ElementalReactionKey] =
            "An element meets another element's aura on an enemy, and the "
          + "two react.",
        [ArmKeywordTips.CompanionKey] =
            "A shared ally card, such as Jean's Gale Blade. Varka's "
          + "Knights count too.",
        [ArmKeywordTips.LightfallSwordKey] =
            "A blade hung over an enemy. Its badge counts down the turns "
          + "until it falls.",

        // ---- Yae. Sakura on another character's card (hers is
        // `.description_yae`, below).
        [ArmKeywordTips.SakuraKey] =
            "A totem that stays at your side all combat. At most 3 fire "
          + "each turn.",
        [ArmKeywordTips.EditKey] =
            "Give a card an Annotation for this combat, replacing its last. "
          + "Published ones stay and add up.",
        [ArmKeywordTips.TenkoKey] =
            "Every [gold]Sakura[/gold] acts now and goes back to at least "
          + "{SakuraTurns} turns left.",
        [ArmKeywordTips.FoxfireSakuraKey] =
            "A [gold]Sakura[/gold] that deals damage equal to "
          + "{FoxfireBase} plus its Level to ALL enemies when it acts.",
        [ArmKeywordTips.KitsuneSakuraKey] =
            "A fox decoy [gold]Sakura[/gold]. When it acts, you gain "
          + "[gold]Block[/gold] equal to {KitsuneBase} plus its Level.",
        [ArmKeywordTips.FullShrineKey] =
            "Planting makes the Sakura closest to withering act. Same kind: it "
          + "refreshes and gains a Level. Other kind: it withers, and the new "
          + "one takes its Level if higher.",

        // ---- Varka. Oath and Current element kept, one sentence each.
        [ArmKeywordTips.OathKey] =
            "1 Oath per element a card applies, plus 1 per element it "
          + "[gold]Swirls[/gold]. Kept all fight.",
        [ArmKeywordTips.CurrentElementKey] =
            "The last [gold]Pyro[/gold], [gold]Hydro[/gold], [gold]Cryo[/gold] "
          + "or [gold]Electro[/gold] you applied. Your [gold]Swirls[/gold] "
          + "pay out in it.",
        // `.description_named`: the keyword row `.description` is
        // `ArmKeywordTips.KnightTipText`, the card that IS a Knight.
        [ArmKeywordTips.KnightKey] =
            "One of Varka's Companions. Playing one makes its element your "
          + "current element.",
        [ArmKeywordTips.ElementSwitchKey] =
            "Switches your [gold]current element[/gold] to {Element}.",
        [ArmKeywordTips.AscensionReturnKey] =
            "When played, it goes to your [gold]Discard Pile[/gold] and comes "
          + "back after a reshuffle.",
        [ArmKeywordTips.AscensionNoOathKey] = "This hit does not gain Oath.",

        // ---- Furina. One merged Guest Star box (pick 3 (a)): a Guest Star
        // card drops Summon and keeps this.
        [ArmKeywordTips.SpendKey] =
            "Pay that much [gold]Fanfare[/gold]. With less, you cannot play "
          + "the card or its Spend mode.",
        [ArmKeywordTips.FanfareKey] =
            "Gain 1 for each HP you lose, [gold]Drain[/gold] included, or [gold]Repay[/gold]. "
          + "[gold]Spend[/gold] uses it. Resets after each combat.",
        [ArmKeywordTips.DrainKey] =
            "Lose N HP. After combat, up to 1/4 of your Max HP drained comes "
          + "back; [gold]Repay[/gold] the rest.",
        // furina-next paper 3 (2026-10-16): the rule's one line.
        [ArmKeywordTips.RepayKey] =
            "Regain that much drained HP. Any HP a Repay cannot return becomes "
          + "[gold]Block[/gold].",
        [ArmKeywordTips.FlipKey] =
            "Turn this card to its other face; it starts each combat on Ousia.",
        [ArmKeywordTips.BankDamageKey] =
            "Whenever you lose HP, gain that much [gold]Fanfare[/gold]. Its "
          + "damage is the [gold]Fanfare[/gold] you hold: play it when "
          + "the bank is worth it.",
        [ArmKeywordTips.SummonKey] = GuestStarBody,
        [ArmKeywordTips.GuestStarKey] = GuestStarBody,
    };

    /// <summary>The variant rows, row
    /// <c>&lt;key&gt;.description_&lt;variant&gt;</c>.</summary>
    internal static readonly Dictionary<(string Key, string Variant), string> Variants = new()
    {
        // Klee's opening bank, printed only to a Klee
        // (`ArmKeywordTips.KleeOpensWithASpark`).
        [(ArmKeywordTips.SparkKey, OpeningBank)] =
            "Some cards cost [gold]Sparks[/gold] instead of Energy. Start "
          + "each combat with {OpeningSpark}.",
        [(ArmKeywordTips.EmptyFieldKey, OwnLine)] =
            "No [gold]Bomb[/gold] on the field: this card is only its own "
          + "line.",
        // Yae's Sakura: the strike and the timer (paper sec.2, shrine r2;
        // the Sakura Levels paper, pick 1 (a), 2026-10-17).
        [(ArmKeywordTips.SakuraKey, Yae)] =
            "At the end of your turn, deals {SakuraBase} damage plus "
          + "{SakuraPerLevel} for each Level. Lasts "
          + "{SakuraTurns} turns, then strikes again.",
    };

    /// <summary>The row key of a tip key's body.</summary>
    internal static string RowKey(string key) =>
        key == ArmKeywordTips.KnightKey ? key + ".description_named" : key + ".description";

    /// <summary>The row key of a variant.</summary>
    internal static string RowKey(string key, string variant) => key + ".description_" + variant;

    internal static CodeRow Row(string key) => new(Table, RowKey(key), Bodies[key]);

    internal static CodeRow Row(string key, string variant) =>
        new(Table, RowKey(key, variant), Variants[(key, variant)]);

    /// <summary>Every row (<see cref="CodeText.Sources"/>).</summary>
    internal static IEnumerable<CodeRow> Rows() =>
        Bodies.Keys.Select(Row)
            .Concat(Variants.Keys.Select(v => Row(v.Key, v.Variant)));

    /// <summary>The key's body as the player reads it.</summary>
    internal static string Text(string key, params (string Name, object Value)[] vars) =>
        CodeText.Format(Row(key), vars.Length == 0 ? Vars : CodeText.With(Vars, vars));

    /// <summary>A variant's body as the player reads it.</summary>
    internal static string Variant(string key, string variant) =>
        CodeText.Format(Row(key, variant), Vars);

    /// <summary><paramref name="seatBody"/>, or the player's words for
    /// <paramref name="key"/> when a player is reading.</summary>
    internal static string For(string key, string seatBody) =>
        !TipAudience.Seat && Bodies.ContainsKey(key) ? Text(key) : seatBody;

    /// <summary>The Spark tip, the player's way.</summary>
    internal static string SparkBody(bool openingBank) =>
        openingBank
            ? Variant(ArmKeywordTips.SparkKey, OpeningBank)
            : Text(ArmKeywordTips.SparkKey);

    /// <summary>
    /// A guest's own tip (pick 3 (a)): "the guest's sentence only where the
    /// face does not already say it". A face that prints the act shows the
    /// line; a face that prints the line shows the act; a face that prints
    /// neither shows both. The seat reads the whole sentence.
    ///
    /// WHICH THE FACE PRINTS IS DECLARED, NOT READ (the localization census,
    /// 2026-10-23, group 3). This used to search the card's English face for
    /// "Act:" and for the line's opening words, which a translated face never
    /// matches. The card generator stamps <see cref="IPrintsGuestAct"/> or
    /// <see cref="IPrintsGuestLine"/> on the row
    /// (`gen_klee_cards.guest_face_interface`), the way
    /// <see cref="ISetsOffFirstCard"/> replaced the Set off reading.
    /// </summary>
    internal static string Guest(CardModel card, StagePerformer who)
    {
        var upgraded = card.IsUpgraded;
        if (TipAudience.Seat) return StagePerformerBadge.ActText(who, upgraded);
        return card switch
        {
            IPrintsGuestAct => StagePerformerBadge.LineText(who, upgraded),
            IPrintsGuestLine => StagePerformerBadge.ActOnlyText(who, upgraded),
            _ => StagePerformerBadge.GuestText(who, upgraded),
        };
    }
}

/// <summary>A Guest Star card whose face prints its guest's act ("Act:
/// ..."), so the guest's tip shows only the line. Stamped by the card
/// generator.</summary>
public interface IPrintsGuestAct
{
}

/// <summary>A Guest Star card whose face prints its guest's line, so the
/// guest's tip shows only the act. Stamped by the card generator.</summary>
public interface IPrintsGuestLine
{
}
