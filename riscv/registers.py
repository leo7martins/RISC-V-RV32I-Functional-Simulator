class RegisterFile:
    initial_values = [0x00000000, 0x00000000, 0x7fffeffc, 0x10018000,
                    0x00000000, 0x10010000, 0x00400000, 0x000d2a56,
                    0x00000006, 0x00000001, 0x00000000, 0x00000000,
                    0x00000000, 0x00000000, 0x00000000, 0x00000000,
                    0x00000000, 0x00000000, 0x1001000c, 0x00000000,
                    0xff000000, 0x00000000, 0x00000014, 0x00000000,
                    0x00000000, 0x00000000, 0x00000000, 0x00000000,
                    0x7ab0014e, 0x1200ffff, 0x112ec218, 0x00a000b0]

    def __init__(self, cpu):
        self.cpu = cpu
        self.reset()

    def reset(self):
        self.regs = list(self.initial_values)

    def validate_index(self, reg_index):
        if not (0 <= reg_index < 32):
            raise ValueError(f"Índice de registador inválido: x{reg_index}. Deve estar entre 0 e 31.")
        
    def read(self, reg_index):
        self.validate_index(reg_index)
        return self.regs[reg_index]

    def write(self, reg_index, value):
        self.validate_index(reg_index)
        if reg_index != 0:
            self.regs[reg_index] = value & 0xFFFFFFFF
            self.cpu.last_rd = reg_index