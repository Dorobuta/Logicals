# Logicals

This project is a proof of concept aimed at emulating OpenVMS logicals and logical tables.
This is not meant to be a production grade effort, only to demonstrate the concepts are valid.

This code is not optimal, error handling is almost non-existant, and I'm sure there are better ways of doing things.

The project consists of the following parts:

logical server
command file parser
logical value get demonstrator
sample logical command file (*.txt)

the parser does not do DCL value replacments, so you need to either add this capability, or do what I did for testing and hard code the environment value
so, 'CUR_ENV' was replaced with DEV_00423

The project is entirely in Python at the moment. I plan to add a C client library to allow for the setting and getting of logicals. The server will remain
in Python. This is because the entire emulation is built around Python's dictionary and list capabilities.

A logical, in simplest terms, is simply a name-value pair.
logicals exist in tables. Tables are named. a table can contain other tables. tables can be organized in search lists, which controls the order and which
tables are searched to provide a value for a named logical.

+-------------+
| search List |
+-------------+
      |
      |             +--------+
      +------------>| table 1|
      |             +--------+
      |                 |
      |                 +----> logical, value 
      |                 +----> logical, value
      |                 .
      |                 .
      |                 +----> logical, value
      |
      |             +--------+
      +------------>| table 2|
      |             +--------+
      |                 |
      |                 +----> logical, value
      |                 +----> logical, value
      |                 .
      |                 .
      |                 +----> logical, value
      |             +--------+
      +------------>| table 3|
                    +--------+
                       |
                       +----> logical, value
                       +----> logical, value
                       .
                       .
                       +----> logical, value


in the example above, the search list contains three logical tables, table 1, table 2, and table 3. The order they appear in the search list is
the order that they will be searched for the named logical. The first match is returned.


