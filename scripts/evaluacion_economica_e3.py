"""Bloque 3 (Entrega Final E3): Evaluación Económica Calibrada con Planilla del Equipo.

Alineada con Analisis_TE_Byueno_con a_sensibilidad.xlsx (Towler & Sinnott, WACC = 14,11 %,
horizonte 10 años, depreciación lineal 5 años sobre FCI, rampa 50 % Año 1, impuesto 25,5 % -> 23 % en 2029).
"""
from __future__ import annotations

import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]

AHORRO_REAL = 3.96   # se recalcula en main() con la simulación de planta
AGUA_REAL_SIM = 16.0

SUPUESTOS_E3 = {
    "capex_eq_A": 52100.0,        # USD (FV 3522 + sensorica/DCS + DB&B, planilla equipo)
    "capex_eq_B_extra": 85000.0,  # USD adicionales por analizadores en línea AIT 3105 / AIC 3522
    "f_inst": 2.0,                # Factor de instalación ISBL (Towler & Sinnott)
    "f_de": 0.30,                 # Diseño e ingeniería (30 % ISBL)
    "f_cont": 0.20,               # Contingencia (20 % ISBL)
    "camp_calib": 3000.0,         # Campaña experimental previa de calibración (USD)
    "opex_water_base": 7722.0,    # USD/año (agua operación/lavado planilla equipo)
    "opex_lab_A": 2400.0,         # USD/año (LIMS c/2 h)
    "opex_lab_B": 14400.0,        # USD/año (reactivos/mantención analizadores en línea)
    "delta_eta": 0.020,           # Mejora conservadora de eficiencia global (2,0 % vs. meta SQM 5-10 %)
    "precio_kno3": 875.0,         # USD/t (promedio rango SQM 800-950 USD/t)
    "margen_op": 0.15,            # Margen operacional (15 % -> Mu = 131,25 USD/t)
    "tarifa_agua": 1.95,          # USD/m³ (tarifa SISS / agua industrial)
    "ahorro_agua_t_h": 0.0,       # t/h agua dilución ahorrada (0,0 Caso Base; 7,96 Fase 1)
    "wacc": 0.1411,               # Tasa de descuento anual (14,11 %)
    "tax_y1": 0.255,              # Impuesto 1ra categoría año 1 = 2027 (25,5 %)
    "tax_y2": 0.240,              # año 2 = 2028 (24,0 %)
    "tax_y3p": 0.230,             # desde el año 3 = 2029 (23,0 %); gradualidad de la ley de agosto 2026 (supone año 1 = 2027)
    "dep_years": 5,               # Depreciación lineal 5 años sobre FCI
    "horizon": 10,                # Horizonte de evaluación (años)
    "ramp_y1": 0.50,              # Reconocimiento 50 % beneficios en Año 1
}


def ahorro_agua_realizado_t_h(D_nom: float = 12.0, agua_real: float = 19.96) -> tuple[float, float]:
    """Ahorro de agua REALIZADO (no nominal) de la simulación de planta bajo las perturbaciones de la ventana.

    Devuelve (ahorro [t/h] respecto de la media real de planta, agua media realizada [t/h]). El setpoint nominal no es el agua
    realizada: los trims por ClO4-/Mg del lazo agregan agua al perturbarse la planta.
    """
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from msmpr_core import plant as P
    ventana = P.cargar_ventana_operacion()
    _, res = P.simular_desde_ventana_operacion({**ventana, "D_nom_t_h": D_nom})
    return max(agua_real - float(res["agua_media_t_h"]), 0.0), float(res["agua_media_t_h"])


def calcular_van(flujos: np.ndarray, tasa: float) -> float:
    t = np.arange(len(flujos), dtype=float)
    return float(np.sum(flujos / ((1.0 + tasa) ** t)))


def calcular_tir(flujos: np.ndarray) -> float:
    lo, hi = -0.50, 5.00
    if calcular_van(flujos, lo) * calcular_van(flujos, hi) >= 0:
        return float("nan")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if calcular_van(flujos, mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def evaluar_proyecto(sup: dict, alternativa: str = "A") -> tuple[dict, pd.DataFrame]:
    s = {**SUPUESTOS_E3, **sup}
    capex_eq = s["capex_eq_A"] + (s["capex_eq_B_extra"] if alternativa == "B" else 0.0)
    isbl = capex_eq * s["f_inst"]
    fci = isbl * (1.0 + s["f_de"] + s["f_cont"])
    capex_tot = fci + s["camp_calib"]

    opex_lab = s["opex_lab_B"] if alternativa == "B" else s["opex_lab_A"]
    opex_tot = s["opex_water_base"] + opex_lab + 0.06 * isbl

    H_op = 7920.0
    Mu = s["precio_kno3"] * s["margen_op"]
    m_ref = 500000.0 / H_op
    m_crudo = 76.76
    eta_6000 = m_ref / m_crudo
    d_eta = s["delta_eta"]

    b1 = 281.70101858513 * 0.0146341463414634 * H_op * d_eta * eta_6000 * Mu
    b2 = 80.0 * d_eta * m_ref * Mu
    b3 = ((m_crudo - m_ref) / 100.0) * H_op * d_eta * Mu
    b4 = (500000.0 * (63.0 / 5531.0)) * (1.0 - eta_6000) * d_eta * Mu
    b5 = (4.61 * ((m_crudo + (500000.0 * (63.0 / 5531.0)) / H_op) / m_crudo) * H_op) * d_eta * s["tarifa_agua"]
    b_agua_dil = s["ahorro_agua_t_h"] * H_op * s["tarifa_agua"]
    ben_reg = b1 + b2 + b3 + b4 + b5 + b_agua_dil

    dep_ann = fci / s["dep_years"]
    flujos = [-capex_tot]
    rows_cf = [{
        "Año": 0, "Beneficio [kUSD]": 0.0, "OPEX [kUSD]": 0.0, "EBITDA [kUSD]": 0.0,
        "Deprec. [kUSD]": 0.0, "Impuesto [kUSD]": 0.0, "Flujo Neto [kUSD]": round(-capex_tot / 1e3, 2),
        "Flujo Desc. [kUSD]": round(-capex_tot / 1e3, 2), "Acum. Desc. [kUSD]": round(-capex_tot / 1e3, 2),
    }]
    cum = -capex_tot
    cum_disc = -capex_tot
    pb_s = pb_d = float("nan")

    for yr in range(1, int(s["horizon"]) + 1):
        ben = ben_reg * (s["ramp_y1"] if yr == 1 else 1.0)
        ebitda = ben - opex_tot
        dep = dep_ann if yr <= s["dep_years"] else 0.0
        ebit = ebitda - dep
        tr = s["tax_y1"] if yr == 1 else (s["tax_y2"] if yr == 2 else s["tax_y3p"])
        tax = max(ebit * tr, 0.0)
        fc = ebitda - tax
        dfc = fc / ((1.0 + s["wacc"]) ** yr)
        pc, pcd = cum, cum_disc
        cum += fc
        cum_disc += dfc
        if np.isnan(pb_s) and cum >= 0:
            pb_s = (yr - 1) + (-pc) / fc
        if np.isnan(pb_d) and cum_disc >= 0:
            pb_d = (yr - 1) + (-pcd) / dfc
        flujos.append(fc)
        rows_cf.append({
            "Año": yr, "Beneficio [kUSD]": round(ben / 1e3, 2), "OPEX [kUSD]": round(opex_tot / 1e3, 2),
            "EBITDA [kUSD]": round(ebitda / 1e3, 2), "Deprec. [kUSD]": round(dep / 1e3, 2),
            "Impuesto [kUSD]": round(tax / 1e3, 2), "Flujo Neto [kUSD]": round(fc / 1e3, 2),
            "Flujo Desc. [kUSD]": round(dfc / 1e3, 2), "Acum. Desc. [kUSD]": round(cum_disc / 1e3, 2),
        })

    arr = np.asarray(flujos, float)
    van = calcular_van(arr, s["wacc"])
    tir = calcular_tir(arr)
    resumen = {
        "Alternativa": "A (Recomendada: DCS + FV 3522 + LIMS)" if alternativa == "A" else "B (Con analizadores en línea AIT/AIC)",
        "CAPEX [kUSD]": round(capex_tot / 1e3, 1),
        "OPEX [kUSD/año]": round(opex_tot / 1e3, 1),
        "Beneficio bruto [kUSD/año]": round(ben_reg / 1e3, 1),
        "VAN [kUSD]": round(van / 1e3, 1),
        "TIR [%]": round(100.0 * tir, 1) if not np.isnan(tir) else float("nan"),
        "Payback simple [años]": round(pb_s, 2) if not np.isnan(pb_s) else float("nan"),
        "Payback descontado [años]": round(pb_d, 2) if not np.isnan(pb_d) else float("nan"),
    }
    return resumen, pd.DataFrame(rows_cf)


def main():
    global AHORRO_REAL
    AHORRO_REAL, AGUA_REAL_SIM = ahorro_agua_realizado_t_h()
    ra, fc_a = evaluar_proyecto(SUPUESTOS_E3, "A")
    rb, fc_b = evaluar_proyecto(SUPUESTOS_E3, "B")
    df_comp = pd.DataFrame([ra, rb])

    escenarios = [
        ("Conservador Estricto (Δη=1,3 %, f=2,2, P=800)", dict(delta_eta=0.013, f_inst=2.2, precio_kno3=800.0)),
        ("Caso Base Conservador (Δη=2,0 %, sin agua dil.)", dict()),
        ("Fase 1 con ahorro de agua NOMINAL (Δη=2,5 % + 7,96 t/h, cota superior)", dict(delta_eta=0.025, ahorro_agua_t_h=7.96)),
        (f"Fase 1 con ahorro de agua REALIZADO ({AHORRO_REAL:.2f} t/h; Δη=2,5 %)", dict(delta_eta=0.025, ahorro_agua_t_h=AHORRO_REAL)),
        ("Optimista (Δη=5,0 % meta SQM, f=1,5, P=950)", dict(delta_eta=0.050, f_inst=1.5, precio_kno3=950.0)),
    ]
    rows_esc = []
    for nom, kw in escenarios:
        r, _ = evaluar_proyecto({**SUPUESTOS_E3, **kw}, "A")
        rows_esc.append({
            "Escenario": nom, "CAPEX [kUSD]": r["CAPEX [kUSD]"],
            "Beneficio bruto [kUSD/año]": r["Beneficio bruto [kUSD/año]"],
            "VAN [kUSD]": r["VAN [kUSD]"], "TIR [%]": r["TIR [%]"],
            "Payback simple [años]": r["Payback simple [años]"],
            "Payback descontado [años]": r["Payback descontado [años]"],
        })
    df_esc = pd.DataFrame(rows_esc)

    van_base = ra["VAN [kUSD]"]
    specs_tor = [
        ("Mejora eficiencia Δη (1,0 % vs 3,5 %)", dict(delta_eta=0.010), dict(delta_eta=0.035)),
        ("Ahorro agua dilución Fase 1 (0 vs 7,96 t/h nominal)", dict(ahorro_agua_t_h=0.0), dict(ahorro_agua_t_h=7.96)),
        ("Factor instalación f_inst (3,5 vs 1,5)", dict(f_inst=3.5), dict(f_inst=1.5)),
        ("Margen operacional (12 % vs 18 %)", dict(margen_op=0.12), dict(margen_op=0.18)),
        ("Tasa descuento WACC (18 % vs 10 %)", dict(wacc=0.18), dict(wacc=0.10)),
        ("Precio KNO$_3$ (800 vs 950 USD/t)", dict(precio_kno3=800.0), dict(precio_kno3=950.0)),
    ]
    rows_tor = []
    for nom, klo, khi in specs_tor:
        vlo = evaluar_proyecto({**SUPUESTOS_E3, **klo}, "A")[0]["VAN [kUSD]"]
        vhi = evaluar_proyecto({**SUPUESTOS_E3, **khi}, "A")[0]["VAN [kUSD]"]
        rows_tor.append({
            "Variable": nom.replace("$_3$", "₃"), "VAN Bajo [kUSD]": vlo, "VAN Alto [kUSD]": vhi,
            "Amplitud [kUSD]": round(abs(vhi - vlo), 1), "_lbl": nom,
        })
    df_tor_plot = pd.DataFrame(rows_tor).sort_values("Amplitud [kUSD]", ascending=True)
    df_tor = df_tor_plot.drop(columns=["_lbl"]).sort_values("Amplitud [kUSD]", ascending=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = np.arange(len(df_tor_plot))
    for i, row in enumerate(df_tor_plot.itertuples(index=False)):
        vlo, vhi = row[1], row[2]
        ax.barh(i, vlo - van_base, left=van_base, color="tab:red", alpha=0.82, height=0.55,
                label="Escenario desfavorable" if i == 0 else None)
        ax.barh(i, vhi - van_base, left=van_base, color="tab:green", alpha=0.82, height=0.55,
                label="Escenario favorable" if i == 0 else None)
    ax.axvline(van_base, color="navy", ls="--", lw=1.6, label=f"Caso Base Conservador (VAN = {van_base:.1f} kUSD)")
    ax.axvline(0.0, color="k", ls=":", lw=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels(df_tor_plot["_lbl"], fontsize=9)
    ax.set(xlabel="VAN a 10 años [kUSD] (WACC = 14,11 %)",
           title="Análisis de Sensibilidad Tornado — Alternativa A (Propuesta E3 Calibrada)")
    ax.legend(fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(ROOT / "docs" / "fig" / "14_tornado_economico_E3.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    with pd.ExcelWriter(ROOT / "docs" / "evaluacion_economica_E3.xlsx", engine="openpyxl") as w:
        df_comp.to_excel(w, sheet_name="Comparativa_Alt", index=False)
        df_esc.to_excel(w, sheet_name="Escenarios_AltA", index=False)
        df_tor.to_excel(w, sheet_name="Tornado", index=False)
        fc_a.to_excel(w, sheet_name="Flujo_Caja_AltA", index=False)
        fc_b.to_excel(w, sheet_name="Flujo_Caja_AltB", index=False)

    md = [
        "# Evaluación Económica E3 (Calibrada con Planilla del Equipo — Towler & Sinnott)\n",
        "Base: WACC = `14,11 %`, horizonte `10 años`, depreciación lineal `5 años` sobre FCI, rampa `50 %` Año 1, impuesto `25,5 %` (año 1 = 2027), `24,0 %` (año 2) y `23,0 %` (desde año 3), con año 1 = 2027, campaña de calibración `3,0 kUSD`.\n",
        "## 1. Comparativa de Alternativas (Caso Base Conservador, Δη = 2,0 % sin crédito de agua de dilución)\n",
        df_comp.to_markdown(index=False),
        "\n\n## 2. Escenarios de Alternativa A (Fase 1: ahorro de agua nominal y realizado)\n",
        f"El setpoint de Fase 1 (12,0 t/h) recorta 7,96 t/h solo en términos nominales; bajo las perturbaciones de la simulación el agua media realizada es {AGUA_REAL_SIM:.1f} t/h, es decir un ahorro de {AHORRO_REAL:.2f} t/h frente a la media real de 19,96 t/h. El escenario nominal es una cota superior.\n",
        df_esc.to_markdown(index=False),
        "\n\n## 3. Análisis de Sensibilidad (Tornado — 6 Variables)\n",
        df_tor.to_markdown(index=False),
        "\n\n## 4. Flujo de Caja Descontado — Alternativa A (Caso Base Conservador)\n",
        fc_a.to_markdown(index=False),
        "\n",
    ]
    (ROOT / "docs" / "evaluacion_economica_E3.md").write_text("\n".join(md), encoding="utf-8")
    print("[OK] Bloque 3 calibrado:")
    print(df_comp.to_string(index=False))
    print("\n--- Escenarios Alternativa A ---")
    print(df_esc.to_string(index=False))


if __name__ == "__main__":
    main()
