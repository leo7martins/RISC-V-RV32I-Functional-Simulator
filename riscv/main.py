from cpu import CPU
from assembler import Assembler
from exceptions import (ProgramTerminated,
                        InvalidInstruction,
                        InvalidMemoryAccess,
                        MisalignedMemoryAccess)

REVERSE_ABI = {v: k for k, v in Assembler.ABI_MAP.items() if k != 'fp'}

def execute_program(program_data):
    cpu = CPU(trace=True)
    cpu.memory.load_program(program_data)
    
    print("--- Início da Execução ---\n")
    try:
        ran = False
        while cpu.step():
            ran = True
            if cpu.trace_enabled:
                print(f"PC=0x{cpu.current_pc:x}")
                print(f"INSTR=0x{(cpu.current_instruction & 0xFFFFFFFF):08x}")
                
                if cpu.last_rd is not None:
                    val = cpu.registers.read(cpu.last_rd)
                    abi_name = REVERSE_ABI.get(cpu.last_rd, f"x{cpu.last_rd}")
                    print(f"{abi_name}=0x{val:x}")
                
                print("-" * 20)

        if ran and cpu.pc not in cpu.memory.memory:
            print("\n[AVISO] Programa terminou por falta de instruções (sem ecall/ebreak).")
            
    except ProgramTerminated as e:
        print(f"\n[ENCERRAMENTO NORMAL] {e}")
        
    except (InvalidInstruction, InvalidMemoryAccess, MisalignedMemoryAccess) as e:
        failed_pc = getattr(cpu, 'current_pc', cpu.pc)
        print(f"\n[FALHA ARQUITETURAL] Erro crítico detetado no PC 0x{failed_pc:08x}.")
        print(f"Motivo: {e}")
        
    except Exception as e:
        print(f"\n[ERRO INTERNO] Exceção nativa não tratada no interpretador.")
        print(f"Motivo: {e}")
        
    print("\n--- Fim da Execução ---")

if __name__ == "__main__":
    linhas_de_codigo = [
        "start:",
        "  addi a0, zero, 5",      # Argumento: a0 = 5
        "  jal ra, process_number",# Chama a função e guarda o regresso em 'ra'
        "  addi a7, zero, 10",    # Prepara o encerramento
        "  ecall",                # Fim do programa
        
        "process_number:",
        "  addi sp, sp, -16",     # Abre espaço na Stack (16 bytes)
        "  sw ra, 12(sp)",        # Guarda o endereço de regresso na RAM
        
        "  addi a0, a0, 1",       # Soma 1 ao argumento (a0 = 6)
        "  add a0, a0, a0",       # Duplica o valor (a0 = 12 / 0xc)
        
        "  lw ra, 12(sp)",        # Recupera o endereço de regresso da RAM
        "  addi sp, sp, 16",      # Fecha o espaço da Stack
        "  jalr zero, 0(ra)"
    ]
    
    assembler = Assembler()
    programa_compilado = assembler.assemble(linhas_de_codigo)
    execute_program(programa_compilado)