# Logicals

This project is a proof of concept aimed at emulating OpenVMS logicals and logical tables.
This is not meant to be a production grade effort, only to demonstrate the concepts are valid.

The project consists of the following parts:

logical server
command file parser
logical value get demonstrator
sample logical command file (*.txt)

the parser does not do DCL value replacments, so you need to either add this capability, or do what I did for testing and hard code the environment value
so, 'CUR_ENV' was replaced with DEV_00423