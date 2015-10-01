# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, print_function, unicode_literals
from datetime import date
import sys
if sys.version_info >= (3, ):  # pragma: no cover
    from urllib.parse import quote
else:  # Python 2
    from urllib import quote
from gs.core import (curr_time, to_ascii)


#: The mailto string
MAILTO = 'mailto:{to}?subject={subject}&body={body}'


def mailto(to, subject, body):
    '''Create a ``mailto:`` URL'''
    qTo = quote(to)
    qSubject = quote(subject)
    try:
        qBody = quote(body)
    except KeyError:  # --=mpj17=-- Why is it a KeyError?
        u = to_ascii(body)
        qBody = quote(u)
    retval = MAILTO.format(to=qTo, subject=qSubject, body=qBody)
    return retval


def previous_month():
    '''Get the previous month

:returns: The previous month.
:rtype: datetime.date'''
    dt = curr_time()
    if dt.month == 1:
        newMonth = 12
        newYear = dt.year - 1
    else:
        newMonth = dt.month - 1
        newYear = dt.year
    retval = date(newYear, newMonth, 1)
    return retval
