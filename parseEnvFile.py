
#------------------------------------------------------------------------------------------
#
# parse com file for environment definitions
#
#
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

	continuedLine   = False
	tmpLine         = None
	environmentList = list()

	lines = fileHandle.readlines()
	for line in lines:
		print("Processing: " + line[0:10])

		line = line.lstrip()
		line = line.rstrip("\n\t ")

		#------------------------------------------
		# handle split lines
		#     (multiple lines per statement)
		#------------------------------------------

		if line[-1:] == '-':
			if continuedLine == True:
				line = tmpLine + ' ' + line[:-2]
			else:
				continuedLine = True
				tmpLine = line[:-2]
			continue

		if continuedLine == True:
			continuedLine = False
			line =  tmpLine + ' ' + line

		#------------------------------------------
		# process the line
		#------------------------------------------

		environmentList = parseLine(line)
		if environmentList != None:
			connect2Server(HOST, PORT)
			setEnvironment(environmentList)
			globals()['thisSocket'].close()

	fileHandle.close()

# ------------------------------------------------------------
# parse the line from the file
# ------------------------------------------------------------

def parseLine(line2Parse):

	print("in parseLine")

	retVal = list()
	tableList = ""

	# strip leading '$'
	if line2Parse[0:1] == '$':
		line2Parse = line2Parse[1:]

	# remove any leading whitespace
	line2Parse = line2Parse.lstrip()

	# if this line is a comment, skip it
	if line2Parse[0:1] == "!":
		return None

	if line2Parse.upper().find("ENVLIST") != -1:
		#get env name - it follows '='

		idx = line2Parse.find("=")
		if idx == -1:
			return None

		idx += 1			#move past '='

		# ------------------------------------------
		# parse out the table name
		# ------------------------------------------

		envName = ""
		tmp = line2Parse[idx:].lstrip("\t ")		# strip leading spaces and tabs
		for char in tmp:
			if char != " " and char != "\t":		# a tab or space means end of table name
				envName += char
			else:
				break;

		idx = line2Parse.find(envName) + len(envName)


		# ------------------------------------------
		# parse out the logical name
		# ------------------------------------------
		tmp = line2Parse[idx:].lstrip("\t ").rstrip("\t\n ")		# strip leading/trailing spaces and tabs
		tmp = ''.join(filter(keepChars, tmp))			# remove embedded chars

		tableList = tmp.split(",")

		# ------------------------------------------
		# assemble the list to return
		# ------------------------------------------
		retVal.clear()
		retVal.append(envName)
		retVal.extend(tableList)

		return retVal

	return None

# ------------------------------------------------------------
# filter function to remove embedded chars we don't want
# ------------------------------------------------------------
def keepChars(thisChar):
	if len(thisChar.lstrip("\t\n ")) == 0:
		return False
	else:
		return True

# ------------------------------------------------------------
# set the logical (send message via UDS)
# ------------------------------------------------------------

def setEnvironment(envList):

	print("in setEnvironment")

	if len(envList)== 0:
		return

	message = "SLN," + ','.join(envList)

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

	thisFile = openFile('./envdefine.txt')
	print("file Opened")

	readLines(thisFile)

	thisFile.close()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
