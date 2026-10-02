# Alteração 2026-10-02 — limitador discreto nos laços 4-20 mA (saem o TPS26613 e o TPS7A4001)

Rama `lacos-limitador-discreto`, sobre `main` 7759409. **Só o esquemático foi alterado**; a PCB não foi tocada e tem de ser
actualizada a partir do esquemático (ver [Para o layout](#para-o-layout)).

Tipos de fonte de cada número: **(A)** folha de dados, com página; **(B)** cálculo ou simulação; **(C)** netlist do projecto;
**(D)** suposição, a confirmar.

## 1. Pedido e porquê

Retirar os quatro protectores TPS26613 (U8–U11) e a fonte de 12 V que os alimenta (U12 TPS7A4001, +12V_TPS, divisor VSNS)
**sem perder o que eles protegiam**. Numa simulação do canal sem protecção (ngspice, 2026-10-02), um transmissor em curto ou a
linha AIN ligada a 24–32 V põe **199–290 mA na burden de 110 Ω (4,4–9,3 W numa 0603 de 0,1 W)**. O F4 de 125 mA demora
segundos a minutos e nem está no caminho quando a tensão vem de fora. Um surto de 1 kV mete **11–19,5 mA** no pino do ADC
(máximo 10 mA, AD7124-8 Rev F p.14). Com o TPS a corrente fica em 25–40 mA (TI SLVSFE3C p.5) **(A, B)**.

Também se analisou ligar o +Vs dos TPS directamente ao +24V_ADC. **Não serve**:
- com o barramento a 32 V, o +24V_ADC chega a ~31,5 V, acima dos 30 V recomendados (SLVSFE3C p.4 e Tabela 10-1 p.35);
- os transitórios do barramento chegam a 53,3 V (clamp do SMA6J33A), acima do máximo absoluto de 32 V do +Vs (p.4).

## 2. Circuito novo (por laço; Q1/Q5/R40/R44 no laço 1)

```
P2.7 AIN1 ──┬── D: Q1 BSP297 (SOT-223) ── S ──┬── R40 18R ──┬── R10 0R ── burden R13 110R ── GND_ADC
            │                G                │             │      (R18 3k3 -> ADC, sem alteração)
          D6 SMBJ36A         ├── R44 100k ── VZ_LIM          │
          a GND_ADC          └── C ── Q5 BC847C ── B ────────┘── E (ao nó do R10)
VZ_LIM (comum aos 4 laços): +24V_ADC ── R48 22k ──┬── D26 BZT52H-C10 (10 V) ── GND_ADC
                                                  └── C50 100nF/50V
```

- **Normal:** a porta está a ~9,3 V e o Q1 conduz por completo. Custa 0,38 V de compliance a 20 mA.
- **Limitação:** quando a corrente chega a ~VBE/18 Ω, o Q5 conduz e puxa a porta: limita a 23,7–39 mA de −40 a 85 °C **(B)**.
- **O zener D26 faz o papel do +Vs do TPS:** mesmo com a burden aberta, o nó da burden não passa de ~8,5 V e entram só
  ~1,4 mA no ADC **(B)**.
- **Sem corte térmico:** numa falha mantida, o Q1–Q4 dissipa todo o calor (ver [Para o layout](#para-o-layout)).

## 3. Peças (verificadas na folha de dados — texto e desenho)

| Ref. | Peça | Verificação |
|---|---|---|
| Q1–Q4 | Infineon **BSP297** (BSP297H6327XTSA1), N-MOSFET 200 V, SOT-223 | **Desenho Rev.2.2 p.1: Gate pin 1, Drain pin 2,4 (aba), Source pin 3.** VGS(th) 0,8–1,8 V; RDS(on) 1,8 Ω máx. a 10 V (p.2). SOA com linha **DC de 1,8 W** a TA 25 °C, 6 cm² (p.4, fig. 3). RthJS 25 K/W; **RthJA 115 K/W com pegada mínima e 70 K/W com 6 cm²** (p.2) |
| Q5–Q8 | Nexperia **BC847C** (BC847C,215), NPN 45 V, SOT23 | **Tabela 3 e desenho, Rev.13 p.2: 1 = B, 2 = E, 3 = C.** hFE 420–800 a 5 V / 2 mA (p.4) |
| D26 | Nexperia **BZT52H-C10** (BZT52H-C10,115), SOD123F | **Tabela 2 e desenho, Rev.7 p.2: 1 = K, 2 = A; a barra marca o cátodo.** ±5 %; 375 mW (p.4) |
| R13–R15, R17 | Vishay **TNPW1206110RBEEA**, 110 Ω 0,1 % 25 ppm/K, 1206 | P70 0,27 W em modo geral (p.2); código B = 0,1 %, E = 25 ppm/K (p.3–4). Antes RG1608 0603 de 0,1 W |
| D6, D7, D8, D11 | Diodes **SMBJ36A-13-F** (DO-214AA) | Era 824500301 (30 V de standoff). Numa falha, a linha AIN fica no +24V_AIN (até 32 V); a regra do painel é standoff ≥ 36 V |
| R40–R43 | 18 Ω 1 % 0603 (RC0603FR-0718RL) | Sensor do limitador; 39 mA → 27 mW **(B)** |
| R44–R47 | 100 kΩ 1 % 0603 (RC0603FR-07100KL) | Porta desde VZ_LIM |
| R48 | 22 kΩ 1 % 0603 (RC0603FR-0722KL) | Polarização do zener; 32 V → 21 mW; transitório de 53 V → 2 mA **(B)** |
| C50 | 100 nF 50 V X7R 0603 (C1608X7R1H104K080AA) | Desacoplamento de VZ_LIM |

Símbolos do BSP297 e do BC847C na biblioteca nova `symbols/EBM7_V23_proyecto11.kicad_sym`, achatados de `Device:Q_NMOS`
e `Device:Q_NPN` do KiCad 10 com a numeração da folha. O footprint `EBM7_V23:SOT-223-3_TabPin2` é uma cópia do KiCad 10:
a aba é o pad 2 (dreno). O `SOT-223-3` do projecto numera a aba como pad 4 e deixá-la-ia sem rede.

Folhas e modelos novos em `Documentos_de_Referência`:

- `Infineon_BSP297_Rev2.2.pdf` e `Infineon_PG-SOT223-4-21_BSP297H6327XTSA1_Rev01.00.pdf`;
- `Nexperia_BC847X_SER_Rev13.pdf`, `Nexperia_BZT52H_SER_Rev7.pdf`, `Vishay_TNPW_e3_28758_Rev2026-04-10.pdf`;
- modelos SPICE: `Infineon_small_signal_200V_PSpice.lib` e `Nexperia_BC847C_SPICE.txt`.

## 4. O que mudou no esquemático (folha 6, `06_lacos.kicad_sch`)

- **Retirados:** U8–U11 (TPS26613), U12 (TPS7A4001), R22–R26, C26, C29, C31, C32, C37, C38, os símbolos +12V_TPS, as
  etiquetas VSNS, os 4 «no connect» do SGOOD e os fios e junções que ficaram soltos.
- **Acrescentados:** Q1–Q8, R40–R48, D26, C50 e as etiquetas `LIM1_G`…`LIM4_G` e `VZ_LIM`.
- **Alterados:**
  - D6/D7/D8/D11 → SMBJ36A, DO-214AA;
  - R13–R15/R17 → TNPW1206, footprint 1206R.
- **C34** (10 µF/100 V no +24V_ADC, antes entrada do U12) **fica**: continua a ser desacoplamento do +24V_ADC.
- **Nota na folha:** «DECISAO 2026-10-02». As notas 1, 5, 8–11, 16 e o cabeçalho «DECISAO 21-09-2026» passam a **históricas**
  (falam do TPS26613/TPS7A4001).

A alteração foi feita por script (`simulacao_limitador_2026-10-02/ferramentas/aplicar_limitador.py`) a partir do ficheiro da
`main`, e não à mão.

## 5. Verificação (portas)

`ferramentas/verificar_limitador.py`, saída em `verificar_saida.txt`. **43 de 43 OK.**

- **Componentes:** saem exactamente os 16 previstos e entram os 19 novos; só mudam valor/footprint os 8 previstos.
- **Partição dos pinos não tocados:** idêntica (94 grupos antes, 94 depois). Nenhuma ligação existente mudou.
- **Redes novas com os membros exactos:**
  - dreno ↔ P2.7/9/11/13 e TVS;
  - fonte = {Qk.S, RS.2, Qn.B};
  - nó do 0R = {Qn.E, RS.1, 0R.2};
  - porta = {Qk.G, Qn.C, RG.1};
  - VZ_LIM = {R44–R47, R48, D26.K, C50}.
- **Redes que desaparecem:** +12V_TPS e VSNS.
- **ERC:** **0 erros**. Avisos: `lib_symbol_issues` 288 → 268 (saem os símbolos do TPS); `isolated_pin_label` 9 e
  `same_local_global_label` 1, sem alteração.
- **Biblioteca e footprint novos:** carregam no `kicad-cli` (`sym export svg`, `fp export svg`).
- **kicad-happy:spice sobre o esquemático novo:** 49/49 «pass». Valida a aritmética do analisador (filtros RC, divisores),
  não o circuito; os transistores entram com modelos genéricos.

## 6. Simulação (ngspice-47, modelos do fabricante)

Infineon `BSP297_L0` (nível 3) e Nexperia `BC847C`. Valores lidos do netlist exportado do esquemático novo. Ambiente do canal
**(D)**: cabo 40 m, 0,25 mm²; transmissor 2 fios = fonte de corrente + 100 nF; carril de 3,3 V só fonte + TL431.

| Caso | Resultado **(B)** |
|---|---|
| Normal, 20 mA, barramento 18 / 24 / 32 V | burden 20,01 mA; tensão no transmissor **14,76** / 20,76 / 28,76 V (sem protecção seria 15,14 V a 18 V) |
| Transmissor em curto ou AIN a 32 V externos, −40 / 27 / 60 / 85 °C | **39,2 / 31,1 / 26,9 / 23,7 mA**; burden ≤ 169 mW; Q1 0,67–1,06 W |
| Idem, burden aberta | nó da burden 8,4–8,5 V; 1,4 mA para o ADC (pino a 3,8–4,0 V: mais de AVDD+0,3 V com corrente muito abaixo dos 10 mA) |
| Curto com o modelo Infineon **com nós térmicos** (RthCA 90 K/W) | Tj 72,6 / 119,9 / **142,1 °C** a −40 / 27 / 60 °C; confirma a conta Tj = Ta + P·RthJA |
| Surto 1,2/50 1 kV directo em P2.7 (sem Baseboard), + / − | Vds máx. 72,6 / 42,2 V (BSP297: 200 V); energia na burden **0,017 / 0,094 mJ** (sem protecção 0,81 / 3,06 mJ); ADC −0,41…+1,84 V |

Os netlists de cada caso, os modelos e os resultados estão em `simulacao_limitador_2026-10-02/` (ver o README dessa pasta).
O modelo completo da Infineon com nós térmicos **não converge** em regime normal e a 85 °C. Por isso a tabela usa o `BSP297_L0`
com Tj calculado, e o modelo térmico entra só como contraste.

## Para o layout

1. **Actualizar a PCB a partir do esquemático.**
   - Saem U8–U12, R22–R26, C26, C29, C31, C32, C37 e C38.
   - Entram 4× SOT-223, 4× SOT-23, 9× 0603 R, 1× SOD-123F e 1× 0603 C.
   - D6/D7/D8/D11 passam de SMA (DO-214) a **SMB (DO-214AA)**: são maiores.
   - R13–R15/R17 passam de 0603 a **1206**.
2. **Cobre para o Q1–Q4: é a condição mais importante.** Sem corte térmico, numa falha mantida a 32 V cada BSP297 dissipa
   0,67–1,06 W.
   - Com pegada mínima (115 K/W), Tj = 146 °C a 60 °C e **162 °C a 85 °C**, acima dos 150 °C.
   - É preciso **RthJA ≲ 90 K/W por transistor**; 6 cm² dão 70 K/W (Rev.2.2 p.2).
   - A aba é o **dreno, ou seja a rede AINk (linha de campo)**: o cobre de dissipação fica nessa rede. Respeitar as folgas da
     classe e preferir camadas internas com vias.
3. **Q5–Q8 longe de Q1–Q4.** Aquecidos juntos, o VBE do NPN desce e o limite cai abaixo de 21 mA, e uma falha passaria a
   ler-se como medida válida.
4. Verificar o roteamento em sessão independente (`2shw-pcb:check-roteamento`), como já está nos pendentes.

## Firmware

- Leitura **≥ 21 mA (NAMUR NE43) = falha ou curto no laço**. O limite fica sempre ≥ 23,7 mA (85 °C), por isso um curto
  nunca se lê como medida válida.
- O critério anterior de 24 mA não servia: a 85 °C o limite é 23,7 mA.

## O que se perde em relação ao TPS26613

- corte térmico e rearme automático integrados;
- protecção bipolar;
- modo «loop power» (teste do laço sem alimentação);
- SGOOD (não era usado);
- o «2× no arranque» dos transmissores.

Os limites passam a depender do VBE do NPN (−2 mV/K) em vez de valores garantidos na folha. **Confirmar que os transmissores
usados arrancam com ≤ ~23 mA a quente.**

## Pendentes

- **Ensaio de bancada:**
  - falha mantida a 32 V durante minutos à temperatura máxima do quadro, medindo a temperatura do Q1–Q4;
  - surto IEC 61000-4-5 (a norma foi aplicada de memória nas simulações);
  - arranque dos transmissores reais.
- **Modelos genéricos:** zener e TVS (SMBJ36A) entram com modelos genéricos na simulação.
- **BOM, pacote de fabricação e PCB:** por regenerar.
- **Variante MOSFET (`EBM7-2608-V23-MOSFET`):** não alterada. Lá os TPS também protegem o modo 0–10 V.
- **Revisão independente** desta alteração antes de ir para `main`.
- **Folha de dados do SMBJ36A-13-F:** continua a faltar no repositório (já estava nos pendentes do README).
