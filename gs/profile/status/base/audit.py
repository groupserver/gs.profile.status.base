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
from __future__ import absolute_import, unicode_literals
from datetime import datetime
SUBSYSTEM = 'gs.profile.status.base'
import logging
log = logging.getLogger(SUBSYSTEM)
from pytz import UTC
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.XWFCore.XWFUtils import munge_date
from gs.core import to_id

UNKNOWN = '0'
SENT_STATUS = '1'
SKIPPED_STATUS_EMAIL = '2'
SKIPPED_STATUS_GROUPS = '3'
SKIPPED_STATUS_ANON = '4'


@implementer(IFactory)
class AuditEventFactory(object):
    title = 'Profile summary audit-event factory'
    description = 'Creates a GroupServer audit event for profile-status events'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                 supplementaryDatum='', subsystem=''):
        if code == SENT_STATUS:
            event = SentStatusEvent(context, event_id, date, instanceUserInfo, instanceDatum)
        elif code == SKIPPED_STATUS_EMAIL:
            event = SkippedStatusEmailEvent(context, event_id, date, instanceUserInfo)
        elif code == SKIPPED_STATUS_GROUPS:
            event = SkippedStatusGroupsEvent(context, event_id, date, instanceUserInfo)
        elif code == SKIPPED_STATUS_ANON:
            event = SkippedStatusAnonEvent(context, event_id, date, instanceDatum)
        else:
            event = BasicAuditEvent(
                context, event_id, UNKNOWN, date, userInfo,
                instanceUserInfo, siteInfo, groupInfo, instanceDatum,
                supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class SentStatusEvent(BasicAuditEvent):
    ''' An audit-trail event representing a profile-status being sent to a person'''
    def __init__(self, context, eventId, d, recipientUserInfo, emailAddrs):
        super(SentStatusEvent, self).__init__(
            context, eventId, SENT_STATUS, d, None, recipientUserInfo, None,
            None, emailAddrs, None, SUBSYSTEM)

    def __unicode__(self):
        r = '{userInfo.name} ({userInfo.id}) was sent the profile-status '\
            'notification, using {email}.'
        retval = r.format(userInfo=self.instanceUserInfo, email=self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        r = '<span class="audit-event gs-profile-status-base-{0}">Sent the '\
            'profile-status notification</span>'
        retval = r.format(self.code)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class SkippedStatusEmailEvent(BasicAuditEvent):
    '''An audit-trail event representing a profile-status not being sent
    because the person lacks verified email addresses'''
    def __init__(self, context, eventId, d, recipientUserInfo):
        super(SkippedStatusEmailEvent, self).__init__(
            context, eventId, SKIPPED_STATUS_EMAIL, d, None, recipientUserInfo, None,
            None, None, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Skipped the profile-status notification for {userInfo.name} '\
            '({userInfo.id}) because they have no verified email addresses'
        retval = r.format(userInfo=self.instanceUserInfo)
        return retval

    @property
    def xhtml(self):
        r = '<span class="audit-event gs-profile-status-base-{0}">Skipped the '\
            'profile-status notification: lack verified email addresses</span>'
        retval = r.format(self.code)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class SkippedStatusGroupsEvent(BasicAuditEvent):
    '''An audit-trail event representing a profile-status not being sent
    because the person is not in any groups.'''
    def __init__(self, context, eventId, d, recipientUserInfo):
        super(SkippedStatusGroupsEvent, self).__init__(
            context, eventId, SKIPPED_STATUS_GROUPS, d, None,
            recipientUserInfo, None, None, None, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Skipped the profile-status notification for {userInfo.name} '\
            '({userInfo.id}) because they are not in any groups'
        retval = r.format(userInfo=self.instanceUserInfo)
        return retval

    @property
    def xhtml(self):
        r = '<span class="audit-event gs-profile-status-base-{0}">Skipped the '\
            'profile-status notification: not a member of any groups.</span>'
        retval = r.format(self.code)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class SkippedStatusAnonEvent(BasicAuditEvent):
    '''An audit-trail event representing a profile-status not being sent
    because the person lacks verified email addresses'''
    def __init__(self, context, eventId, d, unknownUserId):
        super(SkippedStatusAnonEvent, self).__init__(
            context, eventId, SKIPPED_STATUS_ANON, d, None, None, None,
            None, unknownUserId, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Skipped the profile-status notification because there is no '\
            'user-object ({userInfoId})'
        retval = r.format(userInfoId=self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        r = '<span class="audit-event gs-profile-status-base-{0}">No '\
            'user for identifier <code>{id}</code>.</span>'
        retval = r.format(self.code, self.instanceDatum)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class Auditor(object):
    def __init__(self, context):
        self.context = context
        self.queries = AuditQuery()
        self.factory = AuditEventFactory()

    def info(self, code, recipientUserInfo=None, instanceDatum=''):
        d = datetime.now(UTC)
        s = code + repr(recipientUserInfo) + instanceDatum + d.isoformat()
        eventId = to_id(s)

        e = self.factory(
            self.context, eventId, code, d, None, recipientUserInfo, None,
            None, instanceDatum, None, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
