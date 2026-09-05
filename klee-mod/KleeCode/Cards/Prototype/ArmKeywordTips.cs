using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Runs;
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
    public const string GroundedKey = "KLEEMOD-ARM_GROUNDED";
    public const string OzKey = "KLEEMOD-ARM_OZ";
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";
    public const string DeployKey = "KLEEMOD-ARM_DEPLOY";
    public const string EvokeKey = "KLEEMOD-ARM_EVOKE";
    public const string DrainKey = "KLEEMOD-ARM_DRAIN";
    public const string EncoreKey = "KLEEMOD-ARM_ENCORE";

    // `EB-378`. NOT A KEYWORD, and the only key here that is not: it titles a
    // RIDER on the rows whose element arrives with the jellyfish rather than
    // with the play. It lives in this class because it is a sentence about the
    // Plan, which is this class's word and this quarantine's rule.
    public const string PlanElementKey = "KLEEMOD-ARM_PLAN_ELEMENT";

    // `EB-418`. THE SECOND KEY HERE THAT TITLES NO KEYWORD, and it names the
    // one Spark income no screen in the game stated: `KleeCompanionSpark`
    // ("Little Hexenzirkul"), the kit rule LAW:145 obliges Klee's own KIT to
    // declare because a Companion card may not print a signature resource on
    // its own face. It sits beside `PlanElementKey` for that key's reason --
    // it is a sentence about the CARD in hand, printed where that card is met.
    public const string CovenSparkKey = "KLEEMOD-ARM_COVEN_SPARK";

    // `EB-553` (R260). THE THIRD KEY HERE THAT TITLES NO KEYWORD, and it names
    // the one rule the reframe's STARTING RELIC now carries: the stage is
    // fielded before the first card is played. The relic's own face is at 117
    // of the 120-character relic ceiling and already states two rules, so the
    // third sentence rides beside it as a tip rather than displacing one of
    // them -- and a tip is where a rule about the board belongs anyway.
    public const string OpeningStageKey = "KLEEMOD-ARM_OPENING_STAGE";

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
    /// number it is. A Bomb is the ENEMY'S burden -- what the target is wearing
    /// moves it and Klee's own Strength and Weak do not, which is the opposite
    /// of what every other damage source in her deck does. A rule that runs
    /// backwards to the rest of the game cannot be inferred from a total that
    /// did not change, so it is printed where the word is met.
    ///
    /// IT IS THREE SENTENCES AND IT FITS, which is the point of the rewrite
    /// ([USER], PR #340, the same call as the Plan tip in #335). The four rules
    /// used to be four sentences and 195 characters, over a ceiling that is the
    /// base game's own longest mechanic tip -- and a seat reads this word every
    /// turn. The compression is in the grammar, not in the content: rule 1's
    /// rate, rule 7 and R248's burden are all still here, and the growth rate
    /// is still interpolated so a repricing cannot leave the sentence lying
    /// (`EB-89`).
    ///
    /// THE LAST SENTENCE IS RULE 3, AND IT IS `EB-361`. A Bomb whose enemy dies
    /// moves to a survivor at its size, and that rule was on no card, no badge
    /// and no tip: three round-10 seats met it as a surprise, one of them
    /// reading a `Bomb 36 / Bombs here: 3` on a Wriggler it had planted 11 on
    /// and filing it as something the screen contradicted. It is stated as the
    /// jump code does it (`ProtoBombPower.JumpCharges`): every charge moves,
    /// Mines included, to a random LIVING enemy, so the word is "a survivor"
    /// rather than "the next enemy".
    ///
    /// WHAT ITS 33 CHARACTERS COST, said plainly because the ceiling is the
    /// reason: rule 2's "all at once" is gone from this tip and lives on the
    /// `Set off` tip, which states it in full ("Every Bomb on the target goes
    /// off first, one at a time"), and "Its hit takes" became "It takes", the
    /// spelling the static badge face already uses.
    ///
    /// `EB-373` REWROTE THE LAST CLAUSE, WHICH WAS TOO GENEROUS BY HALF.
    /// "Takes the enemy's debuffs" is not what the code does: the fold is
    /// <c>FoldedMods</c> in <see cref="KleeMod.Powers.ProtoBombPower"/> and it
    /// reads exactly two things off the target -- its <c>VulnerablePower</c>,
    /// and whichever power sets the lowest damage cap. Every other debuff the
    /// enemy is wearing is left out, and the r9 seat priced two fights off the
    /// sentence as it stood: a Slow 50 enemy took 48 from a pile printing 46
    /// (act 1), and a Flutter 5 enemy took the full 27 from a 27 Bomb while a
    /// printed 8 Attack landed 4 (act 2). Both of those debuffs say "from
    /// Attacks" on their own faces, and the reason they miss a Bomb is the rule
    /// this clause now leads with: a Bomb's hit is not an Attack.
    ///
    /// "ONLY" IS THE LOAD-BEARING WORD, and it is also what makes the sentence
    /// fit. Naming the two terms that DO apply and nothing else says, in one
    /// clause, that no Attack-conditional debuff of the enemy's and no modifier
    /// of Klee's reaches the number -- which is three claims in the room two
    /// used to take. The static badge face beside it (`ProtoBombPower`'s
    /// `description`) spells both halves out for the reader who wants them, the
    /// same split <c>MineClause</c> already has.
    ///
    /// `EB-557` (R261) ADDED THE STARTER LINE. Jumpy Dumpty is Innate under
    /// the arm and Ka-pow! is not, so the opening hand always holds a placer
    /// and never necessarily the detonator -- and the keyword rail's own
    /// `Innate` banner says that about ONE CARD, on the card, to a player who
    /// is holding it. The fact a reader of this word needs is about the DECK:
    /// the first thing you can always do is plant. It is the last sentence
    /// because it is the only one that is not about the charge itself.
    ///
    /// `EB-555` DEFINED THE CAP, IN THE CLAUSE THAT ALREADY USED IT. "Only
    /// Vulnerable and a cap move it" printed on two tips of one screen and the
    /// word was defined on neither: "no screen I saw ever explained what a cap
    /// is. I verified the Vulnerable half; the other half is a term with no
    /// definition anywhere in the text I was shown" (Klee r20 lane 1, (c) 2).
    ///
    /// A DEFINING PHRASE AND NOT A SENTENCE, because the fact is small and a
    /// sentence of its own would spend thirty characters saying what six say
    /// inside the clause: a cap is a limit on the HP the ENEMY can lose, which
    /// is exactly what <c>ProtoBombPower.FoldedMods</c> reads -- whichever
    /// power on the target returns the lowest <c>ModifyDamageCap</c>. Naming
    /// whose HP it is also disposes of the reading the clause could not rule
    /// out before, that a cap might be something of Klee's.
    ///
    /// THE MINE TIP'S COPY IS LEFT ALONE at 133 of 135. It prints directly
    /// under this one, a Mine IS a Bomb, and the term is defined on the screen
    /// either way -- which is the acceptance condition: one definition per
    /// PAGE, rather than one per clause.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "A charge on an enemy: grows " + KleeOverhaulLaw.BombGrowth
          + " a turn, goes off only when [gold]Set off[/gold], or as a "
          + "[gold]Mine[/gold]. "
          + "Not an Attack: only [gold]Vulnerable[/gold] and a cap on the "
          + "enemy's HP loss move it. "
          + "Kills move it on. Your deck opens with a placer.");

    /// <summary>
    /// Rule 2, and the one [USER] named ("Set Off has no tooltip text"). The
    /// ORDER clause is the load-bearing half: the explosions land BEFORE the
    /// rest of the card, which is what makes a cooked pile worth more than the
    /// Attack printed beside it.
    ///
    /// `EB-432` NAMED THE OTHER ORDER, the one INSIDE the pile.
    /// <see cref="KleeMod.Powers.ProtoBombPower.SetOff"/> walks the taken
    /// charges in the order
    /// <see cref="KleeMod.Powers.ProtoBombPower.AddCharge"/> appended them --
    /// the list's own comment is "Charges in placement order" -- and the FIRST
    /// one through the funnel is the one that meets the enemy's aura, because
    /// every reaction consumes it (<c>ReactionEffects</c>, `consumedAura`).
    /// The r11 run-2 seat priced its best turn of the run off that rule and
    /// could only get it by arithmetic: "22 = 8 (the Bomb 5, Melted to 8.75 to
    /// 8) + 8 + 6. Bombs go off in placement order, and the first one is the
    /// one that eats the Melt -- a rule nothing printed, that I could only
    /// infer from the arithmetic."
    ///
    /// "OLDEST FIRST" REPLACES "ONE AT A TIME" AND LOSES NOTHING. An order
    /// that names a first and a rest is one at a time by construction, and the
    /// separateness the old phrase carried -- three charges, three hits, three
    /// Sparks -- is what "each a Pyro hit" says. `EB-287`'s claim that a pile
    /// goes off TOGETHER is still here and is now the subject of the sentence:
    /// "the target's Bombs", all of them.
    ///
    /// "THE FIRST TAKES THE AURA" AND NOT "ONLY THE FIRST REACTS", which would
    /// be false on a board this build really has: a Swirl re-applies the aura
    /// it consumed to every living enemy, the target included
    /// (<c>ReactionEffects</c>, the `Swirl` arm), so a charge behind a Swirl
    /// meets a fresh aura and reacts again. What is true on every board is the
    /// sentence the player is deciding on: the aura in front of them is spent
    /// on the OLDEST charge.
    ///
    /// `EB-443` ADDED THE TWO FACTS THE OLD NEGATIVE LEFT TO INFERENCE. "Not
    /// an Attack" is on the Bomb tip and it answers a question a player did
    /// not ask: the r12 run-2 seat ran the experiment and drew the wrong
    /// conclusion from it -- "Set off ignores enemy Block, and no card says
    /// so. Two 11-point bombs both landed at full value into Skittish 6...
    /// 'not an Attack' plainly did not stop it from HITTING (Skittish did not
    /// fire), and a rule this load-bearing against a whole class of enemy
    /// should not be an inference from a negative." Both halves are read off
    /// the one call the explosion makes:
    /// <see cref="ElementalHit.DealWithoutDealerMods"/> passes
    /// <c>ignoreBlock: false</c>, so Block absorbs it like anything else, and
    /// it reaches <c>CreatureCmd.Damage</c> as <c>ValueProp.Unpowered</c> with
    /// <c>dealer: null</c>, so nothing an enemy keys on being hit by an Attack
    /// can fire. The seat was right about the Block it saw and wrong about the
    /// rule: there was no Block, because Skittish never fired.
    ///
    /// "FOR ITS SIZE" IS WHAT PAID FOR THEM, and it is the trade the Mine tip
    /// already makes for the same reason. A keyword tip is read in HAND, where
    /// there is no pile to quote, so an arithmetic claim here is one this
    /// surface cannot get right; the number a Set off will deal is on the
    /// badge, live, and that is `EB-343`'s own split between the two. "Each a
    /// Pyro hit" keeps what the tip can say -- separate hits, so separate
    /// reactions and separate Sparks. 132 of 135 rendered, no exception taken.
    ///
    /// `EB-490` NAMED THE CLASS INSTEAD OF THE TRIGGER, and the two clauses
    /// `EB-443` landed are why it had to. "Block stops them" and "no Attack
    /// trigger fires" point OPPOSITE WAYS to a reader who does not already
    /// know that Skittish is an on-hit power: the first says a Bomb interacts
    /// with what the enemy has, the second says a Bomb sets nothing off, and
    /// "Attack trigger" reads as something on the player's side of the board.
    /// The r16 Klee seat planned two turns around a tax it was not paying and
    /// got the rule by autopsy -- a 26-HP Gardener dying to 30 points of Bomb
    /// with its "first time hit each turn, gains 6 Block" never firing, which
    /// is most of why Klee beats that elite.
    ///
    /// THE RULE DOES NOT MOVE AND THE CLAIM DOES NOT WIDEN. It is the same
    /// fact read off the same call: the explosion reaches
    /// <c>CreatureCmd.Damage</c> as <c>ValueProp.Unpowered</c> with
    /// <c>dealer: null</c> (<see cref="ElementalHit.DealWithoutDealerMods"/>),
    /// so a power keyed on being HIT has neither an attacker nor a powered hit
    /// to answer. "When-hit power" is what a player calls the thing on the
    /// enemy's status bar; "Attack trigger" is what the code calls it. Same
    /// length to the character, so the ceiling reading above stands unchanged.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSetOff(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SetOffKey,
            // `EB-516`: the AIM clause. A random Set off draws from the
            // enemies already carrying one of hers, and the two rows that do
            // it (Tinder Toss, Rapid Fire) print "a random enemy" and cannot
            // say where it lands -- so the rule lives on the word, which is the
            // one surface both rows carry. Over the tip ceiling and excepted
            // by name in `tools/lint_text_conventions.py`.
            "The target's [gold]Bombs[/gold] go off first, oldest first, each "
          + "a Pyro hit. [gold]Block[/gold] stops them, no when-hit power "
          + "fires, the first takes the aura. A random one picks a Bombed "
          + "enemy first.");

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
    ///
    /// `EB-373` NARROWED THE SECOND SENTENCE HERE TOO, because a Mine IS a
    /// Bomb and the fold that moves one moves the other: `FoldedMods` reads
    /// the target's Vulnerable and its damage cap and nothing else. "The
    /// enemy's debuffs move it" promised a Slow or a Flutter would, and the
    /// number on the badge said otherwise in two of the r9 fights. Same rule,
    /// same words as the Bomb tip, so the two cannot be read against each
    /// other.
    /// </summary>
    /// `EB-436` SAID WHAT THE OLD SENTENCE LEFT OUT, and the old sentence was
    /// true the whole time: "goes off when its enemy attacks you, before the
    /// hit lands" says WHEN and says nothing at all about the hit. The r12
    /// act-1 seat read mitigation into it and played a turn on that read --
    /// three Mines left armed against an elite, five went off, "every hit
    /// landed in full, 36 to 18 HP". A Mine blunts nothing: the only thing a
    /// Mine can do to the attack is stop it happening, by killing the
    /// attacker, and that is `EB-336`'s rule (`Preempted`) -- a Mine whose
    /// explosion kills the attacker costs Klee no HP, and nothing short of a
    /// kill costs the attacker anything.
    ///
    /// "READ THE BADGE:" IS WHAT PAID FOR IT. The clause it introduced is
    /// still here word for word and still names both terms, so `EB-343`'s
    /// rule survives whole; what went is the pointer, which a player standing
    /// in front of the badge does not need and a player in hand cannot use.
    /// 133 of 135 rendered, no exception taken.
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off before its enemy's hit, "
          + "which lands in full unless the Mine kills. Only their "
          + "[gold]Vulnerable[/gold] and a cap move it.");

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
    /// `EB-392` REWROTE IT, because "from the witches' circle" was doing
    /// silent work and the r12 run-2 seat said so: "I could not tell from any
    /// card face whether MY Companion qualified. I found out by counting bombs
    /// on an enemy badge." Then it met a second word on the same screen and
    /// had three: "there is apparently a distinction between `Companion`,
    /// `Hexerei`, and `Klee's own Companion`, and none of the three cards
    /// involved prints which one it is."
    ///
    /// THE FIRST SENTENCE IS ANSWERABLE NOW, and it was not before: every
    /// Hexerei Companion prints the word on its own face
    /// (`gen_klee_cards._hexerei_tag`), so "a Companion card that prints the
    /// word" is a test a player can run on the card in their hand. "And Klee
    /// herself" is the brief's sec.7.4 refinement, unchanged.
    ///
    /// THE SECOND SENTENCE IS THE THIRD WORD, and it is stated as the OVERLAP
    /// it really is rather than as an exclusion. Five rows carry both marks
    /// and thirteen carry only one, so "a different set" would be a lie in
    /// both directions; "some are Klee's own, some are not" is what the sheet
    /// says. `Klee's own` is the exact phrase the Spark rider uses
    /// (<see cref="ForCovenSpark"/>), so the two words meet under one
    /// spelling.
    ///
    /// "IT DOES NOTHING BY ITSELF" LEFT and is not missed: it was true of a
    /// word with no readers, and three cards in Klee's pool have paid for it
    /// since R244. The last sentence says that instead.
    ///
    /// `EB-504`, REOPENED 2026-09-05: THE RULE IS KLEE'S AND THE WORD IS
    /// EVERYONE'S. See <see cref="KleesRuleBelongsHere"/>. The page glossary
    /// was gated on the r17 finding and this tip was the second source, so
    /// Razor's own face still printed the whole sentence on a Kokomi run.
    /// `EB-535`: AND THE LAST SENTENCE NOW SAYS WHAT THE PAYMENT IS.
    ///
    /// THE FIND (Klee r19 lane 2). "I read this a dozen times across five
    /// fights and I still do not know what it does. 'Cards of hers pay' -- pay
    /// what, to whom, and when? I played Razor four times and never saw
    /// anything I could attribute to Hexerei." The rule was on a DIFFERENT
    /// screen the whole time -- <see cref="ForCovenSpark"/>, which rides Klee's
    /// own Personal Companions and not the family tag -- and the seat found it
    /// late and still could not tell whether Razor was one of Klee's own.
    ///
    /// SO THE READER CLAUSE GAVE UP ITS ROOM. "Cards of hers pay when you play
    /// one" is the sentence the seat could extract nothing from, and the cards
    /// it is about print their own rule on their own faces; the family test and
    /// the ownership split stay, because "some are Klee's own, some are not" is
    /// the half that answers the Razor question. 135 of 135 rendered.
    ///
    /// `EB-554` MADE THE OWNERSHIP CLAUSE POINT AT A MARK. "Some are Klee's
    /// own, some are not" told a reader the split exists and gave them no way
    /// to run it: Klee r20 lane 1 played Albedo+ and Razor in one turn, both
    /// printing the word, and Spark stayed at 1 -- "nothing on either card
    /// face distinguishes 'hers' from not-hers, so as a reader I have no way to
    /// predict which Companion pays a Spark. This is the clearest thing I could
    /// not resolve all round." The faces carry the mark now
    /// (`gen_klee_cards._family_tags`), so the sentence says ONLY the marked
    /// ones pay and names the mark it is pointing at. "A play" replaces the
    /// bare cap's grammar and pays for the change.
    ///
    /// THE NUMBERS ARE LIFTED, not typed (`EB-89`'s rule): they are
    /// <see cref="KleeMod.Powers.KleeCompanionSpark"/>'s own, which is the
    /// declaration LAW:145 obliges the KIT to make, so a retune cannot leave
    /// this sentence quoting a retired figure. The BOUND is printed here and
    /// deliberately not on <see cref="ForCovenSpark"/>, where it would state a
    /// ceiling no single clause reaches; here it is the whole of what a player
    /// asking "how much" needs.
    public static IEnumerable<IHoverTip> ForHexerei(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        !KleesRuleBelongsHere(card) ? inherited :
        With(inherited, HexereiKey,
            "A [gold]Companion[/gold] card that prints the word, and Klee "
          + "herself. Only the ones marked Klee's own pay: [blue]"
          + KleeCompanionSpark.Base + "[/blue] [gold]Spark[/gold] a play, up "
          + "to [blue]" + KleeCompanionSpark.MaxPerPlay + "[/blue].");

    /// <summary>
    /// `EB-446`. A NAME ON ONE FACE THAT BELONGS TO ANOTHER CARD.
    ///
    /// THE GAP. <i>Fischl -- Nightrider</i> prints "If Oz is out, he deals 5
    /// Electro damage to a random enemy" and nothing on the screen says what
    /// puts Oz out. The r7 seat played the card five times and never learned
    /// it: the word reads as an undefined keyword, and the thing it actually
    /// names is a DIFFERENT companion card -- the Power <i>Fischl -- Oz, at
    /// Your Side</i> -- which that run never held and may never be offered.
    ///
    /// SO THE TIP NAMES THE POWER, which is the one fact the reader is missing
    /// and cannot derive. `Grounded`'s shape exactly (`EB-372`): a word one
    /// card is written against, defined on the face that prints it rather than
    /// on the card that grants it, because the attach travels with the WORD
    /// (`gen_klee_cards.arm_keyword_tip_calls`) and not with the deck.
    ///
    /// WHAT IT LEAVES TO THE CARDS. How much Oz deals and for how long are the
    /// two faces' own printed numbers, and both move on an upgrade, so the tip
    /// says what Oz IS and which card puts him out and stops there, the way
    /// `ForGrounded` defers its payout to the Power card's own line.
    /// </summary>
    /// `EB-504`, the second of the two words whose rule is Klee's: the Power
    /// that fields Oz is hers, and Fischl's face is drafted by every
    /// character. See <see cref="KleesRuleBelongsHere"/>.
    public static IEnumerable<IHoverTip> ForOz(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        !KleesRuleBelongsHere(card) ? inherited :
        With(inherited, OzKey,
            // A card TITLE is a plain word, never golded
            // (`docs/current/text-conventions.md`, and the lint bites), and
            // the title is quoted WITHOUT its `Fischl --` prefix because the
            // conventions ban a dash of any kind in player text.
            "Fischl's raven, out while you hold the Power Oz, at Your Side. "
          + "He hits at the end of your turn while he is out.");

    /// <summary>
    /// KLEE'S SIXTH, `EB-372`, AND IT IS A WORD THE KIT NAMES ON A FACE THE
    /// PLAYER MAY NEVER HAVE OWNED.
    ///
    /// THE GAP. `Grounded` is a Power of Klee's, and Kaeya's Cold-Blooded
    /// Strike is written against it -- "This turn, Grounded counts nothing as
    /// having gone off" -- as is the buff that card leaves behind
    /// (<see cref="KleeMod.Powers.ColdBloodedPower"/>). A player who drafted
    /// Kaeya without ever drafting Grounded meets the word on a card face with
    /// nothing anywhere on the screen saying what it is, and the r9 seat read
    /// it as noise in both acts (act 1 sec.(c) 3, act 2 sec.(c) 2).
    ///
    /// IT TRAVELS WITH THE WORD AND NOT WITH THE DECK. The attach is derived
    /// from the printed face (`gen_klee_cards.arm_keyword_tip_calls`), so
    /// Kaeya carries the definition because Kaeya prints the word -- whether or
    /// not the run holds Grounded, which is the state the seat was actually in.
    ///
    /// WHAT IT SAYS AND WHAT IT LEAVES TO THE CARD. The CONDITION is the whole
    /// rule and it is what a Kaeya reader needs: `EB-516` moved it to "you have
    /// a Bomb on the field" and the tip moved with it. What Grounded pays for
    /// that is the Power card's own printed line and moves with its upgrade, so
    /// the tip defers to it rather than quoting a number that a second card
    /// would contradict.
    /// </summary>
    /// ONE METHOD WITH AN OPTIONAL CARD, and not an overload: a POWER raises
    /// this tip too -- the buff Kaeya's card leaves behind prints the word for
    /// the rest of the turn, after the card itself has gone -- and every other
    /// attach here ignores its `card` argument anyway. A second entry point
    /// would be a second thing for `ArmKeywordTipTests`' structural pin to
    /// count, and it is the pin that proves every tip goes through `With`.
    public static IEnumerable<IHoverTip> ForGrounded(
        IEnumerable<IHoverTip> inherited, CardModel? card = null) =>
        With(inherited, GroundedKey,
            // A card TYPE is a plain word, never golded
            // (`docs/current/text-conventions.md`, and the lint bites).
            "A Power that pays at the start of your turn, but "
          + "only if you have a [gold]Bomb[/gold] on the field. Its "
          + "card prints what it pays.");

    /// <summary>
    /// `EB-418`, AND IT IS THE ONE NUMBER IN THE KIT A SEAT COULD NOT READ OFF
    /// THE SCREEN.
    ///
    /// THE GAP. <see cref="KleeMod.Powers.KleeCompanionSpark"/> -- "Little
    /// Hexenzirkul" -- mints a Spark on every play of one of Klee's OWN
    /// Personal Companions, and it is printed nowhere: LAW:145 forbids the
    /// Companion card from carrying the grant on its face ("Companion cards may
    /// not themselves grant signature resources"), so the rule moved WHOLE into
    /// her kit at `EB-219` and the sentence did not move with it. The
    /// companions packet says so in as many words -- "the kit already pays a
    /// rider neither card prints" -- and the r11 Opus seat met the consequence
    /// as the only unreadable number in five fights: "My Spark went 1 to 2 with
    /// no bomb going off... This is the one number in the kit I could not read
    /// off the screen."
    ///
    /// WHERE IT HAPPENS IS THE CARD, so that is where it prints. The Spark
    /// keyword tip is full -- four sentences and 130 of its 135 characters
    /// since R242 put the opening bank in it -- and in any case it is met on a
    /// Spark-priced Attack rather than on the Companion that pays. A rider on
    /// the Companion's own face is read at the moment the energy is committed,
    /// which is the moment the seat's read was wrong.
    ///
    /// THE THREE LIMBS ARE THE POWER'S OWN, interpolated from the constants the
    /// grant reads (`EB-89`) so a repricing cannot leave this sentence lying.
    /// The CAP is deliberately not printed: it is the sum of the three limbs
    /// (<see cref="KleeMod.Powers.KleeCompanionSpark.MaxPerPlay"/>), so a
    /// fourth clause would state a bound no reachable play can meet.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCovenSpark(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CovenSparkKey,
            "Playing one of Klee's own [gold]Companions[/gold] makes [blue]"
          + KleeCompanionSpark.Base + "[/blue] [gold]Spark[/gold], [blue]"
          + KleeCompanionSpark.ReactionBonus + "[/blue] more if it triggered "
          + "an [gold]Elemental Reaction[/gold] and [blue]"
          + KleeCompanionSpark.UpgradedBonus
          + "[/blue] more if it is upgraded.");

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
    /// still where it is played, "paid now" is still the cost, "lands next
    /// turn" is still the delay, "on the front enemy" is still the aim, and
    /// the second sentence is the new rule.
    ///
    /// "OR ALL IF IT SAYS SO" IS `EB-329`, AND THE OLD CLAUSE WAS WRONG.
    /// The aim clause said "on the front enemy" and stopped there, while
    /// Kurage's Oath -- a starter -- reads "Deal 7 damage to ALL enemies" and
    /// took two Toadpoles in fight 1 and four Phantasmal Gardeners at the
    /// first elite of the round-5 act-1 run. This tip is reprinted on every
    /// battle screen, so it was the most-read wrong sentence in the build.
    /// The card face is and was correct; the word's definition now defers to
    /// it, which is the same shape `docs/current/text-conventions.md` already
    /// states ("a Plan hits the front enemy unless it says ALL").
    ///
    /// "COUNTS" REPLACES "RAISES IT" for room, and loses nothing: the clause
    /// is about WHOSE modifiers are read, and the pair "enemy Vulnerable
    /// counts; your Weak does not" says that in fewer characters than "raises
    /// it". "First thing" left for the same reason and is the only thing that
    /// did -- 144 characters with it, 132 without, against a ceiling of 135.
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
    ///
    /// "NEVER A MINION" IS `R250`, round-5 sec.6 pick 1 at its default. The
    /// front enemy was leftmost alive, full stop, and two round-5 formations
    /// put a decoy there on purpose -- The Kin's Followers absorbed a Feint
    /// Plan meant for the Priest, and Queen's Torch Head Amalgam took every
    /// single-target Plan for a whole fight (round-5 packet sec.2). The
    /// sixth clause cost room, so "lands next turn on" compressed to "next
    /// turn:" -- nothing else in the first four clauses moved.
    ///
    /// `EB-380` FIXED THAT CLAUSE, WHICH WAS FLAT AND THE RULE IS NOT. "Never
    /// a Minion" is true of a SINGLE-TARGET Plan only: <see cref="Aim"/>
    /// <c>.AllEnemies</c> walks <c>HittableEnemies</c> and takes every living
    /// body, decoys included, and the round-9 act-1 seat watched an
    /// `Exposed Flank+` Plan land on `Eye With Teeth` while this line said it
    /// could not. Both halves are now stated, in the order a reader needs
    /// them: the aim, then the exception the word ALL makes.
    ///
    /// AND `STRENGTH` JOINED THE MODIFIER CLAUSE. The clause named Vulnerable
    /// and Weak and stopped, which reads as a complete list, and the seat
    /// priced `Kurage's Oath+` face 4 under Vajra at Plan 10 expecting her
    /// Strength to ride it (r9 run 2, act 1, (c) 5). It does not: this class's
    /// own header is why -- the carry-out goes through
    /// <see cref="ElementalHit"/> UNPOWERED, so no Strength, no Weak and no
    /// attack buff of hers reaches it. "Enemy" replaced the bare
    /// `[gold]Vulnerable[/gold]` in the same breath, because the sentence is
    /// about WHOSE modifiers are read and the old one left that to inference.
    ///
    /// 135 CHARACTERS RENDERED, at the ceiling and not over it: "the front
    /// enemy" compressed to "front non-Minion" and "or ALL if it says so"
    /// to "or ALL", which is what paid for the two new facts. The
    /// all-Minions board is the one corner left unsaid -- `FrontTarget`
    /// falls back to the leftmost body when every enemy is a Minion -- and it
    /// is a board on which the compressed clause and the full one aim at the
    /// same creature.
    ///
    /// `EB-538` TOOK IT OVER THE CEILING, and it is <see cref="ForSetOff"/>'s
    /// overage for <see cref="ForSetOff"/>'s reason. THE FIND (Kokomi r19 lane
    /// 2): Skittish gave no Block to a body hit by Oath's and Ambush's
    /// carry-outs and then 6 Block to a plain Strike on the same enemy in the
    /// same fight, and the seat could not tell "a defect or a large
    /// undocumented advantage of planning into blockers". It is the second: a
    /// carry-out goes out through <see cref="ElementalHit.Deal"/>, which
    /// reaches <c>CreatureCmd.Damage</c> as <c>ValueProp.Unpowered</c> with
    /// <c>dealer: null</c>, so a power keyed on being HIT has neither an
    /// attacker nor a powered hit to answer.
    ///
    /// SET OFF'S SENTENCE, WORD FOR WORD ("no when-hit power fires"), because
    /// it is the same rule at the same call one kit over and `EB-490` already
    /// paid for the wording: "when-hit power" is what a player calls the thing
    /// on the enemy's status bar, and "Attack trigger" reads as something on
    /// the player's own side of the board. Nothing above it is droppable --
    /// every clause there is a seat's finding -- so the tip is carried in
    /// `tools/lint_text_conventions.py` as a named exception with its reason,
    /// which is the bargain `SetOffKey` already makes.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "On the [gold]Bake-Kurage[/gold], paid now; next turn: front "
          + "non-[gold]Minion[/gold], or ALL, [gold]Minions[/gold] too. "
          + "Enemy [gold]Vulnerable[/gold] counts; your [gold]Weak[/gold] "
          + "and [gold]Strength[/gold] do not. A carry-out is not a hit: no "
          + "when-hit power fires.");

    /// <summary>
    /// `EB-378`: WHERE THE AURA CAME FROM, on the rows whose element is the
    /// jellyfish's and not the card's.
    ///
    /// <see cref="KokomiPlan.ResolveAll"/> deals every damaging Plan clause as
    /// <c>ElementalHit.Deal(..., Element.Hydro, ...)</c> whatever the card's
    /// type, so `Kurage's Oath` -- a SKILL -- leaves a Hydro aura on every
    /// enemy it takes, and the sim's twin does the same
    /// (<c>tier0/engine/kokomi_plan</c>, <c>element="hydro"</c>). The round-9
    /// act-1 seat watched that aura appear "from a card whose face says nothing
    /// about an element", and priced no reaction off it.
    ///
    /// THE CARD NOW DECLARES THE ELEMENT (the gem and the reaction rule, from
    /// <c>gen_klee_cards.aura_elements_for</c>) AND THIS SAYS WHEN. Both halves
    /// are needed and neither is enough: a gem alone would tell a player the
    /// card's own hit applies Hydro, which it does not -- <see
    /// cref="CatalystCadence.PrintedElement"/> answers <c>Element.None</c> for
    /// a Skill and this row deliberately did not change that.
    ///
    /// ATTACHED ONLY WHERE THE TWO DISAGREE. A row whose own damage already
    /// carries the element (every Attack of hers) needs no such sentence, so
    /// `gen_klee_cards.emit` raises this one only where the Plan is the sole
    /// source.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlanElement(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanElementKey,
            "Its own hit applies no aura; the [gold]Bake-Kurage[/gold] carries "
          + "out the [gold]Plan[/gold] as a [gold]Hydro[/gold] hit, which "
          + "does.");

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
    ///
    /// `EB-368` ADDED THE THIRD SENTENCE. The act-2 seat played no Salon card
    /// across three fights, and the reason is the rule this word did not
    /// carry: a member on stage does NOTHING on its own, and what makes it act
    /// afterwards is a Companion card. A player who reads only "joins the
    /// stage and performs at once" prices a deploy as a one-shot, and a
    /// one-shot at that price is never worth the card.
    ///
    /// THE WORD WAS REWRITTEN RATHER THAN EXTENDED, the Bomb's precedent
    /// (`EB-343`, R248): three rules appended to the old two sentences ran 50
    /// characters over the tip ceiling, and the ceiling is the base game's own
    /// longest mechanic tip. All three are here in two sentences, and the tip
    /// takes no length exception. "[gold]Salon[/gold]" goes with them: this tip
    /// only ever renders beside the member tips, which name the stage.
    /// </summary>
    public static IEnumerable<IHoverTip> ForDeploy(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DeployKey,
            "A member joins and performs at once; a full stage "
          + "[gold]Evokes[/gold] the front member first. Afterwards only a "
          + "[gold]Companion[/gold] play performs a member.");

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
    /// `EB-407`. THE WORD IS PRINTED BEFORE THE PLAYER HOLDS ANY. Encore is
    /// named on the Neow screen and on opening-hand faces, and the shipped
    /// surface that states its rule is `EncoreMeterPower`'s badge -- which
    /// only ever renders once the meter is on the board. The Furina round-4
    /// seat made the run's first decision without the word (run 1, (c) 5).
    ///
    /// THREE FACTS, EACH READ OFF ITS OWN SITE, no fourth invented:
    ///   * the buffer, <see cref="KleeMod.Powers.FurinaResources.AbsorbDamage"/>
    ///     -- damage remaining after Block consumes Encore before HP;
    ///   * a card's price, <c>FurinaResourceHooks.BeforeCardPlayed</c> --
    ///     spent immediately after the energy debit and BEFORE resolution;
    ///   * a member's 1, <see cref="KleeMod.Powers.SalonMemberPower"/>'s
    ///     <c>PerformMember</c> -- it pays <c>TickEncoreCost</c> if it can and
    ///     performs at <c>DryDamageMultiplier</c> (3/4) if it cannot.
    ///
    /// AND THE ORDER, WHICH IS THE HALF NOTHING PRINTED. All three draw on one
    /// amount, in the order the events reach it: there is no reservation and
    /// no priority anywhere in those three sites, so a hit that lands first
    /// leaves a member performing dry, and a member that performs first leaves
    /// less buffer for the hit. "One pool, as each lands" is that, in the
    /// space the 135-character tip ceiling leaves.
    /// </summary>
    public static IEnumerable<IHoverTip> ForEncore(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, EncoreKey, EncoreBody());

    /// <summary>
    /// `EB-553` (R260): the reframe's stage is never unlit, and the relic that
    /// fields it is where a player reads so.
    ///
    /// Round 11 read both lanes' turn one as empty BY CONSTRUCTION and the
    /// natural lane counted it -- zero empty turns in the fights where the
    /// starter deploy was in the opening hand, six of twenty-two otherwise.
    /// [USER] took the relic over an Innate starter, so the fact belongs to
    /// the relic and not to a card: it is true on turn one of every fight
    /// whatever the opening hand holds.
    ///
    /// THE MEMBER IS NAMED IN FULL here and short on the badge, which is the
    /// shipped split: <c>SalonMemberPower.ManualFrontName</c> prints
    /// "Crabaletta" because three rules and an identity have to fit under the
    /// power ceiling, and a tip with one sentence in it can afford her title.
    ///
    /// `EB-558` ADDED THE SECOND SENTENCE, because the first one hid a price.
    /// The arrival is a deploy and a deploy performs, so a reader who knows
    /// the deploy rule reads "opens with her on stage" as "opens one Encore
    /// down" -- which is what the build did until R260's arithmetic was
    /// settled. It does not now: the arrival performs at full value and costs
    /// nothing, so turn one opens on the whole of R258's bank. Both halves are
    /// stated, because "performs" without "free" is the reading that costs a
    /// player their opening move.
    /// </summary>
    public static IEnumerable<IHoverTip> ForOpeningStage(
        IEnumerable<IHoverTip> inherited) =>
        With(inherited, OpeningStageKey,
             "Every fight opens with [gold]Mademoiselle Crabaletta[/gold] on "
           + "stage. She performs on arrival for free.");

    /// <summary>
    /// `EB-479` (R258): THE OPENING JOINS THE SENTENCE THAT DEFINES THE WORD,
    /// and only under the arm that grants it -- <see cref="SparkBody"/>'s
    /// shape one character over, for its reason.
    ///
    /// Rounds 5 to 8 each read the reframe's turn one as no decision at 0
    /// Encore, and round 9 called the opening "by construction its own weakest
    /// version". The tip is where a player meets the word, and an opening bank
    /// nobody is told about is one the first turn cannot be planned around.
    /// The shipped kit grants none, so the release sentence stands untouched
    /// with the arm off.
    ///
    /// THE THIRD CLAUSE PAID FOR IT. "As each lands" became "in order" and the
    /// two "to resolve" / "to perform" tails went, which keeps all three
    /// spenders AND the ordering fact inside the 135-character ceiling: 133
    /// rendered under the arm, 134 with it off. The AMOUNT is interpolated
    /// from the arm's own law (`EB-89`'s rule, one meter over), so a retune
    /// cannot leave this sentence quoting a number nothing grants.
    /// </summary>
    private static string EncoreBody()
    {
        // NOT `word`, which is <see cref="SparkBody"/>'s name for its own
        // half: `lint_text_conventions.tip_rows` reads these two bodies out of
        // the SOURCE by const name, and a second `word` in the same file would
        // have it measure the Spark tip's opening twice and this one never.
        const string absorbs =
            "After [gold]Block[/gold] it absorbs damage before HP. ";
        if (!FurinaReframe.Enabled)
        {
            return absorbs + "One pool, as each lands: a card pays to "
                 + "resolve, a member spends 1 to perform or acts at 3/4.";
        }
        return absorbs + "Start each combat with "
             + FurinaReframeLaw.OpeningEncore
             + ". One pool, in order: a card pays, a member spends 1 or acts "
             + "at 3/4.";
    }

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

    /// <summary>
    /// `EB-504`. IS THERE A KLEE IN THIS RUN FOR KLEE'S RULE TO BE ABOUT?
    ///
    /// THE ROW WAS CLOSED ONCE ON THE PAGE GLOSSARY AND REOPENED ON THE CARD.
    /// `Hexerei` rides eighteen companion faces the whole roster can draft and
    /// its rule is Klee's Spark rider; `Oz` is named by Fischl's face, which
    /// every character meets, and the Power that fields him is hers. So the
    /// WORD reaches every run and the RULE reaches one.
    /// `blindplay_notes._ARM_KEYWORD_CHARACTER` gated the page's own glossary
    /// on the r17 finding, and the r18 lane-2 seat then met the same sentence
    /// on Razor's own card: "two Companion cards in a Kokomi run printed
    /// 'Hexerei -- ... Cards of hers pay when you play one.' I could not tell
    /// what is paid, by whom, or whether it applies to me at all, so I refused
    /// both cards partly on that." The card's tip is a second printer.
    ///
    /// THE OWNER FIRST, BECAUSE IT IS THE ONE THAT IS ALWAYS RIGHT. A card in
    /// a hand or a deck belongs to a seat and that seat has a character; only
    /// where there is no owner -- a shelf, a reward, a compendium page -- does
    /// this fall back to the run's player list, which is the same question one
    /// scope out and the one that answers in co-op.
    ///
    /// SILENCE IS NOT EVIDENCE, and it is the page's own direction here
    /// (`absent is not zero`): where NOTHING says who is playing, the rule
    /// prints. A missing tooltip on a Klee run would be the worse failure of
    /// the two, and it is the one this returns true to avoid.
    /// </summary>
    public static bool KleesRuleBelongsHere(CardModel card)
    {
        var inRun = KleeAmongTheRunsPlayers();
        Player? owner = null;
        try
        {
            // A canonical (compendium) copy asserts on `Owner` rather than
            // answering null -- `KokomiPlan.PlanDamageVar`'s guard, verbatim.
            if (card.IsMutable) owner = card.Owner;
        }
        catch (System.Exception)
        {
            owner = null;
        }
        if (owner != null)
        {
            return owner.Character is IKleeCharacter || (inRun ?? false);
        }
        return inRun ?? true;
    }

    /// <summary>Is any seat in this run playing Klee, or does nothing answer?
    /// A state read must never throw (<c>PlayTelemetry.NameOf</c> takes the
    /// same posture), and outside a run there is nothing to read.</summary>
    private static bool? KleeAmongTheRunsPlayers()
    {
        try
        {
            var players = RunManager.Instance?.DebugOnlyGetState()?.Players;
            if (players == null) return null;
            return players.Any(p => p?.Character is IKleeCharacter);
        }
        catch (System.Exception)
        {
            return null;
        }
    }
}
