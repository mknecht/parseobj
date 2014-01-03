#!/usr/bin/python
from __future__ import print_function
import traceback

from parseobj import for_key, foreach, ObjSyntaxError

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


@foreach(print_uppercase_count)
def visit_roles(roles):
    pass


@for_key("roles", visit_roles)
@for_key("name", print)
def visit_opera(opera):
    pass


visit_opera(dutchman)


###############################
# ERROR HANDLING
heading("Get precise error messages what is wrong with the input.")
try:
    visit_opera({"name": "Das Rheingold"})
except ObjSyntaxError:
    traceback.print_exc()


heading("Get context for your error messages")


def raise_error(value):
    if value == "c":
        raise ValueError("Value is unusable!")


try:
    foreach("abcd", raise_error)
except ValueError, e:
    traceback.print_exc()


###############################
# Get the grammar.
heading("Get a pseudo-grammar for the expected input")

visit_opera.print_grammar()


###############################
# Generate example input.
