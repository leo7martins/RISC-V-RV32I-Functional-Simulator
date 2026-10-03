"""Testes unitários do simulador RISC-V RV32I.

Usa apenas a biblioteca padrão (``unittest``), sem dependências externas.

Executar:

    python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

# O pacote usa imports relativos ao próprio diretório (ex.: `from cpu import CPU`),
# por isso adicionamos a pasta do pacote ao sys.path.
PKG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "riscv")
)
sys.path.insert(0, PKG_DIR)

from assembler import Assembler  # noqa: E402
from cpu import CPU  # noqa: E402
from exceptions import (  # noqa: E402
    ProgramTerminated,
    InvalidMemoryAccess,
    MisalignedMemoryAccess,
)
from util import Utility  # noqa: E402


# Sequência de terminação (syscall 10 — exit) acrescentada ao fim de cada
# programa de teste. Sem ela, a CPU continuaria a "caminhar" para além do código
# e tentaria descodificar memória vazia (opcode 0x0).
TERMINATE = ["addi a7, zero, 10", "ecall"]


def run(asm_lines, trace=False):
    """Monta e executa um programa (com terminação) e devolve a instância da CPU."""
    cpu = CPU(trace=trace)
    cpu.memory.load_program(Assembler.assemble(list(asm_lines) + TERMINATE))
    try:
        while cpu.step():
            pass
    except ProgramTerminated:
        pass
    return cpu


class TestUtility(unittest.TestCase):
    def test_extract_bits(self):
        self.assertEqual(Utility.extract_bits(0b11010110, 0, 3), 0b0110)
        self.assertEqual(Utility.extract_bits(0b11010110, 4, 7), 0b1101)

    def test_sign_extend(self):
        self.assertEqual(Utility.sign_extend(0b1000, 4), -8)
        self.assertEqual(Utility.sign_extend(0b0111, 4), 7)

    def test_zero_extend(self):
        self.assertEqual(Utility.zero_extend(0x1FF, 8), 0xFF)


class TestRegisters(unittest.TestCase):
    def test_x0_is_immutable(self):
        cpu = run(["addi x0, x0, 42"])
        self.assertEqual(cpu.registers.read(0), 0)

    def test_addi(self):
        cpu = run(["addi x5, x0, 100"])
        self.assertEqual(cpu.registers.read(5), 100)


class TestArithmetic(unittest.TestCase):
    def test_add(self):
        cpu = run(["addi x1, x0, 5", "addi x2, x0, 7", "add x3, x1, x2"])
        self.assertEqual(cpu.registers.read(3), 12)

    def test_sub_wraps_negative(self):
        cpu = run(["addi x1, x0, 5", "addi x2, x0, 10", "sub x3, x1, x2"])
        self.assertEqual(cpu.registers.read(3), 0xFFFFFFFB)  # -5 em complemento para 2

    def test_and_or_xor(self):
        cpu = run([
            "addi x1, x0, 0b1100",
            "addi x2, x0, 0b1010",
            "and x3, x1, x2",
            "or x4, x1, x2",
            "xor x5, x1, x2",
        ])
        self.assertEqual(cpu.registers.read(3), 0b1000)
        self.assertEqual(cpu.registers.read(4), 0b1110)
        self.assertEqual(cpu.registers.read(5), 0b0110)


class TestAssembler(unittest.TestCase):
    def test_li_small_uses_addi(self):
        cpu = run(["li x5, 42"])
        self.assertEqual(cpu.registers.read(5), 42)

    def test_li_large_uses_lui_addi(self):
        cpu = run(["li x5, 0x12345678"])
        self.assertEqual(cpu.registers.read(5), 0x12345678)

    def test_mv_and_nop(self):
        cpu = run(["li x5, 7", "mv x6, x5", "nop"])
        self.assertEqual(cpu.registers.read(6), 7)


class TestBranches(unittest.TestCase):
    def test_beq_taken_skips_instruction(self):
        cpu = run([
            "addi x1, x0, 1",
            "addi x2, x0, 1",
            "beq x1, x2, skip",
            "addi x3, x0, 99",   # deve ser saltada
            "skip:",
            "addi x4, x0, 1",
        ])
        self.assertNotEqual(cpu.registers.read(3), 99)  # instrução foi saltada
        self.assertEqual(cpu.registers.read(4), 1)

    def test_bne_not_taken(self):
        cpu = run([
            "addi x1, x0, 1",
            "addi x2, x0, 1",
            "bne x1, x2, skip",
            "addi x3, x0, 7",    # NÃO deve ser saltada
            "skip:",
        ])
        self.assertEqual(cpu.registers.read(3), 7)


class TestMemory(unittest.TestCase):
    def test_sw_lw_roundtrip(self):
        cpu = run([
            "lui t0, 0x10010",   # t0 = 0x10010000 (segmento de dados)
            "addi t1, zero, 1234",
            "sw t1, 0(t0)",
            "lw a0, 0(t0)",
        ])
        self.assertEqual(cpu.registers.read(10), 1234)

    def test_write_to_text_segment_raises(self):
        cpu = CPU()
        cpu.memory.load_program(Assembler.assemble([
            "lui t0, 0x400",     # t0 = 0x00400000 (segmento de texto, read-only)
            "addi t1, zero, 1",
            "sw t1, 0(t0)",
        ]))
        with self.assertRaises(InvalidMemoryAccess):
            while cpu.step():
                pass

    def test_misaligned_word_load_raises(self):
        cpu = CPU()
        cpu.memory.load_program(Assembler.assemble([
            "lui t0, 0x10010",
            "addi t0, t0, 2",    # endereço não alinhado a 4
            "lw a0, 0(t0)",
        ]))
        with self.assertRaises(MisalignedMemoryAccess):
            while cpu.step():
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
