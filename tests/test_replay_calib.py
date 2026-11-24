"""Tests de replay_calib con datos SINTÉTICOS (no usa datos de SQM)."""
import numpy as np
import pandas as pd

from msmpr_core import replay, replay_calib as RC


def _df(n=800, seed=0, dependiente_de_mlk=False):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2025-01-01", periods=n, freq="2h")
    mlr = np.clip(rng.normal(1.8, 0.8, n), 0.2, 7.0)
    crudo = np.clip(rng.normal(250, 120, n) + 60 * mlr, 50, 2000)
    mlk = rng.normal(3.7, 0.5, n)
    refi = np.maximum(20, 8 + 12 * mlr + 0.03 * crudo + (25 * (mlk - 3.7) if dependiente_de_mlk else 0) + rng.normal(0, 6, n))
    return pd.DataFrame({"mlrefi_KClO4": mlr, "crudo_ppm": crudo, "crudo_Mg": 0.1, "mlk_Mg": rng.normal(31, 3, n),
                         "mlk_KClO4": mlk * 1.39, "mlk_ClO4": mlk, "refi_ppm": refi, "T2": 40.0}, index=idx).assign(
        Csat=4.3, exceso=lambda d: (d["mlk_ClO4"] - 4.3).clip(lower=0))


def test_auc_ordena_predictores_correctos():
    comp = RC.comparar_predictores(_df(), corte="2025-02-15").set_index("predictor")
    assert comp.loc["ML refinación KClO4 (g/L)", "AUC_test"] > 0.7
    assert abs(comp.loc["KClO4 del MLK (g/L)", "AUC_test"] - 0.5) < 0.12


def test_diagnostico_sin_dependencia_mlk_da_correlacion_nula():
    d = RC.diagnostico_mecanismo(_df())
    assert abs(d["spearman_refi"]["mlk_ClO4"]) < 0.1
    assert abs(d["rezago_crudo_vs_mlkClO4_h"][2]) < 0.1


def test_coef_replay_por_defecto_no_cambia_resultado():
    idx = pd.date_range("2026-11-10", periods=60, freq="10min")
    n = len(idx)
    df = pd.DataFrame({"t_h": np.arange(n) / 6, "Q_SSKd_m3_h": 243.0, "ClO4_SSK": 4.5, "ClO4_MLK_real": 4.6, "Mg_MLK_real": 32.0,
                       "ClO4_MLRefi_real": 1.5, "T_A3210_real": 43.0, "Q_dil_real": 20.0, "Q_purga_real": 20.4}, index=idx)
    a = replay.simular_replay_npt3(df, "baseline_sqm")
    b = replay.simular_replay_npt3(df, "baseline_sqm", coef=dict(replay.COEF_REPLAY))
    pd.testing.assert_frame_equal(a, b)
    assert {"C_MLRefi_g_L", "ppm_refi_sin_piso"} <= set(a.columns)
