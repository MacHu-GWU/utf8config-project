#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from pytest import raises, approx
from utf8config.io import is_same_instance, load_value, dump_value


def test_is_same_instance():
    with raises(Exception):
        is_same_instance([])

    assert is_same_instance([1, 2, 3]) is True
    assert is_same_instance([1, 3.14]) is False
    assert is_same_instance([1, None, 3]) is True
    assert is_same_instance([None, 2, 3]) is True


def test_load_value():
    assert load_value("    ") == "    "
    assert load_value("\t") == "\t"
    assert load_value("\n") == "\n"

    assert load_value("123") == 123
    assert load_value("+123") == 123
    assert load_value("-123") == -123

    assert load_value("3.14") == approx(3.14)
    assert load_value("+3.14") == approx(3.14)
    assert load_value("-3.14") == approx(-3.14)

    assert load_value("  ", allow_space=True) == "  "
    assert load_value("  ", allow_space=False) == None
    assert load_value("Hello World!") == "Hello World!"
    assert load_value("  Hello World!  ", allow_space=True) == "Hello World!"
    assert load_value("  Hello World!  ", allow_space=False) == "Hello World!"
    assert load_value("'Good Boy'") == "Good Boy"
    assert load_value('"Bad Boy"') == "Bad Boy"
    assert load_value("""'"Boy"'""") == '"Boy"'
    assert load_value("'123'") == "123"
    assert load_value("'3.14'") == "3.14"
    assert load_value("'True'") == "True"
    assert load_value(r"C:\用户\管理员") == r"C:\用户\管理员"
    assert load_value("中文") == "中文"

    assert load_value("True") is True
    assert load_value("true") is True
    assert load_value("TRUE") is True
    assert load_value("Yes") is True
    assert load_value("是") is True
    assert load_value("False") is False
    assert load_value("false") is False
    assert load_value("FALSE") is False
    assert load_value("No") is False
    assert load_value("否") is False

    assert load_value("None") is None
    assert load_value("none") is None
    assert load_value("NONE") is None
    assert load_value("null") is None
    assert load_value("") is None

    assert load_value(",") == []
    assert load_value("1, -2, +3") == [1, -2, 3]
    assert load_value("1, , 3") == [1, None, 3]
    assert load_value("1.1, -2.2, +3.3") == approx([1.1, -2.2, 3.3])
    assert load_value("1.1,, +3.3") == approx([1.1, None, 3.3])
    assert load_value("a, b, c") == ["a", "b", "c"]
    assert load_value("a, , c") == ["a", None, "c"]
    assert load_value("a,, c") == ["a", None, "c"]
    assert load_value(r"C:\windows, C:\中文") == [r"C:\windows", r"C:\中文"]
    assert load_value(r"'C:\windows', 'C:\中文'") == [r"C:\windows", r"C:\中文"]
    assert load_value("'1','2','3'") == ["1", "2", "3"]
    assert load_value("yes, no") == [True, False]
    assert load_value("是, 否") == [True, False]
    assert load_value("a, '1', '3.14', 'True', 'no',, 'None'") == [
        "a", "1", "3.14", "True", "no", None, "None"]

    with raises(Exception):
        load_value("1, 3.14, abc, True")


def test_dump_value():
    assert dump_value(None) == "None"
    assert dump_value(True) == "True"
    assert dump_value(False) == "False"
    assert dump_value(1) == "1"
    assert dump_value(-1) == "-1"
    assert dump_value(3.14) == "3.14"
    assert dump_value(-3.14) == "-3.14"
    assert dump_value("Hello World") == "Hello World"
    assert dump_value("123") == "'123'"
    assert dump_value("'123'") == "'123'"
    assert dump_value('"123"') == '"123"'
    assert dump_value("True") == "'True'"
    assert dump_value("true") == "'true'"
    assert dump_value("False") == "'False'"
    assert dump_value("false") == "'false'"
    assert dump_value("Yes") == "'Yes'"
    assert dump_value("No") == "'No'"
    assert dump_value("是") == "'是'"
    assert dump_value("否") == "'否'"
    assert dump_value("None") == "'None'"
    assert dump_value("Null") == "'Null'"
    assert dump_value("True") == "'True'"
    assert dump_value("False") == "'False'"

    assert dump_value("  ", allow_space=True) == "  "
    assert dump_value("  ", allow_space=False) == "''"

    assert dump_value([]) == ","
    assert dump_value([1, -2, 3]) == "1, -2, 3"
    assert dump_value([1.1, -2.2, 3.3]) == "1.1, -2.2, 3.3"
    assert dump_value([1, 2, 3]) == "1, 2, 3"
    assert dump_value([1, 2, 3]) == "1, 2, 3"
    assert dump_value(["a", "b", "c"]) == "a, b, c"
    assert dump_value(["a", "1", "2"]) == "a, '1', '2'"

    with raises(Exception):
        dump_value([1, 3.14, "abc"])

    with raises(Exception):
        dump_value(dict(a=1, b=2, c=3))


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
