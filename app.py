
import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.set_page_config(
    page_title="Ibuprofen–COX-2 Molecular Docking Analyzer",
    page_icon="🧬",
    layout="wide",
)

st.markdown("""
<style>
.main {background: #f7f9fc;}
.hero {
    padding: 2rem 2.2rem; border-radius: 18px;
    background: linear-gradient(135deg,#102a43,#1f5f8b);
    color: white; margin-bottom: 1.5rem;
}
.card {
    padding: 1.2rem; border-radius: 14px; background: white;
    border: 1px solid #d9e2ec; margin-bottom: 1rem;
}
.small {color:#52606d; font-size:.92rem;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🧬 Docking Analyzer")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "🧪 Target & Ligand", "🔬 Docking Workflow",
     "📊 Results", "🧩 Interactions", "📄 Report"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Project: Evaluation of Ibuprofen–COX-2 Binding Interaction Using Molecular Docking")

# ---------- DATA / HELPERS ----------
DEFAULT_RESULTS = pd.DataFrame({
    "Pose": [1, 2, 3, 4, 5],
    "Binding Affinity (kcal/mol)": [-7.8, -7.4, -7.1, -6.8, -6.5],
    "RMSD (Å)": [0.00, 1.24, 1.87, 2.41, 2.96],
})

DEFAULT_INTERACTIONS = pd.DataFrame({
    "Residue": ["Tyr385", "Ser530", "Val349", "Leu352", "Tyr355"],
    "Interaction": ["Hydrogen bond", "Hydrogen bond", "Hydrophobic", "Hydrophobic", "π / hydrophobic"],
    "Distance (Å)": [2.8, 3.1, 3.7, 3.9, 4.2],
})

def csv_download(df, filename):
    return df.to_csv(index=False).encode("utf-8")

# ---------- OVERVIEW ----------
if page == "🏠 Overview":
    st.markdown("""
    <div class="hero">
      <h1>🧬 Ibuprofen–COX-2 Molecular Docking Analyzer</h1>
      <p>Interactive project dashboard for evaluating the predicted binding interaction
      of ibuprofen with cyclooxygenase-2 (COX-2).</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Ligand", "Ibuprofen")
    c2.metric("Target", "COX-2")
    c3.metric("Method", "Molecular Docking")

    st.markdown("### 🎯 Project Objective")
    st.info(
        "To evaluate the predicted binding interaction between ibuprofen and COX-2 "
        "using molecular docking, focusing on docking score/binding affinity, pose "
        "selection, and protein–ligand interactions."
    )

    st.markdown("### 🧠 What is molecular docking?")
    st.write(
        "Molecular docking is a computational approach used to predict how a small "
        "molecule (ligand) may fit into a binding site of a macromolecule such as a "
        "protein. A docking program generates candidate poses and assigns scores that "
        "estimate the favorability of the predicted interaction."
    )

    st.markdown("### 🔁 Project pipeline")
    st.code(
        "COX-2 structure → Protein preparation → Ibuprofen preparation → "
        "Binding-site/grid definition → Docking → Pose ranking → "
        "Interaction analysis → Interpretation",
        language="text"
    )

    st.warning(
        "Important: the values shown in this demo are example values for interface "
        "testing. Replace them with your group's actual docking output before using "
        "the app in a report or presentation."
    )

# ---------- TARGET & LIGAND ----------
elif page == "🧪 Target & Ligand":
    st.title("🧪 Target & Ligand")
    left, right = st.columns(2)

    with left:
        st.subheader("Target: COX-2")
        st.markdown("""
        <div class="card">
        <b>Protein:</b> Cyclooxygenase-2 (COX-2)<br>
        <b>Role:</b> Enzyme involved in prostaglandin biosynthesis and inflammation.<br>
        <b>Docking role:</b> Receptor / target protein.
        </div>
        """, unsafe_allow_html=True)
        st.text_input("PDB ID used in your project", value="Enter your COX-2 PDB ID")
        st.file_uploader("Upload receptor structure", type=["pdb", "ent"])

    with right:
        st.subheader("Ligand: Ibuprofen")
        st.markdown("""
        <div class="card">
        <b>Name:</b> Ibuprofen<br>
        <b>Formula:</b> C₁₃H₁₈O₂<br>
        <b>Molecular weight:</b> ~206.28 g/mol<br>
        <b>Docking role:</b> Ligand.
        </div>
        """, unsafe_allow_html=True)
        st.file_uploader("Upload ibuprofen ligand", type=["pdb", "mol", "mol2", "sdf"])

    st.markdown("### 📌 Structure files")
    st.caption(
        "Upload the exact receptor and ligand structures used in your docking run. "
        "The app does not invent docking coordinates."
    )

# ---------- WORKFLOW ----------
elif page == "🔬 Docking Workflow":
    st.title("🔬 Molecular Docking Workflow")

    steps = [
        ("1", "Protein preparation", "Remove unwanted molecules/waters as appropriate, add hydrogens, assign charges, and prepare the receptor."),
        ("2", "Ligand preparation", "Prepare the ibuprofen structure, including appropriate protonation/geometry and file format."),
        ("3", "Binding site", "Define the COX-2 binding region/grid according to the docking protocol."),
        ("4", "Docking", "Run the selected docking software and generate candidate binding poses."),
        ("5", "Pose ranking", "Compare docking scores and structural plausibility to identify poses for analysis."),
        ("6", "Interaction analysis", "Inspect hydrogen bonds, hydrophobic contacts, π interactions, and interacting residues."),
    ]
    for n, title, desc in steps:
        st.markdown(f"**{n}. {title}** — {desc}")

    st.markdown("### 🧰 Your docking software")
    software = st.selectbox(
        "Select software used by your group",
        ["AutoDock Vina", "PyRx", "AutoDock 4", "SwissDock", "Other"]
    )
    if software == "Other":
        st.text_input("Software name")

    st.markdown("### 📥 Upload docking result")
    uploaded = st.file_uploader(
        "CSV containing your docking poses/scores",
        type=["csv"]
    )
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.success("Docking result loaded.")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not read the CSV: {e}")

# ---------- RESULTS ----------
elif page == "📊 Results":
    st.title("📊 Docking Results")

    uploaded = st.file_uploader("Upload your docking-results CSV", type=["csv"], key="results")
    if uploaded:
        try:
            results = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read the CSV: {e}")
            results = DEFAULT_RESULTS
    else:
        results = DEFAULT_RESULTS

    st.caption("Demo data are shown until you upload your actual docking output.")

    a, b, c = st.columns(3)
    score_col = "Binding Affinity (kcal/mol)"
    if score_col in results.columns:
        best = results[score_col].min()
        a.metric("Lowest demo/loaded score", f"{best:.2f} kcal/mol")
    b.metric("Poses", len(results))
    c.metric("Analysis", "Predicted")

    st.dataframe(results, use_container_width=True)

    if score_col in results.columns:
        chart = results.set_index("Pose")[score_col]
        st.bar_chart(chart)

    st.download_button(
        "⬇️ Download results CSV",
        data=csv_download(results, "docking_results.csv"),
        file_name="docking_results.csv",
        mime="text/csv",
    )

# ---------- INTERACTIONS ----------
elif page == "🧩 Interactions":
    st.title("🧩 Protein–Ligand Interactions")

    uploaded = st.file_uploader(
        "Upload interaction table CSV",
        type=["csv"],
        key="interactions"
    )
    if uploaded:
        try:
            interactions = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read the CSV: {e}")
            interactions = DEFAULT_INTERACTIONS
    else:
        interactions = DEFAULT_INTERACTIONS

    st.caption(
        "The demo interaction table is illustrative. Replace it with interactions "
        "from your actual docking pose."
    )
    st.dataframe(interactions, use_container_width=True)

    st.markdown("### 🔎 Interaction types")
    counts = interactions["Interaction"].value_counts()
    st.bar_chart(counts)

    st.markdown("### 🧠 Interpretation guide")
    st.markdown("""
    - **Hydrogen bonds:** directional polar contacts that can contribute to ligand recognition.
    - **Hydrophobic contacts:** non-polar contacts that may help stabilize a ligand in a hydrophobic pocket.
    - **π interactions:** aromatic or π-associated contacts involving suitable residues.
    - **Distance:** shorter contacts can be structurally relevant, but distance alone does not prove a biologically meaningful interaction.
    """)

# ---------- REPORT ----------
elif page == "📄 Report":
    st.title("📄 Project Report Generator")

    student = st.text_input("Student / Group name")
    pdb_id = st.text_input("COX-2 PDB ID")
    docking_program = st.selectbox("Docking program", ["AutoDock Vina", "PyRx", "AutoDock 4", "SwissDock", "Other"])
    best_score = st.number_input("Best docking score (kcal/mol)", value=-7.8, step=0.1, format="%.2f")
    residues = st.text_input("Key interacting residues", value="Enter residues from your actual docking analysis")

    report = f"""IBUPROFEN–COX-2 MOLECULAR DOCKING

Student / Group: {student or "________________"}
COX-2 PDB ID: {pdb_id or "________________"}
Docking software: {docking_program}

OBJECTIVE
To evaluate the predicted binding interaction of ibuprofen with COX-2 using molecular docking.

METHOD
The COX-2 receptor and ibuprofen ligand were prepared for docking. A binding region was
defined according to the selected docking protocol. Candidate poses were generated and
ranked using the docking score. The selected pose was then examined for protein–ligand
interactions.

RESULTS
Best docking score: {best_score:.2f} kcal/mol
Key interacting residues: {residues}

INTERPRETATION
The docking result represents a computational prediction of how ibuprofen may bind to
the selected COX-2 structure. The score and observed contacts should be interpreted
together with the pose geometry and the limitations of the docking method.

CONCLUSION
Molecular docking provides a structural hypothesis for the interaction between ibuprofen
and COX-2. Experimental validation would be required to establish the biological
significance of the predicted interaction.
"""

    st.text_area("Generated report", report, height=430)
    st.download_button(
        "⬇️ Download report",
        data=report.encode("utf-8"),
        file_name="ibuprofen_cox2_docking_report.txt",
        mime="text/plain",
    )

st.markdown("---")
st.caption("Educational molecular-docking project dashboard • Replace all demo values with your actual docking output.")
