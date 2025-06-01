
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

# we need to consider the case where we get a partial request in the buffer. this will be
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
	searchName     = ""
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

			match len(argList):
				case 2:
					logicalValue = logicals.getLogicalValue(logicalName)
				case 3:
					tableName = argList[2]
					logicalValue = logicals.getLogicalTable(tableName, logicalName)


			if logicalValue != None:
				globals()['connection'].send(logicalValue.encode("utf-8"))
			else:
				globals()['connection'].send("###@@@!!!".encode("utf-8"))


		# ---------------------------------------------
		# get the value of a logical using named list
		# ---------------------------------------------
		case "GTN":

			print("get requested")

			logicalName = argList[1]
			SearchName   = argList[2]

			logicalValue = logicals.getLogicalValueNamedSearch(tableName, searchName)

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

			for item in argList[1:]:
				tmpList.append(item)

			logicals.setSearchOrder(tmpList)

		# ---------------------------------------------
		# create a named search list
		# ---------------------------------------------
		case "SLN":
			tmpList.clear()

			searchName = argList[1]

			for item in argList[2:]:
				tmpList.append(item)

			logicals.setNamedSearchOrder(searchname, tmpList)

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

