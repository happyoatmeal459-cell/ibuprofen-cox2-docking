"""
Evaluation of Ibuprofen–COX-2 Binding Interaction Using Molecular Docking
An educational computational study — Streamlit front end.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import data
from viewer import viewer_html

st.set_page_config(page_title="Decoding the COX-2–Ibuprofen Interaction",
                   page_icon="🧬", layout="wide",
                   initial_sidebar_state="expanded")

CSS = """
<style>
.block-container{padding-top:2.2rem;max-width:1180px}
h1,h2,h3{font-family:"Source Serif 4",Georgia,serif}
.hero{background:linear-gradient(170deg,#0c1a24,#12303a 60%,#0e3a42);
      border-radius:18px;padding:34px 34px 30px;color:#dbe7ee;margin-bottom:8px}
.hero h1{color:#fff;font-size:2.3rem;margin:.2em 0 .25em;line-height:1.15}
.hero p{color:#9fc3cc;font-size:1.05rem;margin:0;max-width:60ch}
.tag{display:inline-block;font-size:.72rem;letter-spacing:.11em;text-transform:uppercase;
     color:#7fdbe0;border:1px solid #2a5560;border-radius:999px;padding:4px 12px}
.card{background:var(--background-color);border:1px solid rgba(128,150,165,.28);
      border-radius:14px;padding:18px 20px;height:100%}
.card h4{margin:0 0 .4em;font-size:1rem}
.card p{font-size:.92rem;opacity:.85;margin:0}
.res{display:inline-block;border:1px solid rgba(128,150,165,.35);border-radius:10px;
     padding:7px 11px;margin:0 7px 7px 0;font-size:.85rem;text-align:center}
.res.hot{border-color:#0e7c86;background:rgba(14,124,134,.12);font-weight:600}
.big{font-family:"Source Serif 4",Georgia,serif;font-size:3rem;font-weight:600;
     color:#0e7c86;line-height:1}
.eyebrow{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;
         color:#0e7c86;font-weight:600}
footer,#MainMenu{visibility:hidden}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def eyebrow(n: int, title: str) -> None:
    st.markdown(f"<div class='eyebrow'>Section {n}</div>", unsafe_allow_html=True)
    st.header(title, anchor=False)


def card(title: str, body: str) -> None:
    st.markdown(f"<div class='card'><h4>{title}</h4><p>{body}</p></div>",
                unsafe_allow_html=True)


# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.subheader("3D viewer controls")
    style = st.radio("Receptor representation", ["cartoon", "sticks", "hidden"],
                     format_func=lambda s: {"cartoon": "Cartoon", "sticks": "Sticks",
                                            "hidden": "Ligand only"}[s],
                     key="style")
    surface = st.checkbox("Molecular surface", value=False,
                          disabled=style != "cartoon")
    pocket = st.checkbox("Show binding-pocket residues", value=False,
                         disabled=style == "hidden")
    ligands = st.radio("Ligand display",
                       ["pose", "exp", "both"],
                       format_func=lambda s: {"pose": "Predicted pose (Vina)",
                                              "exp": "Experimental ibuprofen (4PH9)",
                                              "both": "Overlay both"}[s])
    spin = st.checkbox("Rotate", value=False)
    mode_n = st.select_slider("Pose shown (docking mode)",
                              options=list(range(1, len(data.scores()) + 1)), value=1)
    st.caption("Drag to rotate · scroll to zoom · right-drag to pan. "
               "Use “Reset view” by changing any control above.")
    st.divider()
    st.caption("Educational computational study. Nothing shown here is an "
               "experimental binding measurement.")

poses = data.docked_poses()
near4 = data.nearby_residues(4.0, mode_n)
near35 = data.nearby_residues(3.5, mode_n)
hot = {r[1] for r in near35}

# -------------------------------------------------------------------- hero
left, right = st.columns([1, 1], gap="large")
with left:
    st.markdown(
        "<div class='hero'><span class='tag'>In-silico structural study</span>"
        "<h1>Decoding the COX-2–Ibuprofen Interaction</h1>"
        "<p>An in-silico molecular docking study using AutoDock Vina.</p></div>",
        unsafe_allow_html=True)
    st.caption("Structures are rendered from the supplied experimental and docking "
               "files. The visualisation illustrates geometry only — it does not "
               "demonstrate or measure binding affinity.")
with right:
    components.html(
        viewer_html(data.receptor_pdb(), poses[mode_n - 1][1],
                    data.experimental_ligand_pdb(), [r[1] for r in near4],
                    style=style, surface=surface, show_pocket=pocket,
                    ligands=ligands, spin=spin, height=420),
        height=436)
    st.caption(f"COX-2 (PDB 4PH9, chain A) · ibuprofen, docking mode {mode_n} "
               f"({poses[mode_n - 1][0]:.3f} kcal/mol)")

st.divider()

# --------------------------------------------------------- 1. about
eyebrow(1, "About the study")
c1, c2 = st.columns(2, gap="medium")
with c1:
    card("Cyclooxygenase-2 (COX-2)",
         "COX-2 is an enzyme that converts arachidonic acid into prostaglandin "
         "precursors. Its activity is associated with inflammatory signalling, which "
         "makes its substrate channel a well-studied target for structural and "
         "computational work.")
    st.write("")
    card("Why molecular docking",
         "Docking predicts how a small molecule may be positioned inside a protein "
         "pocket and ranks candidate poses with a scoring function. It is a fast, "
         "hypothesis-generating method: the output is a computational prediction, "
         "not a laboratory measurement.")
with c2:
    card("Ibuprofen",
         "Ibuprofen is a small carboxylic-acid-containing molecule belonging to the "
         "non-steroidal anti-inflammatory drug class. It is small, flexible at a few "
         "rotatable bonds, and has an experimentally determined bound structure in "
         "the COX-2 entry used here.")
    st.write("")
    card("What this project investigates",
         "An independently prepared ibuprofen molecule was docked into the COX-2 "
         "substrate channel defined from chain A of PDB 4PH9. The predicted pose, its "
         "Vina score, and the residues surrounding it were then examined, with the "
         "experimentally observed ligand in 4PH9 used as a structural reference.")

st.divider()

# --------------------------------------------------------- 2. workflow
eyebrow(2, "The docking workflow")
STEPS = [
    ("Protein structure selection",
     "PDB 4PH9, an experimentally determined structure of ibuprofen-bound COX-2, was "
     "selected as the structural reference for the target."),
    ("Receptor preparation",
     "Protein atoms of chain A were extracted and prepared as a rigid receptor with "
     "Meeko. Heteroatom components were excluded at this stage."),
    ("Ligand preparation",
     "An ibuprofen structure was prepared independently of the coordinates already "
     "present in 4PH9, giving the rotatable-bond definition and charges used by Vina."),
    ("Binding-site definition",
     "A search box centred at 13.578, 23.024, 25.205 Å with dimensions "
     "17.917 × 15.932 × 13.624 Å was placed over the ibuprofen-binding region of the "
     "experimental structure."),
    ("Molecular docking",
     "AutoDock Vina 1.2.7 was run with exhaustiveness 8 and nine requested modes, "
     "producing nine ranked candidate poses."),
    ("Pose analysis",
     "The top-ranked pose was inspected in PyMOL, and residues lying within "
     "approximately 4 Å and 3.5 Å of the ligand were listed."),
    ("Experimental-reference comparison",
     "The predicted pose was viewed alongside the experimentally observed ibuprofen "
     "of 4PH9, which serves as a structural point of reference."),
]
for i, (title, body) in enumerate(STEPS, 1):
    with st.expander(f"{i}.  {title}", expanded=(i == 1)):
        st.write(body)

st.divider()

# --------------------------------------------------------- 3. 3D structure
eyebrow(3, "Interactive 3D structure")
st.write("Rendered directly from the supplied files: chain A of `4PH9.pdb` as the "
         "receptor, the selected pose from `ibuprofen_COX2_docked.pdbqt` as the "
         "predicted ligand, and the IBP heteroatom record of 4PH9 chain A as the "
         "experimental reference. Coordinates are unmodified. Use the sidebar for "
         "cartoon / surface / sticks / ligand-only / pocket / rotate controls.")
components.html(
    viewer_html(data.receptor_pdb(), poses[mode_n - 1][1],
                data.experimental_ligand_pdb(), [r[1] for r in near4],
                style=style, surface=surface, show_pocket=pocket,
                ligands=ligands, spin=spin, height=560),
    height=576)

st.divider()

# --------------------------------------------------------- 4. parameters
eyebrow(4, "Docking parameters")
P = data.PARAMS
a, b, c = st.columns(3, gap="medium")
with a:
    st.metric("Receptor", P["receptor"])
    st.metric("PDB ID", P["pdb_id"])
    st.metric("Chain used", P["chain"])
with b:
    st.metric("Ligand", P["ligand"])
    st.metric("Docking software", P["software"])
    st.metric("Preparation / analysis", f'{P["preparation"]} / {P["analysis"]}')
with c:
    st.metric("Exhaustiveness", P["exhaustiveness"])
    st.metric("Number of modes", P["num_modes"])
    st.metric("Receptor treatment", "Rigid")

g1, g2 = st.columns(2, gap="medium")
with g1:
    st.dataframe(pd.DataFrame(
        {"Axis": ["X", "Y", "Z"], "Grid centre (Å)": list(P["center"])}),
        hide_index=True, use_container_width=True)
with g2:
    st.dataframe(pd.DataFrame(
        {"Axis": ["X", "Y", "Z"], "Grid size (Å)": list(P["size"])}),
        hide_index=True, use_container_width=True)
st.caption("The box was centred on the ibuprofen-binding region of the experimental "
           "structure, so the search space covers the COX-2 substrate channel rather "
           "than the whole protein.")

st.divider()

# --------------------------------------------------------- 5. results
eyebrow(5, "Docking results")
best = poses[0][0]
r1, r2 = st.columns([1, 2], gap="large")
with r1:
    st.markdown("<div class='eyebrow'>Best-ranked docking pose</div>"
                f"<div class='big'>−{abs(best):.3f}<span style='font-size:1.1rem;"
                "opacity:.7'> kcal/mol</span></div>"
                "<div style='color:#0e7c86;font-weight:600;font-size:.85rem'>"
                "Vina docking score · Mode 1</div>", unsafe_allow_html=True)
with r2:
    st.warning("This value is a computational scoring estimate generated by AutoDock "
               "Vina and should not be interpreted as an experimentally measured "
               "binding affinity.", icon="⚠️")

df = pd.DataFrame({"Mode": range(1, len(poses) + 1),
                   "Vina score (kcal/mol)": [s for s, _ in poses]})
t1, t2 = st.columns([1, 1], gap="large")
with t1:
    st.dataframe(df.style.format({"Vina score (kcal/mol)": "{:.3f}"}),
                 hide_index=True, use_container_width=True)
with t2:
    st.bar_chart(df.set_index("Mode"), height=320)
st.caption("Values are read directly from the REMARK VINA RESULT lines of "
           "`ibuprofen_COX2_docked.pdbqt` and are shown unrounded.")

st.divider()

# --------------------------------------------------------- 6. binding pocket
eyebrow(6, "Binding pocket")
st.write(f"Residues of chain A lying within the stated distances of the mode "
         f"{mode_n} pose, computed from `receptor_A.pdbqt`.")
st.markdown(f"**Nearby residues (≈ 4 Å) — {len(near4)} residues**")
st.markdown("".join(
    f"<span class='res{' hot' if resid in hot else ''}'>{name}<br>"
    f"<small style='opacity:.7'>{resid}</small></span>"
    for name, resid in near4), unsafe_allow_html=True)
st.markdown(f"**Focused close contacts (≈ 3.5 Å) — {len(near35)} residues**")
st.markdown("".join(
    f"<span class='res hot'>{name}<br><small style='opacity:.7'>{resid}</small></span>"
    for name, resid in near35), unsafe_allow_html=True)
st.info("**How to read this.** These are computationally identified nearby residues "
        "derived from the predicted pose — they are not experimentally validated "
        "interaction residues. The PyMOL visualisation showed a close contact of "
        "approximately 3.4 Å, but this was not independently validated as a hydrogen "
        "bond by donor/acceptor geometry, so no hydrogen bonds are claimed here.")

st.divider()

# --------------------------------------------------------- 7. exp vs predicted
eyebrow(7, "Experimental vs predicted")
e1, e2 = st.columns(2, gap="large")
with e1:
    st.image(str(data.figure_path(6)),
             caption="Figure 6. Comparison of the predicted docked ibuprofen pose "
                     "with experimentally observed ibuprofen.",
             use_container_width=True)
with e2:
    st.write("The experimentally observed ligand position in PDB 4PH9 provides a "
             "structural reference for comparison with the independently docked ligand.")
    st.dataframe(pd.DataFrame({
        "Entity": ["Experimental ibuprofen (IBP) in 4PH9",
                   "Independently prepared ibuprofen",
                   "Vina mode 1 pose"],
        "Role": ["Structural reference", "Docking input", "Prediction"]}),
        hide_index=True, use_container_width=True)
    st.warning("The experimental ligand in 4PH9 is a structural reference only. It is "
               "not the output of this docking calculation, and no RMSD or other "
               "quantitative agreement value was calculated, so none is reported.",
               icon="⚠️")
    st.caption("Select “Overlay both” in the sidebar to see the two ligands together "
               "in the 3D viewer.")

st.divider()

# --------------------------------------------------------- 8. figures
eyebrow(8, "Figures")
st.write("Figures produced during structural analysis in PyMOL and from the Vina output.")
cols = st.columns(2, gap="medium")
for i, (label, caption) in enumerate(data.FIGURE_CAPTIONS):
    with cols[i % 2]:
        st.image(str(data.figure_path(i + 1)), caption=f"{label}. {caption}",
                 use_container_width=True)

st.divider()

# --------------------------------------------------------- 9. methodology
eyebrow(9, "Methodology")
m1, m2 = st.columns(2, gap="medium")
with m1:
    card("Protein",
         "PDB 4PH9 was selected as the structural reference for COX-2. The entry is an "
         "experimentally determined structure of ibuprofen-bound COX-2, and it was used "
         "both as the structural reference and to define the docking region.")
    st.write("")
    card("Ligand preparation",
         "Ibuprofen was independently prepared for docking using Meeko, rather than "
         "being taken from the ligand coordinates already present in the experimental "
         "entry.")
with m2:
    card("Receptor preparation",
         "Chain A protein atoms were prepared as a rigid receptor using Meeko. "
         "Heteroatom components were excluded during receptor preparation.")
    st.write("")
    card("Docking",
         "AutoDock Vina 1.2.7 was used with the search-space centre "
         "(13.578, 23.024, 25.205 Å) and dimensions (17.917 × 15.932 × 13.624 Å), an "
         "exhaustiveness of 8, and nine requested binding modes.")
st.write("")
card("Analysis",
     "PyMOL was used to inspect the predicted pose, the residues near it, close "
     "contacts, and the comparison with the experimental ligand position. For this "
     "application the supplied PDBQT poses are converted to PDB-format records for "
     "browser rendering; only the record formatting changes and every atomic "
     "coordinate is carried over unmodified.")

st.divider()

# --------------------------------------------------------- 10. limitations
eyebrow(10, "Limitations")
for line in [
    "Docking scores are computational estimates.",
    "Docking does not experimentally measure binding affinity.",
    "Protein flexibility is simplified because the receptor was treated as rigid.",
    "The receptor preparation used protein atoms from chain A and excluded heteroatom "
    "components.",
    "Nearby residues identified computationally should not automatically be "
    "interpreted as experimentally confirmed interactions.",
    "The experimental 4PH9 ligand is a structural reference, not the output of the new "
    "docking calculation.",
    "Docking results depend on receptor preparation, ligand preparation, search-space "
    "definition, scoring function, and sampling parameters.",
]:
    st.markdown(f"- {line}")

st.divider()

# --------------------------------------------------------- 11. conclusion
eyebrow(11, "Conclusion")
st.success("This study demonstrates an in-silico workflow for examining the "
           "interaction of ibuprofen with the COX-2 binding region. AutoDock Vina "
           "generated multiple candidate poses, with the top-ranked pose receiving a "
           "score of −7.278 kcal/mol. Structural visualisation in PyMOL enabled "
           "examination of the predicted ligand position and nearby residues, while "
           "the experimentally observed ligand in PDB 4PH9 provided a structural "
           "reference for comparison.", icon="🧪")

st.divider()
st.caption("Educational computational study prepared as an undergraduate "
           "bioinformatics project. All results shown are computational predictions "
           "and structural observations; nothing here constitutes a clinical, "
           "therapeutic, or experimental binding claim. Structural data: RCSB PDB "
           "entry 4PH9. Docking: AutoDock Vina 1.2.7; preparation: Meeko; "
           "visualisation: PyMOL and 3Dmol.js.")
