"""Tests de los parches de revisión (RGA/autoridad de MV, Routh-Hopf exacto, anti-windup, replay, alias AIC)."""
import warnings
import numpy as np
import pandas as pd
import pytest

from msmpr_core import control as C, params, plant, replay


def test_mv_authority_marca_alpha_sin_autoridad():
    pl = plant.Plant(params.make_params())
    x0, u0, d0 = pl.steady_state(alpha=0.25)
    G, lam, cvs, mvs = C.rga_from_plant(pl, x0, u0, d0)
    m0 = pl.metrics(np.asarray(x0, float), u0, d0)
    y0 = [x0[1] if k == "T_C" else m0[k] for k in cvs]
    S, sin_aut = C.mv_authority(G, [u0[m] for m in mvs], y0)
    assert sin_aut[list(mvs).index("alpha")], "alpha no debería tener autoridad sobre ppm con V fijo"
    assert not sin_aut[list(mvs).index("m_evap")]


def test_purga_volumetrica_no_depende_de_alpha_con_V_fijo():
    pl = plant.Plant(params.make_params())
    ppm = []
    for a in (0.15, 0.25, 0.35):
        x, u, d = pl.steady_state(alpha=a)
        ppm.append(pl.metrics(x, u, d)["ppm_ClO4"])
    assert max(ppm) - min(ppm) < 0.1


def test_ku_exacto_menor_que_pade():
    r = C.routh_hopf_analysis(375.0, 5.5, 1.0, 3.8, with_exact=True)
    assert abs(r["Ku_exact"]) < abs(r["Kc_hopf"])           # Padé 1/1 no es conservador
    assert r["padeover_pct"] > 10.0
    Ku, Pu = C.ultimate_gain_exact(375.0, 5.5, 1.0, 3.8)
    assert Ku == pytest.approx(0.0221, rel=0.02) and Pu == pytest.approx(4.14, rel=0.02)


def test_ku_exacto_sin_retardo_es_infinito_o_muy_grande():
    Ku, _ = C.ultimate_gain_exact(5.0, 10.0, 1e-6, 10.0)
    assert Ku > 1e3


def test_commercial_pid_no_queda_pegado_en_saturacion():
    pid = C.CommercialPID(Kc=2.0, tau_I=5.0, tau_D=0.0, sp=1.0, u_bias=0.0, u_min=0.0, u_max=1.0)
    for _ in range(200):                    # error grande positivo -> satura arriba
        pid.step(-5.0, 1.0)
    for _ in range(10):                     # el error se invierte: la integral debe poder bajar
        u = pid.step(5.0, 1.0)
    assert u < 1.0


def test_alias_use_AIC3255_deprecado():
    with pytest.warns(DeprecationWarning):
        plant.simulate_plant_npt3_calibrated(use_AIC3255=False, duration_min=1.0, dt_min=0.5)


def test_replay_fit_metrics_matriz_excedencias():
    idx = pd.date_range("2026-11-10", periods=6, freq="2h")
    real = pd.Series([20, 60, 80, 20, 45, 20], index=idx)
    sim = pd.Series([22, 55, 30, 21, 50, 25], index=idx)
    m = replay.replay_fit_metrics(real, sim)
    assert m["excedencias"] == {"TP": 2, "FN": 1, "FP": 0, "TN": 3, "sensibilidad": 2 / 3, "especificidad": 1.0}


def test_kno3_eq_ml_orden_de_magnitud():
    assert 0.5 < replay.kno3_eq_en_ml_t_m3() < 0.8
