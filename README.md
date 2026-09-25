# IC2S EBM7-2608 V2.3 — variante fixa 4-20 mA

Placa de extensão da família IC2S (Extension Board Model 7) com **quatro entradas 4-20 mA**, **uma entrada de célula de
carga** e **um NTC de junta fria**, medidos por um ADC sigma-delta de 24 bits (**AD7124-8**). Encaixa por baixo na base board:
**P1** é o barramento (alimentação 24 V e 5 V, SPI do processador) e **P2** leva os sinais de campo.

Esta é a variante **fixa**: as quatro entradas são só 4-20 mA. A variante com selecção 0-10 V / 4-20 mA por MOSFET vive noutro
projecto (`EBM7-2608-V23_configuravel`).

Projecto KiCad 10 (testado em 10.0.5). Abrir
`Desenvolvimento_IC2S-EBM7-2608-V2.3-Fixo420/Projeto_IC2S-EBM7-2608-V2.3-Fixo420/IC2S-EBM7-2608-V2.3-Fixo420.kicad_pro`.

Identificador desta versão: **`IC2S-EBM7-2608-V2.3-Fixo420`** (produto IC2S-EBM7-2608, versão 2.3, variante fixa 4-20 mA).

---

## Estado (25-09-2026)

| Verificação | Resultado |
|---|---|
| DRC (`kicad-cli pcb drc --severity-all --schematic-parity`) | **0 erros**, 62 avisos (todos de serigrafia) |
| Ligações por fazer | 0 |
| Paridade esquemático ↔ PCB | 0 |
| ERC | 0 erros |

Não está pronta para fabricar: ver [Pendentes](#pendentes).

---

## Estrutura do repositório

Segue o padrão de pastas dos produtos da 2Solve (o mesmo de `Produtos/Axcel_Sensor`): uma pasta por versão, e dentro dela
projecto, documentos e ficheiros de fabricação, sempre com o identificador no nome.

```
Desenvolvimento_IC2S-EBM7-2608-V2.3-Fixo420/
├── Projeto_IC2S-EBM7-2608-V2.3-Fixo420/
│   ├── IC2S-EBM7-2608-V2.3-Fixo420.kicad_pro / .kicad_sch / .kicad_pcb / .kicad_dru
│   ├── 01_conectores … 08_ntc.kicad_sch          (as oito folhas)
│   ├── footprints/EBM7_V23.pretty, symbols/       (bibliotecas locais, por ${KIPRJMOD})
│   ├── Documentos_de_Referência-IC2S-EBM7-2608-V2.3-Fixo420/   (datasheets das peças desta placa)
│   └── Outputs/drc_report.json
├── Documentos_IC2S-EBM7-2608-V2.3-Fixo420/
│   ├── 00-Especificações_Técnicas_…/   verificações, relatórios, perguntas ao firmware
│   ├── 01-Esquemáticos_…/              Schematic-….pdf, ….step, …-Top_View.pdf, …-Bottom_View.pdf
│   ├── 02-Pinout_…/                    (vazio)
│   └── 03-Diagrama_Blocos_…/           (vazio)
└── Arquivos_Fabricação_IC2S-EBM7-2608-V2.3-Fixo420/
    ├── 00-Gerbers_…/                   ….GTL .G1 .G2 .GBL .GTS .GBS .GTO .GBO .Outline, ….TXT (furação), .gbrjob, .zip
    ├── 01-BOM_List_…/                  …-Preliminar.xlsx
    ├── 02-Pick-and-Place_…/            …-Pick-and-Place-Preliminar.csv
    └── 03-Stencil_…/                   ….GTP (pasta topo), ….GBP (pasta base)
```

Os ficheiros de fabricação e as vistas foram **gerados pelo `kicad-cli` a partir do projecto** a 25-09-2026 e são
**preliminares**: a placa ainda não passou a revisão independente do roteamento. Não enviar a fabricar sem essa revisão.

Os documentos em `00-Especificações_Técnicas` são registos da data em que foram escritos e citam os nomes antigos dos
ficheiros (`IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.*`), anteriores à arrumação de 25-09-2026.

**Onde está cada decisão:** cada folha do esquemático tem um bloco de texto «DECISOES DESTA FOLHA» com notas numeradas. Neste
README cita-se sempre como *folha N, nota M*. A nota é a fonte; este documento resume.

---

## Como funciona, bloco a bloco

### Folha 1 — Conectores

- **P1** (Harwin M20-7822046, fila única de 20) liga à base board. Traz +24 V (P1.20), a massa GND_ADC (P1.19), +5 V, DGND e
  o SPI. Os pinos que esta placa não usa (USB, CS_DAC, I²C…) terminam aqui por desenho da família (nota 1).
- P1.20 leva ~116 mA em regime e ~180 mA em falha, 6 % do que o contacto aguenta (nota 2).
- **P2** (M20-7821446) é o conector de campo: excitação e sinais da célula, e os quatro laços (nota 5). Pinos 6-13 em pares
  `+24V_AINn` / `AINn`.

### Folha 2 — Entrada de 24 V e protecção

Caminho: P1.20 → fusíveis **F1/F2** → díodo de entrada → **+24V_ADC**, que alimenta tudo o que é analógico.

- **F1, F2 = Eaton CC12H750MA (time-lag)**: o I²t de fusão (150 mA²s) fica ~44-90× acima do arranque. O fusível anterior (FF,
  1,5 mA²s) abria no próprio arranque dos condensadores — um dos mecanismos da avaria em campo da V2.2 (notas 1, 2 e 10).
- **D1 = SMA6J33A-Q** (TVS de entrada): standoff 33 V, **clamp real 53,3 V** a 11,3 A — não os 40,6 V que dizia a biblioteca
  (nota 3).
- **C1/C13 = 10 µF / 100 V em 1210**: com o clamp a 53,3 V, um cerâmico de 50 V ficaria acima do nominal (notas 4 e 12).
- **Ramo único +24V_ADC**: as duas ramas antigas eram iguais e saíram (nota 11).
- **Massas:** desde 24-09-2026 **GND_24V e GND_ADC são a mesma rede**. O net-tie que as unia (R1/R200) saiu (nota 7). Motivo:
  as duas são o mesmo domínio a montante; quem isola a lógica do processador é a MainBoard (conversor SCW12B-05), não esta placa.

### Folha 3 — Alimentação

Cadeia analógica: +24V → **U1** (Recom R-78HB5.0-0.5L, conversor 24→5 V) → FB1 → **+5V_ADC** → **U3** (SPX3819) → **+3.3V_ANA**.
A alimentação do lado do PLC (U2) está desenhada na folha 4, junto ao isolador que alimenta.

- O GND do U1 é GND_ADC: o +5V_ADC é a referência ratiométrica da célula (nota 2).
- O U1 não aceita ligação a quente (hot-plug) — aviso para o manual (nota 3).
- **Pré-carga do U1** (nota 13 e adenda de 15-09): o R-78HB só tem exactidão e regulação especificadas acima de ~10 % de carga;
  a placa sozinha fica em 1,6-6,8 %. Há posições para duas resistências de 220 R (0 / 22,7 / 45,5 mA); **a decisão faz-se na
  bancada**.
- **U4 = TL431B** grampeia o +3.3V_ANA a ~3,6 V (divisor 4k42 / 10k). É o sítio para onde os díodos de protecção das entradas
  despejam a corrente de um surto; sem ele o SPX3819, que só fornece corrente, deixava o rail subir até ~10 V e levava o ADC
  e a referência. Corrente real estimada 12-23 mA, contra 100 mA recomendados (nota 14, em que o componente aparece como U14).

### Folha 4 — Barreira digital

- **Alimentação do lado PLC:** +5 V do P1 → **U2** (MCP1824) → **+3.3V** (massa DGND), com C6/C8/C9 e os pontos de teste
  T3 (DGND) e T5 (+3.3V). Alimenta o lado 1 do isolador. Passou da folha 3 para esta em 25-09-2026, só no desenho
  (as ligações não mudaram); as notas que falam dela continuam na folha 3.
- **U5 = ISO7141** passa o SPI entre o lado do PLC (DGND) e o lado analógico (GND_ADC): 3 canais de ida (MOSI, CLK, CS) e 1 de
  volta (MISO), sempre habilitado (notas 3 e 4).
- **Não é isolamento de segurança nesta placa** (nota 1): os 2500 Vrms do ISO7141 exigiriam 3,7 mm de distância cobre-a-cobre e
  o PCB tem ~1 mm. Faz **separação de ruído** entre a lógica e a medida. Para um dia declarar isolamento: ≥ 3,7 mm ao longo da
  barreira (nota 5).
- **No PCB a barreira é física:** DGND e GND_ADC são zonas separadas nas camadas internas e em baixo. O `.kicad_dru` exige
  **1,0 mm** entre as redes do lado PLC (classe `DIGSIDE`) e o resto; há rule areas sem cobre debaixo do ISO7141
  (`keepout_barreira_ISO7141`) e junto ao P1 (`keepout_barreira_P1`, reposto a 25-09).
- Firmware: no arranque, reset do porto série do ADC (64 SCLK com DIN = 1), porque o CS pode oscilar na rampa de alimentação.

### Folha 5 — ADC

- **U6 = AD7124-8**, alimentado por +3.3V_ANA (AVDD, por um filtro passante NFM) e +3.3V_IOVDD (nota 4).
- **Referência dos laços: U7 = ADR4525 (2,5 V) no REFIN2**, por um único 0 Ω. Na V2.2 três 0 Ω punham 5 V nesse pino, acima do
  máximo absoluto de 3,6 V, em todas as placas (nota 1).
- **Célula ratiométrica no REFIN1** = metade da tensão de excitação (nota 2; folha 7, nota 10).
- SYNC com pull-up de 10k (o ADC não tem pull-up interno e com SYNC em baixo fica em reset) (nota 5).
- **Mapa de canais nesta placa:** AIN1 ← AIN4_ADC, AIN2 ← AIN3_ADC, AIN3 ← AIN2_ADC, AIN4 ← AIN1_ADC, AIN5/AIN6 = célula +/−,
  AIN8/AIN9 = NTC. O cruzamento dos laços é herdado da V2.2 e foi mantido para não trocar canais no firmware (folha 6, nota 4).
- Firmware (notas 8 e 9): REF_EN = 1; buffers de entrada ligados; REF_BUFP = REF_BUFM = 0 nos setups com REFIN2.
  As perguntas abertas ao firmware estão em `perguntas_firmware_EBM7_V23L_2026-09-24.md`.

### Folha 6 — Laços 4-20 mA (×4)

Cadeia por canal, do borne ao ADC: **P2** → TVS **SMBJ36A** → fusível **F3-F6** → protector **TPS26613** (U8-U11) →
**burden 110 Ω 0,1 %** → ferrite → RC anti-aliasing → clamps **BAV199** para +3.3V_ANA → ADC.

- **Burden 110 Ω** (decisão de 21-09-2026, na caixa de texto da folha): 2,20 V a 20 mA, fim de escala do ADC (2,5 V) a 22,7 mA.
  Cumpre a nota (2) da Tabela 8-2 do TPS26613 (SLVSFE3C p.20): 4,46 V > 2,20 V. Os 409 Ω da V2.2 davam 8,18 V e violavam-na.
  **A constante do firmware muda de 6,25 para 9,09 mA/V.** MPN: Susumu RG1608P-111-B-T5.
- **TPS26613** limita a corrente a ~32 mA e desliga em sobretensão; aguenta um curto no cabo de campo (nota 8).
  O seu +Vs vem de **U12 = TPS7A4001** a 12 V, e não dos 24 V: o máximo de +Vs é 32 V e o TVS de entrada grampeia a 53,3 V
  (notas 9 e 16). Um só divisor VSNS para os quatro (nota 11).
- **F3-F6 = Schurter 3413.0006.22 (125 mA)** desde 25-09-2026 (nota 1). É **mitigação, não correcção**: aguenta o arranque de um
  sensor a 3 fios e surtos moderados, mas um surto forte ainda o abre. A correcção completa (díodo em série entre o fusível e o
  TVS) está só na variante configurável.
- **BAV199** em vez de BAT54S: fuga 5 nA em vez de 2 µA (nota 15).
- **U12 (TPS7A4001):** footprint corrigido a 25-09 para o land pattern da TI (SBVS162B p.22); os pads NC 3/6/7 ficam a 0,20 mm,
  com excepção própria no `.kicad_dru`. O condensador de entrada **C34 passou a 10 µF / 100 V em 1210**
  (GRM32EC72A106ME05L): o datasheet pede > 1 µF efectivo junto ao pino, e a 32 V um 0805 de 100 V dá ~0,64 µF.

### Folha 7 — Célula de carga

- **H1 (jumper 2×3)** escolhe a tensão de excitação: 1-2 = 2,5 V (U13, LDO), **3-4 = 5 V (omissão)**, 5-6 = 3,3 V (nota 15).
- Caminho: H1 → **D23** (Schottky RB162MM-60) → **R30 68 Ω 1 W** → P2.2 → ponte. O D23 impede que o clamp do campo volte
  para os rails; queda típica ~0,27 V a 11 mA e 25 °C (curva VF-IF do datasheet ROHM). O R30 passou a 1 W porque um curto de
  campo a 5 V dissipa 0,33 W (nota 16).
- TVS no campo (D8/D9 e D10), resistências de entrada 1k3 0,1 % e clamps BAV199 (notas 3, 4 e 12).
- **Medida ratiométrica:** REFIN1 = excitação/2 por um divisor 10k/10k casado; com REF_BUFP = 1 **sempre** (nota 10).
- Células aceites: 1-3 mV/V, 120-1000 Ω (nota 5).

### Folha 8 — NTC

- **Função:** compensação de **junta fria** para termopar; nunca usado em campo até hoje (nota 1).
- Divisor excitado pelo REFOUT do ADC, leitura diferencial em AIN8/AIN9 (notas 2 a 4). Com R21 = 22k a leitura fica dentro da
  gama dos buffers em −40…+85 °C (nota 7).

---

## Placa (PCB)

- 60 × 60 mm, 4 camadas. **F.Cu** sinal · **In1.Cu** e **In2.Cu** planos de massa partidos (DGND | GND_ADC), sem pistas ·
  **B.Cu** sinal e enchimento de massa.
- P1 e P2 montam em baixo (encaixe na base board).
- Classes de rede no `.kicad_pro`: Default, Analog, Digital, Loop, Power5, Power12, Power24 e `DIGSIDE` (auxiliar, só para a
  regra da barreira).

---

## Alterações de 24-25/09/2026

| Data | O quê | Porquê |
|---|---|---|
| 24-09 | GND_24V fundido em GND_ADC; R1 removido; D1 retorna a GND_ADC por via própria | mesmo domínio a montante |
| 25-09 | F3-F6 de 50 mA para 125 mA (3413.0006.22) | mitigar a abertura em surtos moderados e no arranque de sensores |
| 25-09 | Footprint do U12 (TPS7A4001) conforme SBVS162B p.22; regra dos pads NC | DRC limpo sem mentir sobre o land pattern |
| 25-09 | MPN dos burdens 110 Ω: RG1608P-111-B-T5 | faltava MPN |
| 25-09 | C34 → 10 µF / 100 V 1210 | CIN efectivo do TPS7A4001 |
| 25-09 | `keepout_barreira_P1` reposto | tinha desaparecido da placa |
| 25-09 | U2 (MCP1824) e C6/C8/C9/T3/T5 desenhados na folha 4 em vez da 3 | agrupar o lado PLC junto ao isolador; netlist igual |

---

## Notas do esquemático desactualizadas

Algumas notas foram escritas para outra revisão ou para a variante configurável e **não descrevem esta placa**. Até serem
corrigidas, vale o circuito:

- **Folha 5, nota 10** e **folha 6, notas 12-14** («MODO DUPLO», MOSFETs Q1-Q4, divisor 40k2/10k, 0-10 V): esta placa **não
  tem MOSFETs** nem selecção de modo. O mapa de canais correcto está na folha 5 acima.
- **Folha 6, caixa «DECISAO 21-09»**: fala em R10/R11/R12/R16 e R13/R14/R15/R17 — é a que vale para esta placa.
- **Referências de outras versões:** as notas dizem U3 = K78U05 (hoje **U1 = R-78HB5.0**), U14 = TL431 (hoje **U4**),
  U15 = TPS7A4001 (hoje **U12**), D200 = TVS de entrada (hoje **D1**), D31 = Schottky da excitação (hoje **D23**).
- **Folha 7, nota 11**: diz TPS7A2025 para o U13; a peça montada é o **LP5907MFX-2.5**.

---

## Documentos

Estão em `Desenvolvimento_…/Documentos_…/00-Especificações_Técnicas_IC2S-EBM7-2608-V2.3-Fixo420/`.

| Ficheiro | Conteúdo |
|---|---|
| `verificacao_aplicacao_TPS26613_V23L.md` | fórmulas e notas do datasheet do TPS26613 com os valores da BOM |
| `verificacao_aplicacao_AD7124_V23L_2026-09-24.md` | idem para o AD7124-8 (47 linhas avaliadas) |
| `verificacao_aplicacao_D14_pistas_V23L.md` | pistas debaixo do clamp D14 |
| `relatorio_roteamento_EBM7_V23L_2026-09-22.md` | revisão do roteamento a 22-09 |
| `relatorio_emc_EBM7_V23L_2026-09-23.md` | pré-conformidade EMC (CISPR 32 classe A) |
| `comparacao_BOM_V22_V23L_2026-09-23.md` | o que mudou na BOM desde a V2.2 fabricada |
| `perguntas_firmware_EBM7_V23L_2026-09-24.md` | perguntas abertas à equipa de firmware |
| `PROMPT_revisao_independente_V23L.md` | prompt para uma revisão independente em sessão nova |

---

## Pendentes

- Serigrafia: 62 avisos, legendas do H1, texto «5V» fora do contorno.
- Reescrever e assinar o requisito RF5 do escopo com a barreira real (DGND ↔ GND_ADC).
- Corrigir as notas desactualizadas listadas acima.
- Decidir a pré-carga do U1 na bancada.
- BOM final: a `…-Preliminar.xlsx` tem 57 linhas, 137 peças, 1 DNP (R8) e 136 a montar.
- Pick-and-place: o CSV tem 147 linhas, mais 11 do que as peças a montar — os 8 pontos de teste (T1-T8, `TestPad_Via`) e os
  3 fiduciais. Marcar esses footprints como «excluir dos ficheiros de posição» na placa antes de enviar à montadora.
- Datasheets que faltam em `Documentos_de_Referência`: SMBJ36A-13-F (Diodes), MBR1H100SFT3G (onsemi), BLM18PG471SN1D
  (Murata), LED KG EELP41.22, TDK C3216X5R1H106K, e as resistências genéricas (Yageo RC0603, Panasonic ERJ).
- Verificação do roteamento (`2shw-pcb:check-roteamento`) em **sessão independente**, antes de fabricar.
- O mecanismo da avaria em campo da V2.2 (família 2) **não foi medido** (medição G8 com osciloscópio). As protecções desta
  versão são correctas por si, mas não há prova de que resolvem essa avaria.
