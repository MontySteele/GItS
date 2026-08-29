using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Kokomi;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Kokomi's complete personal pool.
///
/// Membership is a CORRECTNESS requirement, not bookkeeping: CardModel.Pool
/// walks ModelDb.AllCardPools and falls through to MockCardPool -- which
/// throws "You monster!" in a shipped build -- when nothing matches. That
/// fires when a card is DRAWN or previewed, not when it is played, so a
/// poolless card takes down whatever task owned the draw. See
/// tools/lint_pool_membership.py for the crash of record.
///
/// Every generated card is reward-eligible today. The off-pool split Klee and
/// Furina carry (kit cards, selector options, Guest Stars) has exactly one
/// member-in-waiting here: ceremonial_garment, her Burst, which is still
/// hand-write work. When it lands it goes in KokomiOffPoolCards, NOT in the
/// roster -- granted-not-drafted is the v1.9 kit invariant.
/// </summary>
public sealed class KokomiCardPool : CardPoolModel
{
    public override string Title => "kokomi";

    // Native frame borrowed while her art pass is outstanding, same standing
    // arrangement Furina shipped under. "silent" is the closest energy colour
    // to hydro in the base set.
    public override string EnergyColorName => "silent";

    public override string CardFrameMaterialPath => "card_frame_green";

    /// <summary>Watatsumi pearl-blue; also her NameColor and map colour, so
    /// the deck screen and the map read as the same character.</summary>
    public override Color DeckEntryCardColor => new("6FC8D6");

    public override Color EnergyOutlineColor => new("1E5A6B");

    public override bool IsColorless => false;

    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        var offered = base.FilterThroughEpochs(unlockState, cards)
            .Where(card => !KokomiOffPoolCards.Ids.Contains(card.Id));
#if PROTOTYPE_CARDS
        // QUARANTINED (sec.12.6 ITEM 15). THE ONE OFFER SEAM: this method feeds
        // GetUnlockedCards, which is the SOLE path into reward rolls, the shop
        // and card transforms (see KleeMod.PrototypeCards, layer 2), so a
        // substitution made here reaches every surface that can offer her a
        // card and no list of surfaces has to be kept in step.
        //
        // Under the memory rule the shipped Kurage's Oath would pay 5 Block per
        // MEMORY PLAY off a face that says "per Bake-Kurage pulse" -- a card
        // paying a different rule from the one it prints, which is the D4
        // defect. So the prototype row takes its place at the same rarity, cost
        // and type, and therefore at the same weight. Reasoning in full on
        // KurageMemory.SwapOfferedOath.
        offered = Powers.KurageMemory.SwapOfferedOath(offered);
#endif
        return offered;
    }

    // RosterAncientCards.Kokomi: VISIBLE in the pool (Dusty Tome draws from
    // GetUnlockedCards) but never rolled, because generation filters Ancient
    // rarity upstream. A character whose pool holds no Ancient card softlocks
    // the act-2 Darv event on an empty draw -- that is the defect this concat
    // exists to prevent, and tools/lint_ancient_coverage.py is its gate.
    protected override CardModel[] GenerateAllCards() =>
        Cards.Kokomi.Generated.KokomiCardRoster.All
            .Concat(RosterAncientCards.Kokomi)
            .Concat(KokomiOffPoolCards.All)
            .ToArray();
}

/// <summary>
/// In the pool for Pool-lookup legality, filtered out of reward rolls.
///
/// Both halves are load-bearing. IN the pool, because CardModel.Pool falls
/// through to MockCardPool and throws the moment a poolless card is drawn --
/// and the kit card is drawn, into hand, every time the meter fills. OUT of
/// rewards, because granted-not-drafted is the v1.9 kit invariant: a Burst
/// you can take from a card reward is loot, and every number on her sheet was
/// measured against a Burst you cannot.
/// </summary>
public static class KokomiOffPoolCards
{
    private static List<CardModel>? _all;
    private static HashSet<ModelId>? _ids;

    public static IReadOnlyList<CardModel> All => _all ??= BuildAll();

    public static HashSet<ModelId> Ids =>
        _ids ??= All.Select(card => card.Id).ToHashSet();

    private static List<CardModel> BuildAll()
    {
        var cards = new List<CardModel>
        {
            // Kit Burst card: granted to hand by KokomiKitGrant when the
            // meter fills, never rollable.
            ModelDb.Card<CeremonialGarment>(),
        };
        // QUARANTINED prototype rows (R213 B, EB-147). Empty in every build
        // that did not set PrototypeCards=true -- the classes are not
        // compiled. Off-pool for the reason the Burst is: Pool must resolve
        // or the card throws "You monster!" on draw, and GetUnlockedCards
        // must not see it or a reward roll could offer a card nobody ruled.
        // See KleeMod.PrototypeCards.
        var prototypes = PrototypeCards.For("kokomi");
        cards.AddRange(prototypes);
        InjectPrototypeLoc(prototypes);
        return cards;
    }

    /// <summary>
    /// QUARANTINED (sec.12.6 ITEM 14): THE PROTOTYPE OATH'S OWN DESCRIPTION
    /// CHANNEL.
    ///
    /// <c>gen_klee_cards</c> renders a Power card's description PER POWER ID,
    /// so <c>kurage_ward</c> prints ONE string -- "Each Bake-Kurage pulse also
    /// grants {X} Block." -- shared between the shipped Oath and the prototype
    /// row. Moving that string in the generator would move a SHIPPED release
    /// face and make it false with the flag off, where the ward really does
    /// still ride the pulse. So the mirror gives the prototype row its own
    /// channel here: one key, dev builds only, overriding the generated face
    /// and nothing else.
    ///
    /// THE KEY IS READ BACK OFF THE LIVE MODEL, which is R4's rule and the only
    /// way to be certain the string written is the string that will be read:
    /// BaseLib prefixes a CustomCardModel's id (KABOOM -> KLEEMOD-KABOOM), and
    /// hardcoding the unprefixed form registers against an id nothing looks up.
    ///
    /// WHY IT LIVES HERE AND NOT IN <c>KleeMod.InjectLocStrings</c> (`EB-194`).
    /// That method is a Harmony postfix on <c>LocManager.Initialize</c>, which
    /// runs during localisation bring-up -- BEFORE any mod card model exists.
    /// The generated cards are <c>autoAdd: false</c> and are constructed
    /// lazily at pool-build time, which is HERE. Calling
    /// <c>PrototypeCards.For</c> from the loc postfix forced
    /// <c>PrototypeRoster</c>'s initializer while <c>ModelDb</c> was still
    /// empty, so <c>ModelDb.Card&lt;T&gt;()</c> threw KeyNotFoundException --
    /// and a static constructor that throws POISONS ITS TYPE for the life of
    /// the process, so every later honest caller (the self-check,
    /// <c>GenerateAllCards</c> at StartRun) rethrew the cached
    /// TypeInitializationException and NO run of any character could start.
    /// The merge has to happen where the models are already built; this is that
    /// place, and it is on the run-start path so it runs before a card is seen.
    ///
    /// The 3 is [USER]'s placeholder and lives on the surface row; it is
    /// restated here because a face has to say a number, and the row and this
    /// string are owed to each other. The upgraded 5 is on the row too and has
    /// no upgrades-sheet home yet, so it is not printed.
    /// </summary>
    private static void InjectPrototypeLoc(IReadOnlyList<CardModel> prototypes)
    {
#if PROTOTYPE_CARDS
        foreach (var proto in prototypes)
        {
            if (proto is not Cards.Prototype.Generated.ProtoKuragesOathMemory)
            {
                continue;
            }
            LocManager.Instance.GetTable("cards").MergeWith(
                new Dictionary<string, string>
                {
                    [proto.Id.Entry + ".description"] =
                        "Whenever the [gold]Bake-Kurage[/gold] plays a card "
                        + "from its memory, gain 3 Block.",
                });
        }
#endif
    }
}
