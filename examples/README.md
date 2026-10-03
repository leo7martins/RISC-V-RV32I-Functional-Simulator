# Exemplos em assembly RISC-V (RV32I)

Programas de exemplo para o simulador. Cada ficheiro é assembly RV32I válido para
o assembler do projeto e pode ser executado com a CLI:

```bash
python run.py examples/soma.s
```

| Ficheiro | Descrição | Resultado esperado |
|---|---|---|
| `soma.s` | Soma `1..10` num ciclo | `55` |
| `fibonacci.s` | Fibonacci iterativo — F(10) | `55` |
| `maximo.s` | Máximo de dois números (42 e 17) | `42` |
| `memoria.s` | Escreve e relê um valor na RAM (`sw` / `lw`) | `1234` |

### Convenções usadas

- O resultado final é colocado em `a0` (`x10`) e impresso com a syscall `1` (`print_int`).
- O programa termina com a syscall `10` (`exit`).
- Os comentários começam com `#` (também é aceite `//`).
