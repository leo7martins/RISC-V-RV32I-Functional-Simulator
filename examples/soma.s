# Soma 1 + 2 + ... + 10 = 55
# Demonstra: ciclo com branch (bge), pseudo-instruções (mv, j) e ecall de saída.

start:
    addi t0, zero, 0        # acumulador = 0
    addi t1, zero, 1        # i = 1
    addi t2, zero, 11       # limite (exclusivo) = 11

loop:
    bge  t1, t2, done       # se i >= 11, termina
    add  t0, t0, t1         # acumulador += i
    addi t1, t1, 1          # i += 1
    j    loop

done:
    mv   a0, t0             # a0 = resultado
    addi a7, zero, 1        # syscall 1: print_int
    ecall
    addi a7, zero, 10       # syscall 10: exit
    ecall
