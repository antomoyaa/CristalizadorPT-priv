# Tabla de resultados para la presentación

Fuentes: simulaciones de este repositorio (`msmpr_core`, NB05/NB06), base química de SQM (n = 6 966, ene-2025 a nov-2026) y presentaciones/informes de SQM. Los resultados de modelo usan parámetros *placeholder* y **no están validados en planta**; los marcados como datos de SQM provienen de la empresa.


## 1. Problema (datos SQM)

| Indicador | Valor | Fuente |
|---|---|---|
| Análisis de refinado >40 ppm (ene-2025 a abr-2026) | 18,0 % de 5 531 | Entrega 2, base de KPI de SQM |
| Refinado >40 ppm (ene-2025 a nov-2026) | 17,5 % de 6 966; mediana 20 ppm; p90 54 ppm | `docs/diagnostico_replay.md` |
| Cristal sin refinar | mediana 201 ppm; 25 % >400 ppm; 15 % >600 ppm | base química (n = 6 966) |
| Producción recuperable al subir eficiencia del Área 6000 5–10 % | ≈ 90 t/d | comunicación de SQM (Entrega 2) |
| Remoción total de ClO4- en el A6000 (SQM) | 89,9 % (62,1 % refinación + 27,8 % lavado) | presentación SQM mayo-2026 |
| Subir el lavado de 60 a 100 L/min | −90 t/d de producto (sin mejora consistente de remoción) | presentación SQM mayo-2026 |

## 2. Qué explica el ppm del refinado (n = 6 966; corte temporal 2026-01-01)

| Predictor | Spearman con ppm refinado | AUC fuera de muestra (>40 ppm) |
|---|---|---|
| KClO4 del ML de refinación (g/L) | 0,52 | 0,74 |
| ClO4 del cristal sin refinar (ppm) | 0,36 | 0,64 |
| Mg del MLK (g/L) | 0,17 | 0,58 |
| KClO4 del MLK (g/L) | 0,03 | 0,47 |
| Exceso del MLK sobre C_sat (hinge del replay) | -0,02 | 0,50 (azar) |


> **Cruce con modelado estadístico (`Prediccion_efecto_de_analitos`, ene–dic 2025):** `Temp_Cristalización2_A3000` (`A3210`) es el predictor operacional n.º 1 por importancia de permutación para $\text{ClO}_4^-$ crudo (`0,071`) y refinado (`0,092`, seguido de `T Cry A3110` con `0,051`); `Agua de dilución` no resulta estadísticamente significativa ($p > 0{,}39$ en OLS); `Cristal sin refinar Mg` alcanza $R^2 = 0{,}653$ fuera de muestra (ventana $8\text{ h}$) dominado por `Agua de lavado Cf 3000` (`0,337`); y `RidgeCV` no supera el *baseline* $\Delta = 0$ en $\text{ClO}_4^-$, descartando un *soft-sensor* ML puro para cerrar el lazo.

## 3. Probabilidad de refinado >40 ppm

| Condición | % de muestras >40 ppm | n |
|---|---|---|
| KClO4 ML refinación ≤ 1,2 g/L | 3,0 % | 1 551 |
| KClO4 ML refinación 1,2–2 g/L | 11,7 % | 2 448 |
| KClO4 ML refinación 2–3 g/L | 22,9 % | 1 548 |
| KClO4 ML refinación 3–4 g/L | 30,8 % | 779 |
| KClO4 ML refinación > 4 g/L | 46,2 % | 640 |
| Cristal sin refinar ≤ 300 ppm | 9,0 % | 4 758 |
| Cristal 300–400 ppm | 28,6 % | 462 |
| Cristal 400–600 ppm | 28,8 % | 709 |
| Cristal 600–800 ppm | 37,7 % | 536 |
| Cristal > 800 ppm | 51,5 % | 501 |
| Cristal ≤ 400 ppm y ML ≤ 1,2 g/L | 2 % | 1 492 |
| Cristal > 600 ppm (cualquier ML) | 44–50 % | 1 037 |

## 4. Modelo: verificación

| Elemento | Resultado | Comentario |
|---|---|---|
| MSMPR / DPBE (d50 estacionario) | analítico 246 µm vs malla 248 µm (0,7 %); span 1,34 | correcto (Gamma de orden 4) |
| Solubilidad KNO3 (Apelblat vs Perry, 20–80 °C) | error ≤ 1,7 % | agua pura |
| Solubilidad KClO4 (SSKd, 25/30/35 °C) | 3,40/3,95/4,63 vs 3,48/3,90/4,59 g/L (≤ 2,3 %) | T de inflexión 41,3 °C vs ≈ 40 °C del ensayo (conservador) |
| Respuesta T a +10 % de evaporación | K = −5,85 °C/(kg/s), τ = 2,18 h, RMSE 0,027 °C | FOPDT sobre el modelo no lineal |
| Routh-Hopf del lazo T-vacío | Padé: Kcu 0,0280; retardo exacto: 0,0221 bar/°C (+27 %); simulación: 0,0124 (Pu 9,7 min) | parámetros de la tabla fijados a mano; Padé no es conservador |
| RGA con Q_purge como MV | λ(ppm, Q_purge) = 1,002; NI = +58,7 | Q_out sin autoridad sobre ρ: bloque T/ρ no evaluable |

## 5. Recirculación B3520 con escalones (6.7)

| Estrategia | ppm máx. | Producción media [t/h] | Cumple <40 ppm |
|---|---|---|---|
| Sin reciclo (operación actual) | 64,5 | 66,5 | No (tras Mg +35 %) |
| Reciclo fijo α = 25 % | 542,8 | 72,2 | No |
| Reciclo inteligente (AIT 3105 + AIC 3522) | 67,6 | 63,1 | No; purga saturada en 100 % desde ≈100 min |
| Inteligente corregido (α0 = 1 + trim por saturación, F303 máx. 60 t/h) | 33,3 | 61,1 | Sí; F303 final ≈ 48 t/h (−5,4 t/h vs actual) |

## 6. Flujo de agua de dilución F303 (modelo; NO validado en planta)

| Fuente / escenario | F303 [t/h] | Criterio |
|---|---|---|
| Diseño PFD / medido en planta | 27,14 / 19,96 | nominal / media nov-2026 |
| Propuesta (README, replay) | 0,50 (promedio 0,67–0,98) | contrafactual sin balance de agua cerrado |
| 6.7, ClO4- +550 ppm | ≥ 22 | mín. F303 constante con ppm ≤ 40 |
| 6.7, Mg2+ +35 % | ≥ 44 (46 con 2 ppm de margen) | ídem |
| 6.8c (+650 ppm ClO4-), barrido fino sin ruido | ≥ 32 (mín. J: 34) | pico ≤ 40 ppm |
| 6.8c, tabla de Pareto original | 36,8 | mín. J en grilla gruesa con ruido |

## 7. Replay contrafactual (campaña 10–15 nov 2026)

| Indicador | Valor | Lectura |
|---|---|---|
| Baseline vs 56 análisis reales | RMSE 22,45 ppm; r = 0,26 | ajuste bajo |
| Excedencias reales detectadas por el baseline | 3 de 15 (sensibilidad 0,20; especificidad 0,93) | no reproduce los picos |
| Excedencias: real vs simulado | 26,8 % vs 11,3 % | el baseline subestima |
| Recalibrar 6 coeficientes (entrena 16-oct a 5-nov; valida 5 a 15-nov) | sensibilidad 0,12 → 0,00 | coprecipitación tiende a 0 |
| Propuesta en el modelo | máx. 23,7 ppm; 0 % >40; −95,1 % de agua | propiedad del modelo (piso de 20 ppm), no predicción de planta |
| Beneficio neto de KNO3 (+6 t/h) | fórmula lineal 0,38·Δagua − 0,055·Δpurga | coeficientes sin calibrar; ML 234 ≈ 0,6 t KNO3-eq/m3 |

## 8. Automatización en cascada TIR → PIRCAL (6.12, Figura 12; modelo con *placeholders*)

Escenario dinámico de 300 min con escalones simultáneos de carga (`+8 %`), temperatura de alimentación (`+3,5 °C`), perturbación de vacío (`+0,008 bar`) y $\text{ClO}_4^-$ en `SSK` (`+650 ppm`).

| Estrategia | $T_2$ máx. / final [°C] | Agua media [t/h] | $\text{ClO}_4^-$ máx. A6000 [ppm] | $\text{KNO}_3$ entrada / licor A3210 [kg/m³] | $d_{50}$ A3210 mín. / final [µm] |
|---|---|---|---|---|---|
| Actual SIN cascada T→P (`PIRCAL` manual, 27,1 t/h) | 41,79 / 41,73 | 27,93 | 64,02 (61,9 % >40) | 538,6 / 188,6 | 467,0 / 517,4 |
| Cascada TIR→PIRCAL + Dilución PFD (27,1 t/h) | 40,52 / 40,00 | 36,20 | 26,37 (0,0 % >40) | 528,1 / 185,6 | 452,7 / 500,2 |
| Cascada TIR→PIRCAL + Sostenible (0,50 t/h + AIC 3522) | 40,52 / 40,00 | 0,67 | 22,65 (0,0 % >40) | 576,2 / 185,0 | 514,0 / 564,0 |
