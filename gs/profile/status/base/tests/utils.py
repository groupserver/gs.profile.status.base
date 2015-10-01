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
from __future__ import absolute_import, unicode_literals, print_function
from mock import patch
from unittest import TestCase
from gs.profile.status.base.utils import previous_month


class PreviousMonthTest(TestCase):

    @patch('gs.profile.status.base.utils.curr_time')
    def test_previous(self, p_curr_time):
        'Test the simple case'
        ct = p_curr_time()
        ct.month = 10
        ct.year = 2015

        r = previous_month()

        self.assertEqual(9, r.month)
        self.assertEqual(2015, r.year)

    @patch('gs.profile.status.base.utils.curr_time')
    def test_previous_year(self, p_curr_time):
        'Test January'
        ct = p_curr_time()
        ct.month = 1
        ct.year = 2015

        r = previous_month()

        self.assertEqual(12, r.month)
        self.assertEqual(2014, r.year)
