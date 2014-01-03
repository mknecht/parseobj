# parseobj

Helps you to parse a Python object graph.

## Features

Here's a trivial object graph: an opera description.

```python
dutchman = {
    "name": "The Flying Dutchman",
    "roles": ["The Dutchman", "Senta", "Daland"]
}
```

### declarative syntax

Let's print the names of the operas, and for each role output the number of upper-case characters.

```python
def print_uppercase_count(name):
    print(len([c for c in name if c.isupper()]))


@for_key("name", print)
@for_key("roles", foreach(print_uppercase_count)(lambda x: None))
def parse_opera(opera):
    pass
```

Then just call your main function:

```python
parse_opera(dutchman)
```

### helpful error messages

Given wrong input, …

```python
parse_opera({"name": "Das Rheingold"})
```

… traversing fails (as it should). The good news: You'll get a helpful error message, too!

```python
# Stacktrace
ObjSyntaxError: <root>: Missing key 'roles', found only: ['name']. Expected dict-like object with key 'roles'.
```

What if your own code surrenders?

```python
def raise_error(value):
    if value == "c":
        raise ValueError("Value is unusable!")

foreach("abcd", raise_error)
```

objparse prepends the location to support you in figuring out what went wrong.

```
ValueError: <root>[2]: Value is unusable!
```


### Pseudo-grammar

Want to figure out what valid input might look like?

```python
parse_opera.print_grammar()
```

Make parseobj print a pseudo-grammar.

```python
{
    "name": "<?>", 
    "roles": []
}
```



## Roadmap

### 0.1

 - [ ] for_value
 - [ ] support optional elements
 - [ ] support more
 - [ ] Direct usability of all decorator functions
 - [ ] Grammar: Indicate that other/more elements in collections/dicts are possible.
 - [ ] Grammar: Consider multiple passes over list
 - [ ] Proper README ;)
 - [ ] proper logging (under defined logger)
 - [ ] API documentation
 - [ ] Test suite
 - [ ] Travis integration
 - [ ] readthedocs integration
 - [ ] installable using setup.py

### later

 - [ ] make exception extension configurable
 - [ ] support for **visitor objects**
 - [ ] consider lengthy values when output
 - [ ] support for **check-only decorators**
 - [ ] support (document) **extensibility**
