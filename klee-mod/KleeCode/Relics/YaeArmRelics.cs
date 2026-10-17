using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Relics;

/// <summary>
/// YAE'S OWN RELICS (the Yae pass, 2026-10-16,
/// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.3). The base
/// game's shape, Kokomi's: one Common, two Uncommons, three Rares and one
/// Shop relic beside Meditations of a Yako. They, Meditations and Enlightened
/// Blessing are her whole relic offer; the Silent borrow leaves the offer
/// (members only), as for Klee, Furina, Varka and Kokomi.
///
/// Every effect asks <see cref="YaeShrine.Live"/>, so a relic held by anyone
/// else does nothing. Four are read where her rules already are
/// (<see cref="YaeShrine"/>): Electroculus in the strike's size (before
/// Edict and Fox Fire), Kagura Bell after the Tenko's strikes, Fox Ofuda in
/// the cap (it stacks with Sakura Channeling), Saiguu's Inkstone in her turn
/// start, after the draw; Proofreader's Glasses rides every Edit's one door
/// (<see cref="YaeShrine.AfterEdits"/>).
///
/// NO SIM TWIN: tier0's Yae twin models Meditations and no other relic, as
/// Kokomi's own relics have none until Balance.
/// </summary>
public static class YaeArmRelics
{
    /// <summary>The seven, in the paper's table order. The pool reads this
    /// list and nothing else.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(KitsuneMask), typeof(SacredSakuraBranch),
        typeof(ProofreadersGlasses), typeof(Electroculus),
        typeof(SaiguusInkstone), typeof(KaguraBell), typeof(FoxOfuda),
    };

    /// <summary>How many copies of <typeparamref name="T"/> this Yae holds;
    /// 0 for anyone else.</summary>
    internal static int Held<T>(Creature? yae) where T : RelicModel =>
        YaeShrine.Live(yae) && yae!.Player is { } player
            ? player.Relics.OfType<T>().Count()
            : 0;

    /// <summary>Flash every copy of <typeparamref name="T"/> she holds.
    /// </summary>
    internal static void FlashAll<T>(Creature yae) where T : RelicModel
    {
        foreach (var relic in yae.Player?.Relics.OfType<T>().ToList()
                              ?? new List<T>())
        {
            relic.Flash();
        }
    }

    /// <summary>"At the start of each combat": her own first turn, after
    /// the draw (Kokomi's Electro Sigil's gate).</summary>
    public static bool FirstTurnOf(RelicModel relic, Player player) =>
        player == relic.Owner
        && YaeShrine.Live(player.Creature)
        && player.PlayerCombatState?.TurnNumber == 1
        && player.Creature is { IsDead: false };

    internal static string Icon(string slug) => "yae/relics/" + slug + ".png";

    /// <summary>Her Sakura tip, read off her starter (a Yae card), so a
    /// relic's hover says what her Sakura are.</summary>
    internal static IEnumerable<IHoverTip> SakuraTip(IEnumerable<IHoverTip> inherited) =>
        ArmKeywordTips.ForSakura(inherited, ModelDb.Card<ProtoYmYakanEvocation>());
}

/// <summary>A relic of hers: Burning Blood until her art pass puts her own
/// file in the pack (Kokomi's relics' fallback chain).</summary>
public abstract class YaeArmRelic : CustomRelicModel
{
    protected YaeArmRelic() : base(autoAdd: false) { }

    /// <summary><c>yae/relics/&lt;slug&gt;.png</c>.</summary>
    protected abstract string Slug { get; }

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path(YaeArmRelics.Icon(Slug)) ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path(YaeArmRelics.Icon(Slug)) ?? base.BigIconPath;
}

/// <summary>Common. "At the start of each combat, apply 1 Weak to ALL
/// enemies." Bag of Marbles' size, on her first turn after the draw (Electro
/// Sigil's hook); it aims at her act-1 bleeding and turns on her Weak cards
/// (Saiguu's Lesson reads it as any Weak she applies). Copies add.</summary>
public sealed class KitsuneMask : YaeArmRelic
{
    public const int Weak = 1;

    protected override string Slug => "kitsune_mask";

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kitsune Mask"),
        ("description",
            "At the start of each combat, apply [blue]" + Weak + "[/blue] "
          + "[gold]Weak[/gold] to ALL enemies."),
    };

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!YaeArmRelics.FirstTurnOf(this, player)) return;
        var combat = player.Creature.CombatState;
        if (combat == null) return;
        var enemies = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (enemies.Count == 0) return;
        Flash();
        foreach (var enemy in enemies)
        {
            if (enemy.IsDead) continue;
            await PowerCmd.Apply<WeakPower>(choiceContext, enemy, Weak,
                                            applier: player.Creature, cardSource: null);
        }
    }
}

/// <summary>Uncommon. "At the start of each combat, plant a Sakura."
/// Anchor-size: about 9 damage over three turns, on the turn she is slowest.
/// A plain Sakura at her plant Level (Fox's Mooncall reads it), on her first
/// turn after the draw.</summary>
public sealed class SacredSakuraBranch : YaeArmRelic
{
    protected override string Slug => "sacred_sakura_branch";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Sacred Sakura Branch"),
        ("description", "At the start of each combat, plant a [gold]Sakura[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        YaeArmRelics.SakuraTip(Array.Empty<IHoverTip>());

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!YaeArmRelics.FirstTurnOf(this, player)) return;
        Flash();
        await YaeShrine.Plant(choiceContext, player.Creature, 1);
    }
}

/// <summary>Uncommon. "The first time you Edit a card each turn, draw 1
/// card." (printed in the house order, text-conventions rule 5, as Kokomi's
/// Resistance Armband is). One card a turn, paid for with an Edit: the turn's first Edit,
/// whatever made it (a hand card, a Sakura, Saiguu's Inkstone), read at
/// every Edit's door (<see cref="YaeShrine.AfterEdits"/>) off the turn's Edit
/// count. An Edit that changes nothing is not an Edit. Copies add.</summary>
public sealed class ProofreadersGlasses : YaeArmRelic
{
    protected override string Slug => "proofreaders_glasses";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Proofreader's Glasses"),
        ("description",
            "The first time each turn you [gold]Edit[/gold] a card, draw "
          + "[blue]1[/blue] card."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(Array.Empty<IHoverTip>(), null);

    /// <summary>The cards the turn's first Edit draws: 1 a copy.</summary>
    public static int DrawFor(Creature? yae) =>
        YaeArmRelics.Held<ProofreadersGlasses>(yae);

    public static async Task FirstEdit(PlayerChoiceContext choiceContext, Creature yae)
    {
        var n = DrawFor(yae);
        if (n <= 0 || yae.Player is not { } player) return;
        YaeArmRelics.FlashAll<ProofreadersGlasses>(yae);
        await CardPileCmd.Draw(choiceContext, n, player);
    }
}

/// <summary>Rare. "Your Sakura's strikes deal 1 more damage." A third more on
/// a Level 1 strike. Added to the strike's size before Edict and Fox Fire
/// (<see cref="YaeShrine.Size"/>, so the badge and the live Tenko line say
/// it too): a Sakura's and a Foxfire Sakura's hit on ALL count; a Kitsune
/// Sakura's Block does not. Copies add.</summary>
public sealed class Electroculus : YaeArmRelic
{
    public const int Damage = 1;

    protected override string Slug => "electroculus";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Electroculus"),
        ("description",
            "Your [gold]Sakura[/gold]'s strikes deal [blue]" + Damage + "[/blue] "
          + "additional damage."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        YaeArmRelics.SakuraTip(Array.Empty<IHoverTip>());

    /// <summary>What it adds to one strike: 1 a copy.</summary>
    public static int Bonus(Creature? yae) =>
        Damage * YaeArmRelics.Held<Electroculus>(yae);
}

/// <summary>Rare. "At the start of your turn, Edit a random card in your
/// hand: Red Ink." One free Edit a turn, after the draw and after the turn's
/// Edit count is cleared (<see cref="YaeShrine.TurnStart"/>), so
/// Serialization, Bestseller, Editor-in-Chief and Proofreader's Glasses read
/// it. It skips cards Red Ink would do nothing on, as Edits already do
/// (<see cref="YaeEditing.EditReaches"/>); none in hand, nothing. Yae
/// Publishing House doubles it as every Edit. One Edit however many copies.
/// </summary>
public sealed class SaiguusInkstone : YaeArmRelic
{
    protected override string Slug => "saiguus_inkstone";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Saiguu's Inkstone"),
        ("description",
            "At the start of your turn, [gold]Edit[/gold] a random card in your "
          + "[gold]Hand[/gold]: [gold]Red Ink[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(
            ArmKeywordTips.ForAnnotation(Array.Empty<IHoverTip>(), null,
                                         YaeAnnotation.RedInk, false),
            null);

    /// <summary>What it may Edit: a card in hand Red Ink would do something
    /// on. PURE over the hand.</summary>
    public static List<CardModel> Candidates(IEnumerable<CardModel> hand) =>
        hand.Where(c => YaeEditing.EditReaches(c, null, YaeAnnotation.RedInk)).ToList();

    public static async Task Edit(PlayerChoiceContext choiceContext, Player player)
    {
        var yae = player.Creature;
        if (YaeArmRelics.Held<SaiguusInkstone>(yae) <= 0) return;
        var cands = Candidates(PileType.Hand.GetPile(player).Cards);
        if (cands.Count == 0) return;
        var card = player.RunState.Rng.CombatCardSelection.NextItem(cands);
        if (card == null) return;
        if (!YaeEditing.Annotate(card, YaeAnnotation.RedInk,
                                 times: YaeEditing.WriteTimes(yae))) return;
        player.Relics.OfType<SaiguusInkstone>().FirstOrDefault()?.Flash();
        YaeShrineLedger.For(yae).NoteEdit();
        await YaeShrine.AfterEdits(choiceContext, yae, 1);
    }
}

/// <summary>Rare. "Whenever you Tenko, each Sakura gains a Level." Turns
/// Tenko from a refresh into growth. The Levels come after the Tenko's
/// strikes (<see cref="YaeShrine.Tenko"/>); a Tenko with no Sakura does
/// nothing. Copies add.</summary>
public sealed class KaguraBell : YaeArmRelic
{
    protected override string Slug => "kagura_bell";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kagura Bell"),
        ("description",
            "Whenever you [gold]Tenko[/gold], each [gold]Sakura[/gold] gains a "
          + "Level."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForTenko(YaeArmRelics.SakuraTip(Array.Empty<IHoverTip>()), null);

    /// <summary>The Levels one Tenko gives each Sakura: 1 a copy.</summary>
    public static int LevelsFor(Creature? yae) => YaeArmRelics.Held<KaguraBell>(yae);

    public static void Ring(Creature yae)
    {
        var n = LevelsFor(yae);
        var ledger = YaeShrineLedger.For(yae);
        if (n <= 0 || ledger.Count == 0) return;
        YaeArmRelics.FlashAll<KaguraBell>(yae);
        ledger.LevelUp(n);
    }
}

/// <summary>Shop. "You can have 1 more Sakura." Sakura Channeling's words,
/// and half its size; it stacks with Channeling
/// (<see cref="YaeShrine.MaxSakura"/>), and the full-shrine plant fires at
/// the new cap. Copies add.</summary>
public sealed class FoxOfuda : YaeArmRelic
{
    public const int More = 1;

    protected override string Slug => "fox_ofuda";

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Fox Ofuda"),
        ("description",
            "You can have [blue]" + More + "[/blue] more [gold]Sakura[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        YaeArmRelics.SakuraTip(Array.Empty<IHoverTip>());

    /// <summary>What it adds to the cap: 1 a copy.</summary>
    public static int Extra(Creature? yae) => More * YaeArmRelics.Held<FoxOfuda>(yae);
}
