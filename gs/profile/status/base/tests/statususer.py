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
from mock import (patch, PropertyMock)
from unittest import TestCase
from gs.profile.status.base.statususer import StatusUser
from .faux import FauxUserInfo


class StatusUserTest(TestCase):
    'Test that StatusUser'

    @patch.object(StatusUser, 'siteGroups', new_callable=PropertyMock)
    def _test_no_sites_no_groups(self, p_siteGroups):
        # --=moj17=-- I cannot figure out how to mock this
        'If the user is in no sites then they are in no groups'
        p_siteGroups.return_value = []
        s = StatusUser(FauxUserInfo())

        r = s.inGroups
        self.assertFalse(r)

    @patch.object(StatusUser, 'siteGroups', new_callable=PropertyMock)
    def test_no_sites_no_activity(self, p_siteGroups):
        'If the user is in no sites then there should be no activity'
        p_siteGroups.return_value = []
        s = StatusUser(FauxUserInfo())

        r = s.hasActivity
        self.assertFalse(r)
