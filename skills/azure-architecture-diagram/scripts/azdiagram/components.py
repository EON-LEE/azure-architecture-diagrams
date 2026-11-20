"""Visual components. Each one emits renderer-neutral primitives into a Scene."""
from . import textfit
from .scene import Badge, Image, Rect, Swatch, Text
from .style import color


def text(sc, th, x, y, s, size, col="ink", bold=False, width=None, anchor="start",
         parent="1", owner=None, role="text", halo=False):
    s = " · ".join(map(str, s)) if isinstance(s, (list, tuple)) else str(s)
    limited = width is not None
    if limited:
        size, ok = textfit.fit(s, size, bold, width, th["min_font"])
    else:
        ok, width = True, textfit.width(s, size, bold)
    return sc.add(Text(sc.uid("t"), x, y, s, size, color(th, col), bold, anchor, width,
                       parent, role, owner, halo, ok, limited))


def icon(sc, lib, key, x, y, size, parent, owner, stand_in=False):
    lib.get(key, owner=owner, stand_in=stand_in)  # resolves now so a bad key fails the build
    return sc.add(Image(sc.uid("i"), x, y, size, key, parent, owner))


def register(sc, lid, box, kind, parent=None):
    sc.boxes[lid], sc.kind[lid], sc.parent[lid] = box, kind, parent


def backdrop(sc, th, x, y):
    """Fill behind (x, y): the deepest filled group or panel, else the paper."""
    best, depth = color(th, "paper"), -1
    for lid, fill in sc.fills.items():
        b = sc.boxes.get(lid)
        if b and b[0] <= x <= b[2] and b[1] <= y <= b[3] and len(sc.ancestors(lid)) > depth:
            best, depth = fill, len(sc.ancestors(lid))
    return best


def paper(sc, th):
    sc.add(Rect("paper", 0, 0, sc.width, sc.height, color(th, "paper"), role="paper"))


def header(sc, th, page):
    w = sc.width
    if page.get("kicker"):
        sc.add(Rect(sc.uid("accent"), 40, 32, 34, 5, color(th, "accent"), role="decor"))
        text(sc, th, 86, 40, page["kicker"], 14, "accent", True, 700)
    if page.get("title"):
        text(sc, th, 40, 98, page["title"], 40, "ink", True, w - 440)
    if page.get("subtitle"):
        text(sc, th, 42, 136, page["subtitle"], 18, "muted", False, w - 84)
    if page.get("tag"):
        text(sc, th, w - 45, 44, page["tag"], 15, "muted", True, 360, "end")
    if page.get("date"):
        text(sc, th, w - 45, 72, page["date"], 14, "muted", False, 360, "end")


def footer(sc, th, page):
    f = page.get("footer") or {}
    if f.get("left"):
        text(sc, th, 40, sc.height - 32, f["left"], 12.5, "muted", False, sc.width - 340)
    if f.get("right"):
        text(sc, th, sc.width - 45, sc.height - 32, f["right"], 12.5, "muted", True, 260, "end")


def group(sc, th, g, box, lib):
    kind = g.get("kind", "plain")
    gk = th["group_kinds"].get(kind)
    if gk is None:
        raise ValueError(f"group {g['id']}: unknown kind '{kind}' (see theme.group_kinds)")
    gs, (x1, y1, x2, y2) = th["group"], box
    gid = g["id"]
    dash = gs["dash"] if g.get("dash", gk["dash"]) else None
    fill = color(th, g.get("fill", gk["fill"]))
    sc.add(Rect(gid, x1, y1, x2 - x1, y2 - y1, fill,
                color(th, g.get("stroke", gk["stroke"])), 1.5, gs["radius"], dash,
                g.get("parent") or "1", True, "group", gid))
    if fill != "none":
        sc.fills[gid] = fill
    tx = x1 + 12
    if g.get("icon"):
        icon(sc, lib, g["icon"], x1 + 10, y1 + 8, gs["icon"], gid, gid, g.get("stand_in", False))
        tx = x1 + 16 + gs["icon"]
    right = x2 - 12
    if g.get("sublabel"):
        t = text(sc, th, right, y1 + 24, g["sublabel"], gs["sublabel"], "muted", False,
                 (x2 - x1) * 0.55, "end", gid, gid)
        right -= textfit.width(t.text, t.size) + 16
    if g.get("label"):
        text(sc, th, tx, y1 + 24, g["label"], gs["label"], g.get("label_color", gk["label"]), True,
             right - tx, "start", gid, gid)


def card(sc, th, n, box, lib):
    cs, (x1, y1, x2, y2) = th["card"], box
    nid, w, h = n["id"], x2 - x1, y2 - y1
    dash = th["group"]["dash"] if n.get("dash") else None
    sc.add(Rect(nid, x1, y1, w, h, color(th, n.get("fill", cs["fill"])),
                color(th, n.get("stroke", cs["stroke"])), 1.5, cs["radius"], dash,
                n.get("parent") or "1", True, "node", nid))
    chips = n.get("chips") or []
    top = y1 if chips else y1 + (h - cs["h"]) / 2
    tx = x1 + 14
    if n.get("icon"):
        isz = cs["icon"]
        icon(sc, lib, n["icon"], x1 + 10, top + (cs["h"] - isz) / 2, isz, nid, nid,
             n.get("stand_in", False))
        tx = x1 + 20 + isz
    tw = x2 - 8 - tx
    if n.get("detail"):
        text(sc, th, tx, top + 27, n["title"], cs["title"], "ink", True, tw, "start", nid, nid)
        text(sc, th, tx, top + 47, n["detail"], cs["detail"], "muted", False, tw, "start", nid, nid)
    else:
        text(sc, th, tx, top + 36, n["title"], cs["title"], "ink", True, tw, "start", nid, nid)
    if chips:
        ch, a, b = cs["chip_h"], top + cs["h"], y2 - 8
        gap = (b - a - len(chips) * ch) / len(chips)
        if gap < 4:
            raise ValueError(f"node {nid}: {len(chips)} chips need more card height")
        for i, chip in enumerate(chips):
            cy = a + gap / 2 + i * (ch + gap)
            sc.add(Rect(sc.uid("chip"), x1 + 12, cy, w - 24, ch, color(th, cs["chip_fill"]),
                        color(th, cs["chip_stroke"]), 1, 6, None, nid, False, "chip", nid))
            text(sc, th, x1 + 24, cy + ch / 2 + 4.5, chip, 12.5, "ink", False, w - 48, "start", nid, nid)


def glyph(sc, th, n, box, lib):
    gs, (x1, y1, x2, y2) = th["glyph"], box
    nid, cy = n["id"], (y1 + y2) / 2
    sc.add(Rect(nid, x1, y1, x2 - x1, y2 - y1, parent=n.get("parent") or "1", container=True,
                role="node", owner=nid))
    tx = x1
    if n.get("icon"):
        isz = n.get("icon_size", gs["icon"])
        icon(sc, lib, n["icon"], x1, cy - isz / 2, isz, nid, nid, n.get("stand_in", False))
        tx = x1 + isz + 10
    ts, ds = n.get("title_size", gs["title"]), n.get("detail_size", gs["detail"])
    if n.get("detail"):
        text(sc, th, tx, cy - 3, n["title"], ts, "ink", True, x2 - tx, "start", nid, nid)
        text(sc, th, tx, cy + 16, n["detail"], ds, "muted", False, x2 - tx, "start", nid, nid)
    else:
        text(sc, th, tx, cy + ts * 0.36, n["title"], ts, "ink", True, x2 - tx, "start", nid, nid)


def tile(sc, th, n, box, lib):
    ts, (x1, y1, x2, y2) = th["tile"], box
    nid, cx = n["id"], (x1 + x2) / 2
    border = n.get("border", False)
    sc.add(Rect(nid, x1, y1, x2 - x1, y2 - y1, "#FFFFFF" if border else "none",
                color(th, "line") if border else "none", 1.5, 8, None, n.get("parent") or "1", True,
                "node", nid))
    isz = n.get("icon_size", ts["icon"])
    if n.get("icon"):
        icon(sc, lib, n["icon"], cx - isz / 2, y1 + 6, isz, nid, nid, n.get("stand_in", False))
    text(sc, th, cx, y1 + isz + 28, n["title"], ts["title"], "ink", True, x2 - x1 - 8, "middle", nid, nid)
    if n.get("detail"):
        text(sc, th, cx, y1 + isz + 46, n["detail"], ts["detail"], "muted", False, x2 - x1 - 8,
             "middle", nid, nid)


NODE_TYPES = {"card": card, "glyph": glyph, "tile": tile}


def node(sc, th, n, box, lib):
    t = n.get("type", th["node_type"])
    if t == "icon":
        from .refstyle import icon_node
        return icon_node(sc, th, n, box, lib)
    fn = NODE_TYPES.get(t)
    if fn is None:
        raise ValueError(f"node {n['id']}: unknown type '{t}' (icon, card, glyph, tile)")
    fn(sc, th, n, box, lib)
