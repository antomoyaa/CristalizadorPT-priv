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


# ----------------------------------------------------------------- sensores (DelayedSensor separado)
def test_continuous_delay_sensor_segundos():
    s = C.ContinuousDelaySensor(delay_s=10.0, initial=1.0)
    out = [s.read(t, 5.0) for t in (0.0, 5.0, 9.9, 10.0, 15.0)]
    assert out[:3] == [1.0, 1.0, 1.0] and out[3] == 5.0 and out[4] == 5.0


def test_discrete_filtered_sensor_minutos_y_resolucion():
    s = C.DiscreteFilteredSensor(theta_min=1.0, tau_m_min=0.0, dt_min=0.5, initial_val=2.0, resolution=0.1)
    lecturas = [s.read(3.0) for _ in range(4)]
    assert lecturas[0] == pytest.approx(2.0) and lecturas[-1] == pytest.approx(3.0)


def test_delayed_sensor_shim_despacha_y_avisa():
    with pytest.warns(DeprecationWarning):
        a = C.DelayedSensor(10.0, 1.0)
    with pytest.warns(DeprecationWarning):
        b = C.DelayedSensor(1.0, 0.5, 0.5, 2.0)
    assert isinstance(a, C.ContinuousDelaySensor) and isinstance(b, C.DiscreteFilteredSensor)


# ----------------------------------------------------------------- RGA con purga como MV (cierre de volumen con dilución)
def test_rga_purga_como_mv_es_independiente_de_T_y_densidad():
    pl = plant.Plant(params.make_params())
    x0, u0, d0 = pl.steady_state(alpha=0.25)
    G, lam, cvs, mvs = C.rga_from_plant(pl, x0, u0, d0, mv_names=("m_evap", "Q_out", "Q_purge"),
                                        volume_closure="Q_dil", t_settle_s=28800)
    i, j = cvs.index("ppm_ClO4"), mvs.index("Q_purge")
    assert lam[i, j] == pytest.approx(1.0, abs=0.05)
    Qp = u0["alpha"] * u0["Q_out"]
    ppm0 = pl.metrics(np.asarray(x0, float), dict(u0, Q_purge=Qp), d0)["ppm_ClO4"]
    assert G[i, j] == pytest.approx(-ppm0 / Qp, rel=0.2)         # ppm ~ 1/purga


def test_rga_volume_closure_invalido():
    pl = plant.Plant(params.make_params())
    x0, u0, d0 = pl.steady_state(alpha=0.25)
    with pytest.raises(ValueError):
        C.rga_from_plant(pl, x0, u0, d0, volume_closure="otro")


# ----------------------------------------------------------------- 6.7: recirculación inteligente (saturación de purga)
def _smart(**kw):
    return plant.simular_recirculacion_y_magnesio("reciclo_inteligente", use_AIT3105=True, hipotesis_mg="combinada", **kw)


def test_recirculacion_original_se_mantiene_con_defaults():
    d = _smart()
    assert d["ppm_ClO4_final_6000"].max() == pytest.approx(67.6, abs=0.3)          # arranque con reciclo
    assert d[d.t_min > 150]["ppm_ClO4_final_6000"].iloc[-1] == pytest.approx(44.4, abs=0.3)
    assert d["alpha_purge_pct"].iloc[-1] == pytest.approx(100.0, abs=0.5)           # purga saturada
    assert "F_303_t_h" in d.columns


def test_alpha0_1_elimina_transitorio_de_arranque():
    d = _smart(alpha0=1.0)
    assert d[d.t_min < 140]["ppm_ClO4_final_6000"].max() < 40.0


def test_trim_por_saturacion_devuelve_autoridad_tras_el_escalon_de_mg():
    sin = _smart(alpha0=1.0, F_303_max=60.0)
    con = _smart(alpha0=1.0, k_trim_sat=0.10, F_303_max=60.0)
    assert sin["ppm_ClO4_final_6000"].iloc[-1] > 40.0
    assert con["ppm_ClO4_final_6000"].max() < 40.0
    assert con["F_303_t_h"].iloc[-1] > sin["F_303_t_h"].iloc[-1]

# ----------------------------------------------------------------- 6.12: cascada TIR -> PIRCAL y seguimiento KNO3 / d50
def test_cascada_temperatura_corrige_offset_vs_manual():
    """Sin cascada (PIRCAL manual) T2 queda con offset; con cascada TIR->PIRCAL regresa a consigna."""
    man = plant.simulate_plant_npt3_calibrated(
        use_AIT3105=False, use_AIC3522=False,
        temp_cascade=False, use_slave_PIRCAL=True, vac_dist_bar=0.008,
    )
    aut = plant.simulate_plant_npt3_calibrated(
        use_AIT3105=True, use_AIC3522=True,
        temp_cascade=True, use_slave_PIRCAL=True, vac_dist_bar=0.008,
        F_303_nom=0.50, F_303_min=0.20, F_303_max=2.50,
    )
    sp43 = plant.simulate_plant_npt3_calibrated(
        use_AIT3105=True, use_AIC3522=True,
        temp_cascade=True, use_slave_PIRCAL=True, T2_sp_C=43.0,
        F_303_nom=0.50, F_303_min=0.20, F_303_max=2.50,
    )
    assert man["T2_C"].iloc[-1] > 41.0
    assert aut["T2_C"].iloc[-1] == pytest.approx(40.0, abs=0.15)
    assert sp43["T2_C"].iloc[-1] == pytest.approx(43.0, abs=0.25)


def test_columnas_kno3_y_d50_en_simulacion_integrada():
    """Verifica columnas KNO3/P_vac_sp sin NaN y mayor KNO3/d50 en régimen sostenible vs. PFD."""
    sost = plant.simulate_plant_npt3_calibrated(
        use_AIT3105=True, use_AIC3522=True,
        temp_cascade=True, use_slave_PIRCAL=True, vac_dist_bar=0.008,
        F_303_nom=0.50, F_303_min=0.20, F_303_max=2.50,
    )
    pfd = plant.simulate_plant_npt3_calibrated(
        use_AIT3105=True, use_AIC3522=True,
        temp_cascade=True, use_slave_PIRCAL=True, vac_dist_bar=0.008,
        F_303_nom=27.14, F_303_min=12.0, F_303_max=42.0,
    )
    cols = ("P_vac1_sp_bar", "P_vac2_sp_bar", "C_KNO3_in1_kg_m3", "C_KNO3_1_kg_m3", "C_KNO3_2_kg_m3")
    for c in cols:
        assert c in sost.columns and sost[c].notna().all()
    assert sost["C_KNO3_in1_kg_m3"].mean() > pfd["C_KNO3_in1_kg_m3"].mean()
    assert sost["d50_2_um"].iloc[-1] > pfd["d50_2_um"].iloc[-1]
