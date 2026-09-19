#include "platform.h"

static volatile uint32_t * const cmsdk_uart = (volatile uint32_t *)MPS2_AN385_UART_BASE;

void platform_init(void) {
    /* CMSDK APB UART0 init: Enable TX (bit 0 = 1) */
    cmsdk_uart[2] |= 0x01U;
}

void platform_uart_putchar(char c) {
    /* STATE offset 0x04 / 4 = index 1. Bit 0 is TXFULL */
    while (cmsdk_uart[1] & 0x01U) {
        __asm__ volatile("nop");
    }
    cmsdk_uart[0] = (uint32_t)c;
}

void platform_uart_puts(const char *s) {
    while (*s) {
        if (*s == '\n' && (s == s || *(s - 1) != '\r')) {
            platform_uart_putchar('\r');
        }
        platform_uart_putchar(*s++);
    }
}

void platform_uart_print_hex(const uint8_t *data, size_t len) {
    static const char hex_chars[] = "0123456789ABCDEF";
    for (size_t i = 0; i < len; i++) {
        platform_uart_putchar(hex_chars[(data[i] >> 4) & 0x0F]);
        platform_uart_putchar(hex_chars[data[i] & 0x0F]);
    }
}

const char *platform_get_name(void) {
    return "QEMU mps2-an385 (ARM Cortex-M3)";
}

void platform_halt(int status) {
    (void)status;
    /* Semi-hosting or halt loop for ARM Cortex-M */
    while (1) {
        __asm__ volatile("wfi");
    }
}
