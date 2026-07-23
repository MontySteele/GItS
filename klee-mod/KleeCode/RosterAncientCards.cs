using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Per-character Ancient-rarity ledger.
///
/// WHY THIS FILE EXISTS (act-2 Darv softlock, 2026-07-23): the Darv ancient
/// event rolls Dusty Tome ~50% of the time, and vanilla
/// DustyTome.SetupForPlayer draws a random CardRarity.Ancient card from the
/// character's pool -- an empty draw NREs inside the event's option
/// generation and the run softlocks on room entry. Every VISIBLE roster
/// character must therefore keep at least one Ancient card in its pool.
///
/// Safe by construction: reward rolls, transforms and shop inventory all
/// exclude CardRarity.Ancient upstream (decompiled CardFactory /
/// CardCreationOptions), so listing a card here never makes it rollable --
/// Dusty Tome is the single acquisition door, and it upgrades the grant.
///
/// GATE: tools/lint_ancient_coverage.py (validate.ps1 S6d) fails the build
/// when a character's list here is empty, unreferenced by its pool, or names
/// a class that is not CardRarity.Ancient. Adding a roster character means
/// adding a property here AND extending the lint's character table.
/// </summary>
public static class RosterAncientCards
{
    private static List<CardModel>? _klee;
    private static List<CardModel>? _furina;

    public static IReadOnlyList<CardModel> Klee => _klee ??= new List<CardModel>
    {
        ModelDb.Card<JumpyDumptyMkOmega>(),
    };

    public static IReadOnlyList<CardModel> Furina => _furina ??= new List<CardModel>
    {
        ModelDb.Card<AllTheWorldsAStage>(),
    };
}

