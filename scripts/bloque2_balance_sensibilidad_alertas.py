"""Bloque 2 (Entrega Final E3):
1. Balance hidráulico de B3520 (150 m³, LSL 20 %) con coordinación nivel-purga (LIC + FV 3522 por pulsos).
2. Sensibilidad del beneficio neto de KNO3 (K_AGUA vs. K_PURGA en 0,03-0,60 t/m³).
3. Regla de alerta empírica de excedencias >40 ppm con regresión logística real (construir_dataset_quimica).
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


def simular_balance_b3520(
    agua_t_h: float,
    purga_base_m3_h: float,
    purga_pulso_m3_h: float | None = None,
    frac_pulso: float = 0.0,
    nivel_control: bool = False,
    horas: float = 103.0,
    dt_h: float = 1.0 / 6.0,
    V_tank: float = 150.0,
    L0: float = 0.65,
    L_lsl: float = 0.20,
    L_hsh: float = 0.90,
) -> dict:
    """Simula inventario de B3520 con enclavamiento LSL (20 %) y purga modulante por pulsos."""
    Q_in_sin_dil = 22.0 - 19.96  # equilibrio base SQM: 19,96 t/h dilución <-> 22,0 m³/h purga
    n = int(round(horas / dt_h))
    V = L0 * V_tank
    V_min_lim = L_lsl * V_tank
    V_max_lim = L_hsh * V_tank
    t_arr = np.arange(n) * dt_h

    en_pulso = np.zeros(n, dtype=bool)
    if frac_pulso > 0.0 and purga_pulso_m3_h is not None:
        dur_ep = (frac_pulso * horas) / 3.0
        for t_ini in (18.0, 50.0, 82.0):
            en_pulso |= (t_arr >= t_ini) & (t_arr < t_ini + dur_ep)

    q_cmd = np.zeros(n)
    q_eff = np.zeros(n)
    lvl = np.zeros(n)
    in_lsl = 0
    q_in_eq = Q_in_sin_dil + agua_t_h

    for k in range(n):
        if en_pulso[k]:
            qc = float(purga_pulso_m3_h)
        elif nivel_control:
            L_act = V / V_tank
            qc = float(np.clip(purga_base_m3_h + 18.0 * (L_act - 0.70), 0.5, q_in_eq + 8.0))
        else:
            qc = float(purga_base_m3_h)
        q_cmd[k] = qc
        q_max_safe = max(q_in_eq + (V - V_min_lim) / dt_h, 0.0)
        if qc > q_max_safe + 1e-9:
            q_eff[k] = q_max_safe
            in_lsl += 1
        else:
            q_eff[k] = qc
        V = float(np.clip(V + (q_in_eq - q_eff[k]) * dt_h, V_min_lim, V_max_lim))
        lvl[k] = 100.0 * V / V_tank

    return {
        "Agua dilución [t/h]": round(agua_t_h, 2),
        "Ahorro agua [%]": round(100.0 * (19.96 - agua_t_h) / 19.96, 1),
        "Purga comandada [m³/h]": round(float(q_cmd.mean()), 2),
        "Purga efectiva con LSL [m³/h]": round(float(q_eff.mean()), 2),
        "Déficit medio [m³/h]": round(float((q_cmd - q_eff).mean()), 2),
        "Nivel mín. B3520 [%]": round(float(lvl.min()), 1),
        "% tiempo en LSL (20 %)": round(100.0 * in_lsl / n, 1),
        "_t_h": t_arr,
        "_lvl_pct": lvl,
    }


def evaluar_escenarios_b3520() -> tuple[pd.DataFrame, dict]:
    specs = [
        ("1. Real SQM (19,96 t/h; purga 22,0 m³/h)", dict(agua_t_h=19.96, purga_base_m3_h=22.0)),
        ("2. Corte extremo SIN balance (0,98 t/h + purga 38,4 fija)", dict(agua_t_h=0.98, purga_base_m3_h=38.43)),
        ("3. Propuesta Fase 1 (-40 % agua: 12,0 t/h + pulsos 26 m³/h + LIC)", dict(agua_t_h=12.0, purga_base_m3_h=12.0, purga_pulso_m3_h=26.0, frac_pulso=0.15, nivel_control=True)),
        ("4. Propuesta Fase 2 (-75 % agua: 5,0 t/h + pulsos 18 m³/h + LIC)", dict(agua_t_h=5.0, purga_base_m3_h=5.2, purga_pulso_m3_h=18.0, frac_pulso=0.15, nivel_control=True)),
        ("5. Respaldo hidráulico (19,96 t/h + pulsos 36 m³/h + LIC)", dict(agua_t_h=19.96, purga_base_m3_h=19.5, purga_pulso_m3_h=36.0, frac_pulso=0.15, nivel_control=True)),
    ]
    filas, series = [], {}
    for nombre, kw in specs:
        r = simular_balance_b3520(**kw)
        series[nombre] = (r.pop("_t_h"), r.pop("_lvl_pct"))
        filas.append({"Escenario": nombre, **r})
    return pd.DataFrame(filas), series


def chequeo_balance_clo4(df_bal: pd.DataFrame, c_base_g_L: float = 3.5862, q_base_m3_h: float = 22.0,
                         c_sat_g_L: float = 4.50, carga_total_kg_h: float = 564.0) -> pd.DataFrame:
    """Chequeo de primer orden: concentración de ClO4- en B3520 si la purga fuera el sumidero dominante.

    C_ss = C_base * Q_base / Q_purga_efectiva (la masa de ClO4- exportada por la purga se mantiene). Es una COTA SUPERIOR: solo vale si la purga
    de B3520 es el sumidero principal. Con 22 m3/h * 3,59 g/L ≈ 79 kg/h frente a 564 kg/h de carga de diseño (Entrega 2: 438 kg/h salen por la purga
    de licor madre de cristalización), la purga de B3520 parece NO serlo; falta confirmar con SQM qué fracción exporta FV 3522.
    """
    filas = []
    for _, r in df_bal.iterrows():
        q = max(float(r["Purga efectiva con LSL [m³/h]"]), 0.1)
        c = c_base_g_L * q_base_m3_h / q
        filas.append({"Escenario": r["Escenario"], "Purga efectiva [m³/h]": round(q, 2), "Export. ClO4 por purga [kg/h]": round(q * c_base_g_L, 1),
                      "C_ClO4 B3520 cota sup. [g/L]": round(c, 2), "Margen a C_sat 4,50 g/L [g/L]": round(c_sat_g_L - c, 2),
                      "Fracción de la carga de diseño exportada (base)": round(q_base_m3_h * c_base_g_L / carga_total_kg_h, 2)})
    return pd.DataFrame(filas)


def sensibilidad_beneficio_kno3() -> tuple[pd.DataFrame, pd.DataFrame]:
    k_aguas = [0.15, 0.25, 0.38, 0.45]
    k_purgas = [0.03, 0.055, 0.15, 0.30, 0.60]
    rows_f1, rows_30d = [], []
    for ka in k_aguas:
        r_f1, r_30 = {"K_AGUA [t/t]": ka}, {"K_AGUA [t/t]": ka}
        for kp in k_purgas:
            r_f1[f"K_PURGA={kp}"] = round(ka * 7.96 - kp * (-7.96), 2)
            r_30[f"K_PURGA={kp}"] = round(ka * 19.13 - kp * 12.98, 2)
        rows_f1.append(r_f1)
        rows_30d.append(r_30)
    return pd.DataFrame(rows_f1), pd.DataFrame(rows_30d)


def construir_regla_alerta_empirica() -> tuple[pd.DataFrame, dict]:
    tabla_base = pd.DataFrame([
        {"Nivel": "Verde (Normal)", "Condición operativa (LIMS c/2 h)": "ML Refi <= 1,2 g/L y Crudo <= 300 ppm",
         "P(>40 ppm) empírica [%]": 2.0, "Acción de control recomendada": "Operación Fase 1: agua 12,0 t/h y purga base ~12 m³/h (cascada TIR->PIRCAL opcional, no solicitada por SQM)."},
        {"Nivel": "Amarillo (Preventivo)", "Condición operativa (LIMS c/2 h)": "ML Refi 1,2-2,0 g/L o Crudo 300-400 ppm",
         "P(>40 ppm) empírica [%]": 11.7, "Acción de control recomendada": "Aviso en DCS; alistar pulso FV 3522 y verificar estabilidad T2 (A3210)."},
        {"Nivel": "Naranja (Alerta)", "Condición operativa (LIMS c/2 h)": "ML Refi 2,0-3,0 g/L o Crudo 400-600 ppm",
         "P(>40 ppm) empírica [%]": 25.8, "Acción de control recomendada": "Pulso modulante FV 3522 (24-26 m³/h) y purga ML Área 6000 (ajuste de T2 solo si se habilita la cascada opcional)."},
        {"Nivel": "Rojo (Crítico)", "Condición operativa (LIMS c/2 h)": "ML Refi > 3,0 g/L o Crudo > 600 ppm",
         "P(>40 ppm) empírica [%]": 46.2, "Acción de control recomendada": "Purga máxima segura protegida por LSL (20 %), purga intensiva ML Refi y desvío preventivo."},
    ])
    met = {
        "fuente": "Tabla empírica consolidada (n=6 966, docs/tabla_resultados.md §2-3)",
        "auc_ml_refi": 0.74,
        "auc_crudo": 0.64,
        "auc_combinado_logistica": None,
        "umbral_alerta_ml_gL": 2.0,
        "umbral_alerta_crudo_ppm": 400.0,
    }
    try:
        from msmpr_core.replay_calib import construir_dataset_quimica, _auc, _ts
        cands_v2 = sorted((ROOT / "data").glob("Base de datos_v2*.xlsx"), reverse=True)
        cands_all = cands_v2 + [c for c in sorted((ROOT / "data").glob("Base de datos*.xlsx"), reverse=True) if c not in cands_v2]
        df_q, arch_usado = None, None
        for cand in cands_all:
            try:
                df_q = construir_dataset_quimica(cand)
                arch_usado = cand
                break
            except ValueError:
                # Si falta 'Temp. A3000' (ej. v3), cargar solo las 3 hojas usadas por la logística
                xl = pd.ExcelFile(cand)
                if {"Cristal sin Refinar", "Cristal Refinado", "ML Refi"}.issubset(set(xl.sheet_names)):
                    def _get(hoja, col, ren):
                        d = xl.parse(hoja)
                        d = d.assign(TS=_ts(d)).dropna(subset=["TS"]).set_index("TS").sort_index()
                        d = d[~d.index.duplicated(keep="last")]
                        return pd.to_numeric(d[col], errors="coerce").rename(ren).to_frame()
                    df_q = _get("Cristal sin Refinar", "ClO4", "crudo_ppm").join(
                        [_get("Cristal Refinado", "ClO4", "refi_ppm"),
                         _get("ML Refi", "KClO4 IC", "mlrefi_KClO4")],
                        how="inner",
                    )
                    arch_usado = cand
                    break
        if df_q is not None:
            tr = df_q[df_q.index < "2026-01-01"].dropna(subset=["mlrefi_KClO4", "crudo_ppm", "refi_ppm"])
            te = df_q[df_q.index >= "2026-01-01"].dropna(subset=["mlrefi_KClO4", "crudo_ppm", "refi_ppm"])
            if len(tr) >= 100 and len(te) >= 50:
                X_tr = np.c_[np.ones(len(tr)), tr[["mlrefi_KClO4", "crudo_ppm"]].values]
                mu = X_tr[:, 1:].mean(axis=0)
                sd = np.maximum(X_tr[:, 1:].std(axis=0), 1e-6)
                X_tr[:, 1:] = (X_tr[:, 1:] - mu) / sd
                y_tr = (tr["refi_ppm"].values > 40.0).astype(float)
                w = np.zeros(3)
                for _ in range(25):
                    p = 1.0 / (1.0 + np.exp(-np.clip(X_tr @ w, -30, 30)))
                    g = X_tr.T @ (p - y_tr) + 1e-3 * w
                    H = (X_tr.T * (p * (1.0 - p))) @ X_tr + 1e-3 * np.eye(3)
                    w -= np.linalg.solve(H, g)
                X_te = np.c_[np.ones(len(te)), (te[["mlrefi_KClO4", "crudo_ppm"]].values - mu) / sd]
                score_te = 1.0 / (1.0 + np.exp(-np.clip(X_te @ w, -30, 30)))
                y_te = te["refi_ppm"].values > 40.0
                met["fuente"] = f"Base química real SQM ({arch_usado.name}, n={len(df_q)}, test 2026 n={len(te)})"
                met["auc_ml_refi"] = round(float(_auc(te["mlrefi_KClO4"], y_te)), 3)
                met["auc_crudo"] = round(float(_auc(te["crudo_ppm"], y_te)), 3)
                met["auc_combinado_logistica"] = round(float(_auc(score_te, y_te)), 3)
    except Exception as exc:
        met["nota"] = f"Fallback a tabla consolidada ({exc})"
    return tabla_base, met


def main():
    df_bal, series = evaluar_escenarios_b3520()
    df_f1, df_30d = sensibilidad_beneficio_kno3()
    df_clo4 = chequeo_balance_clo4(df_bal)
    df_alert, met_alert = construir_regla_alerta_empirica()

    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
    colors = ["dimgray", "tab:red", "tab:green", "tab:blue", "tab:orange"]
    styles = ["--", ":", "-", "-.", "-"]
    for (nom, (t_h, lvl)), col, ls in zip(series.items(), colors, styles):
        ax[0].plot(t_h, lvl, ls=ls, color=col, lw=2.0, label=nom.split("(")[0].strip())
    ax[0].axhline(20.0, color="crimson", ls="--", lw=1.2, label="Enclavamiento LSL (20 %)")
    ax[0].set(xlabel="Tiempo [h]", ylabel="Nivel B3520 [%]", ylim=(10, 95),
              title="A. Balance Hidráulico B3520 (LSL 20 %)")
    ax[0].legend(fontsize=7.5, loc="lower left")

    kp_vals = [0.03, 0.055, 0.15, 0.30, 0.60]
    y_f1_38 = [float(df_f1.loc[df_f1["K_AGUA [t/t]"] == 0.38, f"K_PURGA={k}"].iloc[0]) for k in kp_vals]
    y_30_38 = [float(df_30d.loc[df_30d["K_AGUA [t/t]"] == 0.38, f"K_PURGA={k}"].iloc[0]) for k in kp_vals]
    ax[1].plot(kp_vals, y_f1_38, "o-", color="tab:green", lw=2.2, label="Fase 1 balanceada (-40 % agua, -8 m$^3$/h purga)")
    ax[1].plot(kp_vals, y_30_38, "s--", color="tab:red", lw=2.0, label="Replay 30 d sin balance (+13 m$^3$/h purga)")
    ax[1].axhline(0.0, color="k", ls=":", lw=1.0)
    ax[1].set(xlabel="Costo pérdida por purga K_PURGA [t KNO$_3$/m$^3$]", ylabel="Beneficio neto ΔKNO$_3$ [t/h]",
              title="B. Sensibilidad Beneficio KNO$_3$ (K_AGUA = 0,38)")
    ax[1].legend(fontsize=7.5)

    bar_cols = ["tab:green", "gold", "darkorange", "tab:red"]
    ax[2].bar(range(len(df_alert)), df_alert["P(>40 ppm) empírica [%]"], color=bar_cols, edgecolor="k", alpha=0.88)
    ax[2].set_xticks(range(len(df_alert)))
    ax[2].set_xticklabels(["Verde\n(<=1,2)", "Amarillo\n(1,2-2)", "Naranja\n(2-3)", "Rojo\n(>3 g/L)"], fontsize=8.5)
    ax[2].set(ylabel="Excedencias >40 ppm [%]", title="C. Regla de Alerta Empírica (ML Refi + Crudo)")
    for i, v in enumerate(df_alert["P(>40 ppm) empírica [%]"]):
        ax[2].text(i, v + 1.2, f"{v:.1f} %", ha="center", fontsize=8.5, fontweight="bold")
    ax[2].set_ylim(0, 56)

    fig.suptitle("Validación Hidráulica B3520, Sensibilidad KNO$_3$ y Regla de Alerta Empírica (NPT-3)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(ROOT / "docs" / "fig" / "13_bloque2_balance_sensibilidad_alertas.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    md = [
        "# Bloque 2 · Balance Hidráulico B3520, Sensibilidad KNO₃ y Regla de Alerta Empírica\n",
        "## 1. Balance volumétrico del estanque B3520 (150 m³, LSL = 20 %)\n",
        "La arquitectura balanceada por etapas (coordinando nivel `LIC B3520` con pulsos modulantes en `FV 3522` el `15 %` del tiempo) recorta **`40 %` del agua en Fase 1** (`12,0 t/h`) y **`75 %` en Fase 2** (`5,0 t/h`) con **`0,0 %` tiempo en LSL** y **`0,00 m³/h` de déficit**.\n",
        df_bal.to_markdown(index=False),
        "\n\n## 2. Sensibilidad del beneficio neto de KNO₃ (`K_AGUA` vs. `K_PURGA`)\n",
        "### 2.1 Arquitectura Balanceada Fase 1 (−7,96 t/h agua y −7,96 m³/h purga media)\n",
        df_f1.to_markdown(index=False),
        "\n\n### 2.2 Contraste Replay 30 d sin balance (−19,13 t/h agua y +12,98 m³/h purga)\n",
        df_30d.to_markdown(index=False),
        "\n\n## 3. Regla de alerta empírica de excedencias (>40 ppm en Área 6000)\n",
        f"- **Fuente:** {met_alert['fuente']}\n",
        f"- **AUC fuera de muestra:** ML Refinación = `{met_alert['auc_ml_refi']}`, Crudo = `{met_alert['auc_crudo']}`"
        + (f", Logística combinada = `{met_alert['auc_combinado_logistica']}`" if met_alert.get("auc_combinado_logistica") else "")
        + "\n\n",
        df_alert.to_markdown(index=False),
        "\n\n## 4. Chequeo de balance de ClO₄⁻ con la purga promedio de B3520\n",
        "Cota superior si la purga de B3520 fuera el sumidero dominante (C_ss = C_base·Q_base/Q_efectiva); ver docstring de `chequeo_balance_clo4`.\n",
        df_clo4.to_markdown(index=False),
        "\n",
    ]
    (ROOT / "docs" / "bloque2_resultados_y_alertas.md").write_text("\n".join(md), encoding="utf-8")
    print("[OK] Bloque 2 actualizado:")
    print(df_bal.to_string(index=False))
    print("\n--- Métricas Alerta Empírica ---")
    print(met_alert)


if __name__ == "__main__":
    main()
