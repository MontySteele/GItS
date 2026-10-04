"""The Stage forecast's target kinds reach the observation as words.

2026-09-26, the supporting-pool seat round: Lynette's act forecast carried the
wire kind `random_aura`, the blindness check read it as a snake_case leak, and
every command on the lane was refused.
"""
from understudy import blindplay_board as board
from understudy import qa_packet


def _raw(target):
    """The wire's forecast (`FurinaStageLedger.Snapshot`, the re-founding)."""
    return {"fanfare_after": 2, "block": 0,
            "acts": [{"member": "lynette", "name": "Lynette",
                      "seat_key": 3, "kind": "damage", "amount": 3,
                      "element": "Anemo", "target": target, "times": 1,
                      "price": 0, "skips": False}]}


def test_every_target_kind_is_printed_as_words_and_passes_the_blind_check():
    for kind, words in board.STAGE_TARGET_WORDS.items():
        fc = board._stage_forecast(_raw(kind))
        assert fc["acts"][0]["target"] == words
        qa_packet.assert_blind(fc)


def test_an_enemy_name_passes_through():
    fc = board._stage_forecast(_raw("Tunneler"))
    assert fc["acts"][0]["target"] == "Tunneler"
