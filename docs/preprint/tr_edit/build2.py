import pdfplumber, json, re, statistics, html, pathlib, subprocess, unicodedata
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
    return unicodedata.normalize("NFC", s)

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
                    blocks.append({"type": "table", "tid": (page, intab), "rows": [[unicodedata.normalize("NFC", (c or "").replace("\n", " ")) for c in r] for r in tables[intab]], "page": page})
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
    if "text" in b: b["text"] = tidy(b["text"]).replace("Sürüm: v1.0.0", "Sürüm: v1.0.1").replace("v1.0.0 sürümü", "v1.0.1 sürümü").replace("zenodo.23808330", "zenodo.23817806").replace("doi:10.5281/zenodo.23817806 adresinde arşivlenmiştir.", "doi:10.5281/zenodo.23817806 adresinde arşivlenmiştir (tüm sürümler: doi:10.5281/zenodo.23808329).")

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


# ---- Turkish coinages -> English terms (applied to body, tables, captions) ----
def attractor(m):
    cap = m.group(1) == "Ç"; suf = m.group(2); rest = m.group(3)
    word = "Attractor" if cap else "attractor"
    if re.match(r"\s(rejim|sınır|artefakt|geçiş|\(|ve seyrek)", rest) or rest == "" or suf == "" and rest.startswith(" |"): 
        return word + rest
    smap = {"": "u", "a": "una", "un": "unun", "dur": "udur", "u": "unu", "una": "una", "da": "unda", "dan": "undan", "lar": "ları"}
    return word + " durum" + smap.get(suf, suf) + rest
def terms_en(t):
    t = re.sub(r"([çÇ])ekici durum(\w*)((?:\s\S+)?)", lambda m: attractor(m), t)
    t = re.sub(r"\bdoğal pekiştireçler\b", "doğal reinforcer'lar", t)
    t = t.replace("her pekiştireçle", "her reinforcer ile").replace("pekiştirmenin değil", "reinforcement'ın değil")
    t = re.sub(r"([pP])ekiştirme sinyal", lambda m: ("R" if m.group(1) == "P" else "r") + "einforcement sinyal", t)
    t = re.sub(r"([pP])ekiştireç", lambda m: ("R" if m.group(1) == "P" else "r") + "einforcer", t)
    t = re.sub(r"\b([bB])edenlenmiş\b", lambda m: ("E" if m.group(1) == "B" else "e") + "mbodied", t)
    t = re.sub(r"\b([aA])ra aktarım\b", lambda m: ("R" if m.group(1) == "A" else "r") + "elay", t)
    t = t.replace("nöral sonsal kestirim yöntemi", "neural posterior estimation yöntemi").replace("nöral sonsal kestirici", "neural posterior estimator")
    t = t.replace("sonsal kestiricinin", "posterior estimator'ın").replace("sonsal kestirici", "posterior estimator")
    t = re.sub(r"\b([sS])onsal\b", lambda m: ("P" if m.group(1) == "S" else "p") + "osterior", t)
    t = re.sub(r"\b([öÖ])nsel\b", lambda m: ("P" if m.group(1) == "Ö" else "p") + "rior", t)
    t = re.sub(r"\b([vV])ekil\b", lambda m: ("S" if m.group(1) == "V" else "s") + "urrogate", t)
    t = re.sub(r"\b([oO])kuması\b", lambda m: ("R" if m.group(1) == "O" else "r") + "eadout'u", t)
    t = re.sub(r"\b([oO])kuma\b", lambda m: ("R" if m.group(1) == "O" else "r") + "eadout", t)
    t = t.replace("sızıntılı bütünleştir-ve-ateşle", "leaky integrate-and-fire").replace("bütünleştir-ve-ateşle", "integrate-and-fire")
    t = t.replace("ızgara aramasıyla", "grid search ile")
    t = re.sub(r"\btohumlarıyla\b", "seed'leriyle", t); t = re.sub(r"\btohumları\b", "seed'leri", t); t = re.sub(r"\btohumu\b", "seed'i", t); t = re.sub(r"\btohum\b", "seed", t)
    smap = {"sürüşünde": "drive'ında", "sürüşüne": "drive'ına", "sürüşte": "drive'da", "sürüşe": "drive'a", "sürüşü": "drive'ı", "sürüş": "drive"}
    for a, b in smap.items(): t = re.sub(r"\b" + a + r"\b", b, t)
    t = re.sub(r"\betiketli bağlantı hattı\b", "labelled line'ı", t); t = re.sub(r"\betiketli bağlantı hatları\b", "labelled line'ları", t)
    return t
for b in blocks:
    if "text" in b: b["text"] = terms_en(b["text"])
    if b["type"] == "table": b["rows"] = [[terms_en(c or "") for c in r] for r in b["rows"]]
for b in [x for x in blocks if x["type"] == "figcap"]: b["text"] = terms_en(b["text"])

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
 ("Gürültü tabanları attractor rejiminde 1,68", [4]),
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


HEADS = {
 "varsayılan rejimde ilerleyici": "Varsayılan Rejimde İlerleyici Dopaminerjik Lezyonlar",
 "koku yanıtı beyin genelinde": "Koku Yanıtında Attractor Durumu ve Seyrek Rejim",
 "dopaminin modülatör olarak": "Dopaminin Modülatör Olarak Modellenmesi",
 "reinforcer sinyalleri dopaminerjik": "Reinforcer Sinyallerinin Dopaminerjik Nöronlara İletimi",
 "embodied davranışsal readout, ters": "Embodied Readout, Ters Çıkarım ve Erkek Konnektomu",
 "reinforcer yolundaki iletim": "Reinforcer Yolunda İletim Darboğazı",
 "yapısal hasarın sıralaması": "Yapısal Hasarın İki Rejimdeki Sıralaması",
 "öğretici sinyal sağlandığında": "Öğretici Sinyal Altında Kompartman Haritası",
}
for b in blocks:
    if b["type"] == "h3":
        low = b["text"].lower()
        for k, v in HEADS.items():
            if low.startswith(k): b["text"] = v
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
def tr_upper(s): return s.replace("i", "İ").replace("ı", "I").upper()
for b in blocks:
    if b["type"] in ("title", "h3"): b["text"] = title_case(b["text"])
    if b["type"] == "h2": b["text"] = tr_upper(b["text"])

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
    elif t == "tcap":
        tt = b["text"].replace("**", ""); tt = re.sub(r"^(Tablo \d\.)", r"**\1**", tt)
        parts.append(f'<p class="tcap">{inline(tt)}</p>')
    elif t == "table":
        rows = b["rows"]; h = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
        for r in rows[1:]: h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
        parts.append(h + "</tbody></table>")
    elif t == "figure":
        parts.append(f'<figure><img src="file://{FIG/figs[b["num"]]}" alt="Şekil {b["num"]}"><figcaption>{inline(b["cap"])}</figcaption></figure>')
    elif t == "small":
        cls = "ref" if blocks.index(b) > 0 and any(x["type"] == "h2" and x["text"].startswith("Kaynakça") for x in blocks[:blocks.index(b)]) else "small"
        parts.append(f'<p class="{cls}">{inline(b["text"])}</p>')
        if b["text"].startswith("Tüm kod, sonuç tabloları"): parts.append("<p>Yazılım geliştirme, analiz betikleri ve el yazması taslağının hazırlanmasında büyük dil modeli tabanlı bir asistandan destek alınmıştır; çalışmayı yazar tasarlamış, tüm analizleri yönetip doğrulamış ve içeriğin tüm sorumluluğunu üstlenmiştir.</p>")
    else:
        txt = b["text"]
        if txt.startswith("Bağımsız araştırmacı"): parts.append(f'<p class="affil">{inline(txt)} ORCID: 0009-0004-6757-6220</p>')
        else: parts.append(f'<p>{inline(txt)}</p>')
css = """
@page { size: A4; margin: 25mm 25mm 25mm 25mm; }
html { font-size: 12pt; }
body { font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.5; color: #000; margin: 0; }
h1 { font-size: 14pt; line-height: 1.3; text-align: center; margin: 0 0 12pt; }
.author { text-align: center; font-weight: bold; margin: 0; }
.affil { text-align: center; margin: 0; font-size: 11pt; }
.meta { text-align: center; font-size: 10pt; font-style: italic; margin: 6pt 0 18pt; }
h2 { font-size: 12pt; margin: 18pt 0 6pt; text-transform: none; }
h3 { font-size: 12pt; margin: 12pt 0 6pt; }
p { margin: 0 0 6pt; text-align: justify; text-indent: 0.75cm; }
p.affil, p.author, p.meta, p.tcap, p.ref, h2 + p, h3 + p { text-indent: 0; }
p.tcap { margin: 10pt 0 4pt; text-align: left; font-size: 11pt; font-weight: normal; page-break-after: avoid; break-after: avoid; }
h2, h3 { page-break-after: avoid; break-after: avoid; }
table { border-collapse: collapse; font-size: 10pt; line-height: 1.25; margin: 0 auto 12pt; width: 100%; page-break-inside: avoid; }
th, td { border-top: 1px solid #000; border-bottom: 1px solid #000; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { border-bottom: 1px solid #000; font-weight: bold; }
figure { margin: 10pt 0 12pt; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 135mm; height: auto; display: block; margin: 0 auto 6pt; }
figcaption { font-size: 10pt; line-height: 1.3; text-align: justify; }
p.ref { font-size: 11pt; line-height: 1.3; padding-left: 1cm; text-indent: -1cm; text-align: left; margin: 0 0 6pt; }
p.small { text-align: justify; }
"""
head = '<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Önbaskı</title><style>' + css + "</style></head><body>"
pathlib.Path("out.html").write_text(head + "\n".join(parts) + "</body></html>")
json.dump(blocks, open("blocks2.json", "w"), ensure_ascii=False, indent=0)
print("blocks", len(blocks)); print("\n".join(b["text"] for b in blocks if b["type"] in ("title", "h2", "h3")))
