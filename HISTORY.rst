.. :changelog:

History
-------

0.1.0 (2012-06-02)
++++++++++++++++++
* Initial version

0.1.4 (2012-07-06)
++++++++++++++++++
* Refactoring and re-building of the libraries: moved data-structures into
  `data` module and service-related functions into `service` module;
  auth-related functionality remains in `auth`

* Re-worked samples to be more in line with design for the other client
  libraries.

0.1.5 (2012-07-11)
++++++++++++++++++
* Changed D2LStructure.as_json() to kick back a deep-copy of the encapsulated
  data, instead of a ref to the instance's internal data structure.

* Bug fixes

0.1.6 (2012-07-13)
++++++++++++++++++
* Fix bug in update_social_media_url_by_url(self,name,url)... we should look
  for 'url'-keyed entries, not 'name'-keyed entries.

* Some documentation revisions

* Remove 'exceptions' module as not utilized
