# legacy/ — protótipos iniciais

Esta pasta guarda as versões iniciais do simulador, mantidas **apenas como referência
histórica**. Não fazem parte da versão atual nem são mantidas.

| Ficheiro | Origem | Descrição |
|---|---|---|
| `prototype_v1.py` | `main.py` (raiz do antigo workspace) | Primeiro protótipo: tudo num só ficheiro, com funções soltas e um conjunto mínimo de instruções (`add`, `sub`, `and`, `or`, `lw`, `sw`). |
| `prototype_v2.py` | `projeto.py` | Segundo protótipo: já organizado numa classe `RISCVProcessor`, com ciclo *fetch/decode/execute* e suporte a mais tipos de instrução (R, I, S, B, U, J). |

A implementação atual, organizada em módulos, está em [`../riscv/`](../riscv).
