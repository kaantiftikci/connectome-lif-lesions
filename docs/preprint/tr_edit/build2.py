import pdfplumber, json, re, statistics, html, pathlib, subprocess
FIG = pathlib.Path("/home/user/sinek/artifacts/figures")
figs = {1:"fig1_reserve_curves.png",2:"fig2_sensitivity.png",3:"fig3_posterior_recovery.png",4:"fig4_modulation_curves.png",
        5:"fig5_sex_comparison.png",6:"fig6_jo_retest.png",7:"fig7_pathway_boost.png",8:"fig8_parkinson_predictions.png",9:"fig9_3d_regimes.png"}

# ---------- 1. extraction ----------
def line_markup(chars):
    chars = sorted(chars, key=lambda c: (c["x0"], c["text"]))
    out = []; prev = None; cur_b = cur_i = False; last_key = None
    for c in chars:
        t = c["text"]
        key = (t, round(c["x0"], 1), round(c["x1"], 1))
        if key == last_key: continue          # duplicated ligature glyph
        last_key = key
        if t == "\xad": continue
        b = "Bold" in c["fontname"]; i = "Italic" in c["fontname"]
        if t.isspace():
            out.append(" "); prev = c; continue
        if prev is not None and not prev["text"].isspace() and c["x0"] - prev["x1"] > 0.22 * c["size"]:
            out.append(" ")
        if b != cur_b: out.append("\x02"); cur_b = b
        if i != cur_i: out.append("\x03"); cur_i = i
        out.append(t); prev = c
    if cur_i: out.append("\x03")
    if cur_b: out.append("\x02")
    s = re.sub(r" +", " ", "".join(out)).strip()
    return s

def tidy(s):
    """Convert \x02/\x03 toggles into well-formed **/* runs with spaces outside the markers."""
    for mk, tag in (("\x02", "**"), ("\x03", "*")):
        parts = s.split(mk)
        res = parts[0]
        for k in range(1, len(parts)):
            seg = parts[k]
            if k % 2 == 1:   # opening
                lead = len(seg) - len(seg.lstrip()); res += " " * lead + tag + seg.lstrip()
            else:            # closing: move trailing space of previous run outside
                if res.endswith(" "): res = res[:-1] + tag + " " + seg
                else: res += tag + seg
        s = res
    s = s.replace("** **", " ").replace("* *", " ").replace("****", "").replace("**", "\x02").replace("*", "\x03").replace("\x02", "**").replace("\x03", "*")
    return s

blocks = []
with pdfplumber.open("in.pdf") as pdf:
    for pi, p in enumerate(pdf.pages):
        page = pi + 1
        tables = p.extract_tables(); tboxes = p.find_tables()
        prev = None
        for l in p.extract_text_lines(x_tolerance=2, y_tolerance=3, return_chars=True):
            ch = [c for c in l["chars"] if c["text"].strip()]
            if not ch: continue
            size = round(statistics.median(c["size"] for c in ch), 1)
            bold = sum("Bold" in c["fontname"] for c in ch) / len(ch)
            txt = l["text"].strip()
            if size == 8.0 and (l["x0"] > 300 or "Önbaskı taslağı ·" in txt): continue
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
            last = blocks[-1] if blocks else None
            cont = False
            if last and last["type"] == typ and typ in ("title", "h2", "h3", "tcap", "p", "small", "meta"):
                if gap is not None and gap < 8.5 and not (typ in ("p", "small") and last.get("short")): cont = True
                if gap is None and typ in ("p", "small") and not last.get("short"): cont = True
                if typ == "small" and l["x0"] > 70: cont = True
            if last and last["type"] == "tcap" and typ == "p" and bold > 0.99 and gap is not None and gap < 8.5: cont = True
            if last and last["type"] == "small" and typ == "p" and gap is not None and gap < 8.5 and not re.search(r"[.!?:]$", last["text"]): cont = True
            short = l["x1"] < 505
            if cont: last["text"] += " " + m; last["short"] = short
            else: blocks.append({"type": typ, "text": m, "short": short, "page": page})
            prev = l
for b in blocks:
    if "text" in b: b["text"] = tidy(b["text"])

# split merged figure captions, merge tables with captions
out = []
for b in blocks:
    if b["type"] == "small" and b["text"].lstrip("*").startswith("Şekil"):
        parts = re.split(r"(?=\*\*Şekil \d\.)", b["text"])
        for pt in parts:
            pt = pt.strip()
            if pt: out.append({"type": "figcap", "text": pt, "page": b["page"]})
    else: out.append(b)
blocks = out

# ---------- 2. edits ----------
def strip_md(s): return s.replace("**", "")
# headings: drop bold markers (rendered bold anyway)
for b in blocks:
    if b["type"] in ("title", "h2", "h3", "author"): b["text"] = strip_md(b["text"])
# figure captions: normalise "**Şekil N.**" + italic handling
for b in blocks:
    if b["type"] == "figcap":
        t = strip_md(b["text"]).strip()
        m = re.match(r"(Şekil \d\.)\s*(.*)", t, re.S); b["num"] = int(re.search(r"\d", m.group(1)).group()); b["text"] = f"**{m.group(1)}** {m.group(2).strip()}"
        b["text"] = b["text"].replace("* Drosophila *", " *Drosophila* ").replace("*Drosophila *", "*Drosophila* ")
full = "\n".join(b.get("text", "") for b in blocks)

# first-person -> passive (exact phrases from the corrected text)
REPL = [
("hücre tipi çözünürlüğünde bir lezyon çerçevesi oluşturduk.", "hücre tipi çözünürlüğünde bir lezyon çerçevesi oluşturulmuştur."),
("Simülatörü yayımlanmış referans modelle karşılaştırarak doğruladık (nöron", "Simülatör, yayımlanmış referans modelle karşılaştırılarak doğrulanmıştır (nöron"),
("aracılığıyla nasıl etkilediğini değerlendirdik.", "aracılığıyla nasıl etkilediği değerlendirilmiştir."),
("Ancak bu özgüllüğün bir model artefaktından kaynaklandığını saptadık.", "Ancak bu özgüllüğün bir model artefaktından kaynaklandığı saptanmıştır."),
("Denediğimiz tüm koku girdileri, modeli", "Denenen tüm koku girdileri, modeli"),
("Denediğimiz tüm koku girdileri modeli aynı", "Denenen tüm koku girdileri modeli aynı"),
("her iki rejimde yeniden uyguladığımızda, hub hasarının en ağır ve antihub hasarının en hafif etki oluşturduğu sıralamayı yeniden elde ettik.", "her iki rejimde yeniden uygulandığında, hub hasarının en ağır ve antihub hasarının en hafif etki oluşturduğu sıralama yeniden elde edilmiştir."),
("tek bir APL nöronunun kaybıyla işaret değiştirebildiğini gösterdik.", "tek bir APL nöronunun kaybıyla işaret değiştirebildiği gösterilmiştir."),
("Bu çalışmada Shiu modelinin söz konusu amaçları destekleyip desteklemediğini sınadık.", "Bu çalışmada Shiu modelinin söz konusu amaçları destekleyip desteklemediği sınanmıştır."),
("Lezyon ve okuma çerçevesini, amortize edilmiş ters çıkarım modelini, dopamin-modülatör uzantısını, NeuroMechFly üzerinde bedenlenmiş davranışsal okumayı ve erkek konnektomuna yönelik uygulama hattını oluşturduk.", "Lezyon ve okuma çerçevesi, amortize edilmiş ters çıkarım modeli, dopamin-modülatör uzantısı, NeuroMechFly üzerinde bedenlenmiş davranışsal okuma ve erkek konnektomuna yönelik uygulama hattı oluşturulmuştur."),
("pekiştirme sinyalinin dopaminerjik nöronlara ulaşmadığını gösteriyoruz.", "pekiştirme sinyalinin dopaminerjik nöronlara ulaşmadığı gösterilmektedir."),
("Referans LIF modelini NumPy kullanarak yeniden uyguladık ve yayımlanmış Brian2 çıktısıyla karşılaştırdık.", "Referans LIF modeli NumPy kullanılarak yeniden uygulanmış ve yayımlanmış Brian2 çıktısıyla karşılaştırılmıştır."),
("Bizim uygulamamızda etkin olup referansta sessiz kalan", "Bu uygulamada etkin olup referansta sessiz kalan"),
("Her zaman adımında yalnızca dinlenim potansiyelinden uzaklaşmış nöronları güncellediğimiz için,", "Her zaman adımında yalnızca dinlenim potansiyelinden uzaklaşmış nöronlar güncellendiği için,"),
("Çekici durum yalnızca bizim simülatörümüze özgü değildir.", "Çekici durum yalnızca bu çalışmadaki simülatöre özgü değildir."),
("aynı 68 ORN_DM1 nöronunu 150 Hz'de 500 ms boyunca uyardığımızda,", "aynı 68 ORN_DM1 nöronu 150 Hz'de 500 ms boyunca uyarıldığında,"),
("Kendi modelimizde Kenyon hücrelerinin", "Bu çalışmanın modelinde Kenyon hücrelerinin"),
("Bu yaklaşımı biyolojik düzenlemeye daha yakın bir mekanizmayla değiştirdik:", "Bu yaklaşım, biyolojik düzenlemeye daha yakın bir mekanizmayla değiştirilmiştir:"),
("İki serbest parametreyi, koku uyaranını tek bir kompartmana ait dopaminerjik nöronların doğrudan etkinleştirilmesiyle eşleştirdiğimiz simüle edilmiş koşullanma deneyleri üzerinden ayarladık.", "İki serbest parametre, koku uyaranının tek bir kompartmana ait dopaminerjik nöronların doğrudan etkinleştirilmesiyle eşleştirildiği simüle edilmiş koşullanma deneyleri üzerinden ayarlanmıştır."),
("tüm uyaranlar altında her dopaminerjik kümenin ortalama ateşleme hızını ölçtük.", "tüm uyaranlar altında her dopaminerjik kümenin ortalama ateşleme hızı ölçülmüştür."),
("Parametre uydurma aşamasında yaptığımız gibi dopaminerjik nöronları", "Parametre uydurma aşamasında yapıldığı gibi dopaminerjik nöronları"),
("Beyin modelini NeuroMechFly v2'ye bağladık.", "Beyin modeli NeuroMechFly v2'ye bağlanmıştır."),
("simülatör çıktıları üzerinde bir ridge regresyonu vekil modeli ve nöral sonsal kestirici eğittik.", "simülatör çıktıları üzerinde bir ridge regresyonu vekil modeli ve nöral sonsal kestirici eğitilmiştir."),
("Aynı analiz hattını yayımlanmış MaleCNS v1.0 düz metin dosyaları üzerinde kurduk (164.606 izlenmiş nöron, 25,6 milyon bağlantı) ve uyaran bataryasını hücre tiplerine göre uyarladık.", "Aynı analiz hattı yayımlanmış MaleCNS v1.0 düz metin dosyaları üzerinde kurulmuş (164.606 izlenmiş nöron, 25,6 milyon bağlantı) ve uyaran bataryası hücre tiplerine göre uyarlanmıştır."),
("Bu nedenle doğrudan bir cinsiyet karşılaştırması yapmıyoruz.", "Bu nedenle doğrudan bir cinsiyet karşılaştırması yapılmamıştır."),
("Tat nöronlarından dopaminerjik kümelere uzanan yolu seyrek rejimde izledik.", "Tat nöronlarından dopaminerjik kümelere uzanan yol seyrek rejimde izlenmiştir."),
("Ardından sinyal iletimini sağlayabilecek en küçük yerel değişikliği araştırdık.", "Ardından sinyal iletimini sağlayabilecek en küçük yerel değişiklik araştırılmıştır."),
("çarpımı en yüksek olan 20 ara aktarım nöronunu belirledik.", "çarpımı en yüksek olan 20 ara aktarım nöronu belirlenmiştir."),
("Bu nöronların giriş bağlantılarını, çıkış bağlantılarını veya her ikisini k katsayısıyla ölçekledik ve hedef kümenin yanıtını fizyolojik kabul edilen 150 Hz pekiştireç sürüşünde ölçtük.", "Bu nöronların giriş bağlantıları, çıkış bağlantıları veya her ikisi k katsayısıyla ölçeklenmiş ve hedef kümenin yanıtı fizyolojik kabul edilen 150 Hz pekiştireç sürüşünde ölçülmüştür."),
("Bu nedenle konnektomda bulunan 43 oktopaminerjik nöronu ayrıca inceledik.", "Bu nedenle konnektomda bulunan 43 oktopaminerjik nöron ayrıca incelenmiştir."),
("değiştirilmemiş modelin destekleyemediği koşullanma okumasını yürüttük.", "değiştirilmemiş modelin destekleyemediği koşullanma okuması yürütülmüştür."),
("Jo'nun (2026) eğitim adımını izleyerek koku uyaranını, hayatta kalan PAM nöronlarının doğrudan 100 Hz'de etkinleştirilmesiyle eşleştirdik.", "Jo'nun (2026) eğitim adımı izlenerek koku uyaranı, hayatta kalan PAM nöronlarının doğrudan 100 Hz'de etkinleştirilmesiyle eşleştirilmiştir."),
("Jo'nun (2026) nöron kaybı kuralını dişi konnektomunda yeniden uyguladık.", "Jo'nun (2026) nöron kaybı kuralı dişi konnektomunda yeniden uygulanmıştır."),
("Bununla birlikte antihub/hub oranı bizim modelimizde 1,5–1,7 iken", "Bununla birlikte antihub/hub oranı bu modelde 1,5–1,7 iken"),
("Elde edilen örüntüyü davranış çalışmalarında iştah ve ceza belleğiyle ilişkilendirilen kompartmanlarla karşılaştırdık (Aso", "Elde edilen örüntü, davranış çalışmalarında iştah ve ceza belleğiyle ilişkilendirilen kompartmanlarla karşılaştırılmıştır (Aso"),
("kat daha yüksek ateşlemesine izin verilmesini değerlendirdik;", "kat daha yüksek ateşlemesine izin verilmesi değerlendirilmiştir;"),
("Temel analizleri; ödül kazancı, kapı sabiti κ ve plastisite hızı η parametrelerinin her birini yarıya indirip iki katına çıkararak ve acı tat ara aktarım yolunu kaldırarak (toplam sekiz parametre ayarı) yineledik.", "Temel analizler; ödül kazancı, kapı sabiti κ ve plastisite hızı η parametrelerinin her biri yarıya indirilip iki katına çıkarılarak ve acı tat ara aktarım yolu kaldırılarak (toplam sekiz parametre ayarı) yinelenmiştir."),
("Bulgularımız, bu genellemenin sınırlarından birini ortaya koymaktadır.", "Elde edilen bulgular, bu genellemenin sınırlarından birini ortaya koymaktadır."),
("Bulgularımız, konnektomların uygun olmayan", "Bu bulgular, konnektomların uygun olmayan"),
("Çalışmamızın bazı sınırlılıkları vardır.", "Bu çalışmanın bazı sınırlılıkları vardır."),
("Uygulamamız yalnızca dinlenim potansiyelinden uzaklaşmış nöronları güncellemektedir.", "Bu uygulama yalnızca dinlenim potansiyelinden uzaklaşmış nöronları güncellemektedir."),
]
missing = []
for b in blocks:
    if "text" not in b: continue
    for a, c in REPL:
        b["text"] = b["text"].replace(a, c)
for a, c in REPL:
    if a not in full: missing.append(a[:60])
print("missing replacements:", missing)

# table cell fixes
for b in blocks:
    if b["type"] == "table":
        b["rows"] = [[re.sub(r"(\d)– (\d)", r"\1–\2", (c or "").replace("\n", " ")) for c in r] for r in b["rows"]]

# remove author-contribution / AI sections and the "Şekiller" heading
res = []; skip = False
for b in blocks:
    if b["type"] == "h2":
        t = b["text"]
        if t.startswith("Yazar katkıları"): skip = True; continue
        if t.startswith("Kaynakça"): skip = False
        if t.startswith("Şekiller"): continue
    if skip: continue
    res.append(b)
blocks = res
figcaps = {b["num"]: b for b in blocks if b["type"] == "figcap"}
blocks = [b for b in blocks if b["type"] != "figcap"]
assert len(figcaps) == 9, figcaps.keys()

# place figures after anchor paragraphs
anchors = [
 ("Modelin varsayılan çalışma rejiminde 16 PPL1 nöronunun kaybı", [1]),
 ("Otuz iki dopaminerjik alt tip üzerinde yürütülen 240", [2, 3]),
 ("Denenen tüm koku girdileri modeli aynı kalıcı", [9]),
 ("Gürültü tabanları çekici durum rejiminde 1,68", [4]),
 ("APL inhibisyonu güçlendirilmişken sinaptik ölçeğin taranması", [5]),
 ("Ceza yolu bağlantı grafında mevcuttur", [7]),
 ("Jo'nun bildirdiği sıralama", [6]),
 ("Ödül yolunun modele eklenmesi,", [8]),
]
res = []; placed = set()
for b in blocks:
    res.append(b)
    if b["type"] == "p":
        for start, nums in anchors:
            if b["text"].startswith(start):
                for n in nums: res.append({"type": "figure", "num": n, "cap": figcaps[n]["text"]}); placed.add(n)
blocks = res
assert placed == set(range(1, 10)), placed

# title case (TDK) for title, h2, h3
LOWER = {"ve", "ile", "ya", "veya", "yahut", "ki", "da", "de", "mi", "mı", "mu", "mü"}
def tr_upper_first(w):
    if not w: return w
    m = re.match(r"^(\W*)(.)(.*)$", w, re.S)
    pre, c, rest = m.groups()
    up = {"i": "İ", "ı": "I"}.get(c, c.upper())
    return pre + up + rest
def title_case(s):
    words = s.split(" "); out = []
    for k, w in enumerate(words):
        core = w.strip("*")
        if k > 0 and core.lower() in LOWER: out.append(w); continue
        if re.match(r"^[A-Z0-9]", core): out.append(w); continue   # already capital / acronym
        if core and not core[0].isalpha(): out.append(w); continue
        out.append(tr_upper_first(w))
    return " ".join(out)
for b in blocks:
    if b["type"] in ("title", "h2", "h3"): b["text"] = title_case(b["text"])

# ---------- 3. HTML ----------
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s
parts = []
for b in blocks:
    t = b["type"]
    if t == "title": parts.append(f'<h1>{inline(b["text"])}</h1>')
    elif t == "author": parts.append(f'<p class="author">{inline(b["text"])}</p>')
    elif t == "meta": parts.append(f'<p class="meta">{inline(b["text"])}</p>')
    elif t == "h2": parts.append(f'<h2>{inline(b["text"])}</h2>')
    elif t == "h3": parts.append(f'<h3>{inline(b["text"])}</h3>')
    elif t == "tcap": parts.append(f'<p class="tcap">{inline(b["text"])}</p>')
    elif t == "table":
        rows = b["rows"]; h = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
        for r in rows[1:]: h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
        parts.append(h + "</tbody></table>")
    elif t == "figure":
        parts.append(f'<figure><img src="file://{FIG/figs[b["num"]]}" alt="Şekil {b["num"]}"><figcaption>{inline(b["cap"])}</figcaption></figure>')
    elif t == "small":
        cls = "ref" if blocks.index(b) > 0 and any(x["type"] == "h2" and x["text"].startswith("Kaynakça") for x in blocks[:blocks.index(b)]) else "small"
        parts.append(f'<p class="{cls}">{inline(b["text"])}</p>')
    else:
        txt = b["text"]
        if txt.startswith("Bağımsız araştırmacı"): parts.append(f'<p class="affil">{inline(txt)}</p>')
        else: parts.append(f'<p>{inline(txt)}</p>')
css = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm; }
html { font-size: 10.5pt; }
body { font-family: "Liberation Serif", "FreeSerif", serif; line-height: 1.42; color: #111; margin: 0; }
h1 { font-size: 18pt; line-height: 1.25; margin: 0 0 10pt; }
.author { font-weight: bold; margin: 0 0 2pt; }
.affil { margin: 0 0 4pt; }
.meta { font-size: 8.5pt; font-style: italic; margin: 0 0 14pt; }
h2 { font-size: 13.5pt; margin: 18pt 0 6pt; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 13pt 0 4pt; }
p { margin: 0 0 7pt; text-align: justify; }
p.tcap { margin: 8pt 0 3pt; text-align: left; }
table { border-collapse: collapse; font-size: 8.5pt; margin: 0 0 10pt; width: 100%; page-break-inside: avoid; }
th, td { border-top: 1px solid #bbb; border-bottom: 1px solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
figure { margin: 8pt 0 10pt; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 150mm; height: auto; display: block; margin: 0 auto 4pt; }
figcaption { font-size: 9pt; color: #222; text-align: justify; }
p.ref { font-size: 9pt; padding-left: 14pt; text-indent: -14pt; text-align: left; margin: 0 0 4pt; }
p.small { text-align: justify; }
"""
head = '<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Önbaskı</title><style>' + css + "</style></head><body>"
pathlib.Path("out.html").write_text(head + "\n".join(parts) + "</body></html>")
json.dump(blocks, open("blocks2.json", "w"), ensure_ascii=False, indent=0)
print("blocks", len(blocks)); print("\n".join(b["text"] for b in blocks if b["type"] in ("title", "h2", "h3")))
