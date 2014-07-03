# parseobj

Helps you to parse a Python data structure.

You write your functions. Then you tell *parseobj* how they're connected. Done

*parseobj* will traverse the data for you and call your code, when it looks as expected. It will give you nice error messages, when it does not. And it prints you a pseudo-grammar for the expected input.

**Disclaimer:** This is an experiment, a search for a more pythonic way (for the user, not the library) to traverse data structures.


## How it looks

Here's a trivial object graph: an opera description.

```python
dutchman = {
    "name": "The Flying Dutchman",
    "roles": ["The Dutchman", "Senta", "Daland"]
}
```

### declarative (a bit)

Let's print the names of the operas, and for each role output the number of upper-case characters.

```python
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
```

Output:

```
2
1
1
The Flying Dutchman
```

### helpful error messages

Given invalid input, …

```python
visit_opera({"name": "Das Rheingold"})  # "roles" key missing
```

… traversing fails (as it should). The good news: *parseobj* will tell you **where** it happened and **which expectation** was not met.

```python
# (stacktrace omitted)
ObjSyntaxError: <root>: Missing key 'roles', found only: ['name']. Expected dict-like object with key 'roles'.
```

What if your own code surrenders?

```python
def raise_error(value):
    if value == "c":
        raise ValueError("Value is unusable!")

foreach("abcd", raise_error)
```

*parseobj* prepends the location to support you in figuring out what went wrong.

```
ValueError: <root>[2]: Value is unusable!
```


### pseudo-grammar

Want to figure out what valid input might look like?
Make *parseobj* print a pseudo-grammar.

```python
>>> visit_opera.print_grammar()
{
    "name": "<?>", 
    "roles": []
}
```



## Roadmap

### 0.1

- support optional elements
- support more
- Direct usability of all decorator functions
- Grammar: Indicate that other/more elements in collections/dicts are possible.
- Grammar: Consider multiple passes over list
- Proper README ;)
- proper logging (under defined logger)
- Generate random(?) minimal example
- API documentation
- Test suite
- Travis integration
- readthedocs integration
- installable using setup.py

### later

- use paths to skip levels and avoid empty functions
- make exception extension configurable
- support for **visitor objects**
- consider lengthy values when output
- support for **check-only decorators**
- support (document) **extensibility**
