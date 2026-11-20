"""Page furniture: flow badges, free texts, the workflow/legend side panel and shared-service bands."""
import math

from . import textfit
from .components import backdrop, glyph, register, text
from .scene import Badge, Edge, Image, Rect, Swatch, Text
from .style import color
from .validate import text_box

SIDES = {"above": (0, -1), "below": (0, 1), "left": (-1, 0), "right": (1, 0)}


def kind_style(th, kind):
    ek = th["edge_kinds"].get(kind)
    if ek is None:
        raise ValueError(f"unknown flow kind '{kind}'. Kinds: {', '.join(th['edge_kinds'])}")
    return ek


def badge_color(th, kind):
    return color(th, th["badge"].get("color") or kind_style(th, kind)["color"])


def _walk(pts, d):
    """Point and unit direction at distance d along a polyline."""
    segs = [(p, q, math.dist(p, q)) for p, q in zip(pts, pts[1:]) if math.dist(p, q) > 0]
    if not segs:
        return pts[0], (1.0, 0.0)
    for i, (p, q, seg) in enumerate(segs):
        if d <= seg or i == len(segs) - 1:
            t = min(max(d / seg, 0.0), 1.0)
            return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t), ((q[0] - p[0]) / seg, (q[1] - p[1]) / seg)
        d -= seg


def _seg_dist(c, p, q):
    x = min(max(c[0], min(p[0], q[0])), max(p[0], q[0]))
    y = min(max(c[1], min(p[1], q[1])), max(p[1], q[1]))
    return math.dist(c, (x, y))


def _cost(sc, cx, cy, r, tbs):
    """How many things a badge at (cx, cy) would touch; 0 means a clean spot."""
    bb = (cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3)

    def hit(b):
        return bb[0] < b[2] and b[0] < bb[2] and bb[1] < b[3] and b[1] < bb[3]

    c = 0 if bb[0] >= 0 and bb[1] >= 0 and bb[2] <= sc.width and bb[3] <= sc.height else 10
    c += sum(hit(b) for b in tbs)
    c += sum(hit((i.x, i.y, i.x + i.size, i.y + i.size)) for i in sc.of(Image))
    c += sum(hit((t.x, t.y, t.x + t.w, t.y + t.h)) for t in sc.of(Rect) if t.role == "tile")
    c += sum(hit(b) for b in sc.core.values())
    c += sum(math.dist((cx, cy), (o.cx, o.cy)) < r + o.r + 4 for o in sc.of(Badge))
    c += sum(_seg_dist((cx, cy), p, q) < r + 2 for e in sc.of(Edge) for p, q in zip(e.points, e.points[1:]))
    for k, b in sc.boxes.items():  # straddling a frame line
        if sc.kind[k] in ("group", "band", "panel") and hit(b) and not (
                b[0] <= bb[0] and b[1] <= bb[1] and bb[2] <= b[2] and bb[3] <= b[3]):
            c += 1
    return c


def _on_edge(sc, b, r, tbs):
    """Best free spot beside edge b['edge'], searched outward from pos; returns (edge, (cost, x, y))."""
    e = next((x for x in sc.of(Edge) if x.id == b["edge"]), None)
    if e is None:
        raise ValueError(f"badge {b['n']}: unknown edge '{b['edge']}'")
    pts = e.points
    total = sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
    pos = b.get("pos", "start")
    if pos in ("start", "mid", "end"):
        d0 = {"start": 2 * r + 14, "mid": total / 2, "end": total - 2 * r - 18}[pos]
    elif isinstance(pos, (int, float)) and not isinstance(pos, bool) and 0 <= pos <= 1:
        d0 = total * pos
    else:
        raise ValueError(f"badge {b['n']}: pos must be start, mid, end or a number from 0 to 1")
    side = b.get("side", "auto")
    if side != "auto" and side not in SIDES:
        raise ValueError(f"badge {b['n']}: side must be auto, above, below, left or right")
    off, best = b.get("offset", r + 5), None
    for k in (0, 1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 8, -8):
        (x, y), (_ux, uy) = _walk(pts, min(max(d0 + k * 12, 1), max(total - 1, 1)))
        sides = [side] if side != "auto" else (["above", "below"] if abs(uy) < 0.5 else ["right", "left"])
        for s in sides:
            cx, cy = x + SIDES[s][0] * off, y + SIDES[s][1] * off
            c = _cost(sc, cx, cy, r, tbs)
            if best is None or c < best[0]:
                best = (c, cx, cy)
            if c == 0:
                return e, best
    return e, best


def badges(sc, th, items, ev):
    """Flow badges. `edge:` places one beside that edge (pos/side/offset tune it); `at:` pins it."""
    bs, tbs = th["badge"], None
    for b in items or []:
        kind = b.get("kind")
        if "edge" in b:
            tbs = tbs if tbs is not None else [text_box(t, None) for t in sc.of(Text)]
            e, (c, x, y) = _on_edge(sc, b, bs["r"], tbs)
            kind = kind or e.kind
            if c:
                sc.findings.append({
                    "level": "warning", "code": "badge-placement", "ids": [e.id],
                    "message": f"badge {b['n']}: no free spot beside edge {e.id} near {b.get('pos', 'start')}; "
                               "set pos, side or offset, or pin it with at"})
        else:
            x, y = (ev(v) for v in b["at"])
        sc.add(Badge(sc.uid("badge"), x, y, str(b["n"]), badge_color(th, kind or "request"), bs["r"],
                     bs["size"], "flow", ring=backdrop(sc, th, x, y)))


def texts(sc, th, items, ev):
    for t in items or []:
        x, y = (ev(v) for v in t["at"])
        width = ev(t["width"]) if t.get("width") is not None else None
        text(sc, th, x, y, t["text"], t.get("size", 14), t.get("color", "muted"), t.get("bold", False),
             width, t.get("anchor", "start"), role="note")


def sidebar(sc, th, p, ev, used_kinds):
    """Numbered workflow steps from the top, legend anchored to the bottom of the panel."""
    ps, bs = th["panel"], th["badge"]
    x1, y1, x2, y2 = (ev(v) for v in p["box"])
    pid = p.get("id", "panel")
    sc.add(Rect(pid, x1, y1, x2 - x1, y2 - y1, ps["fill"], "none", 0, ps["radius"], None, "1", True, "panel",
                pid))
    register(sc, pid, (x1, y1, x2, y2), "panel")
    sc.fills[pid] = color(th, ps["fill"])
    sc.no_edges.add(pid)
    if th["style"] == "reference":
        return _ref_steps(sc, th, p, pid, (x1, y1, x2, y2), used_kinds)
    inner = x2 - x1 - 48
    y = y1 + 42
    if p.get("title"):
        text(sc, th, x1 + 24, y, p["title"], ps["title"], "ink", True, inner, parent=pid, owner=pid)
    for j, line in enumerate(textfit.wrap(p.get("note", ""), ps["note"], False, inner)):
        y += 26 if j == 0 else 18
        text(sc, th, x1 + 24, y, line, ps["note"], "muted", False, inner, parent=pid, owner=pid)
    last, y = y, y + 52
    hx = x1 + 62
    tw = x2 - 16 - hx
    for i, s in enumerate(p.get("steps") or [], 1):
        n = str(s.get("n", i))
        sc.add(Badge(sc.uid("badge"), x1 + 37, y - 5, n, badge_color(th, s.get("kind", "request")),
                     bs["r"], bs["size"], "panel", pid, ring=color(th, ps["fill"])))
        text(sc, th, hx, y, s["title"], ps["step_title"], "ink", True, tw, parent=pid, owner=pid)
        last = y
        for j, line in enumerate(textfit.wrap(s.get("text", ""), ps["step_text"], False, tw)):
            last = y + ps["line_h"] + 3 + j * ps["line_h"]
            text(sc, th, hx, last, line, ps["step_text"], "muted", False, tw, parent=pid, owner=pid)
        sc.steps.append(n)
        y = last + ps["step_gap"] + ps["step_title"] + 12
    legend(sc, th, p, pid, (x1, y1, x2, y2), used_kinds, last + 8)


def _ref_steps(sc, th, p, pid, box, used_kinds):
    """Reference style: optional title, then numbered sentences (**bold** service names) spread down
    the column; the legend, if any, sits at the bottom."""
    from .refstyle import rich
    ps, bs = th["panel"], th["badge"]
    x1, y1, x2, y2 = box
    pad, size, lh = ps["pad"], ps["step_text"], ps["line_h"]
    inner, hx = x2 - x1 - 2 * pad, x1 + ps["text_dx"]
    y = y1 + ps["top"]
    if p.get("title"):
        text(sc, th, x1 + pad, y, p["title"], ps["title"], "ink", True, inner, parent=pid, owner=pid)
        y += ps["title"] + 8
    for j, line in enumerate(textfit.wrap(p.get("note", ""), ps["note"], False, inner)):
        text(sc, th, x1 + pad, y, line, ps["note"], "muted", False, inner, parent=pid, owner=pid)
        y += ps["note"] + 6
    if p.get("title") or p.get("note"):
        y += 30
    steps = p.get("steps") or []

    def wrap(sz):
        return [textfit.wrap_rich((f"**{s['title']}** " if s.get("title") else "") + str(s.get("text", "")),
                                  sz, x2 - pad - hx) for s in steps]

    blocks = wrap(size)
    rows = _legend_rows(th, p, used_kinds, inner)
    floor = (y2 - rows[-1][2] - 22 - 24) if rows else y2 - pad
    # A tall panel with short steps leaves a hole above the legend; grow the text (up to grow_max)
    # while the steps still fit with gaps halfway between step_gap and max_gap.
    if len(steps) > 1 and ps.get("grow_max", 1) > 1:
        want, s = (ps["step_gap"] + ps.get("max_gap", ps["step_gap"])) / 2 * (len(steps) - 1), size
        while s + 0.5 <= size * ps["grow_max"]:
            nb = wrap(s + 0.5)
            if (y - size) + sum(len(b) for b in nb) * lh * (s + 0.5) / size + want > floor:
                break
            s, blocks = s + 0.5, nb
        lh, y, size = lh * s / size, y + s - size, s
    # Still short even with max_gap: open the leading (up to lead_max x size), which also reads better in Korean.
    lines = sum(len(b) for b in blocks)
    if len(blocks) > 1 and lines:
        extra = floor - (y - size) - lines * lh - ps.get("max_gap", ps["step_gap"]) * (len(blocks) - 1)
        if extra > 0:
            lh = min(lh + extra / lines, max(lh, size * ps.get("lead_max", 1)))
    gap = ps["step_gap"]
    if len(blocks) > 1:
        free = floor - (y - size) - sum(len(b) for b in blocks) * lh
        gap = max(ps["step_gap"], min(free / (len(blocks) - 1), ps.get("max_gap", ps["step_gap"])))
    last = y - size
    for i, (s, lines) in enumerate(zip(steps, blocks), 1):
        n = str(s.get("n", i))
        sc.add(Badge(sc.uid("badge"), x1 + ps["badge_dx"], y - 5, n, badge_color(th, s.get("kind", "request")),
                     bs["r"], bs["size"], "panel", pid, ring=color(th, ps["fill"])))
        for j, runs in enumerate(lines):
            last = y + j * lh
            rich(sc, th, hx, last, runs, size, "ink", x2 - pad - hx, pid, pid)
        sc.steps.append(n)
        y = last + lh + gap
    legend(sc, th, p, pid, box, used_kinds, last + 8)


def _legend_rows(th, p, used_kinds, inner):
    """Legend rows (what, value, dy). Kinds drawn identically (same color and dash) share one row."""
    ps = th["panel"]
    spec = p.get("legend", "auto")
    if spec in ("none", False, None):
        spec = []
    kinds = [k for k in th["edge_kinds"] if k in used_kinds] if spec == "auto" else list(spec)
    merged = {}
    for k in kinds:
        ek = kind_style(th, k)
        merged.setdefault((ek["color"], ek["dash"]), []).append(ek["label"])
    notes = [ln for n in p.get("legend_notes") or [] for ln in textfit.wrap(n, ps["legend_note"], False, inner)]
    rows, dy = [], 15 + ps["legend_title"] + ps["legend_row"]
    for (col, dash), labels in merged.items():
        rows.append(("item", (col, dash, " / ".join(labels)), dy))
        dy += ps["legend_row"]
    dy += 6 if merged and notes else 0
    for line in notes:
        rows.append(("note", line, dy))
        dy += ps["legend_note_h"]
    return rows


def legend(sc, th, p, pid, box, used_kinds, content_bottom):
    x1, _y1, x2, y2 = box
    ps = th["panel"]
    inner = x2 - x1 - 2 * ps["pad"]
    rows = _legend_rows(th, p, used_kinds, inner)
    if not rows:
        return
    lx = x1 + ps["pad"]
    top = y2 - (rows[-1][2] + 22)
    if top < content_bottom + 16:
        sc.findings.append({
            "level": "error", "code": "panel-too-short", "ids": [pid],
            "message": f"panel '{pid}': steps end at y={content_bottom:.0f} but the legend must start at "
                       f"y={top:.0f}. Enlarge the panel, shorten step text or reduce theme.panel sizes."})
    sc.add(Rect(sc.uid("rule"), lx, top, inner, 1, "#C9D6DF", parent=pid, role="decor", owner=pid))
    text(sc, th, lx, top + 13 + ps["legend_title"], p.get("legend_title", "범례"), ps["legend_title"], "ink",
         True, inner, parent=pid, owner=pid)
    for what, val, d in rows:
        y = top + d
        if what == "item":
            col, dash, label = val
            sc.add(Swatch(sc.uid("swatch"), lx + 2, lx + 46, y - 5, color(th, col), th["edge"]["width"],
                          dash, pid))
            text(sc, th, lx + 56, y, label, ps["legend_text"], "ink", False, x2 - ps["pad"] - (lx + 56),
                 parent=pid, owner=pid)
        else:
            text(sc, th, lx, y, val, ps["legend_note"], "muted", False, inner, parent=pid, owner=pid)


def band(sc, th, b, ev, lib):
    """Shared services strip (identity, governance, monitoring). Edges may end at the band or at one of
    its items (id from the item's `id`, else `<band id>-<n>`) but must not cross it."""
    if th["style"] == "reference":
        return _ref_band(sc, th, b, ev, lib)
    bid = b["id"]
    x1, y1, x2, y2 = (ev(v) for v in b["box"])
    gk, gs = th["group_kinds"]["band"], th["group"]
    sc.add(Rect(bid, x1, y1, x2 - x1, y2 - y1, gk["fill"], gk["stroke"], 1.5, gs["radius"],
                gs["dash"] if gk["dash"] else None, "1", True, "group", bid))
    register(sc, bid, (x1, y1, x2, y2), "band")
    sc.no_edges.add(bid)
    lw, cy = b.get("label_width", 190), (y1 + y2) / 2
    if b.get("label"):
        text(sc, th, x1 + 18, cy - 8 if b.get("note") else cy + 5, b["label"], 15, "ink", True, lw - 28,
             parent=bid, owner=bid)
    if b.get("note"):
        text(sc, th, x1 + 18, cy + 14, b["note"], 12.5, "muted", False, lw - 28, parent=bid, owner=bid)
    items = b.get("items") or []
    slot = (x2 - 10 - x1 - lw) / max(len(items), 1)
    for i, it in enumerate(items):
        sx = x1 + lw + i * slot
        n = {"icon_size": 40, "title_size": 15, "detail_size": 12.5, **it,
             "id": it.get("id") or f"{bid}-{i + 1}", "type": "glyph", "parent": bid}
        box = (sx, y1 + 10, sx + slot - 12, y2 - 10)
        register(sc, n["id"], box, "node", bid)
        glyph(sc, th, n, box, lib)


def _ref_band(sc, th, b, ev, lib):
    """Reference style: dashed frame, label (and note) top-left, icons with labels to their right
    spread evenly in one row."""
    from .refstyle import core_box, icon_node
    bid = b["id"]
    x1, y1, x2, y2 = (ev(v) for v in b["box"])
    gk, gs = th["group_kinds"]["band"], th["group"]
    fill = color(th, gk["fill"])
    sc.add(Rect(bid, x1, y1, x2 - x1, y2 - y1, fill, color(th, gk["stroke"]), gs["sw"], 0,
                gs["dash"] if gk["dash"] else None, "1", True, "group", bid))
    register(sc, bid, (x1, y1, x2, y2), "band")
    if fill != "none":
        sc.fills[bid] = fill
    sc.no_edges.add(bid)
    top = y1
    if b.get("label"):
        base = y1 + 8 + gs["label"]
        lb = text(sc, th, x1 + 14, base, b["label"], gs["label"], "ink", gs["label_bold"], x2 - x1 - 28,
                  parent=bid, owner=bid)
        nx = x1 + 14 + textfit.width(lb.text, lb.size, gs["label_bold"]) + 12
        if b.get("note") and x2 - 14 - nx > 60:
            text(sc, th, nx, base, b["note"], gs["sublabel"], "muted", False, x2 - 14 - nx, parent=bid,
                 owner=bid)
        top = base + 10
    items = b.get("items") or []
    if not items:
        return
    isz = b.get("icon_size", round(th["icon"]["size"] * 0.625, 2))
    slot = (x2 - x1 - 28) / len(items)
    cy = (top + y2) / 2
    for i, it in enumerate(items):
        n = {"icon_size": isz, "label_w": slot - isz - th["icon"]["gap"] - 16, **it, "label_pos": "right",
             "id": it.get("id") or f"{bid}-{i + 1}", "type": "icon", "parent": bid}
        core = core_box(th, n, 0, cy)
        sx = x1 + 14 + i * slot
        core = (sx, core[1], sx + core[2] - core[0], core[3])
        register(sc, n["id"], core, "node", bid)
        icon_node(sc, th, n, core, lib)
