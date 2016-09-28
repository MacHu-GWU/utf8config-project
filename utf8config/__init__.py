#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import string
from collections import OrderedDict
from sfm import nameddict
from six import integer_types, string_types

__version__ = "0.0.1"
__short_description__ = "A utf8 charset config file parser"
__license__ = "MIT"
__author__ = "Sanhe Hu"


def is_same_instance(l):
    """Check whether if items in list is same type or None.
    """
    if len(l) == 0:
        raise ValueError

    i1_class = None.__class__
    for i in l:
        if i is not None:
            i1_class = i.__class__

    for i in l:
        if isinstance(i, i1_class) or i is None:
            pass
        else:
            return False
    return True


def load_value(text="", allow_space=True):
    """
    """
    if allow_space:
        if text != "" and text.strip() == "":
            return text
        else:
            text = text.strip()
    else:
        text = text.strip()

    # Integer and Float
    try:
        return int(text)
    except:
        pass

    try:
        return float(text)
    except:
        pass

    if text.startswith("+"):
        _text = text[1:]
        try:
            return int(_text)
        except:
            pass

        try:
            return float(_text)
        except:
            pass

    if text.startswith("-"):
        _text = text[1:]
        try:
            return -int(_text)
        except:
            pass

        try:
            return -float(_text)
        except:
            pass

    # String
    if (text.startswith("'") and text.endswith("'") and ("','" not in text) and ("', '" not in text)) \
            or (text.startswith('"') and text.endswith('"') and ('","' not in text) and ('", "' not in text)):
        return text[1:-1]

    # Bool
    if text.lower() in ["true", "yes", "是"]:
        return True

    if text.lower() in ["false", "no", "否"]:
        return False

    if text.lower() in ["none", "null", ""]:
        return None

    if "," in text:
        if text == ",":
            return list()
        value = [load_value(s, allow_space=False) for s in text.split(",")]
        if is_same_instance(value):
            return value
        else:
            raise ValueError("items in list has to be same type!")
    return text


def dump_value(value=None, allow_space=True):
    """
    """
    if value is None:
        return "None"
    if value is True:
        return "True"
    if value is False:
        return "False"
    if isinstance(value, integer_types):
        return str(value)
    if isinstance(value, float):
        return str(value)

    if isinstance(value, list):
        if not value:
            return ","

        if is_same_instance(value):
            return ", ".join([dump_value(v) for v in value])
        else:
            raise ValueError("items in list has to be same type!")
    if isinstance(value, string_types):
        if allow_space:
            pass
        else:
            value = value.strip()

        try:
            int(value)
            return "'%s'" % value
        except:
            pass

        try:
            float(value)
            return "'%s'" % value
        except:
            pass

        if value.lower() in ["true", "false", "yes", "no", "是", "否", "null", "none"]:
            return "'%s'" % value
        return value
    return value

bad_charset = set(r"`~!@#$%^&*()-+={[}]|\:;"'<,>.?/\t\r\n')


def validate_key(key):
    """Check the namespace.
    """
    if len(bad_charset.intersection(key)):
        raise ValueError("%r is invalid key" % key)
    if key[0] in string.digits:
        raise ValueError("%r is invalid key" % key)


def extract_comment(line):
    """Extract comment string from `# This is comment`。
    """
    if not line.startswith("#"):
        raise ValueError

    index = 0
    for char in line:
        if char == "#":
            index += 1
        else:
            return line[index:].strip()


def remove_post_comment(lines):
    """

    **中文文档**

    由于一段section的文本最后可能会带有一些注释, 但这些注释是属于下一个section的
    upper_comment, 而不属于这一个section。所以需要移除。
    """
    counter = 0
    reversed_lines = lines[::-1]
    for line in reversed_lines:
        counter += 1
        if not line.startswith("#"):
            break
    new_lines = reversed_lines[counter-1:]
    lines = new_lines[::-1]
    return lines


class Field(nameddict.Base):
    __attrs__ = ["key", "value", "upper_comment", "side_comment"]

    def __init__(self, key, value, upper_comment="", side_comment=""):
        self.key = key
        self.value = value
        self.upper_comment = upper_comment
        self.side_comment = side_comment

    @staticmethod
    def load(text):  # load Field
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        counter = 0
        upper_comment_lines = list()
        side_comment = ""
        for line in lines:
            counter += 1
            if line.startswith("#"):
                comment = extract_comment(line)
                upper_comment_lines.append(comment)
            if not line.startswith("#"):
                if " # " in line:
                    side_comment = line.split(" # ")[-1].strip()
                    key_value = line.split(" # ")[0]
                else:
                    key_value = line
                key, value = key_value.split("=")
                key = key.strip()
                value = load_value(value.strip())

        upper_comment = "\n".join(upper_comment_lines)
        return Field(key, value, upper_comment, side_comment)

    def dump(self):  # dump Field
        lines = list()
        if self.upper_comment:
            lines.append("\n".join(["# " + l.strip()
                                    for l in self.upper_comment.split("\n")]))
        if self.side_comment:
            lines.append("%s = %s # %s" %
                         (self.key, dump_value(self.value), self.side_comment))
        else:
            lines.append("%s = %s" % (self.key, dump_value(self.value)))
        lines.append("")  # 为最后加一个空行
        return "\n".join(lines)


class Section(nameddict.Base):

    """
    Section **没有side_comment**!
    """
    __attrs__ = ["name", "upper_comment", "fields"]

    def __init__(self, name, upper_comment="", fields=None):
        validate_key(name)
        self.name = name

        self.upper_comment = upper_comment

        if fields is None:
            self.fields = OrderedDict()
        else:
            self.fields = fields

    def __getitem__(self, key):
        return self.fields[key]

    def items(self):
        return self.fields.items()

    def add_field(self, field_or_field_list):
        if isinstance(field_or_field_list, list):
            pass
        elif isinstance(field_or_field_list, Field):
            field_or_field_list = [field_or_field_list, ]

        for field in field_or_field_list:
            if field.key in self.fields:
                print(field)
                raise KeyError
            else:
                self.fields[field.key] = field

    def remove_field(self, field_or_field_list):
        if isinstance(field_or_field_list, list):
            pass
        elif isinstance(field_or_field_list, Field):
            field_or_field_list = [field_or_field_list, ]

        for field in field_or_field_list:
            if field.key in self.fields:
                del self.fields[field.key]

    @staticmethod
    def load(text):  # load Section
        # parse header
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        counter = 0
        upper_comment_lines = list()
        for line in lines:
            counter += 1
            if line.startswith("#"):
                comment = extract_comment(line)
                upper_comment_lines.append(comment)
            elif line.startswith("[") and line.endswith("]"):
                name = line[1:-1]
                validate_key(name)
                section = Section(name, "\n".join(upper_comment_lines))
                break

        lines = lines[counter:]

        # parse body
        field_text_list = list()
        field_lines = list()
        for line in lines:
            field_lines.append(line)
            if line.startswith("#"):
                pass
            else:
                field_text_list.append("\n".join(field_lines))
                field_lines = list()

        for field_text in field_text_list:
            field = Field.load(field_text)
            section.add_field(field)

        return section

    def dump(self):  # dump Section
        lines = list()
        if self.upper_comment:
            lines.append("\n".join(["# " + l.strip()
                                    for l in self.upper_comment.split("\n")]))
        lines.append("[%s]\n" % self.name)

        for field in self.fields.values():
            lines.append(field.dump())
        return "\n".join(lines)


class Config(nameddict.Base):

    """
    """
    __attrs__ = ["sections"]

    def __init__(self, sections=None):
        if sections is None:
            self.sections = OrderedDict()
        else:
            self.sections = sections

    def __getitem__(self, key):
        return self.sections[key]

    def items(self):
        return self.sections.items()

    def add_section(self, section_or_section_list):
        if isinstance(section_or_section_list, list):
            pass
        elif isinstance(section_or_section_list, Section):
            section_or_section_list = [section_or_section_list, ]

        for section in section_or_section_list:
            if section.name in self.sections:
                raise KeyError
            else:
                self.sections[section.name] = section

    def remove_section(self, section_or_section_list):
        if isinstance(section_or_section_list, list):
            pass
        elif isinstance(section_or_section_list, Field):
            section_or_section_list = [section_or_section_list, ]

        for section in section_or_section_list:
            if section.key in self.sections:
                del self.sections[section.key]

    @staticmethod
    def load(text):  # load Config
        section_text_list = list()

        section_text_lines = list()
        for line in ["# Empty section", "[empty_section]", "empty = empty"] + [line.strip() for line in text.split("\n") if line.strip()]:
            if line.startswith("[") and line.endswith("]"):
                old_section_text_list = section_text_lines[:]
                section_text_lines = remove_post_comment(section_text_lines)
                section_text_list.append("\n".join(section_text_lines))

                section_text_lines = list()
                for line_ in old_section_text_list[::-1]:
                    if line_.startswith("#"):
                        section_text_lines.append(line_)
                    else:
                        break

                section_text_lines.append(line)
            else:
                section_text_lines.append(line)
        section_text_lines = remove_post_comment(section_text_lines)
        section_text_list.append("\n".join(section_text_lines))

        config = Config()
        for text in section_text_list[2:]:
            section = Section.load(text)
            config.add_section(section)

        return config

    def dump(self):  # dump Config
        lines = list()
        for section in self.sections.values():
            lines.append(section.dump())
        return "\n".join(lines)
