from parseobj import for_key, for_path, ObjSyntaxError

correct = {
    "name": "Turandot Testperson",
    "req": {
        "login": True,
    },
}
optional = {
    "name": "Bob",
    "weight": 29,
    "req": {
        "login": True,
    },
}
incorrect = {
    "nme": "Kermit the Frog",
    "req": {
        "login": True,
    },
}
correct = {
    "name": "Turandot Testperson",
    "req": {
        "login": False,
    },
}

class Person(object):
    def __init__(self):
        self.email = None
        self.weight = None

    def save(self):
        print("Saving person {}".format(self.email))


def savePerson(input):
    def set_name(person, name):
        person.name = name

    def set_weight(person, weight):
        person.weight = weight

    def check_login(person, login):
        if not login:
            raise UnauthorizedError("Was not logged in!" + person.email)

    @for_key("name", set_name)
    @for_key("weight", set_weight, optional=True)
    @for_path(check_login)
    def _savePerson(person):
        person = Person()
        yield person
        person.save()

    return _savePerson(input)

print(parsePerson(correct))
print(parsePerson(optional))
try:
    parsePerson(incorrect)
except ObjSyntaxError, e:
    print(e.message)
    e.print_grammar()
