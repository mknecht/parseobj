#!/usr/bin/python
from __future__ import print_function
import traceback

from parseobj import for_key, foreach, ObjParseError, ObjSyntaxError

heading_counter = 0


def heading(text):
    global heading_counter
    heading_counter += 1
    if heading_counter > 1:
        print("\n"*3, end=None)
    print("{}. {}".format(heading_counter, text))
    print()


###############################
# PARSING
heading("Parse object structures in a functional style.")

dutchman = {
    "name": "The Flying Dutchman",
    "roles": ["The Dutchman", "Senta", "Daland"]
}


def print_uppercase_count(name):
    print(len([c for c in name if c.isupper()]))


@for_key("name", print)
@for_key("roles", foreach(print_uppercase_count)(lambda x: None))
def parse_opera(opera):
    print("The opera has two attributes")


parse_opera(dutchman)


###############################
# ERROR HANDLING
heading("Get precise error messages what is wrong with the input.")
try:
    parse_opera({"name": "Das Rheingold"})
except ObjSyntaxError:
    traceback.print_exc()


heading("Get context for your error messages")


def raise_error(value):
    if value == 3:
        raise ValueError("Value is unusable!")


try:
    foreach([1, 2, 3, 4], raise_error)
except ValueError, e:
    traceback.print_exc()


###############################
# Get the grammar.
heading("Get a pseudo-grammar for the expected input")

parse_opera.print_grammar()


###############################
# Generate example input.
