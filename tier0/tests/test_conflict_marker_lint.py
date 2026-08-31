from tools.lint_conflict_markers import find_markers


def test_a_marker_line_is_a_finding():
    text = "| row |" + chr(10) + "<<<<<<< HEAD" + chr(10) + "| row |" + chr(10) + ">>>>>>> origin/main" + chr(10)
    assert find_markers(text) == [2, 4]


def test_a_setext_heading_is_not_a_finding():
    text = "Title" + chr(10) + "=======" + chr(10) + "body" + chr(10)
    assert find_markers(text) == []


def test_the_tree_is_clean_today():
    import subprocess, sys
    rc = subprocess.run([sys.executable, "tools/lint_conflict_markers.py"]).returncode
    assert rc == 0
