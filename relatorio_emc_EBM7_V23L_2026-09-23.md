# Revisão EMC de pré-conformidade — EBM7 V2.3 legacy (V23L)

**Placa:** `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_pcb`, gravada em 2026-09-23 10:16:16.
**Ferramenta:** skill `kicad-happy:emc` 2.2.0 — `analyze_schematic.py` → `analyze_pcb.py --full` → `analyze_emc.py --standard cispr-class-a --spice-enhanced` (ngspice), corrida `2026-09-23_1028`.
**Norma alvo:** CISPR 32 / EN 55032 classe A (ambiente industrial). O analisador é de *risco*, não prevê conformidade: só o ensaio em laboratório acreditado o faz.
**Método:** cada achado do analisador foi **re-medido** na geometria real da PCB com `pcbnew` (polígonos preenchidos das zonas, vias, pads), porque o analisador não conhece as três referências de terra desta placa. Cada linha diz de onde vem a conclusão: **A** datasheet, **B** física/medida, **C** regra do projecto, **D** critério próprio.

## 1. Resultado bruto do analisador

| | |
|---|---|
| Pontuação de risco | 0 / 100 |
| Achados | 38 — 10 error, 24 warning, 4 info |
| Categorias | plano de terra, desacoplo, I/O, relógio, stackup, emissão, retorno, PDN |

A pontuação **não tem significado** aqui: dos 10 *errors*, 3 (SU-001) e 2 (PD-001) são falsos positivos do analisador e 1 (GP-005) é a arquitectura pretendida (ver §2). Descontados, o risco real é **baixo-médio**, concentrado em vias de retorno.

## 2. Achados verificados um a um

| Regra | Analisador | Verificação na geometria | Veredito | Fonte |
|---|---|---|---|---|
| SU-001 ×3 | «camadas de sinal adjacentes F/In1, In1/In2, In2/B» | In1 e In2 são **planos de terra**: GND_ADC 2 715 mm² + DGND 338 mm² + GND_24V 125 mm² = **87 % da placa** em cada camada interna; B.Cu 82 %. O analisador não reconhece planos formados por várias zonas. | **falso positivo** | B |
| PD-001 +5V_REG | anti-ressonância 398 MHz, alvo 0,028 Ω «Vout = 0,5 V, 0,9 A» | O «0,5» é o sufixo do MPN R-78HB5.0-**0.5**L, não a tensão; a carga de 0,9 A é inventada (a placa consome < 0,2 A). Sem cargas digitais rápidas não há corrente a 400 MHz para excitar o pico. | **falso positivo** | B |
| PD-001 +12V_TPS | anti-ressonância 501 MHz, «Vout = 6,186 V» | Vout real = VREF × (1 + R25/R26) = 1,173 × (1 + 93,1 k/10 k) = **12,09 V** (VREF 1,173 V típ., TI TPS7A4001 p.5). Rail correcto; o pico a 500 MHz é irrelevante para um LDO que alimenta ±Vs dos TPS26613. | **falso positivo** (mas confirma o divisor) | A/B |
| GP-005 | «3 domínios de terra» | DGND (PLC) ↔ GND_ADC isolados pelo ISO7141 (U5); GND_24V ↔ GND_ADC unidos por **R1 0 R**; GND_24V e DGND chegam ambos de P1 (pinos 19 e 3/12/16). É a arquitectura pretendida; barreira medida 1,20 mm (relatório de roteamento). | **intencional** | C/B |
| GP-001 CS_ADC 57 % | «vão no plano de referência» | O analisador só conta GND_ADC. Sobre **DGND** a cobertura real é **68 %**; o troço sem plano é B.Cu (121,2; 100,5)–(120,5; 101,2) a entrar no pad 9 de P1: são os furos do conector. | real, irrelevante (sinal lento, 0,7 mm) | B |
| GP-001 CLK/MISO/MOSI 92–93 % | idem | Cobertura real sobre DGND 92–93 %; os troços a 24–48 % são os últimos 1,3–2 mm até aos pads de P1. Inevitável num conector THT. | real, irrelevante | B |
| GP-001 EXC_SEL 71 % | idem | Real **58 %**: a pista F.Cu (150,0–154,6; 78,4) corre **em cima da fila de pads de H1**, cujos furos abrem In1. EXC_SEL é DC (selector de excitação). | real, irrelevante | B |
| GP-001 MISO_ADC_ISO 75 % | idem | Real **86 %**; vão em (136,0; 98,6)–(136,4) F.Cu e B.Cu (136,0; 98,6–101,2) — é a zona de vias/pads junto a U5 e C13. Sinal SPI isolado com flancos rápidos: ver RP-001. | real, menor | B |
| GP-001 Temp2_AIN9 78 % | idem | Real 76 %; troços F.Cu (150,1–152,3; 82,0) e (150,1; 86,2–87,2) passam sobre os furos de H1 e vias. Entrada analógica lenta filtrada. | real, menor | B |
| GP-001 AIN1–4, Load_Cell±, REFIN1+, VSNS 80–94 % | idem | Reais 87–94 %; os vãos são todos os últimos mm até aos pads de P2 (x = 176,5) ou de fusíveis. | real, irrelevante | B |
| RP-001 MISO_ADC_ISO | «2 transições sem via GND a 1 mm» | Vias (136,0; 98,6) e (136,0; 101,2): GND mais próxima a **2,61 / 3,15 mm**. | **confirmado** — corrigir | B |
| RP-001 Temp2_AIN9, REFIN1+ | idem | (150,1; 86,2) → GND a **5,12 mm**; (152,7; 84,9) → **4,87 mm**; (152,3; 82,0) → 2,78; (164,8; 82,8) → 1,87. | confirmado, prioridade menor (sinais lentos, REFIN1+ é referência do ADC) | B |
| RP-001 VSNS | 4 transições | GND a 2,56–3,27 mm. VSNS é tensão de sentido DC dos TPS26613. | confirmado, irrelevante | B |
| RP-001 CS_ADC | 1 transição | (125,8; 100,5) → DGND a 3,62 mm. | confirmado, menor | B |
| DC-003 C17 | «4,9 mm da via» | **C17 = desacoplo IOVDD do AD7124 (U6.2)**: pad GND a **4,73 mm** da via GND mais próxima; pad +3.3V_IOVDD a 7,38 mm. O AD7124 pede o 0,1 µF «right up against the device» com retorno curto (Rev F p.73). | **confirmado** — corrigir | A/B |
| DC-003 C37, C38 | 4,6 / 4,2 mm | C37.2 GND → via a **6,03 mm**; C38.2 GND → **6,89 mm**; C38.1 +12V_TPS → 11,8 mm. São o condensador de VSNS e o de entrada do U12. | confirmado, menor (redes DC) | B |
| DC-003 C35 | 3,7 mm | Condensador de saída do Recom. | confirmado, menor | B |
| CK-001 CLK, CLK_ADC_ISO | «relógio em camada exterior» | Placa de 4 camadas com plano adjacente a 0,21 mm: microstrip sobre plano é a topologia normal; não há camada interna livre para stripline. | sem acção | B/D |
| IO-001 P1 | «sem filtragem» | P1 é o conector de encaixe na base do PLC (SPI, I²C, 24 V). Os sinais de campo entram por **P2** (lazos 4–20 mA, célula). | sem acção em P1; ver §4 | C |
| IO-002 P2 | «2 pinos GND para 12 sinais» | P2: GND_ADC nos pinos 5 e 14; sinais de campo DC de baixa frequência. | sem acção | B |
| EE-001 | ressonâncias de cavidade 1,18 / 1,67 / 2,36 GHz | Informativo; a placa não tem fontes nessa banda. | informativo | B |

## 3. O que corrigir (por ordem de valor/custo)

1. **Via GND junto a C17.1** (146,40; 95,90) — retorno do desacoplo IOVDD do ADC passa de 4,7 mm a < 1 mm. Uma via 0,6/0,3.
2. **Vias GND de costura junto às vias de MISO_ADC_ISO** (136,0; 98,6) e (136,0; 101,2), do lado GND_ADC da barreira (x ≥ 134,2 para manter a distância ao DGND). São os flancos mais rápidos da placa (saídas do ISO7141).
3. **Via GND junto a C37.2 e C38.2** (147,9; 107,65) e (148,3; 104,75) — desacoplos DC, custo zero.
4. Vias GND junto às vias de sinal de Temp2_AIN9 (150,1; 86,2) e REFIN1+ (152,7; 84,9).
5. Opcional, do relatório anterior: cobre de 5 × 5 mm no cátodo dos TVS D9/D10/D12/D13 com 3 vias (condição da nota 2 do SMBJ36A para o rating de 600 W; baixa a indutância do clamp em ESD).

Nenhuma destas acções move componentes nem toca a barreira. Podem ser aplicadas por script com verificação de clearance, refill e DRC, com o KiCad fechado.

## 4. O que nenhuma ferramenta viu

- **Imunidade** (IEC 61000-4-2/-4/-5/-6 nas entradas de campo por P2) só se verifica em laboratório. A protecção existe (fusível → TVS SMBJ36A → TPS26613 → burden → filtro RC do ADC); o analisador não avalia o caminho nem a tensão de clamp.
- **Emissão conduzida/radiada**: as únicas fontes são o Recom R-78HB (frequência de comutação não consta do PDF Rev 5-2019), o relógio interno do AD7124 (614 kHz) e os flancos do SPI através do ISO7141. Espera-se emissão baixa; a banda a vigiar num pré-ensaio é 30–300 MHz junto a U5 e U1.
- **Cablagem**: a placa liga à base do PLC; o comportamento em cabo depende do conjunto, não desta PCB.

## 5. Limites desta revisão

- Mesma sessão que fez o roteamento e as cirurgias (não é revisão independente).
- O analisador falhou em três pontos que ficam registados para a skill: não reconhece planos de terra formados por várias zonas (SU-001); lê a tensão de saída do MPN do Recom (PD-001); estima 6,19 V para um LDO que dá 12,09 V (PD-001); e o modo `--text` rebenta em cp1252 (corrido com `PYTHONIOENCODING=utf-8`).
- Sem pasta `datasheets/` do projecto (DS-002): as afirmações com datasheet acima vêm dos PDFs em `Documentos_de_Referência` lidos nesta sessão (TPS7A4001 p.5; AD7124-8 Rev F p.73; TPS2661x SLVSFE3C p.36; Würth 824520361 p.1).
- Ficheiros: `emc_analysis/2026-09-23_1028/{schematic,pcb,emc}.json` e `emc_text.txt` na pasta temporária da sessão; medições em `cobertura_gp.py`.

## Adenda 11:05 — plugin actualizado para 2.2.1 e nova corrida

**Plugin:** kicad-happy 2.2.0 (43dad23, 31-08) → **2.2.1** (a6bba1a, `main` de 13-09, que já inclui o lote «v2.3 correctness» por cima da
release 2.2.1 de 01-09). `claude plugin marketplace update kicad-happy` + `claude plugin update kicad-happy@kicad-happy`; scripts corridos
directamente da cache 2.2.1 (o reinício só afecta a skill carregada).

**Placa:** entretanto gravada às **11:03:49** pelo projectista: C17 movido de (146,4; 96,6) para (144,43; 98,6), 36 troços GND_ADC/rede 11
refeitos junto a C17, C37 e D-lado direito. DRC 96 (−2 de serigrafia), 0 por ligar, paridade 0; o toco de 0,25 mm em (160,45; 83,20) continua.

**Achados 2.2.0 (placa 10:16) → 2.2.1 (placa 11:03): 36 → 28, pontuação 0 → 26,5.**

| Mudou | Porquê |
|---|---|
| GP-001 desapareceu em MISO_ADC_ISO, Temp2_AIN9, AIN6, REFIN1+, VSNS | correcção #39 da 2.2.1: o antipad da própria via já não conta como vão do plano — confirma a leitura que eu tinha feito à mão |
| GP-001 CS_ADC error → warning | idem (agora 86 %) |
| DC-003 C17, C37, C35 desapareceram | C17 movido pelo projectista (GND a 1,02 mm); C37.2 agora com via GND a 1,78 mm pelo reroteamento; C35 (3,63 mm) já não passa o limiar |
| PD-001 +5V_REG e +12V_TPS error → **info** «peaks above relevant band» | a 2.2.1 desconta picos fora da banda útil; mas continua a ler Vout = 0,5 V do MPN e 6,186 V para o TPS7A4001 (real 12,09 V) |
| **novo** DC-001 U1 | condensador mais perto do Recom a 5,5 mm (C1); é a «caixa 3» do relatório de roteamento |
| Mantêm-se | SU-001 ×3 (falso positivo, planos multi-zona), GP-005 (intencional), GP-001 nas redes dos conectores THT, RP-001 nas 6 redes, CK-001, IO-001/002, EE-001 |

**Correcção a este relatório (§2, linha DC-003 C17).** C17 (10 µF) **não** é o desacoplo junto ao ADC: a alimentação IOVDD segue
+3.3V_IOVDD → C17 → **C16 (NFM18PC104R1C3D, filtro passante 100 nF)** → Net-(C16-IN) → U6.2, com C16 a 2,76 mm do pino. O elemento «right up
against the device» (AD7124-8 Rev F p.73) é o C16, e o seu ponto fraco é o retorno: os pads GND de C16 têm a via mais próxima a **2,2–3,4 mm**,
enquanto o filtro gémeo do AVDD (C15) tem via a 0,9–1,6 mm. O movimento de C17 melhorou o retorno do 10 µF (1,0 mm) mas deixou o seu pad
+3.3V_IOVDD a 5,5 mm da via de alimentação — irrelevante para um bulk atrás do filtro.

**Lista de acções revista (custo ≈ uma via cada):**
1. Via GND encostada ao pad 2 de **C16** (p. ex. (145,7; 95,9) ou (143,2; 95,9)) — retorno do filtro IOVDD do ADC de 2,2–3,4 mm para < 1 mm.
2. Vias GND de costura junto às vias de MISO_ADC_ISO (136,0; 98,6) e (136,0; 101,2), do lado GND_ADC (x ≥ 134,2).
3. Via GND junto a C38.2 (4,0 mm) e C35.2 (3,6 mm).
4. Vias GND junto às vias de Temp2_AIN9 (150,1; 86,2) e REFIN1+ (152,7; 84,9).
5. Apagar o toco (160,45; 83,20)–(160,45; 82,95).

Ficheiros: `emc_221/2026-09-23_1105/{schematic,pcb,emc}.json`, `emc_text_221.txt`, `legacy_drc_1103.json` (pasta temporária da sessão).

## Correcção 11:30 — a acção 1 (via GND em C16) é retirada

Javier apontou que o footprint `EBM7_V23:NFM0603` já traz os furos de GND. Confirmado no ficheiro da lib e na PCB: o pad 2 (terminal GND do
NFM18PC104) é composto por três peças SMD de 0,4 × 0,6 mm em F.Cu com pasta, uma faixa de 0,4 × 1,8 mm em B.Cu e **três pads thru-hole de
0,2 mm** (em y = −0,7; 0; +0,7, camadas `*.Cu`), com anel de 0,10 mm. O `pcbnew` confirma que o fill GND_ADC de **In1, In2 e B.Cu toca os
três furos** em C16 e em C15: a distância do terminal GND ao plano é zero, não 2,2–3,4 mm. O meu inventário só lista objectos `(via …)` e
ignorou pads PTH — erro de medida meu, registado como lição. A linha DC-003 C17 do §2 e a acção 1 da adenda das 11:05 ficam sem efeito;
a lista passa a começar nas vias de costura do MISO_ADC_ISO.

**O footprint está bem criado?** Electricamente sim, e é deliberado (descrição da lib: «vias do pad 2: furo 0,3 → 0,2 mm, anel 0,05 → 0,10;
a V2.2 fabricada já tinha furos de 0,2»). Contra o land pattern de referência da Murata (NFM18PC104R1C3-0-770-EN p.6, Fig. 3: a 1,0; b 2,2;
c 0,6; d 1,2; e 0,4; f 0,4):

| Item | Murata p.6 | Footprint | Nota |
|---|---|---|---|
| Lands de topo (In/Out) | largura (b−a)/2 = 0,6; extensão exterior 2,2; folga interior 1,0 | 0,6 × 0,6 em x = ±0,8 → 2,2 / 1,0 | igual |
| Lands GND | dois lands 0,4 × 0,4 separados por c = 0,6, extensão d = 1,2 | faixa contínua 0,4 × 1,8 **com pasta ao longo de toda a faixa**, incluindo sob o centro do corpo | difere: cobre e pasta sob o corpo e 0,3 mm para fora de cada lado |
| Furos | não constam (é um substrato de ensaio) | 3 × 0,2 mm, anel 0,10 = `min_via_annular_width` da placa; o do centro fica sob a pasta e sob o corpo | via-em-pad sem tamponar: risco de sucção de solda / vazio; V2.2 foi montada assim |

Recomendação (critério D, não é exigência de datasheet): manter a ligação por furos — é o que dá ao filtro o retorno curto que o AD7124 pede —
mas, numa próxima revisão da lib, retirar a pasta da peça central (y = 0) e do trilho sobre os furos, ou passar os furos para fora do corpo
(y = ±0,9), para o land ficar mais perto da Fig. 3 e sem solda a entrar nos furos. Confirmar com quem montou a V2.2 se houve vazios nesses pads.

## Adenda 12:10 — stencil do NFM18PC (C15/C16 legacy, C29/C31 sem_trilhas) corrigido

**Fonte (A):** Murata NFM18PC104R1C3-0-770 p.16 (aberturas de pasta NFM18PC: GND em dois quadrados 0,4 × 0,4 com vão central 0,4 e
extensão 1,2; sinais 0,6 × 0,6 com 1,0/2,2; espessura 100–150 µm), p.29 (land para refusão: faixa GND 0,4 × 1,5 com três furos
«small diameter thru hole ø0,2–0,3» **sob máscara** — centro e pontas —, janelas expostas só onde há pasta) e p.27 §1-4 (ligar o GND do
chip por via ao plano interno). O fabricante prevê os furos, **nunca dentro da abertura de pasta**.

**O que estava mal:** as peças SMD do GND tinham 0,4 × 0,6 em y = ±0,6 (janela de máscara e pasta 0,3…0,9) e os furos exteriores estavam em
y = ±0,7 — **inteiramente dentro da janela de pasta**: a solda seria sugada pelo furo (vazio no terminal GND, esferas no lado oposto). O furo
central já estava tentado. Na legacy havia ainda uma via 0,6/0,3 livre empilhada sobre o furo exterior de C16 (acrescentada depois das 09:16).

**Correcção aplicada (lib nos dois projectos + 4 instâncias):** janelas GND 0,4 × 0,4 em y = ±0,4 (0,2…0,6, igual à p.16); furos exteriores
em y = ±0,8 com cobre 0,5…1,0 (anel 0,10 na ponta) — dique de máscara de **0,10 mm** entre janela e furo, medido com `pcbnew` nas 4 peças;
furo central inalterado (dique 0,10). Via empilhada removida (redundante com os furos do footprint). Nota: no KiCad o `offset` do furo desloca
o **cobre**, não o furo — a primeira passada deixou o furo em ±0,75 (dique 0,05) e foi refeita.

**DRC:** legacy 96 = 96 antes, 0 por ligar, paridade 0, nenhum item em C15/C16; sem_trilhas 143 = 143 antes (os avisos de courtyard de C31
já existiam). Backups `.antes_nfm_stencil` e `.antes_nfm_stencil2` (PCB e `.kicad_mod`).

**Nota 12:40 (releitura da p.29 ampliada):** a cota 1,5 da Fig. NFM18PC é **entre centros dos furos das pontas** (furos em ±0,75, sob
máscara), não o comprimento da faixa; a faixa de cobre segue até ≈ ±0,88 e o furo central fica sob uma ilha de máscara 0,6 × 0,4. Com ø0,2
em ±0,75 o dique de máscara à janela (0,2…0,6) seria 0,05 mm; o footprint usa furos em ±0,80 e cobre até ±1,0 para um dique de 0,10 mm —
desvio deliberado de 0,05 mm (critério D, registo de máscara). Janelas, pads de sinal e stencil iguais à p.16/p.29. Sem efeito em
diafonia: a faixa GND entre In e Out é a separação prevista do filtro passante; folga cobre GND–sinal 0,3 mm, igual à Murata.

## Correcção 24-09 — procedência da lista de vias (a pedido do Javier: «é o que pede o datasheet?»)

**Nenhum datasheet da pasta pede vias de retorno a uma distância concreta.** O limiar de 1 mm é das regras RP-001 e DC-003 da
ferramenta `kicad-happy:emc` (critério da ferramenta, não do fabricante). O que os datasheets dizem, textual:

- AD7124-8 Rev F p.73 (*Grounding and Layout*): «ensuring that the paths for all return currents are as close as possible to the paths the
  currents took to reach their destinations» — princípio, sem distância; pede também não passar digital sob o ADC, cruzar digital/analógico em
  ângulo recto, alimentação com pistas largas e o 0,1 µF encostado ao chip.
- ISO7141 (SLLSE83F) p.25 (*Layout Guidelines*): «Routing the high-speed traces on the top layer avoids the use of vias … Placing a solid
  ground plane next to the high-speed signal layer … provides an excellent low-inductance path for the return current flow» — a preferência é
  **não ter via** nas linhas rápidas; a via de costura seria paliativo.
- TPS7A4001 (SBVS162B) p.13, §10.1.1: «the ground connection for the output capacitor should connect directly to the GND pin of the device» —
  aplica-se a **C38**; critério diferente de «via a 1 mm», **ainda não medido**.

| Item da lista de 23-09 | Fonte real | Estado |
|---|---|---|
| Vias de costura junto às vias de MISO_ADC_ISO | princípio AD7124 p.73 / ISO7141 p.25; 1 mm é da ferramenta | opcional; SCLK = 1 MHz (Rodrigo, 24-09) → benefício marginal |
| C38 | TPS7A4001 p.13 (GND do C_OUT directo ao pino GND) | único com base em datasheet; medir |
| C35 | nenhuma — e **erro meu**: C35 está no +24V_ADC dos laços, não na saída do Recom | retirado |
| Vias junto a Temp2_AIN9 e REFIN1+ | nenhuma; sinais lentos | retirados |

Nada disto exige nova revisão. Para o roteamento da sem_trilhas valem as regras textuais acima (ISO7141 p.25, AD7124 p.73, TPS7A4001 p.13,
ADR4525 p.35 «reference as close to the load as possible»). O shunt de H1 é só o modelo 3D.

**C38 medido (24-09):** o GND de C38 liga por pista F.Cu de 0,25 mm e 2,66 mm **directamente ao pad térmico (pino 9, GND) do U12**;
o +12V de C38 fica a 2,74 mm do pino OUT. Cumpre TPS7A4001 p.13 («output capacitor … directly to the GND pin»). Melhoria opcional: alargar
essa pista (a mesma secção pede ESL/ESR mínimos). Não há mais nada da lista de vias com base em datasheet.

## ⚠️ Correcção 24-09 — a barreira NÃO mede 1,20 mm

A revisão independente de 24-09 mediu **0,30 mm** cobre-a-cobre entre o domínio PLC e o campo em In1/In2. Re-medido nesta sessão
incluindo os **preenchimentos das zonas** (`barreira_real.py`): F.Cu 1,200 mm; **In1 0,300 mm; In2 0,300 mm; B.Cu 0,400 mm**. O par
crítico é a zona DGND contra a via GND_ADC em (128,20; 116,70) (segunda via de C5.1, presente desde antes da cirurgia de 23-09; C5.1 já
tem via própria em (127,35; 118,70)). Os 1,20 mm que escrevi mediam só pistas e pads, sem zonas — **erro de método meu**. A verificação
«nenhum cobre de campo dentro do contorno DGND» também não apanhou a via, porque ela fica fora do contorno mas a 0,3 mm do seu bordo.
