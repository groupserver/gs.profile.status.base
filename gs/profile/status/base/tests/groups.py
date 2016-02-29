# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 OnlineGroups.net and Contributors.
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
from functools import partial
from mock import (MagicMock, patch, PropertyMock)
from unittest import TestCase
from gs.profile.status.base.groups import (GroupInfo, )


class TestGroupInfo(TestCase):
    '''Test the ``GroupInfo`` class'''

    @patch.object(GroupInfo, 'isAdmin', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'groupVisibility', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'fullMembers', new_callable=PropertyMock)
    def test_privacyTooStrict_not_admin(self, m_fM, m_gV, m_iA):
        'Test that the privacy is never too strict if we are a normal member'
        m_iA.return_value = False
        m_gV().isSecret = True
        m_fM.return_value = list(range(0, 24))

        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.privacyTooStrict

        self.assertFalse(r)

    @patch.object(GroupInfo, 'isAdmin', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'groupVisibility', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'fullMembers', new_callable=PropertyMock)
    def test_privacyTooStrict_not_secret(self, m_fM, m_gV, m_iA):
        'Test that the privacy is never too strict if we are a non-secret group'
        m_iA.return_value = True
        m_gV().isSecret = False
        m_fM.return_value = list(range(0, 24))

        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.privacyTooStrict

        self.assertFalse(r)

    @patch.object(GroupInfo, 'isAdmin', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'groupVisibility', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'fullMembers', new_callable=PropertyMock)
    def test_privacyTooStrict_small(self, m_fM, m_gV, m_iA):
        'Test that the privacy is never too strict if we are a small group'
        m_iA.return_value = True
        m_gV().isSecret = True
        m_fM.return_value = list(range(0, 2))

        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.privacyTooStrict

        self.assertFalse(r)

    @patch.object(GroupInfo, 'isAdmin', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'groupVisibility', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'fullMembers', new_callable=PropertyMock)
    def test_privacyTooStrict(self, m_fM, m_gV, m_iA):
        'Test that the privacy is too strict for large secret groups if we are the admin'
        m_iA.return_value = True
        m_gV().isSecret = True
        m_fM.return_value = list(range(0, 24))

        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.privacyTooStrict

        self.assertTrue(r)

    @patch.object(GroupInfo, 'authorIds', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'userInfo', new_callable=PropertyMock)
    def test_one_is_the_lonliest_number(self, m_uI, m_aI):
        'Test the ``userIsOnlyAuthor`` property'
        m_uI().id = 'example'
        m_aI.return_value = ['example', ]
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.userIsOnlyAuthor

        self.assertTrue(r)

    @patch.object(GroupInfo, 'authorIds', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'userInfo', new_callable=PropertyMock)
    def test_reader(self, m_uI, m_aI):
        'Test the ``userIsOnlyAuthor`` property if the user only read'
        m_uI().id = 'example'
        m_aI.return_value = ['dirk', 'dinsdale', ]
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.userIsOnlyAuthor

        self.assertFalse(r)

    @patch.object(GroupInfo, 'authorIds', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'userInfo', new_callable=PropertyMock)
    def test_friends(self, m_uI, m_aI):
        'Test the ``userIsOnlyAuthor`` property if the user was one of the many authors'
        m_uI().id = 'dirk'
        m_aI.return_value = ['dirk', 'dinsdale', ]
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        r = g.userIsOnlyAuthor

        self.assertFalse(r)

    @staticmethod
    def get_user_info(factoryName, context, userId, anonymous):
        '''A utility method that allows us to easily mock calls to the createObject function'''
        retval = MagicMock()
        retval.id = userId
        retval.name = 'Named {0}'.format(userId)
        retval.anonymous = anonymous
        return retval

    @patch('gs.profile.status.base.groups.createObject')
    def test_prefer_photos_anon(self, m_cO):
        'Ensure we do not return Anonymous as a person with a photo'
        m_cO.side_effect = partial(self.get_user_info, anonymous=True)
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        g.groupInfo = MagicMock()  # Normally the group-info is passed in from the page namespace
        ids = list(range(0, g.maxAuthors))
        r = g.prefer_photos(ids)

        self.assertEqual([], r)
        self.assertEqual(len(ids), m_cO.call_count)

    @patch('gs.profile.status.base.groups.createObject')
    @patch('gs.profile.status.base.groups.get_image_file')
    def test_prefer_photos_no_image(self, m_g_i_f, m_cO):
        'Ensure we cope if no one has an image'
        m_g_i_f.return_value = None
        m_cO.side_effect = partial(self.get_user_info, anonymous=False)
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        g.groupInfo = MagicMock()  # Normally the group-info is passed in from the page namespace
        ids = list(range(0, g.maxAuthors))
        r = g.prefer_photos(ids)

        self.assertEqual(len(ids), m_cO.call_count)
        self.assertEqual(len(ids), m_g_i_f.call_count)
        self.assertEqual(ids, [u.id for u in r])

    @patch('gs.profile.status.base.groups.createObject')
    @patch('gs.profile.status.base.groups.get_image_file')
    def test_prefer_photos(self, m_g_i_f, m_cO):
        'Ensure we prefer it if someone has an image'
        m_g_i_f.side_effect = [None, 'image', None, 'image', 'image']
        m_cO.side_effect = partial(self.get_user_info, anonymous=False)
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        g.groupInfo = MagicMock()  # Normally the group-info is passed in from the page namespace
        ids = list(range(0, 5))
        r = g.prefer_photos(ids)

        self.assertEqual(len(ids), m_cO.call_count)
        self.assertEqual(len(ids), m_g_i_f.call_count)
        # --=mpj17=-- 0 and 2 are last because they lack an image
        self.assertEqual([1, 3, 4, 0, 2], [u.id for u in r])

    @patch.object(GroupInfo, 'userInfo', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'prefer_photos')
    def test_get_max_people_author(self, m_p_p, m_uI):
        'Test the user is removed from the list of people'
        m_p_p.return_value = []
        m_uI().id = 0
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        ids = list(range(0, g.maxAuthors))
        g.get_max_people(ids)

        m_p_p.assert_called_once_with(list(range(1, g.maxAuthors)))

    @patch.object(GroupInfo, 'userInfo', new_callable=PropertyMock)
    @patch.object(GroupInfo, 'prefer_photos')
    def test_get_max_people_user_not_author(self, m_p_p, m_uI):
        'Test the the list of people is fine if the user is not in the lits'
        m_p_p.return_value = []
        m_uI().id = 'example'
        g = GroupInfo(MagicMock(), MagicMock(), MagicMock())
        ids = list(range(0, g.maxAuthors))
        g.get_max_people(ids)

        m_p_p.assert_called_once_with(list(range(0, g.maxAuthors)))
