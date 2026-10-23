"""tools/lint_loc_translations.py: placeholders and staleness of translated rows."""
import json
import subprocess
import sys

from tools.lint_loc_translations import check, english_hash, placeholders, stamp

REFERENCE = {"cards": {
    "KLEEMOD-COUNTDOWN.description":
        "[gold]Set off[/gold] the enemy. Draw {Cards:diff()} {Cards:plural:card|cards}.",
    "KLEEMOD-COUNTDOWN.title": "Countdown",
}}


def _write(root, lang, table, rows):
    path = root / lang / f"{table}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def test_placeholder_heads_ignore_the_branches_inside():
    assert placeholders("Draw {Cards:diff()} {Cards:plural:card|cards}.") == \
        placeholders("抽{Cards:diff()}{Cards:plural:张}牌。")
    assert placeholders("{Amount:cond:==1? next turn|>1? for {} turns|}")["Amount:cond"] == 1


def test_a_clean_stamped_translation_passes(tmp_path):
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    _write(tr, "zhs", "cards", {
        "KLEEMOD-COUNTDOWN.description": "[gold]引爆[/gold]敌人。抽{Cards:diff()}{Cards:plural:张}牌。",
    })
    assert stamp(REFERENCE, "zhs", tr, hs) == 1
    assert check(REFERENCE, tr, hs) == []


def test_a_dropped_placeholder_is_a_finding(tmp_path):
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    _write(tr, "zhs", "cards", {"KLEEMOD-COUNTDOWN.description": "引爆敌人。抽2张牌。"})
    stamp(REFERENCE, "zhs", tr, hs)
    findings = check(REFERENCE, tr, hs)
    assert len(findings) == 1 and "placeholders differ" in findings[0]


def test_a_row_whose_english_moved_is_stale(tmp_path):
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    _write(tr, "zhs", "cards", {"KLEEMOD-COUNTDOWN.title": "倒计时"})
    _write(hs, "zhs", "cards", {"KLEEMOD-COUNTDOWN.title": english_hash("Count Down")})
    findings = check(REFERENCE, tr, hs)
    assert len(findings) == 1 and "STALE" in findings[0]


def test_an_unstamped_or_orphan_row_is_a_finding(tmp_path):
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    _write(tr, "zhs", "cards", {"KLEEMOD-COUNTDOWN.title": "倒计时", "KLEEMOD-GONE.title": "无"})
    findings = check(REFERENCE, tr, hs)
    assert any("no English hash" in f for f in findings)
    assert any("orphan" in f for f in findings)


def test_the_English_folder_and_an_unknown_language_are_handled(tmp_path):
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    _write(tr, "eng", "cards", {"anything": "goes"})
    assert check(REFERENCE, tr, hs) == []
    _write(tr, "xx", "cards", {})
    assert "not one of the game's languages" in check(REFERENCE, tr, hs)[0]


def test_the_tree_is_clean_today():
    rc = subprocess.run([sys.executable, "tools/lint_loc_translations.py"]).returncode
    assert rc == 0


def test_a_translated_teyvat_frame_row_is_a_finding(tmp_path):
    from tools.lint_loc_translations import to_translate
    tr, hs = tmp_path / "tr", tmp_path / "hs"
    frame = {"cards": {"KLEEMOD-COUNTDOWN.title"}}
    _write(tr, "zhs", "cards", {"KLEEMOD-COUNTDOWN.title": "倒计时"})
    stamp(REFERENCE, "zhs", tr, hs)
    findings = check(REFERENCE, tr, hs, frame=frame)
    assert len(findings) == 1 and "Teyvat frame row" in findings[0]
    assert check(REFERENCE, tr, hs) == []
    assert to_translate(REFERENCE, frame) == 1


def test_the_committed_frame_list_names_rows_of_the_reference():
    from tools.lint_loc_translations import FRAME_ROWS, REFERENCE as REF, frame_rows, load_json
    assert FRAME_ROWS.exists()
    reference = load_json(REF)
    frame = frame_rows()
    assert frame.get("events")
    for table, keys in frame.items():
        assert keys <= set(reference[table])
