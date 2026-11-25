# ¿Cuál es el flujo óptimo de agua de dilución (F_303)?

El repositorio no contiene un optimizador de F_303: el flujo es la salida de la ley de razón `F_303 = F_pre · R_eff` (nominal 27,14 t/h, R₀ = 0,0718,
acotado a 12–42 t/h) con trims por ClO₄⁻ (AIT 3105) y Mg²⁺. Los "óptimos" que aparecen son resultados de distintos modelos y criterios:

| Fuente | F_303 | Criterio |
|---|---|---|
| Diseño / planta (medido) | 27,14 / 19,96 t/h | nominal PFD / media campaña nov-2026 |
| README y replay | 0,50 t/h | régimen "sostenible" (sin validación; ver `docs/diagnostico_replay.md`) |
| Paso 10 (NB06), tabla de Pareto | 36,8 t/h | mín J en una grilla gruesa con ruido; el "óptimo" estaba fijado a mano |
| Paso 10, barrido fino sin ruido | 32 t/h mínimo con pico ≤ 40 ppm; mín J = 34 t/h | mismo modelo, escalón +650 ppm ClO₄⁻ |
| 6.7 (`scripts/barrido_dilucion.py`) | ≥ 22 t/h (ClO₄⁻ +550 ppm); ≥ 44 t/h (Mg²⁺ +35 %) | mínimo F_303 constante con ppm ≤ 40 |

El óptimo depende del escenario, del modelo y de los pesos de J (4,5; 1,75; umbral 26,5 ppm; 1,8). Con umbral 40 ppm en vez de 26,5, el mínimo de J pasa
de 34 a 32 t/h. Todos estos modelos usan parámetros placeholder y la evidencia histórica no respalda el vínculo MLK → ppm (`docs/diagnostico_replay.md`),
por lo que ninguno de estos valores debe presentarse como el óptimo de planta.
