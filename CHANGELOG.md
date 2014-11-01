# Changelog

### 1.0.4

* fix for missing Flickr API keys in the bookmarklet on the upgrade bookmarklet page

### 1.0.3

* reorder css files, mediathread specific styles should come after bootstrap

### 1.0.2

* restart nginx during deployment

### 1.0.1

* fix for the Digital Ocean settings file (using list instead of tuples)

### 1.0.0

* updated Mediathread to version [v2014_Fall](https://github.com/ccnmtl/mediathread/releases/tag/v2014_Fall)
* Ansible scripts improved, separated hosts to testing/staging/production
* SSL support added to Ansible scripts
* Fixed the functional testing (Lettuce) database to work with Appsembler code changes

### 0.3.1

* fix for checking how many courses can a user create on the creation form

### 0.3.0

* added a set of ansible scripts for automating provisioning and deployment
* number of courses limit is now individual for a user

### 0.2.17

* serves jsi18n as a static file

### 0.2.16

* removed some uncompressable assets from the compress block

### 0.2.15

* refactoring of compress tags in base.html

### 0.2.14

* moved some S3 settings from app code to settings file

### 0.2.13

* fixed the bug where a newly registered user is redirected to the set password form

### 0.2.12

* fixed the bug when trying to change the avatar

### 0.2.11

* changed the link to the knowledge base on the invite students template

### 0.2.8 - 0.2.10

* when confirming account/email, user is now correctly redirected to the set password page

### 0.2.7

* fixed a bug when trying to invite an existing user but using a email address with different capitalization of letters
than the existing email

### 0.2.6

* completely disable smoke tests so that the Travis CI build doesn't fail

### 0.2.5

* increased the length of organization name field to 100
* fixed the bug where user profiles weren't created for newly invited users

### 0.2.1 - 0.2.4

* bugfixes

### 0.2.0
* user profiles added
* improved call to action bars
* integrated upstream changes from release [v2013_Fall.3](https://github.com/ccnmtl/mediathread/releases/tag/v2013_Fall.3)

### 0.1.2 - 0.1.6

* bugfixes

### 0.1.1

* fixed absolute paths to static files in mediathread.css to be
  compatible with S3

### 0.1

* static files server used Amazon S3 ([#137](https://trello.com/c/03Y3xdxx/137-use-django-storages-to-send-all-static-assets-to-s3))
* added welcome screen for newly registered users ([#146](https://trello.com/c/nkMlxRXq/146-optional-enrolling-to-sample-course))
* fixed sending the correct user type to segment.io ([#148](https://trello.com/c/iNPBSDkh/148-fix-sending-the-user-type-to-segment-io))
* new users have the option of joining the sample course only as students
