# Máximo de dois números: max(42, 17) = 42
# Demonstra: branch condicional (bge) e reutilização do registo de retorno.

start:
    addi a0, zero, 42       # primeiro valor
    addi a1, zero, 17       # segundo valor
    bge  a0, a1, fim        # se a0 >= a1, a0 já é o máximo
    mv   a0, a1             # caso contrário, a0 = a1

fim:
    addi a7, zero, 1        # syscall 1: print_int
    ecall
    addi a7, zero, 10       # syscall 10: exit
    ecall
