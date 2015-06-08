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
from operator import attrgetter
from zope.component import createObject, getMultiAdapter
from gs.group.member.base import user_member_of_group
from Products.GSGroup.groupInfo import GSGroupInfo
from .interfaces import IStatusGroupInfo

#: The "types" of folder objects in the ZMI
FOLDER_TYPES = ['Folder', 'Folder (ordered)']


class NoGroups(ValueError):
    'No groups on the site'


class Skip(NoGroups):
    'No groups on the site, because the site must be skipped'


class SiteGroups(object):
    '''The groups on a site'''

    def __init__(self, user, site):
        if site.getProperty('skip_profile_status', False):
            # Sites with the property "skip_profile_status" set are
            # skipped
            raise Skip

        groups = getattr(site, 'groups')
        # Normally the StatusGroupInfo below, but not always.
        gis = [getMultiAdapter((user, folder), IStatusGroupInfo)
               for folder in groups.objectValues(FOLDER_TYPES)
               if folder.getProperty('is_group', False)]
        self.groupInfos = [gi for gi in gis if gi.show]
        self.groupInfos.sort(key=attrgetter('name'))
        if self.groupInfos is []:
            m = 'Not a member of any groups in {0}'.format(site.getId())
            raise NoGroups(m)

        self.siteInfo = self.get_siteInfo(site)

    @staticmethod
    def get_groupInfo(folder):
        retval = createObject('groupserver.GroupInfo', folder)
        return retval

    @staticmethod
    def get_siteInfo(folder):
        retval = createObject('groupserver.SiteInfo', folder)
        return retval


class StatusGroupInfo(GSGroupInfo):
    def __init__(self, user, group):
        self.user = user
        super(StatusGroupInfo, self).__init__(group)

    @property
    def show(self):
        retval = user_member_of_group(self.user, self.groupObj)
        return retval
