# Relatório de roteamento — EBM7 V2.3 legacy (4-20 mA), estado de 22-09-2026 17:01

**Ficheiro lido:** `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_pcb`, mtime 2026-09-22 17:01:53
(149 footprints, 655 segmentos, 103 vias, 14 zonas). Revisão **só de leitura**; nada foi alterado na placa.

**Independência (declarada):** esta sessão alterou hoje o H1, os 0R selectores, o R30 e a nota da folha 07.
O roteamento é do projectista. O verificador é o mesmo modelo/sessão: **não** cumpre a regra «sessão limpa,
modelo diferente» da `2shw-pcb:check-roteamento`. Vale como pré-revisão; a revisão de portão deve correr em sessão nova.

**Métodos:** `kicad-cli pcb drc --schematic-parity --severity-all` sobre o ficheiro e sobre uma **cópia com zonas
reenchidas** (mesmos números: o que está por ligar é real, não relleno velho); DRC pelo servidor MCP KiCad
(`run_drc`): 102 violações / 38 por ligar / 1 courtyard — **coincide**; medições de geometria por script sobre o texto
do ficheiro (distâncias pad-condensador, barreira, larguras, rule areas, serigrafia); datasheets da pasta de referência.

## Veredito: **NÃO-LIMPO — 1 bloqueante**, 4 importantes, 7 menores

### BLOQUEANTE

**B1 — Barreira de isolação furada por placement: FB1, C7 e C5 estão do lado PLC.**
A placa separa dois domínios: lado PLC (`DGND`, `+5V`, `+3.3V`, SPI de P1 até U5 pinos 1-8) e lado de campo
(`GND_ADC` e tudo o resto). As zonas `DGND_*` chegam a x = 132,5 mm entre y = 110 e 122; as `GND_ADC_*` começam em
133,0: barreira de 0,5 mm nas zonas. Mas **FB1 (129,9; 119,1), C7 (129,2; 116,2) e C5 (128,2; 118,8)**, todos da rede de
campo `+5V_REG`/`+5V_ADC`, estão colocados dentro dessa região, e a pista `+5V_ADC` que os liga a U3 corre a x 129,9-134.
Resultado medido: **pista `+3.3V` (lado PLC) a 0,300 mm da pista `+5V_ADC` (lado de campo), na mesma camada F.Cu**, em
(130,8-131,8; 115,0-115,7). São três pares a 0,300 e dois a 0,449 mm. O ISO7141 dá 3,7 mm de creepage no encapsulado
(SLLSE83F p.17); 0,3 mm na superfície anula a barreira. **Correcção:** mover FB1, C7 e C5 para x ≥ 134 (junto a U3, que
está em 135,3; 115,45) e rotear `+5V_REG → FB1 → C7 → U3.1` inteiramente do lado de campo; manter U2/C6/C8 e a pista
`+3.3V` à esquerda de x ≈ 131. Depois medir de novo: nenhuma pista/pad dos dois domínios a menos do que as zonas (0,5 mm).

### IMPORTANTE

**I1 — 24 pads de `GND_ADC` sem ligação ao plano** (confirmado com zonas reenchidas): C14, C15.2, C20, C22, C23, U7.4,
R29, R37, C39, C43, C44, C47, D6, D7, D9, D10, D12, D13, D19, D20, D21, D22, D24, D25, U8.1/3, U9.1. Não há pour em F.Cu:
cada um precisa de via para In1/B.Cu ou pista curta até uma via. Prioridade aos desacoplos do U6 (C14, C15, C20) e da
referência (C22, C23, U7.4).

**I2 — Recom U1: condensadores longe dos pinos.** `+5V_REG` pin 3 → C3 22 µF a 11,1 mm, C4 100 nF a 12,3 mm, C5 a 21,6 mm;
`+24V_REG` pin 1 → C1 a 8,4 mm. O datasheet (REV 5/2019 p.6) pede os externos «fitted close to the converter pins».
Aproximar C3/C4 do pino 3 e C1 do pino 1 (o Recom comuta a 120-800 kHz).

**I3 — Restos de roteamento que enganam a conectividade:** pista `REFIN1+` de 11,25 mm em B.Cu solta em (163,9; 84,9);
pista `+3.3V_ANA` de 0,7 mm em (138,2; 86,8); via `+3.3V_ANA` em (139,9; 112,6) ligada só numa camada; três pistas
`AIN5/AIN6_ADC_Load_Cell±` soltas em (151,0; 92,3), (157,8; 87,0), (150,9; 91,8). Apagar ou completar.

**I4 — Zona órfã `ilha_1cm2_catodo_D25` em `+12V_TPS`, B.Cu (162,5-177,0; 116,0-124,5).** Herdada da V2.2 (o D25 de
então era um TVS; hoje D25 é um BAV199 em 184,6; 96,5). Fica isolada (2 avisos `isolated_copper`), o pad `+12V_TPS` mais
perto está a 7,3 mm (U11.6) e por baixo dela está D11 (TVS do AIN4). Apagar; se a ilha térmica era para um TVS de
`+12V_TPS`, redesenhá-la debaixo do díodo certo.

### MENOR

- **M1 — Serigrafia órfã do selector:** «2V5» em (157,1; 81,4) e «3V3» em (161,4; 81,4), a 7,7 e 11,7 mm do H1 (agora em
  150,0; 78,4, 2x3). Refazer: 2V5 / 5V / 3V3 junto a cada fila, na ordem do esquemático (1-2 = 2V5, 3-4 = 5V, 5-6 = 3V3).
- **M2 — U12 TPS7A4001 (HVSSOP-8): clearance 0,15 mm entre pads NC 6/7 e pads `+24V_ADC` 5/8**, regra Power24 pede
  0,25. É o passo de 0,65 mm do encapsulado, não o roteamento. Ou os NC vão à rede do pino vizinho no esquemático, ou
  regra DRC que isente os pads NC de U12.
- **M3 — `+24V_ADC` a 0,20 mm** nos cinco troços de fan-out dos pinos 5/8 de U12 (classe Power24 = 0,50). Inevitável no
  passo de 0,65; manter curtos (hoje ≤ 1,3 mm) e alargar logo a seguir.
- **M4 — `Load_Cell+`/`Load_Cell-` a 0,20 mm** (classe Analog = 0,25) em 16 troços entre P2 e R31/R32. Sem efeito
  eléctrico (µA, mV); ou se alarga para 0,25 ou se muda a classe, para o DRC não mentir.
- **M5 — Courtyard C20/C14** sobrepostos (143,0 vs 140,4; 85,4): 0603 a 2,6 mm de centro a centro; afastar 0,15 mm.
- **M6 — Paridade: MPN do U5** (PCB `ISO7141FCCDBQ`, esquemático `ISO7141CCDBQR`). Actualizar PCB a partir do
  esquemático. `lib_footprint_mismatch` em P1/P2 (`HDR1X20/1X14_FEMALE` diferem da biblioteca): actualizar da biblioteca
  ou aceitar por escrito.
- **M7 — Serigrafia:** 57 `silk_over_copper` + 32 `silk_overlap`. Passo final, depois de fechar o cobre.

### Verificado e em ordem

- **Rule areas seguem as peças** (corrigido desde a revisão anterior): Fid1 0,00 mm, Fid2 0,15, Fid3 0,22, barreira ISO7141
  0,70 mm do centro de U5.
- **TPS26613 §11.1:** VSNS a ≥ 2,70 mm de qualquer rede de laço na mesma camada, fora do encapsulado; bypass `+12V_TPS`
  a 2,49-2,54 mm do pino 6 dos quatro U8-U11.
- **AD7124 p.73:** nenhuma pista de rede alheia passa debaixo do U6 (caixa ±3,5 mm); desacoplo AVDD C14/C15 a ~5 mm
  (o datasheet pede «right up against the device» — aceitável, não óptimo).
- **`+3.3V_ANA`:** nasce em U3.5 com C11/C12 no nó e FB2/FB3 a sair desse nó; tronco 0,4 mm até C14/C15 (ADC) e
  C22/C23 (ADR4525); nada de errado na topologia, faltam H1.6, U13/C41, D22/D24/D25.
- **H1 2x3:** redes dos pads = esquemático (1-3-5 `EXC_SEL`; 2 `+2V5_EXC`; 4 `+5V_ADC`; 6 `+3.3V_ANA`); os cortos das
  12:02 foram resolvidos pelo projectista.
- **Larguras:** `+24V`/`+24V_REG` 0,50; `+12V_TPS`, `+5V*` 0,40; laços 0,30 — conforme netclasses, salvo M3/M4.
- Nenhum footprint fora do contorno (118,5-178,5 × 75,0-135,0).

### Não verificado nesta passada

Continuidade do plano `GND_ADC` em In1/In2 sob as pistas de B.Cu (ranhuras), estrangulamentos de enchimento das zonas,
DFT (pontos de teste do plano T&Q), atributos `dnp` PCB × esquemático, ficheiro de posição. Datasheets em falta na pasta:
LP5907 (U13), RB162MM (D23), Samtec FTS (H1), KOA SG73P (R30, lido do download de hoje).

```yaml
evidencia:
  skill: 2shw-pcb:check-roteamento (pre-revisao, sem sessao independente)
  artefatos: [relatorio_roteamento_EBM7_V23L_2026-09-22.md, output/drc_report.json (MCP)]
  sessao_independente: false
  modelo_verificador: Claude Fable 5.1 (mesmo da sessao de edicao)
  drc_violacoes: 102
  por_ligar: 38
  paridade: 1
  bloqueantes: 1
  importantes: 4
  menores: 7
  veredito: NAO-LIMPO
  rodada: 1
```

## Adenda 18:22 — B1 corrigido (opção A, aplicada nesta sessão; verificar em sessão independente)

- Zonas `DGND_B/In1/In2`: bordo inferior a **y = 116,504 para x 126,5–132,5**; mantém-se a 122,304 para x ≤ 126,5, porque
  P1.16 (DGND) e P1.17 (+5V) estão em y 119–121,5 e a pista +5V sobe até (125,3; 117,4). `GND_ADC_*` recebeu a língua
  x 127,001–133,001 × y 117,004–122,304 (0,5 mm de folga em todos os lados).
- Movidos: **C7 → (133,6; 112,1)** (pad +5V_ADC a 1,75 mm de U3.1), **R5 → (130,5; 116,85)**, **D5/R4/T4 → direita do Recom**
  (155,4 / 156,95 / 157,9). Apagados: 13 troços de +5V_ADC na região DGND, 3 de EN, vias GND (134,0;112,6), (134,0;117,4),
  (132,8;115,45), (127,4;116,2) e os tocos; novas vias GND em (133,5;115,45), (134,3;118,35), (127,35;118,7), (155,4;127,0).
- +5V_ADC novo: FB1.2 → R5.2 → y 117,7 → via (134,2;117,45) → B.Cu x 134,75 → via (134,75;113,6) → C7.2 / U3.1, e B.Cu até
  (134,9;103,4) onde retoma a pista existente para H1.6. +5V_REG: U1.3 → y 129,7 → x 157,9 → T4 → R4.1.
- **Medido: mínimo cobre isolado ↔ campo 0,300 → 1,200 mm** (pista +3.3V ↔ pads de R5); nenhum cobre de campo na região DGND.
- DRC 102 → 99 violações (só serigrafia: −3 `silk_over_copper`, +1 `silk_overlap` nas referências de C7/C11/C12/C23),
  por ligar 38 → 35, paridade 1 (MPN do ISO7141, inalterado). Backups: `.antes_barreira` (17:42) … `.antes_barreira5`.
- **Novo achado pré-existente, mesma classe:** pista **+3.3V em B.Cu (124,8–128,0; y 95,0)** entra 1 mm na zona `GND_ADC_B`
  junto a C9/U5 (a escada de `GND_ADC` começa em x 127,0 para y < 95,2): 0,3 mm até o enchimento de campo na mesma camada.
  Corrigir subindo-a para y ≥ 95,5 ou encurtando-a a x ≤ 126,5. Não tocado.

## Adenda 23-09-2026 06:32 — estado actual (só leitura; KiCad aberto)

DRC 120 violações (99 ontem às 18:22), **21 por ligar** (35), paridade 1. Copia com zonas reenchidas dá os mesmos números:
o que está por ligar é real. Desde as 18:22: 13 footprints movidos (R36/R37/R38 e C48/R39 para a direita do U6, C47 junto a
U13, D24/D25 trocados, D21 rodado), 656 → 691 segmentos, 106 → 113 vias, zona órfã `ilha_1cm2_catodo_D25` apagada (I4 fechado).

### Bloqueante novo
**B2 — D21 (TVS 824500101 de Load_Cell−) rodado de 0° para 90° em (168,6; 85,55).** As pistas continuavam a apontar aos pads
da orientação antiga: pad 1 (Load_Cell−) caiu sobre a pista Load_Cell+ (y 83,85) e pad 2 (GND) sobre a pista Load_Cell−
(y 87,15) → **2 `shorting_items`, 5 `solder_mask_bridge`, courtyard sobre D20 e D10, clearance 0,145 mm a D10.1**. Correcção:
voltar D21 a 0° (a pista Load_Cell− já termina em (170,64; 85,55), o pad 1 da orientação original) e ligar o pad 2 ao plano.

### Por ligar (21)
- **GND_ADC, 21 pads sem via:** C14.1, C15.2, C20.1 (desacoplo do ADC); C39.2, R29.2 (REFIN1+); C43.2, C44.1 (filtro da célula);
  D22.1, D24.1, D25.1 (clamps); D19.2, D20.2 (TVS excitação/célula); D6.2, D7.2, D9.2, D10.2, D12.2, D13.2 (TVS dos laços);
  U8.1, U8.3, U9.1 (GND dos TPS26613). Sem pour em F.Cu: uma via por pad ou pista curta até via.
- +3.3V_ANA: D22.2; +2.5_VREF: pista B.Cu 0,8 mm até U6.20 (e via solta em 145,9; 86,2); Load_Cell−: D21.1 (vai com B2).

### Estado dos itens de ontem
| item | estado |
|---|---|
| B1 barreira (FB1/C7/C5 lado PLC) | **fechado** 18:22; mínimo isolado↔campo 1,20 mm; sem cobre de campo na região DGND |
| I1 24 pads GND | 21 restam (lista acima) |
| I2 condensadores do Recom | aberto: C3 12,45 mm, C1 5,52 mm do pino |
| I3 restos soltos | quase fechado: só via +3.3V_ANA (139,9; 112,6) e via +2.5_VREF (145,9; 86,2) |
| I4 zona órfã +12V_TPS | **fechado** |
| M1 serigrafia 2V5/3V3 órfã | aberto (157,1 / 161,4; 81,4) |
| M2 U12 pads NC 0,15 mm | aberto (regra ou rede) |
| M3/M4 larguras +24V_ADC 0,20 / Load_Cell± 0,20 | aberto; novo: `Net-(D5-A)` 0,25 em classe Power24 (classe errada para um LED) |
| M5 courtyard C20/C14 | aberto |
| M6 MPN U5, P1/P2 vs biblioteca | aberto |
| M7 serigrafia | 63 + 40 avisos (cresceu com o placement) |
| +3.3V B.Cu (124,8–128,0; 95,0) na GND_ADC_B junto a C9 | aberto |
| Desacoplo longe: U5.7/U5.10 → 5,8 mm; U6.20 → C25 6,3 mm; U13 → C41 3,4/4,8 mm; VSNS → C37 15–20 mm | inalterado |

### Verificado em ordem
Rule areas seguem as peças; VSNS ≥ 2,70 mm dos laços; nada alheio sob U6; H1 e R30 conforme esquemático; nenhum footprint
fora do contorno; par da célula completo em F.Cu (AIN5 27,5 mm sem via, AIN6 24,9 mm com 2 vias), filtros ainda no lado do conector.

### Correcção de fonte (23-09-2026) — I2, condensadores do Recom
A frase «C1 and C2 are required and should be fitted close to the converter pins» está na secção **Dual Output (two Converters)
with Negative Output** do datasheet (REV 5/2019, p.6), não na aplicação de saída única que usamos. Para saída única o PDF **não
dá instrução de posição** dos condensadores, e o texto extraído não contém «Switching Frequency» (os 120–800 kHz citados ontem
não saem deste PDF). I2 passa a **recomendação de prática** (condensadores de entrada/saída de um conversor comutado junto aos
pinos), não a requisito de datasheet. Mantém-se como IMPORTANTE pela física, com a fonte corrigida.

## Adenda 23-09-2026 09:16 — cirurgia aplicada (caixas 1 e 2, aprovadas por Javier)

Aplicado com verificação de clearance (≥ 0,2 mm a cobre de outra rede, 4 camadas), porta sintáctica + `pcbnew.LoadBoard`
numa cópia antes de gravar, refill e DRC. Backups `.antes_cirurgia` (PCB e .kicad_pro) e `.antes_cirurgia2`.

- **B2 D21**: rodado 90° → 0°; pad 1 caiu na ponta da pista Load_Cell− (170,64; 85,55); pad 2 com via GND. 2 cortos, 5 pontes
  de máscara, 2 courtyards e 1 clearance desapareceram.
- **22 vias GND_ADC** (0,6/0,3, stub 0,3 mm): C14.1, C15.2, C20.1, C39.2, C43.2, C44.1, D6.2, D7.2, D9.2, D10.2, D12.2, D13.2,
  D19.2, D20.2, D21.2, D22.1, D24.1, D25.1, R29.2, U8.1, U8.3, U9.1; mais uma para o grupo C42.1/C45.1 em (161,2; 78,2).
- **Esquina C9/U5** (item «+3.3V B.Cu na GND_ADC_B»): escalão das zonas DGND 96,0 → 94,4 e GND_ADC 95,2 → 93,9; a via (128,0; 95,0),
  a pista B.Cu e C9 ficam dentro do contorno DGND; nenhum cobre PLC dentro do contorno GND_ADC nem cobre de campo dentro do DGND.
  Mínimo isolado ↔ campo mantém-se **1,20 mm**.
- +2.5_VREF: via (145,9; 86,2) ligada a U6.20. C14 −0,10 mm / C20 +0,06 mm (M5 fechado). MPN de U5 = ISO7141CCDBQR (M6,
  paridade 0). `Net-(D5-A)` passou de Power24 a Default no `.kicad_pro`. Load_Cell± 16 troços a 0,25 mm (M4 fechado).
- **Erro meu, corrigido na mesma passada:** a via +3.3V_ANA (139,95; 112,6) que o DRC dava «só numa camada» era o nó entre dois
  troços F.Cu; ao apagá-la partiu-se o ramo dos BAV199. Reposta a junção pelo ponto (139,95; 112,6), sem via.

**Estado:** DRC **97** violações (06:32: 120), das quais 2 erros (pads NC de U12, M2), 57 + 36 de serigrafia, 2 `lib_footprint_mismatch`
(P1/P2); **por ligar 1** (D22.2 ← +3.3V_ANA, sem caminho de 2 troços a partir de D25.2; fica para o projectista); paridade **0**;
nenhuma pista ou via solta. Abertos: I2 (Recom, prática), M1 (serigrafia H1), M2, M3 (+24V_ADC 0,20 no fan-out de U12), M7,
filtros da célula longe do ADC, P1/P2 vs biblioteca, desacoplos de U5/U6.20/U13 e VSNS.

## Adenda 23-09-2026 09:37 — D22.2 ligado pelo projectista; releitura

Javier rotou D22.2 ← +3.3V_ANA (PCB gravada 09:37:45): 9 troços de 0,40 mm + 1 via em (160,45; 80,8); sai de D22.2 em F.Cu, desce a
B.Cu, corre por y = 82,1 debaixo de D24 (lado oposto, com GND_ADC em In1/In2 entre) e entra no bus existente na via (154,75; 79,45).
Moveu ainda as vias GND de C42/C45 (159,2 → 159,55; 80,8) e de D22.1 ((162,6; 81,85) → (161,7; 80,55)). Nenhum footprint ou zona mudou.

- Clearance mínima do caminho novo: **0,382 mm** (F.Cu, vs ADC_Load_Cell+) e 0,400 mm (B.Cu, vs via GND) — acima dos 0,15 da classe e dos
  0,20 do meu critério. Barreira isolado ↔ campo: **1,200 mm**, inalterada.
- DRC: **98** violações, **0 por ligar** (era 1), paridade 0. A violação nova é um **toco redundante** de 0,25 mm em F.Cu,
  (160,45; 83,20)–(160,45; 82,95), sobreposto ao troço maior — apagar. Os 2 erros continuam a ser os pads NC de U12 (M2).
- Ficam como antes: M1 (textos «2V5»/«3V3» órfãos em (157,1; 81,4) e (161,4; 81,4) — o «3V3» está encostado ao pad 1 de D22), M2, M3
  (+24V_ADC a 0,20 no fan-out de U12), 57 + 36 de serigrafia, P1/P2 vs biblioteca, desacoplos «longe» da caixa 3
  (C1/C3 do Recom, C12, C25/C24 de U6.20/U7.6, C41 de U13, C37 dos VSNS).

## ⚠️ Correcção 24-09 — a barreira NÃO mede 1,20 mm

A revisão independente de 24-09 mediu **0,30 mm** cobre-a-cobre entre o domínio PLC e o campo em In1/In2. Re-medido nesta sessão
incluindo os **preenchimentos das zonas** (`barreira_real.py`): F.Cu 1,200 mm; **In1 0,300 mm; In2 0,300 mm; B.Cu 0,400 mm**. O par
crítico é a zona DGND contra a via GND_ADC em (128,20; 116,70) (segunda via de C5.1, presente desde antes da cirurgia de 23-09; C5.1 já
tem via própria em (127,35; 118,70)). Os 1,20 mm que escrevi mediam só pistas e pads, sem zonas — **erro de método meu**. A verificação
«nenhum cobre de campo dentro do contorno DGND» também não apanhou a via, porque ela fica fora do contorno mas a 0,3 mm do seu bordo.
