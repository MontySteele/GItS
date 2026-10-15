using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using BaseLib.Utils;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Enchantments;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Saves.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>Her seven Annotations (paper sec.2), in the order the Edit tip
/// lists them. <see cref="None"/> is "not Annotated". A saved draft and a
/// saved stack store these NUMBERS and NAMES, so neither ever changes.
/// </summary>
public enum YaeAnnotation
{
    None = 0,
    RedInk = 1,
    Footnote = 2,
    DeadlineExtension = 3,
    FoxFire = 4,
    SakuraSeal = 5,
    Royalties = 6,
    Reprint = 7,
}

/// <summary>The seven Annotations' names and rules, one table, read by the
/// Masterpiece, the Reborn faces and the Edit tip.</summary>
public static class YaeAnnotationText
{
    public static string Name(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk => "Red Ink",
        YaeAnnotation.Footnote => "Footnote",
        YaeAnnotation.DeadlineExtension => "Deadline Extension",
        YaeAnnotation.FoxFire => "Fox Fire",
        YaeAnnotation.SakuraSeal => "Sakura Seal",
        YaeAnnotation.Royalties => "Royalties",
        YaeAnnotation.Reprint => "Reprint",
        _ => "",
    };

    public static string Rule(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk =>
            $"This card deals {YaeLaw.RedInkAmount} more damage and gives "
          + $"{YaeLaw.RedInkAmount} more [gold]Block[/gold].",
        YaeAnnotation.Footnote => "When this card is played, draw 1 card.",
        YaeAnnotation.DeadlineExtension => "This card has [gold]Retain[/gold].",
        YaeAnnotation.FoxFire =>
            $"When this card is played, deal {YaeLaw.FoxFireDamage} "
          + "[gold]Electro[/gold] damage to a random enemy.",
        YaeAnnotation.SakuraSeal =>
            "When this card is played, plant a [gold]Sakura[/gold].",
        YaeAnnotation.Royalties =>
            $"When this card is played, gain {YaeLaw.RoyaltiesPayout} Energy.",
        YaeAnnotation.Reprint =>
            "The first time this card is played each combat, play it twice.",
        _ => "",
    };

    /// <summary>What an Annotation does on a SAKURA; empty for the ones with
    /// no Sakura reading. Review r3: Red Ink works on any kind (damage, each
    /// enemy's damage, or Block).</summary>
    public static string SakuraRule(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk =>
            $"The [gold]Sakura[/gold]'s action is {YaeLaw.RedInkAmount} "
          + "bigger.",
        YaeAnnotation.FoxFire =>
            "When the [gold]Sakura[/gold] acts, it also deals "
          + $"{YaeLaw.FoxFireDamage} [gold]Electro[/gold] damage to a random "
          + "enemy.",
        YaeAnnotation.DeadlineExtension =>
            "The [gold]Sakura[/gold] does not wither.",
        _ => "",
    };

    /// <summary>The seven, in the sheet's order.</summary>
    public static readonly YaeAnnotation[] All =
    {
        YaeAnnotation.RedInk, YaeAnnotation.Footnote,
        YaeAnnotation.DeadlineExtension, YaeAnnotation.FoxFire,
        YaeAnnotation.SakuraSeal, YaeAnnotation.Royalties,
        YaeAnnotation.Reprint,
    };

    /// <summary>The one Annotation's tip on the card that applies it: its
    /// card reading, or its Sakura reading on a card that Edits a Sakura.
    /// PURE.</summary>
    public static string TipBody(YaeAnnotation annotation, bool onSakura) =>
        onSakura && SakuraRule(annotation).Length > 0
            ? SakuraRule(annotation)
            : annotation == YaeAnnotation.RedInk
                ? Rule(annotation) + " " + RedInkPlantClause
                : Rule(annotation);

    /// <summary>Red Ink on a card that plants also goes to every Sakura it
    /// plants, the card keeping its own +3.</summary>
    public const string RedInkPlantClause =
        "If it plants, its [gold]Sakura[/gold] get it too.";

    /// <summary>Markup folded out, for a selection prompt. PURE.</summary>
    public static string Plain(string text) =>
        text.Replace("[gold]", "").Replace("[/gold]", "");

    /// <summary>The card reading as a clause about the card being picked.
    /// PURE.</summary>
    public static string PromptClause(YaeAnnotation annotation)
    {
        var rule = Plain(Rule(annotation)).TrimEnd('.');
        rule = rule.Replace("This card", "It").Replace("this card", "it")
                   .Replace("play it twice", "it is played twice");
        return rule.Length == 0 ? rule
            : char.ToLowerInvariant(rule[0]) + rule.Substring(1);
    }

    /// <summary>"Red Ink x2, Reprint": each distinct Annotation once, in the
    /// order first met, with its count past one. PURE.</summary>
    public static string List(IEnumerable<YaeAnnotation> layers)
    {
        var order = new List<YaeAnnotation>();
        var count = new Dictionary<YaeAnnotation, int>();
        foreach (var a in layers)
        {
            if (a == YaeAnnotation.None) continue;
            if (!count.ContainsKey(a))
            {
                order.Add(a);
                count[a] = 0;
            }
            count[a]++;
        }
        return string.Join(", ", order.Select(a =>
            count[a] > 1 ? $"{Name(a)} x{count[a]}" : Name(a)));
    }

    /// <summary>The prefix of the Masterpiece's stack line.</summary>
    public const string PublishedHead = "Published: ";

    /// <summary>The prefix of its temporary-slot line.</summary>
    public const string ThisCombatHead = "This combat: ";

    /// <summary>The line a spent Reprint adds.</summary>
    public const string ReprintUsed = "Reprint: used this combat.";

    /// <summary>
    /// THE MASTERPIECE'S HOVER (review r3: "its tip lists them"): "Published:
    /// Red Ink x2, Reprint. This combat: Footnote." and, once every Reprint
    /// on it is spent this combat, "Reprint: used this combat." The seat page
    /// reads these three heads. PURE.
    /// </summary>
    public static string Summary(IReadOnlyList<YaeAnnotation> stack,
                                 YaeAnnotation temporary, bool reprintUsed)
    {
        var parts = new List<string>();
        if (stack.Count > 0) parts.Add(PublishedHead + List(stack) + ".");
        if (temporary != YaeAnnotation.None)
            parts.Add(ThisCombatHead + Name(temporary) + ".");
        if (reprintUsed) parts.Add(ReprintUsed);
        return string.Join(" ", parts);
    }

    /// <summary>The card face's line: the Annotations that act when the
    /// card is played, golded, with their counts ("[gold]Footnote[/gold] x2.
    /// [gold]Sakura Seal[/gold]."). Empty when none does. PURE.</summary>
    public static string FaceLine(IEnumerable<YaeAnnotation> layers)
    {
        var shown = layers.Where(a => a is YaeAnnotation.Footnote
            or YaeAnnotation.FoxFire or YaeAnnotation.SakuraSeal
            or YaeAnnotation.Royalties).ToList();
        if (shown.Count == 0) return "";
        return string.Join(" ", shown.Distinct().Select(a =>
        {
            var n = shown.Count(x => x == a);
            return n > 1 ? $"[gold]{Name(a)}[/gold] x{n}." : $"[gold]{Name(a)}[/gold].";
        }));
    }
}

/// <summary>
/// THE MASTERPIECE'S ARITHMETIC (review r3, sec.2, ruled 2026-10-14), PURE,
/// so the headless suite pins it by value. Sim twin: the publishing-house
/// half of <c>tier0/engine/yae_shrine.py</c> (<c>layers</c>, <c>count</c>,
/// <c>reprint_replays</c>).
/// </summary>
public static class YaeLayers
{
    /// <summary>Every layer: the stack first, then the temporary slot.
    /// </summary>
    public static IReadOnlyList<YaeAnnotation> All(IReadOnlyList<YaeAnnotation> stack,
                                                   YaeAnnotation temporary) =>
        temporary == YaeAnnotation.None
            ? stack
            : stack.Concat(new[] { temporary }).ToList();

    /// <summary>How many layers of <paramref name="annotation"/>.</summary>
    public static int Count(IReadOnlyList<YaeAnnotation> stack, YaeAnnotation temporary,
                            YaeAnnotation annotation) =>
        stack.Count(a => a == annotation) + (temporary == annotation ? 1 : 0);

    /// <summary>
    /// REPRINT, EXACTLY: the replays this play adds. On the card's first
    /// play each combat, one per Reprint on the stack (then those are inert
    /// for the combat); plus one per ARMED temporary Reprint (an Edit arms
    /// one fresh replay; a copy's are armed).
    /// </summary>
    public static int Replays(int stackReprints, bool playedOnce, int armed) =>
        (playedOnce ? 0 : stackReprints) + Math.Max(0, armed);

    /// <summary>
    /// What Publishing a temporary Reprint does to its armed replay: before
    /// the card's first play this combat the stack now counts it, so it is
    /// dropped (never counted twice); after, it stays armed.
    /// </summary>
    public static int ArmedAfterPublish(YaeAnnotation published, bool playedOnce, int armed) =>
        published == YaeAnnotation.Reprint && !playedOnce ? 0 : armed;

    /// <summary>"Reprint: used": the card carries a Reprint and has no
    /// replay left this combat.</summary>
    public static bool ReprintUsed(int reprints, bool playedOnce, int armed) =>
        reprints > 0 && playedOnce && armed <= 0;
}

/// <summary>
/// A TEXT VAR: the Masterpiece's summary as a description placeholder. The
/// game's SmartFormat writes a placeholder with no format through the
/// object's own <c>ToString()</c> (<c>DynamicVar</c> is not
/// <c>IFormattable</c>), so this var prints its owner's words rather than a
/// number. Its number is 0 and nothing reads it.
/// </summary>
public sealed class YaeTextVar : DynamicVar
{
    private readonly Func<YaeMasterpiece, string> _text;

    public YaeTextVar(string name, Func<YaeMasterpiece, string> text)
        : base(name, 0m)
    {
        _text = text;
    }

    public override string ToString() =>
        _owner is YaeMasterpiece m ? _text(m) : "";
}

/// <summary>
/// THE MASTERPIECE (review r3, sec.2, ruled 2026-10-14: "One custom
/// enchantment holds both layers; its tip lists them"). Every Annotated card
/// carries this one enchantment:
///
///   * THE PERMANENT STACK (<see cref="Published"/>): every Published
///     Annotation, kept for the run. A <c>[SavedProperty]</c>, so the deck
///     card's save keeps it.
///   * ONE TEMPORARY SLOT (<see cref="Temporary"/>): a combat Edit fills it
///     and another Edit replaces it; it never touches the stack and is never
///     saved (a deck card never carries one).
///   * PUBLISHING moves the temporary layer onto the stack, once.
///
/// Stacked Annotations add up: Red Ink +3 each (Sharp's and Nimble's
/// doors), Footnote, Fox Fire, Sakura Seal and Royalties once each when the
/// card is played (after its own effects, <c>CardModel.OnPlayWrapper</c>),
/// Deadline Extension Retain. REPRINT per <see cref="YaeLayers.Replays"/>.
///
/// A change of layers swaps in a fresh model (<see cref="YaeEditing.Apply"/>)
/// so the card redraws its enchantment exactly as an Edit always did; the
/// Reprint state rides across the swap. Sim twin: the publishing-house half
/// of <c>tier0/engine/yae_shrine.py</c>.
/// </summary>
public sealed class YaeMasterpiece : CustomEnchantmentModel, ILocalizationProvider
{
    /// <summary>The hover's text var.</summary>
    public const string LayersKey = "Layers";

    /// <summary>The card face's text var.</summary>
    public const string FaceKey = "Face";

    /// <summary>The hover title.</summary>
    public const string Title = "Annotated";

    private int[] _published = Array.Empty<int>();
    private YaeAnnotation _temporary;
    private bool _playedOnce;
    private int _armed;

    public List<(string, string)>? Localization => new()
    {
        ("title", Title),
        ("description", "{" + LayersKey + "}"),
        ("extraCardText", "{" + FaceKey + "}"),
    };

    /// <summary>The permanent stack, as saved: each layer's number, oldest
    /// first.</summary>
    [SavedProperty]
    public int[] Published
    {
        get => _published;
        set
        {
            AssertMutable();
            _published = value ?? Array.Empty<int>();
        }
    }

    /// <summary>The permanent stack, oldest first.</summary>
    public IReadOnlyList<YaeAnnotation> Stack =>
        _published.Select(n => Enum.IsDefined(typeof(YaeAnnotation), n)
                ? (YaeAnnotation)n : YaeAnnotation.None)
            .Where(a => a != YaeAnnotation.None).ToList();

    /// <summary>The temporary slot (this combat's Edit), or none.</summary>
    public YaeAnnotation Temporary
    {
        get => _temporary;
        internal set
        {
            AssertMutable();
            _temporary = value;
        }
    }

    /// <summary>Played this combat: the stack's Reprints are inert.</summary>
    public bool PlayedOnce => _playedOnce;

    /// <summary>Fresh replays from a temporary Reprint.</summary>
    public int Armed => _armed;

    /// <summary>Every layer, the stack first.</summary>
    public IReadOnlyList<YaeAnnotation> Layers => YaeLayers.All(Stack, _temporary);

    /// <summary>How many layers of <paramref name="annotation"/>.</summary>
    public int Count(YaeAnnotation annotation) =>
        YaeLayers.Count(Stack, _temporary, annotation);

    /// <summary>"Reprint: used this combat."</summary>
    public bool ReprintSpent =>
        YaeLayers.ReprintUsed(Count(YaeAnnotation.Reprint), _playedOnce, _armed);

    /// <summary>Set the layers and the Reprint state (a fresh model only).
    /// </summary>
    internal void Set(IEnumerable<YaeAnnotation> stack, YaeAnnotation temporary,
                      bool playedOnce, int armed)
    {
        AssertMutable();
        _published = stack.Where(a => a != YaeAnnotation.None).Select(a => (int)a).ToArray();
        _temporary = temporary;
        _playedOnce = playedOnce;
        _armed = Math.Max(0, armed);
    }

    /// <summary>A copy is a new card: its Reprints are armed (review r3).
    /// </summary>
    internal void ArmAsCopy()
    {
        AssertMutable();
        _playedOnce = false;
        _armed = _temporary == YaeAnnotation.Reprint ? 1 : 0;
        Status = EnchantmentStatus.Normal;
    }

    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new YaeTextVar(LayersKey, m => m.SummaryText),
        new YaeTextVar(FaceKey, m => YaeAnnotationText.FaceLine(m.Layers)),
    };

    /// <summary>The hover's words.</summary>
    public string SummaryText =>
        YaeAnnotationText.Summary(Stack, _temporary, ReprintSpent);

    /// <summary>The face shows the layers that act when it is played.
    /// </summary>
    public override bool HasExtraCardText =>
        YaeAnnotationText.FaceLine(Layers).Length > 0;

    /// <summary>The icon shows how many layers once there are two.</summary>
    public override bool ShowAmount => Layers.Count > 1;

    public override int DisplayAmount => Layers.Count;

    /// <summary>The Masterpiece rides any card an Edit can reach; the Edit's
    /// own filter (<see cref="YaeEditing.Editable"/>) is the rule.</summary>
    public override bool CanEnchantCardType(CardType cardType) => true;

    /// <summary>Each distinct layer's own rule, under the summary.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        YaeAnnotationText.All.Where(a => Count(a) > 0).Select(a => (IHoverTip)new HoverTip(
            new LocString(Cards.ArmKeywordTips.KeywordTable, Cards.ArmKeywordTips.KeyOf(a) + ".title"),
            YaeAnnotationText.Rule(a))).ToList();

    /// <summary>The newest layer's borrowed base-game icon (Reprint first,
    /// the one a player watches), else the engine's missing-icon fallback.
    /// Placeholder art.</summary>
    protected override string? CustomIconPath
    {
        get
        {
            var layers = Layers;
            if (layers.Count == 0) return null;
            var shown = layers.Contains(YaeAnnotation.Reprint)
                ? YaeAnnotation.Reprint : layers[layers.Count - 1];
            foreach (var path in IconCandidates(shown))
            {
                try
                {
                    if (ResourceLoader.Exists(path)) return path;
                }
                catch (Exception)
                {
                    return null;
                }
            }
            return null;
        }
    }

    /// <summary>The base enchantment icon each Annotation borrows.</summary>
    public static string IconEntry(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk => "sharp",
        YaeAnnotation.Footnote => "swift",
        YaeAnnotation.DeadlineExtension => "steady",
        YaeAnnotation.FoxFire => "imbued",
        YaeAnnotation.SakuraSeal => "sown",
        _ => "glam",
    };

    private static IEnumerable<string> IconCandidates(YaeAnnotation annotation) => new[]
    {
        $"res://images/enchantments/{IconEntry(annotation)}.png",
        $"res://images/enchantments/beta/{IconEntry(annotation)}.png",
    };

    /// <summary>Deadline Extension: Retain, Steady's way (the keyword, added
    /// on enchant; <see cref="YaeEditing.Clear"/> takes it back).</summary>
    protected override void OnEnchant()
    {
        if (Count(YaeAnnotation.DeadlineExtension) > 0) Card.AddKeyword(CardKeyword.Retain);
        RefreshStatus();
    }

    /// <summary>Red Ink: 3 more damage per hit for each layer (a powered
    /// attack only).</summary>
    public override decimal EnchantDamageAdditive(decimal originalDamage, ValueProp props) =>
        props.IsPoweredAttack() ? YaeLaw.RedInkAmount * Count(YaeAnnotation.RedInk) : 0m;

    /// <summary>Red Ink: 3 more Block per gain for each layer.</summary>
    public override decimal EnchantBlockAdditive(decimal originalBlock) =>
        YaeLaw.RedInkAmount * Count(YaeAnnotation.RedInk);

    /// <summary>The play riders, one per layer, the stack first.</summary>
    public override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)
    {
        var owner = Card.Owner;
        foreach (var layer in Layers)
        {
            switch (layer)
            {
                case YaeAnnotation.Footnote:
                    if (owner != null) await CardPileCmd.Draw(choiceContext, 1, owner);
                    break;
                case YaeAnnotation.FoxFire:
                    await YaeShrine.FoxFire(choiceContext, owner?.Creature);
                    break;
                case YaeAnnotation.SakuraSeal:
                    await YaeShrine.Plant(choiceContext, owner?.Creature, 1);
                    break;
                case YaeAnnotation.Royalties:
                    if (owner != null) await PlayerCmd.GainEnergy(YaeLaw.RoyaltiesPayout, owner);
                    break;
            }
        }
    }

    /// <summary>REPRINT (<see cref="YaeLayers.Replays"/>).</summary>
    public override int EnchantPlayCount(int originalPlayCount) =>
        originalPlayCount
        + YaeLayers.Replays(Stack.Count(a => a == YaeAnnotation.Reprint), _playedOnce, _armed);

    /// <summary>After this card's play: the stack's Reprints go inert for
    /// the combat and an armed replay is spent.</summary>
    public override Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card != Card) return Task.CompletedTask;
        _playedOnce = true;
        _armed = 0;
        RefreshStatus();
        return Task.CompletedTask;
    }

    /// <summary>The greyed tab: only when every layer is a spent Reprint
    /// (nothing on the card does anything more this combat).</summary>
    private void RefreshStatus()
    {
        if (!IsMutable) return;
        Status = ReprintSpent && Layers.All(a => a == YaeAnnotation.Reprint)
            ? EnchantmentStatus.Disabled : EnchantmentStatus.Normal;
    }
}

/// <summary>
/// THE PUBLISHING HOUSE (paper sec.2; review r3's two layers): Edit, the
/// Annotated read, Publish, the drafts the after-elite Publish reads, and
/// the signature cards. Sim twin: the publishing-house half of
/// <c>tier0/engine/yae_shrine.py</c>.
/// </summary>
public static class YaeEditing
{
    private const string Table = "cards";

    /// <summary>The Edit selection's prompt (merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>).</summary>
    public const string EditPromptKey = "KLEEMOD-YAE_EDIT.selectionScreenPrompt";

    public const string EditPromptText = "Choose a card to Edit.";

    /// <summary>Each Annotation's own Edit prompt.</summary>
    public static string EditPromptKeyFor(YaeAnnotation annotation) =>
        annotation == YaeAnnotation.None
            ? EditPromptKey
            : "KLEEMOD-YAE_EDIT_" + annotation.ToString().ToUpperInvariant()
              + ".selectionScreenPrompt";

    /// <summary>"Choose a card to Edit: Red Ink (it deals 3 more damage and
    /// gives 3 more Block)." PURE.</summary>
    public static string EditPromptTextFor(YaeAnnotation annotation) =>
        annotation == YaeAnnotation.None
            ? EditPromptText
            : $"Choose a card to Edit: {YaeAnnotationText.Name(annotation)} "
              + $"({YaeAnnotationText.PromptClause(annotation)}). "
              + ReplacesWarning;

    /// <summary>Yae review r4, pick 1 (a) (ruled 2026-10-15): a multi-card
    /// Edit's one chooser, "Edit up to N cards". The game fills
    /// <c>{Amount}</c> from the selector's max.</summary>
    public static string EditUpToPromptKeyFor(YaeAnnotation annotation) =>
        "KLEEMOD-YAE_EDIT_UPTO_" + annotation.ToString().ToUpperInvariant()
        + ".selectionScreenPrompt";

    /// <summary>"Choose up to {Amount} cards to Edit: Red Ink (...)." PURE.
    /// </summary>
    public static string EditUpToPromptTextFor(YaeAnnotation annotation) =>
        $"Choose up to {{Amount}} cards to Edit: {YaeAnnotationText.Name(annotation)} "
        + $"({YaeAnnotationText.PromptClause(annotation)}). "
        + ReplacesWarning;

    /// <summary>The Edit chooser's terms. One card: exactly one, as before.
    /// Several: ONE chooser of zero to <paramref name="times"/> cards, so
    /// the player may stop rather than overwrite an Annotation (GPT, relayed
    /// by [USER], 2026-10-15). A hand chooser picks distinct cards. PURE.
    /// </summary>
    public static CardSelectorPrefs EditPrefs(YaeAnnotation annotation, int times) =>
        times <= 1
            ? new CardSelectorPrefs(new LocString(Table, EditPromptKeyFor(annotation)), 1)
            : new CardSelectorPrefs(new LocString(Table, EditUpToPromptKeyFor(annotation)), 0, times)
            {
                RequireManualConfirmation = true,
            };

    /// <summary>What a multi-card Edit annotates out of the chooser's
    /// answer: each card once, in pick order, at most
    /// <paramref name="times"/>. PURE.</summary>
    public static List<CardModel> EditTargets(IEnumerable<CardModel>? picked, int times)
    {
        var targets = new List<CardModel>();
        if (picked == null) return targets;
        foreach (var card in picked)
        {
            if (targets.Count >= times) break;
            if (card == null || targets.Any(t => ReferenceEquals(t, card))) continue;
            targets.Add(card);
        }
        return targets;
    }

    /// <summary>Yae review r4, item 6: the Edit chooser's warning. The hand
    /// shows each card's current Annotation; this says the Edit overwrites
    /// an unpublished one (a Published stack stays).</summary>
    public const string ReplacesWarning =
        "It replaces any unpublished Annotation the card carries.";

    /// <summary>Yae review r4, item 8: what an Edit says when it has nothing
    /// to Edit (a bubble over Yae).</summary>
    public const string NothingToEditKey = "KLEEMOD-YAE_EDIT_NOTHING.bubble";

    public const string NothingToEditText = "Nothing to Edit.";

    public const string NoSakuraToEditKey = "KLEEMOD-YAE_EDIT_NOSAKURA.bubble";

    public const string NoSakuraToEditText = "No Sakura to Edit.";

    /// <summary>The bubble itself; a missing bubble never breaks a play.
    /// </summary>
    public static void SayNothing(Creature? yae, string key)
    {
        if (yae == null) return;
        try
        {
            TalkCmd.Play(new LocString(Table, key), yae, VfxColor.White);
        }
        catch (Exception)
        {
        }
    }

    /// <summary>The Seven Glamours' prompt.</summary>
    public const string PublishPromptKey = "KLEEMOD-YAE_PUBLISH.selectionScreenPrompt";

    public const string PublishPromptText = "Choose a card to Publish.";

    /// <summary>Reborn as Guuji Yae's prompt.</summary>
    public const string AnnotationPromptKey = "KLEEMOD-YAE_ANNOTATION.selectionScreenPrompt";

    public const string AnnotationPromptText = "Choose an Annotation.";

    /// <summary>Second Printing's prompt (review r3).</summary>
    public const string RecallPromptKey = "KLEEMOD-YAE_RECALL.selectionScreenPrompt";

    public const string RecallPromptText = "Choose an Annotated card to put into your hand.";

    /// <summary>Author's Copy's prompt (review r3).</summary>
    public const string CopyPromptKey = "KLEEMOD-YAE_COPY.selectionScreenPrompt";

    public const string CopyPromptText = "Choose an Annotated card to copy.";

    /// <summary>
    /// THE DRAFT (pick 2 (a), ruled): the temporary layer a deck card's
    /// combat copy carried, kept on the DECK card and saved with it, so a
    /// save and load between the fight and its reward screen keeps it.
    /// Written at every Edit and rewritten at the end of every fight
    /// (<see cref="SnapshotDrafts"/>). The value is a
    /// <see cref="YaeAnnotation"/>'s NAME; null writes nothing.
    /// </summary>
    private static readonly SavedSpireField<CardModel, string?> Drafts =
        new(() => null, "KleeMod_YaeDraft");

    /// <summary>The draft a deck card holds. PURE over the field.</summary>
    public static YaeAnnotation Draft(CardModel? deckCard) =>
        deckCard == null ? YaeAnnotation.None : ParseDraft(Drafts.Get(deckCard));

    /// <summary>A saved draft back to its Annotation; anything unknown is
    /// none. PURE.</summary>
    public static YaeAnnotation ParseDraft(string? saved) =>
        Enum.TryParse<YaeAnnotation>(saved, out var a)
        && Enum.IsDefined(typeof(YaeAnnotation), a)
            ? a : YaeAnnotation.None;

    /// <summary>Record a draft on a deck card.</summary>
    public static void RecordDraft(CardModel deckCard, YaeAnnotation annotation) =>
        Drafts.Set(deckCard, annotation == YaeAnnotation.None ? null : annotation.ToString());

    /// <summary>The card's Masterpiece, or null.</summary>
    public static YaeMasterpiece? Masterpiece(CardModel? card) =>
        card?.Enchantment as YaeMasterpiece;

    /// <summary>Every layer the card carries, the stack first. PURE.</summary>
    public static IReadOnlyList<YaeAnnotation> Layers(CardModel? card) =>
        Masterpiece(card)?.Layers ?? Array.Empty<YaeAnnotation>();

    /// <summary>The permanent stack. PURE.</summary>
    public static IReadOnlyList<YaeAnnotation> Stack(CardModel? card) =>
        Masterpiece(card)?.Stack ?? Array.Empty<YaeAnnotation>();

    /// <summary>The temporary slot. PURE.</summary>
    public static YaeAnnotation Temporary(CardModel? card) =>
        Masterpiece(card)?.Temporary ?? YaeAnnotation.None;

    /// <summary>How many layers of <paramref name="annotation"/>. PURE.
    /// </summary>
    public static int Count(CardModel? card, YaeAnnotation annotation) =>
        Masterpiece(card)?.Count(annotation) ?? 0;

    /// <summary>"Annotated means carrying any Annotation, a Published one
    /// included." PURE.</summary>
    public static bool IsAnnotated(CardModel? card) => Layers(card).Count > 0;

    /// <summary>Does the card carry a Published layer? PURE.</summary>
    public static bool Published(CardModel? card) => Stack(card).Count > 0;

    /// <summary>
    /// "Edit a card in your hand: never the Edit card itself, never a Status
    /// or Curse, never a kit card." PURE.
    /// </summary>
    public static bool Editable(CardModel candidate, CardModel? editor) =>
        !ReferenceEquals(candidate, editor)
        && candidate.Type != CardType.Status
        && candidate.Type != CardType.Curse
        && candidate.Type != CardType.Quest;

    /// <summary>
    /// The cards an Edit (the chooser and Reborn as Guuji Yae) can reach:
    /// <see cref="Editable"/>, and never one the Annotation would do nothing
    /// on (the dead-edit filter). A PUBLISHED card is reachable (review r3,
    /// pick 2 (a), replacing #1308's skip): the Edit fills its temporary
    /// slot. PURE.
    /// </summary>
    public static bool EditReaches(CardModel candidate, CardModel? editor,
                                   YaeAnnotation annotation) =>
        Editable(candidate, editor)
        && YaeAnnotationReach.Affects(candidate, annotation);

    /// <summary>
    /// Clear whatever Enchantment the card carries, taking back the Retain a
    /// Deadline Extension added unless the card prints Retain itself.
    /// </summary>
    public static void Clear(CardModel card)
    {
        var had = card.Enchantment;
        if (had == null) return;
        CardCmd.ClearEnchantment(card);
        if (had is YaeMasterpiece m && m.Count(YaeAnnotation.DeadlineExtension) > 0
            && !card.CanonicalKeywords.Contains(CardKeyword.Retain))
        {
            card.RemoveKeyword(CardKeyword.Retain);
        }
        card.DynamicVars.RecalculateForUpgradeOrEnchant();
    }

    /// <summary>
    /// Give <paramref name="card"/> these layers: a fresh Masterpiece carrying
    /// <paramref name="stack"/> and <paramref name="temporary"/>, the Reprint
    /// state given, swapped in for whatever it wore (so the card redraws it).
    /// No layer at all leaves the card plain.
    /// </summary>
    public static bool Apply(CardModel card, IEnumerable<YaeAnnotation> stack,
                             YaeAnnotation temporary, bool playedOnce, int armed)
    {
        var layers = stack.Where(a => a != YaeAnnotation.None).ToList();
        Clear(card);
        if (layers.Count == 0 && temporary == YaeAnnotation.None) return true;
        var model = (YaeMasterpiece)ModelDb.Enchantment<YaeMasterpiece>().ToMutable();
        model.Set(layers, temporary, playedOnce, armed);
        if (!model.CanEnchant(card)) return false;
        CardCmd.Enchant(model, card, 1m);
        return true;
    }

    /// <summary>
    /// AN EDIT: <paramref name="annotation"/> fills the card's temporary
    /// slot, replacing what was there; the stack is never touched. A
    /// temporary Reprint arms one fresh replay. A combat card also writes
    /// its deck card's draft, which is what the after-elite Publish reads.
    /// </summary>
    public static bool Annotate(CardModel card, YaeAnnotation annotation,
                                bool recordDraft = true)
    {
        if (annotation == YaeAnnotation.None) return false;
        var had = Masterpiece(card);
        if (!Apply(card, Stack(card), annotation, had?.PlayedOnce ?? false,
                   annotation == YaeAnnotation.Reprint ? 1 : 0))
        {
            return false;
        }
        if (recordDraft && card.DeckVersion is { } deck)
        {
            RecordDraft(deck, annotation);
        }
        return true;
    }

    /// <summary>
    /// "Edit a card in your hand: &lt;Annotation&gt;" (one card, which the
    /// player must pick) or "Edit up to N cards in your hand" (Yae review
    /// r4, pick 1 (a), ruled 2026-10-15): ONE chooser of up to
    /// <paramref name="times"/> different cards, which the player may stop
    /// short of, none included. A Published card is reachable
    /// (<see cref="EditReaches"/>). Nothing qualifies: it says so, unless
    /// <paramref name="sayNothing"/> is false (Inked Branches+ after it
    /// Edited a Sakura, Yae review r5, item 2).
    /// </summary>
    public static async Task Edit(PlayerChoiceContext choiceContext,
                                  CardModel editor, YaeAnnotation annotation,
                                  int times, bool sayNothing = true)
    {
        var owner = editor.Owner;
        if (owner?.Creature == null || times <= 0) return;
        if (!PileType.Hand.GetPile(owner).Cards.Any(c => EditReaches(c, editor, annotation)))
        {
            if (sayNothing) SayNothing(owner.Creature, NothingToEditKey);
            return;
        }
        var picked = await CardSelectCmd.FromHand(
            choiceContext, owner, EditPrefs(annotation, times),
            c => EditReaches(c, editor, annotation),
            editor);
        foreach (var card in EditTargets(picked, times))
        {
            if (!Annotate(card, annotation)) continue;
            YaeShrineLedger.For(owner.Creature).NoteEdit();
        }
    }

    /// <summary>
    /// Reborn as Guuji Yae: "Choose an Annotation. Edit every other card in
    /// your hand with it." The sim's pilot takes the row's printed default,
    /// Sakura Seal.
    /// </summary>
    public static async Task EditAll(PlayerChoiceContext choiceContext,
                                     CardModel editor, YaeAnnotation fallback)
    {
        var owner = editor.Owner;
        if (owner?.Creature == null) return;
        var chosen = await Cards.Prototype.YaeModalOptions.Choose(
            choiceContext, owner);
        if (chosen == YaeAnnotation.None) chosen = fallback;
        var cards = PileType.Hand.GetPile(owner).Cards
            .Where(c => EditReaches(c, editor, chosen))
            .ToList();
        if (cards.Count == 0) SayNothing(owner.Creature, NothingToEditKey);
        var n = 0;
        foreach (var card in cards)
        {
            if (Annotate(card, chosen)) n++;
        }
        for (var i = 0; i < n; i++) YaeShrineLedger.For(owner.Creature).NoteEdit();
    }

    /// <summary>
    /// "A Published Annotation lasts the rest of the run": added to the
    /// DECK card's stack, which the run save keeps. Stacks grow (review r3).
    /// </summary>
    public static bool PublishToDeck(CardModel deckCard, YaeAnnotation annotation) =>
        annotation != YaeAnnotation.None
        && Apply(deckCard, Stack(deckCard).Concat(new[] { annotation }),
                 YaeAnnotation.None, false, 0);

    /// <summary>
    /// PUBLISH IN COMBAT: the card's temporary layer moves onto its own
    /// stack, once (<see cref="YaeLayers.ArmedAfterPublish"/> keeps a Reprint
    /// from counting twice). Returns what moved.
    /// </summary>
    public static YaeAnnotation PublishLayer(CardModel card)
    {
        var m = Masterpiece(card);
        if (m == null || m.Temporary == YaeAnnotation.None) return YaeAnnotation.None;
        var moved = m.Temporary;
        Apply(card, m.Stack.Concat(new[] { moved }), YaeAnnotation.None,
              m.PlayedOnce, YaeLayers.ArmedAfterPublish(moved, m.PlayedOnce, m.Armed));
        return moved;
    }

    /// <summary>
    /// The Seven Glamours (2026-10-15): "If this kills an enemy, Publish an
    /// Annotated card in your hand." The player picks one card with a
    /// temporary layer and a deck card (no chooser when there is only one):
    /// the layer joins the combat card's stack and the deck card's. Was every
    /// such card (Yae review r4, item 5), which [USER] ruled OP.
    /// </summary>
    public static async Task PublishFromHand(PlayerChoiceContext choiceContext,
                                             CardModel editor)
    {
        var owner = editor.Owner;
        if (owner == null) return;
        var cands = PileType.Hand.GetPile(owner).Cards
            .Where(c => PublishReaches(c, editor))
            .ToList();
        if (cands.Count == 0) return;
        var picked = cands.Count == 1
            ? cands[0]
            : (await CardSelectCmd.FromHand(
                choiceContext, owner,
                new CardSelectorPrefs(new LocString(Table, PublishPromptKey), 1),
                c => PublishReaches(c, editor),
                editor)).FirstOrDefault();
        if (picked?.DeckVersion is not { } deck) return;
        var moved = PublishLayer(picked);
        if (moved == YaeAnnotation.None) return;
        PublishToDeck(deck, moved);
        RecordDraft(deck, YaeAnnotation.None);
    }

    /// <summary>What The Seven Glamours can Publish: a card in hand an Edit
    /// reaches, with a temporary layer and a deck card. PURE.</summary>
    public static bool PublishReaches(CardModel card, CardModel? editor) =>
        Editable(card, editor) && Temporary(card) != YaeAnnotation.None
        && card.DeckVersion != null;

    // ---- The signature cards (review r3, sec.3) ---------------------------

    /// <summary>
    /// Second Printing: "Put an Annotated card from your Discard Pile into
    /// your hand. [It costs 0 this turn.]"
    /// </summary>
    public static async Task SecondPrinting(PlayerChoiceContext choiceContext,
                                            CardModel editor, bool free)
    {
        var owner = editor.Owner;
        if (owner == null) return;
        var discard = PileType.Discard.GetPile(owner);
        if (!discard.Cards.Any(IsAnnotated)) return;
        var picked = (await CardSelectCmd.FromCombatPile(
            choiceContext, discard, owner,
            new CardSelectorPrefs(new LocString(Table, RecallPromptKey), 1),
            IsAnnotated)).FirstOrDefault();
        if (picked == null) return;
        await CardPileCmd.Add(picked, PileType.Hand);
        if (free) picked.EnergyCost.SetThisTurn(0);
    }

    /// <summary>Serial Novel: <paramref name="n"/> random Annotated cards
    /// from the Discard Pile into the hand, one at a time.</summary>
    public static async Task RecallRandomAnnotated(Player player, int n)
    {
        var rng = player.RunState.Rng.CombatCardSelection;
        for (var i = 0; i < n; i++)
        {
            var cands = PileType.Discard.GetPile(player).Cards.Where(IsAnnotated).ToList();
            if (cands.Count == 0) return;
            await CardPileCmd.Add(rng.NextItem(cands), PileType.Hand);
        }
    }

    /// <summary>
    /// What Author's Copy can copy: an Annotated card in hand, never itself
    /// and never an Author's Copy (review r3: LAW, "copy effects never make
    /// an energy-positive loop"; an Author's Copy+ with Royalties copied by
    /// another made +1 Energy a turn). PURE.
    /// </summary>
    public static bool CopyReaches(CardModel candidate, CardModel? editor) =>
        !ReferenceEquals(candidate, editor)
        && !IsAuthorsCopy(candidate)
        && IsAnnotated(candidate);

    /// <summary>Is this card an Author's Copy (any copy of one)?</summary>
    public static bool IsAuthorsCopy(CardModel? card) =>
        card is Cards.Prototype.Generated.ProtoYmAuthorsCopy;

    /// <summary>
    /// Author's Copy: "Add a copy of an Annotated card in your hand (not an
    /// Author's Copy) to your hand. It keeps its Annotations." A copy is a
    /// new card: its Reprints are armed.
    /// </summary>
    public static async Task AuthorsCopy(PlayerChoiceContext choiceContext,
                                         CardModel editor)
    {
        var owner = editor.Owner;
        if (owner == null) return;
        var picked = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(new LocString(Table, CopyPromptKey), 1),
            c => CopyReaches(c, editor),
            editor)).FirstOrDefault();
        if (picked == null) return;
        var copy = picked.CreateClone();
        Masterpiece(copy)?.ArmAsCopy();
        await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand, owner);
    }

    // ---- Publish after elites and bosses (ruled 2026-10-14) ---------------

    /// <summary>
    /// Does this fight's reward screen carry Meditations of a Yako's Publish?
    /// An elite or a boss that gives rewards, never a normal fight, and never
    /// the final boss. PURE.
    /// </summary>
    public static bool OffersPublish(RoomType roomType, bool givesRewards,
                                     bool finalBoss) =>
        givesRewards && !finalBoss
        && (roomType == RoomType.Elite || roomType == RoomType.Boss);

    /// <summary>
    /// The Publish offer, PURE over its rows: each row is a deck card, the
    /// temporary layer the fight left on it (its draft) and whether it
    /// already carries a Published stack. Offered: every card the fight left
    /// a draft on, in deck order, each once. A Published card is offered
    /// again (review r3: stacks grow).
    /// </summary>
    public static List<T> PublishChoices<T>(
        IEnumerable<(T Card, YaeAnnotation Draft, bool Published)> rows) where T : class =>
        rows.Where(r => r.Draft != YaeAnnotation.None)
            .Select(r => r.Card)
            .Distinct()
            .ToList();

    /// <summary>The Publish offer for a player's deck. A card its draft would
    /// do nothing on is not offered (the dead-edit filter).</summary>
    public static IEnumerable<CardModel> PublishChoices(Player player) =>
        PublishChoices(player.Deck.Cards
            .Where(c => YaeAnnotationReach.Affects(c, Draft(c)))
            .Select(c => (c, Draft(c), Published(c))));

    /// <summary>
    /// At the end of a fight: every deck card's draft becomes the TEMPORARY
    /// layer its combat copy carries now (the stack is already the deck
    /// card's), and a card the fight left without one holds none. Cards
    /// made in combat have no deck card and are skipped.
    /// </summary>
    public static void SnapshotDrafts(Player? player)
    {
        if (player == null) return;
        var carried = new Dictionary<CardModel, YaeAnnotation>();
        foreach (var card in player.PlayerCombatState?.AllCards
                             ?? Enumerable.Empty<CardModel>())
        {
            if (card.DeckVersion is { } deck && Temporary(card) != YaeAnnotation.None)
            {
                carried[deck] = Temporary(card);
            }
        }
        foreach (var deck in player.Deck.Cards)
        {
            RecordDraft(deck, carried.TryGetValue(deck, out var a) ? a : YaeAnnotation.None);
        }
    }

    /// <summary>After a Publish: the fight's evidence is spent.</summary>
    public static void ClearDrafts(Player player)
    {
        foreach (var deck in player.Deck.Cards) RecordDraft(deck, YaeAnnotation.None);
    }

    /// <summary>A copy of a deck card wearing its stack and, in its temporary
    /// slot, its draft, for the Publish grid only: never put in a pile, and
    /// taken out of the run once the grid closes.</summary>
    public static CardModel PublishPreview(CardModel deckCard)
    {
        var preview = deckCard.Owner!.RunState.CloneCard(deckCard);
        Annotate(preview, Draft(deckCard), recordDraft: false);
        return preview;
    }

    /// <summary>The deck cards the grid's picks stand for: each preview is
    /// the copy of the deck card at the same index. PURE.</summary>
    public static List<T> ResolvePicks<T>(IReadOnlyList<T> previews,
                                          IReadOnlyList<T> decks,
                                          IEnumerable<T> picked) where T : class
    {
        var chosen = new List<T>();
        foreach (var p in picked)
        {
            for (var k = 0; k < previews.Count && k < decks.Count; k++)
            {
                if (!ReferenceEquals(previews[k], p)) continue;
                if (!chosen.Contains(decks[k])) chosen.Add(decks[k]);
                break;
            }
        }
        return chosen;
    }
}
