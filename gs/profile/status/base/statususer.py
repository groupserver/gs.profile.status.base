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
from zope.cachedescriptors.property import Lazy
from zope.component import queryMultiAdapter
from gs.cache import cache
from gs.profile.email.base import EmailUserFromUser
from .interfaces import (ISiteGroups, )
from .queries import (PostingStatsQuery, )
from .utils import previous_month

#: The time the list of site-identifiers is cached (in seconds)
SITE_CACHE_TIME = 24*60*60


class StatusUser(object):
    '''The user to get the status for

:param userInfo: The user
:type userInfo: Products.CustomUserFolder.interfaces.IGSUserInfo

The status-user is a lightweight adaptor (as in, not ZCA, because I am Lazy) around the
:class:`Products.CustomUserFolder.interfaces.IGSUserInfo`. It still implements the same interface,
as a standard user, but also supplies

* The Boolean properties :meth:`StatusUser.inGroups` and :meth:`hasActivity`
* The list of email addresses :meth:`StatusUser.addresses`.
'''
    def __init__(self, userInfo):
        self.userInfo = userInfo
        self.context = self.userInfo.context
        self.user = self.userInfo.user
        self.anonymous = self.userInfo.anonymous
        self.id = self.userInfo.id
        self.name = self.userInfo.name
        self.url = self.userInfo.url

    @Lazy
    def gsInstance(self):
        '''The identifier for the GroupServer instance:

:returns: The identifier for the folder that holds the ``Content`` folder.
:rtype: string'''
        site_root = self.context.site_root()
        retval = site_root.getId()
        return retval

    @cache('gs.profile.status.base.hook.SendNotification.possibleSites',
           lambda s: s.gsInstance, SITE_CACHE_TIME)
    def sites(self):
        '''Get the list of all sites

:returns: The folders contained in ``Content`` that have the ``is_division``
          property set to ``True``.
:rtype: list of strings.'''
        site_root = self.context.site_root()
        content = getattr(site_root, 'Content')
        retval = [fid for fid in content.objectIds(self.FOLDER_TYPES)
                  if getattr(getattr(content, fid), 'is_division', False)]
        assert type(retval) == list
        return retval

    @Lazy
    def siteGroups(self):
        '''The site and groups that the user is in

:returns: A list of sites (:class:`.interfaces.ISiteGroups`) that the user is a member of at least
          one group in the site.
:rtype: list'''
        retval = []
        groupIds = [s.split('_member')[0]
                    for s in self.userInfo.user.getGroups()]
        siteIds = [sid for sid in groupIds if sid in self.sites()]

        content = self.context.site_root().Content
        if siteIds:
            siteGroups = [queryMultiAdapter((self.userInfo, getattr(content, s)),
                                            ISiteGroups) for s in siteIds]
            retval = [sg for sg in siteGroups if sg and (sg.groupInfos is not [])]
        assert type(retval) == list
        return retval

    @Lazy
    def inGroups(self):
        '''Is the person in *any* groups (actual groups, not just sites)

:returns: ``True`` if the notification should be sent; ``False`` otherwise.
:rtype: bool'''
        retval = self.siteGroups is not []
        assert type(retval) == bool
        return retval

    @Lazy
    def statsQuery(self):
        retval = PostingStatsQuery()
        return retval

    @Lazy
    def hasActivity(self):
        '''Has the user seen any activity this month

:returns: ``True`` if the user is in one group that has had at least one post; ``False`` otherwise.
:rtype: bool'''
        retval = False  # Standard optimisim
        pm = previous_month()
        for site in self.siteGroups:
            for group in site.groupInfos:
                retval = self.statsQuery.posts_in_month(pm.month, pm.year, group.id, site.id)
                if retval != 0:
                    break
        assert type(retval) == bool
        return retval

    @Lazy
    def emailUser(self):
        retval = EmailUserFromUser(self.userInfo)
        return retval

    @Lazy
    def addresses(self):
        '''The list of delivery (preferred) email addresses'''
        retval = self.emailUser.get_delivery_addresses()
        return retval
