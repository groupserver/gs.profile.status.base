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
from gs.profile.base import ProfileViewlet


class NewsViewlet(ProfileViewlet):
    'The viewlet for the News section'

    mailto = 'mailto:{to}?subject={subject}&body={body}'
    newsHTML = 'gs-profile-status-news.xml'

    @Lazy
    def show(self):
        retval = hasattr(self.siteInfo.siteObj, self.newsHTML)
        return retval

    @Lazy
    def news(self):
        news = getattr(self.siteInfo.siteObj, self.newsHTML)
        retval = news()
        return retval
