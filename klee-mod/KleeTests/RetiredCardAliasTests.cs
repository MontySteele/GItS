using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Utils;
using BaseLib.Utils.Attributes;
using KleeMod.Cards.Retired;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-790 -- the hidden aliases for retired card ids, pinned on the four
/// properties that make them safe rather than on the ids themselves (those are
/// `docs/retired-card-ids.yaml`, gated by `tools/lint_retired_card_ids.py`).
///
/// THE DEFECT they answer: a progress save keeps a `CardStats` row and a
/// `DiscoveredCards` entry for every card a profile has ever seen, and
/// `ProgressState.FromSerializable` validates each through
/// `ModelDb.GetByIdOrNull&lt;CardModel&gt;`. A removed id fails that lookup and
/// writes a non-fatal `ValidationError` to godot.log, twice per boot, forever
/// -- the owner's own profile has carried `KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED`
/// since `EB-726` deleted the Furina reframe (`live-looks-8c`, 2026-09-16),
/// and the save is never to be edited.
///
/// THE RISK they carry: an alias is a real `CardModel` in `ModelDb`. If one
/// were ever offerable, transformable or visible, the fix would have put cut
/// cards back in the game. Each test below is one clause of "it is not".
/// </summary>
public class RetiredCardAliasTests
{
    private static IReadOnlyList<Type> AliasTypes =>
        typeof(RetiredCardAlias).Assembly
            .GetTypes()
            .Where(t => !t.IsAbstract && typeof(RetiredCardAlias).IsAssignableFrom(t))
            .OrderBy(t => t.Name)
            .ToList();

    [Fact]
    public void The_assembly_ships_aliases_at_all()
    {
        // A pin that passes because it found nothing is not a pin: every test
        // below is a `foreach`, and an empty sequence satisfies all of them.
        Assert.NotEmpty(AliasTypes);
    }

    [Fact]
    public void Every_alias_claims_one_explicit_prefixed_id()
    {
        // The id is the WHOLE point, and it is NOT derived from the class name
        // the way every other card in this mod derives its id: an alias must
        // claim an id whose class is gone, and often whose name a live class
        // has since re-used. `[CustomID]` is what BaseLib's PrefixIdPatch
        // reads first, so the literal here is what the save is matched on.
        var seen = new HashSet<string>(StringComparer.Ordinal);

        foreach (var type in AliasTypes)
        {
            var attr = type.GetCustomAttribute<CustomIDAttribute>();
            Assert.True(attr != null, $"{type.Name} has no [CustomID]");
            Assert.StartsWith("KLEEMOD-", attr!.ID, StringComparison.Ordinal);
            Assert.True(seen.Add(attr.ID),
                        $"two aliases claim {attr.ID}");
        }
    }

    [Fact]
    public void Every_alias_is_hidden_and_inert()
    {
        foreach (var type in AliasTypes)
        {
            var card = (RetiredCardAlias)Activator.CreateInstance(type);

            // Out of the compendium.
            Assert.False(card.ShouldShowInCardLibrary,
                         $"{type.Name} would show in the card library");
            // Token: the rarity this mod uses for cards machinery makes.
            Assert.Equal(CardRarity.Token, card.Rarity);
            Assert.Equal(CardType.Skill, card.Type);
            Assert.Equal(TargetType.Self, card.TargetType);
        }
    }

    [Fact]
    public void An_alias_carries_no_rule()
    {
        // A tombstone is not a resurrection. `OnPlay` stays CardModel's
        // virtual no-op, so no alias can re-implement the card that was cut --
        // which is also why the prototype quarantine (R213 B) does not need to
        // reach this directory even though aliases compile in release builds.
        var baseOnPlay = typeof(CardModel).GetMethod(
            "OnPlay", BindingFlags.Instance | BindingFlags.NonPublic);
        Assert.NotNull(baseOnPlay);

        foreach (var type in AliasTypes)
        {
            var onPlay = type.GetMethod(
                "OnPlay", BindingFlags.Instance | BindingFlags.NonPublic);
            Assert.True(onPlay!.DeclaringType == typeof(CardModel),
                        $"{type.Name} overrides OnPlay; an alias is a "
                        + "tombstone, not a card");
        }
    }

    [Fact]
    public void Pool_is_overridden_so_a_poolless_alias_cannot_throw()
    {
        // The one hazard of registering a card in no pool: `CardModel.Pool`
        // walks AllCardPools, finds nothing and falls through to MockCardPool,
        // whose generator throws InvalidOperationException("You monster!") the
        // first time a card NODE is built. Nothing can reach an alias today --
        // it is in no pool, so it is not in ModelDb.AllCards, which is the
        // only source rewards, transforms and the understudy `give:` endpoint
        // read. The override is the belt for the one strap that is not ours:
        // a RUN save whose deck still names a retired id.
        var declared = typeof(RetiredCardAlias)
            .GetProperty("Pool")!.GetGetMethod()!.DeclaringType;

        Assert.Equal(typeof(RetiredCardAlias), declared);
    }

    [Fact]
    public void No_alias_auto_registers_into_a_pool()
    {
        // BaseLib's `autoAdd` demands a [Pool] attribute and would put the
        // card in that pool -- exactly what must not happen. The constructor
        // passes autoAdd:false; this asserts the consequence rather than the
        // argument, because the consequence is what the game reads.
        foreach (var type in AliasTypes)
        {
            Assert.Null(type.GetCustomAttribute<PoolAttribute>());
        }
    }
}
