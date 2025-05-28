
import logicals
import socket
import sys
import os


# --------------------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------------------
server_address = './logical_socket'
closeSocket    = False
disconnect     = False
argList        = []
tmpList        = []
tableName      = ""
logicalName    = ""
logicalValue   = ""
splitChar      = 0x01

connection     = None
client_address = None

# ---------------------------------------------
# remove socket if it already exists
# ---------------------------------------------

try:
	os.unlink(server_address)
except OSError:
	if os.path.exists(server_address):
		raise

# ---------------------------------------------
# create the socket
# ---------------------------------------------

clientSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
clientSocket.bind(server_address)

# --------------------------------------------------------------------------------
# ok, now we get connections and process them
# --------------------------------------------------------------------------------
def getRequests():

	while globals()['closeSocket'] == False:

		print("looking for a connection...")

		globals()['disconnect'] = False

		clientSocket.listen(1)

		globals()['connection'], globals()['client_address'] = clientSocket.accept()
		print('Connection from', str(connection).split(", ")[0][-4:])

		while (globals()['disconnect'] == False and globals()['closeSocket'] == False):

			request = connection.recv(1024)
			request = request.decode("utf-8")

# we need to consider the case where we get a partial request in the buffere. this will be
# indicated by a string not terminated with a splitChar
#
# I beleive we need to do another recv to get the rest of the string. we may have to
# do this multiple times because of multiple requests piling up.

			for item in request.split(chr(splitChar)):
				processRequest(item)

				if (globals()['disconnect'] == True or globals()['closeSocket'] == True):
					break


# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
def processRequest(thisRequest):

	argList.clear()

	tableName      = ""
	logicalName    = ""
	logicalValue   = ""

	for item in thisRequest.split(","):
		argList.append(item.strip())

	if len(argList) == 0:
		return

	match argList[0].upper():

		# ---------------------------------------------
		# set a logical / create a table
		# ---------------------------------------------
		case "SET":
			if argList[1] != None and argList[1] !='':
				tableName    = argList[1]

			if argList[2] != None and argList[2] !='':
				logicalName  = argList[2]

			if argList[3] != None and argList[3] !='':
				logicalValue = argList[3]
			else:
				logicalValue = ''

			logicals.addLogical(tableName, logicalName, logicalValue)
			print("Table: "+ tableName + " logical: "+ logicalName + " value: " + logicalValue)

		# ---------------------------------------------
		# delete a logical / table
		# ---------------------------------------------
		case "DEL":
			if argList[1] != None and argList[1] !='':
				tableName    = argList[1]

			if argList[2] != None and argList[2] !='':
				logicalName  = argList[2]

			logicals.deleteLogical(tableName, logicalName)

		# ---------------------------------------------
		# get the value of a logical
		# ---------------------------------------------
		case "GET":

			print("get requested")

			logicalName = argList[1]

			if len(argList) == 2:
				logicalValue = logicals.getLogicalValue(logicalName)
			else:
				tableName = argList[2]
				logicalValue = logicals.getLogicalTable(tableName, logicalName)

			if logicalValue != None:
				globals()['connection'].send(logicalValue.encode("utf-8"))
			else:
				globals()['connection'].send("###@@@!!!".encode("utf-8"))


		# ---------------------------------------------
		# change a logical value
		# ---------------------------------------------
		case "UPD":
			tmp = 1	# do nothing

		# ---------------------------------------------
		# set the table search order
		# ---------------------------------------------
		case "SEA":
			tmpList.clear()
			count = 0

			for item in argList:
				count = count+1
				if count > 1:
					tmpList.append(item)

				logicals.setSearchOrder(tmpList)

		# consider having several types of search lists:
		# one per environment for all the env tables and values
		# one per PID <- how to clean up on process exit?
		# pid is a requirement for process defined logicals
		# first entry in list should be LNM$PROCESS_<pidvalue>
		#
		# last entry should always be LNM$SYSTEM

		# ---------------------------------------------
		# shutdown and exit
		# ---------------------------------------------
		case "SHUTDOWN":
			print("shutdown requested...")
			globals()['closeSocket'] = True

		# ---------------------------------------------
		# close connection
		# ---------------------------------------------
		case "CLOSE":
			print("Close connection requested...")
			globals()['connection'].close()	# go back and listen...
			globals()['disconnect'] = True

		# ---------------------------------------------
		# default - we have no idea...
		# ---------------------------------------------
		case _:
			tmp = 1

	return

# --------------------------------------------------------------------------------
# main routine
# --------------------------------------------------------------------------------
def main():

	getRequests()
	exit()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module

