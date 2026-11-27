"""Mg como trazador del licor adherido y relación Mg–ClO4- (usa la tabla horaria local `tabla_limpia_valores.xlsx`).

Uso: python scripts/analisis_mg_perclorato.py [ruta_a_tabla_limpia_valores.xlsx]
Escribe docs/fig/13_mg_perclorato.png y docs/analisis_mg_perclorato.json (solo métricas agregadas).
"""
import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from msmpr_core import mg_trazador as M

warnings.filterwarnings("ignore")
ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else next((p for p in (Path("data/tabla_limpia_valores.xlsx"), Path("tabla_limpia_valores.xlsx"),
                                                                    Path("Predicción efecto de analitos/tabla_limpia_valores.xlsx")) if p.exists()), None)
if ruta is None:
    raise SystemExit("No se encontró tabla_limpia_valores.xlsx; pásala como argumento.")

df = M.cargar_tabla_horaria(ruta)
x = M.trazador_licor_adherido(df)
res = M.resumen_trazador(x)
env = M.envolvente_kclo4_vs_mg(df)

fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
nv = res["por_nivel_clo4_cristal"]
etq = ["≤200", "200–400", "400–600", ">600"]
ax[0].bar(etq, [100 * v["frac_exceso_mediana"] for v in nv.values()], color="tab:red", label="% del ClO4 crudo NO explicado por licor adherido")
ax[0].set_ylabel("% no explicado (mediana)")
ax[0].set_xlabel("ClO4- del cristal sin refinar [ppm]")
a2 = ax[0].twinx()
a2.plot(etq, [v["pct_refinado_gt40"] for v in nv.values()], "ko-", label="% refinado > 40 ppm")
a2.set_ylabel("% refinado > 40 ppm")
ax[0].set_title(f"Exceso de ClO4- no explicado por el licor (n={res['n']})")
auc = res["AUC_refinado_gt40"]
nombres = ["ClO4 crudo medido", "Explicado por licor", "NO explicado (exceso)", "KClO4 ML refinación"]
ax[1].barh(nombres, [auc["clo4_cristal_medido"], auc["explicado_por_licor"], auc["exceso_no_explicado"], auc["kclo4_ml_refinacion"]], color=["gray", "tab:blue", "tab:red", "tab:green"])
ax[1].axvline(0.5, color="k", ls="--", lw=1)
ax[1].set_xlim(0.3, 0.9)
ax[1].set_xlabel("AUC para refinado > 40 ppm")
ax[1].set_title("¿Qué parte del ClO4- crudo predice el refinado?")
e = env.dropna()
ax[2].plot([str(i) for i in e.index], e["techo"], "o-", color="tab:purple", label="percentil 95")
ax[2].plot([str(i) for i in e.index], e["mediana"], "s--", color="tab:orange", label="mediana")
ax[2].set_xlabel("Mg2+ del MLK [g/L]")
ax[2].set_ylabel("KClO4 del MLK [g/L]")
ax[2].set_title("KClO4 del MLK vs Mg (techo ≈ 6 g/L)")
ax[2].legend()
ax[2].tick_params(axis="x", rotation=30)
fig.tight_layout()
Path("docs/fig").mkdir(parents=True, exist_ok=True)
fig.savefig("docs/fig/13_mg_perclorato.png", dpi=150)
Path("docs/analisis_mg_perclorato.json").write_text(json.dumps({"trazador": res, "envolvente_kclo4_vs_mg": env.round(3).reset_index().astype(str).to_dict("records")}, indent=1, default=float))
print(json.dumps(res, indent=1, default=float)[:1800])
