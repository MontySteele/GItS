"""Co-op rest site: Mend heals the partner and spends the rest action.

2026-10-09 co-op paired round (`review/records/coop-paired-round-2026-10-09.md`,
about 10 seats on 3 seeds): Mend answered "ok", yet Smith or Rest was still
accepted after it, and the heal mostly did not show.

The cause is the bridge, not the game. `MendRestSiteOption.OnSelect` (v0.111.0
decompile) opens a pick of the partner with `NTargetManager.StartTargeting`
and awaits it; the bridge only ForceClicked the button, so nothing made the
pick. The next command cancelled the targeting, `OnSelect` returned false, and
`RestSiteSynchronizer.ChooseOption` kept every option. The fix names the
partner, clicks, and finishes the pick on them
(`vendor/STS2_MCP/gits/GitsRestSiteMend.cs`), so `OnSelect` heals and returns
true and the option is spent like Rest and Smith.

The bridge has no C# test host, so these pins read the source, as the other
bridge pins do (`test_bridge_potion_discard_synced.py`).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "vendor" / "STS2_MCP"


def _method(src: str, name: str) -> str:
    start = src.index(f"Dictionary<string, object?> {name}(")
    nxt = src.find("private static ", start + 1)
    return src[start:nxt if nxt > 0 else len(src)]


def _code(body: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in body.splitlines())


def test_multiplayer_rest_option_routes_to_the_same_method():
    mp = (BRIDGE / "McpMod.MultiplayerActions.cs").read_text(encoding="utf-8")
    route = re.search(r'"choose_rest_option"\s*=>\s*(\w+)\(', mp)
    assert route, "multiplayer switch lost its choose_rest_option arm"
    assert route.group(1) == "ExecuteChooseRestOption", route.group(1)


def test_mend_names_the_partner_before_the_click_and_aims_after_it():
    src = (BRIDGE / "McpMod.Actions.cs").read_text(encoding="utf-8")
    body = _code(_method(src, "ExecuteChooseRestOption"))
    branch = body.index("GitsRestSiteMend.IsMend(button.Option)")
    partner = body.index("GitsRestSiteMend.Partner(", branch)
    click = body.index("button.ForceClick()", branch)
    aim = body.index("GitsRestSiteMend.AimAt(partner)", branch)
    assert partner < click < aim, (
        "Mend must name its partner before the click (a refusal must not "
        "leave a pick open) and finish the pick after the click opens it")
    assert 'Error("Mend has no living partner to heal")' in body
    assert "Mend was not carried out" in body, (
        "a pick that could not be finished must be refused, not reported ok")


def test_the_helper_finishes_the_targeting_on_the_partner():
    helper = _code((BRIDGE / "gits" / "GitsRestSiteMend.cs").read_text(
        encoding="utf-8"))
    assert "option is MendRestSiteOption" in helper
    # The partner is the living rest-site character that is not the local
    # player -- the set Mend's own AllowHoveringNode offers.
    assert "room.characterAnims" in helper
    assert "!LocalContext.IsMe(c.Player)" in helper
    assert "!c.Player.Creature.IsDead" in helper
    # The pick is finished, not cancelled: OnSelect only returns true (and the
    # synchronizer only spends the option) when the targeting ends on a node.
    assert 'GetMethod("FinishTargeting"' in helper
    hover = helper.index("targetManager.OnNodeHovered(partner)")
    finish = helper.index("FinishTargeting.Invoke(targetManager, new object[] { false })")
    assert hover < finish
    assert "targetManager.IsInSelection" in helper
