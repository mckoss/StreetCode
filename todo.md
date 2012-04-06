StreetCode Application Code

X /1AB broken
  X Fix up client fields to use name, not displayName.
- Merge Michael's mobile code.
- Add form ordering to models.


Admin and Forms

- Do form hooks for processing special controls like QR-code display and Markdown parsing.
  - Use markdown for story text.
  - Add QR codes to client edit page.
- Handle missing fields (null) values as empty controls, not "null".
- Link to parent forms in list form and item form.

REST Data

- Support reference properties:
  - View to use Select picker
  - Update with id
  - schema type should be model name, control=select
- Use Deferred for ajax callbacks in rest library.

- Get all client pages working (link from admin).
- Change to editable shortcodes?
- remove /1* hack for short code
- Ensure all REST calls return JSON formatted error messages - dispayed to user.
- Security added - check_permissions callback.
- Add ETAG's for model data.

Testing

- QUnit based testing for data and forms.
