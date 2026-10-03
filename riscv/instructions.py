from exceptions import ProgramTerminated
from util import Utility

class Instructions:
    @staticmethod
    def execute_add(cpu, instr):
        res = cpu.registers.read(instr.rs1) + cpu.registers.read(instr.rs2)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)
    
    @staticmethod
    def execute_sub(cpu, instr):
        res = cpu.registers.read(instr.rs1) - cpu.registers.read(instr.rs2)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)
    
    @staticmethod
    def execute_xor(cpu, instr):
        res = cpu.registers.read(instr.rs1) ^ cpu.registers.read(instr.rs2)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_or(cpu, instr):
        res = cpu.registers.read(instr.rs1) | cpu.registers.read(instr.rs2)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_and(cpu, instr):
        res = cpu.registers.read(instr.rs1) & cpu.registers.read(instr.rs2)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_sll(cpu, instr):
        res = cpu.registers.read(instr.rs1) << (cpu.registers.read(instr.rs2) & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_srl(cpu, instr):
        res = cpu.registers.read(instr.rs1) >> (cpu.registers.read(instr.rs2) & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_sra(cpu, instr):
        res = Utility.sign_extend(cpu.registers.read(instr.rs1), 32) >> (cpu.registers.read(instr.rs2) & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_slt(cpu, instr):
        if Utility.sign_extend(cpu.registers.read(instr.rs1), 32) < Utility.sign_extend(cpu.registers.read(instr.rs2), 32):
            res = 1
        else:
            res = 0
        cpu.registers.write(instr.rd, res)

    @staticmethod
    def execute_sltu(cpu, instr):
        if cpu.registers.read(instr.rs1) < cpu.registers.read(instr.rs2):
            res = 1
        else:
            res = 0
        cpu.registers.write(instr.rd, res)

    @staticmethod
    def execute_addi(cpu, instr):
        res = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_xori(cpu, instr):
        res = cpu.registers.read(instr.rs1) ^ instr.imm
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_ori(cpu, instr):
        res = cpu.registers.read(instr.rs1) | instr.imm
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_andi(cpu, instr):
        res = cpu.registers.read(instr.rs1) & instr.imm
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_slli(cpu, instr):
        res = cpu.registers.read(instr.rs1) << (instr.imm & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_srli(cpu, instr):
        res = cpu.registers.read(instr.rs1) >> (instr.imm & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_srai(cpu, instr):
        res = Utility.sign_extend(cpu.registers.read(instr.rs1), 32) >> (instr.imm & 0x1F)
        cpu.registers.write(instr.rd, res & 0xFFFFFFFF)

    @staticmethod
    def execute_slti(cpu, instr):
        if Utility.sign_extend(cpu.registers.read(instr.rs1), 32) < instr.imm:
            res = 1
        else:
            res = 0
        cpu.registers.write(instr.rd, res)

    @staticmethod
    def execute_sltiu(cpu, instr):
        if cpu.registers.read(instr.rs1) < (instr.imm & 0xFFFFFFFF):
            res = 1
        else:
            res = 0
        cpu.registers.write(instr.rd, res)

    @staticmethod
    def execute_lw(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, cpu.memory.load_word(addr))

    @staticmethod
    def execute_sw(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.memory.store_word(addr, cpu.registers.read(instr.rs2))

    @staticmethod
    def execute_lb(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, cpu.memory.load_byte(addr, signed=True))

    @staticmethod
    def execute_lbu(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, cpu.memory.load_byte(addr, signed=False))

    @staticmethod
    def execute_lh(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, cpu.memory.load_half(addr, signed=True))

    @staticmethod
    def execute_lhu(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.registers.write(instr.rd, cpu.memory.load_half(addr, signed=False))

    @staticmethod
    def execute_sb(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.memory.store_byte(addr, cpu.registers.read(instr.rs2))

    @staticmethod
    def execute_sh(cpu, instr):
        addr = cpu.registers.read(instr.rs1) + instr.imm
        cpu.memory.store_half(addr, cpu.registers.read(instr.rs2))

    @staticmethod
    def execute_lui(cpu, instr):
        cpu.registers.write(instr.rd, instr.imm)

    @staticmethod
    def execute_beq(cpu, instr):
        if cpu.registers.read(instr.rs1) == cpu.registers.read(instr.rs2):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_bne(cpu, instr):
        if cpu.registers.read(instr.rs1) != cpu.registers.read(instr.rs2):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_blt(cpu, instr):
        if Utility.sign_extend(cpu.registers.read(instr.rs1), 32) < Utility.sign_extend(cpu.registers.read(instr.rs2), 32):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_bge(cpu, instr):
        if Utility.sign_extend(cpu.registers.read(instr.rs1), 32) >= Utility.sign_extend(cpu.registers.read(instr.rs2), 32):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_bltu(cpu, instr):
        if Utility.zero_extend(cpu.registers.read(instr.rs1), 32) < Utility.zero_extend(cpu.registers.read(instr.rs2), 32):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_bgeu(cpu, instr):
        if cpu.registers.read(instr.rs1) >= cpu.registers.read(instr.rs2):
            cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_jal(cpu, instr):
        cpu.registers.write(instr.rd, cpu.pc)
        cpu.pc = cpu.current_pc + instr.imm

    @staticmethod
    def execute_jalr(cpu, instr):
        base_address = cpu.registers.read(instr.rs1)
        cpu.registers.write(instr.rd, cpu.pc)
        target_address = (base_address + instr.imm) & 0xFFFFFFFE
        cpu.pc = target_address

    @staticmethod
    def execute_auipc(cpu, instr):
        cpu.registers.write(instr.rd, (cpu.current_pc + instr.imm) & 0xFFFFFFFF)

    @staticmethod
    def execute_ebreak(cpu, instr):
        raise ProgramTerminated("EBREAK atingido: Ponto de paragem no código.")

    @staticmethod
    def execute_ecall(cpu, instr):
        syscall_number = cpu.registers.read(17)
        if syscall_number == 1:
            print(Utility.sign_extend(cpu.registers.read(10), 32), end='')

        elif syscall_number == 4:
            addr = cpu.registers.read(10)
            result = []
            while True:
                byte = cpu.memory.load_byte(addr, signed=False)
                if byte == 0:
                    break
                result.append(chr(byte))
                addr += 1
            print(''.join(result), end='')

        elif syscall_number == 5:
            try:
                val = int(input())
                cpu.registers.write(10, val & 0xFFFFFFFF)
            except (ValueError, EOFError):
                cpu.registers.write(10, 0)

        elif syscall_number == 10:
            raise ProgramTerminated("Programa encerrado com sucesso (Ecall 10).")

        elif syscall_number == 11:
            print(chr(cpu.registers.read(10) & 0xFF), end='')

        else:
            print(f"[SYSCALL] Serviço {syscall_number} não implementado.")