using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Screens.GameOverScreen;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Story;

/// <summary>
/// THE LINES IN COMBAT (batch 1 sec.4 and sec.5), as the game's own speech
/// bubble (<c>TalkCmd</c>, which needs a loc row: <see cref="StoryLoc"/>
/// writes them under the speaker's <c>characters</c> entry).
///
/// WHEN EACH ONE FIRES, the plainest reading of the paper's "When" column:
///   * boss fight entry: the first player turn of a combat in a boss room,
///     once a combat. With a pair partner at the table the pair exchange
///     plays instead of her solo line (partner first, each over their own
///     creature), so a fight opens on two bubbles, not three.
///   * below a third of her HP: the first time in a combat a loss takes her
///     from at least a third of her max HP to under it (<see
///     cref="StoryRules.CrossedBelowThird"/>), once a combat.
///   * the signature moment, once a combat: Klee's biggest Bomb, one Bomb
///     (not a Mine) explosion landing 30 or more (<see
///     cref="AfterBombWentOff"/>, called from <c>ProtoBombPower.Explode</c>);
///     Varka's Four Winds' Ascension (or Dandelion Gale), the moment one of
///     his table's <see cref="CharacterStory.SignatureCards"/> is played
///     (<see cref="StoryCombatHooks.AfterCardPlayed"/>).
///   * killing a boss: a boss room's combat won, while she stands.
///   * losing / winning the run: the game-over screen's quote line
///     (<see cref="NGameOverScreen_Quote_Story_Patch"/>), since a dead
///     creature cannot speak.
///
/// Visual only: nothing here moves a number, an rng or a choice, so a co-op
/// table cannot disagree about it.
/// </summary>
public static class StoryLines
{
    internal const string Table = "characters";

    public const string BossEntry = "bossEntry";
    public const string LowHp = "lowHp";
    public const string Signature = "signature";
    public const string BossKill = "bossKill";
    public const string RunLoss = "runLoss";
    public const string RunWin = "runWin";

    /// <summary>The loc key of one of a character's lines.</summary>
    public static string Key(string characterEntry, string line) =>
        $"{characterEntry}.story.{line}";

    /// <summary>The loc keys of a pair exchange, filed under the character
    /// whose table holds it (the partner speaks the first).</summary>
    public static string PairKey(string characterEntry, string partnerEntry, bool partnerSpeaks) =>
        $"{characterEntry}.story.pair.{partnerEntry}.{(partnerSpeaks ? "partner" : "own")}";

    private static readonly ConditionalWeakTable<object, CombatLatch> Latches = new();

    /// <summary>This combat's latches.</summary>
    public static CombatLatch LatchFor(object combat) => Latches.GetOrCreateValue(combat);

    /// <summary>One bubble over one creature. A dead or absent speaker says
    /// nothing (<c>TalkCmd</c>'s own guard).</summary>
    internal static void Say(Creature? speaker, string key)
    {
        if (speaker == null) return;
        try
        {
            TalkCmd.Play(new LocString(Table, key), speaker, VfxColor.White);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: line {key} not shown: {e.Message}");
        }
    }

    /// <summary>Lines one after another: each waits for the bubble before it
    /// to finish (TalkCmd's own duration rule). Never awaited by a hook.</summary>
    internal static void Sequence(params (Creature? Speaker, string Key)[] lines)
    {
        TaskHelper.RunSafely(SequenceAsync(lines));
    }

    private static async Task SequenceAsync((Creature? Speaker, string Key)[] lines)
    {
        foreach (var (speaker, key) in lines)
        {
            Say(speaker, key);
            await Cmd.Wait((float)SecondsFor(key), CancellationToken.None, ignoreCombatEnd: true);
        }
    }

    /// <summary>TalkCmd's own timing: 0.12s a printed character, 0.5s floor.</summary>
    private static double SecondsFor(string key)
    {
        var text = new LocString(Table, key).GetFormattedText();
        var raw = Regex.Replace(text, "\\[/?[^\\]]+\\]", "").Replace("\n", "").Replace(" ", "");
        return Math.Max(0.5, raw.Length * 0.12);
    }

    /// <summary>The entry block at a boss: every story character at the
    /// table speaks once, in a pair exchange where one is written for two
    /// characters here (in either one's table), else her own line
    /// (<see cref="StoryRules.BossEntryPlan"/>).</summary>
    internal static void BossEntered(IReadOnlyList<Player> players)
    {
        var plan = StoryRules.BossEntryPlan(players.Select(p => p.Character.GetType()).ToList());
        foreach (var speech in plan)
        {
            var owner = players[speech.OwnerSeat];
            var own = StoryRegistry.EntryOf(speech.Story.Character);
            if (speech.Pair == null)
            {
                Say(owner.Creature, Key(own, BossEntry));
                continue;
            }
            var partner = players[speech.PartnerSeat];
            var partnerEntry = StoryRegistry.EntryOf(speech.Pair.Partner);
            var partnerLine = (partner.Creature, PairKey(own, partnerEntry, partnerSpeaks: true));
            var ownLine = (owner.Creature, PairKey(own, partnerEntry, partnerSpeaks: false));
            if (speech.Pair.OwnFirst) Sequence(ownLine, partnerLine);
            else Sequence(partnerLine, ownLine);
        }
    }

    /// <summary>The signature line over this speaker, once a combat.</summary>
    internal static void SaySignature(Creature speaker, CharacterStory story)
    {
        if (speaker.CombatState == null) return;
        if (!LatchFor(speaker.CombatState).TryTake(speaker, Signature)) return;
        Say(speaker, Key(StoryRegistry.EntryOf(story.Character), Signature));
    }

    /// <summary>
    /// A Bomb or Mine went off (<c>ProtoBombPower.Explode</c>). The placer's
    /// line if this was one Bomb landing 30 or more, once a combat.
    /// </summary>
    public static void AfterBombWentOff(Creature applier, bool isMine, int dealt)
    {
        try
        {
            if (!StoryRules.IsBigBomb(isMine, dealt)) return;
            var story = StoryRegistry.For(applier.Player?.Character);
            if (story == null) return;
            SaySignature(applier, story);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: big Bomb line skipped: {e.Message}");
        }
    }

    /// <summary>The story Curses' clock at a combat's end (Confinement,
    /// Overdue Reports): one more combat served for every copy in every deck,
    /// and the third removes it.</summary>
    internal static async Task ServeStoryCurses(IEnumerable<Player> players)
    {
        foreach (var player in players)
        {
            var served = new List<CardModel>();
            foreach (var card in player.Deck.Cards.OfType<StoryCurse>().ToList())
            {
                card.CombatsServed += 1;
                if (StoryRules.StoryCurseServedOut(card.CombatsServed)) served.Add(card);
            }
            if (served.Count > 0) await CardPileCmd.RemoveFromDeck(served);
        }
    }
}

/// <summary>
/// The story's combat listener, on the roster's one subscription chain
/// (<c>KleeMod.Initialize</c>). Every method's first question is whether a
/// story character is in the fight, so a board without one is a walk over
/// nothing.
/// </summary>
public sealed class StoryCombatHooks : AbstractModel
{
    private static StoryCombatHooks? _instance;

    public override bool ShouldReceiveCombatHooks => true;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        StoryCombatHooks? instance;
        try
        {
            instance = _instance ??= ModelDb.GetById<StoryCombatHooks>(ModelDb.GetId<StoryCombatHooks>());
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story lines not subscribed ({e.GetType().Name}: "
                   + $"{e.Message}); the rest of the combat hooks are unaffected");
            yield break;
        }
        if (instance != null) yield return instance;
    }

    public override Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        try
        {
            var combat = player.Creature?.CombatState;
            if (combat == null || combat.RoundNumber != 1) return Task.CompletedTask;
            if (combat.Encounter?.RoomType != RoomType.Boss) return Task.CompletedTask;
            if (!StoryLines.LatchFor(combat).TryTake(combat, StoryLines.BossEntry)) return Task.CompletedTask;
            StoryLines.BossEntered(combat.Players);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: boss entry lines skipped: {e.Message}");
        }
        return Task.CompletedTask;
    }

    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        try
        {
            if (delta >= 0m || creature.CombatState == null) return Task.CompletedTask;
            var story = StoryRegistry.For(creature.Player?.Character);
            if (story == null) return Task.CompletedTask;
            var after = creature.CurrentHp;
            var before = after + (int)Math.Ceiling(-delta);
            if (!StoryRules.CrossedBelowThird(before, after, creature.MaxHp)) return Task.CompletedTask;
            if (!StoryLines.LatchFor(creature.CombatState).TryTake(creature, StoryLines.LowHp)) return Task.CompletedTask;
            StoryLines.Say(creature, StoryLines.Key(StoryRegistry.EntryOf(story.Character), StoryLines.LowHp));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: low-HP line skipped: {e.Message}");
        }
        return Task.CompletedTask;
    }

    /// <summary>The signature card's play (Varka: Four Winds' Ascension):
    /// his line, once a combat. A speech bubble only.</summary>
    public override Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        try
        {
            var owner = cardPlay.Card?.Owner;
            var speaker = owner?.Creature;
            if (owner == null || speaker == null) return Task.CompletedTask;
            var story = StoryRegistry.For(owner.Character);
            if (story == null || !StoryRules.IsSignaturePlay(story, cardPlay.Card!.GetType())) return Task.CompletedTask;
            StoryLines.SaySignature(speaker, story);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: signature line skipped: {e.Message}");
        }
        return Task.CompletedTask;
    }

    public override Task AfterCombatVictory(CombatRoom room)
    {
        try
        {
            if (room.RoomType != RoomType.Boss) return Task.CompletedTask;
            foreach (var player in room.CombatState.Players)
            {
                var story = StoryRegistry.For(player.Character);
                if (story == null) continue;
                StoryLines.Say(player.Creature,
                    StoryLines.Key(StoryRegistry.EntryOf(story.Character), StoryLines.BossKill));
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: boss line skipped: {e.Message}");
        }
        return Task.CompletedTask;
    }

    /// <summary>The story Curses' clock. <c>AfterCombatEnd</c> runs inside
    /// <c>EndCombatInternal</c>, which a lost fight never reaches -- and a
    /// lost fight is a lost run.</summary>
    public override async Task AfterCombatEnd(CombatRoom room)
    {
        try
        {
            await StoryLines.ServeStoryCurses(room.CombatState.RunState.Players);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: the story Curses' clock failed this combat: {e}");
        }
    }
}

/// <summary>
/// THE RUN'S LAST WORD: the game-over screen's quote line, which the base game
/// fills with a random quote on a loss and leaves empty on a win, before it
/// fades to the run summary's line. A story character's own line takes that
/// first place, for the player whose screen it is.
/// </summary>
[HarmonyPatch(typeof(NGameOverScreen), "InitializeBannerAndQuote")]
internal static class NGameOverScreen_Quote_Story_Patch
{
    private static readonly FieldInfo? QuoteField = AccessTools.Field(typeof(NGameOverScreen), "_deathQuote");
    private static readonly FieldInfo? HistoryField = AccessTools.Field(typeof(NGameOverScreen), "_history");
    private static readonly FieldInfo? PlayerField = AccessTools.Field(typeof(NGameOverScreen), "_localPlayer");

    [HarmonyPostfix]
    private static void Postfix(NGameOverScreen __instance)
    {
        try
        {
            if (PlayerField?.GetValue(__instance) is not Player player) return;
            var story = StoryRegistry.For(player.Character);
            if (story == null) return;
            if (HistoryField?.GetValue(__instance) is not RunHistory history) return;
            if (QuoteField?.GetValue(__instance) is not RichTextLabel quote) return;
            var line = history.Win ? StoryLines.RunWin : StoryLines.RunLoss;
            quote.Text = new LocString(StoryLines.Table,
                StoryLines.Key(StoryRegistry.EntryOf(story.Character), line)).GetFormattedText();
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: game-over line skipped: {e.Message}");
        }
    }
}
