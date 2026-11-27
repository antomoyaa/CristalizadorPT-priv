"""Tests de mg_trazador con datos SINTÉTICOS (no usa datos de SQM)."""
import numpy as np
import pandas as pd
import pytest

from msmpr_core import mg_trazador as M


def _tabla(n=3000, seed=1, exceso_ppm=0.0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2025-01-01", periods=n, freq="h")
    mg_licor = rng.normal(31, 3, n)
    clo4_licor = rng.normal(3.6, 0.4, n)
    frac = rng.normal(0.05, 0.01, n).clip(0.01, 0.12)                 # licor adherido (fracción másica)
    mg_cristal_pct = frac * (mg_licor / 1.45 * 1000.0) / 1e4          # % másico
    exceso = exceso_ppm * rng.uniform(0.5, 1.5, n)
    clo4_cristal = frac * (clo4_licor / 1.45 * 1000.0) + exceso
    refi = np.maximum(20.0, 20.0 + 0.15 * exceso + rng.normal(0, 5, n))   # el refinado solo depende de la parte NO adherida
    return pd.DataFrame({M.COLS["mg_cristal"]: mg_cristal_pct, M.COLS["mg_licor"]: mg_licor, M.COLS["clo4_licor_gL"]: clo4_licor,
                         M.COLS["kclo4_licor_gL"]: clo4_licor * 1.39, M.COLS["clo4_cristal"]: clo4_cristal, M.COLS["refi_ppm"]: refi,
                         M.COLS["ml_refi_kclo4"]: rng.normal(1.5, 0.5, n)}, index=idx)


def test_sin_exceso_todo_el_clo4_lo_explica_el_licor():
    x = M.trazador_licor_adherido(_tabla())
    assert x["frac_exceso"].median() == pytest.approx(0.0, abs=0.02)
    assert x["licor_adherido_frac"].median() == pytest.approx(0.05, abs=0.005)


def test_con_exceso_se_detecta_la_fraccion_no_explicada():
    x = M.trazador_licor_adherido(_tabla(exceso_ppm=150.0))
    r = M.resumen_trazador(x)
    assert 0.3 < r["frac_exceso_mediana"] < 0.8
    assert r["AUC_refinado_gt40"]["exceso_no_explicado"] > r["AUC_refinado_gt40"]["explicado_por_licor"]


def test_envolvente_devuelve_techo_por_tramo_de_mg():
    e = M.envolvente_kclo4_vs_mg(_tabla())
    assert {"n", "mediana", "techo"} <= set(e.columns)
    assert (e["techo"].dropna() >= e["mediana"].dropna()).all()
