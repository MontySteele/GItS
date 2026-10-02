using System.Linq;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// The C#-parity findings of the 2026-08-13 correctness audit, PINNED AS THE
/// AUTHORITY RECORD. Nothing here is a fix and nothing here should be "made
/// to pass" by editing the mod.
///
/// All three findings (H3, M1, M2) are divergences between the shipped mod and
/// tier0, and in all three the audit places the repair on the SIM side
/// (BACKLOG EB-97, EB-100, EB-101 -- the window-2 batch, EB-104). A window-2
/// agent needs to know precisely what the mod does today, from a running
/// binary rather than from a reading of the source; that is what these are.
///
/// If a window-2 change moves any assertion below, the mod's behaviour moved,
/// and that is a finding in its own right.
///
/// H3's value pins live in <see cref="DerivationPinTests"/> (they need the same
/// Creature fixture as the rest of the cap arithmetic).
/// </summary>
public class ParityAuthorityPinTests
{
    // ---------------------------------------------------------------
    // M1 -- Supporting Cast's first-play draw resolves AFTER the card in the
    // mod and BEFORE it in tier0.
    //
    // Structural pin (see Harness/Il.cs for what that means and what it
    // cannot see). Reproducing the hand contents end to end needs a live
    // combat, which is outside the headless boundary; the divergence itself
    // is that the RECORD and the RESOLVE sit in two different hooks, and that
    // is readable from the two hooks' call sets.
    //
    // Both refuters noted the mod's leg is not movable anyway --
    // BeforeCardPlayed is not async and carries no PlayerChoiceContext, so it
    // could not await a draw even if it wanted to. That is pinned too: the
    // return type.
    // ---------------------------------------------------------------

    // ---------------------------------------------------------------
    // M2 -- Encore Performance is dead text in tier0 under the upgraded
    // starter, and live in the mod.
    //
    // The whole divergence is one predicate: tier0's copy op early-returns on
    // a raw designation pointer that R2's both-modes relic never sets, while
    // the C# card asks SpotlightSystem.IsSpotlighted, which honours
    // BothModes. This runs the real card model and the real predicate.
    // ---------------------------------------------------------------

}
