# Verificação de aplicação — pistas debaixo de D14 (BAV199, clamp de AIN1_ADC), EBM7 V2.3 legacy

**Pergunta do projectista (22-09-2026):** as pistas que passam debaixo de D14 podem ficar ou têm de mudar de sítio?
**Ficheiro:** `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_pcb`, mtime 2026-09-22 18:22:59. Só leitura.
**Skill:** `2shw-pcb:verificar-aplicacao-datasheet` (mesma sessão que editou a placa hoje: limitação declarada).

## 1. O que há debaixo de D14 (courtyard 154,05–157,97 × 87,17–90,63; SOT-23 em F.Cu, rot −90)

| camada | rede | o quê |
|---|---|---|
| F.Cu | GND_ADC, +3.3V_ANA, AIN1_ADC | os próprios acessos aos três pads (pad 1 GND, pad 2 +3.3V_ANA com via em 154,85;86,95, pad 3 AIN1_ADC) |
| **B.Cu** | **+3.3V_ANA, 0,40 mm** | **o bus que alimenta a coluna de clamps D14–D17 (x = 154,85, de y 86,85 a 112,95): passa por baixo de D14, 0,45 mm em planta do pad 1** |
| F.Cu | AIN5_ADC_Load_Cell+ | toco solto de 0,7 mm (157,85;87,0)–(157,35;86,5), a 0,74 mm do pad 1 — resto de roteamento |
| In1.Cu, In2.Cu | GND_ADC | planos contínuos sob toda a caixa |

Nó protegido: `AIN1_ADC` = U6.8, R18 (3k3), C27 (100 nF), D14.3. O bus de B.Cu alimenta **só** D14, D15, D16, D17, D22, D24, D25.

## 2. Datasheets usados (grep na sessão)

- onsemi **BAV199LT1/D Rev 12** (Aug 2024), 6 páginas: p.2 IR ≤ 5,0 nA @ 70 V (25 °C) / 80 nA @ 150 °C por díodo; CD ≤ 2,0 pF. **Não tem secção de layout** (p.6 é texto legal).
- Analog Devices **AD7124-8 Rev F**, p.73 *Grounding and Layout*: «Avoid running digital lines under the device …», «Avoid crossover of digital and analog signals», «Run traces on opposite sides of the board at right angles to each other» (técnica de 2 camadas: «the component side of the board is dedicated to ground planes»).
- TI **TPS2661x SLVSFE3C §11.1** (espírito): sinais sensíveis afastados da corrente de laço.

## 3. Tabela (avaliada por `tabela.py`, não escrita à mão)

| CI | fonte (§/tabela/nota, pág.) | fórmula | valores usados | resultado | veredito |
|---|---|---|---|---|---|
| D14 BAV199 / U6 AD7124-8 | AD7124-8 Rev F p.73: 'Avoid running digital lines under the device ... Avoid crossover of digital and analog signals' | `distancia minima cobre digital (SPI/CS/CLK/ISO) <-> no AIN1_ADC (pads e pistas, qualquer camada) >= 2 mm` | d_dig=4.040 nenhuma rede digital debaixo de D14; a mais perto e CS_ADC_ISO a 4,04 mm de U6.8 | d_dig = 4.040 | cumpre |
| D14 / U6 | AD7124-8 Rev F p.73: '... allows the analog ground plane to run under the AD7124-8 to prevent noise coupling' | `planos GND_ADC continuos debaixo de D14 (In1.Cu, In2.Cu) >= 1` | planos=2.000 | planos = 2.000 | cumpre |
| D14 / U6 | AD7124-8 Rev F p.73: 'Run traces on opposite sides of the board at right angles to each other' (tecnica de 2 camadas: 'component side ... ground planes') | `bus +3.3V_ANA em B.Cu (x=154,85) corre em planta sob pistas AIN1 de F.Cu: comprimento paralelo L; aceite se ha >= 1 plano GND entre as camadas` | L_par=4.530, planos=2.000 em 4 camadas os dois planos internos fazem o que a regra pede para 2 camadas | L_par = 4.530 ; planos = 2.000 | cumpre |
| D14 BAV199 | BAV199LT1/D Rev 12 p.2: IR <= 5,0 nA (VR=70 V, 25 C), <= 80 nA (TJ=150 C), por diodo | `corrente normal no bus +3.3V_ANA debaixo de D14 = so a fuga dos 7 BAV199 que alimenta: 7 x IR(150 C) <= 1 uA -> pista sem di/dt` | n=7.000, IR_150=8e-08 | n*IR_150*1e9 = 560.000 | cumpre |
| D14 BAV199 | BAV199LT1/D Rev 12 p.2: CD <= 2,0 pF (VR=0, 1 MHz) | `capacidade que o clamp acrescenta ao no AIN1 vs C27 do filtro: CD/C27 <= 0,1 %` | CD=2e-12, C27=1e-07 | CD/C27*100 = 0.002 | cumpre |
| AIN1_ADC (F.Cu) | criterio do projecto: cobre de outra rede na mesma camada a >= 0,30 mm do no analogico (DRC exige 0,15) | `distancia minima na mesma camada: +5V_ADC (rail DC) a d5, ao longo de L5 em paralelo` | d5=0.347, L5=8.500 rail DC; acoplamento ~0,1 pF contra 100 nF de C27: sem efeito; melhoravel, nao defeito | d5 = 0.347 ; L5 = 8.500 | cumpre |
| AIN1_ADC (F.Cu) | TPS2661x SLVSFE3C 11.1 (espirito): sinais sensiveis afastados da corrente de laco; criterio >= 2 mm na mesma camada | `distancia minima de redes de laco (AINx de campo, +24V_AINx, BRD, IEXC, Load_Cell) ao no AIN1_ADC` | d_loop=8.020 | d_loop = 8.020 | cumpre |
| D14 (housekeeping) | DRC track_dangling: toco AIN5_ADC_Load_Cell+ (157,85;87,0)-(157,35;86,5) dentro do courtyard de D14 | `tocos de outra rede dentro do courtyard de D14 == 0` | tocos=1.000 resto de roteamento (I3 do relatorio): apagar | tocos = 1.000 | **FALHA** |
| D14 BAV199 | BAV199LT1/D Rev 12: 6 paginas; nao tem seccao de layout (p.6 e texto legal) -> 'not in this PDF' | `requisitos de layout do fabricante do diodo: nenhum` | req=0 | req = 0 | cumpre |

cumpre: 8 · FALHA: 1 · falta dado: 0

## 4. Teste de uma multiplicação (acoplamento no nó AIN1)

- Bus B.Cu sob D14: corrente normal = fuga de 7 BAV199 ≤ 7 × 80 nA = **0,56 µA** (pior caso a 150 °C), DC → nenhum di/dt a acoplar. Em falta de campo o clamp conduz mA para +3.3V_ANA, mas aí o dano seria o próprio evento, não a pista.
- Dois planos GND_ADC (In1, In2) entre F.Cu e B.Cu: a capacidade F.Cu↔B.Cu através de dois planos é desprezável; a regra «right angles» do AD7124 é para 2 camadas e aqui está mais do que cumprida.
- +5V_ADC em F.Cu a 0,35 mm da pista AIN1 ao longo de ~8,5 mm: ≈ 0,1 pF de acoplamento contra os 100 nF de C27 (fc = 1/(2π·3k3·100n) = 482 Hz) → razão 1e-6. Rail DC. Sem efeito medível.

## 5. Veredito

**As pistas debaixo de D14 podem ficar.** O único item que falha é o toco solto de `AIN5_ADC_Load_Cell+` dentro do courtyard de D14, que é lixo de roteamento (I3 do relatório das 17:01) e se apaga.

## 6. O que nenhuma ferramenta viu

ERC/DRC não distinguem «pista debaixo de um clamp analógico» de qualquer outra pista; o DRC só mediria clearance na mesma camada. A pergunta só se responde lendo quem alimenta o bus (só clamps → sem corrente) e quantos planos há entre as camadas (dois) — nenhum analisador faz essa conta.

## 7. Limites desta verificação

Não se verificou a continuidade real dos enchimentos de In1/In2 sob D14 (usou-se o contorno das zonas, que cobre a caixa e não tem keepout nem zona de outra rede ali); não se mediu ruído. Mesma sessão que editou a placa hoje: repetir em sessão independente antes do portão.
