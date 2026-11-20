"""Orthogonal edge geometry between element borders, edge labels and crossing gaps."""
from .components import backdrop, text
from .scene import Edge
from .style import color, readable, text_contrast

EPS = 0.01


def segments(points):
    return list(zip(points, points[1:]))


def _inside(v, a, b):
    return a + 1 <= v <= b - 1


def _straight(S, T, axis, v, eid):
    """Horizontal (axis 'y') or vertical (axis 'x') line at v between the facing sides of S and T."""
    i = 1 if axis == "y" else 0
    j = 1 - i
    for box, what in ((S, "source"), (T, "target")):
        if not _inside(v, box[i], box[i + 2]):
            raise ValueError(f"edge {eid}: {axis}={v:g} misses the {what} box ({box[i]:g}..{box[i + 2]:g})")
    if S[j + 2] <= T[j]:
        a, b = S[j + 2], T[j]
    elif T[j + 2] <= S[j]:
        a, b = S[j], T[j + 2]
    else:
        raise ValueError(f"edge {eid}: source and target overlap along the line; use 'via'")
    return [(a, v), (b, v)] if axis == "y" else [(v, a), (v, b)]


def _port(box, p, eid, what):
    """Border point of `box` from which one straight segment reaches the via point p."""
    x1, y1, x2, y2 = box
    px, py = p
    if _inside(px, x1, x2) and not y1 <= py <= y2:
        return (px, y2 if py > y2 else y1)
    if _inside(py, y1, y2) and not x1 <= px <= x2:
        return (x2 if px > x2 else x1, py)
    raise ValueError(f"edge {eid}: via point ({px:g}, {py:g}) must share x or y with the {what} box "
                     f"({x1:g},{y1:g})-({x2:g},{y2:g}) and lie outside it")


def _auto(S, T, eid, CS=None, CT=None):
    """Straight line through the middle of the overlap of the two icon/core boxes."""
    CS, CT = CS or S, CT or T
    oy = min(CS[3], CT[3]) - max(CS[1], CT[1])
    ox = min(CS[2], CT[2]) - max(CS[0], CT[0])
    if oy > 2 and ox <= 0:
        return _straight(S, T, "y", (max(CS[1], CT[1]) + min(CS[3], CT[3])) / 2, eid)
    if ox > 2 and oy <= 0:
        return _straight(S, T, "x", (max(CS[0], CT[0]) + min(CS[2], CT[2])) / 2, eid)
    raise ValueError(f"edge {eid}: boxes are not aligned; give 'y', 'x', 'via' or 'points'")


def cross(p, q, r, s):
    """Interior crossing point of one horizontal and one vertical segment, else None."""
    if abs(p[1] - q[1]) < EPS and abs(r[0] - s[0]) < EPS:
        h, v = (p, q), (r, s)
    elif abs(p[0] - q[0]) < EPS and abs(r[1] - s[1]) < EPS:
        h, v = (r, s), (p, q)
    else:
        return None
    x, y = v[0][0], h[0][1]
    if min(h[0][0], h[1][0]) + 1 < x < max(h[0][0], h[1][0]) - 1 and \
            min(v[0][1], v[1][1]) + 1 < y < max(v[0][1], v[1][1]) - 1:
        return (x, y)
    return None


def route(sc, th, e, ev):
    eid = e["id"]
    for k in ("from", "to"):
        if e.get(k) not in sc.boxes:
            raise ValueError(f"edge {eid}: unknown {k} element '{e.get(k)}'")
    S, T = sc.boxes[e["from"]], sc.boxes[e["to"]]
    modes = [k for k in ("y", "x", "via", "points") if k in e]
    if len(modes) > 1:
        raise ValueError(f"edge {eid}: use only one of y, x, via, points")
    mode = modes[0] if modes else None
    if mode == "points":
        pts = [tuple(ev(v) for v in p) for p in e["points"]]
    elif mode == "via":
        via = [tuple(ev(v) for v in p) for p in e["via"]]
        pts = [_port(S, via[0], eid, "source"), *via, _port(T, via[-1], eid, "target")]
    elif mode:
        pts = _straight(S, T, mode, ev(e[mode]), eid)
    else:
        pts = _auto(S, T, eid, sc.core.get(e["from"]), sc.core.get(e["to"]))
    if len(pts) < 2 or any(abs(p[0] - q[0]) + abs(p[1] - q[1]) < EPS for p, q in segments(pts)):
        raise ValueError(f"edge {eid}: needs at least two distinct points, got {pts}")
    kind = e.get("kind", "request")
    ek = th["edge_kinds"].get(kind)
    if ek is None:
        raise ValueError(f"edge {eid}: unknown kind '{kind}'. Kinds: {', '.join(th['edge_kinds'])}")
    arrow = e.get("arrow", "end")
    if arrow not in ("end", "start", "both", "none"):
        raise ValueError(f"edge {eid}: arrow must be end, start, both or none")
    col = color(th, e.get("color", ek["color"]))
    edge = Edge(eid, pts, col, th["edge"]["width"], e.get("dash", ek["dash"]), e["from"], e["to"], kind,
                arrow, bool(e.get("bridge")))
    for other in sc.of(Edge):
        for p, q in segments(pts):
            for r, s in segments(other.points):
                hit = cross(p, q, r, s)
                if hit:  # the later edge hops over the earlier one
                    edge.gaps.append(hit)
                    sc.crossings.append({"edge": eid, "over": other.id, "bridge": edge.bridge,
                                         "at": [round(hit[0], 1), round(hit[1], 1)]})
    sc.add(edge)
    if e.get("label"):
        if e.get("label_at"):
            x, y = (ev(v) for v in e["label_at"])
            anchor = e.get("label_anchor", "middle")
        else:
            p, q = max(segments(pts), key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
            if abs(p[1] - q[1]) < EPS:
                x, y, anchor = (p[0] + q[0]) / 2, p[1] - 8, "middle"
            else:
                x, y, anchor = p[0] + 8, (p[1] + q[1]) / 2 + 4, "start"
        bg, size, bold = backdrop(sc, th, x, y), th["edge"]["label"], th["edge"]["label_bold"]
        t = text(sc, th, x, y, e["label"], size, readable(th, col, bg, text_contrast(size, bold)), bold, None,
                 anchor, "1", eid, "label", bg)
        edge.label_id = t.id
    return edge
