# Verificação de aplicação — TPS26613 (U8-U11) — EBM7 V2.3 legacy

**Data:** 21-09-2026 · **Placa:** `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI.kicad_pcb`, gravada às **19:11:52** ·
**Datasheet:** `TI_TPS2661x.pdf` (SLVSFE3C, nov. 2020 rev. dez. 2021), citações por `grep` com página ·
**Procedimento:** `2shw-pcb:esquematico` etapa 2.3b / skill `verificar-aplicacao-datasheet` — tabela gerada por avaliação (`tabela.py`), não escrita à mão.

## Estado do roteamento no momento da leitura

549 segmentos (F.Cu 507 · B.Cu 42) · 83 vias · 71 ligações por fazer (eram 80) · DRC: 3 `clearance` · 4 `courtyards_overlap` · 2 `isolated_copper` · 0 `track_dangling` (eram 2) · 76 de serigrafia.
`VSNS`: 73,69 mm (F.Cu 50,27 · B.Cu 23,42), 4 vias; troço vertical em B.Cu em x = 161,300 de y 98,1 a 121,5.
Barreira do ISO7141: sem pistas nem vias no keepout.

## Tabela de verificação

| CI | fonte (§/tabela/nota, pág.) | fórmula | valores usados | resultado | veredito |
|---|---|---|---|---|---|
| TPS26613 U8-U11 | SLVSFE3C Tab. 8-2 nota (1), pág. 20 | `(R1 + R2) <= (+Vs) / 45 uA` | R1=1.15e+04, R2=3325, Vs=12.000 | R1+R2 = 1.482e+04 ; Vs/45e-6 = 2.667e+05 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C Tab. 8-2 nota (2), pág. 20 | `V(SNSF) x (R1+R2)/R2 > I_LOOP x R_burden` | V_SNSF=1.000, R1=1.15e+04, R2=3325, I_LOOP=0.02, R_burden=110.000 R13-R17 = 110R na placa (era 409 herdado) | V_SNSF*(R1+R2)/R2 = 4.459 ; I_LOOP*R_burden = 2.200 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C Tab. 8-2 linha '±Vs supplies', pág. 20 | `+Vs >= V(SNSR) x (R1+R2)/R2  (tem de conseguir sair do modo lazo)` | V_SNSR=1.720, R1=1.15e+04, R2=3325, Vs=12.000 | V_SNSR*(R1+R2)/R2 = 7.669 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §8.3.5.1, pág. 20 | `R1/R2 recomendados se I_LOOP x R_burden > 1,8 V  -> estao presentes (R22, R23||R24)` | I_LOOP=0.02, R_burden=110.000, presentes=1.000 | I_LOOP*R_burden = 2.200 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §7.3 Rec. Operating, pág. 4 | `+Vs <= 30 V` | Vs=12.000 +Vs vem do U12 regulado, nao dos 24 V crus (que chegam a 33) | Vs = 12.000 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §7.3 Rec. Operating, pág. 4 | `VSNS <= 5 V` | Vs=12.000, R1=1.15e+04, R2=3325 | Vs*R2/(R1+R2) = 2.691 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §7.3 Rec. Operating, pág. 4 | `IN, OUT dentro de -50..+50 V  (lazo a 24 V, TVS D1 a 33 V)` | V_max_lazo=33.000 | V_max_lazo = 33.000 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §7.1 Abs max, pág. 4 | `VSNS <= 5,5 V` | Vs=12.000, R1=1.15e+04, R2=3325 | Vs*R2/(R1+R2) = 2.691 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §7.5 IOL tip. 32 mA + Tab. 8-2 nota (2) | `em limite de corrente: I_OL x R_burden < V(SNSF) x (R1+R2)/R2  (nao cai em modo lazo na falta)` | I_OL=0.032, R_burden=110.000, V_SNSF=1.000, R1=1.15e+04, R2=3325 | I_OL*R_burden = 3.520 ; V_SNSF*(R1+R2)/R2 = 4.459 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §11.1 bullet 1, pág. 36 — 'add local bypass capacitors' (limite 3 mm = critério, TI nao da numero) | `distancia pino 6 (+Vs) ao 100 nF local <= 3 mm, nos 4 canais` | d_U8=2.490, d_U9=2.540, d_U10=2.520, d_U11=2.540 | max(d_U8,d_U9,d_U10,d_U11) = 2.540 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §11.1 bullet 2, pág. 36 — 'connect GND pin to GND of ±Vs supplies' | `pino 1 (GND) e pino 3 (-Vs) na mesma rede que a massa do +Vs (GND_ADC), nos 4` | ok_netlist=1.000 | ok_netlist = 1.000 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C §11.1 bullet 3, pág. 36 — 'route both terminals of Rburden differentially to ADC (AINP, AINM)' | `entrada do ADC diferencial sobre R_burden` | diferencial=0 topologia unipolar (R13 a GND_ADC, so AINx_ADC vai ao U6) — decisao de projecto a documentar, nao e de roteamento | diferencial = 0 | **FALHA** |
| TPS26613 U8-U11 | SLVSFE3C §11.1 bullet 4, pág. 36 — 'keep EN/VSNS and SGOOD away from loop current' (2 mm fora do encapsulado = critério) | `distancia minima VSNS <-> redes de lazo na mesma capa, fora da saida de pino, >= 2 mm` | d_min_fora_pino=2.460, d_saida_pino_SOT23_8=1.300 1,30 mm e a distancia pino5-pino7 do SOT-23-8, geometria do encapsulado | d_min_fora_pino = 2.460 ; d_saida_pino_SOT23_8 = 1.300 | cumpre |
| TPS26613 U8-U11 | §11.1 bullet 4 aplicado ao troco novo de VSNS em B.Cu (23,4 mm sob a coluna de OUT em F.Cu) | `planos In1 e In2 (GND_ADC) continuos entre o troco de B.Cu e as pistas de lazo em F.Cu (so as antipads das 4 vias descobertas)` | pontos_cobertos=37.000, pontos_total=51.000, vias=4.000, pontos_por_via=3.500 | pontos_total - pontos_cobertos = 14.000 ; vias*pontos_por_via = 14.000 | cumpre |
| R13-R17 (carga) | critério de derating: I²R <= 50 % do nominal 0603 (0,1 W) | `I_LOOP² x R_burden <= 0,050 W` | I_LOOP=0.02, R_burden=110.000 | I_LOOP**2*R_burden = 0.044 | cumpre |
| AD7124-8 U6 <- lazo | AD7124-8 Rev F: fim de escala = V_REF (ADR4525 2,5 V), unipolar | `I_LOOP x R_burden <= V_REF a 20 mA; fim de escala em mA = V_REF / R_burden` | I_LOOP=0.02, R_burden=110.000, V_REF=2.500 | I_LOOP*R_burden = 2.200 ; V_REF/R_burden*1000 = 22.727 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C Fig. 6-1, pág. 3 (renderizada) — pad 7 = VSNS no 26613; = EN no 26611/12/14 | `pad 7 dos 4 footprints na rede VSNS (pinfunction VSNS_7)` | ok_pinout=1.000 | ok_pinout = 1.000 | cumpre |
| TPS26613 U8-U11 | SLVSFE3C SGOOD (pad 8) — saida de diagnostico por canal | `SGOOD ligado ou decisao escrita de o deixar sem uso` | decisao_escrita=? os 4 SGOOD estao sem ligar; falta a nota de decisao na folha | missing: decisao_escrita | **falta dado** |

cumpre: 16 · FALHA: 1 · falta dado: 1


**Leitura:** 16 cumprem · 1 falha · 1 falta dado. A falha é de **topologia**, não de roteamento; o dado que falta é uma **nota de decisão**, não uma medida.

## Prova de uma multiplicação — cadeia de um canal (idêntica nos quatro)

```
P2.AINx ─► U8 IN ─► U8 OUT ─► R10 0R ─┬─► R13 110R ─► GND_ADC
                                       └─► FB4 ─► R18 3k3 ─► AINx_ADC ─► U6      (C27 100 nF, clamp D14)

  4 mA :  V(OUT) = 0,004 × 110 = 0,44 V      V(ADC) = 0,44 V   (17,6 % do fim de escala de 2,5 V)
 20 mA :  V(OUT) = 0,020 × 110 = 2,20 V      V(ADC) = 2,20 V   (88 %)
22,7 mA:  V(OUT) = 2,50 V = V_REF            fim de escala do ADC — permite ver o fallo NAMUR > 21 mA
32 mA (I_OL, em falta): V(OUT) = 3,52 V  <  4,46 V (umbral de modo lazo)  →  o TPS26613 não muda de modo durante uma falta
Margem ao transmissor a 20 mA: 24 − 0,15 (R_ON 7,5 Ω) − 2,20 − ~0,5 (fusível + díodo) ≈ 21 V
Antes (valores herdados 40k2 + 10k): 20 mA × 50,2 kΩ = 1 004 V — a entrada não podia funcionar em corrente.
```

## O que nenhuma ferramenta viu

- **ERC / DRC**: não lêem datasheets. Um divisor de 50,2 kΩ numa entrada de corrente é eléctricamente perfeito para ambos.
- **Analisador de esquemático (kicad-happy)**: reconhece padrões, não intenções. Viu `R10`/`R13` como divisor de tensão e deu-o por correcto.
- **SPICE (47/47)**: confirmou que o divisor dividia o que dizia dividir. Não pode saber se devia ser um divisor.
- **Revisor independente**: recebeu o checklist de pinagem e roteamento. Nenhum dos dois tinha a linha «fórmulas da secção de aplicação com os valores da BOM».
- **`kicad-cli`**: tolera uma cadeia partida em várias linhas que o editor gráfico rejeita — verificar como carrega o utilizador.

## O que continua a não cumprir, e porquê

1. **§11.1 bullet 3 — `RBurden` diferencial para `AINP`/`AINM`.** A topologia é unipolar: `R13` vai a `GND_ADC` e só `AINx_ADC` chega ao `U6`. É uma recomendação de exactidão (rejeição de ruído de massa), não um limite eléctrico. **Não se resolve no roteamento**: ou se aceita e se escreve como decisão na folha `06_lacos`, ou se muda o esquemático para ligar os dois terminais de `R13` a um par `AINP`/`AINM` do AD7124 (tem 16 entradas). Recomendação: escrever a decisão; a medida em 4-20 mA industrial tolera a perda.
2. **`SGOOD` (pad 8) sem ligar nos quatro.** Perde-se o diagnóstico por canal. Legítimo, mas falta a nota de decisão na folha.

## Limites desta revisão

- Cobre **um** dos seis CI críticos. Faltam AD7124-8, ISO7141, TPS7A4001, SPX3819 e R-78HB com o mesmo rigor.
- `V(SNSF)` = 1,00 V e `V(SNSR)` = 1,72 V são os valores da tabela da pág. 6 tal como extraídos; se essa linha tiver mín/máx que a extracção não captou, o limite de 223 Ω desloca-se ligeiramente. Não muda nenhum veredito com 110 Ω (margem 4,46 V contra 2,20 V).
- Os limites de 3 mm (bypass) e 2 mm (VSNS fora do encapsulado) são **critério do revisor**: a TI não dá número. Estão marcados como tal na tabela.
- O `+Vs` do TPS26613 assume-se 12,0 V; o valor real do `U12` (TPS7A4001 com 93k1/10k) não foi medido nesta revisão.

## Pendentes que saem desta tabela

- Nota de decisão na folha `06_lacos` sobre `SGOOD` sem uso e sobre a entrada unipolar do ADC.
- MPN dos quatro `110R` 0,1 % (`R13`, `R14`, `R15`, `R17`).
- Constante do firmware dos painéis: **9,09 mA/V** (2,20 V a 20 mA).
- `clearance` em (164,40 · 100,65): pista `AIN2` contra a ilha de `GND_ADC` do `U9` — roteamento.
