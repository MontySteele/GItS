// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-184: DOES THIS PLAY NEED A TARGET? ASK THE CHOSEN MODE, NOT THE CARD TYPE.
//
// WHAT WENT WRONG. `ExecutePlayCard` decided a play needed aiming with one
// test -- `card.TargetType == TargetType.AnyEnemy` -- and refused a play that
// carried no `target` with "Card requires a target. Provide 'target' with an
// entity_id." On a `choose_one` card that is the wrong question. Kokomi slice 1
// round 4 `t02`: the seat took the *Gain 3 Block* half of
// `proto_thoma_crimson_ooyoroi_either` and wrote no target, correctly from the
// printed face; the bridge refused, the line never resolved, and the round's
// pair read RETURNED the whole arm on that alone -- "an implementation repair,
// not a board redesign", in the reviewer's words.
//
// WHY THE CARD'S TargetType IS NOT THE ANSWER, AND IS NOT A BUG EITHER. The
// game aims a card BEFORE its mode is chosen: `TargetType` is a property of the
// CardModel, the choose-a-card screen opens inside `OnPlay`, and the 0.111.0
// decompile has no mid-play enemy picker to move the aim after the choice. So
// an Attack-typed modal MUST declare `AnyEnemy` for the sake of the mode that
// aims (codegen: the `choose_one` arm of the TargetType scan). The card type is
// the right answer to "can this card be aimed"; it is not an answer to "does
// this play have to be".
//
// WHERE THE PER-MODE ANSWER COMES FROM. The card carries it. `KleeMod.Cards`
// declares `IModalCard` -- `ModeLabels` and `ModeAimsAtChosenEnemy`, in sheet
// order -- and the roster codegen emits both rows for every `choose_one` card
// from the same sheet key the mode's label and body come from
// (`tools/gen_klee_cards.mode_aims`). This file reads them BY NAME through
// reflection, because the bridge is a separate mod and references nothing of
// ours; a card from any other mod, or from the base game, simply answers "not
// modal" and the old card-type rule stands untouched.
//
// Sim twin: `understudy.targeting.needs_target(row, choose)`, which asks the
// same question of the same sheet row and the same mode -- and, like this file,
// falls back to the whole row when no mode was named.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

namespace STS2_MCP;

/// <summary>One mode of a modal card: what it is called, and whether it aims.</summary>
public readonly struct ModalMode
{
    public ModalMode(string label, bool aims)
    {
        Label = label;
        Aims = aims;
    }

    public string Label { get; }

    public bool Aims { get; }
}

public static class GitsModalTargeting
{
    /// <summary>The two member names. A WIRE CONTRACT with `IModalCard`:
    /// renaming either member there without renaming it here silently restores
    /// EB-184, so both spellings are pinned from the Python side in
    /// tier0/tests/test_eb184_mode_targeting.py.</summary>
    public const string LabelsMember = "ModeLabels";

    public const string AimsMember = "ModeAimsAtChosenEnemy";

    /// <summary>No mode was named, or none matched.</summary>
    public const int NoMode = -1;

    /// <summary>The name matched more than one mode.</summary>
    public const int Ambiguous = -2;

    /// <summary>
    /// This card's modes, in sheet order, or null when the card is not modal.
    /// Null is also the answer for a card whose two rows disagree in length --
    /// a half-read card is not a licence to skip a refusal.
    /// </summary>
    public static IReadOnlyList<ModalMode>? Modes(object? card)
    {
        if (card == null) return null;
        var type = card.GetType();
        var labels = ReadStrings(type.GetProperty(LabelsMember)?.GetValue(card));
        var aims = ReadBools(type.GetProperty(AimsMember)?.GetValue(card));
        if (labels == null || aims == null) return null;
        if (labels.Count == 0 || labels.Count != aims.Count) return null;
        var modes = new List<ModalMode>(labels.Count);
        for (var i = 0; i < labels.Count; i++)
        {
            modes.Add(new ModalMode(labels[i], aims[i]));
        }
        return modes;
    }

    /// <summary>
    /// Which mode does this name mean? Exact first (trimmed, case-insensitive),
    /// then a UNIQUE substring either way round, so a form that abbreviates
    /// "Gain 3 Block, applying no element" to "Gain 3 Block" still lands.
    /// Ambiguity is reported, never guessed at.
    /// </summary>
    public static int Match(IReadOnlyList<ModalMode> modes, string wanted)
    {
        string want = (wanted ?? "").Trim();
        if (want.Length == 0) return NoMode;
        var exact = Indexes(modes, m =>
            string.Equals(m.Trim(), want, StringComparison.OrdinalIgnoreCase));
        if (exact.Count == 1) return exact[0];
        if (exact.Count > 1) return Ambiguous;
        var loose = Indexes(modes, m =>
            m.Contains(want, StringComparison.OrdinalIgnoreCase)
            || want.Contains(m.Trim(), StringComparison.OrdinalIgnoreCase));
        if (loose.Count == 1) return loose[0];
        return loose.Count > 1 ? Ambiguous : NoMode;
    }

    /// <summary>The labels, for a refusal that lists what it would have taken.</summary>
    public static string Labels(IReadOnlyList<ModalMode> modes) =>
        string.Join(" | ", modes.Select(m => $"'{m.Label}'"));

    private static List<int> Indexes(
        IReadOnlyList<ModalMode> modes, Func<string, bool> hit)
    {
        var found = new List<int>();
        for (var i = 0; i < modes.Count; i++)
        {
            if (hit(modes[i].Label ?? "")) found.Add(i);
        }
        return found;
    }

    private static List<string>? ReadStrings(object? value)
    {
        if (value is not IEnumerable seq || value is string) return null;
        var out_ = new List<string>();
        foreach (var item in seq)
        {
            if (item is not string s) return null;
            out_.Add(s);
        }
        return out_;
    }

    private static List<bool>? ReadBools(object? value)
    {
        if (value is not IEnumerable seq) return null;
        var out_ = new List<bool>();
        foreach (var item in seq)
        {
            if (item is not bool b) return null;
            out_.Add(b);
        }
        return out_;
    }
}
