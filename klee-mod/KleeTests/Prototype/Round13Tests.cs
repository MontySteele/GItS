using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Powers;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 13, the legibility rows -- what a face has to say before it is read
/// for the first time.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round13Tests
{
    /// <summary>A generated card's printed face, off an instance allocated
    /// uninitialised: these `Localization` getters are pure string builders
    /// (`Round12Tests`' idiom, and the headless boundary's reason).</summary>
    private static string Face<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == "description").Item2;
    }

    // ==================================================================
    // `EB-446` -- a name one card is written against and another grants
    // ==================================================================
    //
    // THE FIND (Furina r7 (c) 5). <i>Fischl -- Nightrider</i> prints "If Oz is
    // out, he deals 5 Electro damage to a random enemy" and nothing on the
    // screen says what puts Oz out. The seat played it five times and never
    // learned: the thing the word names is a DIFFERENT companion card, the
    // Power <i>Fischl -- Oz, at Your Side</i>, which that run never held.
    //
    // `ForGrounded`'s SHAPE, and its argument: the attach travels with the
    // printed WORD (`gen_klee_cards.arm_keyword_tip_calls`), so the face that
    // names him carries the definition whether or not the deck can grant him
    // -- which is the state the seat was in for all five plays.

    [Fact]
    public void Nightrider_golds_the_name_it_cannot_grant()
    {
        var face = Face<ProtoMcFischlNightrider>();

        Assert.Contains("If [gold]Oz[/gold] is out", face);
    }

    [Fact]
    public void The_face_that_names_him_carries_the_definition()
    {
        // The whole of the fix: the tip is attached FROM THE FACE, so a reader
        // who has never seen the Power still gets told which card it is.
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlNightrider",
                                           "get_ExtraHoverTips")));
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlOz",
                                           "get_ExtraHoverTips")));
    }

    // ==================================================================
    // `EB-454` -- the two elements that printed no tag
    // ==================================================================
    //
    // THE FIND (Kokomi r13 (c) 8). <i>Jean -- Gale Blade</i> "read as untyped
    // until a Reaction preview named Anemo mid-fight", on a screen where every
    // Hydro, Electro, Cryo and Pyro card carries its element. Anemo and Geo
    // leave no aura, so they got no gem and, until now, no keyword either --
    // and the keyword is the tag, not the gem.

    /// <summary>The `KleeKeywords` field a card's `CanonicalKeywords` LOADS.
    /// `ElementBadgeTests.KeywordFieldOf`'s scan, and its reason: BaseLib fills
    /// these fields at `ModelDb.Init`, so in this host every one of them reads
    /// `None` and comparing VALUES would pass for any element at all. A static
    /// field read is `ldsfld`, which `Il.Calls` cannot see, so the byte scan is
    /// the reachable form.</summary>
    private static string[] KeywordFieldsOf(System.Type card)
    {
        var body = card.GetProperty("CanonicalKeywords", HeadlessGame.All)!
            .GetGetMethod()!.GetMethodBody()!.GetILAsByteArray()!;
        var found = new List<string>();
        for (var i = 0; i < body.Length - 4; i++)
        {
            if (body[i] != 0x7E) continue;              // ldsfld
            try
            {
                var field = card.Module.ResolveField(
                    System.BitConverter.ToInt32(body, i + 1));
                if (field?.DeclaringType?.Name == "KleeKeywords")
                {
                    found.Add(field.Name);
                }
            }
            catch
            {
                // Not a field token. Expected while byte-scanning.
            }
        }

        return found.ToArray();
    }

    [Fact]
    public void Gale_blade_declares_the_element_its_damage_carries()
    {
        Assert.Contains("AppliesAnemo",
                        KeywordFieldsOf(typeof(ProtoMcJeanGaleBlade)));
    }

    [Fact]
    public void A_geo_face_declares_its_element_too()
    {
        // Both of the two, because "the tag map covers all six" is the claim
        // and Geo is the half no seat happened to report.
        Assert.Contains("AppliesGeo",
                        KeywordFieldsOf(typeof(ProtoMiGorouInuzaka)));
    }

    [Fact]
    public void The_two_that_leave_no_aura_still_draw_no_gem()
    {
        // THE SPLIT IS THE FIX, and it is why this is a separate assertion
        // rather than one wider map: the gem is the AURA's own icon -- the
        // badge a player will see on the enemy -- and there is none to paint
        // for an element that leaves nothing. `ElementBadge.IconPathFor` is
        // internal, so it is reached the way `ElementBadgeTests` reaches it.
        var badge = typeof(global::KleeMod.KleeMod).Assembly
            .GetTypes().Single(t => t.Name == "ElementBadge");
        var iconPathFor = badge.GetMethod("IconPathFor", HeadlessGame.All)!;

        Assert.Null(iconPathFor.Invoke(null, new object[] { Element.Anemo }));
        Assert.Null(iconPathFor.Invoke(null, new object[] { Element.Geo }));
        Assert.NotNull(iconPathFor.Invoke(null, new object[] { Element.Pyro }));
    }

    // ==================================================================
    // `EB-450` -- the queue the badge printed as a sum
    // ==================================================================
    //
    // THE FIND (Klee r13 (c) 1). The badge printed `Bomb 45 (4 bombs)` -- a
    // sum and a count -- while `EB-432`'s Set off tip says the charges go off
    // oldest first and the FIRST one takes the aura. So on a bombed body
    // wearing Cryo, WHICH charge Melts was a fact the seat had to remember
    // placing rather than read, for a whole fight.

    [Fact]
    public void The_badge_lists_three_charges_in_the_order_they_will_fire()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));
        // Through the power's own door, so the display syncs the way it does
        // in a fight -- `LiveBurn20260902Tests`' reason for the same call.
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(20, false, 0));

        // PLACEMENT ORDER, which is the order `SetOff` walks and therefore the
        // order the aura clause is about. Slash-separated: the sentence around
        // the hole is comma-separated, and a comma list inside it would hide
        // where the pile stops.
        Assert.Equal("5 / 8 / 20",
                     pile.DynamicVars["Charges"].ToString());
    }

    [Fact]
    public void The_list_follows_the_pile_and_not_the_stack()
    {
        // `EB-289`'s defect, one var over: the takes are PURE (they run inside
        // a damage hook where no command may), so the stack amount cannot go
        // down and a face reading it would keep printing a charge that has
        // already gone off.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));

        Assert.Equal("4 / 8", pile.DynamicVars["Charges"].ToString());

        pile.TakeMines();

        Assert.Equal("8", pile.DynamicVars["Charges"].ToString());

        // An emptied pile prints `0` rather than an empty slot: the badge is
        // torn down with the last charge, and a face caught mid-teardown must
        // not render "Bombs here: ,".
        pile.TakeAll();
        Assert.Equal("0", pile.DynamicVars["Charges"].ToString());
    }

    [Fact]
    public void The_face_prints_the_list_where_it_printed_the_count()
    {
        // The two live faces, read as rows: a headless pin can read a row and
        // cannot run `LocManager` (KleeTests README).
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(5));
        var rows = pile.Localization!;

        var plain = rows.First(
            r => r.Item1 == "smartDescription").Item2;
        var mined = rows.First(
            r => r.Item1 == "smartDescriptionMines").Item2;

        Assert.Contains("Bombs here: [blue]{Charges}[/blue]", plain);
        Assert.Contains("Bombs here: [blue]{Charges}[/blue]", mined);
        // `EB-514`: the count is not in THIS sentence -- the list still says
        // it more plainly here -- and it is in the HEADLINE, where the seat
        // reads the number it plans against. Two number groups in one
        // sentence is what this pin was written against; two sentences each
        // saying their own thing is what it now reads.
        Assert.DoesNotContain("Bombs here: [blue]{Charges}[/blue], "
                              + "[blue]{Count}[/blue]", plain);
        // `EB-536` spelled the Sparks out and dropped the plural: this is
        // the MANY-charge half of the grid, so the clause is here and it is
        // never printed for one.
        Assert.Contains("Pyro damage, in [blue]{Count}[/blue] hits", plain);
        Assert.Contains("Pyro damage, in [blue]{Count}[/blue] hits", mined);
    }

    // ==================================================================
    // `EB-453` -- the panel that omitted a Plan and mis-stated a number
    // ==================================================================
    //
    // THE FIND (Kokomi r13 (c) 5). Two Plans written, ONE printed, and
    // `War Council, 7 (the 7 is damage)` above a body that had lost 9. Both
    // halves are one shape: the page could only print what the wire carried,
    // and the wire carried neither the Plan the fight cut off nor the name of
    // the thing that dealt the other 2.

    [Fact]
    public void A_rider_names_itself_to_the_plan_it_landed_inside()
    {
        // `MovedOn` is a SUBTRACTION and a subtraction has no sources, so the
        // rider is the only thing that can say what it was. The Casket's own
        // strike reports the DELIVERED number, because Vulnerable moves it and
        // the page is trying to account for a total.
        var strike = Il.Method("TamakushiCasket", "Strike");
        var calls = Il.Calls(strike);

        Assert.Contains("ElementalHit.Deal", calls);
        Assert.Contains("KokomiPlan.NoteRider", calls);
    }

    [Fact]
    public void A_rider_outside_a_plan_is_dropped_rather_than_misfiled()
    {
        // The call is unconditional at the strike, so "am I inside a Plan"
        // has to be answered here -- and a strike on the enemy's turn belongs
        // to no Plan at all.
        KokomiPlan.ResetAll();

        KokomiPlan.NoteRider("Tamakushi Casket", 2);

        // Nothing to assert on but the absence of a throw and of a row: the
        // collector is null between Plans, which is the whole guard.
        Assert.Empty(KokomiPlan.CarriedOut(Seat.Kokomi().Player));
    }

    [Fact]
    public void The_wire_carries_the_riders_and_the_unfinished_mark()
    {
        // The field names ARE the contract (`KokomiPlan.Snapshot`'s header),
        // and `understudy/blindplay_board._carried_out_row` reads these two.
        var row = Il.Method("KokomiPlan", "CarriedOutRow");
        var rider = Il.Method("KokomiPlan", "RiderRow");

        Assert.Contains("riders", Il.Strings(row));
        Assert.Contains("unfinished", Il.Strings(row));
        Assert.Contains("source", Il.Strings(rider));
        Assert.Contains("amount", Il.Strings(rider));
    }

    [Fact]
    public void A_rider_says_which_body_it_struck()
    {
        // `EB-518`. THE FOURTH CASKET THAT WAS NEVER THERE.
        //
        // Kokomi r18 lane 1, fight 2: "the carry-out block lists three casket
        // hits, but the numbers need four ... I only found the fourth by
        // subtracting." It did not need four. `EB-453` named the source and
        // the number and NOT the body, so three identical entries over bodies
        // that had lost 9 and 7 divided the even way -- one strike each -- and
        // came up 2 short. Two of the three had landed on the SAME body:
        // `ElementalHit.Deal` resolves the reaction before the hit lands, so
        // the Plan's own Hydro froze that body and the relic answered the
        // Frozen as well as the Weak the same Plan applied.
        //
        // TWO SPELLINGS AND THEY ARE `MovedRow`'s, so the page resolves a
        // rider's body and a moved row's body through one lookup and cannot
        // call the same creature two things in one receipt.
        var rider = Il.Method("KokomiPlan", "RiderRow");

        Assert.Contains("target", Il.Strings(rider));
        Assert.Contains("combat_id", Il.Strings(rider));

        // And the strike is what fills them: the relic is the one line that
        // knows both what it is and whom it hit.
        Assert.Contains("KokomiPlan.NoteRider",
                        Il.Calls(Il.Method("TamakushiCasket", "Strike")));
    }

    [Fact]
    public void The_plans_a_kill_cut_off_are_recorded_before_the_strip_goes()
    {
        // The order is the whole of it: `_showing` holds exactly the Plans
        // that never ran (each resolved Plan removes its own thumbnail), and
        // the old code tore it down on every path. A row read after the
        // teardown would find nothing to name.
        var calls = Il.Calls(Il.Method("KokomiPlan", "ResolveAll"));
        var noteIndex = calls.ToList()
            .FindIndex(c => c.EndsWith("KokomiPlan.NoteUnfinished",
                                       System.StringComparison.Ordinal));

        Assert.True(noteIndex >= 0, "the unfinished Plans are never recorded");
        Assert.Contains("KokomiPlan.Record",
                        Il.Calls(Il.Method("KokomiPlan", "NoteUnfinished")));
        // One writer for both kinds of row, so a beat and a Plan the fight cut
        // off arrive in one order and by one door.
        Assert.Contains("KokomiPlan.Record",
                        Il.Calls(Il.Method("KokomiPlan", "Announce")));
    }

    // ==================================================================
    // `EB-455` -- the card that was dead in hand and never said why
    // ==================================================================
    //
    // THE FIND (Kokomi r13 (b)). Change of Plans "was dead in hand three
    // fights before it was good once and its face never says it needs a
    // written Plan; a first reader plays it into an empty jellyfish". When it
    // did fire it was excellent, so this is legibility and not balance:
    // nothing the card DOES moves.
    //
    // THE BIG ONE'S FORM, which is `EB-261` + `EB-264`: the refusal is
    // `CardModel.IsPlayable` (the extension point the base game documents for
    // exactly this) and the SENTENCE rides `IUnplayableReasonCard`, because
    // `CardModel.CanPlay` collapses every mod-side refusal into
    // `BlockedByCardLogic` and has no slot for what the reason was.

    [Fact]
    public void Change_of_plans_says_why_it_is_refusing()
    {
        var card = new ProtoKkChangeOfPlans();

        // No owner, so no queue: the empty-memory board, and the answer a
        // compendium copy gives too.
        Assert.Equal("no Plan is written",
                     ((IUnplayableReasonCard)card).UnplayableReason);
    }

    [Fact]
    public void A_written_plan_clears_the_refusal()
    {
        // THE QUEUE IS SEEDED DIRECTLY, and that is the headless boundary
        // rather than a shortcut: `KokomiPlan.Schedule` is the writer and it
        // syncs the pending badge through a command, which needs a live
        // combat. What is under test is the READ -- `PlansHeld` over this
        // seat's queue -- and the read is the same one either writer feeds.
        var seat = Seat.Kokomi().WithCombatState();
        var card = new ProtoKkChangeOfPlans();
        Seat.Set(card, "IsMutable", true);
        card.Owner = seat.Player;

        Assert.Equal("no Plan is written",
                     ((IUnplayableReasonCard)card).UnplayableReason);
        Assert.Equal(0, KokomiPlan.PlansHeld(seat.Creature));

        try
        {
            Queue(seat).Add(new KokomiPlan.Entry(
                null, System.Array.Empty<KokomiPlan.Planned>()));

            Assert.Equal(1, KokomiPlan.PlansHeld(seat.Creature));
            Assert.Null(((IUnplayableReasonCard)card).UnplayableReason);
        }
        finally
        {
            KokomiPlan.ResetAll();
        }
    }

    /// <summary>This seat's pending queue, created if it has none. `_queues`
    /// is private static and keyed by `Player`, which is what `Pending` reads
    /// back.</summary>
    private static List<KokomiPlan.Entry> Queue(Seat seat)
    {
        var queues = (System.Collections.IDictionary)typeof(KokomiPlan)
            .GetField("_queues", HeadlessGame.All)!.GetValue(null)!;
        var list = new List<KokomiPlan.Entry>();
        queues[seat.Player] = list;
        return list;
    }

    [Fact]
    public void The_gate_and_the_sentence_read_the_same_queue()
    {
        // One question, one answer. A gate reading one thing and a sentence
        // reading another is how a card comes to refuse for a reason it does
        // not print.
        var playable = Il.Method("ProtoKkChangeOfPlans", "get_IsPlayable");
        var reason = Il.Method("ProtoKkChangeOfPlans",
                               "get_UnplayableReason");

        Assert.Contains("KokomiPlan.PlansHeld", Il.Calls(playable));
        Assert.Contains("KokomiPlan.PlansHeld", Il.Calls(reason));
    }

    [Fact]
    public void The_tip_names_the_power_that_puts_him_out()
    {
        var body = string.Concat(Il.Strings(
            Il.Method("ArmKeywordTips", "ForOz")));

        Assert.Contains("Oz, at Your Side", body);
        // The title is quoted WITHOUT its `Fischl --` prefix: the text
        // conventions ban a dash of any kind in player-facing text, and the
        // lint bites on one.
        Assert.DoesNotContain("--", body);
    }
}
