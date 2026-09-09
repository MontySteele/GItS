using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE -- the seats, the bars, and the verbs her cards spend
/// them with (`EB-719`; the design is
/// <c>review/active/furina-stage-brief-2026-09-08.md</c>, ruled R269).
///
/// <para>WHAT THIS CLASS IS, and what it deliberately is NOT. It is the STATE
/// and the CARD VERBS: three seats front to back, a bar on each, and the
/// summon / rotate / Raise / Spend / act / bow the seventeen faces of sec.12
/// print. It exists because the codegen has to emit those faces into C# that
/// compiles, and a generated card that called nothing would be a face the
/// surface says can be tried and cannot.</para>
///
/// <para>IT IS NOT THE CREATURE, AND `EB-721` IS. The brief's sec.3 rule 1
/// makes a performer a PET on her side of the field with a visible bar, and
/// its rule 6 puts that bar in the damage order between her Block and her HP.
/// A pet body, the damage-order hook, the strip that renders the lead's bar
/// beside her Block (sec.8) and the turn hooks that run the regen and the
/// end-of-turn acts are the C# arm's own work, on branch `stage-cs`. This
/// class is the model they attach to, written from the sim
/// (<c>tier0/engine/furina_stage.py</c>) so that both halves start from one
/// set of rules and one set of numbers
/// (<see cref="FurinaStageLaw"/>, mirrored by
/// <c>tools/lint_constant_parity.py</c>).</para>
///
/// <para>THE SHAPE IS <see cref="FurinaDrain"/>'s, one arm over: a static
/// table keyed on the seat's own <c>Creature</c>, cleared per combat and per
/// play. Tier 0 runs one seat and the mod runs two, so the per-creature key is
/// what keeps a co-op partner's stage out of this one's.</para>
/// </summary>
public static class FurinaStage
{
    /// <summary>One seat. A CLASS and not a record struct, because a bar is
    /// written in place (regen, Raise, Spend, a hit) and a seat that had to be
    /// rebuilt to change its number is a seat two callers can disagree
    /// about -- the sim's own note on <c>Player.stage</c>.</summary>
    public sealed class Seat
    {
        public Seat(string member, int fanfare)
        {
            Member = member;
            Fanfare = fanfare;
        }

        /// <summary>`usher` | `chevalmarin` | `crabaletta`.</summary>
        public string Member { get; }

        /// <summary>The bar. No cap (brief sec.3 rule 4).</summary>
        public int Fanfare { get; set; }
    }

    /// <summary>The three performers, in the order the brief prints them.
    /// Mirrors <c>furina_stage.PERFORMERS</c>.</summary>
    public static readonly string[] Performers =
        { "usher", "chevalmarin", "crabaletta" };

    private static readonly Dictionary<Creature, List<Seat>> _stages = new();
    private static readonly Dictionary<Creature, int> _spent = new();
    private static readonly Dictionary<Creature, List<string>> _pending = new();

    /// <summary>The seats, front first. Never null: an absent entry is an
    /// empty stage, which is what every rule here already answers for.</summary>
    public static List<Seat> Of(Creature? owner)
    {
        if (owner == null) return new List<Seat>();
        if (!_stages.TryGetValue(owner, out var seats))
        {
            seats = new List<Seat>();
            _stages[owner] = seats;
        }
        return seats;
    }

    /// <summary>The FRONT seat -- the one attacks reach and the only one that
    /// regenerates (brief sec.3 rules 4 and 6). Null on an empty stage.</summary>
    public static Seat? Lead(Creature? owner) => Of(owner).FirstOrDefault();

    /// <summary>The BACK-MOST occupied seat, which is the lead when it is
    /// alone (rule 5). Null on an empty stage.</summary>
    public static Seat? Back(Creature? owner) => Of(owner).LastOrDefault();

    public static int LeadFanfare(Creature? owner) => Lead(owner)?.Fanfare ?? 0;

    public static int BackFanfare(Creature? owner) => Back(owner)?.Fanfare ?? 0;

    /// <summary>Rule 8's one refusal: with no performer on stage a Spend rider
    /// cannot fire and the card plays at its base number. The question is
    /// OCCUPANCY and never size -- a bar of any size pays the whole rider.
    /// Mirrors <c>furina_stage.can_spend</c>.</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    // ------------------------------------------------------------------
    // The per-play spend record -- <see cref="FurinaDrain.Amount"/>'s shape
    // and its reason: by the time *Final Bow*'s Block or the Rare's damage
    // resolves, the bar it is measuring is gone.
    // ------------------------------------------------------------------

    /// <summary>A fresh, EMPTY record for one card play.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (owner != null) _spent.Remove(owner);
    }

    /// <summary>What this play took off the bars, for the
    /// <c>CalculatedVar</c> multipliers. Mirrors the sim's
    /// <c>stage_spent</c> count token.</summary>
    public static int Spent(CardModel? card)
    {
        if (card?.Owner?.Creature is not { } owner) return 0;
        return _spent.TryGetValue(owner, out var taken) ? taken : 0;
    }

    /// <summary>The live lead bar, for the <c>stage_lead_fanfare</c>
    /// count.</summary>
    public static int LeadFanfare(CardModel? card) =>
        LeadFanfare(card?.Owner?.Creature);

    /// <summary>The live back bar, for the <c>stage_back_fanfare</c>
    /// count.</summary>
    public static int BackFanfare(CardModel? card) =>
        BackFanfare(card?.Owner?.Creature);

    // ------------------------------------------------------------------
    // Arrivals and departures.
    // ------------------------------------------------------------------

    /// <summary>
    /// The relic Salon Solitaire (brief sec.3 rule 2): Usher takes the front
    /// seat at <see cref="FurinaStageLaw.OpeningFanfare"/> when combat opens.
    /// Idempotent, so a second call on the same combat cannot field twice.
    /// </summary>
    public static void OpenCombat(Creature? owner)
    {
        if (owner == null) return;
        var seats = Of(owner);
        if (seats.Count > 0) return;
        seats.Add(new Seat("usher", FurinaStageLaw.OpeningFanfare));
    }

    /// <summary>
    /// Rule 3. Fill the BACK-MOST EMPTY seat at
    /// <see cref="FurinaStageLaw.SummonFanfare"/>. On a FULL stage rotate the
    /// cast: the front performer leaves without a bow, the other two step
    /// forward, and the newcomer takes the back seat WITH THE LEAVER'S BAR --
    /// "pools are never lost to rotation".
    ///
    /// <para><paramref name="ifPresentRaise"/> is the named summons' second
    /// clause (sec.10 default 2): "Summon Usher. If he is already on stage,
    /// Raise 3 on him instead", so a named summon is never a dead draw. It
    /// raises HIM, wherever he is sitting -- the one place in the kit a Raise
    /// does not go to the back seat, and it is written on the face.</para>
    ///
    /// <para><paramref name="member"/> of <c>"random"</c> rolls one who is NOT
    /// on stage (*Salon Début*, *Understudy*); with every performer seated it
    /// summons nobody.</para>
    ///
    /// <para>AND THE NEWCOMER PERFORMS ITS ACT AT ONCE, which is why this is
    /// awaited.</para>
    /// </summary>
    public static async Task Summon(PlayerChoiceContext choiceContext,
                                    Creature? owner, string member,
                                    int ifPresentRaise = 0)
    {
        if (owner == null) return;
        var seats = Of(owner);
        if (member == "random")
        {
            var free = Performers
                .Where(p => seats.All(s => s.Member != p)).ToList();
            if (free.Count == 0) return;
            var roll = owner.Player?.RunState.Rng.CombatTargets;
            member = roll != null ? roll.NextItem(free) : free[0];
        }
        else
        {
            var seated = seats.FirstOrDefault(s => s.Member == member);
            if (seated != null)
            {
                if (ifPresentRaise > 0) seated.Fanfare += ifPresentRaise;
                return;
            }
        }

        if (seats.Count < FurinaStageLaw.Seats)
        {
            seats.Add(new Seat(member, FurinaStageLaw.SummonFanfare));
        }
        else
        {
            var carried = seats[0].Fanfare;      // no bow: rule 3, sec.10 (5)
            seats.RemoveAt(0);
            seats.Add(new Seat(member, carried));
        }
        await Perform(choiceContext, owner, member);
    }

    /// <summary>*Scene Change* (sec.12): the front performer moves to the back
    /// seat, bar and all. A pure reorder -- no bow, no act, nothing lost
    /// (sec.5.2).</summary>
    public static void SceneChange(Creature? owner)
    {
        var seats = Of(owner);
        if (seats.Count == 0) return;
        var front = seats[0];
        seats.RemoveAt(0);
        seats.Add(front);
    }

    // ------------------------------------------------------------------
    // The bar.
    // ------------------------------------------------------------------

    /// <summary>Rule 4. The LEAD regains
    /// <see cref="FurinaStageLaw.LeadRegen"/> at the start of her turn, from
    /// her SECOND turn on -- the caller owns the turn test, because only it
    /// knows the turn number.</summary>
    public static void RegenLead(Creature? owner)
    {
        var lead = Lead(owner);
        if (lead != null) lead.Fanfare += FurinaStageLaw.LeadRegen;
    }

    /// <summary>Rule 5. Raise lands on the BACK-MOST performer, which is the
    /// lead when it is alone. Returns what landed; 0 on an empty
    /// stage.</summary>
    public static int Raise(Creature? owner, int amount)
    {
        var back = Back(owner);
        if (back == null || amount <= 0) return 0;
        back.Fanfare += amount;
        return amount;
    }

    /// <summary>
    /// Rule 8, the payment leg. Pays from the LEAD for a rider the caller has
    /// already decided fires: "If the lead has less than N, the rider STILL
    /// fires in full, the lead pays what it has and leaves with a bow"
    /// (sec.10 default 4, [USER]'s own words).
    ///
    /// <para>Returns WHAT WAS PAID, not what was asked, because that is the
    /// number sec.13's first report buckets on and the whole of the Expend
    /// deck's argument.</para>
    /// </summary>
    public static async Task<int> Spend(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (owner == null) return 0;
        var lead = Lead(owner);
        if (lead == null) return 0;
        var paid = System.Math.Min(amount, lead.Fanfare);
        lead.Fanfare -= paid;
        _spent[owner] = paid;
        if (lead.Fanfare <= 0)
        {
            Of(owner).Remove(lead);
            await Bow(choiceContext, owner, lead.Member);
        }
        return paid;
    }

    /// <summary>
    /// Rule 7, from the damage order: a hit empties the lead and it JUST
    /// LEAVES -- no bow. Returns what the lead absorbed. The caller is the
    /// damage-order hook (`EB-721`), which is why this takes a settled number
    /// and never a pipeline.
    /// </summary>
    public static int Absorb(Creature? owner, int incoming)
    {
        var lead = Lead(owner);
        if (lead == null || incoming <= 0) return 0;
        var eaten = System.Math.Min(incoming, lead.Fanfare);
        lead.Fanfare -= eaten;
        if (lead.Fanfare <= 0) Of(owner).Remove(lead);
        return eaten;                    // never runs on to the middle seat
    }

    /// <summary>*Let the People Rejoice*, first clause: "Spend all Fanfare on
    /// stage." Empties every bar, remembers who was standing, returns the
    /// total. THE BOWS ARE <see cref="CurtainCall"/>, because the printed
    /// order puts the card's own area damage between them.</summary>
    public static int CollectAll(Creature? owner)
    {
        if (owner == null) return 0;
        var seats = Of(owner);
        var total = seats.Sum(s => s.Fanfare);
        _pending[owner] = seats.Select(s => s.Member).ToList();
        seats.Clear();
        _spent[owner] = total;
        return total;
    }

    /// <summary>The same card's third clause: "Every performer takes a bow,
    /// then returns at 1." Two loops, because the sentence is two: every bow
    /// lands on the board the card left, and only then does anybody come
    /// back.</summary>
    public static async Task CurtainCall(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        if (owner == null) return;
        if (!_pending.TryGetValue(owner, out var company)) return;
        _pending.Remove(owner);
        foreach (var member in company)
            await Bow(choiceContext, owner, member);
        var seats = Of(owner);
        foreach (var member in company)
            if (seats.Count < FurinaStageLaw.Seats)
                seats.Add(new Seat(member, FurinaStageLaw.SummonFanfare));
    }

    /// <summary>*Final Bow* (sec.12): the lead takes a bow and leaves. A BOW
    /// WITHOUT A SPEND, and the one card that grants one -- rule 9 says a bow
    /// is earned by Spend, and this face pays for it with a card and an
    /// Exhaust instead. Returns the bar it left with, which is the Block the
    /// card gains.</summary>
    public static async Task<int> FinalBow(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (owner == null) return 0;
        var lead = Lead(owner);
        if (lead == null) return 0;
        var bar = lead.Fanfare;
        Of(owner).Remove(lead);
        _spent[owner] = bar;
        await Bow(choiceContext, owner, lead.Member);
        return bar;
    }

    // ------------------------------------------------------------------
    // The acts and the bows.
    // ------------------------------------------------------------------

    /// <summary>Rule 10: one performer's flat act, from any seat, reading no
    /// bar. ONE implementation, three callers -- the end-of-turn sweep, a
    /// newcomer's arrival and *Bis!* -- so an act cannot mean three
    /// things.</summary>
    public static async Task Perform(PlayerChoiceContext choiceContext,
                                     Creature? owner, string member)
    {
        if (owner == null) return;
        switch (member)
        {
            case "usher":
                await CreatureCmd.GainBlock(
                    owner, FurinaStageLaw.ActUsherBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case "chevalmarin":
                foreach (var enemy in Enemies(owner))
                    await ElementalHit.Deal(
                        choiceContext, enemy, Elements.Element.Hydro,
                        FurinaStageLaw.ActChevalmarinDamage, owner,
                        powered: false);
                break;
            case "crabaletta":
            {
                var target = RandomEnemy(owner);
                if (target != null)
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.ActCrabalettaDamage, owner,
                        powered: false);
                break;
            }
        }
    }

    /// <summary>*Bis!* (sec.12): the lead performer performs its act now.</summary>
    public static async Task PerformLead(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        var lead = Lead(owner);
        if (lead != null) await Perform(choiceContext, owner, lead.Member);
    }

    /// <summary>Rule 10's sweep, at the end of Furina's turn: EACH performer
    /// performs, in seat order, front first. The company is snapshotted so a
    /// cast that changes mid-sweep cannot skip or double an act.</summary>
    public static async Task EndOfTurnActs(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        foreach (var member in Of(owner).Select(s => s.Member).ToList())
            await Perform(choiceContext, owner, member);
    }

    /// <summary>Rule 9, the curtain call: performed ONCE by a performer
    /// emptied by a Spend. Usher: Block. Chevalmarin: Hydro on every enemy.
    /// Crabaletta: damage to a random enemy.</summary>
    public static async Task Bow(PlayerChoiceContext choiceContext,
                                 Creature? owner, string member)
    {
        if (owner == null) return;
        switch (member)
        {
            case "usher":
                await CreatureCmd.GainBlock(
                    owner, FurinaStageLaw.BowUsherBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case "chevalmarin":
                foreach (var enemy in Enemies(owner))
                    await ElementalHit.ApplyOnly(
                        choiceContext, enemy, Elements.Element.Hydro, owner);
                break;
            case "crabaletta":
            {
                var target = RandomEnemy(owner);
                if (target != null)
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.BowCrabalettaDamage, owner,
                        powered: false);
                break;
            }
        }
    }

    /// <summary>Every seat's record, dropped. Test-facing, and the courtesy
    /// <see cref="FurinaDrain.ResetAll"/> extends for its reason: a static
    /// table keyed on live objects outlives a headless fixture.</summary>
    public static void ResetAll()
    {
        _stages.Clear();
        _spent.Clear();
        _pending.Clear();
    }

    private static List<Creature> Enemies(Creature owner) =>
        owner.CombatState?.HittableEnemies.ToList() ?? new List<Creature>();

    private static Creature? RandomEnemy(Creature owner)
    {
        var targets = Enemies(owner);
        if (targets.Count == 0) return null;
        var rng = owner.Player?.RunState.Rng.CombatTargets;
        return rng != null ? rng.NextItem(targets) : targets[0];
    }
}
