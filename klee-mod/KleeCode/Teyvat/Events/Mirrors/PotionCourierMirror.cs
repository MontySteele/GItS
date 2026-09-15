using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Models.Potions;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// POTION COURIER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/PotionCourier.cs` and cross-checked
/// against the harvest (2 options: Grab Potions, Ransack).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `DynamicVar("FoulPotions", 3)`,
/// the same act gate, Foul Potion's hover tip on the first option, the same
/// three Foul Potions offered as ONE custom reward screen on Grab Potions, and
/// the same single Uncommon rolled out of the character's pool UNIONED with the
/// shared pool on Ransack.
///
/// THE GATE IS `CurrentActIndex > 0`, which is why this event is an act-2/3
/// face's and never act 1's. `RoomSet.EnsureNextEventIsValid` reads the BASE
/// event's gate before the substitution happens, so the mirror carrying the
/// same one is what makes the swap invisible.
///
/// RANSACK ROLLS OFF `PlayerRng.Rewards`, NOT THE EVENT'S `Rng` -- a per-player
/// reward stream the run DOES track, unlike the event stream This or That rolls
/// its gold on. A mirror that reached for `Rng` here would desync the reward
/// stream for every later room, which is the one RNG divergence in this surface
/// that would not stay local. It is the base event's call and it stays.
///
/// THE POTION IS NULL-GUARDED because `NextItem` over an empty sequence answers
/// null -- a character whose pool and the shared pool hold no unlocked Uncommon
/// gets the page and no reward, exactly as in the base game.
/// </summary>
public abstract class PotionCourierMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key name.</summary>
    private const string FoulPotionsKey = "FoulPotions";

    /// <summary>`PotionCourier.cs:21`, value for value -- a plain
    /// `DynamicVar`, not a canonical one, because nothing about three foul
    /// potions is a canonical quantity.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DynamicVar(FoulPotionsKey, 3m) };

    /// <summary>The base event's gate: act 2 or later.</summary>
    public override bool IsAllowed(IRunState runState) => runState.CurrentActIndex > 0;

    /// <summary>Two options, in the base event's order, with Foul Potion's
    /// hover tip on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, GrabPotions, InitialOptionKey("GRAB_POTIONS"),
                HoverTipFactory.FromPotion<FoulPotion>()),
            new EventOption(this, Ransack, InitialOptionKey("RANSACK")),
        };

    /// <summary>`GrabPotions`: `FoulPotions` Foul Potions, offered as one
    /// reward screen.</summary>
    private async Task GrabPotions()
    {
        List<Reward> rewards = new List<Reward>();
        for (int i = 0; i < DynamicVars[FoulPotionsKey].IntValue; i++)
        {
            rewards.Add(new PotionReward(ModelDb.Potion<FoulPotion>().ToMutable(), Owner));
        }

        await RewardsCmd.OfferCustom(Owner, rewards);
        SetEventFinished(L10NLookup(PageKey("GRAB_POTIONS.description")));
    }

    /// <summary>`Ransack`: one Uncommon out of the character's unlocked
    /// potions unioned with the shared pool's, rolled on the reward
    /// stream.</summary>
    private async Task Ransack()
    {
        IEnumerable<PotionModel> uncommons =
            from p in Owner.Character.PotionPool.GetUnlockedPotions(Owner.UnlockState)
                .Concat(ModelDb.PotionPool<SharedPotionPool>().GetUnlockedPotions(Owner.UnlockState))
            where p.Rarity == PotionRarity.Uncommon
            select p;
        PotionModel potion = Owner.PlayerRng.Rewards.NextItem(uncommons);
        if (potion != null)
        {
            await RewardsCmd.OfferCustom(Owner, new List<Reward>(1)
            {
                new PotionReward(potion.ToMutable(), Owner),
            });
        }

        SetEventFinished(L10NLookup(PageKey("RANSACK.description")));
    }
}
