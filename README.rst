.. image:: https://travis-ci.org/MacHu-GWU/utf8config-project.svg?branch=master
    :target: https://travis-ci.org/MacHu-GWU/utf8config-project?branch=master

.. image:: https://codecov.io/gh/MacHu-GWU/utf8config-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/utf8config-project

.. image:: https://img.shields.io/pypi/v/utf8config.svg
    :target: https://pypi.python.org/pypi/utf8config

.. image:: https://img.shields.io/pypi/l/utf8config.svg
    :target: https://pypi.python.org/pypi/utf8config

.. image:: https://img.shields.io/pypi/pyversions/utf8config.svg
    :target: https://pypi.python.org/pypi/utf8config

.. image:: https://img.shields.io/badge/Star_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/utf8config-project


Welcome to ``utf8config`` Documentation
==============================================================================
utf8 format config file IO tool.

Features:

1. Comment Control. (You can choose ignore comment or not while dumping)
2. Allow unicode character.
3. Smart parser for number, string, boolean, None, list.

Example::

    # content of config.ini
    ### DEFAULT is the default section
    ### DEFAULT是默认Section
    [DEFAULT]
    localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
    port = 8080 # 端口号

    ### 下面的是尝试连接的最长时间
    connection_timeout = 60 # 单位是秒, 默认60

    # Test是用来测试各种数据类型是否能被成功解析的
    # 用Configuration.load()看看会不会成功吧

    [TEST]
    # Single Value
    # 以下是单值项
    # 即非列表的值
    int = 123 # 123
    int_pos = +123 # 123
    int_neg = -123 # -123
    float = 3.14 # 3.14
    float_pos = +3.14 # 3.14
    float_neg = -3.14 # -3.14
    str = Hello World! # str "Hello World!"
    str_quote = 'Good Boy' # str "Good Boy"
    str_double_quote = "Bad Boy" # str "Bad Boy"
    str_quote_in_quote = '"Boy"' # str '"Boy"'
    str_int = '123' # str "123"
    str_float = '3.14' # str "3.14"
    str_bool = 'True' # str "True"
    str_path = C:\用户\管理员 # str "C:\用户\管理员"
    str_utf8 = 中文 # str "中文"
    bool_true = True # True
    bool_yes = Yes # True
    bool_false = False # False
    bool_no = No # No
    none_none = None # None
    none_null = null # None
    none = # None

    # List Value
    # 以下是各种列表
    empty_list = , # Empty list []
    int_list = 1, -2, 3 # [1, -2, 3]
    int_none_list = , -2,3 # [None -2, 3]
    float_list = 1.1, -2.2, 3.3 # [1.1, -2.2, 3.3]
    float_none_list = , -2.2,3.3 # [None -2.2, 3.3]
    str_list = a, b, c # ["a", "b", "c"]
    str_single_quote_list = '1', '2', '3' # ["1", "2", "3"]
    str_double_quote_list = "1", "2", "3" # ["1", "2", "3"]
    str_path_list = C:\windows, C:\中文 # ["C:\windows", "C:\中文"]
    str_special_list = a, '1', '3.14', "True", "no", ,"None" # ["a", "1", "3.14", "True", "no", "None"]
    bool_list = True, False # [True, False]
    bool_yes_no_list = Yes, No # [True, False]


Usage:

Read and Write:

.. code-block:: python

    from utf8config import Config, Section, Field

    config = Config.load("config.ini")
    for section_name, section in config.items():
        ...

    section = Config["DEFAULT"]
    for field_name, field in section.items():
        ...

    localhost = section["localhost"]
    port = section["port"]

    localhost.key # "localhost"
    localhost.value # "192.168.0.1"

    with open("config.ini", "w") as f:
        text = config.dump("config.ini", ignore_comment=True)
        f.write(text)


Programmatically Construct Config:

.. code-block:: python

    config = Config()
    DEFAULT = config["DEFAULT"]
    DEFAULT.add_field(Field(key="localhost", value="192.168.0.1"))

    TEST = Section("TEST")
    TEST.add_field(Field(key="numbers", value=[1, 2, 3]))
    config.add_section(TEST)


Quick Links
------------------------------------------------------------------------------

- .. image:: https://img.shields.io/badge/Link-Document-red.svg
      :target: http://www.wbh-doc.com.s3.amazonaws.com/utf8config/index.html

- .. image:: https://img.shields.io/badge/Link-API_Reference_and_Source_Code-red.svg
      :target: http://www.wbh-doc.com.s3.amazonaws.com/utf8config/py-modindex.html

- .. image:: https://img.shields.io/badge/Link-Install-red.svg
      :target: `install`_

- .. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/utf8config-project

- .. image:: https://img.shields.io/badge/Link-Submit_Issue_and_Feature_Request-blue.svg
      :target: https://github.com/MacHu-GWU/utf8config-project/issues

- .. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.python.org/pypi/utf8config#downloads


.. _install:

Install
------------------------------------------------------------------------------

``utf8config`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install utf8config

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade utf8config