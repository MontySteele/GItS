using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// WHO A GUEST STAR CARD WILL MOVE, on its face (2026-10-04, the Furina v2
/// seat round: three times a summon onto a full stage sent a performer off
/// without the player noticing). Kept for the guests (the Salon's Tab,
/// 2026-10-05).
///
/// A Guest Star card's face ends in <c>{InCombat:{StageBow}|}</c>, the base
/// game's in-combat line, and the generated card fills <c>StageBow</c> in
/// <c>AddExtraArgsToDescription</c> from here. The line is empty when the
/// guest simply takes a free seat. The decision is
/// <see cref="StageDirector.GuestRoom"/>, the rule the summon itself runs,
/// so preview and outcome cannot drift.
/// </summary>
public static class FurinaStageBowPreview
{
    /// <summary>The description token the line rides on.</summary>
    public const string Token = "StageBow";

    /// <summary>A Guest Star card's line for its owner's stage as it stands;
    /// empty off a combat, on a canonical card, or for a seat that is not
    /// Furina's.</summary>
    public static string Guest(CardModel card, string member)
    {
        if (TipOwner.CreatureOf(card) is not { } owner
            || owner.CombatState == null || !FurinaStage.LiveFor(owner))
        {
            return "";
        }
        return Line(FurinaStageLedger.For(owner), FurinaStage.Parse(member));
    }

    /// <summary>The line for <paramref name="stage"/> (the pins'; the pool to
    /// 75's rule): "(Clorinde moves to the newest seat and acts)" for a
    /// guest already on stage (it acts since the 2026-10-11 playtest),
    /// "(Charlotte acts, then leaves)" for the oldest guest on a full stage
    /// (it acts on the way out since 2026-10-11), else empty.</summary>
    public static string Line(FurinaStageLedger stage, StagePerformer who)
    {
        var room = StageDirector.GuestRoom(stage.Company.ToList(),
                                           stage.Capacity, who);
        return room.Kind switch
        {
            StageSummonResult.Repeat => CodeText.Format(RepeatRow, CodeText.Vars(
                ("Guest", PerformerWords.Name(who)))),
            StageSummonResult.Evict => CodeText.Format(EvictRow, CodeText.Vars(
                ("Guest", PerformerWords.Name(stage.Seats[room.Index].Who)))),
            _ => "",
        };
    }

    // ---- The lines' rows (the localization census, 2026-10-23, step 2):
    // each in-combat Stage line a card face carries is a row in
    // `card_keywords`, its line break the row's, its numbers vars and a
    // guest's name its own row (`PerformerWords`).
    internal const string Table = "card_keywords";

    internal static readonly CodeRow RepeatRow =
        new(Table, "KLEEMOD-FACE_STAGE_BOW.repeat", "\n({Guest} moves to the newest seat and acts)");
    internal static readonly CodeRow EvictRow =
        new(Table, "KLEEMOD-FACE_STAGE_BOW.evict", "\n({Guest} acts, then leaves)");

    /// <summary>Every Stage line's row (<see cref="CodeText.Sources"/>).</summary>
    public static IEnumerable<CodeRow> TextRows() =>
        new[] { RepeatRow, EvictRow }
            .Concat(FurinaStageFacePreview.TextRows())
            .Concat(PerformerWords.Rows());
}

/// <summary>
/// THE OTHER TWO IN-COMBAT STAGE LINES (the Salon's Tab seat round,
/// 2026-10-05), filled the way <see cref="FurinaStageBowPreview"/> fills a
/// Guest Star's: the generated card ends its face in
/// <c>{InCombat:{StageDrainLine}|}</c> or <c>{InCombat:{StageRepay}|}</c> and
/// adds the token in <c>AddExtraArgsToDescription</c>.
///
/// THE DRAIN LINE. Since the Drain line rule (2026-10-09) a Drain may go
/// past the line, so the card says so in hand, before the play; since her HP
/// legibility pass (2026-10-19) every Drain card says where its Drain lands
/// (<see cref="FurinaStageFacePreview.DrainTag"/>). The one
/// refusal left -- a Drain to 0 HP -- reads "(Not enough HP)", because the
/// game's chooser has no greyed option
/// (<see cref="ModalChoice.SelectAffordableMode"/>). The gate is
/// <see cref="FurinaStage.CanDrain"/>, the one the play and the chooser
/// ask.
///
/// THE REPAY. A Repay with nothing drained did nothing and said nothing; the
/// face prints what it would return now, the clamp
/// <see cref="FurinaStageLedger.RepayRoom"/> applies, without moving it.
/// </summary>
public static class FurinaStageFacePreview
{
    /// <summary>"(Not enough HP)" while a Drain of <paramref name="amount"/>
    /// would take her to 0 HP; else where the Drain lands
    /// (<see cref="DrainTag"/>); then the Block the Drain pays and who pays
    /// it (<see cref="DrainBlock(int, int, bool)"/>). Empty off a combat or
    /// a Furina board.</summary>
    public static string DrainLine(CardModel card, int amount)
    {
        if (Owner(card) is not { } owner) return "";
        if (!FurinaStage.CanDrain(owner, amount)) return NotEnoughHp;
        var ledger = FurinaStageLedger.For(owner);
        var block = DrainBlock(amount, ledger.Mods.Masquerade,
                               ledger.OnStage(StagePerformer.Freminet));
        // The split the play will make (`FurinaStageLedger.NoteDrain`): the
        // part that fits in the buffer left returns, the rest is past the
        // line.
        var returns = ledger.GuestDrainRoom(amount, (int)owner.CurrentHp);
        return DrainTag(returns, amount - returns,
                        ledger.Mods.FiveCenturyAct > 0)
             + block;
    }

    /// <summary>
    /// WHERE A DRAIN LANDS (her HP legibility pass, 2026-10-19, change 2: a
    /// Drain inside the buffer carried no tag, so seats could not tell a
    /// refunded Drain from a real cost until after paying). One tag per Drain
    /// card, for <paramref name="returns"/> HP inside the buffer and
    /// <paramref name="past"/> past the line: "(Returns after combat)" all
    /// inside; "(Past your line: lost unless you Repay)" all past;
    /// "(N returns, M past your line)" split. Under A Five-Century Act
    /// (<paramref name="pastReturns"/>) the past-line part returns too, so
    /// that case keeps "(Past your Drain buffer: returns after combat)" (the
    /// Spend round, 2026-10-10). Empty for no Drain. Pure.
    /// </summary>
    public static string DrainTag(int returns, int past,
                                  bool pastReturns = false)
    {
        returns = System.Math.Max(0, returns);
        past = System.Math.Max(0, past);
        if (returns + past <= 0) return "";
        if (past == 0) return ReturnsTag;
        if (pastReturns) return PastLineReturns;
        if (returns == 0) return PastLineLost;
        return SplitTag(returns, past);
    }

    // ---- The rows (the localization census, 2026-10-23, step 2), each line
    // break the row's, each number a var.
    private const string Table = FurinaStageBowPreview.Table;
    private static readonly string DrainKey = "KLEEMOD-FACE_STAGE_DRAIN_LINE";

    internal static readonly CodeRow ReturnsRow =
        new(Table, DrainKey + ".returns", "\n(Returns after combat)");
    internal static readonly CodeRow PastLineLostRow =
        new(Table, DrainKey + ".past_lost", "\n(Past your line: lost unless you Repay)");
    internal static readonly CodeRow PastLineReturnsRow =
        new(Table, DrainKey + ".past_returns", "\n(Past your Drain buffer: returns after combat)");
    internal static readonly CodeRow SplitRow =
        new(Table, DrainKey + ".split", "\n({Returns} returns, {Past} past your line)");
    internal static readonly CodeRow NotEnoughHpRow =
        new(Table, DrainKey + ".not_enough_hp", "\n(Not enough HP)");
    /// <summary>"(+3 Block: Freminet)": the source is a name's own row.</summary>
    internal static readonly CodeRow BlockFromRow =
        new(Table, DrainKey + ".block_from", "\n(+{Block} Block: {Source})");
    /// <summary>The Masquerade's name, as the Block line names it.</summary>
    internal static readonly CodeRow MasqueradeNameRow =
        new(Table, DrainKey + ".source_masquerade", StageDirector.MasqueradeTitle);
    internal static readonly CodeRow LostRow =
        new(Table, "KLEEMOD-FACE_STAGE_LOST.description", "\n(Lost this combat: {Lost})");
    internal static readonly CodeRow NotEnoughFanfareRow =
        new(Table, "KLEEMOD-FACE_STAGE_SPEND_SHORT.description", "\n(Not enough Fanfare)");
    internal static readonly CodeRow SpendsNoHitRow =
        new(Table, "KLEEMOD-FACE_STAGE_SPEND_HITS.none", "\n(Spends {Spend}: no extra hit)");
    internal static readonly CodeRow SpendsHitsRow =
        new(Table, "KLEEMOD-FACE_STAGE_SPEND_HITS.more",
            "\n(Spends {Spend}: {Hits} more hit{Hits:plural:|s})");
    internal static readonly CodeRow SpendsAllNoHitRow =
        new(Table, "KLEEMOD-FACE_STAGE_SPEND_HITS.all_none", "\n(Spends all {Spend}: no extra hit)");
    internal static readonly CodeRow SpendsAllHitsRow =
        new(Table, "KLEEMOD-FACE_STAGE_SPEND_HITS.all_more",
            "\n(Spends all {Spend}: {Hits} more hit{Hits:plural:|s})");
    internal static readonly CodeRow RepaysRow =
        new(Table, "KLEEMOD-FACE_STAGE_REPAY.repays", "\n(Repays {Repays})");
    internal static readonly CodeRow RepayBlockRow =
        new(Table, "KLEEMOD-FACE_STAGE_REPAY.floor_block", "\n(Repay {Repays}: gain {Pays} Block)");
    internal static readonly CodeRow RepayVigorRow =
        new(Table, "KLEEMOD-FACE_STAGE_REPAY.floor_vigor", "\n(Repay {Repays}: gain {Pays} Vigor)");
    internal static readonly CodeRow RepayDamageRow =
        new(Table, "KLEEMOD-FACE_STAGE_REPAY.floor_damage", "\n(Repay {Repays}: +{Pays} damage)");

    internal static IEnumerable<CodeRow> TextRows() => new[]
    {
        ReturnsRow, PastLineLostRow, PastLineReturnsRow, SplitRow, NotEnoughHpRow, BlockFromRow,
        MasqueradeNameRow, LostRow, NotEnoughFanfareRow, SpendsNoHitRow, SpendsHitsRow,
        SpendsAllNoHitRow, SpendsAllHitsRow, RepaysRow, RepayBlockRow, RepayVigorRow, RepayDamageRow,
    };

    /// <summary>The tag for a Drain wholly inside the buffer.</summary>
    public static string ReturnsTag => CodeText.Format(ReturnsRow);

    /// <summary>The tag for a Drain wholly past the line.</summary>
    public static string PastLineLost => CodeText.Format(PastLineLostRow);

    /// <summary>The tag for a Drain that splits: "(4 returns, 2 past your
    /// line)".</summary>
    public static string SplitTag(int returns, int past) =>
        CodeText.Format(SplitRow, CodeText.Vars(("Returns", returns), ("Past", past)));

    /// <summary>
    /// THE BLOCK A DRAIN PAYS, AND WHO PAYS IT (the Spend rounds review,
    /// 2026-10-10, change 3: a seat could not tell The Masquerade's Block from
    /// Freminet's line and called The Masquerade "neutral"). "(+3 Block: The
    /// Masquerade)" for <paramref name="masquerade"/> copies of the power
    /// (each pays the HP drained), "(+3 Block: Freminet)" while Freminet is
    /// on stage (his line pays the HP drained once), one line each, in the
    /// order <see cref="StageDirector.Drain"/> pays them. Empty when neither
    /// pays. The words, for the pins and the face.
    /// </summary>
    public static string DrainBlock(int amount, int masquerade, bool freminet)
    {
        if (amount <= 0) return "";
        var words = "";
        if (masquerade > 0)
        {
            words += BlockFrom(amount * masquerade,
                               CodeText.Format(MasqueradeNameRow));
        }
        if (freminet)
        {
            words += BlockFrom(amount, PerformerWords.Name(StagePerformer.Freminet));
        }
        return words;
    }

    /// <summary>One source's line: "(+3 Block: Freminet)".</summary>
    public static string BlockFrom(int block, string source) =>
        CodeText.Format(BlockFromRow, CodeText.Vars(("Block", block), ("Source", source)));

    /// <summary>The tag under A Five-Century Act: the HP drained past the
    /// line returns after combat.</summary>
    public static string PastLineReturns => CodeText.Format(PastLineReturnsRow);

    /// <summary>FACADE'S COUNT (her HP legibility pass, 2026-10-19, change
    /// 4: a seat saw 3 Block, then 12, and could not say why): "(Lost this
    /// combat: N)", the count its Block reads
    /// (<see cref="FurinaSweep.LostThisCombat"/>). Empty off a combat or a
    /// Furina board.</summary>
    public static string LostThisCombat(CardModel card) =>
        Owner(card) is { } owner
            ? LostThisCombatWords(FurinaSweep.LostThisCombat(owner))
            : "";

    /// <summary>The words, for the pins.</summary>
    public static string LostThisCombatWords(int lost) =>
        CodeText.Format(LostRow, CodeText.Vars(("Lost", System.Math.Max(0, lost))));

    /// <summary>The refusal's words: a Drain cannot take her to 0 HP.
    /// </summary>
    public static string NotEnoughHp => CodeText.Format(NotEnoughHpRow);

    /// <summary>BACKLOG (Furina: a Spend card silently plays its plain
    /// side): "(Not enough Fanfare)" while a Spend mode's price of
    /// <paramref name="amount"/> cannot be paid, so the card says in hand
    /// that the plain side will play. The gate is
    /// <see cref="FurinaStage.CanSpend"/>, the one the chooser asks. Empty
    /// otherwise, and off a combat or a Furina board.</summary>
    public static string SpendShort(CardModel card, int amount) =>
        Owner(card) is { } owner && !FurinaStage.CanSpend(owner, amount)
            ? NotEnoughFanfare
            : "";

    /// <summary><see cref="SpendShort"/>'s words.</summary>
    public static string NotEnoughFanfare => CodeText.Format(NotEnoughFanfareRow);

    /// <summary>THE FURINA WAVE (2026-10-13, "To change now" 3): what a
    /// "Spend up to <paramref name="cap"/>: hit once more for every 4" buys
    /// now -- "(Spends 2: no extra hit)", "(Spends 6: 1 more hit)". Crashing
    /// Waves spent a bank of 2 for nothing and said nothing. Read through
    /// <see cref="FurinaStage.SpentOrUpTo"/>, the count the play takes, so
    /// the face and the play agree. Empty with nothing to spend, off a
    /// combat or a Furina board.</summary>
    public static string SpendUpToHits(CardModel card, int cap)
    {
        if (Owner(card) is not { } owner) return "";
        var spend = FurinaStage.SpentOrUpTo(card, cap);
        return SpendUpToHitsWords(spend, EmptiesBank(card, owner, spend));
    }

    /// <summary>Co-op seat (2026-10-16): "(Spends 6: 1 more hit)" took the
    /// whole bank of 6 and the next Spend card had nothing. Before the
    /// play, a spend that takes all she holds says so.</summary>
    private static bool EmptiesBank(
        CardModel card, MegaCrit.Sts2.Core.Entities.Creatures.Creature owner,
        int spend)
    {
        if (FurinaStage.Spent(card) > 0) return false;
        if (CenterOfAttentionPower.Covers(owner)) return false;
        var ledger = FurinaStageLedger.For(owner);
        return ledger.Fanfare > 0
            && spend >= ledger.Fanfare + ledger.NaviaDiscount;
    }

    /// <summary>The words, for the pins: "(Spends all 6: 1 more hit)" when
    /// <paramref name="all"/> says the spend empties the bank.</summary>
    public static string SpendUpToHitsWords(int spend, bool all = false)
    {
        if (spend <= 0) return "";
        var more = spend / FurinaStageLaw.SpendUpToEvery;
        var row = more == 0
            ? (all ? SpendsAllNoHitRow : SpendsNoHitRow)
            : (all ? SpendsAllHitsRow : SpendsHitsRow);
        return CodeText.Format(row, CodeText.Vars(("Spend", spend), ("Hits", more)));
    }

    /// <summary>The Drain tip's in-combat sentence (the pool-75 round,
    /// 2026-10-09: every record missed where the line sat): "Your Drain line
    /// is 30: your HP minus your Drain buffer: ..." (the buffer's words since
    /// 2026-10-11). Off the Drain tip since 2026-10-11.
    /// Empty off a combat or a Furina board. NOT KEYED (the localization
    /// census, 2026-10-23, step 2): no player surface prints it any more,
    /// and its <see cref="FurinaStageLaw.LineWhy"/> is the seat page's.</summary>
    public static string LineNow(CardModel card)
    {
        if (Owner(card) is not { } owner) return "";
        var ledger = FurinaStageLedger.For(owner);
        return LineNowWords(ledger.Line, ledger.LineWhy);
    }

    /// <summary>The sentence's words, for the pins.</summary>
    public static string LineNowWords(int line, string why) =>
        $"\nYour Drain line is {line}: {why}."
        // The Spend round 2 (2026-10-10): a line of 0 explains itself.
      + (line <= 0 ? " " + Capitalised(FurinaStageLaw.LineZeroReturns) + "."
                   : "");

    private static string Capitalised(string words) =>
        words.Length == 0 ? words
                          : char.ToUpperInvariant(words[0]) + words.Substring(1);

    /// <summary>"(Repays N)": what a Repay of <paramref name="amount"/>
    /// would return now. Empty off a combat or a Furina board. A Repay's
    /// floor <paramref name="payout"/> ("Block", "Vigor", "damage") leads
    /// whenever the Repay would return less than its full amount:
    /// "(Repay 0: gain 3 Block)" (furina-next paper 3, 2026-10-16: "not
    /// 'Repays 0'"; it read "(Repays 0, +3 Block)" since 2026-10-09). The
    /// Block counts Fontaine Teardrop.</summary>
    public static string Repay(CardModel card, int amount,
                               string payout = "") =>
        Owner(card) is { } owner
            ? Line(Room(owner, amount), amount, payout, PerHp(owner, payout))
            : "";

    /// <summary>What the floor pays for each HP it could not return: 1, and
    /// for the Block floor 1 more for each Fontaine Teardrop
    /// (<see cref="StageDirector.FloorBlock"/>).</summary>
    private static int PerHp(
        MegaCrit.Sts2.Core.Entities.Creatures.Creature owner, string payout) =>
        payout == PayBlock
            ? StageDirector.FloorBlock(1, FurinaStageLedger.For(owner).Mods
                                              .FontaineTeardrop)
            : 1;

    /// <summary>The Repay floor's payout words, as the faces print them.
    /// </summary>
    public const string PayBlock = "Block";

    /// <summary>Pneuma Tides' payout.</summary>
    public const string PayVigor = "Vigor";

    /// <summary>Surging Waters', Hydro Lance's and Cleansing Torrent's
    /// payout.</summary>
    public const string PayDamage = "damage";

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public static string RepayAll(CardModel card) =>
        Owner(card) is { } owner
            ? Line(Room(owner, FurinaStage.DrainedOf(owner)))
            : "";

    /// <summary>The line's words, for the pins.</summary>
    public static string Line(int repays) =>
        CodeText.Format(RepaysRow, CodeText.Vars(("Repays", repays)));

    /// <summary>The line with the Repay floor's payout, the floor first:
    /// "(Repay 1: gain 2 Block)" when a Repay of <paramref name="amount"/>
    /// returns only <paramref name="repays"/> (paper 3, 2026-10-16); the
    /// plain line when it returns all of it or there is no
    /// <paramref name="payout"/>. <paramref name="perHp"/> is what each HP
    /// left pays (2 Block with Fontaine Teardrop).</summary>
    public static string Line(int repays, int amount, string payout,
                              int perHp = 1)
    {
        if (string.IsNullOrEmpty(payout) || repays >= amount)
        {
            return Line(repays);
        }
        var pays = (amount - repays) * perHp;
        var row = payout switch
        {
            PayDamage => RepayDamageRow,
            PayVigor => RepayVigorRow,
            _ => RepayBlockRow,
        };
        return CodeText.Format(row, CodeText.Vars(("Repays", repays), ("Pays", pays)));
    }

    /// <summary>"(Repays N)" for a card that Drains
    /// <paramref name="drainFirst"/> before it Repays (Coup de Théâtre): the
    /// Repay reads the board after the card's own Drain, and names its
    /// floor's <paramref name="payout"/> the same way.</summary>
    public static string RepayAfterDrain(CardModel card, int amount,
                                         int drainFirst, string payout = "") =>
        Owner(card) is { } owner
            ? Line(Room(owner, amount, drainFirst), amount, payout,
                   PerHp(owner, payout))
            : "";

    /// <summary>What a Repay of <paramref name="amount"/> returns at this
    /// HP: never more than she drained, never past Max HP. A read; the
    /// ledger is not clamped here. <paramref name="drainFirst"/> is a Drain
    /// the same card pays before its Repay.</summary>
    public static int Room(MegaCrit.Sts2.Core.Entities.Creatures.Creature owner,
                           int amount, int drainFirst = 0)
    {
        var drained = System.Math.Min(
            FurinaStage.DrainedOf(owner) + drainFirst,
            System.Math.Max(0,
                (int)owner.MaxHp - ((int)owner.CurrentHp - drainFirst)));
        return System.Math.Max(0, System.Math.Min(amount, drained));
    }

    private static MegaCrit.Sts2.Core.Entities.Creatures.Creature? Owner(
        CardModel card) =>
        TipOwner.CreatureOf(card) is { } owner
        && owner.CombatState != null && FurinaStage.LiveFor(owner)
            ? owner
            : null;
}
