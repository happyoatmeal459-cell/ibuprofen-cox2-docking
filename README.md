# Evaluation of Ibuprofen–COX-2 Binding Interaction Using Molecular Docking

Streamlit front end for an educational in-silico docking study of ibuprofen against
cyclooxygenase-2 (COX-2), using the experimental structure PDB **4PH9** as the
structural reference.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>. An internet connection is needed the first
time a page loads, because the 3D viewer pulls **3Dmol.js** from a CDN
(cdnjs, with a jsDelivr fallback). Everything else — structures, poses, scores,
figures — is read from the local `Results/` folder.

## Project structure

```
.
├── app.py                 # All 11 sections of the site, Streamlit UI
├── data.py                # Parses Results/ at runtime: poses, scores, contacts, figures
├── viewer.py              # Builds the 3Dmol.js viewer embedded via components.html
├── requirements.txt
├── .streamlit/config.toml # Light scientific theme
├── standalone/index.html  # Self-contained single-file version (no Python needed)
└── Results/               # Authoritative experimental + docking data
    ├── 4PH9.pdb
    ├── receptor_A.pdbqt
    ├── ibuprofen.pdbqt
    ├── ibuprofen_COX2_docked.pdbqt
    ├── docking_summary.txt        (supplied file is empty; nothing is read from it)
    └── Figures/Figure_1..6_*.png
```

`standalone/index.html` is the same study as one HTML file with all data and images
inlined — open it directly in a browser if you don't want to run Python.

## Where each number comes from

Nothing in this app is hard-coded from memory or estimated.

| Displayed value | Source |
| --- | --- |
| Nine Vina scores (−7.278 … −4.649) | `REMARK VINA RESULT` lines of `ibuprofen_COX2_docked.pdbqt` |
| Predicted ligand poses | `MODEL` blocks of the same file |
| Receptor cartoon | `ATOM` records, chain A, of `4PH9.pdb` |
| Experimental ibuprofen | `HETATM` records with residue name `IBP`, chain A, of `4PH9.pdb` |
| Nearby residues (≈4 Å) and close contacts (≈3.5 Å) | Computed in `data.nearby_residues()` from `receptor_A.pdbqt` against the selected pose |
| Grid centre, grid size, exhaustiveness, mode count | `data.PARAMS` (the parameters used in the experiment) |

The residue sets computed at runtime reproduce the reported lists exactly:
13 residues at 4 Å (VAL117, ARG121, VAL350, LEU353, SER354, TYR356, LEU360, TYR386,
MET523, VAL524, GLY527, ALA528, SER531) and 7 at 3.5 Å (ARG121, TYR356, TYR386,
MET523, GLY527, ALA528, SER531).

### Format conversion

3Dmol.js does not parse PDBQT reliably, so `data._to_pdb()` rewrites ligand records as
PDB `HETATM` lines. It copies **columns 31–54 — the x, y, z coordinates — byte for
byte** and only rebuilds the atom name/element columns. No coordinate, pose, score or
residue identity is altered anywhere in this codebase.

## Scientific scope

Vina scores are computational scoring estimates, not experimentally measured binding
affinities. Residues listed as nearby or in close contact are computationally
identified from the predicted pose and are not experimentally validated interactions;
no hydrogen bonds are claimed, and no RMSD against the experimental ligand is reported
because none was calculated. The experimental ibuprofen in 4PH9 is a structural
reference, not the output of this docking run.

Educational computational study. No clinical or therapeutic claims are made.
