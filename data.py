"""
data.py — reads the authoritative experimental/docking files in Results/.

Nothing in this module invents data. Every number, coordinate, score and
residue identity is parsed from the supplied files at runtime. The only
transformation applied is a PDBQT -> PDB record reformat for browser
rendering, which copies the coordinate columns verbatim.
"""
from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

RESULTS = Path(__file__).parent / "Results"
FIGURES = RESULTS / "Figures"

# AutoDock atom type -> element symbol (used only to write a valid PDB element column)
ELEMENT = {"A": "C", "C": "C", "OA": "O", "O": "O", "N": "N", "NA": "N",
           "SA": "S", "S": "S", "HD": "H", "H": "H", "F": "F", "Cl": "CL",
           "Br": "BR", "I": "I", "P": "P"}


@dataclass(frozen=True)
class Atom:
    resname: str
    resid: int
    x: float
    y: float
    z: float


def _read(path: Path) -> str:
    return path.read_text(errors="ignore").replace("\r", "")


def _atoms(text: str, records=("ATOM", "HETATM")) -> list[Atom]:
    out = []
    for line in text.splitlines():
        if line.startswith(records):
            out.append(Atom(line[17:20].strip(), int(line[22:26]),
                            float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return out


def _to_pdb(pdbqt_block: str) -> str:
    """PDBQT -> PDB records. Columns 31-54 (the coordinates) are copied unchanged."""
    lines, i = [], 1
    for line in pdbqt_block.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            el = ELEMENT.get(line[77:79].strip(), line[77:79].strip()[:1] or "C")
            lines.append("HETATM%5d %-4s LIG L   1    %s  1.00  0.00          %2s"
                         % (i, (el + str(i))[:4], line[30:54], el.rjust(2)))
            i += 1
    return "\n".join(lines) + "\nEND\n"


# ---------------------------------------------------------------- receptor
@lru_cache(maxsize=1)
def receptor_pdb() -> str:
    """Chain A protein atoms of the experimental structure 4PH9 (for rendering)."""
    lines = [l for l in _read(RESULTS / "4PH9.pdb").splitlines()
             if l.startswith("ATOM") and l[21] == "A"]
    return "\n".join(lines) + "\nEND\n"


@lru_cache(maxsize=1)
def receptor_pdbqt_atoms() -> tuple[Atom, ...]:
    """The rigid receptor actually used for docking (receptor_A.pdbqt)."""
    return tuple(_atoms(_read(RESULTS / "receptor_A.pdbqt")))


@lru_cache(maxsize=1)
def experimental_ligand_pdb() -> str:
    """Experimentally observed ibuprofen (IBP) in chain A of 4PH9 — reference only."""
    lines = [l for l in _read(RESULTS / "4PH9.pdb").splitlines()
             if l.startswith("HETATM") and l[17:20] == "IBP" and l[21] == "A"]
    return "\n".join(lines) + "\nEND\n"


@lru_cache(maxsize=1)
def prepared_ligand_pdb() -> str:
    """The independently prepared ibuprofen used as docking input."""
    return _to_pdb(_read(RESULTS / "ibuprofen.pdbqt"))


# ------------------------------------------------------------------- poses
@lru_cache(maxsize=1)
def docked_poses() -> tuple[tuple[float, str], ...]:
    """(vina_score, pdb_text) for each of the predicted binding modes, in rank order."""
    text = _read(RESULTS / "ibuprofen_COX2_docked.pdbqt")
    out = []
    for block in text.split("MODEL")[1:]:
        m = re.search(r"VINA RESULT:\s*(-?\d+\.\d+)", block)
        if not m:
            raise ValueError("A MODEL block has no VINA RESULT line; refusing to guess.")
        out.append((float(m.group(1)), _to_pdb(block)))
    if not out:
        raise ValueError("No MODEL blocks found in ibuprofen_COX2_docked.pdbqt")
    return tuple(out)


def scores() -> list[float]:
    return [s for s, _ in docked_poses()]


# ---------------------------------------------------------------- contacts
@lru_cache(maxsize=8)
def nearby_residues(cutoff: float = 4.0, mode: int = 1) -> tuple[tuple[str, int], ...]:
    """Receptor residues with any atom within `cutoff` Å of the given pose."""
    lig = _atoms(docked_poses()[mode - 1][1])
    found = set()
    c2 = cutoff * cutoff
    for a in receptor_pdbqt_atoms():
        for b in lig:
            if (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2 < c2:
                found.add((a.resname, a.resid))
                break
    return tuple(sorted(found, key=lambda r: r[1]))


# ----------------------------------------------------------------- figures
FIGURE_CAPTIONS = [
    ("Figure 1", "COX-2 binding pocket containing the docked ibuprofen ligand."),
    ("Figure 2", "Close-up view of ibuprofen positioned within the predicted COX-2 binding region."),
    ("Figure 3", "Representative close contact between ibuprofen and a nearby binding-pocket residue."),
    ("Figure 4", "AutoDock Vina docking output showing nine predicted binding modes."),
    ("Figure 5", "Experimentally observed ibuprofen in the COX-2 structure PDB 4PH9."),
    ("Figure 6", "Comparison of the predicted docked ibuprofen pose with experimentally observed ibuprofen."),
]


def figure_path(n: int) -> Path:
    """Tolerates the doubled '.png.png' extension present in the supplied archive."""
    matches = sorted(FIGURES.glob(f"Figure_{n}_*.png*"))
    if not matches:
        raise FileNotFoundError(f"Figure {n} not found in {FIGURES}")
    return matches[0]


def figure_data_uri(n: int) -> str:
    return "data:image/png;base64," + base64.b64encode(figure_path(n).read_bytes()).decode()


# --------------------------------------------------------------- constants
# Docking parameters exactly as used in the experiment.
PARAMS = {
    "receptor": "COX-2", "pdb_id": "4PH9", "chain": "A", "ligand": "Ibuprofen",
    "software": "AutoDock Vina 1.2.7", "preparation": "Meeko", "analysis": "PyMOL",
    "exhaustiveness": 8, "num_modes": 9,
    "center": (13.578, 23.024, 25.205), "size": (17.917, 15.932, 13.624),
}
