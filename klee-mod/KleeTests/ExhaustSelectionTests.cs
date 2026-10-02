using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118 — the Exhaust identity context, mod side.
///
/// Sim twin: `tier0/tests/test_exhaust_context.py`. Both suites ask the same
/// questions of the same six descriptors, and the COLUMN NAMES the two emit
/// are pinned against each other by `test_exhaust_context_parity.py`, which
/// reads `ExhaustSelection.RowKeys` out of the source.
///
/// WHAT IS REACHABLE HERE. `ExhaustSelection` is deliberately free of live
/// combat state — it records printed identity and derives integers — so every
/// behavioural fact below is tested for real, not structurally. The one thing
/// that is NOT reachable is a card actually being PLAYED (README, "The
/// headless boundary"), so the codegen's wiring of Open/Record/Close into a
/// generated `OnPlay` is pinned by its IL call set and labelled as structural.
/// </summary>
public class ExhaustSelectionTests
{
    /// <summary>A playable copy of a generated card, owned by one seat — the
    /// `PlayableCopyOfEncorePerformance` idiom (ParityAuthorityPinTests): a
    /// freshly constructed CardModel is the canonical prototype and its Owner
    /// accessors call AssertMutable, so IsMutable is set directly.</summary>
    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // --- the descriptors --------------------------------------------------

    // --- the derived reads ------------------------------------------------

    // --- THE SCOPING ------------------------------------------------------

    // --- the parity row ---------------------------------------------------

    // --- the codegen wiring (STRUCTURAL) ----------------------------------

}
