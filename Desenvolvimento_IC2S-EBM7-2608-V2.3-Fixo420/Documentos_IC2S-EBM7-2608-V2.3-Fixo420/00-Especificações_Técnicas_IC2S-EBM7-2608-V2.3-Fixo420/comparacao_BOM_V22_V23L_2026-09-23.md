# Comparação de componentes — EBM7 V2.2 (fabricada) → V2.3 legacy 4-20 mA

**Fontes:** BOM de fabricação da V2.2 (`Arquivos_Fabricação…/01-BOM_List…/BOM_PartType-…V22….xls`) e netlist reconstruída da V2.2
(`Reconstruida_IC2S-EBM7-2608-V2.2.Net`); esquemático da V2.3L exportado hoje (`kicad-cli sch export bom` e `netlist`).
**Método:** os designadores foram renumerados entre versões, por isso a correspondência é feita **pela função**: as redes a que cada
peça liga em cada versão. Onde a função foi deduzida da topologia (e não de um documento), está marcado *(inferido)*.

| | V2.2 | V2.3L |
|---|---|---|
| Peças montadas | 119 (BOM) | 137 + 1 DNP (R8) |
| Números de peça distintos | 43 | 54 |

## 1. Entrada e alimentação

| Função | V2.2 | V2.3L | Nota |
|---|---|---|---|
| Alimentação do lado de campo | 2 × **PDM2-S24-S24-S** (U1, U2), DC/DC isolado 24→24 V 2 W | laço directo de +24V por F2 e D3 (+24V_ADC) + **TPS7A4001DGNR** (U12), LDO 24→12 V (+12V_TPS, ±Vs dos TPS26613) com R25 93k1 / R26 10k | o lado de campo deixa de ser isolado do 24 V; GND_24V–GND_ADC unidos por R1 0 R (nota 7 da folha 02) |
| 5 V do lado analógico | **CRE1S2405SC** (U3), DC/DC isolado 24→5 V 1 W | **R-78HB5.0-0.5L** (U1), buck não isolado | |
| Fusíveis de entrada | 0466.125NR 125 mA (F1) + 2 × 3413.0008.22 160 mA (F2, F7) | 2 × **CC12H750MA-TR** (F1, F2) | 3 → 2 |
| Díodos de polaridade | 3 × PMEG6010CEH (D1, D3, D5) | 2 × **MBR1H100SFT3G** (D2, D3) | 3 → 2 |
| TVS na entrada +24V | — | **SMA6J33A-Q** (D1) | novo |
| Bulk de entrada/saída 10 µF | 5 × UMK316BBJ106ML 10 µF 50 V 1210 | 3 × **GRM32EC72A106ME05L** 10 µF 100 V 1210 (C1, C2, C35) + **C3216X5R1H106K** 10 µF 50 V 1206 (C38, +12V_TPS) | |
| Electrolíticos | 2 × ESL107M050AGMAA 100 µF THT | — | saem |
| 100 nF no 24 V do campo | 2 × C1206C104M5RAC 100 nF 50 V 1206 | GRM188R72A104KA35D 100 nF 100 V 0603 (C34, C36) | |
| Condensadores Y da barreira | 6 × C1206C102KGRACTU 1 nF 2 kV | — | saem com a isolação |
| Bulk do 5 V | GRM32ER61A107ME20K 100 µF 10 V 1210 (C17) | 2 × **CL21A226KOQNNNG** 22 µF 0805 (C3, C5) | |
| Carga no +5V_REG | — | 2 × **RC1206FR-07220RL** 220 R 1206 (R2, R3) | novo; carga mínima do Recom *(inferido)* |
| Clamp do +5V_REG | ZMM5234B 6,2 V | ZMM5234B (D4) | mantido |
| LEDs | 3 × LG Q396-PS-35 com 2 × 14k7 (R1, R2) | 2 × **KG EELP41.22** (D5 com R4 2k2 no +5V_REG; D18 com **R27 22k** no +24V_ADC) | 3 → 2 |
| Zener no +24V | BZT52H-B2V4 2,4 V (D25) | — | sai |
| 3,3 V digital | MCP1824ST-3302E/DB (U8) | MCP1824ST-3302E/DB (U2) | mantido |

## 2. Referência, ADC e alimentação analógica

| Função | V2.2 | V2.3L | Nota |
|---|---|---|---|
| ADC | AD7124-8BCPZ | AD7124-8BCPZ (U6) | mantido |
| LDO 3,3 V analógico | SPX3819M5-L-3-3 (U4) | SPX3819M5-L-3-3 (U3) | mantido |
| Referência 2,5 V | ADR4525 (U7) — está na netlist mas **não na BOM XLS** | ADR4525BRZ (U7) | mantido; a BOM da V2.2 omite U7 e C43–C46 |
| Protecção do +3.3V_ANA | — | **TL431BQDBZR** (U4), shunt 3,6 V, com R6 4k42 / R7 10k | novo |
| Desacoplo 100 nF | 15 × TMK107BJ104KA 100 nF 25 V | 26 × **GRM188R72A104KA35D** 100 nF 100 V | uniformizado a 100 V |
| 1 µF | 885012206002 | 885012206002 (C21) + 3 × **C0603C105K4RACTU** (C22, C41, C47) | |
| Filtros passantes | 2 × NFM18PC104R1C3D | 2 × NFM18PC104R1C3D (C15, C16) | mantidos; footprint corrigido hoje |
| Ferrites | 7 × BLM18PG471SN1D | 7 × BLM18PG471SN1D | mantidas |

## 3. Laços 4–20 mA (×4)

| Função | V2.2 | V2.3L | Nota |
|---|---|---|---|
| Protector de laço | — | 4 × **TPS26613DDFR** (U8–U11) + divisor VSNS R22 11k5 / R23, R24 6k65 | novo |
| Resistência de medida (burden) | 249 R + 160 R em série = 409 Ω (8 peças) | 4 × **110 R** (R13, R14, R15, R17) | nota (2) da Table 8-2 do TPS2661x; **sem MPN no esquemático** |
| Fusível por canal | 4 × F0603G0R10FNTR 70 mA 0603 | 4 × **3413.0002.22** 1206 (F3–F6) | |
| TVS na alimentação do laço (+24V_AINx) | 4 × 824500301 | 4 × **SMBJ36A-13-F** (D9, D10, D12, D13) | |
| TVS no sinal (AINx) | 4 × 824500301 | 4 × 824500301 (D6, D7, D8, D11) | mantido |
| Clamp à entrada do ADC | 4 × BAT54SLT1G | **BAV199LT1G** (D14–D17) | |
| 0 R | 3 × 0 R (R150–R152, no +2.5_VREF) | 6 × 0 R (R1 net-tie, R10, R11, R12, R16; R8 DNP) | funções diferentes, não comparar peça a peça |

## 4. Célula de carga

| Função | V2.2 | V2.3L | Nota |
|---|---|---|---|
| Resistência de excitação | CR1206-FX-18R0ELF 18 R ¼ W | **SG73P2BTTD68R0F** 68 R 1 W (R30) | |
| Selector de excitação | FTS-102-01-L-D, 2×2 (+3,3 V) | **FTS-103-01-L-D**, 2×3 (5 V / 3,3 V / 2,5 V) + **RB162MM-60TR** (D23) | |
| Fonte 2,5 V de excitação | — | **LP5907MFX-2.5** (U13) + C47 1 µF | novo (previsão) |
| Resistências série da célula | 2 × ERA-3AEB101V 100 R 0,1 % | 2 × **RG1608P-132-B-T5** 1k3 0,1 % (R31, R32) + **C46** 2,2 µF diferencial | filtro anti-aliasing |
| Referência ratiométrica (REFIN1+) | — | 2 × **RG1608P-103-B-T5** 10k 0,1 % (R28, R29) + BAV199 (D22) | novo |
| TVS nas linhas da célula | 2 × 824500301 | 2 × **824500101** (D20, D21) | |
| TVS na excitação | 824500301 (em IEXC2) | **SMA6J6.0A** (D19, em IEXC_OUT) | |
| Clamp à entrada do ADC | 2 × BAV199LT1G | BAV199LT1G (D24, D25) | mantido |

## 5. NTC

| Função | V2.2 | V2.3L |
|---|---|---|
| NTC | NTCS0603E3103JLT | NTCS0603E3103JLT (R36) |
| Resistência do divisor | ERA-3AEB5621V 5k62 0,1 % | **RG1608P-223-B-T5** 22k 0,1 % (R37) |
| Resistências 3k | 2 × RC0603FR-073KL | 2 × RC0603FR-073KL (R38, R39) |
| Filtro | GCM188R71H103KA37J 10 nF | GCM188R71H103KA37J (C48) |

## 6. Mantidos sem alteração

AD7124-8BCPZ, ISO7141CCDBQR, MCP1824ST-3302E/DB, SPX3819M5-L-3-3, ADR4525, NFM18PC104R1C3D, BLM18PG471SN1D, 824500301 (4 de 11),
BAV199LT1G, ZMM5234B, 0603YD106KAT2A, C1608X5R1E225K080AB, 885012206002, GCM188R71H103KA37J, NTCS0603E3103JLT, CRCW0603100KFKEA,
RC0603FR-072K2L, RC0603FR-073K3L, RC0603FR-073KL, RC0603JR-070RL, M20-7822046 (P1), M20-7821446 (P2).

## 7. Pendentes encontrados nesta comparação

- **R13, R14, R15, R17 (110 R) sem MPN** no esquemático da V2.3L.
- A **BOM XLS da V2.2 não lista U7 (ADR4525) nem C43–C46**, que estão na netlist reconstruída; a BOM de fabricação da V2.2 estava incompleta.
- A exportação agrupada do `kicad-cli` marca os seis 0 R como DNP porque agrupa por valor; só **R8** é DNP. Qualquer BOM de compra tem de ser
  exportada sem agrupar por valor, ou agrupando também pelo campo DNP.

## 8. Dimensionamento do burden de 110 Ω e orçamento RF2 (adenda 23-09)

**Fontes (A):** TI SLVSFE3C p.5 (IOL 25/32/40 mA; IQ ≤ 0,1 µA), p.6 (V(SNSR) 1,72 V, V(SNSF) 1,00 V só típico), p.20 Table 8-2 notas (1)(2),
p.23 Table 8-3 (MODE = GND); Schurter USFF 1206 p.4 (3413.0002 = 50 mA, 430 mV a In); ADI ADR4525 Rev. G p.4 (grau B ±0,02 %,
soldadura ±0,02 %, 2 ppm/°C box, VIN 3–15 V, dropout 500 mV), p.9 (25 ppm/1000 h), p.35 Table 11 (COUT ≥ 1 µF), p.6/p.9 (carga 0,1–100 µF);
AD7124-8 Rev F p.5 (erro de ganho ±0,0025 % G = 1, deriva 1–2 ppm/°C). **Premissas (D):** barramento 18–32 V (decisão 15-09); ambiente
20–60 °C (ΔT 40 K, decisão 04-09); os canais 4-20 mA medem contra +2,5_VREF (ADR4525) — configuração de firmware, não verificada.

| Restrição | Conta | Resultado |
|---|---|---|
| Fundo de escala do ADC | 2,5 V / 110 Ω | 22,7 mA — 20 mA usa 88 %; cobre falha NAMUR ≥ 21 mA |
| TI nota (1) | R1 + R2 = 11k5 + 3k325 = 14,8 kΩ ≤ 12,09 V / 45 µA = 269 kΩ | passa |
| TI nota (2) | V(SNSF)·(R1+R2)/R2 = 4,46 V > I·Rb | 20 mA: 2,2 V (margem 2×); 22 mA: 2,4 V; 40 mA (limite máx.): 4,40 V — margem 1,3 %, só em falha |
| Tensão disponível ao transmissor a 18 V, 20 mA | 18 − D3 ≈ 0,5 [FD] − fusível 0,18 − TPS 12,5 Ω máx. 0,25 − Rb 2,2 | ≈ 14,9 V (transmissores típicos pedem 10–12 V) |
| Potência | 20 mA: 44 mW; 22,7 mA: 57 mW; falha 40 mA: 176 mW 100 ms / 0,9 s | exige ≥ 0,1 W (0,125 W preferível) e capacidade de pulso |
| ADR4525 | VIN 3,3 V ≥ 3,0 V; COUT = C24 100 nF + C25 10 µF = 10,1 µF (1…100 µF) | passa |

**Orçamento RF2 (< 0,2 % FS) com burden 0,1 % / 25 ppm/K:** inicial 0,1 + 0,02 + 0,02 + 0,0025 = 0,14 %; deriva em 40 K 0,1 (Rb) + 0,008 (ref)
+ 0,008 (ADC) + 0,04 (auto-aquecimento ≈ 15 K) + 0,005 (ref, 4500 h) = 0,16 %. **Sem calibração:** pior caso 0,30 % ❌, RSS 0,15 %.
**Com calibração por unidade a 25 °C:** pior caso 0,16 % ✅. Com burden 1 %/100 ppm não cumpre nem calibrado (0,4 % só de deriva).
