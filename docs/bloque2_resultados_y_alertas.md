# Bloque 2: Balance de Volumen `B3520`, Sensibilidad de $\text{KNO}_3$ y Regla de Alerta Empírica

## 1. Cierre de Balance de Agua/Volumen en `B3520` (Ventana 103 h)

| Escenario                                                            |   Agua dilución [t/h] |   Purga comandada [m³/h] |   Purga efectiva con LSL [m³/h] |   Déficit medio de purga [m³/h] |   Nivel mín. B3520 [%] |   % tiempo en LSL (20 %) |
|:---------------------------------------------------------------------|----------------------:|-------------------------:|--------------------------------:|--------------------------------:|-----------------------:|-------------------------:|
| 1. Real SQM (19,96 t/h; purga 22,0 m³/h)                             |                 19.96 |                    22    |                           22    |                            0    |                     60 |                      0   |
| 2. Propuesta 0,98 t/h + purga 38,4 m³/h (SIN reposición)             |                  0.98 |                    38.43 |                            3.6  |                           34.83 |                     20 |                     98.4 |
| 3. Propuesta 10,0 t/h + purga 28,0 m³/h (parcial)                    |                 10    |                    28    |                           12.62 |                           15.38 |                     20 |                     96.4 |
| 4. Balanceado: 19,96 t/h + purga 22,0 m³/h c/pulsos 38 m³/h (15 % t) |                 19.96 |                    22.39 |                           22.39 |                            0    |                     32 |                      0   |


> **Lectura clave:** Reducir el agua de dilución de `19,96` a `0,98 t/h` mientras se eleva la purga a `38,4 m³/h` genera un déficit volumétrico de `~35,4 m³/h` que lleva `B3520` al enclavamiento `LSL (20 %)` en `< 2 h`, limitando la purga efectiva sostenible a `~3,0 m³/h` salvo reposición de licor o menor evaporación. Esto confirma que el escenario de `0,50 t/h` del *replay* no puede operar sin cerrar el balance hídrico global.


## 2. Sensibilidad del Beneficio Neto de $\text{KNO}_3$ (`K_AGUA` y `K_PURGA`)

|   K_AGUA [t KNO3/t agua] |   K_PURGA [t KNO3/m³ purga] |   Delta KNO3 neto [t/h] |   Delta KNO3 neto [kt/año] |   K_PURGA breakeven [t/m³] | Signo económico   |
|-------------------------:|----------------------------:|------------------------:|---------------------------:|---------------------------:|:------------------|
|                     0.15 |                       0.03  |                    2.35 |                      18.83 |                      0.173 | Ganancia          |
|                     0.15 |                       0.055 |                    1.94 |                      15.55 |                      0.173 | Ganancia          |
|                     0.15 |                       0.15  |                    0.38 |                       3.06 |                      0.173 | Ganancia          |
|                     0.15 |                       0.3   |                   -2.08 |                     -16.66 |                      0.173 | Pérdida neta      |
|                     0.15 |                       0.45  |                   -4.55 |                     -36.37 |                      0.173 | Pérdida neta      |
|                     0.15 |                       0.6   |                   -7.01 |                     -56.09 |                      0.173 | Pérdida neta      |
|                     0.25 |                       0.03  |                    4.25 |                      34.02 |                      0.289 | Ganancia          |
|                     0.25 |                       0.055 |                    3.84 |                      30.73 |                      0.289 | Ganancia          |
|                     0.25 |                       0.15  |                    2.28 |                      18.24 |                      0.289 | Ganancia          |
|                     0.25 |                       0.3   |                   -0.18 |                      -1.47 |                      0.289 | Pérdida neta      |
|                     0.25 |                       0.45  |                   -2.65 |                     -21.19 |                      0.289 | Pérdida neta      |
|                     0.25 |                       0.6   |                   -5.11 |                     -40.9  |                      0.289 | Pérdida neta      |
|                     0.38 |                       0.03  |                    6.72 |                      53.76 |                      0.439 | Ganancia          |
|                     0.38 |                       0.055 |                    6.31 |                      50.47 |                      0.439 | Ganancia          |
|                     0.38 |                       0.15  |                    4.75 |                      37.98 |                      0.439 | Ganancia          |
|                     0.38 |                       0.3   |                    2.28 |                      18.27 |                      0.439 | Ganancia          |
|                     0.38 |                       0.45  |                   -0.18 |                      -1.45 |                      0.439 | Pérdida neta      |
|                     0.38 |                       0.6   |                   -2.65 |                     -21.16 |                      0.439 | Pérdida neta      |
|                     0.5  |                       0.03  |                    9    |                      71.98 |                      0.578 | Ganancia          |
|                     0.5  |                       0.055 |                    8.59 |                      68.69 |                      0.578 | Ganancia          |
|                     0.5  |                       0.15  |                    7.03 |                      56.2  |                      0.578 | Ganancia          |
|                     0.5  |                       0.3   |                    4.56 |                      36.49 |                      0.578 | Ganancia          |
|                     0.5  |                       0.45  |                    2.1  |                      16.77 |                      0.578 | Ganancia          |
|                     0.5  |                       0.6   |                   -0.37 |                      -2.94 |                      0.578 | Pérdida neta      |


> **Lectura clave:** El `+6,13 t/h` original corresponde únicamente al punto `K_AGUA = 0,38` y `K_PURGA = 0,055 t/m³`. Con `K_PURGA = 0,60 t KNO₃-eq/m³` (equivalente a licor ML 234 sin recuperación posterior), el balance se vuelve **negativo (`-2,65 t/h` para `K_AGUA = 0,38`)**. Por ello, el beneficio en la evaluación económica E3 debe sustentarse principalmente en la **reducción de reprocesos/rechazos `> 40 ppm`** y no depender de un supuesto `+6 t/h` no calibrado.


## 3. Regla de Alerta Empírica (`P(Refinado > 40 ppm)`)

- **Fuente:** Tabla empírica consolidada (n=6 966, docs/tabla_resultados.md §2–3)

- **AUC fuera de muestra:** ML Refinación = `0.74`, Crudo = `0.64`


| Nivel Alerta          | Condición ML Refinación (A6000)   | Condición Cristal Crudo (A3000)   | P(>40 ppm) empírica   | Acción operacional recomendada                                                                                                   |
|:----------------------|:----------------------------------|:----------------------------------|:----------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| VERDE (Normal)        | ≤ 1,2 g/L                         | ≤ 300 ppm                         | 2,0 % – 3,0 %         | Operación normal con cascada TIR→PIRCAL en automático; seguimiento rutinario LIMS c/2 h.                                         |
| AMARILLO (Preventiva) | 1,2 – 2,0 g/L                     | 300 – 400 ppm                     | 11,7 % – 28,6 %       | Aumentar purga modulante en Área 6000/B3520 dentro de balance hídrico; verificar T2 A3210 y lavado CF 3000.                      |
| NARANJA (Alta)        | 2,0 – 3,0 g/L                     | 400 – 600 ppm                     | 22,9 % – 28,8 %       | Alarma DCS en sala de control; purga prioritaria de ML de refinación (A6000) y revisión de alimentación SSK.                     |
| ROJO (Crítica)        | > 3,0 g/L (o > 4,0 g/L)           | > 600 ppm                         | 30,8 % – 51,5 %       | Intervención inmediata: máxima purga permitida por LSL, verificar temperatura A3210 y segregar/reprocesar lote si supera 40 ppm. |

