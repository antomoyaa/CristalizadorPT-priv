# Relación Mg²⁺–ClO₄⁻: el Mg como trazador del licor adherido

Datos: tabla horaria de 2025 (`tabla_limpia_valores.xlsx`, rama `Prediccion_efecto_de_analitos`), n = 3 391 horas con cristal sin refinar, MLK y refinado.
Código: `msmpr_core/mg_trazador.py`, `scripts/analisis_mg_perclorato.py`. Solo se publican métricas agregadas (`docs/analisis_mg_perclorato.json`).

## Método
El Mg²⁺ no entra a la red del KNO₃: el Mg del cristal mide cuánto licor madre lleva adherido. Si todo el ClO₄⁻ fuera licor adherido,
`ClO4_esperado = Mg_cristal · (ClO4_licor / Mg_licor)`. Lo que se mide por sobre eso es ClO₄⁻ no explicado por impregnación (ocluido o coprecipitado).
Control de cordura: el Mg del cristal implica un licor adherido de ≈ 4,7 % (mediana), coherente con el 7 % del balance de diseño.

## Resultados
| Resultado | Valor |
|---|---|
| ClO₄⁻ del cristal sin refinar **no explicado** por el licor adherido | mediana **33 %** (p25–p75: 17–73 %) |
| …con cristal ≤ 200 / 200–400 / 400–600 / > 600 ppm | 20 % / 46 % / 77 % / 85 % |
| % de refinado > 40 ppm en esos mismos tramos | 6 % / 16 % / 27 % / 49 % |
| AUC (refinado > 40 ppm): ClO₄⁻ explicado por licor | **0,40** (sin información) |
| AUC: ClO₄⁻ **no explicado** (exceso) | **0,79** (> ML de refinación 0,77 y > ClO₄⁻ crudo 0,75) |
| Spearman exceso vs Mg del MLK / vs ClO₄⁻ del MLK | 0,29 / 0,12 |
| Techo (p95) del KClO₄ del MLK, Mg 25–40 g/L | ≈ 5,9–6,0 g/L, plano (cae a 5,1 con Mg > 40, n = 41) |
| Spearman Mg vs ClO₄⁻ del cristal sin refinar (misma muestra) | 0,37 |

## Lectura
1. **Lo que el lavado puede remover (licor adherido) no predice el refinado; lo no adherido sí.** La parte del ClO₄⁻ explicada por el licor tiene AUC 0,40 y la no explicada 0,79. Es coherente con el piso de ≈ 23 % que SQM no logra remover ni con refinación en caliente.
2. **Por sobre ≈ 400 ppm en el cristal, 77–85 % del ClO₄⁻ no es licor adherido.** Ahí la probabilidad de refinado > 40 ppm sube a 27–49 %. Controlar la CSD o el lavado solo actúa sobre el licor adherido, así que su alcance es limitado en ese régimen.
3. **Mg y ClO₄⁻ del licor están desacoplados en el rango operativo** (Spearman ≈ 0 en MLK y SSK; techo de KClO₄ plano ≈ 6 g/L entre 25 y 40 g/L de Mg). No se observa la caída de solubilidad por Mg que suponen los modelos (6.7: −0,85·ΔMg/Mg₀; replay: e^(−0,022·ΔMg)). Solo hay indicio con Mg > 40 g/L (n = 41) o < 20 g/L, que no sirve para calibrar.
4. **El exceso de ClO₄⁻ se asocia más con el Mg del MLK (0,29) que con su ClO₄⁻ (0,12)**, compatible con salting-out del KClO₄, pero la correlación es moderada y no demuestra causa.

## Inconsistencias que esto deja al descubierto
- **Entrega 2 (§6.1.4):** afirma que "todo el perclorato del producto se explica por el licor adherido". Con el Mg como trazador, en promedio un tercio no se explica, y por sobre 400 ppm la mayoría. Hay que corregir el texto.
- **Base de Mg del NB06 6.7:** el modelo parte de Mg(B3520) = 9,2 g/L, mientras que el MLK medido tiene mediana 31 g/L (el replay sí usa 30,5 g/L). El escalón de +35 % se aplica sobre otra base.

## Limitaciones
- Supone Mg del cristal en % másico (`mg_factor = 1e4`), ρ del licor 1,45 kg/L y que el licor adherido tiene la relación ClO₄/Mg del MLK de la misma hora (no el licor de A3210 y sin rezago).
- Es correlacional; la confirmación es PXRD, el lavado escalonado y un ensayo de solubilidad con Mg variable (protocolos de la Entrega 2).
- Solo cubre 2025 (la tabla horaria llega a 16-dic-2025).
