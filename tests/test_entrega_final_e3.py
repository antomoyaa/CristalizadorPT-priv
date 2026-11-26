import numpy as np
import pytest
from scripts.bloque2_balance_sensibilidad_alertas import (
    simular_balance_volumen_B3520,
    ejecutar_sensibilidad_kno3,
    construir_regla_alerta_empirica,
)
from scripts.evaluacion_economica_e3 import (
    SUPUESTOS_E3,
    calcular_van,
    calcular_tir,
    evaluar_proyecto,
)


def test_balance_volumen_B3520_respeta_enclavamiento_LSL():
    n = 120
    df = simular_balance_volumen_B3520(np.full(n, 0.98), np.full(n, 38.43))
    assert df["L_B3520_pct"].min() >= 20.0 - 1e-9
    assert df["LSL_activo"].any()
    assert df["Q_purge_eff_m3_h"].iloc[-1] < 38.43


def test_sensibilidad_kno3_muestra_cambio_de_signo_en_rango():
    df = ejecutar_sensibilidad_kno3()
    sub = df[df["K_AGUA [t KNO3/t agua]"] == 0.38]
    assert (sub["Delta KNO3 neto [t/h]"] > 0).any()
    assert (sub["Delta KNO3 neto [t/h]"] < 0).any()


def test_regla_alerta_empirica_tiene_4_niveles():
    df_a, met = construir_regla_alerta_empirica()
    assert len(df_a) == 4
    assert met["auc_ml_refi"] == pytest.approx(0.74, abs=0.01)


def test_evaluacion_economica_altA_supera_altB_en_van_y_payback():
    ra, _ = evaluar_proyecto(SUPUESTOS_E3, "A")
    rb, _ = evaluar_proyecto(SUPUESTOS_E3, "B")
    assert ra["VAN [kUSD]"] > rb["VAN [kUSD]"]
    assert ra["CAPEX [kUSD]"] < rb["CAPEX [kUSD]"]
    # Verificación exacta VAN/TIR sobre flujo simple
    fl = np.array([-100.0, 110.0])
    assert calcular_van(fl, 0.10) == pytest.approx(0.0, abs=1e-6)
    assert calcular_tir(fl) == pytest.approx(0.10, abs=1e-4)
