
UNKNOWN = "<?>"


class ParseError(RuntimeError):
    pass


def prevent_siblings(f):
    def _check(self, *args, **kwargs):
        if self._has_siblings():
            raise NotImplementedError(
                "Cannot yet give grammar for cases "
                "where there are multiple iterations "
                "over the same dataset, possibly each "
                "spawning descents.")
        return f(self, *args, **kwargs)
    return _check


def _get_grammar_of_thing(thing, **kwargs):
    try:
        return thing.get_grammar(**kwargs)
    except AttributeError:
        return None


def _getvalue(target, key):
    if not key in target:
        raise ParseError(
            u"Mandatory attribute '{}' missing on {}.".format(key, target))
    return target[key]


def foreach(iter_visitor):
    class Foreach(ParseDecorator):

        @prevent_siblings
        def get_grammar(self, is_first_sibling=True):
            if is_first_sibling:
                return [_get_grammar_of_thing(iter_visitor) or UNKNOWN]

        def post_access(self, target):
            for element in target:
                iter_visitor(element)

    return Foreach


def for_key(key, value_visitor):
    class ForKey(ParseDecorator):
        def get_grammar(self, is_first_sibling=True):
            grammar = {key: _get_grammar_of_thing(value_visitor) or UNKNOWN}
            if self._has_siblings():
                grammar.update(self._get_grammar_of_decorated())
            return grammar

        def post_access(self, target):
            value_visitor(target[key])
    return ForKey


def foreach_item(iter_visitor):
    class ForEachItem(ParseDecorator):

        @prevent_siblings
        def get_grammar(self, is_first_sibling=True):
            grammar = {}
            grammar.update(
                _get_grammar_of_thing(iter_visitor) or {UNKNOWN: UNKNOWN})
            return grammar

        def post_access(self, target):
            for key, value in target.items():
                iter_visitor(key, value)
    return ForEachItem


class ParseDecorator(object):
    def __init__(self, f):
        self._f = f

    def get_grammar(self):
            raise NotImplementedError()

    def _has_siblings(self):
        return self._get_grammar_of_decorated() is not None

    def _get_grammar_of_decorated(self):
        return _get_grammar_of_thing(self._f, is_first_sibling=False)

    def print_grammar(self):
        import json
        print(json.dumps(self.get_grammar(), indent=4))

    def __call__(self, target, *args, **kwargs):
        res = self._f(target, *args, **kwargs)
        self.post_access(target)
        return res
