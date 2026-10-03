from memory import Memory
from registers import RegisterFile
from util import Utility, Instruction
from instructions import Instructions
from exceptions import InvalidInstruction, InvalidMemoryAccess, MisalignedMemoryAccess

class CPU:
    def __init__(self, trace=False):
        self.trace_enabled = trace
        self.memory = Memory()
        self.registers = RegisterFile(self)
        self.reset()

        self.instruction_map = {0b0110011: CPU._execute_r_type,
                                0b0010011: CPU._execute_i_type,
                                0b0000011: CPU._execute_load,
                                0b0100011: CPU._execute_store,
                                0b0110111: Instructions.execute_lui,
                                0b1100011: CPU._execute_branch,
                                0b1101111: Instructions.execute_jal,
                                0b1100111: Instructions.execute_jalr,
                                0b0010111: Instructions.execute_auipc,
                                0b1110011: CPU._execute_stop}
        
        self.r_type_table = {(0b000, 0b0000000): Instructions.execute_add,
                            (0b000, 0b0100000): Instructions.execute_sub,
                            (0b110, 0b0000000): Instructions.execute_or,
                            (0b111, 0b0000000): Instructions.execute_and,
                            (0b100, 0b0000000): Instructions.execute_xor,
                            (0b001, 0b0000000): Instructions.execute_sll,
                            (0b101, 0b0000000): Instructions.execute_srl,
                            (0b101, 0b0100000): Instructions.execute_sra,
                            (0b010, 0b0000000): Instructions.execute_slt,
                            (0b011, 0b0000000): Instructions.execute_sltu}

        self.i_type_table = {0b000: Instructions.execute_addi,
                            0b100: Instructions.execute_xori,
                            0b110: Instructions.execute_ori,
                            0b111: Instructions.execute_andi,
                            0b001: Instructions.execute_slli,
                            (0b101, 0b0000000): Instructions.execute_srli,
                            (0b101, 0b0100000): Instructions.execute_srai,
                            0b010: Instructions.execute_slti,
                            0b011: Instructions.execute_sltiu}

        self.load_table = {0b000: Instructions.execute_lb,
                            0b001: Instructions.execute_lh,
                            0b010: Instructions.execute_lw,
                            0b100: Instructions.execute_lbu,
                            0b101: Instructions.execute_lhu}

        self.store_table = {0b000: Instructions.execute_sb,
                            0b001: Instructions.execute_sh,
                            0b010: Instructions.execute_sw}

        self.branch_table = {0b000: Instructions.execute_beq,
                            0b001: Instructions.execute_bne,
                            0b100: Instructions.execute_blt,
                            0b101: Instructions.execute_bge,
                            0b110: Instructions.execute_bltu,
                            0b111: Instructions.execute_bgeu}

        self.stop_table = {0b000000000001: Instructions.execute_ebreak,
                        0b000000000000: Instructions.execute_ecall}

    def reset(self):
        self.pc = 0x00400000
        self.current_instruction = 0
        self.last_rd = None
        self.memory.reset()
        self.registers.reset()

    def fetch(self):
        try:
            self.current_instruction = self.memory.load_word(self.pc)
            self.current_pc = self.pc
            self.pc += 4
            return True
        except (InvalidMemoryAccess, MisalignedMemoryAccess):
            return False

    def decode(self):
        opcode = Utility.extract_bits(self.current_instruction, 0, 6)
        rd     = Utility.extract_bits(self.current_instruction, 7, 11)
        funct3 = Utility.extract_bits(self.current_instruction, 12, 14)
        rs1    = Utility.extract_bits(self.current_instruction, 15, 19)
        rs2    = Utility.extract_bits(self.current_instruction, 20, 24)
        funct7 = Utility.extract_bits(self.current_instruction, 25, 31)
        imm = 0

        if opcode == 0b0110011:  # Tipo R
            pass

        elif opcode in [0b0000011, 0b0010011, 0b1100111, 0b1110011]:  # Tipo I e SYS
            imm = Utility.extract_bits(self.current_instruction, 20, 31)
            imm = Utility.sign_extend(imm, 12)

        elif opcode == 0b0100011:  # Tipo S
            imm_low  = Utility.extract_bits(self.current_instruction, 7, 11)
            imm = (funct7 << 5) | imm_low
            imm = Utility.sign_extend(imm, 12)

        elif opcode == 0b1100011:  # Tipo B
            b12   = Utility.extract_bits(self.current_instruction, 31, 31)
            b11   = Utility.extract_bits(self.current_instruction, 7, 7)
            b10_5 = Utility.extract_bits(self.current_instruction, 25, 30)
            b4_1  = Utility.extract_bits(self.current_instruction, 8, 11)
            imm = (b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1)
            imm = Utility.sign_extend(imm, 13)

        elif opcode in [0b0110111, 0b0010111]:  # Tipo U
            imm = Utility.extract_bits(self.current_instruction, 12, 31)
            imm = Utility.sign_extend((imm << 12), 32)

        elif opcode == 0b1101111:  # Tipo J
            b20 = Utility.extract_bits(self.current_instruction, 31, 31)
            b19_12 = Utility.extract_bits(self.current_instruction, 12, 19)
            b11 = Utility.extract_bits(self.current_instruction, 20, 20)
            b10_1 = Utility.extract_bits(self.current_instruction, 21, 30)
            imm = (b20 << 20) | (b19_12 << 12) | (b11 << 11) | (b10_1 << 1)
            imm = Utility.sign_extend(imm, 21)

        else:
            raise InvalidInstruction(f"Descodificação falhou: Opcode 0x{opcode:x} não reconhecido.")
        
        return Instruction(opcode, rd, rs1, rs2, funct3, funct7, imm)

    def execute(self, instr):
        self.last_rd = None
        func = self.instruction_map.get(instr.opcode)
        if not func:
            raise InvalidInstruction(f"Falha na execução: Opcode {bin(instr.opcode)} não suportado.")
    
        func(self, instr)

    def _execute_r_type(self, instr):
        key = (instr.funct3, instr.funct7)
        func = self.r_type_table.get(key)
        if not func:
            raise InvalidInstruction(f"Descodificação de Register falhou: funct3 0x{instr.funct3:x} não suportado.")
        func(self, instr)

    def _execute_i_type(self, instr):
        key = ((instr.funct3, instr.funct7) if instr.funct3 == 0b101 else instr.funct3)

        if instr.funct3 == 0b001:
            if instr.funct7 != 0b0000000:
                raise InvalidInstruction(f"slli inválido: funct7=0x{instr.funct7:02x} (esperado 0x00)")
        
        func = self.i_type_table.get(key)
        if not func:
            raise InvalidInstruction(f"Descodificação de Immediate falhou: funct3 0x{instr.funct3:x} não suportado.")
        func(self, instr)

    def _execute_load(self, instr):
        func = self.load_table.get(instr.funct3)
        if not func:
            raise InvalidInstruction(f"Descodificação de Load falhou: funct3 0x{instr.funct3:x} não suportado.")
        func(self, instr)

    def _execute_store(self, instr):
        func = self.store_table.get(instr.funct3)
        if not func:
            raise InvalidInstruction(f"Descodificação de Store falhou: funct3 0x{instr.funct3:x} não suportado.")
        func(self, instr)

    def _execute_branch(self, instr):
        func = self.branch_table.get(instr.funct3)
        if not func:
            raise InvalidInstruction(f"Descodificação de Branch falhou: funct3 0x{instr.funct3:x} não suportado.")
        func(self, instr)
    
    def _execute_stop(self, instr):
        func = self.stop_table.get(instr.imm)
        if not func:
            raise InvalidInstruction(f"Descodificação de Stop falhou: funct7 0x{instr.funct7:x} não suportado.")
        func(self, instr)

    def step(self):
        if self.fetch():
            instr = self.decode()
            self.execute(instr)
            return True
        return False