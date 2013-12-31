class ParseError(RuntimeError):
    pass


def _get_grammar_of_thing(thing):
    try:
        return thing.get_grammar()
    except AttributeError:
        return "<?>"


def _getvalue(target, key):
    if not key in target:
        raise ParseError(
            u"Mandatory attribute '{}' missing on {}.".format(key, target))
    return target[key]


def foreach(iter_visitor):
    class Foreach(ParseDecorator):
        def get_grammar(self):
            return "[{child}, ...]".format(
                child=_get_grammar_of_thing(iter_visitor)
            )

        def post_access(self, target):
            for element in target:
                iter_visitor(element)
    return Foreach


def for_key(key, value_visitor):
    class ForKey(ParseDecorator):
        def get_grammar(self):
            return "{{{key}: {child}, {sibling}}}".format(
                sibling=super(ForKey, self).get_grammar() or "...",
                key=key,
                child=_get_grammar_of_thing(value_visitor)
            )

        def post_access(self, target):
            value_visitor(target[key])
    return ForKey


def foreach_item(iter_visitor):
    class ForEachItem(ParseDecorator):
        def get_grammar(self):
            return "{{{child}, ...}}".format(
                sibling=super(ForEachItem, self).get_grammar(),
                child=_get_grammar_of_thing(iter_visitor)
            )

        def post_access(self, target):
            for key, value in target.items():
                iter_visitor(key, value)
    return ForEachItem


class ParseDecorator(object):
    def __init__(self, f):
        self._f = f

    def get_grammar(self):
        return _get_grammar_of_thing(self._f)

    def print_grammar(self):
        print(self.get_grammar())

    def __call__(self, target, *args, **kwargs):
        res = self._f(target, *args, **kwargs)
        self.post_access(target)
        return res
