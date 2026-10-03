class RISCVProcessor:
    INITIAL_REGISTERS = [
        0x00000000, 0x00000000, 0x7fffeffc, 0x10008000,
        0x00000000, 0x10010000, 0x00400000, 0x000d2a56,
        0x00000006, 0x00000001, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x1001000c, 0x00000000,
        0xff000000, 0x00000000, 0x00000014, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x7ab0014e, 0x1200ffff, 0x112ec218, 0x00a000b0
    ]

    def __init__(self):
        self.memory = {}
        self.reset()

    def reset(self):
        self.pc = 0x00400000
        self.current_instruction = 0
        self.last_rd = None
        self.registers = list(self.INITIAL_REGISTERS)
        self.clear_data_segment()

    def clear_data_segment(self):
        base_addr = 0x10010000
        for i in range(32):
            self.memory[base_addr + (i * 4)] = 0

    def load_program(self, program_dict):
        self.memory.update(program_dict)

    def fetch(self):
        if self.pc in self.memory:
            self.current_instruction = self.memory[self.pc]
            return True
        return False

    def decode(self):
        self.opcode = self.current_instruction & 0x7F

        if self.opcode == 0b0110011:  # Tipo R
            self.rd = (self.current_instruction >> 7) & 0x1F
            self.funct3 = (self.current_instruction >> 12) & 0x07
            self.rs1 = (self.current_instruction >> 15) & 0x1F
            self.rs2 = (self.current_instruction >> 20) & 0x1F
            self.funct7 = (self.current_instruction >> 25) & 0x7F

        elif self.opcode in [0b0000011, 0b0010011]:  # Tipo I
            self.rd = (self.current_instruction >> 7) & 0x1F
            self.funct3 = (self.current_instruction >> 12) & 0x07
            self.rs1 = (self.current_instruction >> 15) & 0x1F
            self.imm = (self.current_instruction >> 20) & 0xFFF
        
            if self.imm & 0x800:  # Extensão de Sinal (2'Complement)
                self.imm -= 0x1000

        elif self.opcode == 0b0100011:  # Tipo S
            self.funct3 = (self.current_instruction >> 12) & 0x07
            self.rs1 = (self.current_instruction >> 15) & 0x1F
            self.rs2 = (self.current_instruction >> 20) & 0x1F

            imm_low  = (self.current_instruction >> 7) & 0x1F
            imm_high = (self.current_instruction >> 25) & 0x7F
            self.imm = (imm_high << 5) | imm_low
        
            if self.imm & 0x800:
                self.imm -= 0x1000

        elif self.opcode == 0b1100011:  # Tipo B
            self.funct3 = (self.current_instruction >> 12) & 0x07
            self.rs1    = (self.current_instruction >> 15) & 0x1F
            self.rs2    = (self.current_instruction >> 20) & 0x1F

            b12   = (self.current_instruction >> 31) & 0x1
            b11   = (self.current_instruction >> 7) & 0x1
            b10_5 = (self.current_instruction >> 25) & 0x3F
            b4_1  = (self.current_instruction >> 8) & 0xF
            self.imm = (b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1)
            
            if self.imm & 0x1000: 
                self.imm -= 0x2000

        elif self.opcode == 0b0110111:  # Tipo U
            self.rd = (self.current_instruction >> 7) & 0x1F
            self.imm = self.current_instruction & 0xFFFFF000

        elif self.opcode == 0b1101111:  # Tipo J
            self.rd = (self.current_instruction >> 7) & 0x1F
            b20 = (self.current_instruction >> 31) & 0x1
            b19_12 = (self.current_instruction >> 12) & 0xFF
            b11 = (self.current_instruction >> 20) & 0x1
            b10_1 = (self.current_instruction >> 21) & 0x3FF
            self.imm = (b20 << 20) | (b19_12 << 12) | (b11 << 11) | (b10_1 << 1)
            
            if self.imm & 0x100000: 
                self.imm -= 0x200000

    def execute(self):
        self.last_rd = None

        if self.opcode == 0b0110011:  # Tipo R
            if self.funct3 == 0b000:
                if self.funct7 == 0b0000000:  # add
                    res = self.registers[self.rs1] + self.registers[self.rs2]
                else:  # sub
                    res = self.registers[self.rs1] - self.registers[self.rs2]
            elif self.funct3 == 0b110:  # or
                res = self.registers[self.rs1] | self.registers[self.rs2]
            elif self.funct3 == 0b111:  # and
                res = self.registers[self.rs1] & self.registers[self.rs2]
            
            if self.rd != 0:  # Garante que x0 = 0
                self.registers[self.rd] = res & 0xFFFFFFFF
                self.last_rd = self.rd

        elif self.opcode == 0b0010011:  # Tipo I (addi)
            res = self.registers[self.rs1] + self.imm
            if self.rd != 0: 
                self.registers[self.rd] = res & 0xFFFFFFFF
                self.last_rd = self.rd

        elif self.opcode == 0b0000011: # Tipo I (lw)
            addr = self.registers[self.rs1] + self.imm
            if self.rd != 0: 
                self.registers[self.rd] = self.memory.get(addr, 0)
                self.last_rd = self.rd

        elif self.opcode == 0b0100011:  # Tipo S
            addr = self.registers[self.rs1] + self.imm
            self.memory[addr] = self.registers[self.rs2]

        elif self.opcode == 0b0110111:  # Tipo U
            if self.rd != 0: 
                self.registers[self.rd] = self.imm
                self.last_rd = self.rd

        elif self.opcode == 0b1100011:  # Tipo B
            if self.funct3 == 0b000: # beq
                if self.registers[self.rs1] == self.registers[self.rs2]:
                    self.pc += (self.imm - 4) 

        elif self.opcode == 0b1101111:  # Tipo J
            if self.rd != 0: 
                self.registers[self.rd] = self.pc + 4  # Guarda o endereço da próxima instrução
                self.last_rd = self.rd
            self.pc += (self.imm - 4) # Salta para o destino

    def trace(self):
        reg_info = f" | x{self.last_rd}={self.registers[self.last_rd]:x}" if self.last_rd else ""
        print(f"PC: [0x{self.pc:08x}] | Instr: 0x{self.current_instruction:08x}{reg_info}")
    
    def step(self):
        if self.fetch():
            self.decode()
            self.execute()
            self.trace()
            self.pc += 4
            return True
        return False

def assemble(asm_lines):
    info = {'add':  ['R', '0110011', '000', '0000000'], 'sub':  ['R', '0110011', '000', '0100000'],
        'and':  ['R', '0110011', '111', '0000000'], 'or':   ['R', '0110011', '110', '0000000'],
        'addi': ['I', '0010011', '000'], 'lw':   ['I', '0000011', '010'], 'sw':   ['S', '0100011', '010'],
        'beq':  ['B', '1100011', '000'], 'lui':  ['U', '0110111'], 'jal':  ['J', '1101111']}

    program = {}
    current_address = 0x00400000

    for line in asm_lines:
        tokens = line.replace(",", " ").replace("(", " ").replace(")", " ").split()
        if not tokens: 
            continue
        
        op_name = tokens[0]
        meta = info[op_name]
        itype = meta[0]
        binary = ""

        if itype == 'R':
            rd, rs1, rs2 = [format(int(t[1:]), '05b') for t in tokens[1:4]]
            binary = meta[3] + rs2 + rs1 + meta[2] + rd + meta[1]

        elif itype == 'I':
            rd = format(int(tokens[1][1:]), '05b')
            if op_name == 'lw':
                imm_val = int(tokens[2])
                rs1_val = int(tokens[3][1:])

            elif op_name == 'addi':
                rs1_val = int(tokens[2][1:])
                imm_val = int(tokens[3])

            rs1 = format(rs1_val, '05b')
            imm = format(imm_val & 0xFFF, '012b')
            binary = imm + rs1 + meta[2] + rd + meta[1]

        elif itype == 'S':
            rs2 = format(int(tokens[1][1:]), '05b')
            imm = format(int(tokens[2]) & 0xFFF, '012b')
            rs1 = format(int(tokens[3][1:]), '05b')
            binary = imm[:7] + rs2 + rs1 + meta[2] + imm[7:] + meta[1]

        elif itype == 'B':
            rs1 = format(int(tokens[1][1:]), '05b')
            rs2 = format(int(tokens[2][1:]), '05b')
            imm = format(int(tokens[3]) & 0x1FFF, '013b')
            binary = imm[0] + imm[2:8] + rs2 + rs1 + meta[2] + imm[8:12] + imm[1] + meta[1]

        elif itype == 'U':
            rd = format(int(tokens[1][1:]), '05b')
            imm = format(int(tokens[2]) & 0xFFFFF, '020b')
            binary = imm + rd + meta[1]

        elif itype == 'J':
            rd = format(int(tokens[1][1:]), '05b')
            imm = format(int(tokens[2]) & 0x1FFFFF, '021b')
            binary = imm[0] + imm[10:20] + imm[9] + imm[1:9] + rd + meta[1]

        program[current_address] = int(binary, 2)
        current_address += 4

    return program







codigo_asm =  [
    "addi x1, x0, 10",    # x1 = 10
    "addi x2, x0, 10",    # x2 = 10
    "beq x1, x2, 8",      # Como 10 == 10, DEVE saltar 8 bytes
    "addi x10, x0, 999",   # Esta linha DEVE SER PULADA (PC 0x40000c)
    "addi x4, x0, 1"      # Destino do salto (PC 0x400010)
]

programa_binario = assemble(codigo_asm)
cpu = RISCVProcessor()
cpu.load_program(programa_binario)

print("--- Início da Simulação ---")
while cpu.step():
    pass
print("--- Fim da Simulação ---")

if cpu.registers[10] == 0 and cpu.registers[4] == 1:
    print("✅ Sucesso! O processador ignorou x10 e saltou para x4.")
else:
    print(f"❌ Erro! O valor de x10 é {cpu.registers[10]}. O salto falhou.")