
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

# ---------------------------------------------
# ok, now we get connections and proces them
# ---------------------------------------------

while globals()['closeSocket'] == False:

	print("looking for a connection...")

	globals()['disconnect'] = False

	clientSocket.listen(1)

	connection, client_address = clientSocket.accept()
	print('Connection from', str(connection).split(", ")[0][-4:])

	while (globals()['disconnect'] == False and globals()['closeSocket'] == False):

		request = connection.recv(1024)
		request = request.decode("utf-8")

		argList.clear()

		tableName      = ""
		logicalName    = ""
		logicalValue   = ""

		for item in request.split(","):
			argList.append(item.strip())

		if len(argList) == 0:
			continue

		match argList[0].upper():

			# ---------------------------------------------
			# set a logical / create a table
			# ---------------------------------------------
			case "SET":
				print ("set logical")
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
				tmp = 1

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
					connection.send(logicalValue.encode("utf-8"))
				else:
					connection.send("###@@@!!!".encode("utf-8"))


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

			# search list should be environment driven
			# should environment be passed with each call? probably
			# better idea would be named search lists, and/or process specific search lists.
			# may be certain tables where we need to append env to table name (prefix or suffix?)
			# table with env as logical name, search list as value

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
				connection.close()	# go back and listen...
				globals()['disconnect'] = True

			# ---------------------------------------------
			# default - we have no idea...
			# ---------------------------------------------
			case _:
				tmp = 1


exit()