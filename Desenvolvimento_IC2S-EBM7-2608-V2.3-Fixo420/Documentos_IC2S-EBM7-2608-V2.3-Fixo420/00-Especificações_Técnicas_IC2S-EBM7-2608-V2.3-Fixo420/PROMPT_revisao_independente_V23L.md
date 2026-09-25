# Prompt — revisión independiente EBM7 V2.3 legacy

Copiar todo lo que está entre las dos líneas en una sesión NUEVA de Claude Code
(idealmente con otro modelo), abierta en `C:\hw\hw-ebm7-v2.2`.

---

Eres un revisor independiente de hardware. Vas a revisar una PCB que diseñó otra persona y que otra sesión de IA
modificó. Tu trabajo es verificar, no validar: busca lo que está mal, no confirmes lo que está bien.

## Objeto de la revisión

- Proyecto KiCad 10: `Desenvolvimento_IC2S-EBM7-2608-V2.2\Projeto_IC2S-EBM7-2608-V2.2\KiCad_EBM7_V23_LEGACY_4-20\`
  - PCB: `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_pcb`
  - Esquemático raíz: `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_sch` (8 hojas)
  - Biblioteca de footprints del proyecto: `footprints\EBM7_V23.pretty\`
- Datasheets locales: `Desenvolvimento_IC2S-EBM7-2608-V2.2\Projeto_IC2S-EBM7-2608-V2.2\Documentos_de_Referência-IC2S-EBM7-2608-V2.2\`
- Requisitos del producto: `Desenvolvimento_IC2S-EBM7-2608-V2.2\Documentos_IC2S-EBM7-2608-V2.2\00-Especificações_Técnicas_IC2S-EBM7-2608-V2.2\escopo_EBM7_respin.md` (tabla RF1–RF6).

Es una placa de expansión de PLC: AD7124-8 con 4 lazos 4-20 mA (protectores TPS26613), una célula de carga en puente
con excitación seleccionable por jumper (H1: 5 V / 3,3 V / 2,5 V) y una NTC; aislador ISO7141 hacia el lado digital.

## Datos de entrada que no están en el CAD

El software que lee el AD7124 corre en una Raspberry Pi (no hay firmware en la placa). Su configuración actual,
informada por el responsable del software el 24-09-2026: referencia AVDD en todos los canales; todos los buffers de
entrada y de referencia activados; laços con ganancia 1 unipolar, negativo = DGND interno (código 19); célula con
ganancia 128 bipolar; SINC3, sin rechazo 50/60 Hz; modo continuo, full power, reloj interno; SPI 1 MHz modo 3;
calibración de 6 puntos por placa y por canal guardada en el Pi; AIN8/AIN9 (NTC) no configurados. Tienen previsto
pasar los laços a REFIN2 y la célula a REFIN1.

## Tareas, en este orden

1. **`/2shw-pcb:check-roteamento`** sobre la PCB indicada. Solo lectura.
2. **`/2shw-pcb:verificar-aplicacao-datasheet`** para todos los CI críticos: AD7124-8 (U6), ADR4525 (U7),
   ISO7141 (U5), TPS26613 (U8–U11), TPS7A4001 (U12), LP5907 (U13), SPX3819 (U3), MCP1824 (U2), R-78HB (U1),
   TL431 (U4), y los TVS/diodos de protección. Incluye las restricciones cruzadas entre componentes y el test de una
   multiplicación por cadena analógica (lazo, célula, NTC), evaluando también la configuración de software descrita
   arriba contra el datasheet del AD7124.
3. Un informe final que junte las dos cosas, con los hallazgos ordenados por severidad.

## Reglas

- **Solo lectura.** No modifiques ningún archivo del proyecto, no hagas commits, no ejecutes `sch_annotate`.
  Tus scripts y archivos temporales van a la carpeta temporal de la sesión.
- No toques ni uses como referencia `KiCad_EBM7_V2.3_ensaio_SPI` ni `KiCad_EBM7_V2.3_mouser`.
- **No leas** los informes previos de esta placa hasta haber terminado tus propios hallazgos:
  `relatorio_roteamento_*.md`, `relatorio_emc_*.md`, `verificacao_aplicacao_*.md`, `comparacao_BOM_*.md`,
  `perguntas_firmware_*.md` de la carpeta del proyecto. Al final, y solo al final, puedes compararlos y decir en qué
  coincides y en qué no.
- Toda frase atribuida a un datasheet sale de una búsqueda en el PDF en esta sesión, con página. Si no está, escribe
  «no consta en este PDF». Pinouts: confirma en el dibujo renderizado, no solo en el texto.
- Clasifica cada conclusión por su fuente: A (datasheet), B (física/medida en la placa), C (regla del proyecto),
  D (criterio propio). Un umbral que no venga del datasheet se marca D.
- Mide sobre la geometría real (pcbnew con `C:\Program Files\KiCad\10.0\bin\python.exe`, o `kicad-cli`), no sobre
  suposiciones. Los footprints pueden traer pads pasantes que funcionan como vías: cuéntalos.
- Datos conocidos como faltantes: la sensibilidad de la célula (mV/V) no está definida; el datasheet local del diodo
  D23 es del RB162MM-40, pero la BOM usa RB162MM-60TR. Trátalos como «falta dato», no los inventes.
- Murata, TDK, onsemi y ADI bloquean descargas automáticas: si falta un datasheet, márcalo `[FD]` y sigue.

## Entregables (en portugués, en la carpeta temporal de la sesión)

- `check_roteamento_V23L_independente.md`
- `verificacao_aplicacao_V23L_independente.md`
- `revisao_independente_V23L_resumo.md` — veredicto (lista para fabricar / no), bloqueantes, hallazgos por
  severidad con fuente A/B/C/D, lo que no pudiste verificar y por qué, y al final la comparación con los informes
  previos.

---
