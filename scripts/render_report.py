#!/usr/bin/env python3
"""
render_report.py - draws the profile's "receipts" card from data/evals.json.

Stdlib only. Writes assets/grounding-report-dark.svg and -light.svg.
Percent changes are COMPUTED from the raw numbers, never typed by hand,
so the card cannot contain an arithmetic mistake.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "evals.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(bg="#0d1117", text="#e6edf3", muted="#8b949e", faint="#30363d",
                 bad="#f0883e", good="#3fb950", base="#6e7681"),
    "light": dict(bg="#ffffff", text="#1f2328", muted="#59636e", faint="#d1d9e0",
                  bad="#bc4c00", good="#1a7f37", base="#8c959f"),
}
W, H = 880, 410
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
esc = html.escape


def drop(before, after):
    return round((1 - after / before) * 100)


def render(name, c):
    d, bars = DATA["dots"], DATA["bars"]
    p = []
    add = p.append

    desc = (f"{d['title']}: {d['before']} of {d['total']} before, {d['after']} of {d['total']} after. "
            + " ".join(f"{b['label']}: {b['before_label']} to {b['after_label']}." for b in bars))
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">')
    add(f'<title id="t">{esc(DATA["headline"])}</title><desc id="d">{esc(desc)}</desc>')
    add(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{c["bg"]}" stroke="{c["faint"]}"/>')

    # header
    add(f'<text x="32" y="44" font-family="{MONO}" font-size="12" letter-spacing="2.5" fill="{c["muted"]}">RECEIPTS, NOT ADJECTIVES</text>')
    add(f'<text x="32" y="74" font-family="{SANS}" font-size="22" font-weight="700" fill="{c["text"]}">{esc(DATA["headline"])}</text>')
    add(f'<text x="32" y="96" font-family="{SANS}" font-size="13" fill="{c["muted"]}">{esc(DATA["subtitle"])}</text>')
    add(f'<line x1="430" y1="122" x2="430" y2="364" stroke="{c["faint"]}"/>')

    # left: 10x10 dot grids
    add(f'<text x="32" y="134" font-family="{SANS}" font-size="12" font-weight="700" fill="{c["text"]}">{esc(d["title"])}</text>')
    add(f'<text x="32" y="150" font-family="{SANS}" font-size="11" fill="{c["muted"]}">{esc(d["note"])}</text>')
    for ox, label, n, col in ((32, "BEFORE", d["before"], c["bad"]), (232, "AFTER", d["after"], c["good"])):
        for i in range(d["total"]):
            cx = ox + 5.5 + (i % 10) * 16
            cy = 172 + (i // 10) * 16
            fill = col if i < n else c["faint"]
            add(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="{fill}"/>')
        add(f'<text x="{ox}" y="352" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{c["muted"]}">{label}</text>')
        add(f'<text x="{ox}" y="378" font-family="{SANS}" font-size="22" font-weight="700" fill="{col}">{n}/{d["total"]}</text>')

    # right: bar pairs
    x0, maxw = 456, 240
    for k, b in enumerate(bars):
        y = 134 + k * 80
        pct = drop(b["before"], b["after"])
        plus = "+" if b.get("bound") == "upper" else ""
        add(f'<text x="{x0}" y="{y}" font-family="{SANS}" font-size="12" font-weight="700" fill="{c["text"]}">{esc(b["label"])}</text>')
        add(f'<text x="848" y="{y+26}" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="{c["good"]}">\u2212{pct}%{plus}</text>')
        wb = maxw
        wa = max(4, maxw * b["after"] / b["before"])
        add(f'<rect x="{x0}" y="{y+10}" width="{wb}" height="16" rx="3" fill="{c["base"]}"/>')
        add(f'<text x="{x0+wb+8}" y="{y+23}" font-family="{MONO}" font-size="11" fill="{c["muted"]}">{esc(b["before_label"])}</text>')
        add(f'<rect x="{x0}" y="{y+32}" width="{wa:.1f}" height="16" rx="3" fill="{c["good"]}"/>')
        add(f'<text x="{x0+wa+8:.1f}" y="{y+45}" font-family="{MONO}" font-size="11" font-weight="700" fill="{c["text"]}">{esc(b["after_label"])}</text>')

    add(f'<text x="32" y="398" font-family="{MONO}" font-size="10.5" fill="{c["muted"]}">{esc(DATA["footer"])}</text>')
    add("</svg>")
    (OUT / f"grounding-report-{name}.svg").write_text("\n".join(p), encoding="utf-8")


for n, c in THEMES.items():
    render(n, c)
print("rendered:", ", ".join(f"grounding-report-{n}.svg" for n in THEMES))
