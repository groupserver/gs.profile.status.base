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
from json import dumps as to_json
from logging import getLogger
log = getLogger('gs.profile.status.base.hook')
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, queryMultiAdapter
from zope.formlib import form
from gs.cache import cache
from gs.content.form.api.json import SiteEndpoint
from gs.auth.token import log_auth_error
from gs.profile.email.base import EmailUserFromUser
from .audit import (Auditor, SENT_STATUS, SKIPPED_STATUS_EMAIL, SKIPPED_STATUS_GROUPS,
                    SKIPPED_STATUS_ANON)
from .interfaces import (IGetPeople, ISendNotification, ISiteGroups)
from .notifier import StatusNotifier
from .queries import SkipQuery


class MembersHook(SiteEndpoint):
    '''The page that gets a list of people to send the status reminder to'''
    label = 'Get the people to send the digest to'
    form_fields = form.Fields(IGetPeople, render_context=False)

    @form.action(label='Get', name='get', prefix='',
                 failure='handle_get_people_failure')
    def handle_get_people(self, action, data):
        '''The form action for the *Get members* page.

:param action: The button that was clicked.
:param dict data: The form data.'''
        retval = to_json(self.profileIds)
        return retval

    def handle_get_people_failure(self, action, data, errors):
        log_auth_error(self.context, self.request, errors)
        retval = self.build_error_response(action, data, errors)
        return retval

    @Lazy
    def query(self):
        retval = SkipQuery()
        return retval

    @Lazy
    def profileIds(self):
        '''All the members of the GroupServer instance.'''
        acl_users = self.context.acl_users
        retval = list(set(acl_users.getUserNames()) - set(self.query.skip_people()))
        return retval

#: The time the list of site-identifiers is cached (in seconds)
SITE_CACHE_TIME = 24*60*60


class SendNotification(SiteEndpoint):
    '''The page that sends a status-reminder to a person'''
    label = 'Send a status reminder'
    form_fields = form.Fields(ISendNotification, render_context=False)
    FOLDER_TYPES = ['Folder', 'Folder (ordered)']
    STATUS = {'other_issue': -1024, 'no_email': -8, 'no_groups': -4,
              'no_user': -2, 'ok': 0, }

    @Lazy
    def auditor(self):
        retval = Auditor(self.context)
        return retval

    @form.action(label='Send', name='send', prefix='',
                 failure='handle_send_failure')
    def handle_send(self, action, data):
        '''The form action for the *Send notification* page.

:param action: The button that was clicked.
:param dict data: The form data.'''
        userInfo = createObject('groupserver.UserFromId',
                                self.context, data['profileId'])
        if userInfo.anonymous:
            self.auditor.info(SKIPPED_STATUS_ANON,
                              instanceDatum=data['profileId'])
            m = 'Cannot find the user object for the user ID ({0})'
            msg = m.format(data['profileId'])
            r = {'status': self.STATUS['no_user'], 'message': msg}
        elif self.in_groups(userInfo):
            emailUser = EmailUserFromUser(userInfo)
            if emailUser.get_delivery_addresses():
                notifier = StatusNotifier(userInfo.user, self.request)
                notifier.notify()
                self.auditor.info(SENT_STATUS, userInfo,
                                  repr(emailUser.get_delivery_addresses()))
                m = 'Sent the monthly profile-status notification to {0} '\
                    '({1})'
                msg = m.format(userInfo.name, userInfo.id)
                r = {'status': self.STATUS['ok'], 'message': msg}
            else:  # No email addresses
                self.auditor.info(SKIPPED_STATUS_EMAIL, userInfo)
                m = 'Skipping the monthly profile-status notification for '\
                    '{0} ({1}): no verified email addresses'
                msg = m.format(userInfo.name, userInfo.id)
                r = {'status': self.STATUS['no_email'], 'message': msg}
        else:  # No groups
            self.auditor.info(SKIPPED_STATUS_GROUPS, userInfo)
            m = 'Skipping the monthly profile-status notification for '\
                '{0} ({1}): not in any groups'
            msg = m.format(userInfo.name, userInfo.id)
            r = {'status': self.STATUS['no_groups'], 'message': msg}
        retval = to_json(r)
        return retval

    def in_groups(self, userInfo):
        '''Is the person in *any* groups (actual groups, not just sites)

:param userInfo: The user
:type userInfo: Products.CustomUserFolder.interfaces.IGSUserInfo
:returns: ``True`` if the notification should be sent; ``False`` otherwise.
:rtype: bool'''
        groupIds = [s.split('_member')[0]
                    for s in userInfo.user.getGroups()]
        siteIds = [sid for sid in groupIds if sid in self.sites()]

        retval = False
        content = self.context.site_root().Content
        if siteIds:
            siteGroups = [queryMultiAdapter((userInfo, getattr(content, s)),
                                            ISiteGroups) for s in siteIds]
            siteGroups = [sg for sg in siteGroups
                          if sg and (sg.groupInfos is not [])]
            retval = siteGroups is not []
        return retval

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

:returns: The folders contained in ``Content`` that have ``is_division``
          set to ``True``.
:rtype: list of strings.'''
        site_root = self.context.site_root()
        content = getattr(site_root, 'Content')
        retval = [fid for fid in content.objectIds(self.FOLDER_TYPES)
                  if getattr(getattr(content, fid), 'is_division', False)]
        return retval

    def handle_send_failure(self, action, data, errors):
        log_auth_error(self.context, self.request, errors)
        retval = self.build_error_response(action, data, errors)
        return retval
