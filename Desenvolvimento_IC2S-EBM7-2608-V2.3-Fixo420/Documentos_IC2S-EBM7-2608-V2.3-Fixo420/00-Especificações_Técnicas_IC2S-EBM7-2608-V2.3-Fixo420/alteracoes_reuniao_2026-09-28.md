# Alterações de 28-09-2026 — revisão da reunião

Quatro observações da reunião, aplicadas ao esquemático e ao PCB. Notas no esquemático: **folha 2, notas 2, 13 e 14**.

## 1. Ramo único de 24 V

**Antes:** depois do TVS havia dois ramos iguais, F1 → D2 → +24V_REG (só o U1, R-78HB) e F2 → D3 → +24V_ADC (laços,
LDO de 12 V, LED), cada um com o seu 10 µF / 100 V.

**Agora:** saem **F2, D3 e C2**. F1 → D2 → **+24V_ADC** alimenta tudo; o nome +24V_REG deixa de existir.

- Motivo (equipa): é tudo alimentado pelos mesmos 24 V; os ramos não eram canais independentes nem isolados; ganha-se espaço.
- Corrente: 116 mA em regime, ~180 mA em falha (folha 1, nota 2) contra F1 = 750 mA e D2 = MBR1H100SF 1 A.
- Arranque: ~30 µF a jusante do F1; pela escala da nota 10 (3,4 mA²s para 20 µF) dá ~5 mA²s contra 150 mA²s de fusão:
  **~29× de margem** (era ~44× no ramo com 20 µF). Estimativa, não medida.
- Custo: perde-se a selectividade. Um curto no +24V_ADC abre F1 e desliga a placa inteira (antes só o ramo dos laços).

PCB: saíram as três peças, a pista do ânodo (Net-(D3-A)), a ligação do díodo à diagonal e o toco de GND do condensador. O bus
+24V passa a acabar no pad 1 do F1. A pista do C1 desce em F.Cu (139,80; 127,20 → 128,80) e junta-se, a 45°, à diagonal
que já ia para a via do +24V_ADC em (141,20; 130,10). Largura 0,50 mm (classe Power24). No `.kicad_pro` saíram os padrões
de netclass `+24V_REG` e `Net-(D3-A)`.

## 2. Condensador de entrada do R-78HB

**C1 = 10 µF / 100 V, 1210 (GRM32EC72A106ME05L)**, a 5,5 mm do pino Vin. Recom R-78HB-0.5 (rev. 5-2019), p.4: *«To
protect the converter during power-up, use C1 = 3.3 µF/100V if Vin > 50V»*. Operamos a 24 V, mas o clamp do TVS é 53,3 V,
portanto aplica-se — e 10 µF / 100 V cumpre. A capacidade de saída (~50 µF) está abaixo do máximo de 100 µF (p.2). O
1 µF / 100 V da p.6 é da configuração de saída negativa, que não é a nossa. **Sem alteração.**

## 3. Tensão dos 100 nF

Todos os 25 eram GRM188R72A104KA35D (100 V). Só um precisa: o **C36**, no +24V_ADC (até 53,3 V).

| Grupo | Tensão máxima | Peça |
|---|---|---|
| C36 no +24V_ADC | 53,3 V (clamp) | fica GRM188R72A104KA35D, 100 V — valor `100nF/100V` |
| 4 no +12V_TPS | 12 V; 31,7 V com o divisor do LDO em falha (folha 6, nota 17) | **TDK C1608X7R1H104K080AA, 50 V** |
| 20 em 3,3 V, 5 V, ADC e referência | ≤ 5 V | **TDK C1608X7R1H104K080AA, 50 V** (um só MPN) |

25 V não serve: não cobre os 31,7 V do +12V_TPS. Fonte: catálogo TDK *MLCC commercial general*, p.34 (X7R, 1608,
100 nF ±10 %, DC 50 V). Valor escrito `100nF/50V`. São 24 peças.

## 4. Mesmo MPN para a mesma função

- 10 µF nos rails de 2,5 / 3,3 / 5 V: já era um só MPN (0603YD106KAT2A). Sem alteração.
- 2,2 µF, 22 µF e 10 µF / 100 V (1210): um MPN cada. Sem alteração.
- **1 µF: havia dois** (885012206002 em 1 e C0603C105K4RACTU em 3). Agora os quatro são **TDK C1608X7R1H105K080AB**
  (X7R, 1608, 1 µF ±10 %, DC 50 V; catálogo TDK p.35). Valor escrito `1uF/50V` (antes havia `1uF` e `1uF/16V`).

O catálogo TDK está em `Projeto_…/Documentos_de_Referência-…/TDK_mlcc_commercial_general_en.pdf`.

## Verificação

- Netlist antes/depois: só saem F2, D3, C2 e a rede Net-(D3-A); C1 / D2 / U1 passam de +24V_REG a +24V_ADC; 28 condensadores
  mudam de valor/MPN. Nenhuma outra ligação muda.
- ERC: 0 erros (os avisos são os mesmos de antes).
- DRC (`--severity-all --schematic-parity --all-track-errors`): 0 erros, 62 avisos (serigrafia), 0 por ligar, paridade 0.
- Gerbers, furos, BOM (55 linhas, 134 peças, 133 a montar), pick-and-place (144 linhas), stencil, PDF do esquemático, vistas e STEP regenerados.

Scripts (sessão de 28-09): `sch_2809.py` (esquemático), `pcb_2809.py` (PCB), `pro_2809.py` (netclasses).
