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
from gs.profile.email.base import EmailUser


class EmailViewlet(ProfileViewlet):
    'The email settings viewlet'

    @Lazy
    def emailUser(self):
        retval = EmailUser(self.context, self.userInfo)
        return retval

    @Lazy
    def changeEmailUrl(self):
        r = '{0}{1}/emailsettings.html'
        retval = r.format(self.siteInfo.url, self.userInfo.url)
        return retval

    @Lazy
    def preferred(self):
        retval = self.emailUser.get_delivery_addresses()
        return retval

    @Lazy
    def verified(self):
        allV = self.emailUser.get_verified_addresses()
        retval = [e for e in allV if e not in self.preferred]
        return retval

    @Lazy
    def unverified(self):
        retval = self.emailUser.get_unverified_addresses()
        return retval
