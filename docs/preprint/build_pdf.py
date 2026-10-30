import re, subprocess, sys, pathlib
S = pathlib.Path(sys.argv[1]); FIG = pathlib.Path("/home/user/sinek/artifacts/figures")
figs = {1:"fig1_reserve_curves.png",2:"fig2_sensitivity.png",3:"fig3_posterior_recovery.png",4:"fig4_modulation_curves.png",
        5:"fig5_sex_comparison.png",6:"fig6_jo_retest.png",7:"fig7_pathway_boost.png",8:"fig8_parkinson_predictions.png",9:"fig9_3d_regimes.png"}
def img(n): return f'<img src="file://{FIG/figs[n]}" alt="Figure {n}">'

en = (S/"en.md").read_text(); tr = (S/"tr.md").read_text()
refs = en.split("## References",1)[1].strip()

# ---------- English ----------
en = re.sub(r"^Oct \d+, 2026 · @kaan\n\n", "", en, flags=re.M)
for n in range(1,9):
    en = re.sub(r"&#91;image: Figure %d\. [^\n]*\\\]" % n, img(n), en)
fig9_en = ("Figure 9. Whole-brain spiking activity at 300 ms of a 150 Hz ORN DM1 odour, rendered from the interactive viewer "
           "(viewer/ in the repository): (A) attractor regime, intact; (B) attractor regime, PPL1 removed; (C) sparse regime (APL ×5), intact; "
           "(D) sparse regime, PPL1 removed. Points are neurons at their FlyWire soma positions, coloured by class and lit by recent spikes; "
           "in the attractor regime three quarters of the Kenyon cells (blue) are firing, in the sparse regime the odour code is confined to a few percent of them.")
en = en.replace("**Figure legends.**", img(9) + "\n\n" + fig9_en + "\n\n**Figure legends.**", 1)
en = en.replace("**Figure legends.** Figure 1.", "**Figure legends.** Figure 1.", 1)
en = re.sub(r"(the gate adapted or not adapted to the tonic level\.)\n", r"\1 " + fig9_en.replace("Figure 9. ", "Figure 9. ") + "\n", en, count=1)
# reference in the attractor section
en = en.replace("abolishes the dopaminergic effects\n\nEvery odour input tested drives the model into the same persistent state.",
                "abolishes the dopaminergic effects\n\nEvery odour input tested drives the model into the same persistent state (Figure 9A).", 1)
en = en.replace("(Figure 9A). Driving the 68 ORN\\_DM1", "(Figure 9A). Driving the 68 ORN\\_DM1")
en = re.sub(r"(Multiplying the inhibitory synapses of the two APL neurons onto Kenyon cells by 5 restores sparse coding)", r"\1 (Figure 9C)", en, count=1)

# ---------- Turkish ----------
tr = re.sub(r"^Oct \d+, 2026 · @kaan\n\n", "", tr, flags=re.M)
tr = tr.replace("Bu sekme İngilizce önbaskının Türkçe çevirisidir; şekiller ve kaynakça İngilizce sekmededir.\n\n", "", 1)
tr = tr.replace("Denenen her koku girdisi modeli aynı kalıcı duruma sokuyor.", "Denenen her koku girdisi modeli aynı kalıcı duruma sokuyor (Şekil 9A).", 1)
tr = re.sub(r"(İki APL nöronunun Kenyon hücrelerine inhibitör sinapslarını 5 ile çarpmak seyrek kodlamayı geri getiriyor)", r"\1 (Şekil 9C)", tr, count=1)
m = re.search(r"\*\*Şekiller\.\*\* Şekil 1–8 İngilizce sekmede; açıklamaları: (.*)\n", tr)
legend = m.group(1)
parts = re.split(r"(?=Şekil \d\. )", legend); parts = [p.strip() for p in parts if p.strip()]
fig9_tr = ("Şekil 9. 150 Hz ORN DM1 kokusunun 300. ms'sinde tüm-beyin spike etkinliği, depodaki etkileşimli izleyiciden (viewer/) alınmıştır: "
           "(A) çekici rejimi, sağlam; (B) çekici rejimi, PPL1 kaldırılmış; (C) seyrek rejim (APL ×5), sağlam; (D) seyrek rejim, PPL1 kaldırılmış. "
           "Noktalar FlyWire soma konumlarındaki nöronlar, sınıfa göre renklendirilmiş ve yakın zamandaki spike'larla aydınlatılmış; "
           "çekici rejiminde Kenyon hücrelerinin (mavi) dörtte üçü ateşliyor, seyrek rejimde koku kodu bunların yüzde birkaçıyla sınırlı.")
block = "## Şekiller\n\n" + "\n\n".join(img(i+1) + "\n\n" + p for i,p in enumerate(parts)) + "\n\n" + img(9) + "\n\n" + fig9_tr + "\n\n"
block += "**Şekil açıklamaları.** " + " ".join(parts) + " " + fig9_tr + "\n"
tr = tr.replace(m.group(0), block, 1)
tr = re.sub(r"## Kaynakça\n\nKaynakça İngilizce sekmededir[^\n]*\n", "## Kaynakça\n\n" + refs + "\n", tr, count=1)

css = """
@page { size: A4; margin: 22mm 20mm 24mm 20mm; }
body { font-family: "Source Serif 4", "Noto Serif", Georgia, serif; font-size: 10.5pt; line-height: 1.42; color: #111; max-width: 100%; }
h1 { font-size: 19pt; line-height: 1.25; margin: 0 0 10pt; font-weight: 700; }
h2 { font-size: 13.5pt; margin: 20pt 0 6pt; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; }
p { margin: 0 0 7pt; text-align: justify; hyphens: auto; }
table { border-collapse: collapse; font-size: 9pt; margin: 6pt 0 10pt; width: 100%; page-break-inside: avoid; }
th, td { border-top: 1px solid #bbb; border-bottom: 1px solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
img { max-width: 100%; height: auto; display: block; margin: 10pt auto 4pt; page-break-inside: avoid; }
img + p { font-size: 9pt; color: #333; text-align: left; }
h2 + p { page-break-before: avoid; }
em { font-style: italic; }
"""
for name, md in [("en", en), ("tr", tr)]:
    (S/f"{name}_build.md").write_text(md)
    (S/"style.css").write_text(css)
    subprocess.run(["pandoc", str(S/f"{name}_build.md"), "-f", "markdown+pipe_tables", "-t", "html5", "--standalone", "--metadata", "title= ",
                    "--css", str(S/"style.css"), "-o", str(S/f"{name}.html")], check=True)
    h = (S/f"{name}.html").read_text().replace('<header id="title-block-header">\n<h1 class="title"> </h1>\n</header>', "")
    h = h.replace("<title> </title>", "<title>%s</title>" % ("Preprint" if name=="en" else "Önbaskı"))
    (S/f"{name}.html").write_text(h)
print("ok")
