from util import Utility
from exceptions import MisalignedMemoryAccess, InvalidMemoryAccess

class Memory:
    def __init__(self):
        self.memory = {}
        self.TEXT_START = 0x00400000
        self.TEXT_END   = 0x00500000
        self.DATA_START = 0x10010000
        self.DATA_END   = 0x10020000
        self.STACK_START = 0x7FFF0000
        self.STACK_END   = 0x80000000

    def reset(self):
        self.memory.clear()
        base_addr = self.DATA_START
        for i in range(32):
            self.memory[base_addr + (i * 4)] = 0

    def load_program(self, program):
        self.memory.update(program)
    
    def exists(self, address, size=1):
        end_addr = address + size
        is_in_text = (address >= self.TEXT_START and end_addr <= self.TEXT_END)
        is_in_data = (address >= self.DATA_START and end_addr <= self.DATA_END)
        is_in_stack = (address >= self.STACK_START and end_addr <= self.STACK_END)
        return is_in_text or is_in_data or is_in_stack

    def _validate_access(self, address, size, write=False):
        if not self.exists(address, size):
            raise InvalidMemoryAccess(f"Endereço 0x{address:08x} fora do range permitido")

        if write:
            end_addr = address + size
            if address >= self.TEXT_START and end_addr <= self.TEXT_END:
                raise InvalidMemoryAccess(f"Escrita proibida no segmento de texto (0x{address:08x}) — read-only")

    def load_byte(self, address, signed=True):
        self._validate_access(address, 1)
        value = self.memory.get(address, 0)

        if signed:
            return Utility.sign_extend(value, 8)
        return Utility.zero_extend(value, 8)

    def load_half(self, address, signed=True):
        if address % 2 != 0:
            raise MisalignedMemoryAccess("Erro de alinhamento: Halfword exige múltiplo de 2")

        self._validate_access(address, 2)
        imm_low = self.memory.get(address, 0)
        imm_high = self.memory.get(address + 1, 0)
        value = (imm_high << 8) | imm_low
        
        if signed:  
            return Utility.sign_extend(value, 16)
        return Utility.zero_extend(value, 16)

    def load_word(self, address):
        if address % 4 != 0:
            raise MisalignedMemoryAccess("Erro de alinhamento: Word exige múltiplo de 4")
        
        self._validate_access(address, 4)
        imm_0 = self.memory.get(address, 0)
        imm_1 = self.memory.get(address + 1, 0)
        imm_2 = self.memory.get(address + 2, 0)
        imm_3 = self.memory.get(address + 3, 0)
        
        return (imm_3 << 24) | (imm_2 << 16) | (imm_1 << 8) | imm_0

    def store_byte(self, address, value):
        self._validate_access(address, 1, write=True)
        self.memory[address] = Utility.zero_extend(value, 8)

    def store_half(self, address, value):
        if address % 2 != 0:
            raise MisalignedMemoryAccess("Erro de alinhamento")
        self._validate_access(address, 2, write=True)

        self.memory[address] = Utility.extract_bits(value, 0, 7)
        self.memory[address + 1] = Utility.extract_bits(value, 8, 15)

    def store_word(self, address, value):
        if address % 4 != 0:
            raise MisalignedMemoryAccess("Erro de alinhamento")
        self._validate_access(address, 4, write=True)
            
        value = value & 0xFFFFFFFF
        self.memory[address] = Utility.extract_bits(value, 0, 7)
        self.memory[address + 1] = Utility.extract_bits(value, 8, 15)
        self.memory[address + 2] = Utility.extract_bits(value, 16, 23)
        self.memory[address + 3] = Utility.extract_bits(value, 24, 31)