#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import string
from collections import OrderedDict

import attr
try:
    from .io import load_value, dump_value
except:  # pragma: no cover
    from utf8config.io import load_value, dump_value


bad_charset = set(r"`~!@#$%^&*()-+={[}]|\:;"'<,>.?/\t\r\n ')


def validate_key(key):
    """
    Check the namespace.

    Valid namespace: a-zA-Z0-9, underscore. Not startswith numbers.
    """
    if len(bad_charset.intersection(key)):
        raise ValueError("%r is invalid key" % key)
    if key[0] in string.digits:
        raise ValueError("%r is invalid key" % key)


def extract_comment(line):
    """
    Extract comment string from `# This is comment`。
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
    new_lines = reversed_lines[counter - 1:]
    lines = new_lines[::-1]
    return lines


@attr.s
class Field(object):
    key = attr.ib()
    value = attr.ib()
    upper_comment = attr.ib(default="")
    side_comment = attr.ib(default="")

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

    def dump(self, ignore_comment=False):  # dump Field
        """

        :param no_comment: ignore comment.
        """
        lines = list()
        if ignore_comment:
            lines.append("%s = %s" % (self.key, dump_value(self.value)))
        else:
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


@attr.s
class ContainerStyled(object):
    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.values())

    def items(self):
        return list(self.data.items())

    def _add(self, key, value):
        if key in self.data:
            raise KeyError("Key(%s) already exists!" % key)
        else:
            self.data[key] = value

    def _remove(self, key):
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError("Key(%s) not exists!" % key)

    def _construct_list(self, item_or_list):
        if isinstance(item_or_list, (tuple, list)):
            return item_or_list
        else:
            return (item_or_list,)


@attr.s
class Section(ContainerStyled):

    """
    Section **没有side_comment**!
    """
    name = attr.ib()
    upper_comment = attr.ib(default="")
    data = attr.ib(default=attr.Factory(OrderedDict))

    @property
    def fields(self):
        """
        field dict.
        """
        return self.data

    def add_field(self, field_or_field_list):
        """

        :param field_or_field_list: :class:`Field` or list of it.
        """
        field_or_field_list = self._construct_list(field_or_field_list)
        for field in field_or_field_list:
            self._add(field.key, field)

    def remove_field(self, key_or_key_list):
        """

        :param key_or_key_list: field name or list of it.
        """
        key_or_key_list = self._construct_list(key_or_key_list)
        for key in key_or_key_list:
            self._remove(key)

    @staticmethod
    def load(text):  # load Section
        """
        load section from text.
        """
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

    def dump(self, ignore_comment=False):  # dump Section
        """
        dump section to text.

        :param no_comment: ignore comment.
        """
        lines = list()
        if ignore_comment:
            pass
        else:
            if self.upper_comment:
                lines.append("\n".join(["# " + l.strip()
                                        for l in self.upper_comment.split("\n")]))
        lines.append("[%s]\n" % self.name)

        for field in self.fields.values():
            lines.append(field.dump(ignore_comment=ignore_comment))
        return "\n".join(lines)


@attr.s
class Config(ContainerStyled):
    """
    """
    data = attr.ib(default=attr.Factory(OrderedDict))

    @property
    def sections(self):
        return self.data

    def add_section(self, section_or_section_list):
        """

        :param section_or_section_list: :class:`Section` or list of it.
        """
        section_or_section_list = self._construct_list(section_or_section_list)
        for section in section_or_section_list:
            self._add(section.name, section)

    def remove_section(self, name_or_name_list):
        """

        :param name_or_name_list: section name or list of it.
        """
        name_or_name_list = self._construct_list(name_or_name_list)
        for name in name_or_name_list:
            self._remove(name)

    @staticmethod
    def load(text):  # load Config
        """
        load config from text.
        """
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

    def dump(self, ignore_comment=False):  # dump Config
        """
        dump config to text.

        :param no_comment: ignore comment.
        """
        lines = list()
        for section in self.sections.values():
            lines.append(section.dump(ignore_comment=ignore_comment))
        return "\n".join(lines)
