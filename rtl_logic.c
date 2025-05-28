#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#define SOCKET_PATH "./logical_socket"
#define BUFFER_SIZE 1024

// ------------------------------------------------------------------------------------------
// to do:
//
// if no table name is given, need to look for a lnm$process_<PID> table
// need to implement default search list: lnm$process_<PID>, lnm$group_<??>, lnm$system
// need to figure out how group will work.
// for now, that doesn't matter.
//
// add pid to all calls as the last parameter
//
// where doe env level lists fall in? before or after all the above, or after process only?
// we don't necessarily need 100% emulation of OpenVMS behaviors, just consistency that makes
// some semblance of reasonable.
// ------------------------------------------------------------------------------------------

int rtl_logic(char *logNam, char oper, char *logVal, int *logLen, char *table, char warn)
{
         int                        client_socket,
                                    cmdLen = 0;

         struct sockaddr_un         server_address;

         char                       buffer[BUFFER_SIZE],
                                    theCmd[BUFFER_SIZE],
                                    *closeCmd = "CLOSE",
                                    splitChar = 0x01,
                                    PID[7] = {0,0,0,0,0,0,0}

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
         client_socket = socket(AF_UNIX, SOCK_STREAM, 0);
         if (client_socket == -1)
         {
                  perror("socket");
                  return 1;
         }

         memset(&server_address, 0, sizeof(struct sockaddr_un));
         server_address.sun_family = AF_UNIX;
         strncpy(server_address.sun_path, SOCKET_PATH, sizeof(server_address.sun_path) - 1);

         if (connect(client_socket, (struct sockaddr *)&server_address, sizeof(struct sockaddr_un)) == -1)
         {
                  perror("connect");
                  close(client_socket);
                  return 1;
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
                           theCmd[cmdLen]   = splitChar;
                           theCmd[cmdLen+1] = 0;

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen+1, 0) == -1)
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
                           theCmd[cmdLen]   = splitChar;
                           theCmd[cmdLen+1] = 0;

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen+1, 0) == -1)
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
                           theCmd[cmdLen]   = splitChar;
                           theCmd[cmdLen+1] = 0;

                           // --------------------------------------------------
                           // send the get logical command to server
                           // --------------------------------------------------
                           if (send(client_socket, theCmd, cmdLen+1, 0) == -1)
                           {
                                    perror("send");
                                    close(client_socket);
                                    return 1;
                           }

                           memset(buffer, 0, BUFFER_SIZE);
                           if (recv(client_socket, buffer, BUFFER_SIZE, 0) == -1)
                           {
                                    perror("recv");
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
         if (send(client_socket, closeCmd, strlen(closeCmd), 0) == -1)
         {
                  perror("send");
                  close(client_socket);
                  return 1;;
         }

         close(client_socket);
         return 0;
}
