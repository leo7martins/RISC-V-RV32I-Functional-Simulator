# Fibonacci iterativo: imprime F(10) = 55
# Demonstra: ciclo com branch, atualização de vários registos e pseudo-instruções.

start:
    addi t0, zero, 0        # a = F(0) = 0
    addi t1, zero, 1        # b = F(1) = 1
    addi t2, zero, 10       # n = 10
    addi t3, zero, 0        # i = 0

loop:
    bge  t3, t2, done
    add  t4, t0, t1         # next = a + b
    mv   t0, t1             # a = b
    mv   t1, t4             # b = next
    addi t3, t3, 1
    j    loop

done:
    mv   a0, t0             # a0 = F(10)
    addi a7, zero, 1        # syscall 1: print_int
    ecall
    addi a7, zero, 10       # syscall 10: exit
    ecall
