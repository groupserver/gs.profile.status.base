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
from __future__ import unicode_literals
from zope.interface import Interface
from zope.schema import ASCIILine, Bool, Field
from zope.viewlet.interfaces import IViewletManager
from gs.auth.token import AuthToken
from Products.GSGroup.interfaces import IGSGroupInfo


class IGetPeople(Interface):
    'Get the people'
    token = AuthToken(
        title='Token',
        description='The authentication token',
        required=True)


class ISendNotification(Interface):
    '''Declares the form that will be used to send the notification.'''

    profileId = ASCIILine(
        title='Profile identifier',
        description='The identifier for the recipient of the notification',
        required=True)

    token = AuthToken(
        title='Token',
        description='The authentication token',
        required=True)


class IProfileStatusNotification(IViewletManager):
    '''A viewlet manager for the profile status notification'''


class IProfileStatusNotificationText(IViewletManager):
    '''A viewlet manager for the text-version of the profile status notification'''


class IGSSiteInfoContentProvider(Interface):
    siteInfo = Field(
        title="Site information",
        description="The site-information instance to display",
        required=True,
        readonly=False)

    groupInfos = Field(
        title="Groups information",
        description="The list of groupInfo instances for the groups "
                    "in the site",
        required=True,
        readonly=False)

    pageTemplateFileName = ASCIILine(
        title="Page Template File Name",
        description='The name of the ZPT file that is used to render '
                    'the post.',
        required=False,
        default=b"browser/templates/siteinfo-html.pt")


class IGSGroupInfoContentProvider(Interface):
    groupInfo = Field(
        title="Group information",
        description="The group-information instance to display",
        required=True,
        readonly=False)

    pageTemplateFileName = ASCIILine(
        title="Page Template File Name",
        description='The name of the ZPT file that is used to render '
                    'the post.',
        required=False,
        default=b"browser/templates/groupinfo-html.pt")


class ISiteGroups(Interface):
    siteInfo = Field(
        title='Site information',
        description='Information about the site.')

    groupInfos = Field(
        title='Groups information',
        description='A list of groupInfo objects')


class IStatusGroupInfo(IGSGroupInfo):
    show = Bool(
        title='Show',
        description='True if the group should be shown in the profile '
                    'status')
