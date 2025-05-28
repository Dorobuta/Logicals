#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#define BUFFER_SIZE 1024

// ------------------------------------------------------------
// prototypes
// ------------------------------------------------------------
int rtl_logic(char *, char, char *, int *, char *, char);

// ------------------------------------------------------------
// start of code
// ------------------------------------------------------------
int main(int argc, char **argv)
{
int	stat = 0,
	len = 0;

char	buffer[BUFFER_SIZE];

	// ------------------------------------------------------------
	// call the logic routine and print the results
	// ------------------------------------------------------------

	memset(buffer, 0, BUFFER_SIZE);

	stat = rtl_logic("MDS$CUS_LOK", 'T', buffer, &len, "DEV_00423$APLLOG", 'a');

	printf("\n\nMDS$CUS_LOK value: {%d} %s \n", len, buffer);

	memset(buffer, 0, BUFFER_SIZE);

	stat = rtl_logic("MDS$CUS_CHM_PAY", 'T', buffer, &len, "DEV_00423$APLLOG", 'a');

	printf("\n\nMDS$CUS_CHM_PAY value: {%d} %s \n", len, buffer);

	memset(buffer, 0, BUFFER_SIZE);

	stat = rtl_logic("MDS$CUS_CTM_MNT", 'T', buffer, &len, "DEV_00423$APLLOG", 'a');

	printf("\n\nMDS$CUS_CTM_MNT value: {%d} %s \n", len, buffer);


}
