# Diagnóstico del replay NPT-3 contra la base química real

Base: 6 966 marcas de tiempo de 2 h (ene-2025 a nov-2026) con cristal sin refinar/refinado, ML de refinación, MLK y T de cristalización.
Script: `scripts/diagnostico_replay.py` (necesita los Excel locales). Solo se publican métricas agregadas.

| Predictor del ppm de refinado | Spearman | AUC fuera de muestra (corte 2026-01-01, >40 ppm) |
|---|---|---|
| KClO4 del ML de refinación | 0,52 | **0,74** |
| ClO4 del cristal sin refinar | 0,36 | 0,64 |
| Mg del MLK | 0,17 | 0,58 |
| KClO4 del MLK | 0,03 | 0,47 |
| Exceso del MLK sobre C_sat (hinge del replay) | −0,02 | 0,50 |

Eslabón MLK → cristal crudo: Spearman 0,04–0,06 con rezagos de 0 a 24 h. El MLK supera la C_sat del replay en el 8,8 % de las muestras;
en ellas el crudo tiene mediana 229 ppm (199 sin exceso) y el refinado supera 40 ppm el 16,1 % (17,7 % sin exceso).

Recalibrar seis coeficientes del replay (a0, a_b, a_c, k_cop, c0_refi, k_refi; residuo censurado en el piso de 20 ppm; entrena 16-oct a 5-nov,
valida 5 a 15-nov) no mejora la capacidad de detectar excedencias: la sensibilidad cae de 0,12 a 0,00 en validación, el término de coprecipitación
tiende a 0 (a_c → 0) y los demás coeficientes chocan con sus cotas. El ML de refinación simulado tiene correlación −0,04 con el medido.

**Conclusión.** En estos datos la variable asociada al ppm del refinado es el KClO4 del ML de refinación (Área 6000), coherente con el análisis
interno de SQM (límite ≈ 3,1 g/L). La cadena MLK → coprecipitación → crudo → refinado del replay no tiene respaldo empírico, por lo que su
contrafactual ("0 % >40 ppm" con menos dilución y más purga del MLK) no está validado.

> **Nota metodológica (`calibrar_replay`):** La recalibración de coeficientes se ejecuta sobre la ventana `d30` (`usar_sensores_4d=False`, donde $T_2$ y $Q_{\text{purga}}$ son constantes nominales por ausencia de sensores cada 10 min en los 30 días); esto no afecta el diagnóstico de Spearman/AUC sobre las $n = 6\,966$ muestras históricas reales, que utiliza directamente `Temp. A3000` medida.
