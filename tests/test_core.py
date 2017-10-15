#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import pytest
from pytest import raises, approx
from utf8config.core import (
    validate_key, extract_comment, remove_post_comment,
    Field, Section, Config,
)


def test_validate_key():
    validate_key("DEFAULT")
    for key in ["  ", "1field", "this-field"]:
        with raises(Exception):
            validate_key(key)


def test_extract_comment():
    assert extract_comment("###  This is comment ") == "This is comment"
    with raises(Exception):
        extract_comment("This is not a comment!")


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


def remove_indent(text):
    return "\n".join(
        [line.strip() for line in text.split("\n") if line.strip()])


def read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def write(text, path):
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))


class TestField(object):
    def test_load(self):
        # with upper_comment and side_comment
        text = remove_indent(
            """
            # A full name
            # Has to be titlized
            name = John # The supervisor's name
            """)
        field = Field.load(text)
        assert field.key == "name"
        assert field.value == "John"
        assert field.upper_comment == "A full name\nHas to be titlized"
        assert field.side_comment == "The supervisor's name"

        # with side_comment
        text = remove_indent(
            """
            name = John # The supervisor's name
            """)
        field = Field.load(text)
        assert field.key == "name"
        assert field.value == "John"
        assert field.upper_comment == ""
        assert field.side_comment == "The supervisor's name"

        # no comment
        text = remove_indent("name = John")
        field = Field.load(text)
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
        assert field.dump() == "# A full name\n# Has to be titlized\nname = John # The supervisor's name\n"


class TestSection(object):

    def test_add_remove_field(self):
        section = Section("DEFAULT")
        section.add_field(Field("a", 1))
        with raises(KeyError):
            section.add_field(Field("a", 1))

        section.add_field([Field("b", 2), Field("c", 3)])
        assert section.keys() == ["a", "b", "c"]

        assert section["a"].key == "a"
        assert section["b"].key == "b"
        assert section["c"].key == "c"

        with raises(KeyError):
            section.remove_field("d")

        section.remove_field(["a", "b", "c"])
        assert len(section.keys()) == 0
        assert len(section.values()) == 0
        assert len(section.items()) == 0

    def test_load(self):
        text = remove_indent("""
        ### DEFAULT是默认Section
        [DEFAULT]
        localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
        port = 8080 # 端口号

        ### 下面的是尝试连接的最长时间
        connection_timeout = 60 # 单位是秒, 默认60

        # Test是用来测试各种数据类型是否能被成功解析的
        # 用Configuration.load()看看会不会成功吧
        """)

        section = Section.load(text)
        assert section.name == "DEFAULT"
        assert section.upper_comment == "DEFAULT是默认Section"
        assert section["localhost"].key == "localhost"
        assert section["localhost"].value == "192.168.0.1"
        assert section["localhost"].upper_comment == ""
        assert section["localhost"].side_comment == "IP地址, 默认 192.168.0.1"

        assert section.keys() == ['localhost', 'port', 'connection_timeout']

    def test_dump(self):
        text = remove_indent("""
        ### DEFAULT是默认Section
        [DEFAULT]
        localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
        port = 8080 # 端口号

        ### 下面的是尝试连接的最长时间
        connection_timeout = 60 # 单位是秒, 默认60

        # Test是用来测试各种数据类型是否能被成功解析的
        # 用Configuration.load()看看会不会成功吧
        """)
        section = Section.load(text)
        section.dump()
        section.dump(ignore_comment=True)


class TestConfig(object):
    def test_add_remove_section(self):
        config = Config()
        config.add_section(Section("a"))
        with raises(KeyError):
            config.add_section(Section("a"))

        config.add_section([Section("b"), Section("c")])
        assert config.keys() == ["a", "b", "c"]

        assert config["a"].name == "a"
        assert config["b"].name == "b"
        assert config["c"].name == "c"

        with raises(KeyError):
            config.remove_section("d")

        config.remove_section(["a", "b", "c"])
        assert len(config.keys()) == 0
        assert len(config.values()) == 0
        assert len(config.items()) == 0

    def test_load_and_dump(self):
        text = read(__file__.replace("test_core.py", "config.txt"))
        config = Config.load(text)
        assert config.values()[0].name == "DEFAULT"
        assert config.values()[1].name == "TEST"

        write(
            config.dump(),
            __file__.replace("test_core.py", "config_with_comment.txt"),
        )
        write(
            config.dump(ignore_comment=True),
            __file__.replace("test_core.py", "config_no_comment.txt"),
        )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
