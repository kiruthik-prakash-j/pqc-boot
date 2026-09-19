#include <stdint.h>

extern uint8_t _estack;
extern uint8_t _sbss;
extern uint8_t _ebss;
extern uint8_t _sdata;
extern uint8_t _edata;
extern uint8_t _sidata;
extern int main(void);

void Reset_Handler(void);
void Default_Handler(void);

/* Vector Table for Cortex-M3 (MPS2-AN385) */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack), /* Initial Main Stack Pointer (MSP) */
    Reset_Handler,             /* Reset Handler */
    Default_Handler,           /* NMI Handler */
    Default_Handler,           /* HardFault Handler */
    Default_Handler,           /* MemManage Handler */
    Default_Handler,           /* BusFault Handler */
    Default_Handler,           /* UsageFault Handler */
};

void Reset_Handler(void) {
    /* Copy data section */
    uint8_t *src = &_sidata;
    uint8_t *dst = &_sdata;
    if (src != dst) {
        while (dst < &_edata) {
            *dst++ = *src++;
        }
    }

    /* Zero bss section */
    uint8_t *bss = &_sbss;
    while (bss < &_ebss) {
        *bss++ = 0;
    }

    main();

    while (1) {
        __asm__ volatile ("wfe");
    }
}

void Default_Handler(void) {
    while (1) {
        __asm__ volatile ("wfe");
    }
}
