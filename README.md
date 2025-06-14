# Logicals

This project is a proof of concept aimed at emulating OpenVMS logicals and logical tables.
This is not meant to be a production grade effort, only to demonstrate the concepts are valid.

This code is not optimal, error handling is almost non-existant, and I'm sure there are better ways of doing things.

The project currently consists of the following parts:

logicalServer.py - logical server to handle all aspects of dealing with logicals and logical tables
parsecomfile.py   - command file parser, handles VMS style command files that set logicals (with limitations)
readlogical.py   - logical value get demonstrator
APLINIT_CUS.txt  - sample logical command file (*.txt) from a VMS system
rtl_logic.c      - C routine to allow accessing of logicals from programs in other languages
logicals.py      - python methods for logicals, used by the logical server.


the parser does not do DCL value replacments, so you need to either add this capability, or do what I did for testing and hard code the environment value
so, 'CUR_ENV' was replaced with DEV_00423 for testing in my txt file

The server is entirely in Python. I added a C client to allow for the setting and getting of logicals. 

The server will remain in Python. This is because the entire emulation is built around Python's dictionary and list capabilities.
I considered implmenting it in RUST, but realized it would be far too cumbersome to do even trivial things that python does.

The server is single threaded. Again, this is a POC, not production. Ideally it would be multi-threaded to handle requests simulaneously, as well as implment a 
garbage collection thread for process level logicals and search lists.

A logical, in simplest terms, is simply a name-value pair.
logicals exist in tables. Tables are named. a table can contain other tables. tables can be organized in search lists, which controls the order in which
tables are searched to provide a value for a named logical.

searchlist [table1, table2, table3]
table1 {logical:value, logical2:value,...logicaln:value}
table2 {logical:value, logical2:value,...logicaln:value}
table3 {logical:value, logical2:value,...logicaln:value}

in the example above, the search list contains three logical tables, table 1, table 2, and table 3. The order they appear in the search list is
the order that they will be searched for the named logical. The first match is returned.

search list should always look for a table called LNM$PROCESS_<pid>, this should be the first entry in the list.
The last entry in the list should always be LNM$SYSTEM. This is not implemented at this time.
Search lists are always named. In the event of no named search lists being in effect for a process, then the process and system tables should be in a default list.

LNM$PROCESS should have a limited lifespan and go away when the process exits. a possible solution would be a garbage collectioon thread in the server that walks through 
the LNM$PROCESS tables and checks to see if the process is still alive. Any processes not found would result in the table being deleted. The issue of re-using PIDs by the underlying
OS is a concern (the code is partially written, but commented out)

Limitations of this approach:

1. This is not integrated with the OS, so each application is entirely responsible for requesting translations and using the values accordingly. On OpenVMS, the OS would
   handle a file name like:    user$dat:customer.ism, translating the user$dat into the appropriate path without any awareness of the application.

2. recursion. No recursion is implemented in the translation method. Right now, that logic would need to be implemented, either in the server, or the rtl_logical.c routine. 
   (it could be handled by the application, alternatively.)

3. (Completed - UDP was replaced) UDP vs TCP/IP sockets - UDP is connectionless and has no guaranteed delivery. It probably would be worth the effort of using TCP/IP sockets for production.

4. Search lists. This is currently under developed and needs addressing. I would think that these could be pre-defined into environments, with a process level environment logical
   indicating which search list to use. something like USER$ENV with a value of: DEV_00423, defined in table: LNM$PROCESS_000123, for the process with PID 123. This should reasult in
   the search list dev_00423$search being mapped into the LNM$PROCESS_000123 logical USER$SEARCH_LIST (search lists are functional, need to incorporate SYSTEM tables and process level logicals)

5. (Completed - server fires a thread for each request) The server is currently single threaded.



