"""Reproduce el diagnóstico y la calibración del replay con los Excel locales de SQM (no incluidos en el repo).

Uso (desde la raíz del repo, con data/Base de datos_v2*.xlsx y data/Análisis físicos*.xlsx):
    python scripts/diagnostico_replay.py
Escribe docs/fig/11_diagnostico_replay.png y docs/diagnostico_replay.json (solo métricas agregadas).
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from msmpr_core import replay_calib as RC
from msmpr_core.replay import cargar_ventana_real_sqm, find_sqm_excel

warnings.filterwarnings("ignore")
ruta = find_sqm_excel("base de datos_v2")
if ruta is None:
    raise SystemExit("No se encontró data/Base de datos_v2*.xlsx")

df = RC.construir_dataset_quimica(ruta)
diag = RC.diagnostico_mecanismo(df)
comp = RC.comparar_predictores(df)

d30 = cargar_ventana_real_sqm("2026-10-16 00:00:00", "2026-11-15 23:59:59", usar_sensores_4d=False)
cal = RC.calibrar_replay(d30[d30.index < "2026-11-05"], d30[d30.index >= "2026-11-05"])

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
c = comp.dropna(subset=["AUC_test"]).sort_values("AUC_test")
ax[0].barh(c["predictor"], c["AUC_test"], color="tab:blue")
ax[0].axvline(0.5, color="k", ls="--", lw=1)
ax[0].set_xlabel("AUC fuera de muestra (refinado > 40 ppm)")
ax[0].set_title(f"¿Qué explica el ppm refinado? (n={diag['n']})")
lags = diag["rezago_crudo_vs_mlkClO4_h"]
ax[1].bar([str(k) for k in lags], list(lags.values()), color="tab:red")
ax[1].set_ylim(-0.3, 0.3)
ax[1].axhline(0, color="k", lw=0.8)
ax[1].set_xlabel("Rezago [h]")
ax[1].set_ylabel("Spearman crudo ppm vs ClO4 del MLK")
ax[1].set_title("Eslabón MLK → cristal crudo")
fig.tight_layout()
Path("docs/fig").mkdir(parents=True, exist_ok=True)
fig.savefig("docs/fig/11_diagnostico_replay.png", dpi=150)
Path("docs/diagnostico_replay.json").write_text(
    json.dumps({"diagnostico": diag, "predictores": comp.to_dict("records"), "calibracion_replay": cal}, indent=1, default=float))
print(comp.round(3).to_string())
