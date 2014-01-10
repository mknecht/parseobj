from collections import defaultdict

from parseobj import foreach, ObjSyntaxError


class TestForeach(object):
    def test_given_empty_collection_expecting_exception(self):
        called_with = defaultdict(lambda: [])

        def visit_element(*args):
            called_with[visit_element].append(args)

        @foreach(visit_element)
        def visit_collection(args):
            called_with[visit_collection].append(args)

        col = []
        try:
            visit_collection(col)
            self.fail("Exception expected")
        except ObjSyntaxError:
            self.assert_calls(called_with, visit_collection, [col])
            self.assert_calls(called_with, visit_element)

    def test_given_one_element_expecting_functions_called(self):
        called_with = defaultdict(lambda: [])

        def visit_element(element):
            called_with[visit_element].append(element)

        @foreach(visit_element)
        def visit_collection(collection):
            called_with[visit_collection].append(collection)

        col = [1]
        visit_collection(col)
        self.assert_calls(called_with, visit_collection, [col])
        self.assert_calls(called_with, visit_element, [1])

    def assert_calls(self, recorder, func, *list_of_args):
        assert len(recorder[func]) == len(list_of_args)
        for args in list_of_args:
            self._assertEqual(recorder[func], args)

    def _assertEqual(self, left, right):
        assert left == right
