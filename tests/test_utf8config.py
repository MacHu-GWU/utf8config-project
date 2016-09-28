#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import pytest
from pytest import raises, approx
from dataIO import textfile
from utf8config import (
    is_same_instance, load_value, dump_value,
    extract_comment, remove_post_comment,
    Field, Section, Config,
)


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

    assert load_value("Hello World!") == "Hello World!"
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
    assert dump_value("True") == "'True'"
    assert dump_value("True") == "'True'"

    assert dump_value([]) == ","
    assert dump_value([1, -2, 3]) == "1, -2, 3"
    assert dump_value([1.1, -2.2, 3.3]) == "1.1, -2.2, 3.3"
    assert dump_value([1, 2, 3]) == "1, 2, 3"
    assert dump_value([1, 2, 3]) == "1, 2, 3"
    assert dump_value(["a", "b", "c"]) == "a, b, c"
    assert dump_value(["a", "1", "2"]) == "a, '1', '2'"

    with raises(Exception):
        dump_value([1, 3.14, "abc"])


def test_extract_comment():
    assert extract_comment("###  This is comment ") == "This is comment"


def test_remove_post_comment():
    text = \
        """
    ### DEFAULT是默认Section
    [DEFAULT]
    localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
    port = 8080 # 端口号
    
    ### 下面的是尝试连接的最长时间
    connection_timeout = 60 # 单位是秒, 默认60
    
    # Test是用来测试各种数据类型是否能被成功解析的
    # 用Configuration.load()看看会不会成功吧
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    assert remove_post_comment(lines)[0] == "### DEFAULT是默认Section"
    assert remove_post_comment(
        lines)[-1] == "connection_timeout = 60 # 单位是秒, 默认60"


class TestField:

    def test_load(self):
        # with upper_comment and side_comment
        field = Field.load(
            "# A full name\n# Has to be titlized\nname = John # The supervisor's name\n\n")
        assert field.key == "name"
        assert field.value == "John"
        assert field.upper_comment == "A full name\nHas to be titlized"
        assert field.side_comment == "The supervisor's name"

        # with side_comment
        field = Field.load("name = John # The supervisor's name\n\n")
        assert field.key == "name"
        assert field.value == "John"
        assert field.upper_comment == ""
        assert field.side_comment == "The supervisor's name"

        # no comment
        field = Field.load("name = John")
        assert field.key == "name"
        assert field.value == "John"
        assert field.upper_comment == ""
        assert field.side_comment == ""

    def test_dump(self):
        field = Field(
            key="name",
            value="John",
            upper_comment="A full name\nHas to be titlized",
            side_comment="The supervisor's name",
        )
        assert field.dump(
        ) == "# A full name\n# Has to be titlized\nname = John # The supervisor's name\n"


class TestSection:

    def test_load(self):
        text = """
        ### DEFAULT是默认Section
        [DEFAULT]
        localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
        port = 8080 # 端口号

        ### 下面的是尝试连接的最长时间
        connection_timeout = 60 # 单位是秒, 默认60

        # Test是用来测试各种数据类型是否能被成功解析的
        # 用Configuration.load()看看会不会成功吧
        """
        text = "\n".join([line.strip()
                          for line in text.split("\n") if line.strip()])
        section = Section.load(text)
        assert section.name == "DEFAULT"
        assert section.upper_comment == "DEFAULT是默认Section"
        assert section["localhost"].key == "localhost"
        assert section["localhost"].value == "192.168.0.1"
        assert section["localhost"].upper_comment == ""
        assert section["localhost"].side_comment == "IP地址, 默认 192.168.0.1"

        assert section.keys() == ['localhost', 'port', 'connection_timeout']

    def test_dump(self):
        text = """
        ### DEFAULT是默认Section
        [DEFAULT]
        localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
        port = 8080 # 端口号

        ### 下面的是尝试连接的最长时间
        connection_timeout = 60 # 单位是秒, 默认60

        # Test是用来测试各种数据类型是否能被成功解析的
        # 用Configuration.load()看看会不会成功吧
        """
        text = "\n".join([line.strip()
                          for line in text.split("\n") if line.strip()])
        section = Section.load(text)
#         print(section.dump())


class TestConfig:

    def test_load_and_dump(self):
        text = textfile.read("config.txt")
        config = Config.load(text)
        assert config.values()[0].name == "DEFAULT"
        assert config.values()[1].name == "TEST"

        textfile.write(config.dump(), "config_new.txt")


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), "--tb=native", "-s", ])
