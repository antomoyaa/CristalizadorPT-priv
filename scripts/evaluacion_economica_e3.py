"""Bloque 3 (Entrega Final E3 — IIQ3253):
Evaluación económica comparativa (Alternativa A recomendada vs. Alternativa B con AIT en línea):
- CAPEX / OPEX detallados (supuestos referenciales de ingeniería editables).
- Flujo de caja descontado a 10 años después de impuestos (tasa corporativa Chile 27 %).
- Indicadores: VAN (VPN), TIR, Payback simple y descontado.
- 3 Escenarios (Conservador, Base, Optimista) + Tornado de sensibilidad (5 variables).
Exporta docs/evaluacion_economica_E3.md, docs/evaluacion_economica_E3.xlsx y docs/fig/14_tornado_economico_E3.png.
"""
from __future__ import annotations

import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "docs" / "fig"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# SUPUESTOS REFERENCIALES EDITABLES (confirmar/ajustar con equipo económico/SQM)
# ==============================================================================
SUPUESTOS_E3 = {
    # Parámetros financieros
    "horizonte_anos": 10,
    "wacc": 0.10,                 # Tasa de descuento real anual (10 % base; sensibilidad 8–12 %)
    "tasa_impuesto": 0.27,        # Impuesto de primera categoría Chile (27 %)
    "vida_util_dep": 10,          # Depreciación lineal [años]

    # CAPEX Alternativa A (Recomendada: FV 3522 + DCS TIR->PIRCAL + LIMS + Alertas A6000) [USD]
    "capex_valvula_fv3522": 65_000.0,     # Válvula V-port dúplex + actuador + DBB + montaje
    "capex_dcs_cascada_lims": 45_000.0,   # Programación DCS TIR->PIRCAL, LSL, interfaz LIMS y alarmas
    "capex_ingenieria_hazop": 35_000.0,   # Ingeniería de detalle, HAZOP formal y comisionamiento
    "contingencia_frac": 0.20,            # 20 % contingencia brownfield

    # CAPEX adicional Alternativa B (Analizador en línea AIT 3105) [USD]
    "capex_extra_ait_linea": 220_000.0,   # Analizador en línea + sistema de acondicionamiento de muestra
    "opex_extra_ait_linea": 38_000.0,     # Reactivos, calibración y mantención anual del analizador

    # OPEX anual Alternativa A [USD/año]
    "opex_mantencion_a": 14_000.0,        # Mantención válvula, calibración instrumentos, soporte DCS

    # Base operacional y beneficios conservadores (ligados a datos reales SQM)
    "produccion_anual_t": 520_000.0,      # ~65 t/h x 8 000 h/año (dato PFD/base química)
    "frac_fuera_spec_base": 0.175,        # 17,5 % muestras > 40 ppm (dato real n = 6 966)
    "captura_reduccion_rechazos": 0.35,   # Fracción conservadora de excedencias evitadas (35 % base)
    "costo_reproceso_usd_t": 22.0,        # Costo evitado por tonelada no reprocesada/degradada [USD/t] (editable)
    "ahorro_agua_t_h": 6.0,               # Reducción parcial prudente de dilución [t/h] (NO asume 19 t/h sin balance)
    "horas_ano": 8_000.0,
    "costo_agua_usd_m3": 2.5,             # Costo referencial agua industrial/desalinizada norte Chile [USD/m³]
    "delta_kno3_neto_t_h": 0.0,           # 0,0 t/h en caso base conservador (por incertidumbre K_PURGA Bloque 2)
    "margen_kno3_usd_t": 180.0,           # Margen neto por tonelada adicional de KNO3 [USD/t] (editable)
}


def calcular_van(flujos: np.ndarray, tasa: float) -> float:
    t = np.arange(len(flujos), dtype=float)
    return float(np.sum(flujos / ((1.0 + tasa) ** t)))


def calcular_tir(flujos: np.ndarray) -> float:
    """Calcula TIR por bisección robusta en [-0.95, 10.0]."""
    if flujos[0] >= 0 or np.sum(flujos[1:]) <= 0:
        return float("nan")
    lo, hi = -0.95, 10.0
    f_lo, f_hi = calcular_van(flujos, lo), calcular_van(flujos, hi)
    if f_lo * f_hi > 0:
        return float("nan")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        f_mid = calcular_van(flujos, mid)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return 0.5 * (lo + hi)


def calcular_payback(flujos: np.ndarray, tasa: float = 0.0) -> float:
    t = np.arange(len(flujos), dtype=float)
    desc = flujos / ((1.0 + tasa) ** t)
    acum = np.cumsum(desc)
    for k in range(1, len(acum)):
        if acum[k] >= 0:
            prev = acum[k - 1]
            return float((k - 1) + (-prev) / max(desc[k], 1e-9))
    return float("inf")


def evaluar_proyecto(sup: dict, alternativa: str = "A") -> tuple[dict, pd.DataFrame]:
    """Genera flujo de caja descontado e indicadores para Alternativa A o B."""
    n = int(sup["horizonte_anos"])
    capex_base = (
        sup["capex_valvula_fv3522"]
        + sup["capex_dcs_cascada_lims"]
        + sup["capex_ingenieria_hazop"]
    )
    if alternativa == "B":
        capex_base += sup["capex_extra_ait_linea"]
    capex_total = capex_base * (1.0 + sup["contingencia_frac"])

    opex_anual = sup["opex_mantencion_a"] + (sup["opex_extra_ait_linea"] if alternativa == "B" else 0.0)

    # Beneficios anuales [USD/año]
    t_evitadas = sup["produccion_anual_t"] * sup["frac_fuera_spec_base"] * sup["captura_reduccion_rechazos"]
    # Alternativa B aporta una captura marginal pequeña adicional (+5 % relativo) por menor retardo
    if alternativa == "B":
        t_evitadas *= 1.05
    ben_calidad = t_evitadas * sup["costo_reproceso_usd_t"]
    ben_agua = sup["ahorro_agua_t_h"] * sup["horas_ano"] * sup["costo_agua_usd_m3"]
    ben_kno3 = sup["delta_kno3_neto_t_h"] * sup["horas_ano"] * sup["margen_kno3_usd_t"]
    ben_total = ben_calidad + ben_agua + ben_kno3

    dep = capex_total / sup["vida_util_dep"]
    flujos = np.zeros(n + 1)
    flujos[0] = -capex_total

    filas_fc = [{
        "Año": 0, "Beneficios [kUSD]": 0.0, "OPEX [kUSD]": 0.0, "Depreciación [kUSD]": 0.0,
        "UAI [kUSD]": 0.0, "Impuesto [kUSD]": 0.0, "Flujo Neto [kUSD]": -capex_total / 1e3,
        "Flujo Descontado [kUSD]": -capex_total / 1e3,
    }]

    for yr in range(1, n + 1):
        uai = ben_total - opex_anual - dep
        imp = max(0.0, uai * sup["tasa_impuesto"])
        f_neto = (ben_total - opex_anual) - imp
        flujos[yr] = f_neto
        f_desc = f_neto / ((1.0 + sup["wacc"]) ** yr)
        filas_fc.append({
            "Año": yr,
            "Beneficios [kUSD]": round(ben_total / 1e3, 1),
            "OPEX [kUSD]": round(-opex_anual / 1e3, 1),
            "Depreciación [kUSD]": round(-dep / 1e3, 1),
            "UAI [kUSD]": round(uai / 1e3, 1),
            "Impuesto [kUSD]": round(-imp / 1e3, 1),
            "Flujo Neto [kUSD]": round(f_neto / 1e3, 1),
            "Flujo Descontado [kUSD]": round(f_desc / 1e3, 1),
        })

    van = calcular_van(flujos, sup["wacc"])
    tir = calcular_tir(flujos)
    pb_s = calcular_payback(flujos, 0.0)
    pb_d = calcular_payback(flujos, sup["wacc"])

    resumen = {
        "Alternativa": "A (Recomendada: DCS + FV 3522 + LIMS)" if alternativa == "A" else "B (Con analizador en línea AIT)",
        "CAPEX [kUSD]": round(capex_total / 1e3, 1),
        "OPEX [kUSD/año]": round(opex_anual / 1e3, 1),
        "Beneficio bruto [kUSD/año]": round(ben_total / 1e3, 1),
        "VAN [kUSD]": round(van / 1e3, 1),
        "TIR [%]": round(100.0 * tir, 1) if np.isfinite(tir) else float("nan"),
        "Payback simple [años]": round(pb_s, 2) if np.isfinite(pb_s) else float("inf"),
        "Payback descontado [años]": round(pb_d, 2) if np.isfinite(pb_d) else float("inf"),
    }
    return resumen, pd.DataFrame(filas_fc)


def main() -> None:
    res_a, fc_a = evaluar_proyecto(SUPUESTOS_E3, "A")
    res_b, fc_b = evaluar_proyecto(SUPUESTOS_E3, "B")
    df_comp = pd.DataFrame([res_a, res_b])

    # Escenarios (Conservador, Base, Optimista) sobre Alternativa A
    esc_defs = {
        "Conservador": {"captura_reduccion_rechazos": 0.15, "costo_reproceso_usd_t": 15.0, "ahorro_agua_t_h": 0.0, "wacc": 0.12},
        "Base": {},
        "Optimista": {"captura_reduccion_rechazos": 0.55, "costo_reproceso_usd_t": 30.0, "ahorro_agua_t_h": 12.0, "wacc": 0.08},
    }
    filas_esc = []
    for nom, patch in esc_defs.items():
        s = {**SUPUESTOS_E3, **patch}
        r, _ = evaluar_proyecto(s, "A")
        r["Escenario"] = nom
        filas_esc.append(r)
    df_esc = pd.DataFrame(filas_esc)[
        ["Escenario", "CAPEX [kUSD]", "Beneficio bruto [kUSD/año]", "VAN [kUSD]", "TIR [%]", "Payback descontado [años]"]
    ]

    # Análisis de sensibilidad tipo Tornado (5 variables sobre Alternativa A)
    van_base = res_a["VAN [kUSD]"]
    sens_vars = [
        ("Captura de rechazos >40 ppm (15 % – 55 %)", "captura_reduccion_rechazos", 0.15, 0.55),
        ("Costo evitado reproceso (12 – 32 USD/t)", "costo_reproceso_usd_t", 12.0, 32.0),
        ("Ahorro de agua de dilución (0 – 15 t/h)", "ahorro_agua_t_h", 0.0, 15.0),
        ("Tasa de descuento WACC (12 % – 8 %)", "wacc", 0.12, 0.08),
        ("Variación de CAPEX (+30 % / -20 %)", "_capex_mult", 1.30, 0.80),
    ]
    filas_tor = []
    for etiqueta, clave, v_low, v_high in sens_vars:
        vals = []
        for v in (v_low, v_high):
            s = dict(SUPUESTOS_E3)
            if clave == "_capex_mult":
                for ck in ("capex_valvula_fv3522", "capex_dcs_cascada_lims", "capex_ingenieria_hazop"):
                    s[ck] *= v
            else:
                s[clave] = v
            r, _ = evaluar_proyecto(s, "A")
            vals.append(r["VAN [kUSD]"])
        filas_tor.append({
            "Variable": etiqueta,
            "VAN Bajo [kUSD]": vals[0],
            "VAN Base [kUSD]": van_base,
            "VAN Alto [kUSD]": vals[1],
            "Amplitud [kUSD]": round(abs(vals[1] - vals[0]), 1),
        })
    df_tor = pd.DataFrame(filas_tor).sort_values("Amplitud [kUSD]", ascending=True)

    # Gráfico Tornado
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    y = np.arange(len(df_tor))
    ax.barh(y, df_tor["VAN Bajo [kUSD]"] - van_base, left=van_base, color="#d62728", alpha=0.85, label="Caso desfavorable")
    ax.barh(y, df_tor["VAN Alto [kUSD]"] - van_base, left=van_base, color="#2ca02c", alpha=0.85, label="Caso favorable")
    ax.axvline(van_base, color="k", lw=1.4, label=f"VAN Base = {van_base:,.0f} kUSD")
    ax.axvline(0.0, color="gray", ls="--", lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(df_tor["Variable"], fontsize=9)
    ax.set_xlabel("Valor Actual Neto — VAN [kUSD]")
    ax.set_title("Análisis de Sensibilidad Tornado (Alternativa A — Supuestos Referenciales E3)", fontweight="bold")
    ax.legend(fontsize=8.5, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "14_tornado_economico_E3.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Exportar Excel y Markdown
    with pd.ExcelWriter(ROOT / "docs" / "evaluacion_economica_E3.xlsx", engine="openpyxl") as w:
        df_comp.to_excel(w, sheet_name="Comparativa_A_vs_B", index=False)
        df_esc.to_excel(w, sheet_name="Escenarios_AltA", index=False)
        df_tor.sort_values("Amplitud [kUSD]", ascending=False).to_excel(w, sheet_name="Tornado_Sensibilidad", index=False)
        fc_a.to_excel(w, sheet_name="FlujoCaja_AltA", index=False)
        fc_b.to_excel(w, sheet_name="FlujoCaja_AltB", index=False)

    md = [
        "# Evaluación Económica Preliminar (Rúbrica E3 — Supuestos Referenciales Editables)\n",
        "> **Nota de trazabilidad:** Los precios unitarios, CAPEX y costos de reproceso son **valores referenciales de ingeniería** (editables en `SUPUESTOS_E3` dentro de `scripts/evaluacion_economica_e3.py`) hasta contar con cotizaciones formales o confirmación de SQM. El caso base asume **$\\Delta\\text{KNO}_3 = 0{,}0\\text{ t/h}$** para no depender del beneficio no calibrado del *replay*.\n",
        "## 1. Comparativa de Alternativas (Horizonte 10 años, WACC 10 %, Impuesto 27 %)\n",
        df_comp.to_markdown(index=False),
        "\n\n## 2. Escenarios — Alternativa A (Recomendada)\n",
        df_esc.to_markdown(index=False),
        "\n\n## 3. Análisis de Sensibilidad (Tornado — 5 Variables)\n",
        df_tor.sort_values("Amplitud [kUSD]", ascending=False).to_markdown(index=False),
        "\n\n## 4. Flujo de Caja Descontado — Alternativa A (Caso Base)\n",
        fc_a.to_markdown(index=False),
        "\n",
    ]
    (ROOT / "docs" / "evaluacion_economica_E3.md").write_text("\n".join(md), encoding="utf-8")

    print("[OK] Bloque 3 generado:")
    print("  - docs/evaluacion_economica_E3.md")
    print("  - docs/evaluacion_economica_E3.xlsx")
    print("  - docs/fig/14_tornado_economico_E3.png")
    print("\n--- Comparativa Alternativas ---")
    print(df_comp.to_string(index=False))
    print("\n--- Escenarios Alternativa A ---")
    print(df_esc.to_string(index=False))


if __name__ == "__main__":
    main()
