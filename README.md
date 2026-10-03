# RISC-V RV32I — Functional Simulator

Simulador **funcional** (interpretador a nível de instrução) do conjunto de instruções
**RISC-V RV32I**, escrito em **Python puro**, sem qualquer dependência externa.

O projeto inclui um **assembler de duas passagens** (com suporte a labels e pseudo-instruções),
uma **CPU** que implementa o ciclo *fetch → decode → execute*, uma **memória segmentada**
(texto, dados e stack) com validação de acesso e alinhamento, e um pequeno conjunto de
**syscalls** (`ecall` / `ebreak`).

---

## Funcionalidades

- **Assembler de duas passagens** com tabela de símbolos (labels), comentários (`#` e `//`) e
  pseudo-instruções (`li`, `mv`, `nop`, `ret`, `j`).
- **Instruções RV32I** dos tipos R, I, S, B, U e J.
- **CPU** com registos `x0..x31` (aliases ABI: `zero`, `ra`, `sp`, `a0`, `t0`, …) e `x0` fixo a 0.
- **Memória segmentada** (Text / Data / Stack) com:
  - validação de endereços dentro dos segmentos;
  - proteção de escrita no segmento de texto (read-only);
  - verificação de alinhamento (word/halfword).
- **Exceções arquiteturais** próprias (`InvalidInstruction`, `InvalidMemoryAccess`,
  `MisalignedMemoryAccess`, `ProgramTerminated`, …).
- **Syscalls** (`ecall`) para imprimir inteiros, strings e caracteres, ler inteiros e terminar.

---

## Estrutura do projeto

```
.
├── riscv/                    # Pacote com o simulador
│   ├── assembler.py          # Assembler de duas passagens
│   ├── cpu.py                # Ciclo fetch / decode / execute
│   ├── instructions.py       # Implementação de cada instrução
│   ├── memory.py             # Memória segmentada + validação
│   ├── registers.py          # Banco de 32 registos (x0..x31)
│   ├── exceptions.py         # Exceções arquiteturais
│   ├── util.py               # Utilitários (extração de bits, extensão de sinal)
│   └── main.py               # Programa de demonstração
├── examples/                 # Programas de exemplo em assembly (.s)
├── tests/                    # Testes unitários (unittest, sem dependências)
├── legacy/                   # Protótipos iniciais (referência histórica)
└── run.py                    # CLI para correr ficheiros .s
```

> Nota: o pacote usa *imports* relativos ao próprio diretório (ex.: `from cpu import CPU`),
> por isso é executado a partir da sua pasta — ver secção **Como executar**.

---

## Requisitos

- **Python 3.8+**
- **Sem dependências externas** (apenas a biblioteca padrão).

---

## Como executar

**Demonstração incluída** (imprime o resultado e o *trace* de execução):

```bash
python riscv/main.py
```

**Correr um programa assembly (`.s`)** com a CLI:

```bash
python run.py examples/soma.s
```

---

## Exemplos

| Ficheiro | Descrição | Resultado esperado |
|---|---|---|
| `examples/soma.s` | Soma `1..10` num ciclo | `55` |
| `examples/fibonacci.s` | Fibonacci iterativo (F(10)) | `55` |
| `examples/maximo.s` | Máximo de dois números (42 e 17) | `42` |
| `examples/memoria.s` | Escreve e relê um valor na RAM (`sw`/`lw`) | `1234` |

---

## Instruções suportadas

| Tipo | Instruções |
|---|---|
| **R** | `add` `sub` `sll` `slt` `sltu` `xor` `srl` `sra` `or` `and` |
| **I (aritmética)** | `addi` `slti` `sltiu` `xori` `ori` `andi` `slli` `srli` `srai` |
| **Load** | `lb` `lh` `lw` `lbu` `lhu` |
| **Store** | `sb` `sh` `sw` |
| **Branch** | `beq` `bne` `blt` `bge` `bltu` `bgeu` |
| **U** | `lui` `auipc` |
| **J** | `jal` `jalr` |
| **Sistema** | `ecall` `ebreak` |
| **Pseudo** | `li` `mv` `nop` `ret` `j` |

### Syscalls (`ecall`)

O número do serviço é colocado em `a7` (`x17`) e o argumento em `a0` (`x10`).

| `a7` | Serviço | Descrição |
|---|---|---|
| `1` | `print_int` | Imprime o inteiro em `a0` |
| `4` | `print_string` | Imprime a string terminada em `\0` no endereço `a0` |
| `5` | `read_int` | Lê um inteiro para `a0` |
| `10` | `exit` | Termina o programa |
| `11` | `print_char` | Imprime o caractere em `a0` |

---

## Mapa de memória

| Segmento | Início | Fim |
|---|---|---|
| Texto (instruções, read-only) | `0x00400000` | `0x00500000` |
| Dados | `0x10010000` | `0x10020000` |
| Stack | `0x7FFF0000` | `0x80000000` |

O *program counter* (PC) começa em `0x00400000`.

---

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem utilitários de bits, registos, aritmética, assembler, branches e
comportamento da memória (incluindo exceções de acesso).

---

## Licença

Distribuído sob a licença **MIT** — ver [LICENSE](LICENSE).
