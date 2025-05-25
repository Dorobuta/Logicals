#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#define SOCKET_PATH "./logical_socket"
#define BUFFER_SIZE 1024

int main()
{
         int                        client_socket;

         struct sockaddr_un         server_address;

         char                       buffer[BUFFER_SIZE],
                                    *getCmd = "GET,MDS$CTM_PROD_EDIT,DEV_00423$APLLOG",
                                    *closeCmd = "CLOSE";

         // --------------------------------------------------
         // build the socket stuff and connect to the server
         // --------------------------------------------------
         client_socket = socket(AF_UNIX, SOCK_STREAM, 0);
         if (client_socket == -1)
         {
                  perror("socket");
                  exit(EXIT_FAILURE);
         }

         memset(&server_address, 0, sizeof(struct sockaddr_un));
         server_address.sun_family = AF_UNIX;
         strncpy(server_address.sun_path, SOCKET_PATH, sizeof(server_address.sun_path) - 1);

         if (connect(client_socket, (struct sockaddr *)&server_address, sizeof(struct sockaddr_un)) == -1)
         {
                  perror("connect");
                  close(client_socket);
                  exit(EXIT_FAILURE);
         }

         // --------------------------------------------------
         // send the get logical command to server
         // --------------------------------------------------
         printf("Connected to server.\n");

         if (send(client_socket, getCmd, strlen(getCmd), 0) == -1)
         {
                  perror("send");
                  close(client_socket);
                  exit(EXIT_FAILURE);
         }

         printf("\n command issued: %s", getCmd);
         printf("\nwaiting for response...");

         memset(buffer, 0, BUFFER_SIZE);
         if (recv(client_socket, buffer, BUFFER_SIZE, 0) == -1)
         {
                  perror("recv");
                  close(client_socket);
                  exit(EXIT_FAILURE);
         }

         printf("Received: %s\n", buffer);

         // --------------------------------------------------
         // close the socket and declare victory
         // --------------------------------------------------
         if (send(client_socket, closeCmd, strlen(closeCmd), 0) == -1)
         {
                  perror("send");
                  close(client_socket);
                  exit(EXIT_FAILURE);
         }

         close(client_socket);
         return 0;
}
