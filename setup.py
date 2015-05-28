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
import codecs
import os
import sys
from setuptools import setup, find_packages
from version import get_version

version = get_version()

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.rst"),
                 encoding='utf-8') as f:
    long_description += '\n' + f.read()

requires = [
    'setuptools',
    'pytz',
    'sqlalchemy',
    'zope.app.pagetemplate',
    'zope.browserpage',
    'zope.cachedescriptors',
    'zope.component',
    'zope.contentprovider',
    'zope.formlib',
    'zope.interface',
    'zope.schema',
    'zope.tal',
    'zope.tales',
    'zope.viewlet',
    'gs.auth.token',
    'gs.cache',
    'gs.content.email.base',
    'gs.content.email.layout',
    'gs.content.form.api.json',
    'gs.core',
    'gs.database',
    'gs.group.memeber.base',
    'gs.group.member.canpost',
    'gs.group.member.email.base',
    'gs.group.privacy',
    'gs.group.stats',
    'gs.profile.base',
    'gs.profile.email.base',
    'gs.profile.image.base',
    'gs.profile.notify',
    'gs.site.member',
    'Products.CustomUserFolder',
    'Products.GSGroup',
    'Products.GSGroupMember',
]
if (sys.version_info < (3, 4)):
    requires += ['setuptools', ]

setup(
    name='gs.profile.status.base',
    version=version,
    description="The profile status notification on GroupServer",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='profile, groupserver, email, notification',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='https://github.com/groupserver/gs.profile.status.base/',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.profile', 'gs.profile.status'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points="""
    # -*- Entry points: -*-
    """,)
