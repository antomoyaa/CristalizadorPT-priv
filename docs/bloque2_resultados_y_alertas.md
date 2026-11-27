# Bloque 2 · Balance Hidráulico B3520, Sensibilidad KNO₃ y Regla de Alerta Empírica

## 1. Balance volumétrico del estanque B3520 (150 m³, LSL = 20 %)

La arquitectura balanceada por etapas (coordinando nivel `LIC B3520` con pulsos modulantes en `FV 3522` el `15 %` del tiempo) recorta **`40 %` del agua en Fase 1** (`12,0 t/h`) y **`75 %` en Fase 2** (`5,0 t/h`) con **`0,0 %` tiempo en LSL** y **`0,00 m³/h` de déficit**.

| Escenario                                                         |   Agua dilución [t/h] |   Ahorro agua [%] |   Purga comandada [m³/h] |   Purga efectiva con LSL [m³/h] |   Déficit medio [m³/h] |   Nivel mín. B3520 [%] |   % tiempo en LSL (20 %) |
|:------------------------------------------------------------------|----------------------:|------------------:|-------------------------:|--------------------------------:|-----------------------:|-----------------------:|-------------------------:|
| 1. Real SQM (19,96 t/h; purga 22,0 m³/h)                          |                 19.96 |               0   |                    22    |                           22    |                   0    |                   65   |                      0   |
| 2. Corte extremo SIN balance (0,98 t/h + purga 38,4 fija)         |                  0.98 |              95.1 |                    38.43 |                            3.68 |                  34.75 |                   20   |                     98.2 |
| 3. Propuesta Fase 1 (-40 % agua: 12,0 t/h + pulsos 26 m³/h + LIC) |                 12    |              39.9 |                    13.89 |                           13.89 |                   0    |                   38.3 |                      0   |
| 4. Propuesta Fase 2 (-75 % agua: 5,0 t/h + pulsos 18 m³/h + LIC)  |                  5    |              74.9 |                     6.9  |                            6.9  |                   0    |                   40.8 |                      0   |
| 5. Respaldo hidráulico (19,96 t/h + pulsos 36 m³/h + LIC)         |                 19.96 |               0   |                    21.83 |                           21.83 |                   0    |                   33.5 |                      0   |


## 2. Sensibilidad del beneficio neto de KNO₃ (`K_AGUA` vs. `K_PURGA`)

### 2.1 Arquitectura Balanceada Fase 1 (−7,96 t/h agua y −7,96 m³/h purga media)

|   K_AGUA [t/t] |   K_PURGA=0.03 |   K_PURGA=0.055 |   K_PURGA=0.15 |   K_PURGA=0.3 |   K_PURGA=0.6 |
|---------------:|---------------:|----------------:|---------------:|--------------:|--------------:|
|           0.15 |           1.43 |            1.63 |           2.39 |          3.58 |          5.97 |
|           0.25 |           2.23 |            2.43 |           3.18 |          4.38 |          6.77 |
|           0.38 |           3.26 |            3.46 |           4.22 |          5.41 |          7.8  |
|           0.45 |           3.82 |            4.02 |           4.78 |          5.97 |          8.36 |


### 2.2 Contraste Replay 30 d sin balance (−19,13 t/h agua y +12,98 m³/h purga)

|   K_AGUA [t/t] |   K_PURGA=0.03 |   K_PURGA=0.055 |   K_PURGA=0.15 |   K_PURGA=0.3 |   K_PURGA=0.6 |
|---------------:|---------------:|----------------:|---------------:|--------------:|--------------:|
|           0.15 |           2.48 |            2.16 |           0.92 |         -1.02 |         -4.92 |
|           0.25 |           4.39 |            4.07 |           2.84 |          0.89 |         -3.01 |
|           0.38 |           6.88 |            6.56 |           5.32 |          3.38 |         -0.52 |
|           0.45 |           8.22 |            7.89 |           6.66 |          4.71 |          0.82 |


## 3. Regla de alerta empírica de excedencias (>40 ppm en Área 6000)

- **Fuente:** Base química real SQM (Base de datos_v2.xlsx, n=7128, test 2026 n=3416)

- **AUC fuera de muestra:** ML Refinación = `0.739`, Crudo = `0.635`, Logística combinada = `0.758`


| Nivel                 | Condición operativa (LIMS c/2 h)        |   P(>40 ppm) empírica [%] | Acción de control recomendada                                                              |
|:----------------------|:----------------------------------------|--------------------------:|:-------------------------------------------------------------------------------------------|
| Verde (Normal)        | ML Refi <= 1,2 g/L y Crudo <= 300 ppm   |                       2   | Operación Fase 1: agua 12,0 t/h, purga base ~12 m³/h, cascada TIR->PIRCAL en 40 °C.        |
| Amarillo (Preventivo) | ML Refi 1,2-2,0 g/L o Crudo 300-400 ppm |                      11.7 | Aviso en DCS; alistar pulso FV 3522 y verificar estabilidad T2 (A3210).                    |
| Naranja (Alerta)      | ML Refi 2,0-3,0 g/L o Crudo 400-600 ppm |                      25.8 | Pulso modulante FV 3522 (24-26 m³/h), trim térmico T2 (+1-2 °C) y purga ML Área 6000.      |
| Rojo (Crítico)        | ML Refi > 3,0 g/L o Crudo > 600 ppm     |                      46.2 | Purga máxima segura protegida por LSL (20 %), purga intensiva ML Refi y desvío preventivo. |

