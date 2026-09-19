#include "platform.h"

static volatile uint8_t * const uart16550 = (volatile uint8_t *)RISCV_VIRT_UART_BASE;

void platform_init(void) {
    /* NS16550 UART initialization on RISC-V Virt */
    /* Line control reg = 3 (8 data bits, no parity, 1 stop bit) */
    uart16550[3] = 0x03;
    /* Enable FIFO */
    uart16550[2] = 0x01;
}

void platform_uart_putchar(char c) {
    /* LSR bit 5 (0x20) is THRE (Transmit Holding Register Empty) */
    while ((uart16550[5] & 0x20) == 0) {
        __asm__ volatile("nop");
    }
    uart16550[0] = (uint8_t)c;
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
    return "QEMU riscv-virt (RISC-V 64-bit)";
}

void platform_halt(int status) {
    (void)status;
    /* QEMU virt test poweroff / exit device at 0x100000 */
    volatile uint32_t *syscon = (volatile uint32_t *)0x100000U;
    *syscon = 0x5555;
    while (1) {
        __asm__ volatile("wfi");
    }
}
