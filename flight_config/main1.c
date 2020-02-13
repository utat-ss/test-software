// This program is not intended to be compiled/run. It is only in this folder
// because harness.py expects a file named main1.c.

#include <uart/uart.h>

int main(void) {
    init_uart();
    print("\n\nStarting blank program\n");
    print("Done\n");
}
