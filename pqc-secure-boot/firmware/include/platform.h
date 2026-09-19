#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Platform identifiers */
#define PLATFORM_HOST       0
#define PLATFORM_RISCV_VIRT 1
#define PLATFORM_MPS2_AN385 2
#define PLATFORM_ARM_VIRT   3

/* Hardware UART MMIO Base Addresses */
#define RISCV_VIRT_UART_BASE 0x10000000U
#define MPS2_AN385_UART_BASE 0x40004000U
#define ARM_VIRT_UART_BASE   0x09000000U

/* Hardware Driver API */
void platform_init(void);
void platform_uart_putchar(char c);
void platform_uart_puts(const char *s);
void platform_uart_print_hex(const uint8_t *data, size_t len);
void platform_halt(int status) __attribute__((noreturn));

/* Platform info strings */
const char *platform_get_name(void);

#ifdef __cplusplus
}
#endif

#endif /* PLATFORM_H */
