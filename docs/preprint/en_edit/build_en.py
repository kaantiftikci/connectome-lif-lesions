import re, html, pathlib
FIG = pathlib.Path("/home/user/sinek/artifacts/figures")
figs = {1:"fig1_reserve_curves.png",2:"fig2_sensitivity.png",3:"fig3_posterior_recovery.png",4:"fig4_modulation_curves.png",
        5:"fig5_sex_comparison.png",6:"fig6_jo_retest.png",7:"fig7_pathway_boost.png",8:"fig8_parkinson_predictions.png",9:"fig9_3d_regimes.png"}
t = pathlib.Path("en.md").read_text().replace("\\_", "_")
paras = [p.strip() for p in t.split("\n\n") if p.strip()]

# ---- first person -> passive ----
REPL = [
("We built a cell-type-resolved lesion framework on the FlyWire female connectome (138,639 neurons) and the MaleCNS male connectome (164,606 neurons), validated the simulator against the reference model (per-neuron rate correlation 0.963), and measured how progressive loss of dopaminergic clusters (PAM, PPL1, PPL2, PPM1) changes network output under a six-stimulus battery, in an embodied body model, and through an amortised inverse model that infers lesions from phenotypes.",
 "A cell-type-resolved lesion framework was built on the FlyWire female connectome (138,639 neurons) and the MaleCNS male connectome (164,606 neurons), the simulator was validated against the reference model (per-neuron rate correlation 0.963), and the effect of progressive loss of dopaminergic clusters (PAM, PPL1, PPL2, PPM1) on network output was measured under a six-stimulus battery, in an embodied body model, and through an amortised inverse model that infers lesions from phenotypes."),
("a dopamine-as-modulator layer that we fitted to conditioning data", "a dopamine-as-modulator layer fitted to conditioning data"),
("Every odour input tested drives the model into the same persistent state.", "Every odour input tested drives the model into the same persistent state (Figure 9A)."),
("Multiplying the two APL neurons' inhibitory synapses onto Kenyon cells by 5 restores sparse coding", "Multiplying the two APL neurons' inhibitory synapses onto Kenyon cells by 5 restores sparse coding (Figure 9C)"),
("every odour input we tested drives", "every odour input tested drives"),
("We conclude that connectome-constrained LIF models", "It is concluded that connectome-constrained LIF models"),
("We asked whether the Shiu model supports this.", "This study tested whether the Shiu model supports this."),
("We built the lesion and readout machinery, an amortised inverse model, a dopamine-as-modulator extension, an embodied readout in NeuroMechFly, and a male-connectome pipeline, and we report that the model's",
 "The lesion and readout machinery, an amortised inverse model, a dopamine-as-modulator extension, an embodied readout in NeuroMechFly, and a male-connectome pipeline were built, and it is reported that the model's"),
("Our NumPy re-implementation of the reference LIF model reproduces", "The NumPy re-implementation of the reference LIF model reproduces"),
("The attractor is not a property of our simulator.", "The attractor is not a property of the present simulator."),
("We replaced this with the biological arrangement:", "This was replaced with the biological arrangement:"),
("We fitted the two free parameters by simulated conditioning, pairing odour with", "The two free parameters were fitted by simulated conditioning, pairing odour with"),
("We measured the mean firing rate of each cluster under every stimulus of the battery, in both regimes.", "The mean firing rate of each cluster was measured under every stimulus of the battery, in both regimes."),
("at any synaptic scale we tested,", "at any synaptic scale tested,"),
("as we did for the parameter fit,", "as was done for the parameter fit,"),
("We traced the route from gustatory neurons to the dopaminergic clusters in the sparse regime.", "The route from gustatory neurons to the dopaminergic clusters was traced in the sparse regime."),
("We then asked for the smallest local change that conducts.", "The smallest local change that conducts was then sought."),
("Taking the 20 relays with the largest product of input from the active set and output onto the target cluster, we scaled the input hop, the output hop or both by a factor k and measured the target cluster",
 "Taking the 20 relays with the largest product of input from the active set and output onto the target cluster, the input hop, the output hop or both were scaled by a factor k and the target cluster was measured"),
("so we looked at the 43 octopaminergic neurons of the connectome directly.", "so the 43 octopaminergic neurons of the connectome were examined directly."),
("With the punishment pathway restored (both hops 4-fold), we ran the conditioning readout", "With the punishment pathway restored (both hops 4-fold), the conditioning readout was run"),
("Following the training step of Jo (2026), we paired the odour with direct 100 Hz drive of the surviving PAM neurons and measured the learning index",
 "Following the training step of Jo (2026), the odour was paired with direct 100 Hz drive of the surviving PAM neurons and the learning index was measured"),
("We added the reward route as a single extrasynaptic term, the mean rate of the sugar gustatory neurons times 0.5 added to the effective dopamine rate of every surviving PAM neuron (the octopaminergic signal the connectome lacks), kept the 4-fold relay route for bitter taste, and paired the odour with each reinforcer",
 "The reward route was added as a single extrasynaptic term, the mean rate of the sugar gustatory neurons times 0.5 added to the effective dopamine rate of every surviving PAM neuron (the octopaminergic signal the connectome lacks), the 4-fold relay route for bitter taste was kept, and the odour was paired with each reinforcer"),
("not by us, and can be compared", "not by prior choice, and can be compared"),
("We ran the protocol at two operating points, the sparse regime (APL ×5, 7 MBON types respond to the odour) and an intermediate one (APL ×3, 20 % of Kenyon cells active, 12 MBON types respond), and measured the learning index",
 "The protocol was run at two operating points, the sparse regime (APL ×5, 7 MBON types respond to the odour) and an intermediate one (APL ×3, 20 % of Kenyon cells active, 12 MBON types respond), and the learning index was measured"),
("and we count it as a model artefact.", "and it is counted as a model artefact."),
("whose inhibition of Kenyon cells we strengthened to obtain", "whose inhibition of Kenyon cells was strengthened to obtain"),
("To test whether the attractor also compromises published lesion results, we re-ran the neuron-loss rule of Jo (2026) on the female connectome:",
 "To test whether the attractor also compromises published lesion results, the neuron-loss rule of Jo (2026) was re-run on the female connectome:"),
("is, we suggest, the same attractor", "is, it is suggested, the same attractor"),
("We coupled the brain model to NeuroMechFly v2 by mapping", "The brain model was coupled to NeuroMechFly v2 by mapping"),
("We trained a ridge surrogate and a neural posterior estimator on simulator pairs to infer lesions from phenotypes.", "A ridge surrogate and a neural posterior estimator were trained on simulator pairs to infer lesions from phenotypes."),
("We built the same pipeline on MaleCNS v1.0 from the released flat files (164,606 traced neurons, 25.6 million edges) and carried the stimulus battery across by cell type.",
 "The same pipeline was built on MaleCNS v1.0 from the released flat files (164,606 traced neurons, 25.6 million edges) and the stimulus battery was carried across by cell type."),
("We therefore report no clean sex comparison:", "No clean sex comparison is therefore reported:"),
("Our results mark one boundary of that range.", "The present results mark one boundary of that range."),
("Taken at the default operating point, our lesion experiment yields", "Taken at the default operating point, the lesion experiment yields"),
("Our own study inherits limitations.", "The present study inherits limitations."),
("The compartment identities we use are connectivity-based, and we have not asserted their correspondence to the classical Greek compartment names.",
 "The compartment identities used here are connectivity-based, and their correspondence to the classical Greek compartment names has not been asserted."),
("Our implementation updates only neurons away from rest", "The implementation updates only neurons away from rest"),
]
full = "\n\n".join(paras)
for a, b in REPL:
    assert a in full, a[:70]
paras = [p for p in paras]
for i, p in enumerate(paras):
    for a, b in REPL: p = p.replace(a, b)
    paras[i] = p
left = [m.group(0) for p in paras for m in re.finditer(r"[^.]*\b(We|we|Our|our|us)\b[^.]*\.", p)]
print("remaining first person:", left)

# ---- structure ----
blocks = []
for p in paras:
    if p.startswith("# "): blocks.append(("title", p[2:])); continue
    if re.match(r"^Oct \d+, 2026 · @kaan$", p): continue
    if p.startswith("## "): blocks.append(("h2", p[3:])); continue
    if p.startswith("### "): blocks.append(("h3", p[4:])); continue
    if p.startswith("| "): blocks.append(("table", p)); continue
    if p.startswith("&#91;image:"): continue
    blocks.append(("p", p))
# drop author/AI section, Figures section, keep legends
out = []; skip = False; legends = None
for typ, txt in blocks:
    if typ == "h2":
        if txt.startswith("Author contributions"): skip = True; continue
        if txt.startswith("References"): skip = False
        if txt.startswith("Figures"): skip = True; continue
        if txt.startswith("Data, code"): skip = False
    if skip:
        if typ == "p" and txt.startswith("**Figure legends.**"): legends = txt
        continue
    out.append((typ, txt))
blocks = out
caps = {}
for m in re.finditer(r"Figure (\d)\. (.*?)(?= Figure \d\. |$)", legends.replace("**Figure legends.** ", ""), re.S):
    caps[int(m.group(1))] = f"**Figure {m.group(1)}.** {m.group(2).strip()}"
caps[9] = ("**Figure 9.** Whole-brain spiking activity at 300 ms of a 150 Hz ORN DM1 odour, rendered from the interactive viewer (viewer/ in the repository): "
           "(A) attractor regime, intact; (B) attractor regime, PPL1 removed; (C) sparse regime (APL ×5), intact; (D) sparse regime, PPL1 removed. "
           "Points are neurons at their FlyWire soma positions, coloured by class and lit by recent spikes; in the attractor regime three quarters of the Kenyon cells (blue) are firing, "
           "in the sparse regime the odour code is confined to a few percent of them.")
assert len(caps) == 9, caps.keys()

# split into sections and reorder results
def sections(blocks):
    secs = []; cur = None
    for typ, txt in blocks:
        if typ in ("h2", "h3"): cur = [(typ, txt)]; secs.append(cur)
        elif cur is None: secs.append([(typ, txt)])
        else: cur.append((typ, txt))
    return secs
secs = sections(blocks)
def find(prefix): return next(i for i, s in enumerate(secs) if s[0][0] in ("h2", "h3") and s[0][1].startswith(prefix))
emb = secs.pop(find("Embodiment, inverse inference")); secs.insert(find("Where the reinforcer pathway fails"), emb)
st = secs.pop(find("Structural damage ranks")); secs.insert(find("What the wiring predicts"), st)
blocks = [b for s in secs for b in s]

# methods lead-ins -> h3
METH = {"Connectome data": "Connectome Data", "Network model": "Network Model", "Lesions": "Lesions", "Stimulus battery and phenotype": "Stimulus Battery and Phenotype",
        "Modulation layer": "Modulation Layer", "Embodiment": "Embodied Simulation", "Inference": "Inverse Inference", "Reinforcer pathway": "Reinforcer Pathway Analysis",
        "Neuron-loss re-test": "Neuron-Loss Protocol Re-Test", "Teaching-signal routes and Parkinson protocols": "Teaching-Signal Routes and Parkinson Protocols", "Reproducibility": "Reproducibility"}
out = []; inmeth = False
for typ, txt in blocks:
    if typ == "h2": inmeth = txt.startswith("Methods")
    if inmeth and typ == "p":
        m = re.match(r"\*\*(.+?)\.\*\*\s*(.*)", txt, re.S)
        if m and m.group(1) in METH:
            out.append(("h3", METH[m.group(1)]))
            body = m.group(2)
            if m.group(1) == "Connectome data":
                f, male = body.split(" Male: ", 1)
                out.append(("p", "**Female connectome:** " + f.replace("Female: ", "", 1))); out.append(("p", "**Male connectome:** " + male)); continue
            out.append(("p", body)); continue
    out.append((typ, txt))
blocks = out

# table captions
TCAP = {"Dopaminergic subtype": "Direct connections between dopaminergic subtypes and the most strongly affected output neurons.",
        "Group, 100 % loss": "Phenotype distances at complete loss of the PPL1 and PAM clusters.",
        "Stimulus": "Mean firing rates (Hz) of the PAM and PPL1 clusters by stimulus.",
        "Reinforcer to target": "Effect of strengthening relay connections on the dopaminergic cluster response.",
        "Regime": "Effects of neuron loss under the hub, shuffled and antihub maps.",
        "Operating point": "MBON learning responses after sugar pairing."}
out = []; tn = 0
for typ, txt in blocks:
    if typ == "table":
        first = txt.split("|")[1].strip(); tn += 1
        out.append(("tcap", f"**Table {tn}.** {TCAP[first]}"))
    out.append((typ, txt))
blocks = out

# figures after anchors
ANCH = [("In the model's default regime", [1]), ("A sweep over 240 lesions", [2, 3]), ("Every odour input tested drives", [9]), ("Noise floors 1.68", [4]),
        ("**Male connectome.**", [5]), ("The punishment pathway exists in the wiring", [7]), ("The ordering reported by Jo", [6]), ("With the reward route supplied", [8])]
out = []; placed = set()
for typ, txt in blocks:
    out.append((typ, txt))
    if typ == "p":
        for a, nums in ANCH:
            if txt.startswith(a):
                for n in nums: out.append(("figure", n)); placed.add(n)
assert placed == set(range(1, 10)), placed
blocks = out

# headings
H3 = {"Simulator validation": "Simulator Validation and Lesion Framework", "Progressive dopaminergic lesions": "Progressive Dopaminergic Lesions in the Default Regime",
      "The odour response": "Attractor State in the Odour Response and the Sparse Regime", "Treating dopamine": "Modelling Dopamine as a Modulator",
      "Reinforcers never reach": "Conduction of Reinforcer Signals to Dopaminergic Neurons", "Embodiment, inverse": "Embodied Readout, Inverse Inference and the Male Connectome",
      "Where the reinforcer pathway": "Conduction Bottleneck in the Reinforcer Pathway", "Structural damage": "Ranking of Structural Damage across the Two Regimes",
      "What the wiring predicts": "Compartment Map under a Teaching Signal", "Predictions for fly models": "Predictions for *Drosophila* Models of Parkinson's Disease"}
SMALL = {"a","an","the","and","or","of","in","on","for","to","with","by","at","under","across","as","but","nor","from","its"}
def tcase(s):
    w = s.split(" "); r = []
    for k, x in enumerate(w):
        core = x.strip("*")
        if k and core.lower() in SMALL: r.append(x); continue
        if core[:1].isupper() or core[:1] == "*": 
            r.append(x if core[:1] != "*" else x); continue
        r.append(x[0].upper() + x[1:])
    return " ".join(r)
out = []
for typ, txt in blocks:
    if typ == "h3":
        for k, v in H3.items():
            if txt.startswith(k): txt = v
        txt = tcase(txt)
    if typ == "h2": txt = txt.upper()
    if typ == "title": txt = tcase(txt).replace("Drosophila", "*Drosophila*").replace("Connectome-constrained", "Connectome-Constrained").replace("Simulation-based", "Simulation-Based").replace(": the Limits", ": The Limits")
    out.append((typ, txt))
blocks = out

# ---- html ----
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s); s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s
def table_html(md):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in md.split("\n") if ln.strip() and not re.match(r"^\|?\s*-", ln)]
    h = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
    for r in rows[1:]: h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
    return h + "</tbody></table>"
parts = []; inrefs = False
for typ, txt in blocks:
    if typ == "title": parts.append(f"<h1>{inline(txt)}</h1>")
    elif typ == "h2": inrefs = txt.startswith("REFERENCES"); parts.append(f"<h2>{inline(txt)}</h2>")
    elif typ == "h3": parts.append(f"<h3>{inline(txt)}</h3>")
    elif typ == "tcap": parts.append(f'<p class="tcap">{inline(txt)}</p>')
    elif typ == "table": parts.append(table_html(txt))
    elif typ == "figure": parts.append(f'<figure><img src="file://{FIG/figs[txt]}" alt="Figure {txt}"><figcaption>{inline(caps[txt])}</figcaption></figure>')
    else:
        if txt.startswith("**Kaan Tiftikçi**"): parts.append(f'<p class="author">Kaan Tiftikçi</p>')
        elif txt.startswith("Independent researcher"): parts.append(f'<p class="affil">{inline(txt)}</p>')
        elif txt.startswith("*Preprint draft"): parts.append(f'<p class="meta">{inline(txt.strip("*"))}</p>')
        elif inrefs: parts.append(f'<p class="ref">{inline(txt)}</p>')
        else: parts.append(f"<p>{inline(txt)}</p>")
css = pathlib.Path("../tr2/build2.py").read_text().split('css = """')[1].split('"""')[0]
head = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Preprint</title><style>' + css + "</style></head><body>"
pathlib.Path("out.html").write_text(head + "\n".join(parts) + "</body></html>")
print("\n".join(txt for typ, txt in blocks if typ in ("title", "h2", "h3")))
