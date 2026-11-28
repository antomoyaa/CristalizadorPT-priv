# ¿Cuál es el flujo óptimo de agua de dilución (F_303)?

El repositorio no contiene un optimizador de F_303: el flujo es la salida de la ley de razón `F_303 = F_pre · R_eff` (nominal 27,14 t/h, R₀ = 0,0718,
acotado a 12–42 t/h) con trims por ClO₄⁻ (AIT 3105) y Mg²⁺. Los "óptimos" que aparecen son resultados de distintos modelos y criterios:

| Fuente | F_303 | Criterio |
|---|---|---|
| Diseño / planta (medido) | 27,14 / 19,96 t/h | nominal PFD / media campaña nov-2026 |
| Replay original | 0,50 t/h | **descartado**: inviable hidráulicamente (Bloque 2) y sin balance de agua |
| Plan por fases (Bloque 2 / E3) | Fase 1: 12,0 nominal (≈ 16,0 realizado); Fase 2: 5,0 (falla la ventana) | balance hidráulico de B3520 + simulación de planta |
| DPBE·MSMPR §9.5 / `config/ventana_operacion.json` | 15,0 (tolerancia ≈ 2) | setpoint de la ventana; el DPBE predice coprecipitación bajo ≈ 13 |
| Paso 10 (NB06), tabla de Pareto | 36,8 t/h | mín J en una grilla gruesa con ruido; el "óptimo" estaba fijado a mano |
| Paso 10, barrido fino sin ruido | 32 t/h mínimo con pico ≤ 40 ppm; mín J = 34 t/h | mismo modelo, escalón +650 ppm ClO₄⁻ |
| 6.7 (`scripts/barrido_dilucion.py`) | ≥ 22 t/h (ClO₄⁻ +550 ppm); ≥ 44 t/h (Mg²⁺ +35 %) | mínimo F_303 constante con ppm ≤ 40 |

El óptimo depende del escenario, del modelo y de los pesos de J (4,5; 1,75; umbral 26,5 ppm; 1,8). Con umbral 40 ppm en vez de 26,5, el mínimo de J pasa
de 34 a 32 t/h. Todos estos modelos usan parámetros placeholder y la evidencia histórica no respalda el vínculo MLK → ppm (`docs/diagnostico_replay.md`),
por lo que ninguno de estos valores debe presentarse como el óptimo de planta.
