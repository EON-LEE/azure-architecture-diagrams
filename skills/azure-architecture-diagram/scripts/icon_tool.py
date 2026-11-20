#!/usr/bin/env python3
"""Fetch, import and search the official Microsoft icon packs that render.py uses.

  python icon_tool.py packs                      # cache status
  python icon_tool.py fetch [--packs azure,fabric] [--force]
  python icon_tool.py import PACK PATH           # use an archive you downloaded yourself
  python icon_tool.py search "api management" [--pack azure]
"""
import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azdiagram.icons import IconLibrary, cache_dir, load_packs  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (azure-architecture-diagram skill)"}


def valid(path, pack):
    """True when `path` is an archive of the expected format that holds SVGs under the pack root."""
    root = pack.get("root", "")
    try:
        if pack["format"] == "zip":
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
        else:
            with tarfile.open(path, "r:gz") as t:
                names = t.getnames()
    except (OSError, zipfile.BadZipFile, tarfile.TarError):
        return False
    return any(n.startswith(root) and n.lower().endswith(".svg") for n in names)


def download(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r, \
            open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def npm_pack(spec, dest):
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        raise RuntimeError("npm not found")
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([npm, "pack", spec, "--silent"], cwd=tmp, capture_output=True, text=True,
                           timeout=300)
        if r.returncode:
            raise RuntimeError((r.stderr or r.stdout).strip()[:300])
        shutil.move(str(next(Path(tmp).glob("*.tgz"))), dest)


def fetch(names, force, cache):
    packs, ok = load_packs(), True
    cache.mkdir(parents=True, exist_ok=True)
    for name in names:
        p = packs[name]
        dest = cache / p["file"]
        if dest.exists() and not force and valid(dest, p):
            print(f"{name}: cached ({dest})")
            continue
        part, errors = dest.with_name(dest.name + ".part"), []
        sources = ([("npm", p["npm"])] if p.get("npm") else []) + [("url", p["url"])]
        for how, src in sources:
            try:
                (npm_pack if how == "npm" else download)(src, part)
                if not valid(part, p):
                    raise RuntimeError("the download is not the expected icon archive")
                part.replace(dest)
                print(f"{name}: downloaded via {how} ({dest.stat().st_size // 1024} KB)")
                break
            except Exception as exc:  # report and try the next source
                errors.append(f"{how}: {exc}")
        else:
            ok = False
            part.unlink(missing_ok=True)
            print(f"{name}: FAILED ({'; '.join(errors)}). Download it from {p['source_page']} and run: "
                  f"icon_tool.py import {name} <file>", file=sys.stderr)
    return ok


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Manage the official icon packs.")
    ap.add_argument("--icons", help="icon cache directory")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("packs")
    f = sub.add_parser("fetch")
    f.add_argument("--packs", help="comma-separated pack names (default: all)")
    f.add_argument("--force", action="store_true")
    i = sub.add_parser("import")
    i.add_argument("pack")
    i.add_argument("path")
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--pack")
    s.add_argument("--limit", type=int, default=40)
    a = ap.parse_args(argv)
    cache, packs = cache_dir(a.icons), load_packs()

    if a.cmd == "packs":
        print(f"cache: {cache}")
        for name, p in packs.items():
            f = cache / p["file"]
            print(f"  {name:14} {f'{f.stat().st_size // 1024} KB' if f.exists() else 'missing':>10}  {p['title']}")
        return 0
    if a.cmd == "fetch":
        names = a.packs.split(",") if a.packs else list(packs)
        unknown = [n for n in names if n not in packs]
        if unknown:
            print(f"unknown packs: {unknown}. Packs: {', '.join(packs)}", file=sys.stderr)
            return 2
        return 0 if fetch(names, a.force, cache) else 1
    if a.cmd == "import":
        if a.pack not in packs:
            print(f"unknown pack '{a.pack}'. Packs: {', '.join(packs)}", file=sys.stderr)
            return 2
        if not valid(a.path, packs[a.pack]):
            print(f"{a.path} is not the {a.pack} icon archive ({packs[a.pack]['format']} with SVGs under "
                  f"'{packs[a.pack].get('root', '')}')", file=sys.stderr)
            return 1
        cache.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(a.path, cache / packs[a.pack]["file"])
        print(f"{a.pack}: imported to {cache / packs[a.pack]['file']}")
        return 0
    hits = IconLibrary(a.icons).search(a.query, a.pack, a.limit)
    print("\n".join(hits) if hits else "no match (run 'icon_tool.py packs' to check the cache)")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
