# Decisiones de Diseño de Control y Pendientes de Planta (NPT-3, SQM)

Última actualización: 2026-11-25. Fuente de lo confirmado: planos P&ID GEA/ABB 172164, reuniones del equipo y validación sobre campañas SQM (`117 passed, 2 skipped` en `pytest`). Lo no confirmado con ingeniería de SQM se mantiene declarado como supuesto.

---

## 1. Decisiones Técnicas Adoptadas (Arquitectura Oficial)

* **Dilución ambientalmente sostenible (`AIT 3105 → FFIC 3102 → FIRC 3103 / FV 3103`):**
  * **Plan de dilución por fases (hipótesis de diseño, NO validada en planta):** Fase 1 con setpoint $12{,}0\text{ t/h}$ ($-40\%$ nominal frente a los $19{,}96\text{ t/h}$ reales; agua media realizada $\approx 16{,}0\text{ t/h}$ bajo perturbaciones, $-20\%$) con `LIC B3520` y pulsos de `FV 3522`. Fase 2 ($5{,}0\text{ t/h}$) no cumple la ventana en simulación. El régimen de $0{,}50\text{ t/h}$ queda **descartado** por inviabilidad hidráulica (Bloque 2).
  * Incorpora compensador dinámico *Lead-Lag* (`LeadLagCompensator`), selector **Override de sobresaturación $\text{KNO}_3$** ($\sigma_{\min} = 0{,}02$) y restricción dura de saturación de $\text{KClO}_4$ calibrada (`dilution_kclo4_hard_constraint`, $\ln\Gamma_{\text{KClO}_4,0} = 1{,}571$, $T_{\text{sat}} = 41{,}29\text{ }^\circ\text{C}$).
  * **Estado de validación:** el "óptimo" depende del modelo y del escenario (6.7: $\geq 22\text{ t/h}$ con $\text{ClO}_4^-$ +550 ppm y $\geq 44\text{ t/h}$ con $\text{Mg}^{2+}$ +35 %; Paso 10: $32\text{–}34\text{ t/h}$; DPBE §9.5: setpoint $15{,}0\text{ t/h}$ con tolerancia $\approx 2\text{ t/h}$). La Fase 1 ($12{,}0\text{ t/h}$) queda bajo el límite que marca el DPBE y debe validarse con ensayos. Ver `docs/revision_dilucion_optima.md` y `docs/diagnostico_replay.md`.
  * *(Nota: el barrido histórico de $[12, 42]\text{ t/h}$ y el antiguo $F_{303}^* = 36{,}8\text{ t/h}$ corresponden a iteraciones previas sin tope ambiental y quedan solo como anexo de referencia).*
* **Purga modulante continua post-`B3520` (`AIC 3522 → FIC 3522 → FV 3522`):**
  * Reemplaza la purga *on/off* actual por una válvula rotatoria bola *V-port* de igual porcentaje ($18\text{–}65\text{ m}^3/\text{h}$, posición `FO` + enclavamiento `LSL` en `B3520` + *Double Block & Bleed*).
  * **Realimentación sin CAPEX de analizador en línea:** alimentada con la **cromatografía iónica (CI) de laboratorio cada $2\text{ h}$** vía LIMS → DCS (aprovechando la constante de tiempo dominante $\tau \approx 2{,}2\text{ h}$ del circuito).
  * Justificación multivariable: con cierre de volumen por dilución (`volume_closure="Q_dil"`), $\lambda(\text{ppm}, Q_{\text{purge}}) = 1{,}002$ (lazo de calidad independiente de $T$ y $\rho$, diseñable como SISO). **Límite:** `Q_out` carece de autoridad sobre la densidad en este modelo, así que el emparejamiento del bloque $T/\rho$ (vacío–descarga) queda pendiente de un modelo con descarga de cristales explícita.
* **Control de Temperatura vía Vacío (`TIR 3101/3201 → PIRCAL 3101/3201`):**
  * Presión de vacío modulada en $[-0{,}920, -0{,}870]\text{ bar man.}$ (`A3110`) y $[-0{,}975, -0{,}940]\text{ bar man.}$ (`A3210`) con sintonía amortiguada **Tyreus–Luyben** (descarta Ziegler–Nichols y evita ciclos límite de Hopf), ponderación 2-DOF ($\beta = 0{,}5$), anti-windup por retrocálculo y *trim* térmico suave en `A3210` ($43{,}0\text{–}44{,}3\text{ }^\circ\text{C}$ en campaña SQM).
* **Control de Inventario y Densidad (`LIRCSAHL`, `DIRCAHL → FIRCAL → SIC`):**
  * `DIRCAHL 3101/3201` mide densidad de pulpa ($x_{S,1} = 13\%$, $x_{S,2} = 20\%$) actuando sobre bombas `P3112`/`P3212` (confirmado: **no** manipula agua de dilución). Nivel mantenido al $60\%$ (`LIRCSAHL`).
* **Alcance empírico y recomendación al Área 6000 (`docs/diagnostico_replay.md`):**
  * El contraste contra $n = 6\,966$ muestras históricas reales muestra que el predictor empírico principal de refinado $> 40\text{ ppm}$ es el $\text{KClO}_4$ del **ML de Refinación en Área 6000** (Spearman $0{,}52$, AUC $= 0{,}74$, límite interno $\approx 3{,}1\text{ g/L}$), mientras que el eslabón `MLK → crudo → refinado` no muestra respaldo empírico directo. Por tanto, el control en Área 3000 actúa como capa regulatoria/preventiva y se recomienda extender el monitoreo y control de $\text{KClO}_4$ al Área 6000.

---

## 2. Supuestos y Parámetros Pendientes de Confirmación en Planta (SQM)

| Ítem pendiente / Supuesto | Estado actual en el modelo | Quién / cómo confirmar | Dónde impacta |
| :--- | :--- | :--- | :--- |
| **Rangeability y capacidad mínima de `FV 3103`** | Fase 1: $12{,}0\text{ t/h}$ nominal ($\tau_v = 8\text{ s}$ placeholder) | Hoja de datos de válvula `FV 3103` en SQM | Cierre de `FIRC 3103` a $12{,}0\text{ t/h}$ |
| **Capacidad receptora aguas abajo de `FV 3522`** | Diseño hasta $65\text{ m}^3/\text{h}$ en posición `FO` + `LSL` en `B3520` | HAZOP formal con operaciones SQM | Ratifica `FO` vs. `FC` + recirculación mínima |
| **Punto de muestreo y retardo de `AIT 3105`** | Aguas arriba de dilución (*feedforward*), supuesto $\theta_{\text{AIT}} = 10\text{–}15\text{ min}$ | P&ID / proveedor de analizador | `LeadLagCompensator` y barrido NB06 §6.5 |
| **Solubilidad real $\Gamma_{\text{KNO}_3,0}$ y efecto $k_{\text{Mg}}$** | `planta_sqm.Cstar_ref` sintético; $k_{\text{Mg}} = 0$ por falta de 2.º ensayo | Laboratorio SQM (`informe_parametros.md` §7) | `params.BASE_PLANTA_SQM`, `dpbe.TERMO_SQM_DEFAULT` |
| **Calibración cinética ($k_G, k_B, K_d$)** | Placeholders (`params.placeholders()`) | Ensayos sembrados y calibración (`estimacion-parametros`) | `params.apply_calibration` |
| **Resolución `DIRCAHL` y ruido PI** | Cuantización $0{,}0002\text{–}0{,}0015$ sólidos; ruido OU $\tau_c = 10\text{ min}$ | Hojas técnicas densímetros + historiador PI | `plant.py`, `control.Ruido` |
| **Especificación contractual escrita de producto** | $w_{\text{KNO}_3}$ mín., $\text{ClO}_4^-$ máx. $40\text{ ppm}$ (provisional) | SQM por escrito | `config/specs.yaml` |
