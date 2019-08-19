.. :changelog:

History
-------

0.1.8()
+++++++
* added support to the `auth` module for building an anonymous user context
  (context with no user ID/Key pair) -- clients can use such a context to make
  calls to the various API Property/Version routes to query LMS for API versions
* moved auth to use direct `==` comparison to check for empty parameters instead
  of use `in (singleItemList,)` pattern.
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
  "simple upload" process for those Valence routes that use simple file upload.

0.1.6 (2012-07-13)
++++++++++++++++++
* Fix bug in `update_social_media_url_by_url()`... we should look
  for 'url'-keyed entries, not 'name'-keyed entries.

* Some documentation revisions

* Remove 'exceptions' module as not utilized

0.1.5 (2012-07-11)
++++++++++++++++++
* Changed `D2LStructure.as_json()` to kick back a deep-copy of the encapsulated
  data, instead of a ref to the instance's internal data structure.

* Bug fixes

0.1.4 (2012-07-06)
++++++++++++++++++
* Refactoring and re-building of the libraries: moved data-structures into
  `data` module and service-related functions into `service` module;
  auth-related functionality remains in `auth`

* Re-worked samples to be more in line with design for the other client
  libraries.

0.1.0 (2012-06-02)
++++++++++++++++++
* Initial version

