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
from collections import namedtuple
from functools import reduce
from operator import concat, attrgetter
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from gs.group.member.base import user_member_of_group, user_admin_of_group
from gs.profile.base import ProfileViewlet, ProfileContentProvider
from gs.site.member.sitemembershipvocabulary import SiteMembership


SiteGroups = namedtuple('SiteGroups', ['siteInfo', 'groupInfos'])


class GroupsViewlet(ProfileViewlet):
    'The groups viewlet'

    @Lazy
    def userGroups(self):
        self.userInfo.user.get

    @staticmethod
    def get_groupInfo(folder):
        retval = createObject('groupserver.GroupInfo', folder)
        return retval

    @staticmethod
    def get_siteInfo(folder):
        retval = createObject('groupserver.SiteInfo', folder)
        return retval

    def get_sitegroups(self, siteId):
        content = self.context.Content
        site = getattr(content, siteId)
        groups = getattr(site, 'groups')

        groupInfos = []
        for folder in groups.objectValues(['Folder', 'Folder (ordered)']):
            if user_member_of_group(self.userInfo, folder):
                groupInfo = self.get_groupInfo(folder)
                groupInfos.append(groupInfo)

        if groupInfos is []:
            m = 'Not a member of any groups in {0}'.format(siteId)
            raise ValueError(m)
        groupInfos.sort(key=attrgetter('name'))
        siteInfo = self.get_siteInfo(site)
        retval = SiteGroups(siteInfo=siteInfo, groupInfos=groupInfos)
        return retval

    @Lazy
    def sites(self):
        sites = list(SiteMembership(self.context))
        sites.sort(key=attrgetter('title'))
        retval = [self.get_sitegroups(s.token) for s in sites]

        return retval

    @Lazy
    def groups(self):
        retval = reduce(concat, [s.groupInfos for s in self.sites])
        return retval


class SiteInfo(ProfileContentProvider):
    'Ths site-information content provider'
    def __init__(self, profile, request, view):
        super(SiteInfo, self).__init__(profile, request, view)
        self.__updated = False

    @Lazy
    def isAdmin(self):
        site = self.siteInfo.siteObj
        user = self.userInfo.user
        retval = ('DivisionAdmin' in user.getRolesInContext(site))
        assert type(retval) == bool
        return retval

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        r = pageTemplate(self)
        return r


class GroupInfo(ProfileContentProvider):
    'Ths group-information content provider'
    def __init__(self, profile, request, view):
        super(GroupInfo, self).__init__(profile, request, view)
        self.__updated = False

    @Lazy
    def isAdmin(self):
        retval = user_admin_of_group(self.userInfo, self.groupInfo)
        return retval

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        r = pageTemplate(self)
        return r
