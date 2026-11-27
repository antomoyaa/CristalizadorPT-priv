"""Pruebas unitarias de los Bloques 2 y 3 (balance B3520, sensibilidad KNO3, alertas y economía E3)."""
import numpy as np
import pytest

from scripts.bloque2_balance_sensibilidad_alertas import (
    construir_regla_alerta_empirica,
    evaluar_escenarios_b3520,
    sensibilidad_beneficio_kno3,
)
from scripts.evaluacion_economica_e3 import (
    SUPUESTOS_E3,
    calcular_tir,
    calcular_van,
    evaluar_proyecto,
)


def test_balance_b3520_corte_extremo_falla_pero_fase1_y_fase2_cumplen():
    df_b, _ = evaluar_escenarios_b3520()
    extremo = df_b[df_b["Escenario"].str.contains("Corte extremo")].iloc[0]
    fase1 = df_b[df_b["Escenario"].str.contains("Fase 1")].iloc[0]
    fase2 = df_b[df_b["Escenario"].str.contains("Fase 2")].iloc[0]
    assert extremo["% tiempo en LSL (20 %)"] > 80.0
    assert fase1["% tiempo en LSL (20 %)"] == 0.0 and fase1["Ahorro agua [%]"] == pytest.approx(39.9, abs=0.5)
    assert fase2["% tiempo en LSL (20 %)"] == 0.0 and fase2["Ahorro agua [%]"] == pytest.approx(74.9, abs=0.5)


def test_sensibilidad_kno3_fase1_es_siempre_positiva():
    df_f1, df_30d = sensibilidad_beneficio_kno3()
    vals_f1 = df_f1.drop(columns=["K_AGUA [t/t]"]).values
    assert (vals_f1 > 0.0).all()
    assert df_30d.loc[df_30d["K_AGUA [t/t]"] == 0.38, "K_PURGA=0.6"].iloc[0] < 0.0


def test_regla_alerta_empirica_tiene_4_niveles():
    df_a, met = construir_regla_alerta_empirica()
    assert len(df_a) == 4
    assert met["auc_ml_refi"] >= 0.70


def test_evaluacion_economica_calibrada_altA_gana_y_altB_negativa_en_base():
    ra, _ = evaluar_proyecto(SUPUESTOS_E3, "A")
    rb, _ = evaluar_proyecto(SUPUESTOS_E3, "B")
    rf1, _ = evaluar_proyecto({**SUPUESTOS_E3, "delta_eta": 0.025, "ahorro_agua_t_h": 7.96}, "A")
    assert ra["CAPEX [kUSD]"] == pytest.approx(159.3, abs=0.2)
    assert ra["VAN [kUSD]"] == pytest.approx(130.6, abs=1.5)
    assert rb["VAN [kUSD]"] < 0.0
    assert rf1["VAN [kUSD]"] > ra["VAN [kUSD]"] > 0.0
    fl = np.array([-100.0, 110.0])
    assert calcular_van(fl, 0.10) == pytest.approx(0.0, abs=1e-6)
    assert calcular_tir(fl) == pytest.approx(0.10, abs=1e-4)
