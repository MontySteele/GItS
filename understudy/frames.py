"""OFF-BY-DEFAULT window capture. Frames are MATERIAL, never evidence.

WHAT THIS IS FOR
`S4-G17` and the animation-sprint looks (`AS2-D5` salon composition, `AS2-B5`
motion/facing, `AS2-E2` icon picks) all need one thing the apparatus cannot
give them and one thing it can. It cannot give a judgment: a JSON-state agent
cannot see the screen, and that is the no-fun rule, not a limitation to be
engineered around. It CAN give [USER] frames to look at, taken at moments the
bot can reach and a person would have to grind for -- which is exactly what
EB-52's capture packet was assembled by hand.

THE GUARDRAIL, AND IT IS THE WHOLE CONTRACT OF THIS FILE
A frame produced here is material for a person's sitting. Nothing derived from
it by a bot or an LLM -- not a composition note, not "the ribbon reads well",
not a preference between two takes -- is a claim about look, legibility,
readability or fun. Those stay [USER]-only instruments. `GUARDRAIL` below is
that sentence, it is written onto every manifest row, and a capture that could
not write its manifest row does not happen.

OFF BY DEFAULT, AND ENV-ONLY TO TURN ON
`GITS_UNDERSTUDY_CAPTURE=1`. Same shape and the same reasoning as
`GITS_ILSPY_TREE` (`tools/extract_base_game_pool.py`): a leg whose output is
material sitting on somebody's disk must never be the default and must never be
a path this repo chooses for you. Without it every verb here refuses and says
which variable would enable it.

WHAT IT CAPTURES, AND WHAT IT REFUSES TO
The GAME WINDOW's rectangle, found from the process's own `MainWindowHandle` --
never the whole desktop. A full-screen grab would sweep in whatever else the
machine happens to be showing, which is somebody's private business and is not
the material anybody asked for. Three refusals, each named: no window at all,
a zero-size rectangle, and a MINIMISED window (Windows parks those at a
-32000 origin, which is a valid rectangle nowhere on screen).

HOW IT CAPTURES, AND WHY IT CHANGED (2026-08-13, EB-97)

It asks the WINDOW for its pixels -- `PrintWindow(hWnd, hdc,
PW_RENDERFULLCONTENT)` -- and only falls back to reading the screen under the
window's rectangle if that comes back blank.

That ordering is a defect fix, and the defect is worth stating because the
frames it produced LOOKED fine. The first version copied the screen at the
rectangle `GetWindowRect` reported. A PowerShell host is DPI-UNAWARE, so on a
multi-monitor machine whose displays scale differently, the rectangle it is
handed is virtualised into the primary display's coordinate space -- and the
copy lands on the PRIMARY monitor while the game is on the SECOND one. Every
`frame-20260813-*` frame is a close-up of the desktop wallpaper. Nothing in
the apparatus could see it: the process was found, the handle was real, the
rectangle was 1921x1080, the PNG existed and had the right dimensions, and
the manifest row was written. Existence and dimensions are not verification.
**A frame is verified by OPENING it and seeing the game.** That is now the
standard, and it is in this docstring because it is the only check that would
have caught this.

The script also makes itself per-monitor DPI aware before it asks for
anything, so the fallback path is right as well as second.

The fallback keeps the old honest caveat: it is the screen CONTENT under the
window's rectangle, so a window sitting ON TOP of the game appears in the
frame. `PrintWindow` does not have that problem, which is the other reason it
goes first. The manifest records which route ran, per frame.

WHERE FRAMES GO
`understudy/logs/frames/`, gitignored for the reason `art/g12_captures/` and
`art/eb52_captures/` are: a frame of the running game has Tier F art in it, and
committing one distributes exactly what principles section 9 refuses to. The
manifest travels with them and is cited by path, the way the live-game capture
packets already are.

NO PILLOW, NO NUMPY, NO DEPENDENCY. The suite's imports are pytest/pyyaml/
pillow/numpy and this file needs none of them: the capture is a PowerShell
script over `System.Drawing`, which is on every Windows box, and everything
this module does itself is stdlib. The subprocess call is injected, so the
naming, the refusals and the manifest are testable without taking a picture of
anybody's screen.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

FRAME_DIR = Path(__file__).resolve().parent / "logs" / "frames"
MANIFEST = FRAME_DIR / "frames.jsonl"

CAPTURE_ENV = "GITS_UNDERSTUDY_CAPTURE"

# EB-142 hygiene, 2026-08-25. The auto route is `printwindow` first and
# `copyfromscreen` only if the surface comes back BLANK -- and on this
# Godot/Vulkan window `PrintWindow` returns a surface that is not blank and is
# not complete either: the background and the HUD chrome render, the HAND, the
# ENEMIES and the prompt caption do not. `Test-Blank` sees a varied bitmap,
# says "fine", and every in-combat frame on the default route is a PARTIAL --
# missing exactly the three things anyone captures a combat frame to look at.
# There is no way to make the blank test catch that (the frame genuinely is
# not blank), so the answer is an explicit override rather than a smarter
# heuristic: name the route and take responsibility for its caveat.
ROUTE_ENV = "GITS_UNDERSTUDY_CAPTURE_ROUTE"
ROUTE_AUTO = "auto"
ROUTES = (ROUTE_AUTO, "printwindow", "copyfromscreen")

GAME_IMAGE = "SlayTheSpire2"          # process name, no .exe -- Get-Process

GUARDRAIL = (
    "MATERIAL, not evidence. A frame captured by this apparatus is something "
    "for a person to look at. Nothing a bot or an LLM derives from it is a "
    "claim about look, legibility, readability or fun -- those stay "
    "[USER]-only instruments (Guardrail-7, and the no-fun rule)."
)

DISABLED_NOTE = (
    f"window capture is OFF. Set {CAPTURE_ENV}=1 to enable it. It is env-only "
    f"and off by default on purpose: its output is material sitting on a disk, "
    f"so this repo does not choose to produce it for you."
)


def enabled(env: dict[str, str] | None = None) -> bool:
    env = os.environ if env is None else env
    return (env.get(CAPTURE_ENV) or "").strip() in ("1", "true", "TRUE", "yes")


def route(env: dict[str, str] | None = None) -> str:
    """The capture route this run is pinned to, or `"auto"`.

    Same family and the same reasoning as `CAPTURE_ENV`: env-only, and an
    unrecognised value falls back to `auto` rather than failing the capture --
    a typo should cost a caveat, never the frame.
    """
    env = os.environ if env is None else env
    want = (env.get(ROUTE_ENV) or "").strip().lower()
    return want if want in ROUTES else ROUTE_AUTO


def frame_path(label: str, stamp: str | None = None,
               out_dir: Path | None = None) -> Path:
    """`frame-<stamp>-<label>.png`, with the label reduced to a safe slug.

    The stamp leads so a directory listing is chronological, which is how a
    sitting reads a batch of takes.
    """
    stamp = stamp or time.strftime("%Y%m%d-%H%M%S")
    slug = "".join(c if (c.isalnum() or c in "-_") else "-"
                   for c in (label or "frame").strip().lower()).strip("-")
    return (out_dir or FRAME_DIR) / f"frame-{stamp}-{slug or 'frame'}.png"


# The capture itself. Kept as one script rather than assembled per call so that
# what runs is readable in one piece, which matters for a thing that reads
# pixels off somebody's machine.
_PS_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
# Progress records are written to the ERROR stream as CLIXML by a non-
# interactive host, and the first Add-Type emits one. Silenced so stderr means
# "something went wrong" and nothing else.
$ProgressPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public struct GitsRect { public int Left; public int Top; public int Right; public int Bottom; }
public static class GitsWin {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out GitsRect lpRect);
    // PW_RENDERFULLCONTENT = 2. Asks the window to render ITSELF into a device
    // context, so no screen coordinate, no monitor index and no DPI mapping is
    // involved anywhere in the path.
    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);
    // Per-monitor-v2. Called BEFORE any rectangle is asked for: an unaware
    // host is handed virtualised coordinates, which is exactly how this leg
    // spent a night photographing the wrong monitor.
    [DllImport("user32.dll")]
    public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();
    // FOREGROUNDING, for the copyfromscreen route ONLY. That route reads the
    // SCREEN under the window's rectangle, so it photographs whatever is on
    // top -- and something always is, because the thing driving this capture
    // is a console. SwitchToThisWindow is the shell's own alt-tab and does
    // not carry SetForegroundWindow's focus-stealing restrictions;
    // HWND_TOPMOST is the belt to its braces, and is dropped again after the
    // grab so the game does not stay pinned over everything the user owns.
    [DllImport("user32.dll")]
    public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter,
        int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")]
    public static extern bool IsZoomed(IntPtr hWnd);
}
"@
try { [void][GitsWin]::SetProcessDpiAwarenessContext([IntPtr](-4)) }
catch { try { [void][GitsWin]::SetProcessDPIAware() } catch { } }

# __PIDSEL__ is either an id filter or the image-name lookup. With two game
# processes up, a name lookup takes whichever the OS lists first, so a
# two-lane capture MUST select by pid or it photographs the other lane.
$proc = __PIDSEL__ |
        Where-Object { $_.MainWindowHandle -ne 0 } |
        Select-Object -First 1
if (-not $proc) {
    Write-Output 'NO_WINDOW'
    exit 2
}
$hwnd = $proc.MainWindowHandle
$rect = New-Object GitsRect
[void][GitsWin]::GetWindowRect($hwnd, [ref]$rect)
$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top
if ($w -le 0 -or $h -le 0) {
    Write-Output 'EMPTY_RECT'
    exit 3
}
# A MINIMISED window still has a MainWindowHandle and still reports a positive
# width and height. IsIconic is the direct question; the -32000 origin check
# stays as the belt to its braces, because a restored-but-parked window is a
# rectangle nowhere on screen either way.
if ([GitsWin]::IsIconic($hwnd) -or $rect.Left -le -30000 -or $rect.Top -le -30000) {
    Write-Output 'MINIMISED'
    exit 4
}

function Test-Blank($bitmap) {
    # PrintWindow returns true and an all-black surface for some GPU-composited
    # windows, which is a silent failure wearing a success. Sample a grid: if
    # every sample is the same colour, the render did not happen.
    $first = $null
    for ($x = 4; $x -lt $bitmap.Width; $x += [Math]::Max(1, [int]($bitmap.Width / 16))) {
        for ($y = 4; $y -lt $bitmap.Height; $y += [Math]::Max(1, [int]($bitmap.Height / 16))) {
            $c = $bitmap.GetPixel($x, $y).ToArgb()
            if ($null -eq $first) { $first = $c }
            elseif ($c -ne $first) { return $false }
        }
    }
    return $true
}

# HWND_TOPMOST = -1, HWND_NOTOPMOST = -2; SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE
# = 0x0013. Position and size are never touched -- only Z order.
function Set-Foreground($hWnd) {
    [GitsWin]::SwitchToThisWindow($hWnd, $true)
    [void][GitsWin]::SetWindowPos($hWnd, [IntPtr](-1), 0, 0, 0, 0, 0x0013)
    # The compositor needs a beat to actually put it there. Without this the
    # grab races the raise and photographs the console it was told to get out
    # from behind.
    Start-Sleep -Milliseconds 350
}
function Clear-Foreground($hWnd) {
    [void][GitsWin]::SetWindowPos($hWnd, [IntPtr](-2), 0, 0, 0, 0, 0x0013)
}

$bmp = New-Object System.Drawing.Bitmap $w, $h
$gfx = [System.Drawing.Graphics]::FromImage($bmp)

$forced = '__ROUTE__'
if ($forced -eq 'copyfromscreen') {
    # PINNED by GITS_UNDERSTUDY_CAPTURE_ROUTE. No PrintWindow attempt at all,
    # so the partial surface this route exists to avoid is never written.
    $route = 'copyfromscreen-forced'
    Set-Foreground $hwnd
    try {
        $gfx.Clear([System.Drawing.Color]::Black)
        $gfx.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
    } finally { Clear-Foreground $hwnd }
} else {
    $route = 'printwindow'
    $hdc = $gfx.GetHdc()
    $ok = [GitsWin]::PrintWindow($hwnd, $hdc, 2)
    $gfx.ReleaseHdc($hdc)
    if ($forced -ne 'printwindow' -and ((-not $ok) -or (Test-Blank $bmp))) {
        # Fallback: the screen under the window's rectangle. Now DPI-correct,
        # because awareness was set above -- but still the screen and not the
        # window, so anything sitting on top of the game lands in the frame.
        # Foregrounded for the same reason the forced route is.
        $route = 'copyfromscreen'
        Set-Foreground $hwnd
        try {
            $gfx.Clear([System.Drawing.Color]::Black)
            $gfx.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
        } finally { Clear-Foreground $hwnd }
    } elseif ($forced -eq 'printwindow') {
        $route = 'printwindow-forced'
    }
}
$bmp.Save('__OUT__', [System.Drawing.Imaging.ImageFormat]::Png)
$gfx.Dispose()
$bmp.Dispose()
Write-Output ("OK {0} {1} {2}" -f $w, $h, $route)
"""


def build_script(image: str, out_path: Path,
                 forced_route: str = ROUTE_AUTO,
                 pid: int | None = None) -> str:
    """The script with its four holes filled. Separated so it can be read.

    The substitutions are a process NAME, an integer pid, a path this module
    chose, and a route drawn from `ROUTES` -- none of them caller text
    arriving from a wire; `frame_path` slugs the label before it can reach
    here, an unknown route is normalised to `auto` rather than interpolated,
    and the pid goes through `int()` before it is spelled into the selector.
    """
    if forced_route not in ROUTES:
        forced_route = ROUTE_AUTO
    pidsel = (f"Get-Process -Id {int(pid)} -ErrorAction SilentlyContinue"
              if pid is not None else
              f"Get-Process -Name '{image}' -ErrorAction SilentlyContinue")
    return (_PS_SCRIPT
            .replace("__PIDSEL__", pidsel)
            .replace("__IMAGE__", image)
            .replace("__OUT__", str(out_path).replace("'", "''"))
            .replace("__ROUTE__", forced_route))


def encoded_command(script: str) -> str:
    """PowerShell's own `-EncodedCommand` form: base64 of UTF-16LE.

    NOT `-Command -`, and that cost a probe to learn: a script arriving on
    stdin is processed as if it were typed line by line, so the here-string
    that carries the P/Invoke declaration never survives -- the run exits 0
    having printed nothing, which is a silent no-op wearing a success. NOT a
    temp `.ps1` either, because that is a file this module would have to create,
    find, and be trusted to delete on every path including the ones that throw.
    """
    import base64
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def _run_powershell(script: str,
                    timeout: float = 60.0) -> tuple[int, str, str]:
    """`(exit code, stdout, stderr)`, kept apart on purpose.

    The result token is read off STDOUT alone. Folded together once, a host's
    CLIXML progress blob landed on the end of the success line and the size the
    manifest recorded was that blob.
    """
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive",
         "-ExecutionPolicy", "Bypass",
         "-EncodedCommand", encoded_command(script)],
        capture_output=True, timeout=timeout)
    return (proc.returncode,
            (proc.stdout or b"").decode("utf-8", "replace").strip(),
            (proc.stderr or b"").decode("utf-8", "replace").strip())


def capture(label: str = "frame", note: str = "",
            context: dict | None = None,
            image: str = GAME_IMAGE,
            out_dir: Path | None = None,
            manifest: Path | None = None,
            env: dict[str, str] | None = None,
            runner=_run_powershell,
            stamp: str | None = None,
            pid: int | None = None,
            instance: str = "") -> dict:
    """Take one frame of the game window. Returns a report; never raises.

    `context` is whatever the caller knows about the moment -- screen, act,
    floor, seed. It is COPIED onto the manifest row rather than inferred here:
    this module does not read the wire, and a capture that guessed at where it
    was taken would be a frame labelled with a screen it might not be of.
    """
    if not enabled(env):
        return {"status": "disabled", "message": DISABLED_NOTE,
                "guardrail": GUARDRAIL}

    out = frame_path(label, stamp=stamp, out_dir=out_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        code, stdout, stderr = runner(
            build_script(image, out, forced_route=route(env), pid=pid))
    except Exception as exc:                                 # noqa: BLE001
        return {"status": "error", "message": f"{type(exc).__name__}: {exc}",
                "guardrail": GUARDRAIL, "path": str(out)}

    token = (stdout.splitlines() or [""])[0].strip()
    if code != 0 or not token.startswith("OK"):
        reason = {
            "NO_WINDOW": (f"no visible window for pid {pid}" if pid is not None
                          else f"no visible window for process '{image}'; the "
                               f"game must be running"),
            "EMPTY_RECT": "the window reported a zero-size rectangle",
            "MINIMISED": "the game window is minimised (parked off-screen at "
                         "a -32000 origin); restore it and capture again",
        }.get(token, stderr or token or "no output")
        return {"status": "error", "message": reason,
                "guardrail": GUARDRAIL, "path": str(out)}
    parts = token.split()
    size = " ".join(parts[1:3])
    # WHICH ROUTE RAN IS PART OF THE RECORD. `copyfromscreen` frames can carry
    # an overlapping window; `printwindow` frames cannot. A reader of the
    # manifest is entitled to know which kind of frame they are looking at.
    ran_route = parts[3] if len(parts) > 3 else "unknown"

    row = {
        "record": "frame", "ts": time.time(),
        "path": str(out), "label": label, "note": note,
        "size": size,
        "route": ran_route,
        # The `*-forced` suffix on `route` already says a route was PINNED;
        # this says what it was pinned TO, so a manifest read back months
        # later does not have to infer the env from the suffix.
        "route_requested": route(env),
        # WHICH GAME THIS IS A PICTURE OF. With two lanes up, a frame with no
        # lane on it is a frame nobody can attribute afterwards; `pid` is the
        # fact and `instance` is the label a reader can match to a record row.
        "pid": pid,
        "instance": instance or "lane0",
        "context": dict(context or {}),
        # ON EVERY ROW, not once at the top of the file. A manifest is read in
        # slices and concatenated with other manifests; a guardrail that lives
        # in a header is a guardrail that survives exactly one copy-paste.
        "guardrail": GUARDRAIL,
    }
    _append(manifest or MANIFEST, row)
    return {"status": "ok", "message": f"captured {size} via {ran_route}",
            "guardrail": GUARDRAIL, "path": str(out), "route": ran_route,
            "row": row}


def _append(manifest: Path, row: dict) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
