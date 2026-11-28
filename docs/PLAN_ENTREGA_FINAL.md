# Plan para la entrega final (7 de diciembre de 2026)

Estado al 25-nov-2026. Clasifica cada pendiente según quién lo resuelve y si alcanza el tiempo (12 días). Alineado con la rúbrica E3 (IIQ3253).

## A. Podemos corregir ahora con la información que tenemos

| Pendiente | Qué hacer | Esfuerzo |
|---|---|---|
| Cifra de dilución única | Presentar el plan por fases (Fase 1: 12,0 t/h nominal ≈ 16,0 realizado; 0,50 t/h descartado) y el rango 22–44 t/h de los modelos acoplados (`docs/revision_dilucion_optima.md`) | 1–2 h (parche de .md ya hecho) |
| Replay sin balance de agua | Agregar balance de volumen del lazo B3520 al replay y repetir el contrafactual | 1–2 días |
| Beneficio de KNO3 (+6 t/h) | Análisis de sensibilidad de `K_AGUA` y `K_PURGA` (rango 0,03–0,6 t/m3 de pérdida por purga) y reportar un intervalo | 0,5–1 día |
| Etiquetas con números fijos (celdas 11, 17, 19, 23 del NB06) | Calcularlas de los datos; rotular las curvas de Hopf del Paso 10 como ilustrativas | 0,5 día |
| Reencuadre de la propuesta | Poner como eje el KClO4 del ML de refinación y el cristal que llega a refinación (tablas de `docs/tabla_resultados.md`) | 0,5 día |
| Regla de alerta empírica | Umbrales por tabla/logística: P(>40 ppm) según ML refi y crudo; alarmas al superar ≈ 2 g/L o 400 ppm | 1 día |
| Re-ejecutar NB06 con los Excel | Refrescar salidas y figuras (incluye `06_recirculacion...png`) | 0,5 h |
| Higiene del repositorio | Repo privado, sacar el PDF de SQM de la punta, purgar historial si SQM lo exige | 1 h (comandos en la respuesta del chat) |
| Bloque económico E3 | CAPEX/OPEX, ingresos, tasa de descuento, flujo de caja descontado (VPN, TIR, *payback*), sensibilidad con ≥ 3 variables y escenarios | 3–4 días |
| Aspectos legales/ambientales y ética/seguridad | Permisos, CO2e de construcción y operación, jerarquización de riesgos, HAZOP preliminar de `FV 3522` | 2 días |

## B. Debe resolverlo SQM (experimentos, análisis químicos o datos de planta)

| Pendiente | Qué se necesita |
|---|---|
| Solubilidad real del KNO3 en SSKd y efecto del Mg | Protocolo de la Entrega 2 (§12.10.4): curva q*add por temperatura y matriz |
| Curva de saturación del KClO4 con Mg y NaNO3 | Ensayo nuevo (el actual es referencial de años anteriores) |
| Cinética: MSZW, tiempo de inducción, nucleación secundaria | Protocolos 12.10.2 (kB, kG, Kd) |
| Mecanismo de incorporación del ClO4- | Lavado escalonado y PXRD (12.10.1 y 12.10.5) |
| Efecto de la agitación | Protocolo 12.10.3 |
| Efecto real de la dilución y la purga sobre el ppm | Ensayo escalonado en planta o a escala banco con SSKd real |
| Rangeabilidad de `FV 3103`, capacidad de `FV 3522`, HAZOP | Hojas de datos de válvulas, receptor de la purga, ingeniería SQM |
| Punto de muestreo y retardo del analizador `AIT 3105` | P&ID / proveedor |
| Caudal real de purga (sensor) y flujo de dilución medido | Datos históricos de planta; en nov-2026 la purga real se usa como serie, no como constante |
| Especificación contractual escrita (ClO4- máx. 40 ppm) | Confirmación por escrito |
| Precios y costos para E3 (KNO3, agua, energía, válvulas) | Valores de SQM o fuentes públicas justificadas |

## C. No alcanza antes del 7 de diciembre

- Calibración de kG, kB y Kd con ensayos sembrados del KNO3 real (semanas de laboratorio).
- PXRD y lavado escalonado completos (2–3 semanas de laboratorio y análisis).
- Validación en planta del plan de dilución por fases y de los lazos `AIT 3105`/`AIC 3522` (requiere HAZOP, instalación y campaña).
- Modelo de descarga de cristales para resolver la RGA del bloque T/ρ (desarrollo de 2–3 días; baja prioridad frente a lo económico).
- Optimizar F303 con datos reales (depende de B).

**Cómo decirlo en la entrega:** lo que está respaldado es el diagnóstico (ML de refinación y cristal que llega a refinación) y el diseño de lazos con simulación; lo no respaldado se presenta como hipótesis con el plan experimental y su cronograma.

## D. Orden sugerido de trabajo

| Fecha | Prioridad |
|---|---|
| 26-nov | Aplicar parches, re-ejecutar NB06, repo privado, borrar el PDF de la punta |
| 27–30 nov | Bloque económico E3 (CAPEX/OPEX, flujo de caja, sensibilidad) con escenarios conservadores |
| 1–2 dic | Balance de agua del replay y sensibilidad del beneficio de KNO3 |
| 3 dic | Legal/ambiental (CO2e), ética y seguridad |
| 4–5 dic | Informe final y presentación (secuencia, tiempo, léxico) |
| 6 dic | Ensayo y revisión final |
| 7 dic | Entrega |
