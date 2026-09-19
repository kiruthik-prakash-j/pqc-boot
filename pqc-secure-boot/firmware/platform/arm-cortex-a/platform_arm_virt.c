#include "platform.h"

static volatile uint32_t * const pl011_uart = (volatile uint32_t *)ARM_VIRT_UART_BASE;

void platform_init(void) {
    /* ARM PL011 UART initialization */
}

void platform_uart_putchar(char c) {
    /* Flag Register (FR) offset 0x18 -> index 6. Bit 5 is TXFF (Transmit FIFO full) */
    while (pl011_uart[6] & (1U << 5)) {
        __asm__ volatile("nop");
    }
    pl011_uart[0] = (uint32_t)c;
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
    return "QEMU arm-virt (ARM Cortex-A)";
}

void platform_halt(int status) {
    (void)status;
    while (1) {
        __asm__ volatile("wfi");
    }
}
