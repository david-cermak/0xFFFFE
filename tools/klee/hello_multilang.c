#include <stdio.h>
#include <string.h>
#include <klee/klee.h>

int main() {
    char input[10];

    // Make input symbolic
    klee_make_symbolic(input, sizeof(input), "input");
    klee_assume(input[sizeof(input) - 1] == '\0');

    if (strcmp(input, "hello") == 0) {
        printf("Hello World! (English)\n");
    } else if (strcmp(input, "salut") == 0) {
        printf("Salut le Monde! (French)\n");
    } else if (strcmp(input, "ahoj") == 0) {
        printf("Ahoj Světe! (Czech)\n");
    } else if (strcmp(input, "hola") == 0) {
        printf("¡Hola Mundo! (Spanish)\n");
    } else if (strcmp(input, "ciao") == 0) {
        printf("Ciao Mondo! (Italian)\n");
    } else {
        printf("Unknown greeting!\n");
    }

    return 0;
}
