import json

UNKNOWN = "<?>"
ROOT = "<root>"

ITERABLE, DICT = range(2)


class ObjSyntaxError(RuntimeError):
    pass


def isdecorator(f):
    return isinstance(f, ParseDecorator)


class DictProduction(object):
    def get_grammar(self, components):
        grammar = {}
        for c in components:
            token = c.grammar_class().token
            if token is not None:
                grammar[token[0]] = token[1]
        return grammar


class IterableProduction(object):
    def get_grammar(self, components):
        grammar = []
        for c in components:
            token = c.grammar_class().token
            if token is not None:
                grammar.append(token)
        return grammar


def choose_production(components):
    prod = IterableProduction
    for c in components:
        if c.grammar_class().tokentype == DICT:
            prod = DictProduction
    return prod


class ExecManager(object):
    def __init__(self, target, path_to_self=ROOT):
        self._path_to_self = path_to_self
        self._target = target
        self._target_path = None

    def do_visit(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def path_to_self(self):
        return self._path_to_self

    def _make_target_path(self):
        return (
            (self._path_to_self)
            + (self._target_path or u"")
        )


class ParseDecorator(object):
    exec_class = None

    def __init__(self, f):
        self._f = f
        self._inner_siblings = []
        if isdecorator(f):
            self._inner_siblings.append(f)
            self._inner_siblings.extend(f.inner_siblings)

    def __call__(self, target, *args, **kwargs):
        path_to_self = kwargs.pop("path_to_self", ROOT)
        res = self._f(target, *args, **kwargs)
        self.exec_class(target, path_to_self=path_to_self).do_visit(
            *args, **kwargs)
        return res

    @property
    def inner_siblings(self):
        return self._inner_siblings

    def get_grammar(self):
        components = [self] + self._inner_siblings[:]
        return choose_production(components)().get_grammar(components)

    def print_grammar(self):
        print(json.dumps(self.get_grammar(), indent=4))


def prepend_path_to_exceptions(f):
    def _prepend_path(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except StandardError, e:
            e.args = (u"{}: {}".format(
                self.path_to_self,
                e.message or u"(No error message)"),
            )
            raise
    return _prepend_path


def _get_grammar_of_thing(thing, **kwargs):
    try:
        return thing.get_grammar(**kwargs)
    except AttributeError:
        return None


def for_key(key, value_visitor):
    class ForKey(ExecManager):
        expected = u"Expected dict-like object with key '{}'.".format(key)

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._target_path = u'["{}"]'.format(key)
            self._verify_syntax()
            if isinstance(value_visitor, ParseDecorator):
                kwargs["path_to_self"] = self._make_target_path()
            value_visitor(self._target[key], *args, **kwargs)

        def _verify_syntax(self):
            if self._target is None:
                raise ObjSyntaxError(
                    u"Nothing here. {}".format(self.expected)
                )
            try:
                if not key in self._target:
                    raise ObjSyntaxError(
                        u"Missing key '{missing}', "
                        "found only: {available}. {expected}".format(
                            available=self._target.keys(),
                            expected=self.expected,
                            missing=key,
                        )
                    )
            except TypeError:
                raise ObjSyntaxError(
                    u"No dict-like object. {}".format(key, self.expected)
                )

    class ForKeyGrammar(object):
        @property
        def token(self):
            child = _get_grammar_of_thing(value_visitor)
            return key, child if child is not None else UNKNOWN

        @property
        def tokentype(self):
            return DICT

    class ForKeyDecorator(ParseDecorator):
        exec_class = ForKey
        grammar_class = ForKeyGrammar

    return ForKeyDecorator


def foreach(iterable_or_visitor, visitor=None):
    iter_visitor = visitor if visitor is not None else iterable_or_visitor
    iterable = iterable_or_visitor if visitor is not None else None

    class Foreach(ExecManager):
        expected = u"Expected iterable with at least one element."

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._verify_syntax()
            for idx, element in enumerate(self._target):
                self._target_path = u'["{}"]'.format(idx)
                if isinstance(iter_visitor, ParseDecorator):
                    kwargs["path_to_self"] = self._make_target_path()
                iter_visitor(element, *args, **kwargs)

        def _verify_syntax(self):
            if self._target is None:
                raise ObjSyntaxError(
                    u"Nothing here. {expected}".format(expected=self.expected)
                )
            try:
                if len(self._target) == 0:
                    raise ObjSyntaxError(
                        u"Iterable is empty. {expected}".format(
                            expected=self.expected,
                        )
                    )
            except TypeError:
                raise ObjSyntaxError(
                    u"No iterable. {expected}".format(expected=self.expected)
                )

    class ForeachGrammar(object):
        @property
        def token(self):
            return _get_grammar_of_thing(iter_visitor)

        @property
        def tokentype(self):
            return ITERABLE

    class ForeachDecorator(ParseDecorator):
        exec_class = Foreach
        grammar_class = ForeachGrammar

    if iterable:
        Foreach(iterable).do_visit()
    else:
        return ForeachDecorator


def foreach_item(iter_visitor):
    class ForeachItem(ExecManager):
        expected = (u"Expected dict-like object with at least one item "
                    "key-value pair.")

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._verify_syntax()
            for key, value in self._target.items():
                self._target_path = u'["{}"]'.format(key)
                if isdecorator(iter_visitor):
                    kwargs["path_to_self"] = self._make_target_path()
                iter_visitor(key, value, *args, **kwargs)

        def _verify_syntax(self):
            if self._target is None:
                raise ObjSyntaxError(
                    u"Nothing here. {}".format(self.expected)
                )
            try:
                if len(self._target.items()) == 0:
                    raise ObjSyntaxError(
                        u"Dict is empty. {expected}".format(
                            expected=self.expected,
                        )
                    )
            except TypeError:
                raise ObjSyntaxError(
                    u"No dict-like object. {expected}".format(
                        expected=self.expected)
                )

    class ForeachItemGrammar(object):
        @property
        def token(self):
            return _get_grammar_of_thing(iter_visitor)

        @property
        def tokentype(self):
            return DICT

    class ForeachItemDecorator(ParseDecorator):
        exec_class = ForeachItem
        grammar_class = ForeachItemGrammar

    return ForeachItemDecorator
