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
from __future__ import (absolute_import, print_function, unicode_literals,
                        division)
from datetime import date
from functools import reduce
from operator import concat, attrgetter
from random import shuffle
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from zope.contentprovider.interfaces import UpdateNotCalled
from gs.core import curr_time, comma_comma_and
from gs.group.member.base import user_admin_of_group
from gs.group.privacy.interfaces import IGSGroupVisibility
from gs.group.stats import GroupPostingStats
from gs.profile.base import ProfileViewlet, ProfileContentProvider
from gs.profile.image.base import get_file as get_image_file
from gs.site.member.sitemembershipvocabulary import SiteMembership
from gs.group.member.base import get_group_userids
from gs.group.member.canpost.interfaces import IGSPostingUser
from gs.group.member.email.base import (GroupEmailUser, GroupEmailSetting)
from Products.GSGroup.interfaces import IGSMailingListInfo
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from .interfaces import ISiteGroups
from .queries import PostingStatsQuery
from .sitegroups import NoGroups
from .utils import mailto


class GroupsViewlet(ProfileViewlet):
    'The groups viewlet'

    @Lazy
    def show(self):
        retval = self.sites is not []
        return retval

    @Lazy
    def userGroups(self):
        self.userInfo.user.get

    def get_sitegroups(self, siteId):
        content = self.context.Content
        site = getattr(content, siteId)
        retval = getMultiAdapter((self.userInfo, site), ISiteGroups)
        return retval

    @Lazy
    def sites(self):
        sites = list(SiteMembership(self.context))
        sites.sort(key=attrgetter('title'))
        retval = []
        for s in sites:
            try:
                siteGroups = self.get_sitegroups(s.token)
                retval.append(siteGroups)
            except NoGroups:
                continue
        return retval

    @Lazy
    def groups(self):
        retval = reduce(concat, [s.groupInfos for s in self.sites], [])
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

    #: How many posts are considered *many*, and people should do
    #: something about it, like switch to the digest.
    manyPosts = 31

    #: How many posts are considered *few*, so people may need to
    #: start interacting more closely with the group by coming off
    #: the digest.
    fewPosts = 4

    #: The maximum number of authors to show in the *facepile*.
    maxAuthors = 6

    #: The maximum length (in characters) for the topics and keywords,
    #: ignoring the seperating commas.
    maxTextLen = 127

    def __init__(self, profile, request, view):
        super(GroupInfo, self).__init__(profile, request, view)
        self.__updated = False

    def update(self):
        self.__updated = True
        self.notificationSiteInfo = self.siteInfo
        self.siteInfo = self.groupInfo.siteInfo

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        r = pageTemplate(self)
        return r

    # Methods and properties that are not part of the standard content
    # provider API are below this point

    @Lazy
    def isAdmin(self):
        '''Is the user an administrator of the group?

:returns: ``True`` if the user is a group administrator.
:rtype: bool'''
        retval = user_admin_of_group(self.userInfo, self.groupInfo)
        return retval

    @Lazy
    def groupVisibility(self):
        retval = IGSGroupVisibility(self.groupInfo)
        return retval

    @Lazy
    def groupStats(self):
        retval = GroupPostingStats(self.groupInfo)
        return retval

    @Lazy
    def membersInfo(self):
        retval = GSGroupMembersInfo(self.groupInfo.groupObj)
        return retval

    @Lazy
    def privacyTooStrict(self):
        '''Is the privacy of the group too tight?

:returns: ``True`` if the user is a group administrator, the privacy
          of the group is ``secret``, and there are more than a dozen
          members.
:rtype: bool'''
        retval = (self.isAdmin and self.groupVisibility.isSecret
                  and (self.membersInfo.fullMemberCount > 12))
        return retval

    @Lazy
    def statsQuery(self):
        retval = PostingStatsQuery()
        return retval

    @Lazy
    def previousMonth(self):
        '''Get the previous month from now

:returns: The previous month.
:rtype: datetime.date'''
        dt = curr_time()
        if dt.month == 1:
            newMonth = 12
            newYear = dt.year - 1
        else:
            newMonth = dt.month - 1
            newYear = dt.year
        retval = date(newYear, newMonth, 1)
        return retval

    @Lazy
    def nPosts(self):
        'The number of posts the previous month'
        pm = self.previousMonth
        retval = self.statsQuery.posts_in_month(
            pm.month, pm.year, self.groupInfo.id, self.siteInfo.id)
        return retval

    @Lazy
    def switchToDigest(self):
        '``True`` if the member should switch to digest-mode'
        manyPosts = (self.nPosts >= self.manyPosts)
        geu = GroupEmailUser(self.userInfo, self.groupInfo)
        emailPerPost = geu.get_delivery_setting() == GroupEmailSetting.default
        retval = manyPosts and emailPerPost
        return retval

    @Lazy
    def switchFromDigest(self):
        '``True`` if the member should switch from digest-mode'
        fewPosts = (self.nPosts <= self.fewPosts)
        geu = GroupEmailUser(self.userInfo, self.groupInfo)
        digest = geu.get_delivery_setting() == GroupEmailSetting.digest
        retval = fewPosts and digest
        return retval

    @Lazy
    def authorIds(self):
        pm = self.previousMonth
        retval = self.statsQuery.authors_in_month(
            pm.month, pm.year, self.groupInfo.id, self.siteInfo.id)
        shuffle(retval)  # Mostly for self.specificAuthorIds
        return retval

    @Lazy
    def userIsOnlyAuthor(self):
        retval = ((len(self.authorIds) == 1)
                  and (self.authorIds[0] == self.userInfo.id))
        return retval

    @Lazy
    def nAuthors(self):
        'The number of authors in the previous month, for the ZPT'
        retval = len(self.authorIds)
        return retval

    def get_max_people(self, ids):
        '''Get :var:`maxAuthors` from the list of ids. The ID of the
current user is never in the list'''
        try:
            # Throw the author away.
            ids.remove(self.userInfo.id)
        except ValueError:
            # User not in the list. No worries.
            pass
        retval = self.prefer_photos(ids)[:self.maxAuthors]
        assert type(retval) == list
        assert len(retval) <= self.maxAuthors
        return retval

    def prefer_photos(self, userIds):
        '''Get a list of userInfo object, preferring people with photos

:param list userIds: A list of user identifiers
:returns: A list of userInfo objects, with the people with photos placed first
:rtype: list'''
        r = [createObject('groupserver.UserFromId',
                          self.groupInfo.groupObj, u) for u in userIds]
        photos = []
        noPhotos = []
        for u in r:
            try:
                if u.anonymous:
                    continue
                elif (get_image_file(self.context, u) is not None):
                    photos.append(u)
                else:
                    noPhotos.append(u)
            except IOError:
                noPhotos.append(u)
        retval = photos + noPhotos
        return retval

    @Lazy
    def specificAuthors(self):
        '''Five random recent authors, not including this person

:returns: A list of the user-info instances of five recent authors
:rtype: list'''
        retval = self.get_max_people(self.authorIds)
        return retval

    @Lazy
    def authors(self):
        '''The names of random recent authors, not including this person

:returns: The names of five recent authors, seperated by commas
:rtype: str'''
        authorNames = [u.name for u in self.specificAuthors]
        retval = comma_comma_and(authorNames)
        if (retval is not '') and (self.nAuthors != len(authorNames)):
            retval = 'including {0}'.format(retval)
        return retval

    @Lazy
    def specificMembers(self):
        allIds = get_group_userids(self.groupInfo.groupObj, self.groupInfo)
        shuffle(allIds)
        retval = self.get_max_people(allIds)
        return retval

    @Lazy
    def topics(self):
        pm = self.previousMonth
        retval = self.statsQuery.topics_in_month(
            pm.month, pm.year, self.groupInfo.id, self.siteInfo.id)
        shuffle(retval)
        return retval

    @Lazy
    def nTopics(self):
        retval = len(self.topics)
        return retval

    @Lazy
    def specificTopics(self):
        specificTopics = []
        n = 0
        for topic in self.topics:
            n += len(topic.name)
            if n >= self.maxTextLen:
                break
            specificTopics.append(topic)
        t = '<a href="{siteInfo.url}/r/topic/{topic.lastPostId}">'\
            '{topic.name}</a>'
        topicLinks = [t.format(siteInfo=self.siteInfo, topic=topic)
                      for topic in specificTopics]
        retval = comma_comma_and(topicLinks)
        return retval

    @staticmethod
    def case_reduce(l):
        u = []
        retval = []
        for word in l:
            if word.upper() not in u:
                u.append(word.upper())
                retval.append(word)
        return retval

    @Lazy
    def keywords(self):
        pm = self.previousMonth
        r = self.statsQuery.keywords_in_month(
            pm.month, pm.year, self.groupInfo.id, self.siteInfo.id)
        retval = self.case_reduce(r)
        return retval

    @Lazy
    def specificKeywords(self):
        specificKeywords = []
        n = 0
        for keyword in self.keywords:
            if (len(keyword) > 31) or ('@' in keyword) or ('www' in keyword):
                continue
            n += len(keyword)
            if n >= self.maxTextLen:
                break
            specificKeywords.append(keyword)
        markedUpKeywords = self.markup_keywords(specificKeywords)
        shuffle(markedUpKeywords)
        retval = comma_comma_and(markedUpKeywords)
        return retval

    @staticmethod
    def markup_keywords(keywords):
        l = len(keywords)
        third1 = l//3
        third2 = ((l*2)//3)
        important = ['<b>{0}</b>'.format(w) for w in keywords[:third1]]
        normal = keywords[third1:third2]
        minor = ['<span class="muted">{0}</span>'.format(w)
                 for w in keywords[third2:]]
        retval = important + normal + minor
        assert len(retval) == l
        return retval

    @Lazy
    def canPost(self):
        retval = IGSPostingUser(self.userInfo, self.groupInfo).canPost
        return retval

    @Lazy
    def groupEmail(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval

    @Lazy
    def unsubscribeLink(self):
        b = '''Hello,

Please remove me from {0}
<{1}>.

--
{2} <{3}{4}>'''
        uBody = b.format(self.groupInfo.name, self.groupInfo.url,
                         self.userInfo.name, self.siteInfo.url,
                         self.userInfo.url)
        retval = mailto(self.groupEmail, 'Unsubscribe', uBody)
        return retval

    @Lazy
    def digestLink(self):
        b = '''Hello,

Please set me to digest-mode for {0}
<{1}>.

--
{2} <{3}{4}>'''
        uBody = b.format(self.groupInfo.name, self.groupInfo.url,
                         self.userInfo.name, self.siteInfo.url,
                         self.userInfo.url)
        retval = mailto(self.groupEmail, 'Digest on', uBody)
        return retval

    @Lazy
    def digestOffLink(self):
        b = '''Hello,

Please take me off digest-mode for {0}
<{1}>.

--
{2} <{3}{4}>'''
        uBody = b.format(self.groupInfo.name, self.groupInfo.url,
                         self.userInfo.name, self.siteInfo.url,
                         self.userInfo.url)
        retval = mailto(self.groupEmail, 'Digest off', uBody)
        return retval
