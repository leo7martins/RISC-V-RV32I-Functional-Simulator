#!/usr/bin/env python3
"""CLI para executar um programa assembly RISC-V (RV32I) no simulador.

Uso:
    python run.py <ficheiro.s>

Exemplo:
    python run.py examples/soma.s
"""
import os
import sys

# O pacote usa imports relativos ao próprio diretório (ex.: `from cpu import CPU`),
# por isso a pasta do pacote tem de estar no sys.path.
PKG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "riscv")
sys.path.insert(0, PKG_DIR)

from assembler import Assembler        # noqa: E402
from main import execute_program       # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("Uso: python run.py <ficheiro.s>")
        print("Exemplo: python run.py examples/soma.s")
        return 1

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Erro: ficheiro não encontrado: {path}")
        return 1

    with open(path, "r", encoding="utf-8") as ficheiro:
        linhas = ficheiro.readlines()

    print(f"--- A executar {path} ---")
    programa = Assembler.assemble(linhas)
    execute_program(programa)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
