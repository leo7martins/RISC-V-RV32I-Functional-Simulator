# Escreve um valor na RAM e volta a lê-lo (sw / lw).
# Demonstra: endereçamento do segmento de dados e uso de lui para carregar a base.

start:
    lui  t0, 0x10010        # t0 = 0x10010000 (início do segmento de dados)
    addi t1, zero, 1234     # valor a guardar
    sw   t1, 0(t0)          # mem[0x10010000] = 1234
    lw   a0, 0(t0)          # a0 = mem[0x10010000] = 1234

    addi a7, zero, 1        # syscall 1: print_int
    ecall
    addi a7, zero, 10       # syscall 10: exit
    ecall
