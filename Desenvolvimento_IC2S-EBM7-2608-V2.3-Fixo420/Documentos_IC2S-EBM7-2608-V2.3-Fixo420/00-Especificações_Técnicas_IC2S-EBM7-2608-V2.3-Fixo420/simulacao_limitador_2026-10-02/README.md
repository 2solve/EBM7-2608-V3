# Simulação do limitador discreto (2026-10-02)

Canal de laço 1 da EBM7 V2.3 Fixo420 depois da alteração descrita em
`../alteracao_limitador_discreto_lacos_2026-10-02.md`. Os valores das peças foram lidos do netlist exportado do esquemático
novo.

## Como reproduzir

Correr a partir **desta pasta**. O `.spiceinit` liga a compatibilidade PSpice, necessária para ler a biblioteca da Infineon:

```
ngspice_con -b sim_transmissor_em_curto_bus_32_27.cir
```

Cada `.cir` imprime (ou mede) as grandezas da tabela. Resultados completos:
- `resultados_sim_depois.json` — números;
- `sim_depois_saida.txt` — o resumo legível.

| Ficheiro | Caso |
|---|---|
| `sim_normal_bus_{18,24,32}_27.cir` | funcionamento normal, 20 mA |
| `sim_transmissor_em_curto_bus_32_{-40,27,60,85}.cir` | transmissor em curto, barramento a 32 V |
| `sim_AIN_a_32_V_externo_{...}.cir` | linha AIN ligada a 32 V externos |
| `sim_AIN_a_32_V_externo_burden_aberta_{...}.cir` | idem, com a burden aberta |
| `sim_curto_com_modelo_termico_{-40,27,60}.cir` | contraste com o modelo Infineon completo (nós Tj/Tcase, RthCA 90 K/W) |
| `sim_surto_{positivo,negativo}.cir` | surto 1,2/50 µs, 1 kV, 2 Ω + 40 Ω / 0,5 µF, directo em P2.7 |

## Modelos

- `modelos/Infineon_small_signal_200V_PSpice.lib` — Infineon. Usa-se `BSP297_L0` (nível 3) e, no contraste térmico, `BSP297`.
- `modelos/Nexperia_BC847C_SPICE.txt` — Nexperia. Os nós do modelo são 1 = C, 2 = B, 3 = E, que **não são** os pinos do
  encapsulado. Nos surtos usa-se só o transistor principal do mesmo modelo (`BC847C_CORE`), porque o díodo auxiliar de
  quase-saturação impede a convergência.
- Zener, TVS, BAV199, transmissor e cabo: modelos genéricos ou suposições **(D)**, descritos no cabeçalho dos scripts.

## Ferramentas

`ferramentas/` tem os scripts usados nesta sessão, com caminhos absolutos da máquina onde correram:
- `aplicar_limitador.py` aplica a alteração à folha 6;
- `verificar_limitador.py` são as portas: netlist, ERC e render;
- `sim_depois.py` gera e corre estes netlists;
- `parts.json` tem as peças.

A saída das portas está em `verificar_saida.txt`.
