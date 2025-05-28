# Logicals

This project is a proof of concept aimed at emulating OpenVMS logicals and logical tables.
This is not meant to be a production grade effort, only to demonstrate the concepts are valid.

This code is not optimal, error handling is almost non-existant, and I'm sure there are better ways of doing things.

The project consists of the following parts:

logicalServer.py - logical server to handle all aspects of dealing with logicals and logical tables
parsecomfile.py   - command file parser, handles VMS style command files that set logicals (with limitations)
readlogical.py   - logical value get demonstrator
APLINIT_CUS.txt  - sample logical command file (*.txt) from a VMS system
rtl_logic.c      - C routine to allow accessing of logicals from programs in other languages
logicals.py      - python methods for logicals, used by the logical server.


the parser does not do DCL value replacments, so you need to either add this capability, or do what I did for testing and hard code the environment value
so, 'CUR_ENV' was replaced with DEV_00423

The server is entirely in Python. I added a C client to allow for the setting and getting of logicals. 

The server will remain in Python. This is because the entire emulation is built around Python's dictionary and list capabilities.
I considered implmenting it in RUST, but realized it would be far too cumbersome to do even trivial things that python does.

A logical, in simplest terms, is simply a name-value pair.
logicals exist in tables. Tables are named. a table can contain other tables. tables can be organized in search lists, which controls the order and which
tables are searched to provide a value for a named logical.

searchlist [table1, table2, table3]
table1 {logical:value, logical2:value,...logicaln:value}
table2 {logical:value, logical2:value,...logicaln:value}
table3 {logical:value, logical2:value,...logicaln:value}

in the example above, the search list contains three logical tables, table 1, table 2, and table 3. The order they appear in the search list is
the order that they will be searched for the named logical. The first match is returned.

search list should always look for a table called LNM$PROCESS_<pid>, this should be the first entry in the list.
The last entry in the list should always be LNM$SYSTEM


