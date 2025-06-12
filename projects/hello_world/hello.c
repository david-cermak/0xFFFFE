#include <stdio.h>

int main(int argc, char *argv[])
{
	if (argc > 1) {
		printf("Hello ");
		printf(argv[1]);    // print the first argument
		printf("!\n");
	}
	return 0;
}
