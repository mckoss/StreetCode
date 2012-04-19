# StreetCode Application Code

X /1AB broken
  X Fix up client fields to use name, not displayName.
X Merge Michael's mobile code.
X Add form ordering to models.
- Jet City donation page
- Get all client pages working (link from admin).
X Change to editable shortcodes?
X remove /1* hack for short code
- Shortcode links should be case insensitive!
- get host name from request object - no need in settings - rest/views.py
- Format created/modified date text.  (parse and display)
- Move private keys to datastore globals

# Bugs

- Nulls being displayed in textarea and imageURL on new Client items.
- Sponsor form does not have name field first?
- Models.py - parsing date fails with text timestamp.
- Read-only fields should not be displayed in editable fields (e.g. created and modified).


# Admin and Forms

X Do form hooks for processing special controls like QR-code display and Markdown parsing.
  X Use markdown for story text.
  X Add QR codes to client edit page.
X Handle missing fields (null) values as empty controls, not "null".
- Link to parent forms in list form and item form.
\ Add Bootstrap Less directory and build script for admin pages.
  - Reformat forms for bootstrap
- Display tables for mutli-value (reverse reference) properties.
X Remove Find from item forms.
X Default display name as id# if name is '' or null.
X Ensure strings never null - just ''.
- Distinct display mode for item forms?
- Image uploader with thumbnailing.
X Add link to current reference for reference field.

# REST Data

X Support reference properties:
  X View to use Select picker
  X Update with id
  X schema type should be model name, control=select
* Use Deferred for ajax callbacks in rest library.
- Finish application orm layer in javascript
  - Use in admin
  - Use in mobile profile.
- Include object reference on duplicated traversal - and at end of depth - reconstitute
  in client?  Maybe should have a references section for non-item objects?
X Ensure all REST calls return JSON formatted error messages - dispayed to user.
- Security added - check_permissions callback.
- Add caching to rest app
  - Generate etag hash from data - 304 not modified on GET/HEAD
  - Add Cacheable mixin to models.

# Testing

- QUnit based testing for data and forms.
X Remove demo functions - not needed with Admin interface.
X Deploy to AppEngine.

# Operations

X sc.go2.me -> directing to site.
X streetcodes.org -> directing to site (Google Apps for Domains setup)
X streetcode.me -> for us in qrcodes and shortcuts.
