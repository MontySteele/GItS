"""EB-264: the mod's own sentence (`unplayable_reason_text`, klee-mod half)
wins over the enum (`unplayable_reason`) on both readers, so a Spark-less
Ka-pow! prints why in the mod's words rather than the render's map."""
from understudy import blindplay, qa_packet


ENTRY = {
    "id": "KLEEMOD-PROTO_KO_KAPOW", "name": "Ka-pow!", "cost": 0,
    "type": "attack", "rarity": "basic", "description": "Deal 7 damage.",
    "can_play": False, "unplayable_reason": "BlockedByCardLogic",
    "unplayable_reason_text": "You have no Spark.",
}


def test_the_blind_page_reads_the_sentence_first():
    face = blindplay._card_face(dict(ENTRY))
    assert face["unplayable_reason"] == "You have no Spark."


def test_the_enum_still_reads_when_no_sentence_is_sent():
    entry = dict(ENTRY); entry.pop("unplayable_reason_text")
    face = blindplay._card_face(entry)
    assert face["unplayable_reason"] == "BlockedByCardLogic"
    assert "BlockedByCardLogic" not in qa_packet.unplayable_reason(
        face["unplayable_reason"])
