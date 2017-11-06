This file contains a series of test databases that will be loaded automatically
for the test layer for all the robot tests. This should speed up tests by not
having to create forms and documents via selenium.

The folder layout is

- test_dbs/
  - test_views/
    - frm1.json
    - settings.json
    - ...
  - test_views_data.json
  - test_workflow/
    - frm1.json
    - settings.json
    - ...
  - test_workflow_data.json
  - ...

They will be availble in the plone site based on the folder names under test_dbs.
Currently all the db's are loaded for every test but that might change in the future.