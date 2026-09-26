"""The Stage forecast's target kinds reach the observation as words.

2026-09-26, the supporting-pool seat round: Lynette's act forecast carried the
wire kind `random_aura`, the blindness check read it as a snake_case leak, and
every command on the lane was refused.
"""
from understudy import blindplay_board as board
from understudy import qa_packet


def _raw(target, total_target):
    return {"seats": [], "arrivals": [], "block_after_acts": 0,
            "intent_known": True, "front_takes": 0, "reaches_furina": 0,
            "unknown": False, "act_total": 11,
            "act_total_target": total_target,
            "acts": [{"member": "lynette", "name": "Lynette", "amount": 3,
                      "element": "Anemo", "target": target, "bow": False}]}


def test_every_target_kind_is_printed_as_words_and_passes_the_blind_check():
    for kind, words in board.STAGE_TARGET_WORDS.items():
        fc = board._stage_forecast(_raw(kind, kind))
        assert fc["acts"][0]["target"] == words
        assert fc["act_total_target"] == words
        qa_packet.assert_blind(fc)


def test_an_enemy_name_passes_through():
    fc = board._stage_forecast(_raw("random", "Tunneler"))
    assert fc["act_total_target"] == "Tunneler"
