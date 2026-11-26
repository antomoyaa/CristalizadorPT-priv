# Evaluación Económica Preliminar (Rúbrica E3 — Supuestos Referenciales Editables)

> **Nota de trazabilidad:** Los precios unitarios, CAPEX y costos de reproceso son **valores referenciales de ingeniería** (editables en `SUPUESTOS_E3` dentro de `scripts/evaluacion_economica_e3.py`) hasta contar con cotizaciones formales o confirmación de SQM. El caso base asume **$\Delta\text{KNO}_3 = 0{,}0\text{ t/h}$** para no depender del beneficio no calibrado del *replay*.

## 1. Comparativa de Alternativas (Horizonte 10 años, WACC 10 %, Impuesto 27 %)

| Alternativa                           |   CAPEX [kUSD] |   OPEX [kUSD/año] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback simple [años] |   Payback descontado [años] |
|:--------------------------------------|---------------:|------------------:|-----------------------------:|-------------:|----------:|------------------------:|----------------------------:|
| A (Recomendada: DCS + FV 3522 + LIMS) |            174 |                14 |                        820.7 |       3473.3 |     341.1 |                    0.29 |                        0.32 |
| B (Con analizador en línea AIT)       |            438 |                52 |                        855.7 |       3239.8 |     136.6 |                    0.73 |                        0.8  |


## 2. Escenarios — Alternativa A (Recomendada)

| Escenario   |   CAPEX [kUSD] |   Beneficio bruto [kUSD/año] |   VAN [kUSD] |   TIR [%] |   Payback descontado [años] |
|:------------|---------------:|-----------------------------:|-------------:|----------:|----------------------------:|
| Conservador |            174 |                        204.8 |        639.3 |      82.5 |                        1.4  |
| Base        |            174 |                        820.7 |       3473.3 |     341.1 |                        0.32 |
| Optimista   |            174 |                       1741.5 |       8319.4 |     727.5 |                        0.15 |


## 3. Análisis de Sensibilidad (Tornado — 5 Variables)

| Variable                                  |   VAN Bajo [kUSD] |   VAN Base [kUSD] |   VAN Alto [kUSD] |   Amplitud [kUSD] |
|:------------------------------------------|------------------:|------------------:|------------------:|------------------:|
| Captura de rechazos >40 ppm (15 % – 55 %) |            1677.3 |            3473.3 |            5269.4 |            3592.1 |
| Costo evitado reproceso (12 – 32 USD/t)   |            2044.7 |            3473.3 |            4902   |            2857.3 |
| Ahorro de agua de dilución (0 – 15 t/h)   |            2935.1 |            3473.3 |            4280.7 |            1345.6 |
| Tasa de descuento WACC (12 % – 8 %)       |            3179.9 |            3473.3 |            3809   |             629.1 |
| Variación de CAPEX (+30 % / -20 %)        |            3429.8 |            3473.3 |            3502.4 |              72.6 |


## 4. Flujo de Caja Descontado — Alternativa A (Caso Base)

|   Año |   Beneficios [kUSD] |   OPEX [kUSD] |   Depreciación [kUSD] |   UAI [kUSD] |   Impuesto [kUSD] |   Flujo Neto [kUSD] |   Flujo Descontado [kUSD] |
|------:|--------------------:|--------------:|----------------------:|-------------:|------------------:|--------------------:|--------------------------:|
|     0 |                 0   |             0 |                   0   |          0   |               0   |              -174   |                    -174   |
|     1 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     539.6 |
|     2 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     490.6 |
|     3 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     446   |
|     4 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     405.4 |
|     5 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     368.6 |
|     6 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     335.1 |
|     7 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     304.6 |
|     8 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     276.9 |
|     9 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     251.7 |
|    10 |               820.7 |           -14 |                 -17.4 |        789.3 |            -213.1 |               593.6 |                     228.9 |

