using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Varka;
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
    private static List<CardModel>? _kokomi;
    private static List<CardModel>? _varka;

    // THE ANCIENT AUDIT (review/active/ancient-audit-2026-10-12.md, ruled
    // 2026-10-12: "Otherwise agreed.- let's fix them all"): every kit has one
    // Dusty Tome card and one Archaic Tooth card, like the base characters
    // and Varka. The first card of each list below is the Tooth's (its
    // starter names it through BaseLib's ITranscendenceCard,
    // `gen_klee_cards.TRANSCENDENCE`), listed so its CardModel.Pool resolves
    // to the kit; the vanilla Tome skips every Tooth card, so it draws the
    // second, the card that bends one of the kit's rules.

    public static IReadOnlyList<CardModel> Klee => _klee ??= new List<CardModel>
    {
        // The Tooth's, on Jumpy Dumpty.
        ModelDb.Card<JumpyDumptyMkOmega>(),
        // The Tome's (pool completion, 2026-10-01): bends the arm's rule 2.
        ModelDb.Card<AlicesMasterpiece>(),
    };

    public static IReadOnlyList<CardModel> Furina => _furina ??= new List<CardModel>
    {
        // The Tooth's, on Rising Applause.
        ModelDb.Card<AllTheWorldsAStage>(),
        // The Tome's (pool completion, 2026-10-01): bends rule 8.
        ModelDb.Card<CenterOfAttention>(),
    };

    public static IReadOnlyList<CardModel> Kokomi => _kokomi ??= new List<CardModel>
    {
        // The Tooth's, on Kurage's Oath.
        ModelDb.Card<PrincessOfWatatsumi>(),
        // The Tome's (pool completion, 2026-10-01): bends rule 2.
        ModelDb.Card<DivineStrategy>(),
    };

    /// <summary>
    /// VARKA'S TWO (the Varka review, ruled 2026-10-12). All Four Winds is
    /// the Dusty Tome's; Dandelion Gale is the Archaic Tooth's, Windbound
    /// Execution's replacement, listed so its <c>CardModel.Pool</c> resolves
    /// to his. The vanilla Tome skips every Archaic Tooth card
    /// (<c>ArchaicTooth.TranscendenceCards</c>), so it draws All Four Winds.
    /// </summary>
    public static IReadOnlyList<CardModel> Varka => _varka ??= new List<CardModel>
    {
        ModelDb.Card<AllFourWinds>(),
        ModelDb.Card<DandelionGale>(),
    };
}

