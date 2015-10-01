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
from enum import Enum
from json import dumps as to_json
from logging import getLogger
log = getLogger('gs.profile.status.base.hook')
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from gs.content.form.api.json import SiteEndpoint
from gs.auth.token import log_auth_error
from .audit import (Auditor, SENT_STATUS, SKIPPED_STATUS_EMAIL, SKIPPED_STATUS_GROUPS,
                    SKIPPED_STATUS_ANON, SKIPPED_STATUS_INACTIVE, SKIPPED_STATUS_EXPLICIT)
from .interfaces import (IGetPeople, ISendNotification, )
from .notifier import StatusNotifier
from .queries import (SkipQuery, )
from .statususer import StatusUser


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


class Status(Enum):
    __order__ = 'ok no_user no_groups no_email no_activity other_issue'  # Only needed in 2.7
    ok = 0
    no_user = -2
    no_groups = -4
    no_email = -8
    no_activity = -16
    skip = -32  # Opted out
    other_issue = -1024


class SendNotification(SiteEndpoint):
    '''The page that sends a status-reminder to a person'''
    label = 'Send a status reminder'
    form_fields = form.Fields(ISendNotification, render_context=False)

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
        statusUser = StatusUser(self.context, userInfo)
        if statusUser.anonymous:
            self.auditor.info(SKIPPED_STATUS_ANON,
                              instanceDatum=data['profileId'])
            m = 'Cannot find the user object for the user ID ({0})'
            msg = m.format(data['profileId'])
            r = {'status': Status.no_user.value, 'message': msg}
        elif statusUser.hasSkip:
            # --=mpj17=-- This should never happen, but I have it here just in case
            self.auditor.info(SKIPPED_STATUS_EXPLICIT, statusUser)
            m = 'Skipping the monthly profile-status notification for '\
                '{0} ({1}): explicitly opted out'
            msg = m.format(statusUser.name, statusUser.id)
            r = {'status': Status.skip.value, 'message': msg}
        elif statusUser.inGroups:
            if statusUser.addresses:
                if statusUser.hasActivity:
                    # --=mpj17=-- To summarise, if we are here then the person is in some groups
                    # (not just sites) *and* they have at least one working email address *and*
                    # there has been some activity in at least one group group this last month.
                    notifier = StatusNotifier(statusUser.user, self.request)
                    notifier.notify()
                    self.auditor.info(SENT_STATUS, statusUser, repr(statusUser.addresses))
                    m = 'Sent the monthly profile-status notification to {0} '\
                        '({1})'
                    msg = m.format(statusUser.name, statusUser.id)
                    r = {'status': Status.ok.value, 'message': msg}
                else:  # no activity
                    self.auditor.info(SKIPPED_STATUS_INACTIVE, statusUser)
                    m = 'Skipping the monthly profile-status notification for '\
                        '{0} ({1}): no activity in any groups this month'
                    msg = m.format(statusUser.name, statusUser.id)
                    r = {'status': Status.no_activity.value, 'message': msg}
            else:  # No email addresses
                self.auditor.info(SKIPPED_STATUS_EMAIL, statusUser)
                m = 'Skipping the monthly profile-status notification for '\
                    '{0} ({1}): no verified email addresses'
                msg = m.format(statusUser.name, statusUser.id)
                r = {'status': Status.no_email.value, 'message': msg}
            assert type(r) == dict
        else:  # No groups
            # --=mpj17=-- The groups is calculated first, even though it is very expensive in
            # terms of ZODB access  I do this to get a nice list of people that we may want to
            # drop from the ZODB.
            self.auditor.info(SKIPPED_STATUS_GROUPS, statusUser)
            m = 'Skipping the monthly profile-status notification for '\
                '{0} ({1}): not in any groups'
            msg = m.format(statusUser.name, statusUser.id)
            r = {'status': Status.no_groups.value, 'message': msg}
        retval = to_json(r)
        return retval

    def handle_send_failure(self, action, data, errors):
        log_auth_error(self.context, self.request, errors)
        retval = self.build_error_response(action, data, errors)
        return retval
