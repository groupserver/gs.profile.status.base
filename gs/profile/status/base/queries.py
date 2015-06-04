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
from collections import namedtuple
from functools import reduce
from operator import concat
import sqlalchemy as sa
from gs.database import getTable, getSession


#: Basic topic information
BasicTopic = namedtuple('BasicTopic', ['topicId', 'lastPostId', 'name'])


class LoginQuery(object):

    def __init__(self):
        self.auditEventTable = getTable('audit_event')

    def user_has_login(self, userId):
        aet = self.auditEventTable

        s = aet.select()
        s.append_whereclause(aet.c.instance_user_id == userId)
        s.append_whereclause(aet.c.subsystem == 'groupserver.Login')
        s.append_whereclause(aet.c.event_code == '1')
        s.limit = 1

        session = getSession()
        r = session.execute(s)

        retval = bool(r.rowcount)
        return retval


class SkipQuery(object):
    def __init__(self):
        self.skipTable = getTable('profile_notification_skip')

    def skip_people(self):
        s = self.skipTable.select()

        session = getSession()
        r = session.execute(s)

        retval = [x['user_id'] for x in r]
        return retval

    def has_skip(self, userId):
        s = self.skipTable.select()
        s.append_whereclause(self.skipTable.c.user_id == userId)

        session = getSession()
        r = session.execute(s)

        retval = bool(r.rowcount)
        return retval

    def add_skip(self, userId):
        i = self.skipTable.insert()
        d = {'user_id': userId}

        session = getSession()
        session.execute(i, params=d)

    def remove_skip(self, userId):
        d = self.skipTable.delete(self.skipTable.c.user_id == userId)
        session = getSession()
        session.execute(d)


class PostingStatsQuery(object):
    def __init__(self):
        self.postTable = getTable('post')
        self.topicTable = getTable('topic')
        self.topicKeywordsTable = getTable('topic_keywords')

    @staticmethod
    def year(dateCol):
        retval = sa.extract('year', dateCol)
        return retval

    @staticmethod
    def month(dateCol):
        retval = sa.extract('month', dateCol)
        return retval

    def posts_in_month(self, month, year, groupId, siteId):
        'Get the number of posts in a particular month'
        pt = self.postTable
        s = sa.select([sa.func.count(pt.c.post_id).label('n_posts')])
        s.append_whereclause(self.month(pt.c.date) == month)
        s.append_whereclause(self.year(pt.c.date) == year)
        s.append_whereclause(pt.c.group_id == groupId)
        s.append_whereclause(pt.c.site_id == siteId)

        session = getSession()
        r = session.execute(s)

        retval = r.fetchone()['n_posts']
        return retval

    def topics_in_month(self, month, year, groupId, siteId):
        'Get the names of the topics in a particular month'
        tt = self.topicTable
        s = sa.select([tt.c.topic_id, tt.c.last_post_id, tt.c.original_subject])
        s.append_whereclause(self.month(tt.c.last_post_date) == month)
        s.append_whereclause(self.year(tt.c.last_post_date) == year)
        s.append_whereclause(tt.c.group_id == groupId)
        s.append_whereclause(tt.c.site_id == siteId)
        s.order_by(sa.desc(tt.c.num_posts))

        session = getSession()
        r = session.execute(s)

        retval = [BasicTopic(topicId=x['topic_id'],
                             lastPostId=x['last_post_id'],
                             name=x['original_subject']) for x in r]
        return retval

    def authors_in_month(self, month, year, groupId, siteId):
        'Get the distinct user-ids of the authors in a particular month'
        pt = self.postTable
        s = sa.select([sa.func.distinct(pt.c.user_id).label('user_id')])
        s.append_whereclause(self.month(pt.c.date) == month)
        s.append_whereclause(self.year(pt.c.date) == year)
        s.append_whereclause(pt.c.group_id == groupId)
        s.append_whereclause(pt.c.site_id == siteId)

        session = getSession()
        r = session.execute(s)

        retval = [x['user_id'] for x in r]
        return retval

    def keywords_in_month(self, month, year, groupId, siteId):
        tt = self.topicTable
        tkt = self.topicKeywordsTable
        s = sa.select([tkt.c.keywords])
        s.append_whereclause(self.month(tt.c.last_post_date) == month)
        s.append_whereclause(self.year(tt.c.last_post_date) == year)
        s.append_whereclause(tt.c.group_id == groupId)
        s.append_whereclause(tt.c.site_id == siteId)
        s.append_whereclause(tt.c.topic_id == tkt.c.topic_id)

        session = getSession()
        r = session.execute(s)

        retval = list(set(reduce(concat, [x['keywords'] for x in r], [])))
        return retval
