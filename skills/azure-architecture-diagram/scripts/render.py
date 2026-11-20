#!/usr/bin/env python3
"""Render an architecture spec (YAML) to draw.io, SVG and PNG, then validate the layout.

Usage: python render.py SPEC.yaml --out DIR [--icons DIR] [--no-png] [--scale 1.25] [--strict]
Exit codes: 0 clean, 1 layout errors (or warnings with --strict), 2 spec or icon errors.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azdiagram import build, drawio, svgout, validate  # noqa: E402
from azdiagram.icons import IconError, IconLibrary  # noqa: E402


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Render and validate an Azure architecture diagram spec.")
    ap.add_argument("spec")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--icons", help="icon cache directory (default: AZDIAGRAM_ICON_CACHE or user cache)")
    ap.add_argument("--no-png", action="store_true", help="skip browser rendering (no PNG, PIL metrics)")
    ap.add_argument("--scale", type=float, default=1.25, help="PNG device scale factor")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--debug", action="store_true", help="show the traceback of spec errors")
    a = ap.parse_args(argv)

    lib = IconLibrary(a.icons)
    try:
        spec = build.load(a.spec)
        name = spec.get("name") or Path(a.spec).stem
        scenes = [build.build_page(p, lib) for p in build.pages(spec)]
    except (IconError, ValueError, KeyError, TypeError) as exc:
        if a.debug:
            raise
        print(f"spec error: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    multi = len(scenes) > 1
    jobs = []
    for sc in scenes:
        stem = f"{name}-{sc.page_id}" if multi else name
        svgout.write(sc, lib, out / f"{stem}.svg")
        jobs.append((out / f"{stem}.svg", out / f"{stem}.png", sc.width, sc.height))
    drawio.write(scenes, lib, out / f"{name}.drawio")
    measured = {}
    if not a.no_png:
        from azdiagram import png
        measured = png.render(jobs, a.scale)

    report, errors, warnings = {}, 0, 0
    for sc, job in zip(scenes, jobs):
        boxes = {b["id"]: b for b in measured.get(str(job[0]), [])}
        found = validate.validate(sc, boxes or None)
        report[sc.page_id] = found
        e = sum(f["level"] == "error" for f in found)
        w = sum(f["level"] == "warning" for f in found)
        errors, warnings = errors + e, warnings + w
        print(f"page {sc.page_id}: {e} errors, {w} warnings")
        for f in found:
            if f["level"] != "info":
                print(f"  [{f['level']}] {f['code']}: {f['message']}")
    (out / f"{name}-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
    (out / "icon-provenance.json").write_text(json.dumps(lib.provenance(), ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    files = sorted(p.name for p in out.iterdir() if p.stem.startswith(name) or p.name == "icon-provenance.json")
    print(f"wrote {len(files)} files to {out}: {', '.join(files)}")
    print(f"icons: {len(lib.used)} ({sum(r['stand_in'] for r in lib.used.values())} stand-ins)")
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
