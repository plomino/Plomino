*** Settings *****************************************************************

Resource  description_plominodatabase.robot
Resource  description_workflow.robot

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
   I can see element Start in the workflow editor
   and I can add a Form Task element by dnd