*** Settings *****************************************************************

Resource  description_plominodatabase.robot
Resource  description_workflow.robot
Resource  description_views.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************

Scenario: As a test user I can open Workflow editor
  Given a logged-in test user
   and I open the ide for "mydb"
  Then I can see the workflow editor
   and I can see element Start in the workflow editor

Scenario: As a test user I can add Form task to workflow editor
  Given a logged-in test user
   and I open the ide for "mydb"
  Then I can see the workflow editor
   and I can see element Start in the workflow editor
   and I can add a Form Task element

Scenario: As a test user I can create a view of form with all fields from the workflow editor
  Given a new form "frm_employee" is created and some fields are added
  And I open workflow tab
  And I add a view task from the Add Panel
  And I click on View task
  And I create new view from form
  When I add an All Form View
  Then I can see that the 'Create view of form' dialog is displayed
  And when I fill in the fields with id="mainform_all_view_id", title="mainform_view", form="frm_employee"
  Then I can successfully view all fields in the form with title="mainform_view"

