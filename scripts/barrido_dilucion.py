"""Barrido de agua de dilución F_303 constante: ppm de refinado por escenario (modelo de 6.7) y costo en KNO3.

Uso: python scripts/barrido_dilucion.py
Escenarios: nominal (t < 40 min), ClO4- +550 ppm en SSK (t = 40-140 min), Mg2+ +35 % en SSK (t >= 140 min).
La pérdida de KNO3 usa el coeficiente 0,42 t/h por t/h de agua sobre el nominal (placeholder del modelo).
"""
import warnings

import numpy as np
import pandas as pd

from msmpr_core import plant as P

warnings.filterwarnings("ignore")
filas = []
for x in np.arange(10.0, 70.0, 2.0):
    d = P.simular_recirculacion_y_magnesio("sin_reciclo_actual", use_AIT3105=False, hipotesis_mg="combinada",
                                           F_303_nom=float(x), F_303_min=1.0, F_303_max=120.0)
    g = lambda t: d.iloc[int(round(t / 0.05))]
    filas.append({"F303_t_h": x, "ppm_nominal": g(39).ppm_ClO4_final_6000, "ppm_ClO4_+550": g(139).ppm_ClO4_final_6000,
                  "ppm_Mg_+35%": g(359).ppm_ClO4_final_6000, "perdida_KNO3_t_h": 0.42 * max(x - P.F303_NOM, 0.0)})
r = pd.DataFrame(filas).round(2)
print(r.to_string(index=False))
for col in ("ppm_nominal", "ppm_ClO4_+550", "ppm_Mg_+35%"):
    ok = r[r[col] <= 40.0]
    print(f"F_303 mínimo con {col} <= 40 ppm:", None if ok.empty else float(ok.F303_t_h.min()))
