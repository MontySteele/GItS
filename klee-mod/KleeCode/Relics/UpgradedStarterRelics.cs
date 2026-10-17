using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// G-C3: the upgraded forms Touch of Orobas hands out.
///
/// THE BUG. Touch of Orobas is an act-2 Ancient reward that replaces your
/// starting relic with an upgraded version. Vanilla resolves that through
/// <c>TouchOfOrobas.GetUpgradedStarterRelic</c>, which is a HARDCODED
/// dictionary of five base-game pairs (Burning Blood -> Black Blood, Ring of
/// the Snake -> Ring of the Drake, Divine Right -> Divine Destiny, Bound
/// Phylactery -> Phylactery Unbound, Cracked Core -> Infused Core) with a
/// fallback of <c>ModelDb.Relic&lt;Circlet&gt;()</c> -- the no-effect filler.
/// So on a modded character the "reward" swapped the starter for a relic that
/// does nothing: a strict DOWNGRADE dressed as an upgrade. Reported from the
/// 2026-07-25 co-op A0 playtest.
///
/// THE MECHANISM, found by decompile per the house norm rather than invented.
/// Vanilla itself is not extensible here -- the dictionary is a private static
/// property. But BaseLib already patches exactly this method:
///
///   [HarmonyPatch(typeof(TouchOfOrobas), "GetUpgradedStarterRelic")]
///   private static bool CustomStarterUpgrade(RelicModel starterRelic,
///                                            ref RelicModel? __result)
///   {
///       if (starterRelic is CustomRelicModel customRelicModel)
///       {
///           __result = customRelicModel.GetUpgradeReplacement();
///           return __result == null;
///       }
///       return true;
///   }
///
/// So the extension point is <c>CustomRelicModel.GetUpgradeReplacement()</c>,
/// which defaults to <c>null</c>. All three of our starters are
/// CustomRelicModels and none of them overrode it, so every one fell through
/// to the Circlet. The fix is to override it -- plugging into the mechanism,
/// not reinventing it. No Harmony patch of our own is needed or wanted.
///
/// NUMBERS ARE RATIFIED (red-pen 2026-07-26), not proposed. Worth recording
/// because the first attempt reasoned from the wrong precedent: Burning Blood
/// heals 6 and Black Blood heals 12, so the upgraded forms were drafted as
/// exact doublings of their starters. That works for a flat post-combat heal
/// and fails for an ENGINE INPUT -- doubling Klee's per-detonation Spark rate
/// compounds with every bomb in the deck, and it was rejected as "way too
/// good". The ratified shape is a fixed opening windfall instead. Ratio
/// precedents do not transfer across effect kinds.
///
/// FURINA'S ARRIVED AT THE RED-PEN. G-C3 declined to invent one because every
/// candidate broke either the sprint's "no new behaviour in a starter upgrade"
/// rule or her no-passive-accrual law. R2 (2026-07-26) overrides the FORMER by
/// user authority — see <see cref="CurtainNeverFalls"/>. The accrual law is
/// untouched: the upgrade grants no resource per turn, it removes a choice.
/// </summary>
internal static class UpgradedStarterRelics
{
}

/// <summary>
/// Klee's upgraded starter (Touch of Orobas), displayed as "Dodoco Tales".
/// RATIFIED 2026-07-26.
///
/// Her per-explosion Spark income is the starter's 1 -- this relic keeps the
/// base behaviour rather than replacing it -- and the first explosion each
/// turn pays 2 (the repair, 2026-09-27). The fixed opening windfall it was
/// ratified with (3 Sparks) went with the shipped Sparks rule and came back
/// at 4 in the Klee finish-line batch (2026-10-03): with the kit's own 3
/// opening Sparks, an upgraded Klee opens each combat at 7
/// (<see cref="OpeningSparks"/>).
///
/// WHY A WINDFALL AND NOT A RATE. The first attempt doubled the per-detonation
/// grant, and that was rejected at red-pen as "way too good": a rate multiplies
/// with every bomb in the deck, so it compounds precisely where Klee is already
/// strongest, while a fixed opening bank dilutes across a long fight. The shape
/// mattered more than the number. Measured before ratification (act-2
/// acquisition, generous case): spark +2.3pt, demolition +7.1, reaction +5.0 --
/// strong for the slot, and the slot is an act-2 Ancient whose peers upgrade
/// six cards.
///
/// THE MEASUREMENT TABLE ABOVE GRADES THIS RELIC, NOT THE CARD. Red-pen Part 1
/// item 5 is titled "Explosive Frags", and until R69 that name belonged to two
/// different game objects reachable in the same run: this relic and the Rare
/// Power card `explosive_frags` (docs/klee-cards.yaml), which have
/// unrelated effects. The audit flagged the citation as ambiguous. It is
/// resolved here explicitly: the +2.3 / +7.1 / +5.0 figures are THIS object's,
/// measured as the Orobas upgrade, and item 5's ratification at 3 opening
/// Sparks is this object's ratification.
///
/// R69 (2026-07-26) settled the collision by renaming this side. The card was
/// the prior arrival and the ratified sheet artifact, so it keeps its name and
/// the relic yields. "Dodoco Tales" is Klee's signature catalyst, which keeps
/// the relic in her personal register alongside Pounding Surprise -- and it
/// still satisfies the base-game convention of a DISTINCT name for an upgraded
/// starter rather than a "+" suffix (Burning Blood -> Black Blood).
///
/// The C# TYPE is deliberately still `ExplosiveFrags`. R69 ruled that "no
/// mechanical change of any kind rides on this ruling", and a type rename is
/// not reliably cosmetic here: relic identity is BaseLib's, not this repo's,
/// so a renamed type risks moving the runtime relic id -- which in
/// deterministic-lockstep co-op is a desync, not a cosmetic diff. The
/// player-facing string is the thing the ruling renamed, and it is the thing
/// renamed below. Both names are reserved in docs/reserved-card-names.txt so
/// neither can be re-minted on the other side of the card/relic line.
///
/// Sim parity: tier05/content/relics.yaml `touch_of_orobas_klee`, whose
/// `combat_start_spark` hook is this class's opening bank. The per-detonation
/// half needs no sim entry because it is the starter's own hook, which the sim
/// never removes.
/// </summary>
public sealed class ExplosiveFrags : CustomRelicModel, IBombDetonationListener
    // The same seam Pounding Surprise takes: under the Klee overhaul this
    // relic is the upgraded form of the Spark rule, so it listens to the
    // arm's explosion bus too. ONE PAYMENT PER EXPLOSION (checked by the
    // Ancient audit, 2026-10-12): the shipped detonation bus above rings only
    // for the shipped BombPower, which nothing places any more; every Bomb
    // and Mine is a ProtoBombPower and rings the explosion bus alone
    // (AncientAuditTests pins it).
    , Powers.IProtoExplosionListener
{
    /// <summary>
    /// Sparks per detonation. UNCHANGED from the base relic -- the upgrade is
    /// the opening bank below, not this rate. Kept as a named constant rather
    /// than a literal 1 so that anyone tempted to raise it meets the ruling
    /// first.
    /// </summary>
    public const int SparksPerDetonation = 1;

    /// <summary>Under the Klee arm, the first explosion each turn pays this
    /// many Sparks instead of one (the relics-and-potions paper's repair,
    /// ruled 2026-09-27).</summary>
    public const int FirstExplosionSparks = 2;

    /// <summary>The opening bank (Klee finish-line batch, 2026-10-03, ruled
    /// "Agreed all around!"): "Start each combat with 4 more Sparks." On top
    /// of the kit's <see cref="Powers.KleeOverhaulLaw.OpeningSpark"/> (3), so
    /// an upgraded Klee opens at 7, the Regent's 3 -> 7 stars as the
    /// yardstick.
    /// Sim twin: <c>touch_of_orobas_klee</c>'s <c>combat_start_spark</c>
    /// (tier05/content/relics.yaml).</summary>
    public const int OpeningSparks = 4;

    public ExplosiveFrags() : base(autoAdd: false)
    {
    }

    // Ancient, matching the reward tier that grants it -- Touch of Orobas is
    // itself RelicRarity.Ancient, and the five base-game upgraded forms are
    // not Starter-rarity either. Starter rarity here would also be actively
    // harmful: TouchOfOrobas.GetStarterRelic finds its target with
    // `p.Relics.FirstOrDefault(r => r.Rarity == RelicRarity.Starter)`, so a
    // Starter-rarity replacement could be picked up as the starter by a
    // second Orobas and upgraded again.
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        // R69 (2026-07-26): was "Explosive Frags", which collided with the
        // Rare Power card of that name. See the class summary.
        ("title", "Dodoco Tales"),
        ("description",
            // The repair of 2026-09-27
            // (review/active/relics-potions-klee-furina-2026-09-27.md): one
            // extra Spark a turn, all of it earned; and the opening bank,
            // paid by the kit's opening site (`GrantOpeningSparks` below).
            "Whenever a [gold]Bomb[/gold] goes off, gain [blue]"
          + Powers.KleeOverhaulLaw.SparkPerExplosion + "[/blue] [gold]Spark[/gold], "
          + "or [blue]" + FirstExplosionSparks
          + "[/blue] the first time each turn. "
          // Klee finish-line batch, 2026-10-03: the opening bank. "additional"
          // since the card text pass (2026-10-12, rule 8).
          + "Start each combat with [blue]" + OpeningSparks
          + "[/blue] additional [gold]Sparks[/gold]."
            ),
    };

    protected override string IconBaseName => "burning_blood";

    // EB-162 (2026-08-30). BOTH of these read `klee/relics/pounding_surprise.png`
    // until this change, so Dodoco Tales and Pounding Surprise drew ONE icon and
    // were indistinguishable in the relic bar. That is not two relics a player
    // has to hold at once by luck: Touch of Orobas UPGRADES the starter, so the
    // swap itself is the moment both names are on screen for the same picture.
    // The distinct icon is `art/plan.tsv:relic_dodoco_tales`, rank 1 applied
    // under R212(1) from Item Dodoco's Bomb-Tastic Adventure -- the in-game
    // picture book about Dodoco, which is what "Dodoco Tales" names.
    //
    // KleePck.Path returns null until the resource is IN the pck, and the pck
    // contract is derived by tools/build_pck.ps1, never hand-written
    // (test_roster_runtime_contracts). Until the next build_pck the `??` falls
    // through to base, i.e. burning_blood -- still not Pounding Surprise's icon,
    // so the defect this row names does not reappear in the interval.
    public override string PackedIconPath =>
        KleePck.Path("klee/relics/dodoco_tales.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("klee/relics/dodoco_tales.png") ?? base.BigIconPath;

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Klee);

    /// <summary>
    /// The companion reward slot rides along UNCHANGED. It is not part of the
    /// upgrade -- it is the fourth-offer hook that has to exist for the whole
    /// of every run, and losing it when Orobas fires would be a second
    /// instance of exactly the bug this class fixes.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;

        var companionRarity =
            creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
                ? CardRarity.Rare
                : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, companionRarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }


    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target,
        int damage)
    {
        // Own bombs only: in co-op another player's detonations are theirs.
        if (applier?.Player != Owner) return;

        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature, SparksPerDetonation,
            cardSource: null,
            source: "relic:explosive_frags/detonation");
    }

    /// <summary>
    /// The opening bank: <see cref="OpeningSparks"/> on Klee's first turn,
    /// paid from the kit's own opening site
    /// (<see cref="Powers.KleeOverhaulOpening.GrantSpark"/>: turn 1 after the
    /// draw, per player, Klee only) right after the kit's Sparks, so the first
    /// hand sees all seven and the two gains have one fixed order rather than
    /// two co-tenants of <c>AfterPlayerTurnStart</c>.
    /// </summary>
    public async Task GrantOpeningSparks(
        PlayerChoiceContext choiceContext, Creature creature)
    {
        Flash();
        await SparkPower.Gain(
            choiceContext, creature, OpeningSparks,
            cardSource: null, source: "relic:explosive_frags/combat_start");
    }

    /// <summary>The overhaul's rule 4 on the upgraded relic: the same one Spark
    /// per explosion the base relic mints, so an act-2 Touch of Orobas cannot
    /// silently take the arm's only income away.</summary>
    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (applier.Player != Owner) return;

        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature, SparksFor(applier),
            cardSource: null, source: "relic:explosive_frags/explosion");
    }

    /// <summary>The arm's repair: "Whenever a Bomb goes off, gain 1 Spark.
    /// The first time each turn, gain 2 instead." The turn is the arm
    /// ledger's round, so a Mine on the enemies' turn that follows a turn with
    /// no explosion is that round's first. Spends the latch.</summary>
    public static int SparksFor(Creature applier) =>
        Powers.KleeOverhaulLedger.For(applier).TakeDodocoTales()
            ? FirstExplosionSparks
            : Powers.KleeOverhaulLaw.SparkPerExplosion;
}

/// <summary>
/// Furina's upgraded starter (Touch of Orobas): THE CURTAIN NEVER FALLS, Salon
/// Solitaire upgraded. "At the end of your turn, Repay 2." (the Salon's Tab,
/// 2026-10-05; 3 until the 2026-10-09 playtest trim). The Repay is the kit's
/// (<see cref="Powers.FurinaStage.SingerOf"/>, at
/// <see cref="Powers.FurinaStageLaw.SingerRepayUpgraded"/>); the starter's is
/// 1. It keeps her companion reward slot.
///
/// Its first form (red-pen ruling R2, 2026-07-26: both Spotlight modes at
/// once, a flag on <c>SpotlightSystem</c>) retired with the shipped kits; the
/// Ancient audit (2026-10-12) cut that class doc, which git keeps.
/// </summary>
public sealed class CurtainNeverFalls : CustomRelicModel
{
    public CurtainNeverFalls() : base(autoAdd: false)
    {
    }

    /// <summary>
    /// THE SALON'S TAB (2026-10-05): Salon Solitaire upgraded, "At the end of
    /// your turn, Repay 2." (2026-10-09 playtest trim, was 3.) The Repay is the kit's
    /// (<see cref="Powers.FurinaStage.SingerOf"/>); this relic opens the
    /// combat's ledger as the starter does.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        var furina = Owner?.Creature;
        if (!Powers.FurinaStage.LiveFor(furina)) return;
        await Powers.FurinaStage.OpenCombat(furina);
    }

    // Ancient, never Starter -- see ExplosiveFrags for why that matters.
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "The Curtain Never Falls"),
        ("description",
            "At the end of your turn, [gold]Repay[/gold] [blue]"
          + Powers.FurinaStageLaw.SingerRepayUpgraded + "[/blue]."),
    };

    protected override string IconBaseName => "ring_of_the_snake";

    public override string PackedIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.BigIconPath;

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Furina);

    /// <summary>
    /// Furina's companion reward slot, carried forward UNCHANGED from the base
    /// relic. Not part of the upgrade, and not optional: see
    /// <see cref="PearlOfInsightRelic.TryModifyCardRewardOptions"/> for the
    /// near-miss that put an invariant behind this.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }
}
