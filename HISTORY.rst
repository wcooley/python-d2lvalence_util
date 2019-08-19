.. :changelog:

History
-------

0.1.11 (2013-01-04)
+++++++++++++++++++
* revised `auth.D2LAppContext.create_url_for_authentication` to include an
  `encrypt_request` parameter (true by default) to allow generation of
  for-authentication URLs that do not use HTTPS

* added `data.D2LDropboxSubsmission` and several service functions to fill out
  support for the dropbox routes

* fixed parm name in get dropbox folder route

* fixed the `ExternalEmail` properties for `data.CreateUserData` and
  `data.UpdateUserData` to provide better support for having `None` values
  (which will translate to `null` when serialized to JSON)

* added `service.update_user()` for updating user records

* fixed the `RoleId` property for `data.CreateUserData` to have an empty default
  value rather than a numeric default (which probably isn't a useful default for
  anyone)

* added `data.UserPasswordData` and service methods to support the user password
  routes (deleting, changing, resetting)

* added `data.Organization` and `data.OrgUnit` and service methods to support
  routes that query the org structure

* added `data.EnrollmentData` and service functions to fill out support for
  enrollment routes

* added `data.IncomingGradeValue` and its derived classes, and service functions
  to fill out support for grades routes

* added `data.NewsItem` and several service functions to fill out support for
  the news routes

* added support to `service` module to try and support pre-1.0.0 requests
  package as well as post-1.0.0 versions.

0.1.10 (2012-12-18)
+++++++++++++++++++
* revised `data` and `service` modules to update for compatibility with requests
  package post version 1.0.0

0.1.9 (2012-10-15)
++++++++++++++++++
* added data and service functions for Learning Repostory routes

* added data and service functions for course offering and content routes

* added data and service functions for discussion forum routes
* renamed utility functions in `data` module used for property set/getting to
  suggest they should be internal and not directly used

* added default (empty) value for `DescriptorDict` property to the
  `data.D2LLockerFile` class

* added `files` named parameter to post and put utility methods for simple file
  post/puts

* fix `service.rename_group_locker_folder()` to properly form route

* cleanup service module to python-ify parameter names

0.1.8 (2012-08-30)
++++++++++++++++++
* added support to the `auth` module for building an anonymous user context
  (context with no user ID/Key pair) -- clients can use such a context to make
  calls to the various API Property/Version routes to query LMS for API versions

* moved auth to use direct `==` comparison to check for empty parameters instead
  of use `in (singleItemList,)` pattern

* factored out process of fetching contents of Requests objects into a single
  funtion, moved to examine `request.headers['content.type']` to determine how
  to handle contents rather than just `try` to fetch r.JSON and default to
  r.content

* repaired `service.check_versions()` to pass the `supported_version_request_array`
  as json data

* fixed `service._simple_upload()` to seek underlying buffer stream to head
  position before and after read, instead of trying to seek on the byte-string
  we read the stream into

* added support to the `service` library for distinguishing between anonymous and
  non-anonymous user contexts, and let version calls be made with anonymous
  contexts, raise errors in the case of all other calls that demand a user context

* added more grade routes for fetching 'my' grades

0.1.7 (2012-08-10)
++++++++++++++++++
* added `service.get_profile_by_user_id()`

* added `data.LockerItem`, `data.LockerFolder`, `data.GroupLocker` to support
  locker operations

* added to suite of locker functions to the `service` module to assist with locker
  operations: this includes an example of how you might want to handle the
  "simple upload" process for those Valence routes that use simple file upload

0.1.6 (2012-07-13)
++++++++++++++++++
* Fix bug in `update_social_media_url_by_url()`... we should look
  for 'url'-keyed entries, not 'name'-keyed entries

* Some documentation revisions

* Remove 'exceptions' module as not utilized

0.1.5 (2012-07-11)
++++++++++++++++++
* Changed `D2LStructure.as_json()` to kick back a deep-copy of the encapsulated
  data, instead of a ref to the instance's internal data structure

* Bug fixes

0.1.4 (2012-07-06)
++++++++++++++++++
* Refactoring and re-building of the libraries: moved data-structures into
  `data` module and service-related functions into `service` module;
  auth-related functionality remains in `auth`

* Re-worked samples to be more in line with design for the other client
  libraries

0.1.0 (2012-06-02)
++++++++++++++++++
* Initial version

