#include <stdint.h>

extern uint8_t _estack;
extern uint8_t _sbss;
extern uint8_t _ebss;
extern uint8_t _sdata;
extern uint8_t _edata;
extern uint8_t _sidata;
extern int main(void);

void _start(void) __attribute__((section(".text.entry"), naked, noreturn));

void _start(void) {
#if defined(__aarch64__)
    __asm__ volatile (
        "ldr x0, =_estack\n"
        "mov sp, x0\n"
    );
#elif defined(__arm__)
    __asm__ volatile (
        "ldr sp, =_estack\n"
    );
#endif

    uint8_t *src = &_sidata;
    uint8_t *dst = &_sdata;
    if (src != dst) {
        while (dst < &_edata) {
            *dst++ = *src++;
        }
    }

    uint8_t *bss = &_sbss;
    while (bss < &_ebss) {
        *bss++ = 0;
    }

    main();

    while (1) {
        __asm__ volatile ("wfi");
    }
}
