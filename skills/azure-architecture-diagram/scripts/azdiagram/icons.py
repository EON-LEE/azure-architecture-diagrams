"""Official icon packs: lookup by `pack:name`, search, and provenance records."""
import hashlib
import io
import json
import os
import re
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

PACKS_FILE = Path(__file__).resolve().parent.parent / "packs.json"


class IconError(LookupError):
    pass


def norm(s):
    return re.sub(r"[^0-9a-z\uac00-\ud7a3]", "", s.lower())


def load_packs():
    return json.loads(PACKS_FILE.read_text(encoding="utf-8"))["packs"]


def cache_dir(override=None):
    if override:
        return Path(override)
    if os.environ.get("AZDIAGRAM_ICON_CACHE"):
        return Path(os.environ["AZDIAGRAM_ICON_CACHE"])
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".cache")
    return Path(base) / "azure-architecture-diagram" / "icons"


class IconLibrary:
    def __init__(self, cache=None):
        self.packs = load_packs()
        self.cache = cache_dir(cache)
        self._loaded = {}
        self._data = {}
        self.used = {}

    def _load(self, pack):
        if pack in self._loaded:
            return self._loaded[pack]
        if pack not in self.packs:
            raise IconError(f"unknown icon pack '{pack}'. Packs: {', '.join(self.packs)}")
        spec = self.packs[pack]
        path = self.cache / spec["file"]
        if not path.exists():
            raise IconError(f"icon pack '{pack}' is missing at {path}. "
                            f"Run: python scripts/icon_tool.py fetch --packs {pack}")
        blob = path.read_bytes()
        root = spec.get("root", "")
        files = {}
        if spec["format"] == "zip":
            zf = zipfile.ZipFile(io.BytesIO(blob))
            for name in zf.namelist():
                if name.startswith(root) and name.lower().endswith(".svg"):
                    files[name[len(root):]] = (lambda n=name: zf.read(n))
        else:
            tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz")
            for m in tf.getmembers():
                if m.isfile() and m.name.startswith(root) and m.name.lower().endswith(".svg"):
                    files[m.name[len(root):]] = (lambda m=m: tf.extractfile(m).read())
        strip = [re.compile(p, re.I) for p in spec.get("strip", [])]
        entries, raw = [], {}
        for rel in sorted(files):
            folder, _, base = rel.rpartition("/")
            stem = base[:-4]
            raw[rel] = norm(stem)
            for rx in strip:
                stem = rx.sub("", stem)
            entries.append((rel, folder, stem.strip(), norm(stem)))
        info = {"sha256": hashlib.sha256(blob).hexdigest(), "files": files, "entries": entries,
                "raw": raw}
        self._loaded[pack] = info
        return info

    def lookup(self, key):
        """Resolve `pack:name` or `pack:folder/name` to (pack, relative member path)."""
        pack, sep, name = key.partition(":")
        if not sep or not name.strip():
            raise IconError(f"icon key '{key}' must look like 'pack:name'")
        info, spec = self._load(pack), self.packs[pack]
        folder, _, base = name.strip().rpartition("/")

        def match(n):
            return [e for e in info["entries"]
                    if n in (e[3], info["raw"][e[0]])
                    and (not folder or e[1].lower() == folder.lower())]

        cands = match(norm(base))
        for suffix in spec.get("suffixes", []):
            if cands:
                break
            cands = match(norm(base + suffix))
        if len(cands) > 1 and not folder and spec.get("default_dir"):
            cands = [e for e in cands if e[1].lower() == spec["default_dir"].lower()] or cands
        if not cands:
            hint = ", ".join(self.search(base, pack, 6)) or "none"
            raise IconError(f"icon '{key}' not found. Similar: {hint}")
        if len(cands) > 1:
            raise IconError(f"icon '{key}' is ambiguous: " + ", ".join(self._keys(pack, cands)[:8]))
        return pack, cands[0][0]

    @staticmethod
    def _keys(pack, entries):
        """Keys for `entries`. Files that share a folder and name use the original file name."""
        names = Counter((e[1].lower(), e[3]) for e in entries)
        return [f"{pack}:{e[1] + '/' if e[1] else ''}"
                f"{e[2] if names[(e[1].lower(), e[3])] == 1 else e[0].rpartition('/')[2][:-4]}"
                for e in entries]

    def get(self, key, owner=None, stand_in=False):
        """SVG bytes (BOM stripped) for `key`. Records provenance for every use."""
        if key not in self._data:
            pack, rel = self.lookup(key)
            info, spec = self._load(pack), self.packs[pack]
            data = info["files"][rel]()
            if data.startswith(b"\xef\xbb\xbf"):
                data = data[3:]
            self._data[key] = data
            self.used[key] = {
                "key": key, "pack": pack, "pack_title": spec["title"],
                "source_page": spec["source_page"], "download": spec["url"], "terms": spec["terms"],
                "archive_sha256": info["sha256"], "member": spec.get("root", "") + rel,
                "svg_sha256": hashlib.sha256(data).hexdigest(), "stand_in": False, "used_by": []}
        rec = self.used[key]
        rec["stand_in"] = rec["stand_in"] or bool(stand_in)
        if owner and owner not in rec["used_by"]:
            rec["used_by"].append(owner)
        return self._data[key]

    def is_item(self, key):
        """True for Fabric item icons (most draw the glyph on a rounded tile, so it reads smaller)."""
        return Path(self.lookup(key)[1]).stem.lower().endswith("_item")

    def search(self, query, pack=None, limit=30):
        terms = [norm(t) for t in query.split() if norm(t)]
        out = []
        for p in ([pack] if pack else list(self.packs)):
            try:
                info = self._load(p)
            except IconError:
                continue
            out += self._keys(p, [e for e in info["entries"]
                                  if all(t in e[3] or t in norm(e[1]) for t in terms)])
        return out[:limit]

    def provenance(self):
        return {"generator": "azure-architecture-diagram skill",
                "icons": sorted(self.used.values(), key=lambda r: r["key"])}
