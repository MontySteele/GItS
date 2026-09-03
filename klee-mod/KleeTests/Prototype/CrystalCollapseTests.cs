using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// GOROU &#8212; CRYSTAL COLLAPSE (R236): the Inazuma workshop's one Personal,
/// and the Plan clause that holds a CARD rather than a number.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the split
/// <c>KokomiPlanLedgerTests</c> makes and for the same reason. The Entry's
/// TITLE is real logic and is computed here. The capture and the free copy are
/// structural: both run through <c>CardCmd.AutoPlay</c> and a live
/// <c>ICombatState</c>, which are outside the headless boundary (README), so
/// what is pinned is that the one site that writes a Plan reads the ledger's
/// memory and that the one site that carries this clause out clones, exhausts
/// and aims. The sim twin holds the arithmetic:
/// <c>tier0/tests/test_kokomi_plan.py</c> section 6b plays the copy, proves
/// the original stayed put and proves Nereid's window doubles it.
/// </summary>
public class CrystalCollapseTests
{
    // ---- THE CLAUSE ------------------------------------------------------

    [Fact]
    public void The_plan_vocabulary_carries_the_new_kind()
    {
        // `tools/gen_klee_cards.PLAN_CLAUSE_KINDS` maps the sheet's
        // `play_copy_of_companion` onto this member by NAME, so a rename here
        // is a codegen break rather than a silent approximation.
        Assert.Contains(KokomiPlan.Kind.PlayCopyOfCompanion,
                        System.Enum.GetValues<KokomiPlan.Kind>());
    }

    [Fact]
    public void The_row_prints_exactly_one_clause_and_it_is_that_kind()
    {
        var card = new ProtoMiGorouCrystalCollapse();
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.PlayCopyOfCompanion, clause.Kind);
        // Self-facing: the copy aims itself through `FrontEnemy`, which is the
        // Plan's own reader, so the clause carries no Aim of its own.
        Assert.Equal(KokomiPlan.Aim.Self, clause.Aim);
        Assert.Null(clause.Card);       // filled in when the Plan is WRITTEN
    }

    // ---- THE CAPTURE, structural ----------------------------------------

    [Fact]
    public void Writing_a_plan_reads_the_ledgers_last_companion()
    {
        // THE CAPTURE IS AT WRITING TIME. "The last other Companion card you
        // played THIS turn" is a fact about the turn the Plan was written on,
        // and the Plan resolves on the next one -- so a read at carry-out
        // would find nothing on the usual morning.
        var schedule = typeof(KokomiPlan).GetMethod("Schedule", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "KokomiPlan.Schedule is gone -- the capture moved with it.");
        var calls = Il.Calls(schedule);
        Assert.Contains(calls, c =>
            c.Contains("LastCompanionPlayedThisTurn"));
    }

    [Fact]
    public void The_marker_power_is_what_records_the_companion()
    {
        // Rule 1 guarantees `ProtoBakeKuragePower` is on her for every turn of
        // every combat, so a per-turn fact hung off it is recorded on every
        // board. The General's Banner -- which writes the COUNT beside this --
        // is a card she may never draw.
        var hook = typeof(ProtoBakeKuragePower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "ProtoBakeKuragePower.AfterCardPlayed is gone -- Crystal "
              + "Collapse's memory had no other writer.");
        Assert.Contains("KokomiOverhaulLedger.NoteCompanionCard",
                        Il.Calls(hook));
    }

    // ---- THE FREE COPY, structural --------------------------------------

    [Fact]
    public void The_morning_clones_the_card_and_exhausts_the_copy()
    {
        // A COPY, which is the difference from Moon's Reflection's replay: the
        // caught card stays where the first play sent it. `ExhaustOnNextPlay`
        // is the game's own pile rule, so the copy is not a second permanent
        // card in the deck for one Energy.
        var play = typeof(KokomiPlan).GetMethod("PlayCopy", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "KokomiPlan.PlayCopy is gone.");
        var calls = Il.Calls(play);
        Assert.Contains(calls, c => c.Contains("CloneCard"));
        Assert.Contains(calls, c => c.Contains("ExhaustOnNextPlay"));
        Assert.Contains(calls, c => c.Contains("AutoPlay"));
        // The aim is the Plan's own reader, so a copied Attack lands where a
        // planned hit would.
        Assert.Contains(calls, c => c.Contains("FrontEnemy"));
    }

    // ---- THE STRIP -------------------------------------------------------

    [Fact]
    public void A_plan_that_holds_a_card_prints_its_label_on_the_strip()
    {
        // The wire's `queue[].name` is `Entry.Title`, and Crystal Collapse's
        // face means a different thing every time it is written -- a player
        // who cannot see which card it caught cannot plan around it.
        var held = new KokomiPlan.Entry(
            null, new[] { new KokomiPlan.Planned(
                KokomiPlan.Kind.PlayCopyOfCompanion, 0, KokomiPlan.Aim.Self) },
            "Crystal Collapse: Gorou — Juuga: Forward Unto Victory");
        Assert.Equal("Crystal Collapse: Gorou — Juuga: Forward Unto Victory",
                     held.Title);

        var empty = new KokomiPlan.Entry(
            null, System.Array.Empty<KokomiPlan.Planned>(),
            "Crystal Collapse: nothing");
        Assert.Equal("Crystal Collapse: nothing", empty.Title);

        // Every OTHER Plan is unchanged: no label, so the strip falls back to
        // the writing card's own name (null Source reads "Plan" headlessly).
        var plain = new KokomiPlan.Entry(
            null, System.Array.Empty<KokomiPlan.Planned>());
        Assert.Equal("Plan", plain.Title);
    }

    // ---- THE POOL --------------------------------------------------------

    [Fact]
    public void The_personal_is_in_the_roster_and_not_among_the_universals()
    {
        // A Personal is Kokomi's kit rather than a companion offer: it enters
        // the ROSTER (a row that never did could not be offered to its own
        // character either) and `CompanionPool` gates it by `PersonalPool`.
        var card = new ProtoMiGorouCrystalCollapse();
        Assert.Equal("kokomi", card.PersonalPool);
        Assert.Equal("inazuma", card.Nation);

        // The roster type is `internal` to the mod, so it is reached by name
        // rather than by a reference the test assembly is not entitled to.
        var rosterType = typeof(KokomiPlan).Assembly
            .GetType("KleeMod.Powers.CompanionOverhaulRoster")
            ?? throw new System.InvalidOperationException(
                "CompanionOverhaulRoster is gone -- the one wiring seam moved.");
        Assert.NotNull(rosterType.GetMethod("InazumaUniversals", HeadlessGame.All));
        Assert.NotNull(rosterType.GetMethod("InazumaPersonals", HeadlessGame.All));
        // The two lists are separate methods on purpose, and `Roster` reads
        // both -- tier0's `INAZUMA_OVERHAUL_POOL_IDS` /
        // `INAZUMA_OVERHAUL_PERSONAL_IDS` split is the same split.
        var roster = rosterType.GetMethod("Roster", HeadlessGame.All)!;
        var calls = Il.Calls(roster);
        Assert.Contains(calls, c => c.Contains("InazumaUniversals"));
        Assert.Contains(calls, c => c.Contains("InazumaPersonals"));
    }
}
