import json

UNKNOWN = "<?>"
ROOT = "<root>"


class ObjParseError(RuntimeError):
    pass


class ObjSyntaxError(RuntimeError):
    pass


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
        expected = u"Expected dict-like object with key '{}'".format(key)

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._target_path = '["{}"]'.format(key)
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

        @classmethod
        def get_grammar(cls, grammar_of_decorated, is_first_sibling=True):
            grammar = {key: _get_grammar_of_thing(value_visitor) or UNKNOWN}
            grammar.update(grammar_of_decorated or {})
            return grammar
    return get_parse_decorator(ForKey)


def foreach(iterable_or_visitor, visitor=None):
    iter_visitor = visitor if visitor is not None else iterable_or_visitor
    iterable = iterable_or_visitor if visitor is not None else None

    class Foreach(ExecManager):
        expected = u"Expected iterable with at least one element."

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._verify_syntax()
            for idx, element in enumerate(self._target):
                self._target_path = '["{}"]'.format(idx)
                if isinstance(iter_visitor, ParseDecorator):
                    kwargs["path_to_self"] = self._make_target_path()
                iter_visitor(element, *args, **kwargs)

        @classmethod
        def get_grammar(cls, grammar_of_decorated, is_first_sibling=True):
            return [_get_grammar_of_thing(iter_visitor) or UNKNOWN]

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

    if iterable:
        Foreach(iterable).do_visit()
    else:
        return get_parse_decorator(Foreach)


def foreach_item(iter_visitor):
    class ForEachItem(ExecManager):
        expected = (u"Expected dict-like object with at least one item "
                    "key-value pair.")

        @classmethod
        def get_grammar(self, grammar_of_decorated, is_first_sibling=True):
            grammar = {}
            grammar.update(
                _get_grammar_of_thing(iter_visitor) or {UNKNOWN: UNKNOWN})
            return grammar

        @prepend_path_to_exceptions
        def do_visit(self, *args, **kwargs):
            self._verify_syntax()
            for key, value in self._target.items():
                self._target_path = '["{}"]'.format(key)
                if isinstance(iter_visitor, ParseDecorator):
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
    return ForEachItem


class ExecManager(object):
    def __init__(self, target, path_to_self=ROOT):
        self._path_to_self = path_to_self
        self._target = target
        self._target_path = None

    def do_visit(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get_grammar(cls,  grammar_of_decorated):
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
    pass


def get_parse_decorator(exec_class):
    class TokenSpecificDecorator(ParseDecorator):
        def __init__(self, f):
            self._f = f

        def __call__(self, target, *args, **kwargs):
            path_to_self = kwargs.pop("path_to_self", ROOT)
            res = self._f(target, *args, **kwargs)
            exec_class(target, path_to_self=path_to_self).do_visit(
                *args, **kwargs)
            return res

        @property
        def parent(self):
            return self._parent

        @parent.setter
        def parent(self, new_parent):
            self._parent = new_parent

        def get_grammar(self):
            return exec_class.get_grammar(
                grammar_of_decorated=self._get_grammar_of_decorated())

        def _get_grammar_of_decorated(self):
            return _get_grammar_of_thing(self._f)

        def print_grammar(self):
            print(json.dumps(self.get_grammar(), indent=4))
    return TokenSpecificDecorator
