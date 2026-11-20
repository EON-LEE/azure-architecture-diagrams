"""SVG writer. Icons are embedded as base64 data URIs so every SVG is self-contained."""
import base64
import math
from xml.etree import ElementTree as ET

from .scene import Badge, Edge, Image, Rect, Swatch, Text

XLINK = "http://www.w3.org/1999/xlink"
XMLNS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("xlink", XLINK)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _on(p, a, b):
    return (min(a[0], b[0]) - 0.01 <= p[0] <= max(a[0], b[0]) + 0.01 and
            min(a[1], b[1]) - 0.01 <= p[1] <= max(a[1], b[1]) + 0.01 and
            abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) < 0.5)


def pieces(points, gaps, g):
    """Split a polyline at crossing points so the later edge visibly hops over the earlier one."""
    out, cur = [], [points[0]]
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        for p in sorted((p for p in gaps if _on(p, a, b)), key=lambda p: math.dist(a, p)):
            cur.append((p[0] - ux * g, p[1] - uy * g))
            out.append(cur)
            cur = [(p[0] + ux * g, p[1] + uy * g)]
        cur.append(b)
    out.append(cur)
    return out


def write(sc, lib, path):
    th = sc.theme
    root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=num(sc.width),
                      height=num(sc.height), viewBox=f"0 0 {num(sc.width)} {num(sc.height)}", role="img")
    root.set("aria-labelledby", "title desc")
    root.set("font-family", th["font_family"])
    ET.SubElement(root, "title", id="title").text = sc.title or sc.name
    ET.SubElement(root, "desc", id="desc").text = sc.desc or sc.title or sc.name
    defs = ET.SubElement(root, "defs")
    markers = {}

    def marker(col):
        if col not in markers:
            mid = f"arrow-{len(markers) + 1}"
            a = num(th["edge"]["arrow"])
            m = ET.SubElement(defs, "marker", id=mid, viewBox="0 0 10 10", refX="9", refY="5",
                              markerWidth=a, markerHeight=a, orient="auto-start-reverse",
                              markerUnits="userSpaceOnUse")
            if th["edge"].get("head") == "open":
                p = ET.SubElement(m, "path", d="M1 1 L9 5 L1 9", fill="none", stroke=col)
                p.set("stroke-width", "1.6")
                p.set("stroke-linejoin", "miter")
            else:
                ET.SubElement(m, "path", d="M0 0 L10 5 L0 10 Z", fill=col)
            markers[col] = mid
        return f"url(#{markers[col]})"

    for it in sc.items:
        if isinstance(it, Rect):
            if it.fill == "none" and it.stroke == "none":
                continue
            el = ET.SubElement(root, "rect", x=num(it.x), y=num(it.y), width=num(it.w), height=num(it.h),
                               fill=it.fill, stroke=it.stroke)
            if it.radius:
                el.set("rx", num(it.radius))
            if it.stroke != "none":
                el.set("stroke-width", num(it.sw))
            if it.dash:
                el.set("stroke-dasharray", it.dash)
            el.set("data-id", it.id)
        elif isinstance(it, Image):
            el = ET.SubElement(root, "image", x=num(it.x), y=num(it.y), width=num(it.size),
                               height=num(it.size))
            el.set(f"{{{XLINK}}}href", "data:image/svg+xml;base64,"
                   + base64.b64encode(lib.get(it.key)).decode("ascii"))
            el.set("data-icon", it.key)
        elif isinstance(it, Text):
            el = ET.SubElement(root, "text", x=num(it.x), y=num(it.y), fill=it.color)
            el.set("font-size", num(it.size))
            if it.bold:
                el.set("font-weight", "700")
            if it.anchor != "start":
                el.set("text-anchor", it.anchor)
            if it.halo:
                halo = it.halo if isinstance(it.halo, str) else "#FFFFFF"
                for k, v in (("stroke", halo), ("stroke-width", "5"), ("stroke-linejoin", "round"),
                             ("paint-order", "stroke")):
                    el.set(k, v)
            el.set("data-id", it.id)
            el.set("data-w", num(it.width))
            el.set("data-limited", "1" if it.limited else "0")
            if it.runs:
                el.set(f"{{{XMLNS}}}space", "preserve")
                el.set("style", "white-space:pre")
                for t, bold in it.runs:
                    span = ET.SubElement(el, "tspan")
                    if bold:
                        span.set("font-weight", "700")
                    span.text = t
            else:
                el.text = it.text
        elif isinstance(it, Edge):
            parts = pieces(it.points, it.gaps, th["edge"]["gap"])
            for k, part in enumerate(parts):
                el = ET.SubElement(root, "polyline", fill="none", stroke=it.color,
                                   points=" ".join(f"{num(x)},{num(y)}" for x, y in part))
                el.set("stroke-width", num(it.width))
                el.set("stroke-linejoin", "round")
                if it.dash:
                    el.set("stroke-dasharray", it.dash)
                if k == len(parts) - 1 and it.arrow in ("end", "both"):
                    el.set("marker-end", marker(it.color))
                if k == 0 and it.arrow in ("start", "both"):
                    el.set("marker-start", marker(it.color))
                el.set("data-edge", it.id)
        elif isinstance(it, Badge):
            c = ET.SubElement(root, "circle", cx=num(it.cx), cy=num(it.cy), r=num(it.r), fill=it.color,
                              stroke=it.ring)
            c.set("stroke-width", "2")
            c.set("data-badge", it.n)
            t = ET.SubElement(root, "text", x=num(it.cx), y=num(it.cy + it.size * 0.36), fill="#FFFFFF")
            for k, v in (("font-size", num(it.size)), ("font-weight", "700"), ("text-anchor", "middle"),
                         ("font-family", "'Segoe UI', Arial, sans-serif"), ("data-badge", it.n)):
                t.set(k, v)
            t.text = it.n
        elif isinstance(it, Swatch):
            el = ET.SubElement(root, "line", x1=num(it.x1), y1=num(it.y), x2=num(it.x2), y2=num(it.y),
                               stroke=it.color)
            el.set("stroke-width", num(it.width))
            if it.dash:
                el.set("stroke-dasharray", it.dash)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
