# Regulador de 3,3 V do lado PLC — U2: MCP1824ST-3302E/DB → SPX3819M5-L-3-3/TR (2026-09-28)

Da reunião de 25-09: «esse chip é mais caro… existe regulador menores». O U2 alimenta só o lado 1 do ISO7141 (+5V do P1 → 3,3 V, massa DGND).

## Comparação que decidiu (datasheets locais; preços da API Mouser gravados nos repositórios)

| | MCP1824ST-3302E/DB (saiu) | SPX3819M5-L-3-3/TR | MCP1824T-3302E/OT |
|---|---|---|---|
| Encapsulamento | SOT-223-3 | SOT-23-5 | SOT-23-5 |
| Entrada (operação / máx. absoluto) | 2,1-6,0 V / 6,5 V | 2,5-16 V / 20 V | 2,1-6,0 V / 6,5 V |
| Precisão em temperatura | ±2,5 % | ±2 % | ±2,5 % |
| Estável com cerâmico | sim, «Stable with 1.0 µF Ceramic» (DS22070A p.1) | **não especificado** («bench testing», SPX3819 rev. 2.0.5 p.7); provado em campo na V2.2 | sim (mesmo datasheet) |
| ESD HBM | ≥ 4 kV | 1 kV | ≥ 4 kV |
| Mouser 1 un. | 0,64 USD (25-09) | 0,51 USD (16-09) | 0,56 USD (25-09) |
| Stock Mouser | 11 898 (25-09) | **99** (16-09) | 14 500 (25-09) |

Carga real: só o lado 1 do ISO7141, ≤ 8 mA a 40 Mbps (TI SLLSE83F p.10). O ISO7141 pede VCC1 de 2,7 a 5,5 V
(p.5) e 0,1 µF a ≤ 2 mm do pino (p.22 e p.25): cumprido com qualquer um dos três (C a 1,9 mm).

**Critério da equipa (28-09-2026): menos MPN, mais peças do mesmo tipo.** Na EBM7 o SPX3819 já é o U3/U4 do
+3.3V_ANA; na EBM2 o MCP1824T já é o U4 do 3V3_REF. O MCP1824ST sai das três placas.

## O que mudou

- **U2 = SPX3819M5-L-3-3/TR**, SOT-23-5. Ligações: 1 IN e 3 EN a +5V, 2 GND a DGND, 4 BYP aberto (p.7 permite), 5 OUT a +3.3V.
- Condensadores mantidos (os que já estavam na entrada e na saída).
- PCB: pegada SOT-23-5 no mesmo sitio (127,45; 108,85); tiradas 11 pistas que acabavam nos pads antigos e 2 restos soltos. **Faltam rotear 6 ligações do U2.** Gerbers, BOM de fabrico, pick-and-place e stencil de 28-09 ainda mostram o MCP1824: regenerar depois do roteamento.

## Verificação

- ERC 0 erros; DRC 0 erros, 0 paridade, 6 por ligar (as do U2); netlist: só mudam os pinos do U2.

## Riscos em aberto

- **Estabilidade com cerâmico não garantida no datasheet** do SPX3819; a base é a experiência de campo da V2.2 (SPX3819 do +3.3V_ANA só com cerâmicos). Aqui a carga é ≤ 8 mA, o que joga a favor (p.7), mas não foi medido. Medir na 1.ª placa: 3,3 V em DC e, com osciloscópio emprestado, o ripple na saída.
- **Stock Mouser baixo** (99 un. a 16-09): confirmar antes da compra (LCSC tem).
- ESD 1 kV HBM (entrada no +5V do P1, conector interno: só conta no manuseio).
- Preços e stock são das consultas gravadas (16 e 25-09), não de hoje: a web da Mouser bloqueia leitura automática.

## Complemento: circuito recomendado do datasheet (SPX3819 rev. 2.0.5, Fig. 18 «Standard Application Circuit», p.8)

| Elemento | Datasheet | Na placa |
|---|---|---|
| EN | alto (> 2 V); «ENABLE may be tied directly to VIN» | EN directo a +5V ✅ |
| BYP | condensador «(Opt.)»; pode ficar aberto se o ruído não importa (p.7) | aberto ✅ |
| Entrada | medido com CIN = 1 µF (p.2-3) | 10 µF cerâmico ✅ |
| Saída | desenhado polarizado; 2,2 µF electrolítico ou 1 µF tântalo (p.7) | C8 10 µF + C9 100 nF + **C49 2,2 µF**, todos cerâmicos |

**C49 = 2,2 µF C1608X5R1E225K080AB** (MPN já na BOM) acrescentado em paralelo à saída do U2, para a saída ficar como a do SPX3819 da V2.2 em campo (2,2 µF + 10 µF + 100 nF, só cerâmicos; a V2.2 não tinha nenhum electrolítico junto do SPX3819: os únicos eram C5/C11 de 100 µF nos +24V_ADC dos PDM2). No PCB: clone da pegada do C8, a 3 mm do U2, **2 ligações por rotear**. ERC 0; DRC 0 erros, sem avisos novos.
