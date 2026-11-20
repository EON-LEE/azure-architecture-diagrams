"""Layout checks. Errors fail the render (exit code 1); warnings need a human look at the PNG."""
import math

from . import textfit
from .components import backdrop
from .route import segments
from .scene import Badge, Edge, Image, Rect, Swatch, Text
from .style import LINE_CONTRAST, color, contrast, text_contrast

EPS = 0.01
HOLDERS = ("group", "band", "panel")
SPARSE = 0.2  # design-sparse: share of the diagram area one empty block may take


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _grow(b, dx, dy=None):
    dy = dx if dy is None else dy
    return (b[0] - dx, b[1] - dy, b[2] + dx, b[3] + dy)


def _within(a, b, tol=0.5):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


def _seg_box(p, q, box):
    x1, y1, x2, y2 = box
    if abs(p[0] - q[0]) < EPS:
        return x1 < p[0] < x2 and min(p[1], q[1]) < y2 and max(p[1], q[1]) > y1
    if abs(p[1] - q[1]) < EPS:
        return y1 < p[1] < y2 and min(p[0], q[0]) < x2 and max(p[0], q[0]) > x1
    return any(x1 < p[0] + (q[0] - p[0]) * k / 40 < x2 and y1 < p[1] + (q[1] - p[1]) * k / 40 < y2
               for k in range(41))


def _collinear(p, q, r, s):
    if abs(p[1] - q[1]) < EPS and abs(r[1] - s[1]) < EPS and abs(p[1] - r[1]) < 0.5:
        return min(max(p[0], q[0]), max(r[0], s[0])) - max(min(p[0], q[0]), min(r[0], s[0]))
    if abs(p[0] - q[0]) < EPS and abs(r[0] - s[0]) < EPS and abs(p[0] - r[0]) < 0.5:
        return min(max(p[1], q[1]), max(r[1], s[1])) - max(min(p[1], q[1]), min(r[1], s[1]))
    return 0


def _drop_common(P, Q, tol=0.5):
    """Strip the leading path two orthogonal polylines share (a fan's trunk). Returns both remainders
    and the shared length; polylines that start apart share nothing."""
    if math.dist(P[0], Q[0]) > tol:
        return P, Q, 0.0
    P, Q, run = list(P), list(Q), 0.0
    while len(P) > 1 and len(Q) > 1:
        (a0, a1), (b0, b1) = P[:2], Q[:2]
        la, lb = math.dist(a0, a1), math.dist(b0, b1)
        ua = ((a1[0] - a0[0]) / la, (a1[1] - a0[1]) / la)
        ub = ((b1[0] - b0[0]) / lb, (b1[1] - b0[1]) / lb)
        if math.dist(ua, ub) > 1e-3:
            break
        m = min(la, lb)
        cut = (a0[0] + ua[0] * m, a0[1] + ua[1] * m)
        run += m
        P = P[1:] if la - m < tol else [cut, *P[1:]]
        Q = Q[1:] if lb - m < tol else [cut, *Q[1:]]
    return P, Q, run


def _fan(a, b):
    """Edges drawn alike may share a trunk: from one source (fan-out) or, for solid lines whose dash
    phase cannot drift, into one target (fan-in). Returns the parts that must not overlap."""
    if (a.color, a.dash, a.width) != (b.color, b.dash, b.width):
        return a.points, b.points, 0.0
    if a.src == b.src:
        return _drop_common(a.points, b.points)
    if a.dst == b.dst and not a.dash:
        ra, rb, run = _drop_common(a.points[::-1], b.points[::-1])
        return ra[::-1], rb[::-1], run
    return a.points, b.points, 0.0


def text_box(t, measured):
    m = (measured or {}).get(t.id)
    if m:
        return (m["x"], m["y"], m["x"] + m["w"], m["y"] + m["h"])
    x, y, w, h = textfit.ink_box(t.text, t.x, t.y, t.size, t.bold, t.anchor, t.runs)
    return (x, y, x + w, y + h)


def _near_seg(c, p, q, d):
    """True if point c is within d of the axis-aligned segment p-q."""
    x = min(max(c[0], min(p[0], q[0])), max(p[0], q[0]))
    y = min(max(c[1], min(p[1], q[1])), max(p[1], q[1]))
    return math.dist(c, (x, y)) < d


def validate(sc, measured=None):
    out = list(sc.findings)

    def add(level, code, msg, *ids):
        out.append({"level": level, "code": code, "message": msg, "ids": [i for i in ids if i]})

    texts, edges, badges, images = sc.of(Text), sc.of(Edge), sc.of(Badge), sc.of(Image)
    tb = {t.id: text_box(t, measured) for t in texts}
    who = {t.id: t.owner or t.id for t in texts}
    page = (0, 0, sc.width, sc.height)
    nodes = {k: b for k, b in sc.boxes.items() if sc.kind[k] == "node"}
    holders = {k: b for k, b in sc.boxes.items() if sc.kind[k] in HOLDERS}
    ibox = {i.id: (i.x, i.y, i.x + i.size, i.y + i.size) for i in images}

    for t in texts:
        if not _within(tb[t.id], page):
            add("error", "bounds", f"text '{t.text}' leaves the canvas", who[t.id])
        if not t.fits:
            add("error", "text-fit", f"'{t.text}' needs {textfit.width(t.text, t.size, t.bold):.0f}px at the "
                f"minimum font size but has {t.width:.0f}px; shorten it or widen its box", who[t.id])
        m = (measured or {}).get(t.id)
        if m and t.limited and m["w"] > t.width + 2:
            add("error", "text-overflow", f"'{t.text}' renders {m['w']:.0f}px wide but has {t.width:.0f}px",
                who[t.id])
    for r in sc.of(Rect):
        if not _within((r.x, r.y, r.x + r.w, r.y + r.h), page):
            add("error", "bounds", f"shape {r.id} leaves the canvas", r.owner or r.id)
    for i, a in enumerate(texts):
        box_a = _grow(tb[a.id], 0, -1)  # 2px vertical tolerance between stacked lines
        for b in texts[i + 1:]:
            if _hit(box_a, _grow(tb[b.id], 0, -1)):
                add("error", "text-overlap", f"'{a.text}' overlaps '{b.text}'", who[a.id], who[b.id])
    for t in texts:
        own = {t.owner, *sc.ancestors(t.owner)} if t.owner else set()
        for n, b in nodes.items():
            if n not in own and _hit(tb[t.id], _grow(b, -1)):
                add("error", "text-on-node", f"'{t.text}' overlaps node {n}", who[t.id], n)
        for g, b in holders.items():
            if g in own or not _hit(tb[t.id], b):
                continue
            if t.owner in holders:
                add("error", "label-overlap", f"label '{t.text}' of {t.owner} overlaps {g}", t.owner, g)
            elif t.owner in nodes:
                add("error", "label-on-border", f"label '{t.text}' of {t.owner} reaches into {g}", t.owner, g)
            elif not _within(tb[t.id], b):
                add("warning", "text-on-border", f"'{t.text}' straddles the border of {g}", who[t.id], g)
        p = sc.parent.get(t.owner) if t.owner in nodes else None
        if p in sc.boxes and not _within(tb[t.id], sc.boxes[p]):
            add("error", "label-outside-parent", f"label '{t.text}' of {t.owner} sticks out of {p}", t.owner, p)
        for im in images:  # a group's header icon counts too, so compare owners directly
            if im.owner != t.owner and _hit(tb[t.id], ibox[im.id]):
                add("error", "text-on-icon", f"'{t.text}' overlaps the icon of {im.owner}", who[t.id], im.owner)

    ids = list(sc.boxes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            related = a in sc.ancestors(b) or b in sc.ancestors(a)
            if not related and _hit(_grow(sc.boxes[a], -0.5), _grow(sc.boxes[b], -0.5)):
                add("error", "overlap", f"{a} overlaps {b}", a, b)
    for k, p in sc.parent.items():
        if p and p in sc.boxes and not _within(sc.boxes[k], sc.boxes[p]):
            add("error", "outside-parent", f"{k} is not inside its parent {p}", k, p)

    obstacles = {**nodes, **{k: sc.boxes[k] for k in sc.no_edges}}
    for e in edges:
        segs = segments(e.points)
        ends = {e.src, e.dst}
        skip = ends | set(sc.ancestors(e.src)) | set(sc.ancestors(e.dst))
        if any(not _within((x, y, x, y), page) for x, y in e.points):
            add("error", "bounds", f"edge {e.id} leaves the canvas", e.id)
        for t in texts:
            if t.id != e.label_id and any(_seg_box(p, q, _grow(tb[t.id], 2)) for p, q in segs):
                add("error", "edge-text", f"edge {e.id} crosses text '{t.text}'", e.id, who[t.id])
        for k, b in obstacles.items():
            if k not in skip and any(_seg_box(p, q, _grow(b, -1)) for p, q in segs):
                add("error", "edge-node", f"edge {e.id} passes through {k}", e.id, k)
        for im in images:
            if im.owner not in ends and any(_seg_box(p, q, _grow(ibox[im.id], 1)) for p, q in segs):
                add("error", "edge-icon", f"edge {e.id} crosses the icon of {im.owner}", e.id, im.owner)
        for lid, what in ((e.src, "source"), (e.dst, "target")):
            b = _grow(sc.boxes[lid], -1)
            pts = [(p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k) for p, q in segs for k in (.25, .5, .75)]
            if any(b[0] < x < b[2] and b[1] < y < b[3] for x, y in pts):
                add("error", "edge-reenter", f"edge {e.id} runs inside its {what} {lid}", e.id, lid)
        if any(abs(p[0] - q[0]) > EPS and abs(p[1] - q[1]) > EPS for p, q in segs):
            add("warning", "edge-diagonal", f"edge {e.id} has a diagonal segment", e.id)
        if e.arrow in ("end", "both") and math.dist(*segs[-1]) < 14:
            add("warning", "edge-short-tail", f"edge {e.id}: last segment is under 14px", e.id)
    for i, a in enumerate(edges):
        for b in edges[i + 1:]:
            pa, pb, trunk = _fan(a, b)
            if any(_collinear(p, q, r, s) > 2 for p, q in segments(pa) for r, s in segments(pb)):
                add("warning", "edge-overlap", f"edges {a.id} and {b.id} run on top of each other", a.id, b.id)
            elif trunk > 2:
                add("info", "edge-fan", f"edges {a.id} and {b.id} share a {trunk:.0f}px trunk", a.id, b.id)
    for c in sc.crossings:
        add("info" if c["bridge"] else "warning", "edge-crossing",
            f"edge {c['edge']} crosses {c['over']} at {tuple(c['at'])}"
            + ("" if c["bridge"] else "; reroute or set bridge: true if intended"), c["edge"], c["over"])

    for i, b in enumerate(badges):
        bb = (b.cx - b.r, b.cy - b.r, b.cx + b.r, b.cy + b.r)
        if not _within(bb, page):
            add("error", "bounds", f"badge {b.n} leaves the canvas", b.id)
        for t in texts:
            if _hit(bb, tb[t.id]):
                add("error", "badge-text", f"badge {b.n} overlaps '{t.text}'", b.id, who[t.id])
        for c in badges[i + 1:]:
            if math.dist((b.cx, b.cy), (c.cx, c.cy)) < b.r + c.r + 1:
                add("error", "badge-overlap", f"badges {b.n} and {c.n} overlap", b.id, c.id)
        if b.role == "flow":
            for im in images:
                if _hit(bb, ibox[im.id]):
                    add("error", "badge-icon", f"badge {b.n} overlaps the icon of {im.owner}", b.id, im.owner)
            for n, nb in nodes.items():
                if _hit(_grow(bb, -2), nb):
                    add("warning", "badge-on-node", f"badge {b.n} sits on node {n}", b.id, n)
            if not sc.theme["badge"].get("on_line", True):
                for e in edges:
                    if any(_near_seg((b.cx, b.cy), p, q, b.r - 2) for p, q in segments(e.points)):
                        add("warning", "badge-on-edge", f"badge {b.n} sits on edge {e.id}; this style places "
                            "badges beside the line", b.id, e.id)
    flow, steps = {b.n for b in badges if b.role == "flow"}, set(sc.steps)
    if steps and flow != steps:
        add("warning", "steps-badges", f"workflow steps {sorted(steps - flow)} have no badge on the diagram; "
            f"badges {sorted(flow - steps)} have no step")
    _design(sc, add, texts, edges, badges, images, tb)
    _access(sc, add, edges, badges, tb)
    return out


def _empty_rect(grid, rows, cols, m):
    """Largest all-free rectangle at least m cells on each side: (area, col, row, w, h) in cells."""
    h, best = [0] * cols, (0, 0, 0, 0, 0)
    for r in range(rows):
        for c in range(cols):
            h[c] = 0 if grid[r][c] else h[c] + 1
        stack = []
        for c in range(cols + 1):
            cur, start = (h[c] if c < cols else 0), c
            while stack and stack[-1][1] >= cur:
                s, hh = stack.pop()
                if c - s >= m and hh >= m and (c - s) * hh > best[0]:
                    best = ((c - s) * hh, s, r - hh + 1, c - s, hh)
                start = s
            stack.append((start, cur))
    return best


def _gap(area, marks, cell, m):
    """Largest free rectangle inside `area` once every (box, pad) in `marks` is taken, with both
    sides at least m px: (area px², x, y, w, h), or None."""
    x1, y1, x2, y2 = area
    cols, rows = int((x2 - x1) // cell), int((y2 - y1) // cell)
    if cols < 2 or rows < 2:
        return None
    grid = [[False] * cols for _ in range(rows)]
    for b, pad in marks:
        c0, c1 = max(0, int((b[0] - pad - x1) // cell)), min(cols - 1, int((b[2] + pad - x1) // cell))
        r0, r1 = max(0, int((b[1] - pad - y1) // cell)), min(rows - 1, int((b[3] + pad - y1) // cell))
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                grid[r][c] = True
    n, c, r, w, h = _empty_rect(grid, rows, cols, math.ceil(m / cell))
    return (n * cell * cell, x1 + c * cell, y1 + r * cell, w * cell, h * cell) if n else None


def _design(sc, add, texts, edges, badges, images, tb):
    """Readability warnings: scale for the canvas, empty space in groups, near-miss alignment,
    badges far from their lines and edges with too many bends."""
    th, W, cores = sc.theme, sc.width, sc.core
    sizes = sorted(i.size for i in images if i.owner in cores)
    titles = {}
    for t in texts:
        if t.owner in cores:
            titles[t.owner] = max(titles.get(t.owner, 0), t.size)
    if sizes and titles:
        mi, mt = sizes[len(sizes) // 2], sorted(titles.values())[len(titles) // 2]
        if mi < W / 42 or mt < W / 150:
            k = math.ceil(max(W / 42 / mi, W / 150 / mt) * 20) / 20
            add("warning", "design-scale", f"icons ({mi:.0f}px) and labels ({mt:.1f}px) read small on a "
                f"{W:.0f}px wide canvas; set theme.scale: {k:g} or use a narrower canvas")
    cell, m = 10, 1.5 * th["icon"]["size"]
    marks = [(tb[t.id], 6) for t in texts]
    marks += [((b.cx - b.r, b.cy - b.r, b.cx + b.r, b.cy + b.r), 6) for b in badges]
    marks += [((min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])), 6)
              for e in edges for p, q in segments(e.points)]
    for g, gb in sc.boxes.items():
        if sc.kind[g] != "group":
            continue
        kids = [k for k in sc.boxes if k != g and g in sc.ancestors(k)]
        area = (gb[0], gb[1] + max(th["group"]["tile"], 30) + 6, gb[2], gb[3])
        gap = kids and _gap(area, [(sc.boxes[k], 12) for k in kids] + marks, cell, m)
        if gap and gap[0] >= 0.15 * (area[2] - area[0]) * (area[3] - area[1]):
            add("warning", "design-empty", f"group {g} has an empty {gap[3]}x{gap[4]}px area at "
                f"({gap[1]:.0f}, {gap[2]:.0f}); move nodes into it or shrink the group", g)
    # Reference style: the diagram area (below the header rule, above the footer, left of the panel)
    # should be filled too; a small diagram on a large canvas reads as unfinished.
    hb = sc.boxes.get("header")
    if hb:
        foot = [tb[t.id][1] for t in texts if t.owner == "footer"]
        area = (hb[0], hb[3] + 12, hb[2], (min(foot) if foot else sc.height - 26) - 12)
        used = [(b, 12) for k, b in sc.boxes.items() if sc.kind[k] in ("group", "node", "band")]
        gap = _gap(area, used + marks, cell, m)
        total = (area[2] - area[0]) * (area[3] - area[1])
        if gap and gap[0] >= SPARSE * total:
            add("warning", "design-sparse", f"the diagram area has an empty {gap[3]}x{gap[4]}px block at "
                f"({gap[1]:.0f}, {gap[2]:.0f}), {gap[0] / total:.0%} of the area; spread the layout into it, "
                "shrink the canvas or raise theme.scale")
    # Band items are spread automatically, so a near miss with them is not something to fix.
    cs = [(k, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for k, b in cores.items()
          if not any(sc.kind.get(a) == "band" for a in sc.ancestors(k))]
    for i, (a, ax, ay) in enumerate(cs):
        for b, bx, by in cs[i + 1:]:
            if 0.5 < abs(ax - bx) < 12 and abs(ay - by) < 600:
                add("warning", "design-align", f"{a} and {b} sit {abs(ax - bx):.1f}px off a shared column; "
                    "give them the same center x", a, b)
            if 0.5 < abs(ay - by) < 12 and abs(ax - bx) < 900:
                add("warning", "design-align", f"{a} and {b} sit {abs(ay - by):.1f}px off a shared row; "
                    "give them the same center y", a, b)
    for b in badges:
        if b.role == "flow" and edges and not any(_near_seg((b.cx, b.cy), p, q, b.r + 36)
                                                  for e in edges for p, q in segments(e.points)):
            add("warning", "design-badge-far", f"badge {b.n} is more than {b.r + 36:.0f}px from every line; "
                "anchor it with edge: so it sits beside its flow", b.id)
    for e in edges:
        if len(e.points) > 5:
            add("warning", "design-bends", f"edge {e.id} has {len(e.points) - 1} segments; move nodes so it "
                "needs at most 3 bends", e.id)


ACCESS = {  # what -> (finding text, plural noun, fix); {fg} is the color to change
    "text": ("text color {fg} has contrast {r:.2f}:1 on {bg}", "texts",
             "use a darker text color (theme.colors.ink or muted) or a lighter fill"),
    "line": ("line color {fg} has contrast {r:.2f}:1 on {bg}", "lines",
             "darken the flow color (theme.edge_kinds.<kind>.color or the edge color)"),
    "frame": ("frame color {fg} has contrast {r:.2f}:1 next to {bg}", "frames",
              "darken the frame (theme.group_kinds.<kind>.stroke or the group stroke)"),
    "badge": ("badge color {fg} has contrast {r:.2f}:1 with its {bg} number", "badges",
              "darken the badge (theme.badge.color or the flow kind color)"),
}


def _access(sc, add, edges, badges, tb):
    """Accessibility warnings (WAF: "Ensure sufficient color contrast. Avoid relying solely on color to
    distinguish types"). Contrast uses the WCAG 2.1 minimums; colors other than hex are not measured."""
    th = sc.theme
    paper = color(th, "paper")
    low = {}  # (what, fg, need) -> [worst ratio, its background, failing items, owner ids]

    def check(what, fg, bg, need, item, lid):
        r = contrast(fg, bg)
        if r is None or r >= need:
            return
        hit = low.setdefault((what, fg.upper(), need), [r, bg.upper(), set(), []])
        if r < hit[0]:
            hit[0], hit[1] = r, bg.upper()
        hit[2].add(item)
        if lid and lid not in hit[3]:
            hit[3].append(lid)

    shapes = []  # filled rects drawn so far; the last one under a text is its background
    for it in sc.items:
        if isinstance(it, Rect) and it.role != "decor" and it.fill and it.fill != "none":
            shapes.append(it)
        elif isinstance(it, Text):
            b = tb[it.id]
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            if it.halo:
                bg = it.halo if isinstance(it.halo, str) else "#FFFFFF"
            else:
                bg = next((r.fill for r in reversed(shapes)
                           if r.x <= cx <= r.x + r.w and r.y <= cy <= r.y + r.h), paper)
            check("text", it.color, bg, text_contrast(it.size, it.bold), it.id, it.owner or it.id)
    for e in edges:
        for p, q in segments(e.points):
            check("line", e.color, backdrop(sc, th, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2), LINE_CONTRAST,
                  e.id, e.id)
    for s in sc.of(Swatch):
        check("line", s.color, backdrop(sc, th, (s.x1 + s.x2) / 2, s.y), LINE_CONTRAST, s.id, s.parent)
    for r in sc.of(Rect):
        if r.role not in ("group", "frame") or not r.stroke or r.stroke == "none":
            continue
        lid = r.owner or r.id
        outer = next((sc.fills[a] for a in sc.ancestors(lid) if a in sc.fills), paper)
        for bg in (r.fill if r.fill and r.fill != "none" else outer, outer):
            check("frame", r.stroke, bg, LINE_CONTRAST, r.id, lid)
    for b in badges:
        check("badge", b.color, "#FFFFFF", text_contrast(b.size, True), b.id, b.id)
    for (what, fg, need), (r, bg, items, ids) in low.items():
        found, noun, fix = ACCESS[what]
        add("warning", "design-contrast", found.format(fg=fg, r=r, bg=bg) + f", below {need:g}:1 "
            f"({len(items)} {noun}); {fix}", *ids)
    # Line pattern per flow look: two colors drawn with the same pattern are told apart by color alone.
    looks = {}  # pattern -> color -> [kinds], first edge id
    for e in edges:
        pattern = " ".join(str(e.dash or "").replace(",", " ").split()) or "solid"
        hit = looks.setdefault(pattern, {}).setdefault(str(e.color).upper(), [[], e.id])
        if (e.kind or e.id) not in hit[0]:
            hit[0].append(e.kind or e.id)
    for pattern, cols in looks.items():
        if len(cols) > 1:
            flows = "; ".join(f"{', '.join(k)} in {c}" for c, (k, _) in cols.items())
            line = "solid" if pattern == "solid" else f"dashed '{pattern}'"
            add("warning", "design-color-only", f"flows {flows} are all {line} and differ only by color; give "
                "each a different dash (theme.edge_kinds.<kind>.dash or the edge dash) so the legend does not "
                "rely on color", *[first for _, first in cols.values()])
