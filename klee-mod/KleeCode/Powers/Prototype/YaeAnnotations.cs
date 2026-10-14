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
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>Her five Annotations (paper sec.2), in the order the Edit tip
/// lists them. <see cref="None"/> is "not Annotated". A saved draft stores
/// the member's NAME (<see cref="YaeEditing.Draft"/>), so a name never
/// changes; the numbers follow the sheet's order.</summary>
public enum YaeAnnotation
{
    None = 0,
    RedInk = 1,
    Footnote = 2,
    DeadlineExtension = 3,
    FoxFire = 4,
    SakuraSeal = 5,
    Royalties = 6,
}

/// <summary>
/// ONE ANNOTATION, ONE ENCHANTMENT. Paper sec.2: "her Enchantments, one per
/// card, saved on the card as the engine's <c>CardCmd.Enchant</c> already
/// does". The engine gives a card at most one Enchantment and clones it with
/// the card (a copy of the instance keeps it, a fresh copy by id does not:
/// the paper's reading), runs its <see cref="OnPlay"/> AFTER the card's own
/// effects (<c>CardModel.OnPlayWrapper</c>), and serialises it with a deck
/// card, which is what makes a Published Annotation last the run for free.
///
/// Sim twin: <c>yae_shrine.annotate</c> and the card's <c>enchant_*</c>
/// riders.
/// </summary>
public abstract class YaeAnnotationModel : CustomEnchantmentModel, ILocalizationProvider
{
    /// <summary>Which of the five this is.</summary>
    public abstract YaeAnnotation Annotation { get; }

    /// <summary>The printed name.</summary>
    public string Name => YaeAnnotationText.Name(Annotation);

    /// <summary>What it does, one sentence (the tip and the hover).</summary>
    public string Rule => YaeAnnotationText.Rule(Annotation);

    public List<(string, string)>? Localization => new()
    {
        ("title", Name),
        ("description", Rule),
        ("extraCardText", $"[gold]{Name}[/gold]."),
    };

    /// <summary>The five ride any card an Edit can reach; the Edit's own
    /// filter (<see cref="YaeEditing.Editable"/>) is the rule.</summary>
    public override bool CanEnchantCardType(CardType cardType) => true;

    /// <summary>A borrowed base-game icon where the game ships one, else the
    /// engine's own missing-enchantment fallback (null). Placeholder art.
    /// </summary>
    protected override string? CustomIconPath
    {
        get
        {
            foreach (var path in IconCandidates)
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

    /// <summary>Base enchantment icons this one borrows, best first.</summary>
    protected abstract IEnumerable<string> IconCandidates { get; }

    protected static IEnumerable<string> Borrow(string entry) => new[]
    {
        $"res://images/enchantments/{entry}.png",
        $"res://images/enchantments/beta/{entry}.png",
    };
}

/// <summary>The five Annotations' names and rules, one table, read by the
/// enchantments, the Reborn faces and the Edit tip.</summary>
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
        _ => "",
    };

    /// <summary>What an Annotation does on a SAKURA (ruled 2026-10-14);
    /// empty for the ones with no Sakura reading.</summary>
    public static string SakuraRule(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk =>
            $"Its strike is {YaeLaw.RedInkAmount} bigger (not in Offering).",
        YaeAnnotation.FoxFire =>
            $"When it strikes, it also deals {YaeLaw.FoxFireDamage} "
          + "[gold]Electro[/gold] damage to a random enemy.",
        YaeAnnotation.DeadlineExtension => "It does not wither.",
        _ => "",
    };
}

/// <summary>Red Ink: "this card deals 3 more damage (per hit) and gives 3 more
/// Block (per gain)". Sharp's damage door (a powered attack only) and
/// Nimble's Block door, at <see cref="YaeLaw.RedInkAmount"/>.</summary>
public sealed class RedInkAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.RedInk;



    protected override IEnumerable<string> IconCandidates => Borrow("sharp");

    public override decimal EnchantDamageAdditive(decimal originalDamage, ValueProp props) =>
        props.IsPoweredAttack() ? YaeLaw.RedInkAmount : 0m;

    public override decimal EnchantBlockAdditive(decimal originalBlock) =>
        YaeLaw.RedInkAmount;
}

/// <summary>Footnote: "when played, draw 1, after its own effects".</summary>
public sealed class FootnoteAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.Footnote;



    public override bool HasExtraCardText => true;

    protected override IEnumerable<string> IconCandidates => Borrow("swift");

    public override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)
    {
        if (Card.Owner is not { } owner) return;
        await CardPileCmd.Draw(choiceContext, 1, owner);
    }
}

/// <summary>Deadline Extension: Retain, Steady's way (the keyword, added on
/// enchant). Removed again when an Edit overwrites it, unless the card
/// printed Retain itself (<see cref="YaeEditing.Clear"/>).</summary>
public sealed class DeadlineExtensionAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.DeadlineExtension;



    protected override IEnumerable<string> IconCandidates => Borrow("steady");

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        new[] { HoverTipFactory.FromKeyword(CardKeyword.Retain) };

    protected override void OnEnchant()
    {
        Card.AddKeyword(CardKeyword.Retain);
    }
}

/// <summary>Fox Fire: "when played, deal 4 Electro damage to a random enemy,
/// after its own effects, a pet's hit".</summary>
public sealed class FoxFireAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.FoxFire;



    public override bool HasExtraCardText => true;

    protected override IEnumerable<string> IconCandidates => Borrow("imbued");

    public override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay) =>
        YaeShrine.FoxFire(choiceContext, Card.Owner?.Creature);
}

/// <summary>Sakura Seal: "when played, plant a Sakura, after its own effects".
/// The bridge from the house to the shrine.</summary>
public sealed class SakuraSealAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.SakuraSeal;



    public override bool HasExtraCardText => true;

    protected override IEnumerable<string> IconCandidates => Borrow("sown");

    public override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay) =>
        YaeShrine.Plant(choiceContext, Card.Owner?.Creature, 1);
}

/// <summary>Royalties (design axes batch two, ruled 2026-10-14): "when
/// played, gain 1 Energy", after the card's own effects.</summary>
public sealed class RoyaltiesAnnotation : YaeAnnotationModel
{
    public override YaeAnnotation Annotation => YaeAnnotation.Royalties;

    public override bool HasExtraCardText => true;

    protected override IEnumerable<string> IconCandidates => Borrow("glam");

    public override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)
    {
        if (Card.Owner is not { } owner) return;
        await PlayerCmd.GainEnergy(YaeLaw.RoyaltiesPayout, owner);
    }
}

/// <summary>
/// THE PUBLISHING HOUSE (paper sec.2): Edit, the Annotated read, Publish and
/// the drafts the rest-site Publish reads. Sim twin: the publishing-house
/// half of <c>tier0/engine/yae_shrine.py</c>.
/// </summary>
public static class YaeEditing
{
    private const string Table = "cards";

    /// <summary>The Edit selection's prompt (merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>).</summary>
    public const string EditPromptKey = "KLEEMOD-YAE_EDIT.selectionScreenPrompt";

    public const string EditPromptText = "Choose a card to Edit.";

    /// <summary>The Seven Glamours' prompt.</summary>
    public const string PublishPromptKey = "KLEEMOD-YAE_PUBLISH.selectionScreenPrompt";

    public const string PublishPromptText = "Choose a card to Publish.";

    /// <summary>Reborn as Guuji Yae's prompt.</summary>
    public const string AnnotationPromptKey = "KLEEMOD-YAE_ANNOTATION.selectionScreenPrompt";

    public const string AnnotationPromptText = "Choose an Annotation.";

    /// <summary>
    /// THE DRAFT (pick 2 (a), ruled): "the card keeps the Annotation it last
    /// carried in a combat this run (its draft; the game remembers one draft
    /// per card)". Kept on the DECK card and saved with it (BaseLib's saved
    /// field on <see cref="CardModel"/>, the shape
    /// <c>Relics.VarkaStarterKnight</c> uses on a relic), so a save and load
    /// between the fight and the rest keeps it. Written at every Edit
    /// (<see cref="Annotate"/>), which is "last carried": an Annotation only
    /// changes by an Edit. The value is a <see cref="YaeAnnotation"/>'s
    /// NAME, and the default is null so a card never Edited writes nothing
    /// into the save (BaseLib skips a null value); every other character's
    /// cards carry no field.
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

    /// <summary>The Annotation a card carries, a Published one included.
    /// PURE.</summary>
    public static YaeAnnotation Of(CardModel? card) =>
        card?.Enchantment is YaeAnnotationModel a ? a.Annotation : YaeAnnotation.None;

    /// <summary>"Annotated means carrying any Annotation, a Published one
    /// included." PURE.</summary>
    public static bool IsAnnotated(CardModel? card) => Of(card) != YaeAnnotation.None;

    /// <summary>Annotated cards in the owner's hand; the card being played
    /// counts if it is Annotated (Bestseller counts itself), which is why it
    /// is added when it has already left the hand. PURE over the piles.
    /// </summary>
    public static int AnnotatedInHand(CardModel playing)
    {
        var owner = playing.Owner;
        if (owner == null) return 0;
        var hand = PileType.Hand.GetPile(owner).Cards;
        var n = hand.Count(IsAnnotated);
        if (!hand.Contains(playing) && IsAnnotated(playing)) n++;
        return n;
    }

    /// <summary>
    /// "Edit a card in your hand: never the Edit card itself, never a Status
    /// or Curse, never a kit card." PURE. (The sim's `kit_card` is the old
    /// Burst kit, which no C# card is; a Quest card is the engine's third
    /// never-enchantable type.)
    /// </summary>
    public static bool Editable(CardModel candidate, CardModel? editor) =>
        !ReferenceEquals(candidate, editor)
        && candidate.Type != CardType.Status
        && candidate.Type != CardType.Curse
        && candidate.Type != CardType.Quest;

    /// <summary>The model for one Annotation, fresh and mutable.</summary>
    public static YaeAnnotationModel? Create(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk => (YaeAnnotationModel)ModelDb.Enchantment<RedInkAnnotation>().ToMutable(),
        YaeAnnotation.Footnote => (YaeAnnotationModel)ModelDb.Enchantment<FootnoteAnnotation>().ToMutable(),
        YaeAnnotation.DeadlineExtension => (YaeAnnotationModel)ModelDb.Enchantment<DeadlineExtensionAnnotation>().ToMutable(),
        YaeAnnotation.FoxFire => (YaeAnnotationModel)ModelDb.Enchantment<FoxFireAnnotation>().ToMutable(),
        YaeAnnotation.SakuraSeal => (YaeAnnotationModel)ModelDb.Enchantment<SakuraSealAnnotation>().ToMutable(),
        YaeAnnotation.Royalties => (YaeAnnotationModel)ModelDb.Enchantment<RoyaltiesAnnotation>().ToMutable(),
        _ => null,
    };

    /// <summary>
    /// Clear whatever Enchantment the card carries ("overwriting any it
    /// had"), taking back the Retain a Deadline Extension added unless the
    /// card prints Retain itself.
    /// </summary>
    public static void Clear(CardModel card)
    {
        var had = card.Enchantment;
        if (had == null) return;
        CardCmd.ClearEnchantment(card);
        if (had is DeadlineExtensionAnnotation
            && !card.CanonicalKeywords.Contains(CardKeyword.Retain))
        {
            card.RemoveKeyword(CardKeyword.Retain);
        }
        card.DynamicVars.RecalculateForUpgradeOrEnchant();
    }

    /// <summary>
    /// Give <paramref name="card"/> one Annotation, overwriting any it had.
    /// A combat card also writes its deck card's draft, which is what the
    /// rest-site Publish reads.
    /// </summary>
    public static bool Annotate(CardModel card, YaeAnnotation annotation,
                                bool recordDraft = true)
    {
        var model = Create(annotation);
        if (model == null) return false;
        Clear(card);
        if (!model.CanEnchant(card)) return false;
        CardCmd.Enchant(model, card, 1m);
        if (recordDraft && card.DeckVersion is { } deck)
        {
            RecordDraft(deck, annotation);
        }
        return true;
    }

    /// <summary>
    /// "Edit a card in your hand: &lt;Annotation&gt;", <paramref name="times"/>
    /// times. The player picks each card (the sim's pilot picks by its
    /// default reading, <c>yae_shrine._edit_target</c>). Nothing qualifies:
    /// nothing happens (the cost is already paid). Serialization pays per
    /// Edit.
    /// </summary>
    public static async Task Edit(PlayerChoiceContext choiceContext,
                                  CardModel editor, YaeAnnotation annotation,
                                  int times)
    {
        var owner = editor.Owner;
        if (owner?.Creature == null) return;
        for (var i = 0; i < times; i++)
        {
            var picked = (await CardSelectCmd.FromHand(
                choiceContext, owner,
                new CardSelectorPrefs(new LocString(Table, EditPromptKey), 1),
                c => Editable(c, editor), editor)).FirstOrDefault();
            if (picked == null) return;
            if (!Annotate(picked, annotation)) continue;
            YaeShrineLedger.For(owner.Creature).NoteEdit();
            await SerializationPower.Pay(owner.Creature, 1);
        }
    }

    /// <summary>
    /// Reborn as Guuji Yae: "Choose an Annotation. Edit every other card in
    /// your hand with it." The player chooses from the five faces
    /// (<see cref="Cards.Prototype.YaeModalOptions"/>); the sim's pilot takes
    /// the row's printed default, Sakura Seal.
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
            .Where(c => Editable(c, editor)).ToList();
        var n = 0;
        foreach (var card in cards)
        {
            if (Annotate(card, chosen)) n++;
        }
        if (n == 0) return;
        for (var i = 0; i < n; i++) YaeShrineLedger.For(owner.Creature).NoteEdit();
        await SerializationPower.Pay(owner.Creature, n);
    }

    /// <summary>
    /// "A Published Annotation lasts the rest of the run." Written on the
    /// DECK card, which the engine saves with its Enchantment; the combat
    /// card keeps what it carries. Returns false for a card with no deck
    /// card (a copy made in combat), which has nothing to publish to.
    /// </summary>
    public static bool PublishToDeck(CardModel deckCard, YaeAnnotation annotation) =>
        Annotate(deckCard, annotation, recordDraft: false);

    /// <summary>
    /// The Seven Glamours: "Publish an Annotated card in your hand: its
    /// Annotation lasts the rest of the run." The player picks among the
    /// Annotated cards in hand that have a deck card.
    /// </summary>
    public static async Task PublishFromHand(PlayerChoiceContext choiceContext,
                                             CardModel editor)
    {
        var owner = editor.Owner;
        if (owner == null) return;
        var picked = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(new LocString(Table, PublishPromptKey), 1),
            c => Editable(c, editor) && IsAnnotated(c) && c.DeckVersion != null,
            editor)).FirstOrDefault();
        if (picked?.DeckVersion is not { } deck) return;
        PublishToDeck(deck, Of(picked));
    }

    /// <summary>The deck cards a rest-site Publish can choose: every card
    /// holding a draft. PURE over the deck.</summary>
    public static IEnumerable<CardModel> Publishable(Player player) =>
        player.Deck.Cards.Where(c => Draft(c) != YaeAnnotation.None);
}
