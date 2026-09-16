using System.Collections.Generic;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Retired;

/// <summary>
/// A TOMBSTONE for a card id this mod has shipped and since removed (EB-790).
///
/// THE DEFECT. The progress save keeps a `CardStats` row and a
/// `DiscoveredCards` entry for every card the profile has ever seen, by id.
/// `ProgressState.FromSerializable` validates each one through
/// `ModelDb.GetByIdOrNull&lt;CardModel&gt;(id)` and writes a non-fatal
/// `ValidationError` to godot.log for every miss -- twice per boot, once per
/// surface. Nothing is lost (the row lands in `_unknownCardStats` and
/// `ToSerializable` concatenates it back), but the noise lands in the one file
/// the crash-log discipline says to read FIRST, and it grows by a line for
/// every prototype row this project retires. `live-looks-8c` (2026-09-16)
/// found the owner's own profile carrying `KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED`
/// -- the Furina reframe id `EB-726` deleted -- and the save is never to be
/// touched.
///
/// THE FIX. The game's own boot scan instantiates EVERY non-abstract
/// `AbstractModel` subtype it finds in a mod assembly
/// (`ModelDb.AllAbstractModelSubtypes` -&gt; `ReflectionHelper.GetSubtypesInMods`)
/// and files it in `_contentById` -- which is the dictionary
/// `GetByIdOrNull` reads. A subclass of this base, claiming the retired id
/// through BaseLib's `[CustomID]`, is therefore enough on its own: no pool
/// entry, no registration call, no patch.
///
/// WHAT AN ALIAS IS NOT, and each clause is a property of the code rather
/// than a promise:
///
/// 1. NOT OFFERED, NOT GRANTABLE. `_contentById` is NOT `ModelDb.AllCards`;
///    that walks `AllCardPools` and the starting decks. No character pool's
///    `GenerateAllCards` names an alias, so it is absent from `AllCards` --
///    which is the sole source for reward rolls
///    (`CardCreationOptions.GetPossibleCards`), for card transforms
///    (`CardFactory`), and for the understudy `give:` endpoint, which matches
///    `ModelDb.AllCards` on `Id.Entry` (`gits/GitsGiveCard.cs`, EB-52).
///
/// 2. NOT IN THE CODEX. `showInCardLibrary: false` on the constructor below.
///
/// 3. NOT A CRASH. Being in no pool is exactly the state
///    `tools/lint_pool_membership.py` exists to stop, because `CardModel.Pool`
///    falls through to `MockCardPool`, whose generator throws
///    InvalidOperationException("You monster!") the first time a card NODE is
///    built. `Pool` is `virtual`, so this base OVERRIDES it instead: an alias
///    answers with its old owner's pool without being a member of it. That
///    buys the same guarantee membership buys, and it covers the one path
///    that could still reach an alias -- a RUN save whose deck names a retired
///    id, which before this change resolved to nothing and now resolves to an
///    inert card that draws and discards. The lint knows this base BY NAME;
///    it is an exemption that is read, not a regex that silently fails to
///    match.
///
/// 4. NOT A RULE. `OnPlay` is left at `CardModel`'s virtual no-op. A tombstone
///    is not a resurrection: nothing here re-implements a cut card, which is
///    also why the prototype quarantine (R213 B) does not reach this
///    directory. Aliases compile in EVERY build, release included, because a
///    release package must validate the same save a `+proto` build wrote.
///
/// The subclasses are generated from `docs/retired-card-ids.yaml` by
/// `tools/gen_retired_card_aliases.py`; a row gets into that file
/// automatically when a card leaves a sheet (see the file's header).
/// </summary>
public abstract class RetiredCardAlias : CustomCardModel
{
    protected RetiredCardAlias()
        // Rarity Token, the rarity this mod already uses for cards that exist
        // only because machinery made them (Confiscated is Status for the same
        // reason). It weights a roll inside a pool, and an alias is in no pool.
        // autoAdd:false -- BaseLib's auto-add demands a [Pool] attribute and
        // would put the card in a pool, which is precisely what must not
        // happen. showInCardLibrary:false keeps it out of the compendium.
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self,
               showInCardLibrary: false, autoAdd: false)
    {
    }

    /// <summary>
    /// The pool the retired row used to belong to. Cosmetic: it decides a card
    /// frame and an energy icon that, by points 1 and 2 above, nobody is in a
    /// position to see. It exists so `Pool` never falls through to
    /// `MockCardPool`.
    /// </summary>
    protected abstract CardPoolModel OwnerPool { get; }

    /// <inheritdoc />
    public override CardPoolModel Pool => OwnerPool;

    /// <summary>
    /// One string pair for both surfaces, shared by every alias. BaseLib keys
    /// loc off `Id.Entry`, so this renders under each alias's own id; it is
    /// text no player can reach, and it exists so that a screen which somehow
    /// did reach one would print a sentence rather than a raw loc key.
    /// </summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Retired Card"),
        ("description", "This card was removed from the mod."),
    };
}
