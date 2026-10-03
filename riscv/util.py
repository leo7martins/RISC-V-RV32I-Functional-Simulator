from dataclasses import dataclass

@dataclass
class Instruction:
    opcode: int
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    funct3: int = 0
    funct7: int = 0
    imm: int = 0

    def __post_init__(self):
        if not isinstance(self.opcode, int) or self.opcode < 0:
            raise ValueError(f"Opcode inválido ou negativo: {self.opcode}")

class Utility:
    @staticmethod
    def extract_bits(value, start, end):
        if start > end or start < 0:
            raise ValueError(f"Índices de extração inválidos: start ({start}) > end ({end}).")
        shifted = value >> start
        size = end - start + 1
        mask = (1 << size) - 1
        return shifted & mask

    @staticmethod
    def sign_extend(value, bits):
        if bits <= 0:
            raise ValueError(f"Número de bits para extensão de sinal tem de ser positivo. Recebido: {bits}")
        sign_bit = 1 << (bits - 1)
        if value & sign_bit:
            return value - (1 << bits)
        return value

    @staticmethod 
    def zero_extend(value, bits):
        if bits <= 0:
            raise ValueError(f"Número de bits para extensão de zero tem de ser positivo. Recebido: {bits}")
        mask = (1 << bits) - 1
        return value & mask