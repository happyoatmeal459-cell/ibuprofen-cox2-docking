"""
viewer.py — builds a self-contained 3Dmol.js viewer for embedding in Streamlit
via st.components.v1.html. Structures are injected as PDB text taken directly
from the supplied files; no coordinates are modified.
"""
from __future__ import annotations

import json

CDN = "https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"
FALLBACK = "https://cdn.jsdelivr.net/npm/3dmol@2.4.2/build/3Dmol-min.js"


def viewer_html(receptor: str, pose: str, experimental: str,
                pocket_resi: list[int], *, style: str = "cartoon",
                surface: bool = False, show_pocket: bool = False,
                ligands: str = "pose", spin: bool = False,
                height: int = 520, bg: str = "#08131a") -> str:
    cfg = json.dumps({
        "receptor": receptor, "pose": pose, "exp": experimental,
        "resi": pocket_resi, "style": style, "surface": surface,
        "pocket": show_pocket, "ligands": ligands, "spin": spin, "bg": bg,
    })
    return f"""
<div id="viewport" style="position:relative;width:100%;height:{height}px;
     border-radius:14px;overflow:hidden;background:{bg};border:1px solid #1d3540"></div>
<script src="{CDN}" onerror="window.__f=1"></script>
<script>
const CFG = {cfg};
function boot() {{
  const v = $3Dmol.createViewer(document.getElementById('viewport'),
                                {{backgroundColor: CFG.bg}});
  v.addModel(CFG.receptor, 'pdb');   // model 0 — COX-2 chain A (PDB 4PH9)
  v.addModel(CFG.pose, 'pdb');       // model 1 — predicted pose (AutoDock Vina)
  v.addModel(CFG.exp, 'pdb');        // model 2 — experimental ibuprofen (reference)
  v.setStyle({{}}, {{}});
  const rec = {{model: 0}};
  if (CFG.style === 'cartoon') v.setStyle(rec, {{cartoon: {{color: 'spectrum', opacity: 0.92}}}});
  else if (CFG.style === 'sticks') v.setStyle(rec, {{stick: {{radius: 0.1, colorscheme: 'Jmol'}}}});
  if (CFG.surface) v.addSurface($3Dmol.SurfaceType.VDW,
                                {{opacity: 0.6, color: '#8fc6cf'}}, rec);
  if (CFG.pocket) v.addStyle({{model: 0, resi: CFG.resi}},
                             {{stick: {{radius: 0.16, colorscheme: 'Jmol'}}}});
  if (CFG.ligands === 'pose' || CFG.ligands === 'both')
    v.setStyle({{model: 1}}, {{stick: {{radius: 0.22, colorscheme: 'greenCarbon'}},
                              sphere: {{radius: 0.3, colorscheme: 'greenCarbon'}}}});
  if (CFG.ligands === 'exp' || CFG.ligands === 'both')
    v.setStyle({{model: 2}}, {{stick: {{radius: 0.22, colorscheme: 'magentaCarbon'}},
                              sphere: {{radius: 0.3, colorscheme: 'magentaCarbon'}}}});
  const focus = CFG.ligands === 'exp' ? {{model: 2}} : {{model: 1}};
  v.zoomTo(CFG.style === 'hidden' ? focus : {{}});
  if (CFG.style !== 'hidden') {{ v.zoomTo(focus); v.zoom(0.55); }}
  v.render();
  if (CFG.spin) v.spin('y', 0.4);
}}
if (window.$3Dmol) boot();
else {{
  const s = document.createElement('script');
  s.src = "{FALLBACK}";
  s.onload = boot;
  document.head.appendChild(s);
}}
</script>
"""
