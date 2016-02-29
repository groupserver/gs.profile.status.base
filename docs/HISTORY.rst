Changelog
=========

1.2.3 (2016-02-29)
------------------

* Following the update to `gs.group.member.base`_

.. _gs.group.member.base:
   https://github.com/groupserver/gs.group.member.base

1.2.2 (2015-12-11)
------------------

* Fixing some unit tests
* Following the update to the ``EmailUser`` class from
  `gs.profile.email.base`_

.. _gs.profile.email.base:
   https://github.com/groupserver/gs.profile.email.base

1.2.1 (2015-10-28)
------------------

* Adding to the *pre-header* so the preview in Apple Mail has
  none of the body-text (which was confusing to read)

1.2.0 (2015-10-01)
------------------

* Skipping people that lack activity for the month in **all**
  their groups
* Ensuring that people that have opted out of getting the
  notification are not sent the notification

1.1.4 (2015-09-21)
------------------

* Using ``subject`` rather than ``Subject`` in ``mailto:`` URIs

1.1.3 (2015-09-03)
------------------

* Fixing a spelling mistake, thanks to Jim

1.1.2 (2015-07-06)
------------------

* Fixing a hard-coded group-name
* Being very strict on the definition of *group member*
* Fixing a spelling mistake in the audit-trail code

1.1.1 (2015-06-22)
------------------

* Following the renaming of `gs.site.member.base`_

.. _gs.site.member.base:
   https://github.com/groupserver/gs.site.member.base

1.1.0 (2015-06-10)
------------------

* Reduced the number of topics, and keywords that are shown
* Showing people with profile photos by preference
* Added a ``Digest off`` link for quiet groups
* Split the keywords into important, normal, and minor to provide
  texture
* Added the ability to skip some sites
* Moved the ``Status off`` notification to its own product:
  `gs.profile.status.change`_

.. _gs.profile.status.change:
   https://github.com/groupserver/gs.profile.status.change

1.0.1 (2015-06-02)
------------------

* Fixing the links to the topics
* Fixing the email title so it matches the main heading: *What is
  going on in your groups*
* Fixing the *Change profile* URL.

1.0.0 (2015-05-28)
------------------

Initial version. Before the creation of this product there was no
monthly status notification.

..  LocalWords:  Changelog
