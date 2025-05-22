
#------------------------------------------------------------------------------------------

# parse com file for logical definitions

#------------------------------------------------------------------------------------------

import socket
import sys

fileHandle = None
envName = ""
connected = False

thisSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

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
			setLogical(logicalValues)

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
	while line2Parse[0:1] == ' ':
		line2Parse = line2Parse[1:]

	# if this line is a comment, skip it
	if line2Parse[0:1] == "!":
		return None

	if line2Parse.upper().find("DEFINE") != -1:
		#get table name - it follows '='

		idx = line2Parse.find("=")
		if idx == -1:
			return None

		idx += 1			#move past '='

		tableName = ""
		tmp = line2Parse[idx:]
		for char in tmp:
			if char >= "A" and char <= "z":
				tableName += char
			else:
				if char >= "0" and char <= "9":
					tableName += char
				else:
					if char == "$" or char == "_":
						tableName += char
					else:
						break;

		idx += len(tableName)

		tmp = line2Parse[idx:]
		for char in tmp:
			if char < "A" or char > "z":
				if char != "_":
					idx += 1
				else:
					break
			else:
				break

		logicalName = ""
		tmp = line2Parse[idx:]
		for char in tmp:
			if char >= "A" and char <= "z":
				logicalName += char
			else:
				if char >= "0" and char <= "9":
					logicalName += char
				else:
					if char == "$" or char == "_":
						logicalName += char
					else:
						break;

		idx += len(logicalName)

		tmp = line2Parse[idx:]
		for char in tmp:
			if char < "A" or char > "z":
				if char != "_" and char != "'" and char != '"':
					idx += 1
# do we need to parse out quotes? or do we keep them?

		logicalValue = line2Parse[idx:-1]

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

	try:

		# Send data
		thisSocket.send(message.encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)



	return

def closeMessage():

	try:

		# Send data
		thisSocket.send("CLOSE".encode("utf-8"))

	except socket.error as msg:
    		print(msg)
    		sys.exit(1)


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

#------------------------------------------------------------------------------------------

def main():

	thisFile = openFile('./APLINIT_CUS.txt')
	print("file Opened")

	connect2Server('./logical_socket')

	readLines(thisFile)

	thisFile.close()
	closeMessage()		# tell server we are done.
	thisSocket.close()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
