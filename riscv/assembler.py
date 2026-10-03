from exceptions import InvalidInstruction, AssemblerError

class Assembler:
    ABI_MAP = {'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15,
            'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21,
            's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31}

    @classmethod
    def _parse_reg(cls, reg_str):
        if reg_str in cls.ABI_MAP:
            num = cls.ABI_MAP[reg_str]

        elif reg_str.startswith('x') and reg_str[1:].isdigit():
            num = int(reg_str[1:])
            
        else:
            raise ValueError(f"Registo inválido: {reg_str}")
        
        if not (0 <= num <= 31):
            raise ValueError(f"Índice fora dos limites: {reg_str}")
            
        return format(num, '05b')


    @classmethod
    def _expand_li(cls, line):
        tokens = line.replace(",", " ").split()
        if not tokens or tokens[0] != 'li':
            return [line]
        
        if len(tokens) != 3:
            raise AssemblerError(f"Sintaxe inválida em 'li': '{line}'")
        
        try:
            val = int(tokens[2], 0)
        except ValueError:
            raise AssemblerError(f"Imediato inválido em 'li': '{tokens[2]}'")
        
        rd = tokens[1]
        
        if -2048 <= val <= 2047:
            return [f'addi {rd}, x0, {val}']

        else:
            lower = val & 0xFFF
            upper = (val >> 12) & 0xFFFFF
            if lower & 0x800:
                upper = (upper + 1) & 0xFFFFF
                lower = lower - 0x1000
            return [f'lui {rd}, {upper}', f'addi {rd}, {rd}, {lower}']


    @classmethod
    def assemble(cls, asm_lines):
        info = {'add':  ['R', '0110011', '000', '0000000'], 'sub':  ['R', '0110011', '000', '0100000'],
            'and':  ['R', '0110011', '111', '0000000'], 'or':   ['R', '0110011', '110', '0000000'], 
            'xor':  ['R', '0110011', '100', '0000000'], 'sll':  ['R', '0110011', '001', '0000000'],
            'srl':  ['R', '0110011', '101', '0000000'], 'sra':  ['R', '0110011', '101', '0100000'],
            'slt':  ['R', '0110011', '010', '0000000'], 'sltu': ['R', '0110011', '011', '0000000'],
            
            'addi': ['I', '0010011', '000'], 'xori': ['I', '0010011', '100'], 'ori':  ['I', '0010011', '110'],
            'andi': ['I', '0010011', '111'], 'slli': ['I', '0010011', '001'], 'srli': ['I', '0010011', '101'],
            'srai': ['I', '0010011', '101'],  'slti': ['I', '0010011', '010'], 'sltiu':['I', '0010011', '011'],

            'lb':   ['I', '0000011', '000'], 'lh':   ['I', '0000011', '001'], 'lw':   ['I', '0000011', '010'],
            'lbu':  ['I', '0000011', '100'], 'lhu':  ['I', '0000011', '101'], 'jalr': ['I', '1100111', '000'],
            'sb':   ['S', '0100011', '000'], 'sh':   ['S', '0100011', '001'], 'sw':   ['S', '0100011', '010'],

            'beq':  ['B', '1100011', '000'], 'bne':  ['B', '1100011', '001'], 'blt':  ['B', '1100011', '100'],
            'bge':  ['B', '1100011', '101'], 'bltu': ['B', '1100011', '110'], 'bgeu': ['B', '1100011', '111'],
            
            'lui':  ['U', '0110111'], 'auipc':['U', '0010111'], 'jal':  ['J', '1101111'], 'ebreak': ['Break', '1110011'],
            'ecall': ['SYS', '1110011']}

        base_address = 0x00400000
        symbol_table = {}
        program = {}
        parsed_instructions = []

        for line in asm_lines:
            line = line.replace('\n', ' ')
            line = line.split('#')[0].split('//')[0].strip()
            
            if not line:
                continue
            
            if ':' in line:
                parts = line.split(':', 1)
                label_part = parts[0].strip()
                instr_part = parts[1].strip()
                
                if label_part:
                    parsed_instructions.append(f"{label_part}:")
                if instr_part:
                    parsed_instructions.extend(cls._expand_li(instr_part))
            else:
                parsed_instructions.extend(cls._expand_li(line))


        current_address = base_address
        for item in parsed_instructions:
            if item.endswith(':'):
                label_name = item[:-1]
                if label_name in symbol_table:
                    raise AssemblerError(f"Etiqueta duplicada detetada: '{label_name}'")
                symbol_table[label_name] = current_address
            else:
                current_address += 4


        current_address = base_address
        for item in parsed_instructions:
            if item.endswith(':'):
                continue

            tokens = item.replace(",", " ").replace("(", " ").replace(")", " ").split()
            if not tokens: continue
            
            op_name = tokens[0]
            if op_name == 'nop':
                if len(tokens) != 1:
                    raise AssemblerError(f"'nop' não aceita argumentos: '{' '.join(tokens)}'")
                item = 'addi x0, x0, 0'
                
            elif op_name == 'mv' and len(tokens) == 3:
                item = f'addi {tokens[1]}, {tokens[2]}, 0'

            elif op_name == 'ret':
                item = 'jalr x0, 0(ra)'

            elif op_name == 'j' and len(tokens) == 2:
                item = f'jal x0, {tokens[1]}'
 
            tokens = item.replace(",", " ").replace("(", " ").replace(")", " ").split()
            if not tokens: continue

            op_name = tokens[0]
            try:
                meta = info[op_name]
                itype = meta[0]
                binary = ""

                if itype == 'R':
                    rd, rs1, rs2 = [cls._parse_reg(t) for t in tokens[1:4]]
                    binary = meta[3] + rs2 + rs1 + meta[2] + rd + meta[1]

                elif itype == 'I':
                    rd = cls._parse_reg(tokens[1])
                    if op_name in ['lw', 'lb', 'lh', 'lbu', 'lhu', 'jalr']:
                        if len(tokens) < 4:
                            raise AssemblerError(f"'{op_name}' requer formato: {op_name} rd, offset(rs1). "
                                                f"Recebido: '{' '.join(tokens)}'")
                        try:
                            imm_val = int(tokens[2], 0)
                            rs1 = cls._parse_reg(tokens[3])
                            if not (-2048 <= imm_val <= 2047):  
                                raise AssemblerError(f"Imediato {imm_val} fora do intervalo [-2048, 2047] em '{op_name}'")
                        
                        except (ValueError, IndexError):
                            raise AssemblerError(f"Erro a interpretar '{op_name}': verifica o formato offset(rs1)")
                    
                    else:
                        rs1 = cls._parse_reg(tokens[2])
                        imm_val = int(tokens[3], 0)     
                        if not (-2048 <= imm_val <= 2047):  
                            raise AssemblerError(f"Imediato {imm_val} fora do intervalo [-2048, 2047] em '{op_name}'")

                    if op_name in ['slli', 'srli', 'srai']:
                            if not (0 <= imm_val <= 31):
                                raise AssemblerError(f"Shift inválido em '{op_name}': {imm_val} "
                                                    f"(RV32I suporta apenas 0-31)")

                    if op_name == 'srai':
                        imm = format(imm_val & 0x1F, '05b')
                        binary = '0100000' + imm + rs1 + meta[2] + rd + meta[1]
                    else:
                        imm = format(imm_val & 0xFFF, '012b')
                        binary = imm + rs1 + meta[2] + rd + meta[1]

                elif itype == 'S':
                    rs2 = cls._parse_reg(tokens[1])
                    imm = format(int(tokens[2], 0) & 0xFFF, '012b')
                    rs1 = cls._parse_reg(tokens[3])
                    binary = imm[:7] + rs2 + rs1 + meta[2] + imm[7:] + meta[1]

                elif itype == 'B':
                    rs1 = cls._parse_reg(tokens[1])
                    rs2 = cls._parse_reg(tokens[2])
                    target = tokens[3]
                    
                    if target in symbol_table:
                        offset = symbol_table[target] - current_address
                    else:
                        raise AssemblerError(f"Label indefinida: '{target}'")
                            
                    imm = format(offset & 0x1FFF, '013b')
                    binary = imm[0] + imm[2:8] + rs2 + rs1 + meta[2] + imm[8:12] + imm[1] + meta[1]

                elif itype == 'U':
                    rd = cls._parse_reg(tokens[1])
                    imm = format(int(tokens[2], 0) & 0xFFFFF, '020b')
                    binary = imm + rd + meta[1]

                elif itype == 'J':
                    rd = cls._parse_reg(tokens[1])
                    target = tokens[2]
                    
                    if target in symbol_table:
                        offset = symbol_table[target] - current_address
                    else:
                        try:
                            offset = int(target, 0)
                        except ValueError:
                            raise AssemblerError(f"Label indefinida ou imediato inválido: '{target}'")
                            
                    imm = format(offset & 0x1FFFFF, '021b')
                    binary = imm[0] + imm[10:20] + imm[9] + imm[1:9] + rd + meta[1]

                elif itype == 'Break':
                    binary = "00000000000100000000000001110011"

                elif itype == 'SYS':
                    binary = "00000000000000000000000001110011"

                instr_val = int(binary, 2)
                program[current_address] = instr_val & 0xFF
                program[current_address + 1] = (instr_val >> 8) & 0xFF
                program[current_address + 2] = (instr_val >> 16) & 0xFF
                program[current_address + 3] = (instr_val >> 24) & 0xFF
            
                current_address += 4

            except KeyError:
                raise InvalidInstruction(f"Instrução não reconhecida: '{op_name}'")
            except Exception as e:
                raise InvalidInstruction(f"Erro sintático na linha '{item}'. Detalhe: {e}")

        return program