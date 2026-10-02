using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (a), second half: derivations that need a real Creature.
///
/// Everything here runs the SHIPPED method against a real game object. No
/// arithmetic is restated -- the expected values are literals, so a formula
/// change fails rather than following along.
/// </summary>
public class DerivationPinTests
{
    // ---------------------------------------------------------------
    // AUDIT FINDING H3 -- AUTHORITY PIN, NOT A FIX.
    //
    // The 2026-08-13 correctness audit found that the Fanfare ceiling is
    // computed from LIVE max HP in the mod and from the sheet's FROZEN
    // printed HP in tier0. LAW.md:189 ("Fanfare is capped at %maxHP") makes
    // the mod's live reading the authority and the sim the deviation, so
    // the repair belongs to the sim (BACKLOG EB-97, window 2).
    //
    // These tests exist to RECORD what the C# side does today, so the
    // window-2 fix has something to converge on and cannot quietly move the
    // authority while claiming to move the deviation. They must NOT be
    // "fixed" -- if EB-97 also gives the mod a named FANFARE_CAP_FRACTION
    // constant, the numbers below stay and only the expression changes.
    // ---------------------------------------------------------------


    // ---------------------------------------------------------------
    // Salon tick derivation: printed base + the Fanfare Focus term, then
    // the dry cut. SalonMemberTips and the D1 role chip both render this
    // expression, so it is the one place the six M24 numbers become
    // observable values.
    // ---------------------------------------------------------------

    // ---------------------------------------------------------------
    // EB-122: `KokomiResources.DiscardsThisTurn`, the scaling term behind
    // `what_the_tokoyo_took`.
    //
    // It is a combat HISTORY read, so the count itself needs a live
    // CombatManager and is outside the headless boundary. What IS reachable
    // is the pair of facts that decide whether it is safe to call at all --
    // CalculatedVar previews call multipliers with no combat behind them --
    // plus the structural claim that the expression is the base game's own
    // MementoMori multiplier rather than a re-derivation of it.
    // ---------------------------------------------------------------

    [Fact]
    public void Discards_this_turn_counts_this_turn_and_this_seat()
    {
        // STRUCTURAL, and labelled as such. Two clauses carry the whole
        // meaning and both are the sim's too rather than choices made here:
        // the end-of-turn hand flush does not go through CardCmd.Discard and
        // so writes no entry, and the owner filter keeps a co-op partner's
        // discards out of this card's bonus.
        var calls = Il.Calls(Il.Method("KokomiResources", "DiscardsThisTurn"));

        Assert.Contains("CombatManager.get_History", calls);
        Assert.Contains("CombatHistoryEntry.HappenedThisTurn", calls);
        Assert.Contains("CardModel.get_Owner", calls);
    }
}
