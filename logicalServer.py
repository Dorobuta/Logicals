#!/usr/local/bin python3

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
#	design notes:
#
#		logical tables are implemented as dictionaries.
#		logicals are entries in a dictionary.
#		The logical name is the key.
#
#		logical tables are entries in a master dictionary.
#		the table name is the key.
#
#		a named search is a list of table names to be searched through.
#		named searches are stored in a dictionary.
#		the name of the search is the key.
#		the list is the data.
#
#		a cascaded search is a list of search names.
#		cascaded searches are stored in a dictionary.
#		the key is the name of a named search.
#		the list is the data
#
#		a named search is the equivalent of an environment. It is
#		a collection of logical tables to be searched in a specified order
#		to find the translation of a logical
#
#		a cascaded search allows you to define base sets of tables that
#		an environment builds upon or re-defines.
#
#		for example:
#			dev$branch   -> dev   -> base
#
#		in the above example for dev, base would hold logical values that are the
#		default, or that are always identical across all environments.
#		dev holds the values that have been changed specifically for the entire development space
#		branch holds the vlaues specific to that branch
#
#		search lists defined for the example:
#
#			base   - holds all the logical tables for base
#			dev    - holds the tables and logicals that differ from base
#			branch - holds values specific for the branch
#
#		cascaded searches:
#
#			dev$branch:   [dev,base]
#			dev:          [base]
#
#		logical lookups in dev$branch would first search all the tables
#		defined in dev$branch, followed by the tables in dev, and finally in base.
#		the very first match is returned
#
#		dealing with LNM$PROCESS and LNM$SYSTEM is yet to be implemented
#
#
# DATE        AUTHOR           MODIFICATION(S)
# ----------- ---------------- ---------------------------------------------------
# 08-JUN-2025 Tim Lovern       deprecated the generic search list and replaced it
#                              with a cascade list based on entries in the named
#                              search dictionary.
#
#                              added header documentation to describe the code.
#
# 12-JUN-2025 Tim Lovern       added tableLock and processLock to protect data
#                              from race conditions across threads.
#
#                              cleaned up global references
#
# 13-JUN-2025 Tim Lovern       made logging based on global variable logConnections
#
#
#
#
import logicals
import socket
import sys
import os
import threading
import psutil
import time
import multiprocessing


# --------------------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------------------
server_address = 'localhost'
port           = 5050		# need a better port number
closeSocket    = False
disconnect     = False

processList    = list()		# used to track lnm$process_PID processes
processLock    = threading.Lock()	# lock for process level logicals
tableLock      = threading.Lock()	# lock for setting table values

logConnections = False

# --------------------------------------------------------------------------------
# define the server section - listen for connection and spawn threads
# --------------------------------------------------------------------------------

def server():

	global closeSocket
	global logConnections

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((server_address, port))
	server_socket.listen()

	# ---------------------------------------------
	# start the thread that handles process
	# level logicals (delete tables when processes die)
	# ---------------------------------------------
#	procThread = threading.thread(target=handleProcessDeaths)
#	procThread.start()

	if logConnections == True:
		print(f"Listening on {server_address}:{port}")

	while closeSocket == False:
		client_socket, address = server_socket.accept()
		client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
		client_thread.start()


# --------------------------------------------------------------------------------
# handle a connection in a thread
# --------------------------------------------------------------------------------
def handle_client(client_socket, address):

	global logConnections

	if logConnections == True:
		print(f"Accepted connection from {address}")
	while True:
		try:
			data = client_socket.recv(1024)
			if not data:
				break

			if logConnections == True:
				print(f"Received: {data.decode()} from {address}")

			processRequest(data.decode("utf-8"), client_socket, address)

		except ConnectionResetError:

			print(f"Connection reset by {address}")
			break

	client_socket.close()

	if logConnections == True:
		print(f"Connection closed from {address}")



# --------------------------------------------------------------------------------
# do the actual work
# --------------------------------------------------------------------------------
def processRequest(thisRequest, client_socket, address):

	global logConnections
	global closeSocket
	global tableLock

	tableName      = ""
	searchName     = ""
	logicalName    = ""
	logicalValue   = ""

	argList        = []
	tmpList        = []

	argList.clear()

	for item in thisRequest.split(","):
		argList.append(item.strip())

	if len(argList) == 0:
		return

	match argList[0].upper():

		# ---------------------------------------------
		# set a logical / create a table
		# [CMD, TABLE NAME, LOGICAL NAME, LOGICAL VALUE]
		# ---------------------------------------------
		case "SET":

			tableName    = argList[1]
			logicalName  = argList[2]
			logicalValue = argList[3]

			with tableLock:
				logicals.addLogical(tableName, logicalName, logicalValue)

			if logConnections == True:
				print("Table: "+ tableName + " logical: "+ logicalName + " value: " + logicalValue)

		# ---------------------------------------------
		# delete a logical
		# [CMD, TABLE NAME, LOGICAL NAME]
		# ---------------------------------------------
		case "DEL":

			tableName    = argList[1]
			logicalName  = argList[2]

			with tableLock:
				logicals.deleteLogical(tableName, logicalName)

		# ---------------------------------------------
		# get the value of a logical
		# [CMD, LOGICAL NAME, TABLE NAME]
		# ---------------------------------------------
		case "GET":

			if logConnections == True:
				print("get requested")

			logicalName = argList[1]
			tableName = argList[2]

			with tableLock:
				logicalValue = logicals.getLogicalTable(tableName, logicalName)

			if logicalValue != None:
				client_socket.send(logicalValue.encode("utf-8"))
			else:
				client_socket.send("###@@@!!!".encode("utf-8"))


		# ---------------------------------------------
		# get the value of a logical using named list
		# [CMD, LOGICAL, SEARCH LIST NAME]
		# ---------------------------------------------
		case "GTN":

			if logConnections == True:
				print("get named search requested")

			logicalName = argList[1]
			searchName   = argList[2]

			with tableLock:
				logicalValue = logicals.getLogicalValueNamedSearch(logicalName, searchName)

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
		# set the cascading named search order
		# [CMD, OWNER NAME, NAME 1,...,NAME n]
		# ---------------------------------------------
		case "SCL":
			tmpList.clear()
			searchName = argList[1]

			for item in argList[2:]:
				tmpList.append(item)

			if logConnections == True:
				print(f"SCL: {searchName} = {tmpList}")

			with tableLock:
				logicals.setCascadeSearchOrder(searchName, tmpList)

		# ---------------------------------------------
		# create a named search list
		# [CMD, SEARCH NAME, LIST 1,...,LIST n]
		# ---------------------------------------------
		case "SLN":
			tmpList.clear()

			searchName = argList[1]

			for item in argList[2:]:
				tmpList.append(item)

			if logConnections == True:
				print(f"SLN: {searchName} = {tmpList}")

			with tableLock:
				logicals.setNamedSearchOrder(searchName, tmpList)

		# ---------------------------------------------
		# shutdown and exit
		# [CMD]
		# ---------------------------------------------
		case "SHUTDOWN":

			if logConnections == True:
				print("shutdown requested...")

			with tableLock:
				closeSocket = True

		# ---------------------------------------------
		# close connection (deprecated)
		# ---------------------------------------------
		case "CLOSE":
			if logConnections == True:
				print("Close connection requested...")

		# ---------------------------------------------
		# default - we have no idea...
		# ---------------------------------------------
		case _:
			tmp = 1

	return


# --------------------------------------------------------------------------------
# thread for watching for processes with local logical definitions going away
# we have to garbage collect local definitions at the process (pid)level.
# otherwise we could have orphaned tables, pr worse get a pid recyled and
# have phantom overrides pop up.
# --------------------------------------------------------------------------------
def handleProcessDeaths(pid):

	global closeSocket
	global logConnections
	global processLock

#	howLong      = 60 * 5		# five minutes between pid checks
#	expiredList  = list()
#
#	while closeSocket == False:
#
#		expiredList.clear()
#		time.sleep(howLong)
#
#		if len(processList) == 0:
#			continue
#
#		expiredList = checkProcessTables()
#
#		if len(expiredList) != 0:
#			with processLock:
#			for pid in expiredList:
#				logicals.deleteLogicalTable(f'LNM$PROCESS_{pid}')
#				if pid in processList:
#					del processList[processList.index(pid)]
#
	return

# --------------------------------------------------------------------------------
# check for processes with tables to see if they still exist
#	should be in own thread and sleep between calls.
# --------------------------------------------------------------------------------
def checkProcessTables():

	global logConnections
	global processLock
	global processList

	deadList = list()
	deadList.clear()

	with processLock:
		for proc in processList:
			if psutil.pid_exists(proc) == False:
				deadList.append(proc)
	return deadList

# --------------------------------------------------------------------------------
# main routine
# --------------------------------------------------------------------------------
def main():

	server()
	exit()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module

