==========================
``gs.profile.status.base``
==========================
-------------------------------
The profile status notification
-------------------------------

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2015-04-28
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

The *Profile status* notification_ is sent out once a month to
remind people that they are a member of some GroupServer
groups. It is a complex notification that is made up of many
viewlets_. The notification is sent using the sender_.

Notification
============

There are HTML and plain-text forms of the profile status
reminder, both provided in the context of the *profile*.

* ``gs-profile-status.html``
* ``gs-profile-status.txt``

The content of the notifications are made up of viewlets_. The
message is sent with the subject ``Activity at {siteNames}``,
where the site-names is a comma-separated list of the sites the
recipient is a member of.

Viewlets
========

There are seven viewlets that help manage the complexity of the
notification: one for the `Table of contents`_ and then six for
each of the major parts of the notification. The parts can be
grouped into three.

#. The Introduction_, News_ and Support_ provide general
   information.

#. The `Profile information`_ and `Email settings`_ provide
   information that is just specific to a person.

#. The Groups_ provides the core power-house component of the
   notification.

(As there is both a plain-text and HTML form of the email
notification_ this actually equates to fourteen viewlets; they
share *view* code, but differ in the *page templates*.)

Table of contents
-----------------

Because the notification is so long there is a *Table of
contents* viewlet. It lists the other sections in the
notification, using the ``title`` attribute for the entry and the
``name`` to form the ``href`` for the document-link.

Introduction
------------

The *Introduction* (``gs-profile-status-intro``) explains to the
recipient why he or she is getting the notification.

News
----

The *News* (``gs-profile-status-news``) comprises a plain-text
area at the start of the notification. It is retrieved from the
``gs-profile-status-news.xml`` object in the **ZMI**, and dumped
in place as is. If there is no object then the news section is
omitted.

Profile information
-------------------

The *Profile information* (``gs-profile-status-profile``) is the
first complex viewlet. Its purpose is twofold: **show** what
information the person has on his or her profile, and
**encourage** the recipient to update the profile information.

* If there is no **profile image** then a *missing image* image
  is shown, and the recipient encouraged to add an image.

* If the participant has a **name** that is the same as the
  left-hand side of their email address then he or she is
  encourage to add a nicer name.

* If the recipient has no **biography** then he or she is
  encouraged to fill out a biography.

Even if the participant has all of these things, there is a link
to change them if so desired.

If the participant has never logged in, then a link to the
**reset password** page, rather than the change links, is
provided to help the person log in.

Email settings
--------------

The *Email settings* viewlet (``gs-profile-status-email``) shows
the existing addresses, and tries to encourage the participant to
add more email addresses. The idea is that the recipient will be
better able to manage his or her groups when they have more email
addresses (as the same profile can be used for work and play),
and the site will be better able to contact the recipient.

* Links to start the **verification** process for unverified
  links are given.

* An **Add** button is shown, to add another address.

Groups
------

The *Groups* viewlet (``gs-profile-status-groups``) summarises
the groups that the participant is a member of. It is designed to
encourage **better participation** by getting the participant to
use more of the excellent features of GroupServer_, particularly
the email settings [#settings]_.

The list of groups is broken down by site_, and within each site
is listed the `group information`_.

.. _site:

Site information
~~~~~~~~~~~~~~~~

Each site lists its *Title* and the *About* text.

* If the participant is the administrator of the site then a link
  to the ``admindivision`` page is shown.

* If the *About* text is the default then it is omitted. However,
  the administrator is encouraged to fill out the about text in
  this case.

Group information
~~~~~~~~~~~~~~~~~

Within each site all the groups are listed. For each **group**
the following is shown.

* The title. Next to the title is a **Admin** link, if the
  recipient is a group administrator.

* The start of the **About** text, if set. If there is no about
  text and the recipient is the administrator then he or she is
  encouraged to set the *About* text.

* **The posting statistics** for the group in the last month,
  including the number of posts, topics, and authors.

* A selection of **images** posted to the group in the last month.

* The **names** of some of the authors.

* The **profile photos** of some of the authors.

* The **email settings** for the recipient in that particular
  group. If the number of posts is high (over 30) then a
  suggestion to switch to a daily digest of topics is given.

* A link to **leave** the group, by the ``unsubscribe`` command.

Support
-------

The *Support* viewlet (``gs-profile-status-support``) bookends
the notification, along with the other general-information
viewlets (Introduction_ and News_). It includes a link to **email
support** and a way to find the **FAQ**.

Sender
======

The system for actually sending the notification are provided by
two **web hooks**: one provides the `user list`_ and the other is
used to `send the notification`_.

User list
---------

The page ``gs-profile-status-members.html`` in the *site* context
provides a form that returns a list of people that *can possibly*
receive a notification_, as a JSON object [#json]_. It uses
``gs.auth.token`` [#token]_ for authentication.

Send the notification
---------------------

The page ``gs-profile-status-send.html`` in the *site* context
provides a form that sends a notification_ to a participant. The
form takes the user-identifier of the participant, and a token
[#token]_ for authentication. It returns a status as a JSON
object [#json]_.

Resources
=========

- Code repository:
  https://github.com/groupserver/gs.profile.status.base
- Questions and comments to
  http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17

.. [#settings] See
               <https://github.com/groupserver/gs.group.member.email.settings>

.. [#json] See
            <https://github.com/groupserver/gs.content.form.api.json>

.. [#token] See <https://github.com/groupserver/gs.auth.token>

..  LocalWords:  nz GSProfile TODO redirector LocalWords viewlets