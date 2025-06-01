#!/usr/local/bin python3

# process logical name translations
#
# this is a proof of concept to see if the idea is feasible. Right now, there is a single dictionary of logical tables.
# this could be expanded or even made hierarchical - trees make it more complex and I don't think they're required.
#
# python dictionaries are a great approximation of a logical table.
# conveniently, entries in a dictionary can also be a dictionary (or list, or any object type)
# logicals are basically name-value pairs (except when they are other tables, or lists of logicals)
#
# actual implementation would be a server process handling all the logical name requests
# setting, getting, clearing, etc.
#
# communication with be via UNIX DOMAIN SOCKETS programs would connect via a socket to
# the server and request logical name values. (mds$logic, etc) Does it need to be
# multi-threaded, or can a single thread process requests fast enough?
#
# the server would remain in python, the clients could use any language, though I
# suspect that using C for the client interface would be the easiest implmentation (simply call the routine fromn DBL)
#
#	client connect to socket and issues request for a value.
#	Message is a logical name, or a logical name and a table name
#
#	server looks up the logical in the dictionaries and returns the values.
#
# I'd make the creation and deletion of logicals (tables / values) be on a separate
# domain socket, so it could be protected.
#
# I envision one server per node, but it could be made to use the internet socket protocol, but that introduces a bunch
# of complexities, not insurmountable, but more stuff to worry about. (requires multi-threading)
#
# so why do it this way?
#
#	1. allows for on-the-fly changes and overrides
#	2. a clever person might simply parse all the *INIT.COM files at startup and load the values from
#	   them and not have to create a database (and maintain it)
#	3. command files can override values locally when they run. (clean up is an issue, see to do below)
#	4. python dictionaries handle most of the complex stuff for free. (the routines below are very simple code)
#	5. preserves some of the VMS feel
#	6. command line level commands can be writtent to allow changes in terminal window
#	7. a gui interface woud likewise be fairly straightforward to implment.
#
# to be done with the protoype (in no particular order):
#
#	1. recursive translations - do we want to implement all the attributes VMS
#	   has, like concealed, terminal, etc? (I'd vote no, but that could impact things more)
#
#	2. the server logic needs to be written (lots of python examples out there)
#
#	3. error handling - this is almost totally happy path logic.
#
#	4. user level logicals,i.e. local overrides defined at the process level.
#	   my initial thought is a set of dictionaries that include a PID or other attribute
#	   this would always default to the first entry in a search list. The trick is cleaning them
#	   up when the process terminates. (this will require some thought - easiest is to include a command in the logout)
#

# --------------------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------------------

LOGICAL_TABLES = {}	# holder of all tables
NAMED_SEARCHES = {}	# holder of search lists organized by named key values
SEARCH_ORDER   = []	# a generic search order (should be the default)

# --------------------------------------------------------------------------------
# add a logical to a table (table is created if it doesn't exist  - is this ok?)
# --------------------------------------------------------------------------------
def addLogical(table, logical, value):

	if LOGICAL_TABLES.get(table) == None:
		LOGICAL_TABLES[table] = dict()

	if logical != None:
		thisTable = LOGICAL_TABLES[table]
		thisTable[logical] = value

	return

# --------------------------------------------------------------------------------
# get all the logicals in a table
# --------------------------------------------------------------------------------
def getLogicals(table):

	if LOGICAL_TABLES.get(table) == None:
		return None
	else:
		return LOGICAL_TABLES[table]

# --------------------------------------------------------------------------------
# get all the tables in a searchList
# --------------------------------------------------------------------------------
def getSearchTables(listName):

	if listName == None or ListName == '':
		return SEARCH_ORDER

	thisList = NAMED_SEARCHES[listName]

	return thisList		# can be null


# --------------------------------------------------------------------------------
# get the value of a specific logical, first hit in search list
# --------------------------------------------------------------------------------
def getLogicalValue(logical):

# NEED TO HANDLE EMPTY SEARCH ORDER (USE FIRST TABLE FOUND)

	for table in SEARCH_ORDER:
		if LOGICAL_TABLES.get(table) != None:
			thisTable = LOGICAL_TABLES[table]

			if thisTable.get(logical) != None:
				return thisTable[logical]
	return None

# --------------------------------------------------------------------------------
# get the value of a specific logical, first hit in named search list
# --------------------------------------------------------------------------------
def getLogicalValueNamedSearch(logical, search):

	thisList = NAMED_SEARCHES[search]
	if thisList != None:
		for table in thisList:
			if LOGICAL_TABLES.get(table) != None:
				thisTable = LOGICAL_TABLES[table]

				if thisTable.get(logical) != None:
					return thisTable[logical]

	else:
		for table in SEARCH_ORDER:
			if LOGICAL_TABLES.get(table) != None:
				thisTable = LOGICAL_TABLES[table]

				if thisTable.get(logical) != None:
					return thisTable[logical]
	return None


# --------------------------------------------------------------------------------
# get the value of a specific logical, from a specific table
# --------------------------------------------------------------------------------

def getLogicalTable(table, logical):

	if LOGICAL_TABLES.get(table) != None:
		thisTable = LOGICAL_TABLES[table]

		if thisTable.get(logical) != None:
			return thisTable[logical]

	return None


# --------------------------------------------------------------------------------
# dump all the logicals in a table
# --------------------------------------------------------------------------------
def dumpValues(table):

	if table == None:
		print("\n\nNo logicals")
		return

	for key, value in table.items():
		print(f"{key} \t\t {value}")

# --------------------------------------------------------------------------------
# set the search order
# --------------------------------------------------------------------------------
def setSearchOrder(list):

	SEARCH_ORDER.clear()

	for table in list:
		SEARCH_ORDER.append(table)

# --------------------------------------------------------------------------------
# CREATE A NAMED SEARCH
# --------------------------------------------------------------------------------
def setNamedSearchOrder(name, list):

	if NAMED_SEARCHES[name] != None:
		del NAMED_SEARCHES[name]

	NAMED_SEARCHES[name] = list

# --------------------------------------------------------------------------------
# delete a entire logical table
# --------------------------------------------------------------------------------
def deleteLogicalTable(table):

	if LOGICAL_TABLES.get(table) != None:
		del LOGICAL_TABLES[table]

# --------------------------------------------------------------------------------
# delete logical from a table
# --------------------------------------------------------------------------------
def deleteLogical(table, logical):

	if LOGICAL_TABLES.get(table) != None:
		thisTable = LOGICAL_TABLES[table]

		if thisTable.get("logical") != None:
			del thisTable[logical]

# --------------------------------------------------------------------------------
# main routine
# --------------------------------------------------------------------------------
def main():

	# -- set some baseline logical values --

	addLogical("DEV$APLLOG", "MDS$CUS_ALLOW_DELETE", " ")
	addLogical("DEV$APLLOG", "MDS$CUS_BDG_TYP",      "SGS")
	addLogical("DEV$APLLOG", "MDS$CUS_CAC",          "N")
	addLogical("DEV$APLLOG", "MDS$CUS_CCH_KWD",      "                    ")
	addLogical("DEV$APLLOG", "MDS$CUS_CDU",          "CDUMAN")
	addLogical("DEV$APLLOG", "MDS$CUS_CHM",          "C")
	addLogical("DEV$APLLOG", "MDS$CUS_CHM_PAY",      "I")
	addLogical("DEV$APLLOG", "MDS$CUS_CSH_KWD",      "                    ")
	addLogical("DEV$APLLOG", "MDS$CUS_CTM_MNT",      "NYYNNYYYYNYYYYNYYYYNNNNYNNNNNNNNNNNNNNNNNNNNNNNNNN")
	addLogical("DEV$APLLOG", "MDS$CUS_FKWD",         "FOREIGN")
	addLogical("DEV$APLLOG", "MDS$CUS_FKWD_ERROR",   "@DIS:UKW_SETUP_ERROR.DIS")
	addLogical("DEV$APLLOG", "MDS$CUS_LOK",          "N")
	addLogical("DEV$APLLOG", "MDS$CTM_PROD_EDIT",    "EDIT/TPU/SECTION=CMD:KIT_TPU.TPUSECTION")
	addLogical("DEV$APLLOG", "MDS$CUS_SCDU",         "0005")
	addLogical("DEV$APLLOG", "MDS$CUS_SCH_DATE",     "19950202")
	addLogical("DEV$APLLOG", "MDS$CUS_UCC",          "1")
	addLogical("DEV$APLLOG", "MDS$CUS_XCCA",         "00001")

	# -- do some branch level overrides for testing --

	addLogical("DEV_00001$APLLOG", "MDS$CUS_ALLOW_DELETE", "Y")
	addLogical("DEV_00001$APLLOG", "MDS$CUS_BDG_TYP",      "XXX")
	addLogical("DEV_00001$APLLOG", "MDS$CUS_CAC",          "Y")
	addLogical("DEV_00001$APLLOG", "MDS$CUS_LOK",          "Y")
	addLogical("DEV_00001$APLLOG", "MDS$CTM_PROD_EDIT",    "EDIT/TPU/SECTION=CMD:KIT_TPU_NEW.TPUSECTION")

	print("\n\nDEV$APLLOG\n")

	logicals = getLogicals("DEV$APLLOG")
	dumpValues(logicals)

	print("\n\nDEV_00001$APLLOG\n")

	logicals = getLogicals("DEV_00001$APLLOG")
	dumpValues(logicals)

	setSearchOrder(["DEV_00001$APLLOG", "DEV$APLLOG"])
	print("\n\n\n\nget logical values" + '["DEV_00001$APLLOG", "DEV$APLLOG"]\n')

	print(getLogicalValue("MDS$CUS_LOK"))
	print(getLogicalValue("MDS$CTM_PROD_EDIT"))


	setSearchOrder(["DEV$APLLOG", "DEV_00001$APLLOG"])
	print("\n\n\n\nget logical values(2)" + '["DEV$APLLOG", "DEV_00001$APLLOG"]\n')

	print(getLogicalValue("MDS$CUS_LOK"))
	print(getLogicalValue("MDS$CTM_PROD_EDIT"))

	print("\n\n\nspecific logical from specific table\n\n")
	print("\nDEV_00001$APLLOG : MDS$CUS_ALLOW_DELETE = ", getLogicalTable("DEV_00001$APLLOG", "MDS$CUS_ALLOW_DELETE"))
	print("\n      DEV$APLLOG : MDS$CUS_ALLOW_DELETE = ",       getLogicalTable("DEV$APLLOG", "MDS$CUS_ALLOW_DELETE"))



#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
