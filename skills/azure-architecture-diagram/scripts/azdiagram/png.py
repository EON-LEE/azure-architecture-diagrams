"""Headless-browser rendering: PNG export plus measured text boxes for validation."""
from pathlib import Path

MEASURE = """() => [...document.querySelectorAll('text[data-id]')].map(t => {
  const b = t.getBBox();
  return {id: t.dataset.id, x: b.x, y: b.y, w: b.width, h: b.height};
})"""


def _launch(pw):
    errors = []
    for kw in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            return pw.chromium.launch(headless=True, **kw)
        except Exception as exc:  # try the next browser
            errors.append(f"{kw.get('channel', 'bundled chromium')}: {str(exc).splitlines()[0]}")
    raise RuntimeError("no browser for PNG export (" + "; ".join(errors) + "). Install Edge or Chrome, "
                       "run 'python -m playwright install chromium', or pass --no-png.")


def render(jobs, scale=1.25):
    """jobs: [(svg_path, png_path, width, height)]. Returns {str(svg_path): [measured text boxes]}."""
    from playwright.sync_api import sync_playwright

    out = {}
    with sync_playwright() as pw:
        browser = _launch(pw)
        try:
            for svg, png, w, h in jobs:
                page = browser.new_page(viewport={"width": int(w), "height": int(h)},
                                        device_scale_factor=scale)
                page.goto(Path(svg).resolve().as_uri(), wait_until="load")
                page.evaluate("document.fonts.ready.then(() => true)")
                out[str(svg)] = page.evaluate(MEASURE)
                page.screenshot(path=str(png), animations="disabled")
                page.close()
        finally:
            browser.close()
    return out
