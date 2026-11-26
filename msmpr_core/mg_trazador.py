"""El Mg del cristal como trazador del licor madre adherido: ¿cuánto del ClO4- del cristal explica el licor?

Idea: el Mg2+ no entra a la red del KNO3, así que el Mg medido en el cristal sin refinar indica cuánto licor madre lleva adherido.
Si todo el ClO4- fuera licor adherido, ClO4_esperado[ppm] = Mg_cristal[ppm] * (ClO4_licor / Mg_licor)  (la densidad se cancela).
La parte medida que supera ese valor ("exceso") no se explica por impregnación: sería ocluida o coprecipitada y el lavado no la remueve.

Supuestos que hay que declarar al usarlo:
  * Mg del cristal en % másico (por eso `mg_factor = 1e4`); con la tabla horaria de 2025 la mediana de 0,10 % da un licor adherido
    de ~5 % del cristal, coherente con el ~7 % del balance de diseño.
  * El licor adherido tiene la relación ClO4/Mg del MLK (B3520) medida en la misma hora (no el licor de A3210, sin rezago).
Solo reporta métricas agregadas; el Excel de entrada es confidencial y no está en el repositorio.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

COLS = {
    "mg_cristal": "Cristal sin refinar Mg", "clo4_cristal": "Cristal sin refinal ClO4", "refi_ppm": "Cristal refinado ClO4",
    "mg_licor": "Purga_Recirculación Mg", "clo4_licor_gL": "Purga_Recirculación ClO4 IC", "kclo4_licor_gL": "Purga_Recirculación KClO4 IC",
    "ml_refi_kclo4": "ML_REFI_KCLO4", "T2": "Temp_Cristalización2_A3000",
}


def cargar_tabla_horaria(ruta, hoja="Sheet1") -> pd.DataFrame:
    d = pd.read_excel(ruta, sheet_name=hoja)
    d = d.set_index("Fecha_hora")
    return d.apply(pd.to_numeric, errors="coerce")


def trazador_licor_adherido(df: pd.DataFrame, mg_factor: float = 1e4, cols: dict | None = None) -> pd.DataFrame:
    """Agrega ClO4 esperado por licor adherido, exceso (ppm) y fracción de exceso al DataFrame (solo filas completas)."""
    c = {**COLS, **(cols or {})}
    x = df[[c["mg_cristal"], c["mg_licor"], c["clo4_licor_gL"], c["clo4_cristal"], c["refi_ppm"], c["ml_refi_kclo4"]]].dropna()
    x = x[(x[c["mg_cristal"]] > 0) & (x[c["mg_licor"]] > 0) & (x[c["clo4_licor_gL"]] > 0)].copy()
    mg_ppm = x[c["mg_cristal"]] * mg_factor
    x["licor_adherido_frac"] = mg_ppm / (x[c["mg_licor"]] / 1.45 * 1000.0)       # rho supuesta 1,45 kg/L
    x["clo4_esperado_ppm"] = mg_ppm * (x[c["clo4_licor_gL"]] / x[c["mg_licor"]])
    x["clo4_exceso_ppm"] = x[c["clo4_cristal"]] - x["clo4_esperado_ppm"]
    x["frac_exceso"] = (x["clo4_exceso_ppm"] / x[c["clo4_cristal"]]).clip(-2.0, 1.0)
    x["refi_gt40"] = x[c["refi_ppm"]] > 40.0
    return x


def _auc(score, y):
    y = pd.Series(y).astype(bool).values
    s = pd.Series(score).values
    a, b = s[y], s[~y]
    if len(a) < 5 or len(b) < 5:
        return float("nan")
    return float(mannwhitneyu(a, b, alternative="greater").statistic / (len(a) * len(b)))


def resumen_trazador(x: pd.DataFrame, cols: dict | None = None) -> dict:
    """Métricas agregadas: fracción no explicada, AUC de cada componente y exceso por nivel de ClO4 del cristal."""
    c = {**COLS, **(cols or {})}
    y = x["refi_gt40"]
    por_nivel = x.groupby(pd.cut(x[c["clo4_cristal"]], [0, 200, 400, 600, 1e6]), observed=False).agg(
        n=("frac_exceso", "size"), frac_exceso_mediana=("frac_exceso", "median"), pct_refinado_gt40=("refi_gt40", lambda s: 100 * s.mean()))
    return {
        "n": int(len(x)),
        "licor_adherido_mediana_pct": float(100 * x["licor_adherido_frac"].median()),
        "frac_exceso_mediana": float(x["frac_exceso"].median()),
        "frac_exceso_p25_p75": (float(x["frac_exceso"].quantile(0.25)), float(x["frac_exceso"].quantile(0.75))),
        "AUC_refinado_gt40": {"clo4_cristal_medido": _auc(x[c["clo4_cristal"]], y), "explicado_por_licor": _auc(x["clo4_esperado_ppm"], y),
                              "exceso_no_explicado": _auc(x["clo4_exceso_ppm"], y), "kclo4_ml_refinacion": _auc(x[c["ml_refi_kclo4"]], y)},
        "spearman_exceso_vs_Mg_licor": float(spearmanr(x["clo4_exceso_ppm"], x[c["mg_licor"]]).correlation),
        "spearman_exceso_vs_ClO4_licor": float(spearmanr(x["clo4_exceso_ppm"], x[c["clo4_licor_gL"]]).correlation),
        "por_nivel_clo4_cristal": {str(k): {kk: float(vv) for kk, vv in v.items()} for k, v in por_nivel.iterrows()},
    }


def envolvente_kclo4_vs_mg(df: pd.DataFrame, cols: dict | None = None, bins=(0, 20, 25, 30, 35, 40, 60), q=0.95) -> pd.DataFrame:
    """Percentil `q` y mediana del KClO4 del MLK por tramo de Mg: aproxima el techo de solubilidad observado en planta."""
    c = {**COLS, **(cols or {})}
    m = df[[c["mg_licor"], c["kclo4_licor_gL"]]].dropna()
    m.columns = ["Mg", "KClO4"]
    return m.groupby(pd.cut(m["Mg"], list(bins)), observed=False).agg(n=("KClO4", "size"), mediana=("KClO4", "median"), techo=("KClO4", lambda s: s.quantile(q)))
