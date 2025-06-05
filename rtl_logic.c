// ------------------------------------------------------------------------------------------
// rtl_logic        routine to perform logical name operations (get, set, delete)
//
// Parameter        Description
// ---------------- -------------------------------------------------------------------------
// logNam           pointer to null terminated string used to hold the logical name
//
// oper             character holding operation to be performed
//                  values:
//                            'C' - create (set) logical
//                            'D' - delete a logical
//                            'R' - recursively translate a logical
//                            'T' - translate logical
//
// logVal           pointer to string to recieve or holding logical value
//
// logLen           pointer to integer to recieve length of logical value
//
// table            pointer to string holding the table name
//
// warn             character flag indicating whether or not to echo error messages
//                  or warnings to stdout.
//                  values:
//                            'N' - do not echo error messsages
//                            'Y' - echo error messages
//
// ------------------------------------------------------------------------------------------
// revision history
//
// author            Date         Modification(s)
// ---------------- ------------ -----------------------------------------------------------
// Tim Lovern       30-MAY-2025  initial release
//
// Tim Lovern       03-JUN-2025  Implemented TCP/IP sockets instead of UDP
//                               discovered the C libraries don't like the use of "localhost"
//                               unlike python, and require 127.0.0.1 instead
//
// Tim Lovern       06-JUN-2025  Minor clean up
//
// ------------------------------------------------------------------------------------------

#include <arpa/inet.h>
#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#define SERVER_IP "127.0.0.1"                         // C lib doesn't like "localhost"
#define PORT_NUMBER 5050                              // this is probably a stupid port choice
#define BUFFER_SIZE 1024                              // I don't think any logicals are larger than this

// ------------------------------------------------------------------------------------------
// to do:
//
// if no table name is given, need to look for a lnm$process_<PID> table
// need to implement default search list: lnm$process_<PID>, lnm$group_<??>, lnm$system
// need to figure out how group will work. (I'm thinking group doesn't get implemented)
// using the VMS style table names is also not a given - just using them to keep the implementation
// rationalized against VMS for checking operations
//
// I am leaning towards having the server keep a thread that checks for PIDs going away and doing
// garbage collection on process logicals. (this may be too complex - an alternative is to see if
// there is an event I can catch when a process exits) pidfd_open may be what I need in conjuction with
// poll
//
// add pid to all calls as the last parameter
//
// where do env level lists fall in? before or after all the above, or after process only?
// we don't necessarily need 100% emulation of OpenVMS behaviors, just consistency that makes
// some semblance of reasonable.
//
// need to add the environment into the arglist - this will control which tables are searched
// in lieu of a specific table. Might be able to use an oper and re-use the table for the env name
// other option is to declare " extern char cur_env "
// ------------------------------------------------------------------------------------------

int rtl_logic(char *logNam, char oper, char *logVal, int *logLen, char *table, char warn)
{
         int                        client_socket,
                                    cmdLen = 0;

	struct sockaddr_in         server_address;

         char                       buffer[BUFFER_SIZE],
                                    theCmd[BUFFER_SIZE],
                                    *closeCmd = "CLOSE",
                                    PID[7] = {0,0,0,0,0,0,0};

         static int                 myPid = 0;

         // --------------------------------------------------
         // initialize variables
         // --------------------------------------------------
         if (myPid == 0)
                  myPid =  getpid();

         sprintf(PID, "%06d", myPid);

         // --------------------------------------------------
         // build the socket stuff and connect to the server
         // --------------------------------------------------
         client_socket = socket(AF_INET, SOCK_STREAM, 0);
         if (client_socket < 0)
         {
                  perror("socket");
                  return 1;
         }

         server_address.sin_family       = AF_INET;
         server_address.sin_port         = htons(PORT_NUMBER);
         server_address.sin_addr.s_addr  = inet_addr(SERVER_IP);

	// Connect to the server
	if (connect(client_socket, (struct sockaddr *)&server_address, sizeof(server_address)) < 0)
	{
		perror("Connection failed");
		exit(EXIT_FAILURE);
	}

         // --------------------------------------------------
         // what are we trying to do?
         // --------------------------------------------------
         switch(oper)
         {
                  // ----------------------------------------
                  // create / set (define) a logical
                  // ----------------------------------------
                  case 'C':
                  	// --------------------------------------------------
                  	// build the set command, we are assuming for testing
                  	// that: logNam and table have been trimmed
                  	// appropriately by the calling routine
                  	// --------------------------------------------------
                  	memset(theCmd, 0, BUFFER_SIZE);

                           sprintf(theCmd, "SET,%s,%s,%s", logNam, table, logVal);

                           cmdLen = strlen(theCmd);

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen, 0) == -1)
                           {
                                    perror("send");
                                    close(client_socket);
                                    return 1;
                           }

                           break;

                  // ----------------------------------------
                  // delete (deassign) a logical
                  // ----------------------------------------
                  case 'D':
                  	// --------------------------------------------------
                  	// build the del command, we are assuming for testing
                  	// that: logNam and table have been trimmed
                  	// appropriately by the calling routine
                  	// --------------------------------------------------
                  	memset(theCmd, 0, BUFFER_SIZE);

                           sprintf(theCmd, "DEL,%s,%s", logNam, table);

                           cmdLen = strlen(theCmd);

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen, 0) == -1)
                           {
                                    perror("send");
                                    close(client_socket);
                                    return 1;
                           }

                           break;

                  // ----------------------------------------
                  // recursively translate until fully qualified
                  // ----------------------------------------
                  case 'R':
                           // who should be responsible for this?
                           // should we (this routine) or the server process this?
                           break;

                  // ----------------------------------------
                  // translate logical (return first hit)
                  // ----------------------------------------
                  case 'T':
                  	// --------------------------------------------------
                  	// build the get command, we are assuming for testing
                  	// that: logNam and table have been trimmed
                  	// appropriately by the calling routine
                  	// --------------------------------------------------
                  	memset(theCmd, 0, BUFFER_SIZE);

                           sprintf(theCmd, "GET,%s,%s", logNam, table);

                           cmdLen = strlen(theCmd);

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen, 0) == -1)
                           {
                                    perror("send");
                                    close(client_socket);
                                    return 1;
                           }

                           memset(buffer, 0, BUFFER_SIZE);
                           if (read(client_socket, buffer, BUFFER_SIZE) == -1)
                           {
                                    perror("read");
                                    close(client_socket);
                                    return 1;
                           }

                  	memcpy(logVal, buffer, strlen(buffer));      // we are assuming logVal is big enough
                  	*logLen = strlen(buffer);

                           break;
         }

         // --------------------------------------------------
         // close the socket and declare victory
         // --------------------------------------------------

         close(client_socket);
         return 0;
}
