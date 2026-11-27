"""Pruebas de la interfaz Modelo DPBE·MSMPR (config/ventana_operacion.json) -> Control PID."""
import pytest
from msmpr_core import plant


def test_ventana_operacion_default_sin_cascada_cumple_kpis():
    """Con temp_cascade=False (decisión vigente) la Fase 1 cumple ClO4<40, d50, T y B3520 sin LSL."""
    v = plant.cargar_ventana_operacion()
    assert v["temp_cascade"] is False
    df, res = plant.simular_desde_ventana_operacion(v)
    assert res["temp_cascade_activa"] is False
    assert res["pct_tiempo_ClO4_ok"] == 100.0
    assert res["ppm_ClO4_max_6000"] < 40.0
    assert res["cumple_d50_min"] is True
    assert res["ahorro_agua_vs_real_pct"] > 15.0
    assert res["ahorro_agua_vs_pfd_pct"] > 35.0
    assert res["nivel_min_B3520_pct"] > 20.0
    assert res["pct_tiempo_LSL_B3520"] == 0.0
    assert res["cumple_ventana_global"] is True
    assert "level_B3520_pct" in df.columns


def test_ventana_operacion_cascada_opcional_disponible_y_reduce_offset():
    """La cascada TIR->PIRCAL sigue disponible como opción y elimina el offset térmico si se activa."""
    _, res_sin = plant.simular_desde_ventana_operacion(temp_cascade=False, vac_dist_bar=0.008)
    _, res_con = plant.simular_desde_ventana_operacion(temp_cascade=True, vac_dist_bar=0.008)
    assert res_sin["temp_cascade_activa"] is False
    assert res_con["temp_cascade_activa"] is True
    assert abs(res_con["T2_end_C"] - 40.0) < abs(res_sin["T2_end_C"] - 40.0)
    assert res_con["T2_end_C"] == pytest.approx(40.0, abs=0.15)


def test_ventana_operacion_traduce_R_nom_y_rango_temperaturas():
    """Acepta R_nom (= 1 - alpha) y traduce T1_range_C / T2_range_C a límites de vacío con vac_P."""
    v_custom = {
        "T1_sp_C": 55.0,
        "T2_sp_C": 41.0,
        "T1_range_C": [53.0, 57.0],
        "T2_range_C": [39.0, 43.0],
        "D_nom_t_h": 14.0,
        "D_min_t_h": 6.0,
        "D_max_t_h": 27.14,
        "R_nom": 0.84,
    }
    _, res = plant.simular_desde_ventana_operacion(v_custom, duration_min=120.0)
    assert res["P_vac1_lim_bar"] == (round(plant.vac_P(53.0, 1), 5), round(plant.vac_P(57.0, 1), 5))
    assert res["P_vac2_lim_bar"] == (round(plant.vac_P(39.0, 2), 5), round(plant.vac_P(43.0, 2), 5))
    assert res["temp_cascade_activa"] is False
    assert res["pct_tiempo_ClO4_ok"] == 100.0
