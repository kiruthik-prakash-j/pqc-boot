#include "platform.h"
#include <stdio.h>
#include <stdlib.h>

void platform_init(void) {
    /* Host native stdout init */
    setvbuf(stdout, NULL, _IONBF, 0);
}

void platform_uart_putchar(char c) {
    putchar(c);
}

void platform_uart_puts(const char *s) {
    fputs(s, stdout);
}

void platform_uart_print_hex(const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02X", data[i]);
    }
}

const char *platform_get_name(void) {
    return "Host Native Runner (Linux x86_64)";
}

void platform_halt(int status) {
    exit(status);
}
