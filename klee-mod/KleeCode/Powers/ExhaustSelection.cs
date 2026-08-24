using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// EB-118 — THE EXHAUST IDENTITY CONTEXT, mod side.
///
/// The card you chose to Exhaust tells the exhausting card what to do. Every
/// chosen-Exhaust selector (the generated `CardSelectCmd.FromHand` +
/// `CardCmd.Exhaust` block) opens a context, records a printed descriptor per
/// victim, and closes it; a LATER effect on the SAME card reads derived
/// totals off it — total printed cost, counts by type, by ownership, by
/// upgrade state.
///
/// SIM TWIN: `tier0/engine/effects.py` `_op_exhaust_from` and
/// `exhaust_selection_counts`. The six descriptors are printed identity only,
/// which is the whole reason both engines can record the same row: nothing
/// here reads a live combat, a power stack or a pile.
///
/// THE SCOPE KEY IS THE RESOLVING CARD INSTANCE, not the combat and not the
/// creature. That is what makes this a CONTEXT rather than a combat-global
/// `last_exhausted`: a second card asking reads nothing, because it is not the
/// card that opened the entry. Two facts follow, and both are the ruling:
///
///   * a SECOND selector on one card REPLACES the first entry (Open clears);
///   * nothing has to clean up after a card play — a stale entry is
///     unreachable by construction, since only the instance that opened it
///     can name it.
///
/// The OWNER is part of the key as well. That is the G-B1 lesson (Best
/// Friends Forever copying the partner's companions): a "this resolution"
/// tracker keyed on anything shared is correct in solo and wrong in co-op,
/// and solo is the only configuration tier 0.5 can see. Reading `Owner` off a
/// canonical model throws (EB-94), so it is read defensively and a seat that
/// cannot be read is `null` on both the write and the read — consistent, not
/// guessed.
///
/// THE THREE TELEMETRY RULES APPLY (PlayTelemetry.cs): this touches no game
/// state, consumes no RNG, and every public entry point is wrapped. A
/// measurement that can desync a co-op table or lose a run is worse than no
/// measurement.
///
/// Kokomi's rotation law (C11) is applied by the SELECTOR
/// (`KokomiResources.OwnCard`) before anything reaches here, so her context
/// never carries a Status or a Curse. The mechanism itself is
/// character-neutral: Dodge Roll's explicit status filter records its victims
/// here too. There is deliberately NO "Status exhausted" reward grammar — the
/// row reports rarity and stops.
/// </summary>
public static class ExhaustSelection
{
    /// <summary>The printed identity of one exhausted card. `Cost` is
    /// `EnergyCost.Canonical` — the PRINTED cost, the sim's `card.cost`, not
    /// `GetAmountToSpend()`, which is that cost after this instance's
    /// modifiers and would make the same card record two different numbers in
    /// two runs. An X-cost card records <see cref="XCost"/>, which no derived
    /// total counts (sim: the descriptor keeps "X" raw).</summary>
    public readonly struct Victim
    {
        public Victim(string id, int cost, CardType type, CardRarity rarity,
                      bool companion, bool upgraded)
        {
            Id = id;
            Cost = cost;
            Type = type;
            Rarity = rarity;
            Companion = companion;
            Upgraded = upgraded;
        }

        public string Id { get; }

        public int Cost { get; }

        public CardType Type { get; }

        public CardRarity Rarity { get; }

        public bool Companion { get; }

        public bool Upgraded { get; }
    }

    /// <summary>The cost recorded for an X-cost victim. Negative so it can
    /// never be summed by accident into a total a card would pay for.</summary>
    public const int XCost = -1;

    /// <summary>The parity row's columns, in order. ONE definition, and the
    /// sim reads these literals out of this file
    /// (`tier0/tests/test_exhaust_context_parity.py`) and compares them with
    /// `effects.EXHAUST_SELECTION_ROW_KEYS`, so neither engine can add or
    /// rename a column alone.</summary>
    public static readonly string[] RowKeys =
    {
        "card", "victims", "size", "cost", "attacks", "skills", "powers",
        "companions", "personal", "upgraded",
    };

    private static CardModel? _scope;
    private static Player? _seat;
    private static readonly List<Victim> _selection = new();

    /// <summary>Open this effect's own context. Called at the top of a
    /// selector block, BEFORE the selection screen, so a selector the player
    /// cancels or that offers nothing leaves an EMPTY context rather than the
    /// previous effect's.</summary>
    public static void Open(CardModel resolvingCard)
    {
        try
        {
            _scope = resolvingCard;
            _seat = SeatOf(resolvingCard);
            _selection.Clear();
        }
        catch (Exception e)
        {
            Warn(nameof(Open), e);
        }
    }

    /// <summary>Record one victim, from its printed fields only. Called
    /// inside the exhaust loop, beside `CardCmd.Exhaust`.</summary>
    public static void Record(CardModel resolvingCard, CardModel victim)
    {
        try
        {
            if (!InScope(resolvingCard)) return;
            _selection.Add(Describe(victim));
        }
        catch (Exception e)
        {
            Warn(nameof(Record), e);
        }
    }

    /// <summary>Close the selection and emit its parity row. The context
    /// stays READABLE — closing publishes the row, it does not retract the
    /// context the rest of the card is about to read.</summary>
    public static void Close(CardModel resolvingCard)
    {
        try
        {
            if (!InScope(resolvingCard)) return;
            Diagnostics.PlayTelemetry.ExhaustSelectionResolved(
                SeatOf(resolvingCard), ParityRow(resolvingCard));
        }
        catch (Exception e)
        {
            Warn(nameof(Close), e);
        }
    }

    /// <summary>The selection <paramref name="resolvingCard"/> itself took,
    /// or nothing at all for any other card.</summary>
    public static IReadOnlyList<Victim> Current(CardModel? resolvingCard)
    {
        try
        {
            return resolvingCard != null && InScope(resolvingCard)
                ? _selection
                : Array.Empty<Victim>();
        }
        catch (Exception e)
        {
            Warn(nameof(Current), e);
            return Array.Empty<Victim>();
        }
    }

    // --- the derived reads ------------------------------------------------
    //
    // These are what a CalculatedVar multiplier calls: the codegen renders
    // `static (card, _) => ExhaustSelection.<Name>(card)`, and the `card` a
    // CalculatedVar hands the lambda IS the resolving card, which is exactly
    // the scope key. A hover preview outside a resolution therefore reads 0,
    // which is honest: the selection does not exist until the card is played.

    public static int Size(CardModel? card) => Current(card).Count;

    /// <summary>Total PRINTED cost. X-cost victims contribute nothing.</summary>
    public static int Cost(CardModel? card) =>
        Current(card).Where(v => v.Cost != XCost).Sum(v => v.Cost);

    public static int Attacks(CardModel? card) => OfType(card, CardType.Attack);

    public static int Skills(CardModel? card) => OfType(card, CardType.Skill);

    public static int Powers(CardModel? card) => OfType(card, CardType.Power);

    public static int Companions(CardModel? card) =>
        Current(card).Count(v => v.Companion);

    /// <summary>The complement of <see cref="Companions"/>, spelled out
    /// rather than inferred: a card that rewards rotating your OWN cards out
    /// asks a different question from `size - companions`, and a sheet row
    /// should be able to say which one it means.</summary>
    public static int Personal(CardModel? card) =>
        Current(card).Count(v => !v.Companion);

    public static int Upgraded(CardModel? card) =>
        Current(card).Count(v => v.Upgraded);

    /// <summary>The parity row as a JSON object, keys and order per
    /// <see cref="RowKeys"/>. Rendered here rather than in the telemetry
    /// writer so the column names live in exactly one file.</summary>
    public static string ParityRow(CardModel? resolvingCard)
    {
        var victims = Current(resolvingCard);
        var sb = new StringBuilder("{");
        for (var i = 0; i < RowKeys.Length; i++)
        {
            if (i > 0) sb.Append(',');
            Key(sb, RowKeys[i]);
            switch (RowKeys[i])
            {
                case "card":
                    Str(sb, resolvingCard == null ? string.Empty
                                                  : IdOf(resolvingCard));
                    break;
                case "victims":
                    sb.Append('[');
                    for (var v = 0; v < victims.Count; v++)
                    {
                        if (v > 0) sb.Append(',');
                        Str(sb, victims[v].Id);
                    }
                    sb.Append(']');
                    break;
                default:
                    sb.Append(Derived(RowKeys[i], resolvingCard)
                                .ToString(CultureInfo.InvariantCulture));
                    break;
            }
        }
        return sb.Append('}').ToString();
    }

    /// <summary>One derived value by column name. The switch is what keeps
    /// <see cref="RowKeys"/> from listing a column nothing can produce: an
    /// unknown name throws here rather than writing a silent zero.</summary>
    public static int Derived(string key, CardModel? card) => key switch
    {
        "size" => Size(card),
        "cost" => Cost(card),
        "attacks" => Attacks(card),
        "skills" => Skills(card),
        "powers" => Powers(card),
        "companions" => Companions(card),
        "personal" => Personal(card),
        "upgraded" => Upgraded(card),
        _ => throw new ArgumentOutOfRangeException(
            nameof(key), key, "not a derived exhaust-selection column"),
    };

    internal static Victim Describe(CardModel card) =>
        new(IdOf(card),
            card.EnergyCost.CostsX ? XCost : card.EnergyCost.Canonical,
            card.Type,
            card.Rarity,
            card is ICompanionCard,
            card.IsUpgraded);

    /// <summary>The model ENTRY, never the localized title: a title is a
    /// display string, two cards may share one, and it moves with the
    /// language. The entry is the class name in screaming snake case
    /// (`PearlDiver` → `PEARL_DIVER`), so the sim's sheet id is this
    /// lowercased — a parity reader case-folds, it does not expect a literal
    /// match.</summary>
    private static string IdOf(CardModel card) => card.Id.Entry;

    private static int OfType(CardModel? card, CardType type) =>
        Current(card).Count(v => v.Type == type);

    private static bool InScope(CardModel resolvingCard) =>
        ReferenceEquals(_scope, resolvingCard)
        && ReferenceEquals(_seat, SeatOf(resolvingCard));

    /// <summary>The seat this card belongs to, or null when it cannot be
    /// read. A canonical CardModel's `Owner` getter THROWS (EB-94), and this
    /// is a measurement path: it must not be the thing that takes a run
    /// down.</summary>
    private static Player? SeatOf(CardModel card)
    {
        try
        {
            return card.Owner;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static void Key(StringBuilder sb, string key)
    {
        Str(sb, key);
        sb.Append(':');
    }

    private static void Str(StringBuilder sb, string value)
    {
        sb.Append('"');
        foreach (var c in value)
        {
            if (c == '"' || c == '\\') sb.Append('\\').Append(c);
            else if (c < ' ') sb.Append(' ');
            else sb.Append(c);
        }
        sb.Append('"');
    }

    private static void Warn(string where, Exception e) =>
        MegaCrit.Sts2.Core.Logging.Log.Warn(
            $"[{KleeMod.ModId}] exhaust selection {where}: "
            + $"{e.GetType().Name}: {e.Message}");
}
