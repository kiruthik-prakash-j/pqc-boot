#include <stdint.h>

extern uint8_t _sbss;
extern uint8_t _ebss;
extern uint8_t _sdata;
extern uint8_t _edata;
extern uint8_t _sidata;
extern int main(void);

void _start(void) __attribute__((section(".text.entry"), naked, noreturn));

void _start(void) {
    /* Setup stack pointer for RISC-V (rv64 / rv32) */
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        "la sp, _estack\n"
        ".option pop\n"
    );

    /* Zero out BSS section */
    uint8_t *bss = &_sbss;
    while (bss < &_ebss) {
        *bss++ = 0;
    }

    /* Copy initialized data section if sidata != sdata */
    uint8_t *src = &_sidata;
    uint8_t *dst = &_sdata;
    if (src != dst) {
        while (dst < &_edata) {
            *dst++ = *src++;
        }
    }

    main();

    while (1) {
        __asm__ volatile ("wfi");
    }
}
