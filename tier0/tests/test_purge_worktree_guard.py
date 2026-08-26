"""The worktree purge guard, exercised hermetically.

WHY THIS TEST IS THE POINT OF THE TOOL, same as
`test_backup_game_ref_guard.py` is the point of the backup script.
`tools/purge_worktree.py` exists for ONE refusal: `git worktree remove` deletes
gitignored content out of a CLEAN worktree, and on 2026-08-24 a routine purge
of stale worktrees took both surviving `game_ref/` backups that way (BACKLOG
`EB-128`). A wrapper whose refusal is untested is a wrapper nobody can trust
enough to type instead of the raw git command.

EVERY TEST BUILDS ITS OWN GIT REPOSITORY IN `tmp_path`. Nothing here reads,
writes near, or removes a real worktree, a real `game_ref/` or the vault -- a
test for a destructive tool must not itself be capable of the destruction. The
repositories are created with `-c user.*` on the command line so a machine with
no git identity still runs them.
"""

import shutil
import subprocess

import pytest

from tools import purge_worktree as pw

pytestmark = pytest.mark.skipif(shutil.which("git") is None,
                                reason="git is not on PATH")

GITIGNORE = "\n".join([
    "__pycache__/", "bin/", "obj/", "local.props", "*.pck",
    "game_ref/", "game_ref_backup/", "art/raw/", "*.zip", "",
])


def _git(args, cwd):
    proc = subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
         "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return proc.stdout


def _repo(tmp_path):
    """A repository with one commit and one linked worktree."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init", "-b", "main"], repo)
    (repo / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (repo / "README.md").write_text("hermetic\n", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "-m", "seed"], repo)
    tree = tmp_path / "repo-work"
    _git(["worktree", "add", str(tree), "-b", "work"], repo)
    return repo, tree


def _write(path, text="x\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ------------------------------------------------------ the classifier ----

def test_cheap_to_lose_ignored_paths_are_expected():
    """Build outputs and caches: a rebuild, not somebody's work."""
    for path in ("bin/", "klee-mod/KleeCode/bin/", "obj/", "local.props",
                 "klee-mod/local.props", "understudy/__pycache__/",
                 "tier0/x.pyc", "card_gallery.html",
                 "understudy/logs/soak/", "out.csv"):
        assert pw.is_expected(path), path


def test_the_things_the_repo_has_already_lost_are_not_expected():
    """`game_ref/` heads this list because it has been destroyed four times."""
    for path in ("game_ref/", "game_ref_backup/", "sts2_decompiled/",
                 "game_assets/", "art/raw/", "art/candidates/",
                 "ImageGen/images/", ".sentinel/", "docs/mockups/",
                 "art-drop.zip"):
        assert not pw.is_expected(path), path


def test_the_lost_trees_carry_their_own_restore_note():
    """A refusal that says "are you sure" is worse than one that says what to
    do first, so `game_ref/` names its backup tool by path."""
    note = pw.why_irreplaceable("game_ref/")
    assert note and "tools.backup_game_ref" in note
    assert "EB-128" in note
    assert pw.why_irreplaceable("game_ref_backup/")
    assert pw.why_irreplaceable("bin/") is None


# ---------------------------------------------------------- the refusal ----

def test_a_clean_worktree_passes_the_check(tmp_path):
    repo, tree = _repo(tmp_path)
    assert pw.check(tree, repo) == []


def test_expected_ignored_data_alone_does_not_refuse(tmp_path):
    """A worktree that only grew build output is removable. A guard that
    refused every ignored byte would be a guard everybody learns to --force."""
    repo, tree = _repo(tmp_path)
    _write(tree / "local.props")
    _write(tree / "klee-mod" / "bin" / "Klee.dll")
    _write(tree / "understudy" / "__pycache__" / "soak.pyc")
    assert pw.check(tree, repo) == []
    assert pw.main([str(tree), "--repo", str(repo), "--dry-run"]) == 0
    assert tree.is_dir()


def test_an_unexpected_ignored_tree_refuses_and_the_data_survives(
        tmp_path, capsys):
    """THE 2026-08-24 INCIDENT, replayed. git calls this worktree clean."""
    repo, tree = _repo(tmp_path)
    _write(tree / "local.props")                      # expected, not the point
    _write(tree / "game_ref" / "ironclad_pool.yaml", "- id: bash\n")
    assert _git(["status", "--porcelain"], tree).strip() == "", \
        "the incident's precondition: git reports the worktree CLEAN"

    assert pw.check(tree, repo) == ["game_ref/"]
    assert pw.main([str(tree), "--repo", str(repo)]) == 2

    err = capsys.readouterr().err
    assert "REFUSING" in err and "game_ref/" in err
    assert "tools.backup_game_ref" in err
    assert "local.props" not in err, "an expected path is not an accusation"
    # And nothing was removed.
    assert (tree / "game_ref" / "ironclad_pool.yaml").read_text(
        encoding="utf-8") == "- id: bash\n"
    assert tree in pw.linked_worktrees(repo)


def test_the_refusal_is_not_softened_by_dry_run(tmp_path):
    """`--dry-run` is a way to ASK, not a way past the answer."""
    repo, tree = _repo(tmp_path)
    _write(tree / "game_ref" / "ironclad_pool.yaml")
    assert pw.main([str(tree), "--repo", str(repo), "--dry-run"]) == 2
    assert tree.is_dir()


def test_force_does_not_open_the_ignored_data_door(tmp_path):
    """`--force` is git's flag for TRACKED modifications and is passed
    through as such. Letting it also mean "and delete the ignored tree" would
    give the one habitual escape hatch two meanings."""
    repo, tree = _repo(tmp_path)
    _write(tree / "game_ref" / "ironclad_pool.yaml")
    assert pw.main([str(tree), "--repo", str(repo), "--force"]) == 2
    assert (tree / "game_ref" / "ironclad_pool.yaml").exists()


def test_acknowledge_is_the_only_door_and_it_opens(tmp_path, capsys):
    """The flag has to be typed after seeing the list, and then it works --
    otherwise the tool is unusable and gets routed around."""
    repo, tree = _repo(tmp_path)
    _write(tree / "game_ref" / "ironclad_pool.yaml")
    assert pw.main([str(tree), "--repo", str(repo), "--acknowledge"]) == 0
    assert "game_ref/" in capsys.readouterr().out
    assert not tree.exists()
    assert pw.linked_worktrees(repo) == []


def test_a_clean_worktree_is_removed_without_ceremony(tmp_path):
    repo, tree = _repo(tmp_path)
    assert pw.main([str(tree), "--repo", str(repo)]) == 0
    assert not tree.exists()


def test_a_collapsed_ignored_directory_is_opened_and_not_guessed_at(tmp_path):
    """git reports the SHALLOWEST wholly-ignored directory, so a worktree
    where `klee-mod/` itself is untracked reports `klee-mod/` rather than
    `klee-mod/KleeCode/bin/`. Judging the collapsed NAME alone would refuse a
    worktree holding nothing but build output -- and a guard that refuses
    everything is a guard people route around."""
    repo, tree = _repo(tmp_path)
    _write(tree / "klee-mod" / "KleeCode" / "bin" / "Klee.dll")
    _write(tree / "klee-mod" / "local.props")
    assert pw.ignored_paths(tree) == ["klee-mod/"], "the collapse is the setup"
    assert pw.check(tree, repo) == []


def test_one_unexpected_file_inside_a_collapsed_directory_still_refuses(
        tmp_path):
    """The expansion is a way to say yes to build output, not a way for
    anything to hide under one."""
    repo, tree = _repo(tmp_path)
    _write(tree / "scratch" / "bin" / "Klee.dll")
    _write(tree / "scratch" / "game_ref" / "ironclad_pool.yaml")
    assert pw.ignored_paths(tree) == ["scratch/"]
    assert pw.check(tree, repo) == ["scratch/"]


def test_an_empty_ignored_directory_loses_nothing(tmp_path):
    repo, tree = _repo(tmp_path)
    (tree / "game_ref").mkdir()
    assert pw.check(tree, repo) == []


# ------------------------------------------------- what is not a worktree ---

def test_the_main_checkout_is_never_a_target(tmp_path, capsys):
    """`git worktree list` prints the main worktree first and this tool drops
    it. A mistyped path must be a refusal, never a repository."""
    repo, _tree = _repo(tmp_path)
    assert pw.main([str(repo), "--repo", str(repo)]) == 2
    assert "not a linked worktree" in capsys.readouterr().err
    assert (repo / "README.md").exists()


def test_a_plain_directory_is_never_a_target(tmp_path, capsys):
    repo, _tree = _repo(tmp_path)
    stranger = tmp_path / "not-a-worktree"
    stranger.mkdir()
    _write(stranger / "precious.yaml")
    assert pw.main([str(stranger), "--repo", str(repo)]) == 2
    assert "not a linked worktree" in capsys.readouterr().err
    assert (stranger / "precious.yaml").exists()


def test_a_missing_path_refuses_rather_than_succeeding_vacuously(
        tmp_path, capsys):
    repo, _tree = _repo(tmp_path)
    assert pw.main([str(tmp_path / "gone"), "--repo", str(repo)]) == 2
    assert "REFUSED" in capsys.readouterr().err
