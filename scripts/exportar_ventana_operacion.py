"""Escribe config/ventana_operacion.json desde valores del modelo DPBE·MSMPR (CLI de `plant.exportar_ventana_operacion`).

Ejemplo:  python scripts/exportar_ventana_operacion.py --D-nom 15 --T1 60 --T2 42 --origen "Cristalizador_SQM.ipynb §9.5 (commit abc123)"
Desde el notebook (celda al final de §9.5):
    from msmpr_core.plant import exportar_ventana_operacion
    exportar_ventana_operacion({"D_nom_t_h": D_opt, "T1_sp_C": T1_opt, "T2_sp_C": T2_opt, "d50_obj_um": d50_opt},
                               origen="Cristalizador_SQM.ipynb §9.5")
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from msmpr_core.plant import exportar_ventana_operacion  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--D-nom", type=float, dest="D_nom_t_h")
ap.add_argument("--T1", type=float, dest="T1_sp_C")
ap.add_argument("--T2", type=float, dest="T2_sp_C")
ap.add_argument("--d50", type=float, dest="d50_obj_um")
ap.add_argument("--origen", default="")
a = vars(ap.parse_args())
origen = a.pop("origen")
out = exportar_ventana_operacion({k: v for k, v in a.items() if v is not None}, origen=origen)
print("Escrito config/ventana_operacion.json:", {k: out[k] for k in ("D_nom_t_h", "T1_sp_C", "T2_sp_C", "d50_obj_um", "origen")})
