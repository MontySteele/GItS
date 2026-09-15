using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Models.Monsters;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE BATTLEWORN DUMMY, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/BattlewornDummy.cs` and cross-checked
/// against the harvest (3 options: Setting 1, Setting 2, Setting 3).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `IsShared`, the same three
/// HP vars re-scaled for the party size and act at option-build time, the same
/// three encounters entered WITH a resume, and the same `Resume` -- the
/// defeat page when the encounter ran out of time, and otherwise the victory
/// page plus the reward that setting earns: a potion for V1, two random
/// upgrades for V2, the next relic off the front of the queue for V3.
///
/// EVERY THREE `ScaleHpForMultiplayer` CALLS PASS THE **V1** ENCOUNTER. That
/// is the base event's code, and it looks like a bug -- Setting 2 and Setting 3
/// scale their printed HP against V1's encounter rather than their own. A
/// mirror copies it: correcting it would change the numbers the page prints
/// and that is a BALANCE change, not a transcription. It is listed in the PR
/// as an observed base-game oddity, not fixed here.
///
/// THE RESUME IS WHERE THE REWARD LIVES, not the option. The options only
/// enter combat with `shouldResumeAfterCombat: true`, and `Resume` is called
/// back with the `CombatRoom` -- which is also where the encounter's
/// `RanOutOfTime` is read, and where the room's own `ExtraRewards` for this
/// player are concatenated on before the one offer.
///
/// THE POTION ROLLS OFF `PlayerRng.Rewards`, the tracked per-player reward
/// stream, not the event's `Rng`; the two upgrades shuffle on the EVENT's
/// `Rng`. Both are the base event's choice and both are kept where they are.
/// </summary>
public abstract class BattlewornDummyMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names.</summary>
    private const string Setting1HpKey = "Setting1Hp";

    private const string Setting2HpKey = "Setting2Hp";

    private const string Setting3HpKey = "Setting3Hp";

    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>`BattlewornDummy.cs:30-35`, value for value -- the three
    /// monsters' floor HP, before the party scaling below.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar(Setting1HpKey, ModelDb.Monster<BattleFriendV1>().MinInitialHp),
            new DynamicVar(Setting2HpKey, ModelDb.Monster<BattleFriendV2>().MinInitialHp),
            new DynamicVar(Setting3HpKey, ModelDb.Monster<BattleFriendV3>().MinInitialHp),
        };

    /// <summary>
    /// Three options, in the base event's order, after the three printed HP
    /// numbers are re-scaled for the party size and act.
    ///
    /// ALL THREE SCALE AGAINST THE **V1** ENCOUNTER, which is the base event's
    /// own code and is transcribed rather than corrected -- see the class
    /// comment.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        int playerCount = Owner?.RunState.Players.Count ?? 1;
        int actIndex = Owner?.RunState.CurrentActIndex ?? 0;
        DynamicVars[Setting1HpKey].BaseValue = Creature.ScaleHpForMultiplayer(
            ModelDb.Monster<BattleFriendV1>().MinInitialHp,
            ModelDb.Encounter<BattlewornDummyEventV1Encounter>(), playerCount, actIndex);
        DynamicVars[Setting2HpKey].BaseValue = Creature.ScaleHpForMultiplayer(
            ModelDb.Monster<BattleFriendV2>().MinInitialHp,
            ModelDb.Encounter<BattlewornDummyEventV1Encounter>(), playerCount, actIndex);
        DynamicVars[Setting3HpKey].BaseValue = Creature.ScaleHpForMultiplayer(
            ModelDb.Monster<BattleFriendV3>().MinInitialHp,
            ModelDb.Encounter<BattlewornDummyEventV1Encounter>(), playerCount, actIndex);

        return new List<EventOption>
        {
            new EventOption(this, Setting1, InitialOptionKey("SETTING_1")),
            new EventOption(this, Setting2, InitialOptionKey("SETTING_2")),
            new EventOption(this, Setting3, InitialOptionKey("SETTING_3")),
        };
    }

    private Task Setting1()
    {
        EnterCombatWithoutExitingEvent(
            ModelDb.Encounter<BattlewornDummyEventV1Encounter>(),
            Array.Empty<Reward>(), shouldResumeAfterCombat: true);
        return Task.CompletedTask;
    }

    private Task Setting2()
    {
        EnterCombatWithoutExitingEvent(
            ModelDb.Encounter<BattlewornDummyEventV2Encounter>(),
            Array.Empty<Reward>(), shouldResumeAfterCombat: true);
        return Task.CompletedTask;
    }

    private Task Setting3()
    {
        EnterCombatWithoutExitingEvent(
            ModelDb.Encounter<BattlewornDummyEventV3Encounter>(),
            Array.Empty<Reward>(), shouldResumeAfterCombat: true);
        return Task.CompletedTask;
    }

    /// <summary>The base event's `Resume`, branch for branch: the timer first,
    /// then the per-setting reward, then the room's own extras, then one
    /// offer if anything is in the list.</summary>
    public override async Task Resume(AbstractRoom room)
    {
        CombatRoom combatRoom = (CombatRoom)room;
        BattlewornDummyEventEncounter encounter = (BattlewornDummyEventEncounter)combatRoom.Encounter;
        if (encounter.RanOutOfTime)
        {
            SetEventFinished(L10NLookup(PageKey("DEFEAT.description")));
            return;
        }

        SetEventFinished(L10NLookup(PageKey("VICTORY.description")));
        List<Reward> rewards = new List<Reward>();
        if (encounter is BattlewornDummyEventV1Encounter)
        {
            IEnumerable<PotionModel> items =
                Owner.Character.PotionPool.GetUnlockedPotions(Owner.UnlockState)
                    .Concat(ModelDb.PotionPool<SharedPotionPool>()
                        .GetUnlockedPotions(Owner.UnlockState));
            PotionModel potion = Owner.PlayerRng.Rewards.NextItem(items);
            if (potion != null)
            {
                rewards.Add(new PotionReward(potion.ToMutable(), Owner));
            }
        }
        else if (encounter is BattlewornDummyEventV2Encounter)
        {
            IEnumerable<CardModel> pick = PileType.Deck.GetPile(Owner).Cards
                .Where((CardModel c) => c?.IsUpgradable ?? false)
                .ToList()
                .StableShuffle(Rng)
                .Take(2);
            foreach (CardModel card in pick)
            {
                CardCmd.Upgrade(card);
            }
        }
        else if (encounter is BattlewornDummyEventV3Encounter)
        {
            RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
            rewards.Add(new RelicReward(relic, Owner));
        }

        if (combatRoom.ExtraRewards.ContainsKey(Owner))
        {
            rewards = rewards.Concat(combatRoom.ExtraRewards[Owner]).ToList();
        }

        if (rewards.Count > 0)
        {
            await RewardsCmd.OfferCustom(Owner, rewards);
        }
    }
}
