"""The Steam Workshop workspace (`tools/package_workshop.py`).

Pins what goes up when [USER] runs `ModUploader.exe upload -w <workspace>`:
the mod alone (no harness), a plain version, the uploader's field set, the
two variants' ids and kit lists, and the build switches the C# reads
(`klee-mod/KleeCode/ReleaseVariant.cs`). Builds nothing: the workspace test
uses stand-in files.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import package_workshop as pw

ROOT = Path(__file__).resolve().parents[2]


def test_the_version_is_plain():
    assert pw.check_version("0.3.0") == "0.3.0"
    # The dev stamps carry a `+` mark; a release takes none.
    for bad in ("0.2.1357+dirty", "0.2.1357+proto", "0.3.0+next", "0.3",
                "v0.3.0", ""):
        with pytest.raises(SystemExit):
            pw.check_version(bad)


def test_the_variants():
    public, beta = pw.VARIANTS["public"], pw.VARIANTS["beta"]
    assert public.mod_id == "klee"
    assert "yae" not in public.kits
    assert set(public.kits) == {"klee", "kokomi", "furina", "varka"}
    assert beta.mod_id != public.mod_id
    assert set(beta.kits) == set(pw.ALL_KITS)
    assert beta.title.endswith("(Beta)")


def test_every_kit_id_matches_the_csharp_list():
    src = (ROOT / "klee-mod" / "KleeCode" / "ReleaseVariant.cs").read_text(encoding="utf-8")
    assert 'new[] { "klee", "kokomi", "furina", "varka", "yae" }' in src
    assert pw.ALL_KITS == ("klee", "kokomi", "furina", "varka", "yae")


@pytest.mark.parametrize("name", ["public", "beta"])
def test_the_build_is_a_release_build_with_no_harness(name, tmp_path):
    v = pw.VARIANTS[name]
    args = pw.build_args(v, "0.3.0", tmp_path)
    line = " ".join(args)
    assert args[:2] == ["dotnet", "build"]
    assert "-c Release" in line
    assert "-p:WorkshopRelease=true" in args
    assert f"-p:GitsKits={'+'.join(v.kits)}" in args
    assert "-p:InformationalVersion=0.3.0+workshop." + name in args
    assert "KleeCode.csproj" in line
    assert "STS2_MCP" not in line and "bridge" not in line.lower()
    # Its own output and intermediate folders: the dev bin/Release is untouched.
    assert any(a.startswith("-p:OutDir=") and str(tmp_path) in a for a in args)
    assert any(a.startswith("-p:IntermediateOutputPath=") for a in args)


def test_the_csproj_reads_both_switches():
    proj = (ROOT / "klee-mod" / "KleeCode" / "KleeCode.csproj").read_text(encoding="utf-8")
    assert "'$(WorkshopRelease)' == 'true'" in proj
    assert "WORKSHOP_RELEASE" in proj
    assert "<_Parameter1>GitsKits</_Parameter1>" in proj
    assert "<_Parameter1>GitsWorkshopRelease</_Parameter1>" in proj
    # Off unless named: no default for either in the shared props.
    props = (ROOT / "klee-mod" / "Directory.Build.props").read_text(encoding="utf-8")
    assert "WorkshopRelease" not in props and "GitsKits" not in props


def test_telemetry_is_gated_on_the_release_flag():
    src = (ROOT / "klee-mod" / "KleeCode" / "Diagnostics"
           / "PlayTelemetry.cs").read_text(encoding="utf-8")
    assert "WorkshopRelease.TelemetryWrites(" in src
    assert "if (_writeFailed || !Enabled) return;" in src


def test_the_manifest():
    source = json.loads((ROOT / "klee-mod" / "Klee" / "manifest.json").read_text(encoding="utf-8"))
    pub = pw.manifest_for(pw.VARIANTS["public"], "0.3.0", source)
    beta = pw.manifest_for(pw.VARIANTS["beta"], "0.3.0", source)
    assert (pub["id"], pub["version"]) == ("klee", "0.3.0")
    assert (beta["id"], beta["version"]) == ("klee-beta", "0.3.0")
    assert beta["name"].endswith("(Beta)")
    for m in (pub, beta):
        assert m["has_dll"] and m["has_pck"]
        assert any(d["id"] == "BaseLib" for d in m["dependencies"])


@pytest.mark.parametrize("name", ["public", "beta"])
def test_workshop_json_has_the_uploader_fields(name):
    w = pw.workshop_json(pw.VARIANTS[name], "0.3.0", "friends_only", None)
    assert set(w) == {"title", "description", "visibility", "changeNote", "tags",
                      "dependencies", "contentDescriptors", "minBranch", "maxBranch"}
    assert w["visibility"] == "friends_only"
    # ModUploader reads dependencies as List<ulong>: numbers, BaseLib's item.
    assert w["dependencies"] == [3737335127]
    assert w["minBranch"] is None and w["maxBranch"] is None
    d = w["description"]
    assert d.startswith("[DRAFT")
    for words in ("Klee", "Varka", "Furina", "Kokomi", "Requires BaseLib",
                  "Fan-made, not affiliated with HoYoverse or Mega Crit.",
                  "Free.", "same version", "same variant"):
        assert words in d, words
    assert ("Yae" in d) == (name == "beta")


def test_the_default_visibility_is_friends_only():
    with pytest.raises(SystemExit):
        pw.workshop_json(pw.VARIANTS["public"], "0.3.0", "everyone", None)
    import inspect
    assert 'default="friends_only"' in inspect.getsource(pw.main)


def _fake_surface(tmp_path: Path) -> Path:
    rows = [
        {"id": "proto_kl_spark", "character": "klee"},
        {"id": "proto_ym_slip", "character": "yae"},
        {"id": "proto_ym_borrow", "character": "yae", "art_of": "proto_kl_spark"},
        {"id": "proto_mi_yae_sesshou_sakura", "character": "companion"},
    ]
    p = tmp_path / "surface.yaml"
    import yaml
    p.write_text(yaml.safe_dump(rows), encoding="utf-8")
    return p


def test_a_left_out_kit_takes_its_own_art_and_nothing_shared(tmp_path):
    surface = _fake_surface(tmp_path)
    ship = {
        "proto_kl_spark": tmp_path / "klee" / "proto_kl_spark.png",
        "proto_ym_slip": tmp_path / "yae" / "proto_ym_slip.png",
        "ym_annotation_face": tmp_path / "yae" / "ym_annotation_face.png",
        "proto_mi_yae_sesshou_sakura": tmp_path / "companions" / "proto_mi_yae_sesshou_sakura.png",
    }
    out = pw.excluded_kit_art(pw.VARIANTS["public"], ship, surface)
    assert out >= {"proto_ym_slip", "ym_annotation_face"}
    # A Yae row wearing Klee's art does not take Klee's art with it, and the
    # Universal Companion "Yae Miko -- Sesshou Sakura" stays.
    assert "proto_kl_spark" not in out
    assert "proto_mi_yae_sesshou_sakura" not in out
    assert pw.excluded_kit_art(pw.VARIANTS["beta"], ship, surface) == set()


def _stand_ins(tmp_path: Path):
    dll = tmp_path / "klee.dll"
    dll.write_bytes(b"MZ" + b"\0" * 64)
    pck = tmp_path / "klee.pck"
    pck.write_bytes(b"GDPC" + b"\0" * 64)
    art_dir = tmp_path / "art"
    art_dir.mkdir()
    art = {}
    for stem in ("proto_kl_spark", "proto_vk_oath"):
        p = art_dir / f"{stem}.png"
        p.write_bytes(b"\x89PNG")
        art[stem] = p
    image = tmp_path / "preview.png"
    image.write_bytes(b"\x89PNG" + b"\0" * 100)
    return dll, pck, art, image


@pytest.mark.parametrize("name", ["public", "beta"])
def test_the_workspace_holds_the_mod_only(name, tmp_path):
    v = pw.VARIANTS[name]
    dll, pck, art, image = _stand_ins(tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "mod_id.txt").write_text("123456789\n", encoding="utf-8")
    stale = ws / "content" / "STS2_MCP"
    stale.mkdir(parents=True)
    (stale / "STS2_MCP.json").write_text("{}", encoding="utf-8")

    pw.write_workspace(v, "0.3.0", ws, dll=dll, pck=pck, art=art, image=image,
                       visibility="friends_only", change_note=None)

    assert sorted(p.name for p in ws.iterdir()) == [
        "content", "image.png", "mod_id.txt", "workshop.json"]
    # ModUploader's item id survives a repackage.
    assert (ws / "mod_id.txt").read_text(encoding="utf-8").strip() == "123456789"
    content = ws / "content"
    assert [p.name for p in content.iterdir()] == [v.mod_id]
    mod = content / v.mod_id
    assert sorted(p.name for p in mod.iterdir()) == sorted(
        ["images", "manifest.json", f"{v.mod_id}.dll", f"{v.mod_id}.pck"])
    # The stand-ins are not real pngs, so each falls back to its .png;
    # test_card_art_is_staged_as_lossless_webp covers the conversion.
    assert sorted(p.name for p in (mod / "images" / "cards").iterdir()) == [
        "proto_kl_spark.png", "proto_vk_oath.png"]
    assert [p.name for p in content.rglob("*.json")] == ["manifest.json"]
    manifest = json.loads((mod / "manifest.json").read_text(encoding="utf-8"))
    assert (manifest["id"], manifest["version"]) == (v.mod_id, "0.3.0")
    raw = (ws / "workshop.json").read_bytes()
    assert b"\r\n" not in raw
    assert json.loads(raw)["title"] == v.title


def test_a_placeholder_preview_is_written_when_no_art_exists(tmp_path):
    pytest.importorskip("PIL")
    dll, pck, art, _image = _stand_ins(tmp_path)
    ws = tmp_path / "ws"
    pw.write_workspace(pw.VARIANTS["public"], "0.3.0", ws, dll=dll, pck=pck,
                       art=art, image=tmp_path / "absent.png",
                       visibility="friends_only", change_note="first")
    png = ws / "image.png"
    assert png.read_bytes()[:4] == b"\x89PNG"
    assert png.stat().st_size < pw.IMAGE_LIMIT
    assert json.loads((ws / "workshop.json").read_text(encoding="utf-8"))["changeNote"] == "first"


def test_card_art_is_staged_as_lossless_webp(tmp_path):
    # The Workshop ships card portraits as WebP (~29% smaller than the png);
    # the loader (`RosterArt.PortraitCandidates`) tries .webp, then .png. The
    # conversion must hold every pixel, transparency included.
    Image = pytest.importorskip("PIL.Image")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    rgb = Image.new("RGB", (7, 5))
    rgb.putdata([((x * 37) % 256, (y * 53) % 256, (x * y * 11) % 256)
                 for y in range(5) for x in range(7)])
    rgb.save(src_dir / "a_rgb.png")
    rgba = Image.new("RGBA", (6, 4))
    rgba.putdata([(x * 40, y * 60, 200, (x * y * 30) % 256)
                  for y in range(4) for x in range(6)])
    rgba.save(src_dir / "b_rgba.png")
    (src_dir / "c_broken.png").write_bytes(b"not a png")
    cards = tmp_path / "cards"
    cards.mkdir()

    written = {stem: pw.stage_card(src_dir / f"{stem}.png", cards, stem)
               for stem in ("a_rgb", "b_rgba", "c_broken")}

    assert written["a_rgb"].name == "a_rgb.webp"
    assert written["b_rgba"].name == "b_rgba.webp"
    for stem in ("a_rgb", "b_rgba"):
        with Image.open(src_dir / f"{stem}.png") as want, Image.open(written[stem]) as got:
            assert got.format == "WEBP"
            assert got.convert("RGBA").tobytes() == want.convert("RGBA").tobytes()
    # A source the encoder cannot read ships as the png it was.
    assert written["c_broken"].name == "c_broken.png"
    assert written["c_broken"].read_bytes() == b"not a png"
    assert sorted(p.name for p in cards.iterdir()) == [
        "a_rgb.webp", "b_rgba.webp", "c_broken.png"]


def test_the_encode_cache_reuses_verified_results(tmp_path):
    from PIL import Image
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    img = Image.new("RGBA", (6, 4))
    img.putdata([(x * 40, y * 60, 200, (x * y * 30) % 256)
                 for y in range(4) for x in range(6)])
    img.save(src_dir / "a.png")
    (src_dir / "b.png").write_bytes(b"not a png")
    cache = tmp_path / "cache"
    first = tmp_path / "one"
    first.mkdir()
    a1 = pw.stage_card(src_dir / "a.png", first, "a", cache)
    b1 = pw.stage_card(src_dir / "b.png", first, "b", cache)
    assert (a1.name, b1.name) == ("a.webp", "b.png")
    assert len(list(cache.iterdir())) == 2
    # A second run copies from the cache: same bytes, nothing re-encoded.
    second = tmp_path / "two"
    second.mkdir()
    a2 = pw.stage_card(src_dir / "a.png", second, "a", cache)
    b2 = pw.stage_card(src_dir / "b.png", second, "b", cache)
    assert a2.read_bytes() == a1.read_bytes()
    assert b2.read_bytes() == b"not a png"
    # Edited art misses the cache and is encoded and checked again.
    img.putpixel((0, 0), (1, 2, 3, 4))
    img.save(src_dir / "a.png")
    third = tmp_path / "three"
    third.mkdir()
    a3 = pw.stage_card(src_dir / "a.png", third, "a", cache)
    with Image.open(a3) as got:
        assert got.convert("RGBA").getpixel((0, 0)) == (1, 2, 3, 4)
    assert len(list(cache.iterdir())) == 3


def test_staging_in_parallel_matches_staging_in_order(tmp_path):
    from PIL import Image
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    art = {}
    for n in range(20):
        im = Image.new("RGB", (5, 5), ((n * 13) % 256, n, 255 - n))
        im.save(src_dir / f"c{n:02}.png")
        art[f"c{n:02}"] = src_dir / f"c{n:02}.png"
    cards = tmp_path / "cards"
    cards.mkdir()
    staged = pw.stage_cards(art, cards, tmp_path / "cache")
    assert [p.name for p in staged] == [f"c{n:02}.webp" for n in range(20)]


def test_the_dll_check_is_exact():
    blob = pw._blob("klee+kokomi+furina+varka")
    assert blob[0] == len("klee+kokomi+furina+varka")
    assert blob not in pw._blob("klee+kokomi+furina+varka+yae")


def test_a_dry_run_writes_nothing(tmp_path, capsys):
    dll, pck, art, image = _stand_ins(tmp_path)
    out = tmp_path / "out"
    rc = pw.main(["--variant", "public", "--version", "0.3.0", "--dry-run",
                  "--pck", str(pck), "--images-root", str(tmp_path / "noart"),
                  "--image", str(image), "--out", str(out)])
    assert rc == 0
    assert not out.exists()
    text = capsys.readouterr().out
    assert "content/klee/klee.dll" in text and "content/klee/klee.pck" in text
    assert "dry run" in text


def test_the_workspace_is_ignored():
    assert ".workshop/" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()


# ------------------------------------------------- opt-in run stats ---

URL = "https://gits-telemetry.example.workers.dev"
ROUTE = URL + "/v1/run"


@pytest.mark.parametrize("name", ["public", "beta"])
def test_no_endpoint_means_no_uploader_in_the_build(name, tmp_path):
    v = pw.VARIANTS[name]
    args = pw.build_args(v, "0.3.0", tmp_path)
    assert f"-p:GitsVariant={name}" in args
    assert not any("GitsTelemetryEndpoint" in a for a in args)
    assert pw.telemetry_endpoint(v, None) is None


def test_a_beta_endpoint_is_normalised_and_compiled_in(tmp_path):
    beta = pw.VARIANTS["beta"]
    for given in (URL, URL + "/", ROUTE):
        assert pw.telemetry_endpoint(beta, given) == ROUTE
    args = pw.build_args(beta, "0.3.0", tmp_path, ROUTE)
    assert f"-p:GitsTelemetryEndpoint={ROUTE}" in args


@pytest.mark.parametrize("bad", ["http://gits.example.dev", "gits.example.dev",
                                 "https://a b.dev", "https://x.dev/v1/run?x=1;y"])
def test_an_endpoint_must_be_plain_https(bad):
    with pytest.raises(SystemExit):
        pw.telemetry_endpoint(pw.VARIANTS["beta"], bad)


def test_the_public_variant_refuses_an_endpoint():
    with pytest.raises(SystemExit):
        pw.telemetry_endpoint(pw.VARIANTS["public"], URL)
    with pytest.raises(SystemExit):
        pw.main(["--variant", "public", "--version", "0.3.0", "--dry-run",
                 "--telemetry-endpoint", URL])


def test_the_privacy_paragraph_rides_only_with_the_uploader():
    beta = pw.VARIANTS["beta"]
    without = pw.workshop_json(beta, "0.3.0", "friends_only", None)["description"]
    with_ = pw.workshop_json(beta, "0.3.0", "friends_only", None, ROUTE)["description"]
    assert "Run data." not in without
    assert "Run data." in with_ and with_.startswith(without)
    for words in ("Upload data", "no Steam id", "IP address is not stored",
                  "deleted after a year", "random id", "on by default",
                  "Settings, Mod Configuration (BaseLib), Open Config, Teyvat Spire Roster"):
        assert words in with_, words
    # The paragraph names the setting by the label the mod actually shows.
    hook = (ROOT / "klee-mod" / "KleeCode" / "RunStats" / "RunStatsHook.cs").read_text(encoding="utf-8")
    label = "Share anonymous run stats with the Teyvat Spire developers"
    assert f'"{label}"' in hook and f'"{label}"' in with_
    # Default on (2026-10-18), in the code the page describes.
    assert "ShareAnonymousRunStats { get; set; } = true;" in hook
    # The paste-ready copy in the runbook matches what the packager writes.
    runbook = (ROOT / "docs" / "current" / "operations" / "workshop.md").read_text(encoding="utf-8")
    assert pw.PRIVACY_PARAGRAPH.strip() in runbook


def _dll_with(*strings: str, tmp_path: Path) -> Path:
    p = tmp_path / "klee.dll"
    p.write_bytes(b"MZ" + b"".join(pw._blob(s) for s in strings) + b"\0" * 16)
    return p


def test_the_dll_check_reads_the_endpoint_both_ways(tmp_path):
    beta = pw.VARIANTS["beta"]
    base = ("GitsWorkshopRelease", "GitsKits", "+".join(beta.kits), "GitsVariant", "beta")
    plain = _dll_with(*base, tmp_path=tmp_path)
    pw.check_dll(plain, beta)
    with pytest.raises(SystemExit):
        pw.check_dll(plain, beta, ROUTE)          # asked for, not in the dll
    (tmp_path / "e").mkdir()
    armed = _dll_with(*base, "GitsTelemetryEndpoint", ROUTE, tmp_path=tmp_path / "e")
    pw.check_dll(armed, beta, ROUTE)
    with pytest.raises(SystemExit):
        pw.check_dll(armed, beta)                 # in the dll, not asked for


def test_a_long_blob_takes_a_two_byte_length():
    s = "x" * 150
    b = pw._blob(s)
    assert b[:2] == bytes([0x80, 150]) and b[2:] == s.encode()


def test_the_upload_names_itself_and_hardcodes_no_endpoint():
    """Cloudflare's bot screen in front of the Worker returns 403 to the
    `Python-urllib` agent and 204 to curl or an empty agent (checked by hand
    against the deployed Worker, 2026-10-16). The client sends an explicit,
    honest User-Agent and treats any non-2xx as a dropped failure. Static
    only: nothing here touches the network."""
    hook = (ROOT / "klee-mod" / "KleeCode" / "RunStats" / "RunStatsHook.cs").read_text(encoding="utf-8")
    assert '$"TeyvatSpire/{WorkshopRelease.ModVersion} (+telemetry)"' in hook
    assert '"User-Agent", UserAgent' in hook
    assert "IsSuccessStatusCode" in hook
    assert "TimeSpan.FromSeconds(10)" in hook
    # The endpoint is a build option, read from assembly metadata; no URL in code.
    for src in (ROOT / "klee-mod" / "KleeCode" / "RunStats").glob("*.cs"):
        assert "workers.dev" not in src.read_text(encoding="utf-8"), src.name
    assert "workers.dev" not in (ROOT / "tools" / "package_workshop.py").read_text(encoding="utf-8")


def test_the_csproj_compiles_run_stats_only_with_an_endpoint():
    proj = (ROOT / "klee-mod" / "KleeCode" / "KleeCode.csproj").read_text(encoding="utf-8")
    assert "<ItemGroup Condition=\"'$(GitsTelemetryEndpoint)' == ''\">" in proj
    assert '<Compile Remove="RunStats/**" />' in proj
    assert "GITS_RUN_STATS" in proj
    assert "<_Parameter1>GitsVariant</_Parameter1>" in proj
    props = (ROOT / "klee-mod" / "Directory.Build.props").read_text(encoding="utf-8")
    assert "GitsTelemetryEndpoint" not in props
    mod = (ROOT / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(encoding="utf-8")
    assert mod.count("#if GITS_RUN_STATS") == 2
