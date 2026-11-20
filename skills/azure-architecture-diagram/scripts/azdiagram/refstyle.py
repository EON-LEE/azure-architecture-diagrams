"""Reference style: icon nodes with labels, corner-tile groups, header with a rule, footer."""
from . import textfit
from .components import icon, register, text
from .scene import Rect, Text
from .style import color

LABEL_POS = ("below", "above", "right", "left")


def _keys(n):
    return list(n.get("icons") or ([n["icon"]] if n.get("icon") else []))


def core_box(th, n, cx, cy):
    """Box of the icon (or the framed icon cluster) centered on (cx, cy)."""
    s = th["icon"]
    isz = n.get("icon_size", s["size"])
    k = max(len(_keys(n)), 1)
    fp = s["frame_pad"] if n.get("frame") else 0
    w, h = k * isz + (k - 1) * s["cluster_gap"] + 2 * fp, isz + 2 * fp
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _para(v):
    v = " · ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v or "")
    return [p for p in v.split("\n") if p.strip()]


def label_layout(th, n, core):
    """Label lines plus the attach box (where edges start/end) and the outer box (icon + label)."""
    s = th["icon"]
    pos = n.get("label_pos", "below")
    if pos not in LABEL_POS:
        raise ValueError(f"node {n['id']}: label_pos must be one of {', '.join(LABEL_POS)}")
    lw, tb = n.get("label_w", s["label_w"]), n.get("title_bold", s["title_bold"])
    ts, ds = n.get("title_size", s["title"]), n.get("detail_size", s["detail"])

    def title_lines(size):
        return [ln for p in _para(n.get("title")) for ln in textfit.wrap(p, size, tb, lw)]

    lines = title_lines(ts)
    while len(lines) > s["max_lines"] and ts > th["min_font"]:
        ts -= 0.5
        lines = title_lines(ts)
    rows = [(ln, ts, "ink", tb, s["line_h"] * ts / s["title"]) for ln in lines]
    rows += [(ln, ds, "muted", False, s["detail_line_h"]) for p in _para(n.get("detail"))
             for ln in textfit.wrap(p, ds, False, lw)]
    x1, y1, x2, y2 = core
    if not rows:
        return {"lines": [], "attach": core, "outer": core}
    hh = sum(r[4] for r in rows)
    widest = max(textfit.width(r[0], r[1], r[3]) for r in rows)
    cx, cy, gap = (x1 + x2) / 2, (y1 + y2) / 2, s["gap"]
    top, lx, anchor = {"below": (y2 + gap, cx, "middle"), "above": (y1 - gap - hh, cx, "middle"),
                       "right": (cy - hh / 2, x2 + gap, "start"),
                       "left": (cy - hh / 2, x1 - gap, "end")}[pos]
    out, y = [], top
    for t, size, col, bold, lh in rows:
        out.append((t, size, col, bold, lx, y + lh * 0.78, anchor, lw))
        y += lh
    bx1 = {"middle": cx - widest / 2, "start": lx, "end": lx - widest}[anchor]
    bx2, by1, by2 = bx1 + widest, top, top + hh
    attach = {"below": (x1, y1, x2, by2 + 4), "above": (x1, by1 - 4, x2, y2),
              "right": (x1, min(y1, by1), bx2 + 4, max(y2, by2)),
              "left": (bx1 - 4, min(y1, by1), x2, max(y2, by2))}[pos]
    outer = (min(x1, bx1), min(y1, by1), max(x2, bx2), max(y2, by2))
    return {"lines": out, "attach": attach, "outer": outer}


def icon_node(sc, th, n, core, lib):
    """Icon (or framed cluster) with its label. Edges attach to the icon sides; a line leaving
    toward the label side starts below the label."""
    nid, s = n["id"], th["icon"]
    lay = label_layout(th, n, core)
    ax1, ay1, ax2, ay2 = lay["attach"]
    sc.add(Rect(nid, ax1, ay1, ax2 - ax1, ay2 - ay1, parent=n.get("parent") or "1", container=True,
                role="node", owner=nid))
    register(sc, nid, lay["attach"], "node", n.get("parent"))
    sc.core[nid] = core
    isz, frame = n.get("icon_size", s["size"]), n.get("frame")
    fp = s["frame_pad"] if frame else 0
    if frame:
        if frame not in ("dashed", "solid"):
            raise ValueError(f"node {nid}: frame must be dashed or solid")
        sc.add(Rect(sc.uid("frame"), core[0], core[1], core[2] - core[0], core[3] - core[1], "none",
                    color(th, n.get("stroke", "gray")), 1.4, 0, "6 4" if frame == "dashed" else None, nid,
                    False, "frame", nid))
    x, k = core[0] + fp, s.get("item_scale", 1)
    for key in _keys(n):
        # Fabric item icons draw a glyph inside a light document tile; enlarge the whole tile a little
        # (never crop or recolor it) so its visual weight matches the full-bleed Azure icons.
        z = k if k != 1 and lib.is_item(key) else 1
        d = isz * (z - 1) / 2
        icon(sc, lib, key, x - d, core[1] + fp - d, isz * z, nid, nid, n.get("stand_in", False))
        x += isz + s["cluster_gap"]
    for t, size, col, bold, lx, ly, anchor, lw in lay["lines"]:
        text(sc, th, lx, ly, t, size, col, bold, lw, anchor, nid, nid)


def group(sc, th, g, box, lib):
    """Thin square frame; an icon tile flush in the top-left corner with the label beside it."""
    kind = g.get("kind", "plain")
    gk = th["group_kinds"].get(kind)
    if gk is None:
        raise ValueError(f"group {g['id']}: unknown kind '{kind}' (see theme.group_kinds)")
    gs, (x1, y1, x2, y2), gid = th["group"], box, g["id"]
    stroke = color(th, g.get("stroke", gk["stroke"]))
    fill = color(th, g.get("fill", gk["fill"] if gs.get("tint", True) else "none"))
    sc.add(Rect(gid, x1, y1, x2 - x1, y2 - y1, fill, stroke, gs["sw"],
                gs["radius"], gs["dash"] if g.get("dash", gk["dash"]) else None, g.get("parent") or "1",
                True, "group", gid))
    if fill != "none":
        sc.fills[gid] = fill
    align, t = g.get("label_align", gk.get("label_align", "left")), gs["tile"]
    lcol = g.get("label_color", gk["label"])
    if align == "center":
        if g.get("label"):
            text(sc, th, (x1 + x2) / 2, y1 + 9 + gs["label"], g["label"], gs["label"], lcol, gs["label_bold"],
                 x2 - x1 - 24, "middle", gid, gid)
        return
    tx, base = x1 + 12, y1 + 8 + gs["label"]
    if g.get("icon"):
        sc.add(Rect(sc.uid("tile"), x1, y1, t, t, color(th, gk.get("tile", "#FFFFFF")), stroke, gs["sw"], 0,
                    None, gid, False, "tile", gid))
        icon(sc, lib, g["icon"], x1 + (t - gs["icon"]) / 2, y1 + (t - gs["icon"]) / 2, gs["icon"], gid, gid,
             g.get("stand_in", False))
        tx, base = x1 + t + 12, y1 + t / 2 + gs["label"] * 0.36
    if g.get("label"):
        lb = text(sc, th, tx, base, g["label"], gs["label"], lcol, gs["label_bold"], x2 - 10 - tx, "start",
                  gid, gid)
        nx = tx + textfit.width(lb.text, lb.size, gs["label_bold"]) + 10
        if g.get("sublabel") and x2 - 10 - nx > 40:
            text(sc, th, nx, base, g["sublabel"], gs["sublabel"], "muted", False, x2 - 10 - nx, "start", gid, gid)


def rich(sc, th, x, y, runs, size, col, width, parent="1", owner=None):
    """One line of mixed-weight text (from textfit.wrap_rich)."""
    plain = "".join(t for t, _ in runs)
    ok = textfit.runs_width(runs, size) <= width + 0.5
    return sc.add(Text(sc.uid("t"), x, y, plain, size, color(th, col), False, "start", width, parent, "text",
                       owner, False, ok, True, runs))


def header(sc, th, page, right):
    """Bold title (up to max_lines), description paragraph and a dark rule across the diagram area."""
    hs, x, w = th["header"], 40, right - 40
    y = hs["top"]
    last = y - hs["title"]
    if page.get("title"):
        size = hs["title"]
        lines = textfit.wrap(page["title"], size, True, w)
        while len(lines) > hs["max_lines"] and size > 22:
            size -= 1
            lines = textfit.wrap(page["title"], size, True, w)
        lh = hs["title_line_h"] * size / hs["title"]
        for j, ln in enumerate(lines):
            last = y + j * lh
            text(sc, th, x, last, ln, size, "ink", True, w, owner="header")
    if page.get("description"):
        # Long lines are hard to read; cap the paragraph at desc_max_em characters' worth of width.
        dw = min(w, hs["desc_max_em"] * hs["desc"]) if hs.get("desc_max_em") else w
        for j, runs in enumerate(textfit.wrap_rich(page["description"], hs["desc"], dw)):
            dy = last + (hs["desc_gap"] if j == 0 else hs["desc_line_h"])
            rich(sc, th, x, dy, runs, hs["desc"], "ink", dw, owner="header")
            last = dy
    rule = last + hs["rule_gap"]
    sc.add(Rect(sc.uid("rule"), x, rule, w, hs["rule"], color(th, hs["rule_color"]), role="decor",
                owner="header"))
    register(sc, "header", (x, hs["top"] - hs["title"], right, rule + hs["rule"]), "panel")
    sc.no_edges.add("header")
    return rule + hs["rule"]


def footer(sc, th, page, right):
    """Small gray source lines bottom-left; an accent label centered under the diagram."""
    f, fs = page.get("footer") or {}, th["footer"]
    base, cx, half = sc.height - 26, (40 + right) / 2, 0
    if f.get("center"):
        t = text(sc, th, cx, base, f["center"], fs["center"], "accent", True, right - 40, "middle", owner="footer")
        half = textfit.width(t.text, t.size, True) / 2
    if f.get("right"):
        t = text(sc, th, right, base, f["right"], fs["size"], "muted", False, right - cx - half - 32, "end",
                 owner="footer")
    left = f.get("left") or []
    avail = (cx - half - 72) if f.get("center") else right - 40
    lines = [ln for item in ([left] if isinstance(left, str) else left)
             for ln in textfit.wrap(str(item), fs["size"], False, avail)]
    for j, ln in enumerate(reversed(lines)):
        text(sc, th, 40, base - j * fs["line_h"], ln, fs["size"], "muted", False, avail, owner="footer")
