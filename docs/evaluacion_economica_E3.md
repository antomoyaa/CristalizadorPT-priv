# Evaluación Económica E3 (Calibrada con Planilla del Equipo — Towler & Sinnott)

Base: WACC = `14,11 %`, horizonte `10 años`, depreciación lineal `5 años` sobre FCI, rampa `50 %` Año 1, impuesto `25,5 %` (año 1 = 2027), `24,0 %` (año 2) y `23,0 %` (desde año 3), con año 1 = 2027, campaña de calibración `3,0 kUSD`.

## 1. Comparativa de Alternativas (Caso Base Conservador, Δη = 2,0 % sin crédito de agua de dilución)

| Alternativa                           |   CAPEX [kUSD] |   OPEX [kUSD/año] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback simple [años] |   Payback descontado [años] |
|:--------------------------------------|---------------:|------------------:|-----------------------------:|-------------:|----------:|------------------------:|----------------------------:|
| A (Recomendada: DCS + FV 3522 + LIMS) |          159.3 |              16.4 |                         90.7 |        131.1 |      31.6 |                    3.03 |                         4.1 |
| B (Con analizadores en línea AIT/AIC) |          414.3 |              38.6 |                         90.7 |       -204.7 |       0.1 |                    9.96 |                       nan   |


## 2. Escenarios de Alternativa A (Fase 1: ahorro de agua nominal y realizado)

El setpoint de Fase 1 (12,0 t/h) recorta 7,96 t/h solo en términos nominales; bajo las perturbaciones de la simulación el agua media realizada es 16.0 t/h, es decir un ahorro de 3.95 t/h frente a la media real de 19,96 t/h. El escenario nominal es una cota superior.

| Escenario                                                              |   CAPEX [kUSD] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback simple [años] |   Payback descontado [años] |
|:-----------------------------------------------------------------------|---------------:|-----------------------------:|-------------:|----------:|------------------------:|----------------------------:|
| Conservador Estricto (Δη=1,3 %, f=2,2, P=800)                          |          174.9 |                         54   |        -23.2 |      10.8 |                    5.68 |                      nan    |
| Caso Base Conservador (Δη=2,0 %, sin agua dil.)                        |          159.3 |                         90.7 |        131.1 |      31.6 |                    3.03 |                        4.1  |
| Fase 1 con ahorro de agua NOMINAL (Δη=2,5 % + 7,96 t/h, cota superior) |          159.3 |                        236.3 |        662   |      83.6 |                    1.43 |                        1.64 |
| Fase 1 con ahorro de agua REALIZADO (3.95 t/h; Δη=2,5 %)               |          159.3 |                        174.3 |        436.4 |      63.2 |                    1.77 |                        2.09 |
| Optimista (Δη=5,0 % meta SQM, f=1,5, P=950)                            |          120.2 |                        245.8 |        735.6 |     109.7 |                    1.19 |                        1.32 |


## 3. Análisis de Sensibilidad (Tornado — 6 Variables)

| Variable                                            |   VAN Bajo [kUSD] |   VAN Alto [kUSD] |   Amplitud [kUSD] |
|:----------------------------------------------------|------------------:|------------------:|------------------:|
| Ahorro agua dilución Fase 1 (0 vs 7,96 t/h nominal) |             131.1 |             579.5 |             448.4 |
| Mejora eficiencia Δη (1,0 % vs 3,5 %)               |             -40.5 |             379.3 |             419.8 |
| Factor instalación f_inst (3,5 vs 1,5)              |               8.1 |             170.5 |             162.4 |
| Margen operacional (12 % vs 18 %)                   |              64.1 |             196.6 |             132.5 |
| Tasa descuento WACC (18 % vs 10 %)                  |              89.9 |             186.9 |              97   |
| Precio KNO₃ (800 vs 950 USD/t)                      |             102.3 |             159.4 |              57.1 |


## 4. Flujo de Caja Descontado — Alternativa A (Caso Base Conservador)

|   Año |   Beneficio [kUSD] |   OPEX [kUSD] |   EBITDA [kUSD] |   Deprec. [kUSD] |   Impuesto [kUSD] |   Flujo Neto [kUSD] |   Flujo Desc. [kUSD] |   Acum. Desc. [kUSD] |
|------:|-------------------:|--------------:|----------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|
|     0 |               0    |          0    |            0    |             0    |              0    |             -159.3  |              -159.3  |              -159.3  |
|     1 |              45.34 |         16.37 |           28.96 |            31.26 |              0    |               28.96 |                25.38 |              -133.92 |
|     2 |              90.67 |         16.37 |           74.3  |            31.26 |             10.33 |               63.97 |                49.13 |               -84.79 |
|     3 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                43.34 |               -41.45 |
|     4 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                37.98 |                -3.47 |
|     5 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                33.29 |                29.82 |
|     6 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                25.91 |                55.73 |
|     7 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                22.71 |                78.44 |
|     8 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                19.9  |                98.34 |
|     9 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                17.44 |               115.78 |
|    10 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                15.28 |               131.06 |

