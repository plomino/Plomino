*** Settings *****************************************************************

Resource  description_plominodatabase.robot
Resource  description_workflow.robot

Test Setup   Open SauceLabs test browser
Test Teardown  description_plominodatabase.Plone Test Teardown

*** Test Cases ***************************************************************

Scenario: As a test user I can open Workflow editor
  Given a logged-in site administrator
   and I open the ide for "mydb"
  Then I can see the workflow editor
   and I can see element Start in the workflow editor

Scenario: As a test user I can add Form task to workflow editor
  Given a logged-in site administrator
   and I open the ide for "mydb"
  Then I can see the workflow editor
   and I can see element Start in the workflow editor
   and I can add a Form Task element by dnd