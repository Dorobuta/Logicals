
#------------------------------------------------------------------------------------------
#
# parse com file for environment definitions
#
#
#------------------------------------------------------------------------------------------


import argparse
import socket
import sys
import os

fileHandle = None
envName   = ""
connected = False
PID       = ""
HOST      = "localhost"
PORT      = 5050
parser    = None

thisSocket = None

# ------------------------------------------------------------
# initialization
# ------------------------------------------------------------

def init():

	passedArgs = list()
	passedArgs.clear()

	parser = argparse.ArgumentParser(prog='parseEnv', description="Parse file and create env search lists")

	parser.add_argument('filename',       help = 'File to parse')
	parser.add_argument('-p', '--port',   help = 'Port number override')
	parser.add_argument('-s', '--server', help = 'Server (Host) override')

	args = parser.parse_args()

	passedArgs.append(args.filename)

	if args.server != None:
		passedArgs.append(args.server)
	else:
		passedArgs.append('')

	if args.port != None:
		passedArgs.append(args.port)
	else:
		passedArgs.append('')

	return passedArgs

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

	parseThis = False

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
		parseThis = True
		retVal.append("SLN")
	else:
		if line2Parse.upper().find("CASCADE") != -1:
			parseThis = True
			retVal.append("SCL")


	if parseThis == True:

		#------------------------------------------
		#get env name - it follows '='
		#------------------------------------------

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
# end message via socket
# ------------------------------------------------------------

def setEnvironment(envList):

	print("in setEnvironment")

	if len(envList)== 0:
		return

	message = ','.join(envList)

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
# get a socket to the logical server
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

	theArgs = init()


	globals()['PID'] = f"{os.getpid():06d}"

	thisFile = openFile(theArgs[0])
	print(f"file Opened: {theArgs[0]}")

	if theArgs[1] != '' and theArgs[1] != None:
		globals()['HOST'] = theArgs[1]

	if theArgs[2] != '' and theArgs[2] != None:
		globals()['PORT'] = theArgs[2]

	print(f"Host: {globals()['HOST']} Port: {globals()['PORT']}")

	readLines(thisFile)

	thisFile.close()

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
