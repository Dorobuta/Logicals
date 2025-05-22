import socket
import sys

logicalValue = ""

thisSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# ------------------------------------------------------------
# get a uds socket to the logical server
# ------------------------------------------------------------

def connect2Server(serverName):

	print("in connect2Server")
	print("Server name is: " + serverName)

	try:
		thisSocket.connect(serverName)

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)

	return


# ------------------------------------------------------------
# get the value of the logical
# ------------------------------------------------------------
def getLogical(logNam, tableNam):

	tmpval = ""

	print("in getLogical")

	message = "GET,"+logNam+"," +tableNam
#	message = "GET,MDS$CUS_CTM_MNT"

	try:
		print("sending: " + message)

		# Send data
		thisSocket.send(message.encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)


	try:
		print("receiving...")

		tmpVal = thisSocket.recv(1024)

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)

	return tmpVal.decode()

# ------------------------------------------------------------
# send a close to the server
# ------------------------------------------------------------
def closeMessage():

	try:

		# Send data
		thisSocket.send("CLOSE".encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)

#------------------------------------------------------------------------------------------

def main():

	connect2Server('./logical_socket')			# connect

	logicalValue = getLogical("MDS$CUS_CTM_MNT","DEV_00423$APLLOG")		# get the logical
	print("MDS$CUS_CTM_MNT = " + logicalValue)					# print our result

	logicalValue = getLogical("MDS$CUS_LOK","DEV_00423$APLLOG")			# get the logical
	print("MDS$CUS_LOK = " + logicalValue)					# print our result

	closeMessage()					# tell server we are done.
	thisSocket.close()				# close the socket

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
