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

# --------------------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------------------

LOGICAL_TABLES    = {}	# holder of all tables
NAMED_SEARCHES    = {}	# holder of search lists organized by named key values
CASCADED_SEARCHES = {}	# holder of the names of named search lists to be searched in order
			# the idea being for test to fall thru to dev, for example
			# or train to fall thru to test and then to dev

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
		return None

	if NAMED_SEARCHES.get(listName) == None:
		return None

	thisList = NAMED_SEARCHES[listName]

	return thisList		# can be null


# --------------------------------------------------------------------------------
# get the value of a specific logical, first hit in named search list
# fall through to cascaded list
# --------------------------------------------------------------------------------
def getLogicalValueNamedSearch(logical, searchName):

	thisList    = None
	thisLogical = None

	print(f'logical: {logical} search name: {searchName}')

	if NAMED_SEARCHES.get(searchName):
		thisList = NAMED_SEARCHES[searchName]
		print(f'found named search {searchName}')

	if thisList != None:
		print(f'found list {thisList}')
		for table in thisList:
			if LOGICAL_TABLES.get(table) != None:
				thisLogical = getLogicalTable(table, logical)
				if thisLogical != None:
					return thisLogical

	print('falling into cascaded search')
	if CASCADED_SEARCHES.get(searchName) != None:
		nameList = CASCADED_SEARCHES[searchName]
		print(f'search list found for {searchName} - {nameList}')

		if nameList != None:
			for namedSearch in nameList:
				if NAMED_SEARCHES.get(namedSearch) == None:
					continue

				print(f'searching {namedSearch}')
				thisList = NAMED_SEARCHES[namedSearch]
				for table in thisList:
					if LOGICAL_TABLES.get(table) != None:
						thisLogical = getLogicalTable(table, logical)
						if thisLogical != None:
							return thisLogical

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
# CREATE A NAMED SEARCH
# --------------------------------------------------------------------------------
def setNamedSearchOrder(name, list):

	if NAMED_SEARCHES.get(name) != None:
		del NAMED_SEARCHES[name]

	NAMED_SEARCHES[name] = list

# --------------------------------------------------------------------------------
# CREATE A CASCADED SEARCH
# --------------------------------------------------------------------------------
def setCascadeSearchOrder(name, list):

	if CASCADED_SEARCHES.get(name) != None:
		del CASCADED_SEARCHES[name]

	CASCADED_SEARCHES[name] = list

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

	print("\n\n\nspecific logical from specific table\n\n")
	print("\nDEV_00001$APLLOG : MDS$CUS_ALLOW_DELETE = ", getLogicalTable("DEV_00001$APLLOG", "MDS$CUS_ALLOW_DELETE"))
	print("\n      DEV$APLLOG : MDS$CUS_ALLOW_DELETE = ",       getLogicalTable("DEV$APLLOG", "MDS$CUS_ALLOW_DELETE"))



#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()                                                          # Do not run if script is imported as a module
