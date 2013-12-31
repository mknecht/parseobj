#!/usr/bin/python

from __future__ import print_function
from collections import defaultdict
import json
import os.path

from parseobj import for_key, foreach, foreach_item


cnt_operas = 0
cnt_members = defaultdict(lambda: 0)


def increase_count(role, singer):
    cnt_members[singer] += 1


@foreach_item(increase_count)
def visit_castmember(key):
    pass


@for_key(u"title", print)
@for_key(u"cast", visit_castmember)
def count_opera(opera):
    global cnt_operas
    cnt_operas += 1


@foreach(count_opera)
def visit_pieces(pieces):
    pass


@for_key(u"pieces", visit_pieces)
def visit_introduction(intro):
    pass


obj = json.load(open(os.path.join(os.path.dirname(__file__), "demo.json")))
visit_introduction(obj)
print(u"Operas: {}".format(cnt_operas))
for member, count in cnt_members.items():
    print(u"Occurrences of {}: {}".format(member, count))
visit_introduction.print_grammar()
