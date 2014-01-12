from collections import defaultdict
from itertools import izip

from parseobj import foreach, ObjSyntaxError


def assert_calls(recorder, func, *list_of_args):
    assert len(recorder[func]) == len(list_of_args)
    for actual, expected in izip(recorder[func], list_of_args):
        _assertEqual(actual, expected)


def _assertEqual(left, right):
    assert left == right


class TestForeach(object):
    def test_given_empty_collection_expecting_exception(self):
        called_with = defaultdict(lambda: [])

        def visit_element(*args):
            called_with[visit_element].append(list(args))

        @foreach(visit_element)
        def visit_collection(*args):
            called_with[visit_collection].append(list(args))

        col = []
        try:
            visit_collection(col)
            self.fail("Exception expected")
        except ObjSyntaxError:
            # We're evaluating lazily, hence the collection will be visited,
            # before the missing elements are noticed.
            assert_calls(called_with, visit_collection, [col])
            assert_calls(called_with, visit_element)

    def test_given_one_element_expecting_functions_called(self):
        called_with = defaultdict(lambda: [])

        def visit_element(*args):
            called_with[visit_element].append(list(args))

        @foreach(visit_element)
        def visit_collection(*args):
            called_with[visit_collection].append(list(args))

        col = [1]
        visit_collection(col)
        assert_calls(called_with, visit_collection, [col])
        assert_calls(called_with, visit_element, [1])

    def test_given_multiple_elements_expecting_functions_called(self):
        called_with = defaultdict(lambda: [])

        def visit_element(*args):
            called_with[visit_element].append(list(args))

        @foreach(visit_element)
        def visit_collection(*args):
            called_with[visit_collection].append(list(args))

        col = [1, 2, 3, 4]
        visit_collection(col)
        assert_calls(called_with, visit_collection, [col])
        assert_calls(called_with, visit_element, [1], [2], [3], [4])
