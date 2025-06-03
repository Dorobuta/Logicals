
#------------------------------------------------------------------------------------------

# parse com file for logical definitions

#------------------------------------------------------------------------------------------

import socket
import sys
import os

fileHandle = None
envName   = ""
connected = False
PID       = ""
HOST      = "localhost"
PORT      = 5050

thisSocket = None

# ------------------------------------------------------------
# open the file
# ------------------------------------------------------------

def openFile(fileName):

	fileHandle = open(fileName, "r")

	return fileHandle

# ------------------------------------------------------------
# process the lines in the file
# ------------------------------------------------------------

def readLines(fileHandle):

	print ("in read lines")
	logicalValues = []

	lines = fileHandle.readlines()
	for line in lines:
		print("Processing: " + line[0:10])
		logicalValues = parseLine(line)
		if logicalValues != None:
			connect2Server(HOST, PORT)
			setLogical(logicalValues)
			globals()['thisSocket'].close()

	fileHandle.close()

# ------------------------------------------------------------
# parse the line from the file
# ------------------------------------------------------------

def parseLine(line2Parse):

	print("in parseLine")

	retVal = list()

	# strip leading '$'
	if line2Parse[0:1] == '$':
		line2Parse = line2Parse[1:]

	# remove any leading whitespace
	line2Parse = line2Parse.lstrip()

	# if this line is a comment, skip it
	if line2Parse[0:1] == "!":
		return None

	if line2Parse.upper().find("DEFINE") != -1:
		#get table name - it follows '='

		idx = line2Parse.find("=")
		if idx == -1:
			return None

		idx += 1			#move past '='

		# ------------------------------------------
		# parse out the table name
		# ------------------------------------------

		tableName = ""
		tmp = line2Parse[idx:].lstrip("\t ")		# strip leading spaces and tabs
		for char in tmp:
			if char != " " and char != "\t":		# a tab or space means end of table name
				tableName += char
			else:
				break;

		idx = line2Parse.find(tableName) + len(tableName)


		# ------------------------------------------
		# parse out the logical name
		# ------------------------------------------
		logicalName = ""
		tmp = line2Parse[idx:].lstrip("\t ")		# strip leading spaces and tabs
		for char in tmp:
			if char != " " and char != "\t":		# a space or tab means end of logical name
				logicalName += char
			else:
				break;

		# ------------------------------------------
		# parse out the logical value
		# ------------------------------------------

		idx = line2Parse.find(logicalName) + len(logicalName)

		tmp = line2Parse[idx:].lstrip()			# strip leading spaces and tabs
		tmp = tmp.rstrip("\n ")				# strip trailing new line char

		if tmp[0:1] == "'" or tmp[0:1] =='"':		# closing quote or end of line is end of value
			tmp = tmp[1:]

		if tmp[-1:] == "'" or tmp[-1:] == '"':
			tmp = tmp[:-1]

		logicalValue = tmp

		# ------------------------------------------
		# assemble the list to return
		# ------------------------------------------
		retVal.clear()
		retVal.append(tableName)
		retVal.append(logicalName)
		retVal.append(logicalValue)

		return retVal

	return None

# ------------------------------------------------------------
# set the logical (send message via UDS)
# ------------------------------------------------------------

def setLogical(logicalList):

	print("in setLogical")

	if len(logicalList)== 0:
		return

	if logicalList[2] == None:
		logicalList[2] = ' '

	message = "SET," + logicalList[0] + "," + logicalList[1] + "," + logicalList[2]

	print("message: " + message)

	try:

		# Send data
		globals()['thisSocket'].send(message.encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)



	return

# ------------------------------------------------------------
# send the close connection message
# ------------------------------------------------------------
def closeMessage():

	try:

		# Send data
		tglobals()['thisSocket'].send("CLOSE".encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)


# ------------------------------------------------------------
# get a uds socket to the logical server
# ------------------------------------------------------------

def connect2Server(serverName, portNumber):

	globals()['thisSocket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		globals()['thisSocket'].connect((serverName, portNumber))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)

	return

#------------------------------------------------------------------------------------------

def main():

	globals()['PID'] = f"{os.getpid():06d}"

	thisFile = openFile('./APLINIT_CUS.txt')
	print("file Opened")

#	connect2Server(HOST, PORT)

	readLines(thisFile)

	thisFile.close()
#	closeMessage()		# tell server we are done. (deprecated)
#	thisSocket.close()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
