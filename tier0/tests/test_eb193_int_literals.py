"""EB-193 -- an int-typed CanonicalVar must not be dropped for want of `m`.

`tools/extract_base_game_pool.py` read every card number through a regex that
demanded the C# decimal suffix (`new DamageVar(6m` ...). A CanonicalVar whose
backing type is `int` is constructed from a bare literal and carries no
suffix, so it never matched and was silently absent from the JSON extract --
no warning, no exclusion note, just a missing key. The Regent's Star amounts
were the whole class of the loss: `game_ref/regent.json` carried no Star
number anywhere, its Basic generator reading `"vars": {}` while its
`"upgrades"` showed the delta beside it (that OnUpgrade happens to spell its
number as a decimal), so every Star figure in
`docs/current/research/regent-stars-economy.md` had to be re-decompiled by
hand rather than read out of our own extract.

SEEN TO FAIL. The four int-literal tests below were run against the OLD
patterns -- `(-?[\\d.]+)m` in `VAR` and `VAR_POWER`, `(-?[\\d.]+)m\\)` in `UPG`
and `VAR_NAMED` and in the two inline `UpgradeValueBy` searches -- and all
four failed there: the int-typed var came back missing from `vars`, and the
int-literal upgrade came back as `_unexpressible: ['unrecognised upgrade
statement']`. The remaining two tests guard the OTHER direction (the careless
fix, and the emitted Python type) and pass either way by construction.

NO BASE-GAME DATA. Every fixture here is a synthetic type in the real
decompiled SHAPE -- an int-backed var built from a bare literal, sitting next
to a decimal one -- which is the rule this file's neighbours already keep
(`tier0/tests/test_extract_base_game_pool.py`: "tiny synthetic source trees
... they never read or reproduce base-game data"). The shape itself is
recorded, with its provenance, in the research note cited above.
"""

from __future__ import annotations

from tools import extract_base_game_pool as extract


def _card(vars_decl: str, upgrade: str = "") -> str:
    """One decompiled card in the shape `parse_card` consumes.

    `vars_decl` is the CanonicalVars expression body; `upgrade` is the
    statement list of OnUpgrade, omitted entirely when a card has none.
    """
    upgrade_method = ""
    if upgrade:
        upgrade_method = ("  protected override void OnUpgrade()\n"
                          "  {\n"
                          "    " + upgrade + "\n"
                          "  }\n")
    return ("namespace MegaCrit.Sts2.Core.Models.Cards;\n"
            "\n"
            "public sealed class Widget : CardModel\n"
            "{\n"
            "  protected override IEnumerable<DynamicVar> CanonicalVars =>\n"
            "    " + vars_decl + "\n"
            "  public Widget()\n"
            "    : base(1, CardType.Skill, CardRarity.Basic, TargetType.Self)\n"
            "  { }\n"
            + upgrade_method +
            "}\n")


def test_an_int_literal_var_reaches_the_json_record():
    """Would catch EB-193 itself. The int-backed var vanishes from `vars`
    while the decimal one beside it survives -- which is how a card's upgrade
    delta could be in our extract while its base amount was not, and how a
    whole resource went missing from a pool's JSON without anything failing.
    """
    src = _card("new DynamicVar[2] { new SparksVar(2), "
                "new DamageVar(6m) };")
    card = extract.parse_card(src, "Widget")
    assert card["vars"] == {"Sparks": 2.0, "Damage": 6.0}


def test_an_int_literal_upgrade_delta_reaches_the_json_record():
    """Would catch the same defect on the `UPG` half. An int-typed var's
    OnUpgrade writes a bare literal too, so the summary extract would report
    a card as having no upgrade at all rather than one it could not read.
    """
    src = _card("new SparksVar(2);",
                "base.DynamicVars.Sparks.UpgradeValueBy(1);\n"
                "    base.DynamicVars.Damage.UpgradeValueBy(2m);")
    card = extract.parse_card(src, "Widget")
    assert card["upgrades"] == {"Sparks": 1.0, "Damage": 2.0}


def test_decimal_literals_still_read_exactly_as_they_did():
    """Would catch a widening that traded one shape for another. Making `m`
    optional must ADD int literals and change nothing about decimals --
    including a negative and a fractional one, and a var whose number is
    followed by a second constructor argument rather than by the paren.
    """
    src = _card("new DynamicVar[2] { new DamageVar(6m, ValueProp.None), "
                "new BlockVar(-2.5m) };")
    card = extract.parse_card(src, "Widget")
    assert card["vars"] == {"Damage": 6.0, "Block": -2.5}


def test_the_number_never_runs_past_the_end_of_the_argument():
    """Would catch the careless fix: DELETING the `m` rather than making it
    optional. `[\\d.]+` is greedy, so with nothing behind it the trailing dot
    of a member access on a numeric literal is captured as well (`2.5.` out
    of `2.5.ToString()`), and `float()` then raises on the way into the
    record. The mandatory suffix had been acting as the terminator, so
    removing it has to put one back.
    """
    src = _card("new WidgetVar(2.5.ToString());")
    assert extract.VAR.search(src) is None
    # ...and whatever the pattern does capture must still be a number.
    mixed = _card("new DynamicVar[2] { new SparksVar(2), "
                  "new DamageVar(6m) };")
    for _, raw in extract.VAR.findall(mixed):
        float(raw)


def test_the_sheet_path_keeps_an_int_literal_an_int():
    """Would catch a var reaching the sheet as `2.0` where the game prints
    `2`. The sheet path parses through `_num`, which narrows an integral
    value back to `int`; this pins that the widened `VAR_PLAIN` / `VAR_POWER`
    / `VAR_NAMED` trio all still reach it, in all three ctor spellings.
    """
    src = ("new SparksVar(2), new PowerVar<StrengthPower>(3), "
           'new DynamicVar("Tokens", 4), new DamageVar(2.5m)')
    vals = extract._canonical_vars(src)
    assert vals["Sparks"] == 2 and isinstance(vals["Sparks"], int)
    # A PowerVar registers under both spellings the two hooks disagree on.
    assert vals["Strength"] == 3 and vals["StrengthPower"] == 3
    assert isinstance(vals["StrengthPower"], int)
    assert vals["Tokens"] == 4 and isinstance(vals["Tokens"], int)
    assert vals["Damage"] == 2.5


def test_the_two_sheet_upgrade_readers_accept_an_int_literal_delta():
    """Would catch the EB-193 defect in its last two homes -- the inline
    `UpgradeValueBy` searches in `_upgrade_delta` and
    `_supplement_upgrade_delta`. There the failure is louder but no more
    useful: the statement is recorded as `unrecognised`, so a real upgrade is
    counted against the DSL's coverage instead of being read.
    """
    structural = _card("new SparksVar(2);",
                       "base.DynamicVars.Sparks.UpgradeValueBy(1);")
    fed = {"Sparks": [({"op": "block", "amount": 5}, "amount")]}
    assert extract._upgrade_delta(structural, fed) == {"block": 1}

    supplement = _card("new SparksVar(2);",
                       "base.DynamicVars.Block.UpgradeValueBy(1);")
    row = {"effects": [{"op": "block", "amount": 5}]}
    assert extract._supplement_upgrade_delta(row, supplement) == {"block": 1}


# --------------------------------------------- the same defect, twice over --
#
# `tools/patch_sentinel.py` carries the card extractor's `VAR` regex a second
# time, for relics, and carried the same defect with it. That is where the
# other half of `EB-193`'s acceptance lives: Divine Right is a `RelicModel`,
# not a card, so it can never appear in `game_ref/regent.json` -- the card
# extractor walks `RegentCardPool` only -- and its 3 Stars reach `.sentinel/`
# through `parse_relic` or nowhere.


def _relic(vars_decl: str) -> str:
    """One decompiled relic in the shape `parse_relic` consumes."""
    return (
        "namespace MegaCrit.Sts2.Core.Models.Relics;\n"
        "public class Sentinel : RelicModel\n"
        "{\n"
        "    public override RelicRarity Rarity => RelicRarity.Boss;\n"
        f"    {vars_decl}\n"
        "}\n"
    )


def test_a_relic_var_built_from_an_int_literal_reaches_the_sentinel():
    r"""`EB-193`'s other half. A relic priced in Stars declares an int-backed
    var, so its number carried no `m` and the three relic regexes dropped it
    -- the sentinel watched a relic whose only balance number was invisible to
    it, and would have reported no change across a patch that moved it.

    Seen to FAIL: with `(-?[\d.]+)m` on the three `RELIC_*_VAR` patterns the
    `Stars`, `FocusPower` and `Lightning` keys below are all absent.
    """
    from tools import patch_sentinel

    src = _relic(
        'private readonly StarsVar _s = new StarsVar(3);\n'
        '    private readonly DamageVar _d = new DamageVar(6m, x);\n'
        '    private readonly PowerVar<FocusPower> _f '
        '= new PowerVar<FocusPower>(1);\n'
        '    private readonly DynamicVar _n = new DynamicVar("Lightning", 2);')
    got = patch_sentinel.parse_relic(src, "Sentinel")["vars"]
    assert got["Stars"] == 3          # the int literal, previously dropped
    assert got["FocusPower"] == 1     # ... in its typed spelling
    assert got["Lightning"] == 2      # ... and its named one
    assert got["Damage"] == 6         # the decimal, unchanged


def test_a_relic_var_regex_still_refuses_a_member_access():
    r"""The careless widening, on the relic side: dropping the `m` without
    putting a terminator back lets the greedy `[\d.]+` take the trailing dot
    off `2.5.ToString()` and hand `float()` a string it cannot parse."""
    from tools import patch_sentinel

    src = _relic('private readonly DamageVar _d '
                 '= new DamageVar(2.5.ToString());')
    assert patch_sentinel.parse_relic(src, "Sentinel")["vars"] == {}
