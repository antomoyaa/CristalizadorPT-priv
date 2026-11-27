"""Diagnóstico y calibración del replay NPT-3 contra la base química real (2 h, ene-2025 a nov-2026).

Qué responde:
  1. ¿Hay evidencia en los datos de que el ClO4/KClO4 del MLK (B3520) -> coprecipitación -> cristal crudo -> refinado?
     (`diagnostico_mecanismo`: correlaciones con rezago, estadística por exceso sobre saturación, AUC de excedencias).
  2. ¿Qué variables sí explican el ppm del refinado? (`comparar_predictores`: AUC y métricas fuera de muestra con corte temporal.)
  3. ¿Puede el replay mejorar su ajuste recalibrando sus coeficientes? (`calibrar_replay`: mínimos cuadrados con residuo
     censurado en el piso del método (20 ppm) y validación en una ventana posterior.)

No contiene datos de SQM: lee el Excel local (`data/Base de datos_v2*.xlsx`) y devuelve solo métricas agregadas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import mannwhitneyu

from .replay import COEF_REPLAY, replay_fit_metrics, simular_replay_npt3

UMBRAL = 40.0
PISO = 20.0


def _ts(d):
    return pd.to_datetime(pd.to_datetime(d["Fecha"]).dt.strftime("%Y-%m-%d") + " " + d["Hora"].astype(str), errors="coerce")


def construir_dataset_quimica(ruta_v2) -> pd.DataFrame:
    """Une, por marca de tiempo (2 h), cristal sin refinar/refinado, ML de refinación, MLK y T de cristalización."""
    xl = pd.ExcelFile(ruta_v2)

    def get(hoja, cols, ren, filt=None):
        d = xl.parse(hoja)
        if filt:
            d = d[d["Descripcion"].astype(str).str.contains(filt, case=False, na=False)]
        d = d.assign(TS=_ts(d)).dropna(subset=["TS"]).set_index("TS").sort_index()
        d = d[~d.index.duplicated(keep="last")]
        return d[cols].apply(pd.to_numeric, errors="coerce").rename(columns=ren)

    crudo = get("Cristal sin Refinar", ["ClO4", "Mg"], {"ClO4": "crudo_ppm", "Mg": "crudo_Mg"})
    refi = get("Cristal Refinado", ["ClO4"], {"ClO4": "refi_ppm"})
    mlr = get("ML Refi", ["KClO4 IC", "ClO4 IC"], {"KClO4 IC": "mlrefi_KClO4", "ClO4 IC": "mlrefi_ClO4"})
    mlk = get("Purga-Recirculación", ["KClO4 IC", "ClO4 IC", "Mg"],
              {"KClO4 IC": "mlk_KClO4", "ClO4 IC": "mlk_ClO4", "Mg": "mlk_Mg"}, filt="MLK")
    df = crudo.join([refi, mlr, mlk], how="inner").dropna(subset=["crudo_ppm", "refi_ppm", "mlrefi_ClO4"])
    t = xl.parse("Temp. A3000")
    t["TS"] = pd.to_datetime(t["DateTime"], errors="coerce")
    t = t.dropna(subset=["TS"]).set_index("TS").sort_index()
    T2 = pd.to_numeric(t["Temperatura cristalización"], errors="coerce").resample("2h").mean()
    df["T2"] = T2.reindex(df.index, method="nearest", tolerance=pd.Timedelta("90min")).values
    df["Csat"] = (4.92 + 0.14 * (df["T2"].fillna(43.0) - 43.0)) * np.exp(-0.022 * (df["mlk_Mg"] - 30.5))
    df["exceso"] = (df["mlk_ClO4"] - df["Csat"]).clip(lower=0.0)
    return df


def _auc(score, y_bool):
    s = pd.Series(score).reset_index(drop=True)
    y = pd.Series(y_bool).reset_index(drop=True).astype(bool)
    ok = s.notna()
    a, b = s[ok & y], s[ok & ~y]
    if len(a) < 5 or len(b) < 5:
        return np.nan
    return float(mannwhitneyu(a, b, alternative="greater").statistic / (len(a) * len(b)))


def diagnostico_mecanismo(df: pd.DataFrame) -> dict:
    """Evidencia del eslabón MLK -> cristal crudo y de cada variable sobre el ppm del refinado."""
    out = {"n": int(len(df)), "periodo": (str(df.index.min()), str(df.index.max()))}
    out["spearman_refi"] = df[["mlrefi_KClO4", "crudo_ppm", "crudo_Mg", "mlk_Mg", "mlk_KClO4", "mlk_ClO4", "exceso"]].corrwith(
        df["refi_ppm"], method="spearman").round(3).to_dict()
    out["spearman_crudo"] = df[["mlrefi_KClO4", "mlk_Mg", "mlk_KClO4", "mlk_ClO4", "exceso"]].corrwith(
        df["crudo_ppm"], method="spearman").round(3).to_dict()
    out["rezago_crudo_vs_mlkClO4_h"] = {
        2 * k: round(float(df["crudo_ppm"].corr(df["mlk_ClO4"].shift(k), method="spearman")), 3) for k in (0, 1, 2, 3, 6, 12)}
    a, b = df[df["exceso"] > 0], df[df["exceso"] <= 0]
    out["exceso"] = {"frac_con_exceso": round(float((df["exceso"] > 0).mean()), 3),
                     "crudo_mediana": (float(a["crudo_ppm"].median()), float(b["crudo_ppm"].median())),
                     "pct_refi_gt40": (round(100 * float((a["refi_ppm"] > UMBRAL).mean()), 1),
                                       round(100 * float((b["refi_ppm"] > UMBRAL).mean()), 1))}
    return out


def comparar_predictores(df: pd.DataFrame, corte="2026-01-01") -> pd.DataFrame:
    """AUC (refinado > 40 ppm) fuera de muestra y regresión lineal censurada en el piso, con corte temporal."""
    tr, te = df[df.index < corte], df[df.index >= corte]
    y_te = te["refi_ppm"] > UMBRAL
    filas = []
    for nombre, col in (("ML refinación KClO4 (g/L)", "mlrefi_KClO4"), ("Cristal sin refinar (ppm)", "crudo_ppm"),
                        ("Mg del MLK (g/L)", "mlk_Mg"), ("KClO4 del MLK (g/L)", "mlk_KClO4"),
                        ("Exceso MLK sobre C_sat (hinge del replay)", "exceso")):
        filas.append({"predictor": nombre, "AUC_test": _auc(te[col], y_te)})
    # regresión: ppm = a + b*ML_refi + c*crudo (entrena en tr, evalúa en te)
    cols = ["mlrefi_KClO4", "crudo_ppm"]
    A = np.c_[np.ones(len(tr)), tr[cols].values]
    beta = np.linalg.lstsq(A, tr["refi_ppm"].values, rcond=None)[0]
    pred = np.maximum(PISO, np.c_[np.ones(len(te)), te[cols].values] @ beta)
    m = replay_fit_metrics(te["refi_ppm"], pd.Series(pred, index=te.index))
    filas.append({"predictor": "Regresión ML refi + crudo (ppm)", "AUC_test": _auc(pred, y_te),
                  "RMSE_test": m["todos"]["rmse"], "r_test": m["todos"]["r"],
                  "sens": m["excedencias"]["sensibilidad"], "esp": m["excedencias"]["especificidad"]})
    return pd.DataFrame(filas)


def _residuo_censurado(sim, real):
    real = np.asarray(real, float)
    sim = np.asarray(sim, float)
    ok = ~np.isnan(real)
    r = np.where(real[ok] <= PISO + 0.5, np.maximum(sim[ok] - PISO, 0.0), sim[ok] - real[ok])
    return r


_PARAMS = ("a0", "a_b", "a_c", "k_cop", "c0_refi", "k_refi")
_LB = np.array([0.0, 0.0, 0.0, 0.0, 0.1, 0.0])
_UB = np.array([60.0, 1.0, 1.0, 20000.0, 3.0, 0.02])


def calibrar_replay(df_train: pd.DataFrame, df_test: pd.DataFrame | None = None) -> dict:
    """Recalibra seis coeficientes del replay (baseline_sqm) con residuo censurado y los evalúa en `df_test`."""
    x0 = np.array([COEF_REPLAY[k] for k in _PARAMS], float)

    def f(x):
        coef = dict(zip(_PARAMS, x))
        sim = simular_replay_npt3(df_train, "baseline_sqm", coef=coef)["ClO4_refi_ppm"].values
        return _residuo_censurado(sim, df_train["ClO4_Refi_real"].values)

    sol = least_squares(f, x0, bounds=(_LB, _UB), x_scale=np.maximum(np.abs(x0), 1e-3), max_nfev=60)
    coef = {**COEF_REPLAY, **dict(zip(_PARAMS, sol.x))}

    def evalua(d):
        sim = simular_replay_npt3(d, "baseline_sqm", coef=coef)["ClO4_refi_ppm"]
        base = simular_replay_npt3(d, "baseline_sqm")["ClO4_refi_ppm"]
        real = d["ClO4_Refi_real"]
        return {"calibrado": replay_fit_metrics(real, sim.set_axis(real.index)),
                "original": replay_fit_metrics(real, base.set_axis(real.index))}

    res = {"coef": {k: float(v) for k, v in zip(_PARAMS, sol.x)}, "rmse_censurado_train": float(np.sqrt(np.mean(sol.fun ** 2))),
           "train": evalua(df_train)}
    if df_test is not None:
        res["test"] = evalua(df_test)
    return res
