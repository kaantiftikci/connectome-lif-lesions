import pdfplumber, json, re, statistics
BODY_X0 = 63.9
def line_markup(chars):
    """Rebuild a line's text from chars with **bold** and *italic* runs; insert spaces by x gaps."""
    chars = sorted(chars, key=lambda c: c["x0"])
    out = []; prev = None; cur_b = cur_i = False
    for c in chars:
        t = c["text"]
        if t == "\xad": continue
        b = "Bold" in c["fontname"]; i = "Italic" in c["fontname"]
        if t.isspace():
            out.append(" "); prev = c; continue
        if prev is not None and not prev["text"].isspace() and c["x0"] - prev["x1"] > 0.22 * c["size"]:
            out.append(" ")
        if b != cur_b: out.append("**"); cur_b = b
        if i != cur_i: out.append("*"); cur_i = i
        out.append(t); prev = c
    if cur_i: out.append("*")
    if cur_b: out.append("**")
    s = "".join(out)
    s = re.sub(r" +", " ", s).strip()
    # move markers off spaces: "** text**" -> "**text**"
    s = re.sub(r"\*\* ", " **", s); s = re.sub(r" \*\*(\W)", r"** \1", s)
    s = s.replace("** **", " ").replace("* *", " ")
    return s
blocks = []
with pdfplumber.open("in.pdf") as pdf:
    for pi, p in enumerate(pdf.pages):
        page = pi + 1
        tables = p.extract_tables()
        tboxes = [t for t in p.find_tables()]
        lines = p.extract_text_lines(x_tolerance=2, y_tolerance=3, return_chars=True)
        prev = None
        for l in lines:
            ch = [c for c in l["chars"] if c["text"].strip()]
            if not ch: continue
            size = round(statistics.median(c["size"] for c in ch), 1)
            bold = sum("Bold" in c["fontname"] for c in ch) / len(ch)
            txt = l["text"].strip()
            # running head / footer
            if size == 8.0 and (l["x0"] > 300 or "Önbaskı taslağı ·" in txt): continue
            # inside a table bbox?
            intab = None
            for ti, tb in enumerate(tboxes):
                x0, top, x1, bottom = tb.bbox
                if top - 2 <= l["top"] <= bottom + 2: intab = ti
            if intab is not None:
                if not blocks or blocks[-1].get("type") != "table" or blocks[-1].get("tid") != (page, intab):
                    blocks.append({"type": "table", "tid": (page, intab), "rows": tables[intab], "page": page})
                prev = l; continue
            gap = l["top"] - prev["bottom"] if prev else None
            m = line_markup(l["chars"])
            if size >= 19: typ = "title"
            elif size == 15.0: typ = "h2"
            elif size == 12.0 and bold > 0.9: typ = "h3"
            elif size == 8.5: typ = "meta"
            elif size == 9.0: typ = "small"
            elif size == 10.0 and bold > 0.99 and txt.startswith("Tablo"): typ = "tcap"
            elif size == 10.0 and bold > 0.99 and txt == "Kaan Tiftikçi": typ = "author"
            else: typ = "p"
            # continuation?
            last = blocks[-1] if blocks else None
            cont = False
            if last and last["type"] == typ and typ in ("title", "h2", "h3", "tcap", "p", "small", "meta"):
                if gap is not None and gap < 8.5 and not (typ in ("p", "small") and last.get("short")):
                    cont = True
                if gap is None and typ in ("p", "small") and not last.get("short") and not last.get("endpage_short"):
                    cont = True  # page break inside paragraph
                if typ == "small" and l["x0"] > 70: cont = True  # reference continuation (hanging indent)
                if typ == "small" and l["x0"] < 70 and last.get("ref") : cont = False
            short = l["x1"] < 505
            if cont:
                last["text"] += " " + m; last["short"] = short
            else:
                blocks.append({"type": typ, "text": m, "short": short, "page": page, "x0": round(l["x0"], 1)})
            prev = l
json.dump(blocks, open("blocks.json", "w"), ensure_ascii=False, indent=0)
md = []
for b in blocks:
    if b["type"] == "table":
        rows = [[(c or "").replace("\n", " ") for c in r] for r in b["rows"]]
        md.append("| " + " | ".join(rows[0]) + " |\n|" + "---|" * len(rows[0]) + "\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows[1:]))
    else:
        tag = {"title": "# ", "h2": "## ", "h3": "### ", "author": "", "meta": "", "tcap": "", "p": "", "small": ""}[b["type"]]
        md.append(f"<!--{b['type']} p{b['page']}-->\n{tag}{b['text']}")
open("draft.md", "w").write("\n\n".join(md))
from collections import Counter
print(Counter(b["type"] for b in blocks)); print(len(open("draft.md").read()))
