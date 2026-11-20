"""Spec loading, grid/geometry resolution and page assembly."""
import copy
from pathlib import Path

import yaml

from . import components as C
from . import panel as P
from . import refstyle as R
from .expr import ExprError, evaluate
from .route import route
from .scene import Scene
from .style import make_theme, merge

NODE_TYPES = ("icon", "card", "glyph", "tile")
NODE_KEYS = {"id", "type", "parent", "icon", "title", "detail", "chips", "stand_in", "col", "x", "w",
             "align", "row", "h", "y", "fill", "stroke", "dash", "border", "icon_size", "title_size",
             "detail_size", "at", "icons", "frame", "label_w", "label_pos", "title_bold"}
GROUP_KEYS = {"id", "label", "sublabel", "icon", "kind", "parent", "box", "fit", "pad", "left", "top",
              "right", "bottom", "fill", "stroke", "dash", "label_color", "stand_in", "label_align"}
EDGE_KEYS = {"id", "from", "to", "kind", "label", "label_at", "label_anchor", "bridge", "arrow", "y", "x",
             "via", "points", "color", "dash"}
BADGE_KEYS = {"n", "at", "edge", "pos", "side", "offset", "kind"}


def load(path):
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("the spec must be a YAML mapping")
    return spec


def pages(spec):
    """Each entry under `pages` is deep-merged over the top-level keys (lists are replaced)."""
    base = {k: v for k, v in spec.items() if k != "pages"}
    if not spec.get("pages"):
        return [dict(base, id=base.get("id", "main"))]
    out = []
    for p in spec["pages"]:
        if not p.get("id"):
            raise ValueError("every entry under 'pages' needs an id")
        out.append(merge(copy.deepcopy(base), p))
    return out


def _check(kind, item, allowed):
    if not isinstance(item, dict) or "id" not in item:
        raise ValueError(f"{kind} without id: {item}")
    extra = set(item) - allowed
    if extra:
        raise ValueError(f"{kind} {item['id']}: unknown keys {sorted(extra)} (allowed: {sorted(allowed)})")


def _check_badge(b):
    if not isinstance(b, dict) or "n" not in b:
        raise ValueError(f"badge without n: {b}")
    extra = set(b) - BADGE_KEYS
    if extra:
        raise ValueError(f"badge {b['n']}: unknown keys {sorted(extra)} (allowed: {sorted(BADGE_KEYS)})")
    if ("at" in b) == ("edge" in b):
        raise ValueError(f"badge {b['n']}: give exactly one of at (fixed point) or edge (beside that edge)")
    if "at" in b and {"pos", "side", "offset"} & set(b):
        raise ValueError(f"badge {b['n']}: pos, side and offset only apply with edge")


class Geometry:
    """Lazy, memoized boxes so a spec can say `x: [fa.left, lakehouse.left - 20]`."""

    def __init__(self, page, th):
        c = page.get("canvas") or {}
        self.W, self.H = float(c.get("width", 1920)), float(c.get("height", 1080))
        g = page.get("grid") or {}
        self.cols, self.rows, self.guides = g.get("cols") or {}, g.get("rows") or {}, g.get("guides") or {}
        self.th = th
        self.nodes = {n["id"]: n for n in page.get("nodes") or []}
        self.groups = {x["id"]: x for x in page.get("groups") or []}
        self.fixed = {b["id"]: b["box"] for b in page.get("bands") or []}
        if page.get("panel"):
            self.fixed[page["panel"].get("id", "panel")] = page["panel"]["box"]
        names = [*(n.get("id") for n in page.get("nodes") or []),
                 *(x.get("id") for x in page.get("groups") or []), *self.fixed]
        dup = sorted({n for n in names if names.count(n) > 1})
        if dup:
            raise ValueError(f"duplicate ids: {dup}")
        self.cache, self.busy = {}, []

    def ev(self, v):
        return evaluate(v, self.lookup)

    def lookup(self, name, attr):
        if attr is None:
            if name in ("W", "H"):
                return self.W if name == "W" else self.H
            for table in (self.guides, self.rows):
                if name in table:
                    return self.ev(table[name])
            raise ExprError(f"unknown name '{name}' (guides, rows, W, H; boxes need id.attr)")
        if name in self.cols:
            x1, x2 = self.col(name)
            vals = {"left": x1, "right": x2, "cx": (x1 + x2) / 2, "w": x2 - x1}
        else:
            x1, y1, x2, y2 = self.box(name)
            vals = {"left": x1, "right": x2, "top": y1, "bottom": y2, "cx": (x1 + x2) / 2,
                    "cy": (y1 + y2) / 2, "w": x2 - x1, "h": y2 - y1, "foot": self.outer(name)[3]}
        if attr not in vals:
            raise ExprError(f"'{name}.{attr}': use one of {', '.join(vals)}")
        return vals[attr]

    def col(self, name):
        if name not in self.cols:
            raise ExprError(f"unknown column '{name}'")
        a, b = self.cols[name]
        return self.ev(a), self.ev(b)

    def box(self, lid):
        if lid in self.cache:
            return self.cache[lid]
        if lid in self.busy:
            raise ExprError("geometry cycle: " + " -> ".join([*self.busy, lid]))
        self.busy.append(lid)
        try:
            if lid in self.nodes:
                b = self._node(self.nodes[lid])
            elif lid in self.groups:
                b = self._group(self.groups[lid])
            elif lid in self.fixed:
                b = tuple(self.ev(v) for v in self.fixed[lid])
            else:
                raise ExprError(f"unknown element '{lid}'")
        finally:
            self.busy.pop()
        if b[2] <= b[0] or b[3] <= b[1]:
            raise ValueError(f"'{lid}' resolves to an empty box {tuple(round(v, 1) for v in b)}")
        self.cache[lid] = b
        return b

    def is_icon(self, lid):
        return lid in self.nodes and self.nodes[lid].get("type", self.th["node_type"]) == "icon"

    def outer(self, lid):
        """Icon nodes: icon plus label. Other elements: their box."""
        b = self.box(lid)
        return R.label_layout(self.th, self.nodes[lid], b)["outer"] if self.is_icon(lid) else b

    def _node(self, n):
        t = n.get("type", self.th["node_type"])
        if t not in NODE_TYPES:
            raise ValueError(f"node {n['id']}: unknown type '{t}' ({', '.join(NODE_TYPES)})")
        if t == "icon":
            if "at" in n:
                cx, cy = (self.ev(v) for v in n["at"])
            elif "col" in n and "row" in n:
                cx, cy = sum(self.col(n["col"])) / 2, self.ev(n["row"])
            else:
                raise ValueError(f"node {n['id']}: an icon node needs 'at: [cx, cy]' or 'col' + 'row'")
            return R.core_box(self.th, n, cx, cy)
        if "x" in n:
            x1, x2 = (self.ev(v) for v in n["x"])
        elif "col" in n:
            x1, x2 = self.col(n["col"])
            if "w" in n:
                w, a = self.ev(n["w"]), n.get("align", "left")
                if a not in ("left", "center", "right"):
                    raise ValueError(f"node {n['id']}: align must be left, center or right")
                x1 = {"left": x1, "center": (x1 + x2 - w) / 2, "right": x2 - w}[a]
                x2 = x1 + w
        else:
            raise ValueError(f"node {n['id']}: needs 'col' or 'x'")
        if "y" in n:
            y1, y2 = (self.ev(v) for v in n["y"])
        elif "row" in n:
            cy, h = self.ev(n["row"]), self.ev(n.get("h", self.th[t]["h"]))
            y1, y2 = cy - h / 2, cy + h / 2
        else:
            raise ValueError(f"node {n['id']}: needs 'row' or 'y'")
        return (x1, y1, x2, y2)

    def _group(self, g):
        if "box" in g:
            b = [self.ev(v) for v in g["box"]]
        elif g.get("fit"):
            pad = g.get("pad", self.th["group"]["pad"])
            pad = [pad] * 4 if isinstance(pad, (int, float)) else pad
            bs = [self.outer(i) for i in g["fit"]]
            b = [min(x[0] for x in bs) - pad[0], min(x[1] for x in bs) - pad[1],
                 max(x[2] for x in bs) + pad[2], max(x[3] for x in bs) + pad[3]]
        else:
            raise ValueError(f"group {g['id']}: needs 'box' or 'fit'")
        for i, k in enumerate(("left", "top", "right", "bottom")):
            if k in g:
                b[i] = self.ev(g[k])
        return tuple(b)


def build_page(page, lib):
    th = make_theme(page.get("theme"), page.get("style"))
    ref = th["style"] == "reference"
    geo = Geometry(page, th)
    sc = Scene(page["id"], page.get("page_name") or page.get("title") or page["id"], geo.W, geo.H, th,
               page.get("title", ""), page.get("description", ""))
    for g in geo.groups.values():
        _check("group", g, GROUP_KEYS)
    for n in geo.nodes.values():
        _check("node", n, NODE_KEYS)
    right = geo.box(page["panel"].get("id", "panel"))[0] - 40 if page.get("panel") else geo.W - 40
    C.paper(sc, th)
    if ref:
        R.header(sc, th, page, right)
    else:
        C.header(sc, th, page)

    def depth(gid, seen=()):
        p = geo.groups[gid].get("parent")
        if not p:
            return 0
        if p not in geo.groups or p in seen:
            raise ValueError(f"group {gid}: parent '{p}' is unknown or cyclic")
        return 1 + depth(p, (*seen, gid))

    for g in sorted(geo.groups.values(), key=lambda g: depth(g["id"])):
        box = geo.box(g["id"])
        C.register(sc, g["id"], box, "group", g.get("parent"))
        (R.group if ref else C.group)(sc, th, g, box, lib)
    for n in geo.nodes.values():
        if n.get("parent") and n["parent"] not in geo.groups:
            raise ValueError(f"node {n['id']}: unknown parent group '{n['parent']}'")
        box = geo.box(n["id"])
        C.register(sc, n["id"], box, "node", n.get("parent"))
        C.node(sc, th, n, box, lib)
    # Bands come before edges so an edge can end at a band or at one of its items.
    for b in page.get("bands") or []:
        P.band(sc, th, b, geo.ev, lib)
    used = []
    for e in page.get("edges") or []:
        e = dict(e)
        e.setdefault("id", f"{e.get('from')}-{e.get('to')}")
        _check("edge", e, EDGE_KEYS)
        route(sc, th, e, geo.ev)
        if e.get("kind", "request") not in used:
            used.append(e.get("kind", "request"))
    P.texts(sc, th, page.get("texts"), geo.ev)
    if page.get("panel"):
        P.sidebar(sc, th, page["panel"], geo.ev, used)
    if ref:
        R.footer(sc, th, page, right)
    else:
        C.footer(sc, th, page)
    # Badges go last: they draw on top and their placement sees every other element.
    for b in page.get("badges") or []:
        _check_badge(b)
    P.badges(sc, th, page.get("badges"), geo.ev)
    return sc
