# Control PID y Estrategia *Plantwide* — Cristalizadores de $\text{KNO}_3$ (Planta NPT-3, SQM)

> **Rama:** `PID` | **Alcance:** Tren Integrado **Área 2000 (`B2510`) → Área 3000 (`A3110 / A3210 / B3520`) → Área 6000 (Refinación)**  
> **Estado de validación:** `96 passed, 2 skipped` (`pytest tests/`)

---


> **Alcance y limitaciones (leer antes de citar cifras).** Las cifras de este README (ahorro de agua, ppm, recuperación, beneficio neto de KNO₃)
> provienen de simulación con parámetros *placeholder*: la solubilidad del KNO₃ es sintética (`planta_sqm.Cstar_ref`, pendiente 0,010 K⁻¹ frente a
> ~0,03 K⁻¹ de Perry), los coeficientes de coprecipitación de KClO₄ (82–125 ppm por g/L) difieren entre simuladores y el beneficio neto de KNO₃ del
> *replay* es una fórmula lineal con coeficientes sin calibrar (`replay.K_*`). El "0 % de violaciones" del *replay* es una propiedad del modelo
> (función de umbral sobre la coprecipitación), no una validación: ver `replay.replay_fit_metrics` para cuantificar el ajuste del baseline.
> El RGA/Niederlinski del A3110 aislado no es interpretable para `alpha` (con V fijo, el caudal de purga lo fija el balance de volumen); ver `control.mv_authority`.


> **Diagnóstico del replay (nov-2026):** con la base química real (n = 6 966) el eslabón MLK → cristal crudo → refinado no tiene respaldo empírico y el KClO₄ del ML de refinación es la variable asociada al ppm final; ver `docs/diagnostico_replay.md` y `scripts/diagnostico_replay.py`.

## 1. Resumen Ejecutivo

Este repositorio contiene el modelo fenomenológico (`msmpr_core`), los controladores regulatorios/supervisores y los cuadernos de validación dinámica para los cristalizadores evaporativos al vacío **A3110** y **A3210** de la planta NPT-3 de SQM, con el objetivo de mantener el producto refinado final **$< 40\text{ ppm}$ de $\text{ClO}_4^-$** bajo una estrategia hídricamente sostenible:

* **Reducción drástica de agua de dilución (`FIRC 3103`):** Transición desde el diseño histórico ($27{,}14\text{ t/h}$; $19{,}96\text{ t/h}$ medidos en planta) hacia un régimen sostenible de **$0{,}50\text{ t/h}$ nominales** (promedio **$0{,}67\text{ t/h}$** en simulación calibrada, ahorro de **$97{,}5\%$** vs. diseño y **$96{,}6\%$** vs. operación real), manteniendo el pico en Área 6000 en **$22{,}65\text{ ppm}$**.
* **Control *plantwide* de purga (`AIC 3522 → FV 3522`):** El análisis multivariable **RGA $3\times 3$** e **Índice de Niederlinski** ($NI = -610{,}09 < 0$ en `A3110` aislado vs. $NI = +0{,}803$ y $+1{,}060$ en los sub-bloques regulatorios $2\times 2$) demuestra que la purga debe operar en la capa *plantwide* a la salida de `B3520` en modulación continua, absorbiendo las alzas de $\text{ClO}_4^-$ y $\text{Mg}^{2+}$ sin malgastar agua fresca.
* **Validación sobre campaña real SQM (*Replay* contrafactual, `msmpr_core/replay.py`):** Evaluado sobre 4 días de sensores reales cada 10 min (`10–15 nov 2026`, $26{,}8\%$ de muestras $> 40\text{ ppm}$ en planta actual) y ventana de 30 días ($16{,}0\% > 40\text{ ppm}$). La estrategia integrada alimentada por **cromatografía iónica de laboratorio cada 2 h** logra **$0{,}0\%$ de violaciones** ($\text{máx } 23{,}7\text{ ppm}$ en 4 d; $27{,}4\text{ ppm}$ en 30 d), con un ahorro de **$1\,958\text{ m}^3$ de agua en 4 días ($-95{,}1\%$)** y mejora neta estimada de **$+6{,}1\text{ a } +6{,}6\text{ t/h}$** de $\text{KNO}_3$.
* **Módulos avanzados incorporados:** Compensador dinámico *Lead-Lag* (`LeadLagCompensator`), selector *Override* de sobresaturación (`supersaturation_override_limit`), cinética de disolución en subsaturación (`dpbe.dissolution_rate_m_s`) y acoplamiento $\text{Mg}^{2+}\text{–ClO}_4^-$ (`magnesium_perchlorate_coupling`).

---

<!-- BEGIN_REDLINE_TAGS -->
## 2. Tabla Maestra de Lazos e Instrumentación P&ID (*Redline* — ISA-5.1)

| Equipo / Zona | Tag P&ID Oficial | Color en *Redline* | Función / Lazo | Elemento Final / Notas de Diseño |
| :--- | :--- | :---: | :--- | :--- |
| **Pre-`A3110` (`B2510`)** | `FIRCAHL 3101` | Negro | Medición caudal alimentación `SSKd` (corriente `308`) | Envía señal de carga a `FFIC 3102`. |
| **Pre-`A3110`** | `FFIC 3102` | **Negro + Rojo** | Controlador de razón agua/alimentación | **En rojo:** bloque *Lead-Lag* + *Override* de sobresaturación ($\sigma_{\min} = 0{,}02$) en DCS. |
| **Pre-`A3110`** | `FIRC 3103` / `FV 3103` | Negro | Lazo esclavo de agua de dilución (corriente `303`) | Régimen sostenible propuesto: $0{,}50\text{ t/h}$ nominal $[0{,}20\text{–}2{,}50]\text{ t/h}$ *(rango físico y rangeability de válvula declarados como **supuesto**)*. |
| **Pre-`A3110`** | **`AIT 3105`** | **Rojo (Nuevo)** | Analizador de $\text{ClO}_4^-$ aguas arriba de la dilución | Aplica *trim* anticipativo a `FFIC 3102` y señal *feedforward* hacia purga. |
| **`A3110`** | `LIRCSAHL 3101` → `LV 3101` | Negro | Control de nivel / inventario `A3110` | Válvula de control de nivel `LV 3101`. |
| **`A3110`** | `TIR 3101` → `PIRCAL 3101` | **Negro + Rojo** | Temperatura `A3110` → Presión de vacío | `PIRCAL 3101` actúa sobre válvula de vacío (**en rojo:** cierre de cascada `TIR → PIRCAL`). |
| **`A3110` → `A3210`** | `DIRCAHL 3101` → `FIRCAL 3101` → `SIC 3101` | Negro | Densidad de pulpa salida `A3110` ($x_{S1} = 13\%$) | Variador de velocidad bomba **`P3112`**. |
| **`A3210`** | `LIRCSAHL 3201` | Negro | Control de nivel / inventario `A3210` | Actúa sobre la válvula de descarga hacia el equipo **`S3530`**. |
| **`A3210`** | `TIR 3201` → `PIRCAL 3201` | **Negro + Rojo** | Temperatura `A3210` → Presión de vacío | `PIRCAL 3201` actúa sobre válvula de vacío (**en rojo:** cascada + *trim* térmico suave $[43{,}0\text{–}44{,}3]\text{ }^\circ\text{C}$). |
| **`A3210` → `S3540`** | `DIRCAHL 3201` → `FIRCAL 3201` → `SIC 3201` | Negro | Densidad de pulpa salida `A3210` ($x_{S2} = 20\%$) | Variador de velocidad bomba **`P3212`**. |
| **Salida `B3520` (Purga)** | **`AIC 3522` → (`FIC 3522`) → `FV 3522`** | **Rojo (Nuevo)** | Control exclusivo de purga de licor madre post-`B3520` | **PV:** Cromatografía iónica (CI) de laboratorio c/2 h ingresada a DCS (LIMS). **Actuador:** válvula nueva `FV 3522` modulante (caudal máx. $65\text{ m}^3/\text{h}$ declarado como **supuesto**). |

### Especificación Técnica de la Válvula Propuesta `FV 3522` (Salida `B3520`)

* **Tipo de cuerpo:** Válvula de control rotatoria de bola tipo *V-port* (bola segmentada) para servicio en salmueras saturadas con riesgo de incrustación salina o arrastre de finos *(alternativa solo si el licor está 100 % libre de sólidos: globo de asiento simple)*.
* **Característica de flujo (*Trim*):** Igual porcentaje (*Equal Percentage*, $R = 20\text{–}50$) para control fino a bajos caudales y linealización de ganancia instalada en línea bombeada; carrera normal de diseño en banda **$10\%\text{–}80\%$**.
* **Actuación y accesorios:** Actuador neumático de diafragma + transductor $I/P$ ($4\text{–}20\text{ mA}$) + **posicionador digital** (elimina *stiction*/histéresis por depósitos salinos).
* **Materiales e instalación:** Acero inoxidable **AISI 316L / Duplex**; ubicada en la **descarga de la bomba de `B3520`** con arreglo *Double Block & Bleed* y *bypass* manual de válvula globo.
* **Estrategia y seguridad (*Fail-Safe*):** Operación en cascada **`AIC 3522` (CI lab c/2 h en DCS) → `FIC 3522` → `FV 3522`** con rampa suave de *setpoint*; posición **`FO` (*Fail-Open* / Aire para cerrar)** con enclavamiento de bajo nivel **`LSL` en `B3520`** para proteger la bomba contra cavitación (acción directa en `FIC 3522`).
<!-- END_REDLINE_TAGS -->

---

## 3. Estructura del Repositorio

* **`msmpr_core/`**: Paquete principal de simulación y control.
  * `params.py`: Perfiles termodinámicos (`literatura`, `calibracion`, `planta_sqm`) y `SOSTENIBLE_DILUCION_OVERRIDES`.
  * `dpbe.py`: Balance poblacional discretizado, cinética de crecimiento/nucleación, rama de disolución en subsaturación ($C < C^*$) y termodinámica multicomponente calibrada de $\text{KClO}_4/\text{KNO}_3$ (`m_ClO4_sat`, `T_saturacion_KClO4`, $\ln\Gamma_{\text{KClO}_4,0} = 1{,}571$).
  * `plant.py`: Modelo dinámico `Plant`, simulador acoplado NPT-3 (`simulate_plant_npt3_calibrated`, parametrizado para régimen sostenible) y acoplamiento `magnesium_perchlorate_coupling()`.
  * `control.py`: Controladores PID comerciales con anti-windup, `autotune` SIMC/IMC, `routh_hopf_analysis`, `compute_rga`, `rga_from_plant`, `LeadLagCompensator`, `supersaturation_override_limit` y restricción dura de perclorato `dilution_kclo4_hard_constraint`.
  * `replay.py`: Carga sincronizada de campañas reales SQM y simulador contrafactual (4 días, 30 días y estrés $\text{Mg}^{2+}$).
  * `datos.py`: Conversor y validadores de bases de datos experimentales.
* **`notebooks/`**:
  1. `04_Recirculacion_purga.ipynb`: Estado estacionario, cierre de balances ($Y_{\text{liq}} = Y_{\text{sol}}$) y frente de compromiso pureza vs. recuperación.
  2. `05_Control_PID_dinamico.ipynb`: Lazo abierto, lazo cerrado ante 12 perturbaciones ($\pm$) con ruido coloreado, seguimiento 2-DOF y estabilidad Routh-Hopf ($K_{cu}$).
  3. `06_Control_por_etapas_dilucion.ipynb`: Cierre escalonado `FIRC 3103 → FFIC 3102 → AIT 3105 + AIC 3522`, reciclo/magnesio y *replay* de la campaña real SQM.
* **`docs/`**: Documentación técnica (`control_PID_P&ID.md`, `ROADMAP_control_por_etapas.md`) y figuras exportadas (`docs/fig/`).
* **`tests/`**: Suite de validación automatizada (`96 passed, 2 skipped`).

---

## 4. Instalación y Validación Rápida (`pytest`)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar toda la suite de pruebas unitarias (96 passed, 2 skipped)
python3 -m pytest tests/ -v

# 3. Verificar régimen sostenible (0.50 t/h nominal) en el tren acoplado NPT-3
python3 -c "from msmpr_core import plant; df = plant.simulate_plant_npt3_calibrated(use_AIT3105=True, use_AIC3522=True, tuning_mode='TL_damped', F_303_nom=0.50, F_303_min=0.20, F_303_max=2.50); print('F_303 prom:', round(df['F_303_actual_t_h'].mean(), 2), 't/h | ppm max Refi:', round(df['ppm_ClO4_final_6000'].max(), 2))"

# 4. Verificar matriz RGA 3x3 e Índice de Niederlinski en A3110
python3 -c "import numpy as np, pandas as pd; from msmpr_core import params, plant, control as C; pl = plant.Plant(params.make_params()); x0, u0, d0 = pl.steady_state(alpha=0.25); G, lam, cvs, mvs = C.rga_from_plant(pl, x0, u0, d0); print(pd.DataFrame(lam, index=cvs, columns=mvs).round(3)); print('NI =', round(np.linalg.det(G)/np.prod(np.diag(G)), 2))"

# 5. Verificar solubilidad calibrada de KClO4 y restricción dura (EDT 4.3)
python3 -c "from msmpr_core import dpbe, control as C; o = C.dilution_kclo4_hard_constraint(660.0, 600.0, 0.50/378.18, T_stage2_C=43.0, R_min=0.20/378.18, R_max=2.50/378.18); print('T_sat KClO4 (SSKd):', round(dpbe.T_saturacion_KClO4(dpbe.COMP_SSKD_DEFAULT), 2), '°C | purge_required:', o['purge_required'], '| red_ClO4:', f\"{100*o['clo4_reduction_needed_frac']:.1f}%\")"
```

---

## 5. Próxima Iteración (Integración entre Ramas)

* Completar la integración termodinámica desde `Modelo_Cristalizador_Solubilidad`: $\text{KClO}_4$ ($\ln\Gamma_{\text{KClO}_4,0} = 1{,}571$) ya está acoplado en `dpbe.py`/`control.py`; resta actualizar $\Gamma_{\text{KNO}_3}$ y $k_{\text{Mg}}$ cuando el equipo cierre los ensayos de MLK y $\text{Mg}^{2+}$.
* Aplicar los parámetros cinéticos finales ($k_G, k_B, K_d$) desde `estimacion-parametros` vía `params.apply_calibration(...)` y re-ejecutar `autotune` + `pytest`.
