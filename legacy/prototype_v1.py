def assemble():
    dic = {'add': ['R', '0110011', '000', '0000000'], 'sub': ['R', '0110011', '000', '0100000'],
        'and': ['R', '0110011', '111', '0000000'], 'or':  ['R', '0110011', '110', '0000000'],
        'lw':  ['I', '0000011', '010'], 'sw':  ['S', '0100011', '010']}

    with open("riscv_code.txt", "r") as riscv_code, open("machine_code.txt", "w") as machine_code:
        for line in riscv_code:
            clean_line = line.replace(",", " ").replace("(", " ").replace(")", " ")
            t = clean_line.split()
            if not t: continue

            inf = dic[t[0]]
            result = ""
            if inf[0] == "R":
                rd = format(int(t[1][1:]), "05b")
                rs1 = format(int(t[2][1:]), "05b")
                rs2 = format(int(t[3][1:]), "05b")
                result = inf[3] + rs2 + rs1 + inf[2] + rd + inf[1]
            elif inf[0] == "I":
                rd = format(int(t[1][1:]), "05b")
                imm = format(int(t[2]) & 0xFFF, "012b")
                rs1 = format(int(t[3][1:]), "05b")
                result = imm + rs1 + inf[2] + rd + inf[1]
            elif inf[0] == "S":
                rs2 = format(int(t[1][1:]), "05b")
                imm = format(int(t[2]) & 0xFFF, "012b")
                rs1 = format(int(t[3][1:]), "05b")
                result = imm[0:7] + rs2 + rs1 + inf[2] + imm[7:12] + inf[1]
            machine_code.write(result + '\n')
    pc = 0x00400000
    return pc

register_file = [
        0x00000000,  # 0
        0x00000000,  # 1
        0x7fffeffc,  # 2
        0x10008000,  # 3
        0x00000000,  # 4
        0x10010000,  # 5
        0x00400000,  # 6
        0x000d2a56,  # 7
        0x00000006,  # 8
        0x00000001,  # 9
        0x00000000, # 10
        0x00000000, # 11
        0x00000000, # 12
        0x00000000, # 13
        0x00000000, # 14
        0x00000000, # 15
        0x00000000, # 16
        0x00000000, # 17
        0x1001000c, # 18
        0x00000000, # 19
        0xff000000, # 20
        0x00000000, # 21
        0x00000014, # 22
        0x00000000, # 23
        0x00000000, # 24
        0x00000000, # 25
        0x00000000, # 26
        0x00000000, # 27
        0x7ab0014e, # 28
        0x1200ffff, # 29
        0x112ec218, # 30
        0x00a000b0  # 31
]

def memory_text_allocation(memory: dict[int, int]) -> dict[int, int]:
    with open("machine_code.txt", "r") as machine_code:
        current_address = 0x00400000 # initial PC value
        for instruction in machine_code:
            memory[current_address] = int(instruction.strip("\n"), 2) 
            current_address += 4
    return memory

def memory_data_allocation(memory: dict[int, int]) -> dict[int, int]:
    ret_memory = memory
    current_address = 0x10010000
    for _ in range(32): # 128-byte / 32-word memory
        ret_memory[current_address] = 0
        current_address += 4
    return ret_memory

def memory_init() -> dict[int, int]:
    memory = {}
    memory = memory_text_allocation(memory)
    memory = memory_data_allocation(memory)
    return memory

def main():
    pc = assemble()
    memory = memory_init()
    while pc in memory:
        instruction = memory[pc]
        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x07
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F
        pc += 4
        if opcode == 0b0110011:
            if rd == 0b00000:
                continue
            if funct3 == 0b000:
                if funct7 == 0b0000000:
                    register_file[rd] = (register_file[rs1] + register_file[rs2]) & 0xFFFFFFFF
                elif funct7 == 0b0100000:
                    register_file[rd] = (register_file[rs1] - register_file[rs2]) & 0xFFFFFFFF
            elif funct3 == 0b110:
                register_file[rd] = (register_file[rs1] | register_file[rs2])
            elif funct3 == 0b111:
                register_file[rd] = (register_file[rs1] & register_file[rs2])
        elif opcode == 0b0000011:
            if rd == 0b00000:
                continue
            imm = (instruction >> 20) & 0XFFF
            if (imm & 0x800) > 0:
                imm = imm - 0x1000
            register_file[rd] = memory[register_file[rs1] + imm]
        elif opcode == 0b0100011:
            imm = (((instruction >> 25) << 5) + ((instruction >> 7) & 0x1F)) & 0xFFF
            if (imm & 0x800) > 0:
                imm = imm - 0x1000
            memory[register_file[rs1] + imm] = register_file[rs2]