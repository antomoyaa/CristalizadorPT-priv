# Evaluación Económica E3 (Calibrada con Planilla del Equipo — Towler & Sinnott)

Base: WACC = `14,11 %`, horizonte `10 años`, depreciación lineal `5 años` sobre FCI, rampa `50 %` Año 1, impuesto `25,5 %` (años 1-2) y `23,0 %` (desde año 3), campaña de calibración `3,0 kUSD`.

## 1. Comparativa de Alternativas (Caso Base Conservador, Δη = 2,0 % sin crédito de agua de dilución)

| Alternativa                           |   CAPEX [kUSD] |   OPEX [kUSD/año] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback simple [años] |   Payback descontado [años] |
|:--------------------------------------|---------------:|------------------:|-----------------------------:|-------------:|----------:|------------------------:|----------------------------:|
| A (Recomendada: DCS + FV 3522 + LIMS) |          159.3 |              16.4 |                         90.7 |        130.6 |      31.5 |                    3.04 |                        4.12 |
| B (Con analizadores en línea AIT/AIC) |          414.3 |              38.6 |                         90.7 |       -204.7 |       0.1 |                    9.96 |                      nan    |


## 2. Escenarios de Alternativa A (incluyendo Fase 1 Balanceada con −40 % agua)

| Escenario                                                 |   CAPEX [kUSD] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback simple [años] |   Payback descontado [años] |
|:----------------------------------------------------------|---------------:|-----------------------------:|-------------:|----------:|------------------------:|----------------------------:|
| Conservador Estricto (Δη=1,3 %, f=2,2, P=800)             |          174.9 |                         54   |        -23.2 |      10.8 |                    5.69 |                      nan    |
| Caso Base Conservador (Δη=2,0 %, sin agua dil.)           |          159.3 |                         90.7 |        130.6 |      31.5 |                    3.04 |                        4.12 |
| Objetivo Fase 1 Balanceada (Δη=2,5 % + ahorro agua -40 %) |          159.3 |                        236.3 |        659.9 |      83.2 |                    1.44 |                        1.65 |
| Optimista (Δη=5,0 % meta SQM, f=1,5, P=950)               |          120.2 |                        245.8 |        733.2 |     109.1 |                    1.19 |                        1.32 |


## 3. Análisis de Sensibilidad (Tornado — 6 Variables)

| Variable                                    |   VAN Bajo [kUSD] |   VAN Alto [kUSD] |   Amplitud [kUSD] |
|:--------------------------------------------|------------------:|------------------:|------------------:|
| Ahorro agua dilución Fase 1 (0 vs 7,96 t/h) |             130.6 |             577.5 |             446.9 |
| Mejora eficiencia Δη (1,0 % vs 3,5 %)       |             -40.5 |             378   |             418.5 |
| Factor instalación f_inst (3,5 vs 1,5)      |               7.9 |             169.9 |             162   |
| Margen operacional (12 % vs 18 %)           |              63.8 |             195.9 |             132.1 |
| Tasa descuento WACC (18 % vs 10 %)          |              89.5 |             186.4 |              96.9 |
| Precio KNO₃ (800 vs 950 USD/t)              |             101.9 |             158.9 |              57   |


## 4. Flujo de Caja Descontado — Alternativa A (Caso Base Conservador)

|   Año |   Beneficio [kUSD] |   OPEX [kUSD] |   EBITDA [kUSD] |   Deprec. [kUSD] |   Impuesto [kUSD] |   Flujo Neto [kUSD] |   Flujo Desc. [kUSD] |   Acum. Desc. [kUSD] |
|------:|-------------------:|--------------:|----------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|
|     0 |               0    |          0    |            0    |             0    |              0    |             -159.3  |              -159.3  |              -159.3  |
|     1 |              45.34 |         16.37 |           28.96 |            31.26 |              0    |               28.96 |                25.38 |              -133.92 |
|     2 |              90.67 |         16.37 |           74.3  |            31.26 |             10.97 |               63.32 |                48.63 |               -85.29 |
|     3 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                43.34 |               -41.95 |
|     4 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                37.98 |                -3.96 |
|     5 |              90.67 |         16.37 |           74.3  |            31.26 |              9.9  |               64.4  |                33.29 |                29.32 |
|     6 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                25.91 |                55.23 |
|     7 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                22.71 |                77.94 |
|     8 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                19.9  |                97.84 |
|     9 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                17.44 |               115.28 |
|    10 |              90.67 |         16.37 |           74.3  |             0    |             17.09 |               57.21 |                15.28 |               130.57 |

