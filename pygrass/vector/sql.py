# -*- coding: utf-8 -*-
"""
SQL
===

It is a collection of strings to avoid to repeat the code. ::

    >>> SELECT.format(cols=', '.join(['cat', 'area']), tname='table')
    'SELECT cat, area FROM table;'
    >>> SELECT_WHERE.format(cols=', '.join(['cat', 'area']),
    ...                     tname='table', condition='area>10000')
    'SELECT cat, area FROM table WHERE area>10000;'


"""

#
# SQL
#

#ALTER TABLE
ADD_COL = "ALTER TABLE {tname} ADD COLUMN {cname} {ctype};"
DROP_COL = "ALTER TABLE {tname} DROP COLUMN {cname};"
RENAME_COL = "ALTER TABLE {tname} RENAME COLUMN {old_name} TO {new_name};"
CAST_COL = "ALTER TABLE {tname} ALTER COLUMN {col} SET DATA TYPE {ctype};"
RENAME_TAB = "ALTER TABLE {old_name} RENAME TO {new_name};"

#SELECT
SELECT = "SELECT {cols} FROM {tname};"
SELECT_WHERE = "SELECT {cols} FROM {tname} WHERE {condition};"
SELECT_ORDERBY = "SELECT {cols} FROM {tname} ORDER BY {orderby};"


# GET INFO
PRAGMA = "PRAGMA table_info({tname});"