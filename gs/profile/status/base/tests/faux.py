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
from email.parser import Parser


def faux_email(subject):
    retval = Parser().parsestr(
        b'From: <member@example.com>\n'
        b'To: <group@example.com>\n'
        b'Subject: {0}\n'
        b'\n'
        b'Body would go here\n'.format(subject))
    return retval


def faux_off_email():
    return faux_email('Summary off')


def faux_on_email():
    return faux_email('Summary on')


class FauxSiteInfo(object):
    name = 'An Example Site'
    id = b'example'


class FauxGroupInfo(object):
    name = 'An Example Group'
    id = b'example_group'
    url = 'https://lists.example.com/groups/example_group'
    siteInfo = FauxSiteInfo()
    groupObj = 'This is not a folder'


class FauxUserInfo(object):
    name = 'An Example user'
    id = b'exampleuser'
    anonymous = False
    url = 'https://groups.example.com/p/exampleuser'
    context = None
    user = None
