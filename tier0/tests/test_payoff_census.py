"""The payoff census's rubric, pinned as code.

The census (`tools/payoff_census.py`) is a RUBRIC that happens to be
executable: R137 asked for a classification rule "precisely enough that a
second classifier would reproduce your census from it", and the answer was to
ship the predicates rather than a paragraph. A rubric that can drift silently
is not that, so the predicates get tests.

Two halves, and they are guarded differently.

  * The RULE tests below run everywhere. They feed the classifier hand-built
    card records -- no game data, no `game_ref/` -- and pin what the rubric
    says. These are the ones that would catch an accidental change of
    meaning.
  * The POOL tests are skipped unless `game_ref/` is present, the same guard
    and the same reason as `test_real_silent.py`: the extracted pools are
    gitignored decompiled material, so on a fresh clone there is nothing to
    assert.

TOKEN LAYER, amended 2026-08-10. [USER] ruled the rubric AMENDED to carry a
token-creation layer: a character whose plan is to conjure a card that is not
in her own pool had no layer at all, so every card of that plan was invisible
to the census. The layer family is DERIVED from each pool's own extract, one
layer per token type the pool creates, and the tests below pin that it is
derived -- a hard-coded token name in the tool would be committed base-game
data as well as a rubric that only works for one character.
"""

import json

import pytest

from tier0.content import local_reference
from tools import payoff_census as census

GAME_REF = local_reference.game_ref_dir()

# A card record shaped like `extract_base_game_pool.parse_card`'s output, with
# every field the census reads. Tests override only what they are about.
BLANK = {
    "name": "", "rarity": "Common", "type": "Attack", "cost": 1,
    "vars": {}, "cmds": [], "generic_cmds": [], "powers": [], "orbs": [],
    "keywords": [], "creates": [], "card_refs": [], "calc_vars": [],
}


def card(**over) -> dict:
    return BLANK | over


def calc(reads=()) -> dict:
    """A computed magnitude that counts `reads`."""
    return {"var": "CalculatedVar", "args": ['"CalculatedX"'],
            "reads": sorted(reads)}


# --- the token layer is DERIVED, never listed -------------------------------

def test_a_pool_that_creates_no_token_gets_no_token_layer():
    assert census.token_markers([card(name="A"), card(name="B")]) == {}


def test_one_layer_per_token_type_the_pool_creates():
    pool = [card(name="A", creates=["Tok"]),
            card(name="B", creates=["Tok", "Other"])]
    assert sorted(census.token_markers(pool)) == ["Token:Other", "Token:Tok"]


def test_the_tool_carries_no_token_name_of_its_own():
    """A committed tool may not hold a table of base-game card names.

    Same rule `tools/extract_base_game_pool.py` states for itself: the script
    is safe to commit exactly because it recognises SHAPES, never names. The
    token layer would have been trivial to hard-code for one character, and
    that is the version this test refuses.
    """
    source = (census.REPO / "tools" / "payoff_census.py").read_text(
        encoding="utf-8")
    assert "Shiv" not in source


# --- what the token layer MEANS ---------------------------------------------

def test_making_the_token_is_generating_naming_it_is_not():
    maker = card(name="Maker", creates=["Tok"], card_refs=["Tok"])
    namer = card(name="Namer", card_refs=["Tok"])
    markers = census.token_markers([maker])
    assert census.mentions(maker, markers) == {"Token:Tok"}
    assert census.generates(maker, [], markers) == {"Token:Tok"}
    assert census.mentions(namer, markers) == {"Token:Tok"}
    assert census.generates(namer, [], markers) == set()


def test_a_computed_magnitude_that_counts_the_token_tag_reads_the_layer():
    """The third spelling of a mention, and the one that makes a payoff.

    A card whose damage is "one hit per token in a pile" never names the token
    type -- it counts cards carrying the token's own CardTag. Without the
    calculated var's arguments that card looks like a payoff of nothing.
    """
    reader = card(name="Reader", calc_vars=[calc(["CardTag.Tok"])])
    markers = census.token_markers([card(name="Maker", creates=["Tok"])])
    assert census.mentions(reader, markers) == {"Token:Tok"}
    assert census.generates(reader, [], markers) == set()


def test_the_reader_is_a_payoff_and_the_makers_are_not():
    pool = [card(name=f"Maker{i}", creates=["Tok"]) for i in range(6)]
    reader = card(name="Reader", rarity="Rare",
                  vars={"CalculationBase": 0.0},
                  calc_vars=[calc(["CardTag.Tok"])])
    pool.append(reader)
    markers = census.token_markers(pool)
    rows = [census.classify(c, [], markers) for c in pool]
    arch = census.archetypes(rows)
    assert "Token:Tok" in arch
    assert [r["name"] for r in arch["Token:Tok"]["payoffs"]] == ["Reader"]
    assert len(arch["Token:Tok"]["generators"]) == 6
    # R5: a payoff that names a layer is no longer an unattributed payoff.
    assert not [r["name"] for r in rows if r["unresolved"]]


def test_a_maker_that_also_names_another_layer_is_second_hand_there():
    """The amendment must not turn enablers into payoffs of what they tip.

    A token maker that hover-tips the power its token carries generates
    something, so R4's strict P1 no longer applies to the power -- the mention
    is second-hand. This is the §6.1 exclusion, checked on the new layer.
    """
    maker = card(name="Maker", creates=["Tok"], powers=["SomePower"])
    markers = census.token_markers([maker])
    row = census.classify(maker, [], markers)
    assert row["second_hand_of"] == ["SomePower"]
    assert row["payoff_of"] == []


def test_the_token_layer_faces_the_same_breadth_threshold():
    """No special case: MIN_LAYER admits a token layer or it does not."""
    pool = [card(name=f"Maker{i}", creates=["Tok"])
            for i in range(census.MIN_LAYER - 1)]
    markers = census.token_markers(pool)
    rows = [census.classify(c, [], markers) for c in pool]
    assert "Token:Tok" not in census.archetypes(rows)
    pool.append(card(name="OneMore", creates=["Tok"]))
    rows = [census.classify(c, [], census.token_markers(pool)) for c in pool]
    assert "Token:Tok" in census.archetypes(rows)


# --- a stale extract is refused, not silently censused ----------------------

def test_an_extract_without_the_token_fields_is_refused():
    old = {k: v for k, v in BLANK.items() if k != "creates"}
    with pytest.raises(SystemExit) as err:
        census.require_census_fields([old], "Somebody")
    assert "predates the token-creation layer" in str(err.value)


# --- the real pools ---------------------------------------------------------

pool_test = pytest.mark.skipif(
    not (GAME_REF / "silent.json").exists(),
    reason="game_ref/ is a local artifact; regenerate with "
           "tools/extract_base_game_pool.py")


@pytest.fixture(scope="module")
def censused():
    return census.build(GAME_REF)


@pool_test
def test_exactly_one_pool_admits_a_token_layer(censused):
    """The amendment's whole footprint on the five pools, pinned.

    Token layers are derived per pool, so several could admit. Only one does:
    the other pools either create no token, or create several and print too
    few cards of each to clear the breadth threshold. Recorded as a number so
    a rubric change that quietly widened the family would fail here.
    """
    admitted = {char: [layer for layer in blk["archetypes"]
                       if layer.startswith(census.TOKEN_PREFIX)]
                for char, blk in censused.items()}
    assert sum(len(v) for v in admitted.values()) == 1, admitted


@pool_test
def test_the_admitted_token_layer_has_one_rare_payoff(censused):
    """The shape of the one token archetype canon prints.

    Twelve cards name the token, eight make one, and exactly one card reads
    the count -- a rare. The layer is as broad as that pool's poison layer and
    cashes out through a single card, which is the census's headline shape
    everywhere else too.
    """
    layer, = [a for blk in censused.values()
              for name, a in blk["archetypes"].items()
              if name.startswith(census.TOKEN_PREFIX)]
    assert layer["mentions"] == 12
    assert layer["generators"] == 8
    assert layer["payoffs_by_rarity"] == {"rare": 1}
    assert layer["kind"] == "identity"


@pool_test
def test_the_amendment_attributes_one_of_the_unattributed(censused):
    """R5's unattributed count, pinned at its post-amendment value.

    It was 24 before the token layer and it is 23 after. The number is the
    census's own headline limitation, so it is pinned rather than described:
    both axes of the bands are lower bounds while it is this large.
    """
    unattributed = sum(len(blk["unresolved"]) for blk in censused.values())
    assert unattributed == 23


@pool_test
def test_every_extracted_pool_carries_the_census_fields(censused):
    """The guard above only helps if the real extracts actually pass it."""
    for character in census.CHARACTERS:
        pool = json.loads((GAME_REF / f"{character.lower()}.json")
                          .read_text(encoding="utf-8"))
        census.require_census_fields(pool, character)
