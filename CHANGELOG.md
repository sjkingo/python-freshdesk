Changelog
=========

v1.3.9 - 2022-09-16

 * #80: Add support for Contacts (@mmahacek)

v1.3.8 - 2021-04-21

 * #70: Add methods to create, update and delete Solutions (@Pr0teus)

v1.3.7 - 2020-10-07

 * #64 & #65: Add completed support for time entries in API (@majorcs)

v1.3.6 - 2020-09-15

 * #62: Add create & update company (@aharabedian)

v1.3.5 - 2020-09-01

 * #59: Optionally include extra stats in get_ticket (@jstitch)
 * #60: Add delete company (@aharabedian)

v1.3.4 - 2020-07-24

 * Fix versioning issue. No code changes (@sjkingo)

v1.3.3 - 2020-07-24

 * #58: Add "updated_since" argument to list tickets (@jatzz10)

v1.3.2 - 2020-07-15

 * #55: Added filtering of companies (@RyanOM)

v1.3.1 - 2020-07-13

 * #54: Added pagination support for comments (@jatzz10)
 * Fixed date in changelog for v1.3.0 (@sjkingo)

v1.3.0 - 2020-07-10

 * Return v2 of the Freshdesk API by default (@sjkingo)
 * Reformat codebase with black (@sjkingo)
 * Tidied README (@sjkingo)

v1.2.8 - 2020-07-10

 * #52: Add list companies (@RyanOM)

v1.2.7 - 2020-05-22

 * #50: Fix quoting in ticket query filter (@FellipeMendonca)

v1.2.6 - 2020-01-31

 * #47: Remove obsolete code (@maqquettex)
 * #45: Add support for ticket filtering (@andybotting)
 * #43: Fix Python3 incompatibility in dict test (@hakib)
 * #42: Fix encoding and content-type when creating tickets with attachments (@ArtemGordinsky)
 * Add test environments for Python 3.7 and 3.8 (@sjkingo)

v1.2.5 - 2019-10-23

 * #41: Refactor tests and switch to pytest (@ArtemGordinsky)
 * Fix typo in Company repr (@sjkingo)

v1.2.4 - 2019-10-19

 * #38: Add ticket time entry API (@smontoya)
 * #39: Support binary ticket attachments (@ArtemGordinsky)
 * Drop Python 3.3 from Travis CI and add 3.6 (@sjkingo)

v1.2.3 - 2018-09-23
  
  * #28: Changes from #28 create ticket with attachments (@prenit-coverfox)
  * #25: Changes from #25 update_contact, restore_contact (@vdboor)
  * #22: Changes from #22 pagination in list_groups(@prenit-coverfox)

v1.2.2 - 2018-07-09

  * #20: Changes from #20 including v1 deprecation (@prenit-coverfox)

v1.2.1 - 2018-07-05

  * #21: Fixed set declaration bug in base class (@sjkingo)

v1.2.0 - 2018-06-27

  * Filled out v1 and v2 API's and expanded test cases (@prenit-coverfox)

v1.1.2 - 2018-06-04

  * No code changes: fix release stuff up (@sjkingo)

v1.1.1 - 2018-06-04

  * #16: Add support for Role, Ticket fields and Agent API (@prenit-coverfox)

v1.1.0 - 2018-01-08

  * #13: Fixed group representation (@helix90)
  * #14: Add support for Company API (@helix90)
  * #11: Add support for creating outbound emails (@sorrison)

v1.0.1 - 2017-08-26

  * Allow clients to specify empty filter name (@brephophagist)

v1.0.0 - 2016-06-16

  * Add support for version 2 of the Freskdesk API while maintaining support for
    the older version 1 (@andybotting)

v0.9.4 - 2015-08-09

  * Added support for timesheets (@fstolba)

v0.9.3 - 2015-01-09

  * Implement proper timezone handling instead of hardcoding

v0.9.2 - 2015-01-02

  * Mocked out test suite API for performance
  * Added support for getting a Contact/User from the API

v0.9.1 - 2015-01-01

  * Added full test suite for Ticket API

v0.9.0 - 2014-12-31

  * Initial release with support for the Ticket API
