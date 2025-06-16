#include <stdio.h>
#include <string.h>

#define MAX_INPUT_SIZE 1024

int main(int argc, char *argv[])
{
	char input[MAX_INPUT_SIZE];

	// Read input from stdin
	if (fgets(input, MAX_INPUT_SIZE, stdin) != NULL) {
		// Remove newline if present
		input[strcspn(input, "\n")] = 0;

		printf("Hello ");
		printf(input);    // Safely print the input
		printf("!\n");
	}
	return 0;
}
