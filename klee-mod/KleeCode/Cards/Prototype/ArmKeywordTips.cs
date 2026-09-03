using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// `EB-272`: the QUARANTINED ARMS' KEYWORDS, defined once each.
///
/// THE GAP, and it is the same gap one register row over from Charge and
/// Burst. Every shipped keyword on a face has somewhere a player can read it
/// -- `Block` and `Exhaust` are the base game's, `Applies Pyro` and the eight
/// reaction previews are <see cref="KleeKeywords"/>' -- and not one word the
/// three prototype arms invented had anything at all. [USER] hit it live on
/// the dev build the day this row was filed ("Set Off has no tooltip text"),
/// and both Kokomi seats in round one inferred `Exert` from watching their own
/// HP drop, which is the only way the rule was ever stated to them. The
/// Casket's `Mend` read as BROKEN at full HP for the same reason: the
/// entry-HP bound is real, it is enforced in <see cref="KokomiRules.Mend"/>,
/// and it was printed nowhere.
///
/// A MISSING HOVER TIP RENDERS AS NOTHING AT ALL. There is no wrong number to
/// notice, no exception and no visual seam -- so this class is only half the
/// fix. The other half is that the ATTACH IS DERIVED, not remembered:
/// `gen_klee_cards.emit` reads the `[gold]Keyword[/gold]` tokens out of the
/// row's own built description and attaches the matching call from the table
/// in `ARM_KEYWORDS`. A new row that prints an arm keyword carries its
/// definition because it printed the word, not because somebody remembered.
///
/// WHY A SEPARATE CLASS FROM <see cref="KleeCardTooltips"/> AND
/// <see cref="KokomiRiderTips"/>. It lives under `Cards/Prototype/`, which
/// `KleeCode.csproj` REMOVES from a release build, for the same reason the
/// arms' powers do: these sentences describe rules that exist only under
/// `-p:PrototypeCards=true`, and several of them quote a `*OverhaulLaw`
/// constant that is not compiled otherwise. A release build contains neither
/// the text nor the keys.
///
/// WHAT THESE ARE NOT. They are NOT the badge. `ProtoBombPower` prints the
/// Bomb rules on the ENEMY, live, with the pile's own numbers in them, and
/// `PendingPlansPower` does the same for the Plans she is holding. Those stay
/// exactly as they are. A badge can only be read once the thing exists on
/// the board; the card-side keyword is what a player reads in HAND, in a
/// reward, in a shop and on the blind-play page -- which is where the word was
/// first met and where it explained nothing.
///
/// THE NUMERALS ARE INTERPOLATED FROM THE CONSTANTS THEY QUOTE (`EB-89`), so a
/// retune of `KleeOverhaulLaw.BombGrowth` cannot leave one of these
/// sentences telling a player a retired number.
/// </summary>
public static class ArmKeywordTips
{
    /// <summary>The hover-tip title table, the same one every other tip in the
    /// mod titles itself from.</summary>
    private const string Table = "card_keywords";

    // The keys. `KLEEMOD-ARM_` and not the bare word, because two of these
    // words already have a SHIPPED keyword with a DIFFERENT rule: `Bomb` is
    // `KLEEMOD-BOMB` (the shipped Bomb detonates by itself, this one never
    // does) and `Swirl` is `KLEEMOD-SWIRL_PREVIEW` (a board-aware preview,
    // raised only while a matching aura is out). A shared key would have made
    // one arm silently overwrite the other's definition at the loc merge.
    public const string BombKey = "KLEEMOD-ARM_BOMB";
    public const string SetOffKey = "KLEEMOD-ARM_SET_OFF";
    public const string SparkKey = "KLEEMOD-ARM_SPARK";
    public const string MineKey = "KLEEMOD-ARM_MINE";
    public const string HexereiKey = "KLEEMOD-ARM_HEXEREI";
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";
    public const string DeployKey = "KLEEMOD-ARM_DEPLOY";
    public const string EvokeKey = "KLEEMOD-ARM_EVOKE";
    public const string DrainKey = "KLEEMOD-ARM_DRAIN";

    // ----------------------------------------------------------- Klee ------
    //
    // The four sentences are the ruled brief's sec.3 rules 1, 2, 4 and 6, as
    // slice one prints them (`review/active/klee-overhaul-slice-1-2026-09-01.md`
    // sec.2, "Keywords with tooltips: Bomb, Set off, Spark, Mine").

    /// <summary>Rule 1. Deliberately NOT the badge's paragraph: the badge
    /// speaks about one enemy's live pile, this speaks about the word.
    ///
    /// THE SECOND SENTENCE IS <c>EB-287</c>. The r3 Opus seat called the
    /// stacking "the single most important interaction in the deck and I only
    /// found it by gambling a card on it", because nothing printed said what
    /// happens when a second Bomb lands where one already is. It says what is
    /// TRUE and stops there: the charges share one pile and one badge total
    /// and one <i>Set off</i> pops all of them, but they stay separate charges
    /// and each grows on its own -- fusing them into a single charge is
    /// Careful Arrangement's whole card, and a tip claiming the kit did it for
    /// free would print that card as a blank.
    ///
    /// THE LAST CLAUSE IS `EB-343` (R248), and it is the one thing a player
    /// cannot get from the badge: the badge shows the number, this says whose
    /// number it is. A Bomb is the ENEMY'S burden, their debuffs moving it
    /// while Klee's Strength and Weak do not, which is the opposite of what
    /// every other damage source in her deck does. A rule that runs backwards
    /// to the rest of the game cannot be inferred from a total that did not
    /// change, so it is printed where the word is met.
    ///
    /// IT IS TWO SENTENCES AND IT FITS, which is the point of the rewrite
    /// ([USER], PR #340, the same call as the Plan tip in #335). The four rules
    /// used to be four sentences and 195 characters, over a ceiling that is the
    /// base game's own longest mechanic tip -- and a seat reads this word every
    /// turn. The compression is in the grammar, not in the content: rule 1's
    /// rate, rule 7, rule 2's "all at once" and R248's burden are all still
    /// here, and the growth rate is still interpolated so a repricing cannot
    /// leave the sentence lying (`EB-89`).
    ///
    /// "not yours" RATHER THAN NAMING STRENGTH AND WEAK, and it costs nothing
    /// true: the enemy's debuffs are what DOES move the number, so what is left
    /// to say about the player's own modifiers is that none of them count. The
    /// static badge face beside it (`ProtoBombPower`'s `description`) names the
    /// two by name for the reader who wants them.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "A charge on an enemy: grows " + KleeOverhaulLaw.BombGrowth
          + " a turn, goes off only when [gold]Set off[/gold], all at once. "
          + "Its hit takes the enemy's debuffs, not yours.");

    /// <summary>Rule 2, and the one [USER] named ("Set Off has no tooltip
    /// text"). The ORDER clause is the load-bearing half: the explosions land
    /// BEFORE the rest of the card, which is what makes a cooked pile worth
    /// more than the Attack printed beside it.</summary>
    public static IEnumerable<IHoverTip> ForSetOff(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SetOffKey,
            "Every [gold]Bomb[/gold] on the target goes off first, one at a "
          + "time, each a Pyro hit for its size.");

    /// <summary>Rule 4. The gain rate is read from
    /// <see cref="KleeOverhaulLaw.SparkPerExplosion"/>, which is also
    /// Pounding Surprise's whole body under this arm.</summary>
    public static IEnumerable<IHoverTip> ForSpark(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SparkKey, SparkBody());

    /// <summary>
    /// THE ONE SENTENCE THAT IS NOT THE SAME IN BOTH KLEE ARMS, so it is the
    /// one clause this body decides at runtime rather than printing flat.
    ///
    /// The Sparks arm's rows print `Spark` too (twelve faces of them, from
    /// `Second Helping` to `True Spark Knight`), and under THAT arm the gain
    /// is Pounding Surprise's -- a relic's body, not a kit rule -- so the
    /// overhaul's "you gain one whenever a Bomb goes off" would be a rule
    /// stated about an arm that does not have it. What both arms DO share is
    /// the rest of rule 4, and it is exactly what `SparkPower`'s own retired
    /// face says ("a resource; cards that print a Spark price spend it"): the
    /// alternative cost is live in every prototype build, because
    /// `SparkPower.BaseRuleActive` is `false` whenever `PROTOTYPE_CARDS` is
    /// defined. So the shared clauses are unconditional and the kit rule joins
    /// them only under the arm that owns it.
    /// </summary>
    private static string SparkBody()
    {
        const string word =
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ";
        const string shared = "Gone after combat.";
        if (!KleeOverhaul.Enabled) return word + shared;
        // R242 pick 1 put the opening bank INTO rule 4, and the tip is where a
        // player meets the word: a Spark-priced card in an opening hand is
        // exactly the moment the r4 seat found unplayable by construction, and
        // the sentence that fixes it belongs beside the one that was already
        // there rather than on a relic the player may not have read.
        return word + "Start each combat with " + KleeOverhaulLaw.OpeningSpark
             + ". Pounding Surprise grants more. " + shared;
    }

    /// <summary>
    /// Rule 6, and its SECOND sentence is `EB-291`.
    ///
    /// The Bomb badge learned to say "after [gold]Weak[/gold]" at `EB-287`.
    /// The Mine, which fires on its own during the ENEMY's turn and so is
    /// never in front of a player at the moment it matters, said nothing at
    /// all. The r4 Opus seat left a Gremlin Merc at 3 HP under a "Mine 3" as a
    /// deliberate free kill, the Mine dealt 2, and the enemy survived and hit
    /// him: "The Mine has no equivalent... no number, no Weak note."
    ///
    /// It states the RULE rather than a number, because a keyword tip is read
    /// in hand where there is no pile to quote: a Mine IS a Bomb, so it is the
    /// same Pyro hit for its own size and the same modifiers move it. The live
    /// arithmetic stays where it can be right -- on the badge.
    ///
    /// THE SECOND SENTENCE NAMES THE ENEMY NOW (`EB-343`, R248). It used to say
    /// "[gold]Weak[/gold] shrinks it like any Bomb", which was true of the old
    /// rule and is false of this one -- Weak on Klee no longer reaches a Bomb
    /// at all. What survives is the half the r4 seat actually needed: a Mine's
    /// number is on the badge, and it is not the printed size when the enemy
    /// carries a modifier.
    ///
    /// AND THE SEMICOLON WENT WITH IT, which is not a style note.
    /// `tools/lint_text_conventions.py` reads these bodies out of the SOURCE
    /// with a regex that stops at a semicolon, so the one this sentence
    /// carried had kept the whole Mine tip out of the census -- it was never
    /// measured against the tip ceiling in either wording. The regex is fixed
    /// in the same change; this sentence is a comma now and the tip is 134 of
    /// 135.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off when its enemy attacks "
          + "you, before the hit lands. The enemy's debuffs move it, and the "
          + "badge has the number.");

    /// <summary>
    /// KLEE'S FIFTH, R244 (`review/ruled/klee-hexerei-readers-2026-09-02.md`
    /// sec.4, which asks for this tip by name).
    ///
    /// THE WORD WAS ALREADY ON EIGHTEEN FACES AND EXPLAINED NOWHERE. `Hexerei`
    /// is a one-word family mark carried by thirteen Mondstadt Universals,
    /// Prune's Personal and the four family stand-ins, and it does nothing by
    /// itself -- so until the readers existed there was nothing to read and
    /// nothing to say. Now three cards in Klee's own pool pay for it, and a
    /// player who meets the word on a reward screen has to be able to find out
    /// which cards are in the family.
    ///
    /// THE SECOND SENTENCE IS THE HALF A PLAYER CANNOT INFER, and it is the
    /// brief's sec.7.4 refinement: Klee is herself Hexerei, so a circle is her
    /// plus one witch rather than two cards. Without it, a player holding
    /// Witches' Circle and one Universal would have no way to know the card
    /// was live.
    /// </summary>
    public static IEnumerable<IHoverTip> ForHexerei(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, HexereiKey,
            "A [gold]Companion[/gold] card from the witches' circle. It does "
          + "nothing by itself; Klee is one too, and her own cards pay when "
          + "you play one.");

    // ---------------------------------------------------------- Kokomi -----
    //
    // Her TWO, and the slice's own rules section is what makes it two
    // (`review/active/kokomi-overhaul-slice-1-2026-09-01.md` draft 6 sec.2,
    // "Keywords with tooltips: Plan, Mend"). Draft 2 printed six; Tide, Surge,
    // Exert and Garment left with the rules they named.

    /// <summary>
    /// RULE 2, THE WHOLE KIT, IN TWO SENTENCES AND UNDER THE CEILING. Five
    /// clauses have to fit: where the card is played, that its cost is paid
    /// now, when the line happens, what it aims at, and who deals its damage.
    ///
    /// THE FIFTH CLAUSE IS `EB-334`, and R246 pick 1 asks for it in as many
    /// words. Three seats derived the Plan's arithmetic from the board and got
    /// three different answers, because the rule was stated nowhere: one found
    /// that Plans keep their full number while she is Weak, one that they pay
    /// x0.75 against a Strategic enemy, and one that Vulnerable did not
    /// multiply a Plan at all
    /// (`review/ruled/kokomi-overhaul-round-4c-2026-09-02.md` sec.2). The rule
    /// is now the honest one -- the Bake-Kurage deals it -- and this is where
    /// the player reads it, beside the word it belongs to.
    ///
    /// THE PROSE IS COMPRESSED RATHER THAN EXEMPTED. The four older clauses
    /// used the whole 135-character tip ceiling on their own, so the fifth
    /// briefly took a named exception in `tools/lint_text_conventions.py`.
    /// That was the wrong trade and it was reverted: the ceiling is the base
    /// game's own longest tip (CHANNELING, 134) and THIS tip is read every
    /// turn, so the sentences were rewritten to carry all five clauses in 134
    /// characters instead. Nothing was dropped -- "on the Bake-Kurage" is
    /// still where it is played, "paid now" is still the cost, "lands first
    /// thing next turn" is still the delay, "on the front enemy" is still the
    /// aim, and the second sentence is the new rule.
    ///
    /// "ON THE BAKE-KURAGE" IS STILL `EB-293`'s ANSWER, and it is still the
    /// load-bearing half: a player who has never read the brief has to be able
    /// to find "play it on the jellyfish" from the card in their hand, which is
    /// the slice's own first acceptance sentence (sec.1). The r2 Opus seat
    /// could not tell -- "Plan-only cards never say what happens if you play
    /// them normally... I never risked finding out" -- so a Plan-only row's own
    /// face also leads with "Play on the Bake-Kurage." (the codegen's
    /// <c>_plan_only_line</c>), and this definition is why some rows carry that
    /// line and others do not.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "On the [gold]Bake-Kurage[/gold], paid now; the [gold]Plan[/gold] "
          + "lands first thing next turn on the front enemy. Enemy "
          + "[gold]Vulnerable[/gold] raises it; your [gold]Weak[/gold] does "
          + "not.");

    /// <summary>
    /// THE BOUND IS THE WHOLE POINT OF THIS ROW'S SECOND HALF. The Casket read
    /// as broken at full HP because a Mend at the ceiling does nothing and
    /// nothing on screen said there was a ceiling. The sentence is
    /// <see cref="KokomiRules.Mend"/>'s own ("never above the HP you entered
    /// the fight with"), so the rule and its only explanation are one line
    /// apart.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MendKey,
            "[gold]Mend N[/gold]: heal N HP, never above the HP you entered "
          + "the fight with.");

    // ------------------------------------------------------- companions ----

    /// <summary>
    /// The companion arm's one invented-looking word, and it is not invented:
    /// `Swirl` is the shared Anemo reaction, printed as a VERB by ten Mondstadt
    /// and Inazuma Universals ("Swirl an enemy's aura"). The eight reaction
    /// PREVIEWS already in <see cref="KleeKeywords"/> are board-aware and
    /// appear only while a matching aura is out, so a face that prints the word
    /// over an aura-less board explained nothing. The sentence is the shipped
    /// preview row's, restated for the verb.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSwirl(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SwirlKey,
            "The enemy's aura is consumed and copied onto ALL enemies. No "
          + "aura, no effect.");

    // ---------------------------------------------------- Furina ----------
    //
    // Her THREE, and the reframe packet is what makes it three: sec.4.2 gives
    // the deploy its perform clause, sec.4.4 renames the bow and prices it,
    // sec.4.6 adds the drain. Each names a rule the SHIPPED engine does not
    // have, which is why all three live here rather than in
    // <see cref="SalonMemberTips"/> beside the member table: a release build
    // deploys without performing, bows without tripling or minting, and has
    // no drain at all, so the shipped tips are RIGHT about the shipped rules
    // and these would contradict them on every Furina face in the game.

    /// <summary>
    /// SEC.4.2, and the second sentence is the half a player cannot infer.
    /// Deploying onto a full stage has always displaced the oldest member;
    /// what the arm adds is that the displacement is an <i>Evoke</i> -- the
    /// free one, the reward for filling the stage -- so the word the card
    /// prints has to say where the other word comes from.
    /// </summary>
    public static IEnumerable<IHoverTip> ForDeploy(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DeployKey,
            "A [gold]Salon[/gold] member joins the stage and performs at "
          + "once. Onto a full stage, the front member [gold]Evokes[/gold] "
          + "first.");

    /// <summary>
    /// SEC.4.4, all three clauses, and the numerals are interpolated from
    /// <see cref="FurinaReframeLaw"/> for `EB-89`'s reason: a retune of the
    /// multiplier or the mint must not be able to leave this sentence quoting
    /// a retired number.
    ///
    /// THE PRICE CLAUSE IS NOT DECORATION. `F7` (1) made the Evoke's cost the
    /// card's own printed Encore, which is shipped machinery -- the gate and
    /// the spend both run before the op resolves -- so the word means "this
    /// card charges Encore" on every card that prints it, and a player who
    /// met the word on a Rare should not have to discover that on the second
    /// one.
    /// </summary>
    public static IEnumerable<IHoverTip> ForEvoke(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, EvokeKey,
            "The member performs and leaves. Its [gold]Fanfare[/gold] bonus "
          + "counts " + FurinaReframeLaw.EvokeFocusMult + " times and it "
          + "prints " + FurinaReframeLaw.FanfarePerEvoke
          + " [gold]Fanfare[/gold]. The card's [gold]Encore[/gold] price pays "
          + "for it.");

    /// <summary>
    /// SEC.4.6. TWO SENTENCES BECAUSE IT IS TWO FACTS, and the second is the
    /// one the meter cannot show: after the drain the bar reads 0 whether it
    /// held twelve or nothing, so what the card pays out has to be tied to
    /// what it TOOK in words as well as in code
    /// (<see cref="KleeMod.Powers.FurinaDrain"/>).
    ///
    /// NO THRESHOLD IS MENTIONED because there is none: both drain rows are
    /// playable at any value, including zero, which is the wasted play the
    /// packet deliberately leaves available.
    /// </summary>
    public static IEnumerable<IHoverTip> ForDrain(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DrainKey,
            "Your [gold]Fanfare[/gold] falls to nothing. What the card does "
          + "next is priced off the amount it took.");

    /// <summary>
    /// One tip, appended after whatever the card already carries.
    ///
    /// APPENDED RATHER THAN PREPENDED so a card's own live-arithmetic riders
    /// (the Charge rate, a reaction preview) stay at the
    /// top of the stack: those say what THIS play will do, and a definition of
    /// a word is the thing you read second.
    /// </summary>
    private static IEnumerable<IHoverTip> With(
        IEnumerable<IHoverTip> inherited, string key, string body)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(new LocString(Table, key + ".title"), body);
    }
}
