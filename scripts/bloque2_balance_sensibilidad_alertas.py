"""Bloque 2 (Plan Entrega Final E3):
1. Cierre de balance de volumen/agua en B3520 para el replay contrafactual.
2. Análisis de sensibilidad de beneficio neto de KNO3 (K_AGUA y K_PURGA en [0.03, 0.60] t/m3).
3. Regla de alerta empírica P(Refinado > 40 ppm) con corte temporal 2026-01-01.
"""
from __future__ import annotations

import pathlib
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIG_DIR = ROOT / "docs" / "fig"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. BALANCE DE VOLUMEN / AGUA CERRADO EN B3520 PARA REPLAY
# ==============================================================================
def simular_balance_volumen_B3520(
    Q_dil_t_h: np.ndarray,
    Q_purge_cmd_m3_h: np.ndarray,
    dt_h: float = 1.0 / 6.0,
    Q_dil_base_t_h: float = 19.96,
    Q_purge_base_m3_h: float = 22.0,
    V_B3520_m3: float = 150.0,
    L0_frac: float = 0.60,
    LSL_frac: float = 0.20,
    LSH_frac: float = 0.90,
    rho_agua: float = 1.0,
    rho_ml: float = 1.38,
) -> pd.DataFrame:
    """Integra el inventario volumétrico de B3520 alrededor del equilibrio nominal.

    En estado estacionario base (Q_dil_base, Q_purge_base), las entradas netas de
    licor al estanque equilibran la purga base: Q_net_in_base = Q_purge_base.
    Al cambiar Q_dil y Q_purge_cmd:
        dV/dt = (Q_dil - Q_dil_base)/rho_agua + Q_purge_base - Q_purge_eff
    Si el nivel llega al enclavamiento LSL (20 %), la purga se recorta al caudal
    sostenible por balance hídrico (para evitar cavitación/vaciado de B3520).
    """
    n = len(Q_dil_t_h)
    V = np.empty(n)
    L_pct = np.empty(n)
    Q_purge_eff = np.empty(n)
    deficit_m3_h = np.empty(n)
    lsl_activo = np.zeros(n, dtype=bool)

    V_cur = L0_frac * V_B3520_m3
    V_min = LSL_frac * V_B3520_m3
    V_max = LSH_frac * V_B3520_m3

    for k in range(n):
        # Entrada neta de líquido disponible en B3520 [m3/h]
        Q_in_net = Q_purge_base_m3_h + (Q_dil_t_h[k] - Q_dil_base_t_h) / rho_agua
        q_cmd = float(Q_purge_cmd_m3_h[k])

        V_next_try = V_cur + dt_h * (Q_in_net - q_cmd)
        if V_next_try < V_min:
            # Enclavamiento LSL: limita purga a lo que permite mantener V >= V_min
            q_max_sost = max(0.0, Q_in_net + (V_cur - V_min) / dt_h)
            q_eff = min(q_cmd, q_max_sost)
            lsl_activo[k] = True
        elif V_next_try > V_max:
            # Enclavamiento LSH: fuerza purga mínima para evitar rebalse
            q_min_reb = max(0.0, Q_in_net - (V_max - V_cur) / dt_h)
            q_eff = max(q_cmd, q_min_reb)
        else:
            q_eff = q_cmd

        V_cur = float(np.clip(V_cur + dt_h * (Q_in_net - q_eff), V_min, V_max))
        V[k] = V_cur
        L_pct[k] = 100.0 * V_cur / V_B3520_m3
        Q_purge_eff[k] = q_eff
        deficit_m3_h[k] = max(0.0, q_cmd - q_eff)

    return pd.DataFrame({
        "t_h": np.arange(n) * dt_h,
        "Q_dil_t_h": Q_dil_t_h,
        "Q_purge_cmd_m3_h": Q_purge_cmd_m3_h,
        "Q_purge_eff_m3_h": Q_purge_eff,
        "deficit_purga_m3_h": deficit_m3_h,
        "V_B3520_m3": V,
        "L_B3520_pct": L_pct,
        "LSL_activo": lsl_activo,
    })


def ejecutar_analisis_balance_agua() -> tuple[pd.DataFrame, dict]:
    """Evalúa el cierre de balance hídrico sobre una ventana de 103 h (4 días)."""
    n_steps = 618  # 103 h cada 10 min (misma malla que campaña 10-15 nov 2026)
    dt_h = 1.0 / 6.0

    escenarios = {
        "1. Real SQM (19,96 t/h; purga 22,0 m³/h)": (
            np.full(n_steps, 19.96), np.full(n_steps, 22.0)
        ),
        "2. Propuesta 0,98 t/h + purga 38,4 m³/h (SIN reposición)": (
            np.full(n_steps, 0.98), np.full(n_steps, 38.43)
        ),
        "3. Propuesta 10,0 t/h + purga 28,0 m³/h (parcial)": (
            np.full(n_steps, 10.0), np.full(n_steps, 28.0)
        ),
        "4. Balanceado: 19,96 t/h + purga 22,0 m³/h c/pulsos 38 m³/h (15 % t)": (
            np.full(n_steps, 19.96),
            np.where((np.arange(n_steps) % 100) < 15, 38.0, 19.2),
        ),
    }

    resumen = []
    series = {}
    for nombre, (q_dil, q_p) in escenarios.items():
        df_b = simular_balance_volumen_B3520(q_dil, q_p, dt_h=dt_h)
        series[nombre] = df_b
        resumen.append({
            "Escenario": nombre,
            "Agua dilución [t/h]": round(float(q_dil.mean()), 2),
            "Purga comandada [m³/h]": round(float(q_p.mean()), 2),
            "Purga efectiva con LSL [m³/h]": round(float(df_b["Q_purge_eff_m3_h"].mean()), 2),
            "Déficit medio de purga [m³/h]": round(float(df_b["deficit_purga_m3_h"].mean()), 2),
            "Nivel mín. B3520 [%]": round(float(df_b["L_B3520_pct"].min()), 1),
            "% tiempo en LSL (20 %)": round(100.0 * float(df_b["LSL_activo"].mean()), 1),
        })

    return pd.DataFrame(resumen), series


# ==============================================================================
# 2. SENSIBILIDAD DEL BENEFICIO NETO DE KNO3 (K_AGUA y K_PURGA)
# ==============================================================================
def ejecutar_sensibilidad_kno3(
    delta_agua_t_h: float = 18.98,   # 19.96 -> 0.98 t/h (campaña 4d)
    delta_purga_m3_h: float = 16.43, # 22.00 -> 38.43 m3/h (campaña 4d)
    horas_ano: float = 8000.0,
) -> pd.DataFrame:
    """Evalúa dKNO3 = K_AGUA * delta_agua - K_PURGA * delta_purga en el rango del Plan E3."""
    k_aguas = [0.15, 0.25, 0.38, 0.50]
    k_purgas = [0.03, 0.055, 0.15, 0.30, 0.45, 0.60]  # 0.60 t/m3 = límite ML 234

    filas = []
    for ka in k_aguas:
        for kp in k_purgas:
            neto_t_h = ka * delta_agua_t_h - kp * delta_purga_m3_h
            kp_breakeven = (ka * delta_agua_t_h) / max(delta_purga_m3_h, 1e-9)
            filas.append({
                "K_AGUA [t KNO3/t agua]": ka,
                "K_PURGA [t KNO3/m³ purga]": kp,
                "Delta KNO3 neto [t/h]": round(neto_t_h, 2),
                "Delta KNO3 neto [kt/año]": round(neto_t_h * horas_ano / 1000.0, 2),
                "K_PURGA breakeven [t/m³]": round(kp_breakeven, 3),
                "Signo económico": "Ganancia" if neto_t_h > 0 else "Pérdida neta",
            })
    return pd.DataFrame(filas)


# ==============================================================================
# 3. REGLA DE ALERTA EMPÍRICA P(REFINADO > 40 PPM)
# ==============================================================================
def construir_regla_alerta_empirica() -> tuple[pd.DataFrame, dict]:
    """Calcula regla logística temporal si existe Base de datos_v3.xlsx, o usa la tabla consolidada."""
    candidatos = [
        ROOT / "data" / "Base de datos_v3.xlsx",
        ROOT / "data" / "Base de datos_v2-3.xlsx",
    ]
    excel_real = next((p for p in candidatos if p.exists()), None)

    # Matriz empírica oficial reportada en docs/tabla_resultados.md §3 (n = 6 966)
    reglas_semaforo = pd.DataFrame([
        {
            "Nivel Alerta": "VERDE (Normal)",
            "Condición ML Refinación (A6000)": "≤ 1,2 g/L",
            "Condición Cristal Crudo (A3000)": "≤ 300 ppm",
            "P(>40 ppm) empírica": "2,0 % – 3,0 %",
            "Acción operacional recomendada": "Operación normal con cascada TIR→PIRCAL en automático; seguimiento rutinario LIMS c/2 h.",
        },
        {
            "Nivel Alerta": "AMARILLO (Preventiva)",
            "Condición ML Refinación (A6000)": "1,2 – 2,0 g/L",
            "Condición Cristal Crudo (A3000)": "300 – 400 ppm",
            "P(>40 ppm) empírica": "11,7 % – 28,6 %",
            "Acción operacional recomendada": "Aumentar purga modulante en Área 6000/B3520 dentro de balance hídrico; verificar T2 A3210 y lavado CF 3000.",
        },
        {
            "Nivel Alerta": "NARANJA (Alta)",
            "Condición ML Refinación (A6000)": "2,0 – 3,0 g/L",
            "Condición Cristal Crudo (A3000)": "400 – 600 ppm",
            "P(>40 ppm) empírica": "22,9 % – 28,8 %",
            "Acción operacional recomendada": "Alarma DCS en sala de control; purga prioritaria de ML de refinación (A6000) y revisión de alimentación SSK.",
        },
        {
            "Nivel Alerta": "ROJO (Crítica)",
            "Condición ML Refinación (A6000)": "> 3,0 g/L (o > 4,0 g/L)",
            "Condición Cristal Crudo (A3000)": "> 600 ppm",
            "P(>40 ppm) empírica": "30,8 % – 51,5 %",
            "Acción operacional recomendada": "Intervención inmediata: máxima purga permitida por LSL, verificar temperatura A3210 y segregar/reprocesar lote si supera 40 ppm.",
        },
    ])

    metricas_log = {
        "fuente": "Tabla empírica consolidada (n=6 966, docs/tabla_resultados.md §2–3)",
        "auc_ml_refi": 0.74,
        "auc_crudo": 0.64,
        "auc_combinado_logistica": None,
        "umbral_alerta_ml_gL": 2.0,
        "umbral_alerta_crudo_ppm": 400.0,
    }

    if excel_real is not None:
        try:
            from msmpr_core.replay_calib import _cargar_quimica_historica, _roc_auc
            df_q = _cargar_quimica_historica(excel_real).dropna(
                subset=["fecha", "refi_clo4_ppm", "ml_refi_kclo4_gL", "crudo_clo4_ppm"]
            )
            df_q["y"] = (df_q["refi_clo4_ppm"] > 40.0).astype(int)
            tr = df_q[df_q["fecha"] < "2026-01-01"]
            te = df_q[df_q["fecha"] >= "2026-01-01"]
            if len(tr) > 100 and len(te) > 100:
                # Regresión logística simple por IRLS (sin depender de scikit-learn)
                mu = tr[["ml_refi_kclo4_gL", "crudo_clo4_ppm"]].mean().values
                sd = tr[["ml_refi_kclo4_gL", "crudo_clo4_ppm"]].std().values + 1e-9
                X_tr = np.column_stack([np.ones(len(tr)), (tr[["ml_refi_kclo4_gL", "crudo_clo4_ppm"]].values - mu) / sd])
                X_te = np.column_stack([np.ones(len(te)), (te[["ml_refi_kclo4_gL", "crudo_clo4_ppm"]].values - mu) / sd])
                y_tr = tr["y"].values.astype(float)
                beta = np.zeros(3)
                for _ in range(25):
                    p = 1.0 / (1.0 + np.exp(-np.clip(X_tr @ beta, -30, 30)))
                    W = p * (1.0 - p) + 1e-6
                    H = X_tr.T @ (W[:, None] * X_tr) + 1e-4 * np.eye(3)
                    g = X_tr.T @ (y_tr - p)
                    beta += np.linalg.solve(H, g)
                p_te = 1.0 / (1.0 + np.exp(-np.clip(X_te @ beta, -30, 30)))
                auc_comb = float(_roc_auc(te["y"].values, p_te))
                alerta_te = (te["ml_refi_kclo4_gL"] >= 2.0) | (te["crudo_clo4_ppm"] >= 400.0)
                tp = int((alerta_te & (te["y"] == 1)).sum())
                fn = int((~alerta_te & (te["y"] == 1)).sum())
                fp = int((alerta_te & (te["y"] == 0)).sum())
                tn = int((~alerta_te & (te["y"] == 0)).sum())
                metricas_log.update({
                    "fuente": f"Base real {excel_real.name} (train={len(tr)}, test={len(te)})",
                    "auc_combinado_logistica": round(auc_comb, 3),
                    "sensibilidad_regla_2gL_400ppm": round(tp / max(tp + fn, 1), 3),
                    "especificidad_regla_2gL_400ppm": round(tn / max(tn + fp, 1), 3),
                    "vpp_regla_2gL_400ppm": round(tp / max(tp + fp, 1), 3),
                })
        except Exception as exc:
            metricas_log["nota"] = f"Fallback a tabla consolidada ({exc})"

    return reglas_semaforo, metricas_log


def main() -> None:
    df_bal, series_bal = ejecutar_analisis_balance_agua()
    df_sens = ejecutar_sensibilidad_kno3()
    df_alert, met_alert = construir_regla_alerta_empirica()

    # Figura 13: 3 paneles (Nivel B3520, Sensibilidad KNO3, Probabilidad empírica >40 ppm)
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))

    # Panel A: Nivel B3520 bajo balance cerrado
    for nombre, df_s in series_bal.items():
        short = nombre.split(":")[0] if ":" in nombre else nombre[:28]
        ax[0].plot(df_s["t_h"], df_s["L_B3520_pct"], lw=2.0, label=short)
    ax[0].axhline(20.0, color="crimson", ls="--", lw=1.4, label="Enclavamiento LSL (20 %)")
    ax[0].set(xlabel="Tiempo [h]", ylabel="Nivel B3520 [%]", title="A. Balance de Volumen B3520 (LSL = 20 %)")
    ax[0].legend(fontsize=7.5)
    ax[0].grid(alpha=0.3)

    # Panel B: Sensibilidad beneficio neto KNO3 vs K_PURGA
    for ka, grp in df_sens.groupby("K_AGUA [t KNO3/t agua]"):
        ax[1].plot(grp["K_PURGA [t KNO3/m³ purga]"], grp["Delta KNO3 neto [t/h]"], "o-", lw=2.0, label=f"K_AGUA = {ka:.2f}")
    ax[1].axhline(0.0, color="k", ls="--", lw=1.2)
    ax[1].axvline(0.055, color="tab:green", ls=":", label="K_PURGA replay (0,055)")
    ax[1].axvline(0.60, color="tab:red", ls=":", label="Tope ML 234 (0,60)")
    ax[1].set(xlabel="K_PURGA [t KNO₃ / m³ purga]", ylabel="Beneficio neto ΔKNO₃ [t/h]", title="B. Sensibilidad Beneficio KNO₃")
    ax[1].legend(fontsize=7.5)
    ax[1].grid(alpha=0.3)

    # Panel C: Probabilidad empírica >40 ppm según ML Refinación (n = 6 966)
    bins_ml = ["≤1,2", "1,2–2,0", "2,0–3,0", "3,0–4,0", ">4,0"]
    probs_ml = [3.0, 11.7, 22.9, 30.8, 46.2]
    colors = ["#2ca02c", "#bcbd22", "#ff7f0e", "#d62728", "#8b0000"]
    bars = ax[2].bar(bins_ml, probs_ml, color=colors, edgecolor="black", alpha=0.88)
    for b, p in zip(bars, probs_ml):
        ax[2].text(b.get_x() + b.get_width() / 2, p + 1.2, f"{p:.1f}%", ha="center", fontsize=8.5, fontweight="bold")
    ax[2].axvline(1.5, color="k", ls="--", lw=1.2, label="Umbral alerta (2,0 g/L)")
    ax[2].set(xlabel="KClO₄ en ML de Refinación [g/L]", ylabel="Muestras > 40 ppm [%]", ylim=(0, 54), title="C. Alerta Empírica A6000 (n = 6 966)")
    ax[2].legend(fontsize=8)
    ax[2].grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "13_bloque2_balance_sensibilidad_alertas.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Reporte Markdown
    p_out = ROOT / "docs" / "bloque2_resultados_y_alertas.md"
    md = [
        "# Bloque 2: Balance de Volumen `B3520`, Sensibilidad de $\\text{KNO}_3$ y Regla de Alerta Empírica\n",
        "## 1. Cierre de Balance de Agua/Volumen en `B3520` (Ventana 103 h)\n",
        df_bal.to_markdown(index=False),
        "\n\n> **Lectura clave:** Reducir el agua de dilución de `19,96` a `0,98 t/h` mientras se eleva la purga a `38,4 m³/h` genera un déficit volumétrico de `~35,4 m³/h` que lleva `B3520` al enclavamiento `LSL (20 %)` en `< 2 h`, limitando la purga efectiva sostenible a `~3,0 m³/h` salvo reposición de licor o menor evaporación. Esto confirma que el escenario de `0,50 t/h` del *replay* no puede operar sin cerrar el balance hídrico global.\n",
        "\n## 2. Sensibilidad del Beneficio Neto de $\\text{KNO}_3$ (`K_AGUA` y `K_PURGA`)\n",
        df_sens.to_markdown(index=False),
        "\n\n> **Lectura clave:** El `+6,13 t/h` original corresponde únicamente al punto `K_AGUA = 0,38` y `K_PURGA = 0,055 t/m³`. Con `K_PURGA = 0,60 t KNO₃-eq/m³` (equivalente a licor ML 234 sin recuperación posterior), el balance se vuelve **negativo (`-2,65 t/h` para `K_AGUA = 0,38`)**. Por ello, el beneficio en la evaluación económica E3 debe sustentarse principalmente en la **reducción de reprocesos/rechazos `> 40 ppm`** y no depender de un supuesto `+6 t/h` no calibrado.\n",
        "\n## 3. Regla de Alerta Empírica (`P(Refinado > 40 ppm)`)\n",
        f"- **Fuente:** {met_alert['fuente']}\n",
        f"- **AUC fuera de muestra:** ML Refinación = `{met_alert['auc_ml_refi']}`, Crudo = `{met_alert['auc_crudo']}`"
        + (f", Logística combinada = `{met_alert['auc_combinado_logistica']}`" if met_alert.get("auc_combinado_logistica") else "")
        + "\n\n",
        df_alert.to_markdown(index=False),
        "\n",
    ]
    p_out.write_text("\n".join(md), encoding="utf-8")
    print("[OK] Bloque 2 generado:")
    print("  - docs/bloque2_resultados_y_alertas.md")
    print("  - docs/fig/13_bloque2_balance_sensibilidad_alertas.png")
    print("\n--- Resumen Balance B3520 ---")
    print(df_bal.to_string(index=False))
    print("\n--- Métricas Alerta Empírica ---")
    print(met_alert)


if __name__ == "__main__":
    main()
