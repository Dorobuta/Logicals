#
# LogicalServer.py
#
#	This module provides a TCP/IP socket based server to full requests for
#	getting and defining logical values, a la OpenVMS
#
#	this is not meant as a 100% authentic implementation of the VMS logical
#	structure, but a reasonable facsimile of it with behaviors that are consistent
#	with it.
#
#	obviously, logicals are not utilized by the undferlying OS, so the applications
#	need to do any file name translations, or path translations internally
#
#
import logicals
import socket
import sys
import os
import threading


# --------------------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------------------
server_address = 'localhost'
port           = 5050		# need a better port number
closeSocket    = False
disconnect     = False


# --------------------------------------------------------------------------------
# define the server section - listen for connection and spawn threads
# --------------------------------------------------------------------------------

def server():

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((server_address, port))
	server_socket.listen()

	print(f"Listening on {server_address}:{port}")

	while globals()['closeSocket'] == False:
		client_socket, address = server_socket.accept()
		client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
		client_thread.start()


# --------------------------------------------------------------------------------
# handle a connection in a thread
# --------------------------------------------------------------------------------
def handle_client(client_socket, address):

	print(f"Accepted connection from {address}")
	while True:
		try:
			data = client_socket.recv(1024)
			if not data:
				break

#			print(f"Received: {data.decode()} from {address}")
			processRequest(data.decode("utf-8"), client_socket, address)

		except ConnectionResetError:

			print(f"Connection reset by {address}")
			break

	client_socket.close()
#	print(f"Connection closed from {address}")



# --------------------------------------------------------------------------------
# do the actual work
# --------------------------------------------------------------------------------
def processRequest(thisRequest, client_socket, address):

	tableName      = ""
	searchName     = ""
	logicalName    = ""
	logicalValue   = ""

	argList        = []
	tmpList        = []

	splitChar      = 0x01

	argList.clear()


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
				client_socket.send(logicalValue.encode("utf-8"))
			else:
				client_socket.send("###@@@!!!".encode("utf-8"))


		# ---------------------------------------------
		# get the value of a logical using named list
		# ---------------------------------------------
		case "GTN":

			print("get requested")

			logicalName = argList[1]
			SearchName   = argList[2]

			logicalValue = logicals.getLogicalValueNamedSearch(tableName, searchName)

			if logicalValue != None:
				client_socket.send(logicalValue.encode("utf-8"))
			else:
				client_socket.send("###@@@!!!".encode("utf-8"))

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

			print(f"SLN: {searchName} = {tmpList}")

			logicals.setNamedSearchOrder(searchName, tmpList)

		# ---------------------------------------------
		# shutdown and exit
		# ---------------------------------------------
		case "SHUTDOWN":
			print("shutdown requested...")
			globals()['closeSocket'] = True

		# ---------------------------------------------
		# close connection (deprecated)
		# ---------------------------------------------
		case "CLOSE":
			print("Close connection requested...")

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

	server()
	exit()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module

